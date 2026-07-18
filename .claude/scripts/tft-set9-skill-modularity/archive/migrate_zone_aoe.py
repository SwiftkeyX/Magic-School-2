"""ONE-SHOT: a hitbox that PERSISTS is not a hitbox that fires once. Add `Zone AOE`; split Silco.

    python .claude/scripts/tft-set9-skill-modularity/migrate_zone_aoe.py

Run ONCE, then archive/. Rewrites hero.csv + action-model.csv. INSERTS a row -> force_full.py after.

THE USER: "Silco's skill make the hex become poison, enemy who stand on it take damage every 1 sec.
But for Teemo, he throw a Circle AOE, enemy who get hit by the AOE become posion and take damage every
1 sec until the duration is expired. What do you think?"

The difference is real and testable: Silco's damage comes from BEING IN A PLACE, Teemo's from HAVING
BEEN HIT. Walk out of the chemicals and you stop taking damage; walk away from the poison and it keeps
ticking. Silco's HITBOX persists. Teemo's fires once and leaves a status on the victim.

THE SHEET COULD NOT SAY WHICH. Both read `Circle AOE + Every Ns + duration`, and that duration meant
two different things — the HITBOX's life for Silco, the VICTIM's status for Teemo. Same class of bug
as `AOE (hex)` meaning both the hitbox and the burst it becomes.

`Zone AOE` fixes it at the ACTION, which is where every other hitbox property lives. Then the action
disambiguates the duration, and no column has to:

    Circle AOE (fires once) + an over-time effect  ->  the duration is the VICTIM'S status
    Zone AOE   (persists)   + an over-time effect  ->  the duration is the ZONE'S life

TEEMO NEEDS NO CHANGE — he was already right; only the ambiguity around him was wrong.

AND IT WAS NOT JUST SILCO. Garen ("spin like a beyblade for 4s") and Swain (a pulsing aura while
transformed) are persistent hitboxes too, both wearing Circle AOE. The user took all three.

SILCO ALSO GETS THE PROJECTILE SPLIT ("Throw a vial ... then when the projectile hit the target, it
explode into Circle AOE") — he was modelled as a bare Circle AOE, so the vial he throws was missing
entirely. He is the same shape as Teemo: a projectile, then the thing it becomes.

FLAGGED, NOT FIXED: Garen's cadence is 'Every spin' — a flavour word where every other cadence is a
real interval, and his source never states one. The user's call: leave it rather than invent a number.
"""

import csv
import pathlib

DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")
D = "—"


def read(name):
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return [r for r in csv.reader(f)]


def write(name, rows):
    with (DATA / name).open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)


def main():
    hero = read("hero.csv")
    H = hero[0]
    C = {n: H.index(n) for n in H}

    champ, rows_by = "", {}
    for i, r in enumerate(hero):
        if i and r[C["Champion"]].strip():
            champ = r[C["Champion"]].strip()
        if i:
            rows_by.setdefault(champ, []).append(i)

    # --- Circle AOE -> Zone AOE where the hitbox PERSISTS ---------------------------------------
    n = 0
    for who in ("Silco", "Garen", "Swain"):
        for i in rows_by[who]:
            if hero[i][C["Legacy action"]].strip() == "Circle AOE" \
                    and hero[i][C["Effect Cadence"]].strip().startswith("Every"):
                hero[i][C["Legacy action"]] = "Zone AOE"
                n += 1
    assert n == 3, f"expected 3 persistent Circle AOEs (Silco, Garen, Swain), found {n}"
    print(f"  {n} rows: Circle AOE -> Zone AOE (Silco, Garen, Swain)")

    # --- SILCO: he throws a vial. The projectile was missing entirely. ---------------------------
    s = rows_by["Silco"]
    z = [i for i in s if hero[i][C["Legacy action"]].strip() == "Zone AOE"]
    assert len(z) == 1, f"expected 1 Silco Zone AOE row, found {len(z)}"
    z = z[0]

    proj = [""] * len(H)
    proj[:10] = hero[z][:10]                       # carry the identity block onto the new first row
    for k, v in (("Step", "1"), ("Skill Type", "Active"), ("Trigger (When)", "On Cast"),
                 ("Condition (Only if)", D), ("Action Source", "Self"),
                 ("Legacy action", "Homing Projectile"), ("Aim Target", "Clustered"),
                 ("Offset", D), ("AOE (hex)", "1-hex"),
                 ("Skill Range", hero[z][C["Skill Range"]]), ("Count", "1"), ("Spread", D),
                 ("Cast (s)", D), ("Effect Recipient", D), ("Effect Category", D),
                 ("Effect Detail", D), ("Amount", D), ("Scaling Type", D), ("Scaling", D),
                 ("Effect Cadence", D), ("Effect Duration (s)", D)):
        proj[C[k]] = v

    hero[z][:10] = [""] * 10                       # identity moved to the projectile row above it
    for k, v in (("Step", "2"), ("Trigger (When)", "On Projectile Hit"),
                 ("Action Source", "Step 1 Projectile")):
        hero[z][C[k]] = v
    hero.insert(z, proj)
    print("  Silco: + the vial he throws (step 1 Homing Projectile), zone becomes step 2 "
          "'On Projectile Hit'")

    write("hero.csv", hero)
    print(f"hero.csv: {len(hero) - 1} rows")

    # --- the tab ---------------------------------------------------------------------------------
    am = read("action-model.csv")
    ah = am[0]
    a = {n2: ah.index(n2) for n2 in ah}
    doc_at = next(i for i, r in enumerate(am) if not any(x.strip() for x in r))
    if not any(r[0].strip() == "Zone AOE" for r in am[1:doc_at]):
        row = [""] * len(ah)
        for k, v in (("Legacy Action", "Zone AOE"), ("Apply", "Hitbox"), ("Spawn", "at-Target"),
                     ("Motion", D), ("Behavior", D), ("Shape", "circle"), ("Offset", "per row"),
                     ("Collision", "Area"), ("Cast (s)", "TBD") if "Cast (s)" in a else
                     ("Collision", "Area")):
            if k in a:
                row[a[k]] = v
        row[a["What it does"]] = ("A hitbox that STAYS for a duration, re-applying to whoever is "
                                  "inside it at each tick.")
        row[a["Clarify more"]] = (
            "The difference from Circle AOE is WHERE THE DAMAGE COMES FROM, and it is testable: walk "
            "out of a Zone and it stops; walk away from a Circle AOE's poison and it keeps ticking, "
            "because that one rides on YOU. So the ACTION says which kind of duration a row means - a "
            "Zone's Effect Duration is the HITBOX's life, a Circle AOE's is the victim's status. "
            "Silco's chemicals sit on the ground for 6s; Garen's beyblade and Swain's aura are zones "
            "centred on the caster (Aim = Self). Its Effect Recipient is re-evaluated every tick, "
            "which is the whole point.")
        am.insert(doc_at, row)
        write("action-model.csv", am)
        print("action-model.csv: +Zone AOE")


if __name__ == "__main__":
    main()
