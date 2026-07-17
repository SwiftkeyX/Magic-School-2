---
name: add-champion
description: Add or edit champions (and their reference values) on the tft-set9-skill Google Sheet in FEW turns. Batch-reads every schema convention with one command, builds rows in one script, validates locally, pushes via sync.py, applies the append-merge fix, and verifies compactly. NOT for balance/stat work (use push-champion-stats / tune-champion).
---

# Add / edit champions in the `tft-set9-skill` sheet

This skill encodes the modelling workflow as one **low-turn procedure (target ≤6 turns)** so it is not
re-derived interactively every time — re-deriving it is what burned tokens on the first origin add.

**Read first:** `[[tft-sheet-access]]`, `[[tft-sheet-scripts]]`, and the tooling
[README.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School%202/.claude/scripts/tft-set9-skill-modularity/README.md).

## The tooling (do not re-derive this)

- **Source of truth:** `.claude/scripts/tft-set9-skill-modularity/data/*.csv` — one file per sheet tab.
- **The one writer:** `sync.py` — CSV → sheet, derives every merge, then VALIDATEs.
- **Source champion data:** `tft-set9 → Champions → Skill Description` (a read-only reference sheet).
- **Schema / merge model:** the `Hero` tab is **31 columns** (`context.py` prints the LIVE schema —
  never hard-code the count). Only `Step` + `Skill Type` span a whole step; the run columns
  `Trigger / Condition / Action Source / Legacy action / Count / Spread / Skill Range / Aim Target /
  Cast` **and `AOE` and `Offset`** merge by value-run (a blank inherits the row above); the effect
  columns are per-row.
- **`Legacy action` is a KEY, not a description** — one name (`Pierce Projectile`, `Circle AOE`,
  `Cast`) that must match a row in the **`Action Model` tab** (`data/action-model.csv`) **exactly**,
  or `sync.py` VALIDATE fails. That tab holds the mechanics — **Apply** (DirectApply | Hitbox) ·
  **Spawn** (at-User | at-Target) · **Motion** (— | Projectile | Arc | Forward N hex) · **Behavior**
  (First-Hit | Homing | Pierce | Returning, Projectile only) · **Shape** (1-hex | circle | cone | box
  | custom) **and the `Collision`** — so **never repeat them per row**. `context.py` prints the lookup.
  If a champion's mechanics differ from its action's, it needs its **own action**, not an exception —
  that is how `Wave` (a box-shaped Pierce Projectile) and Nilah's `Cone AOE` happened.
- **An auto-attack is a TRIGGER, not an action.** If the champion's own attack is what fires the row,
  that is `Trigger = On Attack` (`On 3rd Attack`, …) and the action is **`Bonus on AA`**
  (DirectApply, Collision `None` — the attack already delivered the hit). Writing
  `On Attack → Auto-Attack` is circular and wrong. **`Auto-Attack (ranged)` means only a SUMMON
  really attacking** (Azir's Sand Soldier, Soraka's Child of the Star — check `Action Source`);
  **`QuickAA`** is a real burst of N attacks (Bel'Veth). If the attack is *reshaped* rather than
  merely added to, it is neither — Nilah's "attacks strike in a cone" is a `Cone AOE`.
- **What stays per-row:** `Offset` (the hitbox anchor: `centred` / `rear edge` / `front edge` /
  `detached +N` — a cone anchors at its **rear edge**), `AOE (hex)` (the SIZE — a Circle AOE is always
  a circle, but its radius is per row), `Count`, `Spread`. `Collision` is **not** here — the action
  decides it.
- **`Cast (s)` closes the Action block** (after `Collision`), not the effect block — it describes the
  action, so it merges per action like the rest of that block. `—` on an action-start row with no
  cast time; blank on continuations. Rarely set: only Galio (2), Garen (4), Lux (3) have one.
- **`AOE (hex)` is a KEY too** — it must match a row in the **`AOE shape`** tab: `1-hex` /
  `Circle N hex` / `Cone N hex` / `Box WxD`. `Cone N` = widest `2N+1`, depth `N+1`; `Box` is
  `hori × verti` and fractions are real (a wave is `1.5` wide, a blade `0.1`). It describes the
  **hitbox**, not the area a moving hitbox sweeps. `—` only when the action has no hitbox at all.
- **A PROJECTILE's shape is the ROW's** — every projectile action reads `Shape = specify elsewhere`,
  so its `AOE (hex)` states its own hitbox: `1-hex` for a bolt, `Box 1.5x2` for Sona's wave. Projectiles
  are told apart by **Behavior** (Homing / First-Hit / Pierce / Returning), never by shape.
- **A projectile and its BURST are two parts.** If it explodes on impact, that is a SEPARATE step:
  `Trigger = On Projectile Hit`, `Action Source = Step N Projectile`, action `Circle AOE`/`Zone AOE`,
  with the burst's own `AOE (hex)`. The projectile row's whole effect block is `—` — it exists to hit,
  and applies nothing. Never put the burst's radius in the projectile's `AOE (hex)`.
- **`Zone AOE` vs `Circle AOE` — does the damage come from BEING somewhere, or from HAVING BEEN HIT?**
  A **Zone** persists: whoever is inside at each tick is hit, and walking out stops it (Silco's
  chemicals, Garen's spin, Swain's aura). A **Circle AOE** fires once, so an over-time effect is a
  **status on the victim** and follows them (Teemo's poison). The action decides what an over-time
  `Effect Duration` *means* — the zone's life, or the victim's status. Pick it deliberately.
- **`Trigger (When)` and `Effect Recipient` are enforced too** — `Trigger Types` and
  `Effect Recipient Types`. Do not invent one; if a champion needs a new value, add the row and say so.
- **Sequencing is `After Step N`**, never `After <ability name>`. It names the step that must finish
  first, matching Aim's `Step N Aim target`. `After Cast` is gone: 9 champions cast in two different
  steps, so it could not say which. If a step waits for something to *run out* instead, that is an
  Expire trigger (`On Cast Expire`).
- **Trigger = WHEN; Condition = ONLY-IF.** Never pack a gate into the trigger — `On Ally Attack
  Chilled Enemy` was really `On Ally Attack` + `If Target Chilled`.
- **An "except when…" is usually a BRANCH, not a parenthetical.** If a value varies by star or state,
  give the step two rows with `Condition`s (Teemo `If not 4-Star` / `If 4-Star`; Swain, Azir, Karma
  are the same shape) rather than writing `1 (2 at 4-Star)` into the cell. A Step is a MOMENT; its
  rows are its branches.
- **Roster: COMPLETE** — all **75** champions (Set 9.0 + 9.5) are in. `context.py --missing` reports
  0. Nothing is excluded; the source's `Sub-Set` column marks which set each belongs to.

## Procedure

### 1. One batched read — never many small queries
```
python .claude/scripts/tft-set9-skill-modularity/context.py --origin <OriginName>
```
Prints, in one shot: the live schema, the merge model, the conventions that bite, every reference
value `sync.py` enforces, and the source rows for the origin. **Do not** run separate queries per
fact — that is the anti-pattern this replaces. (`context.py --missing` first shows which champions
are still un-added, grouped by origin.)

### 2. Resolve novel mechanics with the user up front
If a champion needs a hitbox shape / spread the taxonomy lacks, ask in **one** batched
`AskUserQuestion` (one question per champion), *before* writing any rows. Prefer composing existing
Actions over inventing new ones; only add a taxonomy term when the user picks it.

### 3. Build in ONE script — import the builder, don't re-derive it
`from builder import build` (`.claude/scripts/tft-set9-skill-modularity/builder.py`) bakes in every
blanking rule for the 31-col schema: identity first-row only; Step/Skill Type on step-start; run-cols
with `Condition = "—"` on a no-condition defining row (blank inherits the champion above via
`fill_down`) and blank on continuations; **Skill Range** = the hero's Range on action-starts; **AOE**
and **Offset** on the action's first effect and blank on continuations (so they merge); effect cols
every row. The **action tuple** is `(trigger, source, action, count, spread, aim, cast, effects)`
— `action` is the `Action Model` key and `cast` is that action's channel time; the effect tuple is
`(cond, recip, cat, det, amt, scaltype, scaling, cadence, dur, aoe, offset)`.
`Cast`/`Move` → `Count "—"`; star-varying counts use slash notation (`6/6/25`). Supply champion data
only — **never hand-write CSV rows in the chat**.

Prefer an EXISTING action: adding a row to `action-model.csv` adds a concept to the model, so only do
it when no combination of the axes already describes the champion, and say so when you do. Register
any **new** action / Collision / Spread / Scaling Type / `(Category, Detail)` pair in its reference
CSV, or `sync.py` VALIDATE fails. Append/splice into `hero.csv` **idempotently** (cut the
block by champion name, re-append) so a re-run is safe; existing rows must not move.

### 4. Validate locally before pushing
```
python .claude/scripts/tft-set9-skill-modularity/context.py --validate
```
Runs `sync.py`'s used-vs-defined check (the same function, `sheet.validate_data()` — not a copy) on
the CSVs, catching a missing reference value with no network round-trip. Also `git diff --stat data/`
to confirm additions-only.

### 5. Push once
```
python .claude/scripts/tft-set9-skill-modularity/sync.py
```
Expect `VALIDATE: ok`. (Run from repo root, `PYTHONIOENCODING=utf-8`.)

### 6. If you ADDED new champions: run the append-merge fix
`sync.py` cannot merge a freshly-appended champion in one pass (see `[[tft-sheet-scripts]]` #6):
symptom is `re-merged — N blocks` too high, step-start `Count`/`Spread` blank instead of `—`. One
command reconciles it, then confirm:
```
python .claude/scripts/tft-set9-skill-modularity/fix_append.py
python .claude/scripts/tft-set9-skill-modularity/sync.py    # must report 0 cells
```
`fix_append.py` blanks continuation identity cells, force-writes the new rows' literal Step/run
values, and re-merges; it is idempotent (no-op if already consistent). (Editing existing champions
only? Skip this step.)

### 7. Verify compactly
Print champion count + the new block's key columns **only** — never re-dump all 155 rows. Acceptance:
`sync.py` twice → **0 cells** + `VALIDATE: ok`.

### 8. Optional — reply to review comments
Overwrite `reply.py`'s `REPLIES` (match keys are a **substring of the comment root**, longest first)
and run it. Leave threads **unresolved** — resolving is the user's call.

## Troubleshooting — if `sync.py` won't reach 0 (see `[[tft-sheet-scripts]]` #7-9)

- **Block count wrong / oscillates** → a **basic filter on Hero** blocks merges. Clear it:
  `clearBasicFilter` on the Hero sheetId, then re-merge. (The user adds filters while reviewing.)
- **A reference tab reports the same N cells every sync** → a row you inserted landed under the tab's
  **doc-block horizontal merge**, which swallows writes to columns 2+. Unmerge that tab's region, sync.
- **You inserted a row MID-FILE** (not appended) → sync rewrites everything below it (it compares by
  position) and can fight `fix_append`. The deterministic reset is **`force_full.py`** (writes every
  Hero cell to the CSV literal, then one re-merge), then `sync.py` to 0.
- **Added a new COLUMN** → also insert it on the sheet (`insertDimension` + set the header — sync never
  writes the header row) and add it to `HERO_COLUMNS`/`RUN_COLUMNS` in `sheet.py`.

## Token discipline (why this skill exists)

- **Batch** the reads and the build into 1-2 scripts. Every extra Bash round-trip re-sends the whole
  growing context — that, times many turns, is the real cost, not the row count.
- **Never re-print full sheet state** to "check" — a 3-line summary (count + the new block) is enough.
- **Generate rows in a script**, don't emit CSV cell-by-cell in the transcript.
