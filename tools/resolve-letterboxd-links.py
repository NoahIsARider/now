# -*- coding: utf-8 -*-
"""
Resolve the boxd.it short links in data/films.json to canonical letterboxd.com film urls.

    python tools/resolve-letterboxd-links.py

One HEAD request per film, 8 at a time (about 11 seconds for 100 films), then cached in
data/films.json so build.py never touches the network. Short links that point at a
personal log entry are normalised to the film page, e.g.
    letterboxd.com/noahisarider/film/nope/  ->  letterboxd.com/film/nope/
"""
import json
import os
import re
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "films.json")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def resolve(url):
    if not url:
        return None
    try:
        op = urllib.request.build_opener(NoRedirect)
        try:
            op.open(urllib.request.Request(url, headers=UA, method="HEAD"), timeout=30)
        except urllib.error.HTTPError as exc:
            loc = (exc.headers.get("Location") or "").split("?")[0]
            if "letterboxd.com" in loc and "/film/" in loc:
                return "https://letterboxd.com/film/" + loc.split("/film/", 1)[1]
    except Exception:                                            # noqa: BLE001
        pass
    return None


def main():
    data = json.load(open(OUT, encoding="utf-8"))
    films = [f for f in data["films"] if f.get("letterboxd")]
    print(f"resolving {len(films)} boxd.it links ...")
    with ThreadPoolExecutor(max_workers=8) as pool:
        for f, url in zip(films, pool.map(resolve, [f["letterboxd"] for f in films])):
            f["letterboxd_url"] = url
    ok = sum(1 for f in data["films"] if f.get("letterboxd_url"))
    print(f"{ok}/{len(data['films'])} resolved")
    for f in data["films"]:
        if f.get("letterboxd") and not f.get("letterboxd_url"):
            print("   unresolved:", f["title"], f["letterboxd"])
    json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
