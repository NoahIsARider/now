# -*- coding: utf-8 -*-
"""
MAYDAY site builder.
    python build.py          ->  writes ./site/  (the directory that gets published)

Source of truth is data/films.json. Edit that, re-run, done.
Design rule: type, whitespace and blue links. No rules, no boxes, no images.
"""
import html
import json
import os
import shutil
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "site")
DATA = os.path.join(ROOT, "data", "films.json")
ASSETS = os.path.join(ROOT, "assets")

# where the site lives. change this if you publish it somewhere else.
SITE_URL = "https://noahisarider.srht.site/MAYDAY"
TAGLINE = ("It is said that once a pilot has issued the MAYDAY distress signal three times, "
           "the probability of survival is almost zero.")
REPO = "https://sr.ht/~noahisarider/MAYDAY/"
LETTERBOXD = "https://letterboxd.com/noahisarider/"


def e(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def stars(rating):
    if not rating:
        return "not rated"
    return "★" * int(rating) + "·" * (5 - int(rating))


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
    <li><a href="{e(REPO)}">source repository</a></li>
  </ul>
  <p class="meta">compiled by <a href="{e(LETTERBOXD)}" rel="me">noahisarider</a> · film data from
  Letterboxd and Wikidata · built {date.today().isoformat()} · no cookies, no trackers</p>
</footer>"""


def masthead(films, moods):
    years = sorted(f["year"] for f in films if f["year"])
    five = sum(1 for f in films if f["rating"] == 5)
    rated = sum(1 for f in films if f["rating"])
    return f"""<header class="mast">
  <h1 class="mark">MAYDAY</h1>
  <p class="quote">{e(TAGLINE)}</p>
  <p class="stats">{len(films)} films, {five} of them with five stars, {len(moods)} moods to filter
  by, {years[0]} to {years[-1]}. {rated} are rated, the rest I logged without leaving a verdict.</p>
</header>"""


def page_index(films, moods):
    entries = []
    for f in films:
        hay = " ".join(filter(None, [f["title"], str(f["year"]), f["director"],
                                     f["country"], " ".join(f["tags"]), f["lead"]]))
        entries.append(f"""  <li class="entry" data-tags="{' '.join(f['tags'])}" data-hay="{e(hay)}">
    <div class="no">{f['n']:02d}</div>
    <div>
      <div class="title"><a href="film/{f['slug']}/">{e(f['title'])}</a>
        <span class="year">{f['year']}</span></div>
      <div class="meta">{e(f['director'] or '')} · {e(' · '.join(f['tags']))} ·
        <span class="stars">{e(stars(f['rating']))}</span></div>
      <div class="lead">{e(f['lead'])}</div>
    </div>
  </li>""")

    body = masthead(films, moods) + f"""
<section class="controls">
  <label class="field"><span class="lab">search the manifest</span>
    <input id="q" type="search" autocomplete="off"
           placeholder="title, director, country, mood" aria-label="Search films"></label>
  <p class="chips" id="chips"><span class="lab">mood:</span></p>
</section>
<p class="count" id="count">showing {len(films)} of {len(films)} films</p>
<ol class="entries">
{chr(10).join(entries)}
</ol>
<p class="empty" id="empty" hidden>Nothing here answers to that. Try fewer words, or clear the mood.</p>
<script id="films-data" type="application/json">{json.dumps({'moods': moods, 'count': len(films)})}</script>
<script src="assets/app.js" defer></script>
{footer('./')}"""
    return layout(title="MAYDAY — a films manifest",
                  desc=("A short, opinionated manifest of films: what to watch, who made it, "
                        "what it will do to you. " + TAGLINE),
                  p="./", path="", body=body)


def page_film(f, films, moods):
    i = films.index(f)
    prev_f = films[i - 1] if i > 0 else None
    next_f = films[i + 1] if i < len(films) - 1 else None

    meta = " · ".join(str(x) for x in [f["year"], f["country"], f"{f['runtime']} min"] if x)
    byline = f"directed by {e(f['director'] or '—')}"
    if f["tags"]:
        byline += f" · {e(' · '.join(f['tags']))}"
    if f["letterboxd"]:
        byline += f' · <a href="{e(f["letterboxd"])}" rel="noopener">on Letterboxd</a>'

    nav = []
    if prev_f:
        nav.append(f'previous <a href="../{prev_f["slug"]}/">{e(prev_f["title"])} '
                   f'{prev_f["year"]}</a>')
    if next_f:
        nav.append(f'next <a href="../{next_f["slug"]}/">{e(next_f["title"])} '
                   f'{next_f["year"]}</a>')
    if not nav:
        nav.append("the end of the manifest")

    body = f"""<p class="top"><a href="../../">← the manifest</a>
  <span>{f['n']:02d} of {len(films):02d}</span></p>
<h1 class="title">{e(f['title'])}</h1>
<p class="lead">{e(f['lead'])}</p>
<p class="film-meta">{e(meta)} · <span class="stars">{e(stars(f['rating']))}</span></p>
<p class="byline">{byline}</p>
<p class="note note-drop">{e(f['note'])}</p>
<p class="pager">{' · '.join(nav)}</p>
{footer('../../')}"""
    return layout(title=f"{f['title']} ({f['year']}) — MAYDAY",
                  desc=f"{f['title']} ({f['year']}), directed by {f['director']}. {f['lead']}",
                  p="../../", path=f"film/{f['slug']}/", body=body)


def page_about(films, moods):
    body = f"""<p class="top"><a href="../">← the manifest</a><span>about</span></p>
<div class="doc">
  <section>
    <h2>What this is</h2>
    <p>A list of films I would hand to someone with no other information about them.
       {e(TAGLINE)}</p>
    <p>It is not a canon, and it is not finished. It is what I have actually watched and would
       defend, with the length and the mood written next to it so you can pick by what you can
       stand to feel tonight.</p>
  </section>
  <section>
    <h2>How a film gets in</h2>
    <ul>
      <li>I watched it and it stayed with me for longer than the week.</li>
      <li>I can say in one sentence what it does to a person.</li>
      <li>I would still recommend it to someone who does not share my taste.</li>
    </ul>
    <p>Everything here comes from my Letterboxd log, where the five-star entries are the spine of
       the list. Films I logged but never rated sit at the bottom, marked
       <span class="k">not rated</span>.</p>
  </section>
  <section>
    <h2>Reading it</h2>
    <ul>
      <li>the number — position, nothing more</li>
      <li>the moods — {e(', '.join(moods))}. A film carries two, at most</li>
      <li>the stars — my own value from Letterboxd, not a score out of ten</li>
    </ul>
  </section>
  <section>
    <h2>About the site</h2>
    <p>One column of type, no rules, no boxes, no images, and no colour except the links, which are
       blue because that is what links are. It is a static page built from a single JSON file and
       published on sourcehut pages. The fonts are served from this domain, so loading a page asks
       nobody else for anything.</p>
    <p>The verdicts and the notes are mine, which is to say they are opinions, and you are allowed
       to disagree with them loudly.</p>
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


def page_404(films, moods):
    body = """<p class="top"><a href="/MAYDAY/">← the manifest</a><span>404</span></p>
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


def favicon():
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
            '<rect width="32" height="32" fill="#fff"/>'
            '<text x="16" y="24" text-anchor="middle" fill="#000"'
            ' font-family="Courier New, monospace" font-size="26" font-weight="bold">M</text>'
            '</svg>')


def main():
    data = json.load(open(DATA, encoding="utf-8"))
    films, moods = data["films"], data["moods"]

    if os.path.isdir(SRC):
        shutil.rmtree(SRC)
    os.makedirs(os.path.join(SRC, "film"), exist_ok=True)

    shutil.copytree(os.path.join(ASSETS, "fonts"), os.path.join(SRC, "assets", "fonts"))
    for f in ("style.css", "app.js"):
        shutil.copy(os.path.join(ASSETS, f), os.path.join(SRC, "assets", f))
    open(os.path.join(SRC, "favicon.svg"), "w", encoding="utf-8").write(favicon())

    def w(path, text):
        full = os.path.join(SRC, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "w", encoding="utf-8").write(text)

    w("index.html", page_index(films, moods))
    for f in films:
        w(f"film/{f['slug']}/index.html", page_film(f, films, moods))
    w("about/index.html", page_about(films, moods))
    w("404.html", page_404(films, moods))

    urls = [f"{SITE_URL}/", f"{SITE_URL}/about/"] + \
           [f"{SITE_URL}/film/{f['slug']}/" for f in films]
    w("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      "".join(f"  <url><loc>{e(u)}</loc></url>\n" for u in urls) + "</urlset>\n")
    w("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    w("films.json", json.dumps(data, ensure_ascii=False, indent=1) + "\n")

    pages = sum(len(fs) for _, _, fs in os.walk(SRC))
    size = sum(os.path.getsize(os.path.join(d, f))
               for d, _, fs in os.walk(SRC) for f in fs)
    print(f"built {pages} files, {size/1024:.0f} KiB into {SRC}")


if __name__ == "__main__":
    main()
