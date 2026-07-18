"""ONE-SHOT: give `AOE (hex)` a real notation, in a new `AOE shape` tab.

    python .claude/scripts/tft-set9-skill-modularity/migrate_aoe_shape.py

Run ONCE, then archive/. Rewrites hero.csv + action-model.csv and writes data/aoe-shape.csv.

THE USER: "It is time we assign the meaning of 'AOE (hex)' for each AOE shape. Make a new tab 'AOE
shape': Box: 1x2 (hori x verti) / Cone: Cone 1 hex [xxx, x] / Cone 2 hex [xxxxx, xxx, x] / Circle:
Circle 1 hex = 1 hex around the target."

The column had become prose - '4 (1 hex at range 1, 3 at range 2)', 'Gwen-shaped', 'X-shape', '1x3
(horizontal)' - so no two cells meant the same thing the same way, and 'Gwen-shaped' was a POINTER to
another champion's cell. Every value is now a key into the new tab, checked by VALIDATE.

CONE N HEX: widest row 2N+1, depth N+1 rows (confirmed with the user). Cone 1 hex is 1 hex at range 1
and 3 at range 2 - which is exactly what Kassadin's prose already said, so the notation fits the data
rather than replacing it.

THE FOUR THE USER DECIDED PER-CHAMPION (each was a row the notation could not express):
  Teemo     '1 (2 at 4-Star)' was a star-varying AOE, which no single key can be. Their answer is
            better than any notation: SPLIT THE STEP into two conditioned branches, the way Swain and
            Karma already are. 'If not 4-Star' -> Circle 1 hex; 'If 4-Star' -> Circle 2 hex.
  Sona      'Send a WAVE' - a wave is wide, so her AOE '2' was a real width the model had lost when
            'Wave' was retired into Pierce Projectile. It is Box 1.5x2, and she needs an action whose
            Shape is box while still piercing -> WAVE IS BACK (see below).
  Malzahar  'all enemies caught BETWEEN the portals' = a 3-wide bar: Box 3x1 (hori x verti), per the
            user's picture (xxx over o).
  Gwen      Box 0.1x2 - the BLADE, not the arc it sweeps. So AOE (hex) describes the HITBOX; the
            sweep stays in Motion=Arc, and she keeps Sweep Laser (the user's call).

WHY 'WAVE' COMES BACK, having been retired as "a duplicate of Pierce Projectile": it was retired
BEFORE Shape was an axis, when the two really were identical. Pierce Projectile is Shape=1-hex - a
bolt - and six champions depend on that. A wave pierces the same way but is a BOX. With Shape as an
axis they are no longer duplicates, so Sona gets her own action and the rule that an action determines
its own axes survives intact. That rule is the whole basis of the lookup; bending it for one champion
would have cost more than one row.
"""

import csv
import pathlib

DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")
D = "—"

# (action, old AOE) -> new AOE key. Every AOE cell in the sheet is listed; anything unmatched raises,
# so a row cannot be silently left in the old prose.
REMAP = {
    ("Circle AOE", "1"): "Circle 1 hex",
    ("Circle AOE", "2"): "Circle 2 hex",
    ("Burst Projectile", "1"): "Circle 1 hex",
    ("Homing Burst Projectile", "2"): "Circle 2 hex",
    ("Cone AOE", "4 (1 hex at range 1, 3 at range 2)"): "Cone 1 hex",   # Kassadin
    ("Cone AOE", "Gwen-shaped"): "Cone 1 hex",                          # Aatrox
    ("Cone AOE", "3 (1 on the tip, 2 on the edge)"): "Cone 1 hex",      # Urgot
    ("Box AOE", "1×2"): "Box 1x2",                                      # Aatrox
    ("Laser Shot", "1×3 (horizontal)"): "Box 3x1",                      # Malzahar
    ("Sweep Laser", "4 (1 hex at range 1, 3 at range 2)"): "Box 0.1x2",  # Gwen: the blade
    ("Custom AOE", "X-shape"): "X-shape",                               # Miss Fortune: genuinely odd
    ("Pierce Projectile", "2"): "Box 1.5x2",                            # Sona -> Wave, below
}

# The tab. One row per key in use, grouped by shape, plus Cone 2 hex which the user gave as the
# notation's second example — the only row here with no user, kept because it is what TEACHES the rule.
AOE_SHAPE = [
    ["AOE (hex)", "Shape", "Meaning", "Picture (o = the origin hex)"],
    ["Circle 1 hex", "circle", "Every hex within 1 of the centre.", "o = centre\n1 ring around it"],
    ["Circle 2 hex", "circle", "Every hex within 2 of the centre.", "o = centre\n2 rings around it"],
    ["Cone 1 hex", "cone",
     "Widest row 3, depth 2. 1 hex at range 1, 3 at range 2 — 4 hexes.",
     "x x x\n  x\n  o"],
    ["Cone 2 hex", "cone",
     "Widest row 5, depth 3. 1 hex at range 1, 3 at range 2, 5 at range 3 — 9 hexes. "
     "NOT YET USED — here to show the rule.",
     "x x x x x\n  x x x\n    x\n    o"],
    ["Box 1x2", "box", "1 wide, 2 deep (hori × verti).", "x\nx\no"],
    ["Box 1.5x2", "box", "1.5 wide, 2 deep. A wave — wider than a bolt, narrower than 2 hexes.",
     "[ x ]\n[ x ]\n  o"],
    ["Box 3x1", "box", "3 wide, 1 deep. A bar across the facing.", "x x x\n  o"],
    ["Box 0.1x2", "box", "A blade: near-zero width, 2 deep.", "|\n|\no"],
    ["X-shape", "custom", "Miss Fortune's X. Does not fit Circle/Cone/Box and is not meant to.",
     "x   x\n  x\nx   x"],
    [],
    ["How to read this tab"],
    ["Every AOE (hex) cell in Hero is a KEY here. sync VALIDATE fails on one with no row, so the "
     "column cannot drift back into prose — it held '4 (1 hex at range 1, 3 at range 2)', "
     "'Gwen-shaped' and 'X-shape' at once, and 'Gwen-shaped' was a pointer to another champion's cell."],
    ["CONE N HEX: widest row = 2N+1, depth = N+1 rows. So the number is the SPREAD to each side at "
     "the far edge, not the total hexes and not the reach."],
    ["BOX WxD: width × depth in hexes, facing the aim. Fractions are real — a wave is 1.5 wide and a "
     "blade is 0.1."],
    ["THIS IS THE HITBOX, not the area a moving hitbox covers. Gwen's blade is Box 0.1x2 even though "
     "her sweep traces a cone: the sweep is Motion=Arc on the action, not a shape."],
    ["An action with no area at all (a Cast, a Move, a 1-hex bolt) reads '—' here, not a size."],
]


def read(name):
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return [r for r in csv.reader(f)]


def write(name, rows):
    with (DATA / name).open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)


def main():
    hero = read("hero.csv")
    h = hero[0]
    c = {n: h.index(n) for n in h}

    # --- Teemo: split step 1 into a 4-star branch, so each AOE is a plain key -------------------
    champ, t = "", []
    for n, r in enumerate(hero):
        if n and r[c["Champion"]].strip():
            champ = r[c["Champion"]].strip()
        if champ == "Teemo" and n:
            t.append(n)
    assert len(t) == 2, f"expected Teemo to own 2 rows, found {len(t)}"
    a1, a2 = hero[t[0]], hero[t[1]]
    a1[c["Condition (Only if)"]] = "If not 4-Star"
    a1[c["AOE (hex)"]] = "Circle 1 hex"

    b1, b2 = list(a1), list(a2)
    for col in h:                       # branch B inherits everything it does not change
        b1[c[col]] = ""
    b1[c["Condition (Only if)"]] = "If 4-Star"
    b1[c["AOE (hex)"]] = "Circle 2 hex"       # "4-Star Upgrade: Increase the explosion radius by 1"
    for col in ("Effect Recipient", "Effect Category", "Effect Detail", "Amount", "Scaling Type",
                "Scaling", "Effect Cadence", "Effect Duration (s)"):
        b1[c[col]] = a1[c[col]]
    hero[t[1] + 1:t[1] + 1] = [b1, b2]
    print(f"  Teemo    step 1 split: 'If not 4-Star' (Circle 1 hex) / 'If 4-Star' (Circle 2 hex)")

    # --- Sona: Pierce Projectile -> Wave (same delivery, box-shaped) ----------------------------
    champ, n_sona = "", 0
    for n, r in enumerate(hero):
        if n and r[c["Champion"]].strip():
            champ = r[c["Champion"]].strip()
        if champ == "Sona" and r[c["Legacy action"]].strip() == "Pierce Projectile":
            r[c["Legacy action"]] = "Wave"
            n_sona += 1
    assert n_sona == 1, f"expected 1 Sona Pierce Projectile row, found {n_sona}"
    print("  Sona     Pierce Projectile -> Wave (pierces the same, but is a box)")

    # --- every AOE cell -> a key -----------------------------------------------------------------
    action, changed, unmatched = "", 0, []
    for n, r in enumerate(hero):
        if n == 0:
            continue
        if r[c["Legacy action"]].strip():
            action = r[c["Legacy action"]].strip()
        v = r[c["AOE (hex)"]].strip()
        if not v or v == D:
            continue
        key = ("Pierce Projectile" if action == "Wave" else action, v)
        if key in REMAP:
            if r[c["AOE (hex)"]] != REMAP[key]:
                r[c["AOE (hex)"]] = REMAP[key]
                changed += 1
        elif v not in {x[0] for x in AOE_SHAPE if x}:
            unmatched.append((action, v))
    if unmatched:
        raise SystemExit(f"AOE values with no mapping: {sorted(set(unmatched))}")
    write("hero.csv", hero)
    print(f"hero.csv: {changed} AOE cells rewritten to keys, {len(hero) - 1} rows")

    write("aoe-shape.csv", AOE_SHAPE)
    print(f"aoe-shape.csv: {sum(1 for r in AOE_SHAPE[1:] if r and r[0] and len(r) > 1)} shapes")

    # --- the tab gains Wave -----------------------------------------------------------------------
    am = read("action-model.csv")
    ah = am[0]
    a = {n: ah.index(n) for n in ah}
    doc_at = next(i for i, r in enumerate(am) if not any(x.strip() for x in r))
    if not any(r[0].strip() == "Wave" for r in am[1:doc_at]):
        row = [""] * len(ah)
        for k, v in (("Legacy Action", "Wave"), ("Apply", "Hitbox"), ("Spawn", "at-User"),
                     ("Motion", "Projectile"), ("Behavior", "Pierce"), ("Shape", "box"),
                     ("Offset", D), ("Collision", "Pierce-All")):
            row[a[k]] = v
        row[a["What it does"]] = ("A wide projectile that passes THROUGH every unit in its path, "
                                  "hitting all of them.")
        row[a["Clarify more"]] = (
            "Has travel speed. A Pierce Projectile that is a BOX rather than a 1-hex bolt - Sona's "
            "'send a wave'. It was retired once for being 'a duplicate of Pierce Projectile', and "
            "that was true BEFORE Shape was an axis, when the two were identical. They are not: a "
            "bolt hits a line of units, a wave is 1.5 hexes wide. Its size is in AOE (hex).")
        am.insert(doc_at, row)
        write("action-model.csv", am)
        print("action-model.csv: +Wave (Hitbox/at-User/Projectile/Pierce/box)")


if __name__ == "__main__":
    main()
