"""Round 6: split Scaling, rename the odd Spread, and lift the Notes out of Column Explain.

Run from repo-root cwd:  python .claude/scripts/tft-review-round6.py

  1. SCALING IS THE LAST FREE-TEXT FIELD, and it leaks. 35 rows carry a value and 27 are
     DISTINCT - that is prose, not a vocabulary. Sorting them shows it was fusing four things:

       * a real MODIFIER          "stacking", "decaying 20/13/0%/s", "per Chakram equipped"
       * a DURATION               "rest of combat", "until next cast"      -> Duration column
       * MULTIPLICITY             "x8 arrows in a cone" (Ashe)             -> Count / Spread
       * prose that is not scaling "redirected onto Taric himself"         -> already in Effect Types

     Fixed the way this sheet always fixes it: split the column. `Scaling Type` is a vocabulary
     (defined in the new `Scaling Types` tab) and `Scaling` keeps the specifics - exactly the
     Effect Category / Effect Detail idiom already used two columns to the left.

     The Ashe row is worth naming: "x8 arrows in a cone" is multiplicity, which Count/Spread was
     built to eliminate - and it SURVIVED that cleanup, because the fix only rewrote each action's
     first row and never its continuation rows. It was the last one left.

  2. `Re-picked per instance` was a bad Spread value. The user: "The rest is spread but this one
     isn't." Correct - the other four answer WHERE the instances go (a geometry); that one
     answered WHEN the aim is decided. Renamed to `Each to its own target`, which is a
     where-answer and sits in the family. The re-picking itself is the point of the Clarify text,
     and remains flagged as the mid-action gap.

  3. COLUMN EXPLAIN WAS HALF NOTES - 20 of its 41 rows. A column legend and a decision log are
     different documents: one says what a cell means, the other says why the schema is shaped
     this way and what was ruled out. The notes move to their own `Design Notes` tab.
"""

from tft_sheet import col_letter, cols, open_sheet, post_replies

SCALING_TAB = "Scaling Types"
NOTES_TAB = "Design Notes"
OLD_SPREAD, NEW_SPREAD = "Re-picked per instance", "Each to its own target"

# Scaling Type -> (what it means, examples)
SCALING_TYPES = [
    ["Stacking", "The amount GROWS each time it is applied, and is permanent.",
     "Viego (every attack adds another stack, permanently), Kled, Kalista's spears."],
    ["Decay", "The amount SHRINKS over time until it is gone.",
     "Sion's bonus HP decays 20/13/0% per second; Irelia's shield decays."],
    ["Falloff per hit", "The amount SHRINKS with each unit it passes through.",
     "Sona -33% per hit, Jhin -56% per hit. A pierce that is worth less the deeper it goes."],
    ["Per Stack", "The amount is MULTIPLIED by a counter the caster is holding.",
     "Aphelios deals bonus damage per Chakram equipped; Kalista's true damage is per spear "
     "removed. The counter itself is an Effect (see 'Note - Stacks')."],
    ["Per Tick", "The amount is applied REPEATEDLY while the action runs.",
     "Garen per spin, Swain per second. Pairs with Cadence = Over Time."],
    ["Burst", "The accumulated amount lands ALL AT ONCE, at the end.",
     "Swain and Shen. The opposite of Per Tick."],
    ["Conditional Bonus", "A bonus that applies ONLY when a condition holds.",
     "Cassiopeia +30% if Wounded, Sett +50% if only one enemy was grabbed, Ahri +33% if essence "
     "stolen. The condition is in the Condition column; the size of the bonus is here."],
    ["Derived", "The amount SCALES OFF some OTHER quantity — on top of its own per-star Amount.",
     "Sejuani increases with max Health, Irelia with the damage her shield absorbed, Samira and "
     "Aphelios with AP. NOTE: this does not mean 'not a stat'. The per-star Amount already carries "
     "the ordinary AD/AP scaling (e.g. '200/300/450% AP'); Derived is for a SECOND quantity layered "
     "on top of it. Samira's flat 10/15/20 shred that also grows with AP is exactly that."],
    ["Per Target Hit", "The amount scales with HOW MANY targets were hit.",
     "Renekton +30% AP per additional enemy, Nasus steals from each enemy hit, Aphelios gains "
     "+1 Chakram per enemy hit by the blast."],
    ["Cap", "An upper BOUND on the effect, not a multiplier.",
     "Azir may have at most 3 Sand Soldiers on the board."],
]

SCALING_PROSE = [
    "How to read this tab",
    "Scaling Type says HOW the amount changes; the Scaling column beside it says by how much. "
    "Same split as Effect Category / Effect Detail: a vocabulary, then the specifics.",
    "If a cell here would say how LONG something lasts, it belongs in Duration. If it would say "
    "how MANY instances fire, it belongs in Count / Spread. If it just restates what the effect "
    "is, it belongs nowhere - Effect Types already defines that. Scaling had been holding all "
    "three, which is why it needed a vocabulary.",
]

# (champion, effect detail, old scaling) -> (Scaling Type, Scaling)
# An em-dash on both means the value did not belong in Scaling at all - see MOVED below.
SCALING_FIX = {
    ("Garen", "Damage", "per spin"): ("Per Tick", "per spin"),
    ("Sona", "Damage", "−33% per hit"): ("Falloff per hit", "−33% per hit"),
    ("Cassiopeia", "Damage", "+30% if Wounded"): ("Conditional Bonus", "+30% if Wounded"),
    ("Samira", "DEF", "+AP"): ("Derived", "+AP"),
    ("Kled", "Attack Speed", "stacking"): ("Stacking", "stacking"),
    ("Swain", "Damage", "per second"): ("Per Tick", "per second"),
    ("Swain", "Damage", "burst"): ("Burst", "burst"),
    ("Sion", "Bonus HP", "decaying 20/13/0%/s"): ("Decay", "20/13/0% per second"),
    ("Irelia", "Shield", "decaying"): ("Decay", "decays over its duration"),
    ("Irelia", "Damage", "+30% of damage absorbed"): ("Derived", "+30% of damage absorbed"),
    ("Jhin", "Damage", "−56% per hit"): ("Falloff per hit", "−56% per hit"),
    ("Sett", "Damage", "+50% if only 1 grabbed"): ("Conditional Bonus", "+50% if only 1 grabbed"),
    ("Sett", "Stun", "+50% if only 1 grabbed"): ("Conditional Bonus", "+50% if only 1 grabbed"),
    ("Shen", "Damage", "burst"): ("Burst", "burst"),
    ("Ahri", "Damage", "+33% if essence stolen"): ("Conditional Bonus", "+33% if essence stolen"),
    ("Renekton", "Heal", "+30% AP per additional enemy hit"):
        ("Per Target Hit", "+30% AP per additional enemy hit"),
    ("Azir", "(summon)", "max 3 Soldiers on the board"): ("Cap", "max 3 Soldiers on the board"),
    ("Nasus", "Bonus HP", "stolen from each enemy hit"): ("Per Target Hit", "from each enemy hit"),
    ("Nasus", "AD", "stolen from each enemy hit"): ("Per Target Hit", "from each enemy hit"),
    ("Nasus", "Armor", "stolen from each enemy hit"): ("Per Target Hit", "from each enemy hit"),
    ("Nasus", "MR", "stolen from each enemy hit"): ("Per Target Hit", "from each enemy hit"),
    ("Sejuani", "True Damage", "increased by max Health"): ("Derived", "increased by max Health"),
    ("Viego", "On-Hit Damage", "stacking"): ("Stacking", "stacking"),
    ("Kalista", "Impale", "stacking"): ("Stacking", "stacking"),
    ("Kalista", "True Damage", "per spear removed"): ("Per Stack", "per spear removed"),
    ("Aphelios", "Chakram", "+1 per enemy hit by the blast"):
        ("Per Target Hit", "+1 per enemy hit by the blast"),
    ("Aphelios", "Damage", "per Chakram equipped"): ("Per Stack", "per Chakram equipped"),
    ("Aphelios", "Omnivamp", "of Chakram damage only; increased by AP"):
        ("Derived", "of Chakram damage only; increased by AP"),
}

# Values that were never scaling. (champion, detail, old) -> (Scaling Type, Scaling, {other fixes})
MOVED = {
    # a DURATION, not a scaling
    ("Sona", "Attack Speed", "rest of combat"): ("—", "—", {"Duration": "Permanent"}),
    ("Ahri", "Mana Reave", "until next cast"): ("—", "—", {"Duration": "Until next cast"}),
    # MULTIPLICITY - Count/Spread already carry it. The last surviving leak: the Count/Spread
    # cleanup only rewrote each action's FIRST row, and this sat on a continuation row.
    ("Ashe", "Chill", "×8 arrows in a cone"): ("—", "—", {}),
    # restates what the effect already is; Effect Types defines both
    ("Taric", "Damage Redirect", "redirected onto Taric himself"): ("—", "—", {}),
    ("Soraka", "Heal", "additional heal"): ("—", "—", {}),
    # behaviour, not scaling - preserved as a Design Note instead of as free text in a data cell
    ("K'Sante", "(reposition)", "chases the knocked-back target"): ("—", "—", {}),
}

DESIGN_NOTES = [
    ["Note - K'Sante",
     "His reposition CHASES the enemy he knocked back.",
     "He does not leap to a fixed hex: he follows the flying body. This used to sit in the Scaling "
     "column as prose ('chases the knocked-back target'), which is not a scaling - Scaling now has "
     "a fixed vocabulary, so the fact lives here instead of in a data cell."],
]

REPLIES = [
    ("Scaling should have its own tab",
     "Yes - and the tab alone would not have been enough, so I split the column too.\n\n"
     "The data made the case: 35 rows carry a Scaling value and 27 of them are DISTINCT. That is "
     "prose, not a vocabulary. Sorting them showed the column was fusing FOUR different things:\n\n"
     "  - a real MODIFIER: 'stacking', 'decaying 20/13/0%/s', 'per Chakram equipped'\n"
     "  - a DURATION: 'rest of combat' (Sona), 'until next cast' (Ahri)\n"
     "  - MULTIPLICITY: 'x8 arrows in a cone' (Ashe)\n"
     "  - prose that is not scaling at all: 'redirected onto Taric himself' - which Effect Types "
     "already defines\n\n"
     "So it is split the way this sheet always splits: 'Scaling Type' is the vocabulary (10 values, "
     "defined in the new 'Scaling Types' tab) and 'Scaling' keeps the specifics. That is the same "
     "Effect Category / Effect Detail idiom sitting two columns to its left.\n\n"
     "One thing your question caught that I had missed: the Ashe row. 'x8 arrows in a cone' is "
     "exactly the multiplicity that Count/Spread was built to eliminate - and it SURVIVED that "
     "cleanup, because my fix only rewrote each action's first row and never its continuation "
     "rows. It was the last one left in the sheet. Gone now."),

    ("The rest is spread but this one isn",
     "You are right, and the name was not the real problem - the value was.\n\n"
     "The other four spreads all answer WHERE the instances go: Same target, Cone, Current + Left "
     "+ Right, 360 radial. All geometry. 'Re-picked per instance' answered a different question - "
     "WHEN the aim is decided - which is why no name for it was going to sit right in that "
     "column.\n\n"
     "Renamed to 'Each to its own target'. That IS a where-answer, so it belongs in the family: "
     "the five stars do not converge and do not form a shape - each one goes to its own target. "
     "The re-picking (each star asks again which enemy is closest to the healed ally) is now the "
     "point of its Clarify text rather than of its name.\n\n"
     "The underlying gap is unchanged and still flagged: the model cannot say that something "
     "changes WHILE an action runs. Gwen's hitbox moves; Soraka's aim is re-evaluated. Two cases, "
     "no column yet - a third settles it."),

    ("Should we have this much Note",
     "No - and the count makes the case: Column Explain was 41 rows and 20 of them were Notes. "
     "Half the tab had stopped explaining columns.\n\n"
     "They are two different documents. A column legend says what a cell MEANS; a note says why "
     "the schema is shaped this way, what was ruled out, and what is still broken. Mixing them "
     "means the legend gets buried in decision history.\n\n"
     "All 20 moved to a new 'Design Notes' tab. Column Explain is back to one job: one row per "
     "column, what it means, how to fill it. Nothing was deleted."),
]


def add_scaling_type_column(sh):
    ws = sh.worksheet("Hero")
    header = ws.get_all_values()[0]
    if any(h.strip() == "Scaling Type" for h in header):
        return False
    at = next(i for i, h in enumerate(header) if h.strip() == "Scaling")
    sh.batch_update({"requests": [{"insertDimension": {
        "range": {"sheetId": ws.id, "dimension": "COLUMNS", "startIndex": at, "endIndex": at + 1},
        "inheritFromBefore": True,
    }}]})
    ws.update([["Scaling Type"]], f"{col_letter(at)}1", value_input_option="RAW")
    print(f"Hero: inserted 'Scaling Type' at column {col_letter(at)}")
    return True


def fix_scaling(sh):
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    c = cols(vals[0])
    edits, champ, unknown = [], "", []

    for i, r in enumerate(vals):
        if i == 0:
            continue
        if r[c["Champion"]].strip():
            champ = r[c["Champion"]].strip()
        cur = r[c["Scaling"]].strip()
        if not cur or cur == "—":
            if not r[c["Scaling Type"]].strip():
                edits.append({"range": f"{col_letter(c['Scaling Type'])}{i + 1}",
                              "values": [["—"]]})
            continue

        key = (champ, r[c["Effect Detail"]].strip(), cur)
        if key in SCALING_FIX:
            stype, sval, extra = (*SCALING_FIX[key], {})
        elif key in MOVED:
            stype, sval, extra = MOVED[key]
        else:
            # already converted on a previous run? then Scaling Type is set and we are done
            if r[c["Scaling Type"]].strip():
                continue
            unknown.append(key)
            continue

        for column, value in {"Scaling Type": stype, "Scaling": sval, **extra}.items():
            if r[c[column]] != value:
                edits.append({"range": f"{col_letter(c[column])}{i + 1}", "values": [[value]]})

    if unknown:
        raise SystemExit(f"Scaling values with no rule — refusing to guess: {unknown}")
    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Hero: {len(edits)} cells set (Scaling split; durations and multiplicity moved out)")


def rename_spread(sh):
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    c = cols(vals[0])
    edits = [{"range": f"{col_letter(c['Spread'])}{i + 1}", "values": [[NEW_SPREAD]]}
             for i, r in enumerate(vals) if r[c["Spread"]].strip() == OLD_SPREAD]
    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Hero: {len(edits)} Spread cells renamed -> '{NEW_SPREAD}'")


def build_scaling_tab(sh):
    ws = next((w for w in sh.worksheets() if w.title == SCALING_TAB), None)
    if ws is None:
        ws = sh.add_worksheet(title=SCALING_TAB, rows=30, cols=3)
        print(f"created the '{SCALING_TAB}' tab")
    rows = [["Scaling Type", "What it means", "Examples"]] + SCALING_TYPES + [["", "", ""]]
    rows += [[p, "", ""] for p in SCALING_PROSE]
    if ws.row_count < len(rows):
        ws.add_rows(len(rows) - ws.row_count)
    ws.clear()
    ws.update(rows, f"A1:C{len(rows)}", value_input_option="RAW")
    ws.format("A1:C1", {"textFormat": {"bold": True},
                        "backgroundColor": {"red": 0.82, "green": 0.88, "blue": 0.82}})
    first = len(SCALING_TYPES) + 2
    sh.batch_update({"requests":
                     [{"unmergeCells": {"range": {"sheetId": ws.id}}}]
                     + [{"mergeCells": {
                         "range": {"sheetId": ws.id, "startRowIndex": i, "endRowIndex": i + 1,
                                   "startColumnIndex": 0, "endColumnIndex": 3},
                         "mergeType": "MERGE_ROWS"}} for i in range(first, len(rows))]
                     + [{"repeatCell": {
                         "range": {"sheetId": ws.id, "startRowIndex": 1, "endRowIndex": len(rows),
                                   "startColumnIndex": 0, "endColumnIndex": 3},
                         "cell": {"userEnteredFormat": {"wrapStrategy": "WRAP",
                                                        "verticalAlignment": "TOP"}},
                         "fields": "userEnteredFormat(wrapStrategy,verticalAlignment)"}}]})
    print(f"{SCALING_TAB}: wrote {len(SCALING_TYPES)} scaling types")


def move_notes(sh):
    """Lift every 'Note - ...' row out of Column Explain into its own tab. Nothing is deleted."""
    ce = sh.worksheet("Column Explain")
    vals = ce.get_all_values()
    notes = [r for r in vals if r and r[0].strip().startswith("Note")]

    ws = next((w for w in sh.worksheets() if w.title == NOTES_TAB), None)
    if ws is None:
        ws = sh.add_worksheet(title=NOTES_TAB, rows=max(len(notes) + 10, 30), cols=3)
        print(f"created the '{NOTES_TAB}' tab")

    existing = [r for r in ws.get_all_values() if r]
    if not existing:                       # brand-new, empty tab: give it a header first
        ws.update([["Note", "In one line", "Detail"]], "A1:C1", value_input_option="RAW")
        ws.format("A1:C1", {"textFormat": {"bold": True},
                            "backgroundColor": {"red": 0.82, "green": 0.88, "blue": 0.82}})
        existing = [["Note", "In one line", "Detail"]]

    have = {r[0].strip() for r in existing if r and r[0].strip()}
    pending = [n for n in notes + DESIGN_NOTES if n[0].strip() not in have]

    if pending:
        need = len(existing) + len(pending) + 2
        if ws.row_count < need:
            ws.add_rows(need - ws.row_count)
        ws.append_rows([(list(n) + ["", "", ""])[:3] for n in pending], value_input_option="RAW")
        print(f"{NOTES_TAB}: moved in {len(pending)} notes")

    # now delete them from Column Explain, bottom-up so indices stay valid
    dead = [i for i, r in enumerate(vals) if r and r[0].strip().startswith("Note")]
    for i in reversed(dead):
        ce.delete_rows(i + 1)
    if dead:
        print(f"Column Explain: removed {len(dead)} note rows — it is a column legend again")


def main():
    sh = open_sheet()
    add_scaling_type_column(sh)
    fix_scaling(sh)
    rename_spread(sh)
    build_scaling_tab(sh)
    move_notes(sh)
    post_replies(REPLIES, warn_unmatched=False)
    print("\nSpread Types is owned by tft-action-templates.py — run it to land the rename.")


if __name__ == "__main__":
    main()
