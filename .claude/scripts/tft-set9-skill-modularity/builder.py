"""Reusable hero-row builder.  `from builder import build`

Produces 32-column `hero.csv` rows with the sheet's blanking rules baked in — supply champion data
only, never hand-write CSV. Used by the `/add-champion` skill's build step.

    build(identity, steps) -> list[list[str]]

    identity : 10 cells
        [Champion, Cost, Role, Origin1, Origin2, Class1, Class2, Range, Summary, Skill Description]
    steps    : [(step_no, skill_type, actions), ...]
        actions : [(trigger, source, action, count, spread, collision, aim, effects), ...]
            effects : [(condition, recipient, category, detail, amount, scaling_type, scaling,
                        cadence, duration, aoe, offset, cast), ...]
    Put the ACTION's AOE and Offset on its FIRST effect (later effects' aoe/offset are ignored — both
    are per-action and merge down). AOE = shape size (e.g. '1', '1×2', 'cone'); Offset = the anchor
    label for a shape AOE ('centred' / 'rear edge' / 'front edge' / 'detached +N'), '—' for non-AOE
    actions. Cast/Leap take Count '—'. Star-varying counts use slash notation ('6/6/25').

WHY EACH BLANKING RULE (each learned by breaking it — see [[tft-sheet-scripts]]):
  - identity (0-9): champion's FIRST row only; blank after (merged per champion).
  - Step + Skill Type (10,11): first row of each STEP only. Compared RAW, so a filled continuation
    row reads as a NEW step and never merges away.
  - run columns (Trigger 12 .. Collision 22, incl. AOE/Offset): on each ACTION's first row. Condition
    writes '—' on a no-condition defining row — blank would inherit the champion above via sync's
    whole-column fill_down. All run cols blank on continuation effect rows so they inherit + merge.
  - Skill Range (19): the hero's Range (identity[7]) on each action-start; blank on continuations.
  - AOE (18) + Offset (17): the action's values on its first effect row; blank on continuations so
    they merge (both are per-action).
  - effect columns: filled on every row.

32-col layout (action region regrouped: who/what/where, then delivery detail, then effects):
  0-9 identity | 10 Step 11 SkillType | 12 Trigger 13 Cond
  14 ActionSource 15 Action 16 Aim 17 Offset 18 AOE 19 SkillRange 20 Count 21 Spread 22 Collision
  23 Recip 24 Cat 25 Detail 26 Amount 27 ScalType 28 Scaling 29 Cadence 30 Duration 31 Cast
"""

D = "—"
NCOLS = 32


def build(identity, steps):
    assert len(identity) == 10, "identity must be 10 cells"
    out, first_champ = [], True
    skill_range = identity[7]                         # Skill Range defaults to the hero's Range
    for step_no, skill_type, actions in steps:
        first_step = True
        for trig, src, act, cnt, spr, col, aim, effects in actions:
            for ei, eff in enumerate(effects):
                cond, recip, cat, det, amt, st, sc, cad, dur, aoe, offset, cast = eff
                r = [""] * NCOLS
                if first_champ:
                    r[:10] = identity
                    first_champ = False
                if first_step:
                    r[10], r[11] = step_no, skill_type
                    first_step = False
                if ei == 0:                            # action-start row: run cols + skill range + AOE/Offset
                    r[12] = trig
                    r[14], r[15], r[16] = src, act, aim
                    r[17], r[18] = offset, aoe
                    r[19], r[20], r[21], r[22] = skill_range, cnt, spr, col
                r[13] = cond or (D if ei == 0 else "")
                r[23], r[24], r[25], r[26] = recip, cat, det, amt
                r[27], r[28], r[29], r[30], r[31] = st, sc, cad, dur, cast
                out.append(r)
    return out


if __name__ == "__main__":  # tiny self-test
    rows = build(
        ["Test", "1 Gold", "Carry", "Void", "", "Sorcerer", "", "4", "Nick", "Desc"],
        [("1", "Active", [("On Cast", "Self", "Circle AOE", "1", D, "Area", "Current",
            [("", "Enemies in area", "Attack", "Damage", "100% AP", D, D, "Once", D, "1", "centred", D),
             ("", "Enemies in area", "Status", "Stun", D, D, D, "Once", "2", D, "", D)])])])
    assert all(len(r) == 32 for r in rows)
    assert rows[0][19] == "4" and rows[0][18] == "1" and rows[0][17] == "centred"  # range + AOE + offset
    assert rows[1][18] == "" and rows[1][17] == "" and rows[1][0] == ""            # per-action cols blank on continuation
    print("builder self-test ok:", len(rows), "rows")
