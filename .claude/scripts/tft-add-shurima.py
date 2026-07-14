"""Add the Shurima champions to the `tft-set9-skill` sheet.

Run from repo-root cwd:  python .claude/scripts/tft-add-shurima.py

Appends 6 champions (Renekton, Taliyah, Akshan, Azir, Nasus, K'Sante) to the `Hero` tab.
Shurima's 9.0 roster is 7, but Cassiopeia is already in the tab as Noxus + Shurima and needs
no change.

Unlike Ionia, Shurima has NO per-unit bonus - its trait is a blanket heal-and-Ascend, so it
stays trait data in tft-set9 -> Origins and produces no extra rows here.

Also generalises `Summon Shadow` -> `Summon` (Zed's Shadow and Azir's Sand Soldier are the same
archetype) and retargets Zed's existing rows onto the new names.

Source of every number: tft-set9 -> Champions -> Skill Description.
"""

from tft_sheet import (D, SAME, ACTION_BLOCK, IDENTITY_BLOCK, col_letter, cols, find_row,
                       merge_request, open_sheet)

# Zed's rows still carry the Zed-specific names; the archetype is now shared with Azir.
RENAMES = {
    "Action": {"Summon Shadow": "Summon"},
    "Aim Target": {"Shadow": "Summon"},
    "Effect Recipient": {"Enemies adjacent to Shadow": "Enemies adjacent to Summon"},
}

# (champion, step) -> {column name: value}. Corrections to rows this script already wrote.
HERO_EDITS = {
    # Taliyah's active fires nothing: the hitbox appears on her target's hex. Not a projectile.
    # (Her passive boulder IS thrown, so it stays a First hit Projectile.)
    ("Taliyah", "2"): {"Action": "Spawn At Target"},
}

# identity (A-J) + actions
# action = (step, skill_type, trigger, condition, action, collision, aim, [effect, ...])
# effect = (recipient, category, detail, amount, scaling, cadence, duration, aoe, cast)
CHAMPIONS = [
    (
        ["Renekton", "1 Gold", "Tank", "Shurima", "", "Bruiser", "", "Frontliner",
         "Healing AOE Bruiser",
         "Deal magic damage to adjacent enemies. Heal for the first enemy hit, and a further 30% "
         "Ability Power for every additional enemy caught in the same swing."],
        [
            ("1", "Active", "On Cast", D, "Circle AOE", "Area", "Self", [
                ("Enemies in area", "Attack", "Damage", "180/270/400% AP", D, "Once", D, "1", D),
                (SAME, "Buff", "Heal", "220/270/320% AP",
                 "+30% AP per additional enemy hit", "Once", D, "1", D),
            ]),
        ],
    ),
    (
        ["Taliyah", "2 Gold", "Carry", "Shurima", "", "Multicaster", "", "Backliner",
         "Knock-up Punisher Mage",
         "Passive: whenever ANY enemy is knocked up or back - by anything, not just her - throw a "
         "boulder towards them; it damages the first enemy it hits. Active: damage the current "
         "target and knock them up, Stunning them for 2s."],
        [
            ("1", "Passive", "On Enemy Knocked Up", D,
             "First hit Projectile", "First-Hit", "Knocked-up enemy", [
                 ("First hit enemy", "Attack", "Damage", "120/180/270% AP", D, "Once", D, D, D),
             ]),
            ("2", "Active", "On Cast", D, "Homing Projectile", "Target-Only", "Current", [
                (SAME, "Attack", "Damage", "220/330/495% AP", D, "Once", D, D, D),
                (SAME, "Status", "Stun", D, D, "Once", "2", D, D),
            ]),
        ],
    ),
    (
        ["Akshan", "3 Gold", "Carry", "Shurima", "", "Deadeye", "", "Backliner",
         "Multi-shot Deadeye",
         "Lock on to the farthest enemy and unleash a hail of 6 shots toward them. Each shot damages "
         "the first enemy it hits - which need not be the enemy locked on to."],
        [
            ("1", "Active", "On Cast", D, "First hit Projectile", "First-Hit", "Farthest", [
                ("First hit enemy", "Attack", "Damage", "125% AD + 20/35/60% AP",
                 "×6 shots (each hits the first enemy in its path)", "Once", D, D, D),
            ]),
        ],
    ),
    (
        ["Azir", "4 Gold", "Carry", "Shurima", "", "Strategist", "", "Backliner",
         "Sand Soldier Summoner",
         "Passive: every third attack, a Sand Soldier damages Azir's target. Active: summon a Sand "
         "Soldier to attack the current target; if Azir already has 3 Soldiers, they all strike at "
         "once instead."],
        [
            ("1", "Passive", "On 3rd Attack", D, "Auto-Attack", "Target-Only", "Current", [
                (SAME, "Attack", "Damage", "110/160/500% AP", D, "Once", D, D, D),
            ]),
            ("2", "Active", "On Cast", D, "Summon", "None", "Self", [
                (SAME, "Summon", "(summon)", D, "max 3 Soldiers", D, D, D, D),
            ]),
            ("3", "Active", "On Cast", "If Already 3 Soldiers",
             "Auto-Attack", "Target-Only", "Current", [
                 (SAME, "Attack", "Damage", "70% AP",
                  "all 3 Soldiers strike at once", "Once", D, D, D),
             ]),
        ],
    ),
    (
        ["Nasus", "4 Gold", "Tank", "Shurima", "", "Juggernaut", "", "Frontliner",
         "Stat-Stealing Juggernaut",
         "Steal max Health, Attack Damage, Armor and Magic Resist from the nearest 4/5/7 enemies for "
         "8s - each stat is deducted from them and added to him. While empowered, every third attack "
         "deals heavy physical damage."],
        [
            # "Steal" is ONE action with eight effects: four debuffs on them, four buffs on him.
            ("1", "Active", "On Cast", D, "Cast", "None", "Nearest 4/5/7 enemies", [
                (SAME, "Debuff", "Max HP", "4/4/15%", D, "Once", "8", D, D),
                (SAME, "Debuff", "AD", "8%", D, "Once", "8", D, D),
                (SAME, "Debuff", "DEF", "4/4/20", D, "Once", "8", D, D),
                (SAME, "Debuff", "MR", "4/4/20", D, "Once", "8", D, D),
                ("Self", "Buff", "Bonus HP", "4/4/15%", "stolen from each enemy hit",
                 "Once", "8", D, D),
                ("Self", "Buff", "AD", "8%", "stolen from each enemy hit", "Once", "8", D, D),
                ("Self", "Buff", "Armor", "4/4/20", "stolen from each enemy hit", "Once", "8", D, D),
                ("Self", "Buff", "MR", "4/4/20", "stolen from each enemy hit", "Once", "8", D, D),
            ]),
            ("2", "Passive", "On 3rd Attack", "If Empowered",
             "Auto-Attack", "Target-Only", "Current", [
                 (SAME, "Attack", "Damage", "380/380/700% AD", D, "Once", D, D, D),
             ]),
        ],
    ),
    (
        ["K'Sante", "5 Gold", "Tank", "Shurima", "", "Bastion", "", "Frontliner",
         "Knockback Slam Tank",
         "Heal, then knock up the current target and smash them to the edge of the battlefield, "
         "damaging and Stunning them. Enemies the flying target collides with are also damaged and "
         "Stunned. If the target cannot be pushed further it is knocked off the battlefield; "
         "otherwise K'Sante chases it."],
        [
            ("1", "Active", "On Cast", D, "Cast", "None", "Self", [
                (SAME, "Buff", "Heal", "10% max HP", D, "Once", D, D, D),
            ]),
            # The thrown body is the hitbox - hence Pierce-All, and "Enemies in path" are whoever
            # the flying target ploughs through.
            ("2", "Active", "After Cast", D, "Knock Back", "Pierce-All", "Current", [
                (SAME, "Attack", "Damage", "250/400/1000% AP", D, "Once", D, D, D),
                (SAME, "Status", "Stun", D, D, "Once", "2/2.5/10", D, D),
                ("Enemies in path", "Attack", "Damage", "250/400/1000% AP", D, "Once", D, D, D),
                ("Enemies in path", "Status", "Stun", D, D, "Once", "1/1.25/5", D, D),
            ]),
            ("3", "Active", "After Knock Back", "If Target at Edge",
             "Cast", "None", "Step 2 Aim target", [
                 (SAME, "Status", "Knock Off", D, D, "Once", D, D, D),
             ]),
            ("4", "Active", "After Knock Back", "If Target Not at Edge",
             "Leap", "None", "Step 2 Aim target", [
                 ("Self", "Movement", "(reposition)", D, "chases the knocked-back target",
                  D, D, D, D),
             ]),
        ],
    ),
]

EFFECT_TYPES = [
    ["Debuff", "Max HP", "Reduce the recipient's maximum Health."],
    ["Debuff", "AD", "Reduce the recipient's Attack Damage."],
    ["Status", "Knock Off",
     "Recipient is knocked clean off the battlefield - removed from combat entirely. An execute, "
     "not a Stun (K'Sante, when the target has no room left to be pushed)."],
]

COLLISION_EDITS = {
    "Pierce-All": {
        4: "Pierce Projectile, Standard Laser, Laser Shot, Charge Into, Knock Back",
        5: "Kayle's pierce projectile hits enemies in the path; Sona's hits enemies AND buffs "
           "allies in the same path (two rows, one action); Sion charges through the cluster and "
           "stuns everyone he collides with; Irelia's Laser Shot pierces everyone in front of her; "
           "K'Sante's Knock Back is the odd one - the hitbox is the ENEMY he threw, and 'enemies in "
           "path' are whoever that flying body ploughs through.",
    },
    "Target-Only": {
        4: "Auto-Attack, Homing Projectile, Current Target Laser, Spawn At Target",
        5: "Kayle's auto-attack; Poppy / Cassiopeia / Samira's homing projectiles; Lux's locked "
           "beam; Azir's Sand Soldier. Taliyah's active too - her hitbox spawns ON the target, so "
           "nothing crosses the gap and nothing in between can be touched.",
    },
    "None": {
        4: "Cast (self OR melee strike), Leap, Summon",
    },
}

# The Trigger / Condition / Aim Target / Effect Recipient value lists are owned by the LATEST
# origin pass - now tft-add-shadowisles-targon.py, which has the most complete set. Condition used
# to be written here; it moved out when that pass added 'If Lethal' and 'If Ally Below 50% HP'.
# Two scripts writing the same cell overwrite each other on every run - that bug has bitten twice.
COLUMN_EXPLAIN_EDITS = {}

COLUMN_EXPLAIN_NOTES = [
    ["Note - Action Source",
     "KNOWN GAP: the schema records what an action aims at, and who the effect lands on — but NOT "
     "who performs it.",
     "It never mattered until Azir. Zed's Shadow attacks around ITSELF, so the source was smuggled "
     "into Aim Target = Summon. Azir's Sand Soldier attacks AZIR's target — source and aim are "
     "different units, so that hack has nowhere to go, and his source rides in the Action name "
     "instead ('Summon Attack'). Two different routes for the same fact. A future schema pass "
     "should add a proper 'Action Source' column (Self / the summon) and put both on it."],
    ["Note - Shurima",
     "Shurima has NO per-unit bonus, unlike Ionia.",
     "Its trait is a blanket heal-and-Ascend for every Shuriman, so there is no per-champion text "
     "to encode and no Passive bonus row. The trait itself lives in tft-set9 -> Origins."],
]


def fix_hero_cells(ws, vals):
    c = cols(vals[0])
    edits = []
    for column, mapping in RENAMES.items():
        for i, r in enumerate(vals):
            if r[c[column]] in mapping:
                edits.append({"range": f"{col_letter(c[column])}{i + 1}",
                              "values": [[mapping[r[c[column]]]]]})

    champ = ""
    for i, r in enumerate(vals):
        if r[c["Champion"]].strip():
            champ = r[c["Champion"]].strip()
        for column, value in HERO_EDITS.get((champ, r[c["Step"]].strip()), {}).items():
            if r[c[column]] != value:
                edits.append({"range": f"{col_letter(c[column])}{i + 1}",
                              "values": [[value]]})

    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Hero: {len(edits)} cells corrected (Summon rename + per-row fixes)")


def append_champions(sh, ws):
    vals = ws.get_all_values()
    c = cols(vals[0])
    width = len(vals[0])
    already = {r[c["Champion"]].strip() for r in vals if r[c["Champion"]].strip()}
    todo = [x for x in CHAMPIONS if x[0][0] not in already]
    if not todo:
        print("Hero: Shurima champions already present")
        return

    effect_cols = ["Effect Recipient", "Effect Category", "Effect Detail", "Amount", "Scaling",
                   "Cadence", "Duration", "AOE", "Cast"]
    start = len(vals) + 1
    rows, merges, blocks = [], [], []
    r = start
    for ident, actions in todo:
        block_start = r
        first = True
        for step, stype, trig, cond, act, coll, aim, effects in actions:
            group = r
            for e in effects:
                row = [""] * width
                if first:
                    for k, v in enumerate(ident):
                        row[k] = v
                if r == group:
                    head = dict(zip(["Step", "Skill Type", "Trigger", "Condition", "Action",
                                     "Collision", "Aim Target"],
                                    [step, stype, trig, cond, act, coll, aim]))
                    # Action Source did not exist when this pass was written; Self is the default,
                    # and Azir's rows are corrected to Summon by tft-add-freljord-piltover.py.
                    if "Action Source" in c:
                        head["Action Source"] = "Self"
                    for name, v in head.items():
                        row[c[name]] = v
                for name, v in zip(effect_cols, e):
                    row[c[name]] = v
                rows.append(row)
                first = False
                r += 1
            if len(effects) > 1:  # one action, many effects -> merge the action block down it
                merges += [(group, r, c[n]) for n in ACTION_BLOCK if n in c]
        if r - block_start > 1:  # merge the identity block down the champion
            merges += [(block_start, r, c[n]) for n in IDENTITY_BLOCK]
        blocks.append((ident[0], block_start, r - 1))

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
    print(f"Effect Types: added {len(pending)} rows")

    ws = sh.worksheet("Collision Types")
    vals = ws.get_all_values()
    edits = []
    for name, cols in COLLISION_EDITS.items():
        i = find_row(vals, 0, name)
        if i is None:
            raise SystemExit(f"Collision Types: row '{name}' not found")
        for c, text in cols.items():
            if vals[i][c] != text:
                edits.append({"range": f"{col_letter(c)}{i + 1}", "values": [[text]]})
    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Collision Types: {len(edits)} cells updated")

    ws = sh.worksheet("Column Explain")
    vals = ws.get_all_values()
    edits = []
    for label, cols in COLUMN_EXPLAIN_EDITS.items():
        i = find_row(vals, 0, label)
        if i is None:
            raise SystemExit(f"Column Explain: row '{label}' not found")
        for c, text in cols.items():
            if vals[i][c] != text:
                edits.append({"range": f"{col_letter(c)}{i + 1}", "values": [[text]]})
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
    append_champions(sh, ws)
    fix_hero_cells(ws, ws.get_all_values())
    fix_reference_tabs(sh)
    print("\nAction Types is owned by tft-apply-comments.py — run it to land the Summon rename "
          "and the Knock Back row.")


if __name__ == "__main__":
    main()
