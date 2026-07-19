"""Reply to the sheet's review comments. Holds the CURRENT round's replies, and nothing else.

Run from repo-root cwd:  python .claude/scripts/tft-set9-skill-modularity/reply.py

Overwrite REPLIES each round; git keeps the history. Comments are left UNRESOLVED — resolving them is
the user's call, always. A MATCH KEY IS A SUBSTRING OF THE COMMENT'S ROOT and fails SILENTLY, so keep
keys long, distinctive, and never a prefix of another.

THIS ROUND (round 10, 2026-07-19): 5 open comments — two coefficients I had left 'unknown' (Olaf,
Lucian), Miss Fortune's delivery, and TWO on Illaoi's tentacle row (its action and its cadence).
All 5 applied. The cadence one is answered with a caveat: it stretches the Condition column, and the
honest fix may be a new column. BUILT. warn_unmatched=False.
"""

from sheet import post_replies

OLAF = "\n".join([
    "Applied — that fills in the coefficient the source never gave.",
    "",
    "  Amount        unknown  ->  0.15% max HP",
    "  Scaling Type  Derived  ->  Per Stack",
    "  Scaling                    per 1% missing Health",
    "",
    "I also changed the Scaling TYPE, which is the more interesting half. 'Derived' says the amount "
    "is computed from another stat; 'Per Stack' says the amount is MULTIPLIED by a counter. Missing "
    "Health % is exactly such a counter — at 40% missing he has 40 stacks of 0.15% max HP — so Per "
    "Stack is the one that actually describes the arithmetic. Same family as Aphelios' Chakrams and "
    "Kalista's spears.",
])

LUCIAN = "\n".join([
    "Fixed — step 2's AOE is now 'Circle 1 hex' (was 'unknown').",
    "",
    "One note on why it reads 'Circle 1 hex' and not the bare '1-hex' key: the action is a Circle "
    "AOE, whose Shape is fixed to 'circle' in the Action Model, so the row has to state a circle "
    "SIZE. The plain '1-hex' key means a single-hex hitbox with no radius at all — which is what "
    "Spawn At Target uses. Same size, different claim.",
    "",
    "Lucian still has one 'unknown' left, and it is a different question: step 3's Mana refund "
    "amount. The source only says 'gain Mana based on the number of unused shots' with no rate, so if "
    "you have the per-shot number that cell can be filled too.",
])

MISS_FORTUNE = "\n".join([
    "Clear, yes — and it means the delivery was wrong, not just a cell. Rebuilt as two steps:",
    "",
    "  1  On Cast       Homing Projectile  aim Current                                 280/280/290% AD",
    "  2  After Step 1  Homing Projectile  aim Closest enemy behind Step 1 Aim target  180/180/180% AD",
    "",
    "What I had was a single Pierce Projectile with two effect rows ('First hit enemy' and 'Enemies "
    "in path (farther)') — the shape I used for Lulu. Your description breaks that in a way worth "
    "spelling out: a pierce passes THROUGH things in a straight line, so its second victim is "
    "whoever happens to stand on that line. Yours is a second projectile that PICKS a target — the "
    "nearest one that is also behind the first. Those differ whenever the nearest enemy behind the "
    "target is not directly in line, which is most of the time.",
    "",
    "The aim key it needed already existed: 'Closest enemy behind Step 1 Aim target' was added for "
    "exactly this in Set 9. Nothing new in the vocabulary.",
    "",
    "Lulu is genuinely the pierce case (one bolt, whoever it passes through), so she is unchanged.",
])

ILLAOI_BOX = "\n".join([
    "Applied — the tentacle passive is a Box AOE now, matching Aatrox exactly:",
    "",
    "  Legacy action   Zone AOE    ->  Box AOE",
    "  Offset          centred     ->  rear edge",
    "  AOE (hex)       unknown     ->  Box 1x2",
    "",
    "This also retires an 'unknown' — I had no size for the zone, and Aatrox's box gives one.",
    "",
    "Worth noting what the change says, since Zone vs Box is not only a shape: a Zone AOE is a hitbox "
    "that PERSISTS and re-checks who is standing in it every tick. A Box AOE fires once per slam. So "
    "as written before, an enemy who walked into the tentacles' area between slams would have been "
    "hit; now only whoever is in the box AT the slam is. That matches 'tentacles slam' much better "
    "than a lingering field did.",
])

ILLAOI_CADENCE = "\n".join([
    "It makes sense, and you are right that it was in the wrong column — but I want to flag what it "
    "cost, because I think it points at a missing column rather than a wrong cell.",
    "",
    "Applied:",
    "  Condition        —           ->  Every 3/3/3 seconds",
    "  Effect Cadence   Every 3s    ->  Once",
    "",
    "Your reasoning is right: 'Every 3s' in Effect Cadence said the EFFECT re-applies on a timer, "
    "which for a Zone means the hitbox sits there and re-damages whoever is inside. What actually "
    "repeats is the SLAM — the action — and each slam applies its damage once. Cadence Once is "
    "correct now.",
    "",
    "THE CAVEAT: 'Every 3/3/3 seconds' is not really an if-else. The sheet's own rule in Column "
    "Explain is 'Trigger = WHEN, Condition = ONLY-IF' — a Condition is a gate that is either true or "
    "false at the moment the trigger fires. A recurrence is a schedule, not a gate. So the cell now "
    "reads as a condition but behaves as a clock, which is the same kind of overloading that got "
    "'Spread' split into Volley Shape + Aim Target.",
    "",
    "Two cleaner options if you want it, neither of which I did on my own initiative:",
    "  (a) a new Trigger value 'Every N seconds' — it IS a when, and Trigger is the when column;",
    "  (b) a real 'Action Cadence' column next to Fire Timing, which is the name you used yourself.",
    "",
    "(a) is one row in Trigger Types and no schema change; (b) is a 33rd column but says it exactly. "
    "Illaoi is currently the only champion with a repeating action, so there is no fleet to migrate "
    "either way — which makes now the cheap moment to pick.",
])

REPLIES = [
    ("Summon do Box AOE like aatrox does", ILLAOI_BOX),
    ("It is not effect cadence", ILLAOI_CADENCE),
    ("For misfortune, this is more like", MISS_FORTUNE),
    ("Attack Speed: 1% = 0.15% Health", OLAF),
    ("1hex AOE for lucian", LUCIAN),
]

if __name__ == "__main__":
    post_replies(REPLIES, warn_unmatched=False)
