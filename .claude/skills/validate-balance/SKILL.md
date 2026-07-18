Step-skill: runs the Layer 3 simulation (`Assets/Editor/BalanceValidator.cs`, Unity menu **Magic School → Validate Balance**) and reports the win-rate matrix, flagging matchups outside the expected band. Read-only against the project. Called by `/balance-pass` after all out-of-band champions have been tuned; loops back to `/tune-champion` if it flags outliers.

---

## Agent

`claude`

---

## Docs

| Doc | Read/Write | Purpose |
|---|---|---|
| `.claude/docs/balance/balance-framework.md` | Read | Expected win-rate bands by cost difference, simulation rules |
| `Assets/Editor/BalanceValidator.cs` | Read | Confirm the menu path and simulation parameters haven't changed |

---

## Entry Condition

All champions currently known to be out of their Layer 2 band have already been through `/tune-champion` (or the user explicitly chose to skip some via `done`).

---

## Step 1 — Compile check

Run `check_compile_errors`. If there are compile errors from a prior `/tune-champion` edit, stop and report them — do not run a simulation against a project that doesn't build.

---

## Step 2 — Run the simulation

Invoke the Unity Editor menu **Magic School → Validate Balance** via `execute_script`, then read the results via `get_unity_logs`. This runs 200 1v1 battles for all champion pairs and prints a win-rate matrix.

---

## Step 3 — Report outliers

Compare printed win rates against `balance-framework.md`'s Expected Win-Rate Bands table (e.g. +1 cost tier should win 55–80%). List every matchup outside its expected band, with the actual win rate and the champions involved.

---

## Step 4 — Route back if needed

If outliers exist, name which champion(s) are implicated and hand them back to `/tune-champion` for another pass. If clean, report "Layer 3 validation clean" and proceed to `/push-champion-stats`.

---

## Exit Condition

Win-rate matrix is within expected bands for all matchups (or the user explicitly accepts a remaining outlier).

---

## Constraints

- Never edit `ChampionRoster.cs`, the sheet, or any doc — this skill only runs the simulation and reports
- Never skip the compile check before running the simulation
- Base-stat simulation rules (no traits/shields/mana/Striker stacks, `IncludeCrit = false` by default) are the tool's own defaults — don't override them without the user asking specifically to check CRIT variance
