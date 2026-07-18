"""ONE-SHOT: put `Cast (s)` back in Hero, INSIDE the Action column group. Undoes my misread.

    python .claude/scripts/tft-set9-skill-modularity/migrate_cast_back.py

Run ONCE, then archive/. Rewrites data/hero.csv + data/action-model.csv; the sheet side is
migrate_cast_back_sheet.py.

WHAT I GOT WRONG. The user wrote "Move this one inside 'Action' tab too" and I moved Cast (s) into the
Action Model TAB. They meant the **Action column group in the Hero tab** — the region under the
'Action' super-header. Their correction: "This isn't what I meant. I mean to move 'Cast in side a
Action column inside Hero tab'. The cast is one the element in each action, but it was rarely specify
most of the time."

So Cast (s) is a HERO column, and the complaint was about POSITION: it sat at the far right, marooned
in the Effect group, when it describes the ACTION. It now sits between Collision and Effect Recipient,
which puts it inside the 'Action' super-header where it belongs.

Their earlier "Cast is determine by action, we just didn't assign it yet" stands and is not in
conflict: the cast time is a property of the action, and most are unassigned. It just does not follow
that it stops being a per-row column — Hero rows ARE action instances.

MERGED PER ACTION, joining the run columns. Every other column in that group merges by value-run, and
"one element in each action" is exactly what a per-action merge shows: one Cast cell per action rather
than '—' repeated down every effect row. So '—' on an action-start row, BLANK on continuations (blank
= "same as above", the sheet's rule).

That rule is self-correcting under merging: a row whose `Legacy action` is blank is either a
continuation OR an action-start that merged into an identical action above it — and in both cases
inheriting the Cast above is right, because it is the same action.

VALUES RESTORED PER-ROW, not action-wide. Moving to the tab had made the three assigned times
action-wide (Galio's 2s becoming every Cast's). Reverted: only Galio 2 / Garen 4 / Lux 3 carry one,
exactly as the last committed state had it, and every other action-start reads '—'.
"""

import csv
import pathlib

DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")
D = "—"
COL = "Cast (s)"

# (champion, step, effect recipient, category, detail) -> cast time. Recovered from the last committed
# hero.csv (git show HEAD), NOT retyped from memory: those three cells are the only ones in the sheet.
ASSIGNED = {
    ("Galio", "1", "Same to Aim Target", "Buff", "Heal"): "2",
    ("Garen", "1", "Enemies in area", "Attack", "Damage"): "4",
    ("Lux", "1", "Same to Aim Target", "Attack", "Damage"): "3",
}


def read(name):
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return [r for r in csv.reader(f)]


def write(name, rows):
    with (DATA / name).open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)


def main():
    hero = read("hero.csv")
    h = hero[0]
    assert COL not in h, f"{COL} is already a Hero column"
    at = h.index("Effect Recipient")            # i.e. straight after Collision, last of the Action group
    c = {n: h.index(n) for n in
         ("Champion", "Step", "Legacy action", "Effect Recipient", "Effect Category", "Effect Detail")}

    out, champ, hits = [h[:at] + [COL] + h[at:]], "", 0
    for r in hero[1:]:
        if r[c["Champion"]].strip():
            champ = r[c["Champion"]].strip()
        key = (champ, r[c["Step"]].strip(), r[c["Effect Recipient"]].strip(),
               r[c["Effect Category"]].strip(), r[c["Effect Detail"]].strip())
        if key in ASSIGNED:
            v = ASSIGNED[key]
            hits += 1
        elif r[c["Legacy action"]].strip():      # an action-start row states its cast time
            v = D
        else:                                    # continuation: blank inherits the action above
            v = ""
        out.append(r[:at] + [v] + r[at:])

    assert hits == len(ASSIGNED), f"matched {hits} of {len(ASSIGNED)} assigned cast times — the rows moved"
    write("hero.csv", out)
    print(f"hero.csv: {len(out[0])} cols (was {len(h)}) — {COL} restored at index {at}, "
          f"inside the Action group; {hits} assigned times back on their own rows")

    # The tab's copy goes: it was my misreading, and a second home for the value is a second thing to
    # keep in step.
    am = read("action-model.csv")
    ah = am[0]
    if COL in ah:
        i = ah.index(COL)
        write("action-model.csv", [r[:i] + r[i + 1:] for r in am])
        print(f"action-model.csv: {COL} column removed ({len(ah) - 1} cols)")
    else:
        print(f"action-model.csv: no {COL} column — nothing to remove")


if __name__ == "__main__":
    main()
