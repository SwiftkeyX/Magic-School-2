# AGENTS.md — Contract for all AI agents (Antigravity, Cursor, etc.)

This project is primarily driven by Claude Code; its full process lives in `CLAUDE.md` and `.claude/rules/`. If you are not Claude Code, this file is your contract. The rule files it references are plain markdown — read them. When anything conflicts, `.claude/rules/` wins.

## Read before any work

- `.claude/rules/git-hygiene.md` — branch, commit, and push rules
- `.claude/rules/workflow.md` — end-to-end task lifecycle and GDD gates
- `.claude/rules/unity-editor.md` — how Unity is edited (MCP tools, scene rules)
- `.claude/rules/docs-structure.md` — fixed folder shape of `.claude/docs/`
- `.claude/rules/doc-conventions.md` — doc ownership and change routing

## Hard rules

### Git
- NEVER commit or push to `main`. All work happens on a feature branch named `<type>/<short-kebab-desc>`, type ∈ `feat|fix|chore|docs|refactor`.
- NEVER force-push or rebase shared history.
- Push only after the user explicitly confirms.

### Unity
- NEVER hand-edit `.unity` scene YAML. Use the coplay MCP tools (`create_game_object`, `set_property`, `execute_script`, ...). If coplay is not connected, stop and tell the user.
- Only one AI tool may drive the Unity Editor at a time. Do not use coplay while Claude Code (or any other agent) has an active session against the editor.
- NEVER call `DontDestroyOnLoad()` — persistent objects belong in `Bootstrap.unity`.
- NEVER call `SceneManager.LoadScene` directly or use `LoadSceneMode.Single` — go through `SceneLoader`.
- New scenes go at `Assets/Scenes/<SceneName>.unity`, never at the `Assets/` root.
- After scene or script changes: check compile errors, play-test, then save the scene.

### GDD gate
- Before modifying any `.cs` under `Assets/Scripts/`, read the owning design doc at `.claude/docs/production/gdd/<System>.md`.
- If your change diverges from the GDD, STOP and flag the divergence to the user — do not edit GDD files yourself. GDD edits are routed through Claude Code's `/write-gdd` and `/reconcile-gdd` workflows.

### Docs
- NEVER create new top-level folders under `.claude/docs/` or `.claude/template-docs/`. Cross-phase or miscellaneous docs go in `.claude/docs/other/`.
- If you add or move a doc, update `.claude/docs/index.md` in the same change.

## Claude Code-only machinery — do not emulate

- `.claude/skills/` are Claude Code slash-command workflows (`/code`, `/make-commit-plan`, `/reconcile-gdd`, ...). Do not run or imitate them.
- Do the minimal equivalent instead: plain atomic commits on a feature branch; leave PR opening and GDD reconciliation to the Claude Code lifecycle unless the user says otherwise.
- `.claude/agents/`, Claude's `memory/`, and the audit-header rules in `.claude/rules/claude-behavior.md` apply to Claude Code only.

## Centralization & Antigravity (Claude Code no. 2)

- **Centralized Skills:** All agent skills, tools, and custom behaviors must reside under `.claude/`. The `.agents/` directory must remain empty, save for `.agents/skills.json` which maps to `.claude/skills/` to pull in centralized definitions.
- **No Local Skills:** Antigravity (and other secondary agents) must not define independent local skills or plugins under `.agents/`. Any custom workflows must be read and followed directly from `.claude/skills/`.
- **Role Alignment (Antigravity - Game Balance Specialist):** Antigravity operates under a specialized role focused entirely on game balancing. Antigravity can read the entire codebase and project files, but only has write permission to files within `.claude/docs/balance/` and the project's Google Sheets (such as the custom auto-battler sheet, while TFT reference sheets are read-only). All coding, Unity editor manipulation, and implementation tasks are strictly handled by Claude Code.

## Claude Command Guide (Co-pilot Integration)

Antigravity should contextually recommend the following Claude Code slash-command workflows to the user:
1. `/read-gdd <system>` — Recommend when starting work on a system or feature to read its design document first.
2. `/write-gdd <system>` — Recommend when a design change is required before editing code, so GDD is updated properly.
3. `/reconcile-gdd` — Recommend after completing code changes to sync implementation details back to GDDs.
4. `/make-commit-plan` — Recommend before staging files to create clean, structured git commits.
5. `/fix-bug <desc>` — Recommend to troubleshoot compilation errors or run automated bug-fixing passes.
6. `/open-pr` — Recommend when a feature is complete and ready to be merged into main.


