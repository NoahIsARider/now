# -*- coding: utf-8 -*-
"""
babel site builder.
    python build.py       ->  writes ../site/babel/  (published at /babel/)

Source of truth is data/books.json, generated from the Goodreads export
(see tools/build-books-from-goodreads.py). Design: blackletter density,
the only light is the gilded mark and the book titles. See DESIGN.md.
"""
import html
import json
import os
import shutil
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(ROOT, "..", "site", "babel"))
DATA = os.path.join(ROOT, "data", "books.json")
ASSETS = os.path.join(ROOT, "..", "assets")
# Courier Prime fonts live under MAYDAY/assets/fonts (shared with MAYDAY and shkb)
CP_FONTS = os.path.normpath(os.path.join(ROOT, "..", "mayday", "assets", "fonts"))

_BASE = os.environ.get("SITE_URL", "https://noahisarider.srht.site").rstrip("/")
SITE_URL = _BASE + "/babel"

MARK = "BABEL"


def e(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def layout(*, title, desc, p, body):
    url = f"{SITE_URL}/"
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
<meta name="theme-color" content="#faf9f6">
<meta name="author" content="noahisarider">
<link rel="icon" href="{p}favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{p}assets/style.css">
<link rel="stylesheet" href="{p}assets/fonts/fonts.css">
</head>
<body>
<div class="shell">
{body}
</div>
</body>
</html>
"""


def footer(p):
    home_root = "../" if p == "" else ("../" * p.count("/"))
    parent = home_root + ""
    return (f'<footer class="foot">'
            f'<a href="{parent}">now</a>'
            f'<a href="{parent}MAYDAY/">films</a>'
            f'<a href="{parent}shkb/">records</a>'
            f'<br>'
            f'<a href="https://www.goodreads.com/ratkingsyndrome">goodreads</a>'
            f'<a href="https://record.club/noahisarider">record.club</a>'
            f'<a href="https://sr.ht/~noahisarider/">sr.ht</a>'
            f'</footer>')


def page_index(data, build_date):
    counts = data["counts"]
    total = counts["total"]

    def entry(b):
        title_html = (f'<a href="{e(b["url"])}" class="btitle">{e(b["title"])}</a>'
                      if b.get("url")
                      else f'<span class="btitle">{e(b["title"])}</span>')
        stars_html = f'<span class="stars">{e(b.get("stars") or "")}</span>'
        meta_parts = []
        if b.get("author"):
            meta_parts.append(e(b["author"]))
        if b.get("year"):
            meta_parts.append(str(b["year"]))
        meta_html = " · ".join(meta_parts)
        return (f'<div class="row"><span class="n">{b["n"]}</span><div class="col">'
                f'<div class="title-line">{title_html}{stars_html}</div>'
                f'{(f"<div class=\"meta\">{meta_html}</div>" if meta_html else "")}'
                f'</div></div>')

    rows_html = "\n".join(entry(b) for b in data["books"])

    body = f"""
<header class="mast">
  <p class="mark">{MARK}</p>
  <p class="stamp">{counts["read"]} read, {counts["rated"]} rated, {counts["year_min"]}..{counts["year_max"]}</p>
</header>
<div id="list" class="list">{rows_html}</div>
{footer("")}
"""
    return layout(title="babel — books", desc=f"{total} books read", p="", body=body)


def page_sitemap():
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"  <url><loc>{SITE_URL}/</loc></url>\n"
            '</urlset>\n')


def page_robots():
    return f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"


def favicon_svg():
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
            '<rect width="32" height="32" fill="#faf9f6"/>'
            '<text x="16" y="26" text-anchor="middle" fill="#1a1a1a"'
            ' font-family="UnifrakturMaguntia, serif" font-size="28" font-weight="400">B</text>'
            '</svg>')


def main():
    data = json.load(open(DATA, encoding="utf-8"))

    if os.path.isdir(SRC):
        shutil.rmtree(SRC)
    os.makedirs(os.path.join(SRC, "assets", "fonts"))
    shutil.copy(os.path.join(ROOT, "assets", "style.css"),
                os.path.join(SRC, "assets", "style.css"))
    shutil.copy(os.path.join(ROOT, "assets", "fonts", "fonts.css"),
                os.path.join(SRC, "assets", "fonts", "fonts.css"))
    shutil.copy(os.path.join(ROOT, "assets", "fonts", "unifrakturmaguntia-regular.woff2"),
                os.path.join(SRC, "assets", "fonts", "unifrakturmaguntia-regular.woff2"))
    # also copy the Courier Prime fonts from MAYDAY so babel doesn't need its own copy
    for name in ("courierprime-400.woff2", "courierprime-700.woff2"):
        shutil.copy(os.path.join(CP_FONTS, name),
                    os.path.join(SRC, "assets", "fonts", name))
    shutil.copy(os.path.join(CP_FONTS, "LICENSE"),
                os.path.join(SRC, "assets", "fonts", "LICENSE"))

    open(os.path.join(SRC, "index.html"), "w", encoding="utf-8").write(
        page_index(data, date.today().isoformat()))
    open(os.path.join(SRC, "sitemap.xml"), "w", encoding="utf-8").write(page_sitemap())
    open(os.path.join(SRC, "robots.txt"), "w", encoding="utf-8").write(page_robots())
    open(os.path.join(SRC, "favicon.svg"), "w", encoding="utf-8").write(favicon_svg())

    size = sum(os.path.getsize(os.path.join(d, f))
               for d, _, fs in os.walk(SRC) for f in fs)
    c = data["counts"]
    print(f"built babel/ — {size/1024:.0f} KiB, {c['total']} books, {c['rated']} rated ({c['five']}×5 {c['four']}×4 {c['three']}×3)")


if __name__ == "__main__":
    main()
