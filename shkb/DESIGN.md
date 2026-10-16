# shkb — a listening manifest

## Temperament and Imagery

MAYDAY is a distress signal in daylight. shkb is what comes after the
struggle stops. You sink, and at a certain depth the surface noise gives way
to a dim, pressure-quiet place where breathing itself has to be relearned.

The page carries this sentence:

> We all get hurt by others, and we all hurt others, and history repeats
> itself again and again. We learn to breathe underwater, like the people
> a century later.
>
> We are all bullies.

So the feeling is not rage and not nostalgia. It is weighted, submerged,
matter-of-fact confession. A list of records as a depth log, kept in the
same typewriter voice as the rest of the site, but read with a lamp on at
the bottom of a pool.

## Visual Strategy

- Same one-narrow-column manifest grammar as MAYDAY. No images, no rules,
  no borders between rows, no cards, no rounded corners, no shadows.
- MAYDAY is black ink on white paper. shkb inverts to deep water: a near
  black blue-green ground, soft grey-blue type, and a single luminous
  shallow-water blue for links and active controls.
- The title of each record is the link itself, lit once and quietly. URLs
  are not spelled out here the way they are on MAYDAY. The water column
  is calm, and MusicBrainz identifiers are unreadable prose.
- The tagline's last line, "We are all bullies.", stands alone at the top, bold in Courier Prime with air around it.
Nothing else gets that weight. (Special Elite at that size prints a false
ink baseline that reads as a link underline, so the verdict is deliberately
not set in the display face.)

## Color Scheme

- ground: `#0b1116` (deep, slightly green water)
- body type: `#aebfc6` water-grey
- display type, entry titles: `#e6eef1` (near-white, not pure white)
- links / active chip / rating: `#7fb6f5` (light seen from underwater)
- visited links: `#6f97c9`
- input and focus wash: `#14202a`
- faint dividing tone, used only inside the search field border: `#22303c`

There must be no second hue, no gradient, and no glow beyond the plain
link colour.

## Typography

- Self-hosted Special Elite for the masthead, record titles and small
  labels, Courier Prime for everything else, same woff2 files as MAYDAY,
  SIL OFL 1.1.
- Masthead `shkb` is a stamped code, 38px, lightly letter-spaced, never
  expanded into the tagline's words.
- Entry titles 21px Special Elite. Artist, year, index and metadata 12.5 to
  13px Courier Prime. Body 15px/1.62.
- Ratings read `10/10` in plain numerals. The denominator is dimmed. Stars
  belong to the films page and must not appear here.

## Layout and Interaction

- Column max width 720px, generous vertical rhythm, index column 3.4ch,
  exactly the MAYDAY grid so the two pages feel like rooms of one house.
- Records are ordered by year, then artist, then title, numbered 001
  onward. Year sits at the right of the title row. EP and single are
  marked in the meta line.
- Only rated records carry a score. An unrated row means listened to, not
  judged. The rating chips `10`, `9`, `8` filter with OR semantics and
  combine with full-text search over title, artist, year and type. The
  `/` key focuses search, `Escape` clears it, as on MAYDAY.
- Count line reads `showing n of 123 releases`. A no-results line explains
  that nothing in the depth log matches.
- Search field is a plain rectangle with a 1px `#22303c` edge and zero
  radius. Dark theme is not an excuse for glass, blur or floating panels.

## Design Taboos

- No cards, no bordered rows, no horizontal rules, no shadows or gradients.
- No rounded corners anywhere, including inputs and buttons.
- No album covers, no photographs, no decorative illustration.
- No stars, hearts or emoji. Ratings are numerals out of ten.
- No white background pasted from the other pages. shkb stays underwater.
- No Chinese characters anywhere on the rendered page or in albums.json.
- No invented links. Every title links to the MusicBrainz release id
  carried in the source export, verified with a real GET.

## Execution Requirements

- `shkb/tools/build-releases-from-export.py` converts a record.club export
  zip into `shkb/data/albums.json`, merging ratings by MBID. The data file
  is the only hand-authored artifact the build depends on.
- `shkb/build.py` is a standalone builder writing to `../site/shkb/` and is
  invoked by the root `build.py`, so the site stays one build, one
  tarball, one publish.
- A dark `favicon.svg` letter `s` uses the link blue, not black.
- Each build must be verified for zero CJK characters and for GET 200 on
  `/shkb/` and `/shkb/albums.json` after publishing.
