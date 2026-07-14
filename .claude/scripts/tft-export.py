"""Snapshot the `tft-set9-skill` sheet into `.claude/scripts/data/*.csv`.

Run from repo-root cwd:  python .claude/scripts/tft-export.py

The CSVs are the SOURCE OF TRUTH; `tft-sync.py` writes them back to the sheet. This script exists to
bootstrap them from the live sheet, and afterwards to re-snapshot if the sheet is ever edited by hand.

WHAT IS AND IS NOT CAPTURED
---------------------------
Captured: every cell's raw value, blanks included.

NOT captured: merges, fonts, colours, column widths. MERGES ARE DERIVED FROM THE VALUES
(`remerge_hero()` in tft_sheet.py), which is precisely why a flat CSV is enough to describe the
sheet. Cosmetics are not reproducible from here and are not meant to be.

A BLANK CELL IS DATA. A merged cell reads back as "" on every row but its first, so a continuation
row exports as a genuine empty string - and `tft-sync.py` writes that same empty string back. The two
round-trip exactly, which is what makes the sync's first run a zero-diff. Never "helpfully" fill a
blank here: `Step` in particular is what remerge reads to find the step boundaries, and filling a
continuation row makes it look like a new step.
"""

import csv
import pathlib

from tft_sheet import open_sheet

DATA = pathlib.Path(".claude/scripts/data")

# Sheet tab name -> csv filename. Every tab the scripts own.
TABS = {
    "Hero": "hero.csv",
    "Column Explain": "column-explain.csv",
    "Action Model": "action-model.csv",
    "Effect Types": "effect-types.csv",
    "Collision Types": "collision-types.csv",
    "Scaling Types": "scaling-types.csv",
    "Spread Types": "spread-types.csv",
    "Design Notes": "design-notes.csv",
}


def main():
    sh = open_sheet()
    DATA.mkdir(parents=True, exist_ok=True)
    have = {w.title for w in sh.worksheets()}

    missing = set(TABS) - have
    if missing:
        raise SystemExit(f"sheet is missing these tabs: {sorted(missing)}")

    for tab, name in TABS.items():
        vals = sh.worksheet(tab).get_all_values()
        # Trim trailing all-blank rows: the grid is padded out with empties, and they are not data.
        while vals and not any(cell.strip() for cell in vals[-1]):
            vals.pop()
        width = max(len(r) for r in vals)
        vals = [r + [""] * (width - len(r)) for r in vals]

        with (DATA / name).open("w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerows(vals)
        print(f"{tab:<16} -> data/{name:<20} {len(vals):>3} rows x {width} cols")


if __name__ == "__main__":
    main()
