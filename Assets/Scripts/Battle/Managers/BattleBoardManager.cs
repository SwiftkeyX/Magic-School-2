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
        [SerializeField] private AutoChessManager _resolver;
        [SerializeField] private GameObject         _hexTilePrefab;
        [SerializeField] private GameObject         _battleUnitPrefab;
        [SerializeField] private UIDocument         _uiDocument;

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
        private Button        _startBattleButton;
        private Label         _placementCountText;
        private ScrollView    _benchScrollView;
        private VisualElement _benchContainer;
        private VisualElement _traitList;
        private readonly Dictionary<string, VisualElement> _benchCardsById = new();

        // ── State ────────────────────────────────────────────────────────────
        private readonly Dictionary<HexCoord, HexTileView>      _tiles             = new();
        private readonly Dictionary<string,   BattleUnit>       _units             = new();
        private readonly Dictionary<string,   HexCoord>         _pendingPlacements = new();
        private readonly Dictionary<string,   CombatantSnapshot> _studentSnapshots  = new();

        private HexGrid _grid;
        private bool    _battleStarted;

        // ── Placement controller (owns drag state and pointer input) ──────────
        private BattlePlacementController _placementCtrl;

        // ── Internal accessors (read by BattlePlacementController) ────────────
        internal bool IsBattleStarted => _battleStarted;
        internal int  MaxSquadSize    => _maxSquadSize;
        internal float HexWidth       => _hexWidth;

        // The drag ghost needs the hero's authored tint. It used to call a static
        // BattleBoardManager.StudentColor(id) that switch'd on the literal "knight"/"archer".
        // It now reads the same snapshot the board renders from — one source, authored on the asset.
        internal Color GetStudentTint(string studentId) =>
            _studentSnapshots.TryGetValue(studentId, out var snap) ? snap.Tint : Color.white;

        // Instance geometry, so the board can be re-laid-out from the Inspector.
        internal Vector3 CoordToWorld(HexCoord c) =>
            new Vector3(c.Col * _hexWidth + (c.Row % 2 == 1 ? _hexOffset : 0f),
                        c.Row * _hexHeight, 0f);

        // ── Lifecycle ────────────────────────────────────────────────────────
        private void Awake()
        {
            _grid = GetComponent<HexGrid>();
        }

        private void Start()
        {
            if (_resolver == null)   { Debug.LogError("[BattleBoardManager] AutoChessManager missing", this); enabled = false; return; }
            if (_uiDocument == null) { Debug.LogError("[BattleBoardManager] UIDocument missing", this); enabled = false; return; }

            _uiDocument.sortingOrder = BattleUISortOrder.BoardBenchHUD;
            _root = _uiDocument.rootVisualElement;
            _startBattleButton  = _root.Q<Button>("start-battle-button");
            _placementCountText = _root.Q<Label>("placement-count-label");
            _benchScrollView    = _root.Q<ScrollView>("bench-scroll");
            _benchContainer     = _benchScrollView.contentContainer;
            _traitList          = _root.Q<VisualElement>("trait-list");

            if (_startBattleButton == null) { Debug.LogError("[BattleBoardManager] start-battle-button not found in UXML", this); enabled = false; return; }

            BuildBoard();

            // Instantiate the placement controller after BuildBoard() so _tiles is fully populated.
            _placementCtrl = new BattlePlacementController(this, _tiles, _pendingPlacements, _grid);

            _resolver.OnCombatantMoved    += HandleMoved;
            _resolver.OnCombatantActed    += HandleActed;
            _resolver.OnCombatantDefeated += HandleDefeated;

            _startBattleButton.SetEnabled(false);
            _startBattleButton.clicked += OnStartBattle;

            _resolver.EnsureCombatantsInitialized();
            var students = _resolver.GetCombatantSnapshots().Where(s => s.IsStudent).ToList();
            foreach (var s in students)
                _studentSnapshots[s.Id] = s;
            BuildBench(students);
            RefreshTraitPanel();
            UpdatePlacementCountText();
#if UNITY_EDITOR
            if (_debugAutoStart) TestAutoPlace();
#endif
        }

        private void OnDestroy()
        {
            if (_resolver == null) return;
            _resolver.OnCombatantMoved    -= HandleMoved;
            _resolver.OnCombatantActed    -= HandleActed;
            _resolver.OnCombatantDefeated -= HandleDefeated;
        }

        // ── Board construction ───────────────────────────────────────────────
        private void BuildBoard()
        {
            var hexSprite = HexSpriteGenerator.GetHexSprite();

            // Full visual height of a pointy-top hex whose centre-to-centre column width = _hexWidth
            float hexVisualHeight = _hexWidth * 2f / Mathf.Sqrt(3f);
            var   scale           = new Vector3(_hexWidth, hexVisualHeight, 1f);

            for (int row = 0; row < _grid.Rows; row++)
            for (int col = 0; col < _grid.Cols; col++)
            {
                var coord = new HexCoord(col, row);
                var go    = Instantiate(_hexTilePrefab, CoordToWorld(coord), Quaternion.identity, transform);
                go.transform.localScale = scale;
                var sr = go.GetComponent<SpriteRenderer>();
                if (sr != null) sr.sprite = hexSprite;
                var view = go.GetComponent<HexTileView>();
                // Player-side is a property of the board, not of the tile — pass it in rather than
                // letting the tile reach for a static board constant.
                view.Init(coord, _grid.PlayerRowCount);
                _tiles[coord] = view;
            }
        }

        private void BuildBench(List<CombatantSnapshot> students)
        {
            _benchContainer.Clear();
            _benchCardsById.Clear();

            foreach (var s in students)
            {
                var card = new VisualElement();
                card.name = $"Card_{s.Id}";
                card.AddToClassList("bench-card");
                card.style.backgroundColor = new StyleColor(s.Tint);   // authored on the asset

                var label = new Label(s.DisplayName);
                label.AddToClassList("bench-card-label");
                card.Add(label);

                card.AddManipulator(new BenchCardDragManipulator(this, s.Id));

                _benchContainer.Add(card);
                _benchCardsById[s.Id] = card;
            }
        }

        // ── Drag/placement entry points (delegate to BattlePlacementController) ──
        public void OnCardDragStart(string studentId) => _placementCtrl?.OnCardDragStart(studentId);
        public void OnCardDrag(Vector2 screenPos)     => _placementCtrl?.OnCardDrag(screenPos);
        public void OnCardDragEnd(Vector2 screenPos)  => _placementCtrl?.OnCardDragEnd(screenPos);
        // removed: OnCardClicked — it forwarded to HeroSelection.Select(), which had zero
        // subscribers. Clicking a bench card did nothing; now it honestly does nothing.

        // ── Placement state mutations (called back by BattlePlacementController) ─
        internal void UnplaceStudent(string studentId)
        {
            if (_pendingPlacements.TryGetValue(studentId, out var coord))
            {
                _grid.ClearOccupant(coord);
                _pendingPlacements.Remove(studentId);
            }
            if (_units.TryGetValue(studentId, out var unit))
            {
                Destroy(unit.gameObject);
                _units.Remove(studentId);
            }
            if (_benchCardsById.TryGetValue(studentId, out var card))
                card.style.opacity = 1f;

            RefreshStartButton();
            UpdatePlacementCountText();
        }

        internal void PlaceStudent(string studentId, HexCoord coord)
        {
            if (!_studentSnapshots.TryGetValue(studentId, out var snap)) return;
            if (_grid.IsOccupied(coord)) return;

            // Squad cap: reject a new placement at the cap. Re-placing an already-placed student
            // (moving it to another tile) is always allowed.
            bool isReplacing = _pendingPlacements.ContainsKey(studentId);
            if (!isReplacing && _pendingPlacements.Count >= _maxSquadSize) return;

            // Remove existing placement if re-placing — restore card alpha first
            if (_pendingPlacements.TryGetValue(studentId, out var oldCoord))
            {
                _grid.ClearOccupant(oldCoord);
                if (_units.TryGetValue(studentId, out var oldUnit))
                {
                    Destroy(oldUnit.gameObject);
                    _units.Remove(studentId);
                }
                if (_benchCardsById.TryGetValue(studentId, out var existingCard))
                    existingCard.style.opacity = 1f;
            }

            _pendingPlacements[studentId] = coord;
            _grid.SetOccupant(coord, studentId);

            var unit = SpawnUnit(snap, coord);
            if (unit == null)
            {
                // Roll back so the board is never left half-placed.
                _pendingPlacements.Remove(studentId);
                _grid.ClearOccupant(coord);
                return;
            }
            _units[studentId] = unit;

            // Dim bench card to show it's placed (kept in the bench so it can be re-dragged)
            if (_benchCardsById.TryGetValue(studentId, out var card))
                card.style.opacity = 0.4f;

            RefreshStartButton();
            UpdatePlacementCountText();
        }

        // Single spawn path for both teams. Appearance comes entirely from the snapshot — the
        // board no longer knows or cares what a "knight" is.
        private BattleUnit SpawnUnit(CombatantSnapshot snap, HexCoord coord)
        {
            var go   = Instantiate(_battleUnitPrefab, CoordToWorld(coord), Quaternion.identity);
            var unit = go.GetComponent<BattleUnit>();
            if (unit == null)
            {
                Debug.LogError($"[BattleBoardManager] BattleUnit component missing on _battleUnitPrefab " +
                               $"(spawning '{snap.DisplayName}')", go);
                Destroy(go);
                return null;
            }

            unit.Init(snap.Id, coord);
            unit.SetVisual(snap.Icon, snap.Tint);
            unit.InitHealthBar(snap.MaxHP, snap.MaxHP);
            return unit;
        }

        private void RefreshStartButton() =>
            _startBattleButton.SetEnabled(_pendingPlacements.Count >= 1 && _pendingPlacements.Count <= _maxSquadSize);

        private void UpdatePlacementCountText()
        {
            if (_placementCountText != null)
                _placementCountText.text = $"{_pendingPlacements.Count}/{_maxSquadSize} heroes placed";
        }

        // ── Test helper (editor/QA only) ─────────────────────────────────────
#if UNITY_EDITOR
        [Header("Debug (Editor only)")]
        [SerializeField] private bool  _debugAutoStart;
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

        // ── Start Battle ─────────────────────────────────────────────────────
        private void OnStartBattle()
        {
            if (_battleStarted || _pendingPlacements.Count == 0) return;
            _battleStarted = true;
            _startBattleButton.style.display = DisplayStyle.None;
            _benchScrollView.style.display   = DisplayStyle.None;

            // Enemy GameObjects are spawned from GetEnemyPlacements() — the same method
            // BeginBattle() now places the simulation from, so sprites and sim cannot disagree.
            var enemyPlacements = _resolver.GetEnemyPlacements();
            var enemySnapshots  = _resolver.GetCombatantSnapshots().Where(s => !s.IsStudent);
            foreach (var e in enemySnapshots)
            {
                if (!enemyPlacements.TryGetValue(e.Id, out var coord)) continue;
                var unit = SpawnUnit(e, coord);
                if (unit != null) _units[e.Id] = unit;
            }

            _resolver.SetPlayerPlacements(_pendingPlacements);
#if UNITY_EDITOR
            if (_debugPlayerStartHpPct < 1f) _resolver.DebugSetAllPlayerHp(_debugPlayerStartHpPct);
#endif
            _resolver.BeginBattle();
            RefreshTraitPanel();   // traits are now applied — reflect the live synergies
        }

        // ── Active-trait panel (left side) ───────────────────────────────────
        // Rebuilds the left trait list from the player's fielded synergies. Active traits
        // (a breakpoint is met) render highlighted; others are dimmed. See Trait.md.
        private void RefreshTraitPanel()
        {
            if (_traitList == null) return;
            _traitList.Clear();

            var traits = _resolver.GetActiveTraits(Team.Player)
                .OrderByDescending(t => t.active != null)
                .ThenByDescending(t => t.count)
                .ToList();

            foreach (var (trait, count, active) in traits)
            {
                if (trait == null) continue;
                bool isActive = active != null;

                var row = new VisualElement();
                row.AddToClassList("trait-row");
                row.AddToClassList(isActive ? "trait-row-active" : "trait-row-inactive");

                var nameLabel = new Label(trait.DisplayName);
                nameLabel.AddToClassList("trait-name");
                if (!isActive) nameLabel.AddToClassList("trait-name-inactive");
                row.Add(nameLabel);

                int target = isActive
                    ? active.UnitCount
                    : (trait.Breakpoints != null && trait.Breakpoints.Count > 0 ? trait.Breakpoints.Min(b => b.UnitCount) : count);
                var countLabel = new Label($"{count}/{target}");
                countLabel.AddToClassList("trait-count");
                row.Add(countLabel);

                _traitList.Add(row);
            }
        }

        // ── Event handlers ───────────────────────────────────────────────────
        private void HandleMoved(string id, HexCoord from, HexCoord to)
        {
            if (!_units.TryGetValue(id, out var unit)) return;
            unit.MoveTo(CoordToWorld(to), to);
        }

        private void HandleActed(string actorId, string targetId, int damage, List<string> flags)
        {
            if (_units.TryGetValue(actorId, out var actor) && _units.TryGetValue(targetId, out var target))
            {
                actor.PlayAttackAnim(target.transform.position);
                target.UpdateHP(_resolver.GetCurrentHP(targetId), _resolver.GetMaxHP(targetId));
            }
        }

        private void HandleDefeated(string id)
        {
            if (!_units.TryGetValue(id, out var unit)) return;
            unit.PlayDeathAnim();
            _units.Remove(id);
        }

        // removed: StudentColor(id) / EnemyColor(id) — hardcoded switch on the literals "knight"
        // and "archer". Any new HeroDataSO asset fell through to the default case and rendered as a
        // gray square, which meant adding a hero required a C# edit. Appearance is now authored on
        // HeroDataSO (Icon / PlayerTint / EnemyTint) and reaches the view via CombatantSnapshot.
        // See Hero GDD Core Rule 7 — presentation is data, never a code lookup.
    }
}
