"""Build `Action Model` - the merge of `Action Types` and `Action Templates` into ONE tab.

Run from repo-root cwd:  python .claude/scripts/tft-action-model.py

WHY
---
The user asked: "What is the difference between Action Template and Action Types?" - and the
honest answer is: not enough to justify two tabs.

  Action Types      = Action | Collision | Cadence | What it does | Clarify more
  Action Templates  = Action | Delivery | Collision | Shape | Cadence | Notes

They agree on Action, Collision and Cadence, and disagree on nothing - Templates is simply the
more precise of the two, because it splits the Action into Delivery x Shape. Two tabs describing
the same 18 actions is how they drift apart, and then nobody knows which one is true.

So: ONE tab, `Action Model`, with the union of their columns. Built as a NEW tab and the two
originals are left untouched - the user's call, "merge them as a new tab, preventing accident".
That is the same play as `Hero (template)`: prove it, then promote it and delete the old ones.

  Action | Delivery | Collision | Shape | Cadence | What it does | Clarify more

WHAT CHANGED IN THE MODEL ITSELF
--------------------------------
Two actions were WRONG, and the user caught both:

  * `Cone Slash` (Gwen) is retired. Her cone is not a cone-shaped hitbox at all - it is a LASER
    that SWEEPS through an arc, and only looks like a cone. Replaced by `Sweep Laser`.
  * `Cast` (Viego) is retired for him - his is a `Laser Shot`.

`Sweep Laser` exposes a gap this schema cannot yet state: the hitbox MOVES while the action runs.
Delivery says where a hitbox spawns; Shape says what it is; neither says that it sweeps. It is
carried in the Shape text for now - flagged in the tab, and worth its own column if a second
swept action ever turns up.
"""

from tft_sheet import col_letter, open_sheet, post_replies

MODEL_TAB = "Action Model"

# Action | Delivery | Collision | Shape | Cadence | What it does | Clarify more
# Delivery answers WHERE THE HITBOX SPAWNS and WHETHER IT TRAVELS. Shape answers WHAT IT IS.
ACTIONS = [
    ["Auto-Attack", "Projectile (spawns on unit, travels)", "Target-Only", "Single", "Not specify",
     "Basic attack on the aimed enemy.",
     "Mechanically this IS a homing projectile - fired at the aim target and always landing on it, "
     "which is why its Collision is Target-Only. It is kept as its own Action only because it is "
     "the unit's default attack rather than an ability. NOT always performed by the champion: read "
     "the Action Source column. Azir's Sand Soldier auto-attacks (Source = Summon), and Sejuani's "
     "passive rides on an ALLY's auto-attack (Source = Ally)."],
    ["Homing Projectile", "Projectile (spawns on unit, travels)", "Target-Only", "Single",
     "Not specify",
     "Fires a projectile that homes on the aim target and applies its effect to it.",
     "Has travel speed. Nothing on the way is touched - the projectile tracks the target until it "
     "lands (Poppy, Cassiopeia, Samira). Kalista's 6 spears are 6 of these at one target."],
    ["First hit Projectile", "Projectile (spawns on unit, travels)", "First-Hit", "Single",
     "Not specify",
     "Fires a projectile that stops on the FIRST unit it hits.",
     "Has travel speed. The first unit it collides with may NOT be the unit aimed at - that is the "
     "whole point: Taliyah's boulder is thrown toward a knocked-up enemy but hits whatever it "
     "meets first, and each of Akshan's 6 shots lands on the first body in its lane."],
    ["Pierce Projectile", "Projectile (spawns on unit, travels)", "Pierce-All", "Line",
     "Not specify",
     "Fires a projectile that passes THROUGH every unit in its path, hitting all of them.",
     "Has travel speed. Recipients can be enemies or allies - Sona's damages enemies AND buffs "
     "allies in the same path. Replaced the old 'Wave', which was a duplicate of it."],
    ["Burst Projectile", "Projectile (spawns on unit, travels)", "First-Hit", "Circle",
     "Not specify",
     "Projectile that flies at the aim target and DETONATES on impact, hitting everyone in an "
     "X-hex circle.",
     "Has travel speed. = First hit Projectile + Circle AOE. It detonates on the FIRST body it "
     "meets, which may not be the unit it was aimed at, and the circle is centred on that IMPACT "
     "hex. If the projectile instead passes THROUGH and detonates on its aim target, that is "
     "Homing Burst (Aphelios), not this."],
    ["Homing Burst", "Projectile (spawns on unit, travels)", "Area", "Circle", "Not specify",
     "Projectile that HOMES on the aim target, passing through everything on the way, and "
     "detonates on it in an X-hex circle.",
     "Has travel speed. = Homing Projectile + Circle AOE. Do NOT confuse with Burst Projectile, "
     "which is First-Hit: that one detonates on the FIRST body it meets, which may not be the unit "
     "it was aimed at. Aphelios' moon blast passes THROUGH heroes and explodes on the clustered "
     "target it was aimed at - the user's correction. Same circle, different delivery."],
    ["Spawn At Target", "Spawn At Target (spawns on target, no travel)", "Target-Only", "Single",
     "Not specify",
     "The hitbox appears directly ON the aim target's hex - nothing is fired and nothing travels.",
     "The third delivery mode. Nothing crosses the gap, so nothing in between can be touched "
     "(Taliyah's active; Soraka's 5 falling stars)."],
    ["Circle AOE", "Spawn At Target (spawns on target, no travel)", "Area", "Circle",
     "Not specify",
     "Affects everyone inside an X-hex circle (X = the AOE (hex) column).",
     "SAME delivery as Spawn At Target - it differs only in SHAPE. The circle is centred on the "
     "AIM TARGET's hex: that is Self for a self-centred spin (Garen, Galio), but the current "
     "target's hex for Karma, Ahri and Yasuo's slam."],
    ["Laser Shot", "Laser (spawns on unit, no travel)", "Pierce-All", "Line", "Once",
     "Beam that pierces ALL units in the path but applies its effect ONCE.",
     "NO travel speed - it spawns on the unit and points at the target. Irelia's frontal hit, "
     "Senna's board-wide beam, and Viego's strike are all this."],
    ["Sweep Laser", "Laser (spawns on unit, no travel)", "Pierce-All",
     "Line — SWEPT through an arc", "Once",
     "A laser that SWEEPS sideways through an arc while it is out, hitting everything the moving "
     "beam passes over.",
     "Gwen. The cone she appears to make is NOT a cone hitbox - it is this line sweeping, and it "
     "only LOOKS like a cone. This is the first action whose hitbox MOVES during the action: "
     "Delivery says where a hitbox spawns and Shape says what it is, but neither can say that it "
     "travels sideways. Carried in the Shape text for now; it deserves its own column if a second "
     "swept action ever appears. Replaced 'Cone Slash', which wrongly modelled the cone as a real "
     "collider."],
    ["Standard Laser", "Laser (spawns on unit, no travel)", "Pierce-All", "Line", "Over time",
     "Beam that pierces ALL units in the path and damages them continuously until it ends.",
     "NO travel speed. Taxonomy only - no Set 9 unit here uses it."],
    ["Current Target Laser", "Laser (spawns on unit, no travel)", "Target-Only", "Single",
     "Over time",
     "Beam locked onto the aimed target ONLY, applying its effect over a duration.",
     "NO travel speed. Nothing between the unit and the target is touched (Lux)."],
    ["Charge Into", "Self body (travels)", "Pierce-All", "Line", "Once",
     "Self CHARGES to the target hex, colliding with every unit in the path, and stops there.",
     "The CASTER's own body is the hitbox. Not an AOE - the units hit are exactly the ones it ran "
     "through (Sion)."],
    ["Knock Back", "Thrown body (travels)", "Pierce-All", "Line", "Once",
     "Self smashes the aimed enemy across the board.",
     "The FLYING ENEMY is the hitbox: everyone it collides with on the way is hit as well. Not a "
     "projectile the caster fired - the thrown body IS the projectile (K'Sante)."],
    ["Grab & Slam", "None (no hitbox projected)", "Flank-Pair", "Pair", "Once",
     "Self grabs one enemy from EACH side and slams them together.",
     "The effect applies only to the grabbed enemies. If only one side is occupied then only one "
     "is grabbed - and the effect is amplified by 50% (Sett)."],
    ["Receive Projectile", "Returning projectile (travels back)", "Self", "Single", "Not specify",
     "Waits for a previously thrown projectile to RETURN to the caster, then applies its effect "
     "to self.",
     "Collision is Self, NOT None: something IS flying back and the unit it collides with is the "
     "caster (Poppy's shield)."],
    ["Cast", "None (no hitbox projected)", "None", "—", "Not specify",
     "Self plays an animation, then applies the stated effect or sets up the step that follows.",
     "Projects no hitbox into the world, so its Collision is ALWAYS None - even when it is a melee "
     "strike on a target (Darius, Yasuo). Who it lands on is carried by Aim Target and Effect "
     "Recipient, not by the collision. Beware: a 'melee strike' is not automatically a Cast - "
     "Viego looked like one and is actually a Laser Shot."],
    ["Leap", "None (no hitbox projected)", "None", "—", "Not specify",
     "Self leaps to the target hex - a reposition.",
     "Projects nothing, so Collision is None. Normally just sets up the follow-up action that does "
     "the damage (Jarvan's and Katarina's landing AOE; Gwen's dash before her sweep)."],
    ["Summon", "None (no hitbox projected)", "None", "—", "Not specify",
     "Self spawns a unit (a clone, a soldier) at a target hex.",
     "The spawned unit becomes a SECOND action source for the steps that follow - it acts on its "
     "own, and its action is centred on IT, not on Self. Zed's Shadow and Azir's Sand Soldier."],
]

HEADER = ["Action", "Delivery (where it spawns / does it travel)", "Collision", "Shape",
          "Cadence", "What it does", "Clarify more"]

PROSE = [
    "How to read this tab",
    "This tab REPLACES 'Action Types' and 'Action Templates', which described the same 18 actions "
    "in two places and disagreed on nothing - one was just less precise. Both are left in the "
    "sheet untouched until this one is signed off; then they go.",
    "An Action is not a primitive - it is a COMPOSITION: Delivery x Collision x Shape. That is why "
    "Burst Projectile = First hit Projectile + Circle AOE, and why Circle AOE has the SAME "
    "delivery as Spawn At Target and differs only in shape.",
    "Count and Spread add a fourth axis - how MANY instances fire and how they are arranged. Those "
    "are columns in the Hero tab, and their values are defined in 'Spread Types'.",
    "KNOWN GAP: nothing here can say that a hitbox MOVES while the action runs. Sweep Laser (Gwen) "
    "is the only case so far and carries it in the Shape text. A second swept action should turn "
    "that into a real column rather than prose.",
]

REPLIES = [
    ("What is the difference between Action Template and Action Types",
     "Not enough to justify two tabs - you are right to push on it.\n\n"
     "  Action Types     = Action | Collision | Cadence | What it does | Clarify more\n"
     "  Action Templates = Action | Delivery | Collision | Shape | Cadence | Notes\n\n"
     "They agree on Action, Collision and Cadence and contradict each other on nothing. Templates "
     "is simply the more precise of the two, because it splits the Action into Delivery x Shape. "
     "Two tabs describing the same 18 actions is exactly how they drift apart, and then nobody "
     "knows which is true.\n\n"
     "Merged into a new 'Action Model' tab with the union of the columns:\n"
     "Action | Delivery | Collision | Shape | Cadence | What it does | Clarify more\n\n"
     "Both old tabs are left in place untouched, as you asked - same play as Hero (template): "
     "prove it, then promote it and delete the old two."),
]


def build(sh):
    ws = next((w for w in sh.worksheets() if w.title == MODEL_TAB), None)
    if ws is None:
        ws = sh.add_worksheet(title=MODEL_TAB, rows=40, cols=len(HEADER))
        print(f"created the '{MODEL_TAB}' tab")

    rows = [HEADER] + ACTIONS + [[""] * len(HEADER)]
    rows += [[p] + [""] * (len(HEADER) - 1) for p in PROSE]

    if ws.row_count < len(rows):
        ws.add_rows(len(rows) - ws.row_count)
    if ws.col_count < len(HEADER):
        ws.add_cols(len(HEADER) - ws.col_count)

    last = col_letter(len(HEADER) - 1)
    ws.clear()
    ws.update(rows, f"A1:{last}{len(rows)}", value_input_option="RAW")
    ws.format(f"A1:{last}1", {"textFormat": {"bold": True},
                              "backgroundColor": {"red": 0.82, "green": 0.88, "blue": 0.82}})

    # prose rows span the tab; unmerge first or a re-run collides with the previous run's merges
    first_prose = len(ACTIONS) + 2
    requests = [{"unmergeCells": {"range": {"sheetId": ws.id}}}]
    requests += [{"mergeCells": {
        "range": {"sheetId": ws.id, "startRowIndex": i, "endRowIndex": i + 1,
                  "startColumnIndex": 0, "endColumnIndex": len(HEADER)},
        "mergeType": "MERGE_ROWS",
    }} for i in range(first_prose, len(rows))]
    requests += [{"repeatCell": {
        "range": {"sheetId": ws.id, "startRowIndex": 1, "endRowIndex": len(rows),
                  "startColumnIndex": 0, "endColumnIndex": len(HEADER)},
        "cell": {"userEnteredFormat": {"wrapStrategy": "WRAP", "verticalAlignment": "TOP"}},
        "fields": "userEnteredFormat(wrapStrategy,verticalAlignment)",
    }}]
    sh.batch_update({"requests": requests})
    print(f"{MODEL_TAB}: wrote {len(ACTIONS)} actions + {len(PROSE)} prose rows")


SUPERSEDED = ["Action Types", "Action Templates"]


def promote(sh):
    """Delete the two tabs `Action Model` replaced.

    The user signed off: "I already see the Action Model. Sound good, use this one from now on.
    Delete the old one." Both described the same 18 actions; leaving them would guarantee they
    drift out of step with the one that is now canonical.

    Refuses to delete unless Action Model is actually populated - deleting the old tabs while the
    new one is empty would destroy the taxonomy outright.
    """
    tabs = {w.title: w for w in sh.worksheets()}
    model = tabs.get(MODEL_TAB)
    if model is None or len(model.get_all_values()) < len(ACTIONS):
        raise SystemExit(f"REFUSING to delete: '{MODEL_TAB}' is missing or short — nothing dropped")

    for title in SUPERSEDED:
        if title in tabs:
            sh.del_worksheet(tabs[title])
            print(f"deleted the superseded '{title}' tab")


def main():
    sh = open_sheet()
    build(sh)
    promote(sh)
    post_replies(REPLIES, warn_unmatched=False)
    print(f"\n'{MODEL_TAB}' is the canonical action taxonomy — the two old tabs are gone.")


if __name__ == "__main__":
    main()
