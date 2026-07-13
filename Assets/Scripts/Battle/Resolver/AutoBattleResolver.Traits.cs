using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Flat stat-bonus trait synergy pass. Runs once from BeginBattle(): counts distinct
    // heroes per trait per team, then applies the highest satisfied breakpoint's StatBonus to
    // each trait member on that team. Members-only, additive, evaluated once. See Trait GDD.
    public partial class AutoBattleResolver
    {
        private static readonly Team[] AllTeams = { Team.Player, Team.Enemy };

        private void ApplyTraitBonuses()
        {
            foreach (Team team in AllTeams)
            {
                var members = _combatants.Where(c => c.Team == team).ToList();
                if (members.Count == 0) continue;

                var counts = CountTraits(members);
                foreach (var kv in counts)
                {
                    TraitData trait = kv.Key;
                    int count = kv.Value;
                    TraitBreakpoint bp = trait.GetActiveBreakpoint(count);
                    if (bp == null) continue;   // below the first breakpoint — no bonus

                    foreach (var c in members.Where(c => c.Traits != null && c.Traits.Contains(trait)))
                        bp.Bonus.ApplyTo(c);

                    Debug.Log($"[AutoBattle] Trait '{trait.DisplayName}' ({team}) active at {count} → " +
                              $"breakpoint {bp.UnitCount} (+HP {bp.Bonus.HP}, +ATK {bp.Bonus.ATK}, " +
                              $"+MG {bp.Bonus.MG}, +DEF {bp.Bonus.DEF}, +MR {bp.Bonus.MR}, " +
                              $"+AS {bp.Bonus.AttackSpeed})");
                }
            }
        }

        // Read-only active-trait readout for a future HUD synergy panel. Not used in combat.
        public List<(TraitData trait, int count, TraitBreakpoint active)> GetActiveTraits(Team team)
        {
            var members = _combatants.Where(c => c.Team == team).ToList();
            return CountTraits(members)
                .Select(kv => (kv.Key, kv.Value, kv.Key.GetActiveBreakpoint(kv.Value)))
                .ToList();
        }

        // Distinct-hero count per trait across the given combatants.
        private static Dictionary<TraitData, int> CountTraits(List<Combatant> members)
        {
            var counts = new Dictionary<TraitData, int>();
            foreach (var c in members)
            {
                if (c.Traits == null) continue;
                foreach (var trait in c.Traits.Distinct())
                {
                    if (trait == null) continue;
                    counts.TryGetValue(trait, out int n);
                    counts[trait] = n + 1;
                }
            }
            return counts;
        }
    }
}
