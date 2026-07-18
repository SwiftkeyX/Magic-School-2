"""Round 9: four more steps that were never steps, and Maokai's passive that was never a passive.

Run from repo-root cwd:  python .claude/scripts/tft-review-round9.py

THE CHANGE
----------
Round 8 established that a Step is a MOMENT in the cast. This round applies that test to the rows it
did not reach, and four champions fail it: their Step 2 fires on `On Cast` — the SAME instant as
Step 1, not a consequence of it. A second step that is triggered by the same event as the first is
not a second step; it is a second effect of the first.

    Shen     Step 1 shields himself   + Step 2 shields the lowest-HP allies   -> one moment
    Orianna  Step 1 shields an ally   + Step 2 empowers her own next attack   -> one moment
    Jayce    Step 1 buffs his AS      + Step 2 buffs adjacent allies' AP      -> one moment
    Viego    Step 1 fires his beam    + Step 2 stacks his on-hit damage       -> one moment

Their Step/Skill Type cells are blanked so the rows become continuation rows of Step 1, and Shen's
and Jayce's remaining steps renumber down. This is the KSANTE_FIX idiom from round 8.

RENUMBERING IS THE DANGEROUS PART, so it was checked rather than assumed. Steps are REFERENCED by
other cells ("Step 2 Aim target"), and round 7 left three of those dangling by renumbering without
looking. The only such references in the whole Hero tab are Yasuo's three (Step 1) and K'Sante's one
(Step 2) — neither champion renumbers here, so nothing dangles.

MAOKAI
------
The user, on his step 0.2: "This shouldn't be passive, right? We should state in his empower attack
effect that his next auto do heal." And on the same row's Action cell: "this one should be 'Cast',
effect = 'Buff' instead."

They are right, and the row was a workaround for a missing word. Maokai's heal is not a passive he
has — it is what his Empowered Attack DOES. Encoding it as a separate always-on step meant the sheet
claimed he heals on attack whether or not he ever cast, which is false; the `If Empowered` condition
was there to take back what the Step number had wrongly promised.

So the row goes, and the thing it was trying to say moves into the effect itself: a new Effect Detail
`Empowered Attack (Maokai)`. That keeps the distinction the user already settled in round 2 — Orianna
and Maokai have ONE empowered attack, spent on the next hit; Viego's stacks and never falls off (his
is `On-Hit Damage`) — while letting Maokai's differ in WHAT it does rather than in how long it lasts.
"""

from tft_sheet import (D, col_letter, cols, open_sheet, post_replies, remerge, sync_notes)

# (Step, Skill Type) declared for EVERY row the champion owns, in order. A blank pair is a
# continuation row — it belongs to the step above it.
#
# Declared, not mutated: a rule that says "blank the row whose Step is 2" destroys data the moment
# the steps renumber underneath it, which is how round 5 wiped Soraka's star step. A declaration
# cannot drift. A step number is a POSITION, not an IDENTITY — so it is never a KEY here, only a
# value, and the position is the list index.
STEPS = {
    "Shen": [
        ("0", "Passive"),   # Ionia bonus
        ("1", "Active"),    # Cast -> shields himself
        ("", ""),           # was Step 2: Cast -> shields the lowest-HP allies. SAME moment.
        ("2", "Active"),    # was Step 3: the AOE after the shields land
        ("", ""),           # ...and its damage effect
    ],
    "Orianna": [
        ("1", "Active"),    # Cast -> shields an ally
        ("", ""),           # was Step 2: Cast -> empowers her next attack. SAME moment.
    ],
    "Jayce": [
        ("1", "Active"),    # Cast -> buffs his own attack speed
        ("", ""),           # was Step 2: Cast -> buffs adjacent allies' AP. SAME moment.
        ("2", "Active"),    # was Step 3: the burst that follows the cast
    ],
    "Viego": [
        ("1", "Active"),    # Laser Shot
        ("", ""),           # was Step 2: Cast -> stacks his On-Hit Damage. SAME moment.
    ],
}

MAOKAI_EFFECT = "Empowered Attack (Maokai)"
MAOKAI_AMOUNT = "220/260/300% AP"

EFFECT_TYPES = [
    ["Buff", MAOKAI_EFFECT,
     "The recipient's NEXT auto-attack also HEALS the recipient for the Amount. One attack, then "
     "spent - the same lifetime as Empowered Attack, but it heals instead of dealing bonus damage. "
     "Maokai only. Distinct from On-Hit Damage (Viego), which stacks and never falls off."],
]

NOTES = [
    ["Note - A second step needs a second MOMENT",
     "If a step's Trigger is the same event as the step above it (both 'On Cast'), it is not a "
     "step - it is another effect of the one above.",
     "Round 8 said a Step is a MOMENT in the cast. This is the test that falls out of it, and four "
     "champions failed it: Shen, Orianna, Jayce and Viego each had a Step 2 triggered by 'On Cast', "
     "the same instant as their Step 1. A consequence gets its own step (Jayce's burst is 'After "
     "Cast'); a simultaneous effect does not. WARNING: collapsing a step RENUMBERS the ones below "
     "it, and steps are referenced by other cells ('Step 2 Aim target'). Check those references "
     "before renumbering - round 7 left three of them dangling by not doing so."],
    ["Note - Empowered Attack (Maokai)",
     "Maokai's heal is not a passive. It is what his Empowered Attack DOES.",
     "He had it as a separate always-on step (0.2) with an 'If Empowered' condition - which is a "
     "workaround for a missing word, not a design. As a step it claimed he heals on attack whether "
     "or not he ever cast, and the condition existed only to take that claim back. The step is gone "
     "and the behaviour moved into the effect itself. This preserves the split settled in round 2: "
     "Orianna and Maokai get ONE empowered attack, spent on the next hit; Viego's stacks forever "
     "(On-Hit Damage). Maokai's now differs in WHAT it does, not in how long it lasts."],
]

# Replies ALREADY POSTED by earlier rounds, on comments whose text also contains "same step".
#
# These are listed FIRST and reproduced verbatim so those comments match HERE and are then SKIPPED as
# already-answered (post_replies skips a comment whose replies already open with the body). Without
# them, the "same step" key below matches their text too and lands a second, wrong reply.
#
# THIS IS NOT HYPOTHETICAL. The first run of this script did exactly that to Soraka's comment - "This
# are the same heal, so it should be combine into same step" - which round 5 had already answered.
# It collected a reply about Shen and Jayce that had nothing to do with it. The reply was deleted by
# hand and this guard added. A match key is a SUBSTRING of the comment's whole text, so a short key
# will silently grab any longer comment that happens to contain it.
ROUND8_BODY = ("Done - collapsed on all five champions you flagged: Swain, Azir, K'Sante, Kayle and "
               "Ahri. Each is now ONE step whose rows are its branches.")
ROUND5_SORAKA_BODY = "Combined - Soraka's two heals are now one step (two effect rows)"

SAME_STEP_BODY = (
    "Done - and you were right on all of them. Four more champions collapsed: Shen, Orianna, Jayce "
    "and Viego.\n\n"
    "Each had a Step 2 whose Trigger was 'On Cast' - the SAME instant as Step 1, not a consequence "
    "of it. That is the test that falls out of what we agreed last round: if a Step is a MOMENT in "
    "the cast, then two steps triggered by the same event are one step with two effects.\n\n"
    "  Shen     1 shields himself   + shields the lowest-HP allies\n"
    "  Orianna  1 shields an ally   + empowers her own next attack\n"
    "  Jayce    1 buffs his AS      + buffs adjacent allies' AP\n"
    "  Viego    1 fires his beam    + stacks his on-hit damage\n\n"
    "Shen's and Jayce's later steps renumbered down. A consequence still earns its own step - "
    "Jayce's burst is 'After Cast', so it stays Step 2.\n\n"
    "If you left this comment on a champion I have NOT named here, say which one: Swain, Azir, "
    "K'Sante, Kayle and Ahri were collapsed last round, so I have read those as already covered.")

MAOKAI_BODY = (
    "Done, and both of your comments on that row were pointing at the same thing.\n\n"
    "The step is GONE. His heal was never a passive - it is what his Empowered Attack DOES. As a "
    "separate always-on step it claimed he heals on attack whether or not he ever cast, which is "
    "false, and the 'If Empowered' condition was only there to take that claim back. A condition "
    "that exists to undo its own Step number is a workaround for a missing word, not a design.\n\n"
    "So the word now exists: a new Effect Detail, 'Empowered Attack (Maokai)' - the recipient's next "
    "auto-attack also HEALS them for 220/260/300% AP. One attack, then spent. It sits on his Step 1 "
    "Cast, which is a Buff, exactly as you said.\n\n"
    "This also keeps the split you settled back in round 2: Orianna and Maokai get ONE empowered "
    "attack, spent on the next hit; Viego's stacks and never falls off, so his is On-Hit Damage. "
    "Maokai's now differs from Orianna's in WHAT it does, rather than in how long it lasts.")

KARMA_BODY = (
    "Done - taken on trust, and the sheet says so now.\n\n"
    "  If not 3rd Cast  ->  Circle AOE        (Count 1)\n"
    "  If 3rd Cast      ->  Pierce Projectile (Count 3, Current + Left + Right)\n\n"
    "Worth saying plainly: this contradicts what I wrote last round. I collapsed her two casts into "
    "one step on the grounds that they were 'the same action, same amount, same AOE - they only ever "
    "differed by Count and Spread'. The first half of that was wrong, and the source text is what "
    "misled me.\n\n"
    "The collapse still stands, though, and for a better reason than the one I gave. Round 8 "
    "established that the rows of one step are BRANCHES that may run DIFFERENT actions - which is "
    "exactly what your correction describes. So Karma stays one step; her two branches simply fire "
    "different things.\n\n"
    "The Collision and shape came from the Action Model rather than from me: Pierce Projectile is "
    "Pierce-All / Line, so her 3rd cast now hits 'Enemies in path' and its AOE is an em-dash - a "
    "line has no circle radius. Circle AOE is Area / Circle, so the first branch keeps its 1-hex AOE.")

SWAIN_BODY = (
    "Done - his burn is a Passive at Step 0 now, not Step 2. You are right that it is not part of "
    "the cast: it ticks for as long as he is transformed, whether or not he casts again.\n\n"
    "One thing I did NOT do, and want to flag rather than bury. You said 'with condition when he was "
    "transformed', and I left the Condition column as an em-dash - because the Trigger already reads "
    "'When Transformed', and putting 'If Transformed' beside it would say the same thing twice. That "
    "is the rule your own Kalista comment set in round 5: her Trigger was 'On Spears Lethal' and her "
    "Condition 'If Lethal', and we deleted the Condition as redundant.\n\n"
    "If you meant the Condition column literally, say so and I will fill it in - but then Kalista's "
    "should come back too, and the rule should change for both.")

REPLIES = [
    # LONGEST KEY FIRST. "same step" is a substring of both of the keys below it, and post_replies
    # takes the FIRST key it finds in a comment's text - so a shorter key listed earlier would
    # swallow the comments meant for a longer one.
    ("same step with if else condition", ROUND8_BODY),          # already answered in round 8
    ("This are the same heal", ROUND5_SORAKA_BODY),             # already answered in round 5
    ("same step. but with if else condition", SAME_STEP_BODY),
    ("same step", SAME_STEP_BODY),
    ("Same step", SAME_STEP_BODY),                              # capital S: a different comment
    # Keys avoid apostrophes and quotes on purpose - the sheet's comments contain curly quotes and
    # non-breaking spaces, and a key that does not match fails SILENTLY.
    ("When I think carefully", MAOKAI_BODY),
    ("We should state in his empower attack effect", MAOKAI_BODY),
    ("1st, 2nd cast: do circle AOE", KARMA_BODY),
    ("Step 2 should be passive", SWAIN_BODY),
]


def val(row, c, name):
    i = c[name]
    return row[i].strip() if len(row) > i else ""


def champ_rows(vals, c, name):
    """0-based indices into `vals` of every row the champion owns (identity block is merged)."""
    out, cur = [], ""
    for i, r in enumerate(vals):
        if i == 0:
            continue
        if val(r, c, "Champion"):
            cur = val(r, c, "Champion")
        if cur == name:
            out.append(i)
    return out


def fix_maokai(sh):
    """Delete the heal row and fold it into his Empowered Attack. Two passes: delete, then rewrite.

    The row is found by its EFFECT, never by 'the row whose Step is 0.2'. Round 7 renumbered Irelia's
    steps and her "insert if she has no step 4" guard fired a second time, duplicating a row. A step
    number is a POSITION; the effect is the IDENTITY.
    """
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    c = cols(vals[0])

    rows = champ_rows(vals, c, "Maokai")
    heal = [i for i in rows
            if val(vals[i], c, "Effect Category") == "Buff"
            and val(vals[i], c, "Effect Detail") == "Heal"]
    if heal:
        ws.delete_rows(heal[0] + 1)
        print(f"Hero: deleted Maokai's step-0.2 heal row (row {heal[0] + 1}) — it is not a passive")
        vals = ws.get_all_values()          # indices below it have all shifted up by one
    else:
        print("Hero: Maokai's heal row is already gone")

    edits = []
    for i in champ_rows(vals, c, "Maokai"):
        if val(vals[i], c, "Effect Detail") in ("Empowered Attack", MAOKAI_EFFECT):
            for col, want in (("Effect Detail", MAOKAI_EFFECT), ("Amount", MAOKAI_AMOUNT)):
                if val(vals[i], c, col) != want:
                    edits.append({"range": f"{col_letter(c[col])}{i + 1}", "values": [[want]]})
    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Hero: Maokai's Empowered Attack — {len(edits)} cells updated")
    return bool(heal or edits)


def collapse(sh):
    """Blank the Step/Skill Type of every row that is not its own moment, and renumber below it."""
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    c = cols(vals[0])

    edits = []
    for name, spec in STEPS.items():
        rows = champ_rows(vals, c, name)
        if len(rows) != len(spec):
            raise SystemExit(f"{name} has {len(rows)} rows, expected {len(spec)} — not touching")
        for k, col in enumerate(("Step", "Skill Type")):
            for j, i in enumerate(rows):
                # LITERAL values, and a RAW comparison — NOT the fill_down trick the other columns
                # use. This is the one place that trick is fatal, and it cost a full acceptance run
                # to find out why:
                #
                #   `Step` is what remerge() reads to FIND the step boundaries. Writing the filled
                #   value ("1") into a continuation row instead of a blank makes that row look like
                #   a NEW STEP START. remerge then refuses to merge it away, so the "1" stays
                #   visible; round 7's renumber_steps() then sees TWO steps both numbered 1, and
                #   renumbers everything below them - which this script undoes on its next run, for
                #   ever.
                #
                # A blank continuation row must therefore BE blank. Round 8's KSANTE_FIX already
                # writes a literal "" for exactly this reason.
                want = spec[j][k]
                if vals[i][c[col]].strip() != want:
                    edits.append({"range": f"{col_letter(c[col])}{i + 1}", "values": [[want]]})

    if not edits:
        print("Hero: Shen, Orianna, Jayce and Viego are already collapsed")
        return False

    # Unmerge before writing, or a merged cell silently eats the write.
    sh.batch_update({"requests": [{"unmergeCells": {"range": {
        "sheetId": ws.id, "startRowIndex": 1, "endRowIndex": len(vals),
        "startColumnIndex": c["Step"], "endColumnIndex": c["Aim Target"] + 1}}}]})
    ws.batch_update(edits, value_input_option="RAW")
    print(f"Hero: {len(edits)} cells rewritten — 4 champions collapsed, Shen and Jayce renumbered")
    return True


def add_effect_type(sh):
    ws = sh.worksheet("Effect Types")
    vals = ws.get_all_values()
    have = {(r[0].strip(), r[1].strip()) for r in vals if len(r) > 1}
    pending = [r for r in EFFECT_TYPES if (r[0], r[1]) not in have]
    if pending:
        ws.append_rows(pending, value_input_option="RAW")
    print(f"Effect Types: added {len(pending)} rows")


def main():
    sh = open_sheet()
    changed = fix_maokai(sh)
    changed = collapse(sh) or changed
    if changed:
        remerge(sh)
    add_effect_type(sh)
    sync_notes(sh, NOTES)
    post_replies(REPLIES, warn_unmatched=False)


if __name__ == "__main__":
    main()
