using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Enemy-side seed for the vanilla engine. Holds authored HeroDataSO assets and projects
    // them to HeroDataSeed (Team.Enemy). Replaces the former serialized EnemyCombatData list.
    public class EnemyDatabaseStub : MonoBehaviour
    {
        [SerializeField] private List<HeroDataSO> _enemies = new List<HeroDataSO>();

        public List<HeroDataSeed> GetUnits() =>
            _enemies.Where(h => h != null).Select(h => h.ToCombatData(Team.Enemy)).ToList();
    }
}
