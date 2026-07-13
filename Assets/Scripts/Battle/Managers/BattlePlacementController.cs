using System.Collections.Generic;
using UnityEngine;

namespace MagicSchool.Battle
{
    /// <summary>
    /// Owns drag state and pointer-input processing for the Placement Phase.
    /// Holds a back-reference to BattleBoardManager and delegates state mutations
    /// (PlaceStudent / UnplaceStudent) to it.
    /// </summary>
    internal sealed class BattlePlacementController
    {
        private readonly BattleBoardManager                _board;
        private readonly Dictionary<HexCoord, HexTileView> _tiles;
        private readonly Dictionary<string, HexCoord>      _pendingPlacements;
        private readonly HexGrid                           _grid;

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
            BattleBoardManager                board,
            Dictionary<HexCoord, HexTileView> tiles,
            Dictionary<string, HexCoord>      pendingPlacements,
            HexGrid                           grid)
        {
            _board             = board;
            _tiles             = tiles;
            _pendingPlacements = pendingPlacements;
            _grid              = grid;
        }

        // removed: OnCardClicked(studentId) — it forwarded to HeroSelection.Select(), which had
        // zero subscribers anywhere in the project. The click did nothing.

        // ── Drag start ────────────────────────────────────────────────────────
        public void OnCardDragStart(string studentId)
        {
            if (_board.IsBattleStarted) return;
            _draggingStudentId = studentId;
            _hoveredTile = null;

            // Highlight valid player tiles — skip entirely when the squad cap is full for a new
            // student. A student being re-placed is always allowed to move.
            bool isReplacing = _pendingPlacements.ContainsKey(studentId);
            bool squadFull   = !isReplacing && _pendingPlacements.Count >= _board.MaxSquadSize;

            if (!squadFull)
            {
                foreach (var kv in _tiles)
                {
                    bool isOwnTile = _pendingPlacements.TryGetValue(studentId, out var own) && kv.Key == own;
                    if (kv.Key.Row < _grid.PlayerRowCount && (!_grid.IsOccupied(kv.Key) || isOwnTile))
                        kv.Value.SetHighlight(true);
                }
            }

            // Create a drag ghost — world-space SpriteRenderer, parented to the board transform.
            // Its tint comes from the hero's authored asset, via the board's snapshot lookup.
            _dragGhost = new GameObject("DragGhost");
            _dragGhost.transform.SetParent(_board.transform, false);
            var sr          = _dragGhost.AddComponent<SpriteRenderer>();
            sr.sprite       = HexSpriteGenerator.GetFallbackSprite();
            var c           = _board.GetStudentTint(studentId);
            sr.color        = new Color(c.r, c.g, c.b, 0.6f);
            sr.sortingOrder = 10;
            _dragGhost.transform.localScale = Vector3.one * 0.4f;
        }

        // ── Drag move ────────────────────────────────────────────────────────
        public void OnCardDrag(Vector2 screenPos)
        {
            if (_dragGhost == null) return;
            Vector3 world = ScreenToWorld(screenPos);
            _dragGhost.transform.position = world;

            // Update hover highlight — nearest valid tile to the cursor
            HexTileView nearestView = FindNearestValidTile(world, out _);
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

            FindNearestValidTile(ScreenToWorld(screenPos), out HexCoord? closest);

            if (closest.HasValue)
                _board.PlaceStudent(_draggingStudentId, closest.Value);
            else if (_pendingPlacements.ContainsKey(_draggingStudentId))
                _board.UnplaceStudent(_draggingStudentId);

            _draggingStudentId = null;
        }

        // ── Helpers ───────────────────────────────────────────────────────────
        private Vector3 ScreenToWorld(Vector2 screenPos)
        {
            Vector3 world = Cam.ScreenToWorldPoint(new Vector3(screenPos.x, screenPos.y, -Cam.transform.position.z));
            world.z = 0f;
            return world;
        }

        // Nearest player-side tile to `world` that the dragged student may legally occupy,
        // within snap distance. Shared by the hover highlight and the drop hit-test so the tile
        // you see highlighted is always the tile you actually drop onto.
        private HexTileView FindNearestValidTile(Vector3 world, out HexCoord? coord)
        {
            bool hasExisting = _pendingPlacements.TryGetValue(_draggingStudentId ?? string.Empty, out var existingCoord);
            float snapRadius = _board.HexWidth * 0.75f;

            HexTileView bestView  = null;
            HexCoord?   bestCoord = null;
            float       minDist   = float.MaxValue;

            foreach (var kv in _tiles)
            {
                if (kv.Key.Row >= _grid.PlayerRowCount) continue;
                bool ownTile = hasExisting && kv.Key == existingCoord;
                if (_grid.IsOccupied(kv.Key) && !ownTile) continue;

                float d = Vector3.Distance(_board.CoordToWorld(kv.Key), world);
                if (d < snapRadius && d < minDist)
                {
                    minDist   = d;
                    bestView  = kv.Value;
                    bestCoord = kv.Key;
                }
            }

            coord = bestCoord;
            return bestView;
        }
    }
}
