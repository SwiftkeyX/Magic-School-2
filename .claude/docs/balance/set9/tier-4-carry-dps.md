# TFT Set 9 Tier 4 Carry DPS Analysis (Unified)

This document provides a unified mathematical breakdown of baseline (unequipped) and well-equipped (3-item) DPS scaling for all 4-Gold carry champions in Teamfight Tactics (Set 9).

Putting baseline and itemized calculations in a single document guarantees that both calculations utilize identical, up-to-date mechanical assumptions (AS-scaling lockouts, targeting splits, and cast animation frames).

---

### 📊 Master DPS Summary Tables

### 📘 Table 1: Baseline (Unequipped) DPS Summary
*Consolidated comparison across 1★, 2★, and 3★ star levels with NO items equipped.*

| Champion | Star | Base AD | AS | Auto Attack DPS | Spell DPS | Total DPS |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Aphelios** (3 Targets, 6 Chakrams) | 1★<br>2★<br>3★ | 65<br>98<br>146 | 0.75 | 59.5<br>89.7<br>161.2 | 35.1<br>52.9<br>246.3 | **94.6**<br>**142.6**<br>**407.5** |
| **Azir** (Max 3 Soldiers + Direct Cast) | 1★<br>2★<br>3★ | 30<br>45<br>68 | 0.75 | 21.3<br>32.0<br>48.4 | 71.8<br>104.5<br>326.6 | **93.1**<br>**136.5**<br>**375.0** |
| **Gwen** (2 Targets Avg) | 1★<br>2★<br>3★ | 55<br>83<br>124 | 0.80 | 38.7<br>58.4<br>87.3 | 105.6<br>158.4<br>422.4 | **144.3**<br>**216.8**<br>**509.7** |
| **Kai'Sa** (15 Missiles Split) | 1★<br>2★<br>3★ | 45<br>68<br>101 | 0.80 | 35.2<br>53.2<br>79.0 | 73.3<br>108.5<br>293.2 | **108.5**<br>**161.7**<br>**372.2** |
| **Lux** (Single Target Channel) | 1★<br>2★<br>3★ | 45<br>68<br>101 | 0.70 | 22.7<br>34.4<br>51.0 | 92.8<br>138.9<br>347.3 | **115.6**<br>**173.3**<br>**398.3** |
| **Yasuo** (2 Targets Avg) | 1★<br>2★<br>3★ | 75<br>113<br>169 | 0.80 | 60.7<br>91.5<br>136.8 | 37.3<br>56.1<br>88.6 | **98.0**<br>**147.6**<br>**225.4** |
| **Zeri** (4 Targets Avg Chain) | 1★<br>2★<br>3★ | 65<br>98<br>146 | 0.80 | 49.3<br>74.3<br>110.8 | 74.0<br>111.5<br>166.1 | **123.3**<br>**185.9**<br>**276.9** |

### ⚔️ Table 2: Well-Equipped (3-Item) DPS Summary
*Consolidated comparison across 1★, 2★, and 3★ star levels with 3 core optimal items equipped. Shows average outputs over a 30s fight.*

| Champion | Star | AD | AS | Auto Attack DPS | Spell DPS | Total DPS |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Aphelios** (3 Targets, 6 Chakrams) | 1★<br>2★<br>3★ | 130<br>196<br>292 | 1.40 | 291.9<br>438.9<br>870.2 | 148.8<br>223.9<br>1040.0 | **440.7**<br>**662.8**<br>**1910.2** |
| **Azir** (Max 3 Soldiers + Direct Cast) | 1★<br>2★<br>3★ | 30<br>45<br>68 | 1.10 | 36.4<br>54.6<br>82.6 | 325.4<br>472.6<br>1569.0 | **361.8**<br>**527.2**<br>**1651.6** |
| **Gwen** (2 Targets Avg) | 1★<br>2★<br>3★ | 55<br>83<br>124 | 0.80 | 42.2<br>63.7<br>95.2 | 307.2<br>460.8<br>1228.8 | **349.4**<br>**524.5**<br>**1324.0** |
| **Kai'Sa** (15 Missiles Split) | 1★<br>2★<br>3★ | 52<br>78<br>116 | 0.92 | 51.5<br>77.3<br>115.0 | 299.7<br>443.6<br>1198.8 | **351.2**<br>**520.9**<br>**1313.8** |
| **Lux** (Single Target Channel) | 1★<br>2★<br>3★ | 45<br>68<br>101 | 0.70 | 23.7<br>35.8<br>53.2 | 258.1<br>386.3<br>965.7 | **281.8**<br>**422.1**<br>**1018.9** |
| **Yasuo** (2 Targets Avg) | 1★<br>2★<br>3★ | 166<br>250<br>373 | 0.80 | 151.5<br>228.1<br>340.3 | 92.9<br>140.0<br>220.4 | **244.4**<br>**368.1**<br>**560.7** |
| **Zeri** (4 Targets Avg Chain) | 1★<br>2★<br>3★ | 137<br>207<br>308 | 1.00 | 151.2<br>228.4<br>339.9 | 226.8<br>342.6<br>509.8 | **377.9**<br>**571.0**<br>**849.7** |

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
    *   *Modeling note*: as a simplification, these docs apply the average crit multiplier to spell damage in baseline rows too (strictly, TFT abilities only crit with JG/IE equipped).
*   **AP vs. AD-ratio spells**: AP multiplies a spell's flat/base damage component only. Pure AD-ratio components do not scale with AP — matching TFT's per-star ability data.

---

## 🔍 Detailed Champion Breakdowns

### 1. Aphelios 🌙
*   **Detailed Math & Formula Proofs**: See [aphelios-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/aphelios-dps-calculation.md)
*   **Combat Role & Mechanics**: Backline physical carry. Fires a physical blast in a 2-hex area (targeting clumps), and equips Chakrams (+3 base, +1 per hit) that add bonus damage on-hit for 7 seconds.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS*: **94.6 / 142.6 / 407.5**
    *   *Well-Equipped (3-Item) Total DPS*: **440.7 / 662.8 / 1910.2**
*   **Aesthetic Balance Note**: Relies heavily on Chakram stack amplification, scaling exponentially with Attack Speed.

---

### 2. Azir ☀️
*   **Detailed Math & Formula Proofs**: See [azir-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/azir-dps-calculation.md)
*   **Combat Role & Mechanics**: Backline AP summoner. Summons Sand Soldiers (max 3) who strike magic damage on every 3rd basic attack of Azir. Once 3 soldiers are active, subsequent casts deal direct magic damage.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS*: **93.1 / 136.5 / 375.0**
    *   *Well-Equipped (3-Item) Total DPS*: **361.8 / 527.2 / 1651.6**
*   **Aesthetic Balance Note**: Guinsoo's ramping shifts his AP modifier to 190 AP (with average 1.10 AS), enabling massive ramping output.

---

### 3. Gwen ✂️
*   **Detailed Math & Formula Proofs**: See [gwen-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/gwen-dps-calculation.md)
*   **Combat Role & Mechanics**: Melee AP carry. Dashes and snips 3 times in a cone, dealing magic damage. Every 3rd cast grants armor and MR.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS*: **144.3 / 216.8 / 509.7**
    *   *Well-Equipped (3-Item) Total DPS*: **349.4 / 524.5 / 1324.0**
*   **Aesthetic Balance Note**: Large cone hitbox makes her a premier frontline AP threat.

---

### 4. Kai'Sa 👾
*   **Detailed Math & Formula Proofs**: See [kaisa-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/kaisa-dps-calculation.md)
*   **Combat Role & Mechanics**: Backline AP carry. Dashes and fires 15 magic missiles split across the nearest 4 targets.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS*: **108.5 / 161.7 / 372.2**
    *   *Well-Equipped (3-Item) Total DPS*: **351.2 / 520.9 / 1313.8**
*   **Aesthetic Balance Note**: Dash provides high survivability while Shojin optimizes cast cycles.

---

### 5. Lux ☀️
*   **Detailed Math & Formula Proofs**: See [lux-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/lux-dps-calculation.md)
*   **Combat Role & Mechanics**: Backline AP burst carry. Channels magic damage barrage at current target over 3s, shredding MR.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS*: **115.6 / 173.3 / 398.3**
    *   *Well-Equipped (3-Item) Total DPS*: **281.8 / 422.1 / 1018.9**
*   **Aesthetic Balance Note**: High single-target melting capability paired with utility shred.

---

### 6. Yasuo 🌪️
*   **Detailed Math & Formula Proofs**: See [yasuo-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/yasuo-dps-calculation.md)
*   **Combat Role & Mechanics**: Melee physical carry. Whirlwind knocks up and slashes target + adjacent enemies (assumed 2 targets average).
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS*: **98.0 / 147.6 / 225.4**
    *   *Well-Equipped (3-Item) Total DPS*: **244.4 / 368.1 / 560.7**
*   **Aesthetic Balance Note**: Heavy AD scaling makes physical spell crits extremely lethal.

---

### 7. Zeri ⚡
*   **Detailed Math & Formula Proofs**: See [zeri-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/zeri-dps-calculation.md)
*   **Combat Role & Mechanics**: Backline physical carry. Executes targets below 10% HP. Active chains physical lightning to 3 additional targets.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS*: **123.3 / 185.9 / 276.9**
    *   *Well-Equipped (3-Item) Total DPS*: **377.9 / 571.0 / 849.7**
*   **Aesthetic Balance Note**: High active buff uptime ensures consistent multi-target physical output.

