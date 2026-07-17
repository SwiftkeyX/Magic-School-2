# TFT Set 9 Tier 1 Carry DPS Analysis (Unified)

This document provides a unified mathematical breakdown of baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels for all Tier 1 carries.

All calculations are derived from first principles using base stats sourced directly from the **TFT Set 9 Basic data** spreadsheet.

---

## 🗺️ Index & Navigation

*   [Table 1: Baseline (Unequipped) DPS Summary](#table-1-baseline-unequipped-dps-summary)
*   [Table 2: Well-Equipped (3-Item) DPS Summary](#table-2-well-equipped-3-item-dps-summary)
*   **Carries Breakdown**:
    *   [Cassiopeia](#1-cassiopeia-)
    *   [Jhin](#2-jhin-)
    *   [Malzahar](#3-malzahar-)
    *   [Samira](#4-samira-)
    *   [Tristana](#5-tristana-)
    *   [Viego](#6-viego-)
*   **Formula Reference**: [Glossary & Formula Index](#-glossary--formula-index)

---

## 📊 Summary Tables

### Table 1: Baseline (Unequipped) DPS Summary
*Consolidated comparison across 1★, 2★, and 3★ star levels with NO items equipped. For champions without combat-duration ramping, the output is identical across fight times.*

| Champion | Hero Archetype | Duration | Star | Base AD | AS | Auto Attack DPS | Spell DPS | Total DPS |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Cassiopeia** | AP backliner, single target focus | Not specify | 1★<br>2★<br>3★ | 40<br>60<br>90 | 0.70 | 25.1<br>37.6<br>56.4 | 43.5<br>65.2<br>97.8 | **68.6**<br>**102.8**<br>**154.2** |
| **Jhin** | AD backliner, Big pierce AOE (avg to 2 target) | Not specify | 1★<br>2★<br>3★ | 54<br>81<br>122 | 0.70 | 34.6<br>51.9<br>78.1 | 35.5<br>53.2<br>80.1 | **70.1**<br>**105.1**<br>**158.2** |
| **Malzahar** | AP backliner, 1x3 hex AOE (avg to 1.5 target) | Not specify | 1★<br>2★<br>3★ | 40<br>60<br>90 | 0.70 | 25.2<br>37.8<br>56.7 | 41.5<br>62.3<br>94.4 | **66.8**<br>**100.1**<br>**151.1** |
| **Samira** | AD backliner, single-target focus | Not specify | 1★<br>2★<br>3★ | 45<br>68<br>101 | 0.70 | 26.5<br>40.1<br>59.6 | 16.8<br>25.4<br>39.7 | **43.3**<br>**65.5**<br>**99.3** |
| **Tristana** | AD backliner, splash AOE (avg hit 2 on AOE), single-focus | Not specify | 1★<br>2★<br>3★ | 45<br>68<br>101 | 0.70 | 40.6<br>61.3<br>91.1 | 26.5<br>40.0<br>59.4 | **67.1**<br>**101.3**<br>**150.5** |
| **Viego** | AP melee carry, single-target focus, stack scaling | 15s | 1★<br>2★<br>3★ | 45<br>68<br>101 | 0.75 | 30.1<br>45.5<br>67.6 | 21.4<br>32.1<br>48.6 | **51.5**<br>**77.6**<br>**116.2** |
| **Viego** | AP melee carry, single-target focus, stack scaling | 30s | 1★<br>2★<br>3★ | 45<br>68<br>101 | 0.75 | 30.1<br>45.5<br>67.6 | 34.8<br>52.2<br>78.7 | **64.9**<br>**97.7**<br>**146.3** |

---

### Table 2: Well-Equipped (3-Item) DPS Summary
*Consolidated comparison across 1★, 2★, and 3★ star levels with 3 core optimal items equipped (ramping effects averaged over combat duration).*

| Champion | Hero Archetype | Duration | Star | AD | AS | Auto Attack DPS | Spell DPS | Total DPS |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Cassiopeia** (170 AP) | AP backliner, single target focus | 15s | 1★<br>2★<br>3★ | 40<br>60<br>90 | 0.70 | 30.5<br>45.8<br>68.6 | 134.8<br>202.2<br>303.4 | **165.3**<br>**248.0**<br>**372.0** |
| **Cassiopeia** (200 AP) | AP backliner, single target focus | 30s | 1★<br>2★<br>3★ | 40<br>60<br>90 | 0.70 | 30.5<br>45.8<br>68.6 | 158.6<br>237.9<br>356.9 | **189.1**<br>**283.7**<br>**425.5** |
| **Jhin** | AD backliner, Big pierce AOE (avg to 2 target) | Not specify | 1★<br>2★<br>3★ | 114<br>171<br>257 | 0.77 | 99.5<br>149.3<br>224.3 | 87.6<br>131.4<br>197.4 | **187.1**<br>**280.7**<br>**421.7** |
| **Malzahar** | AP backliner, 1x3 hex AOE (avg to 1.5 target) | Not specify | 1★<br>2★<br>3★ | 46<br>69<br>104 | 0.70 | 36.2<br>54.2<br>81.7 | 139.4<br>209.1<br>316.8 | **175.6**<br>**263.3**<br>**398.5** |
| **Samira** | AD backliner, single-target focus | Not specify | 1★<br>2★<br>3★ | 65<br>98<br>146 | 0.77 | 47.8<br>72.9<br>107.4 | 45.4<br>69.2<br>107.4 | **93.2**<br>**142.1**<br>**214.8** |
| **Tristana** (1.26 AS) | AD backliner, splash AOE (avg hit 2 on AOE), single-focus | 15s | 1★<br>2★<br>3★ | 65<br>98<br>146 | 1.26 | 141.7<br>215.9<br>318.4 | 117.9<br>179.5<br>264.8 | **259.6**<br>**395.4**<br>**583.2** |
| **Tristana** (1.63 AS) | AD backliner, splash AOE (avg hit 2 on AOE), single-focus | 30s | 1★<br>2★<br>3★ | 65<br>98<br>146 | 1.63 | 175.5<br>267.3<br>394.2 | 152.6<br>232.3<br>342.6 | **328.1**<br>**499.6**<br>**736.8** |
| **Viego** (RFC × 3 - 1.33s) | AP melee carry, single-target focus, stack scaling | 15s | 1★<br>2★<br>3★ | 45<br>68<br>101 | 1.49 | 83.8<br>126.6<br>188.1 | 90.5<br>135.7<br>204.6 | **174.3**<br>**262.3**<br>**392.7** |
| **Viego** (RFC × 3 - 3.11s) | AP melee carry, single-target focus, stack scaling | 30s | 1★<br>2★<br>3★ | 45<br>68<br>101 | 1.49 | 83.8<br>126.6<br>188.1 | 156.8<br>235.2<br>353.7 | **240.6**<br>**361.8**<br>**541.8** |

---

## 👥 Champion Carries Breakdown

### 1. Cassiopeia 🐍

#### 🛡️ Mechanics & Combat Nuance
*   **Ability**: Active deals magic damage and wounds target (50% healing reduction) for 5 seconds. If the target is already wounded, deals bonus magic damage.
*   **Mana Rules**: Attacks required to cast is 3 (charges 30 max mana).
*   **Cast Lockout**: 0.25 seconds base.
*   **Attacks to Cast**: 3 attacks.

#### 🧮 DPS Output Summary
*   **Baseline (Unequipped)**:
    *   15s / 30s Fight: 1★: **68.6** | 2★: **102.8** | 3★: **154.2**
*   **Well-Equipped (Blue Buff + Jeweled Gauntlet + Archangel's)**:
    *   15s Fight (170 AP): 1★: **165.3** | 2★: **248.0** | 3★: **372.0**
    *   30s Fight (200 AP): 1★: **189.1** | 2★: **283.7** | 3★: **425.5**
*   **Detailed DPS Calculations**: [Cassiopeia DPS Calculations](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/cassiopeia-dps-calculation.md)

#### 🔍 Analyze DPS
*   **Wound and Bonus Scaling**: Cassiopeia functions as an early anti-heal carry. Her DPS spikes on subsequent casts against the same target, making her extremely strong at chewing down single high-health units.
*   **Archangel's Ramp**: Archangel's Staff increases her Ability Power by 20 every 5 seconds, resulting in a higher average AP of 200 over a 30-second engagement compared to 170 over 15 seconds.

---

### 2. Jhin 🏹

#### 🛡️ Mechanics & Combat Nuance
*   **Ability**: Active channels a shot dealing physical damage to all enemies in a line, with 40% damage reduction for each subsequent target hit. Averages to 2 targets hit per cast.
*   **Mana Rules**: Attacks required to cast is 5 (charges 50 max mana).
*   **Cast Lockout**: 1.0 second base.
*   **Attacks to Cast**: 5 attacks.

#### 🧮 DPS Output Summary
*   **Baseline (Unequipped)**:
    *   15s / 30s Fight (2 Targets Avg): 1★: **70.1** | 2★: **105.1** | 3★: **158.2**
*   **Well-Equipped (Deathblade + Infinity Edge + Runaan's)**:
    *   15s / 30s Fight (2 Targets Avg): 1★: **187.1** | 2★: **280.7** | 3★: **421.7**
*   **Detailed DPS Calculations**: [Jhin DPS Calculations](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/jhin-dps-calculation.md)

#### 🔍 Analyze DPS
*   **AOE Pierce Performance**: Jhin scales extremely well when firing into clumps of enemies. His physical spell damage can crit, pairing perfectly with Infinity Edge.
*   **Runaan's Hurricane physical bolts**: Add consistent single-target auto DPS while his spell charges.

---

### 3. Malzahar 🔮

#### 🛡️ Mechanics & Combat Nuance
*   **Ability**: Active opens two portals, dealing magic damage and destroying 35% of shields in a 1x3 hex area. Averages to 1.5 targets hit.
*   **Mana Rules**: Attacks required to cast is 6 (charges 60 max mana).
*   **Cast Lockout**: 0.8 seconds base.
*   **Attacks to Cast**: 6 attacks.

#### 🧮 DPS Output Summary
*   **Baseline (Unequipped)**:
    *   15s / 30s Fight (1.5 Targets Avg): 1★: **66.8** | 2★: **100.1** | 3★: **151.1**
*   **Well-Equipped (Blue Buff + Jeweled Gauntlet + Giant Slayer)**:
    *   15s / 30s Fight (1.5 Targets Avg): 1★: **175.6** | 2★: **263.3** | 3★: **398.5**
*   **Detailed DPS Calculations**: [Malzahar DPS Calculations](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/malzahar-dps-calculation.md)

#### 🔍 Analyze DPS
*   **Anti-Shield Utility**: Malzahar's value peaks against compositions relying on heavy shielding (e.g. Bastion or Shield Augments) while maintaining consistent line-splash magic damage.
*   **Giant Slayer Amplification**: Provides a flat 1.25x damage amplification against high-health frontlines.

---

### 4. Samira 🔫

#### 🛡️ Mechanics & Combat Nuance
*   **Ability**: Active fires at current target dealing physical damage and reducing their armor by 10/15/20 for 2 seconds.
*   **Mana Rules**: Attacks required to cast is 3 (charges 30 max mana).
*   **Cast Lockout**: 0.5 seconds base.
*   **Attacks to Cast**: 3 attacks.

#### 🧮 DPS Output Summary
*   **Baseline (Unequipped)**:
    *   15s / 30s Fight: 1★: **43.3** | 2★: **65.5** | 3★: **99.3**
*   **Well-Equipped (Deathblade + Last Whisper + Infinity Edge)**:
    *   15s / 30s Fight: 1★: **93.2** | 2★: **142.1** | 3★: **214.8**
*   **Detailed DPS Calculations**: [Samira DPS Calculations](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/samira-dps-calculation.md)

#### 🔍 Analyze DPS
*   **Armor Shred Utility**: Samira's spell reduces target armor, making it easier for her and her physical allies to deal massive damage.
*   **Synergy in AD Comps**: Highly valued in physical AD carry comps for armor reduction, though her individual DPS is balanced lower to compensate for utility.

---

### 5. Tristana 💣

#### 🛡️ Mechanics & Combat Nuance
*   **Ability**: Active grants AS steroid for 4 seconds. Attacks deal bonus splash physical damage to adjacent hexes.
*   **Mana Rules**: Attacks required to cast is 4 (charges 40 max mana). Buff locks mana generation for 4s.
*   **Cast Lockout**: 0.0 seconds base.
*   **Attacks to Cast**: 4 attacks.

#### 🧮 DPS Output Summary
*   **Baseline (Unequipped)**:
    *   15s / 30s Fight: 1★: **67.1** | 2★: **101.3** | 3★: **150.5**
*   **Well-Equipped (Guinsoo's + Last Whisper + Infinity Edge)**:
    *   15s Fight (1.26 AS avg): 1★: **259.6** | 2★: **395.4** | 3★: **583.2**
    *   30s Fight (1.63 AS avg): 1★: **328.1** | 2★: **499.6** | 3★: **736.8**
*   **Detailed DPS Calculations**: [Tristana DPS Calculations](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/tristana-dps-calculation.md)

#### 🔍 Analyze DPS
*   **Super-Linear Attack Speed Scaling**: Tristana is a backline carry whose baseline DPS appears low because she lacks flat spell damage.
*   **Guinsoo Ramping Uptime**: Under the time-based linear stack model, Guinsoo's Rageblade averages a higher equipped AS of 1.63 over 30s than 1.26 over 15s, significantly boosting her late-fight DPS output.

---

### 6. Viego ⚔️

#### 🛡️ Mechanics & Combat Nuance
*   **Ability**: Active strikes target, dealing magic damage. For the rest of combat, attacks deal stacking magic damage.
*   **Mana Rules**: Attacks required to cast is 5 (charges 50 max mana).
*   **Cast Lockout**: 0.8 seconds base.
*   **Attacks to Cast**: 5 attacks.

#### 🧮 DPS Output Summary
*   **Baseline (Unequipped)**:
    *   15s Fight (0.5 stacks avg): 1★: **51.5** | 2★: **77.6** | 3★: **116.2**
    *   30s Fight (1.5 stacks avg): 1★: **64.9** | 2★: **97.7** | 3★: **146.3**
*   **Well-Equipped (RFC × 3)**:
    *   15s Fight (1.33 stacks avg): 1★: **174.3** | 2★: **262.3** | 3★: **392.7**
    *   30s Fight (3.11 stacks avg): 1★: **240.6** | 2★: **361.8** | 3★: **541.8**
*   **Detailed DPS Calculations**: [Viego DPS Calculations](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/viego-dps-calculation.md)

#### 🔍 Analyze DPS
*   **Close-Range Melee Scaling**: Viego is a close-ranged carry who also focuses mainly on 1 target.
*   **Engagement Scaling**: Stacking magic damage on-hit over combat duration rewards long melee engagements, raising his baseline DPS from 51.5 (15s average) to 64.9 (30s average).
*   **Rapid Firecannon Ramping**: Equipping 3 Rapid Firecannons spikes Viego's Attack Speed to 1.49, allowing him to attack 36 times in 30 seconds and ramp his stacking damage to an average of 3.11 stacks, yielding 541.8 DPS at 3★.

---

## 📖 Glossary & Formula Index

*   **AD (Attack Damage)**: The physical damage dealt by a basic auto-attack. AD scales by 1.5x per star level (2★ = 1.5x, 3★ = 2.25x).
*   **AS (Attack Speed)**: The rate of basic attacks per second. Attack Speed remains flat across star levels.
*   **AP (Ability Power)**: The scaling multiplier applied to base spell damage (base is 100 AP / 1.0x).
*   **Attacks to Cast**: The number of basic attacks required to generate the mana pool needed for a cast (each attack generates 10 mana by default, except with Shojin/Blue Buff).
*   **Cast Lockout (s)**: The duration spent executing the spell cast animation, during which basic attacks are paused. Lockout time is fixed and does not scale with AS:
    
    `Cycle Duration = (Attacks to Cast) / (AS) + Cast Lockout + [Steroid Uptime, if mana locked]`

*   **Auto Attack DPS**: The average damage per second contributed strictly by basic auto-attacks over a cycle:
    
    `Auto Attack DPS = (Total Attacks * AD) / (Cycle Duration) * Crit * Amp`

*   **Spell Base**: The unmitigated baseline damage of the spell before accounting for multi-target averages, piercing, or physical scaling ratios.
*   **Spell Damage**: The final output damage of the spell per cycle, applying target averages and modifiers:
    
    `Spell Damage = Spell Base * AP_mult * Target_density * [Splash/Pierce Multipliers] * Crit * Amp`

*   **Spell DPS**: The average damage per second contributed strictly by spell casts over a cycle:
    
    `Spell DPS = Spell Damage / Cycle Duration`

*   **Total DPS**: The unified DPS of the champion combining basic attacks and spell outputs:
    
    `Total DPS = Auto Attack DPS + Spell DPS`

*   **Crit (Critical Strike Multiplier)**: The scaling factor applied to damage to account for crit rate and damage:
    
    `Crit = 1 + Crit Chance * (Crit Damage - 1)`

*   **Amp (Amplification Multiplier)**: The flat damage amplification factor contributed by item passives (e.g. Giant Slayer):
    
    `Amp = Amp_1 * Amp_2 * ...`
