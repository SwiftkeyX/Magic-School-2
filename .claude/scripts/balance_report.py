#!/usr/bin/env python3
"""Sheet-driven balance report for the Magic School roster.

Reads champion design data live from the Google Sheet (Heroes / Origin / Class
tabs, via the same service account as sheet_sync.py) and numeric stats from
ChampionRoster.cs, then reports:

  1. Sheet <-> code consistency gate (names, costs, traits, roles)
  2. Layer 2 Stat Budget Scores for every champion vs cost-tier bands
  3. Skill & mana cycle analysis (casts per fight, skill DPS vs auto DPS)
  4. Trait breakpoint tables read live from the sheet

Formulas and bands come from .claude/docs/other/balance-framework.md.
Usage:  python balance_report.py [--output report.md] [--offline sheet_dump.json]
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

ROSTER_PATH = Path("Assets/Scripts/Battle/Traits/ChampionRoster.cs")

# Layer 2 target bands per cost tier (balance-framework.md).
# 4c/5c are given as point targets (~2200 / ~2100); +/-10% tolerance applied.
SCORE_BANDS = {
    1: (900, 1100),
    2: (950, 1450),
    3: (1200, 1350),
    4: (2200 * 0.9, 2200 * 1.1),
    5: (2100 * 0.9, 2100 * 1.1),
}

MANA_PER_ATTACK = 10  # universal mana-on-attack (balance-framework.md Layer 1b)


# ---------------------------------------------------------------- sheet side

def read_sheet_tabs(offline_path=None):
    """Return {tab_name: rows} for Heroes, Origin, Class."""
    wanted = ["Heroes", "Origin", "Class"]
    if offline_path:
        with open(offline_path, encoding="utf-8") as f:
            dump = json.load(f)
        return {tab: dump[tab] for tab in wanted}
    import sheet_sync  # reuse credentials + sheet registry
    sh = sheet_sync.get_spreadsheet(sheet_sync.get_client(), sheet_name="auto-battler")
    return {tab: sh.worksheet(tab).get_all_values() for tab in wanted}


STAT_COLUMNS = ["HP", "ATK", "DEF", "MG", "MR", "AS", "CRIT", "Range", "MaxMana", "StartingMana"]
STAT_TO_CODE_FIELD = {
    "HP": "MaxHP", "ATK": "ATK", "DEF": "DEF", "MG": "MG", "MR": "MR",
    "AS": "AttackSpeed", "CRIT": "CRIT", "Range": "Range",
    "MaxMana": "MaxMana", "StartingMana": "StartingMana",
}


def parse_heroes_tab(rows):
    """Rows -> {display_name: {cost, vertical, horizontal, role, stats?}}."""
    header = rows[0]
    idx = {name: i for i, name in enumerate(header) if name}
    has_stats = all(col in idx for col in STAT_COLUMNS)
    heroes = {}
    for row in rows[1:]:
        name = row[idx["Champion Name"]].strip()
        if not name:
            continue
        cost_match = re.search(r"\d+", row[idx["Cost"]])
        entry = {
            "cost": int(cost_match.group()) if cost_match else None,
            "vertical": row[idx["Vertical Class"]].strip(),
            "horizontal": row[idx["Horizontal Class"]].strip(),
            "role": row[idx["Normalized Design Role"]].strip(),
        }
        if has_stats:
            entry["stats"] = {col: row[idx[col]].strip() for col in STAT_COLUMNS}
        heroes[name] = entry
    return heroes


# ----------------------------------------------------------------- code side

CHAMP_FIELDS = {
    "Id": r'Id\s*=\s*"([^"]+)"',
    "DisplayName": r'DisplayName\s*=\s*"([^"]+)"',
    "Cost": r"Cost\s*=\s*(\d+)",
    "Role": r"Role\s*=\s*ChampionRole\.(\w+)",
    "VerticalTrait": r"VerticalTrait\s*=\s*VerticalTrait\.(\w+)",
    "HorizontalTrait": r"HorizontalTrait\s*=\s*HorizontalTrait\.(\w+)",
    "MaxHP": r"MaxHP\s*=\s*(\d+)",
    "ATK": r"ATK\s*=\s*(\d+)",
    "DEF": r"DEF\s*=\s*(\d+)",
    "MG": r"MG\s*=\s*(\d+)",
    "MR": r"MR\s*=\s*(\d+)",
    "AttackSpeed": r"AttackSpeed\s*=\s*([\d.]+)f",
    "CRIT": r"CRIT\s*=\s*(\d+)",
    "Range": r"Range\s*=\s*(\d+)",
    "MaxMana": r"MaxMana\s*=\s*(\d+)",
    "StartingMana": r"StartingMana\s*=\s*(\d+)",
}
SKILL_FIELDS = {
    "SkillName": r'SkillName\s*=\s*"([^"]+)"',
    "Archetype": r"Archetype\s*=\s*SkillArchetype\.(\w+)",
    "OffenseMultiplier": r"OffenseMultiplier\s*=\s*([\d.]+)f",
    "HealMultiplier": r"HealMultiplier\s*=\s*([\d.]+)f",
    "UsesMagicOffense": r"UsesMagicOffense\s*=\s*(true|false)",
}
INT_FIELDS = {"Cost", "MaxHP", "ATK", "DEF", "MG", "MR", "CRIT", "Range", "MaxMana", "StartingMana"}


def parse_roster(path):
    """ChampionRoster.cs -> list of champion dicts (with nested skill dict)."""
    source = path.read_text(encoding="utf-8")
    champions = []
    # Each champion entry starts at "new ChampionData {"; slice source between starts.
    starts = [m.start() for m in re.finditer(r"new ChampionData\s*\{", source)]
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(source)
        block = source[start:end]
        champ = {}
        for field, pattern in CHAMP_FIELDS.items():
            m = re.search(pattern, block)
            if not m:
                raise ValueError(f"Field {field} not found in champion block #{i + 1}")
            champ[field] = int(m.group(1)) if field in INT_FIELDS else m.group(1)
        champ["AttackSpeed"] = float(champ["AttackSpeed"])
        skill = {}
        skill_m = re.search(r"Skill\s*=\s*new SkillDefinition\s*\{(.*)", block, re.DOTALL)
        if skill_m:
            skill_block = skill_m.group(1)
            for field, pattern in SKILL_FIELDS.items():
                m = re.search(pattern, skill_block)
                if m:
                    skill[field] = m.group(1)
        champ["Skill"] = skill
        champions.append(champ)
    return champions


# ------------------------------------------------------------------ analysis

def consistency_gate(heroes, champions):
    """Compare sheet Heroes tab vs ChampionRoster.cs. Returns list of issue strings."""
    issues = []
    code_by_name = {c["DisplayName"]: c for c in champions}
    for name in heroes:
        if name not in code_by_name:
            issues.append(f"`{name}` is in the sheet but missing from ChampionRoster.cs")
    for name in code_by_name:
        if name not in heroes:
            issues.append(f"`{name}` is in ChampionRoster.cs but missing from the sheet")
    for name, sheet in heroes.items():
        code = code_by_name.get(name)
        if not code:
            continue
        checks = [
            ("cost", sheet["cost"], code["Cost"]),
            ("vertical trait", sheet["vertical"], code["VerticalTrait"]),
            ("horizontal trait", sheet["horizontal"], code["HorizontalTrait"]),
            ("role", sheet["role"], code["Role"]),
        ]
        for label, sheet_val, code_val in checks:
            if str(sheet_val) != str(code_val):
                issues.append(
                    f"`{name}` {label} mismatch: sheet=`{sheet_val}` code=`{code_val}`")
        if "stats" in sheet:
            for col, code_field in STAT_TO_CODE_FIELD.items():
                sheet_val, code_val = sheet["stats"][col], str(code[code_field])
                if sheet_val != code_val:
                    issues.append(
                        f"`{name}` stat `{col}` mismatch: sheet=`{sheet_val}` code=`{code_val}` "
                        f"(rerun push_stats_to_sheet.py)")
    return issues


def offense(champ):
    """Layer 2 Offense: MG where it exceeds ATK (casters/supports), else ATK."""
    return max(champ["ATK"], champ["MG"])


def budget_score(champ):
    ehp = champ["MaxHP"] * (100 + champ["DEF"]) / 100.0
    return offense(champ) * champ["AttackSpeed"] * math.sqrt(ehp)


def score_rows(champions):
    rows = []
    for c in sorted(champions, key=lambda c: (c["Cost"], c["DisplayName"])):
        score = budget_score(c)
        lo, hi = SCORE_BANDS[c["Cost"]]
        if score < lo:
            status = f"LOW ({score / lo * 100:.0f}% of band floor)"
        elif score > hi:
            status = "HIGH"
        else:
            status = "in band"
        rows.append((c["DisplayName"], c["Cost"], c["Role"], round(score), f"{lo:.0f}-{hi:.0f}", status))
    return rows


def skill_rows(champions):
    rows = []
    for c in sorted(champions, key=lambda c: (c["Cost"], c["DisplayName"])):
        s = c["Skill"]
        attacks_to_cast = math.ceil(max(0, c["MaxMana"] - c["StartingMana"]) / MANA_PER_ATTACK)
        cycle_s = attacks_to_cast / c["AttackSpeed"] if c["AttackSpeed"] else float("inf")
        auto_dps = c["ATK"] * c["AttackSpeed"]
        mult = float(s.get("OffenseMultiplier", 0) or 0)
        stat = c["MG"] if s.get("UsesMagicOffense") == "true" else c["ATK"]
        hit = mult * stat
        heal_mult = float(s.get("HealMultiplier", 0) or 0)
        if hit:
            impact = f"{hit:.0f} dmg/cast"
            ratio = f"{(hit / cycle_s) / auto_dps:.2f}" if auto_dps and cycle_s else "-"
        elif heal_mult:
            impact = f"{heal_mult * c['MG']:.0f} heal/cast"
            ratio = "-"
        else:
            impact = "utility"
            ratio = "-"
        rows.append((c["DisplayName"], c["Cost"], s.get("SkillName", "?"), s.get("Archetype", "?"),
                     f"{c['StartingMana']}/{c['MaxMana']}", attacks_to_cast, f"{cycle_s:.1f}s", impact, ratio))
    return rows


# ----------------------------------------------------------------- rendering

def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(str(v) for v in row) + " |" for row in rows]
    return "\n".join(out)


def trait_table(rows):
    """Origin/Class tab rows -> markdown table (name, breakpoints, effects)."""
    body = []
    for row in rows[1:]:
        cells = [c.strip() for c in row]
        if not cells or not cells[0]:
            continue
        effects = cells[3].replace("\\n", "<br>") if len(cells) > 3 else ""
        body.append((cells[0], cells[1] if len(cells) > 1 else "", effects))
    return md_table(["Trait", "Breakpoints", "Effects"], body)


def main():
    ap = argparse.ArgumentParser(description="Magic School sheet-driven balance report")
    ap.add_argument("--output", help="write markdown report to this file instead of stdout")
    ap.add_argument("--offline", help="read tabs from a sheet_sync dump JSON instead of the live sheet")
    args = ap.parse_args()

    tabs = read_sheet_tabs(args.offline)
    heroes = parse_heroes_tab(tabs["Heroes"])
    champions = parse_roster(ROSTER_PATH)

    lines = ["# Balance Report (sheet-driven)", ""]
    lines.append(f"Champions in sheet: **{len(heroes)}** - in code: **{len(champions)}**")
    lines.append("")

    lines.append("## 1. Sheet <-> code consistency gate")
    issues = consistency_gate(heroes, champions)
    if issues:
        lines += [f"- {i}" for i in issues]
    else:
        lines.append("All champions match on name, cost, traits, and role.")
    lines.append("")

    lines.append("## 2. Layer 2 Stat Budget Scores")
    lines.append("`Score = Offense x AS x sqrt(HP x (100+DEF)/100)`; bands from balance-framework.md.")
    lines.append("")
    lines.append(md_table(["Champion", "Cost", "Role", "Score", "Band", "Status"], score_rows(champions)))
    lines.append("")

    lines.append("## 3. Skill & mana cycle")
    lines.append(f"Cycle assumes {MANA_PER_ATTACK} mana per attack only (on-hit mana excluded).")
    lines.append("")
    lines.append(md_table(
        ["Champion", "Cost", "Skill", "Archetype", "Mana", "Attacks/cast", "Cycle", "Impact", "SkillDPS/AutoDPS"],
        skill_rows(champions)))
    lines.append("")

    lines.append("## 4. Trait breakpoints (live from sheet)")
    lines.append("")
    lines.append("### Vertical (Origin)")
    lines.append(trait_table(tabs["Origin"]))
    lines.append("")
    lines.append("### Horizontal (Class)")
    lines.append(trait_table(tabs["Class"]))
    lines.append("")

    report = "\n".join(lines)
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        sys.stdout.buffer.write(report.encode("utf-8"))


if __name__ == "__main__":
    main()
