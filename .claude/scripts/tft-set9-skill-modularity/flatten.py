"""Derive `hero-flat.csv` — the un-blanked, un-merged mirror of both schema tabs.

    from flatten import build_flat;  build_flat()

WHY THIS EXISTS. The Hero tabs are built for HUMANS to read: a blank cell means "same as the row
above", and `remerge_hero` turns each run of equal values into a merged range that stores its value
only in the top-left cell. That is unreadable to anything else. Formulas cannot reliably reconstruct
it either — a range read and a single-cell read DISAGREE about merged cells, so a FILTER over a Hero
tab silently skips run tops and returns a value belonging to a different champion. Nothing should
machine-read the merged tabs; they get this mirror instead.

The mirror is DERIVED, never authored — same standing as the merges themselves. `sync.py` rebuilds it
before every write, so it cannot drift from the CSVs it comes from. Do not edit hero-flat.csv by hand;
edit hero.csv / hero-set10.csv and sync.

THE UN-BLANKING RULE, and why the champion boundary is load-bearing:

    at a champion's first row -> take that row's own value, even when it is empty
    otherwise                 -> take the row's own value if it has one, else carry the last

The first clause is the whole point. A plain fill-down would carry the previous champion's value into
a cell that is legitimately empty — `Origin 2` and `Class 2` are blank for most champions — which is
exactly the bug that once gave Illaoi the previous hero's Class 2 (see [[tft-sheet-scripts]] #2). The
builder always writes explicit values (including "—") on a champion's defining rows, so resetting at
the boundary loses nothing.
"""

import csv
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')

SOURCES = [('Set 9', 'hero.csv'), ('Set 10', 'hero-set10.csv')]
OUT = 'hero-flat.csv'
NCOLS = 32


ACTION_COL = 15          # 0-based index of `Legacy action` in the 32-col schema


def _rows(fname):
    with io.open(os.path.join(DATA, fname), encoding='utf-8') as f:
        return list(csv.reader(f))


def _action_groups():
    """{action name: group} from the `Group` column on the Action Model tab.

    The grouping lives on that tab, not in this script, because a group is a property of the ACTION
    — the same reason Apply/Motion/Behavior live there. Returns {} if the column has not been added,
    so the flat mirror still builds.
    """
    rows = _rows('action-model.csv')
    head = [c.strip() for c in rows[0]]
    if 'Group' not in head:
        return {}
    gi = head.index('Group')
    out = {}
    for r in rows[1:]:
        name = (r[0] if r else '').strip()
        group = (r[gi] if gi < len(r) else '').strip()
        if name and group:
            out[name] = group
    return out


def build_flat(verbose=False):
    """Rewrite data/hero-flat.csv from the schema CSVs. Returns the number of data rows."""
    from sheet import base_action     # strips a `[collision=…]` override before the lookup

    groups = _action_groups()
    header = None
    out = []

    for set_label, fname in SOURCES:
        rows = _rows(fname)
        if header is None:
            head = [(rows[0][i] if i < len(rows[0]) else '') for i in range(NCOLS)]
            header = ['Set'] + head + ['Action group']

        carry = [''] * NCOLS
        for raw in rows[1:]:
            row = [(raw[i] if i < len(raw) else '').strip() for i in range(NCOLS)]
            if not any(row):
                continue
            starts_champion = bool(row[0])
            for i in range(NCOLS):
                if starts_champion:
                    carry[i] = row[i]          # reset — an empty cell here is a REAL empty
                elif row[i]:
                    carry[i] = row[i]
            group = groups.get(base_action(carry[ACTION_COL]), '')
            out.append([set_label] + list(carry) + [group])

    path = os.path.join(DATA, OUT)
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(out)

    if verbose:
        champs = len({(r[0], r[1]) for r in out})
        print('flatten: %s <- %d rows, %d champions' % (OUT, len(out), champs))
    return len(out)


if __name__ == '__main__':
    build_flat(verbose=True)
