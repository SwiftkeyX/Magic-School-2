"""ONE-SHOT, SHEET SIDE: delete Hero's four dead axis columns and rebuild the super-header.

    python .claude/scripts/tft-set9-skill-modularity/migrate_legacy_action_sheet.py

Run AFTER migrate_legacy_action.py (which rewrites the CSVs) and BEFORE sync.py (which fills the
values in). This exists because sync.py deliberately cannot do it: sync WRITES CELLS, addressed by
name, and never adds or removes a column — that is what stops it from silently restructuring the
sheet. A column delete is a schema change, so it is a one-shot, run once, then archived.

WHAT IT DOES
  Apply | Spawn | Motion | Behavior | Shape   ->   Legacy action
  (cols 15-19)                                     (col 15; 16-19 deleted)

  The 'Action' super-header spanned EXACTLY those five columns, because it was added in answer to the
  very comment this migration implements — the user asked for "Apply => Shape ... replaced by
  'Action'" (one column) and got a banner merged OVER the five instead. With the axes gone the banner
  has nothing to group, so it widens to the whole action region (Action Source..Collision), mirroring
  'Effect' over the effect columns. That is the Action|Effect split the two-row header was reaching
  for. The user's call.

ORDER IS LOAD-BEARING. Unmerge FIRST: a delete under a live merge leaves the merge half-applied, and
remerge then oscillates for ever (invariant #7 — the same failure a stray basic filter causes). The
data merges are DERIVED, so dropping them costs nothing; sync.py's remerge_hero rebuilds them.

IDEMPOTENT: it checks the header and no-ops if the columns are already gone.
"""

import sys

from sheet import D, col_letter, cols, header_row, open_sheet

AXES = ["Apply", "Spawn", "Motion", "Behavior", "Shape"]
KEY = "Legacy action"

# The action region after the delete: Action Source .. Collision. Named, not indexed — the whole
# reason this tooling stopped breaking (see sheet.py).
ACTION_REGION = ("Action Source", "Collision")
EFFECT_REGION = ("Effect Recipient", "Effect Duration")


def main():
    sh = open_sheet()
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    hr = header_row(vals)
    hdr = vals[hr]

    if KEY in [h.strip() for h in hdr]:
        print(f"Hero already has {KEY!r} — nothing to do.")
        return
    missing = [a for a in AXES if a not in [h.strip() for h in hdr]]
    if missing:
        sys.exit(f"Hero has neither {KEY!r} nor the axes {missing} — refusing to guess. Header: {hdr}")

    at = [h.strip() for h in hdr].index("Apply")
    assert [h.strip() for h in hdr][at:at + 5] == AXES, (
        f"the five axes are not contiguous at col {at}: {hdr[at:at + 5]}. This script deletes a RANGE, "
        f"so it must not run against a reordered header.")

    # 1. Unmerge the ENTIRE tab, super-header included. Deleting a column out from under a live merge
    #    leaves it half-applied and every later remerge fights it.
    sh.batch_update({"requests": [{"unmergeCells": {"range": {"sheetId": ws.id}}}]})
    print("unmerged Hero (super-header + data)")

    # 2. Rename Apply -> Legacy action, in place. It keeps the slot, so nothing downstream shifts.
    ws.update_acell(f"{col_letter(at)}{hr + 1}", KEY)

    # 3. Delete the four now-dead columns. Cell VALUES to the right shift left with them, which is why
    #    the 'Effect' super-header text needs no repositioning — only 'Action' does (step 4).
    sh.batch_update({"requests": [{"deleteDimension": {"range": {
        "sheetId": ws.id, "dimension": "COLUMNS",
        "startIndex": at + 1, "endIndex": at + 5}}}]})
    print(f"deleted 4 columns ({', '.join(AXES[1:])}) — Hero is now {ws.col_count - 4} columns wide")

    # 4. Rebuild the super-header over the WIDENED action region.
    vals = ws.get_all_values()
    hr = header_row(vals)
    c = cols(vals[hr])
    assert vals[hr][c[KEY]].strip() == KEY, "the rename did not land"

    a0, a1 = c[ACTION_REGION[0]], c[ACTION_REGION[1]]
    e0, e1 = c[EFFECT_REGION[0]], c[EFFECT_REGION[1]]
    ws.batch_update([
        {"range": f"{col_letter(at)}{hr}", "values": [[""]]},      # the old banner cell, mid-region
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
    print(f"super-header: 'Action' over {ACTION_REGION[0]}..{ACTION_REGION[1]} "
          f"(cols {a0}-{a1}), 'Effect' over {EFFECT_REGION[0]}..{EFFECT_REGION[1]} (cols {e0}-{e1})")
    print("\nNow run sync.py — it fills the Legacy action values and rebuilds the data merges.")


if __name__ == "__main__":
    main()
