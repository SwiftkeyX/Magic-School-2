using System;

namespace MagicSchool.Battle
{
    // Decouples hero-click sources (BenchCardDrag, BattleUnit) from listeners (HeroInfoPanel)
    // so presentation components never hold direct references to each other.
    public static class HeroSelection
    {
        public static event Action<string> OnHeroSelected;

        public static void Select(string championId) => OnHeroSelected?.Invoke(championId);
    }
}
