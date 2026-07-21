"""Reply to the sheet's review comments. Holds the CURRENT round's replies, and nothing else.

Run from repo-root cwd:
    python .claude/scripts/tft-set9-skill-modularity/reply.py

Overwrite REPLIES each round; git keeps the history. Comments are left UNRESOLVED — resolving them is
the user's call, always. A MATCH KEY IS A SUBSTRING OF THE COMMENT'S ROOT and fails SILENTLY, so keep
keys long, distinctive, and never a prefix of another.

THIS ROUND (round 17, 2026-07-19): one open comment — grouping the Aim Target tab. Applied.
warn_unmatched=False: the Skill Range thread was answered last round and must not be re-answered.
"""

from sheet import post_replies

GROUPED = "\n".join([
    "APPLIED — `Aim Target Types` now has a `Group` column, the rows are sorted into blocks, and the "
    "group label is merged down each block (the same treatment `Effect Types` gets).",
    "",
    "  HP              6   Lowest-HP enemy, Highest HP, [N] lowest-HP enemies,",
    "                      Lowest-HP Ally, Highest-HP Ally, Lowest-HP Allies",
    "  Distance        9   Nearest enemy, Farthest, Nearest [N] enemies, ...",
    "  Current target  5   Current, Current (new), Current + Left + Right, ...",
    "  Enemy state     4   Knocked-up enemy, Marked enemies, Enemy entering range, ...",
    "  Position        5   Board centre, Bench slot, Away from enemies, Clustered, ...",
    "  Reference       3   Step [N] Aim target, Summon, Hex That Projectile Hit",
    "  Random          1",
    "  Self            1",
    "",
    "WHY A NEW COLUMN RATHER THAN REUSING `Kind`. The tab already had `Kind` (single enemy / enemy "
    "set / single ally / ally set / position / self / reference), but your example cuts ACROSS it: "
    "`Lowest-HP enemy`, `Lowest-HP Ally` and `[N] lowest-HP enemies` are three different Kinds and you "
    "want them together. They are two honest axes — `Kind` says WHAT COMES BACK (one unit or many), "
    "`Group` says HOW THE TARGET IS CHOSEN — so `Kind` stayed as data and `Group` was added for "
    "reading. Sorting by Kind alone would have split your HP example across three blocks.",
    "",
    "ONE STRUCTURAL CONSEQUENCE worth recording: `Group` sits in column 0, so the aim KEY moved to "
    "column 1. Every vocabulary check assumed the key was in column 0, which would have made all 34 "
    "aim keys read as undefined at once. There is now a `KEY_COL` map naming the exception, and both "
    "validation paths consult it. VALIDATE passes.",
])

REPLIES = [
    ("It is still hard to read. Could you also group them", GROUPED),
]

if __name__ == "__main__":
    post_replies(REPLIES, warn_unmatched=False)
