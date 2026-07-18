# Set 10 skill tab (`Hero set 10`)

A second schema tab on the `tft-skill` sheet (renamed from `tft-set9-skill` / *TFT Set9 Skill
Research*), holding the Set 10 champions whose traits include **8-Bit, Country, Disco, or EDM**. It
**reuses the Set 9 31-column action schema and the identical reference vocabularies** — a new set's
champions are still made of the same actions and effects, so they validate against the same
`Action Model`, `Effect Types`, `AOE shape`, `Spread Types`, etc.

**Tab names (set on review, 2026-07-18):** the two schema tabs are **`Hero set 9`** (formerly `Hero`)
and **`Hero set 10`** (formerly the lowercase `hero set 10`), renamed for symmetry. Both carry the
two-row `Action`/`Effect` super-header. Tabs are addressed BY NAME, so the rename touched only the
sheet titles and the tooling strings (`SCHEMA_TABS`, `TABS`, `HERO_TAB`).

Source of truth for the champion data: the project's **`tft-set10`** reference sheet
(`1Eutkil9U8RJ4Lqo3l6wk9pbUeVVH80M4JmcRyMEqa2E`, "TFT Set 10 Read-Only"), `Champions` tab. **18
champions** so far — 9 matching 8-Bit/Country, 9 matching Disco/EDM. Note it is the user's curated
roster, so it does **not** carry Riot's full trait lists (e.g. no 8-Bit Kennen/Ziggs).

## The 18 champions

**8-Bit / Country** (initial batch; Corki/Katarina reflect review round 2):

| Champion | Cost | Trait | Class | Range | Action shape modelled |
|---|---|---|---|---|---|
| Corki | 1 | 8-Bit | Big Shot | 5 | `Homing Projectile` → `On Projectile Hit` `Circle AOE` + `Wound` |
| Tahm Kench | 1 | Country | Bruiser | 1 | passive `Buff/Damage Reduction` |
| Garen | 2 | 8-Bit | Sentinel | 1 | `Buff/Bonus HP` + `Buff/Empowered Attack` |
| Katarina | 2 | Country | Crowd Diver | 2 | `Bounce Homing Projectile` ×3 + `Wound` |
| Riven | 3 | 8-Bit | Edgelord | 1 | `Buff/Shield` + `Status/Empowered`, on-attack `Circle AOE` `If Empowered` |
| Samira | 3 | Country | Executioner | 4 | **Style** stacks + `Homing Projectile` (Per Stack) |
| Urgot | 3 | Country | Mosher | 2 | AS→AD convert + `Status/Empowered`, on-attack `Cone AOE` + self-shield |
| Caitlyn | 4 | 8-Bit | Rapidfire | 5 | `First hit Projectile` ×4 **Split across farthest N** |
| Thresh | 4 | Country | Guardian | 1 | `Circle AOE` cluster stun + self-heal (Derived) |

**Disco / EDM** (added round 3):

| Champion | Cost | Trait | Class | Range | Action shape modelled |
|---|---|---|---|---|---|
| Nami | 1 | Disco | Dazzler | 4 | `Homing Projectile` + `Status/Stun` |
| Taric | 1 | Disco | Guardian | 1 | `Buff/Shield` + `Buff/Empowered Attack` (next 2 attacks) |
| Gragas | 2 | Disco | Spellweaver·Bruiser | 1 | heal-over-time → `Circle AOE` + `Status/Chill` |
| Jax | 2 | EDM | Mosher | 1 | `Move` → single hit + `Circle AOE` + permanent AD/AP |
| Lux | 3 | EDM | Dazzler | 5 | `Laser Shot` at farthest (Enemies in path) |
| Blitzcrank | 4 | Disco | Sentinel | 1 | periodic `Cast` zap + `Buff/Shield` + `Status/Empowered` (faster zap) |
| Twisted Fate | 4 | Disco | Dazzler | 5 | `Homing Projectile` ×21 **Split across nearest N** + `Debuff/MR` |
| Zac | 4 | EDM | Bruiser | 1 | `Bounce Homing Projectile` ×3 + `Stun` + self-heal |
| Zed | 4 | EDM | Crowd Diver | 1 | `Status/Mark` → `Summon (untethered)` shadow → delayed burst |

## Tooling change — a second schema tab

The one-writer was hard-wired to a single `Hero` tab. Generalized so its Hero pipeline (merge-derive
+ vocab-validate) runs over **every** entry of a new `SCHEMA_TABS` map:

- `sheet.py` — added `SCHEMA_TABS = {"Hero set 9": "hero.csv", "Hero set 10": "hero-set10.csv"}`;
  `REFERENCE` now excludes **all** schema tabs (not just the primary); `remerge_hero(sh, tab=...)` and
  `validate_data(hero_csv=...)` are parametrized; `HERO_TAB = "Hero set 9"`.
- `sync.py` — `sync_hero(sh, tab, csv_name)`; `main()` loops `SCHEMA_TABS`; `validate()` checks every
  schema CSV against the shared vocab; new `ensure_schema_tab()` creates a declared-but-absent schema
  tab and seeds its header row (sync never writes headers, so `cols()` needs one to resolve against).
- `force_full.py` — takes an optional `<tab>` arg (default `Hero`), CSV looked up from `SCHEMA_TABS`.

**Fresh-tab bootstrap procedure** (invariant #6 applies to the whole tab at once — sync writes the
filled identity down every row because the sheet started blank, and remerge can't un-fill it):

```
python .claude/scripts/tft-set9-skill-modularity/sync.py               # creates + fills the tab
python .claude/scripts/tft-set9-skill-modularity/force_full.py "Hero set 10"   # blank continuations, re-merge
python .claude/scripts/tft-set9-skill-modularity/sync.py               # must report 0
```

After bootstrap, it is an ordinary schema tab: edit `data/hero-set10.csv`, run `sync.py`.

## New vocabulary — added to the SHARED reference tabs

1. **`Effect Types` → (Buff, Style)** — Samira's crit-stack resource. Each stack grants Attack Speed
   and the active scales off the count, both via `Per Stack` scaling; gained on crit, capped at 6,
   reset on cast. Modelled on the existing `Chakram` (Aphelios) precedent: a counter, not a stat.
2. **`Effect Types` → (Status, Empowered)** *(review round 2)* — a self-applied state a champion enters
   for a duration; later steps gate on it with `Condition = "If Empowered"`. Like `Mark`, does nothing
   by itself. Riven / Urgot / Zeri grant it on cast, and their on-attack steps fire only while it holds.
3. **`Action Model` → Bounce Homing Projectile** *(review round 2)* — one projectile that homes on the
   aim target, then re-homes on the next-nearest enemy, chaining **Count** times. Its own action (not a
   Spread — a bounce is a property of the DELIVERY). Katarina (Count 3) and Zeri (chain lightning).
4. **`Spread Types` → Split across farthest N** — Caitlyn's 4 shots at the 4 furthest, one each. The
   mirror of the existing `Split across nearest N`.

**Schema change (review round 5): a new `Fire Timing` column.** Orthogonal to `Spread` — `Spread` says
WHERE the Count instances go, `Fire Timing` says WHEN they fire: **`At Once`** (one volley) or
**`Consecutive`** (one after another). Set only when Count > 1, else `—`; a per-row run column, so a
branch changes it (Karma's 3rd cast fires 3 at once). It exists because `Spread` conflated the two —
`Same target` covers Akshan (6 shots, consecutive) and Xayah (feathers, at once). New `Fire Timing
Types` reference tab; the schema is now **32 columns** (`builder`'s action tuple gained `fire_timing`).
A bounce is `Consecutive` even with `Spread = —`, which is why the column keys off Count, not Spread.

**Convention change (review round 2): a projectile's default shape is `default`, not `1-hex`.** "1-hex
for a projectile should be default for simplicity" — so every ordinary-bolt projectile now reads
`AOE = default` (**32 rows on Hero set 9**, plus the Set 10 projectiles); a non-default projectile still
states its shape (Sona `Box 1.5x2`, Jhin `Box 1x2`). `validate_data`'s geometry check was widened: a
`specify elsewhere` (projectile) Shape may read `default` OR a real shape. The `AOE shape` tab's
`default` row records the dual meaning.

## Modelling calls (settled through the review rounds)

- **Corki** — projectile + burst: a `Homing Projectile` (effect block `—`) then an `On Projectile Hit`
  step (source `Step 1 Projectile`) that detonates a `Circle 1 hex` AOE for the damage + Wound. *(the
  Set 9 Karma/Jayce burst shape; changed from the initial single-AOE model on review.)*
- **Katarina / Zeri** — bounce is the new `Bounce Homing Projectile` action, Count = bounces, Spread `—`.
- **Riven / Urgot** — the "for N seconds, attacks do X" abilities: the cast grants a `Status/Empowered`
  (+ Shield / AS→AD), and a **separate on-attack step** fires `If Empowered`. Urgot's AS→AD reuses the
  Aatrox `Debuff/Attack Speed` + `Buff/AD` idiom; his cone is `Cone 1 hex` (per review).
- **Samira** — `Style` gained on `On Attack` + `Condition "If Critical Strike"` (no `On Crit` trigger);
  reset is an effect row `Buff/Style, Amount "reset to 0"`. The active scales `Per Stack`.
- **Thresh** — `Aim = Clustered`, `Circle AOE`, `AOE = Circle 2 hex` (per review); self-heal is
  `Derived +50% of total damage dealt`.
- **Roles** kept as the Set 10 sheet's own `Design Role` values (`ADCarry`, `APTank`, …); `Role` is not
  a validated vocabulary.

**Disco / EDM calls worth a review pass (round 3):**

- **Zac** *(open — review round 6)* — his BODY bounces, so it is a bounce where the carrier CHARGES:
  the user calls it "Bounce Homing Projectile + Charge". Held pending the Charge/collision cleanup
  (below); likely a new `Bounce Charge` action.
- **Taric** — "next **2** attacks" modelled as `Buff/Empowered Attack` with `Duration = "2 attacks"`.
  `Empowered Attack`'s definition is the *next* (one) attack; the count of 2 rides in the Duration cell.
- **Blitzcrank** *(resolved round 6)* — one passive step with an if/else: `If not Empowered` zaps
  `Every 2s`, `If Empowered` zaps `Every 1s` + 1% max HP. (Was two separate periodic steps.)
- **Twisted Fate** — `Count = "21 (AS-scaled)"`: a runtime-scaling count in a column that is normally a
  literal, carried as text.
- **Jax** *(2 hex, round 6)* — three steps (`Move` → single-target `Cast` + permanent AD/AP buff →
  adjacent `Circle AOE`), leaping to the highest-HP enemy within **2** hex (source text said 1).
- **Zed** *(round 6)* — the Shadow is a plain on-grid `Summon` (it walks the board, just untargetable);
  the delayed/conditional burst is a step gated on `Condition = "After delay or Target < 15% HP"`.

**Taxonomy refactors (review round 6, BUILT):**

- **`Spread` split into two axes.** `Spread` → renamed **`Volley Shape`** (geometric shape only: Cone /
  360° radial / Diagonal to Action Source). The target-SELECTION values (Same target, Each to its own
  target, Split across nearest/farthest N, Split across marked, Current + Left + Right) moved into
  **`Aim Target`, now a validated vocabulary** (`Aim Target Types` tab, ~30 keys grouped by kind).
  Distribution (converge vs split) is inferred from Aim + Count; only `Each to own target` is stated.
  A summon attacking Current needs neither Volley Shape nor Fire Timing.
- **`[collision=X]` is now PARSED** (not a dedicated Action Model row): `sheet.base_action()` strips it
  for the vocab + geometry lookups, and a separate check verifies the base action + the collision.
  Naafiri keeps `Charge [collision=Target-Only]`; the duplicate row is gone. Cost: Hero cells are a
  small parsed language (reopens the v2→v3 "no per-row overrides" line — the user's accepted trade).
- **Zac** — new **`Bounce Charge`** action ("Bounce Homing Projectile + Charge": the caster bounces its
  own body), Count = bounces, Collision Target-Only.

**Round 7 refactors (BUILT):**

- **`Summon` split into three by behaviour:** `Static Summon` (spawns, stands, attacks — Set 9 Zed,
  Azir), `Charge Summon` (spawns unit[s] that charge in; absorbs the old `Summon (untethered)` —
  Naafiri, Gangplank), `Hero Summon` (walks the grid + auto-attacks — Set 10 Zed, Soraka's Child of the
  Star). `Summon` and `Summon (untethered)` retired.
- **Passive steps are numbered `0.1, 0.2, …`** per champion (never the active's `1/2/3` sequence).
  Single passives moved `0`→`0.1`; three mis-numbered as active steps (Zeri chain, Riven, Urgot at
  `2`) → `0.x`. Renumbered in place.
- **Jinx** — aim `Random (2 hex of Current)` (fixed a Spread/Aim-refactor slip that had overwritten it
  with `Each to own target`, now retired).

The deeper reasoning for the shared schema lives in [`set9-skill-design-notes.md`](set9-skill-design-notes.md).
