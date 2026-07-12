using UnityEngine;

namespace MagicSchool.Battle
{
    // Editor/QA-only debug hooks, split out of AutoBattleResolver.cs for file-length
    // hygiene — these don't participate in battle control flow, they're callable
    // shortcuts for testing.
    public partial class AutoBattleResolver
    {
#if UNITY_EDITOR
        public void DebugSetAllPlayerHp(float pct)
        {
            foreach (var c in _combatants)
                if (c.IsPlayer) c.CurrentHP = Mathf.Max(1, Mathf.RoundToInt(c.MaxHP * pct));
        }

        // removed: DebugForceCast(string combatantId) — skill-cast system, rebuilding fresh.
#endif
    }
}
