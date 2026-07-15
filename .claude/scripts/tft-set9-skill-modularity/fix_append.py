"""Reconcile the Hero tab after sync.py APPENDED new champions, then re-merge.

`sync.py` cannot merge a freshly-appended multi-row champion in one pass: it writes the FILLED
identity/run-column values, but remerge_hero splits on every non-blank cell, so a new block stays
un-merged (symptom: `re-merged — N blocks` too high; step-start Count/Spread blank not '—'). This
makes the sheet's new rows match the CSV literally (blank identity continuations, blank run-column
continuations, filled step-starts), then re-merges. Run from repo-root cwd, PYTHONIOENCODING=utf-8:

    python .claude/scripts/tft-set9-skill-modularity/sync.py        # push first
    python .claude/scripts/tft-set9-skill-modularity/fix_append.py  # then this
    python .claude/scripts/tft-set9-skill-modularity/sync.py        # must report 0

Idempotent: run it when already consistent and it writes nothing. Editing existing champions only?
You don't need it.
"""
import csv
import pathlib

import gspread

from sheet import (CRED, KEY, IDENTITY_BLOCK, RUN_COLUMNS, STEP_BLOCK, col_letter, cols, remerge_hero)

DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")


def main():
    sh = gspread.service_account(filename=CRED).open_by_key(KEY)
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    c = cols(vals[0])
    with (DATA / "hero.csv").open(encoding="utf-8", newline="") as f:
        want = list(csv.reader(f))
    while want and not any(x.strip() for x in want[-1]):
        want.pop()
    if len(want) != len(vals):
        raise SystemExit(f"row mismatch: sheet {len(vals)} vs CSV {len(want)} — run sync.py first")
    wc = cols(want[0])

    id_cols = [c[n] for n in IDENTITY_BLOCK]
    force_cols = [c[n] for n in (STEP_BLOCK + RUN_COLUMNS)]
    name_by = {c[n]: n for n in (STEP_BLOCK + RUN_COLUMNS)}

    edits = []
    # 1. blank continuation IDENTITY cells (a champion name duplicated from the row above = the bug).
    for i in range(2, len(vals)):
        ch = vals[i][c["Champion"]].strip() if len(vals[i]) > c["Champion"] else ""
        prev = vals[i - 1][c["Champion"]].strip() if len(vals[i - 1]) > c["Champion"] else ""
        if ch and ch == prev:
            for j in id_cols:
                if len(vals[i]) > j and vals[i][j].strip():
                    edits.append({"range": f"{col_letter(j)}{i + 1}", "values": [[""]]})
    # 2. force STEP + RUN columns to the CSV LITERAL (blanks on continuations, values on step-starts).
    for i in range(1, len(want)):
        for ci in force_cols:
            wi = wc[name_by[ci]]
            lit = want[i][wi] if len(want[i]) > wi else ""
            cur = vals[i][ci] if len(vals[i]) > ci else ""
            if cur != lit:
                edits.append({"range": f"{col_letter(ci)}{i + 1}", "values": [[lit]]})

    if not edits:
        print("fix_append: already consistent — nothing to fix")
    else:
        last = max(id_cols + force_cols)
        sh.batch_update({"requests": [{"unmergeCells": {"range": {
            "sheetId": ws.id, "startRowIndex": 1, "endRowIndex": len(vals),
            "startColumnIndex": 0, "endColumnIndex": last + 1}}}]})
        ws.batch_update(edits, value_input_option="RAW")
        print(f"fix_append: wrote {len(edits)} cells")
    remerge_hero(sh)


if __name__ == "__main__":
    main()
