"""Reply to the sheet's review comments. Holds the CURRENT round's replies, and nothing else.

Run from repo-root cwd:  python .claude/scripts/tft-set9-skill-modularity/reply.py

Overwrite REPLIES each round; git keeps the history. Comments are left UNRESOLVED — resolving them is
the user's call, always.

⚠ A MATCH KEY IS A SUBSTRING OF THE COMMENT'S ROOT TEXT, AND A MISMATCH FAILS SILENTLY.

A short key grabs any longer comment that happens to contain it. This is not hypothetical: the key
"same step" once matched a comment reading "This are the same heal, so it should be combine into same
step" — a comment answered rounds earlier — and landed a reply on it that had nothing to do with it.
The reply had to be deleted by hand.

So: keys are LONG and DISTINCTIVE, the longest is listed first, and a key is never a prefix of
another comment's text. Beware curly quotes and non-breaking spaces (\xa0) — quote nothing you do not
have to.

This round answers the ONE re-opened thread: the user rejected my earlier "leaving it as Pierce
Projectile" and gave explicit instructions for BOTH champions in the same thread (anchored to Ahri's
cell). post_replies matches on the ROOT comment, so the key is the root's distinctive typo, not the
follow-up replies. A new body means post_replies will add a fresh reply under my earlier one rather
than skip the thread as already-answered.
"""

from sheet import post_replies

BURST = (
    "Done — you were right on both, and my earlier 'leaving it as Pierce Projectile' was wrong.\n\n"
    "KARMA — Burst Projectile on every cast now, exactly as you said:\n"
    "  1st / 2nd cast  ->  Burst Projectile  x1\n"
    "  3rd cast        ->  Burst Projectile  x3  (Current + Left + Right)\n"
    "The old rows read Circle AOE / Pierce Projectile, which fought her own description: 'fire a "
    "burst that explodes on impact ... every third cast launches 3 bursts'.\n\n"
    "AHRI — a clean 3-cast cycle, the wave now REPLACES the AOE on the 3rd cast:\n"
    "  1st / 2nd cast  ->  Circle AOE   (essence steal + Mana Reave)\n"
    "  3rd cast        ->  Pierce wave  (360 radial, +33% on essence-stolen enemies)\n"
    "Its condition moved 2nd -> 3rd, and the description dropped 'Every 2/2/0 casts' for 'Every third "
    "cast instead'.\n\n"
    "And Jayce, the only other Burst Projectile, had Collision 'Area' — corrected to 'First-Hit' to "
    "match the Action Model tab: a Burst Projectile IS First-Hit + Circle AOE, so it detonates on the "
    "FIRST body it meets and the circle is centred on that impact hex.")

# LONGEST / MOST DISTINCTIVE KEY FIRST. Unique to exactly one comment (the user's own typo).
REPLIES = [
    ("Karma use Burse Projectile", BURST),
]


if __name__ == "__main__":
    post_replies(REPLIES, warn_unmatched=False)
