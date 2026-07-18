"""ONE-SHOT: make the sequencing triggers modular — 'After X' becomes 'After Step N'.

    python .claude/scripts/tft-set9-skill-modularity/migrate_step_triggers.py

Run ONCE, then archive/. Rewrites hero.csv + trigger-types.csv.

THE USER: "Those trigger condition should be modular BUT some stuff inside are not. The stuff that
only used by certain hero, list them to me."

The list found something sharper than "used by one hero". The real test is: does 'After X' name the
PRECEDING STEP'S ACTION? Six rows failed it, and two of those use POPULAR triggers — which the
one-hero test would never have caught:

    Yasuo    step 2  'After Whirlwind'        <- step 1 is a Pierce Projectile
    Yasuo    step 4  'After Slash'            <- step 3 is a Cast
    Shen     step 2  'After Shielding Allies' <- step 1 is a Cast (it names the EFFECT)
    Poppy    step 2  'After Cast (return)'    <- step 1 is a Homing Projectile
    Aphelios step 2  'After Cast'             <- step 1 is a Homing Burst Projectile
    Qiyana   step 2  'After Move'             <- step 1 is a Move BEHIND

'Whirlwind', 'Slash' and 'Shielding Allies' are not actions and not effects and not anywhere in the
sheet - they are flavour names for one champion's ability, so nothing could ever validate them.

WHY NOT JUST FIX THE SIX to name their real action? Because 'After <Action>' cannot be a rule: NINE
champions run the same action in two different steps (Yasuo casts at step 0 AND step 3), so 'After
Cast' is ambiguous for them by construction. A step number is not.

'After Step N' reuses a referencing pattern the sheet already has - Aim Target's 'Step N Aim target' -
and it cannot name a fiction. Eight triggers collapse into it.

SEJUANI AND KALISTA break the schema's own rule, stated in Column Explain: "Trigger = when; Condition
= only-if". Each packs a state gate INTO the event:
    'On Ally Attack Chilled Enemy' = an ally attacks (when) + the enemy is Chilled (only-if)
    'On Spears Lethal'             = she attacks (when)     + the skill can execute (only-if)
Split, they are ordinary rows built from vocabulary that already exists.
"""

import csv
import pathlib

DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")
D = "—"

# champion -> (old trigger, new trigger, new condition). The user's wording for Kalista's gate:
# "If skill can execute" — it describes the SKILL's gate, not the outcome, which is why it beats
# the existing 'If Kills Target' here.
SPLIT = {
    "Sejuani": ("On Ally Attack Chilled Enemy", "On Ally Attack", "If Target Chilled"),
    "Kalista": ("On Spears Lethal", "On Attack", "If skill can execute"),
}


def read(name):
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return [r for r in csv.reader(f)]


def write(name, rows):
    with (DATA / name).open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)


def main():
    hero = read("hero.csv")
    h = hero[0]
    c = {n: h.index(n) for n in h}

    # Group rows by champion, keeping file order.
    champ, blocks = "", {}
    for n, r in enumerate(hero):
        if n == 0:
            continue
        if r[c["Champion"]].strip():
            champ = r[c["Champion"]].strip()
        blocks.setdefault(champ, []).append(r)

    after, split = 0, 0
    for name, rs in blocks.items():
        # The steps this champion owns, NUMERICALLY. File order is not step order — several champions
        # list their passive (step 0) after the active steps, so "the row above" is the wrong answer.
        steps = sorted({float(r[c["Step"]].strip()) for r in rs if r[c["Step"]].strip()})
        for r in rs:
            t = r[c["Trigger (When)"]].strip()

            if name in SPLIT and t == SPLIT[name][0]:
                _, trig, cond = SPLIT[name]
                r[c["Trigger (When)"]] = trig
                r[c["Condition (Only if)"]] = cond
                split += 1
                continue

            if not t.startswith("After "):
                continue
            s = r[c["Step"]].strip()
            if not s:
                raise SystemExit(f"{name}: an 'After' trigger on a row with no Step — cannot tell "
                                 f"which step precedes it: {t!r}")
            prev = [x for x in steps if x < float(s)]
            if not prev:
                raise SystemExit(f"{name} step {s}: {t!r} but no earlier step exists to follow")
            p = max(prev)
            r[c["Trigger (When)"]] = f"After Step {int(p) if p == int(p) else p}"
            after += 1

    write("hero.csv", hero)
    print(f"hero.csv: {after} 'After X' triggers -> 'After Step N'; {split} trigger/condition splits")

    # Rebuild the vocabulary from what is actually used, so the retired names cannot linger.
    ti = h.index("Trigger (When)")
    used = sorted({r[ti].strip() for r in hero[1:] if r[ti].strip()} - {D})
    old = {r[0].strip(): (r[1] if len(r) > 1 else "") for r in read("trigger-types.csv")[1:]}
    write("trigger-types.csv",
          [["Trigger", "Meaning"]] + [[t, old.get(t, "")] for t in used])
    gone = sorted(set(old) - set(used) - {""})
    print(f"trigger-types.csv: {len(used)} triggers (was {len(old)})")
    print(f"  retired: {gone}")


if __name__ == "__main__":
    main()
