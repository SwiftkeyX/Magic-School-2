using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Player-side seed for the vanilla engine. Holds authored HeroData assets and projects
    // them to UnitCombatData (Team.Player). Replaces the former hardcoded stat structs.
    public class StudentRosterStub : MonoBehaviour
    {
        [SerializeField] private List<HeroData> _heroes = new List<HeroData>();

        public List<UnitCombatData> GetUnits() =>
            _heroes.Where(h => h != null).Select(h => h.ToCombatData(Team.Player)).ToList();
    }
}
