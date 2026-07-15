"""Deterministic reconcile: write EVERY Hero cell to the CSV literal, then re-merge once.

The escape hatch when `sync.py` and `fix_append.py` FIGHT and never reach 0 — which happens after a
mid-file row insert (sync compares by row position, so everything below the insert shifts and the
fill_down merge logic oscillates). This ignores fill_down entirely: it makes the sheet EXACTLY equal
the CSV literal, then `remerge_hero` derives the merges. Run from repo-root cwd, PYTHONIOENCODING=utf-8:

    python .claude/scripts/tft-set9-skill-modularity/force_full.py
    python .claude/scripts/tft-set9-skill-modularity/sync.py    # then confirm 0

If it raises "can't merge cells that cross the borders of an existing filter", clear the Hero basic
filter first (clearBasicFilter) — see [[tft-sheet-scripts]] #7.
"""
import csv
import pathlib

import gspread

from sheet import CRED, KEY, HERO_COLUMNS, col_letter, cols, remerge_hero

DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")


def main():
    sh = gspread.service_account(filename=CRED).open_by_key(KEY)
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    with open(DATA / "hero.csv", encoding="utf-8", newline="") as f:
        want = [r for r in csv.reader(f)]
    while want and not any(x.strip() for x in want[-1]):
        want.pop()
    c = cols(vals[0])
    wc = cols(want[0])
    last = max(c[n] for n in HERO_COLUMNS)

    if len(want) > len(vals):
        if ws.row_count < len(want):
            ws.add_rows(len(want) - ws.row_count)
        vals += [[""] * len(vals[0]) for _ in range(len(want) - len(vals))]

    sh.batch_update({"requests": [{"unmergeCells": {"range": {
        "sheetId": ws.id, "startRowIndex": 1, "endRowIndex": len(vals),
        "startColumnIndex": 0, "endColumnIndex": last + 1}}}]})

    edits = []
    for i in range(1, len(want)):
        for name in HERO_COLUMNS:
            lit = want[i][wc[name]] if len(want[i]) > wc[name] else ""
            cur = vals[i][c[name]] if len(vals[i]) > c[name] else ""
            if cur != lit:
                edits.append({"range": f"{col_letter(c[name])}{i + 1}", "values": [[lit]]})
    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"force_full: wrote {len(edits)} cells to CSV literal")
    remerge_hero(sh)


if __name__ == "__main__":
    main()
