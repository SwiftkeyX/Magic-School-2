using System;
using System.Collections.Generic;

namespace MagicSchool.Battle
{
    [Serializable]
    public struct HexCoord : IEquatable<HexCoord>
    {
        public int Col;
        public int Row;

        public HexCoord(int col, int row)
        {
            Col = col;
            Row = row;
        }

        // ── Adjacency (offset-row hex grid) ──────────────────────────────
        // Even rows: offset tiles are to the right; odd rows: offset to the left.
        // Layout matches the reference image (odd rows shifted right by half a tile).
        private static readonly HexCoord[] _evenRowNeighborOffsets =
        {
            new HexCoord( 1,  0), new HexCoord(-1,  0),   // right, left
            new HexCoord( 0,  1), new HexCoord( 0, -1),   // up-right, down-right
            new HexCoord(-1,  1), new HexCoord(-1, -1),   // up-left, down-left
        };

        private static readonly HexCoord[] _oddRowNeighborOffsets =
        {
            new HexCoord( 1,  0), new HexCoord(-1,  0),
            new HexCoord( 1,  1), new HexCoord( 1, -1),
            new HexCoord( 0,  1), new HexCoord( 0, -1),
        };

        // Bounds are passed in rather than defaulted: the board is now sized on the HexGrid
        // component, so a compile-time default here would be a second, silently-stale source
        // of truth for the board dimensions.
        public static IEnumerable<HexCoord> GetNeighbors(HexCoord coord, int cols, int rows)
        {
            HexCoord[] offsets = (coord.Row % 2 == 0) ? _evenRowNeighborOffsets : _oddRowNeighborOffsets;
            foreach (HexCoord offset in offsets)
            {
                int nc = coord.Col + offset.Col;
                int nr = coord.Row + offset.Row;
                if (nc >= 0 && nc < cols && nr >= 0 && nr < rows)
                    yield return new HexCoord(nc, nr);
            }
        }

        // Cube-coordinate distance for offset hex grids.
        public static int Distance(HexCoord a, HexCoord b)
        {
            int ac, ar, bc, br;
            OffsetToCube(a, out ac, out ar);
            OffsetToCube(b, out bc, out br);
            int dx = ac - bc;
            int dy = ar - br;
            return Math.Max(Math.Abs(dx), Math.Max(Math.Abs(dy), Math.Abs(dx + dy)));
        }

        // Converts offset-row hex coord to cube coordinates (x, z; y = -x-z).
        private static void OffsetToCube(HexCoord h, out int x, out int z)
        {
            x = h.Col - (h.Row - (h.Row & 1)) / 2;
            z = h.Row;
        }

        // ── Equality ──────────────────────────────────────────────────────
        public bool Equals(HexCoord other) => Col == other.Col && Row == other.Row;
        public override bool Equals(object obj) => obj is HexCoord h && Equals(h);
        public override int GetHashCode() => Col * 31 + Row;
        public static bool operator ==(HexCoord a, HexCoord b) => a.Equals(b);
        public static bool operator !=(HexCoord a, HexCoord b) => !a.Equals(b);
        public override string ToString() => $"({Col},{Row})";
    }
}
