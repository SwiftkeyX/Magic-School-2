using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Enemy-side seed for the vanilla engine. Holds authored HeroData assets and projects
    // them to UnitCombatData (Team.Enemy). Replaces the former serialized EnemyCombatData list.
    public class EnemyDatabaseStub : MonoBehaviour
    {
        [SerializeField] private List<HeroData> _enemies = new List<HeroData>();

        public List<UnitCombatData> GetUnits() =>
            _enemies.Where(h => h != null).Select(h => h.ToCombatData(Team.Enemy)).ToList();
    }
}
