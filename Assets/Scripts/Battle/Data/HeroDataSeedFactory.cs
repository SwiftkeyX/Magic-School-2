using System.Collections.Generic;

namespace MagicSchool.Battle
{
    // Projects an authored HeroDataSO into a runtime-seed HeroDataSeed for a given team. Lives
    // here instead of on HeroDataSO so the authored asset never needs to know about the seed
    // layer -- StudentRosterStub/EnemyDatabaseStub (the seed sources) are the boundary between
    // "what a unit is" and "how it enters battle," per Hero.md's Interactions table.
    internal static class HeroDataSeedFactory
    {
        // Never mutates hero -- Traits is copied into a fresh list. Tint is resolved to the
        // side this hero is fighting for, so no consumer downstream ever needs to ask "which
        // team is this?" to know how to draw it.
        public static HeroDataSeed ToCombatData(HeroDataSO hero, Team team)
        {
            return new HeroDataSeed
            {
                DisplayName = hero.DisplayName,
                Team = team,
                Icon = hero.Icon,
                Tint = team == Team.Player ? hero.PlayerTint : hero.EnemyTint,
                MaxHP = hero.MaxHP,
                ATK = hero.ATK,
                DEF = hero.DEF,
                MG = hero.MG,
                MR = hero.MR,
                AttackSpeed = hero.AttackSpeed,
                Range = hero.Range,
                MaxMana = hero.MaxMana,
                ManaPerAttack = hero.ManaPerAttack,
                SkillMultiplier = hero.SkillMultiplier,
                SkillName = hero.SkillName,
                Traits = hero.Traits != null ? new List<TraitDataSO>(hero.Traits) : new List<TraitDataSO>(),
            };
        }
    }
}
