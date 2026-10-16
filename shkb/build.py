# -*- coding: utf-8 -*-
"""
shkb site builder, run as part of the merged home site.
    python build.py       ->  writes ../site/shkb/  (published at /shkb/)

Source of truth is data/albums.json, generated from a record.club export
(see tools/build-releases-from-export.py). Design: a dark depth log, one
column of typewriter type, the only light is the link blue. See DESIGN.md.
"""
import html
import json
import os
import shutil
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(ROOT, "..", "site", "shkb"))
DATA = os.path.join(ROOT, "data", "albums.json")
ASSETS = os.path.join(ROOT, "assets")

_BASE = os.environ.get("SITE_URL", "https://noahisarider.srht.site").rstrip("/")
SITE_URL = _BASE + "/shkb"
CLEAN_URL = SITE_URL.replace("https://", "").replace("http://", "")  # used only in og:desc
REPO = "https://git.sr.ht/~noahisarider/now/tree/master/item/shkb"

TAGLINE_A = ("We all get hurt by others, and we all hurt others, and history "
             "repeats itself again and again.")
TAGLINE_B = "We learn to breathe underwater, like the people a century later."
VERDICT = "We are all bullies."


def e(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def release_url(album):
    return album.get("url", "")


def score(album):
    if album.get("rating") is None:
        return ""
    return f'{album["rating"]}<span class="of">/10</span>'


def kind(album):
    return {"ep": "ep", "single": "single"}.get(album["type"], "")


def layout(*, title, desc, p, body, path, indexable=True):
    url = f"{SITE_URL}/{path}" if path else f"{SITE_URL}/"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(url)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(url)}">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#0b1116">
<meta name="author" content="noahisarider">
{f'<meta name="robots" content="noindex">' if not indexable else ''}
<link rel="icon" href="{p}favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{p}assets/style.css">
</head>
<body>
<div class="shell">
{body}
</div>
</body>
</html>
"""


def footer(p):
    return f"""<footer class="foot">
  <p class="signal">shkb</p>
  <ul>
    <li><a href="{p}">the depth log</a></li>
    <li><a href="/MAYDAY/">films</a></li>
    <li><a href="/">now</a></li>
    <li><a href="{e(REPO)}">source repository</a></li>
  </ul>
  <p class="meta">compiled by noahisarider · record data from a record.club export · built {date.today().isoformat()} · no cookies, no trackers</p>
</footer>"""


def masthead(data):
    c = data["counts"]
    rest = c["total"] - c["albums"]
    rest_note = (f" {c['eps']} eps and {c['singles']} single share the log with them."
                 if rest else "")
    return f"""<header class="mast">
  <h1 class="mark">shkb</h1>
  <div class="quote">
    <p>{e(TAGLINE_A)}</p>
    <p>{e(TAGLINE_B)}</p>
  </div>
  <p class="verdict">{e(VERDICT)}</p>
  <p class="stats">{c['total']} releases, {c['albums']} of them albums.{rest_note}
  {c['rated']} I have rated, {c['ten']} of them ten out of ten.
  {c['year_min']} to {c['year_max']}.</p>
</header>"""


def page_index(data):
    albums = data["albums"]
    entries = []
    for a in albums:
        hay = " ".join([a["title"], a["artist"], str(a["year"]),
                        kind(a) or "album"])
        meta_bits = [a["artist"]]
        if kind(a):
            meta_bits.append(kind(a))
        entries.append(f"""  <li class="entry" data-rating="{a['rating'] if a['rating'] is not None else ''}"
      data-hay="{e(hay.lower())}">
    <div class="no">{a['n']:03d}</div>
    <div>
      <div class="head">
        <span class="name"><a href="{e(release_url(a))}">{e(a['title'])}</a></span>
        <span class="tail"><span class="score">{score(a)}</span>
          <span class="year">{a['year']}</span></span>
      </div>
      <div class="meta">{e(" · ".join(meta_bits))}</div>
    </div>
  </li>""")

    chips = "".join(
        f'<button class="chip" type="button" data-rating="{r}" aria-pressed="false">{r}</button>'
        for r in (10, 9, 8))
    body = masthead(data) + f"""
<section class="controls">
  <label class="field"><span class="lab">search</span>
    <input id="q" type="search" autocomplete="off"
           placeholder="title, artist, or year"
           aria-label="Search releases"></label>
  <p class="chips" id="chips"><span class="lab">score</span>{chips}</p>
</section>
<p class="count" id="count">showing {len(albums)} of {len(albums)} releases</p>
<ol class="entries">
{chr(10).join(entries)}
</ol>
<p class="empty" id="empty" hidden>Nothing in the depth log answers to that.
Try fewer words, or clear the score filters.</p>
<script src="assets/app.js" defer></script>
{footer('./')}"""
    desc = (f"Every record I have listened to, {len(albums)} releases from "
            f"{data['counts']['year_min']} to {data['counts']['year_max']}. "
            + TAGLINE_A + " " + VERDICT)
    return layout(title="shkb — a listening manifest",
                  desc=desc, p="./", path="", body=body)


def page_404():
    body = f"""<p class="top"><a href="/shkb/">← the depth log</a><span class="selfurl">404</span></p>
<div class="doc">
  <section>
    <h2>Nothing at this depth</h2>
    <p>The page you asked for is not on the log. Check the spelling, or go back to the list.</p>
    <p><a href="/shkb/">the depth log</a></p>
  </section>
</div>
""" + footer("/shkb/")
    return layout(title="404 — shkb", desc="Page not found.", p="/shkb/",
                  path="404.html", body=body, indexable=False)


def main():
    data = json.load(open(DATA, encoding="utf-8"))
    albums = data["albums"]

    if os.path.isdir(SRC):
        shutil.rmtree(SRC)

    shutil.copytree(os.path.join(ASSETS, "fonts"), os.path.join(SRC, "assets", "fonts"))
    for f in ("style.css", "app.js"):
        shutil.copy(os.path.join(ASSETS, f), os.path.join(SRC, "assets", f))
    shutil.copy(os.path.join(ASSETS, "favicon.svg"), os.path.join(SRC, "favicon.svg"))

    def w(path, text):
        full = os.path.join(SRC, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "w", encoding="utf-8").write(text)

    w("index.html", page_index(data))
    w("404.html", page_404())

    urls = [f"{SITE_URL}/"]
    w("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      "".join(f"  <url><loc>{e(u)}</loc></url>\n" for u in urls) + "</urlset>\n")
    w("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    w("albums.json", json.dumps(data, ensure_ascii=True, indent=2) + "\n")

    pages = sum(len(fs) for _, _, fs in os.walk(SRC))
    size = sum(os.path.getsize(os.path.join(d, f))
               for d, _, fs in os.walk(SRC) for f in fs)
    rated = sum(1 for a in albums if a["rating"] is not None)
    print(f"built {pages} files, {size/1024:.0f} KiB into {SRC} "
          f"({len(albums)} releases, {rated} rated, index + about)")


if __name__ == "__main__":
    main()
