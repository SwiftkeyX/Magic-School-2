using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MagicSchool.Battle
{
    [RequireComponent(typeof(HexGrid))]
    public partial class AutoBattleResolver : MonoBehaviour
    {
        // ── Events ──────────────────────────────────────────────────────────
        // Setup event — fires at the end of SetCombatants(); subscribers call
        // GetCombatantSnapshots() themselves to get data (no payload per GDD).
        public event Action OnCombatantsSet;

        public event Action<string, string, int, List<string>> OnCombatantActed;
        public event Action<string, HexCoord, HexCoord> OnCombatantMoved;
        public event Action<string> OnCombatantDefeated;
        public event Action<BattleResult> OnBattleComplete;
        // removed: OnSkillCast, OnManaChanged, OnCastStateChanged — skill system, rebuilding fresh

        // Static forwarding event — AudioSystem subscribes here so it does not need
        // FindObjectOfType to reach a non-singleton AutoBattleResolver instance.
        public static event Action<BattleResult> OnAnyBattleComplete;

        // ── Tuning ───────────────────────────────────────────────────────────
        // These were `const` before the editability pass — battle pace and length could not be
        // felt out without a recompile, which is the opposite of how you tune pace.
        [Header("Tuning")]
        [SerializeField, Range(0.02f, 0.5f), Tooltip("Seconds per simulation tick. 0.1 = 10 ticks/sec (TFT resolution).")]
        private float _tickDelay = 0.1f;

        [SerializeField, Range(100, 5000), Tooltip("Hard cap on battle length. At 0.1s/tick, 1200 ticks = 120 seconds.")]
        private int _maxBattleTicks = 1200;

        // Movement is deliberately NOT attack speed. Before this existed, a unit spent its whole
        // attack cycle to take one hex step, so a hero that swung faster also WALKED faster —
        // an artifact of reusing one timer for two jobs, not a design. Every unit now shares this
        // one pace. See Combat.md.
        [SerializeField, Range(0.1f, 3f), Tooltip("Hexes per second. SHARED by every unit — movement is deliberately NOT attack speed.")]
        private float _moveSpeed = 0.65f;

        // Wall-clock playback speed. Set by BattleHUD while the SpeedUp input is held.
        // IMPORTANT: this scales only how fast you *watch* the battle — the simulation step
        // (the two cooldown clocks below) is unchanged, so the outcome is identical
        // at any speed. Speeding up must never alter who wins.
        public float SpeedMultiplier { get; set; } = 1f;

        // ── State ────────────────────────────────────────────────────────────
        private readonly List<Combatant> _combatants = new List<Combatant>();
        private readonly Dictionary<string, HexCoord> _playerPlacements = new Dictionary<string, HexCoord>();
        private HexGrid _grid;
        private bool _battleRunning;

        // Combatant itself lives in its own file (Combatant.cs), top-level in this namespace.

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
            if (_battleRunning) { Debug.LogWarning("[AutoBattleResolver] Battle already running."); return; }
            if (_grid == null) { Debug.LogError("[AutoBattleResolver] HexGrid component required on the same GameObject.", this); return; }

            // _combatants holds BOTH teams — SetCombatants() takes every unit at once and stamps each
            // with a Team. The two sides only differ in where their positions come from, hence the two
            // loops below. Player units go wherever the player dragged them...
            foreach (var kv in _playerPlacements)
            {
                var c = _combatants.FirstOrDefault(x => x.Id == kv.Key);
                if (c == null) continue;
                c.Position = kv.Value;
                _grid.SetOccupant(kv.Value, c.Id);
            }

            // ...while enemies have no author, so their layout is GENERATED — from the SAME source
            // the view spawns them from. This loop used to be re-implemented inline here, in parallel
            // with GetAutoEnemyPlacements() — BattleBoardManager spawns enemy GameObjects from that
            // method, while the simulation placed them from this one. Two copies of the same
            // rule meant a change to either silently desynced the sprites from the sim.
            foreach (var kv in GetAutoEnemyPlacements())
            {
                var c = _combatants.FirstOrDefault(x => x.Id == kv.Key);
                if (c == null) continue;
                c.Position = kv.Value;
                _grid.SetOccupant(kv.Value, c.Id);
            }

            // Apply flat trait-synergy bonuses once, per team, before the loop starts.
            ApplyTraitBonuses();

            StartCoroutine(BattleLoop());
        }

        // TODO(deferred): two open architecture questions, parked — see the CodeTour
        // "Deferred design questions".
        //   1. This class is long, spread across 6 partial files. Divide it by responsibility?
        //   2. BattleLoop() charges the tick for every Combatant. Should each Combatant instead
        //      update its own clocks by subscribing to an event fired by BattleLoop()? That would
        //      invert state ownership — Combat.md Core Rule 1 currently makes the resolver the
        //      SOLE writer of Combatant state. Decide the rule before moving the code.
        private IEnumerator BattleLoop()
        {
            _battleRunning = true;
            Debug.Log("[AutoBattle] START");
            int ticks = 0;

            while (true)
            {
                // ── PHASE 1 — CHARGE both clocks ────────────────────────────────
                // AttackSpeed is per-unit; _moveSpeed is shared. That is the whole point.
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

                // Only the wall-clock wait is scaled by SpeedMultiplier — the sim step above is not.
                yield return new WaitForSeconds(_tickDelay / Mathf.Max(0.01f, SpeedMultiplier));
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

        // Combat helpers (targeting, damage) live in AutoBattleResolver.CombatHelpers.cs.
        // Attack lifecycle (Attack, HandleKill, MoveTowardNearest) lives in AutoBattleResolver.Attack.cs.
    }
}
