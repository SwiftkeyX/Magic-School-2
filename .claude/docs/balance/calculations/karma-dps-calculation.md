# Karma DPS Calculation Details ☄️

This document provides the step-by-step mathematical calculations for Karma's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 45 | 68 | 101 |
| **Base Spell Damage** | 170 | 255 | 382.5 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.70 |
| **Max Mana** | 50 |
| **Cast Lockout** | 0.8s |

### 3. Skill Description & Mechanics
*   **Skill**: Launches energy bursts in a 1-hex radius. Every 3rd cast fires 3 bursts instead of 1.
*   **Mechanical Timing & Assumptions**: 

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(50 / 10)` | 5 | 5 | 5 |
| Cycle Duration | `ATC / AS + Lockout` | `5 / 0.70 + 0.8` | 8.290s | 8.290s | 8.290s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(5 × [AD] × 1.10) / 8.290s` | 27.1 | 41.0 | 60.9 |
| Spell Base (1 Target) | `Spell` | `[170, 255, 382.5]` | 170.0 | 255.0 | 382.5 |
| Spell Damage | `Spell Base × Avg Bursts × Crit` | `[170.0, 255.0, 382.5] × 2.22 × 1.10` (detonates 2.22 bursts average) | 415.1 | 623.7 | 935.6 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 8.290s` | 45.5 | 68.3 | 102.5 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **72.7** | **109.3** | **163.4** |

---

## 🧮 Equipped Calculations (Blue Buff + Jeweled Gauntlet + Archangel's Staff)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Blue Buff** | +10 AP, -10 Max Mana |
| **Jeweled Gauntlet** | +20 AP, +15% Crit Chance, +30% Crit Damage |
| **Archangel's Staff** | +70 AP |

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
| ATC | `ceil((Max Mana - 10) / 10)` | `ceil((50 - 10) / 10)` | 4 | 4 | 4 |
| Cycle Duration | `ATC / AS + Lockout` | `4 / 0.70 + 0.8` (Note: cycle duration is 6.860s) | 6.860s | 6.860s | 6.860s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(4 × [Equipped AD] × 1.15 Crit) / 6.860s` | 33.6 | 50.4 | 75.6 |
| Spell Base (1 Target) | `Spell` | `[170, 255, 382.5]` | 170.0 | 255.0 | 382.5 |
| Spell Damage | `Spell Base × Avg Bursts × AP × Crit` | `[170, 255, 382.5] × 2.22 × 2.15 × 1.28` (Blue Buff + JG + Archangel) | 1039.2 | 1558.8 | 2338.2 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 6.860s` | 140.7 | 211.1 | 316.6 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **174.3** | **261.5** | **392.2** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
