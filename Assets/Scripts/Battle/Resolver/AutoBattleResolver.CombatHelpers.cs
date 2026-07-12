using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Targeting helpers and the shared damage mutation choke point.
    // removed: IsActionLocked, SetMana, SetState, Grid/AllCombatants/GetOpponentsOf/
    // GetAlliesOf/GetOccupantAt skill-execution accessors, GetZoneShreddedDefense,
    // GrantMana, AddDreadZone — skill/trait system, rebuilding fresh.
    public partial class AutoBattleResolver
    {
        private Combatant FindInRange(Combatant actor, List<Combatant> opponents)
        {
            Combatant nearest = null;
            int minDist = int.MaxValue;
            foreach (var o in opponents)
            {
                int d = HexCoord.Distance(actor.Position, o.Position);
                if (d <= actor.Range && d < minDist) { minDist = d; nearest = o; }
            }
            return nearest;
        }

        // Shared shield-absorb + HP-subtract + (optional) event + (optional) kill-check
        // choke point for all damage application. Callers that need to defer the kill
        // check pass autoHandleKill: false and check target.IsDefeated themselves
        // afterward. Returns the post-shield damage actually applied to HP.
        // removed: Phalanx-style intercept redirect — skill system, rebuilding fresh.
        internal int ApplyDamageAndCheckKill(Combatant actor, Combatant target, int damage, out int shieldAbsorbed,
            List<string> tags = null, bool bypassShield = false, bool autoHandleKill = true)
        {
            shieldAbsorbed = 0;
            if (!bypassShield && target.Shield > 0)
            {
                shieldAbsorbed = Math.Min(target.Shield, damage);
                target.Shield -= shieldAbsorbed;
                damage        -= shieldAbsorbed;
            }
            target.CurrentHP -= damage;

            if (tags != null)
                OnCombatantActed?.Invoke(actor?.Id, target.Id, damage, tags);

            if (autoHandleKill && target.IsDefeated)
                HandleKill(actor, target);

            return damage;
        }

        internal void MoveUnit(Combatant c, HexCoord dest)
        {
            _grid.ClearOccupant(c.Position);
            var from = c.Position;
            c.Position = dest;
            _grid.SetOccupant(c.Position, c.Id);
            OnCombatantMoved?.Invoke(c.Id, from, c.Position);
        }
    }
}
