using System.Collections.Generic;
using System.Linq;

namespace MagicSchool.Battle
{
    // Shared by StudentRosterStub and EnemyDatabaseStub -- both are otherwise identical
    // (a List<HeroPlacementEntry> projected to HeroDataSeed/HexCoord), differing only in which
    // Team they stamp and which field holds their entries. Stateless, mirrors
    // AutoChessHelper/Trait/HeroDataSeedFactory's pattern.
    internal static class RosterStubHelper
    {
        public static List<HeroDataSeed> GetUnits(List<HeroPlacementEntry> entries, Team team) =>
            entries.Where(e => e.Hero != null).Select(e => HeroDataSeedFactory.ToCombatData(e.Hero, team)).ToList();

        // Parallel to GetUnits() -- same filter, same order -- so callers can zip the two by index.
        public static List<HexCoord> GetPlacements(List<HeroPlacementEntry> entries) =>
            entries.Where(e => e.Hero != null).Select(e => e.Position).ToList();
    }
}
