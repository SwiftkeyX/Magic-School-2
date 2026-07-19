"""Write `data/*.csv` to the `tft-set9-skill` sheet. THE one writer.

Run from repo-root cwd:  python .claude/scripts/tft-set9-skill-modularity/sync.py

This replaces 17 scripts and ~5,000 lines. The CSVs under `data/` are the source of truth; this
script makes the sheet match them, derives every merge from the values, and then checks the sheet's
own invariants.

WHY ONE WRITER
--------------
The old suite was 4 origin scripts + 8 review-round scripts + 3 reference scripts, ALL re-run on
every pass. Any two of them could write the same cell, and then they overwrote each other on every
run, for ever. That bug was found three times, and two of those three only existed BECAUSE the
scripts were re-run - a one-shot migration cannot fight anything if it is never run again.

One writer per cell was the rule. One writer, full stop, is the rule enforced by construction.

TO MAKE A CHANGE: edit the CSV, run this. The git diff shows exactly which cells moved.

THE THREE RULES THIS SCRIPT IS BUILT AROUND
-------------------------------------------
1. COLUMNS ARE ADDRESSED BY NAME, never by index. The user renames headers ("Collision (If it have
   one)") and columns have been inserted mid-table before; every script that said `r[14]` started
   writing into the wrong column the moment that happened. `cols()` resolves off the sheet's own
   header row, and the CSV is mapped to it by logical name.

2. A BLANK CELL IS DATA. A merged cell reads back "" on every row but its first, so a blank means
   "same as the row above". It must round-trip as a blank. `Step` especially: it is what the merge
   reads to find step BOUNDARIES, so filling a continuation row makes it look like a new step start.

3. NEVER SILENTLY DELETE. If the sheet has more rows than the CSV, this stops and says so.
"""

import csv
import pathlib

from sheet import (HERO_COLUMNS, IDENTITY_BLOCK, MERGED_REFERENCE, REFERENCE, RUN_COLUMNS,
                   SCHEMA_TABS, col_letter, cols, header_row, open_sheet, record_changes,
                   remerge_hero, remerge_reference, unmerge_reference, validate_data)

DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")


def read_csv(name):
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return [r for r in csv.reader(f)]


def trim(vals):
    """Drop trailing all-blank rows - the grid is padded with empties and they are not data."""
    vals = list(vals)
    while vals and not any(c.strip() for c in vals[-1]):
        vals.pop()
    return vals


def cell(row, i):
    return row[i] if len(row) > i else ""


def check_rows(tab, sheet_rows, csv_rows):
    if sheet_rows > csv_rows:
        raise SystemExit(
            f"{tab}: the sheet has {sheet_rows} rows but the CSV has {csv_rows}. Refusing to run - "
            f"syncing would leave {sheet_rows - csv_rows} orphaned rows, and DELETING them is not "
            f"something this script will do behind your back. Re-export, or delete them explicitly.")


def check_cols(tab, sheet_cols, csv_cols):
    """The same guard as check_rows, for COLUMNS - and it exists because its absence CORRUPTED a tab.

    Reference tabs are written POSITIONALLY. Remove a column from the middle of a CSV and every column
    after it shifts left by one, so the write lands each value one column early and the sheet's last
    column is simply orphaned - keeping its old data as a duplicate. That is what happened when
    `Cast (s)` was dropped from action-model.csv: the tab silently became
    `... Collision | What it does | Clarify more | Clarify more(stale)`, and `export.py` then wrote
    the mess back into the CSV.

    It is not detectable downstream: the row counts match, VALIDATE passes (it reads the CSV, not the
    sheet), and sync reports 0 because the sheet now equals what it wrote. Only the export round-trip
    catches it. So: refuse, exactly as check_rows does, and make the caller delete the column on
    purpose.
    """
    if sheet_cols > csv_cols:
        raise SystemExit(
            f"{tab}: the sheet has {sheet_cols} columns but the CSV has {csv_cols}. Refusing to run - "
            f"a positional write would shift every column left and leave column {sheet_cols} orphaned "
            f"with stale data. DELETING a column is not something this script will do behind your "
            f"back: delete it explicitly (deleteDimension), then sync.")


# Columns that get MERGED, and so read back as "" on every row but the first of their run. A blank
# in one of these means "same as the row above" - on BOTH sides of the comparison.
# AOE and Offset join the merged set: both are per-ACTION properties, blank on an action's
# continuation effect rows (which inherit them) and merged across them for display.
MERGED_COLUMNS = set(IDENTITY_BLOCK) | set(RUN_COLUMNS) | {"AOE", "Offset"}


def fill_down(seq, starts=()):
    """Resolve a merged column to its EFFECTIVE values: a blank inherits the row above.

    `starts` RESETS the inheritance — a blank at a block start inherits nothing, because a merge never
    crosses that boundary. Pass the champion-start rows for the identity block.

    WHY THIS MATTERS (it corrupted 9 champions): identity merges are bounded by the CHAMPION
    (remerge_hero merges IDENTITY_BLOCK from one champion-start to the next), but this filled down the
    WHOLE column. A champion with no Class 2 has a genuinely blank cell — and a whole-column fill_down
    reads it as "same as above" and hands them the PREVIOUS champion's class. It stayed invisible for
    every existing champion, because `have` and `mine` filled down identically so nothing was written;
    it only fires on an APPEND, where the sheet has no row yet, the two sides disagree, and sync writes
    the filled value. Illaoi was given Graves' 'Gunner'; six champions were given Gangplank's
    'Reaver King' and Naafari's 'Shurima'.
    """
    out, prev = [], ""
    for i, v in enumerate(seq):
        if i in starts:
            prev = ""
        if v.strip():
            prev = v
        out.append(prev)
    return out


def ensure_schema_tab(sh, tab, csv_name):
    """Create a schema tab that is DECLARED (in SCHEMA_TABS) but absent from the sheet, seeding it
    with the CSV's header row. `Hero set 10` started life this way.

    Same act as add_rows / sync_reference's tab-create: the CSV already says the tab exists, so making
    room for it is not restructuring. The header MUST be seeded here because sync_hero never writes the
    header row (`for name in HERO_COLUMNS: the header rows are NEVER written`) — without a header,
    cols() would have nothing to resolve against. A single header row is enough: header_row() finds the
    `Champion` column whether or not a super-header is later added above it by hand.
    """
    if tab in {w.title for w in sh.worksheets()}:
        return
    want = trim(read_csv(csv_name))
    header = want[header_row(want)]
    ws = sh.add_worksheet(title=tab, rows=len(want) + 5, cols=len(header))
    ws.update(values=[header], range_name="A1", value_input_option="RAW")
    print(f"{tab}: created (declared schema tab, absent from the sheet) — header seeded")


def sync_hero(sh, tab, csv_name):
    """Sync a schema tab by LOGICAL COLUMN NAME, so a renamed or inserted column cannot misalign the
    write. `tab`/`csv_name` select which schema tab (`Hero set 9`/`hero.csv` or `Hero set 10`/its CSV).

    THE COMPARISON HAS TO SURVIVE ITS OWN MERGING, and getting that wrong is a stable infinite loop.

    A merged cell reads back as "" on every row but its first. So when a hand-edit collapses a step,
    the re-merge swallows the continuation row's Trigger into the row above - the SHEET now reads ""
    there while the CSV still names the value. Compare those raw and they differ for ever: write,
    merge, blank, write. The second run is the only thing that catches it.

    So: for merged columns, compare EFFECTIVE against EFFECTIVE (blank = "same as above", on both
    sides) and write the FILLED value - the re-merge absorbs the duplicate by itself, which is what
    makes the rewrite converge.

    STEP AND SKILL TYPE ARE THE EXCEPTION, and they must stay one. `Step` is what remerge_hero()
    reads to find the step BOUNDARIES: fill a continuation row and it looks like a NEW STEP START, so
    it never merges away. They are compared RAW and written LITERALLY, blanks included.
    """
    ensure_schema_tab(sh, tab, csv_name)
    ws = sh.worksheet(tab)
    sheet = trim(ws.get_all_values())
    want = trim(read_csv(csv_name))

    # The Hero tab carries a merged super-header ('Action'/'Effect') ABOVE its column names, so its
    # real header is row `shr` and data starts at `shr+1`. The CSV stays single-header (row 0). Align
    # the two by DATA row, not by absolute index — otherwise the super-header shifts everything by one.
    shr, whr = header_row(sheet), header_row(want)
    sc = cols(sheet[shr])   # logical name -> column index in the SHEET
    wc = cols(want[whr])    # logical name -> column index in the CSV
    n = len(want) - (whr + 1)                       # number of DATA rows (from the CSV)
    check_rows(tab, len(sheet) - (shr + 1), n)

    need = shr + 1 + n                              # header rows + data rows
    if need + 1 > ws.row_count:
        ws.add_rows(need + 1 - ws.row_count)
    if len(sheet) < need:
        sheet += [[""] * len(sheet[shr]) for _ in range(need - len(sheet))]

    # An identity merge is bounded by the CHAMPION, so its fill_down must reset there. Take the
    # boundaries from the CSV (the source of truth) — the sheet may not have the rows yet on an append.
    champ_starts = {k for k in range(n) if cell(want[whr + 1 + k], wc["Champion"]).strip()}

    edits = []
    for name in HERO_COLUMNS:                       # the header rows are NEVER written
        have = [cell(sheet[shr + 1 + k], sc[name]) for k in range(n)]
        mine = [cell(want[whr + 1 + k], wc[name]) for k in range(n)]
        if name in MERGED_COLUMNS:
            starts = champ_starts if name in IDENTITY_BLOCK else ()
            have, mine = fill_down(have, starts), fill_down(mine, starts)
        for k, (a, b) in enumerate(zip(have, mine)):
            if a != b:
                edits.append({"range": f"{col_letter(sc[name])}{shr + 2 + k}", "values": [[b]]})

    if edits:
        # Unmerge first, or a merged cell silently eats the write. remerge_hero() rebuilds the
        # layout afterwards. Start below the header rows so the super-header merge is left intact.
        sh.batch_update({"requests": [{"unmergeCells": {"range": {
            "sheetId": ws.id, "startRowIndex": shr + 1, "endRowIndex": need,
            "startColumnIndex": 0,
            "endColumnIndex": max(sc[n2] for n2 in RUN_COLUMNS + ["AOE", "Offset"]) + 1}}}]})
        ws.batch_update(edits, value_input_option="RAW")
    record_changes(tab, [e["range"] for e in edits])   # for highlight_changes.py to colour
    print(f"{tab}: {len(edits)} cells updated ({n} rows)")
    return bool(edits)


def sync_reference(sh):
    changed = 0
    have = {w.title for w in sh.worksheets()}
    for tab, name in REFERENCE.items():
        want = trim(read_csv(name))
        if tab not in have:
            # A tab named in TABS is DECLARED, so creating it is the same kind of act as add_rows -
            # making room for what the CSV already says. It is not restructuring: the CSV decides.
            sh.add_worksheet(title=tab, rows=len(want) + 5, cols=max(len(r) for r in want))
            print(f"{tab}: created (declared in TABS, absent from the sheet)")

        ws = sh.worksheet(tab)
        # Unmerge FIRST on a merged tab, or a stale merge silently eats every write below its top row.
        if tab in MERGED_REFERENCE:
            unmerge_reference(sh, tab, MERGED_REFERENCE[tab])
        sheet = trim(ws.get_all_values())
        check_rows(tab, len(sheet), len(want))
        check_cols(tab, max((len(r) for r in sheet), default=0), max(len(r) for r in want))

        if len(want) > len(sheet):
            need = len(want) + 1
            if ws.row_count < need:
                ws.add_rows(need - ws.row_count)
            sheet += [[] for _ in range(len(want) - len(sheet))]

        # Grow COLUMNS the same way rows are grown. Without this, adding a column to a reference CSV
        # fails the whole run with "exceeds grid limits" — the write is rejected by the API, so it is
        # loud rather than silent, but it stops sync dead and the tab can never gain a column.
        wide = max(len(r) for r in want)
        if ws.col_count < wide:
            ws.add_cols(wide - ws.col_count)

        edits = []
        for i in range(len(want)):
            for j in range(len(want[i])):
                if cell(sheet[i], j) != cell(want[i], j):
                    edits.append({"range": f"{col_letter(j)}{i + 1}",
                                  "values": [[cell(want[i], j)]]})
        if edits:
            ws.batch_update(edits, value_input_option="RAW")
        record_changes(tab, [e["range"] for e in edits])   # for highlight_changes.py to colour
        if tab in MERGED_REFERENCE:
            remerge_reference(sh, tab, MERGED_REFERENCE[tab])
        changed += len(edits)
        print(f"{tab}: {len(edits)} cells updated")
    return changed > 0


def validate(sh):
    """No value used in a schema tab may be undefined in its reference tab.

    This is the invariant the old `tft-action-templates.py` was checking by hand. It is the thing
    that actually goes wrong when the schema moves: a champion keeps a value whose definition was
    renamed out from under it, and nothing notices.

    The CHECK itself lives in sheet.validate_data() — one implementation, shared with context.py.
    Runs over EVERY schema CSV: Set 10 shares Set 9's reference vocab, so a Set 10 action or effect
    with no defining row is caught here exactly as a Set 9 one is.
    """
    problems = [f"[{csv_name}] {p}" for csv_name in SCHEMA_TABS.values()
                for p in validate_data(csv_name)]
    if problems:
        print("VALIDATE: FAILED")
        for p in problems:
            print(f"  !! {p}")
        raise SystemExit(1)
    print("VALIDATE: ok — every value used in each schema tab is defined in its reference tab")


def main():
    # The flat mirror is DERIVED from the schema CSVs, exactly like the merges are derived from the
    # values — so it is rebuilt here rather than maintained. Doing it before anything is written is
    # what makes drift impossible: there is no state in which the sheet has a flat tab that
    # disagrees with the hero CSVs it came from.
    from flatten import build_flat
    build_flat(verbose=True)

    sh = open_sheet()
    for tab, csv_name in SCHEMA_TABS.items():
        if sync_hero(sh, tab, csv_name):
            # Merges are DERIVED from the values, so they only need recomputing when the values move.
            #
            # THIS MUST RUN BEFORE sync_reference, and that ordering is load-bearing. sync_hero writes
            # the FILLED value into merged columns and depends on this re-merge to absorb the
            # duplicates. If anything between the two raises — a reference tab tripping check_rows,
            # say — the sheet is left filled-but-unmerged, and NO LATER SYNC FIXES IT: the comparison
            # is fill_down on both sides, so a filled continuation and a blank one look identical and
            # every later run reports 0 while the layout is still wrong. That is invariant #6's masking
            # bug reached by a different road, and it happened for real: a Trigger Types row-guard
            # failure skipped the re-merge and left 'After Step 1' written down every continuation row.
            remerge_hero(sh, tab)
    sync_reference(sh)
    validate(sh)


if __name__ == "__main__":
    main()
