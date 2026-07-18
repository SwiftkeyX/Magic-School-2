Standalone balance health-check: runs the sheet-driven balance report and surfaces the sheet↔code consistency gate, Layer 2 scores vs. band, skill/mana cycle economics, and live trait tables. Invocable any time — no PIPELINE gate. First step of `/balance-pass`, but also useful on its own whenever you want a balance snapshot.

---

## Agent

`claude`

---

## Docs

| Doc | Read/Write | Purpose |
|---|---|---|
| `.claude/scripts/balance_report.py` | Read (execute) | The report generator — reads the live sheet + `ChampionRoster.cs`, computes everything below |
| `.claude/docs/balance/balance-framework.md` | Read | Layer 2 Score formula and target bands, to interpret the report |
| `.claude/docs/balance/data-sources.md` | Read | Which sheet is canonical, in case the consistency gate needs a source-of-truth call |

---

## Entry Condition

Invocable at any time. No PIPELINE.md gate — this is cross-phase, ongoing work per `balance-framework.md`'s own scope.

---

## Step 1 — Run the report

Execute `python .claude/scripts/balance_report.py` from repo root. Read the four sections of its output: consistency gate, Layer 2 scores, skill/mana cycle, trait breakpoints.

---

## Step 2 — Resolve the consistency gate first

If the report's §1 consistency gate lists any mismatches (name/cost/trait/role/stat divergence between the sheet and `ChampionRoster.cs`):

```
--- MISMATCH: <Champion> ---
Field:  <field name>
Sheet:  <sheet value>
Code:   <code value>
```

`ChampionRoster.cs` is canonical for numeric stats (per `data-sources.md`) — a stat drift is fixed by re-running `push-champion-stats`. A design-field mismatch (role/cost/trait) has no automatic resolution: ask the user which side is correct, then either edit the sheet cell directly (`sheet_sync.py write`) or flag it for `/code` if `ChampionRoster.cs` needs to change.

**Stop here if mismatches exist** — do not proceed to score analysis on a sheet/code pair that disagrees with itself.

---

## Step 3 — Report Layer 2 scores vs. band

List every champion outside its cost-tier band (from `balance-framework.md`'s Target Score Bands table), grouped by cost tier. This is the actionable list for `/tune-champion`.

---

## Step 4 — Report skill/mana cycle and trait tables

Surface the report's §3 (skill impact vs. auto-DPS, mana cycle) and §4 (live trait breakpoints) as-is — informational context for tuning decisions, not an action list.

---

## Exit Condition

Report printed in full. If run standalone: done. If run as `/balance-pass` Step 1: hand the out-of-band champion list to `/tune-champion`.

---

## Constraints

- Never modify `ChampionRoster.cs`, the sheet, or any doc — this skill only reads and reports
- Never proceed past an unresolved consistency-gate mismatch
- Never invoke coplay MCP tools — this is a script + doc read only
