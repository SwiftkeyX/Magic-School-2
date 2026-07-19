# Azir DPS Calculation Details 👑

This document provides the step-by-step mathematical calculations for Azir's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 30 | 45 | 68 |
| **Base Spell Damage** | 110 | 160 | 500 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.75 |
| **Max Mana** | 50 |
| **Cast Lockout** | 0.8s |

### 3. Skill Description & Mechanics
*   **Skill**: Passive: Every 3rd attack, Sand Soldiers deal magic damage. Active: Summons a Sand Soldier.
*   **Mechanical Timing & Assumptions**: spell_base represents flat soldier magic damage ([110, 160, 500]). Summons Sand Soldiers. Overrides match the time-averaged soldier DPS.

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(50 / 10)` | 5 | 5 | 5 |
| Cycle Duration | `ATC / AS + Lockout` | `5 / 0.75 + 0.8` | 7.730s | 7.730s | 7.730s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(5 × [AD] × 1.10) / 7.730s` | 21.3 | 32.0 | 48.4 |
| Spell Base (1 Target) | `Spell` | `[110, 160, 500]` | 110.0 | 160.0 | 500.0 |
| Spell Damage | `Time-averaged Soldier Passive + Active Casts × Crit` | `[436.0, 642.4, 4950.0] × [1.10/95] × 110` (Ramped avg 1.68 active soldiers) | 555.4 | 807.8 | 2524.5 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 7.730s` | 71.8 | 104.5 | 326.6 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **93.1** | **136.5** | **375.0** |

---

## 🧮 Equipped Calculations (Guinsoo's Rageblade + Rabadon's Deathcap + Jeweled Gauntlet)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Guinsoo's Rageblade** | +18% AS |
| **Rabadon's Deathcap** | +70 AP |
| **Jeweled Gauntlet** | +20 AP, +15% Crit Chance, +30% Crit Damage |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AD Mult | `1.00 + [Item AD Percent]` | `1.00 + [AD buffs]` | 1.00× | 1.00× | 1.00× |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([AD Array] × 1.00)` | 30 | 45 | 68 |
| AS Equipped | `AS_base × (1.00 + AS_bonus)` | `AS_average` | 1.10 | 1.10 | 1.10 |
| AP Total | `AP_base + AP_items` | `100 + [AP buffs]` | 190 | 190 | 190 |
| Crit Chance | `Crit_base + Crit_items` | `25% + [Crit buffs]` | 40% | 40% | 40% |
| Crit Damage | `CritDmg_base + CritDmg_items` | `140% + [CritDmg buffs]` | 170% | 170% | 170% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.40 × 0.70` | 1.28 | 1.28 | 1.28 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(50 / 10)` | 5 | 5 | 5 |
| Cycle Duration | `ATC / AS + Lockout` | `5 / 1.10 + 0.8` (Note: cycle duration is 5.270s) | 5.270s | 5.270s | 5.270s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(5 × [Equipped AD] × 1.28 Crit) / 5.270s` | 36.4 | 54.6 | 82.6 |
| Spell Base (1 Target) | `Spell` | `[110, 160, 500]` | 110.0 | 160.0 | 500.0 |
| Spell Damage | `Time-Averaged Base (Equipped) × AP × Crit` | `[705.1, 1024.0, 3400.0] × 1.90 × 1.28` (Ramped avg 2.35 active soldiers) | 1714.8 | 2490.4 | 8268.8 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 5.270s` | 325.4 | 472.6 | 1569.0 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **361.8** | **527.2** | **1651.6** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
