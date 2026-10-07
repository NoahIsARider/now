# -*- coding: utf-8 -*-
"""
noahisarider — the now page at the root of the sourcehut site.

    python build.py      ->  writes ./site/  (what gets published)

Content lives in data/now.json. Edit that, re-run, done.
When you change something, add a line to "changelog": the newest entry is what the
RSS feed shows as the current state, the older ones stay in the feed as history.
"""
import html
import json
import os
import re
import shutil
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "site")
DATA = os.path.join(ROOT, "data", "now.json")
ASSETS = os.path.join(ROOT, "assets")

SITE_URL = "https://noahisarider.srht.site"
FEED_TITLE = "noahisarider — what I am doing right now"
FEED_DESC = "What I am working on, watching and listening to, updated when it changes."


def e(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def rich(text):
    """inline links only: [label](url) -> <a>"""
    out = e(text)
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', out)


def body_html(now):
    parts = [f'<p class="lead summary">{rich(now["summary"])}</p>']
    for s in now["sections"]:
        if s.get("items"):
            lis = "".join(f"<li>{rich(i)}</li>" for i in s["items"])
            inner = f'<ul class="items">{lis}</ul>'
        else:
            inner = f'<p class="lead">{rich(s.get("body", ""))}</p>'
        parts.append(f'<section>\n  <h2 class="label">{e(s["label"])}</h2>\n  {inner}\n</section>')
    return "\n".join(parts)


def footer_html(now):
    links = "".join(f'<a href="{e(l["href"])}">{e(l["label"])}</a>' for l in now["footer"])
    return f'<footer class="foot">{links}</footer>'


def pretty_date(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    months = ("january", "february", "march", "april", "may", "june", "july",
              "august", "september", "october", "november", "december")
    return f"{d} {months[m - 1]} {y}"


def page_index(now, build_date):
    body = f"""<header class="mast">
  <p class="name">{e(now['name'])}</p>
  <p class="stamp">last updated {e(pretty_date(now['updated']))}</p>
</header>
{body_html(now)}
{footer_html(now)}"""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(now['name'])}</title>
<meta name="description" content="{e(now['summary'])}">
<link rel="canonical" href="{SITE_URL}/">
<link rel="alternate" type="application/rss+xml" title="{e(FEED_TITLE)}" href="{SITE_URL}/feed.xml">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(now['name'])}">
<meta property="og:description" content="{e(now['summary'])}">
<meta property="og:url" content="{SITE_URL}/">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#ffffff">
<meta name="author" content="noahisarider">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<div class="shell">
{body}
</div>
</body>
</html>
"""


def rss_date(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
    days = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
    weekday = days[date(y, m, d).weekday()]
    return f"{weekday}, {d:02d} {months[m - 1]} {y} 12:00:00 +0000"


def page_feed(now, build_date):
    """one item per changelog entry, newest first. the newest carries the full page."""
    current = body_html(now)
    items = []
    for i, entry in enumerate(reversed(now["changelog"])):
        note = entry.get("note", "updated")
        desc = current if i == 0 else f"<p>{e(note)}</p>"
        guid = f"{SITE_URL}/#{entry['date']}"
        items.append(f"""  <item>
    <title>{e(note)}</title>
    <link>{SITE_URL}/</link>
    <guid isPermaLink="false">{e(guid)}</guid>
    <pubDate>{rss_date(entry['date'])}</pubDate>
    <description>{e(desc)}</description>
  </item>""")
    newest = now["changelog"][-1]["date"] if now["changelog"] else now["updated"]
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{e(FEED_TITLE)}</title>
  <link>{SITE_URL}/</link>
  <description>{e(FEED_DESC)}</description>
  <language>en</language>
  <lastBuildDate>{rss_date(newest)}</lastBuildDate>
  <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(items)}
</channel>
</rss>
"""


def favicon():
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
            '<text x="16" y="24" text-anchor="middle" fill="#000"'
            ' font-family="Courier New, monospace" font-size="26" font-weight="bold">n</text>'
            '</svg>')


def main():
    now = json.load(open(DATA, encoding="utf-8"))
    build_date = date.today().isoformat()

    if os.path.isdir(SRC):
        shutil.rmtree(SRC)
    os.makedirs(SRC)
    shutil.copytree(os.path.join(ASSETS, "fonts"), os.path.join(SRC, "assets", "fonts"))
    shutil.copy(os.path.join(ASSETS, "style.css"), os.path.join(SRC, "assets", "style.css"))
    open(os.path.join(SRC, "favicon.svg"), "w", encoding="utf-8").write(favicon())
    open(os.path.join(SRC, "index.html"), "w", encoding="utf-8").write(
        page_index(now, build_date))
    open(os.path.join(SRC, "feed.xml"), "w", encoding="utf-8").write(
        page_feed(now, build_date))
    open(os.path.join(SRC, "robots.txt"), "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    open(os.path.join(SRC, "sitemap.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{SITE_URL}/</loc></url>\n</urlset>\n")

    size = sum(os.path.getsize(os.path.join(d, f))
               for d, _, fs in os.walk(SRC) for f in fs)
    print(f"built site/ — {size/1024:.0f} KiB, updated {now['updated']}, "
          f"{len(now['changelog'])} feed item(s)")


if __name__ == "__main__":
    main()
