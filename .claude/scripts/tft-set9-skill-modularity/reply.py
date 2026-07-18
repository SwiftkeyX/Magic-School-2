"""Reply to the sheet's review comments. Holds the CURRENT round's replies, and nothing else.

Run from repo-root cwd:  python .claude/scripts/tft-set9-skill-modularity/reply.py

Overwrite REPLIES each round; git keeps the history. Comments are left UNRESOLVED — resolving them is
the user's call, always. A MATCH KEY IS A SUBSTRING OF THE COMMENT'S ROOT and fails SILENTLY, so keep
keys long, distinctive, and never a prefix of another.

THIS ROUND (round 7b): summon taxonomy + passive 0.x normalization, both BUILT. warn_unmatched=False.
"""

from sheet import post_replies

SUMMON = "\n".join([
    "Built it — three summon actions, split by behaviour:",
    "",
    "  Static Summon  (spawns, stands, attacks):            Set 9 Zed, Azir",
    "  Charge Summon  (spawns unit[s] that charge in):      Naafiri, Gangplank  (absorbs 'untethered')",
    "  Hero Summon    (walks the grid + auto-attacks):      Set 10 Zed",
    "",
    "'Summon' and 'Summon (untethered)' are retired. Each spawned unit still becomes a SECOND action "
    "source for the steps that follow, so its charge/attack rides on it (Naafiri's packmates keep their "
    "'Charge [collision=Target-Only]' step; the Charge Summon just declares their nature).",
])

PASSIVE = "\n".join([
    "Done — every passive is in the 0.x family now. Single passives moved from '0' to '0.1', and the "
    "three that were mis-numbered as ACTIVE steps (Zeri's chain, Riven's splash, Urgot's cone, all at "
    "'2') became 0.1 / 0.2. 30 steps across Set 9 plus the Set 10 passives.",
    "",
    "One note: I renumbered in place, so a passive that currently sits BELOW its active in the sheet "
    "keeps that file position but reads 0.x. If you want them physically reordered to the TOP of each "
    "champion's block, say so — that is a bigger row-move and I kept it out for now.",
])

REPLIES = [
    ("made each one a action", SUMMON),        # #2
    ("should also be step 0.1", PASSIVE),      # #3
]

if __name__ == "__main__":
    post_replies(REPLIES, warn_unmatched=False)
