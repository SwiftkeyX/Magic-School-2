using System.Collections.Generic;
using System.Linq;
using UnityEngine.UIElements;

namespace MagicSchool.Battle
{
    // Owns the left-side active-trait panel. Rebuilds it from the player's fielded synergies.
    // Active traits (a breakpoint is met) render highlighted; others are dimmed. See Trait.md.
    internal class BattleTraitPanel
    {
        private readonly VisualElement _traitList;
        private readonly ACManager _resolver;

        public BattleTraitPanel(VisualElement traitList, ACManager resolver)
        {
            _traitList = traitList;
            _resolver = resolver;
        }

        // Rebuilds the left trait list from the player's fielded synergies. Active traits
        // (a breakpoint is met) render highlighted; others are dimmed. See Trait.md.
        internal void Refresh()
        {
            if (_traitList == null) return;
            _traitList.Clear();

            var traits = _resolver.GetActiveTraits(Team.Player)
                .OrderByDescending(t => t.active != null)
                .ThenByDescending(t => t.count)
                .ToList();

            foreach (var (trait, count, active) in traits)
            {
                if (trait == null) continue;
                bool isActive = active != null;

                var row = new VisualElement();
                row.AddToClassList("trait-row");
                row.AddToClassList(isActive ? "trait-row-active" : "trait-row-inactive");

                var nameLabel = new Label(trait.DisplayName);
                nameLabel.AddToClassList("trait-name");
                if (!isActive) nameLabel.AddToClassList("trait-name-inactive");
                row.Add(nameLabel);

                int target = isActive
                    ? active.UnitCount
                    : (trait.Breakpoints != null && trait.Breakpoints.Count > 0 ? trait.Breakpoints.Min(b => b.UnitCount) : count);
                var countLabel = new Label($"{count}/{target}");
                countLabel.AddToClassList("trait-count");
                row.Add(countLabel);

                _traitList.Add(row);
            }
        }
    }
}
