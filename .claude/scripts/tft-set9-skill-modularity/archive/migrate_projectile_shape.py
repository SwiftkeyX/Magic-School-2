"""ONE-SHOT: a projectile and the AOE it bursts into are TWO parts. Separate them.

    python .claude/scripts/tft-set9-skill-modularity/migrate_projectile_shape.py

Run ONCE, then archive/. Rewrites hero.csv, action-model.csv, aoe-shape.csv, effect-types.csv.
INSERTS ROWS -> force_full.py afterwards (#9), then sync to 0.

THE USER: "The projectile should have its own shape. NOT the shape of it bursting into AOE (Burst
Projectile). It is 2 different part. The projectile have its own shape and the AOE burst of the
projectile have its own shape separately."

That corrected a real error of mine. I had read 'Burst Projectile' as 'First hit Projectile [Circle
AOE]' — i.e. the projectile IS a circle. It is not: it is a 1-hex bolt that EXPLODES into a circle.
Two hitboxes, one after the other.

And it exposed a conflation already in the sheet: `AOE (hex)` meant THE HITBOX ITSELF for 8 actions
(Circle AOE's circle, Gwen's blade, Malzahar's beam) but THE BURST for the 3 Burst ones — where the
projectile's own 1-hex shape had nowhere to live at all.

THE SPLIT, using a pattern the sheet ALREADY had (Vel'Koz: trigger 'On Projectile Hit', Action Source
'Step 1 Projectile'):

    step N    the projectile flies      AOE = its own shape   -> Movement/(setup)
    step N+1  On Projectile Hit         AOE = the burst       -> the real effect
              src 'Step N Projectile'   Circle AOE

So `Burst Projectile` and `Homing Burst Projectile` retire: a name that hides a second hitbox is the
same bug as `Wave` (a name hiding a shape) and `After Whirlwind` (a name for a step that isn't there).

`Wave` retires too, and THIS time for the user's reason rather than mine: a projectile's shape is
per-row now ('specify elsewhere' on every projectile action), so Sona is `Pierce Projectile` with
`AOE = Box 1.5x2`. Wave existed only to carry a shape the row can now carry itself. Note the model
survived either way — Wave was correct while Shape was per-ACTION, and is redundant now that it is not.

TEEMO GETS BETTER OUT OF THIS. His 4-star branch was on the projectile, but his upgrade is "increase
the EXPLOSION radius by 1 hex" — so it belongs on the burst. After the split he fires one projectile
and the branch sits where the difference actually is.

`Movement/(setup / daggers)` -> `Movement/(setup)`: the delivery rows need it, and Katarina's daggers
had no business being in the vocabulary (same smell as 'After Whirlwind').
"""

import csv
import pathlib

DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")
D = "—"

# Actions whose Motion is Projectile: their SHAPE is now the row's business, not the action's.
PROJECTILES = ["Auto-Attack (ranged)", "Homing Projectile", "First hit Projectile",
               "Pierce Projectile", "Receive Projectile", "QuickAA"]
RETIRE = ["Burst Projectile", "Homing Burst Projectile", "Wave"]
ELSEWHERE = "specify elsewhere"


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
    N = len(H)

    def blank():
        return [""] * N

    def setrow(r, **kw):
        for k, v in kw.items():
            r[C[k]] = v
        return r

    def champ_rows(name):
        cur, out = "", []
        for i, r in enumerate(hero):
            if i and r[C["Champion"]].strip():
                cur = r[C["Champion"]].strip()
            if i and cur == name:
                out.append(i)
        return out

    def delivery(src_row, action, count=None, spread=None, cond=None):
        """The projectile's own row: it flies and delivers, and has no payload of its own."""
        r = blank()
        for k in ("Step", "Skill Type", "Trigger (When)", "Action Source", "Aim Target",
                  "Skill Range", "Cast (s)"):
            r[C[k]] = hero[src_row][C[k]]
        setrow(r, **{"Condition (Only if)": cond if cond is not None else D,
                     "Legacy action": action, "Offset": D, "AOE (hex)": "1-hex",
                     "Count": count if count is not None else hero[src_row][C["Count"]],
                     "Spread": spread if spread is not None else hero[src_row][C["Spread"]],
                     "Effect Recipient": D, "Effect Category": "Movement",
                     "Effect Detail": "(setup)"})
        for k in ("Amount", "Scaling Type", "Scaling", "Effect Cadence", "Effect Duration (s)"):
            r[C[k]] = D
        return r

    def burst(src_row, step, proj_step, aoe, cond=D):
        """The burst: its own step, fired BY the projectile that just landed."""
        r = blank()
        return setrow(r, **{
            "Step": step, "Skill Type": "Active", "Trigger (When)": "On Projectile Hit",
            "Condition (Only if)": cond, "Action Source": f"Step {proj_step} Projectile",
            "Legacy action": "Circle AOE", "Aim Target": hero[src_row][C["Aim Target"]],
            "Offset": "centred", "AOE (hex)": aoe, "Skill Range": hero[src_row][C["Skill Range"]],
            "Count": "1", "Spread": D, "Cast (s)": D})

    def effect(r, src_row):
        """Copy an effect payload off an existing row."""
        for k in ("Effect Recipient", "Effect Category", "Effect Detail", "Amount", "Scaling Type",
                  "Scaling", "Effect Cadence", "Effect Duration (s)"):
            r[C[k]] = hero[src_row][C[k]]
        return r

    out = {}

    # --- KARMA: 2 branches on the projectile (1 burst / 3 bursts); one burst step serves both ------
    k = champ_rows("Karma")
    a, b = k[1], k[2]                                    # 1st-or-2nd cast, 3rd cast
    assert hero[a][C["Legacy action"]] == "Burst Projectile"
    out[a] = [
        delivery(a, "First hit Projectile", count="1", spread=D, cond="If 1st or 2nd Cast"),
        setrow(delivery(a, "", count="3", spread="Current + Left + Right", cond="If 3rd Cast"),
               **{"Legacy action": ""}),        # same action as the branch above: blank, it merges
        effect(burst(a, "2", "1", "Circle 1 hex"), a),
    ]
    out[b] = []                                          # its branch is folded into the rows above

    # --- JAYCE: one projectile at step 2 -> burst becomes step 3 ---------------------------------
    j = [i for i in champ_rows("Jayce") if hero[i][C["Legacy action"]] == "Burst Projectile"][0]
    out[j] = [delivery(j, "First hit Projectile"), effect(burst(j, "3", "2", "Circle 1 hex"), j)]

    # --- APHELIOS: insert the burst as step 2; his old step 2 shifts to 3 -------------------------
    ap = champ_rows("Aphelios")
    p = [i for i in ap if hero[i][C["Legacy action"]] == "Homing Burst Projectile"][0]
    out[p] = [delivery(p, "Homing Projectile"), effect(burst(p, "2", "1", "Circle 2 hex"), p)]
    for i in ap:                                         # the Chakram step now follows the BURST
        if hero[i][C["Step"]].strip() == "2" and hero[i][C["Legacy action"]].strip() == "Cast":
            hero[i][C["Step"]] = "3"
            hero[i][C["Trigger (When)"]] = "After Step 2"

    # --- TEEMO: one projectile; the 4-star branch moves to the BURST, where the radius differs ----
    t = champ_rows("Teemo")
    t1, t1w, t2, t2w = t[0], t[1], t[2], t[3]
    assert hero[t1][C["Condition (Only if)"]] == "If not 4-Star"
    out[t1] = [
        delivery(t1, "Homing Projectile", cond=D),
        effect(burst(t1, "2", "1", "Circle 1 hex", cond="If not 4-Star"), t1),
        effect(blank(), t1w),
        effect(setrow(burst(t2, "", "1", "Circle 2 hex", cond="If 4-Star"),
                      **{"Step": "", "Skill Type": "", "Trigger (When)": "",
                         "Action Source": "", "Legacy action": "", "Aim Target": "",
                         "Offset": "", "Skill Range": "", "Count": "", "Spread": "",
                         "Cast (s)": ""}), t2),
        effect(blank(), t2w),
    ]
    out[t1w] = out[t2] = out[t2w] = []

    # --- HEIMERDINGER --------------------------------------------------------------------------
    hd = champ_rows("Heimerdinger")
    p = [i for i in hd if hero[i][C["Legacy action"]] == "Homing Burst Projectile"][0]
    stun = hd[hd.index(p) + 1]
    out[p] = [delivery(p, "Homing Projectile"),
              effect(burst(p, "2", "1", "Circle 2 hex"), p), effect(blank(), stun)]
    out[stun] = []

    # --- SONA: Wave -> Pierce Projectile; its box shape is the ROW's now ------------------------
    for i in champ_rows("Sona"):
        if hero[i][C["Legacy action"]] == "Wave":
            hero[i][C["Legacy action"]] = "Pierce Projectile"

    # Rebuild with the replacements spliced in.
    #
    # CARRY THE IDENTITY BLOCK ACROSS. A replaced row may be the one holding the champion's name,
    # cost, origin and skill text (cols 0-9) — the block every other row of theirs inherits by being
    # blank. The replacement rows are built fresh and have none of it, so replacing a champion's FIRST
    # row silently deletes the champion: Aphelios, Teemo and Heimerdinger vanished from the sheet
    # entirely on the first run of this, while Karma and Jayce survived only because their identity
    # happened to sit on an earlier row.
    new, dropped = [H], 0
    for i in range(1, len(hero)):
        if i not in out:
            new.append(hero[i])
            continue
        ident = hero[i][:10]
        if any(x.strip() for x in ident):
            if not out[i]:
                raise SystemExit(f"row {i} carries a champion identity ({ident[0]!r}) and would be "
                                 f"deleted outright — it must be replaced, not dropped.")
            out[i][0][:10] = ident
            dropped += 1
        new.extend(out[i])
    hero = new
    print(f"hero.csv: {len(hero) - 1} rows (was {len(read('hero.csv')) - 1}); "
          f"{dropped} identity blocks carried onto their replacement row")

    # --- every plain projectile row states its own shape ----------------------------------------
    act, n = "", 0
    for r in hero[1:]:
        if r[C["Legacy action"]].strip():
            act = r[C["Legacy action"]].strip()
        if act in PROJECTILES and r[C["AOE (hex)"]].strip() == D:
            r[C["AOE (hex)"]] = "1-hex"
            n += 1
    write("hero.csv", hero)
    print(f"  {n} projectile rows: AOE '{D}' -> '1-hex'")

    # --- reference tabs --------------------------------------------------------------------------
    am = read("action-model.csv")
    ah = am[0]
    doc_at = next(i for i, r in enumerate(am) if not any(x.strip() for x in r))
    body = [r for r in am[1:doc_at] if r[0].strip() not in RETIRE]
    for r in body:
        if r[0].strip() in PROJECTILES:
            r[ah.index("Shape")] = ELSEWHERE
            r[ah.index("Clarify more")] = (
                r[ah.index("Clarify more")].rstrip() + " SHAPE IS PER-ROW: a projectile's own hitbox "
                "is in the row's AOE (hex) — a 1-hex bolt for most, Box 1.5x2 for Sona's wave. And it "
                "is the PROJECTILE's shape, never the shape of anything it bursts into: a burst is a "
                "separate step (trigger 'On Projectile Hit', source 'Step N Projectile').").strip()
    write("action-model.csv", [ah] + body + am[doc_at:])
    print(f"action-model.csv: {len(body)} actions (retired {RETIRE}); "
          f"{len(PROJECTILES)} projectiles -> Shape '{ELSEWHERE}'")

    aoe = read("aoe-shape.csv")
    if not any(r and r[0].strip() == "1-hex" for r in aoe):
        i = next(k for k, r in enumerate(aoe) if r and r[0].strip() == "Circle 1 hex")
        aoe.insert(i, ["1-hex", "1-hex", "One hex — a bolt, not an area. The default projectile.",
                       "x\no"])
        write("aoe-shape.csv", aoe)
        print("aoe-shape.csv: +1-hex")

    et = read("effect-types.csv")
    for r in et:
        if len(r) > 1 and r[1].strip() == "(setup / daggers)":
            r[1] = "(setup)"
            r[2] = ("A step with no payload of its own — it only sets up the step that follows. "
                    "Katarina throwing her daggers before she blinks; a projectile that flies so its "
                    "burst can land. Was '(setup / daggers)', which put one champion's ability in the "
                    "vocabulary.")
    write("effect-types.csv", et)
    for r in hero[1:]:
        if r[C["Effect Detail"]].strip() == "(setup / daggers)":
            r[C["Effect Detail"]] = "(setup)"
    write("hero.csv", hero)
    print("effect-types.csv: '(setup / daggers)' -> '(setup)'")


if __name__ == "__main__":
    main()
