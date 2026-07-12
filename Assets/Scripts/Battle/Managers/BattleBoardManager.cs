using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.UIElements;

namespace MagicSchool.Battle
{
    public class BattleBoardManager : MonoBehaviour
    {
        // ── Inspector ────────────────────────────────────────────────────────
        [SerializeField] AutoBattleResolver   _resolver;
        [SerializeField] GameObject           _hexTilePrefab;
        [SerializeField] GameObject           _battleUnitPrefab;
        [SerializeField] private UnityEngine.UIElements.UIDocument _uiDocument;
        // removed: TraitTracker _traitTracker, ChampionRoster _championRoster — trait/champion system, rebuilding fresh

        private UnityEngine.UIElements.VisualElement _root;
        private UnityEngine.UIElements.Button        _startBattleButton;
        private UnityEngine.UIElements.Label         _placementCountText;
        private ScrollView _benchScrollView;
        private UnityEngine.UIElements.VisualElement _benchContainer;
        private UnityEngine.UIElements.VisualElement _traitList;
        private readonly Dictionary<string, UnityEngine.UIElements.VisualElement> _benchCardsById = new();

        // ── Hex constants ────────────────────────────────────────────────────
        private const float HexWidth  = 1.1f;
        private const float HexHeight = 0.95f;
        private const float HexOffset = 0.55f;

        // ── State ────────────────────────────────────────────────────────────
        private readonly Dictionary<HexCoord, HexTileView>      _tiles             = new();
        private readonly Dictionary<string,   BattleUnit>        _units             = new();
        private readonly Dictionary<string,   HexCoord>          _pendingPlacements = new();
        private readonly Dictionary<string,   CombatantSnapshot> _studentSnapshots  = new();

        private HexGrid _grid;
        private bool    _battleStarted;
        private int     _maxSquadSize        = int.MaxValue; // unlimited in standalone; set by BeginPlacement() in production
        // removed: _placementPhaseActive, _championDataLookup — BeginPlacement()/champion system, rebuilding fresh

        // ── Placement controller (owns drag state and pointer input) ──────────
        private BattlePlacementController _placementCtrl;

        // ── Internal properties (read by BattlePlacementController) ──────────
        internal bool IsBattleStarted => _battleStarted;
        internal int  MaxSquadSize    => _maxSquadSize;

        // ── Lifecycle ────────────────────────────────────────────────────────
        private void Awake()
        {
            _grid = GetComponent<HexGrid>();
            if (_grid == null) { Debug.LogError("[BattleBoardManager] HexGrid missing", this); enabled = false; return; }
            // removed: RunManager.Instance?.RegisterBattleBoardManager(this) — meta-progression system, rebuilding fresh
        }

        private void Start()
        {
            if (_resolver == null)    { Debug.LogError("[BattleBoardManager] AutoBattleResolver missing", this); enabled = false; return; }
            if (_uiDocument == null)  { Debug.LogError("[BattleBoardManager] UIDocument missing", this); enabled = false; return; }

            _uiDocument.sortingOrder = BattleUISortOrder.BoardBenchHUD;
            _root = _uiDocument.rootVisualElement;
            _startBattleButton  = _root.Q<UnityEngine.UIElements.Button>("start-battle-button");
            _placementCountText = _root.Q<UnityEngine.UIElements.Label>("placement-count-label");
            _benchScrollView = _root.Q<ScrollView>("bench-scroll");
            _benchContainer = _benchScrollView.contentContainer;
            _traitList = _root.Q<UnityEngine.UIElements.VisualElement>("trait-list");

            if (_startBattleButton == null) { Debug.LogError("[BattleBoardManager] start-battle-button not found in UXML", this); enabled = false; return; }

            BuildBoard();

            // Instantiate the placement controller after BuildBoard() so _tiles is fully populated.
            _placementCtrl = new BattlePlacementController(this, _tiles, _pendingPlacements, _grid, HexWidth);

            _resolver.OnCombatantMoved    += HandleMoved;
            _resolver.OnCombatantActed    += HandleActed;
            _resolver.OnCombatantDefeated += HandleDefeated;

            _startBattleButton.SetEnabled(false);
            _startBattleButton.clicked += OnStartBattle;

            // removed: RunManager-driven production path (BeginPlacement() called externally) —
            // meta-progression system, rebuilding fresh. This standalone path is now unconditional.
            _maxSquadSize = int.MaxValue;
            _resolver.EnsureCombatantsInitialized();
            var snapshots = _resolver.GetCombatantSnapshots();
            var students  = snapshots.Where(s => s.IsStudent).ToList();
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

        // removed: BeginPlacement(List<StudentCombatData>, List<EnemyCombatData>, int) — this
        // was called by RunManager after SetCombatants() in the production flow. Meta-progression
        // system, rebuilding fresh. The standalone path in Start() now covers all cases.

        // ── Board construction ───────────────────────────────────────────────
        // Full visual height of a pointy-top hex whose centre-to-centre column width = HexWidth
        private static readonly float HexVisualHeight = HexWidth * 2f / Mathf.Sqrt(3f);

        private void BuildBoard()
        {
            var hexSprite = HexSpriteGenerator.GetHexSprite();
            var scale     = new Vector3(HexWidth, HexVisualHeight, 1f);

            for (int row = 0; row < HexGrid.Rows; row++)
            for (int col = 0; col < HexGrid.Cols; col++)
            {
                var coord = new HexCoord(col, row);
                var go    = Instantiate(_hexTilePrefab, CoordToWorld(coord), Quaternion.identity, transform);
                go.transform.localScale = scale;
                var sr = go.GetComponent<SpriteRenderer>();
                if (sr != null) sr.sprite = hexSprite;
                var view = go.GetComponent<HexTileView>();
                view.Init(coord);
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
                card.style.backgroundColor = new StyleColor(StudentColor(s.HeroId));

                var label = new Label(s.DisplayName);
                label.AddToClassList("bench-card-label");
                card.Add(label);

                card.AddManipulator(new BenchCardDragManipulator(this, s.Id));

                _benchContainer.Add(card);
                _benchCardsById[s.Id] = card;
            }
        }

        // ── Drag/placement entry points (delegate to BattlePlacementController) ──
        // Thin wrappers — BenchCardDragManipulator's API is unchanged.
        public void OnCardClicked(string studentId)   => _placementCtrl?.OnCardClicked(studentId);
        public void OnCardDragStart(string studentId) => _placementCtrl?.OnCardDragStart(studentId);
        public void OnCardDrag(Vector2 screenPos)     => _placementCtrl?.OnCardDrag(screenPos);
        public void OnCardDragEnd(Vector2 screenPos)  => _placementCtrl?.OnCardDragEnd(screenPos);

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

            _startBattleButton.SetEnabled(_pendingPlacements.Count >= 1 && _pendingPlacements.Count <= _maxSquadSize);
            UpdatePlacementCountText();
        }

        private void UpdatePlacementCountText()
        {
            if (_placementCountText != null)
                _placementCountText.text = $"{_pendingPlacements.Count}/{_maxSquadSize} heroes placed";
        }

        internal void PlaceStudent(string studentId, HexCoord coord)
        {
            if (!_studentSnapshots.TryGetValue(studentId, out var snap)) return;
            if (_grid.IsOccupied(coord)) return;

            // Squad cap: reject placement of a new (currently unplaced) student when cap is reached.
            // Re-placing an already-placed student (moving it to a different tile) is always allowed.
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

            // Spawn unit — MaxHP sourced from snapshot (B3).
            // L3: null-check BattleUnit component before dereferencing; a misconfigured prefab
            // would otherwise NullReferenceException here. Roll back placement state on failure
            // so the board is not left in a half-placed inconsistency.
            var go   = Instantiate(_battleUnitPrefab, CoordToWorld(coord), Quaternion.identity);
            var unit = go.GetComponent<BattleUnit>();
            if (unit == null)
            {
                Debug.LogError($"[BattleBoardManager] BattleUnit component missing on _battleUnitPrefab for student '{studentId}'", go);
                Destroy(go);
                _pendingPlacements.Remove(studentId);
                _grid.ClearOccupant(coord);
                return;
            }
            unit.Init(studentId, coord, snap.HeroId);
            unit.InitHealthBar(snap.MaxHP, snap.MaxHP);
            var sr = go.GetComponent<SpriteRenderer>();
            if (sr != null)
            {
                if (sr.sprite == null) sr.sprite = HexSpriteGenerator.GetFallbackSprite();
                sr.color = StudentColor(snap.HeroId);
            }
            _units[studentId] = unit;

            // Dim bench card to show it's placed (kept in the bench so it can be re-dragged)
            if (_benchCardsById.TryGetValue(studentId, out var card))
                card.style.opacity = 0.4f;

            _startBattleButton.SetEnabled(_pendingPlacements.Count >= 1 && _pendingPlacements.Count <= _maxSquadSize);
            UpdatePlacementCountText();
        }

        // ── Test helper (editor/QA only) ─────────────────────────────────────
#if UNITY_EDITOR
        [SerializeField] private bool  _debugAutoStart;
        [SerializeField] private float _debugPlayerStartHpPct = 1f;

        public void TestAutoPlace()
        {
            // Place whatever students were seeded, by their unique instance Id, across the
            // front row. No hardcoded ids — works for any roster and unique-id scheme.
            int col = 0;
            foreach (var s in _studentSnapshots.Values)
                PlaceStudent(s.Id, new HexCoord(col++, 0));
            OnStartBattle();
        }
#endif

        // ── Start Battle ─────────────────────────────────────────────────────
        private void OnStartBattle()
        {
            if (_battleStarted || _pendingPlacements.Count == 0) return;
            _battleStarted = true;
            _startBattleButton.style.display = UnityEngine.UIElements.DisplayStyle.None;
            _benchScrollView.style.display = UnityEngine.UIElements.DisplayStyle.None;

            // Snapshot enemy data BEFORE RunManager may re-call SetCombatants with the filtered squad.
            // Both paths spawn enemy GOs here (visual layer — BattleBoardManager's job).
            var enemyPlacements = _resolver.GetAutoEnemyPlacements();
            var enemySnapshots  = _resolver.GetCombatantSnapshots().Where(s => !s.IsStudent).ToList();
            foreach (var e in enemySnapshots)
            {
                if (!enemyPlacements.TryGetValue(e.Id, out var coord)) continue;
                var go   = Instantiate(_battleUnitPrefab, CoordToWorld(coord), Quaternion.identity);
                var unit = go.GetComponent<BattleUnit>();
                // L3: null-check BattleUnit component; a misconfigured prefab would NullReferenceException here.
                if (unit == null)
                {
                    Debug.LogError($"[BattleBoardManager] BattleUnit component missing on _battleUnitPrefab for enemy '{e.Id}'", go);
                    Destroy(go);
                    continue;
                }
                unit.Init(e.Id, coord, e.HeroId);
                unit.InitHealthBar(e.MaxHP, e.MaxHP);
                var sr = go.GetComponent<SpriteRenderer>();
                if (sr != null)
                {
                    if (sr.sprite == null) sr.sprite = HexSpriteGenerator.GetFallbackSprite();
                    sr.color = EnemyColor(e.HeroId);
                }
                _units[e.Id] = unit;
            }

            // removed: RunManager-driven production path (ConfirmSquadPlacement) — meta-progression
            // system, rebuilding fresh. This standalone call is now unconditional.
            _resolver.SetUnitPositions(_pendingPlacements);
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

                var row = new UnityEngine.UIElements.VisualElement();
                row.AddToClassList("trait-row");
                row.AddToClassList(isActive ? "trait-row-active" : "trait-row-inactive");

                var nameLabel = new UnityEngine.UIElements.Label(trait.DisplayName);
                nameLabel.AddToClassList("trait-name");
                if (!isActive) nameLabel.AddToClassList("trait-name-inactive");
                row.Add(nameLabel);

                int target = isActive
                    ? active.UnitCount
                    : (trait.Tiers != null && trait.Tiers.Count > 0 ? trait.Tiers.Min(t => t.UnitCount) : count);
                var countLabel = new UnityEngine.UIElements.Label($"{count}/{target}");
                countLabel.AddToClassList("trait-count");
                row.Add(countLabel);

                _traitList.Add(row);
            }
        }

        // removed: ApplyTraitModifiers(AutoBattleResolver, Dictionary<string, HexCoord>) — trait
        // system, rebuilding fresh. Combatants use their base stats as-is (no pre-battle modifier pass).

        // ── Event handlers ───────────────────────────────────────────────────
        private void HandleMoved(string id, HexCoord from, HexCoord to)
        {
            if (!_units.TryGetValue(id, out var unit)) return;
            unit.MoveTo(CoordToWorld(to), to);
        }

        private void HandleActed(string actorId, string targetId, int damage, System.Collections.Generic.List<string> flags)
        {
            if (_units.TryGetValue(actorId, out var actor) && _units.TryGetValue(targetId, out var target))
            {
                actor.PlayAttackAnim(target.transform.position);
                Debug.DrawLine(actor.transform.position, target.transform.position, Color.red, 0.5f);
                int cur = _resolver.GetCurrentHP(targetId);
                int max = _resolver.GetMaxHP(targetId);
                target.UpdateHP(cur, max);
            }
        }

        private void HandleDefeated(string id)
        {
            if (!_units.TryGetValue(id, out var unit)) return;
            unit.PlayDeathAnim();
            _units.Remove(id);
        }

        // removed: HandleSkillCast, HandleManaChanged, HandleCastStateChanged — skill system,
        // rebuilding fresh. BattleUnit still exposes PlayCastText/UpdateMana/SetCastingVisual
        // for whenever that's rebuilt.

        // ── Helpers ──────────────────────────────────────────────────────────
        // internal static so BattlePlacementController can call BattleBoardManager.CoordToWorld()
        // without holding an instance reference — pure geometry, no mutable state.
        internal static Vector3 CoordToWorld(HexCoord c) =>
            new Vector3(c.Col * HexWidth + (c.Row % 2 == 1 ? HexOffset : 0f),
                        c.Row * HexHeight, 0f);

        // internal static so BattlePlacementController can tint the drag ghost consistently.
        internal static Color StudentColor(string id) => id switch
        {
            "knight" => new Color(0.2f, 0.5f, 1.0f),
            "archer" => new Color(0.2f, 0.8f, 0.3f),
            _        => new Color(0.3f, 0.3f, 0.3f),
        };

        private static Color EnemyColor(string id) => id switch
        {
            "knight" => new Color(1.0f, 0.4f, 0.4f),
            "archer" => new Color(1.0f, 0.7f, 0.2f),
            _        => Color.gray,
        };
    }
}
