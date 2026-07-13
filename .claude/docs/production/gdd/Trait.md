# Trait

> **Status**: Approved
> **Last Updated**: 2026-07-13
> **Implements Pillar**: (pillars TBD — game-vision.md not yet authored)

## Summary

A Trait is a synergy tag shared by Heroes. Fielding enough Heroes with the same Trait activates a breakpoint that grants a flat stat bonus to the units that carry it. Traits are `ScriptableObject` assets with ascending unit-count breakpoints; the synergy pass runs once at battle start. This is the genre's core "build a team that combos" hook, in its simplest form — flat stat bonuses only, no active abilities.

> **Quick reference** — Layer: `Feature` · Priority: `MVP` · Key deps: `Hero`, `Combat (AutoBattleResolver)`

---

## Overview

Traits turn a collection of Heroes into a *composition*. Each `TraitData` defines breakpoints (e.g. 2 units → small buff, 4 units → bigger buff). At battle start, for each team, the system counts how many fielded Heroes carry each Trait, selects the highest satisfied breakpoint, and applies that breakpoint's flat stat bonus to every unit on that team that has the Trait. The player's incentive is to field Heroes that share Traits to cross breakpoints.

## Player Fantasy

"My squad is more than the sum of its parts." The player should feel rewarded for recognizing and completing synergies — three Mages hitting a breakpoint should visibly make those Mages hit harder.

---

## Detailed Design

### Core Rules

1. A Trait is a `TraitData : ScriptableObject` created via `Assets/Create → MagicSchool/Trait`, holding `Id`, `DisplayName`, `Description`, and `Breakpoints` (`List<TraitBreakpoint>`).
2. A `TraitBreakpoint` holds `UnitCount` (the threshold), a `StatBonus` (flat additive deltas), and a `Description`. Breakpoints are authored in ascending `UnitCount` order.
3. `StatBonus` is a serializable struct of flat additive deltas: `HP`, `ATK`, `DEF`, `MG`, `MR` (int) and `AttackSpeed` (float). It has `ApplyTo(Combatant)`. Flat additive only — no percentages, no active effects.
4. The synergy pass (`AutoBattleResolver.ApplyTraitBonuses()`) runs **once at the top of `BeginBattle()`**, before the battle loop, after placements are known.
5. Counting is **per team**: for each team independently, count the number of **distinct fielded Heroes** carrying each Trait.
6. For each Trait, select the **highest** `TraitBreakpoint` whose `UnitCount ≤ count` (`TraitData.GetActiveBreakpoint(count)`). If the count is below the first breakpoint, the Trait is inactive and grants nothing.
7. The selected breakpoint's `StatBonus` is applied to **every combatant on that team that carries the Trait** ("trait members benefit"). Units without the Trait are unaffected.
8. Bonuses are additive to base stats and applied once (not per tick). `MaxHP` increases also raise `CurrentHP` by the same amount so the unit starts at full effective HP.
9. Each activated Trait + breakpoint is logged (`Debug.Log`) for verification.
10. `GetActiveTraits(Team)` exposes `(TraitData, count, activeBreakpoint)` for a future HUD synergy panel. (UI display is out of scope for this pass.)

### States and Transitions

A Trait is either **Inactive** (count below first breakpoint) or **Active at breakpoint N** (count ≥ breakpoint N's `UnitCount`, N highest satisfied). Evaluated once at `BeginBattle()`; no mid-battle re-evaluation in the base game (no unit is added/removed during a fight except by death, which does not re-trigger synergy).

---

## Formulas

### Trait activation

```
count(team, trait)        = number of distinct fielded Heroes on `team` whose Traits contains `trait`
activeBreakpoint(trait)   = argmax over breakpoints b where b.UnitCount <= count : b.UnitCount   (null if none)
finalStat(unit)           = baseStat(unit) + Σ activeBreakpoint(trait).Bonus.stat  for each trait the unit carries
```

| Variable | Type | Range | Source | Description |
|---|---|---|---|---|
| `count` | int | 0–squad size | computed | distinct heroes with the trait on that team |
| `UnitCount` | int | 1–9 | ScriptableObject (`TraitBreakpoint`) | breakpoint threshold |
| `Bonus.*` | int/float | flat | ScriptableObject (`StatBonus`) | additive stat delta |

**Edge cases**: a unit carrying two active traits stacks both bonuses additively; below-breakpoint traits contribute 0.

---

## Edge Cases

| Scenario | Expected Behavior | Rationale |
|---|---|---|
| Count below first breakpoint | Trait inactive, no bonus, no log line | Synergy not yet earned |
| Unit carries two active traits | Both `StatBonus`es apply additively | Multi-trait heroes are the point of comping |
| `MaxHP` bonus applied | `CurrentHP` raised by the same delta | Unit should start at full effective HP |
| Enemy team also completes a trait | Enemy units get their own bonus (counted separately) | Per-team counting; future-proofs enemy comps |
| Duplicate `TraitData` reference on one Hero | Counted once per Hero | Distinct-hero count, not reference count |

---

## Dependencies

| System | Direction | Nature |
|---|---|---|
| Hero | This depends on it | Data dependency — reads `Combatant.Traits` (sourced from `HeroData.Traits`) |
| Combat (`AutoBattleResolver`) | Ownership handoff | The synergy pass is a method on the resolver, invoked at `BeginBattle()`, mutating `Combatant` stats before the loop |

---

## Tuning Knobs

| Parameter | Default | Safe Range | Effect of Increase | Effect of Decrease |
|---|---|---|---|---|
| `TraitBreakpoint.UnitCount` | per-breakpoint | 2–9 | harder to activate | easier to activate |
| `StatBonus.ATK/MG` | per-breakpoint | 0–40 | stronger offense synergy | weaker |
| `StatBonus.DEF/MR` | per-breakpoint | 0–30 | tankier synergy | weaker |
| `StatBonus.HP` | per-breakpoint | 0–400 | tankier synergy | weaker |
| `StatBonus.AttackSpeed` | per-breakpoint | 0–0.5 | faster synergy | weaker |

---

## Visual / Audio Requirements

| Event | Visual Feedback | Audio Feedback | Priority |
|---|---|---|---|
| Trait activates at battle start | Left-side HUD synergy panel highlights the active trait (gold) vs inactive (grey) | — | Alpha |

## UI Requirements

| Information | Display Location | Update Frequency | Condition |
|---|---|---|---|
| Player's traits + `count/breakpoint`, active vs inactive | Left panel on the Battle HUD (`BattleBoardHUD`, `trait-list`) | On roster set + battle start | Always visible in battle |

> Populated by `BattleBoardManager.RefreshTraitPanel()` from `AutoBattleResolver.GetActiveTraits(Team.Player)`.

---

## Acceptance Criteria

- [ ] `TraitData` assets can be created via `MagicSchool/Trait` with multiple ascending breakpoints, editable in the Inspector.
- [ ] Fielding units meeting a breakpoint applies that breakpoint's `StatBonus` to exactly the trait-carrying units on that team, logged at battle start.
- [ ] Fielding below a breakpoint applies nothing and logs nothing for that trait.
- [ ] A unit with two active traits receives both bonuses additively.
- [ ] Enemy synergies are counted and applied independently of player synergies.
- [ ] No hardcoded bonus values in code — all live on `TraitData`/`StatBonus` assets.

---

## Cross-References

| This Doc References | Target Doc | Element Referenced | Nature |
|---|---|---|---|
| Reads a unit's traits | `production/gdd/Hero.md` | `HeroData.Traits` / `UnitCombatData.Traits` | Data dependency |
| Runs inside the battle setup | (Combat resolver) | `BeginBattle()` → `ApplyTraitBonuses()` | Ownership handoff |

---

## Open Questions

| Question | Owner | Deadline | Resolution |
|---|---|---|---|
| Should some traits buff the whole team, not just members? | designer | — | Not in base game — members-only keeps rules simple; revisit with real content |
| Should synergy re-evaluate mid-battle? | designer | — | No — evaluated once at start for the base game |
