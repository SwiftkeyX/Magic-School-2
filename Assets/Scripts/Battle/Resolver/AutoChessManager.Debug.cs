using UnityEngine;

namespace MagicSchool.Battle
{
    // Editor/QA-only debug hooks, split out of AutoChessManager.cs for file-length
    // hygiene — these don't participate in battle control flow, they're callable
    // shortcuts for testing.
    public partial class AutoChessManager
    {
#if UNITY_EDITOR
        public void DebugSetAllPlayerHp(float pct)
        {
            foreach (var c in _data.Combatants)
                if (c.Data.IsPlayer) c.Data.CurrentHP = Mathf.Max(1, Mathf.RoundToInt(c.Data.MaxHP * pct));
        }

        // removed: DebugForceCast(string combatantId) — skill-cast system, rebuilding fresh.
#endif
    }
}
