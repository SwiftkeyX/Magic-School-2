# TFT Set 9 Tier 5 Carry DPS Analysis (Unified)

This document provides a unified mathematical breakdown of baseline (unequipped) and well-equipped (3-item) DPS scaling for all 5-Gold carry champions in Teamfight Tactics (Set 9).

Putting baseline and itemized calculations in a single document guarantees that both calculations utilize identical, up-to-date mechanical assumptions (AS-scaling lockouts, targeting splits, and cast animation frames).

---

## 📊 Master DPS Summary Tables

### 📘 Table 1: Baseline (Unequipped) DPS Summary
*Consolidated comparison across 1★, 2★, and 3★ star levels with NO items equipped.*

| Champion | Star | Base AD | AS | Auto Attack DPS | Spell DPS | Total DPS |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Aatrox** (1 adjacent target) | 1★<br>2★<br>3★ | 80<br>120<br>180 | 0.80 | 53.3<br>80.0<br>120.0 | 42.7<br>64.0<br>96.0 | **96.0**<br>**144.0**<br>**216.0** |
| **Ahri** (5 Wave targets avg) | 1★<br>2★<br>3★ | 50<br>75<br>113 | 0.85 | 35.4<br>53.1<br>80.0 | 91.1<br>134.7<br>755.4 | **126.5**<br>**187.8**<br>**835.4** |
| **Bel'Veth** (2000 HP target avg) | 1★<br>2★<br>3★ | 80<br>120<br>180 | 0.85 | 76.8<br>115.2<br>172.8 | 56.0<br>84.0<br>713.3 | **132.8**<br>**199.2**<br>**886.1** |

### ⚔️ Table 2: Well-Equipped (3-Item) DPS Summary
*Consolidated comparison across 1★, 2★, and 3★ star levels with 3 core optimal items equipped. Shows average outputs over a 30s fight.*

| Champion | Star | AD | AS | Auto Attack DPS | Spell DPS | Total DPS |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Aatrox** (1 adjacent target) | 1★<br>2★<br>3★ | 177<br>266<br>398 | 0.80 | 146.3<br>219.5<br>329.2 | 117.1<br>175.7<br>263.5 | **263.4**<br>**395.2**<br>**592.7** |
| **Ahri** (5 Wave targets avg) | 1★<br>2★<br>3★ | 50<br>75<br>113 | 0.85 | 43.5<br>65.3<br>97.9 | 280.0<br>413.5<br>2320.6 | **323.5**<br>**478.8**<br>**2418.5** |
| **Bel'Veth** (2000 HP target avg) | 1★<br>2★<br>3★ | 177<br>266<br>398 | 0.85 | 150.5<br>225.8<br>338.6 | 124.8<br>187.2<br>1358.3 | **275.3**<br>**413.0**<br>**1696.9** |

---

## 📖 Glossary & Formula Index

*   **AD (Attack Damage)**: The physical damage dealt by a basic auto-attack. AD scales by 1.5x per star level (2★ = 1.5x, 3★ = 2.25x).
*   **AS (Attack Speed)**: The rate of basic attacks per second. Attack Speed remains flat across star levels.
*   **AP (Ability Power)**: The scaling multiplier applied to base magic damage (base is 100 AP / 1.0x).
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
    *   *Modeling note*: as a simplification, these docs apply the average crit multiplier to spell damage in baseline rows too (strictly, TFT abilities only crit with JG/IE equipped). True damage never crits at baseline.
*   **AP vs. AD-ratio spells**: AP multiplies a spell's flat/base damage component only. Pure AD-ratio components (e.g. Aatrox/Bel'Veth AD lashes) do not scale with AP — matching TFT's per-star ability data.

---

## 🔍 Detailed Champion Breakdowns

### 1. Aatrox 😈
*   **Detailed Math & Formula Proofs**: See [aatrox-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/aatrox-dps-calculation.md)
*   **Combat Role & Mechanics**: Frontline physical transformation carry. Transforms, gaining Omnivamp and converting bonus AS to AD. Attacks deal physical damage in an area (assumed 1 adjacent target average).
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS*: **96.0 / 144.0 / 216.0**
    *   *Well-Equipped (3-Item) Total DPS*: **263.4 / 395.2 / 592.7**
*   **Aesthetic Balance Note**: Pure AD transformation scaling makes his area slashes highly devastating.

---

### 2. Ahri 🦊
*   **Detailed Math & Formula Proofs**: See [ahri-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/ahri-dps-calculation.md)
*   **Combat Role & Mechanics**: Backline AP carry. Steals essence dealing magic damage. Every 3rd cast fires a massive wave dealing magic damage to all enemies hit (assumed 5 wave targets + 2 essence targets average).
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS*: **126.5 / 187.8 / 835.4**
    *   *Well-Equipped (3-Item) Total DPS*: **323.5 / 478.8 / 2418.5**
*   **Aesthetic Balance Note**: Wave hit density provides exceptional multi-target wipe capability.

---

### 3. Bel'Veth 👑
*   **Detailed Math & Formula Proofs**: See [belveth-dps-calculation.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/docs/balance/calculations/belveth-dps-calculation.md)
*   **Combat Role & Mechanics**: Frontline physical carry. Lashes out rapid strikes, dealing physical damage + target max health true damage execute component (standardized around a 2000 HP target).
*   **Key DPS Outputs**:
    *   *Baseline (Unequipped) Total DPS*: **132.8 / 199.2 / 886.1**
    *   *Well-Equipped (3-Item) Total DPS*: **275.3 / 413.0 / 1696.9**
*   **Aesthetic Balance Note**: True damage percentage execute renders health-stacking tanks ineffective against her.
