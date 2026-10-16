#!/usr/bin/env python3
"""Convert a record.club export zip into shkb/data/albums.json.

Usage:
    python shkb/tools/build-releases-from-export.py path/to/export.zip

The export ships releases.csv (the listening collection) and ratings.csv
(scores out of ten). They are joined on MusicBrainz release id. The output
is sorted by year, then artist, then title, and numbered from 001.

Design contract (see shkb/DESIGN.md): the rendered site is English only,
so this tool refuses CJK characters instead of quietly shipping them.
"""

import csv
import io
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "shkb" / "data" / "albums.json"

CJK = re.compile("[⺀-⿯、-〿㐀-䶿一-鿿＀-￯]")


def read_csv(zip_path, name):
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(name) as fh:
            text = io.TextIOWrapper(fh, encoding="utf-8-sig", newline="")
            return list(csv.DictReader(text))


def ascii_guard(label, text):
    if text and CJK.search(text):
        raise SystemExit(f"refusing to ship CJK in {label}: {text!r}")


def main(argv):
    if len(argv) != 2:
        raise SystemExit("usage: build-releases-from-export.py <export.zip>")
    zip_path = Path(argv[1])
    if not zip_path.exists():
        raise SystemExit(f"export not found: {zip_path}")

    releases = read_csv(zip_path, "releases.csv")
    ratings_rows = read_csv(zip_path, "ratings.csv")
    ratings = {row["MBID"].strip(): int(row["Rating"]) for row in ratings_rows}

    albums = []
    for row in releases:
        title = row["Title"].strip()
        artist = row["Artist"].strip()
        mbid = row["MBID"].strip()
        url = row.get("URL", "").strip()
        kind = row["Type"].strip().lower()
        ascii_guard("title", title)
        ascii_guard("artist", artist)
        if not mbid:
            raise SystemExit(f"missing MBID for {artist} - {title}")
        albums.append(
            {
                "title": title,
                "artist": artist,
                "year": int(row["Year"]),
                "type": kind if kind in {"album", "ep", "single"} else "album",
                "rating": ratings.get(mbid),
                "mbid": mbid,
                "url": url,
            }
        )

    albums.sort(key=lambda a: (a["year"], a["artist"].lower(), a["title"].lower()))
    for i, album in enumerate(albums, 1):
        album["n"] = i

    rated = [a for a in albums if a["rating"] is not None]
    missing = sorted(set(ratings) - {a["mbid"] for a in albums})
    if missing:
        raise SystemExit(f"ratings without a matching release: {missing}")

    counts = {
        "total": len(albums),
        "albums": sum(1 for a in albums if a["type"] == "album"),
        "eps": sum(1 for a in albums if a["type"] == "ep"),
        "singles": sum(1 for a in albums if a["type"] == "single"),
        "rated": len(rated),
        "ten": sum(1 for a in rated if a["rating"] == 10),
        "nine": sum(1 for a in rated if a["rating"] == 9),
        "eight": sum(1 for a in rated if a["rating"] == 8),
        "year_min": min(a["year"] for a in albums),
        "year_max": max(a["year"] for a in albums),
    }

    stamp_ms = re.search(r"(\d{13})", zip_path.name)
    exported = (
        datetime.fromtimestamp(int(stamp_ms.group(1)) / 1000, tz=timezone.utc)
        .date()
        .isoformat()
        if stamp_ms
        else None
    )

    payload = {"exported": exported, "counts": counts, "albums": albums}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"wrote {OUT.relative_to(ROOT)}: {counts['total']} releases, "
        f"{counts['rated']} rated, {counts['year_min']}-{counts['year_max']}"
    )


if __name__ == "__main__":
    main(sys.argv)
