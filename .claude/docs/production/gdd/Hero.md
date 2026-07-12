# Hero

> **Status**: Approved
> **Last Updated**: 2026-07-12
> **Implements Pillar**: (pillars TBD — game-vision.md not yet authored)

## Summary

A Hero is the data definition of a fieldable unit: its identity, base combat stats, cost, and the Traits it carries. Heroes are authored as `ScriptableObject` assets so designers add or tune units in the Inspector with no recompile. At battle setup a Hero is projected into a runtime `UnitCombatData` for a given team; combat itself is owned by the Combat system, not Hero.

> **Quick reference** — Layer: `Feature` · Priority: `MVP` · Key deps: `Trait`, `Combat (AutoBattleResolver)`

---

## Overview

The base auto-chess needs units that are *data*, not hardcoded structs. `HeroData` is that data: one asset per unit (Warrior, Mage, Archer, …). Each carries base stats and a list of `TraitData` references. When a match is seeded, each Hero is converted to a `UnitCombatData` tagged with its `Team` (Player or Enemy); the resolver builds a runtime `Combatant` from that. This decouples "what a unit is" (authored content) from "how it fights" (the resolver).

## Player Fantasy

The player is assembling a squad of distinct, recognizable characters — each Hero should read at a glance as a role (tanky frontliner, fragile mage, long-range archer) whose traits hint at how it combos with others.

---

## Detailed Design

### Core Rules

1. A Hero is a `HeroData : ScriptableObject` created via `Assets/Create → MagicSchool/Hero`.
2. A Hero holds: `Id`, `DisplayName`, `Cost` (reserved for a future shop; default 1), base stats (`MaxHP`, `ATK`, `DEF`, `MG`, `MR`, `CRIT`, `AttackSpeed`, `Range`), skill params (`MaxMana`, `ManaPerAttack`, `SkillMultiplier`, `SkillName` — see `Skill.md`), `Flags` (`BattleBehaviorFlag` list), and `Traits` (`List<TraitData>`).
3. `HeroData.ToCombatData(Team team)` returns a `UnitCombatData` copy stamped with `team`, its stats, `Flags`, and `Traits`. It never mutates the asset.
4. Heroes carry base stats only. Trait bonuses are applied later by the Trait system at battle start — a Hero asset never bakes in synergy bonuses.
5. Seed sources (`StudentRosterStub` for players, `EnemyDatabaseStub` for enemies) expose `List<HeroData>` and return `UnitCombatData` via `ToCombatData(team)`.

### Interactions with Other Systems

| System | Interaction |
|---|---|
| Combat (`AutoBattleResolver`) | `SetCombatants(List<UnitCombatData>)` consumes the projected data; the resolver builds runtime `Combatant`s. Hero provides data in; owns no combat logic. |
| Trait | Hero exposes `Traits` (`List<TraitData>`). The Trait synergy pass reads these off the resulting `Combatant`s; Hero neither counts nor applies synergies. |
| Skill | Hero provides the skill params (`MaxMana`/`ManaPerAttack`/`SkillMultiplier`/`SkillName`) consumed by the mana/empower loop in `Attack()`. See `Skill.md`. |
| Seed sources (`StudentRosterStub`, `EnemyDatabaseStub`) | Hold the authored `HeroData` roster and convert to `UnitCombatData` per team. |

---

## Data Model

### `UnitCombatData` (unified runtime-seed contract)

Replaces the former `StudentCombatData` + `EnemyCombatData` (the duplication was flagged in-code). One serializable type, tagged by `Team`.

| Field | Type | Notes |
|---|---|---|
| `Id`, `DisplayName` | string | |
| `Team` | `Team` enum (`Player`/`Enemy`) | Replaces the implicit student/enemy split |
| `MaxHP`, `ATK`, `DEF`, `MG`, `MR`, `CRIT` | int | Base stats |
| `AttackSpeed` | float | Attacks per second |
| `Range` | int | 1 = melee |
| `MaxMana`, `ManaPerAttack` | int | Skill charge (0 MaxMana = no skill) — see `Skill.md` |
| `SkillMultiplier` | float | Empowered-hit multiplier (e.g. 2.0) |
| `SkillName` | string | Display name of the skill |
| `Flags` | `List<BattleBehaviorFlag>` | e.g. `MagicAttack` |
| `Traits` | `List<TraitData>` | Direct SO references |

---

## Edge Cases

| Scenario | Expected Behavior | Rationale |
|---|---|---|
| Hero has an empty/null `Traits` list | Converts fine; contributes to no synergy | Traitless units are valid |
| Two Heroes share the same `Id` | Allowed at data level; `Id` is a display/lookup key, runtime `Combatant`s are distinguished per instance | Base game has no 3-combine identity rule yet |
| `ToCombatData` called repeatedly | Returns independent copies; asset never mutated | Assets are read-only content |

---

## Dependencies

| System | Direction | Nature |
|---|---|---|
| Trait | This depends on it | Data dependency — Hero references `TraitData` |
| Skill | It depends on this | Data dependency — Skill loop reads Hero's mana/skill params |
| Combat (`AutoBattleResolver`) | It depends on this | Data dependency — resolver consumes `UnitCombatData` |

---

## Tuning Knobs

| Parameter | Default | Safe Range | Effect of Increase | Effect of Decrease |
|---|---|---|---|---|
| `MaxHP` | per-hero | 30–800 | tankier | squishier |
| `ATK` / `MG` | per-hero | 0–80 | more damage | less damage |
| `DEF` / `MR` | per-hero | 0–50 | more mitigation | less mitigation |
| `AttackSpeed` | per-hero | 0.2–1.0 | acts more often | acts less often |
| `Range` | 1 | 1–4 | attacks from further | must close distance |
| `Cost` | 1 | 1–5 | (reserved for future shop) | — |

---

## Acceptance Criteria

- [ ] `HeroData` assets can be created via `MagicSchool/Hero` and edited in the Inspector.
- [ ] `ToCombatData(team)` produces a `UnitCombatData` with correct stats, `Team`, `Flags`, and `Traits`, without mutating the asset.
- [ ] Seed sources build the battle roster from `HeroData` assets. Base roster: one melee (Knight, range 1) + one ranged (Archer, range 2), each with a Skill and the shared Fighter trait; a mirror match fields the same two on both teams.
- [ ] No hardcoded unit stats remain in seed code — all live on assets.

---

## Cross-References

| This Doc References | Target Doc | Element Referenced | Nature |
|---|---|---|---|
| Hero carries traits | `production/gdd/Trait.md` | `TraitData` list | Data dependency |
| Hero data feeds combat | (Combat resolver) | `SetCombatants(List<UnitCombatData>)` | Data dependency |

---

## Open Questions

| Question | Owner | Deadline | Resolution |
|---|---|---|---|
| Do enemies participate in synergies in the base game? | designer | — | Yes — synergies are counted per-team, so enemy comps can gain traits too |
