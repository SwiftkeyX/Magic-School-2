using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Flat stat-bonus trait-synergy queries the manager (AutoChessManager) needs but shouldn't
    // own as its own methods. Stateless -- takes AutoChessData as a parameter rather than
    // holding a reference to it, matching the same decoupled pattern AutoChessHelper uses.
    internal static class Trait
    {
        private static readonly Team[] AllTeams = { Team.Player, Team.Enemy };

        // Runs once from BeginBattle(): counts distinct heroes per trait per team, then applies
        // the highest satisfied breakpoint's StatBonus to each trait member on that team.
        // Members-only, additive, evaluated once. See Trait GDD.
        public static void ApplyTraitBonuses(ACData data)
        {
            foreach (Team team in AllTeams)
            {
                var members = data.Combatants.Where(c => c.Data.Team == team).ToList();
                if (members.Count == 0) continue;

                var counts = CountTraits(members);
                foreach (var kv in counts)
                {
                    TraitDataSO trait = kv.Key;
                    int count = kv.Value;
                    TraitBreakpoint bp = trait.GetActiveBreakpoint(count);
                    if (bp == null) continue;   // below the first breakpoint — no bonus

                    foreach (var c in members.Where(c => c.Data.Traits != null && c.Data.Traits.Contains(trait)))
                        bp.Bonus.ApplyTo(c.Data);

                    Debug.Log($"[AutoBattle] Trait '{trait.DisplayName}' ({team}) active at {count} → " +
                              $"breakpoint {bp.UnitCount} (+HP {bp.Bonus.HP}, +ATK {bp.Bonus.ATK}, " +
                              $"+MG {bp.Bonus.MG}, +DEF {bp.Bonus.DEF}, +MR {bp.Bonus.MR}, " +
                              $"+AS {bp.Bonus.AttackSpeed})");
                }
            }
        }

        // Read-only active-trait readout for a future HUD synergy panel. Not used in combat.
        public static List<(TraitDataSO trait, int count, TraitBreakpoint active)> GetActiveTraits(ACData data, Team team)
        {
            var members = data.Combatants.Where(c => c.Data.Team == team).ToList();
            return CountTraits(members)
                .Select(kv => (kv.Key, kv.Value, kv.Key.GetActiveBreakpoint(kv.Value)))
                .ToList();
        }

        // Distinct-hero count per trait across the given combatants.
        private static Dictionary<TraitDataSO, int> CountTraits(List<HeroSimulation> members)
        {
            var counts = new Dictionary<TraitDataSO, int>();
            foreach (var c in members)
            {
                if (c.Data.Traits == null) continue;
                foreach (var trait in c.Data.Traits.Distinct())
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
