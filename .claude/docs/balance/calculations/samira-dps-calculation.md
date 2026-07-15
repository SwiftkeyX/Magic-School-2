# Samira DPS Calculation Details 🌹

This document provides the step-by-step mathematical calculations for Samira's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 45 | 68 | 101 |
| **Spell AD Ratio** | 1.90 | 1.90 | 2.00 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.70 |
| **Max Mana** | 30 |
| **Cast Lockout** | 0.8s |

### 3. Skill Description & Mechanics
*   **Skill**: Shoot at the current target and deal 190% / 190% / 200% AD physical damage. Reduce their Armor by 10 / 15 / 20 for the rest of combat.
*   **Targeting**: Always single-target (1 target density).
*   **Spell AD Scaling**: The spell scales purely with Attack Damage. It does not deal any flat magic/physical damage.

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(30 / 10)` | 3 | 3 | 3 |
| Cycle Duration | `ATC / AS + Lockout` | `3 / 0.70 + 0.8` | 5.086s | 5.086s | 5.086s |
| Auto Attack DPS | `(ATC × AD) / Cycle` | `(3 × [45, 68, 101]) / 5.086s` | 26.5 | 40.1 | 59.6 |
| Spell Base (1 Target) | `AD × Spell AD Ratio` | `[45, 68, 101] × [1.90, 1.90, 2.00]` | 85.5 | 129.2 | 202.0 |
| Spell Damage | `Spell Base × Target Density` | `[85.5, 129.2, 202.0] × 1.0` | 85.5 | 129.2 | 202.0 |
| Spell DPS | `Spell Damage / Cycle` | `[85.5, 129.2, 202.0] / 5.086s` | 16.8 | 25.4 | 39.7 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **43.3** | **65.5** | **99.3** |

---

## 🧮 Equipped Calculations (Blue Buff + Infinity Edge + Last Whisper)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Blue Buff** | −10 Max Mana (→ 20 mana, 2 attacks to cast). |
| **Infinity Edge** | +35% AD, +15% Crit Chance, +10% Crit Damage. Spells can crit. |
| **Last Whisper** | +10% AD, +10% AS, +10% Crit Chance. |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AD Mult | `1.00 + IE_ad + LW_ad` | `1.00 + 0.35 + 0.10` | 1.45× | 1.45× | 1.45× |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([45, 68, 101] × 1.45)` | 65 | 99 | 146 |
| AS Equipped | `AS_base × (1.00 + LW_as)` | `0.70 × 1.10` | 0.77 | 0.77 | 0.77 |
| AP Total | `AP_base + AP_items` | `100 + 0` | 100 | 100 | 100 |
| Crit Chance | `Crit_base + IE_crit + LW_crit` | `25% + 15% + 10%` | 50% | 50% | 50% |
| Crit Damage | `CritDmg_base + IE_critdmg` | `140% + 10%` | 150% | 150% | 150% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.50 × 0.50` | 1.25 | 1.25 | 1.25 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil((Max Mana − BB Mana) / 10)` | `ceil((30 − 10) / 10)` | 2 | 2 | 2 |
| Cycle Duration | `ATC / AS_equipped + Lockout` | `2 / 0.77 + 0.8` | 3.397s | 3.397s | 3.397s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(2 × [65, 99, 146] × 1.25) / 3.397s` | 47.8 | 72.9 | 107.4 |
| Spell Base (1 Target) | `AD_equipped × Spell AD Ratio` | `[65, 99, 146] × [1.90, 1.90, 2.00]` | 123.5 | 188.1 | 292.0 |
| Spell Damage | `Spell Base × AP × Crit` | `[123.5, 188.1, 292.0] × 1.00 × 1.25` | 154.4 | 235.1 | 365.0 |
| Spell DPS | `Spell Damage / Cycle` | `[154.4, 235.1, 365.0] / 3.397s` | 45.4 | 69.2 | 107.4 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **93.2** | **142.1** | **214.8** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
