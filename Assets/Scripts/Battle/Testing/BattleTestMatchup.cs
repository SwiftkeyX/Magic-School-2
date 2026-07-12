using System.Collections.Generic;
using UnityEngine;

namespace MagicSchool.Battle
{
    // A reusable, named "Team A vs Team B" preset for BattleTestHarness — lets a specific
    // matchup be set up once and re-run indefinitely instead of rebuilt from scratch each session.
    // removed: ChampionRoster-based id validation (_championRoster field, OnValidate/CheckIds) —
    // champion system, rebuilding fresh. Fields kept as inert placeholders documenting intent.
    [CreateAssetMenu(fileName = "BattleTestMatchup", menuName = "MagicSchool/BattleTestMatchup")]
    public class BattleTestMatchup : ScriptableObject
    {
        [Header("Team A — Player side (bench, drag-placed as usual)")]
        public List<string> PlayerChampionIds = new List<string>();

        [Header("Team B — Enemy side (auto-placed as usual)")]
        public List<string> EnemyChampionIds = new List<string>();
    }
}
