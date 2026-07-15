# Gwen DPS Calculation Details ✂️

This document provides the step-by-step mathematical calculations for Gwen's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 55 | 83 | 124 |
| **Base Spell Damage** | 100 | 150 | 400 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.80 |
| **Max Mana** | 35 |
| **Cast Lockout** | 1.0s |

### 3. Skill Description & Mechanics
*   **Skill**: Dashes and snips 3 times in a cone dealing magic damage. Every 3rd cast grants armor and MR.
*   **Mechanical Timing & Assumptions**: spell_base represents flat magic damage ([100, 150, 400]). Snips in a cone. Target density multiplier is 6.00 (average snips hit). Calculated dynamically without overrides.

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(35 / 10)` | 4 | 4 | 4 |
| Cycle Duration | `ATC / AS + Lockout` | `4 / 0.80 + 1.0` | 6.250s | 6.250s | 6.250s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(4 × [AD] × 1.10) / 6.250s` | 35.2 | 53.1 | 79.4 |
| Spell Base (1 Target) | `Spell` | `[100, 150, 400]` | 100.0 | 150.0 | 400.0 |
| Spell Damage | `Spell Base × Target Density` (6 hits average) | `[100.0, 150.0, 400.0] × 6.0` | 600.0 | 900.0 | 2400.0 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 6.250s` | 96.0 | 144.0 | 384.0 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **131.2** | **197.1** | **463.4** |

---

## 🧮 Equipped Calculations (Blue Buff + Jeweled Gauntlet + Rabadon's Deathcap)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Blue Buff** | +10 AP, -10 Max Mana |
| **Jeweled Gauntlet** | +20 AP, +15% Crit Chance, +30% Crit Damage |
| **Rabadon's Deathcap** | +70 AP |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AD Mult | `1.00 + [Item AD Percent]` | `1.00 + [AD buffs]` | 1.00× | 1.00× | 1.00× |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([AD Array] × 1.00)` | 55 | 83 | 124 |
| AS Equipped | `AS_base × (1.00 + AS_bonus)` | `AS_average` | 0.80 | 0.80 | 0.80 |
| AP Total | `AP_base + AP_items` | `100 + [AP buffs]` | 200 | 200 | 200 |
| Crit Chance | `Crit_base + Crit_items` | `25% + [Crit buffs]` | 40% | 40% | 40% |
| Crit Damage | `CritDmg_base + CritDmg_items` | `140% + [CritDmg buffs]` | 170% | 170% | 170% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.40 × 0.70` | 1.28 | 1.28 | 1.28 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil((Max Mana - 10) / 10)` | `ceil((35 - 10) / 10)` | 3 | 3 | 3 |
| Cycle Duration | `ATC / AS + Lockout` | `3 / 0.80 + 1.0` (Note: cycle duration is 5.000s) | 5.000s | 5.000s | 5.000s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(3 × [Equipped AD] × 1.15 Crit) / 5.000s` | 42.2 | 63.7 | 95.2 |
| Spell Base (1 Target) | `Spell` | `[100, 150, 400]` | 100.0 | 150.0 | 400.0 |
| Spell Damage | `Spell Base × Target Density × AP × Crit` | `[100, 150, 400] × 6.00 × 2.15 × 1.28` | 1651.2 | 2476.8 | 6604.8 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 5.000s` | 307.2 | 460.8 | 1228.8 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **349.4** | **524.5** | **1324.0** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
