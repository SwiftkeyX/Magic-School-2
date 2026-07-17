"""Reply to the sheet's review comments. Holds the CURRENT round's replies, and nothing else.

Run from repo-root cwd:  python .claude/scripts/tft-set9-skill-modularity/reply.py

Overwrite REPLIES each round; git keeps the history. Comments are left UNRESOLVED — resolving them is
the user's call, always. A MATCH KEY IS A SUBSTRING OF THE COMMENT'S ROOT and fails SILENTLY, so keep
keys long, distinctive, and never a prefix of another.
"""

from sheet import post_replies

# --- Round: Zone AOE (a hitbox that stays) + Silco's missing vial ---

SILCO = "\n".join([
    "Done — Silco is a projectile then a zone now:",
    "",
    "  step 1  Homing Projectile   AOE 1-hex           -> — (the vial; it applies nothing)",
    "  step 2  On Projectile Hit   src 'Step 1 Projectile'",
    "          Zone AOE            AOE Circle 2 hex    -> Damage/Heal, every 1s for 6s",
    "",
    "The vial was missing from the sheet ENTIRELY — he was a bare Circle AOE, so the thing he throws "
    "was nowhere. He is the same shape as Teemo now: a projectile, then the thing it becomes.",
    "",
    "See your Teemo comment for the Zone AOE half — that one is the more interesting of the two.",
])

ZONE = "\n".join([
    "You have found a real gap, and the difference you are describing is testable, which is what makes "
    "it worth a name: walk OUT of Silco's chemicals and the damage stops; walk away from Teemo's "
    "poison and it keeps ticking, because that one rides on YOU.",
    "",
    "  Silco: the damage comes from BEING IN A PLACE. His hitbox persists.",
    "  Teemo: the damage comes from HAVING BEEN HIT. His hitbox fires once and leaves a status.",
    "",
    "THE SHEET COULD NOT SAY WHICH. Both read 'Circle AOE + Every Ns + duration' — and that duration "
    "silently meant two different things: the HITBOX's life for Silco, the VICTIM's status for Teemo. "
    "Same class of bug as AOE (hex) meaning both the hitbox and the burst it becomes.",
    "",
    "So there is a new action, 'Zone AOE' — a hitbox that STAYS for its duration, re-applying to "
    "whoever is inside at each tick. Its Effect Recipient is re-evaluated every tick; that is the "
    "whole point of it. The ACTION now says which kind of duration a row means, so no column has to:",
    "",
    "  Circle AOE (fires once) + over-time  ->  the duration is the VICTIM'S status",
    "  Zone AOE   (persists)   + over-time  ->  the duration is the ZONE'S life",
    "",
    "TEEMO NEEDED NO CHANGE. He was already right — only the ambiguity around him was wrong.",
    "",
    "AND IT WAS NOT JUST THESE TWO. Garen ('spin like a beyblade for 4s') and Swain (his aura while "
    "transformed) are persistent hitboxes wearing Circle AOE as well. All three are Zones now.",
    "",
    "ONE THING I LEFT ALONE, flagged for you: Garen's cadence reads 'Every spin'. Every other cadence "
    "in the sheet is a real interval (Once / Every 0.5s / Every 1s), and his source only says 'damage "
    "over time' — it never gives a number. I would rather flag it than invent one.",
])

REPLIES = [
    ("Silco throw homing projectile first", SILCO),
    ("Teemo and Silco are really similar", ZONE),
]

if __name__ == "__main__":
    post_replies(REPLIES, warn_unmatched=False)
