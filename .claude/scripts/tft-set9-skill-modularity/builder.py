"""Reusable hero-row builder.  `from builder import build`

Produces 31-column `hero.csv` rows with the sheet's blanking rules baked in — supply champion data
only, never hand-write CSV. Used by the `/add-champion` skill's build step.

    build(identity, steps) -> list[list[str]]

    identity : 10 cells
        [Champion, Cost, Role, Origin1, Origin2, Class1, Class2, Range, Summary, Skill Description]
    steps    : [(step_no, skill_type, actions), ...]
        actions : [(trigger, source, action, count, spread, fire_timing, aim, cast, effects), ...]
            effects : [(condition, recipient, category, detail, amount, scaling_type, scaling,
                        cadence, duration, aoe, offset), ...]
    `fire_timing` is At Once | Consecutive when Count > 1, else '—' (see the 'Fire Timing Types' tab).

    `action` is a KEY into the Action Model tab (data/action-model.csv) — 'Pierce Projectile',
    'Circle AOE', 'Cast'. It must match a row there EXACTLY or sync.py VALIDATE fails; that tab holds
    the mechanics (Apply/Spawn/Motion/Behavior/Shape) AND the Collision, so none are repeated per row.
    `cast` is the action's channel time in seconds — '—' for the ~all that have none assigned. It is
    an ACTION field, not an effect one: one cast time per action, however many effects it produces.
    Offset/AOE stay per-row (an action's shape is fixed but its SIZE and anchor are not). Put the
    ACTION's AOE and Offset on its FIRST effect (per-action, they merge down). Cast/Move take Count
    '—'; star-varying counts use slash notation ('6/6/25').

WHY EACH BLANKING RULE (each learned by breaking it — see [[tft-sheet-scripts]]):
  - identity (0-9): champion's FIRST row only; blank after (merged per champion).
  - Step + Skill Type (10,11): first row of each STEP only. Compared RAW.
  - run columns (Trigger 12, Cond 13, Source 14, Legacy action 15, Aim 16, Count/Spread 20-21,
    Cast 22): on each ACTION's first row. Condition and Cast write '—' on a defining row with no
    value; blank on continuations so they inherit + merge.
  - Skill Range (19): the hero's Range (identity[7]) on each action-start.
  - AOE (18) + Offset (17): the action's values on its first effect row; blank on continuations.
  - effect columns (23-30): filled on every row.

32-col layout (Cast closes the ACTION region; the effect block starts at 24):
  0-9 identity | 10 Step 11 SkillType | 12 Trigger 13 Cond | 14 Source 15 LegacyAction
  16 Aim 17 Offset 18 AOE | 19 SkillRange 20 Count 21 Spread 22 FireTiming 23 Cast
  24 Recip 25 Cat 26 Detail 27 Amount 28 ScalType 29 Scaling 30 Cadence 31 Duration
"""

D = "—"
NCOLS = 32


def build(identity, steps):
    assert len(identity) == 10, "identity must be 10 cells"
    out, first_champ = [], True
    skill_range = identity[7]
    for step_no, skill_type, actions in steps:
        first_step = True
        for trig, src, action, cnt, spr, fire, aim, cast, effects in actions:
            for ei, eff in enumerate(effects):
                cond, recip, cat, det, amt, st, sc, cad, dur, aoe, offset = eff
                r = [""] * NCOLS
                if first_champ:
                    r[:10] = identity
                    first_champ = False
                if first_step:
                    r[10], r[11] = step_no, skill_type
                    first_step = False
                if ei == 0:                            # action-start row
                    r[12] = trig
                    r[14], r[15] = src, action
                    r[16], r[17], r[18] = aim, offset, aoe
                    r[19], r[20], r[21], r[22], r[23] = skill_range, cnt, spr, fire, cast
                r[13] = cond or (D if ei == 0 else "")
                r[24], r[25], r[26], r[27] = recip, cat, det, amt
                r[28], r[29], r[30], r[31] = st, sc, cad, dur
                out.append(r)
    return out


if __name__ == "__main__":  # tiny self-test
    rows = build(
        ["Test", "1 Gold", "Carry", "Void", "", "Sorcerer", "", "4", "Nick", "Desc"],
        [("1", "Active", [("On Cast", "Self", "Circle AOE", "1", D, D, "Current", D,
            [("", "Enemies in area", "Attack", "Damage", "100% AP", D, D, "Once", D, "1", "centred"),
             ("", "Enemies in area", "Status", "Stun", D, D, D, "Once", "2", D, "")])])])
    assert all(len(r) == 32 for r in rows)
    assert rows[0][15] == "Circle AOE" and rows[0][18] == "1" and rows[0][17] == "centred"
    assert rows[0][22] == D and rows[0][23] == D       # fire timing (22) and cast (23), per-ACTION
    assert rows[1][22] == "" and rows[1][23] == ""     # blank on continuations
    assert rows[1][15] == "" and rows[1][18] == "" and rows[1][0] == ""     # per-action cols blank on continuation
    print("builder self-test ok:", len(rows), "rows")
