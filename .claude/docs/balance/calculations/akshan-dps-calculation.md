# Akshan DPS Calculation Details 🦅

This document provides the step-by-step mathematical calculations for Akshan's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 60 | 90 | 135 |
| **Base Spell Damage** | 20 | 35 | 60 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.75 |
| **Max Mana** | 110 |
| **Cast Lockout** | 3.0s |

### 3. Skill Description & Mechanics
*   **Skill**: Locks on to farthest enemy and fires a rapid channel of 6 sniper shots. Each shot deals physical damage: AD * 1.25 + 20/35/60.
*   **Mechanical Timing & Assumptions**: 

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(110 / 10)` | 11 | 11 | 11 |
| Cycle Duration | `ATC / AS + Lockout` | `11 / 0.75 + 3.0` | 17.667s | 17.667s | 17.667s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(11 × [AD] × 1.10) / 17.667s` | 37.4 | 56.0 | 84.1 |
| Spell Base (1 Target) | `AD × 1.25 + Flat` | `[60, 90, 135] × 1.25 + [20, 35, 60]` | 95.0 | 147.5 | 228.8 |
| Spell Damage | `Spell Base × 6.0` (6 shots) | `[95.0, 147.5, 228.75] × 6.0` | 570.0 | 885.0 | 1372.5 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 17.667s` | 32.3 | 50.1 | 77.7 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **69.6** | **106.1** | **161.7** |

---

## 🧮 Equipped Calculations (Deathblade + Infinity Edge + Runaan's Hurricane)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Deathblade** | +66% AD |
| **Infinity Edge** | +35% AD, +35% Crit Chance |
| **Runaan's Hurricane** | +20% AD, ×1.5 Damage Amplification |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AD Mult | `1.00 + [Item AD Percent]` | `1.00 + [AD buffs]` | 2.21× | 2.21× | 2.21× |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([AD Array] × 2.21)` | 133 | 199 | 298 |
| AS Equipped | `AS_base × (1.00 + AS_bonus)` | `AS_average` | 0.83 | 0.83 | 0.83 |
| AP Total | `AP_base + AP_items` | `100 + [AP buffs]` | 100 | 100 | 100 |
| Crit Chance | `Crit_base + Crit_items` | `25% + [Crit buffs]` | 60% | 60% | 60% |
| Crit Damage | `CritDmg_base + CritDmg_items` | `140% + [CritDmg buffs]` | 140% | 140% | 140% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.60 × 0.40` | 1.24 | 1.24 | 1.24 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(110 / 10)` | 11 | 11 | 11 |
| Cycle Duration | `ATC / AS + Lockout` | `11 / 0.83 + 3.0` (Note: cycle duration is 16.870s) | 16.870s | 16.870s | 16.870s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(11 × [Equipped AD] × 1.35 Crit × 1.50 Runaan) / 16.870s` | 161.3 | 246.1 | 367.4 |
| Spell Base (1 Target) | `AD × 1.25 + Flat` | `[133, 199, 298] × 1.25 + [20, 35, 60]` | 95.0 | 147.5 | 228.8 |
| Spell Damage | `Spell Base × 6.0 × Crit` | `[186.25, 283.75, 432.5] × 6.0 × 1.24` | 1385.7 | 2111.1 | 3217.8 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 16.870s` | 82.2 | 121.3 | 187.0 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **243.5** | **367.4** | **554.4** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
