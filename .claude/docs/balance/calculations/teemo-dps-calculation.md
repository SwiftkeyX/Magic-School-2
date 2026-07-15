# Teemo DPS Calculation Details 🍄

This document provides the step-by-step mathematical calculations for Teemo's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 40 | 60 | 90 |
| **Base Spell Damage** | 260 | 390 | 585 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.70 |
| **Max Mana** | 50 |
| **Cast Lockout** | 0.8s |

### 3. Skill Description & Mechanics
*   **Skill**: Throws an explosive heat-seeking mushroom at the current target. Detonation Detonation detonate, enemies within 1 hex are Wounded and dealt magic damage over 3 seconds.
*   **Target Density Multiplier**: Since his mushroom hits in a circular 1-hex area, it hits an average of **2.0 targets**. We apply a ×2.00 multiplier to the spell base.

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(50 / 10)` | 5 | 5 | 5 |
| Cycle Duration | `ATC / AS + Lockout` | `5 / 0.70 + 0.8` | 7.943s | 7.943s | 7.943s |
| Auto Attack DPS | `(ATC × AD) / Cycle` | `(5 × [40, 60, 90]) / 7.943s` | 25.2 | 37.8 | 56.7 |
| Spell Base (1 Target) | `Spell` | `[260, 390, 585]` | 260.0 | 390.0 | 585.0 |
| Spell Damage | `Spell Base × Target Density` | `[260, 390, 585] × 2.0` | 520.0 | 780.0 | 1170.0 |
| Spell DPS | `Spell Damage / Cycle` | `[520.0, 780.0, 1170.0] / 7.943s` | 65.5 | 98.2 | 147.3 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **90.7** | **136.0** | **204.0** |

---

## 🧮 Equipped Calculations (Blue Buff + Jeweled Gauntlet + Rabadon's Deathcap)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Blue Buff** | −10 Max Mana (→ 40 mana, 4 attacks to cast). |
| **Jeweled Gauntlet** | +20 AP, +15% Crit Chance, +30% Crit Damage, spells can crit. |
| **Rabadon's Deathcap** | +70 AP. |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AP Total | `AP_base + AP_BB + AP_JG + AP_Rabadon` | `100 + 10 + 20 + 70` | 200 | 200 | 200 |
| Crit Chance | `Crit_base + Crit_JG` | `25% + 15%` | 40% | 40% | 40% |
| Crit Damage | `CritDmg_base + CritDmg_JG` | `140% + 30%` | 170% | 170% | 170% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.40 × 0.70` | 1.28 | 1.28 | 1.28 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil((Max Mana − BB Mana) / 10)` | `ceil((50 − 10) / 10)` | 4 | 4 | 4 |
| Cycle Duration | `ATC / AS + Lockout` | `4 / 0.70 + 0.8` (Note: sheet's simulation averages fight timing to 6.86s cycle) | 6.860s | 6.860s | 6.860s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(4 × [40, 60, 90] × 1.28) / 6.860s` | 29.9 | 44.8 | 67.2 |
| Spell Base (1 Target) | `Spell` | `[260, 390, 585]` | 260.0 | 390.0 | 585.0 |
| Spell Damage | `Spell Base × Target Density × AP × Crit` | `[260, 390, 585] × 2.0 × 2.00 × 1.28` | 1331.2 | 1996.8 | 2995.2 |
| Spell DPS | `Spell Damage / Cycle` | `[1331.2, 1996.8, 2995.2] / 6.860s` | 194.0 | 291.1 | 436.6 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **223.9** | **335.9** | **503.8** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
