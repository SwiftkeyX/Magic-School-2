# TFT Set 9 Tier 3 Carry DPS Analysis (Unified)

This document provides a unified mathematical breakdown of baseline (unequipped) and well-equipped (3-item) DPS scaling for all 3-Gold carry champions in Teamfight Tactics (Set 9).

Putting baseline and itemized calculations in a single document guarantees that both calculations utilize identical, up-to-date mechanical assumptions (AS-scaling lockouts, targeting splits, and cast animation frames).

---

### 📊 Master DPS Summary Tables

### 📘 Table 1: Baseline (Unequipped) DPS Summary
*Consolidated comparison across 1★, 2★, and 3★ star levels with NO items equipped.*

| Champion | Star | Base AD | AS | Auto Attack DPS | Spell DPS | Total DPS |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Akshan** (Single Target) | 1★<br>2★<br>3★ | 60<br>90<br>135 | 0.75 | 37.4<br>56.0<br>84.1 | 32.3<br>50.1<br>77.7 | **69.6**<br>**106.1**<br>**161.7** |
| **Darius** (1 Reset / 2 Casts Avg) | 1★<br>2★<br>3★ | 65<br>98<br>146 | 0.70 | 37.2<br>56.1<br>83.6 | 34.2<br>51.2<br>75.1 | **71.4**<br>**107.3**<br>**158.7** <br>*(1 Target Baseline: **62.6** / **94.2** / **139.6**)* |
| **Ekko** (Single Target) | 1★<br>2★<br>3★ | 50<br>75<br>113 | 0.80 | 35.5<br>53.2<br>80.1 | 36.2<br>53.9<br>80.9 | **71.6**<br>**107.1**<br>**161.0** |
| **Garen** (1 Target Baseline) | 1★<br>2★<br>3★ | 70<br>105<br>158 | 0.75 | 38.2<br>57.3<br>86.2 | 30.5<br>47.0<br>73.2 | **68.7**<br>**104.2**<br>**159.4** <br>*(2 Target Avg: **99.3** / **151.2** / **232.6**)* |
| **Kalista** (Single Target, 12 stack Rend) | 1★<br>2★<br>3★ | 45<br>68<br>101 | 0.85 | 33.8<br>51.0<br>75.8 | 27.0<br>40.5<br>67.5 | **60.8**<br>**91.5**<br>**143.2** |
| **Karma** (1.33 Targets Avg) | 1★<br>2★<br>3★ | 45<br>68<br>101 | 0.70 | 27.1<br>41.0<br>60.9 | 45.5<br>68.3<br>102.5 | **72.7**<br>**109.3**<br>**163.4** <br>*(1 Target Baseline: **61.3** / **92.4** / **138.0**)* |
| **Katarina** (1.5 Targets / 4.5 hits Avg) | 1★<br>2★<br>3★ | 50<br>75<br>113 | 0.75 | 32.6<br>48.9<br>73.7 | 53.2<br>80.7<br>128.3 | **85.8**<br>**129.6**<br>**202.0** <br>*(1 Target Baseline: **70.4** / **105.6** / **158.7**)* |
| **Rek'Sai** (Target > 66% HP) | 1★<br>2★<br>3★ | 60<br>90<br>135 | 0.75 | 41.9<br>62.8<br>94.2 | 25.6<br>38.5<br>57.7 | **67.5**<br>**101.2**<br>**151.9** |
| **Vel'Koz** (2 Targets Avg) | 1★<br>2★<br>3★ | 40<br>60<br>90 | 0.70 | 24.7<br>37.1<br>55.6 | 45.3<br>67.9<br>113.3 | **70.0**<br>**105.0**<br>**168.9** <br>*(1 Target Baseline: **49.1** / **73.6** / **110.4**)* |

### ⚔️ Table 2: Well-Equipped (3-Item) DPS Summary
*Consolidated comparison across 1★, 2★, and 3★ star levels with 3 core optimal items equipped. Shows time-averaged stats and DPS (no ramping slashes).*

| Champion | Star | AD | AS | Auto Attack DPS | Spell DPS | Total DPS |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Akshan** (Single Target) | 1★<br>2★<br>3★ | 133<br>200<br>300 | 0.83 | 161.3<br>246.1<br>367.4 | 82.2<br>121.3<br>187.0 | **243.5**<br>**367.4**<br>**554.4** |
| **Darius** (1 Reset / 2 Casts Avg) | 1★<br>2★<br>3★ | 133<br>200<br>300 | 0.88 | 118.7<br>177.3<br>264.4 | 103.3<br>155.0<br>231.2 | **222.0**<br>**332.3**<br>**495.6** |
| **Ekko** (Single Target) | 1★<br>2★<br>3★ | 85<br>128<br>191 | 1.00 | 93.8<br>140.3<br>210.5 | 109.7<br>164.0<br>245.9 | **203.5**<br>**304.3**<br>**456.4** |
| **Garen** (1 Target Typical) | 1★<br>2★<br>3★ | 119<br>179<br>268 | 0.94 | 97.4<br>146.3<br>219.0 | 97.4<br>146.3<br>219.0 | **194.8**<br>**292.6**<br>**438.0** |
| **Kalista** (Single Target, 12 stack Rend) | 1★<br>2★<br>3★ | 45<br>68<br>101 | 2.02 | 102.7<br>154.1<br>245.7 | 135.5<br>203.3<br>324.2 | **238.2**<br>**357.4**<br>**569.9** |
| **Karma** (1.33 Targets Avg) | 1★<br>2★<br>3★ | 45<br>68<br>101 | 0.70 | 33.6<br>50.4<br>75.6 | 140.7<br>211.1<br>316.6 | **174.3**<br>**261.5**<br>**392.2** |
| **Katarina** (1.5 Targets / 4.5 hits Avg) | 1★<br>2★<br>3★ | 50<br>75<br>113 | 0.75 | 41.7<br>62.6<br>93.9 | 113.5<br>172.3<br>274.1 | **155.2**<br>**234.9**<br>**368.0** |
| **Rek'Sai** (Target < 66% HP, Marked) | 1★<br>2★<br>3★ | 123<br>185<br>277 | 0.94 | 130.3<br>195.5<br>293.2 | 64.4<br>96.6<br>144.9 | **194.7**<br>**292.1**<br>**438.1** |
| **Vel'Koz** (2 Targets Avg) | 1★<br>2★<br>3★ | 40<br>60<br>90 | 0.70 | 30.9<br>46.4<br>69.5 | 135.9<br>203.8<br>339.7 | **166.8**<br>**250.2**<br>**409.2** |

---

## 📖 Glossary & Formula Index

*   **AD (Attack Damage)**: The physical damage dealt by a basic auto-attack. AD scales by 1.5x per star level (2★ = 1.5x, 3★ = 2.25x).
*   **AS (Attack Speed)**: The rate of basic attacks per second. Attack Speed remains flat across star levels.
*   **AP (Ability Power)**: The scaling multiplier applied to base spell damage (base is 100 AP / 1.0x).
*   **Attacks to Cast**: The number of basic attacks required to generate the mana pool needed for a cast (each attack generates 10 mana by default, except with Shojin).
*   **Cast Lockout (s)**: The duration spent executing the spell cast animation, during which basic attacks are paused. **Lockout time scales with Attack Speed**, modeled as:
    
 `Lockout(AS) = (Base Lockout) / (AS)`

*   **Cycle Duration (s)**: The total time of one full combat loop:
    
 `Cycle Duration = (Attacks to Cast + Base Lockout) / (AS)`

*   **Auto Attack DPS**: The average damage per second contributed strictly by basic auto-attacks over a cycle:
    
 `Auto Attack DPS = (Attacks to Cast * AD) / (Cycle Duration) * Crit * Amp`

*   **Spell DPS**: The average damage per second contributed strictly by the spell over a cycle:
    
 `Spell DPS = (Spell Damage) / (Cycle Duration) * Crit * Amp`

*   **Total DPS**: The combined damage output over a cycle:
    
 `Total DPS = Auto Attack DPS + Spell DPS`

*   **Crit Multiplier (Crit)**: The average multiplier applied by Critical strike chance and damage:
    
 `Average Crit Multiplier = 1 + Crit Chance * (Crit Damage - 1)`

    *   *Baseline (No Crit Items)*: 25% Crit Chance, 140% Crit Damage (`1.10x` multiplier) — TFT base crit damage is 140%.
    *   *Jeweled Gauntlet (JG)*: 40% Crit Chance, 170% Crit Damage (`1.28x` multiplier). Spells can crit.
    *   *Infinity Edge (IE)*: 60% Crit Chance, 140% Crit Damage (`1.24x` multiplier). Spells can crit.
    *   *IE + Last Whisper (LW)*: 70% Crit Chance, 140% Crit Damage (`1.28x` multiplier).
*   **AP vs. AD-ratio spells**: AP multiplies a spell's flat/base damage component only (e.g. Darius's 55/80/110 flat). Pure AD-r## 🔍 Detailed Champion Breakdowns

### 1. Akshan 🦅
*   **Detailed Math & Formula Proofs**: See [akshan-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/akshan-dps-calculation.md)
*   **Combat Role & Mechanics**: Backline sniper. Channels 6 physical damage shots locking onto the farthest enemy.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS*: **69.7 / 104.4 / 156.7**
    *   *Well-Equipped (3-Item) Total DPS*: **243.5 / 367.4 / 554.4**
*   **Aesthetic Balance Note**: Focuses purely on backline sniper value rather than tank melting.

---

### 2. Darius 🪓
*   **Detailed Math & Formula Proofs**: See [darius-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/darius-dps-calculation.md)
*   **Combat Role & Mechanics**: Melee physical execution carry. Slashes target; recasts instantly on kill with slight falloff.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS (1 Target)*: **62.6 / 94.3 / 140.7** (1 Reset Avg: **75.5 / 113.3 / 169.9**)
    *   *Well-Equipped (3-Item) Total DPS (1 Reset Avg)*: **222.0 / 332.3 / 495.6**
*   **Aesthetic Balance Note**: Balanced hybrid profile of durability and execution.

---

### 3. Ekko ⏳
*   **Detailed Math & Formula Proofs**: See [ekko-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/ekko-dps-calculation.md)
*   **Combat Role & Mechanics**: Melee magic assassin. Dives target, dealing magic damage and healing for 20% of damage taken in the last 4s.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS*: **71.7 / 107.5 / 161.5**
    *   *Well-Equipped (3-Item) Total DPS*: **203.5 / 304.3 / 456.4**
*   **Aesthetic Balance Note**: Durability-focused assassin whose target-access value compensates for slightly lower raw front-to-back DPS.

---

### 4. Garen 🌀
*   **Detailed Math & Formula Proofs**: See [garen-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/garen-dps-calculation.md)
*   **Combat Role & Mechanics**: Melee physical spinner. Spins for 4s, dealing AD-ratio physical damage to adjacent targets. Spins scale with AS.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS (1 Target Typical)*: **68.7 / 103.1 / 154.9** (2 Targets Avg: **99.2 / 148.9 / 223.6**)
    *   *Well-Equipped (3-Item) Total DPS (1 Target Typical)*: **194.8 / 292.6 / 438.0**
*   **Aesthetic Balance Note**: Judgement is modeled on 1 target typical to maintain fair benchmark alignment with Darius.

---

### 5. Kalista 🎯
*   **Detailed Math & Formula Proofs**: See [kalista-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/kalista-dps-calculation.md)
*   **Combat Role & Mechanics**: Single-target tank shredder. Stacks true damage spears and executes target automatically.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS*: **60.0 / 90.3 / 134.6**
    *   *Well-Equipped (3-Item) Total DPS*: **238.2 / 357.4 / 569.9**
*   **Aesthetic Balance Note**: True damage and automatic execute thresholds make her a highly efficient anti-tank option.

---

### 6. Karma 🪷
*   **Detailed Math & Formula Proofs**: See [karma-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/karma-dps-calculation.md)
*   **Combat Role & Mechanics**: Backline AP burst carry. Fires energy bursts in splash area, with every 3rd cast firing 3 bursts.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS (1 Target)*: **70.3 / 105.7 / 158.0** (2 Targets Avg: **112.3 / 168.6 / 252.4**)
    *   *Well-Equipped (3-Item) Total DPS (2 Targets Avg)*: **245.2 / 367.8 / 551.7**
*   **Aesthetic Balance Note**: Large blast hitboxes make Karma one of the most reliable and highest-output splash carries.

---

### 7. Katarina 🔪
*   **Detailed Math & Formula Proofs**: See [katarina-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/katarina-dps-calculation.md)
*   **Combat Role & Mechanics**: Melee AP assassin. Teleports to backline, throwing 3 daggers and slashing adjacent targets.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS (1 Target)*: **70.4 / 105.6 / 158.7** (1.5 Targets Avg: **88.6 / 133.0 / 199.9**)
    *   *Well-Equipped (3-Item) Total DPS (1.5 Targets Avg)*: **155.2 / 234.9 / 368.0**
*   **Aesthetic Balance Note**: Highest raw baseline and equipped outputs among assassins, with built-in healing reduction utility.

---

### 8. Rek'Sai 🦎
*   **Detailed Math & Formula Proofs**: See [reksai-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/reksai-dps-calculation.md)
*   **Combat Role & Mechanics**: Melee physical bruiser. Bite deals physical damage, converting to true damage if target is under 66% HP, and scaling higher on marked targets.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS (<66% HP)*: **67.5 / 101.3 / 151.9**
    *   *Well-Equipped (3-Item) Total DPS (<66% HP)*: **194.7 / 292.1 / 438.1**
*   **Aesthetic Balance Note**: True damage execution and self-healing provide massive combat efficiency.

---

### 9. Vel'Koz 👁️
*   **Detailed Math & Formula Proofs**: See [velkoz-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/velkoz-dps-calculation.md)
*   **Combat Role & Mechanics**: Backline AP carry. Fission bolt splits perpendicularly on first hit, dealing 50% damage to passed targets.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS (1 Target)*: **49.1 / 73.6 / 110.4** (2 Splits Avg: **60.9 / 91.3 / 136.9**)
    *   *Well-Equipped (3-Item) Total DPS (2 Splits Avg)*: **166.8 / 250.2 / 409.2**
*   **Aesthetic Balance Note**: Splits allow massive frontline-to-backline cleave when enemy boards are clumped.
