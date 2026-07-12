using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MagicSchool.Battle
{
    public partial class AutoBattleResolver : MonoBehaviour
    {
        // ── Events ──────────────────────────────────────────────────────────
        // Setup event — fires at the end of SetCombatants(); subscribers call
        // GetCombatantSnapshots() themselves to get data (no payload per GDD).
        // May fire more than once before BeginBattle() if RunManager narrows the
        // roster (full roster first, then fielded squad after ConfirmSquadPlacement).
        public event Action                                     OnCombatantsSet;

        public event Action<string, string, int, List<string>> OnCombatantActed;
        public event Action<string, HexCoord, HexCoord>        OnCombatantMoved;
        public event Action<string>                             OnCombatantDefeated;
        public event Action<BattleResult>                       OnBattleComplete;
        // removed: OnSkillCast, OnManaChanged, OnCastStateChanged — skill system, rebuilding fresh

        // Static forwarding event — AudioSystem subscribes here so it does not need
        // FindObjectOfType to reach a non-singleton AutoBattleResolver instance.
        public static event Action<BattleResult>                OnAnyBattleComplete;

        // ── Constants ────────────────────────────────────────────────────────
        private const float TickDelay      = 0.1f;   // 10 ticks/second — matches TFT resolution
        private const int   MaxBattleTicks = 1200;   // 120s max (was 200 × 0.6s)

        // removed: DreadknightShieldHpThresholdPct, TricksterDashHpThresholdPct — trait system, rebuilding fresh

        // ── State ────────────────────────────────────────────────────────────
        private readonly List<Combatant>              _combatants       = new List<Combatant>();
        private readonly Dictionary<string, HexCoord> _playerPlacements = new Dictionary<string, HexCoord>();
        private          HexGrid                      _grid;
        private          bool                         _battleRunning;

        // removed: [SerializeField] ChampionRoster _championRoster — champion system, rebuilding fresh
        // removed: Kinetic trait state block + internal accessors — trait system, rebuilding fresh
        // removed: ActiveZoneEffect/_activeZones (Dread Overlord zone skill) — skill system, rebuilding fresh

        // Combatant itself lives in its own file (Combatant.cs), top-level in this namespace.

        // ── Lifecycle ────────────────────────────────────────────────────────
        // removed: Awake() RunManager.Instance?.RegisterAutoBattleResolver(this) — meta-progression
        // system, rebuilding fresh. No RunManager to register with in the standalone engine.

        // Pre-battle setup API (SetCombatants, SetUnitPositions, GetAutoEnemyPlacements,
        // EnsureCombatantsInitialized, GetCombatantSnapshots) now lives in
        // AutoBattleResolver.Setup.cs.

        // ── Battle ───────────────────────────────────────────────────────────
        public void BeginBattle()
        {
            if (_battleRunning) { Debug.LogWarning("[AutoBattleResolver] Battle already running."); return; }

            // removed: RunManager phase-guard (RunManager.Instance != null && CurrentPhase != Battle)
            // — meta-progression system, rebuilding fresh.

            _grid = GetComponent<HexGrid>();
            if (_grid == null) { Debug.LogError("[AutoBattleResolver] HexGrid component required on same GameObject."); return; }

            // Apply player placements
            foreach (var kv in _playerPlacements)
            {
                var c = _combatants.FirstOrDefault(x => x.Id == kv.Key);
                if (c == null) continue;
                c.Position = kv.Value;
                _grid.SetOccupant(kv.Value, c.Id);
            }

            // Auto-place enemies
            int col = 0, row = HexGrid.PlayerRowCount;
            foreach (var c in _combatants.Where(c => !c.IsPlayer))
            {
                if (col >= HexGrid.Cols) { col = 0; row++; }
                c.Position = new HexCoord(col++, row);
                _grid.SetOccupant(c.Position, c.Id);
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
                // removed: TickStatusCounters/TickDreadZones/ApplyBleedTicks/TickDreadknightShield/
                // TickTricksterDashTrigger/TickTricksterUntargetable/TickKineticMana/
                // ResolveKineticBonusActions/TickCastChannels — trait + skill-cast systems,
                // rebuilding fresh. No per-tick status effects until then.

                // Accumulate action progress (replaces integer timer decrement).
                foreach (var c in _combatants.Where(c => !c.IsDefeated))
                {
                    c.ActionProgress += c.AttackSpeed * TickDelay;
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
                if (ticks >= MaxBattleTicks)
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

                yield return new WaitForSeconds(TickDelay);
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

        // AutoBattleResolver.Phases.cs is now empty (removed per-tick trait/skill phases).
        // Combat helpers (targeting, damage mutation) live in AutoBattleResolver.CombatHelpers.cs.
        // Attack lifecycle (Attack, HandleKill, MoveTowardNearest) lives in AutoBattleResolver.Attack.cs.
    }
}
