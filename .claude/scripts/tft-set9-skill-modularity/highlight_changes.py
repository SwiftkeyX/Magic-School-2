"""Colour the cells the writers changed, so a review is easy. REUSABLE every round.

    python .claude/scripts/tft-set9-skill-modularity/highlight_changes.py           # colour, clear prior
    python .claude/scripts/tft-set9-skill-modularity/highlight_changes.py --clear   # remove all highlights

`sync.py` / `force_full.py` RECORD every cell they change into `changes-state.json` (see
`sheet.record_changes`). This reads that, CLEARS the previous round's highlight (so old amber does not
pile up), paints the newly-changed cells amber, and rotates `pending -> highlighted` so the next round
starts clean. Run it right after a sync / force_full round; run again next round and only the newest
changes stay coloured.

Merged cells: the writers record the exact cell they wrote; a cell that later became a non-anchor of a
merge is coloured harmlessly (Sheets applies the fill to the merge's anchor). Run from repo-root cwd,
PYTHONIOENCODING=utf-8.
"""
import json
import re
import sys

from sheet import CHANGES_FILE, open_sheet

AMBER = {"red": 1.0, "green": 0.85, "blue": 0.4}    # "I changed this"
WHITE = {"red": 1.0, "green": 1.0, "blue": 1.0}     # cleared (sheet default)


def parse_a1(a1):
    """'P5' -> (row0, col0), both 0-based. Tolerates a gspread sheet prefix ("'Hero set 9'!P5"):
    gspread.Worksheet.batch_update rewrites each edit's range to include the tab title, and that is
    what the writers record, so strip everything up to the last '!'."""
    a1 = a1.split("!")[-1].strip()
    m = re.fullmatch(r"([A-Z]+)(\d+)", a1)
    col = 0
    for ch in m.group(1):
        col = col * 26 + (ord(ch) - 64)
    return int(m.group(2)) - 1, col - 1


def fmt(gid, a1, color):
    r, c = parse_a1(a1)
    return {"repeatCell": {
        "range": {"sheetId": gid, "startRowIndex": r, "endRowIndex": r + 1,
                  "startColumnIndex": c, "endColumnIndex": c + 1},
        "cell": {"userEnteredFormat": {"backgroundColor": color}},
        "fields": "userEnteredFormat.backgroundColor"}}


def main(clear=False):
    if not CHANGES_FILE.exists():
        print("no changes-state.json — nothing to highlight (run sync/force_full first)")
        return
    state = json.loads(CHANGES_FILE.read_text(encoding="utf-8"))
    sh = open_sheet()
    gid = {ws.title: ws.id for ws in sh.worksheets()}
    reqs = []

    # 1. clear the PREVIOUS round's highlight, always — old amber must not accumulate
    cleared = 0
    for tab, cells in state.get("highlighted", {}).items():
        if tab in gid:
            reqs += [fmt(gid[tab], a1, WHITE) for a1 in cells]
            cleared += len(cells)

    if clear:
        if reqs:
            sh.batch_update({"requests": reqs})
        state["highlighted"] = {}
        CHANGES_FILE.write_text(json.dumps(state, indent=1), encoding="utf-8")
        print(f"cleared {cleared} highlighted cells")
        return

    # 2. paint the PENDING (newly changed) cells amber
    painted = 0
    for tab, cells in state.get("pending", {}).items():
        if tab in gid:
            reqs += [fmt(gid[tab], a1, AMBER) for a1 in cells]
            painted += len(cells)

    if reqs:
        sh.batch_update({"requests": reqs})

    # 3. rotate pending -> highlighted so the next round clears exactly these
    state["highlighted"] = state.get("pending", {})
    state["pending"] = {}
    CHANGES_FILE.write_text(json.dumps(state, indent=1), encoding="utf-8")
    print(f"highlighted {painted} changed cells amber ({cleared} prior highlights cleared)")


if __name__ == "__main__":
    main(clear="--clear" in sys.argv)
