# -*- coding: utf-8 -*-
"""Build the Nymph games shelf into ../site/nymph/.

Content model:
  data/games.json  — the statement block plus one object per game

A game carries title, studio, year, url, a one line lede and a short note.
Alphabetical by title, numbered on the page, no scores and no dates.
The page is one list: masthead, statement, shelf, footer. No nav, no about.

Run from the root build.py (build_section("nymph")) or directly.
"""
import html
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "site", "nymph"))
DATA = os.path.join(HERE, "data", "games.json")
ASSETS = os.path.join(HERE, "assets")

SITE_URL = os.environ.get("SITE_URL", "https://noahisarider.srht.site")
BASE = SITE_URL.rstrip("/") + "/nymph"
MARK = "nymph"
DESC = "The games I own and keep installed, one note each."

# The switch. Runs before the first paint so the page never flashes the wrong
# paper, and remembers the choice. Without javascript the system decides.
SCRIPT = """<script>
(function () {
  var root = document.documentElement, key = "nymph-theme", pick = null;
  try { pick = localStorage.getItem(key); } catch (e) {}
  if (pick !== "day" && pick !== "night") {
    pick = window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "night" : "day";
  }
  root.setAttribute("data-theme", pick);
  document.addEventListener("click", function (ev) {
    var el = ev.target.closest ? ev.target.closest("[data-theme-set]") : null;
    if (!el) return;
    var value = el.getAttribute("data-theme-set");
    root.setAttribute("data-theme", value);
    try { localStorage.setItem(key, value); } catch (e) {}
  });
})();
</script>"""


def e(s):
    return html.escape(str(s if s is not None else ""), quote=True)


# --------------------------------------------------------------------------
# chrome

def mast(pre):
    return f'''<header class="mast">
  <a class="mark" href="{pre}">nymph</a>
  <div class="aside">
    <p class="stamp">games by noahisarider</p>
    <p class="light">
      <button type="button" data-theme-set="day">day</button>
      <span class="sep">/</span>
      <button type="button" data-theme-set="night">night</button>
    </p>
  </div>
</header>'''


def footer(depth):
    pre = "../" if depth == 1 else "../../"
    return (f'<footer class="foot">'
            f'<a href="{pre}">now</a>'
            f'<a href="{pre}babel/">books</a>'
            f'<a href="{pre}MAYDAY/">films</a>'
            f'<a href="{pre}shkb/">records</a>'
            f'<br>'
            f'<a href="https://www.goodreads.com/ratkingsyndrome">goodreads</a>'
            f'<a href="https://record.club/noahisarider">record.club</a>'
            f'<a href="https://letterboxd.com/noahisarider/">letterboxd</a>'
            f'<a href="https://sr.ht/~noahisarider/">sr.ht</a>'
            f'</footer>')


def layout(title, desc, depth, body, path=""):
    font_pre = ("assets/fonts/" if depth == 1 else "../assets/fonts/")
    css_pre = ("assets/style.css" if depth == 1 else "../assets/style.css")
    fav_pre = ("favicon.svg" if depth == 1 else "../favicon.svg")
    pre = "./" if depth == 1 else "../"
    url = f"{BASE}/{path}" if path else f"{BASE}/"
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
<meta name="author" content="noahisarider">
<link rel="icon" href="{fav_pre}" type="image/svg+xml">
<link rel="stylesheet" href="{font_pre}fonts.css">
<link rel="stylesheet" href="{css_pre}">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#f0fa92" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#1a1a17" media="(prefers-color-scheme: dark)">
{SCRIPT}
</head>
<body>
<div class="shell">
{mast(pre)}
{body}
{footer(depth)}
</div>
</body>
</html>
"""


# --------------------------------------------------------------------------
# pages

def page_index(data):
    st = data["statement"]
    games = data["games"]
    kicker = f'{e(st["kicker"])}<span class="sep">/</span>{len(games)} games'
    lead_html = f'''<section class="lead">
  <p class="kicker">{kicker}</p>
  <h1 class="title">{e(st["title"])}</h1>
  <p class="lede">{e(st["lede"])}</p>
</section>'''

    rows = []
    for n, g in enumerate(games, start=1):
        rows.append(f'''    <li><a href="{e(g["url"])}">
      <span class="row-kicker">{n:03d}<span class="sep">/</span>{e(g["studio"])}<span class="sep">/</span>{e(g["year"])}</span>
      <span class="row-title">{e(g["title"])}</span>
      <span class="row-lede">{e(g["lede"])}</span>
      <span class="row-note">{e(g["note"])}</span>
    </a></li>''')
    shelf = f'''<section class="index">
  <h2 class="label">the shelf</h2>
  <ul class="rows">
{chr(10).join(rows)}
  </ul>
</section>'''
    return layout(f'{MARK} — games', DESC, 1, lead_html + shelf)


def page_404():
    body = ('<section class="lead">'
            '<p class="kicker">404</p>'
            '<h1 class="title">Nothing here</h1>'
            '<p class="lede">That shelf is empty, or the link is wrong.</p>'
            '</section>'
            '<p class="back"><a href="./">all games</a></p>')
    return layout(f'404 — {MARK}', "page not found", 1, body)


def favicon_svg():
    # the same stamped block as the masthead, flipped with the page
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
            '<style>.paper{fill:#1a1a17}.type{fill:#f0fa92}'
            '@media (prefers-color-scheme: dark){.paper{fill:#f0fa92}'
            '.type{fill:#1a1a17}}</style>'
            '<circle class="paper" cx="16" cy="16" r="16"/>'
            '<text class="type" x="16" y="23" text-anchor="middle" '
            'font-family="Georgia, serif" font-size="19" font-weight="bold">n</text>'
            '</svg>')


def main():
    data = json.load(open(DATA, encoding="utf-8"))
    if os.path.isdir(SRC):
        shutil.rmtree(SRC)
    os.makedirs(SRC)
    shutil.copytree(ASSETS, os.path.join(SRC, "assets"))
    open(os.path.join(SRC, "favicon.svg"), "w", encoding="utf-8").write(favicon_svg())
    open(os.path.join(SRC, "index.html"), "w", encoding="utf-8").write(
        page_index(data))
    open(os.path.join(SRC, "404.html"), "w", encoding="utf-8").write(page_404())

    size = sum(os.path.getsize(os.path.join(d, f))
               for d, _, fs in os.walk(SRC) for f in fs)
    print(f"built nymph/ — {size/1024:.0f} KiB, {len(data['games'])} game(s), one page")


if __name__ == "__main__":
    main()
