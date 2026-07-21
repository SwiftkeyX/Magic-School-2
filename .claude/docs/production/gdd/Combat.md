# Combat

> **Status**: Approved
> **Last Updated**: 2026-07-13
> **Implements Pillar**: (pillars TBD — game-vision.md not yet authored)

## Summary

Combat is the auto-resolved battle: once `BeginBattle()` is called the player does not act again. `AutoBattleSimulator` steps a fixed-rate tick simulation in which every unit runs **two independent clocks** — one for attacking, one for moving — until one side is wiped or the tick cap is hit. It is the only system that mutates `HeroDataRuntime` state during a fight; everything visual is a subscriber.

> **Quick reference** — Layer: `Core` · Priority: `MVP` · Key deps: `Hero`, `Trait`, `Skill`, `HexGrid`

---

## Overview

The player arranges heroes on a hex board, presses go, and watches. Each tick (0.1s by default) every living unit charges both of its clocks. When a unit's attack clock fills it strikes whatever is within its `Range`; when its move clock fills and nothing is in range, it steps one hex toward the nearest enemy. The battle ends when one team has no survivors, or at the tick cap, where the side with more units standing is declared the winner.

## Player Fantasy

"My composition fights for me." The player's agency is entirely in the setup — who is fielded, where they stand, which traits are active. The battle must therefore be *legible*: a unit's behavior should be explainable from its stats alone, with no hidden couplings the player cannot see.

---

## Detailed Design

### Core Rules

1. **The simulation is the only writer.** `AutoBattleSimulator` is the sole mutator of `HeroDataRuntime` state during a battle. The view (`BattleBoardManager`) reacts to events (`OnCombatantActed`, `OnCombatantMoved`, `OnCombatantDefeated`, `OnBattleComplete`) and never writes back.
2. **Every unit runs two independent clocks.** Both are `0 → 1` fractions of one cycle, not countdown timers.
   - `HeroDataRuntime.AttackCooldown` charges at **`AttackSpeed × _tickDelay`** per tick — **per-unit**.
   - `HeroDataRuntime.MoveCooldown` charges at **`_moveSpeed × _tickDelay`** per tick — **shared**, the same value for every unit on the board.
3. **`AttackSpeed` governs attack cadence and nothing else.** It does not affect movement. Movement pace is uniform across all heroes **by design** — a hero that swings faster does not walk faster.
4. **Each tick runs four phases, in this order:**
   1. **Charge** — every living unit accrues both clocks.
   2. **Attack** — units with `AttackCooldown ≥ 1.0` **and a target within `Range`** attack, then subtract `1.0`. Processed in descending `AttackSpeed` order. A unit with nothing in range does **not** act here and does **not** lose its charge.
   3. **Move** — units with `MoveCooldown ≥ 1.0` **and no target in range** step one hex toward the nearest opponent, then subtract `1.0`.
   4. **Clamp** — both clocks are capped at `1.0`.
5. **A unit either attacks or moves in a tick, never both.** Having a target in range suppresses movement; the unit stands and fights.
6. **The attack clock keeps charging while a unit walks.** A unit therefore arrives in range with an attack ready and strikes immediately. **Moving no longer costs a unit its attack.**
7. **Subtracting `1.0` (rather than resetting to `0`) is load-bearing.** The overflow carries into the next cycle, which is what keeps `AttackSpeed` continuous instead of quantised to the tick rate: at `_tickDelay = 0.1`, `AttackSpeed` 0.35 and 0.30 must remain genuinely different.
8. **The clamp is a separate phase and must stay one.** See *Why the clamp is its own phase* below — folding it into the charge silently breaks Rule 7.
9. **A battle ends** when either team has no living combatants. If `_maxBattleTicks` is reached first, the team with more surviving units wins and the result is flagged `TimedOut`.
10. **`SpeedMultiplier` scales only the wall-clock wait between ticks — never the simulation step.** The outcome of a battle is identical at any playback speed. Speeding up what you watch must never change who wins.

### Why the clamp is its own phase

**A trap worth recording.** The obvious implementation — clamping during the charge, `Min(x + delta, 1f)` — quietly destroys Rule 7. A unit sitting at `1.02` gets pinned to `1.0`; it attacks, subtracts `1.0`, and lands on `0.0` instead of `0.02`. It loses a sliver of progress on **every single cycle**, and attack speed is re-quantised to the tick rate — exactly the property Rule 7 exists to protect.

Clamping *after* the action phases only touches units that **could not act** (they walked all tick, or stood in range banking move charge). A unit that attacked has already subtracted `1.0` and sits below the cap, so its overflow survives untouched.

The clamp's actual job is to stop **banking**: without it, a unit that walked 30 ticks would arrive holding 1.8 attacks and burst on contact. With it, a unit arrives with **exactly one** attack ready.

### States and Transitions

A combatant is **Alive** (`CurrentHP > 0`) or **Defeated**. Defeat is terminal — there is no revive, and a defeated unit's grid cell is released immediately. Within Alive, a unit is *engaging* (a target is within `Range`; it attacks, it does not move) or *approaching* (nothing in range; it moves, it does not attack). The transition is re-evaluated every tick from board position — there is no committed state to exit.

### Interactions with Other Systems

| System | Interaction |
|---|---|
| Hero | `HeroDataSO.ToCombatData(team)` seeds each `HeroDataRuntime`'s stats. The resolver reads them; it never writes back to the asset. |
| Trait | `ApplyTraitBonuses()` runs **once**, at the top of `BeginBattle()`, before the loop — flat `StatBonus` deltas applied to trait members per team. |
| Skill | Mana is gained per **attack**; at `MaxMana` the next attack is empowered by `SkillMultiplier`. |
| HexGrid | Owns occupancy (`SetOccupant` / `ClearOccupant`) and pathing (`FindNearest`, `GetNextStep`). The resolver asks; the grid answers. |
| BattleBoardManager | Subscribes to the resolver's events to drive sprites. Enemy placements come from `GetAutoEnemyPlacements()` — the **same** method the simulation places from, so view and sim cannot desync. |

---

## Formulas

### The two clocks

```
AttackCooldown += AttackSpeed × _tickDelay      // per-unit
MoveCooldown   += _moveSpeed   × _tickDelay      // shared by every unit

attack when  AttackCooldown >= 1.0  AND  a target is within Range   → AttackCooldown -= 1.0
move   when  MoveCooldown   >= 1.0  AND  no target is within Range  → MoveCooldown   -= 1.0

then, every tick:  AttackCooldown = min(AttackCooldown, 1.0)
                   MoveCooldown   = min(MoveCooldown,   1.0)
```

| Variable | Type | Range | Source | Description |
|---|---|---|---|---|
| `AttackSpeed` | float | 0.05–1.0 | `HeroDataSO` (per hero) | attacks per second |
| `_moveSpeed` | float | 0.1–3.0 | Inspector (resolver) | hexes per second — **identical for every unit** |
| `_tickDelay` | float | 0.02–0.5 | Inspector (resolver) | seconds per simulation tick |

**Edge cases**: `AttackSpeed` is floored at `0.05` by `HeroDataSO` (see Hero.md) — at `0` a unit would still walk, but never swing.

---

## Edge Cases

| Scenario | Expected Behavior | Rationale |
|---|---|---|
| Unit walks a long distance, then arrives in range | Attacks **once** immediately, then settles into its normal cadence | The clamp caps banked charge at one attack — no burst on contact |
| Unit stands in range for a long fight | Move charge sits pinned at `1.0`; it steps the instant its target dies and the next is out of range | No ramp-up lag after a kill |
| Both teams' last units die on the same tick | Battle ends; `Won` is evaluated from surviving player units (none → loss) | Win check runs after each actor resolves |
| Tick cap reached with both sides alive | Side with more survivors wins, `TimedOut = true` | A battle must always terminate |
| `AttackSpeed = 0` slips through | Unit walks to the enemy and never attacks — the fight runs to the tick cap | Guarded by `HeroDataSO`'s `MinAttackSpeed` floor, not by this system |

---

## Dependencies

| System | Direction | Nature |
|---|---|---|
| Hero | This depends on it | Data dependency — `HeroDataRuntime` stats seeded from `HeroDataSO` |
| Trait | This depends on it | Ownership handoff — `ApplyTraitBonuses()` mutates `HeroDataRuntime` stats before the loop |
| Skill | This depends on it | Rule dependency — mana per attack; empowered hit |
| HexGrid | This depends on it | Data dependency — occupancy and next-step pathing |
| BattleBoardManager | It depends on this | State trigger — subscribes to the resolver's events to drive the view |

---

## Tuning Knobs

| Parameter | Default | Safe Range | Effect of Increase | Effect of Decrease |
|---|---|---|---|---|
| `_moveSpeed` | 0.65 | 0.1–3.0 | units close distance faster; melee comps get stronger | slower approach; ranged comps get stronger |
| `_tickDelay` | 0.1 | 0.02–0.5 | coarser simulation, cheaper | finer resolution, more ticks per second |
| `_maxBattleTicks` | 1200 | 100–5000 | longer cap before a timeout | battles time out sooner |

> `_moveSpeed` is the **only** movement knob in the game. It is shared, not per-hero.

---

## Consequences of the two-clock model

Recorded because both were true *before* this design and silently stopped being true:

- **No trait can affect movement.** `StatBonus` (Trait.md) carries an `AttackSpeed` delta but has **no** `MoveSpeed` field. Under the old single-clock model an attack-speed trait bonus secretly buffed movement too. That is now impossible — a deliberate consequence, not an oversight. Giving traits a movement bonus means adding `MoveSpeed` to `StatBonus` **and** making movement per-unit first.
- **Skills fire earlier than they used to.** Mana is gained per attack (Skill.md), and units no longer forfeit attacks to walk. More attacks land per battle, so mana charges faster.

---

## UI Requirements

| Information | Display Location | Update Frequency | Condition |
|---|---|---|---|
| Unit HP, position, defeat state | Board sprites | On each resolver event | During battle |
| Battle result (win/lose) | Battle HUD | On `OnBattleComplete` | At battle end |

---

## Cross-References

| This Doc References | Target Doc | Element Referenced | Nature |
|---|---|---|---|
| Seeds combatant stats | `production/gdd/Hero.md` | `HeroDataSO.ToCombatData()`, `AttackSpeed` | Data dependency |
| Applies synergy bonuses at start | `production/gdd/Trait.md` | `ApplyTraitBonuses()`, `StatBonus` | Ownership handoff |
| Mana gain and empowered hit | `production/gdd/Skill.md` | `ManaPerAttack`, `SkillMultiplier` | Rule dependency |

---

## Acceptance Criteria

- [ ] Two heroes with **different** `AttackSpeed` step at the **same** cadence — movement is visibly uniform.
- [ ] Those same two heroes still attack at **different** rates — the clocks are genuinely independent.
- [ ] A unit that crosses the board attacks **once** on arrival, not a burst.
- [ ] Attack speed stays continuous: `AttackSpeed` 0.30 and 0.35 produce measurably different attack counts, not the same tick-quantised count.
- [ ] A battle always terminates — by wipe, or by the `_maxBattleTicks` cap with `TimedOut = true`.
- [ ] `SpeedMultiplier` changes only how fast the battle is *watched*; the winner and tick count are identical at any speed.
- [ ] No hardcoded values — `_moveSpeed`, `_tickDelay`, `_maxBattleTicks` are all Inspector-exposed.

---

## Open Questions

| Question | Owner | Deadline | Resolution |
|---|---|---|---|
| Should `_moveSpeed` become a per-hero stat (a "fast" archetype)? | designer | — | **No, deliberately.** The requirement is that every hero shares one default movement speed. Revisit only with a hero concept that needs it — it would mean a `MoveSpeed` on `HeroDataSO` and a `MoveSpeed` on `StatBonus`. |
| Should a unit be able to move *and* attack in the same tick? | designer | — | No — in-range suppresses movement. Keeps the sim legible. |
