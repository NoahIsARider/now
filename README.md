# now

The page at <https://noahisarider.srht.site/> — what I am working on, watching and
listening to. One narrow column of text, no rules, no boxes, no images, no navigation.
Updated when something changes, with an RSS feed for whoever wants it.

## Layout

```
data/now.json            the now page. edit this for the front page.
data/papers.json         the papers page (papers.html): what I am reading, with notes.
build.py                 reads both, then calls mayday/build.py, writes the whole site/
assets/style.css         the design: one narrow column, black on white, blue links
assets/fonts/            Special Elite + Courier Prime, self-hosted, OFL 1.1
mayday/                  the MAYDAY films manifest, served at /MAYDAY/
mayday/data/films.json   the film list, generated from a Letterboxd export
mayday/build.py          builds the manifest into site/MAYDAY/
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

The papers page is the same idea: edit `data/papers.json`, re-run. Papers are grouped
(`label` + `papers`); each paper has `title`, optional `url`, `authors`, `venue`, `year`,
optional `status` (shown unless it is `read`), and an optional `note` — `note` accepts the
same inline `[text](url)` links.

## Publishing

`noahisarider.srht.site/` is one site in one repository. The now page is at the root,
the papers page at `/papers.html`, and the films manifest at `/MAYDAY/`.

The build writes all three into one `site/` tree, so `publish.sh` makes one tarball and one
upload. A publish still replaces the whole site at the server, but the replacement now
contains `/MAYDAY/` already, nothing gets wiped and nothing has to be sent a second time.

```sh
./publish.sh          # uses ~/.srht-token
```

Edit the manifest in `mayday/data/films.json` (or regenerate it with
`python mayday/tools/build-films-from-export.py <letterboxd-export.zip>`), then run the same
`python build.py` and `./publish.sh` as always. See `mayday/README.md` for how the list is
made.

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
