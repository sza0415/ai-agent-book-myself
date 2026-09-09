#!/usr/bin/env python3
"""Check embedded Chinese figure fonts using Poppler's pdffonts.

Modified by sza0415 on 2026-09-09: inspect actual PDF font resources instead
of arbitrary compressed streams, and distinguish Hiragino Sans GB (Simplified
Chinese) from Japanese Hiragino fonts. Requires pdffonts (Poppler).

Usage: verify_pdf_fonts.py <pdf> [<pdf> ...]
"""

import re
import subprocess
import sys
from collections import Counter

# Allow occasional Japanese fallback for rare glyphs, but flag widespread use.
# Counts embedded PDF font resources, not compressed streams or text characters.
HIRAGINO_LIMIT = 20
FONT_ROW = re.compile(
    r"^(\S+)\s+.+?\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$"
)


def font_group(name):
    name = re.sub(r"^[A-Z]{6}\+", "", name)
    if name.startswith("HiraginoSansGB"):
        return "HiraginoSansGB"
    if name.startswith(("HiraginoSansCNS", "HiraginoSansTC")):
        return "HiraginoTraditionalChinese"
    if name.startswith("Hiragino"):
        return "HiraginoJapanese"
    for family in ("PingFang", "Songti", "Heiti", "Noto"):
        if family in name:
            return family
    return None


def scan(path):
    result = subprocess.run(
        ["pdffonts", str(path)], check=True, capture_output=True, text=True
    )
    hits = Counter()
    for line in result.stdout.splitlines():
        row = FONT_ROW.match(line)
        if row and row[2] == "yes":
            group = font_group(row[1])
            if group:
                hits[group] += 1
    return hits


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    failed = False
    for path in sys.argv[1:]:
        try:
            hits = scan(path)
        except (OSError, subprocess.CalledProcessError) as error:
            print(f"{path}: ERROR: cannot inspect PDF fonts: {error}")
            return 1
        print(f"{path}: embedded font resources {dict(hits)}")
        if hits["PingFang"] == 0:
            print("  ERROR: no embedded PingFang -- check figure font installation")
            failed = True
        if hits["HiraginoJapanese"] > HIRAGINO_LIMIT:
            print(f"  ERROR: {hits['HiraginoJapanese']} Japanese Hiragino font resources"
                  f" (limit {HIRAGINO_LIMIT}) -- inspect figure text for fallback")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
