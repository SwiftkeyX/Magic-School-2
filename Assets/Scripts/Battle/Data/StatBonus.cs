using System;

namespace MagicSchool.Battle
{
    // Flat additive stat deltas granted by an active trait tier. No percentages and no
    // active effects — the base-game Trait system applies only flat bonuses (see Trait GDD).
    [Serializable]
    public struct StatBonus
    {
        public int   HP;
        public int   ATK;
        public int   DEF;
        public int   MG;
        public int   MR;
        public float AttackSpeed;

        // Applies this bonus additively to a runtime combatant. An HP increase also raises
        // CurrentHP by the same delta so the unit starts at full effective HP.
        // internal: HeroDataRuntime is internal, so this method cannot be public (CS0051).
        internal void ApplyTo(HeroDataRuntime c)
        {
            c.MaxHP       += HP;
            c.CurrentHP   += HP;
            c.ATK         += ATK;
            c.DEF         += DEF;
            c.MG          += MG;
            c.MR          += MR;
            c.AttackSpeed += AttackSpeed;
        }
    }
}
