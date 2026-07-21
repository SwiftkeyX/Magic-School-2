# Hero

> **Status**: Approved
> **Last Updated**: 2026-07-13
> **Implements Pillar**: (pillars TBD — `game-vision.md` exists but is an unfilled template; no pillars are authored yet)

## Summary

A Hero is the data definition of a fieldable unit: its identity, base combat stats, presentation, and the Traits it carries. Heroes are authored as `ScriptableObject` assets so designers add or tune units in the Inspector with no recompile. At battle setup a Hero is projected into a runtime `HeroDataSeed` for a given team; combat itself is owned by the Combat system, not Hero.

> **Quick reference** — Layer: `Feature` · Priority: `MVP` · Key deps: `Trait`, `Combat (AutoBattleSimulator)`

> **Governing rule** — `best-practices.md` → *Tunable Data*: ScriptableObject assets, never hardcoded values. Every authored property of a Hero — **including its visual identity** — lives on the asset. A Hero property that requires a C# edit to take effect is a defect, not a design.

---

## Overview

The base auto-chess needs units that are *data*, not hardcoded structs. `HeroDataSO` is that data: one asset per unit (Warrior, Mage, Archer, …). Each carries base stats and a list of `TraitDataSO` references. When a match is seeded, each Hero is converted to a `HeroDataSeed` tagged with its `Team` (Player or Enemy); the resolver builds a runtime `HeroDataRuntime` from that. This decouples "what a unit is" (authored content) from "how it fights" (the resolver).

## Player Fantasy

The player is assembling a squad of distinct, recognizable characters — each Hero should read at a glance as a role (tanky frontliner, fragile mage, long-range archer) whose traits hint at how it combos with others.

---

## Detailed Design

### Core Rules

1. A Hero is a `HeroDataSO : ScriptableObject` created via `Assets/Create → MagicSchool/Hero`.
2. A Hero holds:
   - **Identity** — `DisplayName`
   - **Presentation** — `Icon` (`Sprite`), `PlayerTint` (`Color`), `EnemyTint` (`Color`). The same Hero fields both teams, tinted differently per side.
   - **Base stats** — `MaxHP`, `ATK`, `DEF`, `MG`, `MR`, `AttackSpeed`, `Range`
   - **Skill params** — `MaxMana`, `ManaPerAttack`, `SkillMultiplier`, `SkillName` (see `Skill.md`)
   - **Traits** — `List<TraitDataSO>`
3. `HeroDataSO.ToCombatData(Team team)` returns a `HeroDataSeed` copy stamped with `team`, its stats, presentation, and `Traits`. It never mutates the asset.
4. Heroes carry base stats only. Trait bonuses are applied later by the Trait system at battle start — a Hero asset never bakes in synergy bonuses.
5. Seed sources (`StudentRosterStub` for players, `EnemyDatabaseStub` for enemies) expose `List<HeroDataSO>` and return `HeroDataSeed` via `ToCombatData(team)`.
6. **There is no per-unit damage-archetype flag.** `BattleBehaviorFlag` (and its sole surviving member, `MagicAttack`) was removed — damage archetype is a property of the *action*, not the unit, so it does not belong on `HeroDataSO` at all. Every attack resolves ATK vs DEF until a real magic-damage mechanic is designed on the skill/action itself (see `Skill.md`).
7. **Presentation is data, never a code lookup.** No system may map a Hero's `Id` to a color, sprite, or any other visual via a hardcoded `switch`/dictionary. Consumers read `Icon`/`PlayerTint`/`EnemyTint` off the `CombatantSnapshot`. This is what makes Acceptance Criterion 1 (below) hold.

### Interactions with Other Systems

| System | Interaction |
|---|---|
| Combat (`AutoBattleSimulator`) | `SetCombatants(List<HeroDataSeed>)` consumes the projected data; the resolver builds runtime `HeroDataRuntime`s. Hero provides data in; owns no combat logic. |
| Trait | Hero exposes `Traits` (`List<TraitDataSO>`). The Trait synergy pass reads these off the resulting `HeroDataRuntime`s; Hero neither counts nor applies synergies. |
| Skill | Hero provides the skill params (`MaxMana`/`ManaPerAttack`/`SkillMultiplier`/`SkillName`) consumed by the mana/empower loop in `Attack()`. See `Skill.md`. |
| Seed sources (`StudentRosterStub`, `EnemyDatabaseStub`) | Hold the authored `HeroDataSO` roster and convert to `HeroDataSeed` per team. |

---

## Data Model

### `HeroDataSeed` (unified runtime-seed contract)

Replaces the former `StudentCombatData` + `EnemyCombatData` (the duplication was flagged in-code). One serializable type, tagged by `Team`.

| Field | Type | Notes |
|---|---|---|
| `DisplayName` | string | |
| `Team` | `Team` enum (`Player`/`Enemy`) | Replaces the implicit student/enemy split |
| `Icon` | `Sprite` | Authored on the asset. Null → the procedural fallback square. |
| `PlayerTint`, `EnemyTint` | `Color` | Per-side tint. Selected by `Team` at projection time. |
| `MaxHP`, `ATK`, `DEF`, `MG`, `MR` | int | Base stats |
| `AttackSpeed` | float | Attacks per second |
| `Range` | int | 1 = melee |
| `MaxMana`, `ManaPerAttack` | int | Skill charge (0 MaxMana = no skill) — see `Skill.md` |
| `SkillMultiplier` | float | Empowered-hit multiplier (e.g. 2.0) |
| `SkillName` | string | Display name of the skill |
| `Traits` | `List<TraitDataSO>` | Direct SO references |

**Removed fields.** `CRIT` and `Cost` were specified here and authored on every Hero asset, but **neither was ever read by any system** — `CRIT` never reached the damage formula, `Cost` had no shop to spend it in. They are removed rather than left inert; see Open Questions.

`Icon`/`PlayerTint`/`EnemyTint` flow onward to **`CombatantSnapshot`** (the read-only UI contract), which is what lets `BattleBoardManager` tint and sprite a unit with no knowledge of what a "knight" is.

---

## Authoring Guardrails

`HeroDataSO` fields carry `[Range]` and `[Tooltip]` attributes, and `OnValidate()` clamps:

| Field | Clamp | Failure it prevents |
|---|---|---|
| `AttackSpeed` | `≥ 0.05` | `0` → `AttackCooldown` never reaches 1.0 → the unit **never attacks**. It still walks (movement is on its own clock — see Combat.md), so it closes on the enemy and then stands there, and the battle silently runs to its 120-second tick cap |
| `MaxHP` | `≥ 1` | `0` → `current/max` = NaN in the health bar, and the unit is defeated on spawn |
| `DEF`, `MR` | `≥ 0` | `-100` → divide-by-zero in `ApplyMitigation`'s `100/(100+DEF)` |
| `SkillMultiplier` | `≥ 1` | `< 1` → the "empowered" hit lands *weaker* than a normal one |

Each of these was authorable before this pass, and each failed **silently**.

---

## Edge Cases

| Scenario | Expected Behavior | Rationale |
|---|---|---|
| Hero has an empty/null `Traits` list | Converts fine; contributes to no synergy | Traitless units are valid |
| Two Heroes are the same type (mirror match, duplicate roster entries) | Never collide — `HeroDataSO` carries no authored identity key at all. Each runtime `HeroDataRuntime`'s instance id is built purely positionally (`Team` + an incrementing index at `SetCombatants()` time) | There was never actually a collision risk to guard against; identity lives in the asset reference, not a hand-typed string |
| `ToCombatData` called repeatedly | Returns independent copies; asset never mutated | Assets are read-only content |

---

## Dependencies

| System | Direction | Nature |
|---|---|---|
| Trait | This depends on it | Data dependency — Hero references `TraitDataSO` |
| Skill | It depends on this | Data dependency — Skill loop reads Hero's mana/skill params |
| Combat (`AutoBattleSimulator`) | It depends on this | Data dependency — resolver consumes `HeroDataSeed` |

---

## Tuning Knobs

Safe ranges below are enforced by `[Range]` in the Inspector — they are not merely advisory.

| Parameter | Default | Safe Range | Effect of Increase | Effect of Decrease |
|---|---|---|---|---|
| `MaxHP` | per-hero | 30–800 | tankier | squishier |
| `ATK` / `MG` | per-hero | 0–80 | more damage | less damage |
| `DEF` / `MR` | per-hero | 0–50 | more mitigation | less mitigation |
| `AttackSpeed` | per-hero | 0.05–1.0 | **attacks** more often | **attacks** less often |
| `Range` | 1 | 1–4 | attacks from further | must close distance |

> `AttackSpeed` governs attack cadence **only**. It does not affect how fast a hero moves — movement runs on its own shared clock (`_moveSpeed`, on the resolver) and is identical for every hero. See `Combat.md`. There is deliberately **no** per-hero movement stat.

---

## Acceptance Criteria

- [ ] **A new Hero requires zero C# edits.** Creating a `HeroDataSO` asset and adding it to a roster fields a unit that renders in its authored `Icon`/tint, fights, and participates in synergies — with **no code change anywhere**. *(Before this pass, a new Hero rendered as an untinted gray square, because `BattleBoardManager` mapped `Id` → color via a hardcoded `switch` on the literals `"knight"` and `"archer"`.)*
- [ ] `HeroDataSO` assets can be created via `MagicSchool/Hero` and edited in the Inspector.
- [ ] `ToCombatData(team)` produces a `HeroDataSeed` with correct stats, presentation, `Team`, and `Traits`, without mutating the asset.
- [ ] Seed sources build the battle roster from `HeroDataSO` assets. Base roster: one melee (Knight, range 1) + one ranged (Archer, range 2), each with a Skill and the shared Fighter trait; a mirror match fields the same two on both teams.
- [ ] No hardcoded unit stats **or unit visuals** remain in code — all live on assets.
- [ ] An out-of-range value (e.g. `AttackSpeed = 0`, which would let a hero walk up to the enemy and then never swing) is clamped or rejected at author time, not discovered as a 120-second stall at runtime.

---

## Cross-References

| This Doc References | Target Doc | Element Referenced | Nature |
|---|---|---|---|
| Hero carries traits | `production/gdd/Trait.md` | `TraitDataSO` list | Data dependency |
| Hero data feeds combat | `production/gdd/Combat.md` | `SetCombatants(List<HeroDataSeed>)` | Data dependency |
| `AttackSpeed` drives only the attack clock | `production/gdd/Combat.md` | `AttackCooldown`, the two-clock model | Rule dependency |

---

## Open Questions

| Question | Owner | Deadline | Resolution |
|---|---|---|---|
| Do enemies participate in synergies in the base game? | designer | — | Yes — synergies are counted per-team, so enemy comps can gain traits too |
| Is there a crit mechanic? | designer | — | **No.** `CRIT` was authored on every Hero but never reached the damage formula. Removed **pending the feature**, not ruled out forever — re-add the field together with the roll in `CombatMath`. |
| Is there a shop? | designer | — | **No.** `Cost` was "reserved for a future shop" that does not exist. Removed **pending the feature** — re-add with the shop that spends it. |
| Should damage archetype (physical/magic) come back as a per-unit flag? | designer | — | **No.** It belongs on the action, not the unit — re-add it on the skill/action itself, together with a real magic-damage mechanic, not as a `HeroDataSO` flag. |
| Will Summons (hero-cast) or non-Hero enemies need their own authored type? | designer | — | Not yet. Today `EnemyDatabaseStub` returns the same `HeroDataSO` assets players use — there is no separate enemy-only content. `HeroDataSO`'s fields (`SkillMultiplier`, `Traits`, `PlayerTint`/`EnemyTint`) are Hero-shaped, not yet proven generic. Revisit when either is actually designed — the runtime layer (`HeroDataRuntime`) is already source-agnostic and may be the natural shared contract; the authored layer likely is not. |
