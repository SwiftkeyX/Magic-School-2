# TFT Set 9 Tier 2 Carry DPS Analysis (Unified)

This document provides a unified mathematical breakdown of baseline (unequipped) and well-equipped (3-item) DPS across 1★, 2★, and 3★ star levels for all Tier 2 carries.

All calculations are derived from first principles using base stats sourced directly from the **TFT Set 9 Basic data** spreadsheet.

---

## 🗺️ Index & Navigation

*   [Table 1: Baseline (Unequipped) DPS Summary](#table-1-baseline-unequipped-dps-summary)
*   [Table 2: Well-Equipped (3-Item) DPS Summary](#table-2-well-equipped-3-item-dps-summary)
*   **Carries Breakdown**:
    *   [Jinx](#1-jinx-)
    *   [Teemo](#2-teemo-)
    *   [Taliyah](#3-taliyah-)
    *   [Zed](#4-zed-)
*   **Formula Reference**: [Glossary & Formula Index](#-glossary--formula-index)

---

## 📊 Summary Tables

### Table 1: Baseline (Unequipped) DPS Summary
*Consolidated comparison across 1★, 2★, and 3★ star levels with NO items equipped (applicable for both 15s and 30s fights).*

| Champion | Hero Archetype | Duration | Star | Base AD | AS | Auto Attack DPS | Spell DPS | Total DPS |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Jinx** | AD backliner, split-target rockets (5 rockets total) | Not specify | 1★<br>2★<br>3★ | 50<br>75<br>113 | 0.75 | 33.9<br>50.9<br>76.6 | 43.5<br>65.9<br>104.4 | **77.4**<br>**116.8**<br>**181.0** |
| **Teemo** | AP backliner, 1 circular hex AOE (avg to 2 targets) | Not specify | 1★<br>2★<br>3★ | 40<br>60<br>90 | 0.70 | 25.2<br>37.8<br>56.7 | 65.5<br>98.2<br>147.3 | **90.7**<br>**136.0**<br>**204.0** |
| **Taliyah** | AP backliner, combo knockup synergy (avg to 2 targets) | Not specify | 1★<br>2★<br>3★ | 40<br>60<br>90 | 0.70 | 28.2<br>42.3<br>63.4 | 67.7<br>101.6<br>152.3 | **95.9**<br>**143.9**<br>**215.7** |
| **Zed** | AD melee assassin, critical strike focus (avg to 2 targets) | Not specify | 1★<br>2★<br>3★ | 55<br>83<br>124 | 0.70 | 35.6<br>53.4<br>80.1 | 33.5<br>50.3<br>75.1 | **69.1**<br>**103.7**<br>**155.2** |

### Table 2: Well-Equipped (3-Item) DPS Summary
*Consolidated comparison across 1★, 2★, and 3★ star levels with 3 core optimal items equipped (applicable for both 15s and 30s fights).*

| Champion | Hero Archetype | Duration | Star | AD | AS | Auto Attack DPS | Spell DPS | Total DPS |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Jinx** (Standard) | AD backliner, split-target rockets (5 rockets total) | 15s | 1★<br>2★<br>3★ | 93<br>140<br>210 | 1.35 | 173.7<br>261.4<br>392.2 | 137.4<br>210.8<br>329.9 | **311.1**<br>**472.2**<br>**722.1** |
| **Jinx** (Standard) | AD backliner, split-target rockets (5 rockets total) | 30s | 1★<br>2★<br>3★ | 93<br>140<br>210 | 1.75 | 214.8<br>323.4<br>485.1 | 170.0<br>260.7<br>408.1 | **384.8**<br>**584.1**<br>**893.2** |
| **Teemo** (Standard) | AP backliner, 1 circular hex AOE (avg to 2 targets) | Not specify | 1★<br>2★<br>3★ | 40<br>60<br>90 | 0.70 | 29.9<br>44.8<br>67.2 | 194.0<br>291.1<br>436.6 | **223.9**<br>**335.9**<br>**503.8** |
| **Taliyah** (Standard) | AP backliner, combo knockup synergy (avg to 2 targets) | Not specify | 1★<br>2★<br>3★ | 40<br>60<br>90 | 0.70 | 31.6<br>47.4<br>71.1 | 130.3<br>195.5<br>293.2 | **161.9**<br>**242.9**<br>**364.3** |
| **Zed** (Standard) | AD melee assassin, critical strike focus (avg to 2 targets) | Not specify | 1★<br>2★<br>3★ | 122<br>183<br>275 | 0.70 | 56.8<br>85.3<br>127.9 | 121.9<br>182.9<br>274.3 | **178.7**<br>**268.2**<br>**402.2** |

---

## 👥 Champion Carries Breakdown

### 1. Jinx 🚀

#### 🛡️ Mechanics & Combat Nuance
*   **Ability**: Fires 5 rockets, splitting damage across nearby targets. Spell deals physical damage: $AD \times 1.50 / 1.55 / 1.60 + 15 / 20 / 35$ per rocket.
*   **Mana Rules**: Attacks required to cast is 7 (charges 70 max mana).
*   **Cast Lockout**: $1.0$ second base.
*   **Attacks to Cast**: 7 attacks.

#### 🧮 DPS Output Summary
*   **Baseline (Unequipped)**:
    *   15s / 30s Fight: 1★: **77.4** | 2★: **116.8** | 3★: **181.0**
*   **Well-Equipped (Guinsoo's + Deathblade + Runaan's)**:
    *   15s Fight (1.35 AS avg): 1★: **311.1** | 2★: **472.2** | 3★: **722.1**
    *   30s Fight (1.75 AS avg): 1★: **384.8** | 2★: **584.1** | 3★: **893.2**
*   **Detailed DPS Calculations**: [Jinx DPS Calculations](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/jinx-dps-calculation.md)

#### 🔍 Analyze DPS
*   **Splash Cleanup Benchmark**: Jinx represents the baseline for Tier 2 backline splash damage, with output scaling safely above Tier 1 carries due to higher baseline ratios.
*   **Guinsoo's Synergy**: Runaan's Hurricane physical bolts amplify her auto attack contribution, which pairs well with Guinsoo's Attack Speed ramping to scale rocket output.

---

### 2. Teemo 🍄

#### 🛡️ Mechanics & Combat Nuance
*   **Ability**: Throws an explosive mushroom. detonates on 2.0 targets average, dealing magic damage over 3 seconds and wounding them (-33% healing).
*   **Mana Rules**: Attacks required to cast is 5 (charges 50 max mana).
*   **Cast Lockout**: $0.8$ seconds base.
*   **Attacks to Cast**: 5 attacks.

#### 🧮 DPS Output Summary
*   **Baseline (Unequipped)**:
    *   15s / 30s Fight (2.0 targets avg): 1★: **90.7** | 2★: **136.0** | 3★: **204.0**
*   **Well-Equipped (Blue Buff + Jeweled Gauntlet + Deathcap)**:
    *   15s / 30s Fight: 1★: **223.9** | 2★: **335.9** | 3★: **503.8**
*   **Detailed DPS Calculations**: [Teemo DPS Calculations](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/teemo-dps-calculation.md)

#### 🔍 Analyze DPS
*   **DoT Counterplay**: While Teemo displays very high theoretical DPS numbers, his damage is damage-over-time (DoT) which allows healing counterplay, preventing burst-focused dominance.
*   **Blue Buff Cast Spikes**: Equipped Blue Buff reduces his max mana pool, accelerating his mushroom cycling and increasing AoE board-burn coverage.

---

### 3. Taliyah 🪨

#### 🛡️ Mechanics & Combat Nuance
*   **Ability**: Active seismic shove knocks up current target. Passive launches boulders dealing magic damage whenever any enemy is knocked up by any source.
*   **Mana Rules**: Attacks required to cast is 6 (charges 60 max mana).
*   **Cast Lockout**: $0.8$ seconds base.
*   **Attacks to Cast**: 6 attacks.

#### 🧮 DPS Output Summary
*   **Baseline (Unequipped)**:
    *   15s / 30s Fight (2 boulders): 1★: **95.9** | 2★: **143.9** | 3★: **215.7**
*   **Well-Equipped (Jeweled Gauntlet + Archangel's + Gunblade)**:
    *   15s / 30s Fight: 1★: **161.9** | 2★: **242.9** | 3★: **364.3**
*   **Detailed DPS Calculations**: [Taliyah DPS Calculations](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/taliyah-dps-calculation.md)

#### 🔍 Analyze DPS
*   **Synergy Dependency**: Taliyah's standalone baseline output is low, but she scales exponentially when paired with knockup synergies (e.g. Sett, Poppy), presenting a highly draft-dependent design.
*   **Archangel's Ramping**: Archangel's Staff adds AP over time, significantly scaling passive boulder damage in late-combat sequences.

---

### 4. Zed 🥷

#### 🛡️ Mechanics & Combat Nuance
*   **Ability**: Shadow clones double-slash adjacent targets, dealing physical damage scaled by AD ratio.
*   **Mana Rules**: Attacks required to cast is 7 (charges 70 max mana).
*   **Cast Lockout**: $0.8$ seconds base.
*   **Attacks to Cast**: 7 attacks.

#### 🧮 DPS Output Summary
*   **Baseline (Unequipped)**:
    *   15s / 30s Fight (2 targets): 1★: **69.1** | 2★: **103.7** | 3★: **155.2**
*   **Well-Equipped (Infinity Edge + Titan's + Bloodthirster)**:
    *   15s / 30s Fight: 1★: **178.7** | 2★: **268.2** | 3★: **402.2**
*   **Detailed DPS Calculations**: [Zed DPS Calculations](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/zed-dps-calculation.md)

#### 🔍 Analyze DPS
*   **Backline Threat Trade-off**: Zed is balanced strictly below Jinx in multi-target conditions due to his access to backline infiltration, trading raw AoE output for direct carry access.
*   **Titan's and Crit Multipliers**: Infinity Edge ensures his physical slash outputs crit consistently, which scales strongly with the stacked AD and AP from Titan's Resolve.

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
