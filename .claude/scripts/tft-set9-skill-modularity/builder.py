"""Reusable hero-row builder.  `from builder import build`

Produces 33-column `hero.csv` rows with the sheet's blanking rules baked in — supply champion data
only, never hand-write CSV. Used by the `/add-champion` skill's build step.

    build(identity, steps) -> list[list[str]]

    identity : 11 cells
        [Champion, Cost, Role, Damage Type, Origin1, Origin2, Class1, Class2, Range, Summary,
         Skill Description]
    `Role` is one of the five nouns on the 'Role Types' tab and `Damage Type` is AD | AP | '—';
    both are validated. They are two columns rather than Set 10's single glued `ADTank`/`APCaster`.
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
  - identity (0-10): champion's FIRST row only; blank after (merged per champion).
  - Step + Skill Type (11,12): first row of each STEP only. Compared RAW.
  - run columns (Trigger 13, Cond 14, Source 15, Legacy action 16, Aim 17, Count/Spread 21-22,
    Cast 24): on each ACTION's first row. Condition and Cast write '—' on a defining row with no
    value; blank on continuations so they inherit + merge.
  - Skill Range (20): the hero's Range (identity[8]) on each action-start.
  - AOE (19) + Offset (18): the action's values on its first effect row; blank on continuations.
  - effect columns (25-32): filled on every row.

33-col layout (Cast closes the ACTION region; the effect block starts at 25). Every index after 2
shifted by one when `Damage Type` was inserted on 2026-07-21 — if you are reading a stale index
somewhere, that is why:
  0-10 identity | 11 Step 12 SkillType | 13 Trigger 14 Cond | 15 Source 16 LegacyAction
  17 Aim 18 Offset 19 AOE | 20 SkillRange 21 Count 22 Spread 23 FireTiming 24 Cast
  25 Recip 26 Cat 27 Detail 28 Amount 29 ScalType 30 Scaling 31 Cadence 32 Duration
"""

D = "—"
NCOLS = 33


def build(identity, steps):
    assert len(identity) == 11, "identity must be 11 cells"
    out, first_champ = [], True
    skill_range = identity[8]
    for step_no, skill_type, actions in steps:
        first_step = True
        for trig, src, action, cnt, spr, fire, aim, cast, effects in actions:
            for ei, eff in enumerate(effects):
                cond, recip, cat, det, amt, st, sc, cad, dur, aoe, offset = eff
                r = [""] * NCOLS
                if first_champ:
                    r[:11] = identity
                    first_champ = False
                if first_step:
                    r[11], r[12] = step_no, skill_type
                    first_step = False
                if ei == 0:                            # action-start row
                    r[13] = trig
                    r[15], r[16] = src, action
                    r[17], r[18], r[19] = aim, offset, aoe
                    r[20], r[21], r[22], r[23], r[24] = skill_range, cnt, spr, fire, cast
                r[14] = cond or (D if ei == 0 else "")
                r[25], r[26], r[27], r[28] = recip, cat, det, amt
                r[29], r[30], r[31], r[32] = st, sc, cad, dur
                out.append(r)
    return out


if __name__ == "__main__":  # tiny self-test
    rows = build(
        ["Test", "1 Gold", "Mage", "AP", "Void", "", "Sorcerer", "", "4", "Nick", "Desc"],
        [("1", "Active", [("On Cast", "Self", "Circle AOE", "1", D, D, "Current", D,
            [("", "Enemies in area", "Attack", "Damage", "100% AP", D, D, "Once", D, "1", "centred"),
             ("", "Enemies in area", "Status", "Stun", D, D, D, "Once", "2", D, "")])])])
    assert all(len(r) == 33 for r in rows)
    assert rows[0][3] == "AP" and rows[0][2] == "Mage"     # the split identity pair
    assert rows[0][16] == "Circle AOE" and rows[0][19] == "1" and rows[0][18] == "centred"
    assert rows[0][23] == D and rows[0][24] == D       # fire timing (23) and cast (24), per-ACTION
    assert rows[1][23] == "" and rows[1][24] == ""     # blank on continuations
    assert rows[1][16] == "" and rows[1][19] == "" and rows[1][0] == ""     # per-action cols blank on continuation
    print("builder self-test ok:", len(rows), "rows")
