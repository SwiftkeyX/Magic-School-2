using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MagicSchool.Battle
{
    [RequireComponent(typeof(HexGrid))]
    public partial class AutoBattleSimulator : MonoBehaviour
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
        private readonly List<HeroDataRuntime> _combatants = new List<HeroDataRuntime>();
        private readonly Dictionary<string, HexCoord> _playerPlacements = new Dictionary<string, HexCoord>();
        private HexGrid _grid;
        private bool _battleRunning;

        // HeroDataRuntime itself lives in its own file (HeroDataRuntime.cs), top-level in this namespace.

        // ── Lifecycle ────────────────────────────────────────────────────────
        // _grid is cached here (not in BeginBattle) because GetAutoEnemyPlacements() needs the
        // board dimensions and is called *before* the battle starts, by BattleBoardManager.
        private void Awake()
        {
            _grid = GetComponent<HexGrid>();
        }

        // ── Battle ───────────────────────────────────────────────────────────
        public void BeginBattle()
        {
            if (_battleRunning) { Debug.LogWarning("[AutoBattleSimulator] Battle already running."); return; }
            if (_grid == null) { Debug.LogError("[AutoBattleSimulator] HexGrid component required on the same GameObject.", this); return; }

            // Place player's unit on the grid — wherever the player dragged it.
            PlaceUnitOnGrid(_playerPlacements);

            // Place enemy's unit on the grid — auto-generated from the SAME source
            // BattleBoardManager spawns enemy GameObjects from, so sprites and sim can't desync.
            PlaceUnitOnGrid(GetAutoEnemyPlacements());

            // Apply flat trait-synergy bonuses once, per team, before the loop starts.
            ApplyTraitBonuses();

            StartCoroutine(BattleLoop());
        }

        // Stamps each placed combatant's grid Position and marks the cell occupied.
        private void PlaceUnitOnGrid(Dictionary<string, HexCoord> placements)
        {
            foreach (var kv in placements)
            {
                var c = _combatants.FirstOrDefault(x => x.Id == kv.Key);
                if (c == null) continue;
                c.Position = kv.Value;
                _grid.SetOccupant(kv.Value, c.Id);
            }
        }

        // TODO(deferred): two open architecture questions, parked — see the CodeTour
        // "Deferred design questions".
        //   1. This class is long, spread across 6 partial files. Divide it by responsibility?
        //   2. BattleLoop() charges the tick for every HeroDataRuntime. Should each HeroDataRuntime
        //      instead update its own clocks by subscribing to an event fired by BattleLoop()? That
        //      would invert state ownership — Combat.md Core Rule 1 currently makes the resolver the
        //      SOLE writer of HeroDataRuntime state. Decide the rule before moving the code.
        private IEnumerator BattleLoop()
        {
            _battleRunning = true;
            Debug.Log("[AutoBattle] START");
            int ticks = 0;

            while (true)
            {
                // ── PHASE 1 — CHARGE both clocks ────────────────────────────────
                foreach (var c in _combatants.Where(c => !c.IsDefeated))
                {
                    c.AttackCooldown += c.AttackSpeed * _tickDelay;
                    c.MoveCooldown += _moveSpeed * _tickDelay;
                }

                // ── PHASE 2 — ATTACK (charged AND a target in range) ────────────
                var readyToAttackCombatants = _combatants
                    .Where(c => !c.IsDefeated && c.AttackCooldown >= 1.0f)
                    .OrderByDescending(c => c.AttackSpeed)
                    .ToList();

                foreach (var actor in readyToAttackCombatants)
                {
                    if (actor.IsDefeated) continue;

                    var opponents = _combatants.Where(c => !c.IsDefeated && c.IsPlayer != actor.IsPlayer).ToList();
                    if (opponents.Count == 0) break;

                    var inRange = FindInRange(actor, opponents);

                    // Nothing in range: the unit does NOT attack — and does NOT lose its charge.
                    // It will move in Phase 3 instead. Moving no longer costs a unit its attack.
                    if (inRange == null) continue;

                    Attack(actor, inRange);

                    // Subtract one full cycle; overflow carries into the next cycle naturally
                    actor.AttackCooldown -= 1.0f;

                    // Win check
                    bool playersAlive = _combatants.Any(c => c.IsPlayer && !c.IsDefeated);
                    bool enemiesAlive = _combatants.Any(c => !c.IsPlayer && !c.IsDefeated);
                    if (!enemiesAlive || !playersAlive) goto BattleEnd;
                }

                // ── PHASE 3 — MOVE (charged AND nothing in range) ───────────────
                var readyToMoveCombatants = _combatants
                    .Where(c => !c.IsDefeated && c.MoveCooldown >= 1.0f)
                    .ToList();

                foreach (var actor in readyToMoveCombatants)
                {
                    if (actor.IsDefeated) continue;

                    var opponents = _combatants.Where(c => !c.IsDefeated && c.IsPlayer != actor.IsPlayer).ToList();
                    if (opponents.Count == 0) break;

                    // A unit with a target in range stands and fights; it does not reposition.
                    if (FindInRange(actor, opponents) != null) continue;

                    MoveTowardNearest(actor, opponents);
                    actor.MoveCooldown -= 1.0f;
                }

                // ── PHASE 4 — CLAMP ─────────────────────────────────────────────
                // DO NOT fold this into Phase 1. Clamping during the charge (Min(x + delta, 1f))
                // would pin a unit sitting at 1.02 down to 1.0; it attacks, and lands on 0.0
                // instead of 0.02 — losing a sliver EVERY cycle and re-quantising attack speed to
                // the tick rate, which is exactly what the overflow carry above exists to prevent.
                // Clamping HERE only bites units that could not act, which is what stops a unit
                // that walked 30 ticks from banking 1.8 attacks and bursting on contact. It
                // arrives with exactly ONE attack ready. See Combat.md, Core Rules 7-8.
                foreach (var c in _combatants.Where(c => !c.IsDefeated))
                {
                    c.AttackCooldown = Mathf.Min(c.AttackCooldown, 1f);
                    c.MoveCooldown = Mathf.Min(c.MoveCooldown, 1f);
                }

                // Hard length cap: at _maxBattleTicks (1200 ticks = 120s at 0.1s/tick), declare a
                // Timeout and end the battle early. The side with more survivors wins.
                ticks++;
                if (ticks >= _maxBattleTicks)
                {
                    int pCount = _combatants.Count(c => c.IsPlayer && !c.IsDefeated);
                    int eCount = _combatants.Count(c => !c.IsPlayer && !c.IsDefeated);
                    var result = new BattleResult { Won = pCount > eCount, TicksElapsed = ticks, TimedOut = true };
                    Debug.Log($"[AutoBattle] TIMEOUT — {(result.Won ? "PLAYERS WIN" : "PLAYERS LOSE")}");
                    OnBattleComplete?.Invoke(result);
                    OnAnyBattleComplete?.Invoke(result);
                    _battleRunning = false;
                    yield break;
                }

                // Only the wall-clock wait is scaled by GameSpeedMultiplier — the sim step above is not.
                yield return new WaitForSeconds(_tickDelay / Mathf.Max(0.01f, GameSpeedMultiplier));
            }
            
            // A label — the jump target of `goto BattleEnd` in the attack phase. It exists to escape
            // the foreach AND the enclosing while(true) in one jump: a plain `break` would only leave
            // the inner foreach, and the battle would keep ticking with a dead team. This is the one
            // case where C# `goto` is the honest tool.
        BattleEnd:
            {
                bool won = _combatants.Any(c => c.IsPlayer && !c.IsDefeated);
                int finalTicks = ticks;
                var res = new BattleResult { Won = won, TicksElapsed = finalTicks, TimedOut = false };
                Debug.Log($"[AutoBattle] END — {(won ? "PLAYERS WIN" : "PLAYERS LOSE")} in {finalTicks} ticks");
                OnBattleComplete?.Invoke(res);
                OnAnyBattleComplete?.Invoke(res);
                _battleRunning = false;
            }
        }

        // Combat helpers (targeting, damage) live in AutoBattleSimulator.CombatHelpers.cs.
        // Attack lifecycle (Attack, HandleKill, MoveTowardNearest) lives in AutoBattleSimulator.Attack.cs.
    }
}
