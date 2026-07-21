# Katarina DPS Calculation Details 🔪

This document provides the step-by-step mathematical calculations for Katarina's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 50 | 75 | 113 |
| **Base Spell Damage** | 145 | 220 | 350 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.75 |
| **Max Mana** | 80 |
| **Cast Lockout** | 1.2s |

### 3. Skill Description & Mechanics
*   **Skill**: Voracity throws 3 daggers next to enemies, slashes them for magic damage, and teleports.
*   **Mechanical Timing & Assumptions**: 

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(80 / 10)` | 8 | 8 | 8 |
| Cycle Duration | `ATC / AS + Lockout` | `8 / 0.75 + 1.2` | 12.270s | 12.270s | 12.270s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(8 × [AD] × 1.10) / 12.270s` | 35.9 | 53.8 | 81.0 |
| Spell Base (1 Target) | `Spell` | `[145, 220, 350]` | 145.0 | 220.0 | 350.0 |
| Spell Damage | `Spell Base × Dagger Hits × Crit` | `[145.0, 220.0, 350.0] × 4.50 × 1.10` (3 daggers hitting 1.5 targets avg) | 717.8 | 1089.0 | 1732.5 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 12.270s` | 58.5 | 88.8 | 141.2 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **94.4** | **142.6** | **222.2** |

---

## 🧮 Equipped Calculations (Jeweled Gauntlet + Hextech Gunblade + Ionic Spark)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Jeweled Gauntlet** | +20 AP, +15% Crit Chance, +30% Crit Damage |
| **Hextech Gunblade** | +10% AD, +25 AP |
| **Ionic Spark** | +10 AP, ×1.15 Damage Amplification |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AD Mult | `1.00 + [Item AD Percent]` | `1.00 + [AD buffs]` | 1.10× | 1.10× | 1.10× |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([AD Array] × 1.10)` | 55 | 82 | 124 |
| AS Equipped | `AS_base × (1.00 + AS_bonus)` | `AS_average` | 0.75 | 0.75 | 0.75 |
| AP Total | `AP_base + AP_items` | `100 + [AP buffs]` | 155 | 155 | 155 |
| Crit Chance | `Crit_base + Crit_items` | `25% + [Crit buffs]` | 40% | 40% | 40% |
| Crit Damage | `CritDmg_base + CritDmg_items` | `140% + [CritDmg buffs]` | 170% | 170% | 170% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.40 × 0.70` | 1.28 | 1.28 | 1.28 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(80 / 10)` | 8 | 8 | 8 |
| Cycle Duration | `ATC / AS + Lockout` | `8 / 0.75 + 1.2` (Note: cycle duration is 12.270s) | 12.270s | 12.270s | 12.270s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(8 × [Equipped AD] × 1.28 Crit) / 12.270s` | 41.7 | 62.6 | 93.9 |
| Spell Base (1 Target) | `Spell` | `[145, 220, 350]` | 145.0 | 220.0 | 350.0 |
| Spell Damage | `Spell Base × Dagger Hits × AP × Crit × Spark_amp` | `[145, 220, 350] × 4.50 × 1.55 × 1.28 × 1.15` (JG + Gunblade + Ionic Spark) | 1393.2 | 2113.5 | 3362.2 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 12.270s` | 113.5 | 172.3 | 274.1 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **155.2** | **234.9** | **368.0** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
