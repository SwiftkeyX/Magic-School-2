"""Reply to the sheet's review comments. Holds the CURRENT round's replies, and nothing else.

Run from repo-root cwd:  python .claude/scripts/tft-set9-skill-modularity/reply.py

Overwrite REPLIES each round; git keeps the history. Comments are left UNRESOLVED — resolving them is
the user's call, always. A MATCH KEY IS A SUBSTRING OF THE COMMENT'S ROOT and fails SILENTLY, so keep
keys long, distinctive, and never a prefix of another.

THIS ROUND (round 6c): Refactor 1 built — Spread -> Volley Shape (shape only), Aim Target now a
validated tab that absorbed the target-selection spreads. warn_unmatched=False.
"""

from sheet import post_replies

SPREAD_AIM = "\n".join([
    "Built it. 'Spread' is now 'Volley Shape' and holds ONLY the geometric shapes — Cone (Ashe), "
    "360 radial (Ahri), Diagonal to Action Source (Vel'Koz).",
    "",
    "Everything that picked WHICH enemies — Same target, Each to its own target, Split across "
    "nearest/farthest N, Split across marked, Current + Left + Right — moved into Aim Target, which is "
    "now a VALIDATED vocabulary (its own 'Aim Target Types' tab, ~30 keys grouped single-enemy / "
    "enemy-set / ally / self / per-instance / reference). Distribution (converge vs split) is inferred "
    "from Aim + Count, so it did not need a third column. Two tabs, cleanly separated — as you sketched.",
])

SUMMON = "\n".join([
    "Handled by the same change. A summon that just attacks the current target now carries NO Volley "
    "Shape and NO Fire Timing — its aim is simply Current (or 'Nearest enemy to owner' for the summon's "
    "own attacks). 'How many soldiers' lives on the Summon action's Count, not a spread. Azir's awkward "
    "'Same target / At Once' is gone.",
])

CURRENT3 = "\n".join([
    "Right — and it landed there. 'Current + 3 nearest' (Twisted Fate) and 'Split across nearest N' "
    "(Kai'Sa, now 'Nearest 4 enemies') are both Aim Target 'enemy set' values now, in the SAME column, "
    "no longer split between Aim and Spread.",
])

REPLIES = [
    ("are really similar", SPREAD_AIM),             # #1
    ("doesn't sound right", SUMMON),                # #2
    ("another potential spread member", CURRENT3),  # #6
]

if __name__ == "__main__":
    post_replies(REPLIES, warn_unmatched=False)
