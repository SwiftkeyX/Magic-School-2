# -*- coding: utf-8 -*-
"""Build `data/archetype-review.csv` — the proposed Hero archetype tag for every champion.

This is a REVIEW tab, not a schema tab: it exists so the user can comment per champion on the
proposed tags before they become real `Archetype 1`/`Archetype 2` columns on the two Hero tabs.
Once the review is signed off, the tags move into those columns and this tab is deleted.

Decisions applied (user, round 11):
  D1 two columns          `Archetype 1` + `Archetype 2`, the Origin 1/2 & Class 1/2 precedent
  D2 vocabulary capped    a tag covering <5 champions collapses into the next one earned
  D3 spammer, his rule    "mage AND max mana <= 60"
  D4 cross-set axis       `Role` left alone; it will never agree across two Riot sets
  Q2 Naafari -> Naafiri   the tab's spelling was wrong; source and Riot both say Naafiri
  Q3 Pierce-All is AOE    his Sona call, read off the sheet's own `Collision` axis

Run from repo root:  python .claude/scripts/tft-set9-skill-modularity/build_archetype_review.py
Then `sync.py` writes the tab. Mana comes from the two SOURCE sheets, which is the only fact this
tooling cannot get from its own CSVs.
"""
import csv, json, re, collections, os
import gspread

D = ".claude/scripts/tft-set9-skill-modularity/data/"
HERE = os.path.dirname(os.path.abspath(__file__))
CRED = "google-service-credential.json"
SOURCES = [("1xj6em5XlvIN1gWHTKOPDsssmkgnS3jIsaLnAMjYyPUA", "S9"),
           ("1Eutkil9U8RJ4Lqo3l6wk9pbUeVVH80M4JmcRyMEqa2E", "S10")]
CACHE = os.path.join(HERE, "mana-cache.json")


def fetch_stats():
    """(effective mana, attack speed, MAX mana) per champion, cached — two network reads otherwise."""
    if os.path.exists(CACHE):
        return {tuple(k.split("|")): tuple(v) for k, v in json.load(open(CACHE)).items()}
    gc = gspread.service_account(filename=CRED)
    out = {}
    for key, tag in SOURCES:
        v = gc.open_by_key(key).worksheet("Champions").get_all_values()
        h = v[0]
        ni = next(i for i, x in enumerate(h) if "Champion" in x)
        si, mi, ai = h.index("Starting Mana"), h.index("Max Mana"), h.index("AS")
        for r in v[1:]:
            n = r[ni].strip()
            if not n:
                continue
            try:
                out[f"{tag}|{n}"] = (int(r[mi]) - int(r[si]), float(r[ai]), int(r[mi]))
            except ValueError:
                pass  # Maokai's mana is literally 'N/A' in source — he is the mana-leech champion.
    json.dump(out, open(CACHE, "w"))
    return {tuple(k.split("|")): tuple(v) for k, v in out.items()}


STATS = fetch_stats()
STATS_BASE = {tuple(k.split("|")): v for k, v in
              json.load(open(os.path.join(HERE, "base-stats-cache.json"))).items()}

# The user's rule, verbatim: "Spammer = guy who are mage and also have max mana <= 60".
# This is MAX mana, not max-minus-starting — an earlier pass used effective mana and got Karma wrong
# (eff 50 but max 50, so she qualifies) and Sona wrong (eff 45 but max 80, so she does not, which is
# what he wanted: he called her an AOE mage, never a spammer). Do not "fix" this back to effective.
SPAM_MAX = 60

# AOE vs Single-Target now comes from the sheet's OWN `Collision` axis rather than a hand-kept list.
# Collision is defined on its tab as "the set of units the action physically touches", which is
# exactly the question. Pierce-All ("EVERY unit along the path") is why Sona's Pierce Projectile
# counts as AOE — the user's call, and the data already said so.
# `Flank-Pair` was deleted from the Collision vocabulary in round 14 — it existed for exactly one
# action on exactly one champion (Sett), who now uses a centred Box AOE instead.
MULTI = {"Area", "Pierce-All"}
SINGLE = {"Target-Only", "First-Hit"}


def action_collision():
    rows = list(csv.reader(open(D + "action-model.csv", encoding="utf-8")))
    h = rows[0]
    ci = next(i for i, x in enumerate(h) if "ollision" in x)
    return {r[0].strip(): r[ci].strip() for r in rows[1:] if r[0].strip() and r[ci].strip()}


COLL = action_collision()
SUMMON = {"Static Summon", "Hero Summon", "Charge Summon"}
AA_RIDER = {"Bonus on AA", "QuickAA", "Auto-Attack (ranged)", "Auto-Attack (melee)"}
DIVE = {"Move", "Move Behind", "Charge", "Bounce Charge"}
CC = {"Stun", "Chill", "Disarm", "Knock Off", "Impale"}

# CLASS_FN (a class trait -> function noun map) and function() LIVED HERE AND ARE GONE, 2026-07-21.
# They existed to DERIVE a role, and the role is now stated on the Hero tabs — see role(). Deleting
# them rather than leaving them unused is deliberate: this file has already been bitten twice by a
# mapping that outlived the vocabulary it produced (`Strategist -> Support` kept resolving to a role
# that no longer existed, which sent Teemo to Marksman). Dead code that still computes a plausible
# answer is the dangerous kind, and every judgement these encoded is baked into the column now.

# Round 11, the user's correction: "Assassin should be the hero that can target enemy's backline"
# (his examples: Akshan for his furthest aim, Katarina for her Rogue trait). That split in two, and
# the two live at DIFFERENT layers because they are different things:
#   `Assassin`        ROLE noun — melee, physically dives in. Keeps his phrase "AOE Assassin".
#                     Now stated in the Hero tabs' `Role` column, not computed here.
#   `Snipe Backline`  PATTERN tag  — ranged, picks a far target from where it stands. So Set 10 Lux
#                     stays a `Spell Spammer Mage` first and gains the snipe property second, rather
#                     than having his own original call overwritten.
# Backline aims are matched by PATTERN, not by a literal set. Two rounds of vocabulary work broke a
# literal set twice: `Farthest enemy` merged into `Farthest`, then `4 furthest enemies` became the
# family `[N] furthest enemies` — and a set naming the VOCAB KEY silently stopped matching the HERO
# CELL, which still says `4 furthest enemies`. Caitlyn dropped out of Snipe Backline that way.
# Hero cells keep literals; anything reading them must match literals.
BACKLINE_RE = re.compile(r"(?:^Farthest\b)|(?:^\d+(?:/\d+)* furthest enemies$)")


def is_backline_aim(aim):
    return bool(BACKLINE_RE.match(aim))
# `Crowd Diver` was here and is NOT a dive class — his call: "I see you put a lot of Crown diver as
# a assassin. They are all fighter, not assassin." Dropping it moves 5 Set 10 heroes to Fighter
# (Katarina, Zed, Yone, Evelynn, Qiyana). Set 9 Zed and Katarina KEEP Assassin via Rogue — the same
# character reads differently per set, which he confirmed is correct: the set's own trait decides.
DIVE_CLASSES = {"Rogue"}
# `Move Behind` ALONE is deliberately NOT enough. It is a short reposition, not backline access —
# the user's call on Urgot and Gnar: "true that they jump into enemy, but most of time they don't
# reach backline". Rek'Sai drops for the same reason (she burrows to a MARKED target, not a far one).
# Graves stays: he is Rogue-class, and the trait itself is the backline access.

# Most informative first: Archetype 1 takes the highest-priority tag this champion earns.
PRIORITY = ["Spell Spammer", "Snipe Backline", "Utility", "AOE", "Shield", "Heal", "Summoner",
            "Crowd Control", "Shred", "Single-Target", "On-Hit"]


def load(fn, tag):
    rows = list(csv.reader(open(D + fn, encoding="utf-8")))
    hdr, rows = rows[0], rows[1:]
    c = {n: i for i, n in enumerate(hdr)}
    out, cur = [], None
    for r in rows:
        if r[0].strip():
            base = re.sub(r"\s*\(.*\)$", "", r[0].strip())
            # `Naafari` was the tab's misspelling and is now FIXED in hero.csv, so this alias is a
            # no-op guard kept only so the join cannot silently drop her again if it ever regresses.
            base = {"Naafari": "Naafiri"}.get(base, base)
            eff, AS, maxm = STATS.get((tag, base), (None, None, None))
            # BY NAME, not by index: `Damage Type` was inserted at index 3 on 2026-07-21 and every
            # column after it shifted, which silently turned `range` into a Class and `summary`
            # into the Range. `c` is already the header map — these three were the only reads that
            # bypassed it.
            cur = {"set": tag, "name": r[0].strip(), "cost": r[1].replace(" Gold", ""),
                   "role": r[c["Role"]], "range": r[c["Range"]], "summary": r[c["Summary"]],
                   "dmgtype": r[c["Damage Type"]], "eff": eff, "maxmana": maxm,
                   "classes": [x.strip() for x in (r[c["Class 1"]], r[c["Class 2"]]) if x.strip()],
                   "acts": set(), "effs": set(), "aims": set(), "amounts": [], "gives": set()}
            out.append(cur)
        cur["acts"].add(r[c["Legacy action"]].strip())
        cur["aims"].add(r[c["Aim Target"]].strip())
        if r[c["Effect Category"]].strip() == "Attack" and r[c["Amount"]].strip() not in ("", "—"):
            cur["amounts"].append(r[c["Amount"]].strip())
        cur["gives"].add((r[c["Effect Category"]].strip(), r[c["Effect Detail"]].strip(),
                          r[c["Effect Recipient"]].strip()))
        ec, ed = r[c["Effect Category"]].strip(), r[c["Effect Detail"]].strip()
        if ec not in ("", "—"):
            cur["effs"].add((ec, ed))
    return out


def is_melee(ch):
    return ch["range"].strip() in ("1", "2")


def is_sniper(ch):
    """Ranged and picks a back-line target.

    SENNA IS IN, as of 2026-07-21. She used to be excluded by a `"Support" not in role` test, and
    that test died with the role: normalising Role onto five nouns removed `Support` entirely, so
    the condition became vacuously true for every champion. Rather than reconstruct the exclusion,
    the user was asked and confirmed she belongs — which the data already argued, since her beam is
    235/250/2000% AD, the highest of the whole group, against Akshan's 125% (and he called Akshan an
    assassin). Senna and Set 10 Lux are otherwise IDENTICAL rows — both Laser Shot, Pierce-All, aim
    Farthest — so treating them differently was never defensible on anything but the dead column.
    """
    return not is_melee(ch) and bool({a for a in ch["aims"] if is_backline_aim(a)})


def damage_score(ch):
    """A ROUGH tier-2 ability-damage proxy, in 'points of raw damage at a 100-AP item'.

    Deliberately shown on the tab, because it is NOT trustworthy as an absolute number and the user
    corrects it by eye. Two known distortions, both real and both unfixable from current columns:
      UNDER-counts repetition — Garen is `80/82/85% AD` `Every spin` for 4s and scores it ONCE,
        because `Effect Cadence` says how OFTEN but no column gives a tick rate.
      OVER-counts multi-step — K'Sante's `400% AP` appears on both his Knock Back and his Charge
        step and is summed twice, though it is likely one damage instance described in two places.
    Tier 2 is used per the user's rule: tier 3 is a luxury number players do not reach.
    """
    st = STATS_BASE.get((ch["set"], re.sub(r"\s*\(.*\)$", "", ch["name"])), {})
    ad = st.get("AD", 55.0)
    total = 0.0
    for amount in ch["amounts"]:
        t2 = re.sub(r"(\d+)/(\d+)/(\d+)", lambda m: m.group(2), amount)
        for pct, kind in re.findall(r"(\d+(?:\.\d+)?)%\s*(AD|AP)", t2):
            total += float(pct) / 100 * (ad if kind == "AD" else 100.0)
    return round(total)


# The user's definition (round 11c): "Make Tank the hero that don't do much damage but provide other
# utility. Make Fighter a hero that do dmage a lot." The line below is the MEDIAN of the melee
# front-liners' damage scores — a stated split, not a discovered one, because the ranking is a smooth
# continuum with no natural break. It is a seed for the user to correct, which is the agreed process.
#   240 (the median) made Galio a Fighter at 300, contradicting "Galio = Heal Tank, AOE Tank".
#   300 (the 70th percentile) is the lowest line that satisfies EVERY worked example he has given:
#   Poppy 240 Tank, Galio 300 Tank, K'Sante 800 Fighter, Kayn 1200 Fighter. Comparison is strictly
#   `>`, so a champion sitting ON the line is a Tank — being at the 70th percentile is not "a lot".
FIGHTER_MIN = 300
UTILITY = {"Shield", "Armor", "MR", "Damage Reduction", "Bonus HP", "Heal", "Damage Redirect",
           "Untargetable", "Omnivamp", "Attack Speed", "AD", "AP", "Mana", "Empowered Attack"}


# USER_ROLE held his four flat disagreements with the source (Warwick, Urgot and Olaf are Fighters
# where the source says Tank; Nilah is a Marksman despite being melee at range 2). It is GONE for
# the same reason as CLASS_FN: those four calls are now written into the Hero tabs' `Role` column,
# and a second copy of a fact is a copy that will disagree.


def role(ch):
    """One noun per champion: what it IS. Now a PASSTHROUGH of the Hero tabs' own `Role` column.

    THIS FUNCTION USED TO DERIVE THE ROLE, and on 2026-07-21 the thing it derived became the thing
    it reads: the user's reviewed roles were written back onto both Hero tabs, replacing the
    imported source values. Keeping the derivation would have made the script feed on its own
    output — and NOT harmlessly, because it was built to read the SOURCE vocabulary. Its ranged
    branch tested `role.startswith("AD")` against strings like `ADCaster`; against a normalised
    `Marksman` that test fails and the champion falls through to be re-judged on class, so Mage and
    Marksman would flip on a rebuild. A derivation whose input is its own output is not idempotent
    just because it looks stable for the Tank case.

    The USER_ROLE overrides and the old heuristics are gone with it: both are already baked into
    the column, which is now the single place a role is stated. Correct a role by editing the Hero
    CSV, not by adding a rule here.
    """
    return ch["role"].strip()


def is_utility(ch):
    """A benefit handed to an ALLY that no other archetype already names, plus economy effects.

    Deliberately EXCLUDES Shield and Heal: both are already archetypes, so including them would tag
    Soraka `Utility` and `Heal` for one effect. This is the leftover — Jayce's flank buff, Ryze's
    Armor/MR aura, Sona's attack speed — plus Gold and Item, which are the only non-combat effects
    the sheet models. The user's replacement for the Support role.
    """
    for cat, det, recip in ch["gives"]:
        if det in ("Gold", "Item"):
            return True
        if cat == "Buff" and det not in ("Shield", "Heal") and "all" in recip.lower():
            return True
    return False


def patterns(ch):
    acts, effs = ch["acts"], ch["effs"]
    details = {d for _, d in effs}
    p = []
    # The user's own definition (round 11): "Spammer = guy who are mage and also have max mana <= 60".
    # Note MAX mana, not effective — and gated to mages, so it never lands on a tank or a fighter.
    # eff == 0 means no mana bar at all: a permanent passive, the opposite of a spammer.
    if ch["role_n"] == "Mage" and ch["maxmana"] is not None and 0 < ch["maxmana"] <= SPAM_MAX:
        p.append("Spell Spammer")
    if is_sniper(ch):
        p.append("Snipe Backline")
    if {COLL.get(a) for a in acts} & MULTI:
        p.append("AOE")
    if "Shield" in details:
        p.append("Shield")
    if "Heal" in details or "Omnivamp" in details:
        p.append("Heal")
    if acts & SUMMON:
        p.append("Summoner")
    if details & CC:
        p.append("Crowd Control")
    if any(c == "Debuff" for c, _ in effs):
        p.append("Shred")
    cols = {COLL.get(a) for a in acts}
    if not (cols & MULTI) and (cols & SINGLE):
        p.append("Single-Target")
    if is_utility(ch):
        p.append("Utility")
    if acts & AA_RIDER:
        p.append("On-Hit")
    return sorted(p, key=PRIORITY.index)


champs = load("hero.csv", "S9") + load("hero-set10.csv", "S10")
for ch in champs:
    ch["dmg"] = damage_score(ch)
    ch["role_n"] = role(ch)
    ch["pats"] = patterns(ch)

# --- D2: the cap. Now that Role is its OWN column, patterns are no longer glued to a noun, so the
# cross-product that forced this cap is gone — a pattern spans every role and is naturally common.
# The cap is kept only as a guard against a future pattern that lands on almost nobody.
MIN = 5
PROTECTED = {"Spell Spammer", "Snipe Backline"}   # user-defined; small BY DESIGN, never auto-dropped
counts = collections.Counter(p for ch in champs for p in ch["pats"])
rare = {t for t, n in counts.items() if n < MIN and t not in PROTECTED}
for ch in champs:
    ch["pats"] = [p for p in ch["pats"] if p not in rare]

for ch in champs:
    ch["a1"] = ch["pats"][0] if ch["pats"] else "—"
    ch["a2"] = ch["pats"][1] if len(ch["pats"]) > 1 else ""

vocab = collections.Counter()
for ch in champs:
    for p in ch["pats"]:
        vocab[p] += 1
roles = collections.Counter(ch["role_n"] for ch in champs)

spam = [c for c in champs if "Spell Spammer" in (c["a1"] + "|" + c["a2"])]

# --- the review tab -------------------------------------------------------------------------
# `Your call` is deliberately left EMPTY: it is the user's column to type into, and sync.py would
# overwrite anything written there on the next run. Review happens in Drive comments; this column is
# for quick verdicts he wants visible in the grid itself.
HEAD = ["Set", "Champion", "Cost", "Max Mana", "Dmg score", "Role", "Archetype 1", "Archetype 2",
        "Current Summary", "Why these tags", "Your call"]


def why(ch):
    bits = []
    if "Spell Spammer" in ch["a1"] + ch["a2"]:
        bits.append(f"mage, max mana {ch['maxmana']} <= 60")
    cols = sorted({COLL.get(a) for a in ch["acts"] if COLL.get(a)} & (MULTI | SINGLE))
    if cols:
        bits.append("collision " + "/".join(cols))
    if is_melee(ch) and ch["role_n"] in ("Tank", "Fighter"):
        bits.append(f"dmg {ch['dmg']} {'>=' if ch['dmg'] >= FIGHTER_MIN else '<'} {FIGHTER_MIN}")
    return "; ".join(bits)


rows = [HEAD]
rows += [[ch["set"], ch["name"], ch["cost"], ch["maxmana"] if ch["maxmana"] is not None else "N/A",
          ch["dmg"], ch["role_n"], ch["a1"], ch["a2"] or "—", ch["summary"], why(ch), ""]
         for ch in champs]

DOC = [
    "How to read this tab",
    "THIS TAB IS TEMPORARY. It is a review surface for the proposed 'Hero archetype' column, not a "
    "vocabulary the Hero tabs validate against. Once the tags below are signed off they move into new "
    "'Archetype 1' / 'Archetype 2' columns on 'Hero set 9' and 'Hero set 10', a 'Hero Archetype Types' "
    "tab is created so VALIDATE enforces them, and this tab is deleted.",
    "TWO COLUMNS, NOT ONE, because a champion can be two things at once (Galio is an AOE Tank AND a "
    "Heal Tank). That follows the precedent already on the identity block beside it: Origin 1/Origin 2 "
    "and Class 1/Class 2. One value per cell keeps VALIDATE working unchanged.",
    "A TAG IS 'PATTERN + FUNCTION'. The FUNCTION noun (Tank, Mage, Bruiser, Assassin, Marksman, "
    "Fighter, Juggernaut, Support) comes from the champion's CLASS trait — all 27 classes across both "
    "sets collapse onto those eight, which is what lets ONE vocabulary span Set 9 and Set 10. Role "
    "overrides Class for front-liners: Galio is a Sorcerer-class TANK, and calling him an AOE Mage "
    "loses the only thing that decides where he is placed.",
    "AOE vs SINGLE-TARGET IS READ OFF 'Collision', not kept by hand. Collision is already defined on "
    "its own tab as the set of units an action physically touches, so AOE = Area / Pierce-All / "
    "Flank-Pair and Single-Target = Target-Only / First-Hit. This is why Sona counts as AOE: her "
    "Pierce Projectile is Pierce-All, 'EVERY unit along the path'. It stays correct when a new action "
    "is added, because the new action must declare a Collision anyway.",
    "SPELL SPAMMER = MAGE AND MAX MANA <= 60 (the user's rule, round 11). Note MAX mana, NOT "
    "max-minus-starting. An earlier pass used effective mana and got two champions wrong: Karma "
    "(eff 50 but max 50, so she DOES qualify) and Sona (eff 45 but max 80, so she does NOT — which is "
    "correct, he called her an AOE mage, never a spammer). Do not 'simplify' this back to effective mana.",
    "NO FORMULA REPRODUCES THE SPAMMER LABELS ON ITS OWN. The five champions whose Summary already "
    "said 'Spammer' rank 11th, 12th, 24th, 50th and 58th of 133 on casts-per-second (AS x 10 / mana), "
    "so the <=60 line is a STATED rule, not a discovered one. VALIDATE will enforce the tag's spelling; "
    "it can never enforce that an assignment is right. That part stays a human call.",
    "THE VOCABULARY IS CAPPED. A pattern+function tag covering fewer than 5 champions collapses into "
    "the next tag that champion earns — otherwise the cross-product explodes to 54 tags for 135 "
    "champions, 14 of them covering exactly one champion, which is a second Summary rather than an "
    "archetype. Two exemptions: 'Spell Spammer' survives at any count (the user called it important), "
    "and tags the user NAMED HIMSELF outrank the threshold ('AOE Juggernaut' covers only four).",
    "OPEN QUESTION — SAMIRA. Her Summary says 'Single-Target Shred Spammer' and her max mana is 30, "
    "the lowest on either tab, but she is an AD carry and the rule says MAGE, so she gets no spammer "
    "tag. Sona is the same shape: Summary still says 'Spell Spammer', archetype now says AOE Mage. "
    "Either both Summaries get edited to stop claiming it, or the rule widens from 'mage' to 'any caster'.",
    "NAAFIRI: this sheet spelled her 'Naafari'. Source and Riot both spell her 'Naafiri'. Nothing "
    "depended on it until mana had to be joined from the source sheet, at which point she silently "
    "dropped out. Fixed on 'Hero set 9' in this same round.",
    "MAOKAI has no mana in source at all ('N/A') — he is the mana-leech champion, so he can never "
    "qualify as a spammer. That is data, not a gap.",
    "",
    "ROLES — %s" % ", ".join(f"{k} {v}" for k, v in roles.most_common()),
    "",
    "ARCHETYPE PATTERNS — %d over %d champions (%d spammers)" % (len(vocab), len(champs), len(spam)),
]
DOC += [f"{n} x  {t}" for t, n in vocab.most_common()]

rows.append([""] * len(HEAD))
rows += [[d] + [""] * (len(HEAD) - 1) for d in DOC]

with open(D + "archetype-review.csv", "w", encoding="utf-8", newline="") as f:
    csv.writer(f).writerows(rows)

print(f"{len(champs)} champions, {len(vocab)} tags, {len(spam)} spammers")
print(f"wrote {D}archetype-review.csv — {len(rows)} rows")
print("next: add \"Archetype Review\": \"archetype-review.csv\" to sheet.TABS, then run sync.py")
