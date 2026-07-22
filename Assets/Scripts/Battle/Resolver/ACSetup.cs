using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Owns pre-battle setup: build combatants, inject placements, the read-only snapshot/HP
    // accessors UI consumers use, and the editor-only debug hooks. Takes AutoChessData and the
    // facade's placement dictionaries as parameters rather than holding a reference to the
    // facade -- same decoupled pattern as HeroSimulation/AutoChessHelper/ACSimulator
    // (Combat.md Interactions table).
    internal class ACSetup
    {
        private readonly ACData _data;
        private readonly GameObject _owner;
        private readonly Dictionary<string, HexCoord> _playerPlacements;
        private readonly Dictionary<string, HexCoord> _enemyPlacements;
        private readonly Func<bool> _isBattleRunning;
        private readonly Action _onCombatantsSet;

        public ACSetup(
            ACData data,
            GameObject owner,
            Dictionary<string, HexCoord> playerPlacements,
            Dictionary<string, HexCoord> enemyPlacements,
            Func<bool> isBattleRunning,
            Action onCombatantsSet)
        {
            _data = data;
            _owner = owner;
            _playerPlacements = playerPlacements;
            _enemyPlacements = enemyPlacements;
            _isBattleRunning = isBattleRunning;
            _onCombatantsSet = onCombatantsSet;
        }

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
            _onCombatantsSet?.Invoke();
        }

        // API for setting hero's placement at the start of the combat
        private void SetInitialCombatantsPlacements(Dictionary<string, HexCoord> target, Dictionary<string, HexCoord> input, string methodName)
        {
            if (_isBattleRunning()) { Debug.LogError($"[AutoChessManager] {methodName} called after battle started."); return; }
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
                                       $"and only {defaults.Count} authored placements exist for {units.Count} units.", _owner);
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

            var playerStub = _owner.GetComponent<StudentRosterStub>();
            var enemyStub = _owner.GetComponent<EnemyDatabaseStub>();

            if (playerStub == null || enemyStub == null)
            {
                var missing = new List<string>();
                if (playerStub == null) missing.Add(nameof(StudentRosterStub));
                if (enemyStub == null) missing.Add(nameof(EnemyDatabaseStub));
                Debug.LogError($"[AutoChessManager] Cannot seed the battle — {string.Join(" and ", missing)} " +
                               $"missing from GameObject '{_owner.name}'. HexGrid, AutoChessManager, both roster " +
                               $"components and BattleBoardManager must all live on the same GameObject.", _owner);
                return;
            }

            var all = new List<HeroDataSeed>();
            all.AddRange(playerStub.GetUnits());
            all.AddRange(enemyStub.GetUnits());

            if (all.Count == 0)
                Debug.LogWarning($"[AutoChessManager] Roster components on '{_owner.name}' contain no HeroDataSO assets — " +
                                 $"the board will be empty.", _owner);

            SetInitialCombatantsRuntimeData(all);
        }

        #region setter & getter
        public void SetPlayerPlacements(Dictionary<string, HexCoord> placements) => SetInitialCombatantsPlacements(_playerPlacements, placements, nameof(SetPlayerPlacements));
        public void SetEnemyPlacements(Dictionary<string, HexCoord> placements) => SetInitialCombatantsPlacements(_enemyPlacements, placements, nameof(SetEnemyPlacements));

        public Dictionary<string, HexCoord> GetPlayerPlacements()
        {
            var playerStub = _owner.GetComponent<StudentRosterStub>();
            var defaults = playerStub != null ? playerStub.GetPlacements() : new List<HexCoord>();

            return CheckEachHeroPlacement(isPlayer: true, _playerPlacements, defaults, errorOnMissing: false);
        }

        public Dictionary<string, HexCoord> GetEnemyPlacements()
        {
            var enemyStub = _owner.GetComponent<EnemyDatabaseStub>();
            if (enemyStub == null)
            {
                Debug.LogError("[AutoChessManager] Cannot place enemies — EnemyDatabaseStub missing from GameObject.", _owner);
                return new Dictionary<string, HexCoord>();
            }

            return CheckEachHeroPlacement(isPlayer: false, _enemyPlacements, enemyStub.GetPlacements(), errorOnMissing: true);
        }
        #endregion

        // ── Debug ────────────────────────────────────────────────────────────────
        // Folded in from AutoChessManager.Debug.cs -- editor/QA-only hooks, callable shortcuts
        // for testing. Don't participate in battle control flow.
#if UNITY_EDITOR
        public void DebugSetAllPlayerHp(float pct)
        {
            foreach (var c in _data.Combatants)
                if (c.Data.IsPlayer) c.Data.CurrentHP = Mathf.Max(1, Mathf.RoundToInt(c.Data.MaxHP * pct));
        }

        // removed: DebugForceCast(string combatantId) — skill-cast system, rebuilding fresh.
#endif
    }
}
