# Ahri DPS Calculation Details 🦊

This document provides the step-by-step mathematical calculations for Ahri's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 50 | 75 | 113 |
| **Base Spell Damage** | 250 | 375 | 3000 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.85 |
| **Max Mana** | 50 |
| **Cast Lockout** | 1.0s |

### 3. Skill Description & Mechanics
*   **Skill**: Steals essence from targets dealing magic damage. Every 3rd cast unleashes a massive wave dealing magic damage to all enemies hit.
*   **Mechanical Timing & Assumptions**: spell_base represents flat magic damage ([250, 375, 3000]). Steals essence and waves. Overrides account for the massive 3rd cast wave damage averaged across the fight.

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(50 / 10)` | 5 | 5 | 5 |
| Cycle Duration | `ATC / AS + Lockout` | `5 / 0.85 + 1.0` | 7.060s | 7.060s | 7.060s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(5 × [AD] × 1.10) / 7.060s` | 35.4 | 53.1 | 80.0 |
| Spell Base (1 Target) | `Spell` | `[250, 375, 3000]` | 250.0 | 375.0 | 3000.0 |
| Spell Damage | `Essence Thief (Cycle Average)` | `[250, 375, 3000]` (Essence thief + wave average overrides) | 643.2 | 951.0 | 5333.1 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 7.060s` | 91.1 | 134.7 | 755.4 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **126.5** | **187.8** | **835.4** |

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
| Equipped AD | `round(AD_base × AD_Mult)` | `round([AD Array] × 1.00)` | 50 | 75 | 113 |
| AS Equipped | `AS_base × (1.00 + AS_bonus)` | `AS_average` | 0.85 | 0.85 | 0.85 |
| AP Total | `AP_base + AP_items` | `100 + [AP buffs]` | 200 | 200 | 200 |
| Crit Chance | `Crit_base + Crit_items` | `25% + [Crit buffs]` | 40% | 40% | 40% |
| Crit Damage | `CritDmg_base + CritDmg_items` | `140% + [CritDmg buffs]` | 170% | 170% | 170% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.40 × 0.70` | 1.28 | 1.28 | 1.28 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil((Max Mana - 10) / 10)` | `ceil((50 - 10) / 10)` | 4 | 4 | 4 |
| Cycle Duration | `ATC / AS + Lockout` | `4 / 0.85 + 1.0` (Note: cycle duration is 5.880s) | 5.880s | 5.880s | 5.880s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(4 × [Equipped AD] × 1.15 Crit) / 5.880s` | 43.5 | 65.3 | 97.9 |
| Spell Base (1 Target) | `Spell` | `[250, 375, 3000]` | 250.0 | 375.0 | 3000.0 |
| Spell Damage | `Spell Base (Equipped Average) × AP × Crit` | `[643.3, 950.8, 5333.3] × 2.00 AP × 1.28 Crit` | 1646.8 | 2434.0 | 13653.2 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 5.880s` | 280.0 | 413.5 | 2320.6 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **323.5** | **478.8** | **2418.5** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
