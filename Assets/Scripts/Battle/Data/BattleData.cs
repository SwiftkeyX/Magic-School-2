using System;
using System.Collections.Generic;
using UnityEngine;

namespace MagicSchool.Battle
{
    public enum DamageType { Physical, Magic }

    // Which side a unit fights for. Replaces the former implicit student/enemy split.
    public enum Team { Player, Enemy }

    public struct BattleResult
    {
        public bool Won;          // true when the player team won
        public int  TicksElapsed; // simulation ticks the battle ran (10 ticks/second)
        public bool TimedOut;     // true when the battle hit the tick cap instead of a wipe
    }

    // Unified data contract for any unit entering battle, tagged by Team.
    // Produced by HeroData.ToCombatData(); consumed by AutoBattleSimulator.SetCombatants().
    //
    // Tint is already resolved to the fighting side by ToCombatData(), so nothing downstream
    // has to branch on Team to know how to draw the unit.
    [Serializable]
    public class UnitCombatData
    {
        public string DisplayName;
        public Team   Team;

        // Presentation, authored on HeroData. Carrying it here (and on into CombatantSnapshot)
        // is what lets the board render a unit without a hardcoded Id → color lookup.
        public Sprite Icon;
        public Color  Tint = Color.white;

        public int    MaxHP;
        public int    ATK;
        public int    DEF;
        public int    MG;
        public int    MR;
        public float  AttackSpeed;      // attacks per second
        public int    Range = 1;        // 1 = melee, >1 = ranged

        // Skill / mana (see Skill.md). MaxMana 0 = no skill.
        public int    MaxMana;
        public int    ManaPerAttack;
        public float  SkillMultiplier;
        public string SkillName;

        public List<TraitData>          Traits = new List<TraitData>();
    }

    // Read-only snapshot exposed to BattleHUD and BattleBoardManager for initialization.
    // This is the view's ONLY source of unit appearance — see Hero GDD Core Rule 7.
    public class CombatantSnapshot
    {
        public string Id;          // unique per combatant instance
        public string DisplayName;
        public bool   IsStudent;   // true when the unit's Team == Team.Player
        public Sprite Icon;        // authored on HeroData; null → procedural fallback square
        public Color  Tint;        // authored on HeroData, resolved for this unit's team
        public int    MaxHP;
        public int    CurrentHP;
        public HexCoord Position;
        public int    Range;
    }
}
