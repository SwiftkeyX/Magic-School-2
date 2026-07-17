"""Generate the read-only `Dashboard` tab — a comprehensive, champion-centric view of the Hero data.

STATUS: PARKED and STALE. The user set it aside ("ditch it for now"), and it is still stale — but less
so than it was. It reads `action-model.csv` for each action's `Columns used` profile; that CSV is back
and managed by sync.py again (Hero's `Legacy action` keys into it), so the lookup it wants EXISTS,
but the tab has no `Columns used` column any more. To revive it: add that column back to
`action-model.csv` (or derive the profile from the axes — an action with Motion=Projectile shows
Count/Spread, one with Shape=circle shows Offset/AOE), then re-wire `dashboard.generate(sh)` into
sync.py's main(). Nothing else about it rotted: it was always keyed by the ACTION NAME, which is
exactly what Hero holds again.

DERIVED, never edited. Built from `data/hero.csv` (the source of truth) + each Action's `Columns used`
profile in `data/action-model.csv`. Idempotent: a second run writes 0 cells (it diffs against the tab).

Each action's `Targeting` cell shows ONLY the columns that action's profile declares (so a projectile
shows Count/Spread, an AOE shows Offset/AOE, a Cast shows just its aim) — the per-action column
profiles doing their job, no '—' clutter. `Effect` composes the effect rows into readable text.
"""
import csv
import pathlib

import gspread

from sheet import cols, col_letter

DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")
TAB = "Dashboard"
HEADER = ["Champion", "Step", "Type", "Trigger", "Action", "Targeting", "Effect"]
D = "—"


def _read(name):
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return [r for r in csv.reader(f)]


def _profiles():
    """Action name -> set of logical Hero columns it uses (from the 'Columns used' field)."""
    am = _read("action-model.csv")
    h = am[0]
    ai, ci = h.index("Action"), h.index("Columns used")
    out = {}
    for r in am[1:]:
        if r and r[0].strip() and len(r) > ci and r[ci].strip():
            out[r[ai].strip()] = {c.strip() for c in r[ci].split(",") if c.strip()}
    return out


def _targeting(r, c, prof):
    """Compose the Targeting cell from the action's profile columns only, skipping '—'/trivial."""
    p = []
    aim = r[c["Aim Target"]].strip()
    if aim and aim != D:
        p.append("aim " + aim)
    cnt = r[c["Count"]].strip()
    if "Count" in prof and cnt and cnt not in (D, "1"):
        p.append("×" + cnt)
    spr = r[c["Spread"]].strip()
    if "Spread" in prof and spr and spr != D:
        p.append(spr)
    off = r[c["Offset"]].strip()
    if "Offset" in prof and off and off != D:
        p.append(off)
    aoe = r[c["AOE"]].strip()
    if "AOE" in prof and aoe and aoe != D:
        p.append("AOE " + aoe)
    coll = r[c["Collision"]].strip()
    if "Collision" in prof and coll and coll not in (D, "None"):
        p.append(coll)
    return " · ".join(p)


def _effect(r, c, action_aim):
    """Compose one effect row into readable text: 'Detail Amount (dur) → recipient'."""
    det = r[c["Effect Detail"]].strip()
    amt = r[c["Amount"]].strip()
    dur = r[c["Effect Duration"]].strip()
    recip = r[c["Effect Recipient"]].strip()
    s = det
    if amt and amt != D:
        s += " " + amt
    if dur and dur != D:
        s += " (perm)" if dur == "Permanent" else f" ({dur}s)"
    if recip == "Same to Aim Target":
        recip = action_aim
    if recip and recip != D:
        s += " → " + recip
    return s.strip()


def _build_rows():
    hero = _read("hero.csv")
    h = hero[0]
    c = cols(h)
    prof = _profiles()
    W = len(h)

    def meta(r):
        o1, o2 = r[c["Origin 1"]].strip(), r[c["Origin 2"]].strip()
        k1, k2 = r[c["Class 1"]].strip(), r[c["Class 2"]].strip()
        org = o1 + ("/" + o2 if o2 else "")
        cls = k1 + ("/" + k2 if k2 else "")
        return " — ".join(x for x in (
            r[c["Champion"]].strip(), r[c["Cost"]].strip(), f"{org} / {cls}",
            "R" + r[c["Range"]].strip(), r[c["Summary"]].strip()) if x.strip(" —/R"))

    rows = [HEADER]
    cur_step = cur_type = cur_aim = ""
    for raw in hero[1:]:
        r = (raw + [""] * W)[:W]
        if r[c["Step"]].strip():
            cur_step = r[c["Step"]].strip()
        if r[c["Skill Type"]].strip():
            cur_type = r[c["Skill Type"]].strip()
        if r[c["Champion"]].strip():                       # champion section header row
            rows.append([meta(r)] + [""] * (len(HEADER) - 1))
        if r[c["Action"]].strip():                         # action-start row
            cur_aim = r[c["Aim Target"]].strip()
            action = r[c["Action"]].strip()
            rows.append(["", cur_step, cur_type, r[c["Trigger"]].strip(), action,
                         _targeting(r, c, prof.get(action, set())), _effect(r, c, cur_aim)])
        else:                                              # continuation effect row
            rows.append(["", "", "", "", "", "", _effect(r, c, cur_aim)])
    return rows


def generate(sh):
    """Write the Dashboard tab idempotently (diff against current content, like sync_reference)."""
    target = _build_rows()
    try:
        ws = sh.worksheet(TAB)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=TAB, rows=len(target) + 10, cols=len(HEADER))
    if ws.row_count < len(target):
        ws.add_rows(len(target) - ws.row_count + 5)
    if ws.col_count < len(HEADER):
        ws.add_cols(len(HEADER) - ws.col_count)

    cur = ws.get_all_values()
    edits = []
    for i in range(max(len(target), len(cur))):
        want = target[i] if i < len(target) else [""] * len(HEADER)
        have = cur[i] if i < len(cur) else []
        for j in range(len(HEADER)):
            a = have[j] if j < len(have) else ""
            b = want[j] if j < len(want) else ""
            if a != b:
                edits.append({"range": f"{col_letter(j)}{i + 1}", "values": [[b]]})
    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"{TAB}: {len(edits)} cells updated ({len(target)} rows)")
    return len(edits)


if __name__ == "__main__":
    from sheet import open_sheet
    generate(open_sheet())
