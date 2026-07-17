"""ONE-SHOT: drop Hero's `Collision` column — the action already decides it — and add the
`Effect Recipient` vocabulary tab.

    python .claude/scripts/tft-set9-skill-modularity/migrate_drop_collision.py

Run ONCE, then archive/. Rewrites hero.csv, writes data/effect-recipient-types.csv. The sheet-side
column delete is migrate_drop_collision_sheet.py.

THE USER: "Collision is no need here anymore, get rid of it. Is that make sense though?"

It does, and the sheet earned it. Collision was kept per-row for a REAL reason: `Burst Projectile`
was First-Hit on three rows and Target-Only on one, which no per-action lookup can say. That last
exception was Urgot — and he turned out not to be a Burst Projectile at all but a Cone AOE. With him
moved, EVERY action has exactly one Collision (verified below, not assumed), so the column restates
the Action Model tab on every row: the same drift risk the five axes had.

WHAT IF A FUTURE CHAMPION BREAKS IT? Then they get their own action, exactly as Wave and Cone AOE
just did. That is the model working, not failing: an action is a bundle of mechanics, and a champion
whose mechanics differ has a different action.

`collision-types.csv` STAYS. Hero no longer uses it, but the Action Model tab's Collision column does,
and validate_data() now checks THAT — a tab-against-tab check, which is new: with no Hero column left
to validate, nothing else would notice the taxonomy rotting.

EFFECT RECIPIENT: "Make a tab for Effect Recipient too. This is for reinforcement of the vocab like
Trigger tab." Same deal: the tab is not the point, the VALIDATE is. Seeded from the 16 values in use.
"""

import csv
import pathlib

DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")
D = "—"
COL = "Collision (If it have one)"


def read(name):
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return [r for r in csv.reader(f)]


def write(name, rows):
    with (DATA / name).open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)


def fill_down(seq):
    out, prev = [], ""
    for v in seq:
        if v.strip():
            prev = v
        out.append(prev)
    return out


def main():
    hero = read("hero.csv")
    h = hero[0]
    ci, li = h.index(COL), h.index("Legacy action")

    # PROVE it is derivable before deleting it. A blank Collision inherits the row above (it is a run
    # column), so compare EFFECTIVE values or you invent splits that are not there.
    eff = fill_down([r[ci] for r in hero[1:]])
    per_action = {}
    for r, e in zip(hero[1:], eff):
        n = r[li].strip()
        if n:
            per_action.setdefault(n, set()).add(e.strip())
    varies = {n: v for n, v in per_action.items() if len(v - {""}) > 1}
    if varies:
        raise SystemExit(f"Collision still VARIES for {varies} — it is not derivable, refusing to "
                         f"delete a column that carries real per-row data.")
    print(f"  verified: all {len(per_action)} actions have exactly one Collision — derivable")

    # the tab must already agree, or deleting Hero's column loses the truth
    am = read("action-model.csv")
    ah = am[0]
    tab = {}
    for r in am[1:]:
        if not any(x.strip() for x in r):
            break
        if r[0].strip():
            tab[r[0].strip()] = r[ah.index("Collision")].strip()
    mismatch = {n: (tab.get(n), next(iter(v - {""})))
                for n, v in per_action.items() if tab.get(n) != next(iter(v - {""}), "")}
    if mismatch:
        raise SystemExit(f"the tab disagrees with the data on {mismatch} — reconcile before deleting")
    print(f"  verified: the Action Model tab already carries the same Collision for all {len(tab)}")

    write("hero.csv", [r[:ci] + r[ci + 1:] for r in hero])
    print(f"hero.csv: {len(h) - 1} cols (was {len(h)}) — {COL} removed")

    # --- Effect Recipient vocabulary ------------------------------------------------------------
    ri = h.index("Effect Recipient")
    used = sorted({r[ri].strip() for r in hero[1:] if r[ri].strip()} - {D})
    write("effect-recipient-types.csv", [["Effect Recipient", "Meaning"]] + [[v, ""] for v in used])
    print(f"effect-recipient-types.csv: {len(used)} recipients in use")


if __name__ == "__main__":
    main()
