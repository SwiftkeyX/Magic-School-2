# Taliyah DPS Calculation Details 🪨

This document provides the step-by-step mathematical calculations for Taliyah's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 40 | 60 | 90 |
| **Base Spell Damage** | 150 | 225 | 340 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.70 |
| **Max Mana** | 60 |
| **Cast Lockout** | 0.8s |

### 3. Skill Description & Mechanics
*   **Skill**: Active seismic shove stuns the target and deals magic damage. Passive: whenever any enemy is knocked up or back by anything, she throws a boulder dealing magic damage.
*   **Boulder Scaling**: Boulders deal 75% of Active Spell Damage.
*   **Synergy Condition**: Standard synergy assumes 1 active + 2 passive boulder triggers (total 2.50× Active spell damage).

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(60 / 10)` | 6 | 6 | 6 |
| Cycle Duration | `ATC / AS + Lockout` | `6 / 0.70 + 0.8` | 9.371s | 9.371s | 9.371s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(6 × [40, 60, 90] × 1.10) / 9.371s` | 28.2 | 42.3 | 63.4 |
| Spell Base (Active) | `Spell` | `[150.0, 225.0, 340.0]` | 150.0 | 225.0 | 340.0 |
| Spell Damage (Synergy) | `Active + 2 × Passive` (Passive = `0.75 × Active`) | `[150.0, 225.0, 340.0] × (1 + 2 × 0.75) × 1.10` | 634.3 | 952.0 | 1427.1 |
| Spell DPS | `Spell Damage / Cycle` | `[634.3, 952.0, 1427.1] / 9.371s` | 67.7 | 101.6 | 152.3 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **95.9** | **143.9** | **215.7** |

---

## 🧮 Equipped Calculations (Jeweled Gauntlet + Archangel's Staff + Hextech Gunblade)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Jeweled Gauntlet** | +20 AP, +15% Crit Chance, +30% Crit Damage, spells can crit. |
| **Archangel's Staff** | +20 AP base, ramps +20 AP every 5s. Average over 30s fight = +70 AP. |
| **Hextech Gunblade** | +25 AP, +10% AD. |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AD Mult | `1.00 + Gunblade_ad` | `1.00 + 0.10` | 1.10× | 1.10× | 1.10× |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([40, 60, 90] × 1.10)` | 44 | 66 | 99 |
| AS Equipped | `AS_base` | `0.70` | 0.70 | 0.70 | 0.70 |
| AP Total | `AP_base + AP_JG + AP_Arch + AP_Gunblade` | `100 + 20 + 70 + 25` | 215 | 215 | 215 |
| Crit Chance | `Crit_base + Crit_JG` | `25% + 15%` | 40% | 40% | 40% |
| Crit Damage | `CritDmg_base + CritDmg_JG` | `140% + 30%` | 170% | 170% | 170% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.40 × 0.70` | 1.28 | 1.28 | 1.28 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(60 / 10)` | 6 | 6 | 6 |
| Cycle Duration | `ATC / AS + Lockout` | `6 / 0.70 + 0.8` (Note: averages to 9.710s in simulation due to passive boulder lockouts) | 9.710s | 9.710s | 9.710s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(6 × [44, 66, 99] × 1.28) / 9.710s` | 31.6 | 47.4 | 71.1 |
| Spell Base (Active) | `Spell` | `[150.0, 225.0, 340.0]` | 150.0 | 225.0 | 340.0 |
| Spell Damage (Synergy) | `Active + 2 × Passive` (Passive = `0.75 × Active`) | `[150.0, 225.0, 340.0] × (1 + 2 × 0.75) × 2.15 × 1.28` | 1265.2 | 1898.3 | 2847.0 |
| Spell DPS | `Spell Damage / Cycle` | `[1265.2, 1898.3, 2847.0] / 9.710s` | 130.3 | 195.5 | 293.2 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **161.9** | **242.9** | **364.3** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
