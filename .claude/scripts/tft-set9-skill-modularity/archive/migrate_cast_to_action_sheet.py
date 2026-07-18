"""ONE-SHOT, SHEET SIDE: delete Hero's `Cast (s)` column now that the Action Model tab owns it.

    python .claude/scripts/tft-set9-skill-modularity/migrate_cast_to_action_sheet.py

Run AFTER migrate_cast_to_action.py (CSVs) and BEFORE sync.py (values). sync.py deliberately cannot
delete a column - it writes cells, addressed by name, and never restructures. A column delete is a
schema change, so it is a one-shot: run once, then archive.

`Cast (s)` is Hero's LAST column and the 'Effect' super-header stops one short of it (Effect
Recipient..Effect Duration), so the delete touches no merge. Unmerging the data region anyway is
cheap and keeps this identical to the Legacy-action migration: a delete under a live merge leaves it
half-applied and remerge then oscillates for ever (invariant #7).

IDEMPOTENT: no-ops if the column is already gone.
"""

import sys

from sheet import col_letter, header_row, open_sheet

COL = "Cast (s)"


def main():
    sh = open_sheet()
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    hr = header_row(vals)
    hdr = [h.strip() for h in vals[hr]]

    if COL not in hdr:
        print(f"Hero has no {COL!r} column — nothing to do.")
        return
    at = hdr.index(COL)
    tail = [h for h in hdr[at + 1:] if h]
    if tail:
        sys.exit(f"{COL} is not the last column — {tail} sit after it. This deletes ONE column and "
                 f"assumes nothing shifts under it; check the header before re-running.")

    sh.batch_update({"requests": [{"unmergeCells": {"range": {
        "sheetId": ws.id, "startRowIndex": hr + 1, "endRowIndex": len(vals),
        "startColumnIndex": 0, "endColumnIndex": at + 1}}}]})
    sh.batch_update({"requests": [{"deleteDimension": {"range": {
        "sheetId": ws.id, "dimension": "COLUMNS", "startIndex": at, "endIndex": at + 1}}}]})
    print(f"deleted column {col_letter(at)} ({COL}) — Hero is now {ws.col_count - 1} columns wide")
    print("\nNow run force_full.py (the data merges were just dropped), then sync.py to 0.")


if __name__ == "__main__":
    main()
