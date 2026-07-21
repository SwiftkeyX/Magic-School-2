using System.Collections.Generic;
using System.Linq;

namespace MagicSchool.Battle
{
    // The manager's world state: the roster and the board it fights on. Pulled out of
    // AutoChessManager so AutoChessHelper's queries take one cohesive object instead of two
    // separate parameters. Deliberately does NOT include _playerPlacements (pre-battle setup
    // buffer) or _battleRunning (the manager's own lifecycle guard) -- those aren't part of
    // the simulation's live world state and don't belong here.
    internal class AutoChessData
    {
        public List<HeroSimulation> Combatants { get; } = new List<HeroSimulation>();
        public HexGrid Grid { get; set; }

        // Builds one combatant's runtime state from its seed data and adds it to the roster.
        // Lives here (not AutoChessManager) because it only ever touches Combatants.
        public void AddCombatant(HeroDataSeed seed, string id)
        {
            var data = new HeroDataRuntime
            {
                Id          = id,
                DisplayName = seed.DisplayName,
                Team        = seed.Team,
                Icon        = seed.Icon,
                Tint        = seed.Tint,
                MaxHP       = seed.MaxHP,
                CurrentHP   = seed.MaxHP,
                ATK         = seed.ATK,
                DEF         = seed.DEF,
                AttackSpeed = seed.AttackSpeed,
                Range       = seed.Range,
                MG          = seed.MG,
                MR          = seed.MR,
                MaxMana         = seed.MaxMana,
                ManaPerAttack   = seed.ManaPerAttack,
                SkillMultiplier = seed.SkillMultiplier,
                SkillName       = seed.SkillName,
                Mana        = 0,
                SkillArmed  = false,
                Traits      = seed.Traits ?? new List<TraitDataSO>(),
            };
            Combatants.Add(new HeroSimulation(data));
        }

        public int GetCurrentHP(string id) =>
            Combatants.FirstOrDefault(c => c.Data.Id == id)?.Data.CurrentHP ?? 0;

        public int GetMaxHP(string id) =>
            Combatants.FirstOrDefault(c => c.Data.Id == id)?.Data.MaxHP ?? 0;

        public List<CombatantSnapshot> GetCombatantSnapshots()
        {
            return Combatants.Select(c => new CombatantSnapshot
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
    }
}
