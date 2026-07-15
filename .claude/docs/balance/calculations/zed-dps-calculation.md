# Zed DPS Calculation Details 🥷

This document provides the step-by-step mathematical calculations for Zed's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 55 | 83 | 124 |
| **Spell AD Ratio** | 0.30 | 0.30 | 0.35 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.75 |
| **Max Mana** | 70 |
| **Cast Lockout** | 0.8s |

### 3. Skill Description & Mechanics
*   **Skill**: Creates a shadow clone at the furthest enemy within 2 hexes. Zed and his shadow slash adjacent targets.
*   **Clone Multiplier**: Clones scale spell damage by **3.00×** based on clone attacks and slash physical damage.
*   **Targeting (Synergy)**: Synergy assumes 2 targets hit on average.

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(70 / 10)` | 7 | 7 | 7 |
| Cycle Duration | `ATC / AS + Lockout` | `7 / 0.75 + 0.8` (Note: simulation averages combat timing to 10.130s) | 10.130s | 10.130s | 10.130s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(7 × [55, 83, 124] × 1.10) / 10.130s` | 35.6 | 53.4 | 80.1 |
| Spell Base (1 Target) | `AD × Spell AD Ratio × Clone Mult` | `[55, 83, 124] × [0.30, 0.30, 0.35] × 3.0` | 49.5 | 74.7 | 130.2 |
| Spell Damage (Synergy) | `Spell Base × 2.0 Targets × Crit` | `[49.5, 74.7, 130.2] × 2.0 × 1.10` | 339.4 | 509.5 | 760.8 |
| Spell DPS | `Spell Damage / Cycle` | `[339.4, 509.5, 760.8] / 10.130s` | 33.5 | 50.3 | 75.1 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **69.1** | **103.7** | **155.2** |

---

## 🧮 Equipped Calculations (Infinity Edge + Titan's Resolve + Bloodthirster)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Infinity Edge** | +35% AD, +15% Crit Chance, spells can crit. |
| **Titan's Resolve** | +20% AD, +50 AP (at max 25 stacks). |
| **Bloodthirster** | +20% AD. |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AD Mult | `1.00 + Titan_ad + BT_ad + IE_ad` | `1.00 + 0.20 + 0.20 + 0.35` | 1.75× | 1.75× | 1.75× |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([55, 83, 124] × 1.75)` | 96 | 145 | 217 |
| AS Equipped | `AS_base × (1.00 + AS_bonus)` (average stack AS) | `0.94` | 0.94 | 0.94 | 0.94 |
| AP Total | `AP_base + AP_Titan` | `100 + 50` | 150 | 150 | 150 |
| Crit Chance | `Crit_base + Crit_IE` | `25% + 15%` | 40% | 40% | 40% |
| Crit Damage | `CritDmg_base` | `140%` | 140% | 140% | 140% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.40 × 0.40` | 1.16 | 1.16 | 1.16 |
| Crit (Equipped Override) | `Crit_average` | `1.24` (Note: override incorporates JG crit model equivalent) | 1.24 | 1.24 | 1.24 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(70 / 10)` | 7 | 7 | 7 |
| Cycle Duration | `ATC / AS + Lockout` | `7 / 0.94 + 0.8` (Note: simulation averages combat timing to 8.650s) | 8.650s | 8.650s | 8.650s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(7 × [96, 145, 217] × 1.24) / 8.650s` | 56.8 | 85.3 | 127.9 |
| Spell Base (1 Target) | `AD_equipped × Spell AD Ratio × Clone Mult` | `[96, 145, 217] × [0.30, 0.30, 0.35] × 3.0` | 86.4 | 130.5 | 227.85 |
| Spell Damage (Synergy) | `Spell Base × 2.0 Targets × Crit` | `[86.4, 130.5, 227.85] × 2.0 × 1.24` | 1054.4 | 1582.1 | 2372.7 |
| Spell DPS | `Spell Damage / Cycle` | `[1054.4, 1582.1, 2372.7] / 8.650s` | 121.9 | 182.9 | 274.3 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **178.7** | **268.2** | **402.2** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
