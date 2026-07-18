"""ONE-SHOT: add the 11 Set 9.5 champions, completing the roster (64 -> 75).

    python .claude/scripts/tft-set9-skill-modularity/add_set95.py

Run ONCE, then archive/. Appends to data/hero.csv and registers the new effects. Then:
sync.py -> fix_append.py -> sync.py to 0.

IDENTITY IS READ FROM THE SOURCE, never retyped: cost, role, origin, class, range and the skill text
all come from `tft-set9 -> Champions`, so a typo cannot creep in. Only the STEP MODEL below is mine.
Cost is normalised to 'N Gold' (the source writes '5' for Gangplank and '1 Gold' for Graves).

RANGE: the source still says 'N/A' for Fiora/Quinn/Xayah; the user gave 1 / 4 / 4.

DECISIONS TAKEN WITH THE USER THIS ROUND:
  - Nautilus knocks up + stuns. NO pull status ("Add 2 effect => knockup + stun. No pull status.").
  - New effects: Status/Knock Up, Buff/Untargetable, Buff/Range, Status/Soul Link, Buff/CC Immunity.
  - Gangplank's Dreadway = Summon + Charge (the ship carries the hitbox) + a Circle AOE crash.
  - 'ignite' is NOT a new effect: it is Attack/True Damage with a cadence, which already works.
  - The stat STEAL reuses Nasus's shape (Debuff on the target, Buff on self).

KNOCK UP FILLS A REAL HOLE: 'On Enemy Knocked Up' was already a trigger (Taliyah) and 'Knocked-up
enemy' an Aim Target, but nothing in the sheet could CAUSE a knock-up. Two columns referenced a thing
no effect could produce.

FLAGGED, NOT GUESSED (see the terminal summary):
  - Naafari's packmates: modelled as `Cast` from the Summon. `Auto-Attack (ranged)` would assert a
    projectile, and `Auto-Attack (melee)` was retired at 0 rows. They may want it revived.
  - Gangplank's crash aims at 'Current': the source says "the first enemy hit", and there is no aim
    for that. His Charge is Pierce-All (the tab's), but the ship stops at the first ENEMY while
    passing THROUGH allies — the model cannot say that yet.
  - Fiora's untargetable duration: the source gives none.
"""

import csv
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import gspread

from builder import build
from sheet import CRED, D

DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")
SOURCE = "1xj6em5XlvIN1gWHTKOPDsssmkgnS3jIsaLnAMjYyPUA"

RANGE_OVERRIDE = {"Fiora": "1", "Quinn": "4", "Xayah": "4"}   # source says N/A; the user's numbers

SUMMARY = {
    "Graves": "Smoke-Cloud Chiller", "Illaoi": "Soul-Link Tank",
    "Twisted Fate": "Delayed-Burst Mage", "Nautilus": "Knock-Up Anchor",
    "Gangplank": "Dreadway Admiral", "Naafari": "Packmate Duelist",
    "Milio": "Bouncing-Ball Support", "Mordekaiser": "Stat-Stealing Reaper",
    "Fiora": "Untargetable Duellist", "Quinn": "Marking Skirmisher",
    "Xayah": "Feather Volley",
}

NEW_EFFECTS = [
    ("Status", "Knock Up", "Recipient is thrown into the air, unable to act until it lands. The "
     "sheet already had 'On Enemy Knocked Up' as a TRIGGER and 'Knocked-up enemy' as an Aim Target "
     "- this is the effect that causes what those two referenced."),
    ("Status", "Soul Link", "Recipient is linked to the caster for the duration. While linked, a "
     "share of the damage the RECIPIENT takes is healed back to the caster (Illaoi)."),
    ("Buff", "Untargetable", "Recipient cannot be targeted or hit for the duration. Not the same as "
     "Damage Reduction: nothing can select them at all."),
    ("Buff", "Range", "Increase the recipient's attack range, in hexes."),
    ("Buff", "CC Immunity", "Recipient ignores crowd control (Stun, Chill, Disarm, Knock Up...) for "
     "the duration."),
]


def read(name):
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return [r for r in csv.reader(f)]


def write(name, rows):
    with (DATA / name).open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)


def source_rows():
    ch = gspread.service_account(filename=CRED).open_by_key(SOURCE).worksheet("Champions").get_all_values()
    h = ch[0]
    I = {n: h.index(n) for n in ("Champion Name", "Cost", "Design Role", "Origin 1", "Origin 2",
                                 "Class 1", "Class 2", "Range", "Skill Description")}
    out = {}
    for r in ch[1:]:
        if len(r) <= I["Skill Description"] or not r[I["Champion Name"]].strip():
            continue
        n = r[I["Champion Name"]].strip()
        cost = r[I["Cost"]].strip()
        if cost and "Gold" not in cost:
            cost = f"{cost} Gold"                    # the source is inconsistent; the sheet is not
        rng = RANGE_OVERRIDE.get(n, r[I["Range"]].strip())
        out[n] = [n, cost, r[I["Design Role"]].strip(), r[I["Origin 1"]].strip(),
                  r[I["Origin 2"]].strip(), r[I["Class 1"]].strip(), r[I["Class 2"]].strip(),
                  rng, SUMMARY.get(n, ""), (r[I["Skill Description"]] or "").strip()]
    return out


# effect tuple: (cond, recip, cat, det, amt, scalT, scaling, cadence, dur, aoe, offset)
# action tuple: (trigger, source, action, count, spread, aim, cast, effects)
def steps(name, S):
    R = S[name][7]                                   # this champion's Range
    if name == "Graves":
        return [
            ("1", "Active", [
                ("On Cast", "Self", "Homing Projectile", "1", D, "Current", D,
                 [(D, D, D, D, D, D, D, D, D, "1-hex", D)]),
            ]),
            ("2", "Active", [
                ("On Projectile Hit", "Step 1 Projectile", "Circle AOE", "1", D, "Current", D,
                 [(D, "Enemies in area", "Attack", "Damage", "200/200/205% AD + 30/45/60% AP",
                   D, D, "Once", D, "Circle 1 hex", "centred")]),
            ]),
            ("3", "Active", [
                # the cloud it leaves: a ZONE — walk out and the Chill stops
                ("After Step 2", "Step 1 Projectile", "Zone AOE", "1", D, "Step 1 Aim target", D,
                 [(D, "Enemies in area", "Status", "Chill", "30%", D, D, "Every 0.5s", "3/3.5/4",
                   "Circle 1 hex", "centred")]),
            ]),
        ]
    if name == "Illaoi":
        return [
            ("1", "Active", [
                ("On Cast", "Self", "Cast", D, D, "Current", D,
                 [(D, "Same to Aim Target", "Attack", "Damage", "250/375/560% AP", D, D, "Once", D, D, D),
                  (D, "Same to Aim Target", "Status", "Soul Link", D, D, D, "Once", "5", "", ""),
                  # Taric's shape: a share of damage the RECIPIENT takes, stated on the caster's row
                  (D, "Self", "Buff", "Heal", "25/30/40%", "Derived",
                   "of all damage the linked target takes", "Once", "5", "", "")]),
            ]),
        ]
    if name == "Twisted Fate":
        return [
            ("1", "Active", [
                ("On Cast", "Self", "Homing Projectile", "1", D, "Current", D,
                 [(D, "Same to Aim Target", "Attack", "Damage", "155/235/380% AP", D, D, "Once", D,
                   "1-hex", D)]),
            ]),
            # the 1.25s wait IS the action's cast time — the cards sit on the target, then go off
            ("2", "Active", [
                ("After Step 1", "Self", "Circle AOE", "1", D, "Step 1 Aim target", "1.25",
                 [(D, "Enemies in area", "Attack", "Damage", "185/275/435% AP", D, D, "Once", D,
                   "Circle 1 hex", "centred")]),
            ]),
        ]
    if name == "Nautilus":
        return [
            ("0", "Passive", [
                ("Game Start", "Self", "Cast", D, D, "Self", D,
                 [(D, "Same to Aim Target", "Buff", "Armor", "40%", "Derived",
                   "of Armor from all sources", "Once", "Permanent", D, D),
                  (D, "Same to Aim Target", "Buff", "MR", "40%", "Derived",
                   "of MR from all sources", "Once", "Permanent", "", "")]),
            ]),
            ("1", "Active", [
                ("On Cast", "Self", "Circle AOE", "1", D, "Self", D,
                 [(D, "Enemies in area", "Attack", "Damage", "150/225/360% AP", D, D, "Once", D,
                   "Circle 2 hex", "centred"),
                  (D, "Enemies in area", "Status", "Knock Up", D, D, D, "Once", D, "", ""),
                  (D, "Enemies in area", "Status", "Stun", D, D, D, "Once", "1.5/1.5/2", "", "")]),
            ]),
        ]
    if name == "Gangplank":
        return [
            ("0", "Passive", [
                ("Game Start", "Self", "Cast", D, D, "Self", D,
                 [(D, "Same to Aim Target", "Buff", "Armor", "50", D, D, "Once", "Permanent", D, D),
                  (D, "Same to Aim Target", "Buff", "MR", "50", D, D, "Once", "Permanent", "", ""),
                  (D, "Same to Aim Target", "Buff", "Range", "3", D, D, "Once", "Permanent", "", "")]),
            ]),
            ("0.1", "Passive", [
                ("On Attack", "Self", "Bonus on AA", "1", D, "Current", D,
                 [(D, "Same to Aim Target", "Attack", "True Damage", "250/250/2500% AP", D, D,
                   "Every 0.5s", "2", D, D),          # 'ignite' — not a new effect, just a cadence
                  (D, "Self", "Buff", "Mana", "5", D, D, "Once", D, "", "")]),
            ]),
            ("1", "Active", [
                ("On Cast", "Self", "Summon", D, D, "Self", D,
                 [(D, D, "Summon", "(summon)", D, D, D, "Once", D, D, D)]),
            ]),
            ("2", "Active", [
                # the ship carries the hitbox: whatever it sails through is affected
                ("After Step 1", "Dreadway", "Charge", "1", D, "Clustered", D,
                 [(D, "Allies in path", "Buff", "Attack Speed", "35/50/300%", D, D, "Once", "3",
                   "1-hex", "centred"),
                  (D, "Allies in path", "Buff", "CC Immunity", D, D, D, "Once", "3", "", "")]),
            ]),
            ("3", "Active", [
                ("After Step 2", "Dreadway", "Circle AOE", "1", D, "Current", D,
                 [(D, "Enemies in area", "Attack", "Damage", "450/675/9001% AP", D, D, "Once", D,
                   "Circle 3 hex", "centred"),
                  (D, "Allies in area", "Buff", "Attack Speed", "35/50/300%", D, D, "Once", "3", "", ""),
                  (D, "Allies in area", "Buff", "CC Immunity", D, D, D, "Once", "3", "", "")]),
            ]),
        ]
    if name == "Naafari":
        return [
            ("0", "Passive", [
                ("Game Start", "Self", "Cast", D, D, "Self", D,
                 [(D, "Same to Aim Target", "Buff", "Omnivamp", "15%", D, D, "Once", "Permanent", D, D)]),
            ]),
            ("1", "Active", [
                ("On Cast", "Self", "Cast", D, D, "Current", D,
                 [(D, "Same to Aim Target", "Attack", "Damage", "175/175/180% AD", D, D, "Once", D, D, D)]),
            ]),
            ("2", "Active", [
                ("After Step 1", "Self", "Summon", D, D, "Step 1 Aim target", D,
                 [(D, D, "Summon", "(summon)", D, D, D, "Once", D, D, D)]),
            ]),
            ("3", "Active", [
                # FLAGGED: 'Cast' avoids asserting a delivery. Auto-Attack (melee) is retired.
                ("After Step 2", "Summon", "Cast", D, D, "Step 1 Aim target", D,
                 [(D, "Same to Aim Target", "Attack", "Damage", "190/195/200% AD", D,
                   "total across all packmates", "Once", D, D, D)]),
            ]),
        ]
    if name == "Milio":
        return [
            ("1", "Active", [
                ("On Cast", "Self", "Homing Projectile", "1", D, "Current", D,
                 [(D, "Same to Aim Target", "Attack", "Damage", "220/330/500% AP", D, D, "Once", D,
                   "1-hex", D),
                  (D, "Same to Aim Target", "Status", "Stun", D, D, D, "Once", "1.5", "", "")]),
            ]),
            ("2", "Active", [
                ("On Projectile Hit", "Step 1 Projectile", "Homing Projectile", "1", D,
                 "Closest enemy behind Step 1 Aim target", D,
                 [(D, "Same to Aim Target", "Attack", "Damage", "180/270/400% AP", D, D, "Once", D,
                   "1-hex", D)]),
            ]),
            ("3", "Active", [
                ("On Projectile Hit", "Step 2 Projectile", "Circle AOE", "1", D,
                 "Step 2 Aim target", D,
                 [(D, "Enemies in area", "Attack", "Damage", "90/140/200% AP", D, D, "Once", D,
                   "Circle 1 hex", "centred")]),
            ]),
        ]
    if name == "Mordekaiser":
        return [
            ("0", "Passive", [
                ("On Attack", "Self", "Bonus on AA", "1", D, "Current", D,
                 [("If not Empowered", "Same to Aim Target", "Attack", "Damage", "100/150/375% AP",
                   D, D, "Once", D, D, D)]),
                ("On Attack", "Self", "Bonus on AA", "1", D, "Current", D,
                 [("If Empowered", "Same to Aim Target", "Attack", "Damage", "250/375/900% AP",
                   D, D, "Once", D, D, D)]),
            ]),
            ("1", "Active", [
                ("On Cast", "Self", "Cast", D, D, "Self", D,
                 [(D, "Same to Aim Target", "Buff", "Shield", "40% max HP", D, D, "Once", "5", D, D),
                  (D, "Same to Aim Target", "Buff", "Range", "1", D, D, "Once", "5", "", "")]),
            ]),
            ("2", "Active", [
                # Nasus's shape: the kill steals stats onto Self, for the rest of combat
                ("On Kill", "Self", "Cast", D, D, "Current", D,
                 [("If Empowered", "Self", "Buff", "Bonus HP", "6/6/15%", "Derived",
                   "of the killed enemy's stat", "Once", "Permanent", D, D),
                  ("", "Self", "Buff", "AD", "6/6/15%", "Derived",
                   "of the killed enemy's stat", "Once", "Permanent", "", ""),
                  ("", "Self", "Buff", "AP", "6/6/15%", "Derived",
                   "of the killed enemy's stat", "Once", "Permanent", "", ""),
                  ("", "Self", "Buff", "Armor", "6/6/15%", "Derived",
                   "of the killed enemy's stat", "Once", "Permanent", "", ""),
                  ("", "Self", "Buff", "MR", "6/6/15%", "Derived",
                   "of the killed enemy's stat", "Once", "Permanent", "", "")]),
            ]),
        ]
    if name == "Fiora":
        return [
            ("1", "Active", [
                ("On Cast", "Self", "Cast", D, D, "Self", D,
                 [(D, "Same to Aim Target", "Buff", "Untargetable", D, D, D, "Once", D, D, D)]),
            ]),
            ("2", "Active", [
                ("After Step 1", "Self", "QuickAA", "4", "Same target", "Lowest-HP enemy", D,
                 [(D, "Same to Aim Target", "Attack", "Damage", "160/160/240% AD", D, D, "Once", D,
                   "1-hex", D),
                  (D, "Same to Aim Target", "Attack", "True Damage", "60/90/270% AP", D, D, "Once", D, "", ""),
                  (D, "Self", "Buff", "Heal", "15%", "Derived", "of the total damage dealt",
                   "Once", D, "", "")]),
            ]),
        ]
    if name == "Quinn":
        return [
            ("1", "Active", [
                ("On Cast", "Self", "Pierce Projectile", "1", D,
                 "Row or column with most enemies", D,
                 [(D, "Enemies in path", "Status", "Mark", D, D, D, "Once", "4", "Box 1x2", D),
                  (D, "Enemies in path", "Debuff", "Damage Amplification", "10% AP", D, D, "Once",
                   "4", "", "")]),
            ]),
            ("2", "Active", [
                ("After Step 1", "Self", "Cast", "1", "Split across marked", "Step 1 Aim target", D,
                 [(D, "Marked enemies", "Attack", "Damage", "550/555/565% AD", D, D, "Once", D, D, D)]),
            ]),
        ]
    if name == "Xayah":
        return [
            ("0", "Passive", [
                ("On Attack", "Self", "Bonus on AA", "1", D, "Current", D,
                 [("If Ionia Active", "Self", "Buff", "Mana", "5", D, D, "Once", D, D, D)]),
            ]),
            ("1", "Active", [
                ("On Cast", "Self", "Pierce Projectile", "7/7/15", "Same target", "Current", D,
                 [(D, "Same to Aim Target", "Attack", "Damage", "80/80/100% AD + 15/25/60% AP",
                   D, D, "Once", D, "1-hex", D),
                  (D, "First hit enemy", "Debuff", "DEF", "6", "Per Stack",
                   "each feather removes 6", "Once", "Permanent", "", "")]),
            ]),
        ]
    raise SystemExit(f"no step model for {name}")


def main():
    S = source_rows()
    hero = read("hero.csv")
    H = hero[0]
    have = {r[0].strip() for r in hero[1:] if r[0].strip()}

    names = ["Graves", "Illaoi", "Twisted Fate", "Nautilus", "Gangplank", "Naafari", "Milio",
             "Mordekaiser", "Fiora", "Quinn", "Xayah"]
    # idempotent: drop any block we are about to re-add, so a re-run cannot duplicate a champion
    out, cur = [], ""
    for r in hero[1:]:
        if r[0].strip():
            cur = r[0].strip()
        if cur not in names:
            out.append(r)

    added = 0
    for n in names:
        assert n in S, f"{n} is not in the source sheet"
        assert S[n][7], f"{n} has no Range"
        rows = build(S[n], steps(n, S))
        assert all(len(r) == len(H) for r in rows), f"{n}: wrong column count"
        out += rows
        added += 1
        print(f"  {n:<13} {len(rows):>2} rows  | {S[n][1]:<7} {S[n][3]:<11} "
              f"{S[n][5] or '-':<12} R{S[n][7]}")
    write("hero.csv", [H] + out)
    print(f"hero.csv: +{added} champions, {len(out)} data rows "
          f"({len(have | set(names))} champions total)")

    # --- register the new effects ----------------------------------------------------------------
    et = read("effect-types.csv")
    doc_at = next((i for i, r in enumerate(et) if not any(x.strip() for x in r)), len(et))
    body, doc = et[1:doc_at], et[doc_at:]
    prev, seen = "", set()
    for r in body:
        if r[0].strip():
            prev = r[0].strip()
        seen.add((prev, r[1].strip() if len(r) > 1 else ""))
    for cat, det, mean in NEW_EFFECTS:
        if (cat, det) in seen:
            continue
        # insert at the END of that category's block, so the merge stays one block per category
        last = max(i for i, r in enumerate(body)
                   if (r[0].strip() or next((body[j][0].strip() for j in range(i, -1, -1)
                                             if body[j][0].strip()), "")) == cat)
        body.insert(last + 1, ["", det, mean])
        print(f"  + effect {cat}/{det}")
    write("effect-types.csv", [et[0]] + body + doc)

    # --- register the new recipient ---------------------------------------------------------------
    er = read("effect-recipient-types.csv")
    if not any(r and r[0].strip() == "Marked enemies" for r in er):
        er.append(["Marked enemies", "Every enemy carrying the Mark this skill applied."])
        write("effect-recipient-types.csv", er)
        print("  + recipient 'Marked enemies'")


if __name__ == "__main__":
    main()
