using System.Collections.Generic;
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

        public List<HeroDataSeed> GetUnits() => RosterStubHelper.GetUnits(_heroes, Team.Player);

        public List<HexCoord> GetPlacements() => RosterStubHelper.GetPlacements(_heroes);
    }
}
