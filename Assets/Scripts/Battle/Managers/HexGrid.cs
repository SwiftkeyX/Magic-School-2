using System.Collections.Generic;
using UnityEngine;

namespace MagicSchool.Battle
{
    // Board occupancy + pathfinding.
    //
    // Board dimensions were `const` before the editability pass, which meant the board could not
    // be resized without a recompile. They are now serialized instance fields, so every consumer
    // must reach them through a HexGrid instance — there is no static board size any more.
    public class HexGrid : MonoBehaviour
    {
        [SerializeField, Range(3, 16), Tooltip("Board width in hexes.")]
        private int _cols = 7;

        [SerializeField, Range(4, 16), Tooltip("Board height in hexes. Split evenly-ish between the two sides.")]
        private int _rows = 8;

        [SerializeField, Range(1, 15), Tooltip("How many rows (from row 0 up) belong to the player. The rest are the enemy's.")]
        private int _playerRowCount = 4;

        public int Cols           => _cols;
        public int Rows           => _rows;
        public int PlayerRowCount => _playerRowCount;

        private readonly Dictionary<HexCoord, string> _occupants = new Dictionary<HexCoord, string>();

        // The player's half must leave at least one row for the enemy, or enemies would be
        // auto-placed off the board and never reachable.
        private void OnValidate()
        {
            _playerRowCount = Mathf.Clamp(_playerRowCount, 1, Mathf.Max(1, _rows - 1));
        }

        public bool IsOccupied(HexCoord coord) => _occupants.ContainsKey(coord);

        public string GetOccupantId(HexCoord coord) =>
            _occupants.TryGetValue(coord, out string id) ? id : null;

        public void SetOccupant(HexCoord coord, string unitId)
        {
            if (unitId == null)
                _occupants.Remove(coord);
            else
                _occupants[coord] = unitId;
        }

        public void ClearOccupant(HexCoord coord) => _occupants.Remove(coord);

        public void Clear() => _occupants.Clear();

        // BFS: returns the next step from `from` toward `to`, skipping occupied cells.
        // Returns null if no path exists or destination is already occupied.
        public HexCoord? GetNextStep(HexCoord from, HexCoord to, string moverId)
        {
            if (from == to) return null;

            var visited = new HashSet<HexCoord> { from };
            var queue = new Queue<(HexCoord coord, HexCoord firstStep)>();

            foreach (HexCoord neighbor in HexCoord.GetNeighbors(from, _cols, _rows))
            {
                // A unit may move through occupied cells only if the occupant is the mover itself.
                string occupant = GetOccupantId(neighbor);
                if (occupant != null && occupant != moverId && neighbor != to) continue;
                if (visited.Contains(neighbor)) continue;
                visited.Add(neighbor);
                queue.Enqueue((neighbor, neighbor));
            }

            while (queue.Count > 0)
            {
                var (current, firstStep) = queue.Dequeue();
                if (current == to) return firstStep;

                foreach (HexCoord neighbor in HexCoord.GetNeighbors(current, _cols, _rows))
                {
                    if (visited.Contains(neighbor)) continue;
                    string occupant = GetOccupantId(neighbor);
                    if (occupant != null && occupant != moverId && neighbor != to) continue;
                    visited.Add(neighbor);
                    queue.Enqueue((neighbor, firstStep));
                }
            }

            return null;
        }

        // Finds the coord (among candidates) closest to `from` by hex distance.
        public HexCoord? FindNearest(HexCoord from, IEnumerable<HexCoord> candidates)
        {
            HexCoord? best = null;
            int bestDist = int.MaxValue;
            foreach (HexCoord c in candidates)
            {
                int d = HexCoord.Distance(from, c);
                if (d < bestDist)
                {
                    bestDist = d;
                    best = c;
                }
            }
            return best;
        }

        // removed: GetInRange, GetLinearPath, CubeRound, FindLargestClusterCenter — scaffolding for
        // a targeting system (Linear Path / Largest Cluster filters) that does not exist. No caller.
    }
}
