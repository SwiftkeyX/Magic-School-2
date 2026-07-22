using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;
using UObject = UnityEngine.Object;

namespace MagicSchool.Battle
{
    // Owns board tile construction (BuildBoard) and bench card construction (BuildBench).
    // Shared state dictionaries (_tiles, _benchCardsById) are owned by the facade and passed
    // by reference so mutations here are visible to BattlePlacementController and BattleUnitController
    // — same pattern as ACSetup populating ACData.Combatants (Combat.md Interactions table).
    internal class BattleBoardBuilder
    {
        private readonly HexGrid _grid;
        private readonly GameObject _hexTilePrefab;
        private readonly float _hexWidth;             // used once in BuildBoard for tile visual scale
        private readonly Func<HexCoord, Vector3> _coordToWorld;
        private readonly Transform _parent;
        // BenchCardDragManipulator's constructor requires a direct BattleBoardManager reference
        // (see BenchCardDragManipulator.cs) — the one necessary exception to the
        // Action/Func-callback pattern.
        private readonly BattleBoardManager _board;
        private readonly Dictionary<HexCoord, HexTileView> _tiles;
        private readonly Dictionary<string, VisualElement> _benchCardsById;
        private readonly VisualElement _benchContainer;

        public BattleBoardBuilder(
            HexGrid grid,
            GameObject hexTilePrefab,
            float hexWidth,
            Func<HexCoord, Vector3> coordToWorld,
            Transform parent,
            BattleBoardManager board,
            Dictionary<HexCoord, HexTileView> tiles,
            Dictionary<string, VisualElement> benchCardsById,
            VisualElement benchContainer)
        {
            _grid = grid;
            _hexTilePrefab = hexTilePrefab;
            _hexWidth = hexWidth;
            _coordToWorld = coordToWorld;
            _parent = parent;
            _board = board;
            _tiles = tiles;
            _benchCardsById = benchCardsById;
            _benchContainer = benchContainer;
        }

        internal void BuildBoard()
        {
            var hexSprite = HexSpriteGenerator.GetHexSprite();

            // Full visual height of a pointy-top hex whose centre-to-centre column width = _hexWidth
            float hexVisualHeight = _hexWidth * 2f / Mathf.Sqrt(3f);
            var scale = new Vector3(_hexWidth, hexVisualHeight, 1f);

            for (int row = 0; row < _grid.Rows; row++)
                for (int col = 0; col < _grid.Cols; col++)
                {
                    var coord = new HexCoord(col, row);
                    var go = UObject.Instantiate(_hexTilePrefab, _coordToWorld(coord), Quaternion.identity, _parent);
                    go.transform.localScale = scale;
                    var sr = go.GetComponent<SpriteRenderer>();
                    if (sr != null) sr.sprite = hexSprite;
                    var view = go.GetComponent<HexTileView>();
                    // Player-side is a property of the board, not of the tile — pass it in rather than
                    // letting the tile reach for a static board constant.
                    view.Init(coord, _grid.PlayerRowCount);
                    _tiles[coord] = view;
                }
        }

        internal void BuildBench(List<CombatantSnapshot> students)
        {
            _benchContainer.Clear();
            _benchCardsById.Clear();

            foreach (var s in students)
            {
                var card = new VisualElement();
                card.name = $"Card_{s.Id}";
                card.AddToClassList("bench-card");
                card.style.backgroundColor = new StyleColor(s.Tint);   // authored on the asset

                var label = new Label(s.DisplayName);
                label.AddToClassList("bench-card-label");
                card.Add(label);

                card.AddManipulator(new BenchCardDragManipulator(_board, s.Id));

                _benchContainer.Add(card);
                _benchCardsById[s.Id] = card;
            }
        }
    }
}
