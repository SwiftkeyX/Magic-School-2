using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;
using UObject = UnityEngine.Object;

namespace MagicSchool.Battle
{
    // Owns all unit lifecycle operations: spawning, placing, unplacing, and responding to
    // sim events (moved, acted, defeated). Shared state dictionaries are owned by the facade
    // and passed by reference so mutations here are visible to OnStartBattle and BattlePlacementController
    // — same pattern as ACSetup sharing _playerPlacements/_enemyPlacements with ACManager.
    internal class BattleUnitController
    {
        private readonly Dictionary<string, BattleUnit> _units;
        private readonly Dictionary<string, HexCoord> _pendingPlacements;
        private readonly Dictionary<string, CombatantSnapshot> _studentSnapshots;
        private readonly Dictionary<string, VisualElement> _benchCardsById;
        // _maxSquadSize is a tunable [SerializeField, Range(1,12)] — passed as a getter so
        // Inspector edits during play stay live (mirrors getGameSpeedMultiplier in ACSimulator).
        private readonly Func<int> _getMaxSquadSize;
        private readonly GameObject _battleUnitPrefab;
        private readonly HexGrid _grid;
        private readonly ACManager _resolver;
        private readonly Button _startBattleButton;
        private readonly Label _placementCountText;
        private readonly Func<HexCoord, Vector3> _coordToWorld;

        public BattleUnitController(
            Dictionary<string, BattleUnit> units,
            Dictionary<string, HexCoord> pendingPlacements,
            Dictionary<string, CombatantSnapshot> studentSnapshots,
            Dictionary<string, VisualElement> benchCardsById,
            Func<int> getMaxSquadSize,
            GameObject battleUnitPrefab,
            HexGrid grid,
            ACManager resolver,
            Button startBattleButton,
            Label placementCountText,
            Func<HexCoord, Vector3> coordToWorld)
        {
            _units = units;
            _pendingPlacements = pendingPlacements;
            _studentSnapshots = studentSnapshots;
            _benchCardsById = benchCardsById;
            _getMaxSquadSize = getMaxSquadSize;
            _battleUnitPrefab = battleUnitPrefab;
            _grid = grid;
            _resolver = resolver;
            _startBattleButton = startBattleButton;
            _placementCountText = placementCountText;
            _coordToWorld = coordToWorld;
        }

        internal void UnplaceStudent(string studentId)
        {
            if (_pendingPlacements.TryGetValue(studentId, out var coord))
            {
                _grid.ClearOccupant(coord);
                _pendingPlacements.Remove(studentId);
            }
            if (_units.TryGetValue(studentId, out var unit))
            {
                UObject.Destroy(unit.gameObject);
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
            if (!isReplacing && _pendingPlacements.Count >= _getMaxSquadSize()) return;

            // Remove existing placement if re-placing — restore card alpha first
            if (_pendingPlacements.TryGetValue(studentId, out var oldCoord))
            {
                _grid.ClearOccupant(oldCoord);
                if (_units.TryGetValue(studentId, out var oldUnit))
                {
                    UObject.Destroy(oldUnit.gameObject);
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

        // Called by the facade's OnStartBattle to spawn enemy visual units — no placement
        // dictionary or bench card involved, just Instantiate + register.
        internal void SpawnEnemyUnit(CombatantSnapshot snap, HexCoord coord)
        {
            var unit = SpawnUnit(snap, coord);
            if (unit != null) _units[snap.Id] = unit;
        }

        // Single spawn path for both teams. Appearance comes entirely from the snapshot — the
        // board no longer knows or cares what a "knight" is.
        private BattleUnit SpawnUnit(CombatantSnapshot snap, HexCoord coord)
        {
            var go = UObject.Instantiate(_battleUnitPrefab, _coordToWorld(coord), Quaternion.identity);
            var unit = go.GetComponent<BattleUnit>();
            if (unit == null)
            {
                Debug.LogError($"[BattleBoardManager] BattleUnit component missing on _battleUnitPrefab " +
                               $"(spawning '{snap.DisplayName}')", go);
                UObject.Destroy(go);
                return null;
            }

            unit.Init(snap.Id, coord);
            unit.SetVisual(snap.Icon, snap.Tint);
            unit.InitHealthBar(snap.MaxHP, snap.MaxHP);
            return unit;
        }

        internal void RefreshStartButton() =>
            _startBattleButton.SetEnabled(_pendingPlacements.Count >= 1 && _pendingPlacements.Count <= _getMaxSquadSize());

        internal void UpdatePlacementCountText()
        {
            if (_placementCountText != null)
                _placementCountText.text = $"{_pendingPlacements.Count}/{_getMaxSquadSize()} heroes placed";
        }

        // ── Event handlers ───────────────────────────────────────────────────
        internal void HandleMoved(string id, HexCoord from, HexCoord to)
        {
            if (!_units.TryGetValue(id, out var unit)) return;
            unit.MoveTo(_coordToWorld(to), to);
        }

        internal void HandleActed(string actorId, string targetId, int damage, List<string> flags)
        {
            if (_units.TryGetValue(actorId, out var actor) && _units.TryGetValue(targetId, out var target))
            {
                actor.PlayAttackAnim(target.transform.position);
                target.UpdateHP(_resolver.GetCurrentHP(targetId), _resolver.GetMaxHP(targetId));
            }
        }

        internal void HandleDefeated(string id)
        {
            if (!_units.TryGetValue(id, out var unit)) return;
            unit.PlayDeathAnim();
            _units.Remove(id);
        }
    }
}
