using UnityEngine;

namespace MagicSchool.Battle
{
    // removed: ChampionRoster-based matchup pre-seeding (_championRoster, _matchup fields,
    // the whole Awake() body, ToEnemyCombatData()) — champion/skill system, rebuilding fresh.
    // AutoBattleResolver.EnsureCombatantsInitialized() now unconditionally seeds from
    // StudentRosterStub/EnemyDatabaseStub, so this class is currently a no-op placeholder.
    public class BattleTestHarness : MonoBehaviour
    {
        [SerializeField] private AutoBattleResolver _resolver;
        [SerializeField] private BattleTestMatchup _matchup;
    }
}
