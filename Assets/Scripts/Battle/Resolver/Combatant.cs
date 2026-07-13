using System.Collections.Generic;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Per-unit runtime simulation state built by AutoBattleResolver.SetCombatants()
    // from UnitCombatData. Never persisted.
    internal class Combatant
    {
        public string Id;          // unique per combatant instance (grid/units/placement key)
        public string HeroId;      // hero/type id (e.g. "knight") — stable identity of the unit type
        public string DisplayName;
        public Team Team;
        public bool IsPlayer => Team == Team.Player;

        // Presentation, carried from HeroData so the view never has to look it up by Id.
        public Sprite Icon;
        public Color Tint;

        public int MaxHP;
        public int CurrentHP;
        public int ATK;
        public int DEF;
        public int MG;
        public int MR;
        public float AttackSpeed;
        public int Range;
        public HexCoord Position;
        public float ActionProgress;  // accumulates AttackSpeed × tick delay each tick; fires at ≥ 1.0
        public bool IsDefeated => CurrentHP <= 0;

        public List<BattleBehaviorFlag> Flags;
        public List<TraitData> Traits;        // synergy tags; read by the trait pass at BeginBattle()
        public string CurrentTargetId;        // last basic-attack target

        // ── Skill / mana (see Skill.md) ─────────────────────────────────────
        public int    Mana;              // current charge; starts at 0
        public int    MaxMana;           // 0 = no skill
        public int    ManaPerAttack;     // gained per basic attack
        public bool   SkillArmed;        // when true, the next attack is empowered
        public float  SkillMultiplier;   // empowered-hit damage multiplier
        public string SkillName;

        // removed: Shield — read on every hit in ApplyDamageAndCheckKill, but never written by
        // anything. Re-add with the first mechanic that actually grants shield.
    }
}
