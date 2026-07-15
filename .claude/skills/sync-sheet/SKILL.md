---
name: sync-sheet
description: Read and write data to/from any of the project's 5 Google Sheets (Custom Auto-Battler, TFT Set 9, TFT Set 9 Analysis, TFT Set 10, TFT Set 11) using the background sheet_sync.py script.
---

# Google Sheet Sync Skill (Background API)

This skill allows the agent to read and write to the project's Google Sheets directly in the background using the [sheet_sync.py](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School/.claude/scripts/sheet_sync.py) command-line utility. This avoids launching a browser and interrupting the user.

There are **5 registered sheets** (see [`sheets_config.json`](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School/.claude/scripts/sheets_config.json) and [`data-sources.md`](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School/.claude/docs/balance/data-sources.md) for the full registry): `auto-battler` (default — ours, canonical), `tft-set9`, `tft-set9-analysis`, `tft-set10`, and `tft-set11` (external references). All five are marked `writable: true` — there is no read-only guard on any registered sheet. Select a non-default sheet with `--sheet <name>` before the subcommand, e.g. `python .claude/scripts/sheet_sync.py --sheet tft-set9 read <TabName>`.

## Purpose of the Google Sheet (`auto-battler`, the default)
This Google Sheet acts as the **design database** for the game. It contains the source of truth for:
* **Heroes**: All champions — cost, classes, origins, roles, combat logic, and full numeric stats (HP, ATK, DEF, MG, MR, AS, CRIT, Range, MaxMana, StartingMana).
* **Origins (Vertical Classes)**: breakpoints and effects.
* **Classes (Horizontal Classes)**: breakpoints and effects.
* **Dashboard**: An interactive team builder and trait tracker for checking synergies.

`ChampionRoster.cs` remains the **canonical** source for numeric stats — the Heroes tab's stat columns are a read-friendly mirror of it, not an independent source. When code stats change, re-run `python .claude/scripts/push_stats_to_sheet.py` (from repo root) to refresh the mirror; it matches rows by champion name and aborts if the sheet has a name the code doesn't (or vice versa), so it never silently misaligns a row.

The code in [ChampionRoster.cs](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School/Assets/Scripts/Battle/Traits/ChampionRoster.cs) and [TraitSystem.md](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School/.claude/docs/production/gdd/TraitSystem.md) must remain in sync with this sheet.

## Credentials
The credentials for this connection are stored in the root credential file [google-service-credential.json](file:///c:/Organized%20Files/Working/Unity/Unity%20Project/Magic%20School/google-service-credential.json).

## Steps to Read the Sheet
To fetch data from any tab in the spreadsheet, run `.claude/scripts/sheet_sync.py` from the workspace root.

* **Format as Table (Human-Readable):**
  ```bash
  python .claude/scripts/sheet_sync.py read <TabName>
  ```
* **Format as JSON (For parsing):**
  ```bash
  python .claude/scripts/sheet_sync.py read <TabName> --format json
  ```
* **Format as CSV:**
  ```bash
  python .claude/scripts/sheet_sync.py read <TabName> --format csv
  ```

*Available TabNames: `Heroes`, `Origin`, `Class`, `Dashboard`.*

## Steps to Write to the Sheet
To update a cell in the spreadsheet, run the script's `write` command:

```bash
python .claude/scripts/sheet_sync.py write <TabName> <Cell> "<Value>"
```
*Example:*
```bash
python .claude/scripts/sheet_sync.py write Heroes B2 "Ironclad"
```

## Steps to Bulk-Write Rows

To write many rows in a single API call (e.g. rebuilding a whole data block), use the `write-range` command. It takes a worksheet name, a start cell, and a `--file` pointing to a local JSON file containing a list of rows (each row itself a list of cell values — use JSON rather than CSV so fields containing commas don't need escaping):

```bash
python .claude/scripts/sheet_sync.py --sheet tft-set9 write-range "Meta Comps" A1 --file rows.json
```

If the named worksheet doesn't exist yet, it is created automatically (sized to fit the data) before writing — useful for adding a brand-new tab to a spreadsheet. Same `writable: true` guard as `write` applies.

## Steps to Dump All Sheet Content
To download all tabs of a sheet into a single local, self-describing JSON file (default name `<sheet>_dump_<date>.json`, embeds a `_meta` block with sheet name/key/timestamp):

```bash
python .claude/scripts/sheet_sync.py dump
python .claude/scripts/sheet_sync.py --sheet tft-set9 dump
```
