"""ONE-SHOT: collapse Hero's five action axes back into a single `Legacy action` key.

    python .claude/scripts/tft-set9-skill-modularity/migrate_legacy_action.py

Rewrites data/hero.csv (36 -> 32 cols) and data/action-model.csv (adds Shape + the missing rows).
Run ONCE, then archive/. It is NOT idempotent against a sheet — it only rewrites the CSVs; the
sheet-side column delete is migrate_legacy_action_sheet.py, and sync.py does the rest.

WHY: Apply/Spawn/Motion/Behavior/Shape are functionally determined by the action's NAME — verified
below on all 135 action rows. Storing them per-row was ~200 rows restating a 23-row lookup, which can
only drift. The axes move to the Action Model tab (which already had them as columns), Hero keeps the
key, and the reader follows the key. `Auto-Attack` is the ONE name that genuinely split (melee
DirectApply vs ranged Hitbox), so it becomes two names — the tab already had both rows.

Collision does NOT move: it splits per-row (Burst Projectile is First-Hit on 3 rows, Target-Only on 1),
so it is real per-row data. Same for Offset (Circle/Box AOE vary) and AOE size.

THE ASSERT IS THE POINT. This refuses to write unless every axis cell it drops is reproducible from
the name it keeps, so the migration cannot lose data quietly.
"""

import csv
import pathlib
import subprocess

DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")
D = "—"
AXES = ["Apply", "Spawn", "Motion", "Behavior", "Shape"]
V1 = "0db5e27~1:.claude/scripts/tft-set9-skill-modularity/data/hero.csv"

# v1 name -> the name used from here on. Only Auto-Attack changes MEANING (its axes split by range);
# the rest are renames that make the tab's key exact-matchable: the champion parentheticals
# ("Sweep Laser (Gwen)") are annotations, not part of the name, and belong in `Clarify more`.
# Leap -> Move answers the user's open sheet comment ("Leap is too vague. Let's use 'Move' instead.").
# The two stay DISTINCT — same axes, but "behind" is real positional intent a lookup should not
# swallow, and the reason Katarina/Zed read differently from Jarvan.
RENAME = {
    "QuickAA": "Auto-Attack (ranged) / QuickAA",
    "Leap": "Move",
    "Leap Behind": "Move Behind",
}

# Prose for the three actions Hero uses that the hand-made tab never got a row for. Recovered from
# the v1 action-model.csv (0db5e27~1) rather than rewritten — it is the user's own text.
RESTORED = {
    "Burst Projectile": (
        "Projectile that flies at the aim target and DETONATES on impact, hitting everyone in an "
        "X-hex circle.",
        "Has travel speed. = First hit Projectile + Circle AOE. It detonates on the FIRST body it "
        "meets, which may not be the unit it was aimed at, and the circle is centred on that IMPACT "
        "hex. If the projectile instead passes THROUGH and detonates on its aim target, that is "
        "Homing Burst Projectile (Aphelios), not this."),
    "Homing Burst Projectile": (
        "Projectile that HOMES on the aim target, passing through everything on the way, and "
        "detonates on it in an X-hex circle.",
        "Has travel speed. = Homing Projectile + Circle AOE. Do NOT confuse with Burst Projectile, "
        "which is First-Hit: that one detonates on the FIRST body it meets, which may not be the "
        "unit it was aimed at. Aphelios' moon blast passes THROUGH heroes and explodes on the "
        "clustered target it was aimed at - the user's correction. Same circle, different delivery."),
    "Current Target Laser": (
        "Beam locked onto the aimed target ONLY, applying its effect over a duration.",
        "NO travel speed. Nothing between the unit and the target is touched (Lux)."),
}


def fill_down(seq):
    """Resolve a merged column to its EFFECTIVE values: a blank inherits the row above.

    Collision and Offset are RUN columns — a blank is not "missing", it is "same as above" (K'Sante's
    Leap reads blank and inherits None). Deriving per-action values from the RAW cells invents splits
    that are not there.
    """
    out, prev = [], ""
    for v in seq:
        if v.strip():
            prev = v
        out.append(prev)
    return out


def read_csv(p):
    with p.open(encoding="utf-8", newline="") as f:
        return [r for r in csv.reader(f)]


def write_csv(p, rows):
    with p.open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)


def trim(rows):
    rows = list(rows)
    while rows and not any(c.strip() for c in rows[-1]):
        rows.pop()
    return rows


def legacy_name(v1_action, apply_):
    """The v1 name, except Auto-Attack — the one action whose axes are NOT determined by its name."""
    if v1_action == "Auto-Attack":
        return "Auto-Attack (melee)" if apply_ == "DirectApply" else "Auto-Attack (ranged) / QuickAA"
    return RENAME.get(v1_action, v1_action)


def main():
    old = trim(list(csv.reader(subprocess.run(
        ["git", "show", V1], capture_output=True, text=True, encoding="utf-8").stdout.splitlines())))
    new = trim(read_csv(DATA / "hero.csv"))
    assert len(old) == len(new), f"row count moved: v1 {len(old)} vs v2 {len(new)}"

    oi = old[0].index("Action")
    ni = {a: new[0].index(a) for a in AXES}

    # 1. Derive name -> axes, and PROVE the mapping is a function (one axis-tuple per name).
    seen, rows = {}, []
    for o, n in zip(old[1:], new[1:]):
        act = o[oi].strip()
        axes = tuple(n[ni[a]].strip() for a in AXES)
        if not act:                                  # continuation row: axes must be blank
            assert axes == ("", "", "", "", ""), f"continuation row carries axes: {axes}"
            rows.append("")
            continue
        name = legacy_name(act, axes[0])
        if name in seen:
            assert seen[name] == axes, (
                f"NOT A FUNCTION — {name!r} maps to both {seen[name]} and {axes}. "
                f"Collapsing would LOSE the difference. Split the name first.")
        seen[name] = axes
        rows.append(name)

    print(f"round-trip ok: {len(seen)} names determine the axes on "
          f"{sum(1 for r in rows if r)} action rows")

    # 2. hero.csv — the 5 axis columns become one key, in the same slot (col 15, after Action Source).
    at = ni["Apply"]
    out = [new[0][:at] + ["Legacy action"] + new[0][at + len(AXES):]]
    for r, name in zip(new[1:], rows):
        out.append(r[:at] + [name] + r[at + len(AXES):])
    assert all(len(r) == 32 for r in out), "hero.csv must be 32 columns"
    write_csv(DATA / "hero.csv", out)
    print(f"hero.csv: {len(out[0])} cols ({len(new[0])} before), {len(out) - 1} data rows")

    # 3. action-model.csv — add Shape (derived), add the rows Hero uses that the tab never had,
    #    split Leap, and de-parenthesise the keys so the name matches Hero exactly.
    am = trim(read_csv(DATA / "action-model.csv"))
    hdr = am[0]
    bi, oc = hdr.index("Behavior"), hdr.index("Offset")

    def split_row(r):
        return r[:bi + 1] + [""] + r[bi + 1:]        # Shape slot after Behavior

    doc_at = next(i for i, r in enumerate(am) if not any(c.strip() for c in r))
    body, doc = [split_row(r) for r in am[1:doc_at]], [split_row(r) for r in am[doc_at:]]
    head = hdr[:bi + 1] + ["Shape"] + hdr[bi + 1:]

    # Split the lumped Leap row and rename it per the user's comment; the two are separate Hero names.
    for i, r in enumerate(body):
        if r[0] == "Leap / Leap Behind":
            behind = list(r)
            r[0], behind[0] = "Move", "Move Behind"
            r[-2] = "Self moves to the target hex - a reposition."
            behind[-2] = ("Self moves to the hex BEHIND the target - a reposition that ends up on "
                          "the far side of it.")
            body.insert(i + 1, behind)
            break

    # De-parenthesise: the key must match Hero's cell exactly, so the champion note moves to prose.
    for r in body:
        if "(" in r[0] and not r[0].startswith("Auto-Attack"):
            name, note = r[0].split(" (", 1)
            r[0] = name.strip()
            who = note.rstrip(")")
            r[-1] = (f"{who}'s. " + r[-1]).strip()

    known = {r[0] for r in body}
    for name in sorted(seen):
        if name not in known:
            body.append([name] + [""] * (len(head) - 1))
            print(f"  + new tab row: {name}")

    # Fill Shape (and any blank axis on the new rows) from the data — never hand-typed.
    hero_rows = trim(read_csv(DATA / "hero.csv"))
    hc = {n: hero_rows[0].index(n)
          for n in ("Legacy action", "Collision (If it have one)", "Offset")}

    def observed(col):
        """name -> set of EFFECTIVE values seen on that action's rows."""
        eff = fill_down([r[hc[col]] for r in hero_rows[1:]])
        out = {}
        for r, e in zip(hero_rows[1:], eff):
            name = r[hc["Legacy action"]].strip()
            if name:
                out.setdefault(name, set()).add(e.strip())
        return out

    coll, offs = observed("Collision (If it have one)"), observed("Offset")

    def per_action(vals):
        """One value = a property OF THE ACTION. More = real per-row data; say so, don't pick one."""
        vals = vals - {""}
        return next(iter(vals)) if len(vals) == 1 else "per row"

    # The tab is the USER'S document. Fill what is blank; never overwrite what they wrote. Where their
    # value disagrees with the data, REPORT it — do not pick a side. Their values are principled (the
    # tab's own rule is "DirectApply projects no hitbox, so Collision is None") and the Hero data does
    # not always honour that, so an auto-overwrite would quietly encode the data's bug into the doc.
    disagree = []
    for r in body:
        name = r[0]
        if name not in seen:
            continue
        for k, a in enumerate(AXES):
            slot = head.index(a)
            if a == "Shape" or not r[slot].strip():
                r[slot] = seen[name][k] or D
        # Offset: fill the new rows only. The tab's Offset column documents where a hitbox is MEANT to
        # sit; Hero writes '—' for every action with no AOE. Those two are answering different
        # questions, so diffing them just manufactures 14 non-findings. Collision is a straight
        # same-question disagreement and IS worth surfacing.
        if not r[head.index("Offset")].strip():
            r[head.index("Offset")] = per_action(offs[name]) or D
        slot, want = head.index("Collision"), per_action(coll[name])
        if not r[slot].strip():
            r[slot] = want or D
        elif r[slot].strip() != want and want:
            disagree.append((name, "Collision", r[slot].strip(), want))
        if name in RESTORED:
            r[head.index("What it does")], r[head.index("Clarify more")] = RESTORED[name]

    if disagree:
        print("\n  !! tab and Hero data DISAGREE (tab kept as written — your call):")
        for name, label, mine, want in disagree:
            print(f"       {name:31} {label:9} tab={mine!r:14} data={want!r}")

    # The doc block's axis list and its closing note both describe the OLD layout. Insert the Shape
    # line, then fix the note — separate passes, or the insert's `break` skips the note entirely.
    for i, r in enumerate(doc):
        if r[0] == "Offset":                          # the Shape axis line goes above Offset
            doc.insert(i, ["Shape", "1-hex | circle | cone | box | custom",
                           "(Hitbox only)"] + [""] * (len(head) - 3))
            break
    for r in doc:
        if r[0].startswith("SHAPE / SIZE lives in the HERO tab"):
            r[0] = ("SHAPE is per-ACTION and lives HERE — a Circle AOE is always a circle. SIZE stays "
                    "in the HERO tab (the AOE (hex) column), because the radius is per row. Collision "
                    "and Offset also stay in Hero: they are mostly per-action and are shown here for "
                    "reference, but where an action genuinely varies they read 'per row' and the Hero "
                    "cell is the truth.")
    write_csv(DATA / "action-model.csv", [head] + body + doc)
    print(f"action-model.csv: {len(body)} actions, {len(head)} cols")


if __name__ == "__main__":
    main()
