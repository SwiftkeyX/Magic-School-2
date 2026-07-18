# Jinx DPS Calculation Details 🚀

This document provides the step-by-step mathematical calculations for Jinx's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 50 | 75 | 113 |
| **Spell AD Ratio** | 1.50 | 1.55 | 1.60 |
| **Spell Flat Damage** | 15 | 20 | 35 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.75 |
| **Max Mana** | 70 |
| **Cast Lockout** | 1.0s |

### 3. Skill Description & Mechanics
*   **Skill**: Fires 5 rockets at random enemies within 2 hexes of the current target. Each rocket deals physical damage: `15 / 20 / 35 (+150% / 155% / 160% AD)`.
*   **Rockets Sum**: Since she fires 5 rockets and we want the total spell damage, the base spell damage per cast is $5 \times (\text{Flat} + \text{AD Ratio} \times \text{AD})$.
*   **Sustained Cast Loop**: Jinx requires 70 mana per cast, which takes 7 attacks. The sustained loop is used for DPS calculations.

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(70 / 10)` | 7 | 7 | 7 |
| Cycle Duration | `ATC / AS + Lockout` | `7 / 0.75 + 1.0` | 10.333s | 10.333s | 10.333s |
| Auto Attack DPS | `(ATC × AD) / Cycle` | `(7 × [50, 75, 113]) / 10.333s` | 33.9 | 50.9 | 76.6 |
| Spell Base (1 Rocket) | `AD × Spell AD Ratio + Spell Flat` | `[50, 75, 113] × [1.50, 1.55, 1.60] + [15, 20, 35]` | 90.0 | 136.25 | 215.8 |
| Spell Damage (5 Rockets) | `Spell Base × 5` | `[90.0, 136.25, 215.8] × 5` | 450.0 | 681.3 | 1079.0 |
| Spell DPS | `Spell Damage / Cycle` | `[450.0, 681.3, 1079.0] / 10.333s` | 43.5 | 65.9 | 104.4 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **77.4** | **116.8** | **181.0** |

---

## 🧮 Equipped Calculations (Guinsoo's Rageblade + Deathblade + Runaan's Hurricane)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Guinsoo's Rageblade** | Ramps AS (average equipped AS is 1.35 [15s] / 1.75 [30s]). See [Guinsoo's Rageblade AS Ramp Calculations](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/guinsoo-dps-calculation.md). |
| **Deathblade** | +66% AD. |
| **Runaan's Hurricane** | +20% AD, basic attacks fire an extra bolt dealing 50% AD (model as `1.50×` total auto damage multiplier). |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AD Mult | `1.00 + DB_ad + Runaan_ad` | `1.00 + 0.66 + 0.20` | 1.86x | 1.86x | 1.86x |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([50, 75, 113] × 1.86)` | 93 | 140 | 210 |
| AS Equipped (15s) | `AS_average(15s)` | `0.96 + 0.0525 × 7.5` | 1.35 | 1.35 | 1.35 |
| AS Equipped (30s) | `AS_average(30s)` | `0.96 + 0.0525 × 15` | 1.75 | 1.75 | 1.75 |
| AP Total | `AP_base + AP_items` | `100 + 0` | 100 | 100 | 100 |
| Crit Chance | `Crit_base` | `25%` | 25% | 25% | 25% |
| Crit Damage | `CritDmg_base` | `140%` | 140% | 140% | 140% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.25 × 0.40` | 1.10 | 1.10 | 1.10 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(70 / 10)` | 7 | 7 | 7 |
| Spell Base (1 Rocket) | `AD_equipped × Spell AD Ratio + Spell Flat` | `[93, 140, 210] × [1.50, 1.55, 1.60] + [15, 20, 35]` | 154.5 | 237.0 | 371.0 |
| Spell Damage (5 Rockets) | `Spell Base × 5 × Crit` | `[154.5, 237.0, 371.0] × 5 × 1.10` | 849.75 | 1303.5 | 2040.5 |
| **Case 1: 15s Fight** | | | | | |
| Cycle Duration (15s) | `ATC / AS_equipped(15s) + Lockout` | `7 / 1.35 + 1.0` | 6.185s | 6.185s | 6.185s |
| Auto Attack DPS (15s) | `(ATC × AD_equipped × Crit × Runaan_amp) / Cycle` | `(7 × [93, 140, 210] × 1.10 × 1.50) / 6.185s` | 173.7 | 261.4 | 392.2 |
| Spell DPS (15s) | `Spell Damage / Cycle` | `849.75 / 6.185s` | 137.4 | 210.8 | 329.9 |
| **Total DPS (15s)** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **311.1** | **472.2** | **722.1** |
| **Case 2: 30s Fight** | | | | | |
| Cycle Duration (30s) | `ATC / AS_equipped(30s) + Lockout` | `7 / 1.75 + 1.0` | 5.000s | 5.000s | 5.000s |
| Auto Attack DPS (30s) | `(ATC × AD_equipped × Crit × Runaan_amp) / Cycle` | `(7 × [93, 140, 210] × 1.10 × 1.50) / 5.000s` | 214.8 | 323.4 | 485.1 |
| Spell DPS (30s) | `Spell Damage / Cycle` | `849.75 / 5.000s` | 170.0 | 260.7 | 408.1 |
| **Total DPS (30s)** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **384.8** | **584.1** | **893.2** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
