using System.Linq;
using UnityEngine;
using System.Collections.Generic;

namespace MagicSchool.Battle
{
    // Shared per-tick queries the manager (AutoChessManager) needs but shouldn't own as its own
    // methods. Stateless -- takes AutoChessData as a parameter rather than holding a reference
    // to it, matching the same decoupled pattern HeroSimulation uses.
    internal static class AutoChessHelper
    {
        // Every living unit on the opposing side.
        public static List<HeroDataRuntime> GetOpponentsOf(AutoChessData data, HeroSimulation actor)
        {
            return data.Combatants
                .Where(c => !c.Data.IsDead && c.Data.IsPlayer != actor.Data.IsPlayer)
                .Select(c => c.Data)
                .ToList();
        }

        public static bool CheckWinCondition(AutoChessData data)
        {
            bool playersAlive = data.Combatants.Any(c => c.Data.IsPlayer && !c.Data.IsDead);
            bool enemiesAlive = data.Combatants.Any(c => !c.Data.IsPlayer && !c.Data.IsDead);
            return !enemiesAlive || !playersAlive;
        }

        // Clears the defeated unit's grid cell and logs the kill. Does NOT fire
        // OnCombatantDefeated -- events live on the manager, only it has subscribers.
        public static void HandleKillIfNeeded(AutoChessData data, AttackResult result)
        {
            if (!result.WasKill) return;

            var targetSim = data.Combatants.FirstOrDefault(h => h.Data.Id == result.TargetId);
            if (targetSim == null) return;

            data.Grid.ClearOccupant(targetSim.Data.Position);
            Debug.Log($"[AutoBattle] {targetSim.Data.DisplayName} DEFEATED");
        }
    }
}
