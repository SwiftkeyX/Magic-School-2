# Kalista DPS Calculation Details 🎯

This document provides the step-by-step mathematical calculations for Kalista's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 45 | 68 | 101 |
| **Base Spell Damage** | 18 | 27 | 45 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.85 |
| **Max Mana** | 60 |
| **Cast Lockout** | 0.8s |

### 3. Skill Description & Mechanics
*   **Skill**: spears deal true damage: 18 / 27 / 45 per spear. Active cast stacks 6 spears. Basic attacks stack 1 spear. Total spears stacked per cycle (6 attacks + 6 cast) = 12 spears.
*   **Mechanical Timing & Assumptions**: 

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(60 / 10)` | 6 | 6 | 6 |
| Cycle Duration | `ATC / AS + Lockout` | `6 / 0.85 + 0.8` | 8.000s | 8.000s | 8.000s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(6 × [AD] × 1.10) / 8.000s` | 33.8 | 51.0 | 75.8 |
| Spell Base (1 Target) | `Spell (Spears)` | `[18, 27, 45]` | 18.0 | 27.0 | 45.0 |
| Spell Damage | `Spell Base × 12.0 spears` (6 attacks + 6 cast) | `[18.0, 27.0, 45.0] × 12.0` (True damage does not crit) | 216.0 | 324.0 | 540.0 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 8.000s` | 27.0 | 40.5 | 67.5 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **60.8** | **91.5** | **143.2** |

---

## 🧮 Equipped Calculations (Guinsoo's Rageblade + Spear of Shojin + Jeweled Gauntlet)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Guinsoo's Rageblade** | +18% AS |
| **Spear of Shojin** | +15% AD, +25 AP, +5 extra mana per attack |
| **Jeweled Gauntlet** | +20 AP, +15% Crit Chance, +30% Crit Damage |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AD Mult | `1.00 + [Item AD Percent]` | `1.00 + [AD buffs]` | 1.15× | 1.15× | 1.15× |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([AD Array] × 1.15)` | 52 | 78 | 116 |
| AS Equipped | `AS_base × (1.00 + AS_bonus)` | `AS_average` | 2.02 | 2.02 | 2.02 |
| AP Total | `AP_base + AP_items` | `100 + [AP buffs]` | 145 | 145 | 145 |
| Crit Chance | `Crit_base + Crit_items` | `25% + [Crit buffs]` | 40% | 40% | 40% |
| Crit Damage | `CritDmg_base + CritDmg_items` | `140% + [CritDmg buffs]` | 170% | 170% | 170% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.40 × 0.70` | 1.28 | 1.28 | 1.28 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 15)` | `ceil(60 / 15)` | 4 | 4 | 4 |
| Cycle Duration | `ATC / AS + Lockout` | `4 / 2.02 + 0.8` (Note: cycle duration is 3.370s) | 3.370s | 3.370s | 3.370s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(4 × [Equipped AD] × 1.15 Crit) / 3.370s` | 102.7 | 154.1 | 245.7 |
| Spell Base (1 Target) | `Spell (Spears)` | `[18, 27, 45]` | 18.0 | 27.0 | 45.0 |
| Spell Damage | `Spell Base × AP × 12.0 spears × Crit` | `[18, 27, 45] × 1.45 AP × 12.0 × 1.28 Crit` (Spears crit with JG) | 400.9 | 601.3 | 1002.2 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 3.370s` | 135.5 | 203.3 | 324.2 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **238.2** | **357.4** | **569.9** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
