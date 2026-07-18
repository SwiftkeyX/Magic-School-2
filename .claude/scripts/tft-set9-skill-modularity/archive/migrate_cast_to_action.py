"""ONE-SHOT: Cast (s) is a property of the ACTION, so move it out of Hero into the Action Model tab.

    python .claude/scripts/tft-set9-skill-modularity/migrate_cast_to_action.py

Run ONCE, then archive/. Rewrites data/hero.csv (32 -> 31 cols) + data/action-model.csv. The sheet-side
column delete is migrate_cast_to_action_sheet.py; sync.py then fills the values.

THE USER: "Cast is determine by action, we just didn't assign it yet. Include it in action tab too."

That settles a reading I had backwards. I had counted 199 rows of '—' as "this action has NO cast
time" - a real value, per-champion - and concluded the column could not move, because Galio's Cast is
2s while 45 other Casts are '—'. But '—' there means NOT ASSIGNED YET. Under that reading the column
is exactly like the five axes: one value per action, and the sheet simply has not filled most of them
in. Nothing supports my reading over the user's - and it is their design.

CONSEQUENCE, stated because it is the one thing this cannot undo: the three assigned values become
ACTION-WIDE.
    Galio  Cast                  2s  -> every Cast (45 other rows) is now 2s
    Garen  Circle AOE            4s  -> every Circle AOE (21 other rows) is now 4s
    Lux    Current Target Laser  3s  -> he is that action's only user, so nothing changes
The alternative was to keep 3 champion-specific numbers and lose the model; the user chose the model.

TBD, not '—', for the 21 unassigned actions: '—' is the sheet's "not applicable" marker, and it would
assert that those actions are INSTANT - re-introducing the exact wrong reading this migration fixes.
An action with a genuinely instant cast can be set to '—' deliberately, later, by the user.
"""

import csv
import pathlib

DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")
D = "—"
TBD = "TBD"
COL = "Cast (s)"


def read(name):
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return [r for r in csv.reader(f)]


def write(name, rows):
    with (DATA / name).open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)


def main():
    hero = read("hero.csv")
    h = hero[0]
    ci, li = h.index(COL), h.index("Legacy action")

    # An action's cast time = the one ASSIGNED value among its rows ('—' = unassigned, so ignore it).
    # Cast (s) is a per-effect column (filled on every row), so read it against the action in force.
    assigned, cur = {}, ""
    for r in hero[1:]:
        if r[li].strip():
            cur = r[li].strip()
        v = r[ci].strip()
        if v and v != D:
            assigned.setdefault(cur, set()).add(v)

    clash = {a: v for a, v in assigned.items() if len(v) > 1}
    if clash:
        raise SystemExit(f"two different cast times for one action: {clash}. The user's model says "
                         f"an action HAS one cast time, so this needs deciding before the move.")
    assigned = {a: next(iter(v)) for a, v in assigned.items()}
    for a, v in sorted(assigned.items()):
        print(f"  assigned: {a:<24} {v}s")

    # hero.csv: drop the column. It is the LAST one, so nothing shifts under it.
    assert ci == len(h) - 1, f"{COL} is not the last column ({ci} of {len(h)})"
    write("hero.csv", [r[:ci] + r[ci + 1:] for r in hero])
    print(f"hero.csv: {len(h) - 1} cols (was {len(h)}) — {COL} removed")

    # action-model.csv: add the column, seeded from what the sheet already knew.
    am = read("action-model.csv")
    ah = am[0]
    at = ah.index("Collision") + 1                 # sits with the other per-action mechanics
    head = ah[:at] + [COL] + ah[at:]
    out, in_doc = [head], False
    for r in am[1:]:
        if not any(x.strip() for x in r):
            in_doc = True
        name = r[0].strip()
        val = "" if in_doc else assigned.get(name, TBD)
        out.append(r[:at] + [val] + r[at:])
    write("action-model.csv", out)
    n = sum(1 for r in out[1:] if r[at] == TBD)
    print(f"action-model.csv: +{COL} — {len(assigned)} assigned, {n} {TBD}")


if __name__ == "__main__":
    main()
