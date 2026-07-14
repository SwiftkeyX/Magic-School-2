"""Shared helpers for the tft-set9-skill sheet scripts.

Columns are resolved BY HEADER NAME, never by hard-coded index. The Hero tab has had columns
inserted into the middle of it (Action Source, before Action), and every script that addressed
cells as `r[14]` silently started writing into the wrong column the moment that happened. Look
the index up from row 1 instead and the whole class of bug goes away.

Imported by tft-add-*.py and tft-apply-comments.py, which run from repo-root cwd:
    python .claude/scripts/<name>.py
"""

import gspread
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.service_account import Credentials

KEY = "1X5glHjVcgv3yYG4Q2SyV9YJS3sv_wH5XAg3RLOHnUa4"
CRED = "google-service-credential.json"

D = "—"                        # the sheet's "not applicable" marker
SAME = "Same to Aim Target"    # recipient shorthand when it equals the Aim Target

# Logical name -> header text to look for. Headers carry parenthetical suffixes the user has
# edited over time ("Collision (If it have one)"), so matching is exact-first, then prefix.
HERO_COLUMNS = [
    "Champion", "Cost", "Role", "Origin 1", "Origin 2", "Class 1", "Class 2", "Range",
    "Summary", "Skill Description",
    "Step", "Skill Type", "Trigger", "Condition", "Action Source", "Action",
    "Count", "Spread", "Collision",
    "Aim Target", "Effect Recipient", "Effect Category", "Effect Detail",
    "Amount", "Scaling Type", "Scaling", "Cadence", "Duration", "AOE", "Cast",
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
RUN_COLUMNS = ["Trigger", "Condition", "Action Source", "Action", "Count", "Spread", "Collision",
               "Aim Target"]


def remerge_hero(sh):
    """Lay out EVERY merge on the Hero tab. The ONE place merges are computed.

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
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    c = cols(vals[0])
    last_col = c["Aim Target"]

    def merge(a, b, col):
        return {"mergeCells": {"range": {
            "sheetId": ws.id, "startRowIndex": a, "endRowIndex": b,
            "startColumnIndex": col, "endColumnIndex": col + 1}, "mergeType": "MERGE_COLUMNS"}}

    def spans(col):
        """(start, end) row pairs, split wherever `col` holds a value. A merged cell reads back ""
        on every row but its first, so a non-blank cell IS the start of a new block."""
        starts = [i for i, r in enumerate(vals) if i > 0 and len(r) > col and r[col].strip()]
        return list(zip(starts, starts[1:] + [len(vals)]))

    # Clear the whole region first, or a stale merge silently swallows the cells under it.
    reqs = [{"unmergeCells": {"range": {
        "sheetId": ws.id, "startRowIndex": 1, "endRowIndex": len(vals),
        "startColumnIndex": 0, "endColumnIndex": last_col + 1}}}]

    champions = spans(c["Champion"])
    for a, b in champions:
        if b - a > 1:
            reqs += [merge(a, b, c[n]) for n in IDENTITY_BLOCK]

    steps = spans(c["Step"])
    for a, b in steps:
        if b - a > 1:
            reqs += [merge(a, b, c[n]) for n in STEP_BLOCK]
        for n in RUN_COLUMNS:
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
    print(f"Hero: re-merged — {len(champions)} champion blocks, {len(steps)} steps")


# The round scripts import this name. Kept as an alias so they keep working until they are archived.
remerge = remerge_hero


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

    A comment is matched by the FIRST key found in its text, so list a longer key before any
    key that is a prefix of it. Comments are left UNRESOLVED — resolving is the user's call.
    Idempotent: a comment whose replies already open with this body is skipped.

    `warn_unmatched` is for the script that answers EVERY comment; a script that owns only a
    few of them passes False, or it warns about the comments another script already answered.
    """
    creds = Credentials.from_service_account_file(
        CRED, scopes=["https://www.googleapis.com/auth/drive"])
    s = AuthorizedSession(creds)
    url = f"https://www.googleapis.com/drive/v3/files/{KEY}/comments"
    r = s.get(url, params={"fields": "comments(id,content,replies(content))", "pageSize": 100})
    r.raise_for_status()

    posted = 0
    for c in r.json().get("comments", []):
        body = next((t for k, t in replies if k in c["content"]), None)
        if body is None:
            if warn_unmatched:
                print(f"  !! no reply drafted for: {c['content'][:60]!r}")
            continue
        if any(body[:40] in rp.get("content", "") for rp in c.get("replies", [])):
            continue
        rr = s.post(f"{url}/{c['id']}/replies", params={"fields": "id"}, json={"content": body})
        rr.raise_for_status()
        posted += 1
    print(f"Comments: posted {posted} replies (left unresolved)")
