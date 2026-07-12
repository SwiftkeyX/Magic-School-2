using System;
using System.Collections.Generic;
using UnityEngine;

namespace MagicSchool.Battle
{
    // One synergy breakpoint: how many trait members are required (UnitCount) and the flat
    // bonus granted once that many are fielded on a team.
    [Serializable]
    public class TraitTier
    {
        public int       UnitCount;
        public StatBonus Bonus;
        [TextArea] public string Description;
    }

    // A synergy tag shared by heroes. Fielding enough heroes carrying this trait on a team
    // activates the highest satisfied tier and grants its flat StatBonus to the trait's
    // members. Authored as an asset; base game applies flat bonuses only. See Trait GDD.
    [CreateAssetMenu(menuName = "MagicSchool/Trait", fileName = "Trait")]
    public class TraitData : ScriptableObject
    {
        public string Id;
        public string DisplayName;
        [TextArea] public string Description;

        // Author in ascending UnitCount order, e.g. (2 → small buff), (4 → bigger buff).
        public List<TraitTier> Tiers = new List<TraitTier>();

        // Highest tier whose UnitCount <= count, or null when below the first breakpoint.
        public TraitTier GetActiveTier(int count)
        {
            TraitTier active = null;
            foreach (var t in Tiers)
                if (t.UnitCount <= count && (active == null || t.UnitCount > active.UnitCount))
                    active = t;
            return active;
        }
    }
}
