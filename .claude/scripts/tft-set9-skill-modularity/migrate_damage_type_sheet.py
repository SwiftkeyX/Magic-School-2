"""ONE-SHOT SHEET SIDE (2026-07-21): open the `Damage Type` column on both schema tabs.

    python .claude/scripts/tft-set9-skill-modularity/migrate_damage_type_sheet.py [--apply]

Run AFTER migrate_role_damage.py has updated the CSVs, and BEFORE force_full/sync — sync_hero
resolves columns through `cols(sheet_header)` and never writes a header row itself, so a column
that exists in the CSV but not on the tab makes it raise rather than misalign (which is the
behaviour we want, but it means the header has to be opened here first).

Three things, in this order, per tab:
  1. insertDimension a blank column at index 3, directly after `Role`.
  2. Write `Damage Type` into the real header row (the tabs carry a merged super-header above it,
     so the header is not row 1 — header_row() finds it by locating the `Champion` column).
  3. REPAIR the 'Action' / 'Effect' super-header merges. Google shifts merge ranges itself when a
     column is inserted before them, but this asserts the end state instead of trusting it: a
     half-applied header merge SILENTLY SWALLOWS writes to the columns beneath it (invariant #8),
     and the symptom — the same N cells rewritten every sync, only the first column sticking — is
     slow to recognise and costs a full rebuild.

Idempotent: a tab that already has the column is skipped, so a partial run is safe to repeat.
"""

import sys

sys.path.insert(0, ".claude/scripts/tft-set9-skill-modularity")

from sheet import SCHEMA_TABS, col_letter, header_row, open_sheet   # noqa: E402

NEW_COL = "Damage Type"
AFTER = "Role"


def super_header_merges(sheet_id, header, hr):
    """The two merged banner cells above the column names: 'Action' over Action Source..Cast, and
    'Effect' over the effect block. Derived from the header BY NAME so they land correctly however
    many columns have been inserted — the old spans (14-24, 24-32) were literals and this migration
    is precisely the event that invalidates a literal."""
    names = [c.strip() for c in header]
    action_start = names.index("Action Source")
    effect_start = names.index("Effect Recipient")
    return [(action_start, effect_start), (effect_start, len(names))]


def main():
    apply = "--apply" in sys.argv
    sh = open_sheet()
    meta = {s["properties"]["title"]: s for s in sh.fetch_sheet_metadata()["sheets"]}

    for tab in SCHEMA_TABS:
        ws = sh.worksheet(tab)
        vals = ws.get_values()
        hr = header_row(vals)
        header = vals[hr]
        if NEW_COL in [c.strip() for c in header]:
            print("%s: already has %s — skipped" % (tab, NEW_COL))
            continue
        at = [c.strip() for c in header].index(AFTER) + 1

        new_header = header[:at] + [NEW_COL] + header[at:]
        want = super_header_merges(ws.id, new_header, hr)
        print("%s: insert col %s (%s), header row %d, banners -> %s"
              % (tab, col_letter(at), NEW_COL, hr + 1, want))
        if not apply:
            continue

        # PHASE 1 — insert, alone in its own batch. It CANNOT share a batch with the merge repair
        # below: Google applies requests in order and shifts existing merges as part of the insert,
        # so an unmerge naming the pre-insert span (14-24) then addresses a range that is no longer
        # a whole merged block, and the API rejects the ENTIRE batch with "You must select all cells
        # in a merged range". Batches are atomic, so that failure is safe — but it is also silent
        # about which half was wrong. Two phases, each verified.
        sh.batch_update({"requests": [{"insertDimension": {
            "range": {"sheetId": ws.id, "dimension": "COLUMNS",
                      "startIndex": at, "endIndex": at + 1},
            # False: do NOT inherit Role's formatting/validation. This is a different vocabulary,
            # and inheriting a dropdown from Role would silently reject every AD/AP value.
            "inheritFromBefore": False}}]})
        ws.update(values=[[NEW_COL]], range_name="%s%d" % (col_letter(at), hr + 1),
                  value_input_option="RAW")

        # PHASE 2 — assert the banners rather than trust the auto-shift. If they already moved
        # correctly this is a no-op; if they did not, a half-covered banner SILENTLY SWALLOWS every
        # later write to the columns beneath it (invariant #8).
        fresh = {s["properties"]["title"]: s
                 for s in sh.fetch_sheet_metadata()["sheets"]}[tab].get("merges", [])
        have = sorted((m["startColumnIndex"], m["endColumnIndex"])
                      for m in fresh if m.get("startRowIndex", 0) < hr)
        if have == sorted(want):
            print("   inserted; banners auto-shifted correctly %s" % have)
            continue
        reqs = [{"unmergeCells": {"range": {
            "sheetId": ws.id, "startRowIndex": 0, "endRowIndex": hr,
            "startColumnIndex": a, "endColumnIndex": b}}} for a, b in have]
        reqs += [{"mergeCells": {"range": {
            "sheetId": ws.id, "startRowIndex": 0, "endRowIndex": hr,
            "startColumnIndex": a, "endColumnIndex": b},
            "mergeType": "MERGE_ALL"}} for a, b in want]
        sh.batch_update({"requests": reqs})
        print("   inserted; banners REPAIRED %s -> %s" % (have, want))

    if not apply:
        print("\nDry run — nothing written. Re-run with --apply.")
    else:
        print("\nNext: force_full.py for BOTH tabs, then sync.py twice (space calls ~30s: the read "
              "quota is 60/min and sync reads every tab).")


if __name__ == "__main__":
    main()
