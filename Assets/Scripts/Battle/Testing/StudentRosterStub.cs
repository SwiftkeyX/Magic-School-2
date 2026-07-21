using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Player-side seed for the vanilla engine. Holds authored HeroDataSO assets and projects
    // them to HeroDataSeed (Team.Player). Replaces the former hardcoded stat structs.
    public class StudentRosterStub : MonoBehaviour
    {
        [SerializeField] private List<HeroDataSO> _heroes = new List<HeroDataSO>();

        public List<HeroDataSeed> GetUnits() =>
            _heroes.Where(h => h != null).Select(h => h.ToCombatData(Team.Player)).ToList();
    }
}
