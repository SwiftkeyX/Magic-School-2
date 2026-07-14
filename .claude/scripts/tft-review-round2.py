"""Apply the second review round on the Shadow Isles / Targon pass.

Run from repo-root cwd:  python .claude/scripts/tft-review-round2.py

Three of the user's comments correct the MODEL, not just cells:

  1. CADENCE IS NOT A DURATION. `Perm` was being used as a Cadence, but Cadence is the
     APPLICATION time of an effect - and a permanent buff is applied exactly ONCE; it simply
     never expires. So Cadence = Once, and Duration = Permanent. The user put it exactly right:
     "the stack have application time to 1, but it stay permanent". This lands on 14 rows, and 12
     of them predate this pass (every Ionia bonus passive, plus Samira and Kled) - the error was
     always there; Viego just made it visible.

  2. `Empowered Attack` WAS COVERING TWO MECHANICS. Orianna and Maokai get ONE empowered attack,
     consumed by the next hit. Viego STACKS his and it never falls off, so every attack is
     empowered forever. Same words, different mechanic. Viego moves to a new `On-Hit Damage`, and
     Empowered Attack's definition tightens to strictly the one-shot.

  3. GWEN'S CONE IS NOT A HITBOX. "It didn't spawn as a cone hitbox but it was laser that got
     sweep to look like the cone." So `Cone Slash` is retired for `Sweep Laser`, and the earlier
     'Note - Cone' - which taught that a cone CAN be a real collider - is now FALSE and is
     rewritten, not amended. A cone is never a hitbox: it is either an arrangement of separate
     hitboxes (Ashe) or the illusion left by a sweeping one (Gwen).

Plus: Viego is a Laser Shot, not a Cast. Maokai's range is 1.

`Action Model` (tft-action-model.py) is the tab that defines the actions now. This script only
corrects `Hero`, `Effect Types` and `Column Explain`.
"""

from tft_sheet import D, col_letter, cols, open_sheet, post_replies

# Gwen's cone, from the user's sketch: one hex at range 1, three at range 2. Depth 2, 4 hexes.
GWEN_CONE = "4 (1 hex at range 1, 3 at range 2)"

# (champion, step) -> {column: value}
HERO_FIXES = {
    # Not a melee Cast - it is a beam. The user was explicit: "The viego isn't cast, it was laser
    # shot." Laser Shot is Pierce-All, which means it hits EVERYTHING in the path - and the source
    # text only ever mentions the current target. Asked as Q8; the recipient is left as-is until
    # answered, so this script does not silently widen who he damages.
    ("Viego", "1"): {"Action": "Laser Shot", "Collision": "Pierce-All"},
    # The cone is an illusion left by a sweeping laser, not a collider.
    ("Gwen", "2"): {"Action": "Sweep Laser", "Collision": "Pierce-All", "AOE": GWEN_CONE},
}

# (champion, category, detail) -> {column: value}. Keyed on the effect, because these land on
# continuation rows inside a multi-effect action.
EFFECT_FIXES = {
    # Every attack, forever - not one attack, once. That is a different effect from Orianna's.
    ("Viego", "Buff", "Empowered Attack"): {"Effect Detail": "On-Hit Damage"},
}

# Maokai's whole stat block is N/A in the source. The user: "Maokai skill is to empower the AA, so
# it just normal AA range" - he is a melee Bastion, so 1.
IDENTITY_FIXES = {("Maokai", "Range"): "1"}

EFFECT_TYPES = [
    ["Buff", "On-Hit Damage",
     "EVERY attack by the recipient deals bonus damage, for as long as the buff lasts. Distinct "
     "from Empowered Attack, which is spent on the NEXT attack and then gone. Viego's stacks and "
     "never expires (Duration = Permanent); Aphelios' lasts 7s."],
]

# Empowered Attack now means strictly the one-shot - tightened so the two cannot blur again.
EFFECT_REDEFS = {
    ("Buff", "Empowered Attack"):
        "The recipient's NEXT attack deals bonus damage - ONE attack, then the buff is spent. If "
        "every attack is buffed for a duration, that is On-Hit Damage, not this (Orianna, Maokai).",
}

COLUMN_EXPLAIN_EDITS = {
    # 'Perm' is gone: it was a Duration wearing a Cadence's clothes.
    "Cadence": {
        2: "Once / Over Time. This is the APPLICATION time of the effect - how the effect is "
           "dealt out, not how long it lasts. A permanent buff is applied ONCE and then never "
           "expires: that is Cadence = Once with Duration = Permanent, NOT a cadence of its own. "
           "('Perm' was previously used here and was a category error.)",
    },
    "Duration (s)": {
        2: "Numeric seconds; per-star when it varies - e.g. Stun 1.5/2/8, Shred 3. 'Permanent' if "
           "it lasts the whole combat and never falls off (Viego's stacks, every Ionia bonus). "
           "Blank / em-dash if the effect is instant and has nothing to expire.",
    },
    # This note previously taught that Shape = Cone is a real collider (Gwen). That is FALSE - she
    # is a sweeping laser. Rewritten rather than amended: the old text is not salvageable.
    "Note - Cone: shape vs spread": {
        1: "A cone is NEVER a hitbox. It is always either an arrangement or an illusion.",
        2: "There is no cone collider anywhere in this sheet. Two different things LOOK like a "
           "cone: (1) SPREAD = Cone ('Spread Types') - N separate hitboxes ARRANGED in a cone, "
           "each its own projectile. Ashe's 8 arrows: each stops on the first body in ITS lane, "
           "which is why a wide Ashe cone can still miss. (2) A SWEEPING hitbox - Gwen's Sweep "
           "Laser is a LINE that sweeps sideways through an arc, and the cone is just the shape "
           "its path leaves behind. An earlier version of this note claimed Gwen's cone was a real "
           "collider; that was wrong.",
    },
}

REPLIES = [
    # Match keys are substrings of the COMMENT's own text - not of a reply underneath it, which
    # post_replies never looks at. And keep them short: this comment contains a NON-BREAKING space
    # ("weird\xa0as a cadence"), so a longer key silently failed to match.
    ("I think Permanenet is weird",
     "Yes, and you have named the error exactly: Cadence is the APPLICATION time, and a permanent "
     "buff is applied once - it just never expires. Cadence = Once, Duration = Permanent.\n\n"
     "This was not only the new rows. 14 rows carried Cadence = Perm and 12 of them predate this "
     "pass - every Ionia bonus passive, plus Samira's DEF shred and Kled's Attack Speed. The "
     "mistake was always in the sheet; Viego is just where it became visible. All 14 are fixed.\n\n"
     "'Perm' is removed from the Cadence value list, which is now strictly Once / Over Time, and "
     "'Permanent' is documented as a Duration value."),

    ("This is different from Oriana",
     "Agreed, and that settles Q2 - they are two different mechanics wearing one name.\n\n"
     "Orianna and Maokai: ONE empowered attack, spent on the next hit, gone.\n"
     "Viego: the stack never falls off, so EVERY attack is empowered for the rest of combat.\n\n"
     "Viego moves to a new effect, Buff > On-Hit Damage: 'every attack deals bonus damage for as "
     "long as the buff lasts'. Empowered Attack's definition is tightened to strictly the one-shot "
     "so the two cannot blur back together. Viego's Duration is now 'Permanent' and his Cadence is "
     "Once, per your other comment."),

    ("Did this get metion that her empower attack can only used once",
     "It does now. Maokai IS the one-shot kind - his heal rides on the single next attack and is "
     "then spent - and the Effect Types definition of Empowered Attack now says that explicitly: "
     "'the recipient's NEXT attack deals bonus damage - ONE attack, then the buff is spent'.\n\n"
     "That wording only became possible once Viego moved OFF Empowered Attack onto the new On-Hit "
     "Damage (see your Viego comment). While one word covered both mechanics it could not be "
     "pinned down without making it wrong for the other."),

    ("For gwen, her cone is a laser hitbox",
     "That is a better answer than either option I offered you, and it kills the action I built.\n\n"
     "'Cone Slash' is retired. Gwen is now 'Sweep Laser': laser delivery (spawns on her, no "
     "travel), Pierce-All, Shape = 'Line - SWEPT through an arc'. The cone is not a collider at "
     "all - it is just the shape the sweeping line leaves behind.\n\n"
     "It also exposes a real gap: NOTHING in this schema can say that a hitbox MOVES while the "
     "action runs. Delivery says where it spawns, Shape says what it is, Count/Spread says how "
     "many and where - none of them say it travels sideways. For now the sweep is carried in the "
     "Shape text and flagged as a known gap in 'Action Model'. One case is not enough to justify a "
     "column; a second swept action would be.\n\n"
     "The old 'Note - Cone' taught that a cone CAN be a real hitbox. That is now false, so I "
     "rewrote it rather than adding to it: a cone is never a hitbox - it is either an arrangement "
     "of separate hitboxes (Ashe) or the illusion left by a sweeping one (you)."),

    ("This is Laser shot",
     "Done - Viego's step 1 is now Laser Shot (Pierce-All), not Cast.\n\n"
     "One thing I did NOT change, because I would be inventing it: Laser Shot pierces EVERYTHING "
     "in its path, but the source text only ever says 'deal damage to the current target'. So his "
     "Effect Recipient still reads 'Same to Aim Target' - i.e. only the aimed enemy is damaged. If "
     "the beam really does damage every enemy it passes through, tell me and I will change the "
     "recipient to 'Enemies in path'. Asked as Q8."),

    ("Q7 - Senna",
     "You asked: \"isn't Farthest work like her skill wanted?\" - it does, and checking the sheet, "
     "my question was based on a false premise. Sorry.\n\n"
     "I said I had ADDED 'Farthest' as a new value. I had not: Akshan (row 77) was already using "
     "it. It was simply missing from the documented list in Column Explain, so I mistook an "
     "undocumented value for a new one.\n\n"
     "Both values are real and both stay: 'Farthest' = the furthest enemy on the board (Akshan, "
     "Senna), and 'Farthest (within N hex)' = the furthest one inside a search radius (Zed within "
     "2, Yasuo within 3). Nothing to collapse. No change needed."),

    ("Q2 - Viego and Aphelios both overload",
     "Answered by your own comment on Viego's row - so this one is closed.\n\n"
     "You said it plainly: Orianna has ONE empowered attack, spent the moment she next attacks; "
     "Viego stacks his and the stack never goes away, so every attack is empowered. That is two "
     "mechanics under one name, which is what I suspected but could not settle from the text.\n\n"
     "Done: Viego moves to a new Buff > On-Hit Damage ('EVERY attack deals bonus damage for as "
     "long as the buff lasts'), and Empowered Attack is tightened to strictly the one-shot. "
     "Aphelios never actually used Empowered Attack - his per-Chakram bonus was already an "
     "Attack > Damage row - so he needed no change."),

    ("Q6 - Gwen's cone size",
     "Maokai's Range is set to 1 - melee, his normal attack range, per your answer. That closes "
     "the only stat the source left blank for him.\n\n"
     "Your Gwen sketch I read as: one hex directly in front of her, then three hexes across at "
     "range 2 - a depth-2 cone, 4 hexes total. AOE is now '4 (1 hex at range 1, 3 at range 2)'. "
     "Correct me if the tip is wider than that."),
]

QUESTIONS = [
    ("Q9 - The 'Range' column holds two different units, and that is my fault",
     "Q9 - The 'Range' column holds two different units, and that is my fault\n\n"
     "The column is headed 'Range'. Checking all 43 champions:\n\n"
     "- The 35 champions that were already there hold a POSITION: 'Frontliner' or 'Backliner'. "
     "Every single one.\n"
     "- The 8 I added (Shadow Isles + Targon) hold a NUMBER: Viego 1, Gwen 2, Senna 4, Kalista 4, "
     "Soraka 4, Taric 1, Aphelios 4.\n\n"
     "I took the header at its word and copied the numeric Range straight from tft-set9 -> "
     "Champions. Everyone before me used the column for front/back position instead. So the column "
     "now means two things, and one of us has to move.\n\n"
     "This also makes the Maokai answer you just gave me land in the wrong unit: I set his Range "
     "to 1 (melee), but if this column is really 'position' then he should read 'Frontliner'.\n\n"
     "Which do you want?\n"
     "(a) The column IS position. Then my 8 champions are wrong - I convert them to Frontliner / "
     "Backliner, and the column gets RENAMED (it is not a range).\n"
     "(b) The column IS range (the header is right). Then the 35 older champions are wrong and I "
     "backfill real numbers from the source for all of them.\n"
     "(c) Both matter - then they are two columns, not one, and I add the missing one.\n\n"
     "I lean (c): 'is it a frontliner' and 'how many hexes can it reach' are different facts and "
     "the source sheet carries both. But 35-vs-8 says the established meaning is position, so I "
     "am not going to overwrite either group on my own authority."),

    ("Q8 - Viego's beam: does it damage everyone it pierces?",
     "Q8 - Viego's beam: does it damage everyone it pierces?\n\n"
     "You said Viego is a Laser Shot, not a Cast, and I have changed it (Hero row 116).\n\n"
     "But Laser Shot is defined as Pierce-All: the beam passes through and hits EVERY unit in its "
     "path. The source text says only 'Deal 110/165/250% AP magic damage to the current target' - "
     "it never mentions anyone else.\n\n"
     "So the two halves of the row now disagree, and I have deliberately left the disagreement "
     "visible rather than resolving it by guesswork:\n"
     "  Collision       = Pierce-All        (the hitbox pierces)\n"
     "  Effect Recipient = Same to Aim Target (only the aimed enemy is damaged)\n\n"
     "Which is right?\n"
     "(a) The beam pierces but only the aimed enemy takes damage - the pierce is cosmetic. Then "
     "the row is correct as it stands, and Laser Shot needs to allow a Target-Only recipient.\n"
     "(b) Everyone in the path takes damage. Then Recipient becomes 'Enemies in path' and the "
     "source text is simply incomplete.\n\n"
     "I would rather ask than widen who a champion damages on my own authority."),
]


def fix_hero(sh):
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    c = cols(vals[0])
    edits = []
    champ = ""

    for i, r in enumerate(vals):
        if i == 0:
            continue
        if r[c["Champion"]].strip():
            champ = r[c["Champion"]].strip()
        n = i + 1

        for (ch, column), value in IDENTITY_FIXES.items():
            if champ == ch and r[c["Champion"]].strip() and r[c[column]] != value:
                edits.append({"range": f"{col_letter(c[column])}{n}", "values": [[value]]})

        step = r[c["Step"]].strip()
        key = (champ, r[c["Effect Category"]].strip(), r[c["Effect Detail"]].strip())
        for column, value in {**HERO_FIXES.get((champ, step), {}),
                              **EFFECT_FIXES.get(key, {})}.items():
            if r[c[column]] != value:
                edits.append({"range": f"{col_letter(c[column])}{n}", "values": [[value]]})

        # Cadence is an application time, not a lifetime. Perm was neither.
        if r[c["Cadence"]].strip() == "Perm":
            edits.append({"range": f"{col_letter(c['Cadence'])}{n}", "values": [["Once"]]})
            if r[c["Duration"]].strip() in ("", D):
                edits.append({"range": f"{col_letter(c['Duration'])}{n}",
                              "values": [["Permanent"]]})

    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Hero: {len(edits)} cells corrected (Perm sweep + Viego/Gwen/Maokai)")


def fix_reference_tabs(sh):
    ws = sh.worksheet("Effect Types")
    vals = ws.get_all_values()
    seen = {(r[0], r[1]) for r in vals}
    pending = [e for e in EFFECT_TYPES if (e[0], e[1]) not in seen]
    if pending:
        ws.append_rows(pending, value_input_option="RAW")
        vals = ws.get_all_values()
    edits = [{"range": f"C{i + 1}", "values": [[text]]}
             for i, r in enumerate(vals)
             for key, text in EFFECT_REDEFS.items()
             if (r[0], r[1]) == key and r[2] != text]
    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Effect Types: added {len(pending)} rows, {len(edits)} definitions tightened")

    ws = sh.worksheet("Column Explain")
    vals = ws.get_all_values()
    edits = []
    for label, columns in COLUMN_EXPLAIN_EDITS.items():
        i = next((k for k, r in enumerate(vals) if r[0].strip() == label), None)
        if i is None:
            raise SystemExit(f"Column Explain: row '{label}' not found")
        for col, text in columns.items():
            if vals[i][col] != text:
                edits.append({"range": f"{col_letter(col)}{i + 1}", "values": [[text]]})
    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Column Explain: {len(edits)} cells updated")


def ask(sh_key_session):
    from google.auth.transport.requests import AuthorizedSession
    from google.oauth2.service_account import Credentials
    from tft_sheet import CRED, KEY

    creds = Credentials.from_service_account_file(
        CRED, scopes=["https://www.googleapis.com/auth/drive"])
    s = AuthorizedSession(creds)
    url = f"https://www.googleapis.com/drive/v3/files/{KEY}/comments"
    r = s.get(url, params={"fields": "comments(content)", "pageSize": 100})
    r.raise_for_status()
    existing = [c["content"] for c in r.json().get("comments", [])]

    posted = 0
    for tag, body in QUESTIONS:
        if any(tag in c for c in existing):
            continue
        s.post(url, params={"fields": "id"}, json={"content": body}).raise_for_status()
        posted += 1
    print(f"Questions: posted {posted} new")


def main():
    sh = open_sheet()
    fix_hero(sh)
    fix_reference_tabs(sh)
    post_replies(REPLIES, warn_unmatched=False)
    ask(sh)


if __name__ == "__main__":
    main()
