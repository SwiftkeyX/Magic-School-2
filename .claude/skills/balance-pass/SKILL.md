Cross-phase orchestrator: runs the full sheet-driven balance workflow end to end — checks balance state, tunes every out-of-band champion, validates via simulation, and publishes the result. Invocable any time; not gated by PIPELINE.md, since balancing is ongoing work per `balance-framework.md`'s own "cross-phase" scope.

---

## Agent

Orchestrator — routes to sub-skills. See sub-skill agent assignments.

---

## Docs

| Doc | Read/Write | Purpose |
|---|---|---|
| `.claude/docs/balance/balance-framework.md` | Read | The 3-layer process and target bands this pass enforces |

---

## Entry Condition

None — invocable any time.

---

## Steps

**Step 1 — Check balance state**
Run `/check-balance`. If it reports consistency-gate mismatches, stop here — the user must resolve those before tuning can proceed.

**Step 2 — Tune every out-of-band champion**
For each champion `/check-balance` §3 flagged outside its band, run `/tune-champion`. Loop through the full list — never skip a champion silently.

**Step 3 — Validate**
Run `/validate-balance`. If it flags win-rate outliers, route the implicated champions back to `/tune-champion` (Step 2), then re-run `/validate-balance`. Repeat until clean or the user accepts a remaining outlier.

**Step 4 — Publish**
Once `/validate-balance` is clean, run `/push-champion-stats`.

---

## Exit Condition

`/push-champion-stats` has completed — sheet, `TraitSystem.md`, and `balance-framework.md`'s Current Scores table all reflect the tuned roster.

---

## Constraints

- Never skip a step-skill or reorder them — consistency gate, then tuning, then validation, then publish, in that order
- Never proceed past an unresolved consistency-gate mismatch from Step 1
- Never tick `PIPELINE.md` — this pass isn't phase-gated
