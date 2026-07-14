"""Round 4: the Range column becomes a real range, and Soraka gets a re-picking spread.

Run from repo-root cwd:  python .claude/scripts/tft-review-round4.py

DECISIONS TAKEN (by the user, in the terminal - the Range one was "too wrong for the comment")
----------------------------------------------------------------------------------------------
  Q9  The `Range` column IS a range. The header was right all along and the DATA was wrong: all 35
      champions added before Shadow Isles held a position ('Frontliner' / 'Backliner') in it.
      Those are discarded and every champion is backfilled with its real hex range from
      tft-set9 -> Champions -> Range.

      Note what is being thrown away: Frontliner/Backliner appears NOWHERE in the source sheet, so
      it was a human judgement someone made and it is not recoverable from tft-set9. It is being
      dropped on the user's explicit call. If it turns out to matter, it has to come back as its
      OWN column - it must never move back into this one.

  Q3  Soraka's 5 stars RE-PICK their target between stars: each star asks again which enemy is
      closest to the healed ally, so they can walk from body to body over the 5 seconds. Spread
      'Same target' was wrong. New spread: `Re-picked per instance`.

  Q1  "Effect sound right to me" - a stack counter stays an Effect Detail (Impale / Chakram /
      On-Hit Damage). NO new Stacks column. Recorded so it is not re-litigated.

THE PATTERN WORTH NAMING
------------------------
`Re-picked per instance` is the SECOND thing this model cannot say, after Gwen's sweeping laser.
Both are the same shape: something changes WHILE the action runs. Gwen's hitbox moves; Soraka's
aim is re-evaluated. Every axis so far (Delivery, Shape, Collision, Count, Spread) describes an
action as if it were frozen at the moment of cast. Two cases is not yet a column - but it is no
longer a coincidence, and a third would settle it.
"""

import gspread

from tft_sheet import col_letter, cols, open_sheet, post_replies

SOURCE_KEY = "1xj6em5XlvIN1gWHTKOPDsssmkgnS3jIsaLnAMjYyPUA"   # tft-set9

# Maokai's whole stat block is N/A in the source. The user: "Maokai skill is to empower the AA, so
# it just normal AA range" - melee Bastion, so 1. The ONLY value here not taken from the source.
RANGE_OVERRIDES = {"Maokai": "1"}

SPREAD_FIX = {("Soraka", "3"): {"Spread": "Re-picked per instance"}}

# The 'Champion … Skill Description' row is OWNED by tft-apply-comments.py, so the Range wording
# lives there, not here. This script writing it too would mean two scripts fighting over one cell
# on every run - which is exactly what the acceptance test caught when I tried it.
COLUMN_EXPLAIN_NOTES = [
    ["Note - Range",
     "This column is a NUMBER of hexes. It used to hold Frontliner/Backliner for 35 champions.",
     "The header always said 'Range' but the data disagreed with it: the first 35 champions stored "
     "a POSITION (Frontliner / Backliner) and the Shadow Isles / Targon 8 stored the real hex "
     "range from the source. The user's call: the header is right, so every champion is now "
     "backfilled from tft-set9 -> Champions -> Range and the position labels are gone. WARNING: "
     "Frontliner/Backliner exists NOWHERE in tft-set9 - it was somebody's judgement and it is not "
     "recoverable. If it is ever needed again it must come back as its OWN column and never into "
     "this one. Maokai is the single value not from the source (his whole stat block is N/A "
     "there); he is 1, melee, per the user."],
    ["Note - Stacks",
     "A stack counter is an Effect Detail, NOT a column. Decided - do not re-open.",
     "Viego's stacking On-Hit Damage, Kalista's Impale and Aphelios' Chakram are all the same "
     "shape: a counter that does nothing itself and multiplies a later effect. It was proposed as "
     "a 4th axis deserving its own column, like Action Source and Count/Spread before it. The "
     "user's answer: 'Effect sound right to me' - it stays an Effect Detail. Recorded here so the "
     "question is not asked a third time."],
    ["Note - Mid-action change (KNOWN GAP)",
     "The schema describes every action as if frozen at the moment of cast. Two champions break "
     "that.",
     "Gwen's Sweep Laser: the HITBOX MOVES while the action runs - Delivery says where a hitbox "
     "spawns and Shape says what it is, but neither can say it travels sideways. Soraka's stars: "
     "the AIM IS RE-EVALUATED between instances (Spread = Re-picked per instance), so the target "
     "can change mid-action. Same shape of gap, twice: something changes DURING the action, and "
     "every axis we have (Delivery / Shape / Collision / Count / Spread) assumes nothing does. Two "
     "cases is not enough to justify a column. A THIRD would settle it - watch for one."],
]

REPLIES = [
    ("Q9 (re-ask)",
     "Decided in the terminal, as you asked: the column IS a range. The header was right and the "
     "DATA was wrong.\n\n"
     "All 43 champions now carry their real hex range from tft-set9 -> Champions -> Range (Kayle "
     "4, Poppy 1, Jhin 5, Ashe 6, ...). The 35 'Frontliner'/'Backliner' values are gone.\n\n"
     "One thing you should know about what was just thrown away: Frontliner/Backliner appears "
     "NOWHERE in tft-set9. It was a human judgement someone made, and it is not recoverable from "
     "the source - I can rebuild ranges from tft-set9 any time, but I cannot rebuild those. If it "
     "turns out you want that classification back, it has to come back as its OWN column. It must "
     "never go back into this one. Flagged as 'Note - Range'.\n\n"
     "Maokai is the only value not from the source (his stat block is entirely N/A there): he is "
     "1, melee, per your answer."),

    ("Q3 (re-ask)",
     "New spread added: 'Re-picked per instance'. Soraka's step 3 now uses it.\n\n"
     "Each of the 5 stars asks again which enemy is closest to the healed ally, so they can walk "
     "from body to body across the 5 seconds. 'Same target' asserted the opposite and was wrong.\n\n"
     "This is worth flagging, because it is the SECOND time this has bitten: it is the same shape "
     "of gap as Gwen's sweeping laser. Gwen's HITBOX moves while the action runs; Soraka's AIM is "
     "re-evaluated while the action runs. Every axis in this model - Delivery, Shape, Collision, "
     "Count, Spread - describes an action as if it were frozen at the instant of cast, and twice "
     "now that has turned out to be false.\n\n"
     "Two cases is not enough to build a column on, so I have not. But it is no longer a "
     "coincidence, and a third would settle it. Recorded as 'Note - Mid-action change (KNOWN GAP)' "
     "so we notice the third one when it arrives."),

    ("Q1 (re-ask)",
     "Understood - it stays an Effect Detail, and I will stop pushing on it.\n\n"
     "Viego's On-Hit Damage, Kalista's Impale and Aphelios' Chakram remain three separate Effect "
     "Details rather than becoming a 'Stacks' column.\n\n"
     "Recorded as 'Note - Stacks' in Column Explain, with the reasoning and your answer, so that "
     "nobody (me included) proposes the same column again in three months."),
]


def backfill_range(sh):
    src = gspread.service_account(filename="google-service-credential.json").open_by_key(SOURCE_KEY)
    cv = src.worksheet("Champions").get_all_values()
    h = cv[0]
    ni, ri = h.index("Champion Name"), h.index("Range")
    source = {r[ni].strip(): r[ri].strip() for r in cv[1:] if r[ni].strip()}

    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    c = cols(vals[0])

    edits, unknown = [], []
    for i, r in enumerate(vals):
        if i == 0 or not r[c["Champion"]].strip():
            continue
        champ = r[c["Champion"]].strip()
        want = RANGE_OVERRIDES.get(champ, source.get(champ, ""))
        if not want.isdigit():
            unknown.append(champ)
            continue
        if r[c["Range"]].strip() != want:
            edits.append({"range": f"{col_letter(c['Range'])}{i + 1}", "values": [[want]]})

    if unknown:
        raise SystemExit(f"Range unresolved for {unknown} — refusing to guess")
    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Hero: {len(edits)} Range cells backfilled from tft-set9 (position labels discarded)")


def fix_spread(sh):
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    c = cols(vals[0])
    edits, champ = [], ""
    for i, r in enumerate(vals):
        if i == 0:
            continue
        if r[c["Champion"]].strip():
            champ = r[c["Champion"]].strip()
        for column, value in SPREAD_FIX.get((champ, r[c["Step"]].strip()), {}).items():
            if r[c[column]] != value:
                edits.append({"range": f"{col_letter(c[column])}{i + 1}", "values": [[value]]})
    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Hero: {len(edits)} Spread cells corrected (Soraka re-picks)")


def fix_column_explain(sh):
    ws = sh.worksheet("Column Explain")
    vals = ws.get_all_values()
    seen = {r[0].strip() for r in vals if r}
    notes = [n for n in COLUMN_EXPLAIN_NOTES if n[0] not in seen]
    if notes:
        ws.append_rows(notes, value_input_option="RAW")
    print(f"Column Explain: {len(notes)} note rows appended")


def main():
    sh = open_sheet()
    backfill_range(sh)
    fix_spread(sh)
    fix_column_explain(sh)
    post_replies(REPLIES, warn_unmatched=False)
    print("\n'Re-picked per instance' is defined by tft-action-templates.py (owner of Spread "
          "Types) — run it next.")


if __name__ == "__main__":
    main()
