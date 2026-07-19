# TFT Set 9 Tier 3 Carry DPS Analysis (Unified)

This document provides a unified mathematical breakdown of baseline (unequipped) and well-equipped (3-item) DPS scaling for all 3-Gold carry champions in Teamfight Tactics (Set 9).

Putting baseline and itemized calculations in a single document guarantees that both calculations utilize identical, up-to-date mechanical assumptions (AS-scaling lockouts, targeting splits, and cast animation frames).

---

> [!NOTE]
> **Mitigation & True Damage Note**: Raw DPS values assume targets have **0 Armor / 0 Magic Resist**. In actual gameplay, champions who deal true damage (**Kalista**, **Rek'Sai**) or possess built-in armor shred/reduction (like **Samira** at Tier 1) will maintain significantly higher effective relative DPS against armored target dummies than shown on paper. A future pass will test these units against standardized high-defense targets.

### 📊 Master DPS Summary Tables

### 📘 Table 1: Baseline (Unequipped) DPS Summary
*Consolidated comparison across 1★, 2★, and 3★ star levels with NO items equipped.*

| Champion | Star | Base AD | AS | Auto Attack DPS | Spell DPS | Total DPS |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Akshan** (Single Target) | 1★<br>2★<br>3★ | 60<br>90<br>135 | 0.75 | 41.1<br>61.6<br>92.5 | 35.5<br>55.1<br>85.5 | **76.6**<br>**116.7**<br>**177.9** |
| **Darius** (1 Reset / 2 Casts Avg) | 1★<br>2★<br>3★ | 65<br>98<br>146 | 0.70 | 41.0<br>61.8<br>92.0 | 37.6<br>56.3<br>82.6 | **78.6**<br>**118.0**<br>**174.6** <br>*(1 Target Baseline: **60.8** / **91.5** / **135.2**)* |
| **Ekko** (Single Target) | 1★<br>2★<br>3★ | 50<br>75<br>113 | 0.80 | 39.0<br>58.5<br>88.2 | 39.8<br>59.3<br>88.9 | **78.8**<br>**117.8**<br>**177.1** |
| **Garen** (1 Target Baseline) | 1★<br>2★<br>3★ | 70<br>105<br>158 | 0.75 | 42.0<br>63.0<br>94.8 | 33.6<br>51.7<br>80.6 | **75.6**<br>**114.7**<br>**175.4** <br>*(2 Target Avg: **109.2** / **166.4** / **256.0**)* |
| **Kalista** (Single Target, 12 stack Rend) | 1★<br>2★<br>3★ | 45<br>68<br>101 | 0.85 | 37.1<br>56.1<br>83.3 | 27.0<br>40.5<br>67.5 | **64.1**<br>**96.6**<br>**150.8** |
| **Karma** (1.33 Targets Avg) | 1★<br>2★<br>3★ | 45<br>68<br>101 | 0.70 | 29.9<br>45.1<br>67.0 | 50.1<br>75.1<br>112.7 | **80.0**<br>**120.2**<br>**179.7** <br>*(1 Target Baseline: **67.6** / **101.6** / **151.7**)* |
| **Katarina** (1.5 Targets / 4.5 hits Avg) | 1★<br>2★<br>3★ | 50<br>75<br>113 | 0.75 | 35.9<br>53.8<br>81.0 | 58.5<br>88.8<br>141.2 | **94.4**<br>**142.6**<br>**222.2** <br>*(1 Target Baseline: **74.9** / **113.0** / **175.1**)* |
| **Rek'Sai** (Target > 66% HP) | 1★<br>2★<br>3★ | 60<br>90<br>135 | 0.75 | 46.0<br>69.1<br>103.6 | 25.6<br>38.5<br>57.7 | **71.6**<br>**107.6**<br>**161.3** |
| **Vel'Koz** (2 Targets Avg) | 1★<br>2★<br>3★ | 40<br>60<br>90 | 0.70 | 27.2<br>40.8<br>61.2 | 49.8<br>74.8<br>124.6 | **77.0**<br>**115.6**<br>**185.8** <br>*(1 Target Baseline: **52.1** / **78.2** / **123.5**)* |

### ⚔️ Table 2: Well-Equipped (3-Item) DPS Summary
*Consolidated comparison across 1★, 2★, and 3★ star levels with 3 core optimal items equipped. Shows time-averaged stats and DPS (no ramping slashes).*

| Champion | Star | AD | AS | Auto Attack DPS | Spell DPS | Total DPS |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Akshan** (Single Target) | 1★<br>2★<br>3★ | 133<br>199<br>298 | 0.83 | 161.3<br>241.3<br>361.4 | 82.1<br>125.1<br>190.7 | **243.4**<br>**366.5**<br>**552.2** |
| **Darius** (1 Reset / 2 Casts Avg) | 1★<br>2★<br>3★ | 114<br>172<br>256 | 0.88 | 101.8<br>153.6<br>228.6 | 90.8<br>136.1<br>200.0 | **192.5**<br>**289.6**<br>**428.5** |
| **Ekko** (Single Target) | 1★<br>2★<br>3★ | 65<br>98<br>147 | 1.00 | 71.7<br>108.1<br>162.2 | 109.7<br>163.5<br>245.3 | **181.5**<br>**271.7**<br>**407.5** |
| **Garen** (1 Target Typical) | 1★<br>2★<br>3★ | 98<br>147<br>221 | 0.94 | 80.1<br>120.1<br>180.6 | 80.1<br>123.4<br>192.2 | **160.2**<br>**243.5**<br>**372.8** |
| **Kalista** (Single Target, 12 stack Rend) | 1★<br>2★<br>3★ | 52<br>78<br>116 | 2.02 | 79.0<br>118.5<br>176.2 | 119.0<br>178.4<br>297.4 | **198.0**<br>**296.9**<br>**473.6** |
| **Karma** (1.33 Targets Avg) | 1★<br>2★<br>3★ | 45<br>68<br>101 | 0.70 | 33.6<br>50.8<br>75.4 | 151.4<br>227.1<br>340.7 | **185.0**<br>**277.5**<br>**416.0** |
| **Katarina** (1.5 Targets / 4.5 hits Avg) | 1★<br>2★<br>3★ | 50<br>75<br>113 | 0.75 | 45.9<br>68.9<br>103.7 | 146.0<br>221.5<br>352.4 | **191.9**<br>**290.4**<br>**456.2** |
| **Rek'Sai** (Target < 66% HP, Marked) | 1★<br>2★<br>3★ | 123<br>184<br>277 | 0.94 | 130.4<br>195.0<br>293.6 | 64.4<br>96.3<br>145.0 | **194.8**<br>**291.3**<br>**438.6** |
| **Vel'Koz** (2 Targets Avg) | 1★<br>2★<br>3★ | 40<br>60<br>90 | 0.70 | 30.9<br>46.3<br>69.5 | 152.9<br>229.3<br>382.1 | **183.8**<br>**275.6**<br>**451.6** |

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
    *   *Baseline (Unequipped) Total DPS*: **76.6 / 116.7 / 177.9**
    *   *Well-Equipped (3-Item) Total DPS*: **243.4 / 366.5 / 552.2**
*   **Aesthetic Balance Note**: Focuses purely on backline sniper value rather than tank melting.

---

### 2. Darius 🪓
*   **Detailed Math & Formula Proofs**: See [darius-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/darius-dps-calculation.md)
*   **Combat Role & Mechanics**: Melee physical execution carry. Slashes target; recasts instantly on kill with slight falloff.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS (1 Target)*: **60.8 / 91.5 / 135.2** (1 Reset Avg: **78.6 / 118.0 / 174.6**)
    *   *Well-Equipped (3-Item) Total DPS (1 Reset Avg)*: **192.5 / 289.6 / 428.5**
*   **Aesthetic Balance Note**: Balanced hybrid profile of durability and execution.

---

### 3. Ekko ⏳
*   **Detailed Math & Formula Proofs**: See [ekko-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/ekko-dps-calculation.md)
*   **Combat Role & Mechanics**: Melee magic assassin. Dives target, dealing magic damage and healing for 20% of damage taken in the last 4s.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS*: **78.8 / 117.8 / 177.1**
    *   *Well-Equipped (3-Item) Total DPS*: **181.5 / 271.7 / 407.5**
*   **Aesthetic Balance Note**: Durability-focused assassin whose target-access value compensates for slightly lower raw front-to-back DPS.

---

### 4. Garen 🌀
*   **Detailed Math & Formula Proofs**: See [garen-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/garen-dps-calculation.md)
*   **Combat Role & Mechanics**: Melee physical spinner. Spins for 4s, dealing AD-ratio physical damage to adjacent targets. Spins scale with AS.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS (1 Target Typical)*: **75.6 / 114.7 / 175.4** (2 Targets Avg: **109.2 / 166.4 / 256.0**)
    *   *Well-Equipped (3-Item) Total DPS (1 Target Typical)*: **160.2 / 243.5 / 372.8**
*   **Aesthetic Balance Note**: Judgement is modeled on 1 target typical to maintain fair benchmark alignment with Darius.

---

### 5. Kalista 🎯
*   **Detailed Math & Formula Proofs**: See [kalista-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/kalista-dps-calculation.md)
*   **Combat Role & Mechanics**: Single-target tank shredder. Stacks true damage spears and executes target automatically.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS*: **64.1 / 96.6 / 150.8**
    *   *Well-Equipped (3-Item) Total DPS*: **198.0 / 296.9 / 473.6**
*   **Aesthetic Balance Note**: True damage and automatic execute thresholds make her a highly efficient anti-tank option.

---

### 6. Karma 🪷
*   **Detailed Math & Formula Proofs**: See [karma-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/karma-dps-calculation.md)
*   **Combat Role & Mechanics**: Backline AP burst carry. Fires energy bursts in splash area, with every 3rd cast firing 3 bursts.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS (1 Target)*: **67.6 / 101.6 / 151.7** (1.33 Targets Avg: **80.0 / 120.2 / 179.7**)
    *   *Well-Equipped (3-Item) Total DPS (1.33 Targets Avg)*: **185.0 / 277.5 / 416.0**
*   **Aesthetic Balance Note**: Large blast hitboxes make Karma one of the most reliable and highest-output splash carries.

---

### 7. Katarina 🔪
*   **Detailed Math & Formula Proofs**: See [katarina-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/katarina-dps-calculation.md)
*   **Combat Role & Mechanics**: Melee AP assassin. Teleports to backline, throwing 3 daggers and slashing adjacent targets.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS (1 Target)*: **74.9 / 113.0 / 175.1** (1.5 Targets Avg: **94.4 / 142.6 / 222.2**)
    *   *Well-Equipped (3-Item) Total DPS (1.5 Targets Avg)*: **191.9 / 290.4 / 456.2**
*   **Aesthetic Balance Note**: Highest raw baseline and equipped outputs among assassins, with built-in healing reduction utility.

---

### 8. Rek'Sai 🦎
*   **Detailed Math & Formula Proofs**: See [reksai-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/reksai-dps-calculation.md)
*   **Combat Role & Mechanics**: Melee physical bruiser. Bite deals physical damage, converting to true damage if target is under 66% HP, and scaling higher on marked targets.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS (<66% HP)*: **71.6 / 107.6 / 161.3**
    *   *Well-Equipped (3-Item) Total DPS (<66% HP)*: **194.8 / 291.3 / 438.6**
*   **Aesthetic Balance Note**: True damage execution and self-healing provide massive combat efficiency.

---

### 9. Vel'Koz 👁️
*   **Detailed Math & Formula Proofs**: See [velkoz-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/velkoz-dps-calculation.md)
*   **Combat Role & Mechanics**: Backline AP carry. Fission bolt splits perpendicularly on first hit, dealing 50% damage to passed targets.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS (1 Target)*: **52.1 / 78.2 / 123.5** (2 Splits Avg: **77.0 / 115.6 / 185.8**)
    *   *Well-Equipped (3-Item) Total DPS (2 Splits Avg)*: **183.8 / 275.6 / 451.6**
*   **Aesthetic Balance Note**: Splits allow massive frontline-to-backline cleave when enemy boards are clumped.
