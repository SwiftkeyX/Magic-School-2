"""ONE-SHOT: 'Auto-Attack' as an ACTION was a category error. Split it by what actually happens.

    python .claude/scripts/tft-set9-skill-modularity/migrate_bonus_on_aa.py

Run ONCE, then archive/. Rewrites data/hero.csv + data/action-model.csv, then sync.py pushes it.

THE USER'S POINT: "On attack do action Auto-Attack (melee)" is circular. If the TRIGGER is the attack,
the ACTION cannot also be the attack — the action is whatever RIDES on it. The source text says so
every time: "Attacks heal for 30/35/40% AP" (Warwick), "attacks deal bonus damage" (Kayle), "Attacks
impale a spear" (Kalista). Warwick proves it: On Attack -> Auto-Attack -> Buff/HEAL. He is not
attacking; he is healing because he attacked.

So the real cut is BONUS-ON-ATTACK vs PERFORMS-AN-ATTACK, not melee vs ranged:

  Bonus on AA   the attack already happened (it is the trigger) and delivered the hit. The action
                projects NO hitbox of its own -> DirectApply, Collision None. 8 rows.
  Auto-Attack   something really does attack. All three are a SUMMON acting on its own (Azir's Sand
    (ranged)    Soldier, Soraka's Child of the Star) — never the champion, whose own attack is the
                trigger instead.
  QuickAA       Bel'Veth "lash out 6/6/25 times" — a real burst of N attacks. Un-folded from the
                Auto-Attack row: it PERFORMS attacks, so lumping it with a bonus was backwards.

This RETIRES `Auto-Attack (melee)` (zero rows) and dissolves the melee/ranged split entirely: every
melee AA row was a bonus. The split was a PROXY for this distinction — melee bonuses are DirectApply
and ranged bonuses ride a projectile — which is why it looked like it held.

NILAH is not a bonus: "Attacks strike in a cone" reshapes the attack itself into one Area hitbox.
Her row said Spread=Cone AND Count=1, which the sheet's own rule forbids — a single instance has
nothing to arrange (SPREAD_DEFAULT), and Spread=Cone means N SEPARATE hitboxes arranged in a cone
(Ashe's 8 arrows, Count=8). One cone-shaped hitbox is a Cone AOE, like Kassadin's.

TRISTANA needed nothing: her explode-on-impact was ALREADY a Circle AOE (step 2). The Auto-Attack row
is step 3, her 4-star upgrade ("Every 10th attack deals 100% AD bonus"), which is a plain bonus.

WARWICK's step 2 was 'After Cast', same as 9 other champions — but theirs fire immediately after the
cast and his fires 2.5s later, when the Attack Speed buff ends ("Gain 100% AS for 2.5 seconds. THEN,
stun"). Different event, so: 'On Cast Expire' (the user's wording).
"""

import csv
import pathlib

DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")
D = "—"

BONUS = "Bonus on AA"
AA_RANGED = "Auto-Attack (ranged)"
QUICK = "QuickAA"
OLD_RANGED = "Auto-Attack (ranged) / QuickAA"
OLD_MELEE = "Auto-Attack (melee)"

# champion -> the name its Auto-Attack row becomes. Every AA row in the sheet is listed, so a row this
# script does not know about is a NEW one and must fail loudly rather than be silently left behind.
REASSIGN = {
    "Kayle": BONUS, "Nasus": BONUS, "Sejuani": BONUS, "Kalista": BONUS,
    "Aphelios": BONUS, "Warwick": BONUS, "Zeri": BONUS, "Tristana": BONUS,
    "Azir": AA_RANGED, "Soraka": AA_RANGED,
    "Bel'Veth": QUICK,
    "Nilah": "Cone AOE",
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
    c = {n: h.index(n) for n in
         ("Champion", "Step", "Trigger (When)", "Legacy action", "Offset", "Spread",
          "Collision (If it have one)")}

    champ, changed, seen = "", [], set()
    for r in hero[1:]:
        if r[c["Champion"]].strip():
            champ = r[c["Champion"]].strip()
        act = r[c["Legacy action"]].strip()

        # Warwick's step-2 stun waits out the 2.5s buff; the other 9 'After Cast' rows do not.
        if champ == "Warwick" and r[c["Trigger (When)"]].strip() == "After Cast":
            r[c["Trigger (When)"]] = "On Cast Expire"
            changed.append((champ, "trigger", "After Cast -> On Cast Expire"))

        if act not in (OLD_RANGED, OLD_MELEE):
            continue
        if champ not in REASSIGN:
            raise SystemExit(f"{champ} has an Auto-Attack row this script does not know about. "
                             f"Decide what it is before running.")
        seen.add(champ)
        new = REASSIGN[champ]
        r[c["Legacy action"]] = new

        if new == BONUS:
            # The AA already delivered the hit; the bonus projects nothing of its own.
            r[c["Collision (If it have one)"]] = "None"
            r[c["Offset"]] = D
        elif new == "Cone AOE":
            # One cone-shaped hitbox. Spread=Cone asserted N arranged instances, but Count is 1.
            r[c["Spread"]] = D
            r[c["Offset"]] = "front edge"          # every other Cone AOE row anchors this way
        changed.append((champ, "action", f"{act} -> {new}"))

    missing = set(REASSIGN) - seen
    if missing:
        raise SystemExit(f"expected an Auto-Attack row for {sorted(missing)} and found none")

    write("hero.csv", hero)
    for who, kind, what in changed:
        print(f"  {who:<10} {kind:<8} {what}")
    print(f"hero.csv: {len(changed)} rows changed")

    # --- the tab: add Bonus on AA + QuickAA, rename the ranged row, retire the melee row ---
    am = read("action-model.csv")
    ah = am[0]
    a = {n: ah.index(n) for n in ("Legacy Action", "Apply", "Spawn", "Motion", "Behavior", "Shape",
                                  "Offset", "Collision", "What it does", "Clarify more")}
    doc_at = next(i for i, r in enumerate(am) if not any(x.strip() for x in r))
    body, doc = am[1:doc_at], am[doc_at:]

    def row(**kw):
        r = [""] * len(ah)
        for k, v in kw.items():
            r[a[k]] = v
        return r

    body = [r for r in body if r[0].strip() != OLD_MELEE]      # retired: zero rows use it
    for r in body:
        if r[0].strip() == OLD_RANGED:
            r[0] = AA_RANGED
            r[a["Clarify more"]] = (
                "Only ever a SUMMON acting on its own (Azir's Sand Soldier, Soraka's Child of the "
                "Star) - read Action Source. The champion's OWN attack is never this: it is a "
                "TRIGGER ('On Attack'), and what rides on it is 'Bonus on AA'.")

    body.append(row(**{
        "Legacy Action": BONUS, "Apply": "DirectApply", "Spawn": D, "Motion": D, "Behavior": D,
        "Shape": D, "Offset": D, "Collision": "None",
        "What it does": "An effect that rides on an auto-attack that has ALREADY happened.",
        "Clarify more": (
            "Pair it with Trigger = 'On Attack' / 'On 3rd Attack' / etc - the attack is the TRIGGER, "
            "so the action must not also be the attack. Projects NO hitbox: the auto-attack already "
            "delivered the hit, and this only adds an effect to it, so Collision is None. The effect "
            "is the point, and it need not be damage - Warwick HEALS ('Attacks heal for 30/35/40% "
            "AP'), Kalista impales, Zeri executes. Replaced 'Auto-Attack' as an action, which was "
            "circular ('On attack, do an auto-attack') - the user's call. If the attack itself is "
            "RESHAPED rather than merely added to, it is not this: Nilah's cone is a Cone AOE."),
    }))
    body.append(row(**{
        "Legacy Action": QUICK, "Apply": "Hitbox", "Spawn": "at-User", "Motion": "Projectile",
        "Behavior": "Homing", "Shape": "1-hex", "Offset": "centred", "Collision": "Target-Only",
        "What it does": "The unit attacks the target N times in QUICK SUCCESSION - N "
                        "basic-attack-like hits in a row, not a real ability cast.",
        "Clarify more": (
            "Bel'Veth: 6/6/25 rapid attacks on the lowest-HP enemy, carried in Count. It PERFORMS "
            "attacks, which is why it is its own action and not 'Bonus on AA' - and why it is no "
            "longer folded in with Auto-Attack (ranged), whose only users are summons."),
    }))

    for r in doc:                                   # the AXES legend still names the retired split
        if r[0].startswith("SHAPE is per-ACTION"):
            r[0] += (" Auto-Attack is NOT an action when the champion attacks: that is Trigger = 'On "
                     "Attack' + the action 'Bonus on AA'.")
    write("action-model.csv", [ah] + body + doc)
    print(f"action-model.csv: {len(body)} actions "
          f"(+{BONUS}, +{QUICK}, {OLD_MELEE} retired, {OLD_RANGED} -> {AA_RANGED})")


if __name__ == "__main__":
    main()
