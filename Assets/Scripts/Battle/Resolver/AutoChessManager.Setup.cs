using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Pre-battle setup API (build combatants, inject placements) and the read-only
    // snapshot/HP accessors UI consumers use.
    public partial class AutoChessManager
    {
        // Unified seed API: one list of HeroDataSeed, each tagged with its Team.
        public void SetCombatants(List<HeroDataSeed> units)
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

            Debug.Log($"[AutoChessManager] SetCombatants complete ({_data.Combatants.Count(c => c.Data.IsPlayer)} players, " +
                      $"{_data.Combatants.Count(c => !c.Data.IsPlayer)} enemies) — firing OnCombatantsSet.");
            OnCombatantsSet?.Invoke();
        }

        public void SetPlayerPlacements(Dictionary<string, HexCoord> placements)
        {
            if (_battleRunning) { Debug.LogError("[AutoChessManager] SetPlayerPlacements called after battle started."); return; }
            foreach (var kv in placements)
                _playerPlacements[kv.Key] = kv.Value;
        }

        // Symmetric to SetPlayerPlacements() -- both sides can now receive placement input on
        // top of their authored default formation (StudentRosterStub / EnemyDatabaseStub).
        public void SetEnemyPlacements(Dictionary<string, HexCoord> placements)
        {
            if (_battleRunning) { Debug.LogError("[AutoChessManager] SetEnemyPlacements called after battle started."); return; }
            foreach (var kv in placements)
                _enemyPlacements[kv.Key] = kv.Value;
        }

        // Merges manually-set placements (_playerPlacements, via SetPlayerPlacements) over
        // StudentRosterStub's authored default formation. A unit with neither is left unplaced
        // -- normal before the player has dragged everything, so this does not error.
        public Dictionary<string, HexCoord> GetPlayerPlacements()
        {
            var result = new Dictionary<string, HexCoord>(_playerPlacements);

            var playerStub = GetComponent<StudentRosterStub>();
            if (playerStub == null) return result;

            var players  = _data.Combatants.Where(c => c.Data.IsPlayer).ToList();
            var defaults = playerStub.GetPlacements();

            for (int i = 0; i < players.Count; i++)
            {
                string id = players[i].Data.Id;
                if (result.ContainsKey(id) || i >= defaults.Count) continue;
                result[id] = defaults[i];
            }
            return result;
        }

        // The single source of truth for where enemies stand. BeginBattle() places the simulation
        // from this, and BattleBoardManager spawns the enemy GameObjects from it — so the sprites
        // and the sim can no longer disagree. Merges manually-set placements (_enemyPlacements,
        // via SetEnemyPlacements) over EnemyDatabaseStub's authored default formation — the same
        // standard as player placement, neither side's starting position is computed.
        public Dictionary<string, HexCoord> GetEnemyPlacements()
        {
            var result = new Dictionary<string, HexCoord>();
            var enemyStub = GetComponent<EnemyDatabaseStub>();
            if (enemyStub == null)
            {
                Debug.LogError("[AutoChessManager] Cannot place enemies — EnemyDatabaseStub missing from GameObject.", this);
                return result;
            }

            var enemies  = _data.Combatants.Where(c => !c.Data.IsPlayer).ToList();
            var defaults = enemyStub.GetPlacements();

            for (int i = 0; i < enemies.Count; i++)
            {
                string id = enemies[i].Data.Id;
                if (_enemyPlacements.TryGetValue(id, out var input))
                {
                    result[id] = input;
                    continue;
                }
                if (i >= defaults.Count)
                {
                    Debug.LogError($"[AutoChessManager] No placement for enemy '{enemies[i].Data.DisplayName}' " +
                                   $"(entry {i}) — not set via SetEnemyPlacements(), and EnemyDatabaseStub has only " +
                                   $"{defaults.Count} authored placements for {enemies.Count} enemies.", this);
                    continue;
                }
                result[id] = defaults[i];
            }
            return result;
        }

        // Builds the roster from this GameObject's StudentRosterStub + EnemyDatabaseStub, if it
        // hasn't been seeded already. Errors out naming exactly what's missing, rather than
        // silently producing an empty board.
        public void EnsureCombatantsInitialized()
        {
            if (_data.Combatants.Count > 0) return;

            var playerStub = GetComponent<StudentRosterStub>();
            var enemyStub  = GetComponent<EnemyDatabaseStub>();

            if (playerStub == null || enemyStub == null)
            {
                var missing = new List<string>();
                if (playerStub == null) missing.Add(nameof(StudentRosterStub));
                if (enemyStub == null)  missing.Add(nameof(EnemyDatabaseStub));
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

            SetCombatants(all);
        }

        public List<CombatantSnapshot> GetCombatantSnapshots() => _data.GetCombatantSnapshots();

        public int GetCurrentHP(string id) => _data.GetCurrentHP(id);

        public int GetMaxHP(string id) => _data.GetMaxHP(id);
    }
}
