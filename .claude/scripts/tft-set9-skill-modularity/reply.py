"""Reply to the sheet's review comments. Holds the CURRENT round's replies, and nothing else.

Run from repo-root cwd:  python .claude/scripts/tft-set9-skill-modularity/reply.py

Overwrite REPLIES each round; git keeps the history. Comments are left UNRESOLVED — resolving them is
the user's call, always. A MATCH KEY IS A SUBSTRING OF THE COMMENT'S ROOT and fails SILENTLY, so keep
keys long, distinctive, and never a prefix of another.
"""

from sheet import post_replies

# --- Round: remaining-11 roster review (Nilah / Aatrox / Qiyana / Jinx / Spread naming) ---

SPREAD_NAME = (
    "Good catch — Jinx's 'Each to its own target' isn't a spatial spread at all; it's a per-instance "
    "TARGET re-pick (each rocket re-rolls a random enemy). The column really covers two ideas: spatial "
    "layout (Cone, 360° radial, Diagonal) AND target distribution (Split across nearest N, Each to its "
    "own target). If you want, I'd rename the column to 'Targeting' or 'Distribution', which fits both "
    "senses. I left the header as 'Spread' for now — say the word and I'll rename it across the sheet.")

NILAH_AOE = "Done — cleared that AOE cell on Nilah's cone auto (it's back to '—')."

NILAH_LASER = (
    "Done — Nilah's every-3rd-attack line is now the 'Laser Shot' action (Pierce-All), not Pierce "
    "Projectile.")

NILAH_LUMP = (
    "Done — the shield (Cast) and the dash (Leap) now share one step, both triggered 'On Cast', so it "
    "reads 'On Cast => Cast and Leap'.")

AATROX_AS = (
    "Captured — added a Self 'Debuff / Attack Speed' row ('all bonus AS removed') alongside the AD "
    "buff, so the sheet shows the bonus AS is consumed by the conversion, not kept.")

AATROX_MELEE = (
    "Reworked — added a new 'Melee AOE' action (a hitbox centred ON the caster, not the aim target) "
    "and gave Aatrox's transformed attack three looping instances of it: 1st a 1×2 box, 2nd a "
    "Gwen-shaped cone, 3rd a 1-hex circle. The AOE (hex) column carries each shape; the Condition "
    "column carries the 1st/2nd/3rd loop position. Registered Melee AOE in the Action Model tab.")

QIYANA = (
    "Remodelled — Qiyana now Leaps THROUGH the current target (step 1), then step 2 sends a wave "
    "modelled as a Pierce Projectile that passes through everyone in the line, dealing the damage and "
    "knocking up (Stun: 1.5s on the first target hit, 0.5s on the rest). Dropped 'Charge Into'.")

JINX = (
    "Done — Jinx's 5 rockets are now 'Homing Projectile' (they seek their random targets). I left "
    "Urgot's leg-blast as 'Burst Projectile' since it fires in a fixed direction rather than homing — "
    "tell me if you want that changed too.")

QIYANA_LEAPBEHIND = (
    "Done — Qiyana's step 1 is now 'Leap Behind' (she rips through and ends up behind the target).")

QIYANA_COND = (
    "Fixed — dropped 'First target hit' / 'Other targets' from the Condition column. The two Stun rows "
    "now differ only by Effect Recipient (First hit enemy vs Enemies in path) and Duration (1.5s vs "
    "0.5s), so Condition is free to mean an ACTION gate, as you said.")

AOE_TAXONOMY = (
    "Implemented (per our walk-through). AOE actions are now shape TEMPLATES — Circle AOE / Cone AOE / "
    "Box AOE / Custom AOE — reused across heroes; 'Melee AOE' is gone. The caster-vs-target centre is "
    "DERIVED from Action Source + Aim Target (Aim=Self → on the source, incl. a summon; else on the "
    "target), so no Melee/Range naming is needed. Added a new 'Offset' column (an anchor label: "
    "centred / rear edge / front edge / detached +N; '—' for non-AOE) — e.g. Aatrox's box is 'rear "
    "edge', Kassadin's cone 'front edge'. Shape size stays in AOE (hex); odd shapes (MF's X) use "
    "Custom AOE. Migrated every instant/spawned AOE user; projectiles + lasers left untouched.")

V2_MOVE = "Done — moved the axes explanation below the table (doc-block style, like the other tabs)."

V2_ASSESS = (
    "Deleted Burst + Homing Burst Projectile — they're just First-Hit/Homing + Circle now. On "
    "'finished?': the action PRIMITIVE is complete, and Collision is now DERIVED from "
    "Delivery+Behavior+Shape, so it stops being a column. What is NOT here (stays per-row in Hero, not "
    "part of an action's definition): Count, Spread, Aim Target, Action Source, Skill Range. On 'Hero "
    "v2 — really similar?': yes, mostly — same champion-centric layout; the only real change is the "
    "single 'Action' column exploding into ~5 (Apply/Delivery/Behavior/Shape/Motion) and Collision "
    "dropping out. Wider, but more modular. See my note for a side-by-side; migrating Hero is a real "
    "cost/benefit call, not a must.")

DASHBOARD_DITCH = (
    "Done — ditched it for now: deleted the Dashboard tab and un-wired it from sync. Kept dashboard.py "
    "(and the 'Columns used' profiles it reads) parked in the tooling, so we can switch it back on any "
    "time by calling dashboard.generate(sh) in sync's main().")

COLUMN_PROFILES = (
    "Built it — both parts. (1) Each Action now declares a 'Columns used' profile in the Action Model "
    "tab: e.g. Circle AOE → Aim Target, Offset, AOE, Collision, Skill Range; Homing Projectile → "
    "Count, Spread, Collision (no AOE/Offset); Leap → Aim Target, Offset. (2) A new generated, "
    "read-only 'Dashboard' tab shows each champion's full kit, and each action's Targeting cell shows "
    "ONLY the columns its profile declares — so the '—' clutter is gone. The champion-centric Hero "
    "stays the source you edit; the Dashboard is derived from it and regenerates every sync "
    "(idempotent). I went with the dashboard-only option you picked; per-type tabs can come later off "
    "the same profiles.")

ACTION_GROUPING = (
    "Done — grouped the Action Model rows by delivery family (adjacency only, no header rows; the doc "
    "block stays at the bottom): Basic attack (Auto-Attack, QuickAA) · Projectile (Homing, First hit, "
    "Pierce, Burst, Homing Burst, Receive) · AOE (Spawn At Target, Circle, Cone, Box, Custom) · Laser "
    "(Laser Shot, Sweep, Standard, Current Target) · Movement/body (Charge Into, Knock Back, Grab & "
    "Slam, Leap, Leap Behind) · Other (Cast, Summon).")

COLUMN_ORDER = (
    "Done — regrouped the columns for readability. The action region now reads: Action Source | "
    "Action | Aim Target | Offset | AOE (hex) | Skill Range | Count | Spread | Collision, then the "
    "effect block, then Cast. Applied on the sheet and in the source CSV + tooling (the merge logic no "
    "longer assumes AOE/Offset are the rightmost columns). sync converges to 0 cells with VALIDATE ok.")


# LONGEST / MOST DISTINCTIVE KEY FIRST. Each is a substring of exactly one open comment root.
REPLIES = [
    ("Do we have a better", SPREAD_NAME),   # NB: reviewer's text has a non-breaking space before 'name'
    ("Get rid of this one", NILAH_AOE),
    ("For nilah, it is Laser shot", NILAH_LASER),
    ("Lump this into", NILAH_LUMP),
    ("AS are converted", AATROX_AS),
    ("I should name it", AATROX_MELEE),
    ("leap through her target", QIYANA),
    ("Homing Projectile.", JINX),
    ("Use Leap behind", QIYANA_LEAPBEHIND),
    ("condition for the action", QIYANA_COND),
    ("should also have Range AOE", AOE_TAXONOMY),
    ("I want column to have this format", COLUMN_ORDER),
    ("group those action together", ACTION_GROUPING),
    ("define which column each Action", COLUMN_PROFILES),
    ("ditch it for now", DASHBOARD_DITCH),
    ("Move the explanation below", V2_MOVE),
    ("Now deleting Burst Projectile", V2_ASSESS),
]


if __name__ == "__main__":
    # warn off: comment [5] (the Melee/Range AOE taxonomy discussion) is being handled with the user
    # directly, not via a scripted reply.
    post_replies(REPLIES, warn_unmatched=False)
