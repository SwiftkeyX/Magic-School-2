using System.Collections.Generic;
using UnityEngine;

namespace MagicSchool.Battle
{
    // One per unit, wrapping its HeroDataRuntime. Owns the actual per-tick writes once the
    // manager (AutoChessManager) says it's this unit's turn: charging clocks, resolving an
    // attack, or taking a step. Holds no reference back to the manager -- TryAttack()/TryMove()
    // return what happened, and the manager translates that into events. See Combat.md Core Rule 1.
    internal class HeroSimulation
    {
        public HeroDataRuntime Data { get; }

        public HeroSimulation(HeroDataRuntime data)
        {
            Data = data;
        }

        // ── Charge / Clamp (Combat.md Core Rule 4, phases 1 and 4) ──────────────────────────
        public void ChargeClocks(float tickDelay, float moveSpeed)
        {
            Data.AttackCooldown += Data.AttackSpeed * tickDelay;
            Data.MoveCooldown += moveSpeed * tickDelay;
        }

        public void ClampClocks()
        {
            Data.AttackCooldown = Mathf.Min(Data.AttackCooldown, 1f);
            Data.MoveCooldown = Mathf.Min(Data.MoveCooldown, 1f);
        }

        // ── Attack (Combat.md Core Rule 4 phase 2; Skill.md Core Rule 3) ────────────────────
        // Returns null if nothing was in range -- the unit keeps its charge (Combat.md Rule 4.2).
        public AttackResult? TryAttack(List<HeroDataRuntime> opponents)
        {
            var target = FindInRange(Data, opponents);
            if (target == null) return null;

            Data.CurrentTargetId = target.Id;

            // Damage archetype (physical/magic) is not yet a mechanic -- every attack resolves
            // ATK vs DEF until a real magic-damage system is designed on the action/skill itself
            // (see Hero.md Core Rule 6, Skill.md Core Rule 5).
            int damage = CombatMath.ApplyMitigation(Data.ATK, target.DEF);

            // SKILL: a charged unit empowers its next attack (see Skill.md).
            bool cast = false;
            if (Data.SkillArmed)
            {
                damage = Mathf.RoundToInt(damage * Data.SkillMultiplier);
                Data.SkillArmed = false;
                cast = true;
                Debug.Log($"[AutoBattle] SKILL! {Data.DisplayName} casts {Data.SkillName} — empowered attack (x{Data.SkillMultiplier})");
            }

            target.CurrentHP -= damage;
            bool wasKill = target.IsDefeated;

            Debug.Log($"[AutoBattle] {Data.DisplayName} → {target.DisplayName}: {damage} dmg{(cast ? " [SKILL]" : "")} (HP:{target.CurrentHP}/{target.MaxHP})");

            // MANA: gain after attacking; arm the skill for the NEXT attack when full.
            if (Data.MaxMana > 0)
            {
                Data.Mana += Data.ManaPerAttack;
                if (Data.Mana >= Data.MaxMana)
                {
                    Data.Mana = 0;
                    Data.SkillArmed = true;
                    Debug.Log($"[AutoBattle] {Data.DisplayName} mana full — {Data.SkillName} armed for next attack");
                }
            }

            // Subtract one full cycle; overflow carries into the next cycle naturally (Combat.md Rule 7).
            Data.AttackCooldown -= 1f;

            return new AttackResult(target.Id, damage, wasKill);
        }

        // ── Move (Combat.md Core Rule 4 phase 3) ────────────────────────────────────────────
        // Returns null if the unit has a target in range (stands and fights, per Combat.md Rule 5)
        // or no path exists. grid is passed in directly rather than via a back-reference.
        public MoveResult? TryMove(List<HeroDataRuntime> opponents, HexGrid grid)
        {
            if (FindInRange(Data, opponents) != null) return null;

            var oppPositions = opponents.ConvertAll(o => o.Position);
            var nearest = grid.FindNearest(Data.Position, oppPositions);
            if (nearest == null) return null;

            var next = grid.GetNextStep(Data.Position, nearest.Value, Data.Id);
            if (next == null) return null;

            grid.ClearOccupant(Data.Position);
            var from = Data.Position;
            Data.Position = next.Value;
            grid.SetOccupant(Data.Position, Data.Id);

            Debug.Log($"[AutoBattle] {Data.DisplayName} moves {from} → {Data.Position}");

            Data.MoveCooldown -= 1f;
            return new MoveResult(from, Data.Position);
        }

        // Stateless targeting helper, unchanged from before the split.
        private static HeroDataRuntime FindInRange(HeroDataRuntime actor, List<HeroDataRuntime> opponents)
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
    }

    // What TryAttack() did -- the manager fires OnCombatantActed (and OnCombatantDefeated, if
    // WasKill) from this, rather than HeroSimulation firing events itself.
    internal readonly struct AttackResult
    {
        public readonly string TargetId;
        public readonly int Damage;
        public readonly bool WasKill;

        public AttackResult(string targetId, int damage, bool wasKill)
        {
            TargetId = targetId;
            Damage = damage;
            WasKill = wasKill;
        }
    }

    // What TryMove() did -- the manager fires OnCombatantMoved from this.
    internal readonly struct MoveResult
    {
        public readonly HexCoord From;
        public readonly HexCoord To;

        public MoveResult(HexCoord from, HexCoord to)
        {
            From = from;
            To = to;
        }
    }
}
