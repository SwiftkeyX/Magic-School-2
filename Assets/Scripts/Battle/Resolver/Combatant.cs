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
        // Attack cooldown as a 0→1 fraction of one attack cycle, not a countdown timer. Each tick
        // adds AttackSpeed × tickDelay; at ≥ 1.0 the unit acts, then 1.0 is SUBTRACTED rather than
        // reset to zero — so a fast unit's overflow carries into the next cycle instead of being
        // discarded. That carry is what keeps attack speed continuous rather than quantised to the
        // tick rate: at 0.1s/tick, AttackSpeed 0.35 and 0.30 stay genuinely different.
        public float ActionProgress;
        public bool IsDefeated => CurrentHP <= 0;

        public List<BattleBehaviorFlag> Flags;
        public List<TraitData> Traits;        // synergy tags; read by the trait pass at BeginBattle()
        public string CurrentTargetId;        // last basic-attack target

        // ── Skill / mana (see Skill.md) ─────────────────────────────────────
        public int Mana;              // current charge; starts at 0
        public int MaxMana;           // 0 = no skill
        public int ManaPerAttack;     // gained per basic attack
        public bool SkillArmed;        // when true, the next attack is empowered
        public float SkillMultiplier;   // empowered-hit damage multiplier
        public string SkillName;

        // removed: Shield — read on every hit in ApplyDamageAndCheckKill, but never written by
        // anything. Re-add with the first mechanic that actually grants shield.
    }
}
