"""Reusable hero-row builder.  `from builder import build`

Produces 31-column `hero.csv` rows with the sheet's blanking rules baked in — supply champion data
only, never hand-write CSV. Used by the `/add-champion` skill's build step.

    build(identity, steps) -> list[list[str]]

    identity : 10 cells
        [Champion, Cost, Role, Origin1, Origin2, Class1, Class2, Range, Summary, Skill Description]
    steps    : [(step_no, skill_type, actions), ...]
        actions : [(trigger, source, action, count, spread, collision, aim, effects), ...]
            effects : [(condition, recipient, category, detail, amount, scaling_type, scaling,
                        cadence, duration, aoe, cast), ...]
    Put the ACTION's AOE on its FIRST effect (later effects' aoe is ignored — AOE is per-action and
    merges down). Cast/Leap take Count '—'. Star-varying counts use slash notation ('6/6/25').

WHY EACH BLANKING RULE (each learned by breaking it — see [[tft-sheet-scripts]]):
  - identity (0-9): champion's FIRST row only; blank after (merged per champion).
  - Step + Skill Type (10,11): first row of each STEP only. Compared RAW, so a filled continuation
    row reads as a NEW step and never merges away.
  - run columns (Trigger 12 .. Aim Target 20): on each ACTION's first row. Condition writes '—' on a
    no-condition defining row — blank would inherit the champion above via sync's whole-column
    fill_down. All run cols blank on continuation effect rows so they inherit + merge.
  - Skill Range (19): the hero's Range (identity[7]) on each action-start; blank on continuations.
  - AOE (29): the action's AOE on its first effect row; blank on continuations so it merges.
  - effect columns: filled on every row.

31-col layout (Skill Range inserted before Aim Target):
  0-9 identity | 10 Step 11 SkillType | 12 Trigger 13 Cond 14 Src 15 Action 16 Count 17 Spread
  18 Collision 19 SkillRange 20 Aim | 21 Recip 22 Cat 23 Detail 24 Amount 25 ScalType 26 Scaling
  27 Cadence 28 Duration 29 AOE 30 Cast
"""

D = "—"
NCOLS = 31


def build(identity, steps):
    assert len(identity) == 10, "identity must be 10 cells"
    out, first_champ = [], True
    skill_range = identity[7]                         # Skill Range defaults to the hero's Range
    for step_no, skill_type, actions in steps:
        first_step = True
        for trig, src, act, cnt, spr, col, aim, effects in actions:
            for ei, eff in enumerate(effects):
                cond, recip, cat, det, amt, st, sc, cad, dur, aoe, cast = eff
                r = [""] * NCOLS
                if first_champ:
                    r[:10] = identity
                    first_champ = False
                if first_step:
                    r[10], r[11] = step_no, skill_type
                    first_step = False
                if ei == 0:                            # action-start row: run cols + skill range + AOE
                    r[12], r[14], r[15], r[16] = trig, src, act, cnt
                    r[17], r[18], r[19], r[20] = spr, col, skill_range, aim
                    r[29] = aoe
                r[13] = cond or (D if ei == 0 else "")
                r[21], r[22], r[23], r[24] = recip, cat, det, amt
                r[25], r[26], r[27], r[28], r[30] = st, sc, cad, dur, cast
                out.append(r)
    return out


if __name__ == "__main__":  # tiny self-test
    rows = build(
        ["Test", "1 Gold", "Carry", "Void", "", "Sorcerer", "", "4", "Nick", "Desc"],
        [("1", "Active", [("On Cast", "Self", "Circle AOE", "1", D, "Area", "Current",
            [("", "Enemies in area", "Attack", "Damage", "100% AP", D, D, "Once", D, "1", D),
             ("", "Enemies in area", "Status", "Stun", D, D, D, "Once", "2", D, D)])])])
    assert all(len(r) == 31 for r in rows)
    assert rows[0][19] == "4" and rows[0][29] == "1"       # skill range + action AOE on the start row
    assert rows[1][29] == "" and rows[1][0] == ""          # AOE + identity blank on the continuation
    print("builder self-test ok:", len(rows), "rows")
