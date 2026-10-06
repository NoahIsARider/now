# MAYDAY

A films manifest. Black lines, straight lines, nothing else.

> It is said that once a pilot has issued the MAYDAY distress signal three times,
> the probability of survival is almost zero.

A static site: an index of films with a one-line verdict each, a page per film, an about
page, and a machine-readable copy of the whole list. It is published on
[sourcehut pages](https://pages.sr.ht) at <https://noahisarider.srht.site/MAYDAY/>.

## Layout

```
data/films.json     the list. this is the only file you edit.
build.py            reads the json, writes site/
assets/style.css    all of the design. one narrow column, no rules, no boxes,
                    no colour except the blue links.
assets/app.js       search box + mood filters. no dependencies.
assets/fonts/       Special Elite + Courier Prime, self-hosted woff2, OFL 1.1
site/               generated output. not in git. this is what gets published.
publish.sh          build + upload to pages.sr.ht
.build.yml          the same thing, run by builds.sr.ht on every push
```

## Editing the list

Add or change an entry in `data/films.json`, then:

```sh
python build.py
```

A film record:

```json
{
  "n": 4,
  "slug": "first-cow",
  "title": "First Cow",
  "year": 2019,
  "director": "Kelly Reichardt",
  "country": "United States",
  "runtime": 121,
  "rating": 5,
  "tags": ["quiet", "tender"],
  "lead": "One sentence printed under the title on the film page.",
  "note": "Two or three sentences. The body of the film page.",
  "letterboxd": "https://letterboxd.com/noahisarider/film/first-cow/"
}
```

- `slug` becomes the URL: `film/first-cow/`
- `rating` is 1-5 or `null`. `null` prints **not rated** and no stars.
- `tags` must come from the `moods` list at the top of the file. Two per film reads best.
- `n` is the position on the manifest. Renumber by hand, the builder prints them in file order.

## Publishing

The site lives at `noahisarider.srht.site/MAYDAY/`. To update it, either

**Automatically** — push to the repository on git.sr.ht. `builds.sr.ht` runs `build.py`,
tars `site/` and uploads it. Nothing to configure, the manifest requests its own
`pages.sr.ht/PAGES:RW` token for the duration of the build.

**By hand** — needs a personal access token from <https://meta.sr.ht/oauth2/personal-tokens>
with the scope `pages.sr.ht/PAGES:RW`:

```sh
echo "$TOKEN" > ~/.srht-token      # then publish.sh picks it up on its own
./publish.sh                       # or: SRHT_TOKEN=... ./publish.sh
```

`SRHT_DOMAIN` and `SRHT_SUBDIR` override the two variables at the top of the script.

## Notes

- Film metadata (year, director, country, runtime) was assembled from a Letterboxd RSS
  export and enriched against Wikidata. Spot-check anything that looks wrong.
- The ratings are the Letterboxd star values. Films at the bottom of the manifest were
  logged but never rated: they are watched, not necessarily recommended. Prune them or
  give them stars.
- No cookies, no trackers, no external requests. Fonts are served from this domain.
- Site content is the author's. `assets/fonts/` is under the SIL Open Font License 1.1.

## Re-entering the token

sr.ht tokens can expire. When publishing fails with 401:

```sh
python tools/token-window.py      # then open http://127.0.0.1:8788/
```

A one-field local page (127.0.0.1 only) writes the new token straight to
`~/.srht-token`. Nothing is echoed back or logged.
