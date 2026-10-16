# -*- coding: utf-8 -*-
"""
MAYDAY site builder, run as part of the merged home site.
    python build.py       ->  writes ../site/MAYDAY/  (published at /MAYDAY/)

Source of truth is data/films.json, which is generated from the Letterboxd export
(see tools/build-films-from-export.py). Ratings and reviews are the author's own.
Design: type, whitespace and blue links. No rules, no boxes, no images.
"""
import html
import json
import os
import shutil
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(ROOT, "..", "site", "MAYDAY"))
DATA = os.path.join(ROOT, "data", "films.json")
ASSETS = os.path.join(ROOT, "assets")

CLEAN_URL = "noahisarider.srht.site/MAYDAY"          # what the links display
SITE_URL = "https://" + CLEAN_URL                   # canonical / og:url
TAGLINE = ("It is said that once a pilot has issued the MAYDAY distress signal three times, "
           "the probability of survival is almost zero.")
REPO = "https://git.sr.ht/~noahisarider/now/tree/master/item/mayday"
LETTERBOXD = "https://letterboxd.com/noahisarider/"


def e(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def soft(url):
    """display text for a url, with <wbr> after each slash so narrow screens break it at
    the separators. <wbr> is markup, not a character, so a copied url stays clean."""
    return e(url).replace("/", "/<wbr>")


def stars(rating):
    if rating is None:
        return ""
    n = int(rating)
    half = "½" if (rating - n) >= 0.5 else ""
    return "★" * n + half


def status(f):
    """what to print where the score goes: stars, or 'liked', or nothing at all"""
    if f["rating"]:
        return stars(f["rating"])
    return "liked" if f.get("liked") else ""


def exposed(url):
    """the link text: the address as you would read it out loud, without the scheme"""
    return soft(url.replace("https://", ""))


def paras(text):
    """a blank line in a review is a paragraph break"""
    if not text:
        return []
    norm = text.replace(chr(13) + chr(10), chr(10)).replace(chr(13), chr(10))
    return [c.strip() for c in norm.split(chr(10) + chr(10)) if c.strip()]


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
<meta name="theme-color" content="#ffffff">
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
  <p class="signal">MAYDAY MAYDAY MAYDAY</p>
  <ul>
    <li><a href="{p}">the manifest</a></li>
    <li><a href="{p}about/">about this list</a></li>
    <li><a href="/">now</a></li>
    <li><a href="/shkb/">records</a></li>
    <li><a href="{e(REPO)}">source repository</a></li>
  </ul>
  <p class="meta">compiled by <a href="{e(LETTERBOXD)}" rel="me">noahisarider</a> · film data from
  Letterboxd and Wikidata · built {date.today().isoformat()} · no cookies, no trackers</p>
</footer>"""


def masthead(films, profile):
    rated = [f for f in films if f["rating"]]
    years = sorted(f["year"] for f in films)
    return f"""<header class="mast">
  <h1 class="mark">MAYDAY</h1>
  <p class="quote">{e(TAGLINE)}</p>
  <p class="stats">{len(films)} films on the list. {len(rated)} I have rated,
  {sum(1 for f in films if f['rating'] == 5)} of them five stars, and
  {sum(1 for f in films if f['review'])} I wrote something about. {years[0]} to {years[-1]}.</p>
</header>"""


def page_index(films, profile, ratings):
    entries = []
    for f in films:
        hay = " ".join(filter(None, [f["title"], str(f["year"]), f.get("director"),
                                     f.get("country"), f.get("review")]))
        meta = " · ".join(filter(None, [
            status(f),
            f.get("director"),
            f.get("country"),
            f"{f['runtime']} min" if f.get("runtime") else None,
        ]))
        review = ""
        if f.get("review"):
            ps = "".join(f"<p>{e(p)}</p>" for p in paras(f["review"]))
            review = f'      <blockquote class="review">{ps}</blockquote>\n'
        lb = f.get("letterboxd_url")
        link = (f'<a class="url" href="{e(lb)}" rel="noopener">{exposed(lb)}</a>'
                if lb else "")
        entries.append(f"""  <li class="entry" data-rating="{f['rating'] if f['rating'] is not None else ''}"
      data-liked="{'1' if f['liked'] else '0'}" data-hay="{e(hay)}">
    <div class="no">{f['n']:02d}</div>
    <div>
      <div class="head">
        <span class="name">{e(f['title'])}
          <span class="year">{f['year']}</span></span>
        {link}
      </div>
      <div class="meta">{e(meta)}</div>
{review}    </div>
  </li>""")

    chips = "".join(
        f'<button class="chip" type="button" data-rating="{r}" aria-pressed="false">'
        f'{stars(r)}</button>' for r in ratings)
    body = masthead(films, profile) + f"""
<section class="controls">
  <label class="field"><span class="lab">search</span>
    <input id="q" type="search" autocomplete="off"
           placeholder="title, director, country, or words from a review"
           aria-label="Search films"></label>
  <p class="chips" id="chips"><span class="lab">rating</span>{chips}
    <button class="chip" type="button" data-liked="1" aria-pressed="false">liked</button></p>
</section>
<p class="count" id="count">showing {len(films)} of {len(films)} films</p>
<ol class="entries">
{chr(10).join(entries)}
</ol>
<p class="empty" id="empty" hidden>Nothing here answers to that. Try fewer words, or clear
the filters.</p>
<script src="assets/app.js" defer></script>
{footer('./')}"""
    return layout(title="MAYDAY — a films manifest",
                  desc=("Every film I have rated, with what I wrote about it. "
                        + TAGLINE),
                  p="./", path="", body=body)


def page_about(films, profile, ratings):
    rated = [f for f in films if f["rating"]]
    five = sum(1 for f in films if f["rating"] == 5)
    reviews = sum(1 for f in films if f["review"])
    liked_only = sum(1 for f in films if f["rating"] is None and f.get("liked"))
    reviewed_only = sum(1 for f in films
                        if f["rating"] is None and not f.get("liked") and f.get("review"))
    body = f"""<p class="top"><a href="../">← the manifest</a><span class="selfurl">about</span></p>
<div class="doc">
  <section>
    <h2>What this is</h2>
    <p>{len(rated)} films I have rated, {five} of them five stars, {liked_only} I liked without
       leaving a score, and {reviewed_only} I wrote about without scoring at all.
       {e(TAGLINE)}</p>
    <p>{e(profile['bio'])}</p>
  </section>
  <section>
    <h2>How a film gets in</h2>
    <ul>
      <li>I watched it and gave it a score, or liked it without one.</li>
      <li>I can say in one sentence what it does to a person, and {reviews} of these I have.</li>
      <li>I would still recommend it to someone who does not share my taste.</li>
    </ul>
    <p>Everything on this site comes out of my own Letterboxd log, which is where the rest of
       what I have watched stays.</p>
  </section>
  <section>
    <h2>Reading it</h2>
    <ul>
      <li>the number — position on the list, highest rated first</li>
      <li>the stars — my own score: {stars(5)}, {stars(4.5)}, {stars(4)}, {stars(3.5)}, {stars(3)}</li>
      <li><span class="k">liked</span> — liked on Letterboxd without giving it a score</li>
      <li>the blue address on each line — that film's page on Letterboxd, spelled out</li>
    </ul>
  </section>
  <section>
    <h2>About the site</h2>
    <p>One column of type, no rules, no boxes, no images, and no colour except the links, which
       are blue because that is what links are. It is a static page built from a single JSON file
       and published on sourcehut pages. The fonts are served from this domain, so loading a page
       asks nobody else for anything.</p>
    <p>Film metadata (director, country, length) is matched against Wikidata and left blank when
       there is no clean match, rather than guessed. The scores and the notes are mine, which is to
       say they are opinions, and you are allowed to disagree with them loudly. A few notes were
       written in Chinese and are translated here, with the originals kept in films.json.</p>
  </section>
  <section>
    <h2>Where to find things</h2>
    <ul>
      <li><a href="{e(LETTERBOXD)}">Letterboxd</a> — everything I have watched</li>
      <li><a href="{e(REPO)}">Source repository</a> — this site, and the list as one JSON file</li>
      <li><a href="films.json">films.json</a> — the whole manifest, machine-readable</li>
    </ul>
  </section>
</div>
{footer('../')}"""
    return layout(title="About — MAYDAY",
                  desc="What this films manifest is, how a film gets on it, and how the site is built.",
                  p="../", path="about/", body=body)


def page_404(films, profile, ratings):
    body = f"""<p class="top"><a href="/MAYDAY/">← the manifest</a><span class="selfurl">404</span></p>
<div class="doc">
  <section>
    <h2>Nothing at this address</h2>
    <p>The page you asked for is not on the manifest. Check the spelling, or go back to the list.</p>
    <p><a href="/MAYDAY/">the manifest</a></p>
  </section>
</div>
""" + footer("/MAYDAY/")
    return layout(title="404 — MAYDAY", desc="Page not found.", p="/MAYDAY/",
                  path="404.html", body=body, indexable=False)


def main():
    data = json.load(open(DATA, encoding="utf-8"))
    films, profile, ratings = data["films"], data["profile"], data["ratings"]

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

    w("index.html", page_index(films, profile, ratings))
    w("about/index.html", page_about(films, profile, ratings))
    w("404.html", page_404(films, profile, ratings))

    urls = [f"{SITE_URL}/", f"{SITE_URL}/about/"]
    w("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      "".join(f"  <url><loc>{e(u)}</loc></url>\n" for u in urls) + "</urlset>\n")
    w("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    # the published data file keeps every field except the Chinese originals: the site
    # itself is all english, and review_zh is kept in the repository, not on the web.
    public = json.loads(json.dumps(data))
    for f in public["films"]:
        f.pop("review_zh", None)
    w("films.json", json.dumps(public, ensure_ascii=False, indent=1) + "\n")

    pages = sum(len(fs) for _, _, fs in os.walk(SRC))
    size = sum(os.path.getsize(os.path.join(d, f))
               for d, _, fs in os.walk(SRC) for f in fs)
    print(f"built {pages} files, {size/1024:.0f} KiB into {SRC} "
          f"({len(films)} films on one page, {sum(1 for f in films if f.get('review'))} reviews, "
          f"index + about only)")


if __name__ == "__main__":
    main()
