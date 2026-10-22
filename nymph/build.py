# -*- coding: utf-8 -*-
"""Build the Nymph blog into ../site/nymph/.

Content model:
  posts/*.md  — one file per post, front matter + markdown body
  about.md    — the about page

Front matter is a small key: value block between two '---' lines:
  title, slug, date (YYYY-MM-DD), category, lede

Run from the root build.py (build_section("nymph")) or directly.
"""
import datetime as dt
import html
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "site", "nymph"))
POSTS_DIR = os.path.join(HERE, "posts")
ABOUT_MD = os.path.join(HERE, "about.md")
ASSETS = os.path.join(HERE, "assets")

SITE_URL = os.environ.get("SITE_URL", "https://noahisarider.srht.site")
BASE = SITE_URL.rstrip("/") + "/nymph"
CONTACT = "noahchou2005@gmail.com"
MARK = "nymph"

MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")
DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


def e(s):
    return html.escape(str(s), quote=True)


def pretty_date(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{MONTHS[m - 1]} {d}, {y}"


def rfc822(iso, hour=9):
    """RFC 822 date, built by hand so %a/%b never follow the system locale."""
    d = dt.date.fromisoformat(iso)
    return (f"{DAYS[d.weekday()]}, {d.day:02d} {MONTHS[d.month - 1][:3]} "
            f"{d.year} {hour:02d}:00:00 +0000")


# --------------------------------------------------------------------------
# front matter + tiny markdown subset

def parse_doc(path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if not m:
        raise ValueError(f"missing front matter: {path}")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, m.group(2).strip()


def inline(text):
    # escape first, then reintroduce trusted tags
    text = e(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  lambda mm: f'<a href="{mm.group(2)}">{mm.group(1)}</a>', text)
    return text


def md_to_html(markdown):
    lines = markdown.replace("\r\n", "\n").split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.strip() == "---":
            out.append("<hr>")
            i += 1
            continue
        hm = re.match(r"^(#{2,4})\s+(.*)$", line)
        if hm:
            level = len(hm.group(1))  # the post title is the page h1
            out.append(f"<h{level}>{inline(hm.group(2))}</h{level}>")
            i += 1
            continue
        if line.startswith("> "):
            buf = []
            while i < len(lines) and lines[i].startswith("> "):
                buf.append(lines[i][2:])
                i += 1
            out.append("<blockquote>" + inline(" ".join(buf)) + "</blockquote>")
            continue
        if line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(f"<li>{inline(lines[i][2:])}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        buf = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not _block_start(lines[i]):
            buf.append(lines[i])
            i += 1
        out.append("<p>" + inline(" ".join(x.strip() for x in buf)) + "</p>")
    return "\n".join(out)


def _block_start(line):
    return bool(re.match(r"^(#{2,4}\s|> |- |---$)", line))


# --------------------------------------------------------------------------
# chrome

def mast(pre):
    return f'''<header class="mast">
  <a class="mark" href="{pre}">nymph</a>
  <p class="stamp">writing by noahisarider</p>
</header>'''


def bar(active, pre):
    """depth 1 = section root (/nymph/), 2 = one level deeper (posts, about)."""
    writing_cls = ' class="on"' if active == "writing" else ""
    about_cls = ' class="on"' if active == "about" else ""
    return f'''<nav class="bar">
  <span class="bar-left">
    <a href="{pre}"{writing_cls}>writing</a>
    <a href="{pre}about/"{about_cls}>about</a>
  </span>
  <span class="bar-right">
    <a href="{pre}feed.xml">rss</a>
    <a href="mailto:{CONTACT}">mail</a>
  </span>
</nav>'''


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


def layout(title, desc, depth, active, body):
    font_pre = ("assets/fonts/" if depth == 1 else "../assets/fonts/")
    css_pre = ("assets/style.css" if depth == 1 else "../assets/style.css")
    fav_pre = ("favicon.svg" if depth == 1 else "../favicon.svg")
    pre = "./" if depth == 1 else "../"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="icon" href="{fav_pre}" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="nymph" href="{pre}feed.xml">
<link rel="stylesheet" href="{font_pre}fonts.css">
<link rel="stylesheet" href="{css_pre}">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#f0fa92" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#1a1a17" media="(prefers-color-scheme: dark)">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
</head>
<body>
<div class="shell">
{mast(pre)}
{bar(active, pre)}
{body}
{footer(depth)}
</div>
</body>
</html>
"""


def lead(doc, link, depth, tag=None, show_date=True):
    """kicker, one big statement, lede. stacked, nothing beside it."""
    kicker = e(tag) if tag is not None else e(doc["category"])
    if show_date:
        kicker += '<span class="sep">/</span>' + pretty_date(doc["date"])
    title = e(doc["title"])
    title_html = (f'<a href="{link}">{title}</a>' if link else title)
    return f'''<section class="lead">
  <p class="kicker">{kicker}</p>
  <h1 class="title">{title_html}</h1>
  <p class="lede">{e(doc.get("lede", ""))}</p>
</section>'''


# --------------------------------------------------------------------------
# pages

def page_index(posts):
    latest = posts[0]
    rest = posts[1:]
    lead_html = lead(latest, f'{latest["slug"]}/', depth=1)
    if rest:
        rows = "\n".join(
            f'''    <li><a href="{p["slug"]}/">
      <span class="row-kicker">{e(p["category"])}<span class="sep">/</span>{pretty_date(p["date"])}</span>
      <span class="row-title">{e(p["title"])}</span>
      <span class="row-lede">{e(p.get("lede", ""))}</span>
    </a></li>'''
            for p in rest)
        earlier = f'''<section class="index">
  <h2 class="label">earlier</h2>
  <ul class="rows">
{rows}
  </ul>
</section>'''
    else:
        earlier = ""
    return layout(f'{MARK} — writing',
                  "Notes on reading, watching, listening, and building.",
                  1, "writing", lead_html + earlier)


def page_post(doc, body_html):
    body = (lead(doc, None, depth=2)
            + f'<article class="prose">{body_html}</article>'
            + '<p class="back"><a href="../">all writing</a></p>')
    return layout(f'{doc["title"]} — {MARK}', doc.get("lede", ""),
                  2, "writing", body)


def page_about(doc, body_html):
    body = (lead(doc, None, depth=2, tag="about", show_date=False)
            + f'<article class="prose">{body_html}</article>'
            + '<p class="back"><a href="../">all writing</a></p>')
    return layout(f'about — {MARK}', doc.get("lede", ""), 2, "about", body)


def page_feed(posts):
    items = []
    for p in posts:
        url = f'{BASE}/{p["slug"]}/'
        items.append(
            "    <item>\n"
            f"      <title>{e(p['title'])}</title>\n"
            f"      <link>{url}</link>\n"
            f"      <guid isPermaLink=\"true\">{url}</guid>\n"
            f"      <pubDate>{rfc822(p['date'])}</pubDate>\n"
            f"      <category>{e(p['category'])}</category>\n"
            f"      <description>{e(p.get('lede', ''))}</description>\n"
            "    </item>")
    now = dt.datetime.now(dt.timezone.utc)
    built = (f"{DAYS[now.weekday()]}, {now.day:02d} "
             f"{MONTHS[now.month - 1][:3]} {now.year} "
             f"{now.hour:02d}:{now.minute:02d}:{now.second:02d} +0000")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>\n'
            f"  <title>nymph</title>\n"
            f"  <link>{BASE}/</link>\n"
            f"  <atom:link href=\"{BASE}/feed.xml\" rel=\"self\" "
            "type=\"application/rss+xml\"/>\n"
            "  <description>writing by noahisarider</description>\n"
            "  <language>en</language>\n"
            f"  <lastBuildDate>{built}</lastBuildDate>\n"
            + "\n".join(items) + "\n</channel></rss>\n")


def page_404():
    body = ('<section class="lead">'
            '<p class="kicker">404</p>'
            '<h1 class="title">Nothing here</h1>'
            '<p class="lede">That note has not been written, or the link is wrong.</p>'
            '</section>'
            '<p class="back"><a href="./">all writing</a></p>')
    return layout(f'404 — {MARK}', "page not found", 1, "writing", body)


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
    if os.path.isdir(SRC):
        shutil.rmtree(SRC)
    os.makedirs(SRC)
    shutil.copytree(ASSETS, os.path.join(SRC, "assets"))
    open(os.path.join(SRC, "favicon.svg"), "w", encoding="utf-8").write(favicon_svg())

    posts = []
    for fn in sorted(os.listdir(POSTS_DIR)):
        if not fn.endswith(".md"):
            continue
        meta, body_md = parse_doc(os.path.join(POSTS_DIR, fn))
        meta.setdefault("slug", fn[:-3])
        meta["body_html"] = md_to_html(body_md)
        posts.append(meta)
    posts.sort(key=lambda p: p["date"], reverse=True)

    os.makedirs(os.path.join(SRC), exist_ok=True)
    open(os.path.join(SRC, "index.html"), "w", encoding="utf-8").write(
        page_index(posts))
    open(os.path.join(SRC, "404.html"), "w", encoding="utf-8").write(page_404())
    open(os.path.join(SRC, "feed.xml"), "w", encoding="utf-8").write(
        page_feed(posts))

    for p in posts:
        d = os.path.join(SRC, p["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(
            page_post(p, p["body_html"]))

    about_meta, about_md = parse_doc(ABOUT_MD)
    ad = os.path.join(SRC, "about")
    os.makedirs(ad, exist_ok=True)
    open(os.path.join(ad, "index.html"), "w", encoding="utf-8").write(
        page_about(about_meta, md_to_html(about_md)))

    size = sum(os.path.getsize(os.path.join(d, f))
               for d, _, fs in os.walk(SRC) for f in fs)
    print(f"built nymph/ — {size/1024:.0f} KiB, {len(posts)} post(s), about")


if __name__ == "__main__":
    main()
