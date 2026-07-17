# Archived TFT sheet scripts — DO NOT RUN THESE

These 33 scripts (~5,000 lines) built and corrected the `tft-set9-skill` sheet between the first
Ionia pass and the `Legacy action` migration. **Their work is done and is baked into the sheet.** They
are kept for history — to answer *"why is the schema shaped like this?"* — and for nothing else.

**The sheet is now written by exactly one script: `../sync.py`, from the CSVs in `../data/`.**

## Why they were retired

Every one of these was re-run on every acceptance pass, so any two of them could write the same cell
and then overwrite each other for ever. That bug was found three separate times — and **two of the
three only existed because the scripts were re-run at all.** A one-shot migration cannot fight
anything if it is never run again.

They are also, by now, mostly *lies*. Each `tft-review-roundN.py` patches the sheet from state N-1 to
state N, so its declarations describe a sheet that no longer exists. `tft-add-ionia.py` spent three
rounds crashing on every run against a tab that had been deleted, and nobody noticed.

## What is where

| Script | What it did |
|---|---|
| `tft-add-{ionia,shurima,shadowisles-targon,freljord-piltover}.py` | encoded each origin's champions |
| `tft-review-round{2..9}.py` | one script per round of the user's review; each patched the previous state |
| `tft-apply-comments.py` | round-1 corrections, `Collision Types`, the identity-block merge |
| `tft-action-model.py` | built the `Action Model` tab |
| `tft-action-templates.py` | `Spread Types` + the Count/Spread invariant (now `validate()` in `../sync.py`) |
| `tft-promote-template.py` | renamed `Hero (template)` over the old `Hero` tab |
| `tft-ask-questions.py` | posted the open questions as sheet comments |
| `migrate_legacy_action.py` | collapsed Hero's five axis columns into `Legacy action` (CSV side); proved the axes were determined by the name before writing |
| `migrate_legacy_action_sheet.py` | the sheet side of the same: deleted the four dead columns, widened the `Action` super-header |
| `migrate_bonus_on_aa.py` | retired `Auto-Attack` as an action (it is a TRIGGER): 8 rows → `Bonus on AA`, summons → `Auto-Attack (ranged)`, Bel'Veth → `QuickAA`, Nilah → `Cone AOE`, Warwick's trigger → `On Cast Expire` |
| `migrate_split_charge.py` | split the two actions that hid a second job: `Charge Into` → `Charge` + `Move`, and K'Sante's `Knock Back` → the smash + the thrown body as its own `Charge` source |
| `migrate_group_and_triggers.py` | sorted `Effect Types` by category so it could merge into 6 blocks, and seeded the `Trigger Types` vocabulary from the 27 triggers in use |
| `migrate_cast_to_action.py` | moved `Cast (s)` out of Hero into the Action Model tab (CSV side) — the cast time belongs to the action |
| `migrate_cast_to_action_sheet.py` | the sheet side of the same: deleted Hero's last column |
| `migrate_cast_back.py` | reverted that: `Cast (s)` back into Hero's Action block (the user meant the Action COLUMN GROUP, not the tab) |
| `migrate_cast_back_sheet.py` | the sheet side: re-inserted the column, widened the `Action` super-header |
| `migrate_aoe_shape.py` | made `AOE (hex)` a vocabulary (`AOE shape` tab); split Teemo's 4-star branch; brought back `Wave` for Sona |
| `migrate_drop_collision.py` | dropped Hero's `Collision` (the action decides it — proved derivable before deleting); seeded the `Effect Recipient` vocabulary |
| `migrate_drop_collision_sheet.py` | the sheet side: deleted the column, reshaped the `Action` super-header |
| `migrate_step_triggers.py` | `After X` → `After Step N` (6 named things that did not exist); split Sejuani's and Kalista's trigger+condition |
| `migrate_projectile_shape.py` | a projectile's shape became the row's (`specify elsewhere`); its BURST became a separate step (`On Projectile Hit`); retired `Burst Projectile`, `Homing Burst Projectile`, `Wave` |
| `migrate_zone_aoe.py` | added `Zone AOE` (a hitbox that PERSISTS) so an over-time duration says whose it is; split Silco's vial |
| `add_set95.py` | added the 11 Set 9.5 champions, completing the roster at 75; +5 effects (Knock Up, Soul Link, Untargetable, Range, CC Immunity) |

**The `tft-*` scripts will not even import from here** — they do `from tft_sheet import ...`, and the
shared helper is now `../sheet.py`, which does not resolve from this folder. That is deliberate.

The two `migrate_legacy_action*` scripts DO still import cleanly (`from sheet import ...` resolves
when run by path from repo root), so they are the more dangerous kind of archive: runnable. Both are
guarded — the sheet one no-ops if `Legacy action` already exists, and the CSV one reads a `git show`
of a commit-pinned v1 `hero.csv` and asserts against today's — but **do not run them.** They are here
to explain how the column collapsed, not to do it again.

## If you need to change the sheet

Edit the CSV in `../data/`, run `python .claude/scripts/tft-set9-skill-modularity/sync.py`. The git diff shows exactly
which cells moved. See `../README.md`, and `.claude/docs/tft/set9-skill-schema-review.md` §O.
