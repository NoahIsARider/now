# -*- coding: utf-8 -*-
"""
MAYDAY site builder.
    python build.py          ->  writes ./site/  (the directory that gets published)

Source of truth is data/films.json. Edit that, re-run, done.
"""
import html
import json
import os
import re
import shutil
import unicodedata
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "site")
DATA = os.path.join(ROOT, "data", "films.json")
ASSETS = os.path.join(ROOT, "assets")

# where the site will live. change this if you publish it somewhere else.
SITE_URL = "https://noahisarider.srht.site/MAYDAY"
SITE_NAME = "MAYDAY"
TAGLINE = ("It is said that once a pilot has issued the MAYDAY distress signal three times, "
           "the probability of survival is almost zero.")
REPO = "https://sr.ht/~noahisarider/MAYDAY/"
LETTERBOXD = "https://letterboxd.com/noahisarider/"

MORSE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.',
    'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.',
    'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-',
    'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..',
}


def e(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def morse(text):
    return [MORSE[c] for c in text.upper() if c in MORSE]


def beacon_svg(word="MAYDAY"):
    """A distress call drawn with straight line segments only: a square wave."""
    unit = 9.0
    y_hi, y_lo = 20.0, 62.0
    x = 0.0
    pts = []
    for gi, group in enumerate(morse(word)):
        if gi:
            x += unit * 3  # letter gap
            pts.append((x, y_lo))
            x += 0
        for si, sym in enumerate(group):
            if si:
                pts.append((x, y_lo))
                x += unit  # symbol gap
            pts.append((x, y_hi))
            x += unit * (3 if sym == '-' else 1)
            pts.append((x, y_hi))
            pts.append((x, y_lo))
    width = x
    d = " ".join(f"{'M' if i == 0 else 'L'}{px:.1f},{py:.1f}"
                 for i, (px, py) in enumerate(pts))
    codex = " / ".join("".join("·" if c == "." else "—" for c in g) for g in morse(word))
    return (
        f'<svg viewBox="0 0 {width:.1f} 74" preserveAspectRatio="none" role="img" '
        f'aria-label="the word {word} in Morse code">'
        f'<path d="{d}" fill="none" stroke="#000" stroke-width="1.5" '
        f'vector-effect="non-scaling-stroke"/></svg>'
        f'<div class="codex">{e(word)} &nbsp; {e(codex)}</div>'
    )


def stars(rating):
    if not rating:
        return "NOT RATED"
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
<div class="hazard"></div>
{body}
<div class="hazard"></div>
</div>
</body>
</html>
"""


def footer(p):
    return f"""<footer class="foot">
<div class="foot__row">
  <div>
    <div class="signal">MAYDAY MAYDAY MAYDAY</div>
    <div class="meta">{e(TAGLINE)}</div>
  </div>
  <div>
    <ul>
      <li><a href="{p}">The manifest</a></li>
      <li><a href="{p}about/">About this list</a></li>
      <li><a href="{e(REPO)}">Source repository</a></li>
    </ul>
  </div>
  <div>
    <ul>
      <li>compiled by <a href="{e(LETTERBOXD)}" rel="me">noahisarider</a></li>
      <li>film data from Letterboxd and Wikidata</li>
      <li class="meta">built {date.today().isoformat()} · no cookies, no trackers</li>
    </ul>
  </div>
</div>
</footer>"""


def header(extra=""):
    return f"""<header class="mast">
  <h1 class="mark">MAYDAY<span class="cursor" aria-hidden="true"></span></h1>
  <p class="quote"><b>DISTRESS CALL, THREE TIMES · </b>{e(TAGLINE)}</p>
  <div>{extra}</div>
</header>"""


def stats_html(films, moods):
    years = sorted(f["year"] for f in films if f["year"])
    rated = [f for f in films if f["rating"]]
    return f"""<ul class="stats">
  <li><span>Films</span>{len(films)}</li>
  <li><span>Five stars</span>{sum(1 for f in films if f['rating'] == 5)}</li>
  <li><span>Moods</span>{len(moods)}</li>
  <li><span>Years</span>{years[0]}–{years[-1]}</li>
</ul>"""


def page_index(films, moods):
    rows = []
    for f in films:
        hay = " ".join(filter(None, [f["title"], str(f["year"]), f["director"],
                                     f["country"], " ".join(f["tags"]), f["lead"]]))
        rows.append(f"""<tr data-tags="{' '.join(f['tags'])}" data-hay="{e(hay)}">
  <td class="col-no filmno">{f['n']:02d}</td>
  <td class="col-title"><div class="filmtitle"><a href="film/{f['slug']}/">{e(f['title'])}</a></div>
      <div class="filmyear">{f['year']}</div></td>
  <td class="col-dir">{e(f['director'] or '—')}</td>
  <td class="col-mood moods">{e(' · '.join(f['tags']))}</td>
  <td class="col-star stars">{e(stars(f['rating']))}</td>
</tr>""")

    body = header(stats_html(films, moods)) + f"""
<div class="hazard"></div>
<section class="controls">
  <label class="field"><span>SEARCH THE MANIFEST</span>
    <input id="q" type="search" autocomplete="off" placeholder="title, director, country, mood" aria-label="Search films"></label>
  <div class="chips" id="chips"><span class="label">MOOD</span></div>
</section>
<div class="count" id="count">SHOWING {len(films)} / {len(films)} FILMS</div>
<table class="manifest">
  <thead><tr><th class="col-no">№</th><th>FILM</th><th class="col-dir">DIRECTOR</th>
  <th class="col-mood">MOOD</th><th class="col-star">RATING</th></tr></thead>
  <tbody>
{chr(10).join(rows)}
  </tbody>
</table>
<div class="empty" id="empty" hidden>Nothing on the manifest answers to that. Try fewer words, or clear the mood filters.</div>
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

    facts = [
        ("Director", e(f["director"] or "—")),
        ("Country", e(f["country"] or "—")),
        ("Running time", f"{f['runtime']} min"),
        ("Mood", e(" · ".join(f["tags"]))),
        ("Rating", f"{e(stars(f['rating']))} <span>({'Letterboxd' if f['rating'] else 'not rated yet'})</span>"),
    ]
    if f["letterboxd"]:
        facts.append(("On Letterboxd", f'<a href="{e(f["letterboxd"])}" rel="noopener">the log entry</a>'))
    facts.append(("Position", f"{f['n']:02d} of {len(films):02d}"))

    body = f"""<div class="sheet__bar">
  <a href="../../">← MANIFEST</a><span>{f['n']:02d} / {len(films):02d}</span>
</div>
<div class="sheet__head">
  <div>
    <h1 class="sheet__title">{e(f['title'])}</h1>
    <p class="sheet__lead">{e(f['lead'])}</p>
  </div>
  <div><ul class="facts">
{chr(10).join(f'    <li><b>{k}</b><span>{v}</span></li>' for k, v in facts)}
  </ul></div>
</div>
<div class="sheet__body">
  <p class="note-drop">{e(f['note'])}</p>
</div>
<div class="beacon">{beacon_svg()}</div>
<nav class="pager">
  <div><span>PREVIOUS</span>{('<a href="../' + prev_f['slug'] + '/">' + e(prev_f['title']) + ' ' + str(prev_f['year']) + '</a>') if prev_f else '<span class="none">start of the manifest</span>'}</div>
  <div><span>NEXT</span>{('<a href="../' + next_f['slug'] + '/">' + e(next_f['title']) + ' ' + str(next_f['year']) + '</a>') if next_f else '<span class="none">end of the manifest</span>'}</div>
</nav>
{footer('../../')}"""
    return layout(title=f"{f['title']} ({f['year']}) — MAYDAY",
                  desc=f"{f['title']} ({f['year']}), directed by {f['director']}. {f['lead']}",
                  p="../../", path=f"film/{f['slug']}/", body=body)


def page_about(films, moods):
    body = f"""<div class="sheet__bar"><a href="./">← MANIFEST</a><span>ABOUT</span></div>
<div class="doc">
  <section>
    <h2>What this is</h2>
    <p>A list of films I would hand to someone with no other information about them. {e(TAGLINE)}</p>
    <p>It is not a canon, it is not ranked by importance, and it is not finished. It is what I have
       actually watched and would defend, with the length and the mood written next to it so you can
       pick by what you can stand to feel tonight.</p>
  </section>
  <section>
    <h2>How a film gets in</h2>
    <ul>
      <li>I watched it and it stayed with me for longer than the week.</li>
      <li>I can say in one sentence what it does to a person.</li>
      <li>I would still recommend it to someone who does not share my taste.</li>
    </ul>
    <p>Everything here is drawn from my Letterboxd log, where the five-star entries are the spine of
       the list. Films logged but not yet rated sit at the bottom of the manifest and are marked
       <span class="k">not rated</span>.</p>
  </section>
  <section>
    <h2>Reading the manifest</h2>
    <ul>
      <li><span class="k">№</span> — position, nothing more.</li>
      <li><span class="k">Mood</span> — {e(', '.join(moods))}. A film carries two, at most.</li>
      <li><span class="k">Rating</span> — my own star value from Letterboxd, not a score out of ten.</li>
      <li><span class="k">The beacon</span> — the distress call, spelled in Morse and drawn with
          straight lines, on every film page.</li>
    </ul>
  </section>
  <section>
    <h2>About the site</h2>
    <p>Two typefaces, one black rule, no colour, no images, no tracking, no cookies. It is a static
       page built from a single JSON file and published on sourcehut pages. The font files are served
       from this domain, so loading a page makes no requests to anybody else.</p>
    <p>Film metadata comes from Letterboxd and Wikidata. The one-line verdicts and the notes are mine,
       which is to say they are opinions and you are allowed to disagree with them loudly.</p>
  </section>
  <section>
    <h2>Where to find things</h2>
    <ul>
      <li><a href="{e(LETTERBOXD)}">Letterboxd</a> — everything I have watched</li>
      <li><a href="{e(REPO)}">Source repository</a> — the list itself, as one JSON file</li>
      <li><a href="films.json">films.json</a> — the whole manifest, machine-readable</li>
    </ul>
  </section>
</div>
{footer('../')}"""
    return layout(title="About — MAYDAY",
                  desc="What this films manifest is, how a film gets on it, and how the site is built.",
                  p="../", path="about/", body=body)


def page_404(films, moods):
    body = """<div class="sheet__bar"><a href="/MAYDAY/">← MANIFEST</a><span>404</span></div>
<div class="doc">
  <section>
    <h2>Nothing at this address</h2>
    <p>The page you asked for is not on the manifest. Check the spelling, or go back to the index.</p>
    <p><a href="/MAYDAY/">Return to the manifest</a></p>
  </section>
</div>
""" + footer("/MAYDAY/")
    return layout(title="404 — MAYDAY", desc="Page not found.", p="/MAYDAY/",
                  path="404.html", body=body, indexable=False)


def favicon():
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
            '<rect width="32" height="32" fill="#fff"/>'
            '<g fill="none" stroke="#000" stroke-width="2">'
            '<path d="M2 27V5l11 14L24 5v22"/><path d="M2 30h28"/></g></svg>')


def main():
    data = json.load(open(DATA, encoding="utf-8"))
    films, moods = data["films"], data["moods"]

    if os.path.isdir(SRC):
        shutil.rmtree(SRC)
    os.makedirs(os.path.join(SRC, "film"), exist_ok=True)

    # assets
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
    print("  index.html")
    for f in films:
        print(f"  film/{f['slug']}/")
    print("  about/  404.html  sitemap.xml  robots.txt  films.json")


if __name__ == "__main__":
    main()
