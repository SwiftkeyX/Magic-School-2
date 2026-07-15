# Jhin DPS Calculation Details 🏹

This document provides the step-by-step mathematical calculations for Jhin's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 54 | 81 | 122 |
| **Spell AD Ratio** | 3.00 | 3.00 | 3.44 |
| **Spell Flat Damage** | 60 | 90 | 135 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.70 |
| **Max Mana** | 114 |
| **Cast Lockout** | 1.6s |

### 3. Skill Description & Mechanics
*   **Skill**: In the actual game, Jhin's spell scales with Attack Damage (it deals 300% / 300% / 344% AD plus flat 60 / 90 / 135 physical damage). If we only calculate the flat 60/90/135 damage from the sheet, his spell DPS will be mathematically incorrect and extremely low.
*   **Base Single-Target Factor**: The basic data sheet's base 1★ spell damage ($461.5$) represents the single-target damage of $(AD \times \text{AD Ratio} + \text{Flat}) \times 2.08$ (where $2.08$ is the target density multiplier).
*   **Line Pierce Falloff**: Spell pierces through multiple enemies, dealing reduced damage per target: Target 1 (100%), Target 2 (44% due to 56% falloff). Hitting an average of 2 targets gives a **1.44× pierce multiplier** on top of the base.
*   **Sustained Cast Loop**: Jhin requires a full 114 mana per cast, which takes 12 attacks. The sustained loop is used for DPS calculations.

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(114 / 10)` | 12 | 12 | 12 |
| Cycle Duration | `ATC / AS + Lockout` | `12 / 0.70 + 1.6` | 18.743s | 18.743s | 18.743s |
| Auto Attack DPS | `(ATC × AD) / Cycle` | `(12 × [54, 81, 122]) / 18.743s` | 34.6 | 51.9 | 78.1 |
| Spell Base (1 Target) | `(AD × Spell AD Ratio + Spell Flat) × 2.08` | `([54, 81, 122] × [3.00, 3.00, 3.44] + [60, 90, 135]) × 2.08` | 461.5 | 692.3 | 1042.0 |
| Spell Damage (2 Targets) | `Spell Base × Pierce` | `[461.5, 692.3, 1042.0] × 1.44` | 664.6 | 996.9 | 1500.5 |
| Spell DPS | `Spell Damage / Cycle` | `[664.6, 996.9, 1500.5] / 18.743s` | 35.5 | 53.2 | 80.1 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **70.1** | **105.1** | **158.2** |

---

## 🧮 Equipped Calculations (Deathblade + Infinity Edge + Last Whisper)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Deathblade** | +66% AD |
| **Infinity Edge** | +35% AD, +15% Crit Chance, +10% Crit Damage, spells can crit |
| **Last Whisper** | +10% AD, +10% AS, +10% Crit Chance |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AD Mult | `1.00 + DB_ad + IE_ad + LW_ad` | `1.00 + 0.66 + 0.35 + 0.10` | 2.11× | 2.11× | 2.11× |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([54, 81, 122] × 2.11)` | 114 | 171 | 257 |
| AS Equipped | `AS_base × (1.00 + LW_as)` | `0.70 × 1.10` | 0.77 | 0.77 | 0.77 |
| AP Total | `AP_base + AP_items` | `100 + 0` | 100 | 100 | 100 |
| Crit Chance | `Crit_base + IE_crit + LW_crit` | `25% + 15% + 10%` | 50% | 50% | 50% |
| Crit Damage | `CritDmg_base + IE_critdmg` | `140% + 10%` | 150% | 150% | 150% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.50 × 0.50` | 1.25 | 1.25 | 1.25 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(114 / 10)` | 12 | 12 | 12 |
| Cycle Duration | `ATC / AS_equipped + Lockout` | `12 / 0.77 + 1.6` | 17.184s | 17.184s | 17.184s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(12 × [114, 171, 257] × 1.25) / 17.184s` | 99.5 | 149.3 | 224.3 |
| Spell Base (1 Target) | `(AD_equipped × Spell AD Ratio + Spell Flat) × 2.08` | `([114, 171, 257] × [3.00, 3.00, 3.44] + [60, 90, 135]) × 2.08` | 836.2 | 1254.2 | 1884.5 |
| Spell Damage (2 Targets) | `Spell Base × Pierce × AP × Crit` | `[836.2, 1254.2, 1884.5] × 1.44 × 1.00 × 1.25` | 1505.2 | 2257.6 | 3392.1 |
| Spell DPS | `Spell Damage / Cycle` | `[1505.2, 2257.6, 3392.1] / 17.184s` | 87.6 | 131.4 | 197.4 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **187.1** | **280.7** | **421.7** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
