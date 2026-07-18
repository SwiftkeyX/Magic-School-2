---
name: analyze-dps
description: Re-calculate and document a champion's baseline and equipped DPS in the project's standardized table format, using first-principles formulas driven solely by base stats from the TFT Set 9 "Hero Data" sheet.
---

# Champion DPS Analysis Workflow Skill

This skill outlines the process for conducting and documenting champion DPS calculations. The goal is to ensure mathematical precision and consistent documentation layout across all champion DPS pages.

## Core Principles

1. **Source of Truth**: All champion base stats (AD, AS, Max Mana, Start Mana, and 2★/3★ scaling AD) must be sourced solely from the **"TFT Set 9 Basic data"** spreadsheet (`tft-set9`). **Do not read or use** the "TFT Set 9 Champions Analysis" spreadsheet (`tft-set9-analysis`).
2. **No Overrides or Pre-Calculated Tables**: Completely ignore the `baseline_override` and `equipped_override` fields in `champion_db.py`. Do not try to force calculations to match pre-computed comparison summaries. All values must be calculated dynamically from first-principles formulas using the raw stats.
3. **Formula and Calculation Separation**: All math tables must explicitly separate the raw algebraic Formula (variables only) from the Calculation (concrete numbers plugged in).

---

## Step-by-Step Analysis Workflow

### Step 1: Stat Extraction
Locate the champion in the "Hero Data" tab of the TFT Set 9 Google Sheet and retrieve:
* Base AD (1★, 2★, 3★)
* Base Attack Speed (AS)
* Max Mana & Start Mana
* Cast Lockout (seconds)
* Base Spell Damage (1★, 2★, 3★)

### Step 2: Set Up Core Variables
Populate the **Scaling stats** and **Fixed stats** tables under `⚙️ Core Variables & Mechanics`:
* **Scaling stats**: AD, Base Spell Damage (across 1★, 2★, 3★).
* **Fixed stats**: AS, Max Mana, Start Mana, Cast Lockout.
* **Skill Description**: Document special traits or conditional multipliers (e.g. Wound multiplier of 1.30×).

### Step 3: Run Baseline (Unequipped) Calculations
Compute the following steps for 1★, 2★, and 3★ levels:
1. **Attacks to Cast**: $\text{Attacks to Cast} = \left\lceil \dfrac{\text{Max Mana} - \text{Start Mana}}{10} \right\rceil$
2. **Cycle Duration**: $\text{Cycle Duration} = \dfrac{\text{Attacks to Cast}}{AS} + \text{Lockout}$
3. **Auto Attack DPS**: $\text{Auto DPS} = \dfrac{\text{Attacks to Cast} \times AD}{\text{Cycle Duration}}$
4. **Spell Base (1 Target)**: If the spell is not flat (e.g. scales with AD or has hidden multipliers in basic data), show its derivation: $(AD \times \text{Ratio} + \text{Flat}) \times \text{Scaling Factor}$.
5. **Spell Damage**: Multiply `Spell Base` by any conditional multi-target or pierce multipliers (e.g. Wound or Pierce).
6. **Spell DPS**: $\text{Spell DPS} = \dfrac{\text{Spell Damage}}{\text{Cycle Duration}}$
7. **Total DPS**: $\text{Auto DPS} + \text{Spell DPS}$

### Step 4: Run Equipped Calculations
For the standard 3-item configuration:
1. **Determine Item Modifiers**: Compile the total AP, Crit Chance, Crit Damage, and Max Mana reductions.
2. **Derive Stats**:
   * $AP_{total} = AP_{base} + AP_{items}$
   * $\text{Crit Chance} = 25\% + \text{Item Crit Chance}$
   * $\text{Crit Damage} = 140\% + \text{Item Crit Damage}$
   * $\text{Crit Multiplier} = 1 + \text{Crit Chance} \times (\text{Crit Damage} - 1)$
3. **Calculate Cycle and DPS Steps**: Run the Attacks to Cast, Cycle Duration, Auto DPS, Spell Base (1 Target) (scaling AD if applicable), Spell Damage (applying AP, Crit, and Pierce multipliers), Spell DPS, and Total DPS steps utilizing the equipped multipliers and mana reduction values.

### Step 5: Format the Markdown Page
Write the output file under `.claude/docs/balance/calculations/[champion]-dps-calculation.md` using the exact layout defined in [template-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School/.claude/docs/balance/calculations/template-dps-calculation.md). Ensure that non-flat spells always utilize the split `Spell Base` / `Spell Damage` rows in both tables.
