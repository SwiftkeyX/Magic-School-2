"""Deterministic reconcile: write EVERY cell of a schema tab to the CSV literal, then re-merge once.

The escape hatch when `sync.py` and `fix_append.py` FIGHT and never reach 0 — which happens after a
mid-file row insert (sync compares by row position, so everything below the insert shifts and the
fill_down merge logic oscillates), AND when a schema tab is FRESHLY CREATED: sync writes the filled
identity down every row (the sheet started blank), and remerge then splits on every non-blank cell so
the identity block never merges (invariant #6, for the whole tab at once). This ignores fill_down
entirely: it makes the sheet EXACTLY equal the CSV literal — blanks included — then `remerge_hero`
derives the merges from those literal blanks. Run from repo-root cwd, PYTHONIOENCODING=utf-8:

    python .claude/scripts/tft-set9-skill-modularity/force_full.py ["<tab>"]
    python .claude/scripts/tft-set9-skill-modularity/sync.py    # then confirm 0

`<tab>` defaults to `Hero set 9`; pass `"Hero set 10"` (a key of SCHEMA_TABS) for the Set 10 tab. Its
CSV is looked up from SCHEMA_TABS, so the two never drift.

If it raises "can't merge cells that cross the borders of an existing filter", clear the tab's basic
filter first (clearBasicFilter) — see [[tft-sheet-scripts]] #7.
"""
import csv
import pathlib
import sys

import gspread

from sheet import (CRED, KEY, HERO_COLUMNS, HERO_TAB, SCHEMA_TABS, col_letter, cols, header_row,
                   record_changes, remerge_hero)

DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")


def main(tab=HERO_TAB):
    csv_name = SCHEMA_TABS[tab]                      # KeyError here = not a schema tab, which is right
    sh = gspread.service_account(filename=CRED).open_by_key(KEY)
    ws = sh.worksheet(tab)
    vals = ws.get_all_values()
    with open(DATA / csv_name, encoding="utf-8", newline="") as f:
        want = [r for r in csv.reader(f)]
    while want and not any(x.strip() for x in want[-1]):
        want.pop()
    # Hero has a merged super-header above its names; the CSV is single-header. Align by DATA row.
    shr, whr = header_row(vals), header_row(want)
    c, wc = cols(vals[shr]), cols(want[whr])
    ds, dw = shr + 1, whr + 1
    last = max(c[n] for n in HERO_COLUMNS)
    n = len(want) - dw

    if ds + n > len(vals):
        if ws.row_count < ds + n:
            ws.add_rows(ds + n - ws.row_count)
        vals += [[""] * len(vals[shr]) for _ in range(ds + n - len(vals))]

    sh.batch_update({"requests": [{"unmergeCells": {"range": {
        "sheetId": ws.id, "startRowIndex": ds, "endRowIndex": len(vals),
        "startColumnIndex": 0, "endColumnIndex": last + 1}}}]})

    edits = []
    for k in range(n):
        si, wi_row = ds + k, dw + k
        for name in HERO_COLUMNS:
            lit = want[wi_row][wc[name]] if len(want[wi_row]) > wc[name] else ""
            cur = vals[si][c[name]] if len(vals[si]) > c[name] else ""
            if cur != lit:
                edits.append({"range": f"{col_letter(c[name])}{si + 1}", "values": [[lit]]})
    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    record_changes(tab, [e["range"] for e in edits])   # for highlight_changes.py to colour
    print(f"{tab}: force_full wrote {len(edits)} cells to CSV literal")
    remerge_hero(sh, tab)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else HERO_TAB)
