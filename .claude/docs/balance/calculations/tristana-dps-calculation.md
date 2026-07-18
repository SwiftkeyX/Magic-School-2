# Tristana DPS Calculation Details 💣

This document provides the step-by-step mathematical calculations for Tristana's baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | 45 | 68 | 101 |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | 0.70 |
| **Max Mana** | 40 |
| **Cast Lockout** | 0.0s |

### 3. Skill Description & Mechanics
*   **Skill**: Gain +70% Attack Speed for 4 seconds. During the duration, attacks explode on impact and deal **60% AD physical damage** to enemies within 1 hex (splash).
*   **Steroid Rotation**: Tristana cannot gain mana during her active steroid. Her cycle consists of a 4-attack mana generation phase followed by a 4-second active steroid phase.
*   **AS Steroid Buff**: She gains AS during her steroid, bringing her unequipped steroid AS to **1.19 AS** (generating 4.76 attacks), and her equipped steroid AS to **2.63 AS** (generating 10.52 attacks).
*   **Splash Density**: Deals splash damage to 1 adjacent target, represented by a **1.00× splash multiplier**.

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(40 / 10)` | 4 | 4 | 4 |
| Cycle Duration | `ATC / AS + Steroid Duration` | `4 / 0.70 + 4.0` | 9.714s | 9.714s | 9.714s |
| Steroid Attacks | `Steroid Duration × (AS × 1.70)` | `4.0 × 1.19` | 4.76 | 4.76 | 4.76 |
| Total Cycle Attacks | `ATC + Steroid Attacks` | `4 + 4.76` | 8.76 | 8.76 | 8.76 |
| Auto Attack DPS | `(Total Cycle Attacks × AD) / Cycle` | `(8.76 × [45, 68, 101]) / 9.714s` | 40.6 | 61.3 | 91.1 |
| Spell Base (1 Target) | `0.60 × AD` | `0.60 × [45, 68, 101]` | 27.0 | 40.8 | 60.6 |
| Spell Damage | `Steroid Attacks × Spell Base` | `4.76 × [27.0, 40.8, 60.6]` | 128.5 | 194.2 | 288.5 |
| Spell DPS | `Spell Damage / Cycle` | `[128.5, 194.2, 288.5] / 9.714s` | 13.2 | 20.0 | 29.7 |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **53.8** | **81.3** | **120.8** |

---

## 🧮 Equipped Calculations (Guinsoo's Rageblade + Last Whisper + Infinity Edge)

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **Guinsoo's Rageblade** | Ramps AS (average equipped AS is 1.26 [15s] / 1.63 [30s], steroid AS is 2.26 [15s] / 2.63 [30s]). See [Guinsoo's Rageblade AS Ramp Calculations](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/guinsoo-dps-calculation.md). |
| **Last Whisper** | +10% AD, +10% AS, +10% Crit Chance. |
| **Infinity Edge** | +35% AD, +15% Crit Chance, spells can crit. |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AD Mult | `1.00 + LW_ad + IE_ad` | `1.00 + 0.10 + 0.35` | 1.45× | 1.45× | 1.45× |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([45, 68, 101] × 1.45)` | 65 | 99 | 146 |
| AS Equipped (15s) | `AS_average(15s)` | `1.26` (averages +7.5 Guinsoo stacks over 15s) | 1.26 | 1.26 | 1.26 |
| AS Buffed (15s) | `AS_equipped(15s) + Steroid` | `1.26 + 1.00` | 2.26 | 2.26 | 2.26 |
| AS Equipped (30s) | `AS_average(30s)` | `1.63` (averages +15 Guinsoo stacks over 30s) | 1.63 | 1.63 | 1.63 |
| AS Buffed (30s) | `AS_equipped(30s) + Steroid` | `1.63 + 1.00` | 2.63 | 2.63 | 2.63 |
| Crit Chance | `Crit_base + LW_crit + IE_crit` | `25% + 10% + 15%` | 50% | 50% | 50% |
| Crit Damage | `CritDmg_base + IE_critdmg` | `140% + 0%` | 140% | 140% | 140% |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage − 1)` | `1 + 0.50 × 0.40` | 1.20 | 1.20 | 1.20 |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil(Max Mana / 10)` | `ceil(40 / 10)` | 4 | 4 | 4 |
| Spell Base (1 Target) | `0.60 × AD_equipped` | `0.60 × [65, 99, 146]` | 39.0 | 59.4 | 87.6 |
| **Case 1: 15s Fight (1.26 average AS)** | | | | | |
| Cycle Duration (15s) | `ATC / AS_equipped(15s) + Steroid Duration` | `4 / 1.26 + 4.0` | 7.175s | 7.175s | 7.175s |
| Steroid Attacks (15s) | `Steroid Duration × AS_buffed(15s)` | `4.0 × 2.26` | 9.04 | 9.04 | 9.04 |
| Total Cycle Attacks (15s) | `ATC + Steroid Attacks` | `4 + 9.04` | 13.04 | 13.04 | 13.04 |
| Auto Attack DPS (15s) | `(Total Attacks × AD_equipped × Crit) / Cycle` | `(13.04 × [65, 99, 146] × 1.20) / 7.175s` | 141.7 | 215.9 | 318.4 |
| Spell Damage (15s) | `Steroid Attacks × Spell Base × Crit` | `9.04 × [39.0, 59.4, 87.6] × 1.20` | 423.1 | 644.4 | 950.3 |
| Spell DPS (15s) | `Spell Damage / Cycle` | `[423.1, 644.4, 950.3] / 7.175s` | 59.0 | 89.8 | 132.4 |
| **Total DPS (15s)** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **200.7** | **305.7** | **450.8** |
| **Case 2: 30s Fight (1.63 average AS)** | | | | | |
| Cycle Duration (30s) | `ATC / AS_equipped(30s) + Steroid Duration` | `4 / 1.63 + 4.0` | 6.454s | 6.454s | 6.454s |
| Steroid Attacks (30s) | `Steroid Duration × AS_buffed(30s)` | `4.0 × 2.63` | 10.52 | 10.52 | 10.52 |
| Total Cycle Attacks (30s) | `ATC + Steroid Attacks` | `4 + 10.52` | 14.52 | 14.52 | 14.52 |
| Auto Attack DPS (30s) | `(Total Attacks × AD_equipped × Crit) / Cycle` | `(14.52 × [65, 99, 146] × 1.20) / 6.454s` | 175.5 | 267.3 | 394.2 |
| Spell Damage (30s) | `Steroid Attacks × Spell Base × Crit` | `10.52 × [39.0, 59.4, 87.6] × 1.20` | 492.3 | 750.3 | 1105.9 |
| Spell DPS (30s) | `Spell Damage / Cycle` | `[492.3, 750.3, 1105.9] / 6.454s` | 76.3 | 116.3 | 171.4 |
| **Total DPS (30s)** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **251.8** | **383.6** | **565.6** |

---

## ⚠️ Script Reference (champion_db.py)

> [!WARNING]
> `champion_db.py` is **not the source of truth** and should not be used to drive calculations. Stats in that file may drift from the sheet. The calculations above are authoritative.
>
> The script file is retained for historical reference only. See the header comment in [champion_db.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/scripts/champion_db.py) for details.
