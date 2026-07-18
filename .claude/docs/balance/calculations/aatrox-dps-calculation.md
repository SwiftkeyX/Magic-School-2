# Aatrox DPS Calculation Details 😈

This document provides the step-by-step mathematical calculations for Aatrox's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

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
| **Attack Speed (AS)** | 0.80 |
| **Max Mana** | 50 |
| **Cast Lockout** | 1.0s |

### 3. Skill Description & Mechanics
*   **Skill**: Transforms for a duration, convert AS to AD. Attacks deal physical damage in an area. Splash Assumptions: Assuming attacks hit an average of 2 targets total (1 main + 1 adjacent target), scaling auto-attack damage multiplier to 1.80x (normal + 80% splash).
*   **Mechanical Timing & Assumptions**: spell_base is [0, 0, 0] since there is no flat spell damage, and spell_ad_ratio is [0.80, 0.80, 0.80] (splash AD ratio).

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(50 / 10)` | 5 | 5 | 5 |
| Cycle Duration | `ATC / AS + Lockout` | `5 / 0.80 + 1.0` | 7.500s | 7.500s | 7.500s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(5 × [AD] × 1.10) / 7.500s` | 53.3 | 80.0 | 120.0 |
| Spell Base (1 Target) | `Spell` | `[0, 0, 0]` | 0.0 | 0.0 | 0.0 |
| Spell Damage | `5.0 attacks × AD × Splash Ratio` | `5.0 × [80, 120, 180] × 0.80` | 320.0 | 480.0 | 720.0 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 7.500s` | 42.7 | 64.0 | 96.0 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **96.0** | **144.0** | **216.0** |

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
| AS Equipped | `AS_base × (1.00 + AS_bonus)` | `AS_average` | 0.80 | 0.80 | 0.80 |
| AP Total | `AP_base + AP_items` | `100 + [AP buffs]` | 100 | 100 | 100 |
| Crit Chance | `Crit_base + Crit_items` | `25% + [Crit buffs]` | 60% | 60% | 60% |
| Crit Damage | `CritDmg_base + CritDmg_items` | `140% + [CritDmg buffs]` | 140% | 140% | 140% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.60 × 0.40` | 1.24 | 1.24 | 1.24 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(50 / 10)` | 5 | 5 | 5 |
| Cycle Duration | `ATC / AS + Lockout` | `5 / 0.80 + 1.0` (Note: cycle duration is 7.500s) | 7.500s | 7.500s | 7.500s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(5 × [Equipped AD] × 1.35 Crit) / 7.500s` | 146.3 | 219.5 | 329.2 |
| Spell Base (1 Target) | `Spell` | `[0, 0, 0]` | 0.0 | 0.0 | 0.0 |
| Spell Damage | `5.0 attacks × AD_equipped × Splash Ratio × Crit` | `5.0 × [177, 265, 398] × 0.80 × 1.24` | 878.2 | 1314.4 | 1974.1 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 7.500s` | 117.1 | 175.7 | 263.5 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **263.4** | **395.2** | **592.7** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
