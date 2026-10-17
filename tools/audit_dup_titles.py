# -*- coding: utf-8 -*-
import json
from collections import defaultdict, Counter

data = json.load(open('babel/data/books.json', encoding='utf-8'))
by_title = defaultdict(list)
for b in data['books']:
    by_title[b['title']].append(b)

dups = {t: rows for t, rows in by_title.items() if len(rows) > 1}
print(f'total books: {len(data["books"])}')
print(f'unique titles: {len(by_title)}')
print(f'duplicated titles: {len(dups)}')
print()

removed = 0
for title, rows in sorted(dups.items()):
    # sort by rating desc, then year desc
    rows_sorted = sorted(rows, key=lambda b: (-b['rating'], -(b['year'] or 0)))
    keep = rows_sorted[0]
    drop = rows_sorted[1:]
    removed += len(drop)
    print(f'★ {title}')
    for b in rows_sorted:
        marker = '  ← KEEP' if b is keep else '       ×DROP'
        print(f'  [{b["n"]}] {b["author"]} ({b["year"]}) {b["stars"]}{marker}')
    print()

print(f'TO REMOVE: {removed} rows')
print(f'AFTER DEDUP: {len(data["books"]) - removed} unique books')
