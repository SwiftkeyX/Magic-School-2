"""Round 8: a Step is a MOMENT IN THE CAST, and each row is one branch of it.

Run from repo-root cwd:  python .claude/scripts/tft-review-round8.py

THE CHANGE
----------
The user, on five different champions: "same step, but with if else condition."

They are right, and it finishes what Karma started. Karma was the EASY case: both her branches
fired the same action (Burst Projectile), so only Count/Spread had to leave the merged action
block. These five switch to a DIFFERENT ACTION depending on the condition:

    Swain    not transformed -> Cast (gain HP)        already transformed -> Circle AOE burst
    Azir     fewer than 3 Soldiers -> Summon          already 3 -> they all Auto-Attack
    K'Sante  target at edge -> Knock Off              not at edge -> Leap after it
    Kayle    Lvl 1-5 -> Auto-Attack                   Lvl 6-8 / 9+ -> Pierce Projectile
    Ahri     every cast -> Circle AOE                 2nd cast -> ALSO a Pierce Projectile

So `Action`, `Collision`, `Aim Target` and `Trigger` cannot be properties of the STEP any more.
The action block dissolves. What replaces it:

    Step = one MOMENT in the cast.
    Row  = one BRANCH of that moment: condition -> action -> effect.

MERGING NOW FOLLOWS THE VALUES, NOT THE SCHEMA
----------------------------------------------
Only `Step` and `Skill Type` merge across a whole step. Everything else merges wherever
CONSECUTIVE ROWS AGREE - so a plain one-action step still looks exactly as it did, and a branching
step shows its branches. Merging becomes a display of the data instead of an assertion about it,
which is the only way it survives a schema where any column may differ per row.

NOT ALL FIVE ARE EXCLUSIVE. Ahri's wave is ADDITIONAL to her Circle AOE, not instead of it, so her
first branch keeps an em-dash condition rather than a false "if not 2nd cast". Encoding an
either/or where the game has an and would be a lie that reads as rigour.
"""

from tft_sheet import (D, RUN_COLUMNS, SAME, STEP_BLOCK, col_letter, cols, open_sheet, post_replies,
                       remerge, sync_notes)

# Each champion's rows, declared outright. Mutating what is already there is how the Soraka and
# Azir bugs happened; a declaration cannot drift.
def _row(**kw):
    base = {n: "" for n in ["Step", "Skill Type", "Trigger", "Condition", "Action Source",
                            "Action", "Count", "Spread", "Collision", "Aim Target",
                            "Effect Recipient", "Effect Category", "Effect Detail", "Amount",
                            "Scaling Type", "Scaling", "Cadence", "Duration", "AOE", "Cast"]}
    base.update({"Scaling Type": D, "Scaling": D, "Duration": D, "AOE": D, "Cast": D})
    base.update(kw)
    return base


BLOCKS = {
    # Her whole kit is one passive whose behaviour is gated by level - three branches of one
    # moment, only ever one of which can apply.
    "Kayle": [
        _row(Step="0", **{"Skill Type": "Passive"}, Trigger="On Attack", Condition="Lvl 1-5",
             **{"Action Source": "Self"}, Action="Auto-Attack", Count="1", Spread=D,
             Collision="Target-Only", **{"Aim Target": "Current"},
             **{"Effect Recipient": SAME, "Effect Category": "Attack", "Effect Detail": "Damage"},
             Amount="30/45/70% AP", Cadence="Once"),
        _row(Trigger="On 3rd Attack", Condition="Lvl 6-8", **{"Action Source": "Self"},
             Action="Pierce Projectile", Count="1", Spread=D, Collision="Pierce-All",
             **{"Aim Target": "Current"},
             **{"Effect Recipient": "Enemies in path", "Effect Category": "Attack",
                "Effect Detail": "Damage"}, Amount="30/45/70% AP", Cadence="Once"),
        _row(Trigger="On 3rd Attack", Condition="Lvl 6-8", **{"Action Source": "Self"},
             Action="Pierce Projectile", Count="1", Spread=D, Collision="Pierce-All",
             **{"Aim Target": "Current"},
             **{"Effect Recipient": "Enemies in path", "Effect Category": "Debuff",
                "Effect Detail": "MR"}, Amount="20%", Cadence="Over Time", Duration="3"),
        _row(Trigger="On Attack", Condition="Lvl 9+", **{"Action Source": "Self"},
             Action="Pierce Projectile", Count="1", Spread=D, Collision="Pierce-All",
             **{"Aim Target": "Current"},
             **{"Effect Recipient": "Enemies in path (farther)", "Effect Category": "Attack",
                "Effect Detail": "Damage"}, Amount="30/45/70% AP", Cadence="Once"),
    ],
    # One cast, two outcomes. (The "When Transformed" burn was a step of its own here; round 9
    # demoted it to the passive it always was - see the last row of this block.)
    "Swain": [
        _row(Step="1", **{"Skill Type": "Active"}, Trigger="On Cast",
             Condition="If not Transformed", **{"Action Source": "Self"}, Action="Cast", Count=D,
             Spread=D, Collision="None", **{"Aim Target": "Self"},
             **{"Effect Recipient": SAME, "Effect Category": "Buff", "Effect Detail": "Bonus HP"},
             Amount="325/375/550% AP", Cadence="Once"),
        _row(Trigger="On Cast", Condition="If Already Transformed", **{"Action Source": "Self"},
             Action="Circle AOE", Count="1", Spread=D, Collision="Area",
             **{"Aim Target": "Self"},
             **{"Effect Recipient": SAME, "Effect Category": "Buff", "Effect Detail": "Bonus HP"},
             Amount="225/260/385% AP", Cadence="Once"),
        _row(Trigger="On Cast", Condition="If Already Transformed", **{"Action Source": "Self"},
             Action="Circle AOE", Count="1", Spread=D, Collision="Area",
             **{"Aim Target": "Self"},
             **{"Effect Recipient": "Enemies in area", "Effect Category": "Attack",
                "Effect Detail": "Damage"}, Amount="100/160/300% AP",
             **{"Scaling Type": "Burst"}, Scaling="burst", Cadence="Once"),
        # ROUND 9 MADE THIS A PASSIVE. The user: "Step 2 should be passive with condition when he
        # was transformed." They are right, and it is the same mistake as Karma's: this burn is not
        # a MOMENT IN THE CAST at all. It is always-on for as long as he is transformed - it ticks
        # (Cadence = Over Time) whether or not he casts again. A cast sequence is not where it
        # belongs, so it is Step 0.
        #
        # Its Condition stays an em-dash, by the rule Kalista's row established in round 5: the
        # Trigger "When Transformed" ALREADY says the only thing a Condition "If Transformed" would
        # say, and the sheet does not say a thing twice.
        _row(Step="0", **{"Skill Type": "Passive"}, Trigger="When Transformed", Condition=D,
             **{"Action Source": "Self"}, Action="Circle AOE", Count="1", Spread=D,
             Collision="Area", **{"Aim Target": "Self"},
             **{"Effect Recipient": "Enemies in area", "Effect Category": "Attack",
                "Effect Detail": "Damage"}, Amount="25/40/60% AP",
             **{"Scaling Type": "Per Tick"}, Scaling="per second", Cadence="Over Time"),
    ],
    "Azir": [
        _row(Step="0", **{"Skill Type": "Passive"}, Trigger="On 3rd Attack", Condition=D,
             **{"Action Source": "Summon"}, Action="Auto-Attack", Count="1", Spread=D,
             Collision="Target-Only", **{"Aim Target": "Current"},
             **{"Effect Recipient": SAME, "Effect Category": "Attack",
                "Effect Detail": "Damage"}, Amount="110/160/500% AP", Cadence="Once"),
        _row(Step="1", **{"Skill Type": "Active"}, Trigger="On Cast",
             Condition="If fewer than 3 Soldiers", **{"Action Source": "Self"}, Action="Summon",
             Count="3", Spread=D, Collision="None", **{"Aim Target": D},
             **{"Effect Recipient": SAME, "Effect Category": "Summon",
                "Effect Detail": "(summon)"}, Amount=D,
             **{"Scaling Type": "Cap"}, Scaling="max 3 Soldiers on the board", Cadence=D),
        _row(Trigger="On Cast", Condition="If Already 3 Soldiers",
             **{"Action Source": "Summon"}, Action="Auto-Attack", Count="3",
             Spread="Same target", Collision="Target-Only", **{"Aim Target": "Current"},
             **{"Effect Recipient": SAME, "Effect Category": "Attack",
                "Effect Detail": "Damage"}, Amount="70% AP", Cadence="Once"),
    ],
    "Ahri": [
        _row(Step="0", **{"Skill Type": "Passive"}, Trigger="Game Start",
             Condition="If Ionia Active", **{"Action Source": "Self"}, Action="Cast", Count=D,
             Spread=D, Collision="None", **{"Aim Target": "Self"},
             **{"Effect Recipient": SAME, "Effect Category": "Buff",
                "Effect Detail": "Mana Regen"}, Amount="3 /s", Cadence="Once",
             Duration="Permanent"),
        # Her wave is ADDITIONAL to the Circle AOE, not instead of it - so this branch keeps an
        # em-dash, not a false "If not 2nd Cast".
        _row(Step="1", **{"Skill Type": "Active"}, Trigger="On Cast", Condition=D,
             **{"Action Source": "Self"}, Action="Circle AOE", Count="1", Spread=D,
             Collision="Area", **{"Aim Target": "Current"},
             **{"Effect Recipient": "Enemies in area", "Effect Category": "Attack",
                "Effect Detail": "Damage"}, Amount="105/150/1000% AP", Cadence="Once"),
        _row(Trigger="On Cast", Condition=D, **{"Action Source": "Self"}, Action="Circle AOE",
             Count="1", Spread=D, Collision="Area", **{"Aim Target": "Current"},
             **{"Effect Recipient": "Enemies in area", "Effect Category": "Debuff",
                "Effect Detail": "Mana Reave"}, Amount="20%", Cadence="Once",
             Duration="Until next cast"),
        _row(Trigger="On Cast", Condition="If 2nd Cast", **{"Action Source": "Self"},
             Action="Pierce Projectile", Count="1", Spread="360° radial", Collision="Pierce-All",
             **{"Aim Target": "Self"},
             **{"Effect Recipient": "All enemies", "Effect Category": "Attack",
                "Effect Detail": "Damage"}, Amount="260/390/1999% AP",
             **{"Scaling Type": "Conditional Bonus"}, Scaling="+33% if essence stolen",
             Cadence="Once"),
    ],
}

# K'Sante's last two steps are one moment with two exclusive branches. Only his step 4 row changes
# (it becomes a continuation of step 3), so he is patched rather than re-declared.
KSANTE_FIX = {"Step": "", "Skill Type": ""}

NOTES = [
    ["Note - A Step is a MOMENT, not an action",
     "Step = one moment in the cast. Each ROW is one branch of it: condition -> action -> effect. "
     "Two rows of one step may run DIFFERENT actions.",
     "Karma was the easy case - both her branches fired the same action, so only Count/Spread had "
     "to go per-row. Swain, Azir, K'Sante, Kayle and Ahri switch ACTION on the condition (Swain "
     "casts if untransformed and bursts if not; Azir summons unless he already has 3 Soldiers). So "
     "Action, Collision, Aim Target and Trigger are per-ROW too, and the 'action block' is gone. "
     "MERGING NOW FOLLOWS THE VALUES: only Step and Skill Type merge across a whole step; every "
     "other column merges wherever consecutive rows happen to agree. A merge is now a display of "
     "the data, not a claim about it - which is the only way it survives a schema where any column "
     "may differ per row. NOTE: branches are not always exclusive. Ahri's wave is ADDITIONAL to "
     "her Circle AOE, so her first branch has no condition - writing 'if not 2nd cast' there would "
     "be a lie that reads as rigour."],
]

REPLIES = [
    ("This should be alternative to 1",
     "Done - Swain is one step with two branches.\n\n"
     "  If not Transformed      -> Cast, gain 325/375/550% AP HP (and he transforms)\n"
     "  If Already Transformed  -> Circle AOE only: 225/260/385% AP HP + a 100/160/300% AP burst\n\n"
     "The 'When Transformed' AOE stays its own step, because it is a CONSEQUENCE of the first "
     "branch rather than an alternative to it. It also had to move below both branches - a step's "
     "rows must be contiguous or the merge cannot span them.\n\n"
     "This one cost more than Karma did, and it is worth saying why. Karma's two branches fired "
     "the SAME action, so only Count/Spread had to become per-row. Yours fire DIFFERENT actions "
     "(Cast vs Circle AOE), so Action, Collision, Aim Target and Trigger had to go per-row as well "
     "- the action block is gone. A Step is now a MOMENT in the cast, and each row is one branch of "
     "it. Merging follows the values instead: only Step and Skill Type merge across a step, and "
     "everything else merges where consecutive rows agree, so a plain one-action step looks exactly "
     "as it did."),

    ("same step with if else condition",
     "Done - collapsed on all five champions you flagged: Swain, Azir, K'Sante, Kayle and Ahri. "
     "Each is now ONE step whose rows are its branches.\n\n"
     "One I deliberately did NOT make exclusive: Ahri. Her 2nd-cast wave is ADDITIONAL to her "
     "Circle AOE, not instead of it, so her first branch keeps an em-dash condition rather than a "
     "false 'If not 2nd Cast'. Encoding an either/or where the game has an and would be a lie that "
     "reads as rigour.\n\n"
     "See the Swain reply for what this cost: the action block is gone, and a Step is now a moment "
     "in the cast rather than a single action."),

    ("Is this intended?",
     "No - that was a duplicate, and I created it. Irelia had TWO identical Laser Shot steps.\n\n"
     "The cause is worth knowing because it bit three times in one change. tft-apply-comments.py "
     "inserts Irelia's second hitbox only if she does not already have a step '4'. Round 7 "
     "renumbered her steps (her passive moved to step 0, so everything below shifted down one), so "
     "the check looked for a step 4, found none, and inserted the row a SECOND time.\n\n"
     "A step number is a POSITION, not an IDENTITY. The same mistake corrupted Azir - a stale "
     "(champion, step) key overwrote his Summon with an Auto-Attack - and left Yasuo's three "
     "re-aims pointing at the wrong step. All three are fixed, and Irelia's guard now keys on "
     "whether the ACTION exists rather than on a step number."),

    ("Change to \"and was permanent\"",
     "Done - Stacking now reads 'The amount GROWS each time it is applied, and is permanent.'"),

    ("This is more suitable",
     "Careful - that wording would orphan three rows, so I have written something close to it "
     "instead.\n\n"
     "If Derived means 'not off a stat like AD/AP', then Samira (+AP), Aphelios (increased by AP) "
     "and Sejuani have no type left. What I think you mean is 'not off its own per-star Amount' - "
     "and that IS the distinction, so I have made it explicit:\n\n"
     "  'The amount SCALES OFF some OTHER quantity - on top of its own per-star Amount. NOTE: this "
     "does not mean not-a-stat. The per-star Amount already carries the ordinary AD/AP scaling "
     "(200/300/450% AP); Derived is for a SECOND quantity layered on top. Samira's flat 10/15/20 "
     "shred that also grows with AP is exactly that.'\n\n"
     "If you did mean to exclude AD/AP outright, say so and I will split it into two types - but "
     "then those three rows need a home."),

    ("Let's flag this",
     "Flagged and left alone, as you asked.\n\n"
     "'Spread' keeps its name and 'Each to its own target' keeps its slot. The underlying doubt - "
     "that this column may be answering two different questions (WHERE the instances go, and WHEN "
     "the aim is decided) - is recorded in Design Notes as 'Note - Mid-action change (KNOWN GAP)', "
     "alongside Gwen's sweeping hitbox, which is the same gap seen from the other side.\n\n"
     "Two cases is not enough to build a column on. A third settles it, and we will know it when "
     "it arrives."),
]


def rebuild(sh):
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    c = cols(vals[0])

    def champ_rows(name):
        out, cur = [], ""
        for i, r in enumerate(vals):
            if i == 0:
                continue
            if r[c["Champion"]].strip():
                cur = r[c["Champion"]].strip()
            if cur == name:
                out.append(i)
        return out

    # A MERGED cell reads back as "" on every row but its first. So comparing the sheet against a
    # spec that names a value on every row would ALWAYS mismatch — rewrite, unmerge, re-merge, for
    # ever. Compare EFFECTIVE against EFFECTIVE: in both the sheet and the spec, a blank in a
    # mergeable column means "same as the row above". Idempotence is the only test that has ever
    # caught these bugs, so the comparison has to survive its own merging.
    #
    # STEP_BLOCK IS DELIBERATELY EXCLUDED. `Step` is what remerge() reads to find the step
    # BOUNDARIES, so a blank continuation row must genuinely BE blank: fill it with the value above
    # and that row starts to look like a new step, remerge refuses to merge it away, and round 7's
    # renumber_steps() then sees two steps with the same number and renumbers everything below.
    # Round 9 hit exactly that. Step and Skill Type are compared RAW and written LITERALLY, which is
    # what KSANTE_FIX below has always done.
    MERGEABLE = set(RUN_COLUMNS)

    def fill_down(getter, n, col):
        out, last = [], ""
        for k in range(n):
            v = getter(k, col)
            if v.strip():
                last = v
            out.append(last if col in MERGEABLE else v)
        return out

    edits = []
    for name, spec in BLOCKS.items():
        rows = champ_rows(name)
        if len(rows) != len(spec):
            raise SystemExit(f"{name} has {len(rows)} rows, expected {len(spec)} — not touching")
        for col in spec[0]:
            have = fill_down(lambda k, cc: vals[rows[k]][c[cc]], len(rows), col)
            want = fill_down(lambda k, cc: spec[k][cc], len(rows), col)
            for k in range(len(rows)):
                if have[k] != want[k]:
                    # write the FILLED value, not the blank: merging afterwards clears the
                    # duplicates by itself, so this is what makes the rewrite converge.
                    edits.append({"range": f"{col_letter(c[col])}{rows[k] + 1}",
                                  "values": [[want[k]]]})

    # K'Sante: only his step-4 row changes — it becomes the second branch of step 3.
    ks = champ_rows("K'Sante")
    last = ks[-1]
    for col, value in KSANTE_FIX.items():
        if vals[last][c[col]] != value:
            edits.append({"range": f"{col_letter(c[col])}{last + 1}", "values": [[value]]})

    if not edits:
        print("Hero: the five branching champions are already collapsed")
        return False

    # unmerge everything below the identity block before rewriting, or a merged cell eats the write
    sh.batch_update({"requests": [{"unmergeCells": {"range": {
        "sheetId": ws.id, "startRowIndex": 1, "endRowIndex": len(vals),
        "startColumnIndex": c["Step"], "endColumnIndex": c["Aim Target"] + 1}}}]})
    ws.batch_update(edits, value_input_option="RAW")
    print(f"Hero: {len(edits)} cells rewritten — 5 champions collapsed into branching steps")
    return True


def main():
    sh = open_sheet()
    if rebuild(sh):
        remerge(sh)
    sync_notes(sh, NOTES)
    post_replies(REPLIES, warn_unmatched=False)


if __name__ == "__main__":
    main()
