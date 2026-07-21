# Skill

> **Status**: Approved
> **Last Updated**: 2026-07-13
> **Implements Pillar**: (pillars TBD — `game-vision.md` exists but is an unfilled template; no pillars are authored yet)

## Summary

Every Hero has one active Skill powered by a simple mana charge. A unit gains mana each time it basic-attacks; when mana fills, the unit *casts* — its next basic attack is empowered (deals multiplied damage) — then mana resets. This is the genre's "spell" beat in its simplest base-game form: no cast-time channel, no targeting, no mana UI — just a periodic empowered hit that reads as "attack harder."

> **Quick reference** — Layer: `Feature` · Priority: `MVP` · Key deps: `Hero`, `Combat (AutoBattleSimulator)`

---

## Overview

Skills give each Hero a rhythm: charge up over a few attacks, then unleash a bigger hit. Mana starts at 0, rises by `ManaPerAttack` on every basic attack, and at `MaxMana` the unit arms its skill. The next attack consumes the charge and multiplies its damage by `SkillMultiplier`. Mana then resets and the cycle repeats. It is distinct from Trait bonuses (which are flat and always-on): a Skill is an *active* burst that only lands periodically.

## Player Fantasy

"My hero is building up to something." The player should feel anticipation as a unit charges and satisfaction when the empowered hit lands noticeably harder than its normal swings.

---

## Detailed Design

### Core Rules

1. Skill parameters live on `HeroDataSO` (authored) and are copied to `HeroDataSeed` → the runtime `HeroDataRuntime`: `MaxMana`, `ManaPerAttack`, `SkillMultiplier`, `SkillName`.
2. A `HeroDataRuntime` tracks runtime `Mana` (starts at 0) and `SkillArmed` (starts false).
3. On each basic attack (`AutoBattleSimulator.Attack()`), in order:
   a. Compute mitigated base damage.
   b. **If `SkillArmed`**: `damage = round(damage × SkillMultiplier)`, clear `SkillArmed`, log `SKILL! {name} casts {SkillName}`.
   c. Apply damage.
   d. **Gain mana** (only if `MaxMana > 0`): `Mana += ManaPerAttack`; if `Mana ≥ MaxMana`, set `Mana = 0` and `SkillArmed = true` (armed for the *next* attack).
4. A unit with `MaxMana ≤ 0` has no skill and never arms.
5. The empowered attack uses the same offense type as the basic attack (ATK vs DEF — there is no per-unit magic-damage flag; see `Hero.md` Core Rule 6). The skill only scales the final damage; it does not change targeting or range.
6. Mana is gained *after* damage resolves, so with `MaxMana 3, ManaPerAttack 1` the 4th attack (then 7th, 10th, …) is empowered.
7. **Damage applies directly to HP — there is no shield layer.** `HeroDataRuntime.Shield` and the shield-absorb branch in `ApplyDamageAndCheckKill()` were removed: the field was read on every hit but **never written by anything**, so it was dead weight in the hottest path in the game. Re-add it together with the first mechanic that actually grants shield.

### States and Transitions

| State | Entry | Exit | Behavior |
|---|---|---|---|
| Charging | Mana `< MaxMana` | Mana reaches `MaxMana` | Normal attacks; mana rises |
| Armed | Mana reaches `MaxMana` | Next attack fires | Next attack will be empowered |

### Interactions with Other Systems

| System | Interaction |
|---|---|
| Combat (`AutoBattleSimulator`) | The whole charge/empower loop lives inside `Attack()`. No new per-tick phase. |
| Hero | Provides `MaxMana`/`ManaPerAttack`/`SkillMultiplier`/`SkillName` via `HeroDataSO` → `HeroDataSeed`. |
| Trait | Independent. Trait bonuses raise base stats (including ATK) before battle; the skill multiplies the *already-buffed* attack, so the two stack. |

---

## Formulas

### Empowered attack damage

```
base     = ApplyMitigation(offense, defense)      // existing CombatMath
final    = SkillArmed ? round(base × SkillMultiplier) : base
```

| Variable | Type | Range | Source | Description |
|---|---|---|---|---|
| `SkillMultiplier` | float | 1.5–3.0 | ScriptableObject (`HeroDataSO`) | empowered-hit multiplier |
| `MaxMana` | int | 2–10 | ScriptableObject (`HeroDataSO`) | attacks-to-charge (with ManaPerAttack) |
| `ManaPerAttack` | int | 1–3 | ScriptableObject (`HeroDataSO`) | mana gained per basic attack |

**Edge cases**: `SkillMultiplier ≤ 1` makes the "empowered" hit no stronger — treated as a misconfiguration, not special-cased.

---

## Edge Cases

| Scenario | Expected Behavior | Rationale |
|---|---|---|
| `MaxMana ≤ 0` | Never arms; plain basic attacks only | Traitless/skill-less units are valid |
| Armed unit is killed before its next attack | Charge is lost | No skill queue persists past death |
| Empowered hit overkills the target | Normal kill handling | Skill only scales damage |
| Unit moves instead of attacking | No mana gained | Mana is tied to attacks, not ticks |

---

## Dependencies

| System | Direction | Nature |
|---|---|---|
| Hero | This depends on it | Data dependency — skill params sourced from `HeroDataSO` |
| Combat (`AutoBattleSimulator`) | Ownership handoff | The charge/empower loop is inside `Attack()` |

---

## Tuning Knobs

| Parameter | Default | Safe Range | Effect of Increase | Effect of Decrease |
|---|---|---|---|---|
| `MaxMana` | 3 | 2–10 | casts less often | casts more often |
| `ManaPerAttack` | 1 | 1–3 | casts sooner | casts later |
| `SkillMultiplier` | 2.0 | 1.5–3.0 | bigger burst | smaller burst |

---

## Visual / Audio Requirements

| Event | Visual Feedback | Audio Feedback | Priority |
|---|---|---|---|
| Skill cast | (future) unit flash / cast text; mana bar fill | cast SFX | Alpha |

> Base game logs the cast; mana-bar UI and cast VFX are a later pass (BattleUnit already has stubbed `UpdateMana`/`PlayCastText` hooks).

---

## Acceptance Criteria

- [ ] A unit gains mana per attack and, at `MaxMana`, its next attack is empowered by `SkillMultiplier` (logged).
- [ ] Empowered-hit damage ≈ `SkillMultiplier` × a normal hit against the same target.
- [ ] Mana resets after casting and the cycle repeats.
- [ ] A unit with `MaxMana ≤ 0` never casts.
- [ ] Skill and Trait bonuses stack (skill multiplies the trait-buffed attack).
- [ ] No hardcoded skill values in code — all on `HeroDataSO`.

---

## Cross-References

| This Doc References | Target Doc | Element Referenced | Nature |
|---|---|---|---|
| Skill params come from the hero | `production/gdd/Hero.md` | `HeroDataSO` mana/skill fields | Data dependency |
| Skill scales the basic attack | (Combat resolver) | `Attack()` in `AutoBattleSimulator.Attack.cs` | Ownership handoff |
| Skill multiplies trait-buffed ATK | `production/gdd/Trait.md` | `StatBonus.ATK` | Rule dependency |

---

## Open Questions

| Question | Owner | Deadline | Resolution |
|---|---|---|---|
| Should mana also gain when taking damage (TFT-style)? | designer | — | Not in base game — attack-only keeps the loop simple |
| Should the skill do something other than "attack harder" (heal, AoE)? | designer | — | Not yet — base game skill is a single empowered hit |
| Should `SkillName` become an enum or SO instead of a hand-typed string? | designer | — | Not yet — there is exactly one skill behavior today (the empowered hit), so a type would enumerate a set of one. Revisit when a second, genuinely distinct skill behavior is designed. |
