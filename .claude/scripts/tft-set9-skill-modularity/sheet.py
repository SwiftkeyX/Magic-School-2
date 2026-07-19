"""Shared helpers for the tft-set9-skill sheet. Imported by export.py and sync.py.

Columns are resolved BY HEADER NAME, never by hard-coded index. The Hero tab has had columns
inserted into the middle of it (Action Source, before Action), and the user renames headers as they
go (`Trigger` is really `Trigger (When)` in the sheet). Every script that addressed cells as `r[14]`
silently started writing into the wrong column the moment that happened. Look the index up from
row 1 instead and the whole class of bug goes away.

Everything here runs from repo-root cwd:
    python .claude/scripts/tft-set9-skill-modularity/sync.py
"""

import csv
import pathlib
import re

import gspread
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.service_account import Credentials

KEY = "1X5glHjVcgv3yYG4Q2SyV9YJS3sv_wH5XAg3RLOHnUa4"
CRED = "google-service-credential.json"
DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")

# Review aid: which cells the writers touched, so highlight_changes.py can COLOUR them for the user to
# review. The one-writer (sync.py / force_full.py) records every A1 cell it changes here; the state
# ACCUMULATES across runs (a two-pass sync records pass 1's edits then pass 2's zero) until
# highlight_changes.py consumes `pending`, colours it, and rotates it into `highlighted`. Transient
# review state, not source — gitignored.
CHANGES_FILE = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/changes-state.json")


def record_changes(tab, a1_cells):
    """Append the A1 cells a writer just changed on `tab`, deduped, for highlight_changes.py.

    Reusable across sync.py, force_full.py, and across runs — never overwrites, so the acceptance
    double-sync does not erase pass 1's edits with pass 2's zero. Best-effort: a failure here must
    never break a sheet write, so it swallows its own errors."""
    import json
    cells = [c for c in a1_cells if c]
    if not cells:
        return
    try:
        state = json.loads(CHANGES_FILE.read_text(encoding="utf-8")) if CHANGES_FILE.exists() else {}
        pend = state.setdefault("pending", {}).setdefault(tab, [])
        seen = set(pend)
        for c in cells:
            if c not in seen:
                pend.append(c)
                seen.add(c)
        CHANGES_FILE.write_text(json.dumps(state, indent=1), encoding="utf-8")
    except Exception as e:            # a highlight-bookkeeping failure must not abort a real write
        print(f"  (record_changes skipped: {e})")


D = "—"                        # the sheet's "not applicable" marker
SAME = "Same to Aim Target"    # recipient shorthand when it equals the Aim Target

# Sheet tab name -> csv filename. THE definition of which tabs the tooling owns; sync.py (writer) and
# export.py (reader) both derive from it.
#
# It lives here because it was two lists, one per script, and they drifted: `Action Model` was added
# back to sync's map and export simply forgot it, so the tab was written but could never be read back
# — a hand-edit to it would be silently destroyed by the next sync. Same failure mode the merge layout
# has (one function, one file, on purpose): two copies of a fact will disagree, given a chance.
#
# `Action Model` is the lookup Hero's `Legacy action` keys into. Only `Hero` has a logical column
# schema; the rest are plain tables synced positionally.
TABS = {
    "Hero set 9": "hero.csv",
    "Hero set 10": "hero-set10.csv",
    "Column Explain": "column-explain.csv",
    "Action Model": "action-model.csv",
    "AOE shape": "aoe-shape.csv",
    "Offset Types": "offset-types.csv",
    "Trigger Types": "trigger-types.csv",
    "Effect Recipient Types": "effect-recipient-types.csv",
    "Effect Types": "effect-types.csv",
    "Collision Types": "collision-types.csv",
    "Scaling Types": "scaling-types.csv",
    "Volley Shape Types": "volley-shape.csv",     # renamed from 'Spread Types'
    "Aim Target Types": "aim-target-types.csv",   # new: the validated Aim Target vocabulary
    "Fire Timing Types": "fire-timing.csv",
    # Action Source became a validated vocabulary in round 14: it had drifted into structural keys
    # (Self, Summon, Step N Projectile) mixed with champion pet names (Dreadway, Child of the Star,
    # Shadow) — prose in a column with no tab, the same road that gave AOE (hex) 'Gwen-shaped'.
    "Action Source Types": "action-source-types.csv",
    "Design Notes": "design-notes.csv",
    # TEMPORARY review surface for the proposed 'Hero archetype' column (round 11). Built by
    # build_archetype_review.py. Delete this entry and the tab once the tags move onto the Hero tabs.
    "Archetype Review": "archetype-review.csv",
    # DERIVED, not authored: the un-blanked mirror of both schema tabs, rebuilt by flatten.py at the
    # top of every sync. It exists because the Hero tabs are merged for human reading and cannot be
    # machine-read — see flatten.py. Never edit hero-flat.csv by hand.
    "Hero flat": "hero-flat.csv",
}

# Tabs that carry the Hero LOGICAL-COLUMN schema — merge-derived display + vocab validation —
# rather than being synced positionally like a reference table. There are two of them now: `Hero`
# (`Hero set 9`) and `Hero set 10`. The Set 10 tab REUSES the identical 31-column schema AND the
# identical reference vocabularies (Action Model, Effect Types, AOE shape, ...) — a new set's champions
# are still made of the same actions and effects, so a second schema tab validates against the same
# tabs. The map is tab -> its CSV, exactly like TABS; sync.py runs its Hero pipeline over each entry.
# (Tabs were `Hero` / `hero set 10` until 2026-07-18, when the user renamed them for set symmetry —
# addressed by NAME everywhere, so the rename is just these strings + the sheet titles.)
SCHEMA_TABS = {
    "Hero set 9": "hero.csv",
    "Hero set 10": "hero-set10.csv",
}

HERO_TAB = "Hero set 9"
# Everything that is NOT a schema tab is a reference table, synced positionally. Must exclude EVERY
# schema tab, or `Hero set 10` would be written as a plain table and its merges/validation skipped.
REFERENCE = {t: f for t, f in TABS.items() if t not in SCHEMA_TABS}

# Reference tab -> the column merged vertically for display (0-based). Same rule as Hero: a merged
# cell reads back "" on every row but its first, so the CSV carries the blank and the merge is
# DERIVED from the values. `Effect Types` groups by category (the user: "merge the cell in Effect
# category until it left with only 4 row") - which needs the rows SORTED by category first, or a
# scattered category cannot merge into one block.
MERGED_REFERENCE = {"Effect Types": 0}

# Logical name -> header text to look for. Headers carry parenthetical suffixes the user has
# edited over time ("Collision (If it have one)"), so matching is exact-first, then prefix.
# Order here MIRRORS the sheet's physical column order (CSV, sheet and builder all read left-to-right
# the same way). cols() still resolves BY NAME, so order is not load-bearing for lookups — only
# IDENTITY_BLOCK = HERO_COLUMNS[:10] depends on the first ten being the identity block. The action
# region was regrouped for readability (the user's call): who/what/where first — Action Source,
# Action, Aim Target, Offset, AOE — then the delivery detail (Skill Range, Count, Spread, Collision),
# then the effect block. `Offset` is the AOE anchor label; it and `AOE` are per-ACTION merged columns.
# `Effect Cadence` / `Effect Duration` were plain `Cadence` / `Duration (s)` — the user renamed them
# for clarity (both describe the EFFECT). The names here MUST track the sheet's header text: cols()
# matches exact-then-prefix, and "Effect Duration (s)".startswith("Duration") is False, so a stale
# name does not fall back gracefully — it raises, which is the behaviour we want.
HERO_COLUMNS = [
    "Champion", "Cost", "Role", "Origin 1", "Origin 2", "Class 1", "Class 2", "Range",
    "Summary", "Skill Description",
    "Step", "Skill Type", "Trigger", "Condition",
    # `Legacy action` is a KEY into the `Action Model` tab, which holds the axes (Apply/Spawn/Motion/
    # Behavior/Shape) that describe it. Those axes lived here per-row for one day (v2, 0db5e27) and
    # moved out: they are functionally determined by the name — verified on all 135 action rows — so
    # per-row copies were ~200 rows restating a 23-row lookup, and could only drift out of sync.
    # Collision/Offset/AOE STAY here: they genuinely vary per row (Burst Projectile is First-Hit on
    # three rows and Target-Only on one), which is exactly what a lookup cannot express.
    "Action Source", "Legacy action", "Aim Target", "Offset", "AOE",
    # `Collision` is GONE from Hero: the action decides it. It was per-row for a real reason until
    # Urgot — the last action whose Collision varied — turned out to be a Cone AOE, not a Burst
    # Projectile. The Action Model tab is now its only home.
    "Skill Range", "Count",
    # `Volley Shape` (was `Spread` until 2026-07-18) holds ONLY the geometric shape of a multi-instance
    # volley — Cone / 360 / Diagonal — whoever is standing there. The user split the old overloaded
    # `Spread`: the target-SELECTION values (Same target, Each to its own target, Split across
    # nearest/farthest N, Split across marked, Current + Left + Right) moved to `Aim Target`, which is
    # now a validated vocabulary too. Distribution is inferred from Aim + Count (multi-target aim =
    # split, single = converge).
    "Volley Shape",
    # `Fire Timing` (added 2026-07-18) is ORTHOGONAL to both: it says WHEN the Count instances fire —
    # `At Once` or `Consecutive`. Set only when Count > 1; '—' otherwise. Per-row like Count (a RUN
    # column), so a branch can change it (Karma's 3rd cast fires 3 at once).
    "Fire Timing",
    # `Cast` sits at the END of the action region, not with the effects. It describes the ACTION (the
    # user: "the cast is one the element in each action"), and it used to be the sheet's LAST column —
    # marooned past the effect block, which is what made it read as an effect property.
    "Cast",
    "Effect Recipient", "Effect Category", "Effect Detail",
    "Amount", "Scaling Type", "Scaling", "Effect Cadence", "Effect Duration",
]

# The action-instance block: these cells are vertically merged across the rows of one action.
# NOTE: `Condition` is deliberately NOT in here. It is PER-EFFECT, not per-action - a single effect
# row can be conditional while its siblings are not (Soraka heals an ally, and heals them again
# only if they are below 50% HP: same action, one row gated, one not). While Condition was merged
# it could only gate a whole action, which forced that bonus heal to be faked as a separate step.
# `Count`/`Spread` are NOT here either, for the same reason as Condition: Karma's 1st cast fires
# ONE burst and her 3rd fires THREE, from the same action. A merged Count cannot say that, which
# is the only reason those were ever two separate steps.
#
# ROUND 8 finished the job: a Step is a MOMENT in the cast, and its rows are BRANCHES of it, which
# may run different ACTIONS (Swain casts if untransformed and bursts if not; Azir summons unless he
# already has 3 Soldiers). So Trigger/Action/Collision/Aim went per-row too, and only these two are
# left. Merging is now done by VALUE RUNS — see remerge() in tft-review-round8.py — so a merge is a
# display of the data rather than a claim about it.
ACTION_BLOCK = ["Step", "Skill Type"]

# Count/Spread defaults. A single instance has nothing to arrange - but the cell must still say
# so. Blank would read as "unknown"; the em-dash says "there is only one".
COUNT_DEFAULT = "1"
SPREAD_DEFAULT = D

# The champion-identity block: merged down every row a champion owns.
IDENTITY_BLOCK = HERO_COLUMNS[:10]


def open_sheet():
    return gspread.service_account(filename=CRED).open_by_key(KEY)


def col_letter(i):
    s, i = "", i + 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def cols(header):
    """Map logical column name -> 0-based index, resolved off the sheet's own header row."""
    out = {}
    for name in HERO_COLUMNS:
        exact = [i for i, h in enumerate(header) if h.strip() == name]
        if exact:
            out[name] = exact[0]
            continue
        pre = [i for i, h in enumerate(header) if h.strip().startswith(name)]
        if not pre:
            raise SystemExit(f"Hero header has no column matching {name!r}: {header}")
        out[name] = pre[0]
    return out


def header_row(vals):
    """Index of the REAL (column-name) header row. The Hero tab carries a merged super-header row
    ('Action' / 'Effect') ABOVE its names for readability, so its names live on row 1; the single-
    header CSVs and every other tab keep them on row 0. Locate by the one column that is always a name
    (`Champion`), so the same code works with or without the super-header. Data starts at header+1."""
    for i, row in enumerate(vals[:3]):
        if any(c.strip() == "Champion" for c in row):
            return i
    return 0


def find_row(vals, col, value):
    for i, r in enumerate(vals):
        if len(r) > col and r[col].strip() == value:
            return i
    return None


def action_groups(vals, c):
    """Yield (start, end) row indices for each action instance.

    An action starts on a row with a Step number and runs through the rows below it that have
    none — those are its extra effects.
    """
    step = c["Step"]
    starts = [i for i, r in enumerate(vals) if i > 0 and r[step].strip()]
    for a, b in zip(starts, starts[1:] + [len(vals)]):
        yield a, b


def champion_blocks(vals, c):
    """Yield (name, start, end) row indices for each champion's identity block."""
    ch = c["Champion"]
    starts = [i for i, r in enumerate(vals) if i > 0 and r[ch].strip()]
    for a, b in zip(starts, starts[1:] + [len(vals)]):
        yield vals[a][ch].strip(), a, b


def merge_request(sheet_id, start, end, col):
    return {"mergeCells": {
        "range": {"sheetId": sheet_id, "startRowIndex": start, "endRowIndex": end,
                  "startColumnIndex": col, "endColumnIndex": col + 1},
        "mergeType": "MERGE_COLUMNS",
    }}


# Only these two span a whole step. Every other column merges by VALUE RUN — see remerge().
STEP_BLOCK = ACTION_BLOCK

# The columns that merge wherever consecutive rows happen to agree.
RUN_COLUMNS = ["Trigger", "Condition", "Action Source", "Legacy action", "Count", "Volley Shape",
               "Fire Timing", "Skill Range", "Aim Target", "Cast"]


def remerge_hero(sh, tab=HERO_TAB):
    """Lay out EVERY merge on a schema tab (`Hero set 9` or `Hero set 10`). The ONE place merges live.

    `tab` names the schema tab to lay out. Everything else is DERIVED from that tab's own values and
    its own header row (via header_row/cols), so the identical logic serves both schema tabs — the
    Set 10 tab is single-header where Hero carries a two-row super-header, and header_row() absorbs
    that difference by locating the `Champion` column rather than assuming a fixed row.

    MERGES ARE DERIVED FROM THE VALUES, never stored. That is what lets the sheet's data live in a
    plain CSV: re-running this reconstructs the layout exactly. Three layers:

      1. IDENTITY BLOCK  - Champion..Skill Description, merged down every row a champion owns.
      2. STEP BLOCK      - Step/Skill Type, spanning a whole step.
      3. VALUE RUNS      - Trigger..Aim Target, merged wherever CONSECUTIVE ROWS AGREE, because any
                           of them may differ between the branches of one step (Swain casts if
                           untransformed and bursts if not).

    A merge is therefore a DISPLAY of the data, not a CLAIM about it - the only form of merging that
    survives a schema where any column may differ per row.

    This is one function, in one file, on purpose. Two implementations of a merge layout is a merge
    FIGHT waiting to happen: one unmerges what the other merged, on every run, for ever.
    """
    ws = sh.worksheet(tab)
    vals = ws.get_all_values()
    hr = header_row(vals)          # real header row; data starts at hr+1 (super-header above it stays)
    c = cols(vals[hr])
    # The unmerge must cover EVERY merged column, wherever it physically sits. AOE + Offset merge like
    # the run block; since the action region was regrouped they may now sit LEFT of Skill Range / Count
    # / Spread / Collision, so take the max over all of them rather than assuming AOE/Offset are last.
    # (Effect columns between merged ones are never merged, so unmerging across them is a no-op.)
    last_col = max(c[n] for n in RUN_COLUMNS + ["AOE", "Offset"])

    def merge(a, b, col):
        return {"mergeCells": {"range": {
            "sheetId": ws.id, "startRowIndex": a, "endRowIndex": b,
            "startColumnIndex": col, "endColumnIndex": col + 1}, "mergeType": "MERGE_COLUMNS"}}

    def spans(col):
        """(start, end) row pairs, split wherever `col` holds a value. A merged cell reads back ""
        on every row but its first, so a non-blank cell IS the start of a new block."""
        starts = [i for i, r in enumerate(vals) if i > hr and len(r) > col and r[col].strip()]
        return list(zip(starts, starts[1:] + [len(vals)]))

    # Clear the whole region first, or a stale merge silently swallows the cells under it. Start below
    # the header rows so the merged super-header ('Action'/'Effect') on row 0 is left untouched.
    reqs = [{"unmergeCells": {"range": {
        "sheetId": ws.id, "startRowIndex": hr + 1, "endRowIndex": len(vals),
        "startColumnIndex": 0, "endColumnIndex": last_col + 1}}}]

    champions = spans(c["Champion"])
    for a, b in champions:
        if b - a > 1:
            reqs += [merge(a, b, c[n]) for n in IDENTITY_BLOCK]

    steps = spans(c["Step"])
    for a, b in steps:
        if b - a > 1:
            reqs += [merge(a, b, c[n]) for n in STEP_BLOCK]
        for n in RUN_COLUMNS + ["AOE", "Offset"]:
            # Compare EFFECTIVE values: a blank continuation row means "same as the row above" and
            # must merge WITH it. Comparing the raw cells would see "" != "Knock Back" and split
            # them - silently destroying the merge on every multi-effect action in the sheet.
            eff, prev = [], ""
            for i in range(a, b):
                v = vals[i][c[n]] if len(vals[i]) > c[n] else ""
                if v.strip():
                    prev = v
                eff.append(prev)
            run = 0
            for k in range(1, b - a + 1):
                if k == b - a or eff[k] != eff[run]:
                    if k - run > 1:
                        reqs.append(merge(a + run, a + k, c[n]))
                    run = k

    sh.batch_update({"requests": reqs})
    print(f"{tab}: re-merged — {len(champions)} champion blocks, {len(steps)} steps")


# The round scripts import this name. Kept as an alias so they keep working until they are archived.
remerge = remerge_hero


def unmerge_reference(sh, tab, col):
    """Drop the merges on one reference column, so a write cannot be swallowed by a stale one.

    A merged cell EATS a write to any row but its first, silently (invariant #8 - the doc-block bug).
    So the order is always unmerge -> write -> remerge, exactly as sync_hero does it.
    """
    ws = sh.worksheet(tab)
    sh.batch_update({"requests": [{"unmergeCells": {"range": {
        "sheetId": ws.id, "startRowIndex": 1, "endRowIndex": ws.row_count,
        "startColumnIndex": col, "endColumnIndex": col + 1}}}]})


def remerge_reference(sh, tab, col):
    """Merge runs of one reference column. Derived from the values, same as Hero's merges.

    A run starts on a non-blank cell and continues through the blanks below it - which is exactly how
    the CSV encodes it, so a flat CSV still fully describes the tab.
    """
    ws = sh.worksheet(tab)
    vals = ws.get_all_values()
    while vals and not any(c.strip() for c in vals[-1]):
        vals.pop()
    starts = [i for i, r in enumerate(vals) if i > 0 and len(r) > col and r[col].strip()]
    reqs = []
    for a, b in zip(starts, starts[1:] + [len(vals)]):
        if b - a > 1:
            reqs.append({"mergeCells": {"range": {
                "sheetId": ws.id, "startRowIndex": a, "endRowIndex": b,
                "startColumnIndex": col, "endColumnIndex": col + 1}, "mergeType": "MERGE_COLUMNS"}})
    if reqs:
        sh.batch_update({"requests": reqs})
    print(f"{tab}: re-merged — {len(starts)} blocks in column {col}")


# Hero column -> the reference CSV whose first column defines its legal values.
VOCAB = {
    "Legacy action": "action-model.csv",     # THE lookup: a key with no row here resolves to nothing
    "AOE": "aoe-shape.csv",                  # sizes are keys too, or the column drifts back to prose
    # Offset was the LAST geometry column with no tab, so nothing could catch a SENTENCE in it — and
    # one was proposed ("spawn projectile behind her, and line them up in a row"). Prose in an
    # unchecked column is how AOE (hex) once held 'Gwen-shaped'. Anchors are keys now, +N/-N included.
    "Offset": "offset-types.csv",
    "Trigger": "trigger-types.csv",
    "Effect Recipient": "effect-recipient-types.csv",
    "Scaling Type": "scaling-types.csv",
    "Volley Shape": "volley-shape.csv",     # Cone | 360 | Diagonal (was 'Spread')
    "Aim Target": "aim-target-types.csv",   # now validated: absorbed the target-selection spreads
    "Fire Timing": "fire-timing.csv",       # At Once | Consecutive (Count > 1 only)
    # Names the thing that ACTS, which is not always the champion. Validated since round 14 — it was
    # the last structural column taking free text, and it had already drifted to pet names.
    "Action Source": "action-source-types.csv",
}

# Reference tab -> (its csv, the column to check, the csv defining that column's vocabulary).
# Hero is not the only thing that can rot. `Collision` left Hero (the action decides it), so nothing
# was left to check it against `collision-types.csv` — the taxonomy could drift with no Hero column
# to notice. A tab's own vocabulary needs validating too.
TAB_VOCAB = [("action-model.csv", "Collision", "collision-types.csv"),
             # Offset mostly lives HERE now, not in Hero: an action that fixes its anchor owns it and
             # the Hero cell reads '—' (the rule ~12 actions already followed; Cone AOE and Charge were
             # the stragglers). So the tab's own column is the one that can rot unseen — Hero's check
             # cannot see a value no Hero row uses, e.g. Gilgamesh Projectile's 'rank -1'.
             # The loop already exempts '—' and 'per row', which is exactly this column's vocabulary.
             ("action-model.csv", "Offset", "offset-types.csv")]


def read_data(name):
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return [r for r in csv.reader(f)]


def fill_down(seq):
    """Resolve a merged column to its EFFECTIVE values: a blank inherits the row above."""
    out, prev = [], ""
    for v in seq:
        if v.strip():
            prev = v
        out.append(prev)
    return out


COLLISION_OVERRIDE = re.compile(r"\s*\[collision=([^\]]+)\]\s*$")


def base_action(s):
    """Strip a `[collision=Y]` override off a Legacy action, returning the base action name.

    The bracket is a PARSED override now (the user's 2026-07-18 call): `Charge [collision=Target-Only]`
    is base `Charge` with its Collision overridden to Target-Only, and there is NO dedicated Action
    Model row for the variant any more. So every place that looks the action up in Action Model — the
    VOCAB check, the geometry lookup — must resolve to the base first. (Upgrading the convention to a
    real parse re-opens per-row overrides v2→v3 closed, but the user chose it, for one fewer row.)"""
    return COLLISION_OVERRIDE.sub("", s).strip()


def validate_data(hero_csv="hero.csv"):
    """No value used in a schema tab may be undefined in its reference tab. Returns a list of problems.

    THE ONE implementation. sync.py raises on it; context.py prints it for the /add-champion flow.
    It was written twice - once in each - and they drifted the moment Effect Types gained a merge:
    sync.py learned to fill_down its category column and context.py did not, so the same CSVs passed
    one check and failed the other with 36 phantom errors. Exactly the bug the single tab map and the
    single merge layout exist to prevent. One fact, one function.

    `hero_csv` names which schema CSV to check (`hero.csv` for Set 9, `hero-set10.csv` for Set 10).
    Both are validated against the SAME shared reference vocabularies — a Set 10 champion using an
    action or effect with no row in Action Model / Effect Types is exactly the drift this catches.
    """
    hero = read_data(hero_csv)
    c = cols(hero[0])

    def cell(r, i):
        return r[i] if len(r) > i else ""

    def used(name):
        return {cell(r, c[name]).strip() for r in hero[1:]} - {"", D}

    def defined(csv_name, col=0):
        """First column of a reference tab, header dropped, STOPPING at the first all-blank row -
        every prose/doc block below that separator is documentation, not vocabulary."""
        out = set()
        for r in read_data(csv_name)[1:]:
            if not any(x.strip() for x in r):
                break
            if cell(r, col).strip():
                out.add(cell(r, col).strip())
        return out

    def used_for_vocab(name):
        # Legacy action may carry a `[collision=Y]` override; the base is what Action Model defines.
        vals = used(name)
        return {base_action(v) for v in vals} if name == "Legacy action" else vals

    problems = [f"{label}: {sorted(miss)} used in Hero but not defined in {src}"
                for label, src in VOCAB.items()
                for miss in [used_for_vocab(label) - defined(src)] if miss]

    # Effect Types is MERGED by category, so its Category column is blank on every row but a block's
    # first. Reading it raw turns every pair below a block top into ('', Detail) - matching nothing.
    et = read_data("effect-types.csv")[1:]
    effects = set(zip([v.strip() for v in fill_down([cell(r, 0) for r in et])],
                      [cell(r, 1).strip() for r in et]))
    pairs = {(cell(r, c["Effect Category"]).strip(), cell(r, c["Effect Detail"]).strip())
             for r in hero[1:]} - {("", "")}
    # (D, D) is not an undefined effect — it is NO effect, and it is a legitimate row: a projectile
    # exists to hit something, and applies nothing itself (the burst that follows does). Blank would
    # be wrong there (blank means "same as the row above"), so the em-dash pair says it explicitly.
    orphan = {p for p in pairs if p not in effects and all(p) and p != (D, D)}
    if orphan:
        problems.append(f"Effect: {sorted(orphan)} used in Hero but not defined in effect-types.csv")

    for src, col, vocab in TAB_VOCAB:
        rows = read_data(src)
        i = rows[0].index(col)
        used_t = set()
        for r in rows[1:]:
            if not any(x.strip() for x in r):
                break
            if cell(r, i).strip():
                used_t.add(cell(r, i).strip())
        miss = used_t - defined(vocab) - {D, "per row"}
        if miss:
            problems.append(f"{src} {col}: {sorted(miss)} used but not defined in {vocab}")

    # An action named `X [collision=Y]` states Y TWICE — in its own name and in its Collision cell —
    # and two copies of one fact disagree given a chance. The bracket is a NAMING CONVENTION, not a
    # parsed syntax (Hero's cell stays a plain key into this tab, so no reader learns a mini-language),
    # and this is the price of that: a name that can lie. It is the user's way of keeping Collision out
    # of Hero, where it would be "most of the time useless" — so the override rides in the action name,
    # and the check makes the name honest. `X` must be a real action too, or the variant is orphaned.
    # GEOMETRY: the Hero cell follows from the action's own axis, exactly, in BOTH directions.
    #   tab '—'        -> Hero '—'        the action projects no hitbox; there is nothing to place
    #   tab fixed      -> Hero 'default'  the action owns it; the row points at it
    #   tab 'per row'  -> Hero a value    only the row can say it (a circle's SIZE, a bolt's shape)
    # This check is ONLY possible because 'default' exists. While action-fixed also wrote an em-dash,
    # a row that had LOST its value read identically to a correct one, so the rule could not be
    # enforced at all — it just rotted, which is how Cone AOE and Charge drifted apart. The user's
    # call, and it turned a convention into an invariant.
    am_rows = []
    for r in read_data("action-model.csv")[1:]:
        if not any(x.strip() for x in r):
            break                       # the doc block below the blank row is not vocabulary
        if cell(r, 0).strip():
            am_rows.append(r)
    t_off = {cell(r, 0).strip(): cell(r, 6).strip() for r in am_rows}
    t_shape = {cell(r, 0).strip(): cell(r, 5).strip() for r in am_rows}
    # Offset/AOE are MERGED columns: a blank inherits the row above, exactly as sync compares them.
    eff_off = fill_down([cell(r, c["Offset"]) for r in hero[1:]])
    eff_aoe = fill_down([cell(r, c["AOE"]) for r in hero[1:]])
    for k, r in enumerate(hero[1:]):
        act = base_action(cell(r, c["Legacy action"]).strip())   # strip the [collision=Y] override
        if not act or act not in t_off:
            continue                    # continuation rows inherit; unknown keys are VOCAB's problem
        for axis, tabv, got in (("Offset", t_off[act], eff_off[k].strip()),
                                ("AOE (hex)", t_shape[act], eff_aoe[k].strip())):
            if axis == "AOE (hex)":
                # SHAPE axis. A PROJECTILE's Shape is 'specify elsewhere', and 1-hex is now its DEFAULT
                # (the user's simplification, 2026-07-18: "1-hex for a projectile should be default for
                # simplicity"). So a projectile row may read 'default' (the ordinary 1-hex bolt) OR a
                # real shape for a non-default projectile (Sona's Box 1.5x2, Jhin's Box 1x2) — the one
                # axis where BOTH are legal. A fixed '1-hex' action (Charge, Spawn At Target, Current
                # Target Laser) still reads exactly 'default'; a circle/cone/box/custom must state a
                # size (or 'unknown'); '—' means no hitbox.
                if tabv == D:
                    ok, want = got == D, D
                elif tabv == "specify elsewhere":
                    ok, want = got not in (D, ""), "'default' (1-hex bolt) or a real shape"
                elif tabv == "1-hex":
                    ok, want = got == "default", "default"
                else:
                    ok, want = got not in (D, "default", ""), "a real value"
            else:
                fixed = tabv not in (D, "per row", "specify elsewhere",
                                     "circle", "cone", "box", "custom")
                want = (D if tabv == D else "default" if fixed else "a real value")
                ok = (got == D) if tabv == D else (got == "default") if fixed else (
                    got not in (D, "default", ""))
            if not ok:
                problems.append(f"{axis}: row {k + 2} ('{act}') says {got!r} but the action's "
                                f"{axis.split()[0]} is {tabv!r} — expected {want}")

    # `X [collision=Y]` is a PARSED override in HERO now, not a dedicated Action Model row (the user's
    # 2026-07-18 call — one fewer row, at the price of a Hero cell that is a mini-language). So the
    # check moved here, onto the Hero cell: the base `X` must be a real action, and `Y` must be a real
    # collision. Collision is not a Hero column, so nothing else verifies `Y` — this is its only guard.
    am = read_data("action-model.csv")
    names = {cell(r, 0).strip() for r in am[1:] if cell(r, 0).strip()}
    collisions = defined("collision-types.csv")
    seen_override = set()
    for k, r in enumerate(hero[1:]):
        val = cell(r, c["Legacy action"]).strip()
        m = COLLISION_OVERRIDE.search(val)
        if not m or val in seen_override:
            continue
        seen_override.add(val)
        base, declared = base_action(val), m.group(1).strip()
        if base not in names:
            problems.append(f"Legacy action: '{val}' overrides '{base}', which is not an action")
        if declared not in collisions:
            problems.append(f"Legacy action: '{val}' has collision={declared!r}, "
                            f"not defined in collision-types.csv")
    return problems


NOTES_TAB = "Design Notes"


def sync_notes(sh, notes=(), edits=None):
    """Append/update rows in the `Design Notes` tab. The ONE place notes are written.

    Notes used to live in `Column Explain`, and grew to 20 of its 41 rows - half the tab had
    stopped explaining columns. A column legend ("what does this cell mean") and a decision log
    ("why is the schema this shape, what did we rule out") are different documents.

    Every script routes its notes through here. If any of them still appended to Column Explain,
    it would re-append on every run - the note is no longer there to be found, so its "already
    present?" check would never be satisfied. That is exactly what broke when the tab was split.
    """
    ws = sh.worksheet(NOTES_TAB)
    vals = [r for r in ws.get_all_values() if r]
    have = {r[0].strip() for r in vals if r[0].strip()}

    pending = [n for n in notes if n[0].strip() not in have]
    if pending:
        need = len(vals) + len(pending) + 2
        if ws.row_count < need:
            ws.add_rows(need - ws.row_count)
        ws.append_rows([(list(n) + ["", "", ""])[:3] for n in pending], value_input_option="RAW")
        vals = [r for r in ws.get_all_values() if r]

    cells = []
    for label, columns in (edits or {}).items():
        i = next((k for k, r in enumerate(vals) if r[0].strip() == label), None)
        if i is None:
            raise SystemExit(f"{NOTES_TAB}: row '{label}' not found")
        for col, text in columns.items():
            if (vals[i][col] if col < len(vals[i]) else "") != text:
                cells.append({"range": f"{col_letter(col)}{i + 1}", "values": [[text]]})
    if cells:
        ws.batch_update(cells, value_input_option="RAW")
    print(f"{NOTES_TAB}: {len(pending)} notes appended, {len(cells)} cells updated")


def post_replies(replies, warn_unmatched=True):
    """Reply to the sheet's review comments. `replies` is [(match, body), ...].

    A comment is matched by the FIRST key found in its text, so list a longer key before any key that
    is a prefix of it. Comments are left UNRESOLVED — resolving is the user's call.

    Idempotent twice over:
      - a comment whose replies already open with this body is skipped;
      - a comment the USER HAS RESOLVED is skipped entirely.

    RESOLVED COMMENTS ARE NEVER ANSWERED. The user resolves a comment when they are done with it —
    often because they posted it twice. Replying anyway just piles noise onto a closed thread, and a
    short match key makes that easy to do by accident: the user duplicated one comment four times and
    resolved two, so a key matching its text would have answered threads they had already closed.

    `warn_unmatched` is for a script that answers EVERY open comment; one that owns only a few passes
    False, or it warns about the comments another round already answered.
    """
    creds = Credentials.from_service_account_file(
        CRED, scopes=["https://www.googleapis.com/auth/drive"])
    s = AuthorizedSession(creds)
    url = f"https://www.googleapis.com/drive/v3/files/{KEY}/comments"
    r = s.get(url, params={"fields": "comments(id,content,resolved,replies(content))",
                           "pageSize": 100})
    r.raise_for_status()

    posted = skipped = 0
    for c in r.json().get("comments", []):
        if c.get("resolved"):
            skipped += 1
            continue
        # The user's comments routinely contain non-breaking spaces (\xa0) where a normal space is
        # expected ("better\xa0name"), which silently breaks substring keys. Normalise before matching.
        content = c["content"].replace(" ", " ")
        body = next((t for k, t in replies if k in content), None)
        if body is None:
            if warn_unmatched:
                print(f"  !! no reply drafted for: {c['content'][:60]!r}")
            continue
        if any(body[:40] in rp.get("content", "") for rp in c.get("replies", [])):
            continue
        rr = s.post(f"{url}/{c['id']}/replies", params={"fields": "id"}, json={"content": body})
        rr.raise_for_status()
        posted += 1
    print(f"Comments: posted {posted} replies ({skipped} resolved threads left alone)")
