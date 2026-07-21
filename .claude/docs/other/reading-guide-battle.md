# Reading Guide — the Battle system

> ⚠️ **TEMPORARY / SCRATCH.** An onboarding aid, not a spec. It is *not* a source of truth — the
> GDDs (`production/gdd/`) are. Delete when no longer needed, and remove its line from
> `.claude/docs/index.md` at the same time.
>
> Describes the code as of the `refactor/editability-pass` branch (PR #1).

---

## Start here

**`Assets/Scripts/Battle/Resolver/AutoBattleSimulator.cs` → the `BattleLoop()` coroutine.**

That is the spine of the entire game. Everything else either feeds it data or draws what it decided.

But it needs ~10 minutes of vocabulary first, or the types won't mean anything. So:

---

## Tier 1 — the vocabulary (~250 lines, one sitting)

| # | File | Lines | Why this one |
|---|---|---|---|
| 1 | `Battle/Data/BattleData.cs` | 81 | Every other file speaks in these types: `Team`, `HeroDataSeed`, `CombatantSnapshot`, `BattleResult`. Read this and the rest stops looking foreign. |
| 2 | `Battle/Data/HeroDataSO.cs` | 122 | What a unit **is** when a designer authors it. Jump to `ToCombatData()` at the bottom — that method is the doorway from *authored asset* into *the simulation*. |
| 3 | `Battle/Resolver/HeroDataRuntime.cs` | 47 | What a unit **becomes** during a fight. |

**The single most useful thing you can do:** open `HeroDataSeed` (in `BattleData.cs`) and
`HeroDataRuntime.cs` side by side. The fields `HeroDataRuntime` has *extra* — `CurrentHP`, `Mana`,
`AttackCooldown`, `MoveCooldown`, `Position`, `SkillArmed` — are exactly "state that exists only
while fighting."

**That diff *is* the design.** Authored data on the left, runtime state on the right.

---

## Tier 2 — the engine (this is the actual game)

| # | File | Lines | Why this one |
|---|---|---|---|
| 4 | **`Resolver/AutoBattleSimulator.cs`** | 167 | **The heart.** Go straight to `BattleLoop()`. |
| 5 | `Resolver/AutoBattleSimulator.Attack.cs` | 77 | What one hit does. |
| 6 | `Resolver/CombatMath.cs` | 27 | The one damage formula. |
| 7 | `Resolver/AutoBattleSimulator.CombatHelpers.cs` | 41 | Targeting + the single damage choke point. |
| 8 | `Resolver/AutoBattleSimulator.Traits.cs` + `Data/TraitDataSO.cs` | 66 + 40 | Synergy. |

### The whole game, in one paragraph

Every tick (0.1s), each living unit charges **two independent clocks**:
`AttackCooldown += AttackSpeed × tickDelay` (per-unit) and `MoveCooldown += _moveSpeed × tickDelay`
(**shared** — the same pace for everyone). When a clock crosses **1.0** the unit spends it:
**attack** if an enemy is within `Range`, otherwise **step toward the nearest one**. Repeat until one
side is wiped, or the tick cap hits. That's it — the whole auto-battler is `BattleLoop()`.

The two clocks are separate on purpose. When there was only one, a hero that swung faster also
*walked* faster, and walking cost you an attack. `AttackSpeed` now governs attack cadence and
nothing else. See `production/gdd/Combat.md`.

### Things worth noticing as you read

- **`.Attack.cs` contains the entire Skill system.** There is no `Skill.cs`. Mana gain, arming, and
  the empowered hit are ~20 lines inside `Attack()`. Charge → arm → next attack is multiplied.
- **`CombatMath` is 27 lines and holds the most important number in the game.** `MitigationConstant`
  (100) is the defense value at which incoming damage is halved. Raise it and defense gets weaker
  everywhere; lower it and every point of DEF matters more.
- **`.Traits.cs` is the cleanest system in the codebase.** Count trait-carriers per team → pick the
  highest satisfied tier → apply its flat bonus once, at battle start. Learn the house style here.

---

## Tier 3 — the board and the view

| # | File | Lines | Why this one |
|---|---|---|---|
| 9 | `Managers/HexGrid.cs` + `Data/HexCoord.cs` | 109 + 76 | Where things stand and how they path. `GetNextStep()` is a BFS. `HexCoord` is offset-hex math — read `Distance()` and move on. |
| 10 | `Resolver/AutoBattleSimulator.Setup.cs` | 145 | How a battle gets *seeded*: assets in, `HeroDataRuntime`s out. |
| 11 | `Managers/BattleBoardManager.cs` | 382 | **Read this last.** |
| 12 | `Views/BattleUnit.cs` | 310 | One unit's visuals: HP bar, move lerp, attack lunge, death fade. |

> **On `BattleBoardManager`:** it is a **god class with five jobs** — builds the board, builds the
> bench, owns placement state, spawns units, and adapts resolver events into visuals. It is the
> hardest file in the project *because it does five things*, not because it is clever. Splitting it
> is known work, deliberately left out of PR #1.

---

## The one trace that explains everything

If you'd rather understand it by *following a battle* than by reading files — press Play, and this
is what actually happens:

```
BattleBoardManager.Start()
  └→ EnsureCombatantsInitialized()      seed from the roster components
       └→ HeroDataSO.ToCombatData(team) authored asset  →  HeroDataSeed
            └→ SetCombatants()          HeroDataSeed    →  HeroDataRuntime   ← sim state is born HERE
  └→ BuildBoard()   BuildBench()

[you drag a hero onto a tile]
  └→ PlaceStudent()                     mark grid occupancy + spawn a BattleUnit view

[Start Battle]
  └→ GetAutoEnemyPlacements()           ← ONE source of truth for where enemies stand
  └→ BeginBattle()
       └→ ApplyTraitBonuses()           synergies applied ONCE, before the loop
       └→ BattleLoop()  ──────────────────────┐
            every 0.1s, in four phases:       │
              1. CHARGE                       │
                   AttackCooldown += AttackSpeed×dt   ← per-unit clock
                   MoveCooldown   += _moveSpeed  ×dt   ← SHARED clock
              2. ATTACK  (charged AND in range)
                   Attack()
              3. MOVE    (charged AND nothing in range)
                   MoveTowardNearest()
              4. CLAMP both clocks to <= 1.0  ← stops banking; keep it its OWN phase
                  └→ fires OnCombatantActed / OnCombatantMoved / OnCombatantDefeated
                       └→ BattleBoardManager animates the sprites
            until one side is wiped ──────────┘
       └→ OnBattleComplete  →  BattleHUD shows Victory / Defeated
```

### The key architectural insight

**The resolver never touches a GameObject.** It runs a pure simulation and *announces* what happened
via C# events. `BattleBoardManager` listens and makes the sprites agree.

That separation is the best decision in the project. It's also why the bug fixed in PR #1 was
dangerous: enemy placement was the **one place** where the view and the sim each derived the same
fact *independently* — instead of the view deriving it from the sim. Two copies of one rule meant a
unit's sprite could stand somewhere its combatant did not.

---

## Reading the comments

The code is dense with `// removed: ... rebuilding fresh` markers. **These are load-bearing for a
reader** — they tell you what *used to* be there (champions, meta-progression/RunManager, per-tick
trait abilities, the skill-cast lifecycle) so you don't waste time hunting for systems that were
deliberately torn out.

Two known gaps you'll notice and should not be confused by:

- **The Skill system is invisible in-game.** It only emits `Debug.Log`. `BattleUnit` has
  `InitManaBar` / `UpdateMana` / `PlayCastText` / `SetCastingVisual`, all marked
  **NOT CURRENTLY CALLED** — they're kept deliberately (per `Skill.md`) for the pass that re-adds
  the events that drive them.
- **`AutoBattleSimulator` has no GDD.** All three existing GDDs (Hero, Skill, Trait) couple to it,
  but it has no spec of its own. It is the highest-value doc still to write.
