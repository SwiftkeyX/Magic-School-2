# Malzahar DPS Calculation Details 🔮

This document provides the step-by-step mathematical calculations for Malzahar's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 40 | 60 | 90 |
| **Base Spell Damage** | 220 | 330 | 500 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.70 |
| **Max Mana** | 50 |
| **Cast Lockout** | 0.8s |

### 3. Skill Description & Mechanics
*   **Skill**: Spawns two portals dealing magic damage in a rectangular area. Portal hits instantly destroy 50% of active shields on all hit targets.
*   **Target Density Multiplier**: Since his portal hit-area is rectangular, it typically hits an average of **1.50 targets**. We apply a ×1.50 multiplier to the single-target damage to obtain the total spell damage per cast.

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(50 / 10)` | 5 | 5 | 5 |
| Cycle Duration | `ATC / AS + Lockout` | `5 / 0.70 + 0.8` | 7.943s | 7.943s | 7.943s |
| Auto Attack DPS | `(ATC × AD) / Cycle` | `(5 × [40, 60, 90]) / 7.943s` | 25.2 | 37.8 | 56.7 |
| Spell Base (1 Target) | `Spell` | `[220, 330, 500]` | 220.0 | 330.0 | 500.0 |
| Spell Damage | `Spell Base × Target Density` | `[220.0, 330.0, 500.0] × 1.50` | 330.0 | 495.0 | 750.0 |
| Spell DPS | `Spell Damage / Cycle` | `[330.0, 495.0, 750.0] / 7.943s` | 41.5 | 62.3 | 94.4 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **66.8** | **100.1** | **151.1** |

---

## 🧮 Equipped Calculations (Spear of Shojin + Jeweled Gauntlet + Rabadon's Deathcap)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Spear of Shojin** | +15% AD, +15 AP. Unique passive: Attacks grant +5 extra mana (total 15 mana/auto). |
| **Jeweled Gauntlet** | +20 AP, +15% Crit Chance, +30% Crit Damage, spells can crit. |
| **Rabadon's Deathcap** | +70 AP. |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AP Total | `AP_base + AP_Shojin + AP_JG + AP_Rabadon` | `100 + 15 + 20 + 70` | 215 | 215 | 215 |
| Crit Chance | `Crit_base + Crit_JG` | `25% + 15%` | 40% | 40% | 40% |
| Crit Damage | `CritDmg_base + CritDmg_JG` | `140% + 30%` | 170% | 170% | 170% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.40 × 0.70` | 1.28 | 1.28 | 1.28 |
| AD Mult | `1.00 + Shojin_ad` | `1.00 + 0.15` | 1.15× | 1.15× | 1.15× |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([40, 60, 90] × 1.15)` | 46 | 69 | 104 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 15)` | `ceil(50 / 15)` | 4 | 4 | 4 |
| Cycle Duration | `ATC / AS + Lockout` | `4 / 0.70 + 0.8` | 6.514s | 6.514s | 6.514s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(4 × [46, 69, 104] × 1.28) / 6.514s` | 36.2 | 54.2 | 81.7 |
| Spell Base (1 Target) | `Spell` | `[220, 330, 500]` | 220.0 | 330.0 | 500.0 |
| Spell Damage | `Spell Base × Target Density × AP × Crit` | `[220, 330, 500] × 1.50 × 2.15 × 1.28` | 908.2 | 1362.2 | 2064.0 |
| Spell DPS | `Spell Damage / Cycle` | `[908.2, 1362.2, 2064.0] / 6.514s` | 139.4 | 209.1 | 316.8 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **175.6** | **263.3** | **398.5** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
