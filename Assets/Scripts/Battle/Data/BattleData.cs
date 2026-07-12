using System;
using System.Collections.Generic;

namespace MagicSchool.Battle
{
    public enum DamageType { Physical, Magic }

    // Which side a unit fights for. Replaces the former implicit student/enemy split.
    public enum Team { Player, Enemy }

    // Optional per-unit combat behaviors. MagicAttack makes a unit strike with MG/MR
    // instead of ATK/DEF; the rest are reserved hooks for future abilities.
    public enum BattleBehaviorFlag
    {
        FirstHitDouble,
        AOEAttack,
        TakesReducedDamage,
        ShadowSurge,
        MagicAttack,    // when present, unit uses MG/MR instead of ATK/DEF
    }

    public struct BattleResult
    {
        public bool Won;          // true when the player team won
        public int  TicksElapsed; // simulation ticks the battle ran (10 ticks/second)
        public bool TimedOut;     // true when the battle hit the tick cap instead of a wipe
    }

    // Unified data contract for any unit entering battle, tagged by Team. Replaces the
    // former StudentCombatData + EnemyCombatData split (the duplication was flagged in-code).
    // Produced by HeroData.ToCombatData(); consumed by AutoBattleResolver.SetCombatants().
    [Serializable]
    public class UnitCombatData
    {
        public string Id;
        public string DisplayName;
        public Team   Team;
        public int    MaxHP;
        public int    ATK;
        public int    DEF;
        public int    MG;
        public int    MR;
        public float  AttackSpeed;      // attacks per second
        public int    CRIT;
        public int    Range = 1;        // 1 = melee, >1 = ranged

        // Skill / mana (see Skill.md). MaxMana 0 = no skill.
        public int    MaxMana;
        public int    ManaPerAttack;
        public float  SkillMultiplier;
        public string SkillName;

        public List<BattleBehaviorFlag> Flags  = new List<BattleBehaviorFlag>();
        public List<TraitData>          Traits = new List<TraitData>();
    }

    // Read-only snapshot exposed to BattleHUD and BattleBoardManager for initialization.
    public class CombatantSnapshot
    {
        public string Id;          // unique per combatant instance
        public string HeroId;      // hero/type id — used for cosmetic lookups (colors)
        public string DisplayName;
        public bool   IsStudent;   // true when the unit's Team == Team.Player
        public int    MaxHP;
        public int    CurrentHP;
        public HexCoord Position;
        public int    Range;
        public List<BattleBehaviorFlag> Flags;
    }
}
