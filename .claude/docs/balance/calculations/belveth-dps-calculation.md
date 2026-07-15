# Bel'Veth DPS Calculation Details 🦈

This document provides the step-by-step mathematical calculations for Bel'Veth's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 80 | 120 | 180 |
| **Base Spell Damage** | 0 | 0 | 0 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.85 |
| **Max Mana** | 70 |
| **Cast Lockout** | 1.2s |

### 3. Skill Description & Mechanics
*   **Skill**: Lashes out 6 times (1★, 2★) / 25 times (3★). Each lash deals physical damage equal to 60% AD, plus a true damage execute component based on target max health: 1% / 1.5% / 5% target max health.
*   **Mechanical Timing & Assumptions**: spell_base is [0, 0, 0] since there is no flat damage component, and spell_ad_ratio is [0.60, 0.60, 0.60] (lash AD scaling).

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(70 / 10)` | 7 | 7 | 7 |
| Cycle Duration | `ATC / AS + Lockout` | `7 / 0.85 + 1.2` | 7.290s | 7.290s | 7.290s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(7 × [AD] × 1.10) / 7.290s` | 76.8 | 115.2 | 172.8 |
| Spell Base (1 Target) | `Spell` | `[0, 0, 0]` | 0.0 | 0.0 | 0.0 |
| Spell Damage | `(AD × 0.60 + 2000 HP × Max HP Execute %) × Lashes` | `([80, 120, 180] × 0.60 + 2000 × Execute %) × [6, 6, 25]` | 408.0 | 612.0 | 5200.0 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 7.290s` | 56.0 | 84.0 | 713.3 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **132.8** | **199.2** | **886.1** |

---

## 🧮 Equipped Calculations (Deathblade + Infinity Edge + Bloodthirster)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Deathblade** | +66% AD |
| **Infinity Edge** | +35% AD, +35% Crit Chance |
| **Bloodthirster** | +20% AD |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AD Mult | `1.00 + [Item AD Percent]` | `1.00 + [AD buffs]` | 2.21× | 2.21× | 2.21× |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([AD Array] × 2.21)` | 177 | 265 | 398 |
| AS Equipped | `AS_base × (1.00 + AS_bonus)` | `AS_average` | 0.85 | 0.85 | 0.85 |
| AP Total | `AP_base + AP_items` | `100 + [AP buffs]` | 100 | 100 | 100 |
| Crit Chance | `Crit_base + Crit_items` | `25% + [Crit buffs]` | 60% | 60% | 60% |
| Crit Damage | `CritDmg_base + CritDmg_items` | `140% + [CritDmg buffs]` | 140% | 140% | 140% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.60 × 0.40` | 1.24 | 1.24 | 1.24 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(70 / 10)` | 7 | 7 | 7 |
| Cycle Duration | `ATC / AS + Lockout` | `7 / 0.85 + 1.2` (Note: cycle duration is 7.290s) | 7.290s | 7.290s | 7.290s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(7 × [Equipped AD] × 1.35 Crit) / 7.290s` | 150.5 | 225.8 | 338.6 |
| Spell Base (1 Target) | `Spell` | `[0, 0, 0]` | 0.0 | 0.0 | 0.0 |
| Spell Damage | `(AD_equipped × 0.60 × Crit + 2000 HP × Max HP Execute %) × Lashes` | `([177, 265, 398] × 0.60 × 1.24 + 2000 × Execute %) × [6, 6, 25]` | 909.8 | 1364.7 | 9902.0 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 7.290s` | 124.8 | 187.2 | 1358.3 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **275.3** | **413.0** | **1696.9** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
