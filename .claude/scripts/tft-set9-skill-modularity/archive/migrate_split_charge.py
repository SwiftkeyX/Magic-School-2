"""ONE-SHOT: split the two actions that were secretly doing two jobs (the user's Sion analysis).

    python .claude/scripts/tft-set9-skill-modularity/migrate_split_charge.py

Run ONCE, then archive/. Rewrites data/hero.csv + data/action-model.csv. INSERTS ROWS, so sync will
rewrite everything below the insert point (invariant #9) — that is correct but heavy, and force_full.py
is the escape hatch if sync and remerge fight.

THE USER'S POINT (on Sion): "It should be 2 action combine: 1) Charge: this one apply hitbox on the
user, if the user move into them, they're hit. BUT doesn't specify that using this make him move.
2) Move: this one make Sion move toward target hex."

Exactly right, and 'Charge Into' hid the move inside a name. Split:

  Charge   a hitbox carried ON a unit; whatever that unit moves into is hit. It does NOT move
           anything by itself — Motion is '—'. The unit's own movement carries it.
  Move     the reposition, as its own action.

K'SANTE IS THE SAME SHAPE, which is why his was the last Collision disagreement in the sheet: the tab
said None (he is DirectApply — HE projects no hitbox) and the data said Pierce-All. Both were right
about different things, and that is the tell. The FLYING ENEMY is the hitbox, not K'Sante. So his four
effect rows are really two actions:

  Knock Back (DirectApply, None)  smashes the target        -> the target is Damaged + Stunned
  Charge     (Pierce-All)         source = the flying body  -> Enemies in path are Damaged + Stunned

'Charge' now has TWO users with different carriers — Sion himself, and K'Sante's victim — which is
what makes it a real action rather than a name for one champion's ability. The thrown body joins
'Step 1 Projectile' and 'Child of the Star' as a non-champion Action Source.

Its Aim Target is '—', an existing legal value, NOT a new one: the flying body does not aim at
anybody. It goes where it was smashed, and whoever is in the way is hit. Inventing a 'Board edge' aim
would add vocabulary to say "no aim", which is what '—' already says.
"""

import csv
import pathlib

DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")
D = "—"

C = {}          # column name -> index, filled in main()


def read(name):
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return [r for r in csv.reader(f)]


def write(name, rows):
    with (DATA / name).open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)


def find(hero, champ, action, detail=None):
    """Row index of `champ`'s row carrying `action` (and optionally that Effect Detail)."""
    cur, hits = "", []
    for n, r in enumerate(hero):
        if n == 0:
            continue
        if r[C["Champion"]].strip():
            cur = r[C["Champion"]].strip()
        if cur == champ and r[C["Legacy action"]].strip() == action:
            hits.append(n)
    if detail is not None:
        hits = [n for n in hits if hero[n][C["Effect Detail"]].strip() == detail]
    if len(hits) != 1:
        raise SystemExit(f"expected exactly 1 row for {champ}/{action}/{detail}, found {hits}")
    return hits[0]


def main():
    hero = read("hero.csv")
    C.update({n: i for i, n in enumerate(hero[0])})
    n_before = len(hero)

    # --- SION: Charge Into -> Charge, + a Move row for the reposition it was hiding -------------
    s = find(hero, "Sion", "Charge Into")
    hero[s][C["Legacy action"]] = "Charge"

    # A second action in the SAME step: fill only what CHANGES, and let every other cell inherit the
    # row above (blank = "same as above"). That is how K'Sante's existing Move row is written.
    move = [""] * len(hero[0])
    move[C["Legacy action"]] = "Move"
    move[C["Collision (If it have one)"]] = "None"        # differs: the Charge above is Pierce-All
    move[C["Effect Recipient"]] = "Self"
    move[C["Effect Category"]] = "Movement"
    move[C["Effect Detail"]] = "(reposition)"
    for n in ("Amount", "Scaling Type", "Scaling", "Effect Cadence", "Effect Duration (s)", "Cast (s)"):
        move[C[n]] = D
    # After Sion's LAST Charge effect row (the Stun continuation), before his next step.
    end = s + 1
    while end < len(hero) and not hero[end][C["Legacy action"]].strip() \
            and not hero[end][C["Step"]].strip():
        end += 1
    hero.insert(end, move)
    print(f"  Sion      Charge Into -> Charge, + Move row inserted at {end}")

    # --- K'SANTE: the flying body is a second source, not K'Sante's own hitbox -------------------
    k = find(hero, "K'Sante", "Knock Back")
    hero[k][C["Collision (If it have one)"]] = "None"     # HE projects nothing; the tab was right

    # His 'Enemies in path' rows belong to the thrown body. Promote the first to an action-start.
    # BOUND THE SCAN TO THIS ACTION'S OWN ROWS — an unbounded search runs off the end of K'Sante and
    # collects every other champion's 'Enemies in path' row (Viego's, Ashe's...). The action ends at
    # the next row that starts a step or names an action.
    k_end = k + 1
    while k_end < len(hero) and not hero[k_end][C["Step"]].strip() \
            and not hero[k_end][C["Legacy action"]].strip():
        k_end += 1
    path = [n for n in range(k + 1, k_end)
            if hero[n][C["Effect Recipient"]].strip() == "Enemies in path"]
    if len(path) != 2:
        raise SystemExit(f"expected 2 'Enemies in path' rows under K'Sante's Knock Back "
                         f"(rows {k + 1}..{k_end - 1}), got {path}")
    p = path[0]
    hero[p][C["Action Source"]] = "Knocked-back enemy"
    hero[p][C["Legacy action"]] = "Charge"
    hero[p][C["Aim Target"]] = D                          # it does not aim; it goes where it was hit
    hero[p][C["Collision (If it have one)"]] = "Pierce-All"
    print(f"  K'Sante   Knock Back -> None + Charge (source = the thrown body) at row {p}")

    assert len(hero) == n_before + 1, "exactly one row should have been inserted"
    write("hero.csv", hero)
    print(f"hero.csv: {len(hero) - 1} data rows (was {n_before - 1})")

    # --- the tab -------------------------------------------------------------------------------
    am = read("action-model.csv")
    ah = am[0]
    a = {n: ah.index(n) for n in ah}
    for r in am[1:]:
        if not any(x.strip() for x in r):
            break
        if r[0].strip() == "Charge Into":
            r[0] = "Charge"
            r[a["Motion"]] = D          # the hitbox does not move ITSELF - its carrier does
            r[a["What it does"]] = ("A hitbox carried ON a unit: whatever that unit moves into is hit.")
            r[a["Clarify more"]] = (
                "It does NOT move anything - pair it with a 'Move' action for that. Splitting the two "
                "was the user's call, and it is why 'Charge Into' is gone: that name hid a "
                "reposition inside it. The CARRIER is whoever Action Source names, and it need not be "
                "the caster: Sion carries it himself, while K'Sante's is carried by the ENEMY he "
                "smashed (Source = 'Knocked-back enemy'), whose body hits everyone it flies through. "
                "Not an AOE - the units hit are exactly the ones the carrier passed through.")
        if r[0].strip() == "Knock Back":
            r[a["Clarify more"]] = (
                "K'Sante's. HE projects no hitbox, so his Collision is None - the smash lands on the "
                "aimed enemy only. The FLYING BODY is a separate action ('Charge', Source = "
                "'Knocked-back enemy'), which is what hits everyone on the way. Those were one row "
                "until the user pointed out the same problem on Sion; while they were lumped, this "
                "tab said None and the Hero row said Pierce-All, and both were right about a "
                "different half of it.")
    write("action-model.csv", am)
    print("action-model.csv: Charge Into -> Charge (Motion '—'), Knock Back prose updated")


if __name__ == "__main__":
    main()
