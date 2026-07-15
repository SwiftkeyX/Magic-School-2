# Cassiopeia DPS Calculation Details 🐍

This document provides the step-by-step mathematical calculations for Cassiopeia's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 40 | 60 | 90 |
| **Base Spell Damage** | 160 | 240 | 360 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.70 |
| **Max Mana** | 30 |
| **Cast Lockout** | 0.5s |

### 3. Skill Description & Mechanics
*   **Skill**: Deal magic damage to the current target and Wound them for 5 seconds. If already Wounded, deal **+30% bonus magic damage**.
*   **Wound Multiplier**: Her cast cycle is shorter than the wound duration (5s), so every cast after the first hits a Wounded target. We apply a **×1.30 wound multiplier** to all spell damage.

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(30 / 10)` | 3 | 3 | 3 |
| Cycle Duration | `ATC / AS + Lockout` | `3 / 0.70 + 0.5` | 4.786s | 4.786s | 4.786s |
| Auto Attack DPS | `(ATC × AD) / Cycle` | `(3 × [40, 60, 90]) / 4.786s` | 25.1 | 37.6 | 56.4 |
| Spell Base (1 Target) | `Spell` | `[160, 240, 360]` | 160.0 | 240.0 | 360.0 |
| Spell Damage | `Spell Base × Wound` | `[160, 240, 360] × 1.30` | 208.0 | 312.0 | 468.0 |
| Spell DPS | `Spell Damage / Cycle` | `[208.0, 312.0, 468.0] / 4.786s` | 43.5 | 65.2 | 97.8 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **68.6** | **102.8** | **154.2** |

---

## 🧮 Equipped Calculations (Blue Buff + Jeweled Gauntlet + Archangel's Staff)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Blue Buff** | −10 Max Mana (→ 20 mana, 2 attacks to cast). |
| **Jeweled Gauntlet** | +20 AP, +15% Crit Chance, +30% Crit Damage, spells can crit. |
| **Archangel's Staff** | +20 AP base, ramps +20 AP every 5s. Average over 30s fight = +70 AP. |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AP Total (15s) | `AP_base + AP_BB + AP_JG + AP_Arch(15s)` | `100 + 10 + 20 + 40` (Archangel averages +40 AP over 15s) | 170 | 170 | 170 |
| AP Total (30s) | `AP_base + AP_BB + AP_JG + AP_Arch(30s)` | `100 + 10 + 20 + 70` (Archangel averages +70 AP over 30s) | 200 | 200 | 200 |
| Crit Chance | `Crit_base + Crit_JG` | `25% + 15%` | 40% | 40% | 40% |
| Crit Damage | `CritDmg_base + CritDmg_JG` | `140% + 30%` | 170% | 170% | 170% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.40 × 0.70` | 1.28 | 1.28 | 1.28 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil((Max Mana − BB Mana) / 10)` | `ceil((30 − 10) / 10)` | 2 | 2 | 2 |
| Cycle Duration | `ATC / AS + Lockout` | `2 / 0.70 + 0.5` | 3.357s | 3.357s | 3.357s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(2 × [40, 60, 90] × 1.28) / 3.357s` | 30.5 | 45.8 | 68.6 |
| Spell Base (1 Target) | `Spell` | `[160, 240, 360]` | 160.0 | 240.0 | 360.0 |
| **Case 1: 15s Fight (170 AP)** | | | | | |
| Spell Damage (15s) | `Spell Base × Wound × AP × Crit` | `[160, 240, 360] × 1.30 × 1.70 × 1.28` | 452.6 | 678.9 | 1018.4 |
| Spell DPS (15s) | `Spell Damage / Cycle` | `[452.6, 678.9, 1018.4] / 3.357s` | 134.8 | 202.2 | 303.4 |
| **Total DPS (15s)** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **165.3** | **248.0** | **372.0** |
| **Case 2: 30s Fight (200 AP)** | | | | | |
| Spell Damage (30s) | `Spell Base × Wound × AP × Crit` | `[160, 240, 360] × 1.30 × 2.00 × 1.28` | 532.5 | 798.7 | 1198.1 |
| Spell DPS (30s) | `Spell Damage / Cycle` | `[532.5, 798.7, 1198.1] / 3.357s` | 158.6 | 237.9 | 356.9 |
| **Total DPS (30s)** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **189.1** | **283.7** | **425.5** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
