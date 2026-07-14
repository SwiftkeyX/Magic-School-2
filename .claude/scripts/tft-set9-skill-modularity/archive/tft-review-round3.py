"""Apply the answers to Q4, Q5 and Q8 - and re-ask the three questions still open.

Run from repo-root cwd:  python .claude/scripts/tft-review-round3.py

ANSWERED
--------
  Q8 Viego  "It pierce and hit everybody, the description for skill here is wrong."
            -> Recipient becomes 'Enemies in path'. Note what this means: the SOURCE TEXT is
               wrong, not the sheet. tft-set9 says he damages 'the current target'; he does not.
               First time a champion's own skill description has been overruled - flagged in the
               sheet so nobody later "fixes" the row back to match the bad source.
  Q5 Taric  "Redirect those dmg to himself." -> the damage lands on TARIC, not on his shield.
            The shield is just what he happens to be holding when it arrives.
  Q4 Kalista "The spear must stack to the point it can kill the enemy, then it immediately
            triggers." -> lethal is the ONLY removal path, so Trigger 'On Spears Lethal' says it
            and Condition 'If Lethal' was saying it twice. Condition collapses to an em-dash.

STILL OPEN - re-asked, this time ANCHORED AT THE PROBLEM CELL
------------------------------------------------------------
  Q1  Is 'stacks' a missing axis?          -> anchored on Viego's On-Hit Damage cell
  Q3  Do Soraka's 5 stars re-pick?         -> anchored on Soraka's Spread cell
  Q9  What unit is the 'Range' column?     -> anchored on the Range HEADER cell

Q9 was resolved with an EMPTY reply, so it never actually got an answer - and it is the one that
blocks 43 rows. Re-asking rather than guessing.

Drive accepts an anchor and echoes it back, but does not resolve A1 notation into a quoted cell
the way its own UI-made anchors do. So each question is ALSO written as a cell NOTE on the exact
cell, which is guaranteed to show there.
"""

import json

from google.auth.transport.requests import AuthorizedSession
from google.oauth2.service_account import Credentials

from tft_sheet import CRED, D, KEY, col_letter, cols, open_sheet, post_replies, sync_notes

# (champion, step) -> {column: value}
HERO_FIXES = {
    # The beam really does pierce - the skill description in tft-set9 is simply wrong.
    ("Viego", "1"): {"Effect Recipient": "Enemies in path"},
    # Lethal is the only removal path, so the trigger carries it and the condition is redundant.
    ("Kalista", "2"): {"Trigger": "On Spears Lethal", "Condition": D},
}

# (champion, category, detail) -> {column: value}
# Taric's Scaling used to read "redirected into Taric's shield". Round 6 emptied the cell
# entirely: it was never a scaling, just a restatement of what Damage Redirect already means, and
# Scaling now has a fixed vocabulary. The correction lives in the Effect Types definition below.
EFFECT_FIXES = {}

EFFECT_REDEFS = {
    ("Buff", "Damage Redirect"):
        "A share of the damage the recipient takes is dealt to the CASTER instead. It is not a "
        "shield on the recipient and not damage prevention - the damage still happens, it just "
        "happens to someone else. Taric takes it himself; his own Shield is incidental, merely "
        "what it lands on.",
    ("Status", "Impale"):
        "A spear left standing in the target. It does nothing until removed - and the ONLY thing "
        "that removes it is lethality: the spears stack until their combined true damage would "
        "kill the target, and Kalista rips them all out at that moment. There is no other way for "
        "a spear to come out.",
}

COLUMN_EXPLAIN_NOTES = [
    ["Note - Viego / bad source text",
     "His row deliberately CONTRADICTS the source skill description. That is not an error.",
     "tft-set9 -> Champions says Viego deals his damage 'to the current target'. The user "
     "confirmed the real behaviour: 'It pierce and hit everybody, the description for skill here "
     "is wrong.' So he is a Laser Shot (Pierce-All) with Recipient = Enemies in path. This is the "
     "first row where the champion's own skill text is known to be WRONG. Flagged here so nobody "
     "later 'corrects' the row back to match the bad source."],
]

REPLIES = [
    # Match keys are substrings of the COMMENT text, never of a reply underneath it -
    # post_replies only ever looks at the comment. Getting this wrong fails SILENTLY.
    ("Q8 - Viego's beam",
     "Done - Viego's Effect Recipient is now 'Enemies in path', so the row says he damages "
     "everyone the beam passes through.\n\n"
     "Worth flagging what just happened, because it is a first: the SOURCE is wrong, not the "
     "sheet. tft-set9 -> Champions says he deals his damage 'to the current target'. Every number "
     "in this sheet is traceable to that column, so a row that knowingly contradicts it needs to "
     "say so out loud - otherwise the next person to compare sheet against source 'fixes' Viego "
     "back to being wrong.\n\n"
     "Recorded as 'Note - Viego / bad source text' in Column Explain."),

    ("Q5 - Taric",
     "Fixed - the redirect lands on TARIC, not on his shield.\n\n"
     "I had written 'redirected into Taric's shield', which quietly implied the redirect only "
     "works while the shield is up. Your answer says otherwise: the damage goes to him. His shield "
     "is incidental - it is just what happens to be standing between that damage and his health "
     "when it arrives.\n\n"
     "The Effect Types definition of Damage Redirect now says it plainly: the damage is not "
     "prevented and the recipient is not shielded - it still happens, it just happens to someone "
     "else."),

    ("Q4 - Kalista",
     "Then the Condition was redundant and it is gone.\n\n"
     "I had Trigger = 'On Spear Removal' + Condition = 'If Lethal', hedging in case a spear could "
     "come out some other way. You have confirmed it cannot: the spears stack until their combined "
     "true damage would kill, and that is what pulls them. So the trigger IS the lethality.\n\n"
     "Kalista's step 2 now reads Trigger = 'On Spears Lethal', Condition = em-dash. 'If Lethal' is "
     "removed from the Condition value list entirely - it existed only for this one row."),
]

# question -> (A1 cell it is about, why that cell)
QUESTIONS = [
    ("Q9", "H1",
     "Q9 (re-ask) - What unit is this column? You resolved it without answering.\n\n"
     "This header says 'Range', and the column below it holds TWO different things:\n\n"
     "- The 35 champions added before Shadow Isles hold a POSITION: 'Frontliner' or 'Backliner'.\n"
     "- The 8 I added hold a NUMBER: Viego 1, Gwen 2, Senna 4, Kalista 4, Soraka 4, Taric 1, "
     "Aphelios 4.\n\n"
     "I trusted the header and copied the numeric Range from tft-set9. Everyone before me used it "
     "for front/back position. One of us has to move, and it is 43 rows either way - so I am not "
     "picking on my own authority.\n\n"
     "(a) It IS position -> I convert my 8 to Frontliner/Backliner, and the column gets RENAMED, "
     "because it is not a range.\n"
     "(b) It IS range -> I backfill real numbers for the other 35 from the source.\n"
     "(c) BOTH matter -> they are two columns, not one, and I add the missing one.\n\n"
     "I lean (c): 'does it stand in front' and 'how many hexes can it reach' are different facts, "
     "and tft-set9 carries both. But 35-vs-8 says the established meaning is position.\n\n"
     "This also decides Maokai: I set his Range to 1 from your answer, but under (a) he should "
     "read 'Frontliner'."),

    ("Q3", "R132",
     "Q3 (re-ask) - Do Soraka's 5 stars re-pick their target between stars?\n\n"
     "This cell says Spread = 'Same target', which asserts the target is chosen ONCE and all 5 "
     "stars land on that same enemy.\n\n"
     "Source: 'Over the next 5 seconds, 5 stars hit the enemy closest to THEM' - 'them' being the "
     "ally she healed. Over 5 seconds the board moves, so 'the enemy closest to the ally' can "
     "change between star 1 and star 5.\n\n"
     "If each star re-evaluates who is closest, 'Same target' is wrong and this needs a NEW Spread "
     "value - something like 'Re-picked per instance'. It would be the first spread where the aim "
     "is re-evaluated DURING the action rather than fixed at cast, which is a real distinction the "
     "model does not yet make.\n\n"
     "Which is it?"),

    ("Q1", "W117",
     "Q1 (re-ask) - Is a stack counter its own Effect, or a missing axis? Still the biggest open "
     "question.\n\n"
     "This cell is Viego's 'On-Hit Damage'. Three of the 8 new champions carry a COUNTER that "
     "other effects scale off, and the schema has no word for the idea - so I encoded all three "
     "differently:\n\n"
     "- Viego (this cell): stacks forever -> Buff > On-Hit Damage, Scaling 'stacking'.\n"
     "- Kalista (W121): spears stack in the target -> Status > Impale.\n"
     "- Aphelios (W136): 3 Chakram, +1 per enemy hit -> Buff > Chakram.\n\n"
     "They are the same shape: a number that goes up, does nothing by itself, and multiplies a "
     "LATER effect. That is exactly what Action Source looked like before it earned a column, and "
     "what multiplicity looked like before Count/Spread - a real recurring axis with nowhere to "
     "live, leaking into whatever field was nearest.\n\n"
     "Is 'Stacks' a real axis that deserves a column, or is a per-champion Effect Detail the right "
     "home and I am over-generalising from 3 cases?\n\n"
     "I lean toward it being real - but 3 is a small sample, and building a column is a bigger "
     "commitment than inventing an Effect Detail, so I would rather you decide."),
]


def fix_hero(sh):
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    c = cols(vals[0])
    edits, champ = [], ""
    for i, r in enumerate(vals):
        if i == 0:
            continue
        if r[c["Champion"]].strip():
            champ = r[c["Champion"]].strip()
        step = r[c["Step"]].strip()
        key = (champ, r[c["Effect Category"]].strip(), r[c["Effect Detail"]].strip())
        for column, value in {**HERO_FIXES.get((champ, step), {}),
                              **EFFECT_FIXES.get(key, {})}.items():
            if r[c[column]] != value:
                edits.append({"range": f"{col_letter(c[column])}{i + 1}", "values": [[value]]})
    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Hero: {len(edits)} cells corrected (Viego pierce, Taric redirect, Kalista trigger)")


def fix_reference_tabs(sh):
    ws = sh.worksheet("Effect Types")
    vals = ws.get_all_values()
    edits = [{"range": f"C{i + 1}", "values": [[text]]}
             for i, r in enumerate(vals)
             for key, text in EFFECT_REDEFS.items()
             if (r[0], r[1]) == key and r[2] != text]
    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Effect Types: {len(edits)} definitions corrected")

    ws = sh.worksheet("Column Explain")
    vals = ws.get_all_values()


def ask_at_cells(sh):
    """Post each open question ANCHORED at its problem cell, and mirror it as a cell note.

    Drive accepts an anchor and echoes it back, but will not resolve A1 notation into a quoted
    cell the way its own UI-made anchors (opaque numeric range ids) do - so the anchor alone may
    not pin the comment visibly. The cell NOTE is the belt to that braces: it is written by the
    Sheets API directly onto the cell and always shows there.
    """
    ws = sh.worksheet("Hero")
    creds = Credentials.from_service_account_file(
        CRED, scopes=["https://www.googleapis.com/auth/drive"])
    s = AuthorizedSession(creds)
    url = f"https://www.googleapis.com/drive/v3/files/{KEY}/comments"
    r = s.get(url, params={"fields": "comments(content)", "pageSize": 100})
    r.raise_for_status()
    existing = [c["content"] for c in r.json().get("comments", [])]

    posted = 0
    for tag, cell, body in QUESTIONS:
        head = body.split("\n")[0]
        if any(head in c for c in existing):
            continue
        anchor = json.dumps({"type": "workbook-range", "uid": ws.id, "range": f"Hero!{cell}"})
        s.post(url, params={"fields": "id"},
               json={"content": body, "anchor": anchor}).raise_for_status()
        posted += 1
    print(f"Questions: posted {posted} anchored comments")

    # cell notes, written straight onto the grid
    requests = [{"repeatCell": {
        "range": _a1_to_gridrange(ws.id, cell),
        "cell": {"note": f"{tag} — see the comment on this cell.\n\n{body}"},
        "fields": "note",
    }} for tag, cell, body in QUESTIONS]
    sh.batch_update({"requests": requests})
    print(f"Questions: wrote {len(requests)} cell notes ({', '.join(q[1] for q in QUESTIONS)})")


def _a1_to_gridrange(sheet_id, cell):
    letters = "".join(ch for ch in cell if ch.isalpha())
    row = int("".join(ch for ch in cell if ch.isdigit()))
    col = 0
    for ch in letters:
        col = col * 26 + (ord(ch.upper()) - 64)
    return {"sheetId": sheet_id, "startRowIndex": row - 1, "endRowIndex": row,
            "startColumnIndex": col - 1, "endColumnIndex": col}


def main():
    sh = open_sheet()
    fix_hero(sh)
    fix_reference_tabs(sh)
    post_replies(REPLIES, warn_unmatched=False)
    ask_at_cells(sh)
    sync_notes(sh, COLUMN_EXPLAIN_NOTES)


if __name__ == "__main__":
    main()
