# Darius DPS Calculation Details 🪓

This document provides the step-by-step mathematical calculations for Darius's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 65 | 98 | 146 |
| **Base Spell Damage** | 55 | 80 | 110 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.70 |
| **Max Mana** | 90 |
| **Cast Lockout** | 1.0s |

### 3. Skill Description & Mechanics
*   **Skill**: Slashes target dealing physical damage. If this kills them, he immediately casts again dealing reduced damage (10% falloff at 1★).
*   **Mechanical Timing & Assumptions**: 

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(90 / 10)` | 9 | 9 | 9 |
| Cycle Duration | `ATC / AS + Lockout` | `9 / 0.70 + 1.0` | 15.710s | 15.710s | 15.710s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(9 × [AD] × 1.10) / 15.710s` | 37.2 | 56.1 | 83.6 |
| Spell Base (1 Target) | `AD × 3.50 + Flat` | `[65, 98, 146] × 3.50 + [55, 80, 110]` | 282.5 | 423.0 | 621.0 |
| Spell Damage | `Spell Base × Reset Mult` | `[282.5, 423.0, 621.0] × 1.90` (Average 1 reset/2 casts) | 536.8 | 803.7 | 1179.9 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 15.710s` | 34.2 | 51.2 | 75.1 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **71.4** | **107.3** | **158.7** |

---

## 🧮 Equipped Calculations (Infinity Edge + Bloodthirster + Titan's Resolve)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Infinity Edge** | +35% AD, +35% Crit Chance |
| **Bloodthirster** | +20% AD |
| **Titan's Resolve** | +20% AD, +50 AP |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AD Mult | `1.00 + [Item AD Percent]` | `1.00 + [AD buffs]` | 1.75× | 1.75× | 1.75× |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([AD Array] × 1.75)` | 114 | 172 | 256 |
| AS Equipped | `AS_base × (1.00 + AS_bonus)` | `AS_average` | 0.88 | 0.88 | 0.88 |
| AP Total | `AP_base + AP_items` | `100 + [AP buffs]` | 150 | 150 | 150 |
| Crit Chance | `Crit_base + Crit_items` | `25% + [Crit buffs]` | 60% | 60% | 60% |
| Crit Damage | `CritDmg_base + CritDmg_items` | `140% + [CritDmg buffs]` | 140% | 140% | 140% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.60 × 0.40` | 1.24 | 1.24 | 1.24 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(90 / 10)` | 9 | 9 | 9 |
| Cycle Duration | `ATC / AS + Lockout` | `9 / 0.88 + 1.0` (Note: cycle duration is 12.500s) | 12.500s | 12.500s | 12.500s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(9 × [Equipped AD] × 1.35 Crit) / 12.500s` | 118.7 | 177.3 | 264.4 |
| Spell Base (1 Target) | `AD × 3.50 + Flat` | `[114, 172, 256] × 3.50 + [55, 80, 110]` | 282.5 | 423.0 | 621.0 |
| Spell Damage | `((AD_equipped × 3.50) + (Spell Base × 1.50)) × 1.90 × Crit` | `(([114, 172, 256] × 3.50) + ([55, 80, 110] × 1.50)) × 1.90 × 1.24` | 1291.3 | 1937.8 | 2889.9 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 12.500s` | 103.3 | 155.0 | 231.2 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **222.0** | **332.3** | **495.6** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
