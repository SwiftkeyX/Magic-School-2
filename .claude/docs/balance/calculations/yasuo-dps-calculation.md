# Yasuo DPS Calculation Details 🌪️

This document provides the step-by-step mathematical calculations for Yasuo's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 75 | 113 | 169 |
| **Base Spell Damage** | 0 | 0 | 0 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.80 |
| **Max Mana** | 110 |
| **Cast Lockout** | 1.2s |

### 3. Skill Description & Mechanics
*   **Skill**: Whirlwind knocks up target and slashes adjacent enemies. Spell deals physical damage: AD * 4.50 / 4.50 / 4.75 to the main target, plus slash physical damage to adjacent enemies.
*   **Mechanical Timing & Assumptions**: spell_base is [0, 0, 0] and spell_ad_ratio is [4.50, 4.50, 4.75]. Target density is 2.0. Overrides match the time-averaged 6-attack cycle.

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(110 / 10)` | 11 | 11 | 11 |
| Cycle Duration | `ATC / AS + Lockout` | `11 / 0.80 + 1.2` | 14.950s | 14.950s | 14.950s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(11 × [AD] × 1.10) / 14.950s` | 55.2 | 83.1 | 124.3 |
| Spell Base (1 Target) | `Spell` | `[0, 0, 0]` | 0.0 | 0.0 | 0.0 |
| Spell Damage | `AD × (4.50 whirlwind × 1.50 targets + slash)` | `[75, 113, 169] × (6.75 if idx<2 else 7.125)` | 506.2 | 762.8 | 1204.1 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 14.950s` | 33.9 | 51.0 | 80.5 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **89.0** | **134.2** | **204.9** |

---

## 🧮 Equipped Calculations (Infinity Edge + Deathblade + Bloodthirster)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Infinity Edge** | +35% AD, +35% Crit Chance |
| **Deathblade** | +66% AD |
| **Bloodthirster** | +20% AD |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AD Mult | `1.00 + [Item AD Percent]` | `1.00 + [AD buffs]` | 2.21× | 2.21× | 2.21× |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([AD Array] × 2.21)` | 166 | 250 | 373 |
| AS Equipped | `AS_base × (1.00 + AS_bonus)` | `AS_average` | 0.80 | 0.80 | 0.80 |
| AP Total | `AP_base + AP_items` | `100 + [AP buffs]` | 100 | 100 | 100 |
| Crit Chance | `Crit_base + Crit_items` | `25% + [Crit buffs]` | 60% | 60% | 60% |
| Crit Damage | `CritDmg_base + CritDmg_items` | `140% + [CritDmg buffs]` | 140% | 140% | 140% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.60 × 0.40` | 1.24 | 1.24 | 1.24 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(110 / 10)` | 11 | 11 | 11 |
| Cycle Duration | `ATC / AS + Lockout` | `11 / 0.80 + 1.2` (Note: cycle duration is 14.950s) | 14.950s | 14.950s | 14.950s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(11 × [Equipped AD] × 1.35 Crit) / 14.950s` | 151.3 | 227.8 | 339.9 |
| Spell Base (1 Target) | `Spell` | `[0, 0, 0]` | 0.0 | 0.0 | 0.0 |
| Spell Damage | `AD_equipped × (4.50 whirlwind × 1.50 targets + slash) × Crit` | `[166, 250, 373] × (6.75 if idx<2 else 7.125) × 1.24` | 1389.4 | 2092.5 | 3295.4 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 14.950s` | 92.9 | 140.0 | 220.4 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **244.2** | **367.8** | **560.3** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
