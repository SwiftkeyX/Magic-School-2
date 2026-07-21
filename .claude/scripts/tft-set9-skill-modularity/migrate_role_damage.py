"""ONE-SHOT (2026-07-21): normalise `Role` to 5 nouns and add the `Damage Type` column.

    python .claude/scripts/tft-set9-skill-modularity/migrate_role_damage.py [--apply]

Without --apply it prints the report and writes nothing.

WHY THIS IS ONE-SHOT AND GUARDED: Set 10's damage type is read off the AD/AP prefix of the OLD
`Role` values (`ADTank`, `APCaster`), which this same script overwrites. Run it twice and the
second run has no prefix left to read. It therefore REFUSES if `Damage Type` is already a column.
Archive it after the CSVs are committed.

Two columns, two different provenances — stated on the tabs so nobody mistakes one for the other:

  Role         COPIED from `Archetype Review`, which is the user's reviewed judgement (his 14
               corrections plus the 4 hard-coded disagreements with the source). Not re-derived
               here: build_archetype_review.py owns that logic and becomes a passthrough after
               this migration, because the column it used to read is now the column it writes.

  Damage Type  Set 10: STATED by the source (`ADTank` -> AD). Authoritative, no inference.
               Set 9:  DERIVED — the stat the champion's ABILITY DAMAGE scales on, where
               "damage" means an `Attack` category effect row. Utility scaling (a shield or
               heal that happens to scale AP) is deliberately ignored, which is what separates
               Warwick — an AD auto-attacker whose only AP number is a heal — from a real mage.

The derivation was validated against Set 10's stated prefixes before being trusted on Set 9:
59 of 60. The single miss is Olaf, and he misses for the honest reason — his ability deals no
scaled damage at all, so the rule reads a utility number instead of reading damage wrongly. That
same failure mode is why ABSTAIN below is a hand-call list rather than a fallback heuristic: when
there is no damage scaling, guessing from whatever number is left is exactly what got Olaf wrong.
"""

import collections
import csv
import pathlib
import re
import sys

DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")
ROLES = {"Tank", "Fighter", "Mage", "Marksman", "Assassin"}

# The 7 Set 9 champions whose ability deals no AD/AP-scaled damage, so the rule abstains.
# `—` is not a gap here, it is the answer: these two scale on neither stat.
ABSTAIN = {
    "Orianna": "AP",    # entire kit is % AP — shield + empowered attack
    "Maokai": "AP",     # Empowered Attack 220/260/300% AP
    "Taric": "AP",      # Shield 500/580/680% AP
    "Kled": "AD",       # only AP number is an Attack Speed buff; his damage is autos
    "Warwick": "AD",    # only AP number is a heal; his damage is autos
    "Cho'Gath": "—",    # 12% of the TARGET's max HP — neither stat
    "Ryze": "—",        # 150/200/300% of his own Armor + MR — neither stat
}


def rd(name):
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return list(csv.reader(f))


def wr(name, rows):
    with (DATA / name).open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)


def tier2(amount):
    """Collapse `a/b/c` to its MIDDLE value — the user's rule: tier 3 is a luxury players
    don't reach and it skews every comparison (Senna's beam is 2000% AD at tier 3)."""
    return re.sub(r"(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)", lambda m: m.group(2), amount)


def review_roles():
    """(set, champion) -> role, from the Archetype Review tab. Rows below the champion block are
    the tab's prose legend; they are skipped by requiring a real role in the Role column."""
    out = {}
    rows = rd("archetype-review.csv")
    head = rows[0]
    si, ci, ri = head.index("Set"), head.index("Champion"), head.index("Role")
    for r in rows[1:]:
        if len(r) > ri and r[si].strip() in ("S9", "S10") and r[ri].strip() in ROLES:
            out[(r[si].strip(), r[ci].strip())] = r[ri].strip()
    return out


def damage_type(rows, cat_i, amt_i):
    """The stat this champion's ability DAMAGE scales on, or None when it deals none.

    Returning None rather than falling back to "whatever percentage is left" is the whole point:
    the fallback is what made Olaf — an AD tank whose only scaled number is an AP utility buff —
    come out AP on the Set 10 ground-truth check.
    """
    best = {"AD": 0.0, "AP": 0.0}
    for r in rows:
        amount = r[amt_i].strip() if len(r) > amt_i else ""
        if not amount or amount == "—":
            continue
        if (r[cat_i].strip() if len(r) > cat_i else "") != "Attack":
            continue
        for pct, kind in re.findall(r"(\d+(?:\.\d+)?)%\s*(AD|AP)", tier2(amount)):
            best[kind] = max(best[kind], float(pct))
    if best["AD"] == best["AP"]:
        return None
    return "AD" if best["AD"] > best["AP"] else "AP"


def migrate(csv_name, set_key, roles, report):
    rows = rd(csv_name)
    head = rows[0]
    if "Damage Type" in head:
        sys.exit("REFUSED: %s already has a Damage Type column — this script is one-shot, and "
                 "Set 10's damage type can only be read off the ORIGINAL role prefix." % csv_name)
    ci, ri = head.index("Champion"), head.index("Role")
    cat_i, amt_i = head.index("Effect Category"), head.index("Amount")

    # Group by champion. The identity block is MERGED, so only a champion's FIRST row carries a
    # value and every later row is a deliberate blank meaning "same as above" (invariant #2).
    blocks, order = collections.defaultdict(list), []
    cur = None
    for r in rows[1:]:
        if len(r) > ci and r[ci].strip():
            cur = r[ci].strip()
            order.append(cur)
        blocks[cur].append(r)

    old_role, new_dmg, new_role = {}, {}, {}
    for champ in order:
        old = next((r[ri].strip() for r in blocks[champ] if len(r) > ri and r[ri].strip()), "")
        old_role[champ] = old
        if set_key == "S10":
            # STATED, not inferred: the source spells the damage type into the role itself.
            new_dmg[champ] = old[:2] if old[:2] in ("AD", "AP") else "—"
        else:
            derived = damage_type(blocks[champ], cat_i, amt_i)
            new_dmg[champ] = derived if derived else ABSTAIN[champ]
            if not derived:
                report.append(("ABSTAIN", set_key, champ, old, new_dmg[champ]))
        new_role[champ] = roles[(set_key, champ)]

    # Rewrite: Role gets the normalised noun, Damage Type is inserted directly after it. Both are
    # identity columns, so both are written ONLY on the champion's first row — writing them on
    # every row would break remerge_hero, which splits a block on any non-blank cell (invariant #6).
    out = [head[:ri + 1] + ["Damage Type"] + head[ri + 1:]]
    cur = None
    for r in rows[1:]:
        r = list(r) + [""] * (len(head) - len(r))
        if r[ci].strip():
            cur = r[ci].strip()
            role_cell, dmg_cell = new_role[cur], new_dmg[cur]
        else:
            role_cell, dmg_cell = "", ""
        out.append(r[:ri] + [role_cell, dmg_cell] + r[ri + 1:])

    for champ in order:
        report.append(("ROLE", set_key, champ, old_role[champ],
                       "%s / %s" % (new_role[champ], new_dmg[champ])))
    return out, len(order)


def main():
    apply = "--apply" in sys.argv
    roles = review_roles()
    report = []
    results = {}
    for csv_name, set_key in (("hero.csv", "S9"), ("hero-set10.csv", "S10")):
        rows = rd(csv_name)
        ci = rows[0].index("Champion")
        champs = {r[ci].strip() for r in rows[1:] if len(r) > ci and r[ci].strip()}
        missing = sorted(c for c in champs if (set_key, c) not in roles)
        if missing:
            sys.exit("REFUSED: no reviewed Role for %s: %s" % (set_key, missing))
        results[csv_name] = migrate(csv_name, set_key, roles, report)

    abstains = [x for x in report if x[0] == "ABSTAIN"]
    print("Set 9 abstentions (hand calls, no ability damage scaling): %d" % len(abstains))
    for _, s, c, old, new in abstains:
        print("   %-4s %-12s old Role %-8s -> Damage Type %s" % (s, c, old, new))

    for csv_name, (out, n) in results.items():
        head = out[0]
        ri, di = head.index("Role"), head.index("Damage Type")
        rc = collections.Counter(r[ri] for r in out[1:] if r[ri])
        dc = collections.Counter(r[di] for r in out[1:] if r[di])
        print("\n%s — %d champions, %d columns" % (csv_name, n, len(head)))
        print("   Role:        %s" % dict(rc.most_common()))
        print("   Damage Type: %s" % dict(dc.most_common()))
        assert sum(rc.values()) == n and sum(dc.values()) == n, "identity cell count != champions"
        assert set(rc) <= ROLES, "off-vocabulary role: %s" % (set(rc) - ROLES)
        assert set(dc) <= {"AD", "AP", "—"}, "off-vocabulary damage type: %s" % set(dc)

    if apply:
        for csv_name, (out, _) in results.items():
            wr(csv_name, out)
        print("\nWRITTEN. Next: sheet-side column insert, then force_full + sync.")
    else:
        print("\nDry run — nothing written. Re-run with --apply.")


if __name__ == "__main__":
    main()
