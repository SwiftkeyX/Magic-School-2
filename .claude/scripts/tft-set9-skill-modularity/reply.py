"""Reply to the sheet's review comments. Holds the CURRENT round's replies, and nothing else.

Run from repo-root cwd:  python .claude/scripts/tft-set9-skill-modularity/reply.py

Overwrite REPLIES each round; git keeps the history. Comments are left UNRESOLVED — resolving them is
the user's call, always.

⚠ A MATCH KEY IS A SUBSTRING OF THE COMMENT'S WHOLE TEXT, AND A MISMATCH FAILS SILENTLY.

A short key grabs any longer comment that happens to contain it. This is not hypothetical: the key
"same step" once matched a comment reading "This are the same heal, so it should be combine into same
step" — a comment answered rounds earlier — and landed a reply on it that had nothing to do with it.
The reply had to be deleted by hand.

So: keys are LONG and DISTINCTIVE, the longest is listed first, and a key is never a prefix of
another comment's text. Beware curly quotes and non-breaking spaces (\xa0) — quote nothing you do not
have to.
"""

from sheet import post_replies

ZED = (
    "Done — Zed is one step now.\n\n"
    "You are right, and the sheet was hiding WHY it was right. His steps 2 and 3 both triggered on "
    "'After Summon' — the same instant — and the only thing that actually differed between them was "
    "the Action Source:\n\n"
    "  Self    -> Circle AOE around Zed\n"
    "  Summon  -> Circle AOE around the Shadow\n\n"
    "Which is exactly what the skill says: 'Zed AND HIS SHADOW each slash adjacent enemies.' One "
    "moment, two actors. That is one step with two branches, not two steps.")

IRELIA = (
    "Done — Irelia too, and it is the same shape as Zed.\n\n"
    "Her steps 2 and 3 both triggered on 'On Shield Expire' — the same instant — and differed only "
    "in the hitbox they threw:\n\n"
    "  Circle AOE  around herself   (Area)\n"
    "  Laser Shot  at her target    (Pierce-All)\n\n"
    "Two hitboxes from one event is one step with two branches. A step earns its own number by being "
    "a separate MOMENT, and these are not.\n\n"
    "Those two were the last of them: no champion in the sheet now has two consecutive steps sharing "
    "a Trigger.")

SAMIRA = (
    "Fixed — Samira is 'First hit Projectile', and her Collision went with it: 'Target-Only' -> "
    "'First-Hit'.\n\n"
    "That correction was not cosmetic. Target-Only says the projectile touches ONLY the unit it was "
    "aimed at; First-Hit says it touches WHOEVER IT HITS FIRST, which may not be that unit. Different "
    "claim about the geometry, and the Action Model already had the right one — I had just picked the "
    "wrong action.")

AHRI = (
    "Checked, and I am leaving it as Pierce Projectile — but you were right to stop me, because the "
    "comment I acted on was on KARMA and this cell is AHRI. Two different champions, and I nearly "
    "changed the wrong one.\n\n"
    "For the record, so it is not ambiguous later:\n\n"
    "  KARMA  3rd cast  -> Pierce Projectile  (Count 3, Current + Left + Right) — your instruction\n"
    "  AHRI   2nd cast  -> Pierce Projectile  (360° radial, hits All enemies)   — unchanged\n\n"
    "Ahri's source says 'unleash a wave that damages ALL ENEMIES HIT', which is a thing that passes "
    "through everything in its path — Pierce-All. A Burst Projectile detonates at one point and hits "
    "a circle there, so it could not hit 'all enemies hit' on the way out.")

SION = (
    "Fixed — Sion's Charge Into is Count '—' now.\n\n"
    "You have named a rule rather than a cell, and it is the same one that already covers Cast and "
    "Leap: an em-dash means the question CANNOT apply — there is no way to charge twice in one "
    "action. That is different from Count 1, which says 'one instance, and there could have been "
    "more'. Sion was the only Charge Into in the sheet.")

CADENCE = (
    "Renamed — 'Cadence' -> 'Effect Cadence'.\n\n"
    "Agreed, and for a reason worth stating: it describes the EFFECT, not the action. That puts it in "
    "the same family as Effect Recipient / Effect Category / Effect Detail, and the name now says so. "
    "The Column Explain legend was renamed with it.")

DURATION = (
    "Renamed — 'Duration (s)' -> 'Effect Duration (s)'.\n\n"
    "Same reasoning as Cadence: it is a property of the EFFECT, not of the action, and the name should "
    "say which. I kept the '(s)' so the unit stays obvious. The Column Explain legend was renamed with "
    "it.")

KARMA = (
    "Fixed — the Condition now says what you said.\n\n"
    "  If 1st or 2nd Cast  ->  Circle AOE         (Count 1)\n"
    "  If 3rd Cast         ->  Pierce Projectile  (Count 3, Current + Left + Right)\n\n"
    "It had read 'If not 3rd Cast', which is the same logic stated as a NEGATION — and you wrote it "
    "positively ('1st, 2nd cast'). You were right that it did not reflect what you wrote; a reader "
    "should not have to invert a condition in their head to check it against the game.\n\n"
    "Her actions were already correct. The 'why is this Pierce Projectile?' comment turned out to be "
    "on Ahri's row, not Karma's — answered there.")

# LONGEST / MOST DISTINCTIVE KEY FIRST. Every key below is unique to exactly one comment.
REPLIES = [
    ("step 2 and 3 for zed", ZED),
    ("2 and 3 are the same step", IRELIA),
    ("For samira, this is", SAMIRA),
    ("Burse Projectile", AHRI),            # the user's own typo — usefully unique
    ("Charge Into don't have Count", SION),
    ("Effect Cadence", CADENCE),
    ("Effect Duration", DURATION),
    ("1st, 2nd cast: do circle AOE", KARMA),
]


if __name__ == "__main__":
    post_replies(REPLIES, warn_unmatched=False)
