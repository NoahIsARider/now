# -*- coding: utf-8 -*-
"""Build babel/data/books.json from a Goodreads library export CSV.

Reads Book Id, Title, Author, My Rating, Year Published, Date Read,
Exclusive Shelf.  Rows whose title or author contain CJK codepoints
are first looked up in translations.py; hit -> English title used, else
row is skipped.  Non-CJK rows pass through untouched.  All rows sorted
by (rating desc, title).  Output mirrors albums.json / films.json.
"""
import csv
import json
import os
import re
import sys
from collections import Counter

# Allow importing translations.py when run from repo root
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from translations import lookup, lookup_author  # noqa: E402

CJK = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\u3000-\u303f\uff00-\uffef]')


def main(csv_path):
    with open(csv_path, encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))

    rejected_cjk = 0
    kept = []
    for r in rows:
        title = (r.get('Title') or '').strip()
        author = (r.get('Author') or '').strip()
        if not title:
            continue

        has_cjk = CJK.search(title) or CJK.search(author)
        if has_cjk:
            en_title = lookup(title)
            if en_title:
                title = en_title
            else:
                rejected_cjk += 1
                continue

        bid = (r.get('Book Id') or '').strip()

        # normalize author for CJK rows
        if CJK.search(author):
            en_author = lookup_author(author, bid)
            if en_author:
                author = en_author
            else:
                # fallback: strip all CJK runs, keep only Latin fragments
                stripped = CJK.sub(' ', author)
                stripped = re.sub(r'\s+', ' ', stripped).strip()
                if stripped and not CJK.search(stripped):
                    author = stripped
                else:
                    author = ''  # no salvageable Latin → drop author field
        rating_raw = (r.get('My Rating') or '').strip()
        rating = int(float(rating_raw)) if rating_raw else 0
        year = (r.get('Year Published') or '').strip()
        shelf = (r.get('Exclusive Shelf') or '').strip()
        link = f'https://www.goodreads.com/book/show/{bid}' if bid else ''

        kept.append({
            'bid': bid,
            'title': title,
            'author': author,
            'year': int(year) if year.isdigit() else None,
            'rating': rating,
            'read': shelf == 'read',
            'url': link,
        })

    kept.sort(key=lambda b: (-b['rating'], b['title'].lower()))

    # dedupe by title (case-insensitive): first occurrence after sort =
    # highest rating; tie-breaker: highest year
    seen = set()
    kept_dedup = []
    for b in kept:
        t = b['title'].lower()
        if t not in seen:
            seen.add(t)
            kept_dedup.append(b)
    kept = kept_dedup

    ratings = Counter(b['rating'] for b in kept)
    books = []
    for i, b in enumerate(kept, 1):
        n = f'{i:03d}'
        rating = b['rating']
        if rating > 0:
            stars = '★' * rating + '☆' * (5 - rating)
        else:
            stars = ''
        books.append({
            'n': n,
            'title': b['title'],
            'author': b['author'],
            'year': b['year'],
            'rating': rating,
            'stars': stars,
            'url': b['url'],
        })

    out = {
        'exported': '2026-10-16',
        'source': csv_path,
        'counts': {
            'total': len(kept),
            'rejected_cjk_no_translation': rejected_cjk,
            'read': sum(1 for b in kept if b['read']),
            'rated': sum(1 for b in kept if b['rating'] > 0),
            'five': ratings.get(5, 0),
            'four': ratings.get(4, 0),
            'three': ratings.get(3, 0),
            'zero': ratings.get(0, 0),
            'year_min': min((b['year'] for b in kept if b['year']), default=None),
            'year_max': max((b['year'] for b in kept if b['year']), default=None),
        },
        'books': books,
    }
    return out


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python build-books-from-goodreads.py <csv>', file=sys.stderr)
        sys.exit(2)
    data = main(sys.argv[1])
    dest = os.path.join(_HERE, '..', 'data', 'books.json')
    dest = os.path.abspath(dest)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    c = data['counts']
    print(f'written {dest}: total={c["total"]} rejected={c["rejected_cjk_no_translation"]}')
    print(f'  read={c["read"]} rated={c["rated"]} 5={c["five"]} 4={c["four"]} 3={c["three"]} zero={c["zero"]}')
    print(f'  year={c["year_min"]}..{c["year_max"]}')
