Step-skill: publishes tuned champion stats — refreshes the Google Sheet's stat-column mirror from `ChampionRoster.cs` and updates the champion stat table in `TraitSystem.md`. Called by `/balance-pass` as the final step, once `/validate-balance` is clean.

---

## Agent

`claude`

---

## Docs

| Doc | Read/Write | Purpose |
|---|---|---|
| `.claude/scripts/push_stats_to_sheet.py` | Read (execute) | Refreshes the sheet's Heroes tab stat columns from `ChampionRoster.cs` |
| `.claude/docs/production/gdd/TraitSystem.md` | Read + Write (surgical) | Champion stat table — the doc-side source of truth for tuned values |
| `.claude/docs/balance/balance-framework.md` | Read + Write (surgical) | "Current Scores" table — refresh with post-tuning values |

---

## Entry Condition

`/validate-balance` reported clean (or the user explicitly accepted a remaining outlier and wants to publish anyway).

---

## Step 1 — Push stats to the sheet

Run `python .claude/scripts/push_stats_to_sheet.py`. It matches rows by champion name and aborts on any name mismatch — if it aborts, stop and report the mismatch rather than forcing it.

---

## Step 2 — Update TraitSystem.md

Surgically update only the champion stat table rows that changed this session — do not rewrite the whole doc.

---

## Step 3 — Refresh balance-framework.md's Current Scores table

Re-run `python .claude/scripts/balance_report.py` and replace the "Current Scores" table in `balance-framework.md` with the fresh output, updating the generation date/comment.

---

## Exit Condition

Sheet, `TraitSystem.md`, and `balance-framework.md` all reflect the tuned values. Report a summary of which champions changed and by how much.

---

## Constraints

- Never edit `ChampionRoster.cs` here — this skill only publishes what `/tune-champion` already wrote
- Surgical doc edits only — never rewrite an entire GDD or the whole balance-framework.md file
- If `push_stats_to_sheet.py` aborts on a name mismatch, stop and report it — do not edit the sheet by hand to force a match
