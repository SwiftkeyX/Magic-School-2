using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MagicSchool.Battle
{
    [RequireComponent(typeof(HexGrid))]
    public partial class AutoChessManager : MonoBehaviour
    {
        // ── Events ──────────────────────────────────────────────────────────
        // Fires once combatants are seeded; subscribers call GetCombatantSnapshots() for data.
        public event Action OnCombatantsSet;

        // A unit attacked: (actorId, targetId, damage, tags).
        public event Action<string, string, int, List<string>> OnCombatantActed;
        // A unit moved one hex: (id, fromHex, toHex).
        public event Action<string, HexCoord, HexCoord> OnCombatantMoved;
        // A unit died: (id).
        public event Action<string> OnCombatantDefeated;
        // This battle ended: carries the result.
        public event Action<BattleResult> OnBattleComplete;
        // Static — fires for ANY battle instance, so listeners with no scene reference can subscribe.
        public static event Action<BattleResult> OnAnyBattleComplete;

        // ── Tuning ───────────────────────────────────────────────────────────
        // These were `const` before the editability pass — battle pace and length could not be
        // felt out without a recompile, which is the opposite of how you tune pace.
        [Header("Tuning")]
        [SerializeField, Range(0.02f, 0.5f), Tooltip("Seconds per simulation tick. 0.1 = 10 ticks/sec (TFT resolution).")]
        private float _tickDelay = 0.1f;

        [SerializeField, Range(100, 5000), Tooltip("Hard cap on battle length. At 0.1s/tick, 1200 ticks = 120 seconds.")]
        private int _maxBattleTicks = 1200;

        [SerializeField, Range(0.1f, 3f), Tooltip("Hexes per second. SHARED by every unit — movement is deliberately NOT attack speed.")]
        private float _moveSpeed = 0.65f;

        // Wall-clock playback speed. Set by BattleHUD while the SpeedUp input is held.
        // IMPORTANT: this scales only how fast you *watch* the battle — the simulation step
        // (the two cooldown clocks below) is unchanged, so the outcome is identical
        // at any speed. Speeding up must never alter who wins.
        public float GameSpeedMultiplier { get; set; } = 1f;

        // ── State ────────────────────────────────────────────────────────────
        // The world state (roster + board) lives in AutoChessData, shared with AutoChessHelper.
        // HeroSimulation performs its own writes once told it's that unit's turn (Combat.md
        // Core Rule 1); _playerPlacements/_enemyPlacements and _battleRunning stay here -- pre-
        // battle setup buffers and the manager's own lifecycle guard, none of it is "world state."
        private readonly AutoChessData _data = new AutoChessData();
        private readonly Dictionary<string, HexCoord> _playerPlacements = new Dictionary<string, HexCoord>();
        private readonly Dictionary<string, HexCoord> _enemyPlacements = new Dictionary<string, HexCoord>();
        private bool _battleRunning;

        // ── Lifecycle ────────────────────────────────────────────────────────
        // _data.Grid is cached here (not in BeginBattle) because GetEnemyPlacements() needs
        // the board dimensions and is called *before* the battle starts, by BattleBoardManager.
        private void Awake()
        {
            _data.Grid = GetComponent<HexGrid>();
        }

        // ── Battle ───────────────────────────────────────────────────────────
        public void BeginBattle()
        {
            if (_battleRunning) { Debug.LogWarning("[AutoChessManager] Battle already running."); return; }
            if (_data.Grid == null) { Debug.LogError("[AutoChessManager] HexGrid component required on the same GameObject.", this); return; }

            // Place player's unit on the grid — wherever it was dragged, else its default formation.
            PlaceUnitOnGrid(GetPlayerPlacements());

            // Place enemy's unit on the grid — the SAME source BattleBoardManager spawns enemy
            // GameObjects from, so sprites and sim can't desync.
            PlaceUnitOnGrid(GetEnemyPlacements());

            // Apply flat trait-synergy bonuses once, per team, before the loop starts.
            ApplyTraitBonuses();

            StartCoroutine(BattleLoop());
        }

        // Stamps each placed combatant's grid Position and marks the cell occupied.
        private void PlaceUnitOnGrid(Dictionary<string, HexCoord> placements)
        {
            foreach (var kv in placements)
            {
                var c = _data.Combatants.FirstOrDefault(x => x.Data.Id == kv.Key);
                if (c == null) continue;
                c.Data.Position = kv.Value;
                _data.Grid.SetOccupant(kv.Value, c.Data.Id);
            }
        }

        private IEnumerator BattleLoop()
        {
            _battleRunning = true;
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

                // Only the wall-clock wait is scaled by GameSpeedMultiplier — the sim step above is not.
                yield return new WaitForSeconds(_tickDelay / Mathf.Max(0.01f, GameSpeedMultiplier));
            }
        }

        // ── PHASE 1 — CHARGE both clocks ────────────────────────────────────────
        // Each HeroSimulation charges its own HeroDataRuntime; AttackSpeed is per-unit,
        // _moveSpeed is shared. That is the whole point.
        private void ChargePhase()
        {
            foreach (var c in _data.Combatants.Where(c => !c.Data.IsDead))
                c.ChargeClocks(_tickDelay, _moveSpeed);
        }

        // ── PHASE 2 — ATTACK (charged AND a target in range) ────────────────────
        // Returns true the instant either side is wiped, so BattleLoop() can end the battle
        // immediately instead of waiting for the tick to finish.
        private bool AttackPhase()
        {
            var readyToAttackCombatants = _data.Combatants
                .Where(c => !c.Data.IsDead && c.Data.AttackCooldown >= 1.0f)
                .OrderByDescending(c => c.Data.AttackSpeed)
                .ToList();

            foreach (var actor in readyToAttackCombatants)
            {
                if (actor.Data.IsDead) continue;

                var opponents = AutoChessHelper.GetOpponentsOf(_data, actor);
                if (opponents.Count == 0) break;

                // Nothing in range: the unit does NOT attack — and does NOT lose its charge.
                // It will move in Phase 3 instead. Moving no longer costs a unit its attack.
                var result = actor.TryAttack(opponents);
                if (result == null) continue;

                OnCombatantActed?.Invoke(actor.Data.Id, result.Value.TargetId, result.Value.Damage, new List<string>());
                AutoChessHelper.HandleKillIfNeeded(_data, result.Value);
                if (result.Value.WasKill) OnCombatantDefeated?.Invoke(result.Value.TargetId);

                if (AutoChessHelper.CheckWinCondition(_data)) return true;
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

                var opponents = AutoChessHelper.GetOpponentsOf(_data, actor);
                if (opponents.Count == 0) break;

                // A unit with a target in range stands and fights; TryMove re-checks this itself.
                var moveResult = actor.TryMove(opponents, _data.Grid);
                if (moveResult != null)
                    OnCombatantMoved?.Invoke(actor.Data.Id, moveResult.Value.From, moveResult.Value.To);
            }
        }

        // ── PHASE 4 — CLAMP ──────────────────────────────────────────────────────
        // DO NOT fold this into Phase 1. Clamping during the charge (Min(x + delta, 1f))
        // would pin a unit sitting at 1.02 down to 1.0; it attacks, and lands on 0.0
        // instead of 0.02 — losing a sliver EVERY cycle and re-quantising attack speed to
        // the tick rate, which is exactly what the overflow carry above exists to prevent.
        // Clamping HERE only bites units that could not act, which is what stops a unit
        // that walked 30 ticks from banking 1.8 attacks and bursting on contact. It
        // arrives with exactly ONE attack ready. See Combat.md, Core Rules 7-8.
        private void ClampPhase()
        {
            foreach (var c in _data.Combatants.Where(c => !c.Data.IsDead))
                c.CooldownCap();
        }

        // ── PHASE 5 — OVERTIME (tick cap) ────────────────────────────────────────
        // Hard length cap: at _maxBattleTicks (1200 ticks = 120s at 0.1s/tick), declare a
        // Timeout and end the battle early. The side with more survivors wins.
        // Returns true once the battle has ended (BattleLoop() checks this instead of a goto).
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
            OnBattleComplete?.Invoke(result);
            OnAnyBattleComplete?.Invoke(result);
            _battleRunning = false;
        }

        // Per-hero turn logic (targeting, attack, movement) lives in HeroSimulation.cs; the
        // shared per-tick queries (opponent lists, the win-check, kill cleanup) live in
        // AutoChessHelper.cs. This class only sequences the tick and fires events.
    }
}
