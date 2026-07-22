using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Owns the tick loop: BeginBattle's grid placement + trait-bonus application, then the
    // five-phase BattleLoop (Combat.md Core Rule 4). Takes AutoChessData as a parameter and
    // reports back through callbacks instead of holding a reference to the facade -- same
    // decoupled pattern as HeroSimulation/AutoChessHelper (Combat.md Interactions table).
    internal class ACSimulator
    {
        private readonly ACData _data;
        private readonly float _tickDelay;
        private readonly int _maxBattleTicks;
        private readonly float _moveSpeed;
        private readonly Func<float> _getGameSpeedMultiplier;

        // ================================ Action ================================
        private readonly Action<bool> _setBattleRunning;
        private readonly Action<string, string, int, List<string>> _onActed;
        private readonly Action<string, HexCoord, HexCoord> _onMoved;
        private readonly Action<string> _onDefeated;
        private readonly Action<BattleResult> _onComplete;
        private readonly Action<BattleResult> _onAnyComplete;

        public ACSimulator(
            ACData data,
            float tickDelay,
            int maxBattleTicks,
            float moveSpeed,
            Func<float> getGameSpeedMultiplier,
            Action<bool> setBattleRunning,
            Action<string, string, int, List<string>> onActed,
            Action<string, HexCoord, HexCoord> onMoved,
            Action<string> onDefeated,
            Action<BattleResult> onComplete,
            Action<BattleResult> onAnyComplete)
        {
            _data = data;
            _tickDelay = tickDelay;
            _maxBattleTicks = maxBattleTicks;
            _moveSpeed = moveSpeed;
            _getGameSpeedMultiplier = getGameSpeedMultiplier;
            _setBattleRunning = setBattleRunning;
            _onActed = onActed;
            _onMoved = onMoved;
            _onDefeated = onDefeated;
            _onComplete = onComplete;
            _onAnyComplete = onAnyComplete;
        }

        // ============================= Main function ================================
        public IEnumerator RunBattle(Dictionary<string, HexCoord> playerPlacements, Dictionary<string, HexCoord> enemyPlacements)
        {
            // At start of the combat, place player and enemy unit on the grid
            ACHelper.PlaceUnitOnGrid(_data, playerPlacements);
            ACHelper.PlaceUnitOnGrid(_data, enemyPlacements);

            // Apply flat trait-synergy bonuses once, per team, before the loop starts.
            Trait.ApplyTraitBonuses(_data);

            _setBattleRunning(true);
            Debug.Log("[AutoBattle] START");
            int ticks = 0;

            while (true)
            {
                // charge attack and move cooldown
                ChargePhase();

                // attack if the attack coolodwn is finished
                if (AttackPhase())
                {
                    bool won = _data.Combatants.Any(c => c.Data.IsPlayer && !c.Data.IsDead);
                    CompleteBattle(new BattleResult { Won = won, TicksElapsed = ticks, TimedOut = false }, endedEarly: true);
                    yield break;
                }

                // move if the move cooldown is finished
                MovePhase();

                // clamp the attack and move cooldown to not make it go above 1
                ClampPhase();

                ticks++;

                // end the battle early if the time exceed capacity
                if (OverTimePhase(ticks)) yield break;

                // tick cooldown before starting next battle loop
                yield return new WaitForSeconds(_tickDelay / Mathf.Max(0.01f, _getGameSpeedMultiplier()));
            }
        }

        #region Phase Function
        // ── PHASE 1 — CHARGE both clocks ────────────────────────────────────────
        // Each HeroSimulation count cooldown for AttackSpeed and MoveSpeed
        private void ChargePhase()
        {
            foreach (var c in _data.Combatants.Where(c => !c.Data.IsDead))
                c.ChargeClocks(_tickDelay, _moveSpeed);
        }

        // ── PHASE 2 — ATTACK  ────────────────────
        // Hero that ready to attack, attack enemy
        private bool AttackPhase()
        {
            var readyToAttackCombatants = _data.Combatants
                .Where(c => !c.Data.IsDead && c.Data.AttackCooldown >= 1.0f)
                .OrderByDescending(c => c.Data.AttackSpeed)
                .ToList();

            foreach (var actor in readyToAttackCombatants)
            {
                if (actor.Data.IsDead) continue;

                var opponents = ACHelper.GetOpponentsOf(_data, actor);
                if (opponents.Count == 0) break;

                // Nothing in range: the unit does NOT attack — and does NOT lose its charge.
                // It will move in Phase 3 instead. Moving no longer costs a unit its attack.
                var result = actor.TryAttack(opponents);
                if (result == null) continue;

                _onActed?.Invoke(actor.Data.Id, result.Value.TargetId, result.Value.Damage, new List<string>());
                ACHelper.HandleKillIfNeeded(_data, result.Value);
                if (result.Value.WasKill) _onDefeated?.Invoke(result.Value.TargetId);

                if (ACHelper.CheckWinCondition(_data)) return true;
            }
            return false;
        }

        // ── PHASE 3 — MOVE (charged AND nothing in range) ───────────────────────
        private void MovePhase()
        {
            var readyToMoveCombatants = _data.Combatants
                .Where(c => !c.Data.IsDead && c.Data.MoveCooldown >= 1.0f)
                .ToList();

            foreach (var actor in readyToMoveCombatants)
            {
                if (actor.Data.IsDead) continue;

                var opponents = ACHelper.GetOpponentsOf(_data, actor);
                if (opponents.Count == 0) break;

                // A unit with a target in range stands and fights; TryMove re-checks this itself.
                var moveResult = actor.TryMove(opponents, _data.Grid);
                if (moveResult != null)
                    _onMoved?.Invoke(actor.Data.Id, moveResult.Value.From, moveResult.Value.To);
            }
        }

        // ── PHASE 4 — CLAMP ──────────────────────────────────────────────────────
        private void ClampPhase()
        {
            foreach (var c in _data.Combatants.Where(c => !c.Data.IsDead))
                c.CooldownCap();
        }

        // ── PHASE 5 — OVERTIME (tick cap) ────────────────────────────────────────
        // Hard length cap: at _maxBattleTicks (1200 ticks = 120s at 0.1s/tick), declare a
        // Timeout and end the battle early. The side with more survivors wins.
        // Returns true once the battle has ended (RunBattle() checks this instead of a goto).
        private bool OverTimePhase(int ticks)
        {
            if (ticks < _maxBattleTicks) return false;

            int pCount = _data.Combatants.Count(c => c.Data.IsPlayer && !c.Data.IsDead);
            int eCount = _data.Combatants.Count(c => !c.Data.IsPlayer && !c.Data.IsDead);
            CompleteBattle(new BattleResult { Won = pCount > eCount, TicksElapsed = ticks, TimedOut = true }, endedEarly: false);
            return true;
        }

        // Fires the battle-end events and resets the running flag. endedEarly distinguishes the
        // log line only (an early wipe vs. hitting the tick cap) -- both paths are otherwise identical.
        private void CompleteBattle(BattleResult result, bool endedEarly)
        {
            string outcome = result.Won ? "PLAYERS WIN" : "PLAYERS LOSE";
            Debug.Log(endedEarly
                ? $"[AutoBattle] END — {outcome} in {result.TicksElapsed} ticks"
                : $"[AutoBattle] TIMEOUT — {outcome}");
            _onComplete?.Invoke(result);
            _onAnyComplete?.Invoke(result);
            _setBattleRunning(false);
        }
        #endregion
    }
}
