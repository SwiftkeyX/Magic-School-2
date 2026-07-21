# Systems Design

> List every system in the game, its single responsibility, what it depends on, and which tier it belongs to. Fill this out as part of Phase 1 before writing any code.

## Systems Table

| System | Responsibility | Depends On | Tier |
|---|---|---|---|
| GameManager | Owns game state enum and core game data (singleton) | — | 1 |
| SceneLoader | Handles all scene transitions | GameManager | 1 |
| InputHandler | Reads raw input and exposes it to other systems | — | 1 |
| Combat (AutoBattleSimulator) | Runs the auto-battle simulation on the hex grid (movement, attacks, mitigation, win/lose) | Hero, Trait, HexGrid | 2 |
| Hero | Data-driven unit definition (`HeroDataSO` ScriptableObject); projects to unified `HeroDataSeed` per team | Trait, Skill | 3 |
| Trait | Flat stat-bonus synergy system (`TraitDataSO` ScriptableObject); applied per-team at battle start | Hero, Combat | 3 |
| Skill | Per-hero active skill via a mana charge; at full mana the next attack is empowered (in `Attack()`) | Hero, Combat | 3 |

## Tier Definitions

| Tier | Label | Must work before… |
|---|---|---|
| 1 | Foundation | Any gameplay can be tested |
| 2 | Core Loop | Win/lose is reachable |
| 3 | Supporting | Content is complete |
