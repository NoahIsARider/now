# DESIGN.md — Nymph

## Temperament and Imagery

Nymph is a lemon-paper editorial page: one narrow column of soft, full-bodied
serif type on a wall of lemon yellow. The reference is a magazine article
page — a small label, one large statement, a lede, then the text — stripped of
every appliance a magazine would normally add. It should feel typeset rather
than designed: nothing but ink, paper, and a hairline rhythm, in the way the
`babel`, `shkb` and root pages are built.

The same page exists after dark. When the reader's system asks for a dark
scheme the paper and the ink simply trade places — black page, lemon type —
and every proportion, measure and hairline stays exactly where it was. It is
the same page in the other light, not a second design.

## Visual Strategy

- The paper is the page, not a hero band. Colour runs edge to edge, top to
  bottom, on every page.
- One full-width statement per view, stacked: label above, title below.
- Everything is a single centred column; no sidebars, no grids, no cards.
- Structure is carried by upper-case micro-labels and 1px hairlines only.
- Exactly zero decoration: no badge, no pill, no seal, no icon. The one
  reversed block in the design is the wordmark.

## Color Scheme

Two palettes, chosen by `prefers-color-scheme`, built from the same seven
tokens. Nothing else in the stylesheet knows about colour.

| Token        | Light                    | Dark                      | Use                        |
|--------------|--------------------------|---------------------------|----------------------------|
| `--page`     | `#f0fa92`                | `#1a1a17`                 | the whole page background  |
| `--ink`      | `#1a1a17`                | `#f0fa92`                 | headlines and body text    |
| `--ink-soft` | `rgba(26,26,23,.64)`     | `rgba(240,250,146,.66)`   | labels, nav, footer        |
| `--ink-faint`| `rgba(26,26,23,.40)`     | `rgba(240,250,146,.38)`   | separators, underlines     |
| `--lede`     | `rgba(26,26,23,.82)`     | `rgba(240,250,146,.86)`   | italic ledes               |
| `--rule`     | `rgba(26,26,23,.16)`     | `rgba(240,250,146,.20)`   | hairlines                  |
| `--mark-bg`  | `#1a1a17`                | `#f0fa92`                 | wordmark block             |
| `--mark-fg`  | `#f0fa92`                | `#1a1a17`                 | wordmark knockout type     |

The wordmark block is always the inverse of the page, so it reads as a stamp
in either light. Print always resolves to black on white, whatever the screen
is set to.

There is no accent colour. Emphasis comes from size and weight, never hue.

## Typography

- **Fraunces** (self-hosted variable woff2, SIL OFL): every headline, lede,
  list title and body paragraph. `font-optical-sizing: auto`; the roundness
  axis is opened up (`font-variation-settings: "SOFT" 30` for text, `55` for
  headlines) so the serifs stay plump and soft rather than sharp.
  Display weight 700 at `clamp(38px, 8.6vw, 68px)`, line-height 1.01,
  letter-spacing -0.028em. Body 18.5px / 1.68, italic for ledes.
- **Inter** (self-hosted variable woff2, SIL OFL): only micro-labels — the
  masthead stamp, nav, category/date kickers, footer. 10.5–11px, uppercase,
  letter-spacing .14–.2em, weight 500–600.
- Measures: titles wrap by balance, ledes cap at 40ch, prose at 62ch.

## Layout and Interaction

- `.shell` is one column, `max-width: 640px`, centred, 24px side padding.
- Masthead: wordmark `nymph` stamped into a block of the page's opposite
  colour, type knocked out of it, left; `writing by noahisarider` right,
  hairline under it. Nav row: `writing about` left, `rss mail` right, hairline
  under it.
- Lead block: upper-case kicker (`note / October 17, 2026`), the statement,
  then a one-sentence italic lede. Newest post always takes the lead.
- Index: older posts stack — kicker, title, lede, each row closed by a
  hairline. No dates in columns, nothing side by side.
- Post and about pages reuse the same lead block; body starts after a hairline,
  ends with an `all writing` back link.
- Footer: the site-wide two-row convention, hairline above.
- Interaction budget: links only. No javascript anywhere, no sticky bars.

## Design Taboos

- No cards, pills, badges, shadows, gradients, glass, images, or icons.
- No rounded corners of any kind.
- No third palette. Light and dark are the same two colours swapped, and the
  swap is done by `prefers-color-scheme` only.
- No manual theme switch, no toggle in the nav, no javascript to remember a
  choice. The reader's system already knows.
- No second typeface family as display; no thin weights.
- No CJK characters anywhere in output.
- Never invent post content; posts come from markdown files only.

## Execution Requirements

- Posts are markdown files in `posts/` with a simple `key: value` front
  matter block. Dropping in a new file and rebuilding is the entire workflow.
- Fonts self-hosted under `assets/fonts/` (regenerate with
  `python nymph/tools/fetch-fonts.py`); zero requests to Google.
- Check horizontal overflow at 390px and 1024px after structural changes.
- Follow the two-row footer convention shared with the rest of the site.
