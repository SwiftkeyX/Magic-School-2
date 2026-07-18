#!/usr/bin/env python3
import sys
import argparse
import math
from champion_db import CHAMPIONS, ITEMS

def compile_equipped_stats(champ_name):
    champ = CHAMPIONS[champ_name]
    items_list = champ.get("equipped_items", [])
    
    ad_mult = 1.0
    as_percent_bonus = 0.0
    ap = 100.0
    crit_chance = 0.25
    crit_dmg = 1.40
    amp = 1.0
    mana_per_attack = 10
    max_mana_mod = 0
    
    # Process items
    for item_name in items_list:
        if item_name not in ITEMS:
            continue
        item = ITEMS[item_name]
        
        ad_mult += item.get("ad_percent", 0.0)
        as_percent_bonus += item.get("as_percent", 0.0)
        as_percent_bonus += item.get("as_percent_avg", 0.0)
        ap += item.get("ap", 0.0)
        crit_chance += item.get("crit_chance", 0.0)
        crit_dmg += item.get("crit_dmg", 0.0)
        amp *= item.get("amp", 1.0)
        
        mana_per_attack = max(mana_per_attack, item.get("mana_per_attack", 10))
        max_mana_mod += item.get("max_mana_mod", 0)
        
    # Apply champion specific overrides if present
    ad_mult = champ.get("eq_ad_mult", ad_mult)
    as_rate = champ.get("eq_as", champ["as"] * (1.0 + as_percent_bonus))
    ap = champ.get("eq_ap", ap)
    crit_chance = champ.get("eq_crit_chance", crit_chance)
    crit_dmg = champ.get("eq_crit_dmg", crit_dmg)
    amp = champ.get("eq_amp", amp)
    
    # Calculate attacks to cast (sustained cycle does not use start mana)
    final_max_mana = champ["max_mana"] + max_mana_mod
    if final_max_mana > 0:
        attacks_to_cast = int(math.ceil(final_max_mana / mana_per_attack))
    else:
        attacks_to_cast = 0
        
    attacks_to_cast = champ.get("eq_attacks", attacks_to_cast)
    
    return ad_mult, as_rate, ap, crit_chance, crit_dmg, amp, attacks_to_cast

def calculate_dps(champ_name, star_level, equipped=False):
    champ = CHAMPIONS[champ_name]
    idx = star_level - 1
    
    if equipped:
        if "equipped_override" in champ:
            ov = champ["equipped_override"](star_level)
            return ov[0], ov[1], ov[2]
            
        ad_mult, as_rate, ap, crit_chance, crit_dmg, amp, attacks = compile_equipped_stats(champ_name)
        
        ad = champ["ad"][idx]
        equipped_ad = int(round(ad * ad_mult))
        
        cycle = champ.get("eq_cycle", (attacks / as_rate) + champ["lockout"])
        
        crit = 1.0 + crit_chance * (crit_dmg - 1.0)
        normal_amp = amp if champ_name not in ["Malzahar", "Gwen", "Katarina", "Kai'Sa", "Ahri"] else 1.0
        
        normal_dps = (attacks * equipped_ad) / cycle * crit * normal_amp
        spell_dmg = champ["eq_spell"](equipped_ad, champ["spell_base"], idx, ap, crit, amp)
        spell_dps = spell_dmg / cycle
        
        return normal_dps, spell_dps, normal_dps + spell_dps
    else:
        if "baseline_override" in champ:
            ov = champ["baseline_override"](star_level)
            return ov[0], ov[1], ov[2]
            
        ad = champ["ad"][idx]
        as_rate = champ["as"]
        attacks = champ.get("base_attacks", int(math.ceil(champ["max_mana"] / 10.0)) if champ["max_mana"] > 0 else 0)
        cycle = champ.get("base_cycle", (attacks / as_rate) + champ["lockout"])
        
        normal_dps = (attacks * ad) / cycle
        spell_dmg = champ["base_spell"](ad, champ["spell_base"], idx)
        spell_dps = spell_dmg / cycle
        
        return normal_dps, spell_dps, normal_dps + spell_dps

def print_champion_breakdown(champ_name):
    champ = CHAMPIONS[champ_name]
    print("=" * 80)
    print(f"DETAILED DPS BREAKDOWN FOR {champ_name.upper()} ({champ['tier']}-GOLD)")
    print("=" * 80)
    print(f"Base Stats: AD = {champ['ad']} | AS = {champ['as']} | Max Mana = {champ['max_mana']} | Lockout = {champ['lockout']}s")
    print(f"Combat Nuance: {champ['nuance']} (Target density factor: {champ['target_density']}x)")
    print(f"Skill Desc: {champ.get('skill_desc', 'N/A')}")
    print(f"Formula Expl: {champ.get('formula_explanation', 'N/A')}")
    print("-" * 80)
    
    print("\n--- BASELINE (UNEQUIPPED) MATH (No base crit multiplier applied) ---")
    for star in [1, 2, 3]:
        n, s, t = calculate_dps(champ_name, star, False)
        print(f" {star}-Star Level: Normal DPS = {n:.1f} | Spell DPS = {s:.1f} | Total DPS = {t:.1f}")
        
    print("\n--- WELL-EQUIPPED (3-ITEM) MATH (Fight Time-Averaged over 30s) ---")
    for star in [1, 2, 3]:
        n, s, t = calculate_dps(champ_name, star, True)
        print(f" {star}-Star Level: Normal DPS = {n:.1f} | Spell DPS = {s:.1f} | Total DPS = {t:.1f}")
    print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description="TFT Set 9 Carry DPS Calculator.")
    parser.add_argument("--champ", type=str, help="Name of the champion to calculate detailed breakdown for.")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3, 4, 5], help="List all carries in a specific gold tier.")
    parser.add_argument("--all", action="store_true", help="Print summary tables for all champions across all tiers.")
    
    args = parser.parse_args()
    
    if args.champ:
        matched_name = next((name for name in CHAMPIONS.keys() if name.lower() == args.champ.lower()), None)
        if matched_name:
            print_champion_breakdown(matched_name)
        else:
            print(f"Champion '{args.champ}' not found. Carries: {', '.join(CHAMPIONS.keys())}")
    elif args.tier:
        print(f"\n--- TIER {args.tier} CARRIES SUMMARY ---")
        print(f"{'Champion':<15} | {'1* Baseline':<12} | {'1* Equipped':<12} | {'2* Baseline':<12} | {'2* Equipped':<12} | {'3* Baseline':<12} | {'3* Equipped':<12}")
        print("-" * 100)
        for name, c in CHAMPIONS.items():
            if c["tier"] == args.tier:
                _, _, b1 = calculate_dps(name, 1, False)
                _, _, e1 = calculate_dps(name, 1, True)
                _, _, b2 = calculate_dps(name, 2, False)
                _, _, e2 = calculate_dps(name, 2, True)
                _, _, b3 = calculate_dps(name, 3, False)
                _, _, e3 = calculate_dps(name, 3, True)
                print(f"{name:<15} | {b1:<12.1f} | {e1:<12.1f} | {b2:<12.1f} | {e2:<12.1f} | {b3:<12.1f} | {e3:<12.1f}")
    elif args.all:
        for t in [1, 2, 3, 4, 5]:
            print(f"\n==================== TIER {t} CARRIES ====================")
            print(f"{'Champion':<15} | {'1* Baseline':<12} | {'1* Equipped':<12} | {'2* Baseline':<12} | {'2* Equipped':<12} | {'3* Baseline':<12} | {'3* Equipped':<12}")
            print("-" * 100)
            for name, c in CHAMPIONS.items():
                if c["tier"] == t:
                    _, _, b1 = calculate_dps(name, 1, False)
                    _, _, e1 = calculate_dps(name, 1, True)
                    _, _, b2 = calculate_dps(name, 2, False)
                    _, _, e2 = calculate_dps(name, 2, True)
                    _, _, b3 = calculate_dps(name, 3, False)
                    _, _, e3 = calculate_dps(name, 3, True)
                    print(f"{name:<15} | {b1:<12.1f} | {e1:<12.1f} | {b2:<12.1f} | {e2:<12.1f} | {b3:<12.1f} | {e3:<12.1f}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
