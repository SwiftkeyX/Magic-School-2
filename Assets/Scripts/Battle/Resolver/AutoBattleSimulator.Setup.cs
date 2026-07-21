using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Pre-battle setup API (build combatants, inject placements) and the read-only
    // snapshot/HP accessors UI consumers use.
    public partial class AutoBattleSimulator
    {
        // Unified seed API: one list of UnitCombatData, each tagged with its Team.
        public void SetCombatants(List<UnitCombatData> units)
        {
            _combatants.Clear();
            _playerPlacements.Clear();

            int idx = 0;
            foreach (var u in units)
            {
                _combatants.Add(new Combatant
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
                    Traits      = u.Traits ?? new List<TraitData>(),
                });
            }

            Debug.Log($"[AutoBattleSimulator] SetCombatants complete ({_combatants.Count(c => c.IsPlayer)} players, " +
                      $"{_combatants.Count(c => !c.IsPlayer)} enemies) — firing OnCombatantsSet.");
            OnCombatantsSet?.Invoke();
        }

        public void SetUnitPositions(Dictionary<string, HexCoord> placements)
        {
            if (_battleRunning) { Debug.LogError("[AutoBattleSimulator] SetUnitPositions called after battle started."); return; }
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
            foreach (var c in _combatants.Where(c => !c.IsPlayer))
            {
                if (col >= _grid.Cols) { col = 0; row++; }
                if (row >= _grid.Rows)
                {
                    Debug.LogError($"[AutoBattleSimulator] Ran out of enemy rows placing '{c.DisplayName}' — " +
                                   $"the board ({_grid.Cols}x{_grid.Rows}, {_grid.PlayerRowCount} player rows) " +
                                   $"cannot seat this many enemies.", this);
                    break;
                }
                result[c.Id] = new HexCoord(col++, row);
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
                Debug.LogError($"[AutoBattleSimulator] Cannot seed the battle — {string.Join(" and ", missing)} " +
                               $"missing from GameObject '{name}'. HexGrid, AutoBattleSimulator, both roster " +
                               $"components and BattleBoardManager must all live on the same GameObject.", this);
                return;
            }

            var all = new List<UnitCombatData>();
            all.AddRange(stub.GetUnits());
            all.AddRange(database.GetUnits());

            if (all.Count == 0)
                Debug.LogWarning($"[AutoBattleSimulator] Roster components on '{name}' contain no HeroData assets — " +
                                 $"the board will be empty.", this);

            SetCombatants(all);
        }

        public List<CombatantSnapshot> GetCombatantSnapshots()
        {
            return _combatants.Select(c => new CombatantSnapshot
            {
                Id          = c.Id,
                DisplayName = c.DisplayName,
                IsStudent   = c.IsPlayer,
                Icon        = c.Icon,
                Tint        = c.Tint,
                MaxHP       = c.MaxHP,
                CurrentHP   = c.CurrentHP,
                Position    = c.Position,
                Range       = c.Range,
            }).ToList();
        }

        public int GetCurrentHP(string id) =>
            _combatants.FirstOrDefault(c => c.Id == id)?.CurrentHP ?? 0;

        public int GetMaxHP(string id) =>
            _combatants.FirstOrDefault(c => c.Id == id)?.MaxHP ?? 0;
    }
}
