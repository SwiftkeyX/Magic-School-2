"""ONE-SHOT: group Effect Types by category, and build the Trigger Types vocabulary tab.

    python .claude/scripts/tft-set9-skill-modularity/migrate_group_and_triggers.py

Run ONCE, then archive/. Writes data/effect-types.csv + data/trigger-types.csv; sync.py pushes them
(it creates the new tab and derives the merge).

EFFECT TYPES — the user: "This is kinda messy. How about merge the cell in Effect category until it
left with only 4 row Buff, Debuff, Attack, Status." The tab was in ARRIVAL order, so 'Buff' appeared
19 times scattered down it and could not merge into anything. Sorting by category first is what makes
the merge possible; the merge then leaves ONE cell per category, which is what they asked for.

Kept all SIX categories, not four: Movement (12 Hero rows) and Summon (2) are real and in use, and
dropping them would have to relocate 14 rows. The user confirmed this reading.

Within a category the original order is PRESERVED (stable sort) - the arrival order is the only
record of when each effect was added, and re-alphabetising would destroy it for no gain.

TRIGGER TYPES — the user: "I don't want you to add some random trigger. So let's make its own tab, so
we know what trigger currently we have." The tab is the vocabulary; the enforcement is sync.py's
VALIDATE, which now fails on any Hero trigger with no row here. Without that check the tab is just a
list that drifts - the exact failure the Action Model tab had while it was hand-maintained.

Seeded from what the sheet ACTUALLY uses, never invented: every distinct non-blank Trigger in
hero.csv. Meanings are left blank for the user to fill where they want.
"""

import csv
import pathlib

DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")

# Display order. Mirrors the 'Column Explain' listing (Attack / Status / Buff / Debuff / Movement /
# Summon) so the tab and its legend read the same way round.
ORDER = ["Attack", "Status", "Buff", "Debuff", "Movement", "Summon"]


def read(name):
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return [r for r in csv.reader(f)]


def write(name, rows):
    with (DATA / name).open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)


def main():
    # --- Effect Types: sort by category, then blank the continuations so the merge can be derived --
    rows = read("effect-types.csv")
    head, body = rows[0], [r for r in rows[1:] if any(c.strip() for c in r)]
    assert len(body) == len(rows) - 1, "Effect Types has a doc block; the sort would reorder it"

    unknown = {r[0].strip() for r in body} - set(ORDER)
    if unknown:
        raise SystemExit(f"category with no place in ORDER: {sorted(unknown)}")

    body.sort(key=lambda r: ORDER.index(r[0].strip()))   # stable: arrival order kept within a block
    prev = None
    for r in body:
        cat = r[0].strip()
        if cat == prev:
            r[0] = ""                    # blank = "same as above"; the merge is derived from this
        prev = cat
    write("effect-types.csv", [head] + body)
    print(f"effect-types.csv: {len(body)} effects grouped into {len(ORDER)} merged blocks "
          f"({', '.join(ORDER)})")

    # --- Trigger Types: seeded from the triggers Hero actually uses -----------------------------
    hero = read("hero.csv")
    ti = hero[0].index("Trigger (When)")
    used = sorted({r[ti].strip() for r in hero[1:] if r[ti].strip()} - {"—"})
    write("trigger-types.csv",
          [["Trigger", "Meaning"]] + [[t, ""] for t in used])
    print(f"trigger-types.csv: {len(used)} triggers in use ->\n    " + "\n    ".join(used))


if __name__ == "__main__":
    main()
