using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Shared per-tick queries the manager (AutoChessManager) needs but shouldn't own as its own
    // methods. Stateless -- takes _combatants/_grid as parameters rather than holding a
    // reference to either, matching the same decoupled pattern HeroSimulation uses.
    internal static class AutoChessHelper
    {
        // Every living unit on the opposing side.
        public static List<HeroDataRuntime> GetOpponentsOf(List<HeroSimulation> combatants, HeroSimulation actor)
        {
            return combatants
                .Where(c => !c.Data.IsDefeated && c.Data.IsPlayer != actor.Data.IsPlayer)
                .Select(c => c.Data)
                .ToList();
        }

        public static bool CheckWinCondition(List<HeroSimulation> combatants)
        {
            bool playersAlive = combatants.Any(c => c.Data.IsPlayer && !c.Data.IsDefeated);
            bool enemiesAlive = combatants.Any(c => !c.Data.IsPlayer && !c.Data.IsDefeated);
            return !enemiesAlive || !playersAlive;
        }

        // Clears the defeated unit's grid cell and logs the kill. Does NOT fire
        // OnCombatantDefeated -- events live on the manager, only it has subscribers.
        public static void HandleKillIfNeeded(List<HeroSimulation> combatants, HexGrid grid, AttackResult result)
        {
            if (!result.WasKill) return;

            var targetSim = combatants.FirstOrDefault(h => h.Data.Id == result.TargetId);
            if (targetSim == null) return;

            grid.ClearOccupant(targetSim.Data.Position);
            Debug.Log($"[AutoBattle] {targetSim.Data.DisplayName} DEFEATED");
        }
    }
}
