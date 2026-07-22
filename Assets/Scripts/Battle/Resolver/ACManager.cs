using System;
using System.Collections.Generic;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Public facade for the Combat system (Combat.md). Holds every event and public method
    // external callers (BattleBoardManager, BattleHUD, tests) already use; internally delegates
    // to ACSimulator (tick loop + traits) and ACSetup (seeding/placement + debug hooks). Neither
    // internal class holds a reference back to this class or to each other -- same decoupled
    // pattern as HeroSimulation/AutoChessHelper (Combat.md Interactions table).
    [RequireComponent(typeof(HexGrid))]
    public class ACManager : MonoBehaviour
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
        private readonly ACData _data = new ACData();
        private readonly Dictionary<string, HexCoord> _playerPlacements = new Dictionary<string, HexCoord>();
        private readonly Dictionary<string, HexCoord> _enemyPlacements = new Dictionary<string, HexCoord>();
        private bool _battleRunning;

        private ACSimulator _simulator;
        private ACSetup _setup;



        // ── Lifecycle ────────────────────────────────────────────────────────
        private void Awake()
        {
            _data.Grid = GetComponent<HexGrid>();

            _simulator = new ACSimulator(
                _data, _tickDelay, _maxBattleTicks, _moveSpeed,
                getGameSpeedMultiplier: () => GameSpeedMultiplier,
                setBattleRunning: running => _battleRunning = running,
                onActed: (id, targetId, damage, tags) => OnCombatantActed?.Invoke(id, targetId, damage, tags),
                onMoved: (id, from, to) => OnCombatantMoved?.Invoke(id, from, to),
                onDefeated: id => OnCombatantDefeated?.Invoke(id),
                onComplete: result => OnBattleComplete?.Invoke(result),
                onAnyComplete: result => OnAnyBattleComplete?.Invoke(result));

            _setup = new ACSetup(
                _data, gameObject, _playerPlacements, _enemyPlacements,
                isBattleRunning: () => _battleRunning,
                onCombatantsSet: () => OnCombatantsSet?.Invoke());
        }

        // ── Battle ───────────────────────────────────────────────────────────
        public void BeginBattle()
        {
            if (_battleRunning) { Debug.LogWarning("[AutoChessManager] Battle already running."); return; }
            if (_data.Grid == null) { Debug.LogError("[AutoChessManager] HexGrid component required on the same GameObject.", this); return; }

            StartCoroutine(_simulator.RunBattle(GetPlayerPlacements(), GetEnemyPlacements()));
        }

        // ================================ Setter & Getter =====================================
        public void SetInitialCombatantsRuntimeData(List<HeroDataSeed> units) => _setup.SetInitialCombatantsRuntimeData(units);
        public void EnsureCombatantsInitialized() => _setup.EnsureCombatantsInitialized();

        public List<CombatantSnapshot> GetCombatantSnapshots() => _data.GetCombatantSnapshots();
        public int GetCurrentHP(string id) => _data.GetCurrentHP(id);
        public int GetMaxHP(string id) => _data.GetMaxHP(id);

        public void SetPlayerPlacements(Dictionary<string, HexCoord> placements) => _setup.SetPlayerPlacements(placements);
        public void SetEnemyPlacements(Dictionary<string, HexCoord> placements) => _setup.SetEnemyPlacements(placements);
        public Dictionary<string, HexCoord> GetPlayerPlacements() => _setup.GetPlayerPlacements();
        public Dictionary<string, HexCoord> GetEnemyPlacements() => _setup.GetEnemyPlacements();

        // ================================ Traits ================================
        public List<(TraitDataSO trait, int count, TraitBreakpoint active)> GetActiveTraits(Team team) => Trait.GetActiveTraits(_data, team);

#if UNITY_EDITOR
        // ================================ Debug (delegates to ACSetup) ================================
        public void DebugSetAllPlayerHp(float pct) => _setup.DebugSetAllPlayerHp(pct);
#endif
    }
}
