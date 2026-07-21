using System.Collections.Generic;

namespace MagicSchool.Battle
{
    // Targeting helpers and the shared damage choke point.
    public partial class AutoBattleSimulator
    {
        private HeroDataRuntime FindInRange(HeroDataRuntime actor, List<HeroDataRuntime> opponents)
        {
            HeroDataRuntime nearest = null;
            int minDist = int.MaxValue;
            foreach (var o in opponents)
            {
                int d = HexCoord.Distance(actor.Position, o.Position);
                if (d <= actor.Range && d < minDist) { minDist = d; nearest = o; }
            }
            return nearest;
        }

        // Single choke point for all damage application: subtract HP, optionally fire the event,
        // optionally check the kill. Callers that need to defer the kill check pass
        // autoHandleKill: false and check target.IsDefeated themselves afterward.
        //
        // removed: the shield-absorb branch (and the bypassShield / out shieldAbsorbed params).
        // HeroDataRuntime.Shield was read on every hit but never written by anything — dead weight in
        // the hottest path in the game. Re-add with the first mechanic that actually grants shield.
        internal int ApplyDamageAndCheckKill(HeroDataRuntime actor, HeroDataRuntime target, int damage,
            List<string> tags = null, bool autoHandleKill = true)
        {
            target.CurrentHP -= damage;

            if (tags != null)
                OnCombatantActed?.Invoke(actor?.Id, target.Id, damage, tags);

            if (autoHandleKill && target.IsDefeated)
                HandleKill(actor, target);

            return damage;
        }
    }
}
