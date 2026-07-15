#!/usr/bin/env python3
"""Push champion numeric stats from ChampionRoster.cs into the Heroes sheet.

The Heroes tab currently holds design data only (cost, traits, role, combat
logic) with no numeric stats. This adds stat columns (HP, ATK, DEF, MG, MR,
AS, CRIT, Range, MaxMana, StartingMana) so the sheet becomes readable at a
glance without cross-referencing the code, matched to existing sheet rows by
champion name (not by row index) so no data is misaligned.
"""
import sys

import sheet_sync
from balance_report import parse_roster, ROSTER_PATH, STAT_COLUMNS, STAT_TO_CODE_FIELD as FIELD_MAP


def col_letter(n):
    """1-indexed column number -> spreadsheet column letter."""
    letters = ""
    while n > 0:
        n, rem = divmod(n - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def main():
    champions = parse_roster(ROSTER_PATH)
    by_name = {c["DisplayName"]: c for c in champions}

    client = sheet_sync.get_client()
    sh = sheet_sync.get_spreadsheet(client, sheet_name="auto-battler")
    ws = sh.worksheet("Heroes")
    rows = ws.get_all_values()
    header, data_rows = rows[0], rows[1:]

    name_col_idx = header.index("Champion Name")
    existing_stat_cols = [c for c in STAT_COLUMNS if c in header]
    if existing_stat_cols:
        print(f"Columns already present, aborting to avoid duplicates: {existing_stat_cols}")
        sys.exit(1)

    missing = [name for name in (r[name_col_idx] for r in data_rows) if name not in by_name]
    if missing:
        print(f"Sheet has names missing from ChampionRoster.cs, aborting: {missing}")
        sys.exit(1)

    start_col_num = len(header) + 1  # next free column, 1-indexed
    end_col_num = start_col_num + len(STAT_COLUMNS) - 1
    start_letter, end_letter = col_letter(start_col_num), col_letter(end_col_num)

    values = [STAT_COLUMNS]
    for row in data_rows:
        name = row[name_col_idx]
        champ = by_name[name]
        values.append([str(champ[FIELD_MAP[col]]) for col in STAT_COLUMNS])

    range_name = f"{start_letter}1:{end_letter}{len(data_rows) + 1}"
    ws.update(range_name=range_name, values=values)
    print(f"Wrote {len(STAT_COLUMNS)} stat columns ({start_letter}:{end_letter}) for {len(data_rows)} champions to Heroes!{range_name}")


if __name__ == "__main__":
    main()
