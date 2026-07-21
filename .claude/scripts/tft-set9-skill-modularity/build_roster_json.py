"""Emit the roster dashboard's data: hero.csv + hero-set10.csv -> one JSON blob.

Run from repo-root cwd:
    python .claude/scripts/tft-set9-skill-modularity/build_roster_json.py

Writes `roster-data.json` next to this script. Re-run it after any sync to refresh the dashboard,
then re-publish the Artifact with the regenerated page.

THE POINT OF THIS SCRIPT IS THE UN-BLANKING. A schema tab's blank cell is DATA — "same as the row
above" — so a raw row is not readable on its own. Here every inherited value is resolved back to a
standalone row, which is what a lookup table needs. The three blanking families are un-blanked
differently, and the champion boundary resets all of them (see [[tft-sheet-scripts]] invariant #2 —
a whole-column fill_down is what once gave Illaoi the previous champion's Class 2).
"""

import csv
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
OUT = os.path.join(HERE, 'roster-data.json')

SETS = [('set9', 'hero.csv', 'Set 9'), ('set10', 'hero-set10.csv', 'Set 10')]

# Column indices — the 33-col schema. Addressed by name below, never trusted positionally here
# beyond this one map, which is checked against the header on load.
NAMES = ['Champion', 'Cost', 'Role', 'Damage Type', 'Origin 1', 'Origin 2', 'Class 1', 'Class 2',
         'Range', 'Summary', 'Skill Description', 'Step', 'Skill Type', 'Trigger', 'Condition',
         'Action Source', 'Legacy action', 'Aim Target', 'Offset', 'AOE', 'Skill Range', 'Count',
         'Volley Shape', 'Fire Timing', 'Cast', 'Effect Recipient', 'Effect Category',
         'Effect Detail', 'Amount', 'Scaling Type', 'Scaling', 'Effect Cadence',
         'Effect Duration']

(C_CHAMP, C_COST, C_ROLE, C_DMG, C_O1, C_O2, C_CL1, C_CL2, C_RANGE, C_SUM, C_DESC, C_STEP, C_TYPE,
 C_TRIG, C_COND, C_SRC, C_ACT, C_AIM, C_OFF, C_AOE, C_SRANGE, C_COUNT, C_VOLLEY, C_FIRE, C_CAST,
 C_RECIP, C_CAT, C_DET, C_AMT, C_STYPE, C_SCALE, C_CAD, C_DUR) = range(33)

# Run columns inherit from the row above; Offset/AOE are per-action and do the same.
RUN = [C_TRIG, C_COND, C_SRC, C_ACT, C_AIM, C_SRANGE, C_COUNT, C_VOLLEY, C_FIRE, C_CAST,
       C_OFF, C_AOE]
IDENT = list(range(0, 11))     # 11 since `Damage Type` joined the identity block


def cell(row, i):
    return (row[i] if i < len(row) else '').strip()


def load(fname):
    rows = list(csv.reader(io.open(os.path.join(DATA, fname), encoding='utf-8')))
    hdr = rows[0]
    assert cell(hdr, C_CHAMP).startswith('Champion'), 'unexpected header: %r' % hdr[:2]
    return rows[1:]


def build(fname, set_label):
    rows = load(fname)
    champs, cur = [], None
    # `raw_*` flags are read BEFORE un-blanking, because a filled cell is exactly how the tab
    # marks where a step or an action begins. Un-blank first and that boundary is lost.
    for row in rows:
        if not any(cell(row, i) for i in range(len(NAMES))):
            continue
        starts_champ = bool(cell(row, C_CHAMP))
        starts_step = bool(cell(row, C_STEP))
        starts_action = bool(cell(row, C_ACT))

        if starts_champ:
            cur = {
                'set': set_label,
                'n': cell(row, C_CHAMP),
                'cost': cell(row, C_COST),
                'role': cell(row, C_ROLE),
                'origins': [v for v in (cell(row, C_O1), cell(row, C_O2)) if v],
                'classes': [v for v in (cell(row, C_CL1), cell(row, C_CL2)) if v],
                'range': cell(row, C_RANGE),
                'summary': cell(row, C_SUM),
                'desc': cell(row, C_DESC),
                'steps': [],
                '_carry': {},
            }
            champs.append(cur)
        if cur is None:
            continue

        carry = cur['_carry']
        for i in RUN:
            v = cell(row, i)
            if v:
                carry[i] = v
        get = lambda i: cell(row, i) or carry.get(i, '')

        if starts_step or not cur['steps']:
            cur['steps'].append({
                'no': cell(row, C_STEP) or '?',
                'type': cell(row, C_TYPE) or '',
                'actions': [],
            })
        step = cur['steps'][-1]

        if starts_action or not step['actions']:
            step['actions'].append({
                'trigger': get(C_TRIG),
                'cond': get(C_COND),
                'src': get(C_SRC),
                'action': get(C_ACT),
                'aim': get(C_AIM),
                'offset': get(C_OFF),
                'aoe': get(C_AOE),
                'srange': get(C_SRANGE),
                'count': get(C_COUNT),
                'volley': get(C_VOLLEY),
                'fire': get(C_FIRE),
                'cast': get(C_CAST),
                'effects': [],
            })
        act = step['actions'][-1]

        # A branch row re-states its own Condition; carry it onto the row, not the action above.
        if cell(row, C_COND):
            act['cond'] = cell(row, C_COND)

        eff = {
            'recip': cell(row, C_RECIP),
            'cat': cell(row, C_CAT),
            'det': cell(row, C_DET),
            'amt': cell(row, C_AMT),
            'stype': cell(row, C_STYPE),
            'scale': cell(row, C_SCALE),
            'cad': cell(row, C_CAD),
            'dur': cell(row, C_DUR),
        }
        # A projectile that applies nothing is an all-em-dash block; keep it out of the effect list
        # so the UI can say "applies nothing - it exists to hit" instead of rendering eight dashes.
        if any(v and v != '—' for v in eff.values()):
            act['effects'].append(eff)

    out = []
    for c in champs:
        c.pop('_carry', None)
        blob = json.dumps(c, ensure_ascii=False).lower()
        c['unknown'] = 'unknown' in blob
        out.append(c)
    return out


def main():
    payload = {'generated': None, 'sets': {}}
    import datetime
    payload['generated'] = datetime.date.today().isoformat()
    total = 0
    for key, fname, label in SETS:
        champs = build(fname, label)
        payload['sets'][key] = champs
        total += len(champs)
        steps = sum(len(c['steps']) for c in champs)
        effects = sum(len(a['effects']) for c in champs for s in c['steps'] for a in s['actions'])
        print('%-6s %3d champions | %3d steps | %3d effects | %d with unknown'
              % (label, len(champs), steps, effects, sum(1 for c in champs if c['unknown'])))
    with io.open(OUT, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, separators=(',', ':'))
    print('wrote %s (%d champions, %.0f KB)' % (OUT, total, os.path.getsize(OUT) / 1024.0))


if __name__ == '__main__':
    main()
