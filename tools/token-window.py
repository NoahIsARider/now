# -*- coding: utf-8 -*-
"""A one-field local window for handing the sr.ht token to the publish script.

Runs on 127.0.0.1 only. The value typed into the form is written straight to
~/.srht-token and is never printed to stdout, never echoed back, never logged.
"""
import http.server
import os
import pathlib
import urllib.parse

TOKEN_PATH = pathlib.Path.home() / ".srht-token"
PORT = 8788
FONT_DIR = pathlib.Path(__file__).resolve().parent.parent / "assets" / "fonts"

HEAD = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MAYDAY — sr.ht token</title>
<style>
@font-face{font-family:'Special Elite';src:url('/fonts/specialelite-400.woff2') format('woff2');}
@font-face{font-family:'Courier Prime';font-weight:400;src:url('/fonts/courierprime-400.woff2') format('woff2');}
@font-face{font-family:'Courier Prime';font-weight:700;src:url('/fonts/courierprime-700.woff2') format('woff2');}
*{box-sizing:border-box}
body{margin:0;background:#fff;color:#000;font-family:'Courier Prime','Courier New',monospace;font-size:15px;line-height:1.55}
.shell{max-width:760px;margin:0 auto;border-left:1px solid #000;border-right:1px solid #000;min-height:100vh}
.hazard{height:7px;border-top:1px solid #000;border-bottom:1px solid #000;
  background:repeating-linear-gradient(45deg,#000 0 1px,transparent 1px 7px)}
.mast{display:grid;grid-template-columns:auto 1fr;border-bottom:1px solid #000}
.mast>*{padding:18px}
.mast>*:first-child{border-right:1px solid #000}
h1{font-family:'Special Elite','Courier New',monospace;font-size:44px;line-height:.9;margin:0;letter-spacing:.01em}
.mast p{margin:0;font-size:13px}
.body{padding:22px}
h2{font-family:'Special Elite','Courier New',monospace;font-size:20px;margin:0 0 12px;border-top:2px solid #000;padding-top:12px}
label{display:block;font-size:10.5px;font-weight:700;letter-spacing:.2em;margin-bottom:6px}
input[type=password]{width:100%;font:inherit;padding:10px;border:1px solid #000;background:#fff;color:#000}
input[type=password]:focus{outline:2px solid #000;outline-offset:2px}
button{margin-top:16px;font:inherit;font-weight:700;letter-spacing:.14em;padding:10px 16px;border:1px solid #000;background:#000;color:#fff;cursor:pointer}
button:hover{background:#fff;color:#000}
ol{margin:10px 0 0;padding-left:1.4em;font-size:13px}
li{margin-bottom:4px}
ul.links{margin:14px 0 0;padding:0;list-style:none;font-size:13px}
.key{font-family:'Special Elite',monospace}
.foot{border-top:1px solid #000;padding:14px 22px;font-size:11px;letter-spacing:.14em}
</style></head><body><div class="shell"><div class="hazard"></div>"""

MAST = """<div class="mast"><h1>MAYDAY</h1>
<p>Publishing a films manifest to sourcehut pages.<br>
This page is served by your own machine on <b>127.0.0.1</b> and nothing leaves it.</p></div>"""

FORM = """<div class="body">
<h2>Hand over the sr.ht token</h2>
<p>Create it at <a href="https://meta.sr.ht/oauth2/personal-token" target="_blank" rel="noopener">
meta.sr.ht/oauth2/personal-token</a>, tick the grant</p>
<ol>
  <li><b>pages.sr.ht/PAGES:RW</b> &nbsp;— needed, publishes the site</li>
  <li><b>git.sr.ht/REPOSITORIES:RW</b> &nbsp;— optional, lets me create the repository
      <span class="key">git.sr.ht/~noahisarider/MAYDAY</span> and push the source</li>
</ol>
<form method="post" action="/save" autocomplete="off">
  <label for="t">TOKEN (not shown, not logged, written to ~/.srht-token)</label>
  <input id="t" type="password" name="token" autocomplete="off" spellcheck="false" autofocus>
  <button type="submit">SAVE</button>
</form>
<ul class="links">
  <li>Token page not found? The old plural URL 404s. Use the singular one above.</li>
  <li>Nothing is verified until you press SAVE. The page can be closed afterwards.</li>
</ul>
</div>
<div class="foot">MAYDAY MAYDAY MAYDAY</div></div></body></html>"""

OK = """<div class="body"><h2>Saved</h2>
<p>The token is in <b>~/.srht-token</b>. I did not read it, and it is not in this page or in the transcript.</p>
<p>You can close this tab. Back in the chat, say anything and the publish runs.</p></div>
<div class="foot">MAYDAY MAYDAY MAYDAY</div></div></body></html>"""

BAD = """<div class="body"><h2>That did not look like a token</h2>
<p>It was either empty, shorter than 20 characters, or contained spaces. Nothing was written.</p>
<p><a href="/">Try again</a></p></div>
<div class="foot">MAYDAY MAYDAY MAYDAY</div></div></body></html>"""


class H(http.server.BaseHTTPRequestHandler):
    server_version = "mayday-token-window"

    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.startswith("/fonts/"):
            p = FONT_DIR / os.path.basename(self.path)
            if p.is_file():
                data = p.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "font/woff2")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
        self._send(200, HEAD + MAST + FORM)

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n).decode("utf-8", "replace")
        token = urllib.parse.parse_qs(raw).get("token", [""])[0].strip()
        if len(token) >= 20 and not any(c.isspace() for c in token):
            tmp = TOKEN_PATH.with_name(TOKEN_PATH.name + ".tmp")
            tmp.write_text(token, encoding="utf-8")
            try:
                os.chmod(tmp, 0o600)
            except OSError:
                pass
            tmp.replace(TOKEN_PATH)
            print(f"[token window] received {len(token)} characters, wrote {TOKEN_PATH}", flush=True)
            self._send(200, HEAD + MAST + OK)
        else:
            print(f"[token window] rejected input of length {len(token)}", flush=True)
            self._send(200, HEAD + MAST + BAD)


if __name__ == "__main__":
    socketserver = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), H)
    print(f"[token window] open http://127.0.0.1:{PORT}/  (ctrl-c or kill to stop)", flush=True)
    socketserver.serve_forever()
