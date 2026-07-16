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

from sheet import (D, HERO_COLUMNS, IDENTITY_BLOCK, RUN_COLUMNS, col_letter, cols, open_sheet,
                   remerge_hero)

DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")

HERO = "Hero"
# Reference tabs are plain tables - synced positionally. Only `Hero` has a logical column schema.
# The lumped v1 `Action Model` tab retired when Hero migrated to the decomposed axes (Apply/Spawn/
# Motion/Behavior/Shape). Those axes' vocab lives in the *-types.csv files below, checked by validate();
# they are validation-only (no sheet mirror yet — a combined vocab tab can come later).
REFERENCE = {
    "Column Explain": "column-explain.csv",
    "Effect Types": "effect-types.csv",
    "Collision Types": "collision-types.csv",
    "Scaling Types": "scaling-types.csv",
    "Spread Types": "spread-types.csv",
    "Design Notes": "design-notes.csv",
}


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


# Columns that get MERGED, and so read back as "" on every row but the first of their run. A blank
# in one of these means "same as the row above" - on BOTH sides of the comparison.
# AOE and Offset join the merged set: both are per-ACTION properties, blank on an action's
# continuation effect rows (which inherit them) and merged across them for display.
MERGED_COLUMNS = set(IDENTITY_BLOCK) | set(RUN_COLUMNS) | {"AOE", "Offset"}


def fill_down(seq):
    """Resolve a merged column to its EFFECTIVE values: a blank inherits the row above."""
    out, prev = [], ""
    for v in seq:
        if v.strip():
            prev = v
        out.append(prev)
    return out


def sync_hero(sh):
    """Sync Hero by LOGICAL COLUMN NAME, so a renamed or inserted column cannot misalign the write.

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
    ws = sh.worksheet(HERO)
    sheet = trim(ws.get_all_values())
    want = trim(read_csv("hero.csv"))

    sc = cols(sheet[0])     # logical name -> column index in the SHEET
    wc = cols(want[0])      # logical name -> column index in the CSV
    check_rows(HERO, len(sheet), len(want))

    if len(want) > len(sheet):
        need = len(want) + 1
        if ws.row_count < need:
            ws.add_rows(need - ws.row_count)
        sheet += [[""] * len(sheet[0]) for _ in range(len(want) - len(sheet))]

    edits = []
    for name in HERO_COLUMNS:                       # row 0 is the header - NEVER written
        have = [cell(sheet[i], sc[name]) for i in range(1, len(want))]
        mine = [cell(want[i], wc[name]) for i in range(1, len(want))]
        if name in MERGED_COLUMNS:
            have, mine = fill_down(have), fill_down(mine)
        for k, (a, b) in enumerate(zip(have, mine)):
            if a != b:
                edits.append({"range": f"{col_letter(sc[name])}{k + 2}", "values": [[b]]})

    if edits:
        # Unmerge first, or a merged cell silently eats the write. remerge_hero() rebuilds the
        # layout from the values afterwards.
        sh.batch_update({"requests": [{"unmergeCells": {"range": {
            "sheetId": ws.id, "startRowIndex": 1, "endRowIndex": len(sheet),
            "startColumnIndex": 0,
            "endColumnIndex": max(sc[n] for n in RUN_COLUMNS + ["AOE", "Offset"]) + 1}}}]})
        ws.batch_update(edits, value_input_option="RAW")
    print(f"{HERO}: {len(edits)} cells updated ({len(want) - 1} rows)")
    return bool(edits)


def sync_reference(sh):
    changed = 0
    for tab, name in REFERENCE.items():
        ws = sh.worksheet(tab)
        sheet = trim(ws.get_all_values())
        want = trim(read_csv(name))
        check_rows(tab, len(sheet), len(want))

        if len(want) > len(sheet):
            need = len(want) + 1
            if ws.row_count < need:
                ws.add_rows(need - ws.row_count)
            sheet += [[] for _ in range(len(want) - len(sheet))]

        edits = []
        for i in range(len(want)):
            for j in range(len(want[i])):
                if cell(sheet[i], j) != cell(want[i], j):
                    edits.append({"range": f"{col_letter(j)}{i + 1}",
                                  "values": [[cell(want[i], j)]]})
        if edits:
            ws.batch_update(edits, value_input_option="RAW")
        changed += len(edits)
        print(f"{tab}: {len(edits)} cells updated")
    return changed > 0


def validate(sh):
    """No value used in Hero may be undefined in its reference tab.

    This is the invariant the old `tft-action-templates.py` was checking by hand. It is the thing
    that actually goes wrong when the schema moves: a champion keeps a value whose definition was
    renamed out from under it, and nothing notices.
    """
    hero = trim(read_csv("hero.csv"))
    c = cols(hero[0])

    def used(name):
        return {cell(r, c[name]).strip() for r in hero[1:]} - {"", D}

    def defined(csv_name, col=0):
        return {cell(r, col).strip() for r in read_csv(csv_name)[1:]} - {""}

    pairs = {(cell(r, c["Effect Category"]).strip(), cell(r, c["Effect Detail"]).strip())
             for r in hero[1:]} - {("", "")}
    effects = {(cell(r, 0).strip(), cell(r, 1).strip()) for r in read_csv("effect-types.csv")[1:]}

    problems = []
    for label, missing in (
        ("Apply",        used("Apply") - defined("apply-types.csv")),
        ("Spawn",        used("Spawn") - defined("spawn-types.csv")),
        ("Motion",       used("Motion") - defined("motion-types.csv")),
        ("Behavior",     used("Behavior") - defined("behavior-types.csv")),
        ("Shape",        used("Shape") - defined("shape-types.csv")),
        ("Collision",    used("Collision") - defined("collision-types.csv")),
        ("Scaling Type", used("Scaling Type") - defined("scaling-types.csv")),
        ("Spread",       used("Spread") - defined("spread-types.csv")),
    ):
        if missing:
            problems.append(f"{label}: {sorted(missing)} used in Hero but not defined")

    orphan = {p for p in pairs if p not in effects and all(p)}
    if orphan:
        problems.append(f"Effect: {sorted(orphan)} used in Hero but not defined")

    if problems:
        print("VALIDATE: FAILED")
        for p in problems:
            print(f"  !! {p}")
        raise SystemExit(1)
    print("VALIDATE: ok — every value used in Hero is defined in its reference tab")


def main():
    sh = open_sheet()
    hero_changed = sync_hero(sh)
    sync_reference(sh)
    if hero_changed:
        # Merges are DERIVED from the values, so they only need recomputing when the values move.
        remerge_hero(sh)
    validate(sh)


if __name__ == "__main__":
    main()
