using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.UIElements;

namespace MagicSchool.Battle
{
    [RequireComponent(typeof(HexGrid))]
    public class BattleBoardManager : MonoBehaviour
    {
        // ── Inspector ────────────────────────────────────────────────────────
        [SerializeField] private ACManager _resolver;
        [SerializeField] private GameObject _hexTilePrefab;
        [SerializeField] private GameObject _battleUnitPrefab;
        [SerializeField] private UIDocument _uiDocument;

        [Header("Placement")]
        [SerializeField, Range(1, 12), Tooltip("How many heroes the player may field. Was int.MaxValue, which rendered as \"0/2147483647 heroes placed\".")]
        private int _maxSquadSize = 8;

        [Header("Board Layout")]
        [SerializeField, Range(0.5f, 3f), Tooltip("Centre-to-centre horizontal distance between hex columns.")]
        private float _hexWidth = 1.1f;

        [SerializeField, Range(0.4f, 3f), Tooltip("Centre-to-centre vertical distance between hex rows.")]
        private float _hexHeight = 0.95f;

        [SerializeField, Range(0f, 1.5f), Tooltip("Horizontal shift applied to odd rows (half a hex).")]
        private float _hexOffset = 0.55f;

        private VisualElement _root;
        private Button _startBattleButton;
        private Label _placementCountText;
        private ScrollView _benchScrollView;
        private VisualElement _benchContainer;
        private VisualElement _traitList;
        private readonly Dictionary<string, VisualElement> _benchCardsById = new();

        // ── State ────────────────────────────────────────────────────────────
        private readonly Dictionary<HexCoord, HexTileView> _tiles = new();
        private readonly Dictionary<string, BattleUnit> _units = new();
        private readonly Dictionary<string, HexCoord> _pendingPlacements = new();
        private readonly Dictionary<string, CombatantSnapshot> _studentSnapshots = new();

        private HexGrid _grid;
        private bool _battleStarted;

        // ── Placement controller (owns drag state and pointer input) ──────────
        private BattlePlacementController _placementCtrl;

        // ── Subsystem helpers ─────────────────────────────────────────────────
        private BattleBoardBuilder _builder;
        private BattleUnitController _unitController;
        private BattleTraitPanel _traitPanel;

        // ── Internal accessors (read by BattlePlacementController) ────────────
        internal bool IsBattleStarted => _battleStarted;
        internal int MaxSquadSize => _maxSquadSize;
        internal float HexWidth => _hexWidth;

        // The drag ghost needs the hero's authored tint. It used to call a static
        // BattleBoardManager.StudentColor(id) that switch'd on the literal "knight"/"archer".
        // It now reads the same snapshot the board renders from — one source, authored on the asset.
        internal Color GetStudentTint(string studentId) =>
            _studentSnapshots.TryGetValue(studentId, out var snap) ? snap.Tint : Color.white;

        // Instance geometry, so the board can be re-laid-out from the Inspector.
        internal Vector3 CoordToWorld(HexCoord c) =>
            new Vector3(c.Col * _hexWidth + (c.Row % 2 == 1 ? _hexOffset : 0f),
                        c.Row * _hexHeight, 0f);

        // ========================= Lifecycle =========================
        private void Awake()
        {
            _grid = GetComponent<HexGrid>();
        }

        private void Start()
        {
            if (_resolver == null) { Debug.LogError("[BattleBoardManager] AutoChessManager missing", this); enabled = false; return; }
            if (_uiDocument == null) { Debug.LogError("[BattleBoardManager] UIDocument missing", this); enabled = false; return; }

            _uiDocument.sortingOrder = BattleUISortOrder.BoardBenchHUD;
            _root = _uiDocument.rootVisualElement;
            _startBattleButton = _root.Q<Button>("start-battle-button");
            _placementCountText = _root.Q<Label>("placement-count-label");
            _benchScrollView = _root.Q<ScrollView>("bench-scroll");
            _benchContainer = _benchScrollView.contentContainer;
            _traitList = _root.Q<VisualElement>("trait-list");

            if (_startBattleButton == null) { Debug.LogError("[BattleBoardManager] start-battle-button not found in UXML", this); enabled = false; return; }

            _builder = new BattleBoardBuilder(
                _grid, _hexTilePrefab, _hexWidth, CoordToWorld, transform,
                this, _tiles, _benchCardsById, _benchContainer);
            _builder.BuildBoard();

            // Instantiate the placement controller after BuildBoard() so _tiles is fully populated.
            _placementCtrl = new BattlePlacementController(this, _tiles, _pendingPlacements, _grid);

            _unitController = new BattleUnitController(
                _units, _pendingPlacements, _studentSnapshots, _benchCardsById,
                getMaxSquadSize: () => _maxSquadSize,
                _battleUnitPrefab, _grid, _resolver, _startBattleButton, _placementCountText,
                CoordToWorld);

            _traitPanel = new BattleTraitPanel(_traitList, _resolver);

            _resolver.OnCombatantMoved += _unitController.HandleMoved;
            _resolver.OnCombatantActed += _unitController.HandleActed;
            _resolver.OnCombatantDefeated += _unitController.HandleDefeated;

            _startBattleButton.SetEnabled(false);
            _startBattleButton.clicked += OnStartBattle;

            _resolver.EnsureCombatantsInitialized();
            var students = _resolver.GetCombatantSnapshots().Where(s => s.IsStudent).ToList();
            foreach (var s in students)
                _studentSnapshots[s.Id] = s;
            _builder.BuildBench(students);
            _traitPanel.Refresh();
            _unitController.UpdatePlacementCountText();
#if UNITY_EDITOR
            if (_debugAutoStart) TestAutoPlace();
#endif
        }

        private void OnDestroy()
        {
            if (_resolver == null || _unitController == null) return;
            _resolver.OnCombatantMoved -= _unitController.HandleMoved;
            _resolver.OnCombatantActed -= _unitController.HandleActed;
            _resolver.OnCombatantDefeated -= _unitController.HandleDefeated;
        }

        // ========================= Drag/placement entry points =========================
        public void OnCardDragStart(string studentId) => _placementCtrl?.OnCardDragStart(studentId);
        public void OnCardDrag(Vector2 screenPos) => _placementCtrl?.OnCardDrag(screenPos);
        public void OnCardDragEnd(Vector2 screenPos) => _placementCtrl?.OnCardDragEnd(screenPos);


        // ========================= Placement state mutations =========================
        internal void PlaceStudent(string studentId, HexCoord coord) => _unitController.PlaceStudent(studentId, coord);
        internal void UnplaceStudent(string studentId) => _unitController.UnplaceStudent(studentId);



        // ========================= Test helper (editor/QA only) =========================
#if UNITY_EDITOR
        [Header("Debug (Editor only)")]
        [SerializeField] private bool _debugAutoStart;
        [SerializeField, Range(0.05f, 1f)] private float _debugPlayerStartHpPct = 1f;

        public void TestAutoPlace()
        {
            // Place whatever students were seeded, by their unique instance Id, across the front
            // row — capped by the squad size and the board width.
            int col = 0;
            foreach (var s in _studentSnapshots.Values)
            {
                if (col >= _grid.Cols || col >= _maxSquadSize) break;
                PlaceStudent(s.Id, new HexCoord(col++, 0));
            }
            OnStartBattle();
        }
#endif

        // ========================= Start Battle =========================
        private void OnStartBattle()
        {
            if (_battleStarted || _pendingPlacements.Count == 0) return;
            _battleStarted = true;
            _startBattleButton.style.display = DisplayStyle.None;
            _benchScrollView.style.display = DisplayStyle.None;

            // Enemy GameObjects are spawned from GetEnemyPlacements() — the same method
            // BeginBattle() now places the simulation from, so sprites and sim cannot disagree.
            var enemyPlacements = _resolver.GetEnemyPlacements();
            var enemySnapshots = _resolver.GetCombatantSnapshots().Where(s => !s.IsStudent);
            foreach (var e in enemySnapshots)
            {
                if (!enemyPlacements.TryGetValue(e.Id, out var coord)) continue;
                _unitController.SpawnEnemyUnit(e, coord);
            }

            _resolver.SetPlayerPlacements(_pendingPlacements);
#if UNITY_EDITOR
            if (_debugPlayerStartHpPct < 1f) _resolver.DebugSetAllPlayerHp(_debugPlayerStartHpPct);
#endif
            _resolver.BeginBattle();
            _traitPanel.Refresh();   // traits are now applied — reflect the live synergies
        }
    }
}
