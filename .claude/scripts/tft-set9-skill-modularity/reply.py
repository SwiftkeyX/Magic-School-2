"""Reply to the sheet's review comments. Holds the CURRENT round's replies, and nothing else.

Run from repo-root cwd:  python .claude/scripts/tft-set9-skill-modularity/reply.py

Overwrite REPLIES each round; git keeps the history. Comments are left UNRESOLVED — resolving them is
the user's call, always. A MATCH KEY IS A SUBSTRING OF THE COMMENT'S ROOT and fails SILENTLY, so keep
keys long, distinctive, and never a prefix of another.
"""

from sheet import post_replies

HOMING = (
    "Done — renamed to 'Homing Burst Projectile' everywhere: its three users (Aphelios, Teemo, "
    "Heimerdinger) and every mention in the Action Model tab. Clearer, agreed.")

SKILLRANGE = (
    "Added — a new 'Skill Range' column sits just before Aim Target. I defaulted each champion's value "
    "to its auto-attack Range in hexes, as you said; correct them per-skill whenever. The Column "
    "Explain note spells out the rule: the aim target must be inside this range for the skill to fire, "
    "not just full mana.")

QUICKAA = (
    "Done — added a 'QuickAA' action (N basic-attack-like hits in quick succession, Target-Only) and "
    "gave it to Bel'Veth in place of Cast. Her Count 6/6/25 carries how many hits.")

CADENCE = (
    "Changed — the default tick interval is now 'Every 0.5s' across the periodic effects; Garen keeps "
    "'Every spin'. The Cadence column note was updated to match.")

# LONGEST / MOST DISTINCTIVE KEY FIRST. Each is unique to exactly one comment root.
REPLIES = [
    ("Homing Burst Projectile", HOMING),
    ("name it", SKILLRANGE),        # root: '... name it "Skill Range" ...'
    ("QuickAA", QUICKAA),
    ("Every 0.5 sec", CADENCE),
]


if __name__ == "__main__":
    post_replies(REPLIES, warn_unmatched=False)
