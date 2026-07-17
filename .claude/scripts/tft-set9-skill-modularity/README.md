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
| `dashboard.py` | **Parked & stale.** Generated a read-only champion-centric Dashboard from `action-model.csv`'s `Columns used` profiles. That tab is back and managed again, but it has no `Columns used` column — rework it around the current shape before re-wiring it into `sync.py`. |
| `export.py` | Sheet → CSV. Use only to re-snapshot if the sheet is edited by hand. |
| `reply.py` | Replies to the review comments. Holds **the current round's** replies; overwrite it each round. |
| `sheet.py` | Shared helpers: `TABS` (**the** tab↔CSV map, which `sync.py` and `export.py` both derive from), `cols()`, `remerge_hero()`, `post_replies()`. |
| `context.py` | One batched read for the `/add-champion` skill: schema + the action lookup + conventions + reference vocab (`--origin X` adds source rows, `--missing` lists un-added champions, `--validate` runs the local check). |
| `builder.py` | Reusable `build(identity, steps)` → 31-col rows with the blanking rules baked in. `from builder import build`. |
| `fix_append.py` | Reconcile the append-merge quirk after adding NEW champions, then sync to 0. |
| `force_full.py` | Deterministic escape hatch: write every Hero cell to the CSV literal + one re-merge, when sync/fix_append fight (e.g. after a mid-file insert). |
| `archive/` | 33 retired scripts (~5,000 lines) — the origin passes, the review rounds, and the schema migrations. Kept for history. **Never run them.** |

## The vocabularies, and what enforces them

`sync.py` VALIDATE fails if a Hero cell uses a value with no row in its tab. That check — not the tab
— is what stops a vocabulary drifting: `Action Model` spent a day hand-maintained and invisible to the
tooling, and quietly disagreed with the data.

| Hero column | must match a row in |
|---|---|
| `Legacy action` | `Action Model` (`action-model.csv`) |
| `AOE (hex)` | `AOE shape` (`aoe-shape.csv`) — `Circle N hex` / `Cone N hex` / `Box WxD` |
| `Offset` | `Offset Types` (`offset-types.csv`) — `centred` / `rear edge` / `rank -N` / `detached +N` |
| `Trigger (When)` | `Trigger Types` (`trigger-types.csv`) |
| `Effect Recipient` | `Effect Recipient Types` (`effect-recipient-types.csv`) |
| `Scaling Type` / `Spread` | their `*-types.csv` |
| `Effect Category` + `Effect Detail` | `Effect Types` (as a PAIR) |
| *(tab-vs-tab)* `Action Model`'s `Collision` | `Collision Types` — `TAB_VOCAB`, because no Hero column checks it any more |

## The action model — one name, one lookup

`Hero.Legacy action` holds a **key** (`Pierce Projectile`, `Circle AOE`, `Cast`). How that action
*works* — `Apply` / `Spawn` / `Motion` / `Behavior` / `Shape` — lives in **one row** of the
`Action Model` tab (`data/action-model.csv`). `sync.py` VALIDATE fails if a key has no row there.

Those five axes were Hero **columns** for one day (v2, `0db5e27`) and moved out again, because every
one of them is decided by the action's name — checked across all 135 action rows, 23 names, no
exceptions once `Auto-Attack` is split into `(melee)` and `(ranged)`. Per-row copies were ~200 rows
restating a 23-row lookup, with nothing to stop the two drifting apart.

**What stays in Hero:** `Offset`, `AOE (hex)`, `Count`, `Spread`, `Cast (s)` — an action's shape is
fixed but its **size**, anchor and repetition are not.

**`Collision` left too.** It was per-row for a real reason — `Burst Projectile` was `First-Hit` on
three rows and `Target-Only` on one — until that last exception (Urgot) turned out to be a `Cone AOE`,
not a Burst Projectile at all. Every action now has exactly one Collision, so the column was restating
the tab on every row. **If a future champion breaks that, they get their own action** (which is
exactly how `Wave` and Nilah's `Cone AOE` happened) — that is the model working, not failing.

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
