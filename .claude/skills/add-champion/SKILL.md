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
- **Schema / merge model:** the `Hero` tab is 30 columns. Only `Step` + `Skill Type` span a whole
  step; `Trigger / Condition / Action Source / Action / Count / Spread / Collision / Aim Target`
  merge by value-run (a blank inherits the row above); effect columns are per-row.

## Procedure

### 1. One batched read — never many small queries
```
python .claude/scripts/tft-set9-skill-modularity/context.py --origin <OriginName>
```
Prints, in one shot: the 30-column schema, the merge model, the conventions that bite, every
reference value `sync.py` enforces, and the source rows for the origin. **Do not** run separate
queries per fact — that is the anti-pattern this replaces.

### 2. Resolve novel mechanics with the user up front
If a champion needs a hitbox shape / spread the taxonomy lacks, ask in **one** batched
`AskUserQuestion` (one question per champion), *before* writing any rows. Prefer composing existing
Actions over inventing new ones; only add a taxonomy term when the user picks it.

### 3. Build in ONE script (the builder pattern)
Generate rows in a script — never hand-write CSV rows in the chat. Blanking rules:
- **Identity** (cols 0-9): only the champion's **first** row.
- **Step + Skill Type**: only the **first row of each step** (compared raw — a filled continuation
  row reads as a new step).
- **Run columns** on each **action's first row**; **`Condition = "—"` on a no-condition defining row**
  (blank would inherit the champion above via `fill_down`); blank on continuation effect rows.
- **Effect columns** (20-29): every row.
- `Cast` / `Leap` → `Count "—"`. Star-varying counts use slash notation (`6/6/25`).
- Register any **new** Action / Collision / Spread / Scaling Type / `(Category, Detail)` pair in its
  reference CSV, or `sync.py` VALIDATE fails.

Append to `hero.csv`; make the builder **idempotent** (cut the block by champion name, re-append) so a
re-run is safe. Existing rows must not move — text-splice or append, don't rewrite the whole CSV.

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

## Token discipline (why this skill exists)

- **Batch** the reads and the build into 1-2 scripts. Every extra Bash round-trip re-sends the whole
  growing context — that, times many turns, is the real cost, not the row count.
- **Never re-print full sheet state** to "check" — a 3-line summary (count + the new block) is enough.
- **Generate rows in a script**, don't emit CSV cell-by-cell in the transcript.
