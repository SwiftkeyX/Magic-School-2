# Aphelios DPS Calculation Details 🌙

This document provides the step-by-step mathematical calculations for Aphelios's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 65 | 98 | 146 |
| **Base Spell Damage** | 0 | 0 | 0 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.75 |
| **Max Mana** | 100 |
| **Cast Lockout** | 1.0s |

### 3. Skill Description & Mechanics
*   **Skill**: Fires a blast dealing physical damage: AD * 2.40 / 2.40 / 7.50 in a 2-hex area. Equips Chakrams (+3 base, +1 per enemy hit). Each Chakram adds +7/7/15% AD bonus physical damage on-hit, totaling +42/42/90% AD scaling bonus per attack.
*   **Mechanical Timing & Assumptions**: spell_base is [0, 0, 0] and spell_ad_ratio is [2.40, 2.40, 7.50]. Overrides incorporate complex stacking Chakram damage.

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(100 / 10)` | 10 | 10 | 10 |
| Cycle Duration | `ATC / AS + Lockout` | `10 / 0.75 + 1.0` | 14.670s | 14.670s | 14.670s |
| Auto Attack DPS | `((5.25 × AD × [1.42, 1.42, 1.90] + 4.75 × AD) × Crit) / Cycle` | `([12.205, 12.205, 14.725] × [AD] × 1.10) / 14.670s` | 59.5 | 89.7 | 161.2 |
| Spell Base (1 Target) | `Spell` | `[0, 0, 0]` | 0.0 | 0.0 | 0.0 |
| Spell Damage | `AD × Blast Ratio × Targets × Crit` | `[65, 98, 146] × [7.20, 7.20, 22.50] × 1.10` | 514.8 | 776.2 | 3613.5 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 14.670s` | 35.1 | 52.9 | 246.3 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **59.5**<br>*(or 94.6 with Spell)* | **89.7**<br>*(or 142.6 with Spell)* | **161.2**<br>*(or 407.5 with Spell)* |

---

## 🧮 Equipped Calculations (Guinsoo's Rageblade + Deathblade + Infinity Edge)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Guinsoo's Rageblade** | +18% AS |
| **Deathblade** | +66% AD |
| **Infinity Edge** | +35% AD, +35% Crit Chance |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AD Mult | `1.00 + [Item AD Percent]` | `1.00 + [AD buffs]` | 2.01× | 2.01× | 2.01× |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([AD Array] × 2.01)` | 131 | 197 | 293 |
| AS Equipped | `AS_base × (1.00 + AS_bonus)` | `AS_average` | 1.40 | 1.40 | 1.40 |
| AP Total | `AP_base + AP_items` | `100 + [AP buffs]` | 100 | 100 | 100 |
| Crit Chance | `Crit_base + Crit_items` | `25% + [Crit buffs]` | 60% | 60% | 60% |
| Crit Damage | `CritDmg_base + CritDmg_items` | `140% + [CritDmg buffs]` | 140% | 140% | 140% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.60 × 0.40` | 1.24 | 1.24 | 1.24 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(100 / 10)` | 10 | 10 | 10 |
| Cycle Duration | `ATC / AS + Lockout` | `10 / 1.40 + 1.0` (Note: cycle duration is 7.860s) | 7.860s | 7.860s | 7.860s |
| Auto Attack DPS | `((9.8 × AD_equipped × [1.42, 1.42, 1.90] + 0.2 × AD_equipped) × Crit) / Cycle` | `([14.116, 14.116, 18.82] × [Equipped AD] × 1.24 Crit) / 7.860s` | 291.9 | 438.9 | 870.2 |
| Spell Base (1 Target) | `Spell` | `[0, 0, 0]` | 0.0 | 0.0 | 0.0 |
| Spell Damage | `AD_equipped × Blast Ratio × Targets × Crit` | `[131, 197, 293] × [7.20, 7.20, 22.50] × 1.24` | 1169.6 | 1759.6 | 8174.6 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 7.860s` | 148.8 | 223.9 | 1040.0 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **291.9**<br>*(or 440.7 with Spell)* | **438.9**<br>*(or 662.8 with Spell)* | **870.2**<br>*(or 1910.2 with Spell)* |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
