# Archived TFT sheet scripts — DO NOT RUN THESE

These 17 scripts (~5,000 lines) built and corrected the `tft-set9-skill` sheet between the first
Ionia pass and review round 9. **Their work is done and is baked into the sheet.** They are kept for
history — to answer *"why is the schema shaped like this?"* — and for nothing else.

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

**They will not even import from here** — they do `from tft_sheet import ...`, and the shared helper
is now `../sheet.py`, which does not resolve from this folder. That is deliberate.

## If you need to change the sheet

Edit the CSV in `../data/`, run `python .claude/scripts/tft/sync.py`. The git diff shows exactly
which cells moved. See `../README.md`, and `.claude/docs/tft/set9-skill-schema-review.md` §O.
