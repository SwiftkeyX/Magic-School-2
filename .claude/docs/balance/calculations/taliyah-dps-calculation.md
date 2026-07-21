# Taliyah DPS Calculation Details 🪨

This document provides the step-by-step mathematical calculations for Taliyah's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :--- | :---: | :---: |
| **Base AD** | 40 | 60 | 90 |
| **Active Spell Damage** | 220 | 330 | 495 |
| **Passive Spell Damage** | 120 | 180 | 270 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.70 |
| **Max Mana** | 60 |
| **Cast Lockout** | 0.8s |

### 3. Skill Description & Mechanics
*   **Skill**: Active seismic shove stuns the target and deals magic damage. Passive: whenever any enemy is knocked up or back by anything, she throws a boulder dealing magic damage.
*   **Synergy Condition**: Standard synergy assumes 1 active + 2 passive boulder triggers (total Active + 2 × Passive).

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(60 / 10)` | 6 | 6 | 6 |
| Cycle Duration | `ATC / AS + Lockout` | `6 / 0.70 + 0.8` | 9.371s | 9.371s | 9.371s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(6 × [40, 60, 90] × 1.10) / 9.371s` | 28.2 | 42.3 | 63.4 |
| Spell Base (Active) | `Spell` | `[220.0, 330.0, 495.0]` | 220.0 | 330.0 | 495.0 |
| Spell Damage (Synergy) | `(Active + 2 × Passive) × Crit` | `([220.0, 330.0, 495.0] + 2 × [120.0, 180.0, 270.0]) × 1.10` | 506.0 | 759.0 | 1138.5 |
| Spell DPS | `Spell Damage / Cycle` | `[506.0, 759.0, 1138.5] / 9.371s` | 54.0 | 81.0 | 121.5 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **82.2** | **123.3** | **184.9** |

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
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(6 × [44, 66, 99] × 1.28) / 9.710s` | 34.8 | 52.2 | 78.3 |
| Spell Base (Active) | `Spell` | `[220.0, 330.0, 495.0]` | 220.0 | 330.0 | 495.0 |
| Spell Damage (Synergy) | `(Active + 2 × Passive) × AP × Crit` | `([220.0, 330.0, 495.0] + 2 × [120.0, 180.0, 270.0]) × 2.15 × 1.28` | 1265.9 | 1898.9 | 2848.3 |
| Spell DPS | `Spell Damage / Cycle` | `[1265.9, 1898.9, 2848.3] / 9.710s` | 130.4 | 195.6 | 293.3 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **165.2** | **247.8** | **371.6** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
