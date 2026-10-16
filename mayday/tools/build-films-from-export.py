# -*- coding: utf-8 -*-
"""
Rebuild data/films.json from a Letterboxd export.

    python tools/build-films-from-export.py <path-to-letterboxd-export.zip>

From the export:
    ratings.csv      the manifest, one entry per rated film
    reviews.csv      the review text, verbatim, shown on that film's page
    likes/films.csv  the 'liked' flag, plus films liked but never rated (rating = null)

Added from Wikidata (strictly): director, country, runtime, genre. An item is accepted
only when its English label matches the title AND one of its publication dates falls in
the film's year. Anything else is left blank on purpose: a blank field is honest, a
guessed director is not.

Queries run 8 at a time (sequential lookups take minutes), and the result is cached in
data/films.json, so build.py itself never touches the network.
"""
import csv
import io
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "films.json")
UA = {"User-Agent": "MAYDAY-site-builder/1.0 (noahchou2005@gmail.com)"}
API = "https://www.wikidata.org/w/api.php?"
WORKERS = 8


def get(url, tries=3):
    for a in range(tries):
        try:
            return json.loads(urllib.request.urlopen(
                urllib.request.Request(url, headers=UA), timeout=45).read())
        except Exception:                                    # noqa: BLE001
            if a == tries - 1:
                return None
            time.sleep(0.6 * (a + 1))


def pmap(fn, items):
    """parallel map that keeps order and tolerates failures"""
    out = []
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for r in pool.map(fn, items):
            out.append(r)
    return out


def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", s.lower().replace("&", "and"))


def slugify(title):
    s = unicodedata.normalize("NFKD", title)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:70] or "film"


def read_export(path):
    rows = {}
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if not n.endswith(".csv") or "/deleted/" in n or "/orphaned/" in n:
                continue
            data = list(csv.DictReader(io.TextIOWrapper(z.open(n), encoding="utf-8-sig",
                                                       newline="")))
            rows[n] = data
            rows.setdefault(n.split("/")[-1], data)      # tolerate a wrapping top folder
    return rows


def wbget(ids):
    """entity ids -> entities, batched 45 per request, in parallel"""
    ids = sorted({i for i in ids if i})
    chunks = [ids[i:i + 45] for i in range(0, len(ids), 45)]

    def one(chunk):
        q = urllib.parse.urlencode({"action": "wbgetentities", "ids": "|".join(chunk),
                                    "props": "claims|labels|aliases", "languages": "en",
                                    "format": "json"})
        return (get(API + q) or {}).get("entities", {})

    out = {}
    for part in pmap(one, chunks):
        out.update(part)
    return out


def values(ent, prop):
    vals = []
    for c in ent.get("claims", {}).get(prop, []):
        try:
            vals.append(c["mainsnak"]["datavalue"]["value"])
        except (KeyError, TypeError):
            pass
    return vals


def ids_of(ent, prop):
    return [v["id"] for v in values(ent, prop) if isinstance(v, dict) and v.get("id")]


def label_of(ents, qid):
    return ((ents.get(qid) or {}).get("labels", {}).get("en", {}) or {}).get("value")


FILMY = ("film", "movie", "miniseries", "television series", "animation")
# if the type labels could not be fetched (flaky network), fall back to these classes
FILM_QIDS = {
    "Q11424",     # film
    "Q24869",     # feature film
    "Q506240",    # television film
    "Q1259759",   # miniseries
    "Q5398426",   # television series
    "Q93204",     # documentary film
    "Q202866",    # animated film
    "Q18011172",  # film project
}


def search(term):
    """Wikidata search restricted to films first, because plain text search returns
    constellations, taxa and albums for titles like 'Her', 'Men' or 'Civil War'.
    Television gets a second pass, since a miniseries is not an instance of 'film'."""
    for cls in ("Q11424", "Q1259759", "Q5398426", "Q93204"):
        q = urllib.parse.urlencode({"action": "query", "list": "search",
                                    "srsearch": f"{term} haswbstatement:P31={cls}",
                                    "srnamespace": 0, "srlimit": 10, "format": "json"})
        hits = [h["title"] for h in
                ((get(API + q) or {}).get("query", {}).get("search", []))
                if re.fullmatch(r"Q\d+", h.get("title", ""))]
        if hits:
            return hits
    q = urllib.parse.urlencode({"action": "wbsearchentities", "search": term, "language": "en",
                                "uselang": "en", "type": "item", "limit": 20, "format": "json"})
    return [h["id"] for h in (get(API + q) or {}).get("search", [])][:20]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    rows = read_export(sys.argv[1])
    ratings, reviews, likes = rows["ratings.csv"], rows["reviews.csv"], rows["likes/films.csv"]

    review_of = {(norm(r["Name"]), r["Year"]): r["Review"].strip()
                 for r in reviews if r["Review"].strip()}
    liked = {(norm(r["Name"]), r["Year"]) for r in likes}
    films = [{"title": r["Name"].strip(), "year": int(r["Year"]), "rating": float(r["Rating"]),
              "review": review_of.get((norm(r["Name"]), r["Year"])),
              "liked": (norm(r["Name"]), r["Year"]) in liked,
              "letterboxd": r["Letterboxd URI"].strip()}
             for r in ratings if r["Rating"].strip()]
    rated = {(norm(f["title"]), str(f["year"])) for f in films}
    for r in likes:
        if (norm(r["Name"]), r["Year"]) not in rated:
            films.append({"title": r["Name"].strip(), "year": int(r["Year"]), "rating": None,
                          "review": None, "liked": True,
                          "letterboxd": r["Letterboxd URI"].strip()})
    print(f"{len(films)} films ({len(ratings)} rated, {len(films) - len(ratings)} liked only), "
          f"{sum(1 for f in films if f['review'])} with a written review")

    t0 = time.time()
    print(f"searching wikidata for {len(films)} titles, {WORKERS} at a time ...")
    cands = dict(zip([f["title"] for f in films],
                     pmap(search, [f["title"] for f in films])))
    ents = wbget({i for v in cands.values() for i in v})
    tl = wbget({i for e in ents.values() for i in ids_of(e, "P31")})
    type_labels = {q: ((e.get("labels", {}).get("en", {}) or {}).get("value", ""))
                   for q, e in tl.items()}
    print(f"  {len(cands)} searches, {len(ents)} candidates, {len(tl)} type labels "
          f"({time.time() - t0:.0f}s)")

    def accepts(ent, title, year, type_labels, reasons):
        types = [type_labels.get(i, "") for i in ids_of(ent, "P31")]
        p31 = set(ids_of(ent, "P31"))
        if not (any(any(w in t.lower() for w in FILMY) for t in types) or (p31 & FILM_QIDS)):
            reasons.append("not filmish: " + "/".join(sorted(types)[:2] or sorted(p31)[:2]))
            return False
        labels = [(ent.get("labels", {}).get("en", {}) or {}).get("value", "")]
        labels += [a["value"] for a in (ent.get("aliases", {}).get("en", []) or [])]
        if not any(norm(x) == norm(title) for x in labels if x):
            reasons.append("title != " + (labels[0] or "?"))
            return False
        years = {v["time"][1:5] for v in values(ent, "P577") + values(ent, "P580")
                 if isinstance(v, dict) and "time" in v}
        if str(year) not in years:
            reasons.append(f"year {year} not in {sorted(years) or '-'}")
            return False
        return True

    gate = {}
    picked = {}
    for f in films:
        reasons = []
        for qid in cands.get(f["title"], []):
            ent = ents.get(qid)
            if ent and accepts(ent, f["title"], f["year"], type_labels, reasons):
                picked[f["title"]] = (qid, ent)
                break
        if f["title"] not in picked:
            gate[f["title"]] = (len(cands.get(f["title"], [])), reasons[:3])

    # retry the misses with "title year", which disambiguates most of them
    missed = [f for f in films if f["title"] not in picked]
    print(f"  {len(picked)} matched, retrying {len(missed)} with a year-qualified search")
    cands2 = dict(zip([f["title"] for f in missed],
                      pmap(search, [f"{f['title']} {f['year']}" for f in missed])))
    # a trailing year can break the plain-text match, so retry the bare title too
    for f, hits in zip(missed, pmap(search, [f["title"] for f in missed])):
        if not cands2.get(f["title"]):
            cands2[f["title"]] = hits
    ents2 = wbget({i for v in cands2.values() for i in v})
    tl2 = wbget({i for e in ents2.values() for i in ids_of(e, "P31")})
    type_labels.update({q: ((e.get("labels", {}).get("en", {}) or {}).get("value", ""))
                        for q, e in tl2.items()})
    ents.update(ents2)
    for f in missed:
        reasons = []
        for qid in cands2.get(f["title"], []):
            ent = ents2.get(qid)
            if ent and accepts(ent, f["title"], f["year"], type_labels, reasons):
                picked[f["title"]] = (qid, ent)
                break
        else:
            n, why = gate.get(f["title"], (0, []))
            gate[f["title"]] = (n, why + reasons[:2])
    print(f"  {len(picked)}/{len(films)} films identified ({time.time() - t0:.0f}s)")

    # labels for everything the matched items point at: directors, countries, genres
    refs = {qid: ids_of(e, "P57") + ids_of(e, "P495") + ids_of(e, "P136")
            for qid, e in picked.values()}
    reflabels = {q: ((e.get("labels", {}).get("en", {}) or {}).get("value", ""))
                 for q, e in wbget({i for v in refs.values() for i in v}).items()}

    for f in films:
        pair = picked.get(f["title"])
        if not pair:
            f.update(director=None, country=None, runtime=None, genre=None)
            continue
        qid, ent = pair
        f["qid"] = qid
        f["director"] = ", ".join(x for x in (reflabels.get(i, "") for i in ids_of(ent, "P57"))
                                  if x) or None
        f["country"] = ", ".join(x for x in (reflabels.get(i, "") for i in ids_of(ent, "P495"))
                                 if x) or None
        f["genre"] = ", ".join(x for x in (reflabels.get(i, "") for i in ids_of(ent, "P136"))
                               if x) or None
        durs = [float(v["amount"][1:]) for v in values(ent, "P2047")
                if isinstance(v, dict) and "amount" in v]
        f["runtime"] = round(min(durs)) if durs else None

    seen = {}
    for f in films:
        s = slugify(f["title"])
        seen[s] = seen.get(s, 0) + 1
        f["slug"] = s if seen[s] == 1 else f"{s}-{f['year']}"
    films.sort(key=lambda f: (-(f["rating"] or 0), -f["year"], f["title"].lower()))
    for i, f in enumerate(films, 1):
        f["n"] = i
    for f in films:
        for k in ("director", "country", "runtime", "genre", "review", "qid"):
            f.setdefault(k, None)

    data = {
        "profile": {
            "bio": ("A full-stack developer who happens to love film. Arthouse and auteur cinema "
                    "is home base, the kind of movies that argue with you instead of explaining "
                    "themselves, with a soft spot for anything carrying a social edge."),
            "letterboxd": "https://letterboxd.com/noahisarider/",
        },
        "ratings": sorted({f["rating"] for f in films if f["rating"]}, reverse=True),
        "films": films,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print(f"\nwrote {OUT} in {time.time() - t0:.0f}s")
    print(f"  {sum(1 for f in films if f.get('director'))}/{len(films)} have a director, "
          f"{sum(1 for f in films if f.get('runtime'))} have a runtime")
    blank = [f"{f['title']} ({f['year']})" for f in films if not f.get("director")]
    if blank:
        print("  left blank (no clean wikidata match):")
        for f in films:
            if f.get("director"):
                continue
            n, why = gate.get(f["title"], (0, []))
            print(f"    {f['title']} ({f['year']}) — {n} candidates, "
                  + (" | ".join(why) if why else "no usable candidate"))


if __name__ == "__main__":
    main()
