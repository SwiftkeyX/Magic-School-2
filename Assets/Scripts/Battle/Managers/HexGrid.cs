using System;
using System.Collections.Generic;
using UnityEngine;

namespace MagicSchool.Battle
{
    public class HexGrid : MonoBehaviour
    {
        public const int Cols = 7;
        public const int Rows = 8;          // 0-3 player, 4-7 enemy
        public const int PlayerRowCount = 4;

        private readonly Dictionary<HexCoord, string> _occupants = new Dictionary<HexCoord, string>();

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

        // Returns all coords within hex distance <= range of center, within bounds.
        public List<HexCoord> GetInRange(HexCoord center, int range)
        {
            var result = new List<HexCoord>();
            for (int col = 0; col < Cols; col++)
            {
                for (int row = 0; row < Rows; row++)
                {
                    var coord = new HexCoord(col, row);
                    if (HexCoord.Distance(center, coord) <= range)
                        result.Add(coord);
                }
            }
            return result;
        }

        // BFS: returns the next step from `from` toward `to`, skipping occupied cells.
        // Returns null if no path exists or destination is already occupied.
        public HexCoord? GetNextStep(HexCoord from, HexCoord to, string moverId)
        {
            if (from == to) return null;

            var visited = new HashSet<HexCoord> { from };
            var queue = new Queue<(HexCoord coord, HexCoord firstStep)>();

            foreach (HexCoord neighbor in HexCoord.GetNeighbors(from, Cols, Rows))
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

                foreach (HexCoord neighbor in HexCoord.GetNeighbors(current, Cols, Rows))
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

        // Hexes intersected by a line from `origin` through `through`, extended to
        // the board edge or `maxRange` steps (whichever comes first). Used by the
        // Linear Path targeting filter (Laser/Piercing Beam archetype).
        public List<HexCoord> GetLinearPath(HexCoord origin, HexCoord through, int maxRange)
        {
            var result = new List<HexCoord>();
            HexCoord.ToCube(origin, out int ox, out int oy, out int oz);
            HexCoord.ToCube(through, out int tx, out int ty, out int tz);

            int n = HexCoord.Distance(origin, through);
            if (n == 0) return result;

            for (int step = 1; step <= maxRange; step++)
            {
                double t = (double)step / n;
                double cx = ox + (tx - ox) * t;
                double cy = oy + (ty - oy) * t;
                double cz = oz + (tz - oz) * t;

                HexCoord hex = CubeRound(cx, cy, cz);
                if (hex.Col < 0 || hex.Col >= Cols || hex.Row < 0 || hex.Row >= Rows)
                    break;

                if (result.Count == 0 || result[result.Count - 1] != hex)
                    result.Add(hex);
            }
            return result;
        }

        private static HexCoord CubeRound(double x, double y, double z)
        {
            int rx = (int)Math.Round(x);
            int ry = (int)Math.Round(y);
            int rz = (int)Math.Round(z);

            double xDiff = Math.Abs(rx - x);
            double yDiff = Math.Abs(ry - y);
            double zDiff = Math.Abs(rz - z);

            if (xDiff > yDiff && xDiff > zDiff)
                rx = -ry - rz;
            else if (yDiff > zDiff)
                ry = -rx - rz;
            else
                rz = -rx - ry;

            return HexCoord.FromCube(rx, ry, rz);
        }

        // Among `candidates`, finds the hex whose radius-C neighborhood contains the
        // most `enemyPositions`. Used by the Largest Cluster targeting sort.
        public HexCoord? FindLargestClusterCenter(IEnumerable<HexCoord> candidates, IEnumerable<HexCoord> enemyPositions, int radius)
        {
            var enemyList = new List<HexCoord>(enemyPositions);
            HexCoord? best = null;
            int bestCount = -1;
            foreach (HexCoord candidate in candidates)
            {
                int count = 0;
                foreach (HexCoord enemy in enemyList)
                {
                    if (HexCoord.Distance(candidate, enemy) <= radius)
                        count++;
                }
                if (count > bestCount)
                {
                    bestCount = count;
                    best = candidate;
                }
            }
            return best;
        }
    }
}
