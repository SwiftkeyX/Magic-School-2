using System.Collections.Generic;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Per-unit runtime simulation state built by AutoChessManager.SetCombatants()
    // from HeroDataSeed. Never persisted.
    internal class HeroDataRuntime
    {
        public string Id;          // unique per combatant instance (grid/units/placement key)
        public string DisplayName;
        public Team Team;
        public bool IsPlayer => Team == Team.Player;

        // Presentation, carried from HeroDataSO so the view never has to look it up by Id.
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
        // Two independent clocks charged and clamped by AutoChessManager.BattleLoop() —
        // see the comment above Phase 1 there for how and why.
        public float AttackCooldown;
        public float MoveCooldown;
        public bool IsDefeated => CurrentHP <= 0;

        public List<TraitDataSO> Traits;        // synergy tags; read by the trait pass at BeginBattle()
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
