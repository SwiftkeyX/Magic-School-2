Step-skill: brings one champion's Layer 2 Stat Budget Score into its cost-tier band. Proposes one stat change at a time, applies it, recomputes the score, and loops until in-band or the user says done. Called by `/balance-pass` once per out-of-band champion found by `/check-balance`; mirrors `/tune-pass`'s propose→apply→recheck→loop shape for pure numeric convergence toward an already-documented target — no `/code` GDD-read gate needed since no new design is happening.

---

## Agent

`systems-designer`

---

## Docs

| Doc | Read/Write | Purpose |
|---|---|---|
| `Assets/Scripts/Battle/Traits/ChampionRoster.cs` | Read + Write | The champion's stat block being tuned |
| `.claude/docs/balance/balance-framework.md` | Read | Layer 2 Score formula, target bands, and the Offense/EHP definitions |
| `.claude/scripts/balance_report.py` | Read (execute) | Recompute the score after each change |

---

## Entry Condition

A specific champion and its current out-of-band Score (from `/check-balance` §3, or supplied directly). If invoked standalone, ask which champion and read their current stats from `ChampionRoster.cs` first.

---

## Step 1 — Identify the gap

State the champion's current Score, its band (`balance-framework.md` Target Score Bands table), and whether it's below (too weak) or above (too strong) the band, with the percentage gap.

---

## Step 2 — Propose one stat change

Pick the single stat most likely to close the gap without distorting the champion's role (e.g. a Tank's gap should close via HP/DEF, not ATK — don't turn a tank into a carry to hit a number). State:

1. Field + current value → proposed value (e.g. `MaxHP: 100 → 480`)
2. Recomputed Score at the proposed value
3. Rationale — why this stat, why this direction, and why it preserves the champion's `Design Role`/traits

Wait for the user to approve before applying. Do not apply multiple stat edits at once.

---

## Step 3 — Apply and recompute

Edit `ChampionRoster.cs`. Re-run `python .claude/scripts/balance_report.py` and confirm the champion's new Score.

---

## Step 4 — Evaluate and loop

Ask: **"In band now? (yes / no / tweak / done)"**

- **yes** — Score is in band; this champion is finished
- **no** — still out of band; return to Step 2 with a different or larger adjustment
- **tweak** — same stat, refine the value; return to Step 2
- **done** — user accepts the current state even if slightly outside the band (their call, not a silent skip)

---

## Exit Condition

Champion's Score is in-band (or user explicitly says `done`). If called from `/balance-pass`, return control to it for the next out-of-band champion.

---

## Constraints

- One stat edit per iteration — never batch multiple fields between recomputes
- Never add a new field to `ChampionRoster.cs`, change `Design Role`/traits, or touch the champion's `Skill` block — numeric stat tuning only, per `systems-designer`'s charter
- Never tick `PIPELINE.md` — this isn't a phase-gated step
- Always show the recomputed Score before asking the evaluate question
