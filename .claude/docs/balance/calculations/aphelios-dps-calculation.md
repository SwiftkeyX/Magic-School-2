# Aphelios DPS Calculation Details 🌙

This document provides the step-by-step mathematical calculations for Aphelios's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 65 | 98 | 146 |
| **Base Spell Damage** | 0 | 0 | 0 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.75 |
| **Max Mana** | 100 |
| **Cast Lockout** | 1.0s |

### 3. Skill Description & Mechanics
*   **Skill**: Fires a blast dealing physical damage: AD * 2.00 / 2.00 / 2.50 in a 2-hex area. Equips Chakrams (+3 base, +1 per enemy hit). Each Chakram adds +8% AD bonus physical damage on-hit, totaling +48% AD scaling bonus per attack.
*   **Mechanical Timing & Assumptions**: spell_base is [0, 0, 0] and spell_ad_ratio is [2.00, 2.00, 2.50]. Overrides incorporate complex stacking Chakram damage.

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(100 / 10)` | 10 | 10 | 10 |
| Cycle Duration | `ATC / AS + Lockout` | `10 / 0.75 + 1.0` | 14.670s | 14.670s | 14.670s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(10 × [AD] × 1.10) / 14.670s` | 44.3 | 66.8 | 99.5 |
| Spell Base (1 Target) | `Spell` | `[0, 0, 0]` | 0.0 | 0.0 | 0.0 |
| Spell Damage | `AD × (2.00 blast × 3.0 targets + 5.25 Chakrams × 0.48)` | `[65, 98, 146] × (6.00 + 2.52)` | 553.8 | 835.0 | 1462.9 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 14.670s` | 37.8 | 56.9 | 99.7 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **82.1** | **123.7** | **199.2** |

---

## 🧮 Equipped Calculations (Guinsoo's Rageblade + Deathblade + Infinity Edge)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Guinsoo's Rageblade** | +18% AS |
| **Deathblade** | +66% AD |
| **Infinity Edge** | +35% AD, +35% Crit Chance |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AD Mult | `1.00 + [Item AD Percent]` | `1.00 + [AD buffs]` | 2.00× | 2.00× | 2.00× |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([AD Array] × 2.00)` | 130 | 196 | 292 |
| AS Equipped | `AS_base × (1.00 + AS_bonus)` | `AS_average` | 1.40 | 1.40 | 1.40 |
| AP Total | `AP_base + AP_items` | `100 + [AP buffs]` | 100 | 100 | 100 |
| Crit Chance | `Crit_base + Crit_items` | `25% + [Crit buffs]` | 60% | 60% | 60% |
| Crit Damage | `CritDmg_base + CritDmg_items` | `140% + [CritDmg buffs]` | 140% | 140% | 140% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.60 × 0.40` | 1.24 | 1.24 | 1.24 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(100 / 10)` | 10 | 10 | 10 |
| Cycle Duration | `ATC / AS + Lockout` | `10 / 1.40 + 1.0` (Note: cycle duration is 7.860s) | 7.860s | 7.860s | 7.860s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(10 × [Equipped AD] × 1.35 Crit) / 7.860s` | 198.5 | 300.8 | 447.3 |
| Spell Base (1 Target) | `Spell` | `[0, 0, 0]` | 0.0 | 0.0 | 0.0 |
| Spell Damage | `AD_equipped × (2.00 blast × 3.0 targets + 9.80 Chakrams × 0.48) × Crit` | `[130, 196, 292] × (6.00 + 4.704) × 1.24` | 1725.7 | 2601.8 | 3875.9 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 7.860s` | 212.4 | 321.8 | 545.7 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **410.9** | **622.6** | **993.0** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
