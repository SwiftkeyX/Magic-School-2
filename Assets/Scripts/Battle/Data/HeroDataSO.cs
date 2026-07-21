using System.Collections.Generic;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Data-driven definition of a fieldable unit. Authored as an asset and projected into a
    // runtime HeroDataSeed per team at battle setup. Carries base stats only — trait
    // bonuses are applied later by the Trait synergy pass, never baked in here. See Hero GDD.
    //
    // Presentation (Icon/tints) lives here too, by Hero GDD Core Rule 7: no system may map a
    // hero Id to a visual via a hardcoded switch. Adding a hero must never require a C# edit.
    [CreateAssetMenu(menuName = "MagicSchool/Hero", fileName = "Hero")]
    public class HeroDataSO : ScriptableObject
    {
        [Tooltip("Name shown on the bench card and in combat logs.")]
        public string DisplayName;

        [Header("Presentation")]
        [Tooltip("Unit sprite. Leave empty to fall back to a plain procedural square.")]
        public Sprite Icon;

        [Tooltip("Tint applied when this hero fights on the player's side.")]
        public Color PlayerTint = new Color(0.3f, 0.3f, 0.3f);

        [Tooltip("Tint applied when this same hero fights on the enemy's side.")]
        public Color EnemyTint = Color.gray;

        [Header("Base Stats")]
        [Range(Guardrails.MinMaxHP, 800), Tooltip("Starting and maximum health.")]
        public int MaxHP = 50;

        [Range(0, 80), Tooltip("Physical attack. Mitigated by the target's DEF.")]
        public int ATK = 10;

        [Range(Guardrails.MinDefense, 50), Tooltip("Physical mitigation.")]
        public int DEF = 3;

        [Range(0, 80), Tooltip("Magic attack. Not yet consumed by combat — no magic-damage mechanic exists (see Hero.md Core Rule 6).")]
        public int MG = 0;

        [Range(Guardrails.MinDefense, 50), Tooltip("Magic mitigation.")]
        public int MR = 3;

        [Range(Guardrails.MinAttackSpeed, 1f), Tooltip("Attacks per second. 0 would mean the unit NEVER acts — clamped.")]
        public float AttackSpeed = 0.3f;

        [Range(1, 4), Tooltip("Attack range in hexes. 1 = melee.")]
        public int Range = 1;

        [Header("Skill (see Skill.md)")]
        [Range(0, 10), Tooltip("Mana needed to arm the skill. 0 = this hero has no skill.")]
        public int MaxMana = 3;

        [Range(1, 3), Tooltip("Mana gained per basic attack.")]
        public int ManaPerAttack = 1;

        [Range(Guardrails.MinSkillMultiplier, 3f), Tooltip("Empowered-hit damage multiplier. Below 1 would make the skill WEAKER — clamped.")]
        public float SkillMultiplier = 2f;

        [Tooltip("Skill name shown when the empowered hit lands.")]
        public string SkillName = "Skill";

        [Header("Combat / Synergy")]
        [Tooltip("Synergy tags. Fielding enough carriers of a trait activates its bonus.")]
        public List<TraitDataSO> Traits = new List<TraitDataSO>();

        // Authoring floors, grouped so a reader sees at a glance that these four are a matched set —
        // each guards one specific silent-failure mode (see the Authoring Guardrails table in
        // Hero.md), not four unrelated constants that happen to sit next to each other.
        private static class Guardrails
        {
            public const int   MinMaxHP           = 1;      // 0 → CurrentHP/MaxHP = NaN, unit dead on spawn
            public const int   MinDefense         = 0;      // -100 → divide-by-zero in ApplyMitigation
            public const float MinAttackSpeed     = 0.05f;  // 0 → unit never acts; battle stalls to the tick cap
            public const float MinSkillMultiplier = 1f;     // <1 → the "empowered" hit lands weaker than a normal one
        }

        // [Range] guards the slider, but a value can still arrive via script, a merge, or a
        // hand-edited .asset — so the floors are enforced here as well.
        private void OnValidate()
        {
            MaxHP = Mathf.Max(Guardrails.MinMaxHP, MaxHP);
            DEF = Mathf.Max(Guardrails.MinDefense, DEF);
            MR = Mathf.Max(Guardrails.MinDefense, MR);
            AttackSpeed = Mathf.Max(Guardrails.MinAttackSpeed, AttackSpeed);
            SkillMultiplier = Mathf.Max(Guardrails.MinSkillMultiplier, SkillMultiplier);
            MaxMana = Mathf.Max(0, MaxMana);
            Range = Mathf.Max(1, Range);
        }

        // Projects this hero into a runtime-seed HeroDataSeed for the given team.
        // Never mutates the asset — Traits is copied into a fresh list.
        // Tint is resolved to the side this hero is fighting for, so no consumer downstream
        // ever needs to ask "which team is this?" to know how to draw it.
        public HeroDataSeed ToCombatData(Team team)
        {
            return new HeroDataSeed
            {
                DisplayName = DisplayName,
                Team = team,
                Icon = Icon,
                Tint = team == Team.Player ? PlayerTint : EnemyTint,
                MaxHP = MaxHP,
                ATK = ATK,
                DEF = DEF,
                MG = MG,
                MR = MR,
                AttackSpeed = AttackSpeed,
                Range = Range,
                MaxMana = MaxMana,
                ManaPerAttack = ManaPerAttack,
                SkillMultiplier = SkillMultiplier,
                SkillName = SkillName,
                Traits = Traits != null ? new List<TraitDataSO>(Traits) : new List<TraitDataSO>(),
            };
        }
    }
}
