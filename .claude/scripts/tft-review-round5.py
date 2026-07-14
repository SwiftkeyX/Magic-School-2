"""Round 5: Kalista's Count, Soraka's merged heal, and a per-effect Condition.

Run from repo-root cwd:  python .claude/scripts/tft-review-round5.py

  1. KALISTA IS COUNT 1, NOT 6. "It was a projectile that when hit, the enemy got +6 impale."
     One projectile. Six STACKS. I had read '6 spears' as six action instances and set Count 6 /
     Spread 'Same target'.

     That is a misuse of the column, and a tempting one: Count is how many times the ACTION FIRES,
     not how much the EFFECT grants. Akshan's 6 shots are 6 projectiles, each its own hitbox, each
     able to miss - Count 6 is right there. Kalista fires ONE projectile that cannot miss twice and
     lands 6 stacks on impact - that is a magnitude, and magnitudes live in Amount. Written up as
     'Note - Count vs Amount' so the next person does not make the same read.

  2. SORAKA'S TWO HEALS ARE ONE STEP. "This are the same heal, so it should be combined into same
     step." They are: one cast, healing one ally, with a bonus if that ally is below 50% HP.

     This forces a schema change. Condition sat in the ACTION BLOCK - merged down every effect row
     of an action, so it could only ever gate the WHOLE action. That is exactly why the bonus heal
     was split into its own step: there was nowhere to say "this effect is conditional, that one is
     not". Merging the steps means CONDITION BECOMES PER-EFFECT: her base heal has no condition,
     and the row below it does.

     Existing actions are unaffected - a condition that gates the whole action simply repeats down
     that action's rows. But the column is no longer merged, and that is the honest shape: some
     conditions gate an action, some gate a single effect, and only a per-row column can say which.
"""

from tft_sheet import D, SAME, col_letter, cols, open_sheet, post_replies

# (champion, step) -> {column: value}
HERO_FIXES = {
    # One projectile, six stacks. Not six projectiles.
    ("Kalista", "3"): {"Count": "1", "Spread": D},
}

# (champion, category, detail, step) -> {column: value}
AMOUNT_FIXES = {
    ("Kalista", "Status", "Impale", "3"): {"Amount": "6 spears"},
}

COLUMN_EXPLAIN_NOTES = [
    ["Note - Count vs Amount",
     "Count is how many times the ACTION FIRES. It is not how much the EFFECT grants.",
     "The trap: Kalista's active reads 'impale 6 spears', and that looks like Count 6. It is not - "
     "she fires ONE projectile which lands 6 stacks on impact, so Count = 1 and the 6 lives in "
     "Amount. Compare Akshan: his 6 shots are 6 SEPARATE projectiles, each its own hitbox, each "
     "able to miss independently - that is Count 6. Ask: could one of them miss while another "
     "hits? If yes it is Count. If the number can only ever be all-or-nothing, it is an Amount."],
    ["Note - Condition is PER-EFFECT",
     "Condition is NOT part of the action block. A single effect row can be gated while its "
     "siblings are not.",
     "Soraka forced this: one cast heals the lowest-HP ally, and heals them AGAIN if they are "
     "below 50% HP. Same action, same target, same effect - one row gated, one not. While "
     "Condition was merged across the action it could only gate the WHOLE action, so the bonus "
     "heal had to be faked as a separate step; that was a workaround for a missing capability, not "
     "a modelling decision. Condition is now per-EFFECT-ROW. It may still LOOK merged on most "
     "champions - when every effect of an action shares one condition, merging the identical value "
     "is just display. The rule is that it CAN be split, and Soraka's is."],
]

# The note above is appended once; if its text changes later, notes-append will not update it - so
# it is also listed here, where it IS rewritten in place.
COLUMN_EXPLAIN_EDITS = {
    "Note - Condition is PER-EFFECT": {
        1: "Condition is NOT part of the action block. A single effect row can be gated while its "
           "siblings are not.",
        2: "Soraka forced this: one cast heals the lowest-HP ally, and heals them AGAIN if they "
           "are below 50% HP. Same action, same target, same effect - one row gated, one not. "
           "While Condition was merged across the action it could only gate the WHOLE action, so "
           "the bonus heal had to be faked as a separate step; that was a workaround for a missing "
           "capability, not a modelling decision. Condition is now per-EFFECT-ROW. It may still "
           "LOOK merged on most champions - when every effect of an action shares one condition, "
           "merging the identical value is just display. The rule is that it CAN be split, and "
           "Soraka's is.",
    },
}

REPLIES = [
    ("This one is 1 count",
     "Corrected - Kalista is Count 1, Spread em-dash, and the 6 moved into Amount ('6 spears').\n\n"
     "You caught me misusing the column. Count is how many times the ACTION FIRES; I read '6 "
     "spears' as six instances when it is one projectile landing six stacks.\n\n"
     "The test that separates them, which I did not have before: COULD ONE OF THEM MISS WHILE "
     "ANOTHER HITS? Akshan's 6 shots are 6 separate projectiles, each its own hitbox, each able to "
     "miss on its own - that is Count 6. Your spears cannot: they are all-or-nothing on a single "
     "impact, so the 6 is a magnitude, and magnitudes live in Amount.\n\n"
     "Written up as 'Note - Count vs Amount' in Column Explain, because it is exactly the kind of "
     "thing that gets re-broken later."),

    ("This are the same heal",
     "Combined - Soraka's two heals are now one step (two effect rows), and that required a schema "
     "change worth explaining.\n\n"
     "Condition used to be part of the ACTION BLOCK: merged down every effect row, so it could "
     "only ever gate the WHOLE action. That is the ONLY reason the bonus heal was a separate step "
     "- there was nowhere to say 'this effect is conditional, that one is not'. Splitting it was a "
     "workaround for a missing capability, not a real modelling decision, and you were right that "
     "it reads wrong.\n\n"
     "So CONDITION IS NOW PER-EFFECT. Her step 1 holds both heals: the base one with no condition, "
     "and the bonus one gated by 'If Ally Below 50% HP' on its own row.\n\n"
     "Nothing else breaks - a condition that gates a whole action just repeats down that action's "
     "rows. And the column is now honest about something that was always true: some conditions "
     "gate an action, some gate a single effect. Recorded as 'Note - Condition is PER-EFFECT'."),
]


# Soraka's block, stated OUTRIGHT rather than patched.
#
# The first version of this function MUTATED whatever it found - "take the row whose Step is 2 and
# fold it into step 1". It was not idempotent, and it ate her stars: run 1 folded the bonus heal
# and renumbered the star step from 3 to 2, so run 2 found THAT row as "the row whose Step is 2",
# blanked its action cells and merged them away. Spawn At Target, Count 5 and the Re-picked spread
# were destroyed by the second run of a script that had worked perfectly on the first.
#
# The fix is not a better guard. It is to stop mutating: declare the three rows and write them, so
# the outcome does not depend on what the previous run left behind.
SORAKA_ROWS = [
    # step 1, row A - the base heal
    {"Step": "1", "Skill Type": "Active", "Trigger": "On Cast", "Condition": D,
     "Action Source": "Self", "Action": "Cast", "Count": "1", "Spread": D, "Collision": "None",
     "Aim Target": "Lowest-HP Ally",
     "Effect Recipient": SAME, "Effect Category": "Buff", "Effect Detail": "Heal",
     "Amount": "140/160/180% AP", "Scaling": D, "Cadence": "Once", "Duration": D, "AOE": D,
     "Cast": D},
    # step 1, row B - the SAME heal again, gated. Only a per-effect Condition can say this.
    {"Step": "", "Skill Type": "", "Trigger": "", "Condition": "If Ally Below 50% HP",
     "Action Source": "", "Action": "", "Count": "", "Spread": "", "Collision": "",
     "Aim Target": "",
     "Effect Recipient": SAME, "Effect Category": "Buff", "Effect Detail": "Heal",
     "Amount": "140/160/180% AP", "Scaling": "additional heal", "Cadence": "Once", "Duration": D,
     "AOE": D, "Cast": D},
    # step 2 - the falling stars (was step 3, before the heals became one step)
    {"Step": "2", "Skill Type": "Active", "Trigger": "After Cast", "Condition": D,
     "Action Source": "Self", "Action": "Spawn At Target", "Count": "5",
     "Spread": "Re-picked per instance", "Collision": "Target-Only",
     "Aim Target": "Nearest enemy to the healed ally",
     "Effect Recipient": SAME, "Effect Category": "Attack", "Effect Detail": "Damage",
     "Amount": "120/180/280% AP", "Scaling": D, "Cadence": "Over Time", "Duration": "5", "AOE": D,
     "Cast": D},
]

# merged down step 1's two rows. Condition is NOT here - that is the whole point.
SORAKA_MERGE = ["Step", "Skill Type", "Trigger", "Action Source", "Action", "Count", "Spread",
                "Collision", "Aim Target"]


def rebuild_soraka(sh):
    """Write Soraka's 3 rows from SORAKA_ROWS, and re-merge her action block correctly."""
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    c = cols(vals[0])

    rows = [i for i in range(1, len(vals)) if _champ_at(vals, c, i) == "Soraka"]
    if len(rows) != len(SORAKA_ROWS):
        raise SystemExit(f"Soraka has {len(rows)} rows, expected {len(SORAKA_ROWS)} — not touching")
    top, bottom = rows[0], rows[-1]

    edits = []
    for i, spec in zip(rows, SORAKA_ROWS):
        for name, value in spec.items():
            if vals[i][c[name]] != value:
                edits.append({"range": f"{col_letter(c[name])}{i + 1}", "values": [[value]]})
    if not edits:
        print("Hero: Soraka's block already correct")
        return

    # unmerge the action columns across her whole block before rewriting, or a merged cell
    # swallows the write
    sh.batch_update({"requests": [{"unmergeCells": {
        "range": {"sheetId": ws.id, "startRowIndex": top, "endRowIndex": bottom + 1,
                  "startColumnIndex": c["Step"], "endColumnIndex": c["Aim Target"] + 1},
    }}]})
    ws.batch_update(edits, value_input_option="RAW")
    # re-merge only step 1's two rows, and only the action block - never Condition
    sh.batch_update({"requests": [{"mergeCells": {
        "range": {"sheetId": ws.id, "startRowIndex": top, "endRowIndex": top + 2,
                  "startColumnIndex": c[n], "endColumnIndex": c[n] + 1},
        "mergeType": "MERGE_COLUMNS",
    }} for n in SORAKA_MERGE]})
    print(f"Hero: rebuilt Soraka rows {top + 1}-{bottom + 1} ({len(edits)} cells); "
          f"both heals in step 1, Condition per-effect, stars intact as step 2")


def _champ_at(vals, c, i):
    for k in range(i, 0, -1):
        if vals[k][c["Champion"]].strip():
            return vals[k][c["Champion"]].strip()
    return ""


def fix_hero(sh):
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    c = cols(vals[0])
    edits, champ = [], ""
    for i, r in enumerate(vals):
        if i == 0:
            continue
        if r[c["Champion"]].strip():
            champ = r[c["Champion"]].strip()
        step = r[c["Step"]].strip()
        key = (champ, r[c["Effect Category"]].strip(), r[c["Effect Detail"]].strip(), step)
        for column, value in {**HERO_FIXES.get((champ, step), {}),
                              **AMOUNT_FIXES.get(key, {})}.items():
            if r[c[column]] != value:
                edits.append({"range": f"{col_letter(c[column])}{i + 1}", "values": [[value]]})
    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Hero: {len(edits)} cells corrected (Kalista Count 1, 6 spears -> Amount)")


def add_notes(sh):
    ws = sh.worksheet("Column Explain")
    vals = ws.get_all_values()
    seen = {r[0].strip() for r in vals if r}
    notes = [n for n in COLUMN_EXPLAIN_NOTES if n[0] not in seen]
    if notes:
        ws.append_rows(notes, value_input_option="RAW")
        vals = ws.get_all_values()

    edits = []
    for label, columns in COLUMN_EXPLAIN_EDITS.items():
        i = next((k for k, r in enumerate(vals) if r[0].strip() == label), None)
        if i is None:
            raise SystemExit(f"Column Explain: row '{label}' not found")
        for col, text in columns.items():
            if vals[i][col] != text:
                edits.append({"range": f"{col_letter(col)}{i + 1}", "values": [[text]]})
    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Column Explain: {len(notes)} notes appended, {len(edits)} cells updated")


def main():
    sh = open_sheet()
    fix_hero(sh)
    rebuild_soraka(sh)
    add_notes(sh)
    post_replies(REPLIES, warn_unmatched=False)


if __name__ == "__main__":
    main()
