"""Add the Shadow Isles + Targon champions to `Hero`.

Run from repo-root cwd:  python .claude/scripts/tft-add-shadowisles-targon.py

Roster (tft-set9 -> Champions, counts checked against tft-set9 -> Origins):
  Shadow Isles (5): Viego, Maokai, Kalista, Gwen, Senna
  Targon       (3): Soraka, Taric, Aphelios

Senna is Redeemer + Shadow Isles and goes in under her Origin 2, as Ekko did for Piltover and
Cassiopeia for Shurima. Neither trait has a per-unit bonus (Shadow Isles shields after 12 damage
events; Targon amplifies healing team-wide), so there are no bonus rows - the Freljord/Piltover
precedent, not the Ionia one.

FIRST PASS SINCE Count/Spread BECAME CANONICAL
----------------------------------------------
Every action here sets Count and Spread explicitly. backfill_hero() in tft-action-templates.py
would default a blank to 1/em-dash, but that is a safety net, not the plan: a blank cell reads as
"unknown", and the whole point of the column is that multiplicity stops hiding in free text.

Three champions exercise the model on data it has never seen, and it holds without a new Spread:
Kalista's 6 spears, Gwen's 3 snips and Soraka's 5 stars are all Count > 1, Spread = Same target.

OWNERSHIP
---------
This is the latest origin pass, so it takes over the `Column Explain` VALUE LISTS - Trigger,
Condition, Aim Target, Effect Recipient - from tft-add-freljord-piltover.py (which held the first
three) and tft-add-shurima.py (which held Condition). One owner per cell: two scripts writing the
same cell overwrite each other on every run, and that bug has bitten twice.

`Action Types` and `Action Templates` are NOT touched here. Gwen's new `Cone Slash` action is
registered by the scripts that own those tabs - tft-apply-comments.py and tft-action-templates.py.

Source of every number: tft-set9 -> Champions -> Skill Description.
"""

from tft_sheet import (ACTION_BLOCK, D, IDENTITY_BLOCK, SAME, col_letter, cols, merge_request,
                       open_sheet, sync_notes)

# identity (A-J) + actions
# action = (step, skill_type, trigger, condition, source, action, count, spread, collision, aim,
#           [effect, ...])
# effect = (recipient, category, detail, amount, scaling, cadence, duration, aoe, cast)
CHAMPIONS = [
    (
        ["Viego", "1 Gold", "Carry", "Shadow Isles", "", "Rogue", "", "1",
         "Stacking Melee Assassin",
         "Deal 110/165/250% Ability Power magic damage to the current target. For the rest of "
         "combat, Viego's attacks deal 20/30/45% Ability Power bonus stacking magic damage."],
        [
            # Range 1: the cast is a melee strike, so it projects no hitbox - Collision None.
            ("1", "Active", "On Cast", D, "Self", "Cast", "1", D, "None", "Current", [
                (SAME, "Attack", "Damage", "110/165/250% AP", D, "Once", D, D, D),
            ]),
            # "For the rest of combat" is what Cadence = Perm is for; Duration stays an em-dash
            # rather than inventing a number for "forever".
            ("2", "Active", "On Cast", D, "Self", "Cast", "1", D, "None", "Self", [
                (SAME, "Buff", "Empowered Attack", "20/30/45% AP", "stacking", "Perm", D, D, D),
            ]),
        ],
    ),
    (
        # tft-set9 lists Maokai's ENTIRE stat block as N/A - including Range. Left as an em-dash
        # rather than guessed at; recorded as 'Note - Maokai'. (The Yasuo precedent: the source is
        # silent, so the sheet says so.)
        ["Maokai", "1 Gold", "Tank", "Shadow Isles", "", "Bastion", "", D,
         "Mana-Leeching Healing Tank",
         "Sap Magic: Passive: Whenever an enemy casts an Ability, gain 5 Mana. Active: On his next "
         "attack, heal for 220/260/300% Ability Power."],
        [
            ("1", "Passive", "On Enemy Cast", D, "Self", "Cast", "1", D, "None", "Self", [
                (SAME, "Buff", "Mana", "5", D, "Once", D, D, D),
            ]),
            ("2", "Active", "On Cast", D, "Self", "Cast", "1", D, "None", "Self", [
                (SAME, "Buff", "Empowered Attack", D, D, "Once", D, D, D),
            ]),
            # The heal rides on the empowered attack, so the ACTION is the auto-attack (aimed at
            # the enemy) while the EFFECT lands on Maokai. Aim and Recipient genuinely differ.
            ("3", "Passive", "On Attack", "If Empowered", "Self", "Auto-Attack", "1", D,
             "Target-Only", "Current", [
                 ("Self", "Buff", "Heal", "220/260/300% AP", D, "Once", D, D, D),
             ]),
        ],
    ),
    (
        ["Kalista", "3 Gold", "Carry", "Shadow Isles", "", "Challenger", "", "4",
         "Spear-Stacking Executioner",
         "Passive: Attacks impale a spear in the target, which deals 18/27/45% Ability Power true "
         "damage when removed. Kalista rips the spears out if it would kill the target. Active: "
         "Impale 6 spears in the current target."],
        [
            ("1", "Passive", "On Attack", D, "Self", "Auto-Attack", "1", D, "Target-Only",
             "Current", [
                 (SAME, "Status", "Impale", D, "stacking", "Perm", D, D, D),
             ]),
            # The payout is a separate step because it fires on a different trigger: the spears sit
            # in the target doing nothing until they are pulled.
            # Lethal is the ONLY thing that ever pulls a spear (user-confirmed): the stacks build
            # until their combined true damage would kill, and it fires THEN. So the trigger says
            # it and the Condition is an em-dash - 'If Lethal' would only say it a second time.
            ("2", "Passive", "On Spears Lethal", D, "Self", "Cast", "1", D, "None",
             "Current", [
                 (SAME, "Attack", "True Damage", "18/27/45% AP", "per spear removed", "Once",
                  D, D, D),
             ]),
            # 6 spears, all into the one aimed enemy - Count 6, Spread Same target. Each is its own
            # hitbox, so each lands its own Impale (contrast Karma, whose 3 share one hitbox).
            ("3", "Active", "On Cast", D, "Self", "Homing Projectile", "6", "Same target",
             "Target-Only", "Current", [
                 (SAME, "Status", "Impale", D, D, "Once", D, D, D),
             ]),
        ],
    ),
    (
        ["Gwen", "4 Gold", "Carry", "Shadow Isles", "", "Slayer", "", "2",
         "Dashing Cone Slayer",
         "Dash around the current target and snip 3 times in a cone, each dealing 100/150/400% "
         "Ability Power magic damage to enemies hit. Every 3 casts, gain 120/120/300 Armor and "
         "Magic Resist for 3/3/5 seconds."],
        [
            ("1", "Active", "On Cast", D, "Self", "Leap", "1", D, "None", "Current", [
                ("Self", "Movement", "(reposition)", D, D, "Once", D, D, D),
            ]),
            # The cone is the HITBOX here (a real collider she swings 3 times), NOT an arrangement
            # of 3 separate hitboxes - which is why Spread is 'Same target' and not 'Cone'. Ashe's
            # Spread = Cone is the other reading: 8 arrows with no cone collider at all. Both tabs
            # spell the difference out.
            ("2", "Active", "After Leap", D, "Self", "Cone Slash", "3", "Same target", "Area",
             "Current", [
                 ("Enemies in area", "Attack", "Damage", "100/150/400% AP", D, "Once", D, D, D),
             ]),
            ("3", "Passive", "On 3rd Cast", D, "Self", "Cast", "1", D, "None", "Self", [
                (SAME, "Buff", "Armor", "120/120/300", D, "Once", "3/3/5", D, D),
                (SAME, "Buff", "MR", "120/120/300", D, "Once", "3/3/5", D, D),
            ]),
        ],
    ),
    (
        # Redeemer + Shadow Isles: entered under Origin 2, as Ekko was under Piltover.
        ["Senna", "5 Gold", "Support", "Redeemer", "Shadow Isles", "Gunner", "", "4",
         "Board-Wide Beam Support",
         "Fire a massive beam at the furthest enemy, dealing 235/250/2000% Attack Damage physical "
         "damage to all enemies hit. Any allies hit gain 200/275/4000% Ability Power Shield for "
         "4/4/15 seconds."],
        [
            # One beam, two recipients - it damages the enemies it pierces AND shields the allies
            # it pierces. Exactly Sona's precedent, and the second real user of Laser Shot.
            ("1", "Active", "On Cast", D, "Self", "Laser Shot", "1", D, "Pierce-All", "Farthest", [
                ("Enemies in path", "Attack", "Damage", "235/250/2000% AD", D, "Once", D, D, D),
                ("Allies in path", "Buff", "Shield", "200/275/4000% AP", D, "Once", "4/4/15",
                 D, D),
            ]),
        ],
    ),
    (
        ["Soraka", "2 Gold", "Support", "Targon", "", "Invoker", "", "4",
         "Star-Fall Healer",
         "Heal the lowest health ally for 140/160/180% Ability Power. If the ally is below 50% "
         "Health, heal them for an additional 140/160/180% Ability Power. Over the next 5 seconds, "
         "5 stars hit the enemy closest to them. Each deals 120/180/280% Ability Power magic "
         "damage."],
        [
            ("1", "Active", "On Cast", D, "Self", "Cast", "1", D, "None", "Lowest-HP Ally", [
                (SAME, "Buff", "Heal", "140/160/180% AP", D, "Once", D, D, D),
            ]),
            # The bonus heal is its own step, not a second effect row: it fires only under a
            # Condition, and Condition is an action-level column merged across the action's rows.
            ("2", "Active", "On Cast", "If Ally Below 50% HP", "Self", "Cast", "1", D, "None",
             "Step 1 Aim target", [
                 (SAME, "Buff", "Heal", "140/160/180% AP", "additional heal", "Once", D, D, D),
             ]),
            # The stars fall ON the enemy - nothing is fired and nothing travels, so this is Spawn
            # At Target. They are aimed relative to the ALLY she healed, not to Soraka.
            ("3", "Active", "After Cast", D, "Self", "Spawn At Target", "5", "Same target",
             "Target-Only", "Nearest enemy to the healed ally", [
                 (SAME, "Attack", "Damage", "120/180/280% AP", D, "Over Time", "5", D, D),
             ]),
        ],
    ),
    (
        ["Taric", "3 Gold", "Tank", "Targon", "", "Bastion", "Sorcerer", "1",
         "Damage-Redirecting Shield Tank",
         "Gain 500/580/680% Ability Power Shield for 4 seconds. It redirects 50% of the damage "
         "received by adjacent allies."],
        [
            # One action, two recipients: the shield lands on Taric, the redirect lands on his
            # neighbours. The redirect is not a shield on THEM - it moves their damage to HIM.
            ("1", "Active", "On Cast", D, "Self", "Cast", "1", D, "None", "Self", [
                (SAME, "Buff", "Shield", "500/580/680% AP", D, "Once", "4", D, D),
                ("Adjacent allies (left & right)", "Buff", "Damage Redirect", "50%",
                 "redirected into Taric's shield", "Once", "4", D, D),
            ]),
        ],
    ),
    (
        ["Aphelios", "4 Gold", "Carry", "Targon", "", "Deadeye", "", "4",
         "Chakram-Stacking Moon Carry",
         "Fire a moon blast at the largest group of enemies that deals 240/240/750% Attack Damage "
         "physical damage to enemies within 2 hexes. For 7 seconds, equip 3 Chakram, plus 1 more "
         "for each enemy hit by the blast. Attacks deal 7/7/15% Attack Damage bonus physical "
         "damage for each Chakram equipped. Aphelios heals for 75% of damage dealt by Chakrams "
         "(increased by Ability Power)."],
        [
            # "the largest group of enemies" is exactly what the existing Clustered aim means.
            ("1", "Active", "On Cast", D, "Self", "Burst Projectile", "1", D, "First-Hit",
             "Clustered", [
                 ("Enemies in area", "Attack", "Damage", "240/240/750% AD", D, "Once", D, "2", D),
             ]),
            # Chakram is a STACK RESOURCE, not a stat: it does nothing by itself, and the two rows
            # below scale off how many are equipped.
            ("2", "Active", "After Cast", D, "Self", "Cast", "1", D, "None", "Self", [
                (SAME, "Buff", "Chakram", "3", "+1 per enemy hit by the blast", "Once", "7",
                 D, D),
            ]),
            ("3", "Passive", "On Attack", "If Empowered", "Self", "Auto-Attack", "1", D,
             "Target-Only", "Current", [
                 (SAME, "Attack", "Damage", "7/7/15% AD", "per Chakram equipped", "Once", D, D, D),
                 ("Self", "Buff", "Omnivamp", "75%", "of Chakram damage only; increased by AP",
                  "Once", D, D, D),
             ]),
        ],
    ),
]

EFFECT_TYPES = [
    ["Buff", "Mana", "Instantly grants the recipient flat Mana. Distinct from Mana Regen, which "
                     "grants it per second."],
    ["Status", "Impale", "A spear left standing in the target. It does nothing until REMOVED, and "
                         "pays out its damage then. Stacks; Kalista rips them all out at once if "
                         "that would be lethal."],
    ["Buff", "Damage Redirect", "A share of the damage the recipient takes is moved onto the "
                                "CASTER instead. Not a shield on the recipient - the damage is "
                                "still dealt, just to someone else (Taric)."],
    ["Buff", "Chakram", "A stack resource held by the caster. It is not a stat and does nothing on "
                        "its own - other effects scale off how many are equipped (Aphelios)."],
]

# This script is the latest origin pass, so it owns these four value lists - see the OWNERSHIP note
# in the module docstring. Additions this pass are marked in the source, not in the cell.
COLUMN_EXPLAIN_EDITS = {
    "Trigger (When)": {
        2: "e.g. On Cast, While Channeling, After Cast, After Leap, On Kill, On Death, Game Start, "
           "On Attack, On 3rd Attack, On 2nd Cast, On 3rd Cast, On Bonus-HP Expire, On Shield "
           "Expire, When Transformed, After Summon, After Whirlwind, After Slash, After Shielding "
           "Allies, On Enemy Knocked Up, After Knock Back, On Ally Attack Chilled Enemy, On Enemy "
           "Cast, On Spears Lethal.",
    },
    # 'If Lethal' was dropped: the user confirmed lethal is the ONLY thing that ever pulls
    # Kalista's spears, so the trigger already says it and the condition was saying it twice.
    "Condition (Only if)": {
        2: "Lvl 1-5 / Lvl 6-8 / Lvl 9+, If Target Wounded, If Already Transformed, If Ally Hit, "
           "If Ionia Active, Every 2/2/0 casts, If Empowered, If Already 3 Soldiers, If Target at "
           "Edge, If Target Not at Edge, If Ally Below 50% HP. (Trigger = when; "
           "Condition = only-if.)",
    },
    "Aim Target": {
        2: "ABSOLUTE, never relative to the Action Source — 'Self' always means the champion, so "
           "a summon's own AOE is aimed at 'Summon' (Zed's shadow), NOT at 'Self'. Values: Current "
           "/ Farthest / Farthest (within N hex) / Clustered / Self / Summon / Lowest-HP Ally / "
           "Lowest-HP Allies / Adjacent (both sides) / Knocked-up enemy / Nearest N enemies / "
           "Nearest enemy to the healed ally / Step N Aim target (re-aims at whatever an earlier "
           "step aimed at — e.g. Yasuo's dash and slam both return to the enemy his Step 2 "
           "whirlwind picked).",
    },
    "Effect Recipient": {
        2: "Aimed enemy / First hit enemy / Enemies in area / Enemies in path / All enemies / "
           "Allies in path / Adjacent allies (left & right) / Self / Grabbed enemies / 2 lowest-HP "
           "allies. If the recipient is exactly the Aim Target, write 'Same to Aim Target' rather "
           "than restating it — the cell then only ever carries NEW information.",
    },
}

COLUMN_EXPLAIN_NOTES = [
    ["Note - Shadow Isles / Targon",
     "Neither has a per-unit bonus, unlike Ionia.",
     "Shadow Isles shields its units after 12 damage events; Targon amplifies all healing and "
     "shielding team-wide. Both are blanket trait effects with no per-champion text to encode, so "
     "there are no bonus rows. The trait numbers live in tft-set9 -> Origins. Senna is Redeemer + "
     "Shadow Isles and is entered under her Origin 2, as Ekko was under Piltover."],
    ["Note - Maokai",
     "His entire stat block is N/A in the source, so Range is an em-dash.",
     "tft-set9 -> Champions lists Health, Armor, MR, Mana, AD, AS and Range as 'N/A' for Maokai "
     "alone. Range is the only one this schema carries, and it is left blank rather than guessed "
     "at - the same rule as Yasuo's unstated Stun duration. If the source is ever filled in, this "
     "is the cell to update."],
    ["Note - Cone: shape vs spread",
     "'Cone' means two different things, deliberately. Check which column it is in.",
     "SHAPE = Cone (see 'Action Templates') is a real cone-shaped HITBOX - one collider. Gwen's "
     "Cone Slash is this, and she swings it 3 times (Count 3, Spread = Same target). SPREAD = Cone "
     "(see 'Spread Types') is the opposite: N SEPARATE hitboxes ARRANGED in a cone, with no cone "
     "collider anywhere - Ashe's 8 arrows, each stopping on the first body in its own lane. A wide "
     "Ashe cone can miss; a Gwen cone cannot."],
]


def append_champions(sh, ws):
    """Append the 8 champions, building every row BY COLUMN NAME.

    Never positionally: the Hero header has had columns inserted into its middle twice now
    (Action Source, then Count/Spread), and every script that addressed cells by index silently
    started writing into the wrong column the moment that happened.
    """
    vals = ws.get_all_values()
    c = cols(vals[0])
    width = len(vals[0])
    already = {r[c["Champion"]].strip() for r in vals if r[c["Champion"]].strip()}
    todo = [x for x in CHAMPIONS if x[0][0] not in already]
    if not todo:
        print("Hero: Shadow Isles/Targon champions already present")
        return

    head_cols = ["Step", "Skill Type", "Trigger", "Condition", "Action Source", "Action",
                 "Count", "Spread", "Collision", "Aim Target"]
    effect_cols = ["Effect Recipient", "Effect Category", "Effect Detail", "Amount", "Scaling",
                   "Cadence", "Duration", "AOE", "Cast"]

    start = len(vals) + 1
    rows, merges, blocks = [], [], []
    r = start
    for ident, actions in todo:
        block = r
        first = True
        for *head, effects in actions:
            group = r
            for e in effects:
                row = [""] * width
                if first:
                    for k, v in enumerate(ident):
                        row[c[IDENTITY_BLOCK[k]]] = v
                if r == group:
                    for name, v in zip(head_cols, head):
                        row[c[name]] = v
                for name, v in zip(effect_cols, e):
                    row[c[name]] = v
                rows.append(row)
                first = False
                r += 1
            if len(effects) > 1:   # one action, many effects -> merge the action block down them
                merges += [(group, r, c[n]) for n in ACTION_BLOCK]
        if r - block > 1:          # merge the identity block down the whole champion
            merges += [(block, r, c[n]) for n in IDENTITY_BLOCK]
        blocks.append((ident[0], block, r - 1))

    end = start + len(rows) - 1
    pre = []
    if end > ws.row_count:
        pre.append({"appendDimension": {"sheetId": ws.id, "dimension": "ROWS",
                                        "length": end - ws.row_count + 2}})
    pre.append({"copyPaste": {   # carry the tab's formatting down onto the new rows
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

    ws = sh.worksheet("Column Explain")
    vals = ws.get_all_values()
    edits = []
    for label, columns in COLUMN_EXPLAIN_EDITS.items():
        i = next((k for k, r in enumerate(vals) if r[0].strip() == label), None)
        if i is None:
            raise SystemExit(f"Column Explain: row '{label}' not found")
        for col, text in columns.items():
            if vals[i][col] != text:
                edits.append({"range": f"{col_letter(col)}{i + 1}", "values": [[text]]})
    if edits:
        ws.batch_update(edits, value_input_option="RAW")



def main():
    sh = open_sheet()
    ws = sh.worksheet("Hero")
    append_champions(sh, ws)
    fix_reference_tabs(sh)
    print("\nGwen's 'Cone Slash' is registered by the tabs' owners: run tft-apply-comments.py "
          "(Action Types) and tft-action-templates.py (Action Templates / Spread Types).")
    sync_notes(sh, COLUMN_EXPLAIN_NOTES)


if __name__ == "__main__":
    main()
