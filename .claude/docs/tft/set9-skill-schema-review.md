# TFT Set9-Skill — Schema Review: what the simplification broke

Comparison of the **old (intended)** vs the **simplified (second)** skill-analysis schema in the `tft-set9-skill` sheet ("TFT Set9 Skill Research"), and a ranked list of what the simplification broke. Source is the Google Sheet in [tft-reference-sheets.md](tft-reference-sheets.md), read via the project's `google-service-credential.json` service account.

The sheet has **4 tabs**:

| Tab | id (gid) | Role |
|---|---|---|
| `Hero (old)` | 0 | Original **intended** model (28-col wide) |
| `Skill Analysis Column Explain (old)` | 1863060106 | Column doc for the old model |
| `Hero` | 1893725546 | **Simplified** second version (16-col long) |
| `Skill Analysis Column Explain` | 1276903414 | Column doc for the new model |

## A. The two schemas

**Old — wide "Parts" model (28 cols).** Per champion, up to **3 Skill-Analysis Parts**. Each Part = one `Skill` cell encoding `[Skill Type], [Condition], [Skill Archetype], [Target Type]`, plus up to two `Effect` cells encoding `[Effect Type], [Apply Time]`. Traits split across `Origin 1/2` and `Class 1/2`. Abbreviations: targets `CT/FT/GFT/CLET/SF`; apply-time `st/ot/perm`.

Example (Kayle, old): `Passive, [Player lvl < 3], Auto Attack, CT` → `Attack, st` … `Passive, [lvl<7 && 3rd auto], Wave AOE, CT` → `Attack, st` + `Debuff [Shred: MR], ot`.

**New — long "one row per effect" model (16 cols).** `Step | Trigger | Action | Target | Effect | Duration | AOE | Cast`. The column doc defines a row as: *"[Trigger], the [Action] hits [Target], applying [Effect] for [Duration]."* Traits merged into single comma-strings; abbreviations spelled out (Once/Over Time/Perm, Current/Clustered/Self).

## B. Findings — what broke (ranked)

### 1. Conflated *aim-target* with *effect-recipient* — the core defect
The old model **deliberately** separated two concepts, and its column doc says so twice:
- *"Skill archetype specifies who the effect was applied to, NOT [Target Type]."*
- *"[Target Type] = the target the skill is aiming at. This does not specify who the effect is applied to."*

The new schema merges both into a single `Target` column and reads a row as *"the Action hits Target, applying Effect."* Result: every self-centered AOE now reads as **self-harm**, and effect-recipient info survives only implicitly inside the Action verb.

| Champion | New row reads as… | Actually |
|---|---|---|
| Garen | "Circle AOE hits **Self** → Damage (Over Time)" | Damages **enemies** around him |
| Galio | "Circle AOE hits **Self** → Damage" | Damages **enemies** around him |
| Jarvan / Katarina / Sion / Swain | "Circle AOE hits **Self** → Damage / Stun / Wound" | Hits **enemies** in the area |
| Sona (ally-hit row) | "Wave hits **Clustered** [enemy] → Buff AS" | Buffs **allies** the wave passed |

This is the main thing the simplification lost.

### 2. Archetype collision-granularity flattened
The old model had **5** delivery archetypes that encoded *collision behavior*:

| Old archetype | Collision behavior | New collapses to |
|---|---|---|
| Standard Projectile | hits first target collided | `Projectile` |
| Standard Laser | pierces all; damages continuously (over time) until it ends | `Laser` |
| Laser Shot | pierces all; damages once | `Laser` |
| Current Target Laser | only the aimed target, over time | `Laser` |
| Wave AOE | passes through, hits all in path | `Wave` |

Note the two piercing lasers differ only by **damage cadence** (Standard Laser = continuous over time; Laser Shot = once), not by how many they hit. New keeps only `Projectile` + `Laser`, so collapsing them erases **both** distinctions at once: *who* the beam hits (Lux's `Current Target Laser` = target-only vs a piercing beam) **and** *how* it damages (continuous vs once).

### 3. "Apply Time" → "Duration" rename mislabels the column
Old `Apply Time` values `st/ot/perm` describe *re-application cadence*. New renamed the column to **Duration** but kept cadence values (Once / Over Time / Perm). Real effect *lengths* then had nowhere to go and were pushed into Effect free-text, e.g. `Shred MR (20%, 3s)`. The header now lies about its data: "Duration = Once" is not a duration.

### 4. `Trigger` overloads three axes the old model kept separate
One new column now encodes three orthogonal things that were distinct fields/conventions in the old model:
- **Skill type:** Active / Passive
- **Lifecycle sequencing:** After Cast / After Leap / On Kill / On Death
- **Gating condition:** Game Start / Bonus HP Expired / If Already Transformed / Lvl ranges / If Ally Hit

Old kept Skill Type as its own concept and put conditions in `[brackets]`.

### 5. Silent value drift (correctness smell)
The simplification didn't just reshape — it **changed data**. Kayle's 3rd-attack-wave breakpoint is `lvl < 7` in old but `Lvl 6-8` in new. The two versions now disagree on the actual design, and the change is undocumented.

### 6. Minor regressions
- `Origin 1/2` and `Class 1/2` merged into comma-strings → no longer filterable per single trait.
- Effect magnitudes modeled inconsistently: some inline in Effect parens (`(+30%)`, `(stacking)`, `(decaying)`), others omitted entirely.

## C. Recommendation

If a schema is rebuilt (including for this game's own model in `Assets/Scripts/Battle/Data/BattleData.cs`):

1. **Restore two distinct fields:** `AimTarget` (who the skill points at) and `EffectRecipient` (who the effect lands on) — or derive recipients from an explicit archetype collision-type. Never let a single "Target" imply both.
2. **Keep archetype collision-type** (first-hit / pierce / area / self-centered / target-only) as structured data, not baked into a verb.
3. **Split cadence vs length:** one field for application cadence (Once/Over-Time/Perm) and a separate numeric field for how long an effect lasts (e.g. Shred 3s).
4. **Split `Trigger`** into `SkillType` (Active/Passive), `Lifecycle` (sequence event), and `Condition` (gate).
5. Keep magnitudes and trait slots as their own structured columns, not free-text.

## D. Realized fix

These recommendations are implemented in the sheet as a corrected tab: **`Hero (corrected)`** (gid 930376992), with a **`Column Explain (corrected)`** legend (gid 1026992711). It re-encodes all 14 champions in a one-row-per-effect layout that restores the lost distinctions:

- Separate `Aim Target` and `Effect Recipient` columns (highlighted) — self-centered AOEs now read "Circle AOE, Aim Self, **Recipient = Enemies in area**"; Sona's ally row reads "Aim Clustered, **Recipient = Allies in path**".
- `Action` keeps distinct archetypes (e.g. Lux stays `Current Target Laser`, Target-Only) plus an explicit `Collision` column.
- `Cadence` (Once/Over Time/Perm) split from numeric `Duration (s)` (e.g. Kayle/Lux shred = 3).
- `Trigger` split into `Skill Type` / `Trigger (When)` / `Condition (Only if)`; traits un-merged into `Origin 1/2` + `Class 1/2`.
- **Kayle** breakpoints corrected to the prose gates (Lvl 1-5 / Lvl 6-8 / Lvl 9+), resolving the finding-#5 value drift.

Refined after user review (sheet comments):
- Effect split into `Effect Category` (Attack / Status / Buff / Debuff / Movement) + `Effect Detail`, per the user's preferred taxonomy (Status = Stun/Slow/Silence/Wound; Buff = stat boost; Debuff = stat deboost).
- Magnitude split into `Amount` (how much) + `Scaling` (how it behaves: stacking / decaying / falls-off / amplified-if-Wounded / burst).
- Rows of one attack share a `Step` and their action-instance cells are **vertically merged**, so multiple effects visibly belong to the same action (e.g. Kayle's `Wave` merged across its Damage + MR-shred rows).
- Two reference tabs added: **`Action Types`** (each delivery archetype + collision behaviour) and **`Effect Types`** (each Effect Category → Detail with a definition). `Amount` clarified to mean the size of *that row's* effect.
