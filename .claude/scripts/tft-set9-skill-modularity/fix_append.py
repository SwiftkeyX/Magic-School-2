"""Reconcile the Hero tab after sync.py APPENDED new champions, then re-merge.

`sync.py` cannot merge a freshly-appended multi-row champion in one pass: it writes the FILLED
identity/run-column values, but remerge_hero splits on every non-blank cell, so a new block stays
un-merged (symptom: `re-merged — N blocks` too high; step-start Count/Spread blank not '—'). This
makes the sheet's new rows match the CSV literally (blank identity continuations, blank run-column
continuations, filled step-starts), then re-merges. Run from repo-root cwd, PYTHONIOENCODING=utf-8:

    python .claude/scripts/tft-set9-skill-modularity/sync.py        # push first
    python .claude/scripts/tft-set9-skill-modularity/fix_append.py  # then this
    python .claude/scripts/tft-set9-skill-modularity/sync.py        # must report 0

Run it ONCE after an append (the /add-champion flow does). Editing existing champions only? Skip it.

NOTE (post-v2 decomposition): it is no longer a clean no-op on a settled sheet. The decomposed axes
(Apply/Spawn/…) mean many consecutive action-starts share a run-column value, which remerge_hero
correctly merges ACROSS them (a value-run) while this script re-writes the literal — so a second run
churns those cells harmlessly (remerge undoes it, and `sync.py` still reports 0). Only run it once.
"""
import csv
import pathlib

import gspread

from sheet import (CRED, KEY, HERO_TAB, IDENTITY_BLOCK, RUN_COLUMNS, SCHEMA_TABS, STEP_BLOCK,
                   col_letter, cols, header_row, remerge_hero)

DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")


def main():
    # fix_append is the Set 9 append flow (the /add-champion skill runs it). Addressed by NAME via
    # HERO_TAB, so it survived the 2026-07-18 'Hero' -> 'Hero set 9' rename with one constant.
    sh = gspread.service_account(filename=CRED).open_by_key(KEY)
    ws = sh.worksheet(HERO_TAB)
    vals = ws.get_all_values()
    with (DATA / SCHEMA_TABS[HERO_TAB]).open(encoding="utf-8", newline="") as f:
        want = list(csv.reader(f))
    while want and not any(x.strip() for x in want[-1]):
        want.pop()
    # Hero has a merged super-header above its names; the CSV is single-header. Align by DATA row.
    shr, whr = header_row(vals), header_row(want)
    c, wc = cols(vals[shr]), cols(want[whr])
    ds, dw = shr + 1, whr + 1                       # data-start indices (sheet, CSV)
    n = len(vals) - ds
    if n != len(want) - dw:
        raise SystemExit(f"row mismatch: sheet {n} vs CSV {len(want) - dw} data rows — run sync.py first")

    id_cols = [c[n2] for n2 in IDENTITY_BLOCK]
    force_cols = [c[n2] for n2 in (STEP_BLOCK + RUN_COLUMNS)]
    name_by = {c[n2]: n2 for n2 in (STEP_BLOCK + RUN_COLUMNS)}

    edits = []
    # 1. blank continuation IDENTITY cells (a champion name duplicated from the row above = the bug).
    for k in range(1, n):
        si, sp = ds + k, ds + k - 1
        ch = vals[si][c["Champion"]].strip() if len(vals[si]) > c["Champion"] else ""
        prev = vals[sp][c["Champion"]].strip() if len(vals[sp]) > c["Champion"] else ""
        if ch and ch == prev:
            for j in id_cols:
                if len(vals[si]) > j and vals[si][j].strip():
                    edits.append({"range": f"{col_letter(j)}{si + 1}", "values": [[""]]})
    # 2. force STEP + RUN columns to the CSV LITERAL (blanks on continuations, values on step-starts).
    for k in range(n):
        si, wi_row = ds + k, dw + k
        for ci in force_cols:
            wi = wc[name_by[ci]]
            lit = want[wi_row][wi] if len(want[wi_row]) > wi else ""
            cur = vals[si][ci] if len(vals[si]) > ci else ""
            if cur != lit:
                edits.append({"range": f"{col_letter(ci)}{si + 1}", "values": [[lit]]})

    if not edits:
        print("fix_append: already consistent — nothing to fix")
    else:
        last = max(id_cols + force_cols)
        sh.batch_update({"requests": [{"unmergeCells": {"range": {
            "sheetId": ws.id, "startRowIndex": ds, "endRowIndex": len(vals),
            "startColumnIndex": 0, "endColumnIndex": last + 1}}}]})
        ws.batch_update(edits, value_input_option="RAW")
        print(f"fix_append: wrote {len(edits)} cells")
    remerge_hero(sh)


if __name__ == "__main__":
    main()
