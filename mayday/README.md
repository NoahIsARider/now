# MAYDAY

A films manifest. Type, whitespace and blue links. No rules, no boxes, no images.

> It is said that once a pilot has issued the MAYDAY distress signal three times,
> the probability of survival is almost zero.

Live at <https://noahisarider.srht.site/MAYDAY/>: every film the author has rated on
Letterboxd (106 of them: 85 rated, 20 liked without a score, 1 he only wrote about), with
his own score, his own review where he wrote one, and each film's Letterboxd address
spelled out as the only link on the line. Two pages in total, the manifest and an about.

## Layout

This directory is the `mayday/` subtree of the home site repository
(<https://git.sr.ht/~noahisarider/now>). It was its own repository until 2026-10-16, so its
full earlier history is in the same git log.

```
data/films.json                    the whole list. the only file you edit by hand.
data/reviews-en.json               english renderings of the reviews written in chinese
tools/build-films-from-export.py   rebuilds films.json from a Letterboxd export (+ Wikidata)
tools/resolve-letterboxd-links.py  turns the export's boxd.it links into letterboxd.com/film/...
tools/token-window.py              one-field local page for re-entering an expired token
build.py                           reads the json, writes ../site/MAYDAY/
assets/style.css                   all of the design
assets/app.js                      search + rating filter, no dependencies
assets/favicon.svg                 the letter M cut out of Special Elite, as a path
assets/fonts/                      Special Elite + Courier Prime, self-hosted, OFL 1.1
```

The published output lands in `../site/MAYDAY/`, which the root `build.py` creates. Nothing is
published from this directory on its own any more.

The blue address at the end of each line is that film on Letterboxd, and it is the only link
on the line. There are no per-film pages any more: the review, the score and the credits all
sit on the manifest itself. Every review is published in English. The Chinese originals stay
in `data/films.json` as `review_zh` and are stripped from the published `films.json`, so no
Chinese is served.

## Rebuilding the list from Letterboxd

Export from Letterboxd (Settings → Data → Export your data), then, from the repository root:

```sh
python mayday/tools/build-films-from-export.py ~/Downloads/letterboxd-<user>-<date>.zip
```

It takes the ratings, the review text and the likes from the archive, then looks up
director, country, runtime and genre on Wikidata. A lookup is only accepted when the
English label matches the title **and** a publication (or TV start) date falls in the
film's year, searching within the film class (`haswbstatement:P31=Q11424`) so that
titles like *Her*, *Men* or *Civil War* do not resolve to constellations and taxa.
Anything that does not match cleanly is left blank on purpose: a blank field is honest,
a guessed director is not. About 103 of 105 match.

It takes roughly two minutes, once. The result is cached in `data/films.json`, so the
build never touches the network.

## Editing by hand

Add or change an entry in `data/films.json`, then run `python build.py` from the repository
root (it builds the whole site, including `../site/MAYDAY/`).

```json
{
  "n": 21,
  "slug": "first-cow",
  "title": "First Cow",
  "year": 2019,
  "rating": 5.0,
  "liked": true,
  "director": "Kelly Reichardt",
  "country": "United States",
  "runtime": 121,
  "genre": "drama film",
  "review": "the text shown under the film, in his own words",
  "letterboxd": "https://boxd.it/krga"
}
```

- `slug` is unused for now, kept in case per-film pages come back.
- `rating` 1–5, halves allowed, or `null` for a film that was liked but never scored.
- `review` may be `null`. Chinese reviews are fine: they fall back to a system CJK face.
- Order in the file is the order on the page. The generator prints the numbers it is given.

## Publishing

The manifest lives at `noahisarider.srht.site/MAYDAY/` and is part of the one site build at
the repository root. From the root, `python build.py` writes `site/MAYDAY/`, and `./publish.sh`
uploads one tarball containing the now page, the papers page and this manifest together.
There is no separate MAYDAY publish step any more, so a root publish cannot wipe this page.

A personal access token for <https://meta.sr.ht/oauth2/personal-token> with scope
`pages.sr.ht/PAGES:RW` is read from `~/.srht-token`. If the token expires,
`python mayday/tools/token-window.py` opens a one-field local page on
<http://127.0.0.1:8788/> that writes a new one straight to `~/.srht-token`.

The old standalone repository at `git@git.sr.ht:~noahisarider/MAYDAY` is kept as a read-only
archive and is no longer pushed.

## Notes

- No cookies, no trackers, no external requests. Fonts are served from this domain.
- Scores and reviews are the author's. Metadata comes from Letterboxd and Wikidata.
- `assets/fonts/` is under the SIL Open Font License 1.1.
