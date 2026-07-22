using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Pre-battle setup API (build combatants, inject placements) and the read-only
    // snapshot/HP accessors UI consumers use.
    public partial class AutoChessManager
    {
        // Unified seed API: make HeroDataRuntime when combat start
        public void SetInitialCombatantsRuntimeData(List<HeroDataSeed> units)
        {
            _data.Combatants.Clear();
            _playerPlacements.Clear();
            _enemyPlacements.Clear();

            // Unique per instance so mirror teams (same hero on both sides) never collide in
            // the grid/_units/placement dictionaries. Purely positional -- no authored identity
            // key is involved (see Hero.md Edge Cases).
            int idx = 0;
            foreach (var u in units)
                _data.AddCombatant(u, $"{u.Team}_{idx++}");

            Debug.Log($"[AutoChessManager] SetInitialCombatantsRuntimeData complete ({_data.Combatants.Count(c => c.Data.IsPlayer)} players, " +
                      $"{_data.Combatants.Count(c => !c.Data.IsPlayer)} enemies) — firing OnCombatantsSet.");
            OnCombatantsSet?.Invoke();
        }

        // API for setting hero's placement at the start of the combat
        private void SetInitialCombatantsPlacements(Dictionary<string, HexCoord> target, Dictionary<string, HexCoord> input, string methodName)
        {
            if (_battleRunning) { Debug.LogError($"[AutoChessManager] {methodName} called after battle started."); return; }
            foreach (var kv in input)
                target[kv.Key] = kv.Value;
        }

        // Function to check if each hero starting placements is set or not. 
        // If not, use default value for that placements
        private Dictionary<string, HexCoord> CheckEachHeroPlacement(bool isPlayer, Dictionary<string, HexCoord> input, List<HexCoord> defaults, bool errorOnMissing)
        {
            var result = new Dictionary<string, HexCoord>(input);
            var units = _data.Combatants.Where(c => c.Data.IsPlayer == isPlayer).ToList();

            for (int i = 0; i < units.Count; i++)
            {
                string id = units[i].Data.Id;

                bool isUnitOnTheBoard = result.ContainsKey(id);
                if (isUnitOnTheBoard) continue;

                if (i >= defaults.Count)
                {
                    if (errorOnMissing)
                        Debug.LogError($"[AutoChessManager] No placement for '{units[i].Data.DisplayName}' " +
                                       $"(entry {i}) — not set via Set{(isPlayer ? "Player" : "Enemy")}Placements(), " +
                                       $"and only {defaults.Count} authored placements exist for {units.Count} units.", this);
                    continue;
                }
                result[id] = defaults[i];
            }

            return result;
        }

        // Builds the hero roster in runtime from this StudentRosterStub + EnemyDatabaseStub
        public void EnsureCombatantsInitialized()
        {
            if (_data.Combatants.Count > 0) return;

            var playerStub = GetComponent<StudentRosterStub>();
            var enemyStub = GetComponent<EnemyDatabaseStub>();

            if (playerStub == null || enemyStub == null)
            {
                var missing = new List<string>();
                if (playerStub == null) missing.Add(nameof(StudentRosterStub));
                if (enemyStub == null) missing.Add(nameof(EnemyDatabaseStub));
                Debug.LogError($"[AutoChessManager] Cannot seed the battle — {string.Join(" and ", missing)} " +
                               $"missing from GameObject '{name}'. HexGrid, AutoChessManager, both roster " +
                               $"components and BattleBoardManager must all live on the same GameObject.", this);
                return;
            }

            var all = new List<HeroDataSeed>();
            all.AddRange(playerStub.GetUnits());
            all.AddRange(enemyStub.GetUnits());

            if (all.Count == 0)
                Debug.LogWarning($"[AutoChessManager] Roster components on '{name}' contain no HeroDataSO assets — " +
                                 $"the board will be empty.", this);

            SetInitialCombatantsRuntimeData(all);
        }


        public List<CombatantSnapshot> GetCombatantSnapshots() => _data.GetCombatantSnapshots();

        public int GetCurrentHP(string id) => _data.GetCurrentHP(id);

        public int GetMaxHP(string id) => _data.GetMaxHP(id);


        #region setter & getter
        public void SetPlayerPlacements(Dictionary<string, HexCoord> placements) => SetInitialCombatantsPlacements(_playerPlacements, placements, nameof(SetPlayerPlacements));
        public void SetEnemyPlacements(Dictionary<string, HexCoord> placements) => SetInitialCombatantsPlacements(_enemyPlacements, placements, nameof(SetEnemyPlacements));

        public Dictionary<string, HexCoord> GetPlayerPlacements()
        {
            var playerStub = GetComponent<StudentRosterStub>();
            var defaults = playerStub != null ? playerStub.GetPlacements() : new List<HexCoord>();

            return CheckEachHeroPlacement(isPlayer: true, _playerPlacements, defaults, errorOnMissing: false);
        }

        public Dictionary<string, HexCoord> GetEnemyPlacements()
        {
            var enemyStub = GetComponent<EnemyDatabaseStub>();
            if (enemyStub == null)
            {
                Debug.LogError("[AutoChessManager] Cannot place enemies — EnemyDatabaseStub missing from GameObject.", this);
                return new Dictionary<string, HexCoord>();
            }

            return CheckEachHeroPlacement(isPlayer: false, _enemyPlacements, enemyStub.GetPlacements(), errorOnMissing: true);
        }
        #endregion
    }
}
