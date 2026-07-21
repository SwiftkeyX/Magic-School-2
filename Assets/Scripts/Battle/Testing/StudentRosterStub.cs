using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Player-side seed for the vanilla engine. Holds authored (HeroDataSO, HexCoord) pairs and
    // projects the Hero half to HeroDataSeed (Team.Player); the Position half is read by
    // AutoChessManager.GetPlayerPlacements() as the default formation, overridable by
    // AutoChessManager.SetPlayerPlacements() (BattlePlacementController drag-and-drop).
    public class StudentRosterStub : MonoBehaviour
    {
        [SerializeField] private List<HeroPlacementEntry> _heroes = new List<HeroPlacementEntry>();

        public List<HeroDataSeed> GetUnits() =>
            _heroes.Where(e => e.Hero != null).Select(e => HeroDataSeedFactory.ToCombatData(e.Hero, Team.Player)).ToList();

        // Parallel to GetUnits() -- same filter, same order -- so callers can zip the two by index.
        public List<HexCoord> GetPlacements() =>
            _heroes.Where(e => e.Hero != null).Select(e => e.Position).ToList();
    }
}
