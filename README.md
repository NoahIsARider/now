# now

The page at <https://noahisarider.srht.site/> — what I am working on, watching and
listening to. One narrow column of text, no rules, no boxes, no images, no navigation.
Updated when something changes, with an RSS feed for whoever wants it.

## Layout

```
data/now.json            the now page. edit this for the front page.
data/papers.json         the papers page (papers.html): what I am reading, with notes.
build.py                 reads both, writes site/
assets/style.css         the design: one narrow column, black on white, blue links
assets/fonts/            Special Elite + Courier Prime, self-hosted, OFL 1.1
site/                    generated output, not in git, this is what gets published
publish.sh               build + upload to the root of the site
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
- Links are inline only: `[text](url)`. Nothing else is parsed.
- **When you change something, add a line to `changelog`.** The newest entry becomes the
  top item in `feed.xml` and carries the full current text, so subscribers see the update.
  Older entries stay in the feed with their note.

The papers page is the same idea: edit `data/papers.json`, re-run. Papers are grouped
(`label` + `papers`); each paper has `title`, optional `url`, `authors`, `venue`, `year`,
optional `status` (shown unless it is `read`), and an optional `note` — `note` accepts the
same inline `[text](url)` links.

## Publishing

`noahisarider.srht.site/` is the domain root, and the films manifest lives at `/MAYDAY/`.

**Publishing the root replaces the whole site, subdirectories included.** Verified: after a
root publish `/MAYDAY/` answered 404. So `publish.sh` here publishes the root and then runs
`../MAYDAY/publish.sh` to put the manifest back. The other direction is harmless — a publish
*into* a subdirectory only touches that subdirectory, so pushing MAYDAY never disturbs this
page. If you ever publish the root by hand, republish MAYDAY afterwards.

```sh
./publish.sh          # uses ~/.srht-token
```

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
