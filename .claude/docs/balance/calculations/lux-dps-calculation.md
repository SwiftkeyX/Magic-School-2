# Lux DPS Calculation Details 🪄

This document provides the step-by-step mathematical calculations for Lux's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 45 | 68 | 101 |
| **Base Spell Damage** | 735 | 1100 | 2750 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.70 |
| **Max Mana** | 40 |
| **Cast Lockout** | 3.0s |

### 3. Skill Description & Mechanics
*   **Skill**: Channels a barrage of light at current target dealing magic damage over 3 seconds, reducing MR.
*   **Mechanical Timing & Assumptions**: spell_base is flat damage ([735, 1100, 2750]). Channels magic barrage on a single target. Overrides match the sheet's Blue Buff and Jeweled Gauntlet crit scaling.

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(40 / 10)` | 4 | 4 | 4 |
| Cycle Duration | `ATC / AS + Lockout` | `4 / 0.70 + 3.0` | 8.710s | 8.710s | 8.710s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(4 × [AD] × 1.10) / 8.710s` | 22.7 | 34.4 | 51.0 |
| Spell Base (1 Target) | `Spell` | `[735, 1100, 2750]` | 735.0 | 1100.0 | 2750.0 |
| Spell Damage | `Spell Base × Target Density × Crit` (Single Target) | `[735.0, 1100.0, 2750.0] × 1.0 × 1.10` | 808.5 | 1210.0 | 3025.0 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 8.710s` | 92.8 | 138.9 | 347.3 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **115.5** | **173.3** | **398.3** |

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
| Equipped AD | `round(AD_base × AD_Mult)` | `round([AD Array] × 1.00)` | 45 | 68 | 101 |
| AS Equipped | `AS_base × (1.00 + AS_bonus)` | `AS_average` | 0.70 | 0.70 | 0.70 |
| AP Total | `AP_base + AP_items` | `100 + [AP buffs]` | 200 | 200 | 200 |
| Crit Chance | `Crit_base + Crit_items` | `25% + [Crit buffs]` | 40% | 40% | 40% |
| Crit Damage | `CritDmg_base + CritDmg_items` | `140% + [CritDmg buffs]` | 170% | 170% | 170% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.40 × 0.70` | 1.28 | 1.28 | 1.28 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil((Max Mana - 10) / 10)` | `ceil((40 - 10) / 10)` | 3 | 3 | 3 |
| Cycle Duration | `ATC / AS + Lockout` | `3 / 0.70 + 3.0` (Note: cycle duration is 7.290s) | 7.290s | 7.290s | 7.290s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(3 × [Equipped AD] × 1.28 Crit) / 7.290s` | 23.7 | 35.8 | 53.2 |
| Spell Base (1 Target) | `Spell` | `[735, 1100, 2750]` | 735.0 | 1100.0 | 2750.0 |
| Spell Damage | `Spell Base × AP × Crit` | `[735, 1100, 2750] × 2.00 × 1.28` (Blue Buff + JG + Rabadon) | 1881.6 | 2816.0 | 7040.0 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 7.290s` | 258.1 | 386.3 | 965.7 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **281.8** | **422.1** | **1018.9** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
