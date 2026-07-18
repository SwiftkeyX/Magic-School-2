# Rek'Sai DPS Calculation Details 🦈

This document provides the step-by-step mathematical calculations for Rek'Sai's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 60 | 90 | 135 |
| **Base Spell Damage** | 0 | 0 | 0 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.75 |
| **Max Mana** | 80 |
| **Cast Lockout** | 0.8s |

### 3. Skill Description & Mechanics
*   **Skill**: Furious Bite deals physical damage. If target is below 66% health, deals true damage instead. True damage bite ratio: 2.50x AD. If target is marked by a previous bite, deals bonus true damage: 2.40x AD (Total bite = 4.90x AD).
*   **Mechanical Timing & Assumptions**: 

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(80 / 10)` | 8 | 8 | 8 |
| Cycle Duration | `ATC / AS + Lockout` | `8 / 0.75 + 0.8` | 11.467s | 11.467s | 11.467s |
| Auto Attack DPS | `(ATC × AD × Crit) / Cycle` | `(8 × [AD] × 1.10) / 11.467s` | 41.9 | 62.8 | 94.2 |
| Spell Base (1 Target) | `AD × Bite Ratio` | `[60, 90, 135] × 2.50` | 150.0 | 225.0 | 337.5 |
| Spell Damage | `AD × Mark Ratio` (Synergy assumes Bite on Marked target below 66% HP) | `[60, 90, 135] × 4.90` (Bite deals true damage, does not crit) | 294.0 | 441.0 | 661.5 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 11.467s` | 25.6 | 38.5 | 57.7 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **67.5** | **101.2** | **151.9** |

---

## 🧮 Equipped Calculations (Bloodthirster + Titan's Resolve + Infinity Edge)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Bloodthirster** | +20% AD |
| **Titan's Resolve** | +20% AD, +50 AP |
| **Infinity Edge** | +35% AD, +35% Crit Chance |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AD Mult | `1.00 + [Item AD Percent]` | `1.00 + [AD buffs]` | 2.05× | 2.05× | 2.05× |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([AD Array] × 2.05)` | 123 | 184 | 277 |
| AS Equipped | `AS_base × (1.00 + AS_bonus)` | `AS_average` | 0.94 | 0.94 | 0.94 |
| AP Total | `AP_base + AP_items` | `100 + [AP buffs]` | 150 | 150 | 150 |
| Crit Chance | `Crit_base + Crit_items` | `25% + [Crit buffs]` | 60% | 60% | 60% |
| Crit Damage | `CritDmg_base + CritDmg_items` | `140% + [CritDmg buffs]` | 140% | 140% | 140% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.60 × 0.40` | 1.24 | 1.24 | 1.24 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(80 / 10)` | 8 | 8 | 8 |
| Cycle Duration | `ATC / AS + Lockout` | `8 / 0.94 + 0.8` (Note: cycle duration is 9.360s) | 9.360s | 9.360s | 9.360s |
| Auto Attack DPS | `(ATC × AD_equipped × Crit) / Cycle` | `(8 × [Equipped AD] × 1.35 Crit) / 9.360s` | 130.3 | 195.5 | 293.2 |
| Spell Base (1 Target) | `AD × Bite Ratio` | `[123, 184, 277] × 2.50` | 150.0 | 225.0 | 337.5 |
| Spell Damage | `AD_equipped × Mark Ratio` (Bite deals true damage, does not crit) | `[123, 184, 277] × 4.90` (AD mult 2.05: BT + TR + IE) | 602.7 | 906.5 | 1357.3 |
| Spell DPS | `Spell Damage / Cycle` | `[Spell Damage] / 9.360s` | 64.4 | 96.6 | 144.9 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **194.7** | **292.1** | **438.1** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
