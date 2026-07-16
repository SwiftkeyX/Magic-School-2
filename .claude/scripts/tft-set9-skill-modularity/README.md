# `tft-set9-skill` sheet — tooling

The Google Sheet `tft-set9-skill` encodes every TFT Set 9 champion's skill as structured data.
**Nothing here touches the Unity game** — this is data/schema work.

**Scope, and why the folder is named so specifically:** this folder writes the **`tft-set9-skill`
sheet, and nothing else**. Other scripts in `.claude/scripts/` also touch TFT data (`sheet_sync.py`,
`balance_report.py`, `push_stats_to_sheet.py`) — they are a different job, and they are none of this
folder's business. A bare `tft/` would have claimed a namespace it does not own.

## To change the sheet

**Edit the CSV in `data/`, then run:**

```
python .claude/scripts/tft-set9-skill-modularity/sync.py
```

That's it. The git diff on the CSV then shows **exactly which cells moved** — which is the whole
point, and something the old 300-line-patch-script-per-round approach could never show.

| File | What it is |
|---|---|
| `data/*.csv` | **The source of truth.** One file per tab. |
| `sync.py` | **THE one writer.** CSV → sheet, derives every merge, then validates. |
| `dashboard.py` | **Parked** (user set it aside for now). Generates a read-only champion-centric **Dashboard** tab from the source + each action's `Columns used` profile. Not wired into `sync.py`; runnable standalone. Re-enable by calling `dashboard.generate(sh)` in `sync.py`'s `main()`. |
| `export.py` | Sheet → CSV. Use only to re-snapshot if the sheet is edited by hand. |
| `reply.py` | Replies to the review comments. Holds **the current round's** replies; overwrite it each round. |
| `sheet.py` | Shared helpers: `cols()`, `remerge_hero()`, `post_replies()`. |
| `context.py` | One batched read for the `/add-champion` skill: schema + conventions + reference vocab (`--origin X` adds source rows, `--missing` lists un-added champions, `--validate` runs the local check). |
| `builder.py` | Reusable `build(identity, steps)` → 31-col rows with the blanking rules baked in. `from builder import build`. |
| `fix_append.py` | Reconcile the append-merge quirk after adding NEW champions, then sync to 0. |
| `force_full.py` | Deterministic escape hatch: write every Hero cell to the CSV literal + one re-merge, when sync/fix_append fight (e.g. after a mid-file insert). |
| `archive/` | 17 retired scripts (~5,000 lines). Kept for history. **Never run them.** |

## Renaming a column

`sync.py` **never writes the header row** — the headers are yours to rename. But `cols()` resolves
columns **by name**, so if you rename one in the sheet you must also rename it in `HERO_COLUMNS`
(`sheet.py`), or every write into that column stops resolving. It fails loudly, not silently.

Run everything from **repo-root cwd**. Set `PYTHONIOENCODING=utf-8` — the sheet contains em-dashes
and `×`, which crash the default Windows console codec.

## The acceptance test

> **Run `sync.py` twice. The second run must report ZERO changes.**

This is the only thing that has ever caught the real bugs. It takes about a minute.

## Three rules, each learned by breaking something

1. **Columns are addressed BY NAME, never by index.** The user renames headers as they go — `Trigger`
   is really `Trigger (When)` in the sheet — and columns have been inserted mid-table. Every script
   that said `r[14]` started writing into the wrong column the moment that happened. `cols()` resolves
   off the sheet's own header row.

2. **A blank cell is DATA.** A merged cell reads back as `""` on every row but its first, so a blank
   means *"same as the row above"* — and **the comparison must be merge-aware on BOTH sides**, or it
   is a stable infinite loop: write, merge, blank, write. `sync.py` compares merged columns by their
   *effective* values (blank inherits the row above) and writes the filled value, letting the
   re-merge absorb the duplicate.

   **`Step` and `Skill Type` are the exception, and must stay one.** `Step` is what the re-merge
   reads to find step *boundaries*, so a filled continuation row looks like a **new step start** and
   never merges away — then a renumber pass fights it for ever. They are compared **raw** and written
   **literally**, blanks included.

3. **Merges are DERIVED from the values, never stored.** That is why a flat CSV fully describes the
   sheet. `remerge_hero()` reconstructs all three layers (champion identity block, step block, value
   runs) from the cell values alone.

## Why it looks like this

There used to be **17 scripts and 5,257 lines** — one per origin, one per review round — and *all of
them were re-run on every pass*, so any two could fight over the same cell. Three such bugs were
found, and **two of them existed only because the scripts were re-run at all.** A one-shot migration
cannot fight anything if it is never run again.

One writer makes that bug class **impossible** rather than merely tested-against.

Full story and the schema's design history: `.claude/docs/tft/set9-skill-schema-review.md` (§O).
