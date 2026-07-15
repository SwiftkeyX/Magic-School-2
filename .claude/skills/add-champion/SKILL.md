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
  never hard-code the count). Only `Step` + `Skill Type` span a whole step;
  `Trigger / Condition / Action Source / Action / Count / Spread / Collision / Skill Range / Aim Target`
  **and `AOE`** merge by value-run (a blank inherits the row above); the other effect columns are per-row.
- **Remaining roster:** run `context.py --missing`. As of the last session, **11 Set 9.0 champions**
  remain — Bilgewater, Darkin, Ixtal, Wanderer, **Zaun**; Fiora/Quinn/Xayah stay excluded (9.5-only).

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
on the action's first effect and blank on continuations (so it merges); effect cols every row.
`Cast`/`Leap` → `Count "—"`; star-varying counts use slash notation (`6/6/25`). Supply champion data
only — **never hand-write CSV rows in the chat**.

Register any **new** Action / Collision / Spread / Scaling Type / `(Category, Detail)` pair in its
reference CSV, or `sync.py` VALIDATE fails. Append/splice into `hero.csv` **idempotently** (cut the
block by champion name, re-append) so a re-run is safe; existing rows must not move.

### 4. Validate locally before pushing
```
python .claude/scripts/tft-set9-skill-modularity/context.py --validate
```
Replicates `sync.py`'s used-vs-defined check on the CSVs — catches a missing reference value with no
network round-trip. Also `git diff --stat data/` to confirm additions-only.

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
