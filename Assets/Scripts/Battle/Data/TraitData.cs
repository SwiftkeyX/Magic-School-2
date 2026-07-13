using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Serialization;

namespace MagicSchool.Battle
{
    // One synergy breakpoint: how many trait members are required (UnitCount) and the flat
    // bonus granted once that many are fielded on a team.
    [Serializable]
    public class TraitBreakpoint
    {
        public int UnitCount;
        public StatBonus Bonus;
        [TextArea] public string Description;
    }

    // A synergy tag shared by heroes. Fielding enough heroes carrying this trait on a team
    // activates the highest satisfied breakpoint and grants its flat StatBonus to the trait's
    // members. Authored as an asset; base game applies flat bonuses only. See Trait GDD.
    [CreateAssetMenu(menuName = "MagicSchool/Trait", fileName = "Trait")]
    public class TraitData : ScriptableObject
    {
        public string Id;
        public string DisplayName;
        [TextArea] public string Description;

        // Author in ascending UnitCount order, e.g. (2 → small buff), (4 → bigger buff).
        // FormerlySerializedAs keeps assets authored as `Tiers` loading after the rename —
        // without it they deserialize to an empty list and the trait silently grants nothing.
        [FormerlySerializedAs("Tiers")]
        public List<TraitBreakpoint> Breakpoints = new List<TraitBreakpoint>();

        // Highest breakpoint whose UnitCount <= count, or null when below the first breakpoint.
        public TraitBreakpoint GetActiveBreakpoint(int count)
        {
            TraitBreakpoint active = null;
            foreach (var b in Breakpoints)
                if (b.UnitCount <= count && (active == null || b.UnitCount > active.UnitCount))
                    active = b;
            return active;
        }
    }
}
