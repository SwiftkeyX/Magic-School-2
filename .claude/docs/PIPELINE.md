# PIPELINE.md

## Phase 1 — Pre-production

- [ ] Fill out `docs/preproduction/game-vision.md`
- [ ] Fill out `docs/preproduction/design-decisions.md`
- [ ] Fill out `docs/preproduction/technical-preferences.md` (engine, platform, performance budgets)
- [ ] Fill out `docs/preproduction/systems-design.md` — list every system, tier, and dependencies
- [ ] Fill out `docs/preproduction/architecture.md` with finalized script table
- [ ] Fill out `docs/preproduction/best-practices.md` — add project-critical patterns section
- [ ] Milestone 0 — vision complete, all systems tiered, architecture and tech stack finalized

## Phase 2 — Production

### Tier 1 — Foundation
- [ ] Create `docs/production/gdd/<system>.md` for each Tier 1 system (copy `.claude/template-docs/production/gdd/_template.md`)
- [ ] *(fill in your Tier 1 systems)*

### Tier 2 — Core Loop
- [ ] Create `docs/production/gdd/<system>.md` for each Tier 2 system (copy `.claude/template-docs/production/gdd/_template.md`)
- [ ] *(fill in your Tier 2 systems)*

- [ ] Milestone 1 — core loop playable end-to-end

### Tier 3 — Supporting Systems
- [ ] Create `docs/production/gdd/<system>.md` for each Tier 3 system (copy `.claude/template-docs/production/gdd/_template.md`)
- [ ] *(fill in your Tier 3 systems)*

- [ ] Milestone 2 — all features in, content complete

## Phase 3 — Beta

- [ ] Juice pass — screen shake, particles, hit-stop, SFX, music, UI animations
- [ ] Feel tuning — tweak values via ScriptableObjects/Inspector
- [ ] Difficulty tuning — curve, pacing, escalation
- [ ] Bug pass — all known issues fixed (`docs/beta/known-issues.md` clear)
- [ ] Performance pass — GC allocs and frame rate within budgets (`docs/preproduction/technical-preferences.md`)
- [ ] Ship — final build, smoke test, release (`docs/beta/build-notes.md` checklist)
