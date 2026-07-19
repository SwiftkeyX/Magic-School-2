"""Build the sheet's `Dashboard` tab — the hero filter/query view.

Run from repo-root cwd:
    python .claude/scripts/tft-set9-skill-modularity/build_dashboard_tab.py

IT READS `Hero flat`, NEVER THE HERO TABS. The Hero tabs are merged for human reading: a blank cell
means "same as the row above", values live only in each merged run's top-left cell, and a range read
DISAGREES with a single-cell read about merged cells — so a FILTER over a Hero tab silently skips run
tops and returns another champion's value. `Hero flat` is the un-blanked mirror (flatten.py), rebuilt
from the CSVs at the top of every sync, so everything here is an ordinary FILTER over a plain table.

Dashboard is a VIEW, not data: it holds formulas, has no CSV, and must never be added to
sheet.TABS or sync.py would overwrite it. This script is its only writer and is idempotent.

DASHBOARD SEMANTICS. The filters mix two grains, and the mix is the point. Hero-level filters (set,
cost, origin, class, role) constrain the hero; row-level ones (action, aim, trigger, effect...)
constrain any single row of that hero's ability. A hero is listed when AT LEAST ONE of their rows
satisfies everything — a semi-join, which falls out of FILTER-then-UNIQUE because the hero-level
columns are identical on every row of a hero, so UNIQUE collapses them to exactly one row per hero.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sheet  # noqa: E402

QUERY_TAB = 'Dashboard'
FLAT = 'Hero flat'
ANY = '(any)'


def a1(col, row):
    s = ''
    while col:
        col, r = divmod(col - 1, 26)
        s = chr(65 + r) + s
    return '%s%d' % (s, row)


def col_letter(col):
    return a1(col, 1)[:-1]


def fcol(letter):
    return "'%s'!$%s$2:$%s" % (FLAT, letter, letter)


# ---------------------------------------------------------------------------------------------
# Filters. `src` is the flat-tab column(s) a filter tests; None means it is handled specially.
# Order here is the order they appear on the tab (left column first, then right).
FILTERS = [
    ('Set', ['A']), ('Cost', ['C']), ('Origin', ['E', 'F']), ('Class', ['G', 'H']),
    ('Role', ['D']), ('Active / Passive', ['M']), ('Trigger', ['N']), ('Condition', ['O']),
    ('Action source', ['P']),
    # 'Action group' (AH on the flat tab) collapses the 28 actions into 7 families — Projectile,
    # AOE, Beam, Charge, Summon, Movement, Direct — so you can ask "who uses a projectile at all?"
    # without naming five actions. The grouping is authored on the Action Model tab, not here.
    ('Action group', ['AH']), ('Action', ['Q']),
    ('Aim target', ['R']), ('AOE (hex)', ['T']), ('Count', ['V']),
    ('Recipient', ['Z']), ('Effect category', ['AA']), ('Effect detail', ['AB']),
    ('Scaling type', ['AD']),
]
SEARCH_LABEL = 'Text search'

RESULT_COLS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
RESULT_HEAD = ['Set', 'Champion', 'Cost', 'Role', 'Origin 1', 'Origin 2', 'Class 1', 'Class 2',
               'Range', 'Nickname']

HEAD_ROW = 16
FIRST = HEAD_ROW + 1
HELP_COL = 53          # BA — hidden option lists, one column per dropdown


def filter_positions():
    """[(label, srcs, label_ref, cell_ref, help_col), ...] laid out in two columns."""
    out = []
    half = (len(FILTERS) + 1) // 2
    for i, (label, srcs) in enumerate(FILTERS):
        if i < half:
            lab, cell = 'B%d' % (5 + i), 'C%d' % (5 + i)
        else:
            lab, cell = 'E%d' % (5 + i - half), 'F%d' % (5 + i - half)
        out.append((label, srcs, lab, cell, HELP_COL + i))
    return out


def search_cell():
    half = (len(FILTERS) + 1) // 2
    row = 5 + len(FILTERS) - half
    return 'E%d' % row, 'F%d' % row


def conditions():
    """One FILTER condition per filter, plus the text search."""
    conds = []
    for label, srcs, _lab, cell, _hc in filter_positions():
        ref = abs_ref(cell)
        # '(any)' short-circuits the test, so an untouched filter constrains nothing. Origin and
        # Class pass TWO source columns because a hero can carry either slot.
        eq = '+'.join('(%s=%s)' % (fcol(s), ref) for s in srcs)
        conds.append('((%s="%s")+%s)' % (ref, ANY, eq))
    _lab, scell = search_cell()
    # Searched text is matched against the fields you would plausibly search by.
    ref = abs_ref(scell)
    hay = '&" "&'.join(fcol(c) for c in ['B', 'K', 'Q', 'R', 'AA', 'AB', 'AC'])
    conds.append('((%s="")+ISNUMBER(SEARCH(%s,%s)))' % (ref, ref, hay))
    return conds


def abs_ref(cell):
    return '$%s$%s' % (cell[0], cell[1:])


def query_cells():
    c = {}
    c['B2'] = 'Hero Query'
    c['B3'] = ("Filter across every hero and see who matches. Hero-level filters (set, cost, origin, "
               "class, role) narrow the hero; the rest match ANY single row of their ability. "
               "Leave a filter on '(any)' to ignore it.")

    for label, srcs, lab, cell, hc in filter_positions():
        c[lab] = label
        c[cell] = ANY
        # option list for this dropdown, with (any) on top
        stacked = ';'.join(fcol(s) for s in srcs)
        c[a1(hc, 1)] = ('={"%s";SORT(UNIQUE(FILTER({%s},{%s}<>"")))}'
                        % (ANY, stacked, stacked))

    slab, scell = search_cell()
    c[slab] = SEARCH_LABEL
    c[scell] = ''

    conds = conditions()
    arr = ','.join(fcol(x) for x in RESULT_COLS)
    result = ('SORT(UNIQUE(FILTER({%s},%s)),1,TRUE,3,TRUE,2,TRUE)' % (arr, ','.join(conds)))
    c[a1(2, FIRST)] = '=IFERROR(%s,"")' % result

    for j, label in enumerate(RESULT_HEAD):
        c[a1(2 + j, HEAD_ROW)] = label

    c['B14'] = 'Heroes matched'
    c['C14'] = '=COUNTA($C$%d:$C)' % FIRST
    return c


# ---------------------------------------------------------------------------------------------
def ensure(sh, title, rows, cols):
    try:
        ws = sh.worksheet(title)
        print('%s: exists — refreshing' % title)
    except Exception:
        ws = sh.add_worksheet(title=title, rows=rows, cols=cols)
        print('%s: created' % title)
    if ws.row_count < rows:
        ws.add_rows(rows - ws.row_count)
    if ws.col_count < cols:
        ws.add_cols(cols - ws.col_count)
    return ws


def write(ws, cells):
    ws.batch_clear(['A1:CZ%d' % ws.row_count])
    data = [{'range': '%s!%s' % (ws.title, r), 'values': [[v]]} for r, v in sorted(cells.items())]
    ws.spreadsheet.values_batch_update({'valueInputOption': 'USER_ENTERED', 'data': data})
    print('%s: wrote %d cells' % (ws.title, len(cells)))


def fmt_common(sid, head_row, ncols, note_width=9):
    def rng(r1, c1, r2, c2):
        return {'sheetId': sid, 'startRowIndex': r1, 'endRowIndex': r2,
                'startColumnIndex': c1, 'endColumnIndex': c2}
    return [
        {'repeatCell': {'range': rng(1, 1, 2, 2),
                        'cell': {'userEnteredFormat': {'textFormat': {'bold': True,
                                                                      'fontSize': 15}}},
                        'fields': 'userEnteredFormat.textFormat'}},
        {'repeatCell': {'range': rng(2, 1, 3, note_width),
                        'cell': {'userEnteredFormat': {'textFormat': {
                            'italic': True,
                            'foregroundColor': {'red': .45, 'green': .45, 'blue': .5}}}},
                        'fields': 'userEnteredFormat.textFormat'}},
        {'repeatCell': {
            'range': rng(head_row - 1, 1, head_row, 1 + ncols),
            'cell': {'userEnteredFormat': {
                'backgroundColor': {'red': .17, 'green': .16, 'blue': .22},
                'textFormat': {'bold': True, 'fontSize': 9,
                               'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
                'verticalAlignment': 'MIDDLE', 'wrapStrategy': 'CLIP'}},
            'fields': ('userEnteredFormat(backgroundColor,textFormat,verticalAlignment,'
                       'wrapStrategy)')}},
        {'updateSheetProperties': {
            'properties': {'sheetId': sid, 'gridProperties': {'frozenRowCount': head_row}},
            'fields': 'gridProperties.frozenRowCount'}},
        {'updateDimensionProperties': {
            'range': {'sheetId': sid, 'dimension': 'COLUMNS', 'startIndex': HELP_COL - 1,
                      'endIndex': HELP_COL + len(FILTERS)},
            'properties': {'hiddenByUser': True}, 'fields': 'hiddenByUser'}},
    ]


def main():
    sh = sheet.open_sheet()
    assert QUERY_TAB not in sheet.TABS, 'Dashboard must never be a sync-owned tab'
    assert FLAT in sheet.TABS, 'Hero flat must be synced before these views can read it'

    # ---- Dashboard (query) --------------------------------------------------------------------
    ws = ensure(sh, QUERY_TAB, 200, HELP_COL + len(FILTERS) + 2)
    write(ws, query_cells())
    sid = ws.id

    def rng(r1, c1, r2, c2):
        return {'sheetId': sid, 'startRowIndex': r1, 'endRowIndex': r2,
                'startColumnIndex': c1, 'endColumnIndex': c2}

    reqs = fmt_common(sid, HEAD_ROW, len(RESULT_HEAD))
    for label, srcs, lab, cell, hc in filter_positions():
        col = ord(cell[0]) - 65
        row = int(cell[1:]) - 1
        reqs.append({'setDataValidation': {
            'range': rng(row, col, row + 1, col + 1),
            'rule': {'condition': {'type': 'ONE_OF_RANGE',
                                   'values': [{'userEnteredValue': '=$%s$1:$%s$300'
                                               % (col_letter(hc), col_letter(hc))}]},
                     'showCustomUi': True, 'strict': False}}})
        lrow, lcol = int(lab[1:]) - 1, ord(lab[0]) - 65
        reqs.append({'repeatCell': {
            'range': rng(lrow, lcol, lrow + 1, lcol + 1),
            'cell': {'userEnteredFormat': {'textFormat': {'bold': True}}},
            'fields': 'userEnteredFormat.textFormat'}})
    for c0, w in ((1, 128), (2, 190), (4, 128), (5, 190)):
        reqs.append({'updateDimensionProperties': {
            'range': {'sheetId': sid, 'dimension': 'COLUMNS', 'startIndex': c0,
                      'endIndex': c0 + 1},
            'properties': {'pixelSize': w}, 'fields': 'pixelSize'}})
    reqs.append({'repeatCell': {
        'range': rng(13, 1, 14, 2),
        'cell': {'userEnteredFormat': {'textFormat': {'bold': True}}},
        'fields': 'userEnteredFormat.textFormat'}})
    sh.batch_update({'requests': reqs})
    print('%s: filters + formatting applied (gid=%s)' % (QUERY_TAB, sid))


if __name__ == '__main__':
    main()
