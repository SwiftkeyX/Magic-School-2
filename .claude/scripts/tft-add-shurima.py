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

import gspread

KEY = "1X5glHjVcgv3yYG4Q2SyV9YJS3sv_wH5XAg3RLOHnUa4"
CRED = "google-service-credential.json"

D = "—"
SAME = "Same to Aim Target"

# Zed's rows still carry the Zed-specific names; the archetype is now shared with Azir.
RENAMES = {
    14: {"Summon Shadow": "Summon"},                          # Action
    16: {"Shadow": "Summon"},                                 # Aim Target
    17: {"Enemies adjacent to Shadow": "Enemies adjacent to Summon"},  # Effect Recipient
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
            ("1", "Passive", "On 3rd Attack", D, "Summon Attack", "Target-Only", "Current", [
                (SAME, "Attack", "Damage", "110/160/500% AP", D, "Once", D, D, D),
            ]),
            ("2", "Active", "On Cast", D, "Summon", "None", "Self", [
                (SAME, "Summon", "(summon)", D, "max 3 Soldiers", D, D, D, D),
            ]),
            ("3", "Active", "On Cast", "If Already 3 Soldiers",
             "Summon Attack", "Target-Only", "Current", [
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
        4: "Auto-Attack, Homing Projectile, Current Target Laser, Summon Attack",
    },
    "None": {
        4: "Cast (self OR melee strike), Leap, Summon",
    },
}

COLUMN_EXPLAIN_EDITS = {
    "Trigger (When)": {
        2: "e.g. On Cast, While Channeling, After Cast, After Leap, On Kill, On Death, Game Start, "
           "On Attack, On 3rd Attack, On 2nd Cast, On 3rd Cast, On Bonus-HP Expire, On Shield "
           "Expire, When Transformed, After Summon, After Whirlwind, After Slash, After Shielding "
           "Allies, On Enemy Knocked Up, After Knock Back.",
    },
    "Condition (Only if)": {
        2: "Lvl 1-5 / Lvl 6-8 / Lvl 9+, If Target Wounded, If Already Transformed, If Ally Hit, "
           "If Ionia Active, Every 2/2/0 casts, If Empowered, If Already 3 Soldiers, If Target at "
           "Edge, If Target Not at Edge. (Trigger = when; Condition = only-if.)",
    },
    "Aim Target": {
        2: "e.g. Current / Farthest (within N hex) / Clustered / Self / Summon / Lowest-HP Allies "
           "/ Adjacent (both sides) / Knocked-up enemy / Nearest N enemies / Step N Aim target "
           "(re-aims at whatever an earlier step aimed at — e.g. Yasuo's dash and slam both return "
           "to the enemy his Step 2 whirlwind picked).",
    },
    "Effect Recipient": {
        2: "Aimed enemy / First hit enemy / Enemies in area / Enemies in path / Allies in path / "
           "Self / Grabbed enemies / 2 lowest-HP allies / Enemies adjacent to Summon. If the "
           "recipient is exactly the Aim Target, write 'Same to Aim Target' rather than restating "
           "it — the cell then only ever carries NEW information.",
    },
}

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


def col_letter(i):
    s, i = "", i + 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def find_row(vals, col, value):
    for i, r in enumerate(vals):
        if len(r) > col and r[col].strip() == value:
            return i
    return None


def rename_zed_rows(ws, vals):
    edits = []
    for col, mapping in RENAMES.items():
        for i, r in enumerate(vals):
            if len(r) > col and r[col] in mapping:
                edits.append({"range": f"{col_letter(col)}{i + 1}",
                              "values": [[mapping[r[col]]]]})
    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Hero: retargeted {len(edits)} cells onto the generalised Summon names")


def append_champions(sh, ws):
    vals = ws.get_all_values()
    already = {r[0].strip() for r in vals if r and r[0].strip()}
    todo = [c for c in CHAMPIONS if c[0][0] not in already]
    if not todo:
        print("Hero: Shurima champions already present")
        return

    start = len(vals) + 1
    rows, merges, blocks = [], [], []
    r = start
    for ident, actions in todo:
        block_start = r
        first = True
        for step, stype, trig, cond, act, coll, aim, effects in actions:
            group = r
            for e in effects:
                head = ident if first else [""] * 10
                mid = [step, stype, trig, cond, act, coll, aim] if r == group else [""] * 7
                rows.append(head + mid + list(e))
                first = False
                r += 1
            if len(effects) > 1:  # one action, many effects -> merge K..Q down the group
                merges += [(group, r, c) for c in range(10, 17)]
        if r - block_start > 1:  # merge the identity block A..J down the champion
            merges += [(block_start, r, c) for c in range(10)]
        blocks.append((ident[0], block_start, r - 1))

    end = start + len(rows) - 1
    pre = []
    if end > ws.row_count:
        pre.append({"appendDimension": {"sheetId": ws.id, "dimension": "ROWS",
                                        "length": end - ws.row_count + 2}})
    pre.append({"copyPaste": {
        "source": {"sheetId": ws.id, "startRowIndex": 1, "endRowIndex": 2,
                   "startColumnIndex": 0, "endColumnIndex": 26},
        "destination": {"sheetId": ws.id, "startRowIndex": start - 1, "endRowIndex": end,
                        "startColumnIndex": 0, "endColumnIndex": 26},
        "pasteType": "PASTE_FORMAT",
    }})
    sh.batch_update({"requests": pre})

    ws.update(rows, f"A{start}:Z{end}", value_input_option="RAW")
    sh.batch_update({"requests": [{"mergeCells": {
        "range": {"sheetId": ws.id, "startRowIndex": a - 1, "endRowIndex": b - 1,
                  "startColumnIndex": c, "endColumnIndex": c + 1},
        "mergeType": "MERGE_COLUMNS",
    }} for a, b, c in merges]})
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
    gc = gspread.service_account(filename=CRED)
    sh = gc.open_by_key(KEY)
    ws = sh.worksheet("Hero")
    rename_zed_rows(ws, ws.get_all_values())
    append_champions(sh, ws)
    fix_reference_tabs(sh)
    print("\nAction Types is owned by tft-apply-comments.py — run it to land the Summon rename "
          "and the Summon Attack / Knock Back rows.")


if __name__ == "__main__":
    main()
