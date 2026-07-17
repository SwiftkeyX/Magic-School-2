"""Reply to the sheet's review comments. Holds the CURRENT round's replies, and nothing else.

Run from repo-root cwd:  python .claude/scripts/tft-set9-skill-modularity/reply.py

Overwrite REPLIES each round; git keeps the history. Comments are left UNRESOLVED — resolving them is
the user's call, always. A MATCH KEY IS A SUBSTRING OF THE COMMENT'S ROOT and fails SILENTLY, so keep
keys long, distinctive, and never a prefix of another.

THIS ROUND IS CORRECTIONS. The three replies below were answered earlier today and then OVERTAKEN by
later decisions — a thread that describes a state which no longer exists is worse than no reply, since
the sheet is what gets read. post_replies is idempotent on BODY, so a correction must be a new body.
"""

from sheet import post_replies

# --- Round: corrections, after the Charge/geometry decisions landed ---

NAAFIRI = "\n".join([
    "CORRECTION to my reply above — the Move row is gone. You decided that a Charge MOVES its carrier, "
    "so step 3 is one row now, not two:",
    "",
    "  step 3  After Step 2   src 'Summon'",
    "          Charge [collision=Target-Only]   Aim 'Step 1 Aim target'",
    "             -> Damage 190/195/200% AD (total across all packmates)",
    "",
    "Ignore the 'Move' line in the reply above; it described a rule that no longer exists. Everything "
    "else in it still stands — the bracket is a real Action Model row, and Target-Only is the "
    "collision that means what you described.",
    "",
    "Two of its cells also changed with the geometry rule: Offset and AOE (hex) both read 'default' "
    "now, because the Charge action already fixes them (centred, 1-hex) and the row no longer repeats "
    "what the action owns.",
    "",
    "STILL OPEN, and I need a number from you: you asked for the 3 wolves to be modelled as 3. Her "
    "190/195/200% AD is the TOTAL across all packmates, so Count 3 needs either a per-wolf amount "
    "(~63.3/65/66.7% AD) or a new rule saying 'the Amount is the total, divide by Count'. I did not "
    "want to invent either.",
])

DELAY = "\n".join([
    "CORRECTION to my reply above — that question is settled, and this is what it landed on. You said "
    "keep the Amount, so the fuse now lives in exactly one cell:",
    "",
    "  step 1  Status / Delayed Blast   Amount 1.25   Effect Duration —",
    "  step 2  Circle AOE               Cast (s) —",
    "",
    "Ignore the 'say the word and I will' at the end of the reply above; it is done.",
    "",
    "Effect Types now says the AMOUNT IS THE FUSE, so the meaning travels with the value rather than "
    "living in this thread.",
])

SOURCE = "\n".join([
    "Still correct as replied — 'Delayed Blast' is the Action Source and nothing since has changed it.",
    "",
    "One addition worth knowing: the same instinct you had here ('name the thing that ACTS') is now "
    "written into the Design Notes tab, because it is a rule and not a one-off. Graves and Silco name "
    "'Step 1 Projectile'; Twisted Fate names 'Delayed Blast'. The victim never names itself — it is "
    "what the bomb is stuck to, not the thing that goes off.",
])

XAYAH_RECIPIENT = "\n".join([
    "Fixed — 'Enemies in path'. You are right, and that cell was contradicting her own action.",
    "",
    "'Gilgamesh Projectile' is Pierce-All: it touches EVERY unit along the path. 'Same to Aim Target' "
    "is what a Target-Only action says - it hits the one it aimed at and nothing else. So the row was "
    "denying the exact thing the action exists for, and the thing you described when you asked for it: "
    "'it could hit several enemy behind the target'.",
    "",
    "Her armour shred below it is UNCHANGED and still 'First hit enemy' - that one is right, because "
    "the source says each feather removes 6 Armor from the FIRST target IT hits. So her one action "
    "now has two recipients, and they genuinely differ:",
    "",
    "  Damage 80/80/100% AD + 15/25/60% AP  -> Enemies in path   (everyone the feathers pierce)",
    "  Debuff DEF 6                         -> First hit enemy   (only who each feather hits first)",
    "",
    "I CHECKED WHETHER THIS WAS SYSTEMIC. It is not - you found the only one. Five other rows look "
    "like it and are all correct, which is worth knowing because it is why I am NOT adding a checker "
    "for this:",
    "",
    "  Swain / Shen / Renekton   Circle AOE aimed at SELF, so 'Same to Aim Target' IS the caster -",
    "                            a self-buff riding on the AOE (your Swain-heal precedent).",
    "  Lissandra                 the Stun lands on the aimed target, the damage on the area.",
    "                            Two effects, two recipients, both right.",
    "  Nilah                     a self attack-speed buff on her laser row.",
    "",
    "The rule that separates them is subtle: a recipient may narrow to one unit when the effect RIDES "
    "ALONG (a buff, a status on the aim target), but not when it is the hitbox's own damage. A checker "
    "would have to tell those apart, and it would cry wolf five times to catch Xayah once.",
])

REPLIES = [
    ("Summon charge into target for Naafiri", NAAFIRI),
    ("I think put delay duration here is a good idea", DELAY),
    ("This is kinda confusing, use", SOURCE),
    ("Enemies in path For Xayah", XAYAH_RECIPIENT),
]

if __name__ == "__main__":
    post_replies(REPLIES, warn_unmatched=True)
