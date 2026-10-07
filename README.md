# MAYDAY

A films manifest. Type, whitespace and blue links. No rules, no boxes, no images.

> It is said that once a pilot has issued the MAYDAY distress signal three times,
> the probability of survival is almost zero.

Live at <https://noahisarider.srht.site/MAYDAY/>: every film the author has rated on
Letterboxd (105 of them: 85 rated, 20 liked), with his own score, his own review where
he wrote one, and the film's page address spelled out as the link.

## Layout

```
data/films.json                    the whole list. the only file you edit by hand.
data/reviews-en.json               english renderings of the reviews written in chinese
tools/build-films-from-export.py   rebuilds films.json from a Letterboxd export (+ Wikidata)
tools/resolve-letterboxd-links.py  turns the export's boxd.it links into letterboxd.com/film/...
tools/token-window.py              one-field local page for re-entering an expired token
build.py                           reads the json, writes site/
assets/style.css                   all of the design
assets/app.js                      search + rating filter, no dependencies
assets/favicon.svg                 the letter M cut out of Special Elite, as a path
assets/fonts/                      Special Elite + Courier Prime, self-hosted, OFL 1.1
site/                              generated output, not in git, this is what gets published
publish.sh                         build + upload to pages.sr.ht
.build.yml                         the same thing, run by builds.sr.ht on push
```

Each line on the index carries two links: the blue address is the film on Letterboxd, and
the number at the start of the line opens that film's page on this site. Every review is
published in English. The Chinese originals stay in `data/films.json` as `review_zh` and are
stripped from the published `films.json`, so no Chinese is served.

## Rebuilding the list from Letterboxd

Export from Letterboxd (Settings → Data → Export your data), then:

```sh
python tools/build-films-from-export.py ~/Downloads/letterboxd-<user>-<date>.zip
```

It takes the ratings, the review text and the likes from the archive, then looks up
director, country, runtime and genre on Wikidata. A lookup is only accepted when the
English label matches the title **and** a publication (or TV start) date falls in the
film's year, searching within the film class (`haswbstatement:P31=Q11424`) so that
titles like *Her*, *Men* or *Civil War* do not resolve to constellations and taxa.
Anything that does not match cleanly is left blank on purpose: a blank field is honest,
a guessed director is not. About 103 of 105 match.

It takes roughly two minutes, once. The result is cached in `data/films.json`, so
`build.py` never touches the network.

## Editing by hand

Add or change an entry in `data/films.json`, then `python build.py`.

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

- `slug` becomes the URL: `film/first-cow/`, and the link printed on each line.
- `rating` 1–5, halves allowed, or `null` for a film that was liked but never scored.
- `review` may be `null`. Chinese reviews are fine: they fall back to a system CJK face.
- Order in the file is the order on the page. The generator prints the numbers it is given.

## Publishing

The site lives at `noahisarider.srht.site/MAYDAY/`. Either

**Automatically** — push to the repository on git.sr.ht. `builds.sr.ht` runs `build.py`,
tars `site/` and uploads it. The manifest requests its own `pages.sr.ht/PAGES:RW` token
for the duration of the build, so no secret is stored in the repository.

**By hand** — needs a personal access token from
<https://meta.sr.ht/oauth2/personal-token> with the scope `pages.sr.ht/PAGES:RW`:

```sh
echo "$TOKEN" > ~/.srht-token      # publish.sh picks this up on its own
./publish.sh
```

`SRHT_DOMAIN` and `SRHT_SUBDIR` override the two variables at the top of the script.
If the token expires, `python tools/token-window.py` opens a one-field local page on
<http://127.0.0.1:8788/> that writes a new one straight to `~/.srht-token`.

## Notes

- No cookies, no trackers, no external requests. Fonts are served from this domain.
- Scores and reviews are the author's. Metadata comes from Letterboxd and Wikidata.
- `assets/fonts/` is under the SIL Open Font License 1.1.
