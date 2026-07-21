# Balance Framework

> **Status**: Active  
> **Scope**: Cross-phase — governs all champion stat and trait tuning decisions  
> **Tools**: `Assets/Editor/BalanceValidator.cs` (simulation runner)

---

## Overview

How do we make sure our game champions are balanced (neither too weak nor too strong)? We use a **three-step process** to design, calculate, and test their power:

1. **Step 1: Under the Hood (Mechanics)**: We configure how champions attack and gain energy (mana) to cast spells. We use a smooth "accumulator" system so attack speed bonuses feel responsive and fair.
2. **Step 2: On Paper (Math & Budgeting)**: We use a mathematical formula (the **Stat Budget Score**) to calculate a power rating for each champion based on their attack, speed, and health. Each champion's gold-cost tier has a target rating they must hit to ensure high-cost units are appropriately stronger than low-cost ones.
3. **Step 3: In Action (Simulations)**: We run simulated battles (200 fights per matchup) inside Unity to check who actually wins. This confirms that the math translates to actual balanced gameplay.

**Rule of Thumb**: Before changing any champion stats, we must first run the math (Step 2) to check if they are in range, and then run simulations (Step 3) to verify they behave correctly in combat.

---

## Layer 1 — Attack Speed Accumulator

### Tick Rate

The resolver runs at **0.1s per tick** (10 ticks/second), matching TFT's resolution.  
`MaxBattleTicks = 1200` (120s ceiling).

### Accumulator Logic

Each unit has a float `ActionProgress` that starts at `0.0f`. Each tick:

```
ActionProgress += AttackSpeed × TickDelay   (= AttackSpeed × 0.1)
```

When `ActionProgress >= 1.0f`, the unit acts and we subtract 1.0 (overflow carries forward):

```
ActionProgress -= 1.0f
```


### Trait Speed Bonuses

Trait bonuses multiply `AttackSpeed` directly before the battle loop (in `ApplyPreBattleTraitModifiers`). Because accumulation uses `AttackSpeed × TickDelay` each tick, the effect is immediate and linear.

| Trait effect | AS multiplier | Effective DPS change |
|---|---|---|
| Ranger BP2 / Warden BP3 | ×1.176 | +17.6% |
| Warden BP4 | ×1.429 | +42.9% |
| Striker max-stack (inline) | ÷0.70 on `gain` | +42.9% while at 8 stacks |

---

## Layer 1b — Mana & Ability Casting

All units gain mana through combat. When `Mana >= MaxMana`, the unit casts its ability (currently a placeholder bonus attack) and mana resets to 0.

### Mana Sources

| Source | Amount |
|---|---|
| Per auto-attack (attacker) | +10 flat |
| Per hit received (defender) | +`clamp(round(preMitDamage × 0.08 / MaxHP × 100), 1, 40)` — 8% of pre-mitigation damage measured as a % of the defender's MaxHP, clamped to 1–40 mana per hit (see `ActiveSkillSystem.md`, `ManaDamageMultiplier = 0.08`) |
| Kinetic trait tick (every 3s) | +5 or +15 depending on BP |
| Kinetic BP4 starting bonus | +30 starting mana at battle start |

> **Why pre-mitigation for on-hit mana?** A tank with 300 DEF would otherwise gain 4× less mana per hit than a squishy carry struck by the same attack. Pre-mitigation keeps mana gain fair across all archetypes.

### Per-Champion Mana Pools

| Champion | MaxMana | StartingMana | Profile |
|---|---|---|---|
| Ironclad | 100 | 0 | Utility tank |
| Bloodhound | 50 | 0 | Spam carry |
| Pyromancer | 50 | 0 | Spam AP carry |
| Windrunner | 50 | 0 | Spam carry |
| Grove Keeper | 80 | 0 | Support |
| Shadowblade | 40 | 0 | Hyper-spam carry |
| Phalanx | 120 | 30 | CC tank (casts once early) |
| Stormbringer | 80 | 0 | Support |
| Phantom Assassin | 60 | 0 | Burst carry |
| Dread Overlord | 150 | 50 | Hyper-tank (long windup) |

---

## Layer 2 — Stat Budget Score

### Formula

```
Score = Offense × AttackSpeed × sqrt( HP × (100 + DEF) / 100 )

Offense = ATK  (physical units)
Offense = MG   (Elementalists and Supports where MG > ATK)
```

**Offense × AS** = raw DPS at 0 armor.  
**sqrt(EHP)** = square root of effective physical HP (reduces tank weight to reflect team-fight realism).

> **Why √EHP?** Pure DPS × EHP measures a unit's theoretical duel power in a vacuum, which over-scores tanks because of their massive EHP. In team combat, a tank's damage output is rarely focused on carries, and tanks are prone to being CC'd or ignored, while carries deal damage from safety. Taking the square root of EHP dampens the weight of raw health and armor so the score reflects a unit's true utility in a dynamic team fight.

> CRIT, traits, shields, omnivamp, Striker stacks excluded — base stats only.

### Target Score Bands (by cost tier, unified across roles)

| Tier | Score range |
|---|---|
| 1c | 900 – 1100 |
| 2c | 950 – 1300 |
| 3c | 1200 – 1450 |
| 4c | ~2200 |
| 5c | ~2500 |

> Bands are **monotonic**: each tier's floor and ceiling sit above the previous tier's, so a balanced higher-cost unit always outscores a balanced lower-cost one. (Fixed 2026-07-06 — previously 2c's ceiling (1450) exceeded 3c's (1350) and the 5c target (~2100) sat below 4c's (~2200).)

### Current Scores (all 30 champions)

> Generated by `python .claude/scripts/balance_report.py` (2026-07-02) from live sheet + `ChampionRoster.cs`.
> The 4c/5c "~" targets are checked with a ±10% tolerance.

| Champion | Cost | Role | Score | In band? |
|---|---|---|---|---|
| Aegis | 1c | Tank | 25 | ❌ legacy scale |
| Bloodhound | 1c | Carry | 1010 | ✅ |
| Cosmic Sprite | 1c | Support | 40 | ❌ legacy scale |
| Ironclad | 1c | Tank | 921 | ✅ |
| Novice Cleric | 1c | Support | 37 | ❌ legacy scale |
| Pyromancer | 1c | Carry | 1092 | ✅ |
| Tech Scrapper | 1c | Carry | 43 | ❌ legacy scale |
| Wildcat | 1c | Carry | 42 | ❌ legacy scale |
| Forest Sentinel | 2c | Tank | 26 | ❌ legacy scale |
| Grove Keeper | 2c | Support | 979 | ✅ |
| Shadowblade | 2c | Carry | 1400 | ❌ above new 2c band (≤1300) |
| Sun Warden | 2c | Tank | 28 | ❌ legacy scale |
| Venom Stalker | 2c | Carry | 56 | ❌ legacy scale |
| Void Mage | 2c | Carry | 57 | ❌ legacy scale |
| Windrunner | 2c | Carry | 1395 | ❌ above new 2c band (≤1300) |
| Night Stalker | 3c | Carry | 80 | ❌ legacy scale |
| Phalanx | 3c | Tank | 1247 | ✅ |
| Rust Colossus | 3c | Tank | 45 | ❌ legacy scale |
| Starweaver | 3c | Support | 89 | ❌ legacy scale |
| Storm Ranger | 3c | Carry | 67 | ❌ legacy scale |
| Stormbringer | 3c | Support | 1346 | ✅ |
| Arcane Sage | 4c | Carry | 137 | ❌ legacy scale |
| Divine Paladin | 4c | Support | 64 | ❌ legacy scale |
| Grave Knight | 4c | Tank | 62 | ❌ legacy scale |
| Phantom Assassin | 4c | Carry | 2248 | ✅ |
| Void Ranger | 4c | Carry | 100 | ❌ legacy scale |
| Beastmaster | 5c | Tank | 87 | ❌ legacy scale |
| Cosmic Leviathan | 5c | Tank | 134 | ❌ legacy scale |
| Dread Overlord | 5c | Tank | 2080 | ❌ below new 5c target (~2500 ±10%) |
| Reaper | 5c | Carry | 203 | ❌ legacy scale |

> **Known roster split**: the original 10 champions are TFT-aligned; the 20 batch
> champions (#11–#30) still use the legacy small stat scale (an explicitly accepted
> known gap per `ChampionRoster.cs` batch comments) and score at 3–11% of their band
> floor. Rescaling them is a pending `/code` task.
>
> **Zero-damage skills found**: Dread Overlord (Dread Cataclysm) and Sun Warden
> (Solar Flare) have `UsesMagicOffense = true` but `MG = 0` — their skills currently
> deal 0 damage.

---

## Layer 3 — Simulation Validation

### Tool

`Assets/Editor/BalanceValidator.cs` — Unity menu: **Magic School → Validate Balance**

Runs 200 1v1 battles for all 10×10 champion pairs, synchronous (no coroutines).
Prints a win-rate matrix and flags matchups outside the expected band.

### Expected Win-Rate Bands

| Cost difference | Expected win % for the higher-cost unit |
|---|---|
| +1 (e.g. 2c vs 1c) | 55 – 80% |
| +2 (e.g. 3c vs 1c) | 70 – 92% |
| +3 (e.g. 4c vs 1c) | 80 – 96% |
| +4 (e.g. 5c vs 1c) | 88 – 98% |

> Units at the same cost tier should win ~45–55% of their mirror matchup.

### Simulation Rules

- Base stats only (no traits, no shields, no Striker stacks, no mana/abilities)
- `IncludeCrit = false` by default — set to `true` to check CRIT variance impact
- Movement ignored — both units start in range (pure 1v1 DPS race)
- Float accumulator mirrors the resolver exactly
- Timeout at 1200 ticks: winner is the unit with more HP remaining

---

## Workflow (sheet-driven)

The Google Sheet is the design source of truth (see the `sync-sheet` skill); numeric
stats live in `ChampionRoster.cs` and must stay in sync with it.

Run **`/balance-pass`** to execute the full loop end to end, or invoke its steps individually:

1. **`/check-balance`** — reads the Heroes/Origin/Class tabs live, parses `ChampionRoster.cs`,
   and reports the sheet↔code **consistency gate**, Layer 2 scores vs. tier bands, skill/mana
   cycle stats, and the live trait tables. Resolve any consistency-gate mismatches first — a
   champion whose sheet row and code stats disagree cannot be meaningfully balanced.
2. **`/tune-champion`** — per out-of-band champion, proposes and applies one stat change at a
   time until the Score is in band.
3. **`/validate-balance`** — runs **Magic School → Validate Balance** and checks the printed
   win-rate outlier list; routes back to `/tune-champion` if outliers are found.
4. **`/push-champion-stats`** — refreshes the sheet's stat mirror, updates the champion stat
   table in `TraitSystem.md`, and regenerates the "Current Scores" table above.

---

## Cross-References

| This doc references | Target | Nature |
|---|---|---|
| Champion stats | `TraitSystem.md` | Source of truth for all HP/ATK/DEF/MG/MR/AS/CRIT/Range values |
| AS accumulator | `AutoBattleSimulator.cs` | `ActionProgress` field, BattleLoop accumulation block |
| Simulation tool | `Assets/Editor/BalanceValidator.cs` | Implementation |
