"""Add the Set 9.0 Ionia champions to the `tft-set9-skill` sheet.

Run from repo-root cwd:  python .claude/scripts/tft-add-ionia.py

Appends 8 champions (Irelia, Jhin, Sett, Zed, Karma, Shen, Yasuo, Ahri) to the `Hero`
tab in the one-row-per-effect schema, vertically merging cols K-Q across the rows of a
single action instance, and extends the reference tabs with the new Action / Collision /
Effect terms those champions introduce.

Xayah is excluded: she is 9.5-only, matching the existing precedent that Demacia's
9.5-only Fiora and Quinn are absent from the tab.

Source of every number: tft-set9 -> Champions -> Skill Description.
"""

import gspread

SKILL_KEY = "1X5glHjVcgv3yYG4Q2SyV9YJS3sv_wH5XAg3RLOHnUa4"

D = "—"  # em-dash: the sheet's "not applicable" marker
MINUS = "−"  # true minus sign, as used in Sona's "-33% per hit"

# Each champion: (identity A-J, [action, ...])
# action = (step, skill_type, trigger, condition, action, collision, aim, [effect, ...])
# effect = (recipient, category, detail, amount, scaling, cadence, duration, aoe, cast)
CHAMPIONS = [
    (
        ["Irelia", "1 Gold", "Tank", "Ionia", "", "Bastion", "", "Frontliner",
         "Decaying Shield Tank",
         "Ionia Bonus: +25 Armor and Magic Resist. Active: enter a defensive stance and gain a "
         "Shield that rapidly decays over 3s. When it expires, deal circular AOE magic damage "
         "plus 30% of the damage absorbed to enemies around and in front of her."],
        [
            ("1", "Passive", "Game Start", "If Ionia Active", "Cast", "None", "Self", [
                ("Self", "Buff", "Armor", "25", D, "Perm", D, D, D),
                ("Self", "Buff", "MR", "25", D, "Perm", D, D, D),
            ]),
            ("2", "Active", "On Cast", D, "Cast", "None", "Self", [
                ("Self", "Buff", "Shield", "350/400/450% AP", "decaying", "Once", "3", D, D),
            ]),
            ("3", "Active", "On Shield Expire", D, "Circle AOE", "Area", "Self", [
                ("Enemies in area", "Attack", "Damage", "70/100/150% AP",
                 "+30% of damage absorbed", "Once", D, "1", D),
            ]),
        ],
    ),
    (
        ["Jhin", "1 Gold", "Carry", "Ionia", "", "Deadeye", "", "Backliner",
         "Falloff Line Carry",
         "Ionia Bonus: +25% Attack Damage. Active: take aim at the current target and fire a shot "
         "through enemies in a line; each enemy hit reduces the damage by 56%."],
        [
            ("1", "Passive", "Game Start", "If Ionia Active", "Cast", "None", "Self", [
                ("Self", "Buff", "AD", "25%", D, "Perm", D, D, D),
            ]),
            ("2", "Active", "On Cast", D, "Laser Shot", "Pierce-All", "Current", [
                ("Enemies in path", "Attack", "Damage", "744% AD & AP",
                 f"{MINUS}56% per hit", "Once", D, D, D),
            ]),
        ],
    ),
    (
        ["Sett", "2 Gold", "Tank", "Ionia", "", "Juggernaut", "", "Frontliner",
         "Grab-and-Slam Stun Tank",
         "Ionia Bonus: +180 max Health. Active: grab an enemy from either side and slam them "
         "together, dealing magic damage and Stunning them. If only one enemy is grabbed, the "
         "damage and Stun duration are increased by 50%."],
        [
            ("1", "Passive", "Game Start", "If Ionia Active", "Cast", "None", "Self", [
                ("Self", "Buff", "Bonus HP", "180", D, "Perm", D, D, D),
            ]),
            ("2", "Active", "On Cast", D, "Grab & Slam", "Flank-Pair", "Adjacent (both sides)", [
                ("Grabbed enemies", "Attack", "Damage", "180/270/420% AP",
                 "+50% if only 1 grabbed", "Once", D, D, D),
                ("Grabbed enemies", "Status", "Stun", D,
                 "+50% if only 1 grabbed", "Once", "1.25/1.5/2", D, D),
            ]),
        ],
    ),
    (
        ["Zed", "2 Gold", "Carry", "Ionia", "", "Rogue", "Slayer", "Frontliner",
         "Shadow Twin Assassin",
         "Ionia Bonus: +15% Critical Strike Chance and Critical Strike Damage. Active: create a "
         "shadow at the furthest enemy within 2 hexes; Zed and his shadow each slash adjacent "
         "enemies for physical damage."],
        [
            ("1", "Passive", "Game Start", "If Ionia Active", "Cast", "None", "Self", [
                ("Self", "Buff", "Crit Chance", "15%", D, "Perm", D, D, D),
                ("Self", "Buff", "Crit Damage", "15%", D, "Perm", D, D, D),
            ]),
            ("2", "Active", "On Cast", D, "Summon Shadow", "None", "Farthest (within 2 hex)", [
                ("Self", "Movement", "(summon)", D, D, D, D, D, D),
            ]),
            ("3", "Active", "After Summon", D, "Circle AOE", "Area", "Self", [
                ("Enemies in area", "Attack", "Damage", "140/140/150% AD + 25/40/50% AP",
                 D, "Once", D, "1", D),
            ]),
            ("4", "Active", "After Summon", D, "Circle AOE", "Area", "Shadow", [
                ("Enemies adjacent to Shadow", "Attack", "Damage",
                 "140/140/150% AD + 25/40/50% AP", D, "Once", D, "1", D),
            ]),
        ],
    ),
    (
        ["Karma", "3 Gold", "Carry", "Ionia", "", "Invoker", "", "Backliner",
         "Burst Spell Spammer",
         "Ionia Bonus: +25 Ability Power. Active: fire a burst of energy that explodes on impact, "
         "dealing magic damage to enemies adjacent to the target. Every third cast launches "
         "3 bursts."],
        [
            ("1", "Passive", "Game Start", "If Ionia Active", "Cast", "None", "Self", [
                ("Self", "Buff", "AP", "25", D, "Perm", D, D, D),
            ]),
            ("2", "Active", "On Cast", D, "Burst Projectile", "Area", "Current", [
                ("Enemies in area", "Attack", "Damage", "200/300/470% AP", D, "Once", D, "1", D),
            ]),
            ("3", "Active", "On 3rd Cast", D, "Burst Projectile", "Area", "Current", [
                ("Enemies in area", "Attack", "Damage", "200/300/470% AP",
                 "×3 bursts", "Once", D, "1", D),
            ]),
        ],
    ),
    (
        ["Shen", "4 Gold", "Tank", "Ionia", "", "Bastion", "Invoker", "Frontliner",
         "Ally-Shielding Burst Tank",
         "Ionia Bonus: +8% Damage Reduction. Active: shield self and the 2 lowest-Health allies "
         "for 4s. After shielding his allies, Shen's Shield refreshes with a burst, dealing magic "
         "damage to adjacent enemies."],
        [
            ("1", "Passive", "Game Start", "If Ionia Active", "Cast", "None", "Self", [
                ("Self", "Buff", "Damage Reduction", "8%", D, "Perm", D, D, D),
            ]),
            ("2", "Active", "On Cast", D, "Cast", "None", "Self", [
                ("Self", "Buff", "Shield", "350/450/2000% AP", D, "Once", "4", D, D),
            ]),
            ("3", "Active", "On Cast", D, "Cast", "None", "Lowest-HP Allies", [
                ("2 lowest-HP allies", "Buff", "Shield", "225/275/1500% AP", D, "Once", "4", D, D),
            ]),
            ("4", "Active", "After Shielding Allies", D, "Circle AOE", "Area", "Self", [
                ("Self", "Buff", "Shield", "(refresh)", D, "Once", "4", "1", D),
                ("Enemies in area", "Attack", "Damage", "240/360/2500% AP",
                 "burst", "Once", D, "1", D),
            ]),
        ],
    ),
    (
        ["Yasuo", "4 Gold", "Carry", "Ionia", "", "Challenger", "", "Frontliner",
         "Whirlwind Dash Carry",
         "Ionia Bonus: +15% Omnivamp. Active: send a whirlwind at the furthest enemy within "
         "3 hexes, knocking up and Stunning all enemies hit. Dash to and slash the original "
         "target for heavy physical damage, then slam it into the ground, damaging enemies "
         "within 1 hex."],
        [
            ("1", "Passive", "Game Start", "If Ionia Active", "Cast", "None", "Self", [
                ("Self", "Buff", "Omnivamp", "15%", D, "Perm", D, D, D),
            ]),
            ("2", "Active", "On Cast", D, "Wave", "Pierce-All", "Farthest (within 3 hex)", [
                ("Enemies in path", "Status", "Stun", D, D, "Once", D, D, D),
            ]),
            ("3", "Active", "After Whirlwind", D, "Leap", "None", "Farthest (within 3 hex)", [
                ("Self", "Movement", "(reposition)", D, D, D, D, D, D),
            ]),
            ("4", "Active", "After Leap", D, "Cast", "Target-Only", "Current", [
                ("Aimed enemy", "Attack", "Damage", "500/500/1500% AD + 55/85/300% AP",
                 D, "Once", D, D, D),
            ]),
            ("5", "Active", "After Slash", D, "Circle AOE", "Area", "Current", [
                ("Enemies in area", "Attack", "Damage", "300/300/750% AD", D, "Once", D, "1", D),
            ]),
        ],
    ),
    (
        ["Ahri", "5 Gold", "Carry", "Ionia", "", "Sorcerer", "", "Backliner",
         "Essence-Steal Spell Carry",
         "Ionia Bonus: +3 Mana per second. Active: steal essence from enemies around the current "
         "target, dealing magic damage and Mana Reaving them. Every 2/2/0 casts, unleash a wave "
         "that damages all enemies hit, dealing 33% more to enemies whose essence has been "
         "stolen."],
        [
            ("1", "Passive", "Game Start", "If Ionia Active", "Cast", "None", "Self", [
                ("Self", "Buff", "Mana Regen", "3 /s", D, "Perm", D, D, D),
            ]),
            ("2", "Active", "On Cast", D, "Circle AOE", "Area", "Current", [
                ("Enemies in area", "Attack", "Damage", "105/150/1000% AP", D, "Once", D, "1", D),
                ("Enemies in area", "Debuff", "Mana Reave", "20%",
                 "until next cast", "Once", D, "1", D),
            ]),
            ("3", "Active", "On 2nd Cast", "Every 2/2/0 casts", "Wave", "Pierce-All", "Current", [
                ("Enemies in path", "Attack", "Damage", "260/390/1999% AP",
                 "+33% if essence stolen", "Once", D, D, D),
            ]),
        ],
    ),
]

ACTION_TYPES = [
    ["Burst Projectile", "Area", "Not specify",
     "Projectile flies at the aim target and DETONATES on impact; the effect hits everyone in an "
     "X-hex circle centred on the IMPACT hex, not on the caster. (Karma's energy burst)"],
    ["Grab & Slam", "Flank-Pair", "Once",
     "Self grabs one enemy from EACH side and slams them together; the effect applies only to the "
     "grabbed enemies. If only one side is occupied, only one is grabbed - and the effect is "
     "amplified. (Sett)"],
    ["Summon Shadow", "None", "Not specify",
     "Self spawns a clone at a target hex. The clone becomes a SECOND action source for the "
     "following step - its AOE is centred on the clone, not on Self. (Zed)"],
]

EFFECT_TYPES = [
    ["Buff", "Armor", "Increase the recipient's Armor (Defense)."],
    ["Buff", "MR", "Increase the recipient's Magic Resist."],
    ["Buff", "AD", "Increase the recipient's Attack Damage."],
    ["Buff", "AP", "Increase the recipient's Ability Power."],
    ["Buff", "Crit Chance", "Increase the recipient's Critical Strike Chance."],
    ["Buff", "Crit Damage", "Increase the recipient's Critical Strike Damage."],
    ["Buff", "Omnivamp", "Recipient heals for a percentage of the damage it deals."],
    ["Buff", "Mana Regen", "Recipient gains Mana per second."],
    ["Debuff", "Mana Reave",
     "Increase the recipient's max Mana until its next cast - delays its next ability."],
    ["Movement", "(summon)",
     "Spawns a clone/summon that acts as a SECOND action source for the following step."],
]

COLLISION_TYPES = [
    ["Flank-Pair",
     "The one enemy on EACH side of the caster (up to 2). Nothing between or beyond them is "
     "touched.",
     "Grabbed enemies",
     "Enemy only",
     "Grab & Slam",
     "Sett grabs one enemy from either side and slams them together; if only one side is "
     "occupied, only that one is grabbed - and the effect is amplified by 50%."],
]

# Column Explain: (row label to find, column index to rewrite, new text)
COLUMN_EXPLAIN_EDITS = [
    ("Trigger (When)", 2,
     "e.g. On Cast, While Channeling, After Cast, After Leap, On Kill, On Death, Game Start, "
     "On Attack, On 3rd Attack, On 2nd Cast, On 3rd Cast, On Bonus-HP Expire, On Shield Expire, "
     "When Transformed, After Summon, After Whirlwind, After Slash, After Shielding Allies."),
    ("Condition (Only if)", 2,
     "Lvl 1-5 / Lvl 6-8 / Lvl 9+, If Target Wounded, If Already Transformed, If Ally Hit, "
     "If Ionia Active, Every 2/2/0 casts. (Trigger = when; Condition = only-if.)"),
    ("Aim Target", 2,
     "e.g. Current / Farthest (within N hex) / Clustered / Self / Shadow / Lowest-HP Allies / "
     "Adjacent (both sides)."),
    ("Effect Recipient", 2,
     "Aimed enemy / Enemies in area / Enemies in path / Allies in path / Self / Grabbed enemies / "
     "2 lowest-HP allies / Enemies adjacent to Shadow."),
]

COLUMN_EXPLAIN_NOTES = [
    ["Note - Ionia Bonus",
     "Each Ionia unit's unique per-unit bonus is modelled as a skill step.",
     "Encoded as Passive / Game Start / Condition = If Ionia Active, Action = Cast, Recipient = "
     "Self, Category = Buff. It doubles in spirit form per the Ionia trait (3/6/9) - that trait "
     "scaling is trait data and lives in tft-set9 -> Origins, not here."],
    ["Note - Yasuo",
     "The whirlwind's Stun has no duration in the source.",
     "tft-set9 -> Champions -> Skill Description states the whirlwind Stuns but never says for "
     "how long. Duration (s) is left as an em-dash rather than inventing a number."],
    ["Note - Roster",
     "The Hero tab covers the Set 9.0 roster only.",
     "9.5-only champions are excluded: Demacia's Fiora and Quinn, and Ionia's Xayah."],
]


def col_letter(i):
    s, i = "", i + 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def main():
    gc = gspread.service_account(filename="google-service-credential.json")
    sh = gc.open_by_key(SKILL_KEY)
    hero = sh.worksheet("Hero")

    existing = hero.get_all_values()
    already = {r[0].strip() for r in existing if r and r[0].strip()}
    if CHAMPIONS[0][0][0] in already:
        print("Hero tab already contains Ionia champions - skipping the Hero write.")
        write_reference_tabs(sh)
        return

    start = len(existing) + 1  # first free row (1-indexed)
    print(f"Hero tab currently ends at row {len(existing)}; appending from row {start}")

    rows, merges = [], []
    r = start
    for ident, actions in CHAMPIONS:
        first = True
        for step, stype, trig, cond, act, coll, aim, effects in actions:
            group_start = r
            for e in effects:
                head = ident if first else [""] * 10
                mid = [step, stype, trig, cond, act, coll, aim] if r == group_start else [""] * 7
                rows.append(head + mid + list(e))
                first = False
                r += 1
            if len(effects) > 1:  # one action, many effects -> merge K..Q down the group
                for c in range(10, 17):  # cols K..Q
                    merges.append({
                        "mergeCells": {
                            "range": {
                                "sheetId": hero.id,
                                "startRowIndex": group_start - 1,
                                "endRowIndex": r - 1,
                                "startColumnIndex": c,
                                "endColumnIndex": c + 1,
                            },
                            "mergeType": "MERGE_COLUMNS",
                        }
                    })

    end = start + len(rows) - 1
    print(f"Writing {len(rows)} rows ({start}-{end}), {len(merges)} merge requests")

    # grow the grid if needed, then copy row 2's formatting down over the new block
    grid_rows = hero.row_count
    pre = []
    if end > grid_rows:
        pre.append({"appendDimension": {"sheetId": hero.id, "dimension": "ROWS",
                                        "length": end - grid_rows + 2}})
    pre.append({"copyPaste": {
        "source": {"sheetId": hero.id, "startRowIndex": 1, "endRowIndex": 2,
                   "startColumnIndex": 0, "endColumnIndex": 26},
        "destination": {"sheetId": hero.id, "startRowIndex": start - 1, "endRowIndex": end,
                        "startColumnIndex": 0, "endColumnIndex": 26},
        "pasteType": "PASTE_FORMAT",
    }})
    sh.batch_update({"requests": pre})

    hero.update(rows, f"A{start}:{col_letter(25)}{end}", value_input_option="RAW")
    if merges:
        sh.batch_update({"requests": merges})
    print("Hero tab written.")

    write_reference_tabs(sh)


def write_reference_tabs(sh):
    for tab, new_rows, key_cols in [("Action Types", ACTION_TYPES, 1),
                                    ("Effect Types", EFFECT_TYPES, 2),
                                    ("Collision Types", COLLISION_TYPES, 1)]:
        ws = sh.worksheet(tab)
        vals = ws.get_all_values()
        seen = {tuple(r[:key_cols]) for r in vals}
        pending = [r for r in new_rows if tuple(r[:key_cols]) not in seen]
        if not pending:
            print(f"{tab}: already up to date")
            continue
        # Collision Types carries a trailing prose block - the new row goes before it
        cut = len(vals)
        for i, row in enumerate(vals):
            if i > 0 and not any(c.strip() for c in row):
                cut = i
                break
        if cut < len(vals):
            ws.insert_rows(pending, row=cut + 1, value_input_option="RAW")
        else:
            ws.append_rows(pending, value_input_option="RAW")
        print(f"{tab}: added {len(pending)} rows after row {cut}")

    ce = sh.worksheet("Column Explain")
    vals = ce.get_all_values()
    updates = []
    for label, col, text in COLUMN_EXPLAIN_EDITS:
        for i, row in enumerate(vals):
            if row and row[0].strip() == label:
                updates.append({"range": f"{col_letter(col)}{i + 1}", "values": [[text]]})
                break
        else:
            raise SystemExit(f"Column Explain: row '{label}' not found")
    ce.batch_update(updates, value_input_option="RAW")

    seen = {r[0].strip() for r in vals if r}
    notes = [n for n in COLUMN_EXPLAIN_NOTES if n[0] not in seen]
    if notes:
        ce.append_rows(notes, value_input_option="RAW")
    print(f"Column Explain: {len(updates)} cells rewritten, {len(notes)} note rows appended")


if __name__ == "__main__":
    main()
