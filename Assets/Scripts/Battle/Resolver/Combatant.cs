using System.Collections.Generic;

namespace MagicSchool.Battle
{
    // Per-unit runtime simulation state built by AutoBattleResolver.SetCombatants()
    // from UnitCombatData. Never persisted.
    internal class Combatant
    {
        public string Id;          // unique per combatant instance (grid/units/placement key)
        public string HeroId;      // hero/type id (e.g. "knight") — used for cosmetic lookups only
        public string DisplayName;
        public Team Team;
        public bool IsPlayer => Team == Team.Player;
        public int MaxHP;
        public int CurrentHP;
        public int ATK;
        public int DEF;
        public int MG;
        public int MR;
        public float AttackSpeed;
        public int Range;
        public HexCoord Position;
        public float ActionProgress;  // accumulates AttackSpeed × TickDelay each tick; fires at ≥ 1.0
        public bool IsDefeated => CurrentHP <= 0;

        public List<BattleBehaviorFlag> Flags;
        public List<TraitData> Traits;        // synergy tags; read by the trait pass at BeginBattle()
        public int Shield;         // general shield-absorption pool (generic damage-absorb mechanic)
        public string CurrentTargetId;        // last basic-attack target; used by the "Current Target" priority sort

        // ── Skill / mana (see Skill.md) ─────────────────────────────────────
        public int    Mana;              // current charge; starts at 0
        public int    MaxMana;           // 0 = no skill
        public int    ManaPerAttack;     // gained per basic attack
        public bool   SkillArmed;        // when true, the next attack is empowered
        public float  SkillMultiplier;   // empowered-hit damage multiplier
        public string SkillName;

        // removed: ChampionId, ChampionRole Role — champion system, rebuilding fresh
        // removed: IsFrontRow, OmnivampPct, BleedDamagePerTick/BleedTicksRemaining,
        //   DreadknightState/StrikerState/TricksterState/ElementalistState/RangerState
        //   and their Dreadknight/Striker/Trickster/Elementalist/Ranger fields — trait system, rebuilding fresh
        // removed: Mana/MaxMana, CastState State, CastTicksRemaining, PendingTargetHex,
        //   IsSilenced/SilenceTicksRemaining, IsStunned/StunTicksRemaining, SkillDefinition Skill,
        //   InterceptPct/InterceptTicksRemaining — skill-cast system, rebuilding fresh
    }
}
