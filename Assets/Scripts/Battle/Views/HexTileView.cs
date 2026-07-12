using UnityEngine;

namespace MagicSchool.Battle
{
    public class HexTileView : MonoBehaviour
    {
        public HexCoord Coord { get; private set; }
        public bool IsPlayerSide => Coord.Row < HexGrid.PlayerRowCount;

        private SpriteRenderer _sprite;
        private Color _baseColor;

        private static readonly Color PlayerColor  = new Color(0.25f, 0.45f, 0.75f, 0.85f);
        private static readonly Color EnemyColor   = new Color(0.75f, 0.25f, 0.25f, 0.85f);
        private static readonly Color HighlightOn  = new Color(0.9f,  0.85f, 0.3f,  1.0f);
        private static readonly Color HoverColor   = new Color(1.0f,  1.0f,  0.55f, 1.0f);

        private bool _isHighlighted;

        public void Init(HexCoord coord)
        {
            Coord = coord;
            _sprite = GetComponent<SpriteRenderer>();
            _baseColor = IsPlayerSide ? PlayerColor : EnemyColor;
            if (_sprite != null) _sprite.color = _baseColor;
            gameObject.name = $"Tile({coord.Col},{coord.Row})";
        }

        public void SetHighlight(bool active)
        {
            if (_sprite == null) return;
            _isHighlighted = active;
            _sprite.color = active ? HighlightOn : _baseColor;
        }

        public void SetHover(bool active)
        {
            if (_sprite == null || !_isHighlighted) return;
            _sprite.color = active ? HoverColor : HighlightOn;
        }
    }
}
