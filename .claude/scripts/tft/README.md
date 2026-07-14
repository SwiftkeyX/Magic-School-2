# TFT Set 9 skill sheet — tooling

The Google Sheet `tft-set9-skill` encodes every TFT Set 9 champion's skill as structured data.
**Nothing here touches the Unity game** — this is data/schema work.

## To change the sheet

**Edit the CSV in `data/`, then run:**

```
python .claude/scripts/tft/sync.py
```

That's it. The git diff on the CSV then shows **exactly which cells moved** — which is the whole
point, and something the old 300-line-patch-script-per-round approach could never show.

| File | What it is |
|---|---|
| `data/*.csv` | **The source of truth.** One file per tab. |
| `sync.py` | **THE one writer.** CSV → sheet, derives every merge, then validates. |
| `export.py` | Sheet → CSV. Use only to re-snapshot if the sheet is edited by hand. |
| `sheet.py` | Shared helpers: `cols()`, `remerge_hero()`, `post_replies()`. |
| `archive/` | 17 retired scripts (~5,000 lines). Kept for history. **Never run them.** |

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
   means *"same as the row above"* and must round-trip as a blank. **Never fill `Step`** — it is what
   the re-merge reads to find step *boundaries*, so a filled continuation row looks like a new step
   start, and a renumber pass will then fight it for ever.

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
