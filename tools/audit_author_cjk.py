# -*- coding: utf-8 -*-
import json, re

data = json.load(open('babel/data/books.json', encoding='utf-8'))
CJK = re.compile(r'[\u4e00-\u9fff]')
bad_title = [b for b in data['books'] if CJK.search(b['title'] or '')]
bad_author = [b for b in data['books'] if CJK.search(b['author'] or '')]
print(f'title CJK residual:  {len(bad_title)}')
print(f'author CJK residual: {len(bad_author)}')
for b in bad_author:
    print(f'  [{b["n"]}] author={b["author"]!r}')

# also spot-check the 23 problematic rows
checks = [
    ("007", "Jean-Philippe Deranty"),
    ("019", "Neil Postman"),
    ("084", "Stephen King"),
    ("025", "Raymond Chandler"),
    ("026", "Thomas Mann"),
    ("060", "Lisa Downing"),
    ("041", "Slavoj"),
    ("114", "Barry"),
]
print('\nspot checks:')
for n, expected in checks:
    row = next((b for b in data['books'] if b['n'] == n), None)
    got = row['author'] if row else 'MISSING'
    ok = expected.lower() in got.lower()
    print(f'  [{n}] {got}  ← {expected} {"✓" if ok else "MISMATCH"}')
