# Script Hygiene

**Never create a new automation/utility script at the project root.** The root holds only what Unity requires there (`*.csproj`, `ProjectSettings/`, `Packages/`, etc.) plus a small set of gitignored data files. Every custom script — Python, PowerShell, shell — lives under `.claude/scripts/`.

## Hard rules

- **New scripts go in `.claude/scripts/`.** This already holds `refresh-gh-token.{py,ps1,sh}` — join that folder rather than dropping a new file at root.
- **Invocation convention:** always run from repo-root cwd using the full path — `python .claude/scripts/<name>.py` — matching the existing `refresh-gh-token.py` precedent. Never `cd` into `.claude/scripts/` first; scripts resolve project paths (e.g. `Assets/...`, root-level credential/dump files) relative to cwd, not to their own location.
- **A related group of scripts gets its own subfolder** — `python .claude/scripts/<dir>/<name>.py`, e.g. `.claude/scripts/tft-set9-skill-modularity/`. Anything with its own data, archive, or helper module belongs in one, so that generic names (`data/`, `archive/`) cannot collide with another group's. **Name the folder for the job it does, not the domain it sits in**: several scripts here touch TFT, so a bare `tft/` would claim a namespace it does not own. The rule's real point is that nothing custom lives at the **project root** — that still holds.
- **This rule targets custom tooling only.** It does not apply to Unity-mandated root files, which must stay where Unity puts them.
- **Gitignored secrets/generated data may stay at root** if a script's relative-path resolution already depends on repo-root cwd. That's a narrow exception for existing data files, not license to add new scripts there.
- **When you add a script, update the doc/skill that references it** (path in code fences, `file://` links) in the same change — a script that moves without its references is a broken reference (see `doc-conventions.md`).
