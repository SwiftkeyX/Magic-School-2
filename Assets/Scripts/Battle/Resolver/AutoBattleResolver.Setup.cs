using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Pre-battle setup API (build combatants, inject placements, apply trait
    // modifiers) and the read-only snapshot/HP/mana accessors UI consumers use.
    public partial class AutoBattleResolver
    {
        // Unified seed API: one list of UnitCombatData, each tagged with its Team.
        // Replaces the former (students, enemies) two-list signature.
        public void SetCombatants(List<UnitCombatData> units)
        {
            _combatants.Clear();
            _playerPlacements.Clear();

            int idx = 0;
            foreach (var u in units)
            {
                _combatants.Add(new Combatant
                {
                    // Unique per instance so mirror teams (same hero id on both sides) never
                    // collide in the grid/_units/placement dictionaries. HeroId keeps the type.
                    Id          = $"{u.Team}_{u.Id}_{idx++}",
                    HeroId      = u.Id,
                    DisplayName = u.DisplayName,
                    Team        = u.Team,
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
                    Flags       = u.Flags  ?? new List<BattleBehaviorFlag>(),
                    Traits      = u.Traits ?? new List<TraitData>(),
                });
            }

            // Signal subscribers (e.g. BattleHUD) that GetCombatantSnapshots() now
            // reflects real data. No payload — callers pull snapshots themselves.
            Debug.Log($"[AutoBattleResolver] SetCombatants complete ({_combatants.Count(c => c.IsPlayer)} players, " +
                      $"{_combatants.Count(c => !c.IsPlayer)} enemies) — firing OnCombatantsSet.");
            OnCombatantsSet?.Invoke();
        }

        public void SetUnitPositions(Dictionary<string, HexCoord> placements)
        {
            if (_battleRunning) { Debug.LogError("[AutoBattleResolver] SetUnitPositions called after battle started."); return; }
            foreach (var kv in placements)
                _playerPlacements[kv.Key] = kv.Value;
        }

        // Returns auto-assigned enemy positions without starting the battle.
        public Dictionary<string, HexCoord> GetAutoEnemyPlacements()
        {
            var result = new Dictionary<string, HexCoord>();
            int col    = 0;
            int row    = HexGrid.PlayerRowCount;   // row 4 = enemy front
            foreach (var c in _combatants.Where(c => !c.IsPlayer))
            {
                if (col >= HexGrid.Cols) { col = 0; row++; }
                result[c.Id] = new HexCoord(col++, row);
            }
            return result;
        }

        // Standalone fallback: populates from StudentRosterStub/EnemyDatabaseStub components
        // on this GameObject. This is now the only seed path — no ChampionRoster in this engine.
        // Callers must invoke this themselves before reading snapshots if they can't guarantee
        // SetCombatants already ran — see BattleBoardManager.Start().
        public void EnsureCombatantsInitialized()
        {
            if (_combatants.Count > 0) return;

            var stub     = GetComponent<StudentRosterStub>();
            var database = GetComponent<EnemyDatabaseStub>();
            if (stub != null && database != null)
            {
                var all = new List<UnitCombatData>();
                all.AddRange(stub.GetUnits());
                all.AddRange(database.GetUnits());
                SetCombatants(all);
            }
        }

        public List<CombatantSnapshot> GetCombatantSnapshots()
        {
            return _combatants.Select(c => new CombatantSnapshot
            {
                Id          = c.Id,
                HeroId      = c.HeroId,
                DisplayName = c.DisplayName,
                IsStudent   = c.IsPlayer,
                MaxHP       = c.MaxHP,
                CurrentHP   = c.CurrentHP,
                Position    = c.Position,
                Range       = c.Range,
                Flags       = c.Flags != null
                                  ? new List<BattleBehaviorFlag>(c.Flags)
                                  : new List<BattleBehaviorFlag>(),
            }).ToList();
        }

        public int GetCurrentHP(string id) =>
            _combatants.FirstOrDefault(c => c.Id == id)?.CurrentHP ?? 0;

        public int GetMaxHP(string id) =>
            _combatants.FirstOrDefault(c => c.Id == id)?.MaxHP ?? 0;

        // removed: GetCurrentMana/GetMaxMana, ApplyPreBattleTraitModifiers(...) — trait/skill
        // system, rebuilding fresh. There is no mana or per-unit trait modifier pass in the
        // standalone engine; combatants use their base stats as-is.
    }
}
