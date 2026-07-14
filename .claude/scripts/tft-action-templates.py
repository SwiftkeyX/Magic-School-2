"""Own the Action Template model: the two reference tabs, and the Count/Spread invariant on `Hero`.

Run from repo-root cwd:  python .claude/scripts/tft-action-templates.py

THE PROBLEM
-----------
The `Action` column fuses two independent axes, and a third had been leaking into free text:

  * COMPOSITION - an action is really delivery x collision x shape. The user spotted this twice:
    "Burst Projectile is First hit Projectile + Circle AOE", and "Circle AOE is exactly Spawn At
    Target, but it was AOE".
  * MULTIPLICITY - how many instances of the action fire, and how they are arranged. This was
    smuggled into the `Scaling` column as prose: "×8 arrows in a cone" (Ashe), "×6 shots"
    (Akshan), "×3 bursts" (Karma), "all 3 Soldiers strike at once" (Azir). That is the exact
    failure mode `Action Source` had before it earned a column.

WHAT THIS SCRIPT OWNS
---------------------
  * `Action Templates` - every Action decomposed into Delivery x Collision x Shape.
  * `Spread Types`     - the arrangement axis, as a first-class reference tab beside
    `Action Types` / `Effect Types` / `Collision Types`. It started as a block at the bottom of
    `Action Templates`, which filed a real axis of the schema as a footnote of another one; the
    user asked for it to get its own tab ("Dedicate new tab to it").
  * The `Count`/`Spread` columns on `Hero` - see backfill_hero().

The model was trialled in a `Hero (template)` tab so nothing that worked could break. The user
signed off on it ("Let's use this one from now on"), so tft-promote-template.py renamed it over
the old tab: the template IS `Hero` now, and there is nothing left to duplicate.
"""

from tft_sheet import (COUNT_DEFAULT, D, SPREAD_DEFAULT, action_groups, col_letter, cols,
                       merge_request, open_sheet, post_replies)

SPREAD_TAB = "Spread Types"

# Action -> (Delivery, Collision, Shape, Cadence, Notes)
# Delivery answers WHERE THE HITBOX SPAWNS and WHETHER IT TRAVELS - the rule from
# 'Note - Projectile vs Laser'. Shape answers WHAT THE HITBOX IS.
# TEMPLATES lived here: the 'Action Templates' tab's contents. That tab is DELETED, merged
# into 'Action Model' (tft-action-model.py), which is now the single source for what an
# action IS. This script keeps only what is still its own: 'Spread Types', and the
# Count/Spread invariant on Hero.

# Spread -> (What it means, Aims around, Used by, Clarify more)
# Spread is the ARRANGEMENT axis: given Count instances of one Action, where do they go? It is
# orthogonal to the Action itself - Ashe's Cone and Akshan's Same target are both First hit
# Projectile. Same 'label | short meaning | detail' shape as Action Types and Collision Types.
SPREADS = [
    [D, "Not applicable - a single instance, so there is nothing to arrange.",
     "The Aim Target", "Every action with Count = 1",
     "The default. Must be an em-dash, never blank: blank would read as 'unknown' rather than "
     "'there is only one instance'."],
    ["Same target", "Every instance converges on the ONE aim target.",
     "The Aim Target",
     "Akshan (6 shots), Azir (3 Soldiers strike), Gwen (3 snips)",
     "Multiplicity with no geometry - it is a burst of repeats, not a shape. Each instance is a "
     "SEPARATE hitbox, so the target is hit once per instance, and one can miss while another "
     "lands. Contrast 'Current + Left + Right', whose instances SHARE one hitbox. And do not "
     "confuse this with an Amount: Kalista fires ONE projectile that lands 6 Impale stacks, so she "
     "is Count 1 - see 'Note - Count vs Amount'."],
    ["Cone", "The instances fan out in a cone in front of the caster.",
     "The Aim Target", "Ashe (8 arrows)",
     "The cone is an emergent shape, NOT a hitbox: there is no cone collider. Each arrow is its "
     "own First hit Projectile and stops on the first body in ITS lane - which is why a wide cone "
     "can still miss. A cone is NEVER a hitbox anywhere in this sheet. The only other thing that "
     "looks like one is Gwen's Sweep Laser, and that is a LINE sweeping sideways - the cone is "
     "just the shape its path leaves behind. (An earlier version of this row claimed Gwen's cone "
     "was a real collider; that was wrong.)"],
    ["Current + Left + Right", "One instance at the current target, one at the enemy to its LEFT, "
     "one to its RIGHT.",
     "The Aim Target + its 2 neighbours", "Karma (3rd cast)",
     "Deliberately not three on the same target, which would be overpowered. All three share ONE "
     "hitbox, so an enemy caught by two of them is not damaged twice - the opposite of "
     "'Same target'."],
    # The first spread whose aim is NOT fixed at cast. See 'Note - Mid-action change' - this and
    # Gwen's sweeping hitbox are the same gap seen twice.
    ["Re-picked per instance", "Each instance CHOOSES ITS OWN TARGET when it fires, so the "
     "instances can walk from body to body.",
     "Re-evaluated per instance — NOT fixed at cast", "Soraka (5 stars, over 5s)",
     "The only spread where the aim is re-evaluated DURING the action. Soraka's stars each ask "
     "again 'which enemy is closest to the healed ally NOW?', and over 5 seconds the board moves, "
     "so star 5 can land on a different enemy than star 1. Contrast 'Same target', which fixes the "
     "target once at cast and sends every instance there regardless."],
    ["360° radial", "One instance expanding from the caster in ALL directions at once.",
     "Self - it is not aimed at anything", "Ahri (2nd-cast wave)",
     "Count stays 1: it is a single expanding hitbox, not N instances. It earns a Spread anyway "
     "because the arrangement is what makes it un-aimed - the hitbox is large enough to reach the "
     "whole board, so Aim Target = Self and Recipient = All enemies."],
]

# (champion, step) -> {column: value}. Multiplicity lifted out of Scaling, plus the Ahri fix.
TEMPLATE_FIXES = {
    ("Ashe", "1"): {"Count": "8", "Spread": "Cone", "Scaling": D},
    ("Akshan", "1"): {"Count": "6", "Spread": "Same target", "Scaling": D},
    ("Karma", "3"): {"Count": "3", "Spread": "Current + Left + Right", "Scaling": D},
    # The Summon step spawns up to 3 soldiers; the strike is 3 auto-attacks on one target.
    ("Azir", "2"): {"Count": "3", "Spread": D, "Scaling": "max 3 Soldiers on the board"},
    ("Azir", "3"): {"Count": "3", "Spread": "Same target", "Scaling": D},
    # Ahri's wave does not travel AT anything: it erupts from her in every direction, and its
    # hitbox is big enough to catch the whole board. Aim is Self, not Current.
    ("Ahri", "3"): {"Count": "1", "Spread": "360° radial", "Aim Target": "Self",
                    "Effect Recipient": "All enemies",
                    "Scaling": "+33% if essence stolen"},
}


def write_tab(sh, title, rows, width):
    """Create-or-rewrite a reference tab wholesale from the constants above.

    Cleared first, so a row dropped from the constants is dropped from the sheet too - without
    the clear, shrinking a tab leaves the old tail rows orphaned below the new content.

    A PROSE ROW (text in col A, nothing beside it) is merged across the full width and wrapped.
    Left unmerged it renders as one long line clipped into a narrow cell, which is unreadable -
    so prose is written as whole sentences and the cell is widened to hold them, rather than the
    sentence being hand-broken across several rows to fit the cell.
    """
    ws = next((w for w in sh.worksheets() if w.title == title), None)
    if ws is None:
        ws = sh.add_worksheet(title=title, rows=max(len(rows), 20), cols=width)
        print(f"created the '{title}' tab")
    if ws.row_count < len(rows):
        ws.add_rows(len(rows) - ws.row_count)
    if ws.col_count < width:
        ws.add_cols(width - ws.col_count)

    ws.clear()
    ws.update(rows, f"A1:{col_letter(width - 1)}{len(rows)}", value_input_option="RAW")
    ws.format(f"A1:{col_letter(width - 1)}1",
              {"textFormat": {"bold": True},
               "backgroundColor": {"red": 0.82, "green": 0.88, "blue": 0.82}})

    prose = [i for i, r in enumerate(rows)
             if i > 0 and r[0].strip() and not any(str(c).strip() for c in r[1:])]
    # clear() wipes values, not merges - so unmerge first, or re-running collides with the
    # merges the previous run left behind.
    requests = [{"unmergeCells": {"range": {"sheetId": ws.id}}}]
    requests += [{"mergeCells": {
        "range": {"sheetId": ws.id, "startRowIndex": i, "endRowIndex": i + 1,
                  "startColumnIndex": 0, "endColumnIndex": width},
        "mergeType": "MERGE_ROWS",
    }} for i in prose]
    requests += [{"repeatCell": {
        "range": {"sheetId": ws.id, "startRowIndex": min(prose), "endRowIndex": max(prose) + 1,
                  "startColumnIndex": 0, "endColumnIndex": width},
        "cell": {"userEnteredFormat": {"wrapStrategy": "WRAP", "verticalAlignment": "TOP"}},
        "fields": "userEnteredFormat(wrapStrategy,verticalAlignment)",
    }}]
    sh.batch_update({"requests": requests})
    print(f"{title}: merged + wrapped {len(prose)} prose rows across A:{col_letter(width - 1)}")
    return ws


def build_spread_tab(sh):
    """Spread gets its own reference tab, alongside Action / Effect / Collision Types.

    It was a block bolted onto the bottom of `Action Templates`, which put a real axis of the
    schema in a footnote. Spread is orthogonal to the Action - Ashe's Cone and Akshan's Same
    target are the same Action - so it is not a property of one, and does not belong under it.
    """
    rows = [["Spread", "What it means", "Aims around", "Used by", "Clarify more"]]
    rows += SPREADS
    rows += [[""] * 5]
    rows += [["How to read this tab", "", "", "", ""]]
    for line in [
        "Spread answers one question: given Count instances of a single Action, WHERE do they go?",
        "It is orthogonal to the Action. Ashe (Cone) and Akshan (Same target) fire the exact same "
        "Action - First hit Projectile - and differ only in arrangement, which is why Spread is "
        "its own tab rather than a property of the Action. The Action's own decomposition lives "
        "in 'Action Templates'.",
        "Count = 1 means Spread is an em-dash: a single instance has nothing to arrange. The one "
        "exception is 360° radial - a single expanding hitbox whose ARRANGEMENT is still what "
        "makes it un-aimed (Aim Target = Self, Recipient = All enemies).",
    ]:
        rows += [[line, "", "", "", ""]]

    write_tab(sh, SPREAD_TAB, rows, 5)
    print(f"{SPREAD_TAB}: wrote {len(SPREADS)} spread definitions")


def backfill_hero(sh):
    """Guarantee every action row in `Hero` carries a Count and a Spread.

    The tab that this script once built as `Hero (template)` IS `Hero` now (see
    tft-promote-template.py), so there is nothing left to duplicate - but the invariant it
    established still has to hold as new regions are added. `append_champions()` in the
    tft-add-*.py scripts fills rows by column NAME and knows nothing about Count/Spread, so a new
    region would land with both cells blank. Blank reads as "unknown"; the default says "fires
    once, nothing to arrange". Filling only the blanks means a region script that sets them
    itself is never overwritten.
    """
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    c = cols(vals[0])

    # A column inserted mid-table is UNMERGED inside every multi-row action, so a continuation
    # row would read as an action of its own. Only merge what is not merged already.
    groups = [(a, b) for a, b in action_groups(vals, c) if b - a > 1]
    meta = sh.fetch_sheet_metadata({"includeGridData": False})
    sheet = next(s for s in meta["sheets"] if s["properties"]["sheetId"] == ws.id)
    merged_cols = {m["startColumnIndex"] for m in sheet.get("merges", [])}
    todo = [n for n in ("Count", "Spread") if c[n] not in merged_cols]
    if todo:
        sh.batch_update({"requests": [merge_request(ws.id, a, b, c[n])
                                      for a, b in groups for n in todo]})
        print(f"Hero: re-merged {todo} across {len(groups)} multi-row actions")

    edits, champ = [], ""
    for i, r in enumerate(vals):
        if i == 0:
            continue
        if r[c["Champion"]].strip():
            champ = r[c["Champion"]].strip()
        if not r[c["Step"]].strip():
            continue
        fix = TEMPLATE_FIXES.get((champ, r[c["Step"]].strip()), {})
        for name, value in {"Count": COUNT_DEFAULT, "Spread": SPREAD_DEFAULT}.items():
            if not r[c[name]].strip():
                edits.append({"range": f"{col_letter(c[name])}{i + 1}", "values": [[value]]})
        for name, value in fix.items():   # the champions whose multiplicity is not the default
            if r[c[name]] != value:
                edits.append({"range": f"{col_letter(c[name])}{i + 1}", "values": [[value]]})
    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Hero: {len(edits)} Count/Spread cells backfilled")


REPLIES = [
    ("Dedicate new tab to it",
     "Done - 'Spread Types' is now its own tab, sitting beside Action Types / Effect Types / "
     "Collision Types instead of hanging off the bottom of Action Templates.\n\n"
     "You are right that it was misfiled. Spread is ORTHOGONAL to the Action, not a property of "
     "one: Ashe (Cone) and Akshan (Same target) fire the exact same Action - First hit Projectile "
     "- and differ only in arrangement. Filing it under Action Templates said the opposite.\n\n"
     "The tab is 5 columns (Spread | What it means | Aims around | Used by | Clarify more) and "
     "documents 5 values, including the '—' default - Count = 1 means there is nothing to arrange, "
     "and that must be an em-dash rather than blank, or it reads as 'unknown'.\n\n"
     "Two things the split forced into the open:\n"
     "- 'Same target' vs 'Current + Left + Right' differ in HITBOX COUNT, not just geometry. "
     "Akshan's 6 shots are 6 separate hitboxes (one target, hit 6 times); Karma's 3 share ONE "
     "hitbox, so an enemy caught twice is not damaged twice. Same axis, opposite hitbox rule.\n"
     "- Ashe's cone is an emergent shape, not a hitbox - there is no cone collider. Each arrow is "
     "its own First hit Projectile that stops on the first body in ITS lane, which is why a wide "
     "cone can still miss.\n\n"
     "Ahri keeps Count = 1: her wave is one expanding hitbox, not N instances. She earns a Spread "
     "anyway because the arrangement is exactly what makes her un-aimed (Aim = Self, Recipient = "
     "All enemies)."),
]


def main():
    sh = open_sheet()
    build_spread_tab(sh)
    backfill_hero(sh)
    post_replies(REPLIES, warn_unmatched=False)
    print("\nThe template model is canonical: `Hero` carries Count/Spread, and the two reference "
          "tabs define them.")


if __name__ == "__main__":
    main()
