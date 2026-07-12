using System.Collections.Generic;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Data-driven definition of a fieldable unit. Authored as an asset and projected into a
    // runtime UnitCombatData per team at battle setup. Carries base stats only — trait
    // bonuses are applied later by the Trait synergy pass, never baked in here. See Hero GDD.
    [CreateAssetMenu(menuName = "MagicSchool/Hero", fileName = "Hero")]
    public class HeroData : ScriptableObject
    {
        public string Id;
        public string DisplayName;
        public int    Cost = 1;              // reserved for a future shop; unused in the base game

        [Header("Base Stats")]
        public int   MaxHP = 50;
        public int   ATK   = 10;
        public int   DEF   = 3;
        public int   MG    = 0;
        public int   MR    = 3;
        public int   CRIT  = 5;
        public float AttackSpeed = 0.3f;     // attacks per second
        public int   Range = 1;              // 1 = melee, >1 = ranged

        [Header("Skill (see Skill.md)")]
        public int    MaxMana = 3;           // attacks-to-charge (with ManaPerAttack); 0 = no skill
        public int    ManaPerAttack = 1;     // mana gained per basic attack
        public float  SkillMultiplier = 2f;  // empowered-hit damage multiplier
        public string SkillName = "Skill";

        public List<BattleBehaviorFlag> Flags  = new List<BattleBehaviorFlag>();
        public List<TraitData>          Traits = new List<TraitData>();

        // Projects this hero into a runtime-seed UnitCombatData for the given team.
        // Never mutates the asset — Flags/Traits are copied into fresh lists.
        public UnitCombatData ToCombatData(Team team)
        {
            return new UnitCombatData
            {
                Id          = Id,
                DisplayName = DisplayName,
                Team        = team,
                MaxHP       = MaxHP,
                ATK         = ATK,
                DEF         = DEF,
                MG          = MG,
                MR          = MR,
                CRIT        = CRIT,
                AttackSpeed = AttackSpeed,
                Range       = Range,
                MaxMana         = MaxMana,
                ManaPerAttack   = ManaPerAttack,
                SkillMultiplier = SkillMultiplier,
                SkillName       = SkillName,
                Flags       = Flags  != null ? new List<BattleBehaviorFlag>(Flags)  : new List<BattleBehaviorFlag>(),
                Traits      = Traits != null ? new List<TraitData>(Traits)          : new List<TraitData>(),
            };
        }
    }
}
