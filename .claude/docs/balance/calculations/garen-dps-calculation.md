# Garen DPS Calculation Details ⚔️

This document provides the step-by-step mathematical calculations for Garen's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 70 | 105 | 158 |
| **Base Spell Damage** | 0 | 0 | 0 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.75 |
| **Max Mana** | 80 |
| **Cast Lockout** | 4.0s |

### 3. Skill Description & Mechanics
*   **Skill**: Judgement is a pure AD-ratio spin (does not scale with AP). Spin AD-ratio scales: 80% / 82% / 85% per star level. Number of spins = 8 (unequipped) | 10 (equipped with +25% bonus AS).
*   **Mechanical Timing & Assumptions**: 

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(80 / 10)` | 8 | 8 | 8 |
| Cycle Duration | `ATC / AS + Lockout` | `8 / 0.75 + 4.0` | 14.670s | 14.670s | 14.670s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(8 × [AD] × 1.10) / 14.670s` | 42.0 | 63.0 | 94.8 |
| Spell Base (1 Target) | `AD × Spin Ratio × Spins` | `[70, 105, 158] × [0.80, 0.82, 0.85] × 8.0` | 448.0 | 688.8 | 1074.4 |
| Spell Damage | `Spell Base × Crit` | `[448.0, 688.8, 1074.4] × 1.10` | 492.8 | 757.7 | 1181.8 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 14.670s` | 33.6 | 51.7 | 80.6 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **75.6** | **114.7** | **175.4** |

---

## 🧮 Equipped Calculations (Bloodthirster + Titan's Resolve + Jeweled Gauntlet)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Bloodthirster** | +20% AD |
| **Titan's Resolve** | +20% AD, +50 AP |
| **Jeweled Gauntlet** | +20 AP, +15% Crit Chance, +30% Crit Damage |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AD Mult | `1.00 + [Item AD Percent]` | `1.00 + [AD buffs]` | 1.40× | 1.40× | 1.40× |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([AD Array] × 1.40)` | 98 | 147 | 221 |
| AS Equipped | `AS_base × (1.00 + AS_bonus)` | `AS_average` | 0.94 | 0.94 | 0.94 |
| AP Total | `AP_base + AP_items` | `100 + [AP buffs]` | 170 | 170 | 170 |
| Crit Chance | `Crit_base + Crit_items` | `25% + [Crit buffs]` | 40% | 40% | 40% |
| Crit Damage | `CritDmg_base + CritDmg_items` | `140% + [CritDmg buffs]` | 170% | 170% | 170% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.40 × 0.70` | 1.28 | 1.28 | 1.28 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(80 / 10)` | 8 | 8 | 8 |
| Cycle Duration | `ATC / AS + Lockout` | `8 / 0.94 + 4.0` (Note: cycle duration is 12.530s) | 12.530s | 12.530s | 12.530s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(8 × [Equipped AD] × 1.28 Crit) / 12.530s` | 80.1 | 120.1 | 180.6 |
| Spell Base (1 Target) | `AD_equipped × Spin Ratio × 8.0` | `[98, 147, 221] × [0.80, 0.82, 0.85] × 8.0` | 627.2 | 964.3 | 1502.8 |
| Spell Damage | `AD_equipped × Spin Ratio × 10.0 × Crit` | `[98, 147, 221] × [0.80, 0.82, 0.85] × 10.0 × 1.28` (10 spins equipped) | 1003.5 | 1545.9 | 2408.0 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 12.530s` | 80.1 | 123.4 | 192.2 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **160.2** | **243.5** | **372.8** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
