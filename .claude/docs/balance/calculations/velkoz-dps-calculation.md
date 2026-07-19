# Vel'Koz DPS Calculation Details 👁️

This document provides the step-by-step mathematical calculations for Vel'Koz's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 40 | 60 | 90 |
| **Base Spell Damage** | 220 | 330 | 550 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.70 |
| **Max Mana** | 60 |
| **Cast Lockout** | 0.8s |

### 3. Skill Description & Mechanics
*   **Skill**: Plasma Fission fires a bolt that splits in two at right angles, dealing 50% damage to all targets passed through.
*   **Mechanical Timing & Assumptions**: 

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(60 / 10)` | 6 | 6 | 6 |
| Cycle Duration | `ATC / AS + Lockout` | `6 / 0.70 + 0.8` | 9.710s | 9.710s | 9.710s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(6 × [AD] × 1.10) / 9.710s` | 27.2 | 40.8 | 61.2 |
| Spell Base (1 Target) | `Spell` | `[220, 330, 550]` | 220.0 | 330.0 | 550.0 |
| Spell Damage | `Spell Base × Splits × Crit` | `[220.0, 330.0, 550.0] × 2.00 × 1.10` (splits perpendicularly on first hit) | 484.0 | 726.0 | 1210.0 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 9.710s` | 49.8 | 74.8 | 124.6 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **77.0** | **115.6** | **185.8** |

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
| Equipped AD | `round(AD_base × AD_Mult)` | `round([AD Array] × 1.00)` | 40 | 60 | 90 |
| AS Equipped | `AS_base × (1.00 + AS_bonus)` | `AS_average` | 0.70 | 0.70 | 0.70 |
| AP Total | `AP_base + AP_items` | `100 + [AP buffs]` | 200 | 200 | 200 |
| Crit Chance | `Crit_base + Crit_items` | `25% + [Crit buffs]` | 40% | 40% | 40% |
| Crit Damage | `CritDmg_base + CritDmg_items` | `140% + [CritDmg buffs]` | 170% | 170% | 170% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.40 × 0.70` | 1.28 | 1.28 | 1.28 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil((Max Mana - 10) / 10)` | `ceil((60 - 10) / 10)` | 5 | 5 | 5 |
| Cycle Duration | `ATC / AS + Lockout` | `5 / 0.70 + 0.8` (Note: cycle duration is 8.290s) | 8.290s | 8.290s | 8.290s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(5 × [Equipped AD] × 1.28 Crit) / 8.290s` | 30.9 | 46.4 | 69.5 |
| Spell Base (1 Target) | `Spell` | `[220, 330, 550]` | 220.0 | 330.0 | 550.0 |
| Spell Damage | `Spell Base × Splits × AP × Crit` | `[220, 330, 550] × 2.00 × 2.00 × 1.28` (Blue Buff + JG + Rabadon) | 1126.4 | 1689.6 | 2816.0 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 8.290s` | 135.9 | 203.8 | 339.7 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **166.8** | **250.2** | **409.2** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
