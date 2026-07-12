using UnityEngine;

namespace MagicSchool.Battle
{
    /// <summary>
    /// Pure static sprite-generation utilities for the battle hex board.
    /// No dependency on scene state or MonoBehaviour lifecycle — extracted from
    /// BattleBoardManager (M1a) so geometry/rendering math has a single home.
    /// </summary>
    internal static class HexSpriteGenerator
    {
        private static Sprite _hexSprite;
        private static Sprite _fallbackSprite;

        /// <summary>
        /// Returns a cached pointy-top hex sprite (128 px, dark border ring, white body).
        /// Body colour is tinted at display time via SpriteRenderer.color.
        /// </summary>
        public static Sprite GetHexSprite()
        {
            if (_hexSprite != null) return _hexSprite;

            const int size   = 128;
            const int border = 5;

            float cx   = (size - 1) / 2f;
            float cy   = (size - 1) / 2f;
            float rOut = cx - 1f;
            float rIn  = rOut - border;

            var outer  = HexVerts(cx, cy, rOut);
            var inner  = HexVerts(cx, cy, rIn);
            var pixels = new Color32[size * size];

            for (int y = 0; y < size; y++)
            for (int x = 0; x < size; x++)
            {
                var p = new Vector2(x, y);
                if (PointInHex(p, outer))
                    pixels[y * size + x] = PointInHex(p, inner)
                        ? new Color32(255, 255, 255, 255)   // body (tinted by SpriteRenderer.color)
                        : new Color32(15,  15,  15,  220);  // border ring
                // else stays default Color32(0,0,0,0) — transparent
            }

            var tex = new Texture2D(size, size, TextureFormat.RGBA32, false);
            tex.filterMode = FilterMode.Bilinear;
            tex.SetPixels32(pixels);
            tex.Apply();

            _hexSprite = Sprite.Create(tex, new Rect(0, 0, size, size), new Vector2(0.5f, 0.5f), size);
            return _hexSprite;
        }

        /// <summary>
        /// Returns a cached 32x32 plain white square sprite used as a drag-ghost fallback
        /// when a bench card has no dedicated sprite.
        /// </summary>
        public static Sprite GetFallbackSprite()
        {
            if (_fallbackSprite != null) return _fallbackSprite;
            var tex    = new Texture2D(32, 32, TextureFormat.RGBA32, false);
            var pixels = new Color32[32 * 32];
            for (int i = 0; i < pixels.Length; i++) pixels[i] = new Color32(255, 255, 255, 255);
            tex.SetPixels32(pixels);
            tex.Apply();
            tex.filterMode = FilterMode.Point;
            _fallbackSprite = Sprite.Create(tex, new Rect(0, 0, 32, 32), new Vector2(0.5f, 0.5f), 32f);
            return _fallbackSprite;
        }

        // ── Private geometry helpers ─────────────────────────────────────────

        private static Vector2[] HexVerts(float cx, float cy, float r)
        {
            var v = new Vector2[6];
            for (int i = 0; i < 6; i++)
            {
                float rad = (90f - 60f * i) * Mathf.Deg2Rad; // pointy-top: first vertex at 12 o'clock
                v[i] = new Vector2(cx + r * Mathf.Cos(rad), cy + r * Mathf.Sin(rad));
            }
            return v;
        }

        private static bool PointInHex(Vector2 p, Vector2[] verts)
        {
            for (int i = 0; i < verts.Length; i++)
            {
                Vector2 a = verts[i];
                Vector2 b = verts[(i + 1) % verts.Length];
                // Vertices are CW, so interior points have cross < 0; exclude when > 0.
                if ((b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x) > 0)
                    return false;
            }
            return true;
        }
    }
}
