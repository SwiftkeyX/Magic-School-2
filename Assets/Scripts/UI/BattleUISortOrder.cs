namespace MagicSchool.Battle
{
    // Explicit UIDocument.sortingOrder values for every UI Toolkit panel sharing
    // Assets/UI/BattleHUDPanelSettings.asset in the Battle scene. All migrated
    // panels reference the same PanelSettings so they composite as one surface
    // (see ADR-001) — this class exists so relative order is a documented
    // decision, not an implicit default-zero-for-everyone tie.
    public static class BattleUISortOrder
    {
        // removed: HeroInfoPanel, TraitHUD constants — champion/trait system, rebuilding fresh
        public const int BoardBenchHUD = 0;
        public const int BattleHUD = 10; // hosts the modal outcome overlay — must stay topmost
    }
}
