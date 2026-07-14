"""Apply the 11 review comments left on the `tft-set9-skill` sheet.

Run from repo-root cwd:  python .claude/scripts/tft-apply-comments.py

Two of the comments are taxonomy corrections that reach back into the existing
Demacia/Noxus rows:

  * Projectile vs Laser is now defined by TRAVEL SPEED. A projectile is fired from the
    unit and travels; a laser spawns on the unit and points at the target with no travel
    time. That makes Jhin's line shot a piercing PROJECTILE, and it makes `Wave` a
    duplicate of that same archetype - so `Wave` is deleted and everything collapses
    into one new action, `Pierce Projectile`.
  * Where Effect Recipient merely restates Aim Target, it now reads `Same to Aim Target`.

Idempotent: re-running detects the work is already done and only tops up what is missing.
"""

from tft_sheet import (COUNT_DEFAULT, D, SPREAD_DEFAULT, col_letter, cols, find_row, open_sheet,
                       post_replies)

# Action Types is Action | Collision | Cadence | What it does | Clarify more.
# `What it does` stays ONE clean sentence; every caveat, rule and example lives in `Clarify more`.
# Anything the user wrote themselves is preserved verbatim in the Clarify column.
# ACTION_ROWS lived here: the 'Action Types' tab's contents. That tab is DELETED - the
# 'Action Model' tab (tft-action-model.py) is the canonical action taxonomy now, and this
# script no longer defines actions at all. It still sweeps Hero for retired action NAMES
# below, because those rewrite champion rows, not the taxonomy.

# Box AOE was proposed for Irelia's frontal hit, then dropped: by the projectile/laser rule it is
# laser-like (no travel speed, spawns on the unit, pierces, lands once) - which is just Laser Shot.
# Summon Attack existed only to smuggle the action's SOURCE into its name. Now that the Action
# Source column carries that, it is just Source=Summon + an ordinary Auto-Attack.
RETIRED_ACTIONS = {"Box AOE": "Laser Shot", "Summon Attack": "Auto-Attack",
                   # Gwen's cone was never a collider - it is a sweeping line (the user's call).
                   "Cone Slash": "Sweep Laser"}

# Zed's Shadow and Azir's Sand Soldier are the same archetype - one action covers both.
RENAMED_ACTIONS = {"Summon Shadow": "Summon"}

# NOTE: the Collision Types row TEXT and the Aim Target / Effect Recipient value lists are owned
# by tft-add-shurima.py (the latest origin pass). This script must not also write them, or the two
# scripts overwrite each other on every run. It still owns Action Types and the rows below.

# A returning projectile DOES collide - with the caster. That is not the same as None, which
# means nothing was projected into the world at all.
SELF_COLLISION_ROW = [
    "Self",
    "The caster itself. Something WAS projected into the world and the unit it collides with on "
    "the way back is the caster.",
    "Self",
    "Self only",
    "Receive Projectile",
    "Poppy's thrown shield flies back and collides with her, applying the shield. Distinct from "
    "None: None means nothing was projected at all (a self-cast, a leap).",
]

COLUMN_EXPLAIN_EDITS = {
    "Champion … Skill Description": {
        2: "MERGED vertically across every row the champion owns, so the identity block spans all "
           "of that champion's steps. Origin/Class un-merged into separate slots. Range is the "
           "unit's attack range in HEXES, from tft-set9 → Champions → Range — a number, never a "
           "position. (It held 'Frontliner'/'Backliner' for 35 champions until round 4; see "
           "'Note - Range'.)",
    },
    "(Merged cells)": {
        2: "When Step/Trigger/Action are merged across rows, those rows are the same attack — "
           "e.g. Kayle's Pierce Projectile both Damages and shreds MR.",
    },
    "Collision": {
        1: "The geometry of the hitbox the Action projects into the world.",
        2: "ONLY an action that PROJECTS something has a collision. A self-cast, a melee Cast or a "
           "Leap projects no hitbox — its Collision is None. Values: First-Hit / Pierce-All / Area "
           "/ Target-Only / Flank-Pair / Self / None. 'Self' means something WAS projected and it "
           "collides with the caster (Poppy's returning shield) — that is not the same as None. "
           "Detailed per Action in the 'Action Model' tab.",
    },
    # Aim Target / Effect Recipient value lists are owned by tft-add-shurima.py - see note above.
    "Effect Category": {
        2: "e.g. Attack / Status / Buff / Debuff / Movement / Summon. See the 'Effect Types' tab.",
    },
    # kept under EDITS, not NOTES: the notes-appender only creates rows, it never updates them,
    # so a note that names a retired action would otherwise go stale unnoticed.
    "Note - Projectile vs Laser": {
        1: "Delivery is told apart by WHERE the hitbox spawns and whether it TRAVELS - not by "
           "shape. There are three modes.",
        2: "PROJECTILE: spawns on the unit and TRAVELS to the target - it has a projectile speed "
           "(Homing / First hit / Pierce / Burst). LASER: spawns on the unit, NO travel - it just "
           "extends toward the target (Standard Laser / Laser Shot / Current Target Laser). SPAWN "
           "AT TARGET: spawns on the TARGET, no travel at all - nothing crosses the gap, so "
           "nothing in between can be touched (Taliyah's active). This is why Jhin is a Pierce "
           "Projectile and not a laser (his shot travels), and why Irelia's frontal hit IS a Laser "
           "Shot (it does not travel - it just appears in front of her, pierces, and lands once).",
    },
}

COLUMN_EXPLAIN_NOTES = [
    ["Note - Projectile vs Laser",
     "The two are told apart by TRAVEL SPEED, not by shape.",
     "PROJECTILE: fired from the unit and travels to the target - it has a projectile speed "
     "(Homing / First hit / Pierce / Burst). LASER: no travel speed at all - it spawns on top of "
     "the unit and points at the target (Standard Laser / Laser Shot / Current Target Laser). "
     "Box AOE is laser-like by this rule: no travel, spawns on the unit, but its hitbox is a "
     "rectangle rather than a beam."],
    ["Note - Auto-Attack",
     "Auto-Attack is itself a homing projectile.",
     "It is fired at the aim target and always lands on it — the same behaviour as Homing "
     "Projectile, which is why its Collision is Target-Only. It is kept as a separate Action only "
     "because it is the unit's default attack rather than an ability."],
    ["Note - Karma",
     "Her 3rd cast fires 3 projectiles, and they do NOT all go to the current target.",
     "One at the current target, one at the enemy to its LEFT, one at the enemy to its RIGHT - "
     "spreading them is what keeps the triple-cast from being overpowered. All 3 share a single "
     "hitbox, so a target already hit is not damaged again."],
]


# --------------------------------------------------------------------------- Hero tab
def fix_hero(sh):
    ws = sh.worksheet("Hero")
    vals = ws.get_all_values()
    c = cols(vals[0])          # resolve columns off the header, never by hard-coded index
    width = len(vals[0])

    def at(name, row):
        return f"{col_letter(c[name])}{row}"

    def val(r, name):
        return r[c[name]] if c[name] < len(r) else ""

    # 1. Irelia's second hitbox - a Laser Shot in front of her, alongside the Circle AOE on her.
    irelia = find_row(vals, c["Champion"], "Irelia")
    jhin = next(i for i in range(irelia + 1, len(vals)) if val(vals[i], "Champion").strip())
    if not any(val(vals[i], "Step").strip() == "4" for i in range(irelia, jhin)):
        sh.batch_update({"requests": [{"insertDimension": {
            "range": {"sheetId": ws.id, "dimension": "ROWS",
                      "startIndex": jhin, "endIndex": jhin + 1},
            "inheritFromBefore": True,
        }}]})
        cells = {
            "Step": "4", "Skill Type": "Active", "Trigger": "On Shield Expire", "Condition": D,
            "Action": "Laser Shot", "Collision": "Pierce-All", "Aim Target": "Current",
            "Effect Recipient": "Enemies in path", "Effect Category": "Attack",
            "Effect Detail": "Damage", "Amount": "70/100/150% AP",
            "Scaling": "+30% of damage absorbed", "Cadence": "Once",
            "Duration": D, "AOE": D, "Cast": D,
        }
        # Both of these columns were added to Hero after this pass was written, so guard on the
        # header rather than assuming: an older sheet must still take the insert.
        if "Action Source" in c:
            cells["Action Source"] = "Self"
        if "Count" in c:
            cells["Count"], cells["Spread"] = COUNT_DEFAULT, SPREAD_DEFAULT
        row = [""] * width
        for name, v in cells.items():
            row[c[name]] = v
        ws.update([row], f"A{jhin + 1}:{col_letter(width - 1)}{jhin + 1}",
                  value_input_option="RAW")
        print(f"Hero: inserted Irelia's second-hitbox step at row {jhin + 1}")
        vals = ws.get_all_values()
    else:
        print("Hero: Irelia's second-hitbox step already present")

    # 2. Galio's Aim Target holds a stray hyphen instead of Self - fix before the sweep below,
    #    or his two rows never register as "recipient == aim".
    edits = []
    galio = find_row(vals, c["Champion"], "Galio")
    if galio is not None and val(vals[galio], "Aim Target").strip() in ("-", ""):
        vals[galio][c["Aim Target"]] = "Self"
        edits.append({"range": at("Aim Target", galio + 1), "values": [["Self"]]})

    # Aim Target carried down through each action's merged block.
    aims, cur = [], ""
    for r in vals:
        if val(r, "Step").strip():
            cur = val(r, "Aim Target")
        aims.append(cur)

    champ = ""
    for i, r in enumerate(vals):
        if i == 0:
            continue
        if val(r, "Champion").strip():
            champ = val(r, "Champion").strip()
        n = i + 1
        action, coll = val(r, "Action"), val(r, "Collision")

        # Wave is gone - it was a duplicate of Pierce Projectile.
        # Jhin's shot has travel speed, so it is a projectile, not a laser. (Irelia's frontal hit
        # genuinely IS a Laser Shot, so this cannot be a blanket rule on the action name.)
        if action == "Wave" or (champ == "Jhin" and action == "Laser Shot"):
            edits.append({"range": at("Action", n), "values": [["Pierce Projectile"]]})

        # Retired actions: Box AOE (= a Laser Shot) and Summon Attack (= Source=Summon + an
        # ordinary Auto-Attack, now that Action Source exists to carry the source).
        if action in RETIRED_ACTIONS:
            edits.append({"range": at("Action", n),
                          "values": [[RETIRED_ACTIONS[action]]]})
        if val(r, "Effect Recipient") == "Enemies in box":
            edits.append({"range": at("Effect Recipient", n),
                          "values": [["Enemies in path"]]})

        # A melee Cast projects no hitbox - it has no collision.
        if action == "Cast" and coll not in ("None", D, ""):
            edits.append({"range": at("Collision", n), "values": [["None"]]})

        # Yasuo's dash, slash and slam all return to the enemy his Step 2 whirlwind picked.
        if champ == "Yasuo" and val(r, "Step").strip() in ("3", "4", "5"):
            if val(r, "Aim Target") != "Step 2 Aim target":
                edits.append({"range": at("Aim Target", n),
                              "values": [["Step 2 Aim target"]]})
            aims[i] = "Step 2 Aim target"

        # Zed's shadow is a summon, not a reposition.
        if val(r, "Effect Detail") == "(summon)" and val(r, "Effect Category") != "Summon":
            edits.append({"range": at("Effect Category", n), "values": [["Summon"]]})

        # The returning projectile collides with the caster - that IS a collision, unlike a
        # self-cast which projects nothing.
        if action == "Receive Projectile" and coll != "Self":
            edits.append({"range": at("Collision", n), "values": [["Self"]]})

        # Collapse a recipient that only restates the aim.
        aim, rec = aims[i], val(r, "Effect Recipient").strip()
        same = ((aim == "Self" and rec == "Self")
                or (rec == "Aimed enemy"
                    and (aim.startswith("Current") or aim.startswith("Step ")))
                or (aim == "Lowest-HP Allies" and rec == "2 lowest-HP allies"))
        if same:
            edits.append({"range": at("Effect Recipient", n),
                          "values": [["Same to Aim Target"]]})

    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Hero: {len(edits)} cells updated")
    merge_champion_blocks(sh, ws)


def merge_champion_blocks(sh, ws):
    """Merge cols A-J down each champion's full row span.

    The identity block was only filled on the champion's first row, so Kayle's name covered
    her step 1 but not steps 2 and 3. Merging makes the block span every step she owns.
    """
    meta = sh.fetch_sheet_metadata({"includeGridData": False})
    sheet = next(s for s in meta["sheets"] if s["properties"]["sheetId"] == ws.id)
    if any(m["startColumnIndex"] < 10 for m in sheet.get("merges", [])):
        print("Hero: champion identity blocks already merged")
        return

    vals = ws.get_all_values()
    starts = [i for i, r in enumerate(vals) if i > 0 and r[0].strip()]
    bounds = list(zip(starts, starts[1:] + [len(vals)]))

    requests = [{"mergeCells": {
        "range": {"sheetId": ws.id, "startRowIndex": a, "endRowIndex": b,
                  "startColumnIndex": c, "endColumnIndex": c + 1},
        "mergeType": "MERGE_COLUMNS",
    }} for a, b in bounds if b - a > 1 for c in range(10)]
    sh.batch_update({"requests": requests})
    print(f"Hero: merged identity cols A-J across {len(bounds)} champion blocks "
          f"({len(requests)} merges)")


# --------------------------------------------------------------- reference tabs
def fix_effect_types(sh):
    ws = sh.worksheet("Effect Types")
    vals = ws.get_all_values()
    edits = []

    # The shadow is a Summon, not a Movement.
    for i, r in enumerate(vals):
        if r[1] == "(summon)" and r[0] != "Summon":
            edits.append({"range": f"A{i + 1}", "values": [["Summon"]]})
            edits.append({"range": f"C{i + 1}", "values": [[
                "Spawns a clone/summon that acts as a SECOND action source for the following "
                "step - its own action is centred on the clone, not on Self."]]})
    if edits:
        ws.batch_update(edits, value_input_option="RAW")

    # Katarina has used this term since before the Ionia pass with no definition.
    if not any(r[1] == "(setup / daggers)" for r in vals):
        ws.append_rows([["Movement", "(setup / daggers)",
                         "A setup step (Katarina throwing her daggers) with no direct combat "
                         "effect of its own; the damage comes from the step that follows."]],
                       value_input_option="RAW")
        print("Effect Types: defined Movement -> (setup / daggers)")
    print(f"Effect Types: {len(edits)} cells updated")


def fix_collision_types(sh):
    """Only ensures the Self collision row exists. The row TEXT is owned by tft-add-shurima.py."""
    ws = sh.worksheet("Collision Types")
    vals = ws.get_all_values()

    if find_row(vals, 0, "Self") is None:
        # goes before the trailing prose block, not after it
        cut = next(i for i, r in enumerate(vals) if i > 0 and not any(c.strip() for c in r))
        ws.insert_rows([SELF_COLLISION_ROW], row=cut + 1, value_input_option="RAW")
        vals = ws.get_all_values()
        print("Collision Types: added the Self row")

    # the continuation-row example may still name the deleted Wave action
    edits = [{"range": f"F{i + 1}",
              "values": [[r[5].replace("her Wave", "her Pierce Projectile")]]}
             for i, r in enumerate(vals) if "Wave" in r[5]]
    if edits:
        ws.batch_update(edits, value_input_option="RAW")
    print(f"Collision Types: {len(edits)} cells updated")


def fix_column_explain(sh):
    ws = sh.worksheet("Column Explain")
    vals = ws.get_all_values()
    edits = []
    for label, cols in COLUMN_EXPLAIN_EDITS.items():
        i = find_row(vals, 0, label)
        if i is None:
            raise SystemExit(f"Column Explain: row '{label}' not found")
        for c, text in cols.items():
            if vals[i][c] != text:
                edits.append({"range": f"{col_letter(c)}{i + 1}", "values": [[text]]})
    ws.batch_update(edits, value_input_option="RAW")

    seen = {r[0].strip() for r in vals if r}
    notes = [n for n in COLUMN_EXPLAIN_NOTES if n[0] not in seen]
    if notes:
        ws.append_rows(notes, value_input_option="RAW")
    print(f"Column Explain: {len(edits)} cells updated, {len(notes)} note rows appended")


# ------------------------------------------------------------------ comment replies
REPLIES = [
    # NOTE: matching is "first key found in the comment text", so the LONGER key must come first -
    # "No need to mention" is a prefix of "No need to mention obvious thing".
    ("No need to mention obvious thing",
     "Removed. 'Sunder' is just TFT's name for Debuff -> DEF, which the Effect Types row already "
     "says - restating it in Scaling added nothing. Scaling is now an em-dash."),
    ("No need to mention",
     "Removed. 'Empowered Attack' is already defined in Effect Types as 'the recipient's NEXT "
     "attack deals bonus damage', so spelling it out again in Scaling was redundant. Scaling is "
     "now an em-dash."),
    ("It's time for creating the action template",
     "Agreed, and your Ashe decomposition is exactly right - it is already latent in the data. "
     "Multiplicity is currently smuggled into the Scaling column as prose in FOUR places: Ashe "
     "'×8 arrows in a cone', Akshan '×6 shots', Karma '×3 bursts', Azir 'all 3 Soldiers strike at "
     "once'. That is the same failure mode Action Source had before it earned a column: a real, "
     "recurring axis leaking into free text because there was nowhere structured to put it. So it "
     "is not bad - it is overdue.\n\n"
     "Built in TWO NEW TABS so nothing that works can break:\n"
     "- 'Action Templates': every Action decomposed into Delivery × Collision × Shape. This is "
     "where your two earlier observations land as structure - Burst Projectile = First hit "
     "Projectile + Circle AOE, and Circle AOE has the SAME delivery as Spawn At Target and differs "
     "only in shape.\n"
     "- 'Hero (template)': a copy of Hero plus Count and Spread columns. Ashe = First hit "
     "Projectile, Count 8, Spread Cone. Akshan = Count 6, Same target. Karma = Count 3, Current + "
     "Left + Right (your note about why it spreads is now the definition of that spread). Azir = "
     "Count 3.\n\n"
     "Ahri: your description changed her encoding. A 360° radial wave from her, hitbox big enough "
     "to reach everyone, is NOT aimed at the current target - so she is now Aim = Self, Spread = "
     "360° radial, Recipient = All enemies. I had her aimed at Current, which was wrong.\n\n"
     "Hero is untouched. If the template model proves out, it becomes the canonical tab."),
    ("This is 2 hex",
     "Fixed - 2 hexes, on both rows of that action (the damage and the Chill). I had guessed 1 "
     "from 'nearby enemies'; the source text gives no number, so thanks for the real value."),
    ("The circle AOE spawn at summon's hex",
     "Yes - and this is a correction to my reasoning, not just to the cell. I had written 'Self' "
     "meaning 'self AS SEEN BY the summon' - i.e. relative to the Action Source. That implicit "
     "reading is exactly what this schema exists to stamp out. Aim Target is now ABSOLUTE: 'Self' "
     "always means the champion, so the shadow's AOE is aimed at 'Summon'. Written into Column "
     "Explain as a rule. Zed's steps 3 and 4 now read Self/Self and Summon/Summon - the two "
     "columns still say different things (Source = who acts, Aim = where it lands); for Zed they "
     "coincide, for Azir they do not."),
    ("I thought it weird to state the action here",
     "Done. Yasuo's melee slash (Cast) now has Collision = None, and the same defect is fixed on "
     "Darius' two Cast rows. Rule written into Column Explain: only an action that PROJECTS a "
     "hitbox into the world has a collision. Kayle's Auto-Attack keeps Target-Only on purpose - "
     "she is range 4, so her attack really is a projectile."),
    ("This should be \"Step 2 Aim target\"",
     "Done - Yasuo's steps 3, 4 and 5 now all read 'Step 2 Aim target'. Added as a documented Aim "
     "Target value in Column Explain: re-aims at whatever an earlier step aimed at."),
    ("If the aim target and effect recipient are the same",
     "Done, and applied across all 22 champions rather than just Ionia - 35 rows now read 'Same to "
     "Aim Target' (Kled, Swain, Sion, Poppy, Lux, Cassiopeia, Samira, Darius, Galio and every "
     "Ionia bonus row). The Effect Recipient cell now only ever carries NEW information. "
     "Convention written into Column Explain."),
    ("Pierce Projectile and Wave are exactly the same",
     "Yes - checked all 5 Wave rows (Kayle x2, Sona, Yasuo, Ahri) and every one travels outward "
     "from the unit and pierces everything in its path. Wave is deleted from Action Types and all "
     "5 rows now read Pierce Projectile."),
    ("This is just flag, no need for changed",
     "Understood - no cell changed. Recorded as 'Note - Karma' in Column Explain: the 3rd cast "
     "fires one projectile at the current target, one at the enemy to its LEFT and one at the "
     "enemy to its RIGHT (spreading them is what stops the triple-cast being overpowered), and "
     "all 3 share a single hitbox so an already-hit target is not damaged twice."),
    ("This should be summon too",
     "Done - 'Summon' is now its own Effect Category (previously mislabelled Movement), defined in "
     "Effect Types."),
    ("This is good candidate to explain the difference",
     "Done. Jhin is now 'Pierce Projectile' - a projectile with travel speed that pierces. Your "
     "rule is written into every projectile/laser row in Action Types and into a 'Note - Projectile "
     "vs Laser' row: PROJECTILE = fired from the unit, HAS travel speed; LASER = no travel speed, "
     "spawns on top of the unit and points at the target."),
    ("This skill have 2 hitbox",
     "Agreed on your follow-up - Box AOE is gone, Irelia's frontal hit is now 'Laser Shot'. By "
     "your own rule it was a laser all along: no travel speed, spawns on the unit, pierces, lands "
     "once - so a separate action was redundant. Irelia keeps both hitboxes as two steps firing On "
     "Shield Expire: step 3 Circle AOE (Area, enemies around her) and step 4 Laser Shot "
     "(Pierce-All, enemies in path in front of her), both for 70/100/150% AP + 30% of damage "
     "absorbed. Laser Shot is no longer taxonomy-only - Irelia is its user, and Jhin is the one "
     "who moved OFF it to Pierce Projectile."),
    ("Every hero didn't cover their own step cell properly",
     "Done - the identity block (Champion .. Skill Description, cols A-J) is now MERGED vertically "
     "across every row the champion owns, so Kayle's block spans steps 1, 2 and 3 instead of only "
     "step 1. Applied to all 22 champions. Convention recorded in Column Explain."),
    ("This should be Self",
     "Good catch, and you are right - this is not the same as None. Poppy's shield IS projected "
     "into the world and collides with her on the way back, so Collision = Self. Changed, and "
     "'Self' is now its own row in Collision Types: something WAS projected and the unit it hits "
     "is the caster. None stays reserved for actions that project nothing at all (a self-cast, a "
     "leap)."),
    ("This skill isn't Homing Projectile",
     "You're right, and it completes the rule rather than breaking it. Nothing travels and nothing "
     "is fired - the hitbox just appears on her target's hex. That is neither a projectile (spawns "
     "on the unit, travels) nor a laser (spawns on the unit, no travel), so it is a THIRD delivery "
     "mode, told apart by where the hitbox SPAWNS: on the target. I named it 'Spawn At Target' - "
     "it isolates exactly what is different (the spawn location), where 'Instant Hitbox' would not "
     "(a laser is instant too). Collision = Target-Only, because nothing crosses the gap so nothing "
     "in between can be touched. Taliyah's active is now Spawn At Target; her passive boulder stays "
     "a First hit Projectile, since that one really is thrown. Note - Projectile vs Laser is now a "
     "three-way rule."),
    ("Nice to note that, Auto-Attack is also a homing projectile",
     "Done - recorded as 'Note - Auto-Attack' in Column Explain, and stated on the Auto-Attack row "
     "itself in Action Types: it IS a homing projectile (fired at the aim target, always lands on "
     "it - hence Collision = Target-Only), and it is kept as a separate Action only because it is "
     "the unit's default attack rather than an ability."),
    ("There is a bunch of mess here too",
     "Fair - that column had become a dumping ground. Action Types is now 5 columns, matching the "
     "Column Explain layout: 'What it does' is one clean sentence per action, and every caveat, "
     "rule and example moved to a new 'Clarify more' column (travel-speed rule, taxonomy-only "
     "markers, per-champion examples). Your note on Burst Projectile about action templates is "
     "kept verbatim, now in Clarify more."),
    ("This are wrong. He run into enemy",
     "Already in place - this cell reads 'Charge Into' (Pierce-All, recipient = Enemies in path), "
     "so Sion stuns everyone he collides with on the way rather than an AOE on landing. This "
     "comment is the request that created that action. No change needed."),
]


def main():
    sh = open_sheet()
    fix_hero(sh)
    fix_effect_types(sh)
    fix_collision_types(sh)
    fix_column_explain(sh)
    # The 'Dedicate new tab to it' comment is answered by tft-action-templates.py, which owns the
    # Spread Types tab - hence warn_unmatched=False.
    post_replies(REPLIES, warn_unmatched=False)


if __name__ == "__main__":
    main()
