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
            _combatants.Clear();
            _playerPlacements.Clear();

            int idx = 0;
            foreach (var u in units)
            {
                var data = new HeroDataRuntime
                {
                    // Unique per instance so mirror teams (same hero on both sides) never
                    // collide in the grid/_units/placement dictionaries. Purely positional —
                    // no authored identity key is involved (see Hero.md Edge Cases).
                    Id          = $"{u.Team}_{idx++}",
                    DisplayName = u.DisplayName,
                    Team        = u.Team,
                    Icon        = u.Icon,
                    Tint        = u.Tint,
                    MaxHP       = u.MaxHP,
                    CurrentHP   = u.MaxHP,
                    ATK         = u.ATK,
                    DEF         = u.DEF,
                    AttackSpeed = u.AttackSpeed,
                    Range       = u.Range,
                    MG          = u.MG,
                    MR          = u.MR,
                    MaxMana         = u.MaxMana,
                    ManaPerAttack   = u.ManaPerAttack,
                    SkillMultiplier = u.SkillMultiplier,
                    SkillName       = u.SkillName,
                    Mana        = 0,
                    SkillArmed  = false,
                    Traits      = u.Traits ?? new List<TraitDataSO>(),
                };
                _combatants.Add(new HeroSimulation(data));
            }

            Debug.Log($"[AutoChessManager] SetCombatants complete ({_combatants.Count(c => c.Data.IsPlayer)} players, " +
                      $"{_combatants.Count(c => !c.Data.IsPlayer)} enemies) — firing OnCombatantsSet.");
            OnCombatantsSet?.Invoke();
        }

        public void SetUnitPositions(Dictionary<string, HexCoord> placements)
        {
            if (_battleRunning) { Debug.LogError("[AutoChessManager] SetUnitPositions called after battle started."); return; }
            foreach (var kv in placements)
                _playerPlacements[kv.Key] = kv.Value;
        }

        // The single source of truth for where enemies stand. BeginBattle() places the simulation
        // from this, and BattleBoardManager spawns the enemy GameObjects from it — so the sprites
        // and the sim can no longer disagree.
        public Dictionary<string, HexCoord> GetAutoEnemyPlacements()
        {
            var result = new Dictionary<string, HexCoord>();
            if (_grid == null) return result;

            int col = 0;
            int row = _grid.PlayerRowCount;   // first enemy row, immediately past the player's half
            foreach (var c in _combatants.Where(c => !c.Data.IsPlayer))
            {
                if (col >= _grid.Cols) { col = 0; row++; }
                if (row >= _grid.Rows)
                {
                    Debug.LogError($"[AutoChessManager] Ran out of enemy rows placing '{c.Data.DisplayName}' — " +
                                   $"the board ({_grid.Cols}x{_grid.Rows}, {_grid.PlayerRowCount} player rows) " +
                                   $"cannot seat this many enemies.", this);
                    break;
                }
                result[c.Data.Id] = new HexCoord(col++, row);
            }
            return result;
        }

        // Standalone seed path: populates from the roster components on this GameObject.
        // Previously this returned silently when a stub was missing, producing an empty board and
        // an empty bench with no error — the failure mode was indistinguishable from "no heroes
        // authored". It now names exactly what is missing.
        public void EnsureCombatantsInitialized()
        {
            if (_combatants.Count > 0) return;

            var stub     = GetComponent<StudentRosterStub>();
            var database = GetComponent<EnemyDatabaseStub>();

            if (stub == null || database == null)
            {
                var missing = new List<string>();
                if (stub == null)     missing.Add(nameof(StudentRosterStub));
                if (database == null) missing.Add(nameof(EnemyDatabaseStub));
                Debug.LogError($"[AutoChessManager] Cannot seed the battle — {string.Join(" and ", missing)} " +
                               $"missing from GameObject '{name}'. HexGrid, AutoChessManager, both roster " +
                               $"components and BattleBoardManager must all live on the same GameObject.", this);
                return;
            }

            var all = new List<HeroDataSeed>();
            all.AddRange(stub.GetUnits());
            all.AddRange(database.GetUnits());

            if (all.Count == 0)
                Debug.LogWarning($"[AutoChessManager] Roster components on '{name}' contain no HeroDataSO assets — " +
                                 $"the board will be empty.", this);

            SetCombatants(all);
        }

        public List<CombatantSnapshot> GetCombatantSnapshots()
        {
            return _combatants.Select(c => new CombatantSnapshot
            {
                Id          = c.Data.Id,
                DisplayName = c.Data.DisplayName,
                IsStudent   = c.Data.IsPlayer,
                Icon        = c.Data.Icon,
                Tint        = c.Data.Tint,
                MaxHP       = c.Data.MaxHP,
                CurrentHP   = c.Data.CurrentHP,
                Position    = c.Data.Position,
                Range       = c.Data.Range,
            }).ToList();
        }

        public int GetCurrentHP(string id) =>
            _combatants.FirstOrDefault(c => c.Data.Id == id)?.Data.CurrentHP ?? 0;

        public int GetMaxHP(string id) =>
            _combatants.FirstOrDefault(c => c.Data.Id == id)?.Data.MaxHP ?? 0;
    }
}
