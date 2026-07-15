"""One batched read of everything you need BEFORE modelling a champion into the tft-set9-skill sheet.

Run from repo-root cwd (set PYTHONIOENCODING=utf-8 — the data has em-dashes and ×):

    python .claude/scripts/tft-set9-skill-modularity/context.py            # conventions + reference lists
    python .claude/scripts/tft-set9-skill-modularity/context.py --validate # local used-vs-defined check
    python .claude/scripts/tft-set9-skill-modularity/context.py --origin Void   # + source rows (network)

This exists so the `/add-champion` workflow does NOT re-derive the schema with ~7 separate queries
(that is what burned tokens). One command prints the header, the merge model, the conventions that
bite, and every reference value `sync.py` VALIDATE enforces. See the `add-champion` skill.
"""

import csv
import pathlib
import sys

from sheet import (CRED, D, HERO_COLUMNS, IDENTITY_BLOCK, RUN_COLUMNS, STEP_BLOCK, cols)

DATA = pathlib.Path(".claude/scripts/tft-set9-skill-modularity/data")
SOURCE_KEY = "1xj6em5XlvIN1gWHTKOPDsssmkgnS3jIsaLnAMjYyPUA"  # tft-set9 (Champions/Origins/Classes)


def rd(name):
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return [r for r in csv.reader(f)]


def col0(name):
    """First-column values of a reference tab (the 'defined' set), header dropped.

    Stops at the first all-blank row — every reference CSV ends with a blank separator then a
    'How to read this tab' prose block, and those are documentation, not values."""
    out = []
    for r in rd(name)[1:]:
        if not any(c.strip() for c in r):
            break
        if r[0].strip():
            out.append(r[0].strip())
    return sorted(out)


def hero():
    rows = rd("hero.csv")
    while rows and not any(c.strip() for c in rows[-1]):
        rows.pop()
    return rows


def print_schema():
    h = hero()
    hdr = h[0]
    per_effect = [n for n in HERO_COLUMNS if n not in set(IDENTITY_BLOCK) | set(STEP_BLOCK) | set(RUN_COLUMNS)]
    print("=== HERO SCHEMA (%d cols) ===" % len(hdr))
    for i, c in enumerate(hdr):
        print("  %2d  %s" % (i, c))
    print("\n=== MERGE MODEL (how a blank is read) ===")
    print("  IDENTITY (merged down a champion): ", IDENTITY_BLOCK)
    print("  STEP BLOCK (span a whole step)   : ", STEP_BLOCK, "  <- compared RAW, blank=continuation")
    print("  RUN COLUMNS (merge by value-run) : ", RUN_COLUMNS, "  <- blank inherits the row ABOVE")
    print("  PER-EFFECT (always filled)       : ", per_effect)
    print("\n=== CONVENTIONS THAT BITE ===")
    print("  * A blank RUN cell inherits the row above (whole-column fill_down). So a DEFINING row")
    print("    with no condition must write '%s', NOT blank, or it inherits the champion above." % D)
    print("  * 'not applicable' is the em-dash '%s', never blank. Blank = 'same as above' / continuation." % D)
    print("  * Cast/Leap -> Count '%s'. Star-varying counts use slash notation: '6/6/25'." % D)
    print("  * Continuation rows: blank cols 0..Aim Target, fill effect cols. Identity blank except row 1.")
    print("  * %d champions currently in hero.csv." % len({r[0].strip() for r in h[1:] if r and r[0].strip()}))


def print_reference():
    print("\n=== REFERENCE VALUES (sync.py VALIDATE enforces these) ===")
    print("  Actions      :", col0("action-model.csv"))
    print("  Collisions   :", col0("collision-types.csv"))
    print("  Spreads      :", col0("spread-types.csv"))
    print("  Scaling Types:", col0("scaling-types.csv"))
    pairs = sorted({(r[0].strip(), r[1].strip()) for r in rd("effect-types.csv")[1:] if len(r) > 1 and r[0].strip()})
    print("  Effect pairs (Category / Detail):")
    for cat, det in pairs:
        print("      %-9s / %s" % (cat, det))


def validate():
    """Replicate sync.py's used-vs-defined check on the CSVs — no network round-trip."""
    h = hero()
    c = cols(h[0])

    def used(name):
        i = c[name]
        return {r[i].strip() for r in h[1:] if len(r) > i} - {"", D}

    defined = {"Action": set(col0("action-model.csv")), "Collision": set(col0("collision-types.csv")),
               "Scaling Type": set(col0("scaling-types.csv")), "Spread": set(col0("spread-types.csv"))}
    pairs = {(r[c["Effect Category"]].strip(), r[c["Effect Detail"]].strip())
             for r in h[1:] if len(r) > c["Effect Detail"]} - {("", "")}
    effects = {(r[0].strip(), r[1].strip()) for r in rd("effect-types.csv")[1:] if len(r) > 1}

    problems = []
    for label in defined:
        miss = used(label) - defined[label]
        if miss:
            problems.append("%s: %s used but not defined" % (label, sorted(miss)))
    orphan = sorted(p for p in pairs if p not in effects and all(p))
    if orphan:
        problems.append("Effect pairs undefined: %s" % orphan)
    print("\n=== LOCAL VALIDATE ===")
    print("  PROBLEMS:", problems if problems else "NONE — ok")
    return not problems


def print_source(origin):
    """Print the source champion rows for an origin from tft-set9 -> Champions (the one network call)."""
    import gspread
    ch = gspread.service_account(filename=CRED).open_by_key(SOURCE_KEY).worksheet("Champions").get_all_values()
    hdr = ch[0]
    o1, o2, name, skill = hdr.index("Origin 1"), hdr.index("Origin 2"), hdr.index("Champion Name"), hdr.index("Skill Description")
    cost, role, c1, c2 = hdr.index("Cost"), hdr.index("Design Role"), hdr.index("Class 1"), hdr.index("Class 2")
    rng = hdr.index("Range")
    hits = [r for r in ch[1:] if len(r) > o2 and origin.lower() in (r[o1].lower(), r[o2].lower())]
    print("\n=== SOURCE: tft-set9 -> Champions, Origin '%s' (%d) ===" % (origin, len(hits)))
    for r in hits:
        print("  %-9s | %-7s | %-6s | %s%s | %s%s | R%s" % (
            r[name], r[cost], r[role], r[o1], ("/" + r[o2] if r[o2] else ""),
            r[c1], ("/" + r[c2] if r[c2] else ""), r[rng] if len(r) > rng else "?"))
        print("      %s" % (r[skill] or "").replace("\n", " "))


def main():
    args = sys.argv[1:]
    if "--validate" in args:
        sys.exit(0 if validate() else 1)
    print_schema()
    print_reference()
    if "--origin" in args:
        print_source(args[args.index("--origin") + 1])


if __name__ == "__main__":
    main()
