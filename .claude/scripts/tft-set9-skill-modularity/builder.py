"""Reusable hero-row builder.  `from builder import build`

Produces 36-column `hero.csv` rows with the sheet's blanking rules baked in — supply champion data
only, never hand-write CSV. Used by the `/add-champion` skill's build step.

    build(identity, steps) -> list[list[str]]

    identity : 10 cells
        [Champion, Cost, Role, Origin1, Origin2, Class1, Class2, Range, Summary, Skill Description]
    steps    : [(step_no, skill_type, actions), ...]
        actions : [(trigger, source, apply, spawn, motion, behavior, shape, count, spread,
                    collision, aim, effects), ...]
            effects : [(condition, recipient, category, detail, amount, scaling_type, scaling,
                        cadence, duration, aoe, offset, cast), ...]

    The action is DECOMPOSED (v2 model), not one lumped name:
      apply    : DirectApply | Hitbox
      spawn    : at-User | at-Target        (Hitbox only, else '—')
      motion   : '—' | Projectile | Arc | Forward N hex
      behavior : First-Hit | Homing | Pierce | Returning   (Motion=Projectile only, else '—')
      shape    : 1-hex | circle | cone | box | custom       (Hitbox only, else '—')
    Collision is KEPT (not derivable — Grab & Slam = Flank-Pair). Put the ACTION's AOE and Offset on
    its FIRST effect (per-action, they merge down). Cast/Leap take Count '—'; star-varying counts use
    slash notation ('6/6/25').

WHY EACH BLANKING RULE (each learned by breaking it — see [[tft-sheet-scripts]]):
  - identity (0-9): champion's FIRST row only; blank after (merged per champion).
  - Step + Skill Type (10,11): first row of each STEP only. Compared RAW.
  - run columns (Trigger 12 .. Aim Target 20, plus the 5 axes 15-19, Count/Spread/Collision 24-26):
    on each ACTION's first row. Condition writes '—' on a no-condition defining row; blank on
    continuations so it inherits + merges.
  - Skill Range (23): the hero's Range (identity[7]) on each action-start.
  - AOE (22) + Offset (21): the action's values on its first effect row; blank on continuations.
  - effect columns (27-35): filled on every row.

36-col layout:
  0-9 identity | 10 Step 11 SkillType | 12 Trigger 13 Cond | 14 Source
  15 Apply 16 Spawn 17 Motion 18 Behavior 19 Shape | 20 Aim 21 Offset 22 AOE
  23 SkillRange 24 Count 25 Spread 26 Collision
  27 Recip 28 Cat 29 Detail 30 Amount 31 ScalType 32 Scaling 33 Cadence 34 Duration 35 Cast
"""

D = "—"
NCOLS = 36


def build(identity, steps):
    assert len(identity) == 10, "identity must be 10 cells"
    out, first_champ = [], True
    skill_range = identity[7]
    for step_no, skill_type, actions in steps:
        first_step = True
        for trig, src, apply, spawn, motion, behavior, shape, cnt, spr, col, aim, effects in actions:
            for ei, eff in enumerate(effects):
                cond, recip, cat, det, amt, st, sc, cad, dur, aoe, offset, cast = eff
                r = [""] * NCOLS
                if first_champ:
                    r[:10] = identity
                    first_champ = False
                if first_step:
                    r[10], r[11] = step_no, skill_type
                    first_step = False
                if ei == 0:                            # action-start row
                    r[12] = trig
                    r[14] = src
                    r[15], r[16], r[17], r[18], r[19] = apply, spawn, motion, behavior, shape
                    r[20], r[21], r[22] = aim, offset, aoe
                    r[23], r[24], r[25], r[26] = skill_range, cnt, spr, col
                r[13] = cond or (D if ei == 0 else "")
                r[27], r[28], r[29], r[30] = recip, cat, det, amt
                r[31], r[32], r[33], r[34], r[35] = st, sc, cad, dur, cast
                out.append(r)
    return out


if __name__ == "__main__":  # tiny self-test
    rows = build(
        ["Test", "1 Gold", "Carry", "Void", "", "Sorcerer", "", "4", "Nick", "Desc"],
        [("1", "Active", [("On Cast", "Self", "Hitbox", "at-Target", D, D, "circle", "1", D, "Area", "Current",
            [("", "Enemies in area", "Attack", "Damage", "100% AP", D, D, "Once", D, "1", "centred", D),
             ("", "Enemies in area", "Status", "Stun", D, D, D, "Once", "2", D, "", D)])])])
    assert all(len(r) == 36 for r in rows)
    assert rows[0][15] == "Hitbox" and rows[0][19] == "circle" and rows[0][22] == "1" and rows[0][21] == "centred"
    assert rows[1][15] == "" and rows[1][22] == "" and rows[1][0] == ""     # per-action cols blank on continuation
    print("builder self-test ok:", len(rows), "rows")
