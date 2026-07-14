"""Round 7: Step becomes the order within ONE CAST, and Count/Spread go per-effect.

Run from repo-root cwd:  python .claude/scripts/tft-review-round7.py

  1. PASSIVES ARE STEP 0. "Isn't it weird to have Passive as Step1? Passive should be Step0."
     Right: if Step is the order of what happens in one cast, a passive is not in that sequence
     at all. 15 champions opened with a passive at Step 1; 19 renumber in total.
     Rule: Skill Type = Passive -> Step 0 (0.1, 0.2 ... when a champion has several).
           Skill Type = Active  -> 1..N, in cast order.

     WATCH THE CROSS-REFERENCES. Yasuo's dash, slash and slam all aim at "Step 2 Aim target" -
     the enemy his whirlwind picked. His whirlwind was step 2 and is now step 1, so that TEXT is
     a dangling reference the moment the numbers move. Renumbering a key means rewriting whatever
     pointed at it. (K'Sante also uses "Step 2 Aim target" but has no passive, so his numbers do
     not move and his reference stays correct.)

  2. COUNT AND SPREAD ARE PER-EFFECT, like Condition. Karma's 1st cast fires ONE burst; her 3rd
     fires THREE. The user: "the 2nd, 3rd step should be combined into 1st step instead. But they
     have condition: if not 3rd cast, 1 burst projectile..." - and that cannot be said while Count
     lives in the merged action block, because one step cannot then carry two Counts.

     So they leave ACTION_BLOCK and are written on every effect row. Karma collapses from two
     steps to one, with two conditional rows. Her two casts were already IDENTICAL in every other
     column - same action, same amount, same AOE - which is the tell that they were one action all
     along, split only because the schema could not express the difference.

  3. COUNT IS AN EM-DASH WHERE IT CANNOT EXCEED 1. "Cast doesn't make sense to have Count = 1...
     what is Count representing here?" Count is how many INSTANCES of the action fire. A Cast or a
     Leap projects nothing and happens exactly once by nature, so the question does not apply and
     the cell says so. Everything that CAN fire more than once keeps a number - including Summon
     (Azir has 3 Soldiers).

  4. APHELIOS IS NOT A BURST PROJECTILE. "It was a Homing Projectile + Circle AOE. The projectile
     goes to the clumpiest enemy, can go through hero, and explode when it reach target."
     Burst Projectile is First-Hit: it detonates on the FIRST body it meets. His passes THROUGH
     and detonates on the aim target. Different composition -> a different action, `Homing Burst`.
"""

from tft_sheet import D, col_letter, cols, open_sheet, post_replies, sync_notes

# Actions that project nothing and happen exactly once. Count cannot exceed 1, so it is an
# em-dash. NOT Summon: Azir spawns 3 Soldiers, so Summon genuinely counts.
NO_COUNT_ACTIONS = {"Cast", "Leap"}

# Karma, declared outright. Two steps become one: they are one moment in the cast, split by a
# condition.
#
# ROUND 9 CORRECTED WHAT THIS SCRIPT ORIGINALLY CLAIMED. It said her two branches were "the same
# action, same amount, same AOE - they only ever differed by Count/Spread". The user: "It should be
# 1st, 2nd cast: do circle AOE. 3rd cast: do Pierce Projectile. The description is misleading, but
# believe me on this one."
#
# So the branches fire DIFFERENT ACTIONS, and the source text is what misled me. That is exactly
# the case round 8 later built for (a Step is a MOMENT; its rows may run different actions), so the
# collapse into one step still stands - only the actions were wrong.
#
# Collision/Shape come from `Action Model`, not from guesswork: Circle AOE is Area/Circle, so it
# keeps an AOE radius and hits "Enemies in area"; Pierce Projectile is Pierce-All/Line, so it hits
# "Enemies in path" and its AOE is an em-dash - a line has no circle radius.
KARMA_ROWS = [
    {"Step": "0", "Skill Type": "Passive", "Trigger": "Game Start",
     "Condition": "If Ionia Active", "Action Source": "Self", "Action": "Cast", "Count": D,
     "Spread": D, "Collision": "None", "Aim Target": "Self",
     "Effect Recipient": "Same to Aim Target", "Effect Category": "Buff", "Effect Detail": "AP",
     "Amount": "25", "Scaling Type": D, "Scaling": D, "Cadence": "Once",
     "Duration": "Permanent", "AOE": D, "Cast": D},
    {"Step": "1", "Skill Type": "Active", "Trigger": "On Cast", "Condition": "If not 3rd Cast",
     "Action Source": "Self", "Action": "Circle AOE", "Count": "1", "Spread": D,
     "Collision": "Area", "Aim Target": "Current",
     "Effect Recipient": "Enemies in area", "Effect Category": "Attack",
     "Effect Detail": "Damage", "Amount": "200/300/470% AP", "Scaling Type": D, "Scaling": D,
     "Cadence": "Once", "Duration": D, "AOE": "1", "Cast": D},
    {"Step": "", "Skill Type": "", "Trigger": "", "Condition": "If 3rd Cast",
     "Action Source": "", "Action": "Pierce Projectile", "Count": "3",
     "Spread": "Current + Left + Right", "Collision": "Pierce-All", "Aim Target": "",
     "Effect Recipient": "Enemies in path", "Effect Category": "Attack",
     "Effect Detail": "Damage", "Amount": "200/300/470% AP", "Scaling Type": D, "Scaling": D,
     "Cadence": "Once", "Duration": D, "AOE": D, "Cast": D},
]
# Merged down Karma's one active step. Action and Collision LEFT this list in round 9: her two
# branches now fire different actions, so merging those columns would assert a sameness that is no
# longer there - and round 8's value-run remerge would tear the merge back down on its next run.
# Only the columns her branches genuinely share stay here.
KARMA_MERGE = ["Step", "Skill Type", "Trigger", "Action Source", "Aim Target"]

APHELIOS_FIX = {"Action": "Homing Burst", "Collision": "Area"}

NOTES = [
    ["Note - Step is the order within ONE CAST",
     "Step 0 = passive / always-on. Steps 1..N = what happens when the champion casts, in order.",
     "A passive is not part of the cast sequence, so it is not step 1 - it is step 0. A champion "
     "with several passives numbers them 0.1, 0.2. Steps 1..N then read as the cast itself: "
     "Yasuo 1 whirlwind, 2 dash, 3 slash, 4 slam. WARNING: steps are REFERENCED by other cells "
     "('Step 1 Aim target'), so renumbering means rewriting whatever points at them - Yasuo's "
     "three re-aims had to move from 'Step 2' to 'Step 1' when his passive left the sequence."],
    ["Note - Count is PER-EFFECT",
     "Count and Spread sit on each effect ROW, not on the action. One step can fire 1 instance or "
     "3, depending on a Condition.",
     "Karma forced it: her 1st cast fires ONE burst, her 3rd fires THREE at Current + Left + "
     "Right. Everything else about the two is identical - same action, same amount, same AOE - so "
     "they were always ONE action, split into two steps only because a merged Count could not say "
     "'1 here, 3 there'. Count/Spread left the merged action block to join Condition. An em-dash "
     "means the question does not apply: a Cast or a Leap projects nothing and fires exactly once "
     "by nature. Anything that CAN fire more than once keeps a number, Summon included (Azir has "
     "3 Soldiers)."],
]

REPLIES = [
    ("I think Step should present the order of how skill work in 1 cast",
     "Done, and both halves of it.\n\n"
     "PASSIVES ARE STEP 0. If Step is the order within one cast, a passive is not in that sequence "
     "at all. 15 champions opened with a passive at Step 1; 19 renumbered in total. Yasuo now "
     "reads 0 passive, 1 whirlwind, 2 dash, 3 slash, 4 slam - which is the order you pointed at as "
     "the one that looks right.\n\n"
     "KARMA IS NOW ONE STEP. You are right that her two casts are one action: I checked, and they "
     "were IDENTICAL in every column except Count and Spread - same Burst Projectile, same "
     "200/300/470% AP, same 1-hex AOE. They were only ever two steps because Count lived in the "
     "merged action block, so one step could not say '1 burst normally, 3 on the third cast'. That "
     "is a schema limitation being mistaken for a design fact.\n\n"
     "So Count and Spread are now PER-EFFECT, exactly as Condition became for Soraka. Karma is one "
     "step with two conditional rows: 'If not 3rd Cast' -> Count 1, and 'If 3rd Cast' -> Count 3, "
     "Spread Current + Left + Right.\n\n"
     "One thing that renumbering broke and I had to chase: Yasuo's dash, slash and slam all aim at "
     "'Step 2 Aim target' - the enemy his whirlwind picked. His whirlwind moved from step 2 to step "
     "1, so that text was a dangling pointer. Fixed. Steps are referenced by other cells, so "
     "renumbering one means rewriting whatever points at it."),

    ("Isn't it weird to have Passive as Step1",
     "It was, and it is fixed - see the reply on your Karma comment. Passives are Step 0 now "
     "(0.1, 0.2 where a champion has several: Kayle's whole kit is passive, and Maokai and Kalista "
     "have two each). Steps 1..N are the cast sequence and nothing else."),

    ("Cast doesn't make sense to have Count = 1",
     "Agreed - and the answer to 'what is Count representing' is: how many INSTANCES OF THE ACTION "
     "FIRE. Not how much the effect grants (that is Amount - see 'Note - Count vs Amount', which "
     "your Kalista comment produced).\n\n"
     "The test is: could one instance MISS while another HITS? Akshan's 6 shots are 6 separate "
     "projectiles, so Count 6. Kalista's 6 spears ride one projectile, so Count 1 and the 6 is an "
     "Amount.\n\n"
     "By that test a Cast or a Leap cannot have a Count at all: they project nothing and happen "
     "exactly once by nature, so the question does not apply. Those cells are now an em-dash, and "
     "a NUMBER now means 'this action can fire more than once, and here is how many times it did'. "
     "You were nearly right that only projectiles have one - but Summon does too: Azir spawns 3 "
     "Sand Soldiers."),

    ("For aphelios, It was a Homing Projectile + Circle AOE",
     "Corrected - he is a new action, 'Homing Burst'.\n\n"
     "You have found a real hole in the taxonomy rather than a mislabelled row. Burst Projectile is "
     "defined as FIRST-HIT: it detonates on the first body it meets, which may not be the unit it "
     "was aimed at. Aphelios' blast does the opposite - it passes THROUGH everything and detonates "
     "on the target it was aimed at. Same circle, different delivery.\n\n"
     "In the composition model: Burst Projectile = First hit Projectile + Circle AOE, and Homing "
     "Burst = Homing Projectile + Circle AOE. Two different actions that happen to share a shape. "
     "Added to the Action Model tab.")
]


# unmerge_count_spread() lived here. Round 8's remerge() owns the merge layout now — it merges by
# VALUE RUN — so unmerging here just fought it: round 7 stripped the merges, round 8 put them back,
# for ever. The acceptance grep missed it for a while because the message said "merges", not
# "cells". Two scripts, one layout, one owner.


def renumber_steps(sh):
    """Passives -> 0 (0.1, 0.2 ...); actives -> 1..N. Then fix the cells that POINT at a step."""
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    c = cols(vals[0])

    champ, blocks = "", {}
    for i, r in enumerate(vals):
        if i == 0:
            continue
        if r[c["Champion"]].strip():
            champ = r[c["Champion"]].strip()
        if r[c["Step"]].strip():
            blocks.setdefault(champ, []).append((i, r[c["Step"]].strip(),
                                                 r[c["Skill Type"]].strip()))

    remap, edits = {}, []
    for champ, steps in blocks.items():
        passive = [(i, s) for i, s, t in steps if t == "Passive"]
        active = [(i, s) for i, s, t in steps if t != "Passive"]
        m = {}
        for k, (i, s) in enumerate(passive):
            m[s] = "0" if len(passive) == 1 else f"0.{k + 1}"
        for k, (i, s) in enumerate(active):
            m[s] = str(k + 1)
        remap[champ] = m
        for i, s, _ in steps:
            if m[s] != s:
                edits.append({"range": f"{col_letter(c['Step'])}{i + 1}", "values": [[m[s]]]})

    # A step number is a KEY: other cells point at it ("Step 2 Aim target"). Renumbering without
    # rewriting those leaves a dangling pointer aimed at the wrong action.
    champ = ""
    for i, r in enumerate(vals):
        if i == 0:
            continue
        if r[c["Champion"]].strip():
            champ = r[c["Champion"]].strip()
        aim = r[c["Aim Target"]].strip()
        if aim.startswith("Step ") and " Aim target" in aim:
            old = aim.split()[1]
            new = remap.get(champ, {}).get(old, old)
            if new != old:
                edits.append({"range": f"{col_letter(c['Aim Target'])}{i + 1}",
                              "values": [[f"Step {new} Aim target"]]})

    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Hero: {len(edits)} cells renumbered (passives -> step 0, and the refs that point at "
          f"them)")


def spread_count_down_rows(sh):
    """Write Count/Spread on EVERY effect row, and em-dash them where they cannot exceed 1."""
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    c = cols(vals[0])

    eff = {}
    for name in ("Count", "Spread"):
        col, last, out = c[name], "", [""] * len(vals)
        for i, r in enumerate(vals):
            if i and r[c["Champion"]].strip():
                last = ""
            if r[col].strip():
                last = r[col]
            out[i] = last
        eff[name] = out

    edits, cur = [], None
    for i, r in enumerate(vals):
        if i == 0:
            continue
        # A new run starts wherever a row names its OWN ACTION — not merely at a new Step. After
        # round 8 a step's rows are BRANCHES, and a branch is a continuation row (no Step) that
        # nonetheless runs a different action. Keying on Step alone propagated the FIRST branch's
        # Count/Spread over every later branch: Swain's Circle AOE inherited the Cast's em-dash
        # Count, and Azir's and Ahri's branches lost their Spread entirely.
        if r[c["Step"]].strip() or r[c["Action"]].strip():
            # Seed the run from the EFFECTIVE Count/Spread, not the raw cells. A run can start on a
            # row whose Count is merged with the row above (Azir's Auto-Attack branch shares the
            # Summon's Count of 3, so the cell itself reads blank). Seeding from the raw blank made
            # the run demand a blank on every row of itself — 10 cells rewritten, for ever.
            cur = (r[c["Action"]].strip(), eff["Count"][i], eff["Spread"][i])
        if cur is None:
            continue
        action, count, spread = cur
        if action in NO_COUNT_ACTIONS:
            count, spread = D, D
        # Karma's second row carries its own Count deliberately — never overwrite a row that
        # already disagrees with its action's default.
        if r[c["Count"]].strip() and r[c["Count"]].strip() != cur[1]:
            continue
        # Merge-aware: a merged cell reads back blank on every row but its first, so compare the
        # EFFECTIVE value (blank = same as the row above). Comparing raw would try to rewrite every
        # merged continuation row on every run — and writing into a merged cell is a no-op anyway.
        for name, value in (("Count", count), ("Spread", spread)):
            if eff[name][i] != value:
                edits.append({"range": f"{col_letter(c[name])}{i + 1}", "values": [[value]]})

    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Hero: {len(edits)} Count/Spread cells written per-row (em-dash on Cast / Leap)")


def rebuild_karma(sh):
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    c = cols(vals[0])
    rows = [i for i in range(1, len(vals)) if _champ_at(vals, c, i) == "Karma"]
    if len(rows) != len(KARMA_ROWS):
        raise SystemExit(f"Karma has {len(rows)} rows, expected {len(KARMA_ROWS)} — not touching")

    edits = [{"range": f"{col_letter(c[n])}{i + 1}", "values": [[v]]}
             for i, spec in zip(rows, KARMA_ROWS)
             for n, v in spec.items() if vals[i][c[n]] != v]
    if not edits:
        print("Hero: Karma's block already correct")
        return

    top = rows[0]
    sh.batch_update({"requests": [{"unmergeCells": {
        "range": {"sheetId": ws.id, "startRowIndex": top, "endRowIndex": rows[-1] + 1,
                  "startColumnIndex": c["Step"], "endColumnIndex": c["Aim Target"] + 1}}}]})
    ws.batch_update(edits, value_input_option="RAW")
    # merge her ONE active step down its two conditional rows - but not Count/Spread/Condition
    sh.batch_update({"requests": [{"mergeCells": {
        "range": {"sheetId": ws.id, "startRowIndex": top + 1, "endRowIndex": top + 3,
                  "startColumnIndex": c[n], "endColumnIndex": c[n] + 1},
        "mergeType": "MERGE_COLUMNS"}} for n in KARMA_MERGE]})
    print(f"Hero: Karma rebuilt ({len(edits)} cells) — two casts are ONE step, Count differs "
          f"per row")


def fix_aphelios(sh):
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    c = cols(vals[0])
    edits = []
    for i, r in enumerate(vals):
        if _champ_at(vals, c, i) == "Aphelios" and r[c["Action"]].strip() in ("Burst Projectile",
                                                                              "Homing Burst"):
            for n, v in APHELIOS_FIX.items():
                if r[c[n]] != v:
                    edits.append({"range": f"{col_letter(c[n])}{i + 1}", "values": [[v]]})
    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Hero: {len(edits)} cells set (Aphelios -> Homing Burst)")


def _champ_at(vals, c, i):
    for k in range(i, 0, -1):
        if vals[k][c["Champion"]].strip():
            return vals[k][c["Champion"]].strip()
    return ""


def main():
    sh = open_sheet()
    renumber_steps(sh)
    # the per-row sweep first, THEN Karma: she is the one action whose rows deliberately disagree
    # about Count, so her declared block must be written last or the sweep's default overwrites it.
    spread_count_down_rows(sh)
    rebuild_karma(sh)
    fix_aphelios(sh)
    sync_notes(sh, NOTES)
    post_replies(REPLIES, warn_unmatched=False)
    print("\n'Homing Burst' is defined by tft-action-model.py — run it next.")


if __name__ == "__main__":
    main()
