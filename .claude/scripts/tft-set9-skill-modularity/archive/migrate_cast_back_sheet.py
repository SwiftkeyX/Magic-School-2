"""ONE-SHOT, SHEET SIDE: re-insert Hero's `Cast (s)` column INSIDE the Action group.

    python .claude/scripts/tft-set9-skill-modularity/migrate_cast_back_sheet.py

Run AFTER migrate_cast_back.py (CSVs) and BEFORE force_full.py / sync.py (values). sync.py writes
cells addressed by name and never adds a column — that is what stops it restructuring the sheet — so
a column insert is a one-shot.

The column goes after `Collision`, closing the ACTION region, and the 'Action' super-header WIDENS to
cover it. That is the whole point of the move: Cast (s) was Hero's last column, marooned past the
effect block, so it read as an effect property when it describes the action.

IDEMPOTENT: no-ops if the column is already there.
"""

import sys

from sheet import col_letter, cols, header_row, open_sheet

COL = "Cast (s)"
AFTER = "Collision"
ACTION_REGION = ("Action Source", "Cast")
EFFECT_REGION = ("Effect Recipient", "Effect Duration")


def main():
    sh = open_sheet()
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    hr = header_row(vals)

    if any(h.strip() == COL for h in vals[hr]):
        print(f"Hero already has {COL!r} — nothing to do.")
        return

    # Locate the anchor BY HAND, not via cols(): cols() resolves every name in HERO_COLUMNS, which
    # already lists `Cast` — the column this script is about to create. It would raise on its own
    # chicken-and-egg. Same exact-then-prefix rule, one column ("Collision (If it have one)").
    hdr = [h.strip() for h in vals[hr]]
    match = [i for i, h in enumerate(hdr) if h == AFTER] or \
            [i for i, h in enumerate(hdr) if h.startswith(AFTER)]
    if not match:
        sys.exit(f"Hero header has no {AFTER!r} column to insert after: {hdr}")
    at = match[0] + 1                                   # insert straight after Collision
    # Unmerge the whole tab first: an insert beside a live merge leaves it half-applied, and the
    # super-header merge has to be rebuilt anyway since the region just got a column wider.
    sh.batch_update({"requests": [{"unmergeCells": {"range": {"sheetId": ws.id}}}]})
    sh.batch_update({"requests": [{"insertDimension": {
        "range": {"sheetId": ws.id, "dimension": "COLUMNS", "startIndex": at, "endIndex": at + 1},
        "inheritFromBefore": True}}]})
    ws.update_acell(f"{col_letter(at)}{hr + 1}", COL)
    print(f"inserted column {col_letter(at)} ({COL}) after {AFTER}")

    vals = ws.get_all_values()
    hr = header_row(vals)
    c = cols(vals[hr])
    if c["Cast"] != at:
        sys.exit(f"the new column did not land where expected: Cast at {c['Cast']}, wanted {at}")

    a0, a1 = c[ACTION_REGION[0]], c[ACTION_REGION[1]]
    e0, e1 = c[EFFECT_REGION[0]], c[EFFECT_REGION[1]]
    ws.batch_update([
        {"range": f"{col_letter(a0)}{hr}", "values": [["Action"]]},
        {"range": f"{col_letter(e0)}{hr}", "values": [["Effect"]]},
    ], value_input_option="RAW")
    sh.batch_update({"requests": [
        {"mergeCells": {"range": {"sheetId": ws.id, "startRowIndex": hr - 1, "endRowIndex": hr,
                                  "startColumnIndex": a0, "endColumnIndex": a1 + 1},
                        "mergeType": "MERGE_ROWS"}},
        {"mergeCells": {"range": {"sheetId": ws.id, "startRowIndex": hr - 1, "endRowIndex": hr,
                                  "startColumnIndex": e0, "endColumnIndex": e1 + 1},
                        "mergeType": "MERGE_ROWS"}},
    ]})
    print(f"super-header: 'Action' now spans cols {a0}-{a1} (Action Source..{COL}), "
          f"'Effect' spans {e0}-{e1}")
    print("\nNow run force_full.py (the data merges were dropped), then sync.py to 0.")


if __name__ == "__main__":
    main()
