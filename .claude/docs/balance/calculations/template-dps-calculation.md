# [Champion Name] DPS Calculation Details [Emoji]

This document provides the step-by-step mathematical calculations for [Champion Name]'s baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels.

> **Source of truth**: All base stats are sourced from the **TFT Set 9 Basic data** spreadsheet.
> DPS is calculated from first principles using the formulas below. No external script output is used.

---

## ⚙️ Core Variables & Mechanics

### 1. Base Stats (from TFT Set 9 Basic data)

**Scaling stats**
| Stat | 1★ | 2★ | 3★ |
| :--- | :---: | :---: | :---: |
| **Base AD** | [Value] | [Value] | [Value] |
| **Base Spell Damage** | [Value] | [Value] | [Value] |

**Fixed stats** *(do not scale with star level)*
| Stat | Value |
| :--- | :---: |
| **Attack Speed (AS)** | [Value] |
| **Max Mana** | [Value] |
| **Start Mana** | [Value] |
| **Cast Lockout** | [Value]s |

### 2. Skill Description & Mechanics
*   **Skill**: [Insert summary of skill effects, duration, and damage scaling]
*   **Mana Rules**: [Specify mana generation locks, cast animations, or Shojin interactions]
*   **Special Scaling / Uptime**: [Detail any stacking mechanics, splash target averages, or steroid adjustments]

---

## 🧮 Baseline (Unequipped) Calculations

### Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil((Max Mana - Start Mana) / 10)` | `ceil(([Max] - [Start]) / 10)` | [Value] | [Value] | [Value] |
| Cycle Duration | `ATC / AS + Lockout + [Steroid Duration, if mana locked]` | `[Attacks] / [AS] + [Lockout/Steroid]` | [Value]s | [Value]s | [Value]s |
| [Buff Attacks] | `[Steroid Duration] × AS_buffed` *(if applicable)* | `[Duration] × [AS]` | [Value] | [Value] | [Value] |
| Total Cycle Attacks | `ATC + [Buff Attacks]` | `[Mana Gen] + [Steroid]` | [Value] | [Value] | [Value] |
| Auto Attack DPS | `(Total Cycle Attacks × AD) / Cycle` | `([Attacks] × [AD]) / [Cycle]` | [Value] | [Value] | [Value] |
| Spell Base (1 Target) | [Formula for base spell scaling] | [Numbers plugged in] | [Value] | [Value] | [Value] |
| Spell Damage | `Spell Base × [Targets/Multipliers]` | `[Base] × [Multiplier]` | [Value] | [Value] | [Value] |
| Spell DPS | `Spell Damage / Cycle` | `[Damage] / [Cycle]` | [Value] | [Value] | [Value] |
| **Total DPS** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **[Value]** | **[Value]** | **[Value]** |

---

## 🧮 Equipped Calculations ([Item 1] + [Item 2] + [Item 3])

### 1. Item Stats & Effects
| Item | Effect |
| :--- | :--- |
| **[Item Name 1]** | [AP, AD%, AS%, Crit%, or Passive effects] |
| **[Item Name 2]** | [AP, AD%, AS%, Crit%, or Passive effects] |
| **[Item Name 3]** | [AP, AD%, AS%, Crit%, or Passive effects] |

### 2. Stats & Multipliers

| Stat | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| AD Mult | `1.00 + [Item AD% modifiers]` | `1.00 + [Modifiers]` | [Value] | [Value] | [Value] |
| Equipped AD | `round(AD_base × AD_Mult)` | `round([AD] × [AD Mult])` | [Value] | [Value] | [Value] |
| AS Equipped | `AS_base × (1 + [Item AS% modifiers])` | `[Base AS] × [1 + Modifiers]` | [Value] | [Value] | [Value] |
| Crit Chance | `0.25 + [Item Crit% modifiers]` | `0.25 + [Modifiers]` | [Value] | [Value] | [Value] |
| Crit Damage | `1.40 + [Item Crit Dmg modifiers]` | `1.40 + [Modifiers]` | [Value] | [Value] | [Value] |
| Crit Multiplier | `1 + Crit Chance × (Crit Damage - 1)` | `1 + [Chance] × ([Dmg] - 1)` | [Value] | [Value] | [Value] |

### 3. DPS Calculations

| Step | Formula | Calculation | 1★ | 2★ | 3★ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| ATC | `ceil((Max Mana - Start Mana - [Mana Items]) / [Mana/Attack])` | `ceil(([Max] - [Start] - [Item]) / [Mana])` | [Value] | [Value] | [Value] |
| Spell Base (1 Target) | [Formula utilizing equipped AP/AD] | [Numbers plugged in] | [Value] | [Value] | [Value] |
| **Case 1: 15s Fight** | | | | | |
| Cycle Duration (15s) | `ATC / AS_equipped(15s) + Lockout + [Steroid]` | `[Attacks] / [AS] + [Lockout/Steroid]` | [Value]s | [Value]s | [Value]s |
| [Buff Attacks/Stacks] | [Attacks or stacks accumulated in 15s] | [Numbers plugged in] | [Value] | [Value] | [Value] |
| Total Cycle Attacks | `ATC + [Buff Attacks]` | `[Mana Gen] + [Steroid]` | [Value] | [Value] | [Value] |
| Auto Attack DPS (15s) | `(Total Attacks × AD_equipped × Crit × [Amp]) / Cycle` | `([Attacks] × [AD] × [Crit] × [Amp]) / [Cycle]` | [Value] | [Value] | [Value] |
| Spell Damage (15s) | `Spell Base × AP_mult × Crit × [Stacks/Amplifiers]` | `[Base] × [AP] × [Crit] × [Amp]` | [Value] | [Value] | [Value] |
| Spell DPS (15s) | `Spell Damage / Cycle` | `[Damage] / [Cycle]` | [Value] | [Value] | [Value] |
| **Total DPS (15s)** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **[Value]** | **[Value]** | **[Value]** |
| **Case 2: 30s Fight** | | | | | |
| Cycle Duration (30s) | `ATC / AS_equipped(30s) + Lockout + [Steroid]` | `[Attacks] / [AS] + [Lockout/Steroid]` | [Value]s | [Value]s | [Value]s |
| [Buff Attacks/Stacks] | [Attacks or stacks accumulated in 30s] | [Numbers plugged in] | [Value] | [Value] | [Value] |
| Total Cycle Attacks | `ATC + [Buff Attacks]` | `[Mana Gen] + [Steroid]` | [Value] | [Value] | [Value] |
| Auto Attack DPS (30s) | `(Total Attacks × AD_equipped × Crit × [Amp]) / Cycle` | `([Attacks] × [AD] × [Crit] × [Amp]) / [Cycle]` | [Value] | [Value] | [Value] |
| Spell Damage (30s) | `Spell Base × AP_mult × Crit × [Stacks/Amplifiers]` | `[Base] × [AP] × [Crit] × [Amp]` | [Value] | [Value] | [Value] |
| Spell DPS (30s) | `Spell Damage / Cycle` | `[Damage] / [Cycle]` | [Value] | [Value] | [Value] |
| **Total DPS (30s)** | `Auto DPS + Spell DPS` | `Auto DPS + Spell DPS` | **[Value]** | **[Value]** | **[Value]** |
