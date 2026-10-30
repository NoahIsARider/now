# now

The page at <https://noahisarider.srht.site/> — what I am working on, watching and
listening to. One narrow column of text, no rules, no boxes, no images, no navigation.
Updated when something changes, with an RSS feed for whoever wants it.

## Layout

```
data/now.json            the now page. edit this for the front page.
build.py                 reads it, then calls babel/, nymph/, mayday/ and shkb/build.py,
                         writes the whole site/
assets/style.css         the design: one narrow column, black on white, blue links
assets/fonts/            Special Elite + Courier Prime, self-hosted, OFL 1.1
babel/                   the books manifest, served at /babel/
babel/data/books.json    the reading list
babel/build.py           builds the manifest into site/babel/
nymph/                   the games shelf, served at /nymph/
nymph/data/games.json    the games, one object per game
nymph/build.py           builds the shelf into site/nymph/
mayday/                  the MAYDAY films manifest, served at /MAYDAY/
mayday/data/films.json   the film list, generated from a Letterboxd export
mayday/build.py          builds the manifest into site/MAYDAY/
shkb/                    the shkb listening manifest, served at /shkb/ (dark, underwater)
shkb/data/albums.json    the record list, generated from a record.club export
shkb/build.py            builds the manifest into site/shkb/
site/                    generated output, not in git, this is what gets published
publish.sh               build + upload everything in one tarball
tools/git-hooks/pre-push  the same thing, run on every push
```

## Editing

Change `data/now.json`, then `python build.py`.

```json
{
  "updated": "2026-10-07",
  "name": "noahisarider",
  "summary": "one line at the top",
  "sections": [
    { "label": "work", "items": ["one bullet", "another bullet"] },
    { "label": "watching", "body": "plain text, with [a link](https://example.com) if you want" }
  ],
  "footer": [ { "label": "rss", "href": "feed.xml" } ],
  "changelog": [ { "date": "2026-10-07", "note": "first version" } ]
}
```

- A section with `items` renders as a bulleted list, one with `body` as a paragraph.
- `summary` is optional, a lead line under the masthead when present, nothing when absent.
- Links are inline only: `[text](url)`. Nothing else is parsed.
- **When you change something, add a line to `changelog`.** The newest entry becomes the
  top item in `feed.xml` and carries the full current text, so subscribers see the update.
  Older entries stay in the feed with their note.

The three manifests work the same way. Edit the JSON, re-run the same `python build.py`,
publish as usual. `babel`, `nymph` and `shkb` each carry a `DESIGN.md` for the page they
render.

## Publishing

`noahisarider.srht.site/` is one site in one repository. The now page is at the root,
the films manifest at `/MAYDAY/`, the records manifest at `/shkb/`, the books at
`/babel/` and the games at `/nymph/`.

The build writes all of them into one `site/` tree, so `publish.sh` makes one tarball and
one upload. A publish still replaces the whole site at the server, but the replacement
contains every subdirectory already, so nothing gets wiped and nothing has to be sent a
second time.

```sh
./publish.sh          # uses ~/.srht-token
```

Edit the manifest in `mayday/data/films.json` (or regenerate it with
`python mayday/tools/build-films-from-export.py <letterboxd-export.zip>`), then run the same
`python build.py` and `./publish.sh` as always. See `mayday/README.md` for how the list is
made.

For records, regenerate from a record.club export zip with
`python shkb/tools/build-releases-from-export.py <record-club-export.zip>`, which writes
`shkb/data/albums.json` and refuses any non-ASCII title or artist, then build and publish the
same way. The page design is fixed in `shkb/DESIGN.md`.

On push, once installed:

```sh
cp tools/git-hooks/pre-push .git/hooks/pre-push && chmod +x .git/hooks/pre-push
```

The token needs `pages.sr.ht/PAGES:RW`, from
<https://meta.sr.ht/oauth2/personal-token>. builds.sr.ht would be the official route, but it
refuses free accounts.

## Notes

- No cookies, no trackers, no external requests. Fonts are served from this domain.
- `assets/fonts/` is under the SIL Open Font License 1.1.
