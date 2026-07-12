using System;

namespace MagicSchool.Battle
{
    // Shared damage-mitigation math (core LoL-style mitigation formula), consolidated
    // here so it can't drift between call sites.
    public static class CombatMath
    {
        public static int ApplyMitigation(float rawOffense, int rawDefense)
        {
            return Math.Max(1, (int)(rawOffense * (100f / (100 + rawDefense))));
        }
    }
}
