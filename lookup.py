#!/usr/bin/env python3
"""Turn 23 lines of 11-bit rows into BIP39 word indexes.

Put official english.txt next to this file.
Create rows.txt with exactly 23 lines, each 11 characters of 0 and 1.

  python3 lookup.py
"""

from pathlib import Path

w = Path("english.txt").read_text(encoding="utf-8").split()
if len(w) != 2048:
    raise SystemExit("english.txt must have 2048 words")

rows = Path("rows.txt").read_text(encoding="utf-8").splitlines()
if len(rows) != 23:
    raise SystemExit(f"rows.txt must have 23 lines, found {len(rows)}")

for i, line in enumerate(rows, 1):
    b = line.strip()
    if len(b) != 11 or any(c not in "01" for c in b):
        raise SystemExit(f"row {i} must be exactly 11 bits of 0/1, got {b!r}")
    n = int(b, 2)
    print(i, n, w[n])
