# TFT Balancing Research Roadmap

This document serves as our long-term research plan and tracking document for understanding and applying Teamfight Tactics (TFT) balancing methodologies to our custom auto-battler project.

---

## Methodology (sheet-first)

Three live Google Sheets back this workflow — see `data-sources.md` for the full registry
(spreadsheet keys, tabs, read/write access). Our own **`auto-battler`** sheet is the live
design database (read via the `sync-sheet` skill / `sheet_sync.py`); champion numeric stats
live in `ChampionRoster.cs` and must stay in sync with it. `.claude/scripts/balance_report.py`
is the analysis tool: it reads the Heroes/Origin/Class tabs live, joins code stats, and
applies the framework in `balance-framework.md`. **`tft-set9`** and **`tft-set10`** are
external, read-only reference sheets — TFT's own Set 9/10 champion and trait data — used to
ground the TFT math in `tft-balancing-analysis.md`/`tft-balancing-rules.md` and to cross-check
that formulas (EHP, mana, star scaling) hold across sets. Local JSON snapshots of all three
live under `.claude/reference/json/`, refreshed via `sheet_sync.py --sheet <name> dump`
(see `data-sources.md` for the exact commands) — they are a **reproducible offline mirror**,
not archived-and-abandoned data.

## Roadmap Overview

To establish a mathematically balanced combat system, we are dissecting TFT's mechanics into distinct research topics. Progress will be tracked here.

| Topic | Focus Area | Status | Target Application |
| :--- | :--- | :---: | :--- |
| **Topic 1** | Trait Synergies & Breakpoint Budgeting | **Comp-level pass applied** — breakpoint tables read live by `.claude/scripts/balance_report.py` §4; cross-set meta-comp pattern analysis in `tft-trait-synergy-patterns.md` (avg. active traits per comp, how hard each is pushed); gold-value budgeting still pending | Validate and align Vertical/Horizontal trait weights |
| **Topic 2** | Ability Scaling & Spell Multipliers | **First pass applied** — skill/mana cycle analysis in `.claude/scripts/balance_report.py` §3; TFT-side spell-scaling research still pending | Design our future champion ability system |
| **Topic 3** | Team Combat & Simulation Modeling | **Pending** | Upgrade `BalanceValidator.cs` to test group comps |
| **Topic 4** | Itemization Math & Stat Modifiers | **Pending** | Set up rules for equipment and teacher upgrades |
| **Topic 5** | Shop Economy, Roll Rates & Pool Sizes | **Pending** | Establish recruit/shop probabilities per level |

---

## Detailed Research Topics

### Topic 1: Trait Synergies & Breakpoint Budgeting
* **Objective:** Study how Riot Games calculates and budgets the power added by traits (Origins and Classes) at different breakpoints (e.g., 2, 4, 6, 8).
* **Research Items:**
  * Map out the stat value of active traits in Set 9 (e.g., Bastion's flat Armor/MR, Sorcerer's flat AP, Challenger's Attack Speed).
  * Calculate the "gold value" of trait stats relative to base stats.
  * Research vertical vs. horizontal synergy tradeoffs (e.g., is running 6-Bastion mathematically superior to running 3-Bastion + 2-Invoker?).
  * ✅ **Done:** cross-set meta-comp pattern analysis — see `tft-trait-synergy-patterns.md`. Across all 56 published comps in Set 9/10/11, real comps run **3-5 active traits on average (3.84)**, the primary trait reaches its true max breakpoint only **11%** of the time, and **81%** of secondary/filler traits sit at their cheapest activation tier. The "6-Bastion vs. 3-Bastion + 2-Invoker" question above resolves empirically toward the latter shape — one trait pushed moderately + several cheap fillers, not several traits maxed at once.
* **Magic School Application:** We need to ensure that hitting trait breakpoints (like Warden 4 or Striker 6) grants a balanced power spike that doesn't completely overshadow base champion stats or gold investments. When curating our own meta comps, target the empirical shape above (3-5 active traits, one pushed mid-to-high, rest at floor) rather than designs that max multiple traits simultaneously.

### Topic 2: Ability Scaling & Spell Multipliers
* **Objective:** Understand how TFT balances a champion's spell output against their auto-attack damage, and how spell values scale with star level.
* **Research Items:**
  * Research the typical base spell damage and shield numbers for 1-cost to 5-cost champions at 1, 2, and 3 stars.
  * Analyze the formula for Ability Power (AP) scaling and AD-based physical spells.
  * Determine the ratio of auto-attack DPS to spell DPS for carries.
* **Magic School Application:** This will guide us in expanding our prototype "bonus attack at 100 mana" into a full active ability system with custom spells (e.g., Area-of-Effect stuns, targeted heals, and active shields).

### Topic 3: Team Combat & Simulation Modeling
* **Objective:** Research how team-level dynamics (focus fire, positioning, frontline shielding backline, and target switching) alter balancing compared to isolated 1v1 fights.
* **Research Items:**
  * Analyze how target acquisition rules (nearest unit, lowest health, highest threat) prevent carries from being assassinated immediately.
  * Study Lanchester's Power Laws or similar mathematical models of combat attrition.
  * Determine how tanks' EHP needs to scale as enemy team size increases.
* **Magic School Application:** We will use this research to upgrade `BalanceValidator.cs` to simulate full team-vs-team skirmishes (e.g., $3\text{v}3$ or $4\text{v}4$) with proper front-to-back targeting lines. Specifically, the current validator only runs base-stat 1v1 matchups; it needs:
  * **Synergy matchups**: $4\times4$ simulations with active traits (e.g. a Vanguard-Warden team vs a Striker-Dreadknight team) to see if synergies blow out the balance bands.
  * **Combat variance (CRIT)**: run with `IncludeCrit = true` and check the standard deviation of win rates. If crit causes 1-cost carries to randomly beat 3-cost carries too often, the base crit rate or crit damage multiplier must be lowered.

### Topic 4: Itemization Math & Stat Modifiers
* **Objective:** Examine the math behind items and equipment, specifically how stat additions (flat health/AD) and multipliers (% speed, % damage) interact.
* **Research Items:**
  * Map out the base stats granted by component items vs. completed items in TFT.
  * Research the formula for multiplicative modifiers (e.g., crit chance overflow, omnivamp stacking, damage amplification).
* **Magic School Application:** When we introduce items or meta progression upgrades (like teacher training buffs), we must ensure they multiply stats in a bounded way that doesn't cause stat bloat.

### Topic 5: Shop Economy, Roll Rates & Pool Sizes
* **Objective:** Analyze the relationship between gold economy, shop roll percentages, and champion bag sizes.
* **Research Items:**
  * Catalog the exact shop roll percentages for 1c, 2c, 3c, 4c, and 5c champions at each player level.
  * Study the concept of "champion pool sizes" (bag sizes) and how it creates scarcity when multiple players contest the same units.
* **Magic School Application:** This research will guide our school roster recruit rates. If upgrading a unit to 3-star increases its health and damage by $3.24\times$, the gold and rarity cost must be high enough to match this massive power spike.

---

## Tooling Backlog

Pending tool improvements that support the research topics above:

* **Auto-calculate the Stat Budget Score in the spreadsheet.** Write a script or update `sheet_sync.py` to compute the Layer 2 Stat Budget Score (see `balance-framework.md`) for every champion whenever their stats are edited, highlighting any champion whose score exits its tier's allowed band.
