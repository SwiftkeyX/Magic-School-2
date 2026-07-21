using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Enemy-side seed for the vanilla engine. Holds authored (HeroDataSO, HexCoord) pairs and
    // projects the Hero half to HeroDataSeed (Team.Enemy); the Position half is read by
    // AutoChessManager.GetEnemyPlacements() as the default formation, overridable by
    // AutoChessManager.SetEnemyPlacements(). Enemy placement is authored input, the same
    // standard as player placement (BattlePlacementController drag-and-drop) -- neither side's
    // starting position is computed.
    public class EnemyDatabaseStub : MonoBehaviour
    {
        [SerializeField] private List<HeroPlacementEntry> _enemies = new List<HeroPlacementEntry>();

        public List<HeroDataSeed> GetUnits() =>
            _enemies.Where(e => e.Hero != null).Select(e => HeroDataSeedFactory.ToCombatData(e.Hero, Team.Enemy)).ToList();

        // Parallel to GetUnits() -- same filter, same order -- so callers can zip the two by index.
        public List<HexCoord> GetPlacements() =>
            _enemies.Where(e => e.Hero != null).Select(e => e.Position).ToList();
    }
}
