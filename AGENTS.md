# AGENTS.md

## Commands

| Task | Command |
|------|---------|
| Build whole site | `python build.py` |
| Local preview | `python -m http.server 8799 --directory site` |
| Rebuild books data | `python babel/tools/build-books-from-goodreads.py <goodreads_library_export.csv>` |

No package manager, no lint config, no tests. Python 3 standard library only.

## Deploy — two hosts, always update both

Sourcehut is canonical; Nekoweb is a mirror. Content changes ship to both.

**sr.ht** (`https://noahisarider.srht.site`):

```sh
./publish.sh          # run from git-bash; reads token from ~/.srht-token
```

One tarball replaces the whole site (root + `/MAYDAY/` + `/shkb/` + `/babel/`), so sub-directories can never be wiped by a root publish.

**Nekoweb** (`https://noahisarider.nekoweb.org`), manual ZIP import:

```powershell
$env:SITE_URL="https://noahisarider.nekoweb.org"; python build.py; Remove-Item Env:SITE_URL
# then zip site/ with .NET ZipArchive (see below), import in the Nekoweb panel
```

Nekoweb rules:
- Build with `SITE_URL` overridden, or canonical/RSS/sitemap URLs point at sr.ht.
- ZIP entry names MUST use forward slashes. Never use `Compress-Archive` — it writes backslash entries and Nekoweb skips every sub-directory. Use `System.IO.Compression.ZipArchive` with `.Replace('\','/')`.
- After either deploy, verify live: HTTP 200 for `/` and `/babel/`, footer links present, zero CJK.

## Layout

```
build.py            root now page + RSS + sitemap; calls each section's build.py
data/now.json       home page content, footer links (two rows), changelog -> RSS
publish.sh          sr.ht build + tar + upload
babel/              books page (white "cult core", UnifrakturMaguntia, no client JS)
shkb/               records depth log
mayday/             films manifest (outputs to site/MAYDAY/)
```

Each section owns `build.py`, `data/*.json`, `assets/`, and outputs into `../site/<section>/`.

babel data pipeline: Goodreads CSV → `babel/tools/build-books-from-goodreads.py` + `translations.py` (CJK title/author lookup) → `babel/data/books.json` (committed). CSV exports are never committed.

## Conventions

- Zero CJK codepoints anywhere in `site/` output — HTML, JSON, CSS, JS. Audit with a `[一-鿿]` regex after builds.
- Footer: internal links row 1 (`rss books films records`), `<br>`, external row 2 (`goodreads record.club letterboxd sr.ht`), `sr.ht` last. Root footer is driven by `data/now.json` (`{"href":"_br_"}` renders the `<br>`); babel footer is hardcoded in `babel/build.py`.
- Fonts are self-hosted WOFF2 under each section's `assets/fonts/` (SIL OFL). No Google Fonts requests.
- Design constraints live in each section's `DESIGN.md` — follow it, no rounded corners, cards, or gradients in babel.
- Credentials live only in `~/.srht-token`. Never print tokens, never commit them. Do not commit `nekoweb-*.zip`.
- Commits only when explicitly asked; author `noahisarider <noahchou2005@gmail.com>`, SSH push for sr.ht and Codeberg, `gh` CLI (HTTPS) for GitHub.
