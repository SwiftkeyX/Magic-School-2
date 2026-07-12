namespace MagicSchool.Battle
{
    // removed: TickStatusCounters, TickDreadZones, ApplyBleedTicks, TickDreadknightShield,
    // TickTricksterDashTrigger, TickTricksterUntargetable, TickKineticMana,
    // ResolveKineticBonusActions, TickCastChannels — these were the per-tick trait-ability
    // and skill-cast phases BattleLoop() called each tick. Trait/skill system, rebuilding
    // fresh. This partial class is intentionally empty until then.
    public partial class AutoBattleResolver
    {
    }
}
