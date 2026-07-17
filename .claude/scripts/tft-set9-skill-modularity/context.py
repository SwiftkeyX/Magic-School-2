"""One batched read of everything you need BEFORE modelling a champion into the tft-set9-skill sheet.

Run from repo-root cwd (set PYTHONIOENCODING=utf-8 — the data has em-dashes and ×):

    python .claude/scripts/tft-set9-skill-modularity/context.py            # conventions + reference lists
    python .claude/scripts/tft-set9-skill-modularity/context.py --validate # local used-vs-defined check
    python .claude/scripts/tft-set9-skill-modularity/context.py --origin Void   # + source rows (network)
    python .claude/scripts/tft-set9-skill-modularity/context.py --missing       # champions not yet added

This exists so the `/add-champion` workflow does NOT re-derive the schema with ~7 separate queries
(that is what burned tokens). One command prints the header, the merge model, the conventions that
bite, and every reference value `sync.py` VALIDATE enforces. See the `add-champion` skill.
"""

import csv
import pathlib
import sys

from sheet import (CRED, D, HERO_COLUMNS, IDENTITY_BLOCK, RUN_COLUMNS, STEP_BLOCK, fill_down,
                   validate_data)

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
    print("  * Cast/Move -> Count '%s'. Star-varying counts use slash notation: '6/6/25'." % D)
    print("  * Continuation rows: blank cols 0..Aim Target, fill effect cols. Identity blank except row 1.")
    print("  * %d champions currently in hero.csv." % len({r[0].strip() for r in h[1:] if r and r[0].strip()}))


def print_actions():
    """The Action Model tab, printed as the lookup it is: pick a name, the axes come with it."""
    rows = rd("action-model.csv")
    hdr = rows[0]
    show = [hdr.index(n) for n in ("Legacy Action", "Apply", "Spawn", "Motion", "Behavior", "Shape",
                                   "Collision")]
    print("\n=== ACTIONS (Hero's `Legacy action` must match one of these EXACTLY) ===")
    print("  %-31s %-12s %-9s %-14s %-10s %-7s %s" % tuple(hdr[i] for i in show))
    for r in rows[1:]:
        if not any(c.strip() for c in r):
            break                                    # the AXES doc block below is not data
        if r[0].strip():
            print("  %-31s %-12s %-9s %-14s %-10s %-7s %s" % tuple(r[i] for i in show))
    print("  ('per row' = varies per Hero row; the Hero cell is the truth, not this tab.)")


def print_reference():
    print("\n=== REFERENCE VALUES (sync.py VALIDATE enforces these) ===")
    print("  Triggers     :", col0("trigger-types.csv"))
    print("  Collisions   :", col0("collision-types.csv"))
    print("  Spreads      :", col0("spread-types.csv"))
    print("  Scaling Types:", col0("scaling-types.csv"))
    # Offset is checked like the rest now, so a champion-adder has to be able to SEE the legal
    # anchors. An enforced vocabulary that the adding tool never prints is a trap, not a guard.
    print("  Offsets      :", col0("offset-types.csv"))
    # Effect Types is MERGED by category, so its Category cell is blank on every row but a block's
    # first. Filtering on `r[0].strip()` here would silently print 6 pairs instead of 44 - the blank
    # is data ("same as above"), not an empty row.
    et = [r for r in rd("effect-types.csv")[1:] if len(r) > 1]
    pairs = sorted(set(zip([v.strip() for v in fill_down([r[0] for r in et])],
                           [r[1].strip() for r in et])))
    print("  Effect pairs (Category / Detail), %d in %d merged blocks:"
          % (len(pairs), len({c for c, _ in pairs})))
    for cat, det in pairs:
        print("      %-9s / %s" % (cat, det))


def validate():
    """sync.py's used-vs-defined check, run on the CSVs — no network round-trip.

    It CALLS sync's check rather than restating it. This was a second copy, and it drifted the day
    Effect Types gained a merge: sync learned that a blank category means 'same as above' and this did
    not, so identical CSVs passed one and failed the other with 36 phantom errors.
    """
    problems = validate_data()
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


EXCLUDED_95 = set()  # nothing is excluded any more: the tab covers the FULL Set 9 roster (9.0
                    # + 9.5, all 75). Fiora/Quinn/Xayah were held out while it was 9.0-only.


def print_missing():
    """Which source champions are NOT in hero.csv yet, grouped by origin (the live remaining roster)."""
    import gspread
    from collections import defaultdict
    ch = gspread.service_account(filename=CRED).open_by_key(SOURCE_KEY).worksheet("Champions").get_all_values()
    h = ch[0]
    nm, o1, o2 = h.index("Champion Name"), h.index("Origin 1"), h.index("Origin 2")
    have = {r[0].strip() for r in hero()[1:] if r and r[0].strip()}
    src = [(r[nm].strip(), r[o1].strip(), r[o2].strip()) for r in ch[1:] if len(r) > o2 and r[nm].strip()]
    missing = [(n, a, b) for n, a, b in src if n not in have]
    to_add = [n for n, a, b in missing if n not in EXCLUDED_95]
    print("=== ROSTER: %d in sheet, %d in source, %d missing (%d to add + %d excluded 9.5) ==="
          % (len(have), len(src), len(missing), len(to_add), len(missing) - len(to_add)))
    by = defaultdict(list)
    for n, a, b in missing:
        by[a].append(n + ("/" + b if b else "") + ("  [excluded 9.5]" if n in EXCLUDED_95 else ""))
    for o in sorted(by):
        print("  %-14s %s" % (o, ", ".join(by[o])))


def main():
    args = sys.argv[1:]
    if "--missing" in args:
        print_missing(); return
    if "--validate" in args:
        sys.exit(0 if validate() else 1)
    print_schema()
    print_actions()
    print_reference()
    if "--origin" in args:
        print_source(args[args.index("--origin") + 1])


if __name__ == "__main__":
    main()
