"""Snapshot the `tft-set9-skill` sheet into `data/*.csv`.

Run from repo-root cwd:  python .claude/scripts/tft-set9-skill-modularity/export.py

The CSVs are the SOURCE OF TRUTH; `sync.py` writes them back to the sheet. This script exists to
bootstrap them from the live sheet, and afterwards to re-snapshot if the sheet is ever edited by hand.

WHAT IS AND IS NOT CAPTURED
---------------------------
Captured: every cell's raw value, blanks included.

NOT captured: merges, fonts, colours, column widths. MERGES ARE DERIVED FROM THE VALUES
(`remerge_hero()` in sheet.py), which is precisely why a flat CSV is enough to describe the sheet.
Cosmetics are not reproducible from here and are not meant to be.

A BLANK CELL IS DATA. A merged cell reads back as "" on every row but its first, so a continuation
row exports as a genuine empty string - and `sync.py` writes that same empty string back. The two
round-trip exactly, which is what makes the sync's first run a zero-diff. Never "helpfully" fill a
blank here: `Step` in particular is what remerge reads to find the step boundaries, and filling a
continuation row makes it look like a new step.
"""

import csv
import pathlib

from sheet import SCHEMA_TABS, TABS, header_row, open_sheet

DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")


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
        # A schema tab carries a display-only merged super-header ('Action'/'Effect') above its
        # column names. The CSV is single-header, so drop everything above the real header row.
        #
        # THIS TESTED `tab == HERO_TAB` AND SO ONLY EVER STRIPPED SET 9 (fixed 2026-07-21). `Hero
        # set 10` was seeded single-header and had its super-header added by hand on review, so
        # every export since had been silently PREPENDING a junk row to hero-set10.csv — growing it
        # by one row and shifting its header to line 1. Nothing caught it because export is rarely
        # run, and sync survives it (header_row() finds the header either way), so the damage was a
        # corrupted snapshot rather than a corrupted sheet. Both schema tabs get the same treatment
        # now, and header_row() safely returns 0 for a tab that has no super-header.
        if tab in SCHEMA_TABS:
            vals = vals[header_row(vals):]
        width = max(len(r) for r in vals)
        vals = [r + [""] * (width - len(r)) for r in vals]

        with (DATA / name).open("w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerows(vals)
        print(f"{tab:<16} -> data/{name:<20} {len(vals):>3} rows x {width} cols")


if __name__ == "__main__":
    main()
