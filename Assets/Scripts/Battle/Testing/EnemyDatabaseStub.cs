using System.Collections.Generic;
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

        public List<HeroDataSeed> GetUnits() => RosterStubHelper.GetUnits(_enemies, Team.Enemy);

        public List<HexCoord> GetPlacements() => RosterStubHelper.GetPlacements(_enemies);
    }
}
