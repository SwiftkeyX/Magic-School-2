"""ONE-SHOT, SHEET SIDE: delete Hero's `Collision` column and reshape the Action super-header.

    python .claude/scripts/tft-set9-skill-modularity/migrate_drop_collision_sheet.py

Run AFTER migrate_drop_collision.py (CSVs), then force_full.py + sync.py. sync writes cells by name
and never restructures, so a column delete is a one-shot. IDEMPOTENT: no-ops if it is already gone.
"""

import sys

from sheet import col_letter, header_row, open_sheet

COL = "Collision"
ACTION_REGION = ("Action Source", "Cast (s)")
EFFECT_REGION = ("Effect Recipient", "Effect Duration (s)")


def find(hdr, name):
    m = [i for i, h in enumerate(hdr) if h == name] or \
        [i for i, h in enumerate(hdr) if h.startswith(name)]
    return m[0] if m else None


def main():
    sh = open_sheet()
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    hr = header_row(vals)
    hdr = [h.strip() for h in vals[hr]]

    at = find(hdr, COL)
    if at is None:
        print(f"Hero has no {COL!r} column — nothing to do.")
        return

    sh.batch_update({"requests": [{"unmergeCells": {"range": {"sheetId": ws.id}}}]})
    sh.batch_update({"requests": [{"deleteDimension": {"range": {
        "sheetId": ws.id, "dimension": "COLUMNS", "startIndex": at, "endIndex": at + 1}}}]})
    print(f"deleted column {col_letter(at)} ({hdr[at]}) — Hero is now {ws.col_count - 1} columns wide")

    vals = ws.get_all_values()
    hr = header_row(vals)
    hdr = [h.strip() for h in vals[hr]]
    a0, a1 = find(hdr, ACTION_REGION[0]), find(hdr, ACTION_REGION[1])
    e0, e1 = find(hdr, EFFECT_REGION[0]), find(hdr, EFFECT_REGION[1])
    if None in (a0, a1, e0, e1):
        sys.exit(f"could not locate the header regions after the delete: {hdr}")

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
    print(f"super-header: 'Action' spans {a0}-{a1}, 'Effect' spans {e0}-{e1}")
    print("\nNow run force_full.py, then sync.py to 0.")


if __name__ == "__main__":
    main()
