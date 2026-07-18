# TFT Set 9 Tier 4 Carry DPS Analysis (Unified)

This document provides a unified mathematical breakdown of baseline (unequipped) and well-equipped (3-item) DPS scaling for all 4-Gold carry champions in Teamfight Tactics (Set 9).

Putting baseline and itemized calculations in a single document guarantees that both calculations utilize identical, up-to-date mechanical assumptions (AS-scaling lockouts, targeting splits, and cast animation frames).

---

### 📊 Master DPS Summary Tables

### 📘 Table 1: Baseline (Unequipped) DPS Summary
*Consolidated comparison across 1★, 2★, and 3★ star levels with NO items equipped.*

| Champion | Star | Base AD | AS | Auto Attack DPS | Spell DPS | Total DPS |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Aphelios** (3 Targets, 6 Chakrams) | 1★<br>2★<br>3★ | 65<br>98<br>146 | 0.75 | 44.3<br>66.8<br>99.5 | 37.8<br>57.0<br>99.7 | **82.1**<br>**123.8**<br>**199.2** |
| **Azir** (Max 3 Soldiers + Direct Cast) | 1★<br>2★<br>3★ | 30<br>45<br>68 | 0.75 | 19.4<br>29.1<br>44.0 | 56.4<br>83.1<br>640.4 | **75.8**<br>**112.2**<br>**684.4** |
| **Gwen** (2 Targets Avg) | 1★<br>2★<br>3★ | 55<br>83<br>124 | 0.80 | 35.2<br>53.1<br>79.4 | 96.0<br>144.0<br>384.0 | **131.2**<br>**197.1**<br>**463.4** |
| **Kai'Sa** (15 Missiles Split) | 1★<br>2★<br>3★ | 45<br>68<br>101 | 0.80 | 32.0<br>48.3<br>71.8 | 66.7<br>98.6<br>266.6 | **98.7**<br>**146.9**<br>**338.4** |
| **Lux** (Single Target Channel) | 1★<br>2★<br>3★ | 45<br>68<br>101 | 0.70 | 20.7<br>31.2<br>46.4 | 84.3<br>126.2<br>315.6| **Yasuo** (2 Targets Avg) | 1★<br>2★<br>3★ | 75<br>113<br>169 | 0.80 | 55.2<br>83.1<br>124.4 | 45.2<br>68.0<br>107.4 | **89.0**<br>**134.2**<br>**204.9** |
| **Zeri** (4 Targets Avg Chain) | 1★<br>2★<br>3★ | 65<br>98<br>146 | 0.80 | 44.8<br>67.6<br>100.7 | 67.2<br>101.4<br>151.0 | **112.0**<br>**169.0**<br>**251.7** |

### ⚔️ Table 2: Well-Equipped (3-Item) DPS Summary
*Consolidated comparison across 1★, 2★, and 3★ star levels with 3 core optimal items equipped. Shows average outputs over a 30s fight.*

| Champion | Star | AD | AS | Auto Attack DPS | Spell DPS | Total DPS |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Aphelios** (3 Targets, 6 Chakrams) | 1★<br>2★<br>3★ | 130<br>197<br>293 | 1.40 | 198.5<br>300.8<br>447.3 | 212.4<br>321.8<br>545.7 | **410.9**<br>**622.6**<br>**993.0** |
| **Azir** (Max 3 Soldiers + Direct Cast) | 1★<br>2★<br>3★ | 30<br>45<br>68 | 1.10 | 36.4<br>54.6<br>82.6 | 281.1<br>416.7<br>2844.7 | **317.5**<br>**471.3**<br>**2927.3** |
| **Gwen** (2 Targets Avg) | 1★<br>2★<br>3★ | 55<br>83<br>124 | 0.80 | 42.2<br>63.7<br>95.2 | 307.2<br>460.8<br>1228.8 | **349.4**<br>**524.5**<br>**1324.0** |
| **Kai'Sa** (15 Missiles Split) | 1★<br>2★<br>3★ | 45<br>68<br>101 | 0.92 | 44.6<br>67.0<br>100.4 | 299.8<br>449.7<br>1249.0 | **344.4**<br>**516.7**<br>**1349.4** |
| **Lux** (Single Target Channel) | 1★<br>2★<br>3★ | 45<br>68<br>101 | 0.70 | 23.7<br>35.6<br>53.4 | 258.2<br>386.3<br>965.7 | **281.9**<br>**421.9**<br>**1019.1** |
| **Yasuo** (2 Targets Avg) | 1★<br>2★<br>3★ | 166<br>250<br>373 | 0.80 | 151.3<br>227.8<br>339.9 | 92.9<br>140.0<br>220.4 | **244.2**<br>**367.8**<br>**560.3** |
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
    *   *Baseline (Unequipped) Total DPS*: **82.1 / 123.8 / 199.2**
    *   *Well-Equipped (3-Item) Total DPS*: **410.9 / 622.6 / 993.0**
*   **Aesthetic Balance Note**: Relies heavily on Chakram stack amplification, scaling exponentially with Attack Speed.

---

### 2. Azir ☀️
*   **Detailed Math & Formula Proofs**: See [azir-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/azir-dps-calculation.md)
*   **Combat Role & Mechanics**: Backline AP summoner. Summons Sand Soldiers (max 3) who strike magic damage on every 3rd basic attack of Azir. Once 3 soldiers are active, subsequent casts deal direct magic damage.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS*: **75.8 / 112.2 / 684.4**
    *   *Well-Equipped (3-Item) Total DPS*: **317.5 / 471.3 / 2927.3**
*   **Aesthetic Balance Note**: Guinsoo's ramping shifts his AP modifier to 190 AP (with average 1.10 AS), enabling massive ramping output.

---

### 3. Gwen ✂️
*   **Detailed Math & Formula Proofs**: See [gwen-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/gwen-dps-calculation.md)
*   **Combat Role & Mechanics**: Melee AP carry. Dashes and snips 3 times in a cone, dealing magic damage. Every 3rd cast grants armor and MR.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS*: **131.2 / 197.1 / 463.4**
    *   *Well-Equipped (3-Item) Total DPS*: **349.4 / 524.5 / 1324.0**
*   **Aesthetic Balance Note**: Large cone hitbox makes her a premier frontline AP threat.

---

### 4. Kai'Sa 👾
*   **Detailed Math & Formula Proofs**: See [kaisa-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/kaisa-dps-calculation.md)
*   **Combat Role & Mechanics**: Backline AP carry. Dashes and fires 15 magic missiles split across the nearest 4 targets.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS*: **98.7 / 146.9 / 338.4**
    *   *Well-Equipped (3-Item) Total DPS*: **344.4 / 516.7 / 1349.4**
*   **Aesthetic Balance Note**: Dash provides high survivability while Shojin optimizes cast cycles.

---

### 5. Lux ☀️
*   **Detailed Math & Formula Proofs**: See [lux-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/lux-dps-calculation.md)
*   **Combat Role & Mechanics**: Backline AP burst carry. Channels magic damage barrage at current target over 3s, shredding MR.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS*: **105.0 / 157.4 / 362.0**
    *   *Well-Equipped (3-Item) Total DPS*: **281.9 / 421.9 / 1019.1**
*   **Aesthetic Balance Note**: High single-target melting capability paired with utility shred.

---

### 6. Yasuo 🌪️
*   **Detailed Math & Formula Proofs**: See [yasuo-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/yasuo-dps-calculation.md)
*   **Combat Role & Mechanics**: Melee physical carry. Whirlwind knocks up and slashes target + adjacent enemies (assumed 2 targets average).
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS*: **89.0 / 134.2 / 204.9**
    *   *Well-Equipped (3-Item) Total DPS*: **244.2 / 367.8 / 560.3**
*   **Aesthetic Balance Note**: Heavy AD scaling makes physical spell crits extremely lethal.

---

### 7. Zeri ⚡
*   **Detailed Math & Formula Proofs**: See [zeri-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/zeri-dps-calculation.md)
*   **Combat Role & Mechanics**: Backline physical carry. Executes targets below 10% HP. Active chains physical lightning to 3 additional targets.
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS*: **112.0 / 169.0 / 251.7**
    *   *Well-Equipped (3-Item) Total DPS*: **324.2 / 486.2 / 729.4**
*   **Aesthetic Balance Note**: High active buff uptime ensures consistent multi-target physical output.

