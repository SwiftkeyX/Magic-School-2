# Ekko DPS Calculation Details ⏳

This document provides the step-by-step mathematical calculations for Ekko's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 50 | 75 | 113 |
| **Base Spell Damage** | 255 | 380 | 570 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.80 |
| **Max Mana** | 50 |
| **Cast Lockout** | 0.8s |

### 3. Skill Description & Mechanics
*   **Skill**: Magic damage dive that heals him for 20% of damage taken in the last 4 seconds.
*   **Mechanical Timing & Assumptions**: 

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(50 / 10)` | 5 | 5 | 5 |
| Cycle Duration | `ATC / AS + Lockout` | `5 / 0.80 + 0.8` | 7.050s | 7.050s | 7.050s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(5 × [AD] × 1.10) / 7.050s` | 35.5 | 53.2 | 80.1 |
| Spell Base (1 Target) | `Spell` | `[255, 380, 570]` | 255.0 | 380.0 | 570.0 |
| Spell Damage | `Spell Base × Target Density × Crit` | `[255.0, 380.0, 570.0] × 1.0 × 1.10` | 280.5 | 418.0 | 627.0 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 7.050s` | 36.2 | 53.9 | 80.9 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **71.6** | **107.1** | **161.0** |

---

## 🧮 Equipped Calculations (Jeweled Gauntlet + Hextech Gunblade + Titan's Resolve)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Jeweled Gauntlet** | +20 AP, +15% Crit Chance, +30% Crit Damage |
| **Hextech Gunblade** | +10% AD, +25 AP |
| **Titan's Resolve** | +20% AD, +50 AP |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AD Mult | `1.00 + [Item AD Percent]` | `1.00 + [AD buffs]` | 1.30× | 1.30× | 1.30× |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([AD Array] × 1.30)` | 65 | 98 | 147 |
| AS Equipped | `AS_base × (1.00 + AS_bonus)` | `AS_average` | 1.00 | 1.00 | 1.00 |
| AP Total | `AP_base + AP_items` | `100 + [AP buffs]` | 195 | 195 | 195 |
| Crit Chance | `Crit_base + Crit_items` | `25% + [Crit buffs]` | 40% | 40% | 40% |
| Crit Damage | `CritDmg_base + CritDmg_items` | `140% + [CritDmg buffs]` | 170% | 170% | 170% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.40 × 0.70` | 1.28 | 1.28 | 1.28 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(50 / 10)` | 5 | 5 | 5 |
| Cycle Duration | `ATC / AS + Lockout` | `5 / 1.00 + 0.8` (Note: cycle duration is 5.800s) | 5.800s | 5.800s | 5.800s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(5 × [Equipped AD] × 1.15 Crit) / 5.800s` | 93.8 | 140.3 | 210.5 |
| Spell Base (1 Target) | `Spell` | `[255, 380, 570]` | 255.0 | 380.0 | 570.0 |
| Spell Damage | `Spell Base × AP × Crit` | `[255, 380, 570] × 1.95 × 1.28` (Hextech Gunblade + Titan + JG) | 636.5 | 948.5 | 1422.7 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 5.800s` | 109.7 | 164.0 | 245.9 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **203.5** | **304.3** | **456.4** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
