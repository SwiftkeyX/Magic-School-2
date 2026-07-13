using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Basic-attack resolution and the kill/death handoff.
    // removed: ApplyDamage() — a private wrapper with no caller.
    public partial class AutoBattleResolver
    {
        private void Attack(Combatant actor, Combatant target)
        {
            actor.CurrentTargetId = target.Id;

            bool isMagic   = actor.Flags != null && actor.Flags.Contains(BattleBehaviorFlag.MagicAttack);
            int rawOffense = isMagic ? actor.MG  : actor.ATK;
            int rawDefense = isMagic ? target.MR : target.DEF;

            int damage = CombatMath.ApplyMitigation(rawOffense, rawDefense);

            // SKILL: a charged unit empowers its next attack (see Skill.md).
            bool cast = false;
            if (actor.SkillArmed)
            {
                damage = Mathf.RoundToInt(damage * actor.SkillMultiplier);
                actor.SkillArmed = false;
                cast = true;
                Debug.Log($"[AutoBattle] SKILL! {actor.DisplayName} casts {actor.SkillName} — empowered attack (x{actor.SkillMultiplier})");
            }

            damage = ApplyDamageAndCheckKill(actor, target, damage, tags: null, autoHandleKill: false);

            Debug.Log($"[AutoBattle] {actor.DisplayName} → {target.DisplayName}: {damage} dmg{(cast ? " [SKILL]" : "")} (HP:{target.CurrentHP}/{target.MaxHP})");
            OnCombatantActed?.Invoke(actor.Id, target.Id, damage, new List<string>());

            // MANA: gain after attacking; arm the skill for the NEXT attack when full.
            if (actor.MaxMana > 0)
            {
                actor.Mana += actor.ManaPerAttack;
                if (actor.Mana >= actor.MaxMana)
                {
                    actor.Mana = 0;
                    actor.SkillArmed = true;
                    Debug.Log($"[AutoBattle] {actor.DisplayName} mana full — {actor.SkillName} armed for next attack");
                }
            }

            if (target.IsDefeated)
                HandleKill(actor, target);
        }

        internal void HandleKill(Combatant actor, Combatant target)
        {
            _grid.ClearOccupant(target.Position);
            Debug.Log($"[AutoBattle] {target.DisplayName} DEFEATED");
            OnCombatantDefeated?.Invoke(target.Id);
        }

        private void MoveTowardNearest(Combatant actor, List<Combatant> opponents)
        {
            var oppPositions = opponents.Select(o => o.Position).ToList();
            var nearest      = _grid.FindNearest(actor.Position, oppPositions);
            if (nearest == null) return;

            var next = _grid.GetNextStep(actor.Position, nearest.Value, actor.Id);
            if (next == null) return;

            _grid.ClearOccupant(actor.Position);
            var from       = actor.Position;
            actor.Position = next.Value;
            _grid.SetOccupant(actor.Position, actor.Id);

            Debug.Log($"[AutoBattle] {actor.DisplayName} moves {from} → {actor.Position}");
            OnCombatantMoved?.Invoke(actor.Id, from, actor.Position);
        }
    }
}
