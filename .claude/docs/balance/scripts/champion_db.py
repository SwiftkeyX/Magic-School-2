# champion_db.py
#
# ============================================================
# WARNING: THIS FILE IS NOT THE SOURCE OF TRUTH
# ============================================================
# All base champion stats (ad, as, max_mana, start_mana,
# lockout) should be driven by the Google Sheets spreadsheet:
#
#   Sheet: "TFT Set 9 Analysis"
#   URL:   https://docs.google.com/spreadsheets/d/1pnbDKR55HxXFUExIXKyksJqaUSrNuw53IfnvBEt9zNY
#   Tab:   "Hero Data"
#
# This file holds FORMULAS, lambdas, item configs, and
# cycle overrides that cannot live in the sheet.
# Stat values here are manually synced from the sheet and
# may drift. Always treat the sheet as authoritative.
#
# KNOWN MISMATCHES vs sheet dump (2026-07-06) — awaiting decision:
#   Jhin     max_mana  Sheet=114   DB=120
#   Samira   lockout   Sheet=0.8   DB=0.5
#   Zed      as        Sheet=0.70  DB=0.75
#   Ekko     max_mana  Sheet=45    DB=50
#   Kalista  max_mana  Sheet=80    DB=60
#   Rek'Sai  max_mana  Sheet=75    DB=80
#
# Tier 4/5 champions (Aphelios, Azir, Gwen, Kai'Sa, Lux,
# Yasuo, Zeri, Aatrox, Ahri, Bel'Veth) are NOT in the
# current sheet dump and cannot be cross-checked.
# ============================================================
#
# Contains all carry champion stats, optimal item configurations,
# and formulas for Set 9 carry analysis.

ITEMS = {
    "Blue Buff": {
        "ap": 10,
        "max_mana_mod": -10,
    },
    "Jeweled Gauntlet": {
        "ap": 20,
        "crit_chance": 0.15,
        "crit_dmg": 0.30,
        "spell_crit": True
    },
    "Archangel's Staff": {
        # Grants +20 AP base. Ramps +20 AP every 5s. Over 30s, average is 100 AP + 10 BB + 20 JG + 20 AA base + 50 AA ramp = 200 AP.
        # AA contribution to average AP is +70.
        "ap": 70,
    },
    "Deathblade": {
        "ad_percent": 0.66
    },
    "Infinity Edge": {
        "ad_percent": 0.35,
        "crit_chance": 0.35,
        "spell_crit": True
    },
    "Last Whisper": {
        "ad_percent": 0.10,
        "as_percent": 0.10,
        "crit_chance": 0.10,
    },
    "Spear of Shojin": {
        "ap": 25,
        "ad_percent": 0.15,
        "mana_per_attack": 15,
    },
    "Giant Slayer": {
        "ap": 20,
        "ad_percent": 0.25,
        "amp": 1.25,
    },
    "Guinsoo's Rageblade": {
        "as_percent": 0.18,
        # Ramping AS is represented via average AS overrides on Guinsoo users.
    },
    "Runaan's Hurricane": {
        "ad_percent": 0.20,
        "amp": 1.50,
    },
    "Rabadon's Deathcap": {
        "ap": 70,
    },
    "Hextech Gunblade": {
        "ap": 25,
        "ad_percent": 0.10,
    },
    "Titan's Resolve": {
        # Fully stacked TR grants +50 AP and +20% AD
        "ap": 50,
        "ad_percent": 0.20,
    },
    "Bloodthirster": {
        "ad_percent": 0.20,
    },
    "Ionic Spark": {
        "ap": 10,
        "amp": 1.15,
    }
}

CHAMPIONS = {
    # TIER 1 CARRIES
    "Cassiopeia": {
        "skill_desc": "Deal 160/240/360 magic damage to the current target and Wound them for 5 seconds. If they are already Wounded, deal 30% bonus magic damage. (Wound: reduces healing received by 33%).",
        "formula_explanation": "Spell base represents the flat base damage ([160, 240, 360]). Spell damage is multiplied by 1.30 to account for wound bonus, which is maintained continuously because her 4.79s unequipped cast cycle is shorter than the 5s wound duration.",
        "tier": 1,
        "ad": [40, 60, 90],
        "as": 0.70,
        "max_mana": 30,
        "start_mana": 0,
        "lockout": 0.5,
        "spell_base": [160, 240, 360],
        "target_density": 1.0,
        "nuance": "wound",
        "base_attacks": 3,
        "base_spell": lambda ad, spell, idx: spell[idx] * 1.30,
        "equipped_items": ["Blue Buff", "Jeweled Gauntlet", "Archangel's Staff"],
        "eq_cycle": 3.3571,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp: (spell[idx] * 1.30) * (ap / 100.0) * crit,
        "baseline_override": lambda star: [25.1, 43.5, 68.6] if star == 1 else ([37.6, 65.2, 102.8] if star == 2 else [56.4, 97.8, 154.2]),
        "equipped_override": lambda star: [30.5, 158.6, 189.1] if star == 1 else ([45.8, 237.9, 283.7] if star == 2 else [68.6, 356.9, 425.5])
    },
    "Jhin": {
        "skill_desc": "Take aim at the current target and deal 300%/300%/344% AD + 60/90/135 physical damage to enemies in a line; each hit reduces this damage by 56% (or deals 44% of the previous hit's damage). Ionia Bonus: +25% Attack Damage.",
        "formula_explanation": "spell_base represents the flat base damage ([60, 90, 135]) and spell_ad_ratio represents the AD scaling (3.00x/3.00x/3.44x). target_density is set to 2.0 (number of targets hit), and pierce_falloff is set to 0.56. Overrides represent the exact hybrid math.",
        "tier": 1,
        "ad": [54, 81, 122],
        "as": 0.70,
        "max_mana": 120,
        "start_mana": 0,
        "lockout": 1.6,
        "spell_base": [60, 90, 135],
        "spell_ad_ratio": [3.00, 3.00, 3.44],
        "target_density": 2.0,
        "pierce_falloff": 0.56,
        "nuance": "ad-ratio physical line",
        "base_spell": lambda ad, spell, idx, ratio=[3.00, 3.00, 3.44], mult=1.44: (ad * ratio[idx] + spell[idx]) * mult,
        "equipped_items": ["Deathblade", "Infinity Edge", "Last Whisper"],
        "eq_spell": lambda ad, spell, idx, ap, crit, amp, ratio=[3.00, 3.00, 3.44], mult=1.44: (ad * ratio[idx] + spell[idx]) * mult * crit,
        "baseline_override": lambda star: [34.6, 35.5, 70.1] if star == 1 else ([51.9, 53.2, 105.1] if star == 2 else [78.1, 80.1, 158.2]),
        "equipped_override": lambda star: [99.1, 94.8, 193.9] if star == 1 else ([148.7, 142.1, 290.8] if star == 2 else [223.1, 213.2, 436.3])
    },
    "Malzahar": {
        "skill_desc": "Open two portals near the current target. Destroy 50% of Shields and deal 220/330/500 magic damage to all enemies caught between the portals.",
        "formula_explanation": "spell_base represents the flat base damage ([220, 330, 500]). Applies target density multiplier of 1.50 directly to the spell base. Calculated dynamically without overrides.",
        "tier": 1,
        "ad": [40, 60, 90],
        "as": 0.70,
        "max_mana": 50,
        "start_mana": 0,
        "lockout": 0.8,
        "spell_base": [220, 330, 500],
        "target_density": 1.5,
        "nuance": "aoe magic",
        "base_attacks": 5,
        "base_spell": lambda ad, spell, idx: spell[idx] * 1.50,
        "equipped_items": ["Spear of Shojin", "Jeweled Gauntlet", "Rabadon's Deathcap"],
        "eq_spell": lambda ad, spell, idx, ap, crit, amp: (spell[idx] * 1.50) * (ap / 100.0) * crit
    },
    "Samira": {
        "skill_desc": "Shoot at the current target and deal 190/190/200% Attack Damage to the first enemy hit. Reduce their Armor by 10/15/20 for the rest of combat.",
        "formula_explanation": "spell_base is [0, 0, 0] since she has no flat spell damage, and spell_ad_ratio is the AD ratio ([1.90, 1.90, 2.00]). Overrides match the armor-shred-assisted sheet values.",
        "tier": 1,
        "ad": [45, 68, 101],
        "as": 0.70,
        "max_mana": 30,
        "start_mana": 0,
        "lockout": 0.5,
        "spell_base": [0, 0, 0],
        "spell_ad_ratio": [1.90, 1.90, 2.00],
        "target_density": 1.0,
        "nuance": "ad-ratio physical",
        "base_spell": lambda ad, spell, idx, ratio=[1.90, 1.90, 2.00]: ad * ratio[idx],
        "equipped_items": ["Deathblade", "Infinity Edge", "Last Whisper"],
        "eq_spell": lambda ad, spell, idx, ap, crit, amp, ratio=[1.90, 1.90, 2.00]: ad * ratio[idx] * crit,
        "baseline_override": lambda star: [26.5, 33.4, 59.9] if star == 1 else ([40.1, 50.1, 90.2] if star == 2 else [59.6, 75.2, 134.8]),
        "equipped_override": lambda star: [45.8, 45.3, 91.1] if star == 1 else ([68.6, 68.0, 136.6] if star == 2 else [102.9, 102.0, 204.9])
    },
    "Tristana": {
        "skill_desc": "Gain 1 Attack Speed for 4 seconds. For the duration, attacks explode on impact and deal 60% Attack Damage physical damage to enemies within 1 hex.",
        "formula_explanation": "spell_base is [0, 0, 0] since she has no base spell damage. Spell damage is physical and calculated as a percentage of her Attack Damage (60% AD). Average equipped AS is set to 1.63 to model Guinsoo stacks + active steroid AS.",
        "tier": 1,
        "ad": [45, 68, 101],
        "as": 0.70,
        "max_mana": 40,
        "start_mana": 0,
        "lockout": 0.0,
        "spell_base": [0, 0, 0],
        "target_density": 1.0,
        "nuance": "as-steroid physical splash",
        "base_spell": lambda ad, spell, idx: 4.72 * (0.60 * ad) * 1.0,
        "equipped_items": ["Guinsoo's Rageblade", "Last Whisper", "Infinity Edge"],
        "eq_as": 1.63,
        "eq_cycle": 6.454,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp: 10.52 * (0.60 * ad) * crit * 1.0,
        "baseline_override": lambda star: [31.5, 22.3, 53.8] if star == 1 else ([47.6, 33.4, 81.0] if star == 2 else [70.7, 50.2, 120.9]),
        "equipped_override": lambda star: [187.3, 81.4, 268.7] if star == 1 else ([282.1, 122.7, 404.8] if star == 2 else [420.3, 182.8, 603.1])
    },
    "Viego": {
        "skill_desc": "Deal 110/165/250 magic damage to the current target. For the rest of combat, Viego's attacks deal 20/30/45 bonus stacking magic damage.",
        "formula_explanation": "spell_base represents the flat base damage ([110, 165, 250]). Includes stacking magic damage on-hit. Baseline and equipped overrides return values corresponding to an average of 2 and 30 stacks respectively over combat.",
        "tier": 1,
        "ad": [45, 68, 101],
        "as": 0.75,
        "max_mana": 50,
        "start_mana": 0,
        "lockout": 0.8,
        "spell_base": [110, 165, 250],
        "target_density": 1.0,
        "nuance": "melee stacking magic",
        "base_spell": lambda ad, spell, idx: spell[idx] + 200.0,
        "equipped_items": ["Hextech Gunblade", "Titan's Resolve", "Jeweled Gauntlet"],
        "eq_as": 0.94,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp: spell[idx] * (ap / 100.0) * crit + 200.0 * crit,
        "baseline_override": lambda star: [30.1, 37.9, 68.0] if star == 1 else ([45.5, 56.9, 102.4] if star == 2 else [67.6, 85.3, 152.9]),
        "equipped_override": lambda star: [79.9, 125.4, 205.3] if star == 1 else ([120.3, 188.1, 308.4] if star == 2 else [179.4, 283.2, 462.6])
    },

    # TIER 2 CARRIES
    "Jinx": {
        "skill_desc": "Fires 5 rockets, splitting damage across nearby targets. Spell deals physical damage: AD * 1.50/1.55/1.60 + 15/20/35 per rocket.",
        "formula_explanation": "spell_base represents the flat base damage ([15, 20, 35]) and spell_ad_ratio is the AD ratio ([1.50, 1.55, 1.60]). target_density is 2.0. Overrides match the rocket launch sequence.",
        "tier": 2,
        "ad": [50, 75, 113], "as": 0.75, "max_mana": 70, "start_mana": 0, "lockout": 1.0,
        "spell_base": [15, 20, 35],
        "spell_ad_ratio": [1.50, 1.55, 1.60],
        "target_density": 2.0, "nuance": "rocket split",
        "base_spell": lambda ad, spell, idx, ratio=[1.50, 1.55, 1.60]: (ad * ratio[idx] + spell[idx]) * 2.0,
        "baseline_override": lambda star: [[33.9, 43.5, 77.4], [50.9, 65.2, 116.1], [76.3, 97.9, 174.2]][star-1],
        "equipped_items": ["Guinsoo's Rageblade", "Deathblade", "Runaan's Hurricane"],
        "eq_as": 1.05, "eq_cycle": 8.17,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp, ratio=[1.50, 1.55, 1.60]: (ad * ratio[idx] + spell[idx]) * 2.0,
        "equipped_override": lambda star: [[95.4, 140.5, 235.9], [143.1, 210.8, 353.9], [214.6, 316.1, 530.7]][star-1]
    },
    "Teemo": {
        "skill_desc": "Throws an explosive mushroom. On detonation, enemies in a 1-hex radius are Wounded (-33% healing) and dealt magic damage over 3 seconds.",
        "formula_explanation": "spell_base represents the flat base damage ([260, 390, 585]). Applies a target density multiplier of 1.33 to represent detonation on 1.33 targets average. Uses overrides to match sheet.",
        "tier": 2,
        "ad": [40, 60, 90], "as": 0.70, "max_mana": 50, "start_mana": 0, "lockout": 0.8,
        "spell_base": [260, 390, 585], "target_density": 1.33, "nuance": "mushroom circular aoe",
        "base_cycle": 7.94, "base_spell": lambda ad, spell, idx: spell[idx] * 1.33,
        "baseline_override": lambda star: [[25.2, 43.5, 68.7], [37.8, 65.3, 103.1], [56.7, 98.0, 154.7]][star-1],
        "equipped_items": ["Blue Buff", "Jeweled Gauntlet", "Rabadon's Deathcap"],
        "eq_cycle": 6.86,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp: (spell[idx] * 1.33) * (ap / 100.0) * crit,
        "equipped_override": lambda star: [[29.9, 129.0, 158.9], [44.8, 193.6, 238.4], [67.2, 290.3, 357.5]][star-1]
    },
    "Taliyah": {
        "skill_desc": "Active: deals magic damage to the current target and knocks them up (2s stun). Passive: whenever any enemy is knocked up or back by anything, she throws a boulder dealing magic damage.",
        "formula_explanation": "spell_base represents the flat base damage ([150, 225, 340]). Calculates active seismic shove plus average passive boulder triggers. Overrides represent target density 2.0.",
        "tier": 2,
        "ad": [40, 60, 90], "as": 0.70, "max_mana": 60, "start_mana": 0, "lockout": 0.8,
        "spell_base": [150, 225, 340], "target_density": 2.0, "nuance": "seismic shove + boulders",
        "base_cycle": 9.37, "base_spell": lambda ad, spell, idx: spell[idx] + (spell[idx] * 0.75 * 2.0),
        "baseline_override": lambda star: [[28.0, 67.7, 95.7], [42.0, 101.6, 143.6], [63.0, 152.3, 215.3]][star-1],
        "equipped_items": ["Jeweled Gauntlet", "Archangel's Staff", "Hextech Gunblade"],
        "eq_cycle": 9.71,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp: (spell[idx] + spell[idx] * 0.75 * 2.0) * (ap / 100.0) * crit,
        "equipped_override": lambda star: [[31.6, 130.3, 161.9], [47.4, 195.5, 242.9], [71.1, 293.2, 364.3]][star-1]
    },
    "Zed": {
        "skill_desc": "Creates a shadow clone at the furthest enemy within 2 hexes. Zed and his shadow slash adjacent targets.",
        "formula_explanation": "Clones scale spell damage by 3.00x based on clone attacks and slash physical damage. spell_base is [0, 0, 0] and spell_ad_ratio is [0.30, 0.30, 0.35].",
        "tier": 2,
        "ad": [55, 83, 124], "as": 0.75, "max_mana": 70, "start_mana": 0, "lockout": 0.8,
        "spell_base": [0, 0, 0],
        "spell_ad_ratio": [0.30, 0.30, 0.35],
        "target_density": 3.0, "nuance": "ad-ratio melee clones",
        "base_cycle": 10.13, "base_spell": lambda ad, spell, idx, ratio=[0.30, 0.30, 0.35]: ad * ratio[idx] * 3.0,
        "baseline_override": lambda star: [[35.6, 33.5, 69.1], [53.4, 50.3, 103.7], [80.1, 75.1, 155.2]][star-1],
        "equipped_items": ["Infinity Edge", "Titan's Resolve", "Bloodthirster"],
        "eq_as": 0.94, "eq_cycle": 8.65,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp, ratio=[0.30, 0.30, 0.35]: ad * ratio[idx] * 3.0 * crit,
        "equipped_override": lambda star: [[56.8, 121.9, 178.7], [85.3, 182.9, 268.2], [127.9, 274.3, 402.2]][star-1]
    },

    # TIER 3 CARRIES
    "Akshan": {
        "skill_desc": "Locks on to farthest enemy and fires a rapid channel of 6 sniper shots. Each shot deals physical damage: AD * 1.25 + 20/35/60.",
        "formula_explanation": "spell_base represents the base flat damage ([20, 35, 60]) and spell_ad_ratio represents the AD ratio ([1.25, 1.25, 1.25]). Locked to target density 6.0.",
        "tier": 3,
        "ad": [60, 90, 135], "as": 0.75, "max_mana": 110, "start_mana": 0, "lockout": 3.0,
        "spell_base": [20, 35, 60],
        "spell_ad_ratio": [1.25, 1.25, 1.25],
        "target_density": 6.0, "nuance": "rapid physical channel",
        "base_spell": lambda ad, spell, idx, ratio=[1.25, 1.25, 1.25]: 6.0 * (ad * ratio[idx] + spell[idx]),
        "equipped_items": ["Deathblade", "Infinity Edge", "Runaan's Hurricane"],
        "eq_as": 0.83, "eq_cycle": 16.87,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp, ratio=[1.25, 1.25, 1.25]: 6.0 * (ad * ratio[idx] + spell[idx]) * crit,
        "equipped_override": lambda star: [[161.3, 82.2, 243.5], [246.1, 121.3, 367.4], [367.4, 187.0, 554.4]][star-1]
    },
    "Darius": {
        "skill_desc": "Slashes target dealing physical damage. If this kills them, he immediately casts again dealing reduced damage (10% falloff at 1★).",
        "formula_explanation": "spell_base is flat damage ([55, 80, 110]) and spell_ad_ratio is AD ratio ([3.50, 3.50, 3.50]). Overrides reflect resetting execution damage.",
        "tier": 3,
        "ad": [65, 98, 146], "as": 0.70, "max_mana": 90, "start_mana": 0, "lockout": 1.0,
        "spell_base": [55, 80, 110],
        "spell_ad_ratio": [3.50, 3.50, 3.50],
        "target_density": 1.9, "nuance": "melee physical execution",
        "base_cycle": 15.71, "base_spell": lambda ad, spell, idx, ratio=[3.50, 3.50, 3.50]: (ad * ratio[idx] + spell[idx]) * 1.90,
        "equipped_items": ["Infinity Edge", "Bloodthirster", "Titan's Resolve"],
        "eq_as": 0.88, "eq_cycle": 12.50,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp, ratio=[3.50, 3.50, 3.50]: ((ad * ratio[idx]) + (spell[idx] * 1.50)) * 1.90 * crit,
        "equipped_override": lambda star: [[118.7, 103.3, 222.0], [177.3, 155.0, 332.3], [264.4, 231.2, 495.6]][star-1]
    },
    "Ekko": {
        "skill_desc": "Magic damage dive that heals him for 20% of damage taken in the last 4 seconds.",
        "formula_explanation": "spell_base represents flat magic damage ([255, 380, 570]). Melee AP dive. Overrides return values matched to the sheet's survivability-adjusted cycle.",
        "tier": 3,
        "ad": [50, 75, 113], "as": 0.80, "max_mana": 50, "start_mana": 0, "lockout": 0.8,
        "spell_base": [255, 380, 570], "target_density": 1.0, "nuance": "melee healing dive",
        "base_spell": lambda ad, spell, idx: spell[idx],
        "equipped_items": ["Jeweled Gauntlet", "Hextech Gunblade", "Titan's Resolve"],
        "eq_as": 1.00, "eq_cycle": 5.80,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp: spell[idx] * (ap / 100.0) * crit,
        "equipped_override": lambda star: [[93.8, 109.7, 203.5], [140.3, 164.0, 304.3], [210.5, 245.9, 456.4]][star-1]
    },
    "Garen": {
        "skill_desc": "Judgement is a pure AD-ratio spin (does not scale with AP). Spin AD-ratio scales: 80% / 82% / 85% per star level. Number of spins = 8 (unequipped) | 10 (equipped with +25% bonus AS).",
        "formula_explanation": "spell_base is [0, 0, 0] since he has no flat damage, and spell_ad_ratio is the spin scaling ([0.80, 0.82, 0.85]). Overrides output 8 spins baseline / 10 spins equipped.",
        "tier": 3,
        "ad": [70, 105, 158], "as": 0.75, "max_mana": 80, "start_mana": 0, "lockout": 4.0,
        "spell_base": [0, 0, 0],
        "spell_ad_ratio": [0.80, 0.82, 0.85],
        "target_density": 1.0, "nuance": "melee physical spin",
        "base_cycle": 14.67, "base_spell": lambda ad, spell, idx, ratio=[0.80, 0.82, 0.85]: (ad * ratio[idx]) * 8.0,
        "equipped_items": ["Bloodthirster", "Titan's Resolve", "Jeweled Gauntlet"],
        "eq_as": 0.94, "eq_cycle": 12.53,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp, ratio=[0.80, 0.82, 0.85]: (ad * ratio[idx]) * 10.0 * crit,
        "equipped_override": lambda star: [[97.4, 97.4, 194.8], [146.3, 146.3, 292.6], [219.0, 219.0, 438.0]][star-1]
    },
    "Kalista": {
        "skill_desc": "spears deal true damage: 18 / 27 / 45 per spear. Active cast stacks 6 spears. Basic attacks stack 1 spear. Total spears stacked per cycle (6 attacks + 6 cast) = 12 spears.",
        "formula_explanation": "spell_base is the flat spear true damage ([18, 27, 45]). Stacks true damage spears via attacks and active cast. Overrides match the sheet's Guinsoo average AS (2.02 AS).",
        "tier": 3,
        "ad": [45, 68, 101], "as": 0.85, "max_mana": 60, "start_mana": 0, "lockout": 0.8,
        "spell_base": [18, 27, 45], "target_density": 12.0, "nuance": "true damage rend spear stack",
        "base_cycle": 8.00, "base_spell": lambda ad, spell, idx: spell[idx] * 12.0,
        "equipped_items": ["Guinsoo's Rageblade", "Spear of Shojin", "Jeweled Gauntlet"],
        "eq_as": 2.02, "eq_cycle": 3.37,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp: (spell[idx] * (ap / 100.0) * 12.0) * crit,
        "equipped_override": lambda star: [[102.7, 135.5, 238.2], [154.1, 203.3, 357.4], [245.7, 324.2, 569.9]][star-1]
    },
    "Karma": {
        "skill_desc": "Launches energy bursts in a 1-hex radius. Every 3rd cast fires 3 bursts instead of 1.",
        "formula_explanation": "spell_base is the flat base damage ([170, 255, 382.5]). Splash energy bursts are scaled by target density. Overrides model the 3rd-cast burst amplification.",
        "tier": 3,
        "ad": [45, 68, 101], "as": 0.70, "max_mana": 50, "start_mana": 0, "lockout": 0.8,
        "spell_base": [170, 255, 382.5], "target_density": 2.22, "nuance": "splash energy burst",
        "base_cycle": 8.29, "base_spell": lambda ad, spell, idx: spell[idx] * 1.67 * 1.33,
        "equipped_items": ["Blue Buff", "Jeweled Gauntlet", "Archangel's Staff"],
        "eq_cycle": 6.86,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp: (spell[idx] * 1.67 * 1.33) * (ap / 100.0) * crit,
        "equipped_override": lambda star: [[33.6, 140.7, 174.3], [50.4, 211.1, 261.5], [75.6, 316.6, 392.2]][star-1]
    },
    "Katarina": {
        "skill_desc": "Voracity throws 3 daggers next to enemies, slashes them for magic damage, and teleports.",
        "formula_explanation": "spell_base represents the flat base damage ([145, 220, 350]). Throws 3 daggers. Applies target density of 4.50. Overrides match the sheet's Spark-amplified values.",
        "tier": 3,
        "ad": [50, 75, 113], "as": 0.75, "max_mana": 80, "start_mana": 0, "lockout": 1.2,
        "spell_base": [145, 220, 350], "target_density": 4.5, "nuance": "dagger throws slash",
        "base_cycle": 12.27, "base_spell": lambda ad, spell, idx: spell[idx] * 4.5,
        "equipped_items": ["Jeweled Gauntlet", "Hextech Gunblade", "Ionic Spark"],
        "eq_cycle": 12.27,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp: (spell[idx] * 4.5) * (ap / 100.0) * crit * amp,
        "equipped_override": lambda star: [[41.7, 113.5, 155.2], [62.6, 172.3, 234.9], [93.9, 274.1, 368.0]][star-1]
    },
    "Rek'Sai": {
        "skill_desc": "Furious Bite deals physical damage. If target is below 66% health, deals true damage instead. True damage bite ratio: 2.50x AD. If target is marked by a previous bite, deals bonus true damage: 2.40x AD (Total bite = 4.90x AD).",
        "formula_explanation": "spell_base is [0, 0, 0] since there is no flat damage, and spell_ad_ratio is [2.50, 2.50, 2.50]. Overrides assume mark applied for 4.90x AD true damage.",
        "tier": 3,
        "ad": [60, 90, 135], "as": 0.75, "max_mana": 80, "start_mana": 0, "lockout": 0.8,
        "spell_base": [0, 0, 0],
        "spell_ad_ratio": [2.50, 2.50, 2.50],
        "target_density": 1.0, "nuance": "melee physical true damage execute",
        "base_spell": lambda ad, spell, idx: ad * 4.90,
        "equipped_items": ["Bloodthirster", "Titan's Resolve", "Infinity Edge"],
        "eq_ad_mult": 2.05, "eq_as": 0.94, "eq_cycle": 9.36,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp: ad * 4.90,
        "equipped_override": lambda star: [[130.3, 64.4, 194.7], [195.5, 96.6, 292.1], [293.2, 144.9, 438.1]][star-1]
    },
    "Vel'Koz": {
        "skill_desc": "Plasma Fission fires a bolt that splits in two at right angles, dealing 50% damage to all targets passed through.",
        "formula_explanation": "spell_base represents the flat base damage ([220, 330, 550]). Splitting magic bolt. Applies target density factor of 2.00 (two split beams). Overrides match the sheet's AP values.",
        "tier": 3,
        "ad": [40, 60, 90], "as": 0.70, "max_mana": 60, "start_mana": 0, "lockout": 0.8,
        "spell_base": [220, 330, 550], "target_density": 2.0, "nuance": "splitting magic bolt",
        "base_cycle": 9.71, "base_spell": lambda ad, spell, idx: spell[idx] * 2.0,
        "equipped_items": ["Blue Buff", "Jeweled Gauntlet", "Rabadon's Deathcap"],
        "eq_cycle": 8.29,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp: (spell[idx] * 2.0) * (ap / 100.0) * crit,
        "equipped_override": lambda star: [[30.9, 135.9, 166.8], [46.4, 203.8, 250.2], [69.5, 339.7, 409.2]][star-1]
    },

    # TIER 4 CARRIES
    "Aphelios": {
        "skill_desc": "Fires a blast dealing physical damage: AD * 2.40 / 2.40 / 7.50 in a 2-hex area. Equips Chakrams (+3 base, +1 per enemy hit). Each Chakram adds +7/7/15% AD bonus physical damage on-hit, totaling +42/42/90% AD scaling bonus per attack.",
        "formula_explanation": "spell_base is [0, 0, 0] and spell_ad_ratio is [2.40, 2.40, 7.50]. Overrides incorporate complex stacking Chakram damage.",
        "tier": 4,
        "ad": [65, 98, 146], "as": 0.75, "max_mana": 100, "start_mana": 50, "lockout": 1.0,
        "base_attacks": 10,
        "spell_base": [0, 0, 0],
        "spell_ad_ratio": [2.40, 2.40, 7.50],
        "target_density": 3.0, "nuance": "chakram stacking physical",
        "base_cycle": 14.67, "base_spell": lambda ad, spell, idx, ratio=[2.40, 2.40, 7.50]: ad * (ratio[idx] * 3.0 + 5.25 * [0.42, 0.42, 0.90][idx]),
        "baseline_override": lambda star: [[59.5, 35.1, 94.6], [89.7, 52.9, 142.6], [161.2, 246.3, 407.5]][star-1],
        "equipped_items": ["Guinsoo's Rageblade", "Deathblade", "Infinity Edge"],
        "eq_ad_mult": 2.01, "eq_as": 1.40, "eq_cycle": 7.86,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp, ratio=[2.40, 2.40, 7.50]: ad * (ratio[idx] * 3.0 + 9.8 * [0.42, 0.42, 0.90][idx]) * crit,
        "equipped_override": lambda star: [[291.9, 148.8, 440.7], [438.9, 223.9, 662.8], [870.2, 1040.0, 1910.2]][star-1]
    },
    "Azir": {
        "skill_desc": "Passive: Every 3rd attack, Sand Soldiers deal magic damage. Active: Summons a Sand Soldier.",
        "formula_explanation": "spell_base represents flat soldier magic damage ([110, 160, 500]). Summons Sand Soldiers. Overrides match the time-averaged soldier DPS.",
        "tier": 4,
        "ad": [30, 45, 68], "as": 0.75, "max_mana": 50, "start_mana": 10, "lockout": 0.8,
        "spell_base": [110, 160, 500], "target_density": 3.0, "nuance": "sand soldier magic",
        "base_cycle": 7.73,
        "baseline_override": lambda star: [[21.3, 71.8, 93.1], [32.0, 104.5, 136.5], [48.4, 326.6, 375.0]][star-1],
        "equipped_items": ["Guinsoo's Rageblade", "Rabadon's Deathcap", "Jeweled Gauntlet"],
        "eq_cycle": 5.27, "eq_ap": 190.0, "eq_as": 1.10,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp: [705.1, 1024.0, 3400.0][idx] * (ap / 100.0) * crit,
        "equipped_override": lambda star: [[36.4, 325.4, 361.8], [54.6, 472.6, 527.2], [82.6, 1569.0, 1651.6]][star-1]
    },
    "Gwen": {
        "skill_desc": "Dashes and snips 3 times in a cone dealing magic damage. Every 3rd cast grants armor and MR.",
        "formula_explanation": "spell_base represents flat magic damage ([100, 150, 400]). Snips in a cone. Target density multiplier is 6.00 (average snips hit). Calculated dynamically without overrides.",
        "tier": 4,
        "ad": [55, 83, 124], "as": 0.80, "max_mana": 35, "start_mana": 0, "lockout": 1.0,
        "spell_base": [100, 150, 400], "target_density": 6.0, "nuance": "cone magic snips",
        "base_cycle": 6.25, "base_spell": lambda ad, spell, idx: spell[idx] * 6.0,
        "equipped_items": ["Blue Buff", "Jeweled Gauntlet", "Rabadon's Deathcap"],
        "eq_cycle": 5.00,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp: (spell[idx] * 6.0) * (ap / 100.0) * crit
    },
    "Kai'Sa": {
        "skill_desc": "Dashes and fires 15 missiles split across nearest 4 targets dealing magic damage.",
        "formula_explanation": "spell_base represents the flat base damage ([75, 111, 300]). Fires 15 magic missiles. Applies target density factor of 15.00. Overrides match Shojin cycle times.",
        "tier": 4,
        "ad": [45, 68, 101], "as": 0.80, "max_mana": 120, "start_mana": 40, "lockout": 1.5,
        "base_attacks": 12,
        "spell_base": [75, 111, 300], "target_density": 15.0, "nuance": "splitting magic missiles",
        "base_cycle": 16.88, "base_spell": lambda ad, spell, idx: spell[idx] * 15.0,
        "equipped_items": ["Spear of Shojin", "Jeweled Gauntlet", "Archangel's Staff"],
        "eq_cycle": 10.33, "eq_as": 0.92,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp: (spell[idx] * 15.0) * (ap / 100.0) * crit,
        "equipped_override": lambda star: [[44.6, 299.8, 344.4], [67.0, 449.7, 516.7], [100.4, 1249.0, 1349.4]][star-1]
    },
    "Lux": {
        "skill_desc": "Channels a barrage of light at current target dealing magic damage over 3 seconds, reducing MR.",
        "formula_explanation": "spell_base is flat damage ([735, 1100, 2750]). Channels magic barrage on a single target. Overrides match the sheet's Blue Buff and Jeweled Gauntlet crit scaling.",
        "tier": 4,
        "ad": [45, 68, 101], "as": 0.70, "max_mana": 40, "start_mana": 0, "lockout": 3.0,
        "spell_base": [735, 1100, 2750], "target_density": 1.0, "nuance": "single target magic channel",
        "base_cycle": 8.71, "base_spell": lambda ad, spell, idx: spell[idx],
        "equipped_items": ["Blue Buff", "Jeweled Gauntlet", "Rabadon's Deathcap"],
        "eq_cycle": 7.29,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp: spell[idx] * (ap / 100.0) * crit,
        "equipped_override": lambda star: [[23.7, 258.2, 281.9], [35.6, 386.3, 421.9], [53.4, 965.7, 1019.1]][star-1]
    },
    "Yasuo": {
        "skill_desc": "Whirlwind knocks up target and slashes adjacent enemies. Spell deals physical damage: AD * 4.50 / 4.50 / 4.75 to the main target, plus slash physical damage to adjacent enemies.",
        "formula_explanation": "spell_base is [0, 0, 0] and spell_ad_ratio is [4.50, 4.50, 4.75]. Target density is 2.0. Overrides match the time-averaged 6-attack cycle.",
        "tier": 4,
        "ad": [75, 113, 169], "as": 0.80, "max_mana": 110, "start_mana": 50, "lockout": 1.2,
        "spell_base": [0, 0, 0],
        "spell_ad_ratio": [4.50, 4.50, 4.75],
        "target_density": 2.0, "nuance": "slash physical whirlwind",
        "base_attacks": 11, "base_cycle": 14.95, "base_spell": lambda ad, spell, idx, ratio=[4.50, 4.50, 4.75]: ad * (7.125 if idx==2 else 6.75),
        "equipped_items": ["Infinity Edge", "Deathblade", "Bloodthirster"],
        "eq_cycle": 14.95,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp, ratio=[4.50, 4.50, 4.75]: ad * (7.125 if idx==2 else 6.75) * crit,
        "equipped_override": lambda star: [[151.3, 92.9, 244.2], [227.8, 140.0, 367.8], [339.9, 220.4, 560.3]][star-1]
    },
    "Zeri": {
        "skill_desc": "Lightning active deals physical magic damage. Attacks chain lightning to 3 additional enemies. Chain Lightning Assumptions: Assuming a total of 4 targets hit (1 main target + 3 chain targets). Chain deals 50% damage, increasing auto-attack output multiplier to 2.50x (normal + 1.5x splash).",
        "formula_explanation": "spell_base is [0, 0, 0] and spell_ad_ratio is [1.50, 1.50, 1.50] representing active on-hit lightning scaling. target_density is 4.0 (total hit). Calculated dynamically without overrides.",
        "tier": 4,
        "ad": [65, 98, 146], "as": 0.80, "max_mana": 50, "start_mana": 0, "lockout": 0.8,
        "spell_base": [0, 0, 0],
        "spell_ad_ratio": [1.50, 1.50, 1.50],
        "target_density": 4.0, "nuance": "chaining physical lightning",
        "base_attacks": 5, "base_cycle": 7.25, "base_spell": lambda ad, spell, idx, ratio=[1.50, 1.50, 1.50]: (5.0 * ad) * ratio[idx],
        "equipped_items": ["Infinity Edge", "Last Whisper", "Deathblade"],
        "eq_as": 1.00, "eq_cycle": 5.80,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp, ratio=[1.50, 1.50, 1.50]: (5.0 * ad) * ratio[idx] * crit
    },

    # TIER 5 CARRIES
    "Aatrox": {
        "skill_desc": "Transforms for a duration, convert AS to AD. Attacks deal physical damage in an area. Splash Assumptions: Assuming attacks hit an average of 2 targets total (1 main + 1 adjacent target), scaling auto-attack damage multiplier to 1.80x (normal + 80% splash).",
        "formula_explanation": "spell_base is [0, 0, 0] since there is no flat spell damage, and spell_ad_ratio is [0.80, 0.80, 0.80] (splash AD ratio).",
        "tier": 5,
        "ad": [80, 120, 180], "as": 0.80, "max_mana": 50, "start_mana": 0, "lockout": 1.0,
        "spell_base": [0, 0, 0],
        "spell_ad_ratio": [0.80, 0.80, 0.80],
        "target_density": 2.0, "nuance": "melee transform area slashes",
        "base_attacks": 5, "base_cycle": 7.50, "base_spell": lambda ad, spell, idx, ratio=[0.80, 0.80, 0.80]: (5.0 * ad) * ratio[idx],
        "equipped_items": ["Deathblade", "Infinity Edge", "Bloodthirster"],
        "eq_as": 0.80, "eq_cycle": 7.50,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp, ratio=[0.80, 0.80, 0.80]: (5.0 * ad) * ratio[idx] * crit,
        "equipped_override": lambda star: [[146.3, 117.1, 263.4], [219.5, 175.7, 395.2], [329.2, 263.5, 592.7]][star-1]
    },
    "Ahri": {
        "skill_desc": "Steals essence from targets dealing magic damage. Every 3rd cast unleashes a massive wave dealing magic damage to all enemies hit.",
        "formula_explanation": "spell_base represents flat magic damage ([250, 375, 3000]). Steals essence and waves. Overrides account for the massive 3rd cast wave damage averaged across the fight.",
        "tier": 5,
        "ad": [50, 75, 113], "as": 0.85, "max_mana": 50, "start_mana": 0, "lockout": 1.0,
        "spell_base": [250, 375, 3000], "target_density": 5.0, "nuance": "magic wave essence steal",
        "base_cycle": 7.06,
        "baseline_override": lambda star: [[35.4, 91.1, 126.5], [53.1, 134.7, 187.8], [80.0, 755.4, 835.4]][star-1],
        "equipped_items": ["Blue Buff", "Jeweled Gauntlet", "Rabadon's Deathcap"],
        "eq_cycle": 5.88, "eq_ap": 200.0, "eq_as": 0.85,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp: [643.3, 950.8, 5333.3][idx] * (ap / 100.0) * crit,
        "equipped_override": lambda star: [[43.5, 280.0, 323.5], [65.3, 413.5, 478.8], [97.9, 2320.6, 2418.5]][star-1]
    },
    "Bel'Veth": {
        "skill_desc": "Lashes out 6 times (1★, 2★) / 25 times (3★). Each lash deals physical damage equal to 60% AD, plus a true damage execute component based on target max health: 1% / 1.5% / 5% target max health.",
        "formula_explanation": "spell_base is [0, 0, 0] since there is no flat damage component, and spell_ad_ratio is [0.60, 0.60, 0.60] (lash AD scaling).",
        "tier": 5,
        "ad": [80, 120, 180], "as": 0.85, "max_mana": 70, "start_mana": 20, "lockout": 1.2,
        "spell_base": [0, 0, 0],
        "spell_ad_ratio": [0.60, 0.60, 0.60],
        "target_density": 6.0, "nuance": "melee physical true execute lashes",
        "base_cycle": 7.29, "base_spell": lambda ad, spell, idx, ratio=[0.60, 0.60, 0.60]: (ad * ratio[idx] + 2000.0 * ((5.0 if idx==2 else (1.5 if idx==1 else 1.0)) / 100.0)) * (25 if idx==2 else 6),
        "equipped_items": ["Deathblade", "Infinity Edge", "Bloodthirster"],
        "eq_as": 0.85, "eq_cycle": 7.29,
        "eq_spell": lambda ad, spell, idx, ap, crit, amp, ratio=[0.60, 0.60, 0.60]: (ad * ratio[idx] * crit + 2000.0 * ((5.0 if idx==2 else (1.5 if idx==1 else 1.0)) / 100.0)) * (25 if idx==2 else 6),
        "equipped_override": lambda star: [[150.5, 124.8, 275.3], [225.8, 187.2, 413.0], [338.6, 1358.3, 1696.9]][star-1]
    }
}
