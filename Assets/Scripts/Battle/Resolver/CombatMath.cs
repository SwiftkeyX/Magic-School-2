using System;

namespace MagicSchool.Battle
{
    // Shared damage-mitigation math, consolidated here so it can't drift between call sites.
    public static class CombatMath
    {
        // The denominator constant in the LoL/TFT-style mitigation curve:
        //
        //     mitigated = offense × K / (K + defense)
        //
        // K is the defense value at which incoming damage is halved. At K = 100, a unit with
        // 100 DEF takes 50% damage; with 50 DEF, 67%. Raising K makes defense weaker across the
        // board; lowering it makes every point of DEF matter more. This is the single most
        // load-bearing balance number in the game — it was previously an unnamed literal `100f`
        // buried in the expression below.
        public const float MitigationConstant = 100f;

        // Damage always lands for at least 1, so a high-DEF unit can never be literally
        // unkillable by a low-ATK one (which would stall the battle to its tick cap).
        public static int ApplyMitigation(float rawOffense, int rawDefense)
        {
            float mitigated = rawOffense * (MitigationConstant / (MitigationConstant + rawDefense));
            return Math.Max(1, (int)mitigated);
        }
    }
}
