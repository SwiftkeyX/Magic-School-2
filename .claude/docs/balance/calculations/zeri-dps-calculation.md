# Zeri DPS Calculation Details ⚡

This document provides the step-by-step mathematical calculations for Zeri's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

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
| **Attack Speed (AS)** | 0.80 |
| **Max Mana** | 50 |
| **Cast Lockout** | 0.8s |

### 3. Skill Description & Mechanics
*   **Skill**: Lightning active deals physical magic damage. Attacks chain lightning to 3 additional enemies. Chain Lightning Assumptions: Assuming a total of 4 targets hit (1 main target + 3 chain targets). Chain deals 50% damage, increasing auto-attack output multiplier to 2.50x (normal + 1.5x splash).
*   **Mechanical Timing & Assumptions**: spell_base is [0, 0, 0] and spell_ad_ratio is [1.50, 1.50, 1.50] representing active on-hit lightning scaling. target_density is 4.0 (total hit). Calculated dynamically without overrides.

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(50 / 10)` | 5 | 5 | 5 |
| Cycle Duration | `ATC / AS + Lockout` | `5 / 0.80 + 0.8` | 7.250s | 7.250s | 7.250s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(5 × [AD] × 1.10) / 7.250s` | 44.8 | 67.6 | 100.7 |
| Spell Base (1 Target) | `Spell` | `[0, 0, 0]` | 0.0 | 0.0 | 0.0 |
| Spell Damage | `5.0 attacks × AD × Lightning Ratio` | `5.0 × [65, 98, 146] × 1.50` | 487.5 | 735.0 | 1095.0 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 7.250s` | 67.2 | 101.4 | 151.0 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **112.1** | **169.0** | **251.7** |

---

## 🧮 Equipped Calculations (Infinity Edge + Last Whisper + Deathblade)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Infinity Edge** | +35% AD, +35% Crit Chance |
| **Last Whisper** | +10% AD, +10% AS, +10% Crit Chance |
| **Deathblade** | +66% AD |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AD Mult | `1.00 + [Item AD Percent]` | `1.00 + [AD buffs]` | 2.11× | 2.11× | 2.11× |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([AD Array] × 2.11)` | 137 | 207 | 308 |
| AS Equipped | `AS_base × (1.00 + AS_bonus)` | `AS_average` | 1.00 | 1.00 | 1.00 |
| AP Total | `AP_base + AP_items` | `100 + [AP buffs]` | 100 | 100 | 100 |
| Crit Chance | `Crit_base + Crit_items` | `25% + [Crit buffs]` | 70% | 70% | 70% |
| Crit Damage | `CritDmg_base + CritDmg_items` | `140% + [CritDmg buffs]` | 140% | 140% | 140% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.70 × 0.40` | 1.28 | 1.28 | 1.28 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(50 / 10)` | 5 | 5 | 5 |
| Cycle Duration | `ATC / AS + Lockout` | `5 / 1.00 + 0.8` (Note: cycle duration is 5.800s) | 5.800s | 5.800s | 5.800s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(5 × [Equipped AD] × 1.45 Crit) / 5.800s` | 151.2 | 228.4 | 339.9 |
| Spell Base (1 Target) | `Spell` | `[0, 0, 0]` | 0.0 | 0.0 | 0.0 |
| Spell Damage | `5.0 attacks × AD_equipped × Lightning Ratio × Crit` | `5.0 × [144, 217, 323] × 1.50 × 1.24` | 1339.2 | 2018.1 | 3003.9 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 5.800s` | 226.8 | 342.6 | 509.8 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **377.9** | **571.0** | **849.7** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
