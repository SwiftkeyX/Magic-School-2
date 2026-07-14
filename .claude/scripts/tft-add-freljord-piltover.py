"""Add the `Action Source` column, then the Freljord + Piltover champions.

Run from repo-root cwd:  python .claude/scripts/tft-add-freljord-piltover.py

WHY THE SCHEMA CHANGES FIRST
----------------------------
Sejuani cannot be encoded without it. Her passive is "whenever an ALLY attacks a Chilled enemy,
THEY deal bonus true damage" - the ally performs the action. The schema recorded what an action
aims at and who the effect lands on, but never WHO PERFORMS IT. That was survivable twice by
smuggling the source elsewhere (Zed's shadow into Aim Target; Azir's soldier into the Action
name "Summon Attack"), but Sejuani's source is neither her nor her summon, so there is nowhere
left to hide it.

So: insert `Action Source` (Self / Summon / Ally) before `Action`, backfill `Self`, fix Zed and
Azir retroactively, and retire `Summon Attack` - which existed only to smuggle the source, and
is now just Source=Summon + Auto-Attack.

Roster: Freljord 3 (Ashe, Lissandra, Sejuani), Piltover 4 (Orianna, Vi, Ekko, Jayce).
Ekko is Zaun + Piltover and goes in under his Origin 2, as Cassiopeia did for Noxus + Shurima.
Neither trait has a per-unit bonus, so there are no bonus rows (unlike Ionia).

Source of every number: tft-set9 -> Champions -> Skill Description.
"""

from tft_sheet import (D, SAME, ACTION_BLOCK, IDENTITY_BLOCK, action_groups, champion_blocks,
                       col_letter, cols, merge_request, open_sheet)

SOURCE = "Action Source"

# (champion, step) -> {column name: value}. The whole point of the new column: these three rows
# had their action SOURCE smuggled into another column, and can now say it plainly.
RETRO = {
    # Zed's shadow slashes around ITSELF, so the AOE is centred on the summon's hex.
    # Aim Target is ABSOLUTE, never relative to the Action Source: writing "Self" here would mean
    # "self as seen by the summon", which is exactly the kind of implicit reading this schema
    # exists to stamp out. The two columns say different things - Source = who acts, Aim = where
    # it lands - and for Zed they happen to coincide.
    ("Zed", "4"): {SOURCE: "Summon", "Aim Target": "Summon",
                   "Effect Recipient": "Enemies in area"},
    # Azir's Sand Soldier auto-attacks AZIR's target - here Source and Aim genuinely differ.
    # "Summon Attack" was a fake action invented only to smuggle the source.
    ("Azir", "1"): {SOURCE: "Summon", "Action": "Auto-Attack"},
    ("Azir", "3"): {SOURCE: "Summon", "Action": "Auto-Attack"},
}

# (champion, Effect Category, Effect Detail) -> {column: value}. Keyed on the effect rather than
# the step, because these corrections land on continuation rows inside a multi-effect action.
EFFECT_FIXES = {
    # "Sunder" is just TFT's name for Debuff -> DEF, which the Effect Types row already says.
    ("Vi", "Debuff", "DEF"): {"Scaling": D},
    # "Empowered Attack" is defined in Effect Types; restating it in Scaling adds nothing.
    ("Orianna", "Buff", "Empowered Attack"): {"Scaling": D},
    # Her AOE is 2 hexes, not 1.
    ("Sejuani", "Attack", "Damage"): {"AOE": "2"},
    ("Sejuani", "Status", "Chill"): {"AOE": "2"},
}

# identity (A-J) + actions
# action = (step, skill_type, trigger, condition, SOURCE, action, collision, aim, [effect, ...])
# effect = (recipient, category, detail, amount, scaling, cadence, duration, aoe, cast)
CHAMPIONS = [
    (
        ["Ashe", "2 Gold", "Support", "Freljord", "", "Deadeye", "", "Backliner",
         "Cone Chill Archer",
         "Fire 8 arrows in a cone. Each arrow damages the first enemy it hits and Chills it "
         "(-30% Attack Speed) for 2s."],
        [
            ("1", "Active", "On Cast", D, "Self", "First hit Projectile", "First-Hit", "Current", [
                ("First hit enemy", "Attack", "Damage", "160/165/175% AD",
                 "×8 arrows in a cone", "Once", D, D, D),
                ("First hit enemy", "Status", "Chill", D,
                 "×8 arrows in a cone", "Once", "2", D, D),
            ]),
        ],
    ),
    (
        ["Lissandra", "3 Gold", "Support", "Freljord", "", "Invoker", "", "Backliner",
         "Stun & Amplify Mage",
         "Stun the current target, damage everything within 2 hexes of it, and leave those enemies "
         "taking 10% more damage for 4s."],
        [
            # One action, three effects - and the Stun lands only on the aimed enemy while the
            # damage and the amp land on everyone in the area. Two different recipients.
            ("1", "Active", "On Cast", D, "Self", "Circle AOE", "Area", "Current", [
                (SAME, "Status", "Stun", D, D, "Once", "2", "2", D),
                ("Enemies in area", "Attack", "Damage", "160/240/400% AP",
                 D, "Once", D, "2", D),
                ("Enemies in area", "Debuff", "Damage Amplification", "10%",
                 D, "Once", "4", "2", D),
            ]),
        ],
    ),
    (
        ["Sejuani", "4 Gold", "Tank", "Freljord", "", "Bruiser", "", "Frontliner",
         "Chill Enabler Tank",
         "Passive: whenever an ALLY attacks a Chilled enemy, that ally's attack deals bonus true "
         "damage. Active: shield self, then damage and Chill nearby enemies."],
        [
            # The action SOURCE is an ally, not Sejuani. This row is the reason the column exists.
            ("1", "Passive", "On Ally Attack Chilled Enemy", D,
             "Ally", "Auto-Attack", "Target-Only", "Current", [
                 (SAME, "Attack", "True Damage", "160/240/1200",
                  "increased by max Health", "Once", D, D, D),
             ]),
            ("2", "Active", "On Cast", D, "Self", "Cast", "None", "Self", [
                (SAME, "Buff", "Shield", "600/700/2000% AP", D, "Once", "4", D, D),
            ]),
            ("3", "Active", "After Cast", D, "Self", "Circle AOE", "Area", "Self", [
                ("Enemies in area", "Attack", "Damage", "160/240/1200% AP",
                 D, "Once", D, "1", D),
                ("Enemies in area", "Status", "Chill", D, D, "Once", "4", "1", D),
            ]),
        ],
    ),
    (
        ["Orianna", "1 Gold", "Support", "Piltover", "", "Sorcerer", "", "Backliner",
         "Shield & Empower Support",
         "Shield the lowest-Health ally for 4s, and empower Orianna's NEXT attack to deal bonus "
         "magic damage."],
        [
            ("1", "Active", "On Cast", D, "Self", "Cast", "None", "Lowest-HP Ally", [
                (SAME, "Buff", "Shield", "200/225/275% AP", D, "Once", "4", D, D),
            ]),
            ("2", "Active", "On Cast", D, "Self", "Cast", "None", "Self", [
                (SAME, "Buff", "Empowered Attack", "290/435/650% AP",
                 "bonus magic damage on her next attack", "Once", D, D, D),
            ]),
        ],
    ),
    (
        ["Vi", "2 Gold", "Tank", "Piltover", "", "Bruiser", "", "Frontliner",
         "Shield & Sunder Bruiser",
         "Shield self for 4s, then damage enemies within 1 hex of the current target and Sunder "
         "them (-20% Armor) for 4s."],
        [
            ("1", "Active", "On Cast", D, "Self", "Cast", "None", "Self", [
                (SAME, "Buff", "Shield", "350/400/450% AP", D, "Once", "4", D, D),
            ]),
            ("2", "Active", "After Cast", D, "Self", "Circle AOE", "Area", "Current", [
                ("Enemies in area", "Attack", "Damage", "300% AD", D, "Once", D, "1", D),
                ("Enemies in area", "Debuff", "DEF", "20%", "Sunder", "Once", "4", "1", D),
            ]),
        ],
    ),
    (
        ["Ekko", "3 Gold", "Carry", "Zaun", "Piltover", "Rogue", "", "Frontliner",
         "Retroactive-Heal Assassin",
         "Heal for 20% of the damage he took in the last 4s, then strike the current target for "
         "magic damage."],
        [
            ("1", "Active", "On Cast", D, "Self", "Cast", "None", "Self", [
                (SAME, "Buff", "Heal", "20% of damage taken in last 4s", D, "Once", D, D, D),
            ]),
            # A melee strike projects no hitbox, so it has no collision.
            ("2", "Active", "After Cast", D, "Self", "Cast", "None", "Current", [
                (SAME, "Attack", "Damage", "255/380/570% AP", D, "Once", D, D, D),
            ]),
        ],
    ),
    (
        ["Jayce", "3 Gold", "Support", "Piltover", "", "Gunner", "", "Backliner",
         "Flank-Buff Gunner",
         "Grant himself Attack Speed and his left and right neighbours Ability Power for 3s, then "
         "fire a blast that detonates on the first enemy hit, damaging everyone near the blast."],
        [
            ("1", "Active", "On Cast", D, "Self", "Cast", "None", "Self", [
                (SAME, "Buff", "Attack Speed", "30/40/50% AP", D, "Once", "3", D, D),
            ]),
            ("2", "Active", "On Cast", D, "Self", "Cast", "None", "Self", [
                ("Adjacent allies (left & right)", "Buff", "AP", "15%", D, "Once", "3", D, D),
            ]),
            ("3", "Active", "After Cast", D, "Self", "Burst Projectile", "Area", "Current", [
                ("Enemies in area", "Attack", "Damage", "275/275/295% AD", D, "Once", D, "1", D),
            ]),
        ],
    ),
]

EFFECT_TYPES = [
    ["Status", "Chill", "Reduce the recipient's Attack Speed by 30%."],
    ["Attack", "True Damage", "Damage that ignores both Armor and Magic Resist."],
    ["Debuff", "Damage Amplification",
     "Recipient takes more damage from ALL sources for the duration (Lissandra)."],
    ["Buff", "Empowered Attack",
     "The recipient's NEXT attack deals bonus damage - it is stored, not applied immediately "
     "(Orianna)."],
]

# Sunder is just the existing Debuff -> DEF under another name; note the alias rather than
# duplicating the row.
EFFECT_ALIASES = {
    ("Debuff", "DEF"):
        "Shred the recipient's Defense (armor). TFT calls this 'Sunder' (Vi) or 'Shred' when it "
        "is Magic Resist - see Debuff -> MR.",
}

COLUMN_EXPLAIN_EDITS = {
    "Action Source": {
        1: "WHO performs the action. Defaults to Self.",
        2: "Self = the champion itself (almost every row). Summon = a unit it spawned acts on its "
           "own (Zed's Shadow, Azir's Sand Soldier). Ally = another unit entirely performs it "
           "(Sejuani's passive rides on an ALLY's attack). This is separate from Aim Target (what "
           "the action points at) and Effect Recipient (who the effect lands on) - three different "
           "questions, three columns.",
    },
    # Trigger / Aim Target / Effect Recipient moved OUT of this script: the value lists are owned
    # by the LATEST origin pass, which is now tft-add-shadowisles-targon.py. It adds On Enemy Cast,
    # On Spear Removal, Farthest and 'Nearest enemy to the healed ally'. Leaving a copy here would
    # mean two scripts writing the same cell - the bug that has bitten twice.
    # was a known-gap warning; the gap is now closed, so the note describes the column instead
    "Note - Action Source": {
        1: "CLOSED (was a known gap): the schema now records who performs an action.",
        2: "Before the Action Source column, the source had to be smuggled: Zed's Shadow into Aim "
           "Target, Azir's Sand Soldier into a fake action called 'Summon Attack'. Sejuani broke "
           "both hacks - an ALLY performs her passive - so the column was added and both were "
           "fixed. 'Summon Attack' is retired: it is just Source=Summon + Auto-Attack.",
    },
}

COLUMN_EXPLAIN_NOTES = [
    ["Note - Delivery vs Shape",
     "The Action column fuses TWO independent things: delivery and shape.",
     "DELIVERY = where the hitbox spawns and whether it travels (projectile / laser / spawn at "
     "target). SHAPE = what the hitbox is (single target / pierces a line / an X-hex circle). "
     "Circle AOE aimed at Current has the SAME delivery as Spawn At Target - it spawns on the "
     "target and nothing travels - and differs only in shape. Likewise Burst Projectile = travel "
     "+ first-hit + circle. A future 'Action Template' pass should split these into their own "
     "columns; for now the Action name carries both."],
    ["Note - Freljord / Piltover",
     "Neither has a per-unit bonus, unlike Ionia.",
     "Freljord's trait is a blanket ice storm and Piltover's is the T-Hex board mechanic - no "
     "per-champion text to encode, so no bonus rows. NOTE a source discrepancy: tft-set9 -> "
     "Origins claims Piltover has 5 natural units, but the Champions tab lists only 4 (Camille is "
     "absent from the source sheet entirely). Champions is what we encode from."],
]


def ensure_action_source(sh, ws):
    """Insert the Action Source column, backfill Self, and close the merge hole it creates."""
    header = ws.get_all_values()[0]
    if any(h.strip() == SOURCE for h in header):
        print("Hero: Action Source column already present")
        return

    at = next(i for i, h in enumerate(header) if h.strip() == "Action")
    sh.batch_update({"requests": [{"insertDimension": {
        "range": {"sheetId": ws.id, "dimension": "COLUMNS",
                  "startIndex": at, "endIndex": at + 1},
        "inheritFromBefore": True,
    }}]})
    ws.update([[SOURCE]], f"{col_letter(at)}1", value_input_option="RAW")
    print(f"Hero: inserted '{SOURCE}' at column {col_letter(at)}")

    # Inserting mid-table shifts the old K-Q merges right, leaving the NEW column unmerged inside
    # every multi-row action. Re-merge it, or a continuation row reads as its own action.
    vals = ws.get_all_values()
    c = cols(vals[0])
    merges = [merge_request(ws.id, a, b, c[SOURCE])
              for a, b in action_groups(vals, c) if b - a > 1]
    if merges:
        sh.batch_update({"requests": merges})
    print(f"Hero: re-merged the new column across {len(merges)} multi-row actions")


def fix_hero(sh, ws):
    vals = ws.get_all_values()
    c = cols(vals[0])
    edits = []

    # Self is the default and must never be blank - a blank would read as "unknown", not "the
    # caster". Only action rows get one; continuation rows inherit via the merge.
    for a, _ in action_groups(vals, c):
        if not vals[a][c[SOURCE]].strip():
            edits.append({"range": f"{col_letter(c[SOURCE])}{a + 1}", "values": [["Self"]]})

    for name, start, end in champion_blocks(vals, c):
        for i in range(start, end):
            step = vals[i][c["Step"]].strip()
            key = (name, vals[i][c["Effect Category"]], vals[i][c["Effect Detail"]])
            for column, value in {**RETRO.get((name, step), {}),
                                  **EFFECT_FIXES.get(key, {})}.items():
                if vals[i][c[column]] != value:
                    edits.append({"range": f"{col_letter(c[column])}{i + 1}",
                                  "values": [[value]]})

    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Hero: {len(edits)} cells set (Self backfill + Zed/Azir source fixes)")


def append_champions(sh, ws):
    vals = ws.get_all_values()
    c = cols(vals[0])
    width = len(vals[0])
    already = {r[c["Champion"]].strip() for r in vals if r[c["Champion"]].strip()}
    todo = [x for x in CHAMPIONS if x[0][0] not in already]
    if not todo:
        print("Hero: Freljord/Piltover champions already present")
        return

    start = len(vals) + 1
    rows, merges, blocks = [], [], []
    r = start
    for ident, actions in todo:
        block = r
        first = True
        for step, stype, trig, cond, source, act, coll, aim, effects in actions:
            group = r
            for e in effects:
                head = ident if first else [""] * 10
                mid = ([step, stype, trig, cond, source, act, coll, aim]
                       if r == group else [""] * 8)
                rows.append(head + mid + list(e))
                first = False
                r += 1
            if len(effects) > 1:
                merges += [(group, r, c[n]) for n in ACTION_BLOCK]
        if r - block > 1:
            merges += [(block, r, c[n]) for n in IDENTITY_BLOCK]
        blocks.append((ident[0], block, r - 1))

    assert all(len(x) == width for x in rows), "row width does not match the header"
    end = start + len(rows) - 1

    pre = []
    if end > ws.row_count:
        pre.append({"appendDimension": {"sheetId": ws.id, "dimension": "ROWS",
                                        "length": end - ws.row_count + 2}})
    pre.append({"copyPaste": {
        "source": {"sheetId": ws.id, "startRowIndex": 1, "endRowIndex": 2,
                   "startColumnIndex": 0, "endColumnIndex": width},
        "destination": {"sheetId": ws.id, "startRowIndex": start - 1, "endRowIndex": end,
                        "startColumnIndex": 0, "endColumnIndex": width},
        "pasteType": "PASTE_FORMAT",
    }})
    sh.batch_update({"requests": pre})

    ws.update(rows, f"A{start}:{col_letter(width - 1)}{end}", value_input_option="RAW")
    sh.batch_update({"requests": [merge_request(ws.id, a - 1, b - 1, col)
                                  for a, b, col in merges]})
    print(f"Hero: appended {len(rows)} rows ({start}-{end}), {len(merges)} merges")
    for name, a, b in blocks:
        print(f"   {name:10} rows {a}-{b}")


def fix_reference_tabs(sh):
    ws = sh.worksheet("Effect Types")
    vals = ws.get_all_values()
    seen = {(r[0], r[1]) for r in vals}
    pending = [e for e in EFFECT_TYPES if (e[0], e[1]) not in seen]
    if pending:
        ws.append_rows(pending, value_input_option="RAW")
        vals = ws.get_all_values()
    edits = [{"range": f"C{i + 1}", "values": [[text]]}
             for i, r in enumerate(vals)
             for key, text in EFFECT_ALIASES.items()
             if (r[0], r[1]) == key and r[2] != text]
    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Effect Types: added {len(pending)} rows, {len(edits)} definitions updated")

    ws = sh.worksheet("Column Explain")
    vals = ws.get_all_values()
    edits = []
    for label, columns in COLUMN_EXPLAIN_EDITS.items():
        i = next((k for k, r in enumerate(vals) if r[0].strip() == label), None)
        if i is None:
            # the Action Source row is new - it belongs right before the Action row
            anchor = next(k for k, r in enumerate(vals) if r[0].strip() == "Action")
            ws.insert_rows([[label, columns[1], columns[2]]], row=anchor + 1,
                           value_input_option="RAW")
            vals = ws.get_all_values()
            print(f"Column Explain: inserted the '{label}' row")
            continue
        for col, text in columns.items():
            if vals[i][col] != text:
                edits.append({"range": f"{col_letter(col)}{i + 1}", "values": [[text]]})
    if edits:
        ws.batch_update(edits, value_input_option="RAW")

    seen = {r[0].strip() for r in vals if r}
    notes = [n for n in COLUMN_EXPLAIN_NOTES if n[0] not in seen]
    if notes:
        ws.append_rows(notes, value_input_option="RAW")
    print(f"Column Explain: {len(edits)} cells updated, {len(notes)} note rows appended")


def main():
    sh = open_sheet()
    ws = sh.worksheet("Hero")
    ensure_action_source(sh, ws)
    append_champions(sh, ws)
    fix_hero(sh, ws)
    fix_reference_tabs(sh)
    print("\nAction Types is owned by tft-apply-comments.py — run it to retire 'Summon Attack'.")


if __name__ == "__main__":
    main()
