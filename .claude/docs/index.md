# Docs Index

> **Structure:** docs live under only five folders — `preproduction/ production/ beta/ other/ tft/` — mirroring `.claude/template-docs/`. Never add a new folder; see `.claude/rules/docs-structure.md`.

## Pre-production (`preproduction/`)

| File | Purpose |
|---|---|
| `preproduction/game-vision.md` | Creative vision — genre, pillars, mechanics, art/audio direction |
| `preproduction/design-decisions.md` | Canonical terminology and mechanic constraints for the codebase |
| `preproduction/systems-design.md` | Every system, its responsibility, tier, and dependencies |
| `preproduction/architecture.md` | Script table — one row per script, responsibility, communication patterns |
| `preproduction/technical-preferences.md` | Engine, platform, performance budgets, test requirements, ADR log |
| `preproduction/best-practices.md` | Project-critical patterns + Unity 6 current patterns |

## Production (`production/`)

| File | Purpose |
|---|---|
| `production/gdd/<system>.md` | Per-system GDD — copy from `.claude/template-docs/production/gdd/_template.md` |

## Beta (`beta/`)

| File | Purpose |
|---|---|
| `beta/build-notes.md` | Unity version, build steps, and release checklist |
| `beta/known-issues.md` | Living bug list — open, fixed, and won't-fix |

## Other (`other/`)

| File | Purpose |
|---|---|
| `other/changelog.md` | Milestone log — one entry per significant decision or release |
| `other/architecture-overview.md` | Auto-generated SRP + coupling summary across all GDDs (`/read-architecture`) |
| `other/reading-guide-battle.md` | ⚠️ **TEMPORARY** — onboarding reading order for the Battle scripts. Delete this row when the file goes. |
| `other/adr/` | Architecture Decision Records — one file per decision |

## TFT reference (`tft/`)

| File | Purpose |
|---|---|
| `tft/tft-reference-sheets.md` | External TFT set 9/10/11 hero/trait/skill Google Sheets — auto-chess genre reference |
| `tft/set9-skill-schema-review.md` | Review: what the simplified set9-skill schema broke vs the intended version |
| `tft/set9-skill-design-notes.md` | The **why** behind the schema — one section per decision, and what it was decided against. The sheet's `Design Notes` tab holds the one-liners and links here |
| `tft/set10-skill-tab.md` | The `Hero set 10` tab — Set 10's 8-Bit/Country champions on the reused 31-col schema: the 9 champions, the 2nd-schema-tab tooling change (and the `Hero`→`Hero set 9` rename), the 3 new vocab rows, and the modelling calls to review |
| `tft/set9-skill-review-comments-archive.md` | Verbatim archive of the 79 resolved sheet-review comment threads (the *reasoning* lives in the sheet's `Design Notes`; this is the raw exchange) |
