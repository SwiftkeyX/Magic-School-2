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
        public event Action                                     OnCombatantsSet;

        public event Action<string, string, int, List<string>> OnCombatantActed;
        public event Action<string, HexCoord, HexCoord>        OnCombatantMoved;
        public event Action<string>                             OnCombatantDefeated;
        public event Action<BattleResult>                       OnBattleComplete;
        // removed: OnSkillCast, OnManaChanged, OnCastStateChanged — skill system, rebuilding fresh

        // Static forwarding event — AudioSystem subscribes here so it does not need
        // FindObjectOfType to reach a non-singleton AutoBattleResolver instance.
        public static event Action<BattleResult>                OnAnyBattleComplete;

        // ── Tuning ───────────────────────────────────────────────────────────
        // These were `const` before the editability pass — battle pace and length could not be
        // felt out without a recompile, which is the opposite of how you tune pace.
        [Header("Tuning")]
        [SerializeField, Range(0.02f, 0.5f), Tooltip("Seconds per simulation tick. 0.1 = 10 ticks/sec (TFT resolution).")]
        private float _tickDelay = 0.1f;

        [SerializeField, Range(100, 5000), Tooltip("Hard cap on battle length. At 0.1s/tick, 1200 ticks = 120 seconds.")]
        private int _maxBattleTicks = 1200;

        // Wall-clock playback speed. Set by BattleHUD while the SpeedUp input is held.
        // IMPORTANT: this scales only how fast you *watch* the battle — the simulation step
        // (ActionProgress += AttackSpeed * _tickDelay) is unchanged, so the outcome is identical
        // at any speed. Speeding up must never alter who wins.
        public float SpeedMultiplier { get; set; } = 1f;

        // ── State ────────────────────────────────────────────────────────────
        private readonly List<Combatant>              _combatants       = new List<Combatant>();
        private readonly Dictionary<string, HexCoord> _playerPlacements = new Dictionary<string, HexCoord>();
        private          HexGrid                      _grid;
        private          bool                         _battleRunning;

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
            if (_grid == null)  { Debug.LogError("[AutoBattleResolver] HexGrid component required on the same GameObject.", this); return; }

            // Apply player placements
            foreach (var kv in _playerPlacements)
            {
                var c = _combatants.FirstOrDefault(x => x.Id == kv.Key);
                if (c == null) continue;
                c.Position = kv.Value;
                _grid.SetOccupant(kv.Value, c.Id);
            }

            // Auto-place enemies from the SAME source the view spawns them from.
            // This loop used to be re-implemented inline here, in parallel with
            // GetAutoEnemyPlacements() — BattleBoardManager spawns enemy GameObjects from that
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

        private IEnumerator BattleLoop()
        {
            _battleRunning = true;
            Debug.Log("[AutoBattle] START");
            int ticks = 0;

            while (true)
            {
                // Accumulate action progress (replaces integer timer decrement).
                foreach (var c in _combatants.Where(c => !c.IsDefeated))
                {
                    c.ActionProgress += c.AttackSpeed * _tickDelay;
                }

                // Collect ready actors (progress ≥ 1.0 = one full attack cycle complete)
                var ready = _combatants
                    .Where(c => !c.IsDefeated && c.ActionProgress >= 1.0f)
                    .OrderByDescending(c => c.AttackSpeed)
                    .ToList();

                foreach (var actor in ready)
                {
                    if (actor.IsDefeated) continue;

                    var opponents = _combatants.Where(c => !c.IsDefeated && c.IsPlayer != actor.IsPlayer).ToList();
                    if (opponents.Count == 0) break;

                    var inRange = FindInRange(actor, opponents);
                    if (inRange != null)
                        Attack(actor, inRange);
                    else
                        MoveTowardNearest(actor, opponents);

                    // Subtract one full cycle; overflow carries into the next cycle naturally
                    actor.ActionProgress -= 1.0f;

                    // Win check
                    bool playersAlive = _combatants.Any(c =>  c.IsPlayer && !c.IsDefeated);
                    bool enemiesAlive = _combatants.Any(c => !c.IsPlayer && !c.IsDefeated);
                    if (!enemiesAlive || !playersAlive) goto BattleEnd;
                }

                ticks++;
                if (ticks >= _maxBattleTicks)
                {
                    int pCount = _combatants.Count(c =>  c.IsPlayer && !c.IsDefeated);
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

            BattleEnd:
            {
                bool won       = _combatants.Any(c => c.IsPlayer && !c.IsDefeated);
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
