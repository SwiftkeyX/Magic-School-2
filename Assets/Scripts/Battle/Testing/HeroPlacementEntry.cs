using System;

namespace MagicSchool.Battle
{
    // One authored unit: which Hero, and the hex it starts the battle standing on (its default
    // formation position, used when nothing overrides it). Pairing these on one entry (rather
    // than parallel HeroDataSO/HexCoord lists) is what makes the Inspector list keep reordering
    // safe -- a list of pairs can't desync into "hero N with position M" the way two separately-
    // reordered lists could. Shared by StudentRosterStub and EnemyDatabaseStub -- both sides
    // author a default formation the same way.
    [Serializable]
    public class HeroPlacementEntry
    {
        public HeroDataSO Hero;
        public HexCoord Position;
    }
}
