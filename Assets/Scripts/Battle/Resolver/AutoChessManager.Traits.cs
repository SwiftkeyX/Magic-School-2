using System.Collections.Generic;

namespace MagicSchool.Battle
{
    // The manager's trait-synergy API surface. Logic lives in Trait.cs (stateless, takes
    // AutoChessData as a parameter) -- this partial just wires it to the manager's _data.
    public partial class AutoChessManager
    {
        private void ApplyTraitBonuses() => Trait.ApplyTraitBonuses(_data);

        // Read-only active-trait readout for a future HUD synergy panel. Not used in combat.
        public List<(TraitDataSO trait, int count, TraitBreakpoint active)> GetActiveTraits(Team team) =>
            Trait.GetActiveTraits(_data, team);
    }
}
