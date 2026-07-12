using System.Collections.Generic;
using UnityEngine;

namespace MagicSchool.Battle
{
    /// <summary>
    /// Owns drag state and pointer-input processing for the Placement Phase.
    /// Holds a back-reference to BattleBoardManager and delegates state mutations
    /// (PlaceStudent / UnplaceStudent) to it — extracted from BattleBoardManager (M1b)
    /// so pointer/drag logic has a single home without a forced split of placement state.
    ///
    /// BattleBoardManager's public OnCard* methods are thin wrappers that call into here;
    /// BenchCardDragManipulator's API is unchanged.
    /// </summary>
    internal sealed class BattlePlacementController
    {
        private readonly BattleBoardManager               _board;
        private readonly Dictionary<HexCoord, HexTileView> _tiles;
        private readonly Dictionary<string, HexCoord>      _pendingPlacements;
        private readonly HexGrid                           _grid;
        private readonly float                             _hexWidth;
        // removed: Dictionary<string, ChampionData> _championDataLookup — champion system, rebuilding fresh

        // ── Drag state ────────────────────────────────────────────────────────
        private string      _draggingStudentId;
        private GameObject  _dragGhost;
        private HexTileView _hoveredTile;
        private Camera      _cam;

        private Camera Cam
        {
            get
            {
                if (_cam == null) _cam = Camera.main;
                return _cam;
            }
        }

        internal BattlePlacementController(
            BattleBoardManager               board,
            Dictionary<HexCoord, HexTileView> tiles,
            Dictionary<string, HexCoord>      pendingPlacements,
            HexGrid                           grid,
            float                             hexWidth)
        {
            _board              = board;
            _tiles              = tiles;
            _pendingPlacements  = pendingPlacements;
            _grid               = grid;
            _hexWidth           = hexWidth;
        }

        // ── Hero selection ─────────────────────────────────────────────────────
        // removed: champion-slug resolution via _championDataLookup — champion system,
        // rebuilding fresh. There is no champion ID distinct from the unit ID anymore.
        public void OnCardClicked(string studentId)
        {
            HeroSelection.Select(studentId);
        }

        // ── Drag start ────────────────────────────────────────────────────────
        public void OnCardDragStart(string studentId)
        {
            if (_board.IsBattleStarted) return;
            _draggingStudentId = studentId;
            _hoveredTile = null;

            // Highlight valid player tiles — skip entirely when squad cap is full for a new student.
            // A student being re-placed (already in _pendingPlacements) is always allowed to move.
            bool isReplacing = _pendingPlacements.ContainsKey(studentId);
            bool squadFull   = !isReplacing && _pendingPlacements.Count >= _board.MaxSquadSize;

            if (!squadFull)
            {
                foreach (var kv in _tiles)
                {
                    bool isOwnTile = _pendingPlacements.TryGetValue(studentId, out var own) && kv.Key == own;
                    if (kv.Key.Row < HexGrid.PlayerRowCount && (!_grid.IsOccupied(kv.Key) || isOwnTile))
                        kv.Value.SetHighlight(true);
                }
            }

            // Create a drag ghost — world-space SpriteRenderer, parented to the board transform.
            _dragGhost = new GameObject("DragGhost");
            _dragGhost.transform.SetParent(_board.transform, false);
            var sr          = _dragGhost.AddComponent<SpriteRenderer>();
            sr.sprite       = HexSpriteGenerator.GetFallbackSprite();
            var c           = BattleBoardManager.StudentColor(studentId);
            sr.color        = new Color(c.r, c.g, c.b, 0.6f);
            sr.sortingOrder = 10;
            _dragGhost.transform.localScale = Vector3.one * 0.4f;
        }

        // ── Drag move ────────────────────────────────────────────────────────
        public void OnCardDrag(Vector2 screenPos)
        {
            if (_dragGhost == null) return;
            Vector3 world = Cam.ScreenToWorldPoint(new Vector3(screenPos.x, screenPos.y, -Cam.transform.position.z));
            world.z = 0f;
            _dragGhost.transform.position = world;

            // Update hover highlight — brightest tile nearest the cursor
            bool isReplacing = _pendingPlacements.TryGetValue(_draggingStudentId, out var ownCoord);
            HexTileView nearestView = null;
            float minDist = float.MaxValue;
            foreach (var kv in _tiles)
            {
                if (kv.Key.Row >= HexGrid.PlayerRowCount) continue;
                bool ownTile = isReplacing && kv.Key == ownCoord;
                if (_grid.IsOccupied(kv.Key) && !ownTile) continue;
                float d = Vector3.Distance(BattleBoardManager.CoordToWorld(kv.Key), world);
                if (d < _hexWidth * 0.75f && d < minDist) { minDist = d; nearestView = kv.Value; }
            }

            if (nearestView != _hoveredTile)
            {
                _hoveredTile?.SetHover(false);
                _hoveredTile = nearestView;
                _hoveredTile?.SetHover(true);
            }
        }

        // ── Drag end ──────────────────────────────────────────────────────────
        public void OnCardDragEnd(Vector2 screenPos)
        {
            // Clear hover then all highlights
            _hoveredTile?.SetHover(false);
            _hoveredTile = null;
            foreach (var kv in _tiles) kv.Value.SetHighlight(false);

            if (_dragGhost != null) { Object.Destroy(_dragGhost); _dragGhost = null; }

            if (_draggingStudentId == null) return;

            // Hit-test world pos -> nearest valid player tile
            Vector3 worldPos = Cam.ScreenToWorldPoint(new Vector3(screenPos.x, screenPos.y, -Cam.transform.position.z));
            worldPos.z = 0f;

            bool hasExisting = _pendingPlacements.TryGetValue(_draggingStudentId, out var existingCoord);
            HexCoord? closest = null;
            float     minDist = float.MaxValue;
            foreach (var kv in _tiles)
            {
                if (kv.Key.Row >= HexGrid.PlayerRowCount) continue;
                bool ownTile = hasExisting && kv.Key == existingCoord;
                if (_grid.IsOccupied(kv.Key) && !ownTile) continue;
                float d = Vector3.Distance(BattleBoardManager.CoordToWorld(kv.Key), worldPos);
                if (d < minDist && d < _hexWidth * 0.75f) { minDist = d; closest = kv.Key; }
            }

            if (closest.HasValue)
                _board.PlaceStudent(_draggingStudentId, closest.Value);
            else if (_pendingPlacements.ContainsKey(_draggingStudentId))
                _board.UnplaceStudent(_draggingStudentId);

            _draggingStudentId = null;
        }
    }
}
