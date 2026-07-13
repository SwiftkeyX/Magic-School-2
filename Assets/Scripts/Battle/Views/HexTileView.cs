using UnityEngine;

namespace MagicSchool.Battle
{
    public class HexTileView : MonoBehaviour
    {
        [Header("Tile Colors")]
        [SerializeField] private Color _playerColor = new Color(0.25f, 0.45f, 0.75f, 0.85f);
        [SerializeField] private Color _enemyColor  = new Color(0.75f, 0.25f, 0.25f, 0.85f);
        [SerializeField] private Color _highlightOn = new Color(0.9f,  0.85f, 0.3f,  1.0f);
        [SerializeField] private Color _hoverColor  = new Color(1.0f,  1.0f,  0.55f, 1.0f);

        public HexCoord Coord { get; private set; }
        public bool IsPlayerSide { get; private set; }

        private SpriteRenderer _sprite;
        private Color _baseColor;
        private bool  _isHighlighted;

        // Player-side is a property of the board's layout, not of the tile — it is passed in by
        // BattleBoardManager rather than read from a static board constant, so the board can be
        // resized from the HexGrid Inspector without recompiling.
        public void Init(HexCoord coord, int playerRowCount)
        {
            Coord        = coord;
            IsPlayerSide = coord.Row < playerRowCount;

            _sprite    = GetComponent<SpriteRenderer>();
            _baseColor = IsPlayerSide ? _playerColor : _enemyColor;
            if (_sprite != null) _sprite.color = _baseColor;
            gameObject.name = $"Tile({coord.Col},{coord.Row})";
        }

        public void SetHighlight(bool active)
        {
            if (_sprite == null) return;
            _isHighlighted = active;
            _sprite.color = active ? _highlightOn : _baseColor;
        }

        public void SetHover(bool active)
        {
            if (_sprite == null || !_isHighlighted) return;
            _sprite.color = active ? _hoverColor : _highlightOn;
        }
    }
}
