# Kai'Sa DPS Calculation Details 👾

This document provides the step-by-step mathematical calculations for Kai'Sa's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 45 | 68 | 101 |
| **Base Spell Damage** | 75 | 111 | 300 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.80 |
| **Max Mana** | 120 |
| **Cast Lockout** | 1.5s |

### 3. Skill Description & Mechanics
*   **Skill**: Dashes and fires 15 missiles split across nearest 4 targets dealing magic damage.
*   **Mechanical Timing & Assumptions**: spell_base represents the flat base damage ([75, 111, 300]). Fires 15 magic missiles. Applies target density factor of 15.00. Overrides match Shojin cycle times.

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(120 / 10)` | 12 | 12 | 12 |
| Cycle Duration | `ATC / AS + Lockout` | `12 / 0.80 + 1.5` | 16.880s | 16.880s | 16.880s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(12 × [AD] × 1.10) / 16.880s` | 32.0 | 48.3 | 71.8 |
| Spell Base (1 Target) | `Spell` | `[75, 111, 300]` | 75.0 | 111.0 | 300.0 |
| Spell Damage | `Spell Base × Missile Hits` (15 missiles total) | `[75.0, 111.0, 300.0] × 15.0` | 1125.0 | 1665.0 | 4500.0 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 16.880s` | 66.6 | 98.6 | 266.6 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **98.6** | **147.0** | **338.4** |

---

## 🧮 Equipped Calculations (Spear of Shojin + Jeweled Gauntlet + Archangel's Staff)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Spear of Shojin** | +15% AD, +25 AP, +5 extra mana per attack |
| **Jeweled Gauntlet** | +20 AP, +15% Crit Chance, +30% Crit Damage |
| **Archangel's Staff** | +70 AP |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AD Mult | `1.00 + [Item AD Percent]` | `1.00 + [AD buffs]` | 1.15× | 1.15× | 1.15× |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([AD Array] × 1.15)` | 52 | 78 | 116 |
| AS Equipped | `AS_base × (1.00 + AS_bonus)` | `AS_average` | 0.92 | 0.92 | 0.92 |
| AP Total | `AP_base + AP_items` | `100 + [AP buffs]` | 215 | 215 | 215 |
| Crit Chance | `Crit_base + Crit_items` | `25% + [Crit buffs]` | 40% | 40% | 40% |
| Crit Damage | `CritDmg_base + CritDmg_items` | `140% + [CritDmg buffs]` | 170% | 170% | 170% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.40 × 0.70` | 1.28 | 1.28 | 1.28 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 15)` | `ceil(120 / 15)` | 8 | 8 | 8 |
| Cycle Duration | `ATC / AS + Lockout` | `8 / 0.92 + 1.5` (Note: cycle duration is 10.330s) | 10.330s | 10.330s | 10.330s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(8 × [Equipped AD] × 1.15 Crit) / 10.330s` | 44.6 | 67.0 | 100.4 |
| Spell Base (1 Target) | `Spell` | `[75, 111, 300]` | 75.0 | 111.0 | 300.0 |
| Spell Damage | `Spell Base × Missile Hits × AP × Crit` | `[75, 111, 300] × 15.00 × 2.15 × 1.28` (Shojin + JG + Archangel) | 3096.0 | 4582.1 | 12384.0 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 10.330s` | 299.8 | 449.7 | 1249.0 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **344.4** | **516.7** | **1349.4** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
