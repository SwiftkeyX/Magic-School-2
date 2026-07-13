# TFT Set9-Skill — Schema Review: what the simplification broke

Comparison of the **old (intended)** vs the **simplified (second)** skill-analysis schema in the `tft-set9-skill` sheet ("TFT Set9 Skill Research"), and a ranked list of what the simplification broke. Source is the Google Sheet in [tft-reference-sheets.md](tft-reference-sheets.md), read via the project's `google-service-credential.json` service account.

> **Note on tabs.** Sections A–C below are a **historical** comparison. The two schemas they analyse —
> `Hero (old)` (gid 0) and the simplified `Hero` (gid 1893725546) — have since been **deleted** from the
> sheet, along with their column-explain tabs. Only the corrected model survives. The sheet's **current**
> 5 tabs are:

| Tab | id (gid) | Role |
|---|---|---|
| `Hero` | 930376992 | The corrected model — the live one (26-col long). Was `Hero (corrected)`. |
| `Column Explain` | 1026992711 | Column legend. Was `Column Explain (corrected)`. |
| `Action Types` | 60401606 | Each delivery archetype + its collision behaviour |
| `Effect Types` | 1336270564 | Each Effect Category → Detail, with a definition |
| `Collision Types` | 582387810 | Each collision's contact set vs effect recipient |

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

These recommendations are implemented as the surviving **`Hero`** tab (gid 930376992), with its **`Column Explain`** legend (gid 1026992711). It re-encodes the champions in a one-row-per-effect layout that restores the lost distinctions:

- Separate `Aim Target` and `Effect Recipient` columns (highlighted) — self-centered AOEs now read "Circle AOE, Aim Self, **Recipient = Enemies in area**"; Sona's ally row reads "Aim Clustered, **Recipient = Allies in path**".
- `Action` keeps distinct archetypes (e.g. Lux stays `Current Target Laser`, Target-Only) plus an explicit `Collision` column.
- `Cadence` (Once/Over Time/Perm) split from numeric `Duration (s)` (e.g. Kayle/Lux shred = 3).
- `Trigger` split into `Skill Type` / `Trigger (When)` / `Condition (Only if)`; traits un-merged into `Origin 1/2` + `Class 1/2`.
- **Kayle** breakpoints corrected to the prose gates (Lvl 1-5 / Lvl 6-8 / Lvl 9+), resolving the finding-#5 value drift.

Refined after user review (sheet comments):
- Effect split into `Effect Category` (Attack / Status / Buff / Debuff / Movement) + `Effect Detail`, per the user's preferred taxonomy (Status = Stun/Slow/Silence/Wound; Buff = stat boost; Debuff = stat deboost).
- Magnitude split into `Amount` (how much) + `Scaling` (how it behaves: stacking / decaying / falls-off / amplified-if-Wounded / burst).
- Rows of one attack share a `Step` and their action-instance cells are **vertically merged**, so multiple effects visibly belong to the same action (e.g. Kayle's `Pierce Projectile` merged across its Damage + MR-shred rows).
- Two reference tabs added: **`Action Types`** (each delivery archetype + collision behaviour) and **`Effect Types`** (each Effect Category → Detail with a definition). `Amount` clarified to mean the size of *that row's* effect.
- `Amount` populated with real per-star values pulled from **tft-set9 → `Champions` → Skill Description** (e.g. Galio `200/300/450% AP`); stun/wound/shield lengths routed to `Duration (s)`. The `Column Explain` legend was split into `Column | Meaning | Clarify more` (clean summary vs details).

## E. Coverage

The `Hero` tab is filled **one origin at a time**. Current coverage — 28 champions, 95 effect rows:

| Origin | Champions | Rows |
|---|---|---|
| Demacia | Kayle, Poppy, Galio, Garen, Sona, Jarvan IV, Lux | 2–18 |
| Noxus | Cassiopeia, Samira, Kled, Swain, Darius, Katarina, Sion | 19–39 |
| Ionia | Irelia, Jhin, Sett, Zed, Karma, Shen, Yasuo, Ahri | 40–71 |
| Shurima | Renekton, Taliyah, Akshan, Azir, Nasus, K'Sante | 72–96 |

Cassiopeia is **Noxus + Shurima** and is counted once, under Noxus.

**Roster rule: Set 9.0 only.** 9.5-only champions are excluded — Demacia's Fiora and Quinn, and Ionia's Xayah. Recorded as `Note - Roster` in `Column Explain`.

**Ionia Bonus.** Ionia is the first origin whose champions each carry a *unique per-unit* bonus (Irelia +25 Armor/MR, Jhin +25% AD, Ahri +3 Mana/s…). Rather than widen the schema with an `Origin Bonus` column that would be blank for all 14 Demacia/Noxus rows, each bonus is encoded as an ordinary **Passive step** — `Skill Type = Passive`, `Trigger = Game Start`, `Condition = If Ionia Active`, `Action = Cast`, `Recipient = Self`, `Category = Buff` — reusing Kled's existing `Game Start` passive precedent. The trait's 3/6/9 spirit-form doubling is *trait* data and stays in `tft-set9 → Origins`.

**New terms Ionia introduced**, all defined in the reference tabs:

- Actions: `Burst Projectile` (projectile that detonates on impact — AOE centred on the **impact hex**, not the caster), `Grab & Slam` (Sett), `Summon Shadow` (Zed — the clone is a *second action source*, so its AOE is centred on the clone).
- Collision: `Flank-Pair` (one enemy on each side, up to 2).
- Effects: `Buff → Armor / MR / AD / AP / Crit Chance / Crit Damage / Omnivamp / Mana Regen`, `Debuff → Mana Reave`, `Summon → (summon)`.
- Aim targets: `Farthest (within N hex)`, `Shadow`, `Lowest-HP Allies`, `Adjacent (both sides)`.

Ionia also produced the first **AOEs aimed at the current target rather than at Self** (Karma, Ahri, Yasuo's slam) — which is exactly the aim-vs-recipient split that finding B.1 above exists to preserve, and it holds without a schema change.

## F. Post-Ionia review pass — the taxonomy corrections

The user reviewed the Ionia pass in the sheet (13 comments) and two of them corrected the **whole tab**, not just the new rows.

### 1. Projectile vs Laser is a question of travel speed

The model had no definition, so it guessed — and put Jhin's line shot under `Laser Shot`. The rule:

| | Definition |
|---|---|
| **Projectile** | Fired **from** the unit and **travels** to the target — it has a projectile speed. `Homing` / `First hit` / `Pierce` / `Burst`. |
| **Laser** | **No travel speed at all.** Spawns on top of the unit and points at the target. `Standard Laser` / `Laser Shot` / `Current Target Laser`. |

Jhin's shot travels *and* pierces, so it is a **`Pierce Projectile`** — a new action. That in turn exposed **`Wave` as a duplicate**: all 5 Wave rows (Kayle ×2, Sona, Yasuo, Ahri) describe a thing that travels outward and pierces everything in its path, which is exactly `Pierce Projectile`. **`Wave` was deleted** and all 5 collapsed onto it.

The rule then did the same work in reverse. Irelia's second hitbox was first modelled as a new `Box AOE` action — but it has no travel speed, spawns on the unit, pierces, and lands once, which *is* `Laser Shot`. **`Box AOE` was retired** before it could calcify, and `Laser Shot` — briefly userless after Jhin left it — is Irelia's. The lesson is that the taxonomy only needs a new action when the *behaviour* is new, and "it doesn't look like a beam" is not behaviour. Recorded as `Note - Projectile vs Laser`.

### 2. Aim Target and Effect Recipient were 50% redundant

In 35 of 70 rows the recipient merely restated the aim (`Self` → `Self`, `Current` → `Aimed enemy`). Those now read **`Same to Aim Target`**, so the column only ever carries *new* information. Applied across all 22 champions — a convention applied to half a column is unreadable.

### Other corrections from the same pass

- **Collision is only for actions that project a hitbox.** A melee `Cast` (Darius, Yasuo) or a `Leap` projects nothing → `None`. But `Receive Projectile` (Poppy) is **`Self`**, a new collision value: her shield *was* projected and it collides with her on the way back. `None` and `Self` are not the same thing.
- **`Summon` is its own Effect Category** (Zed's shadow was mislabelled `Movement`).
- **`Step N Aim target`** is a real Aim Target value — Yasuo's dash, slash and slam all return to the enemy his step-2 whirlwind picked.
- **Identity block (cols A–J) is now vertically merged** across every row a champion owns, so Kayle's block spans steps 1–3 rather than step 1 alone.
- **Irelia has two hitboxes**, not one: a `Circle AOE` on herself *plus* a `Laser Shot` in front, both firing on shield expiry for the same damage. Her step count went 3 → 4.
- **`Auto-Attack` is itself a homing projectile** — fired at the aim target and always landing on it, which is why its Collision is `Target-Only`. It stays a separate Action only because it is the unit's default attack rather than an ability (`Note - Auto-Attack`).
- **`Action Types` gained a `Clarify more` column.** `What it does` had become a dumping ground for rules, caveats and examples; it is now one clean sentence per action, with everything else moved across — mirroring the `Column Explain` layout.
- Two source facts recorded rather than invented: Yasuo's whirlwind Stun has **no stated duration** (`Note - Yasuo`), and Karma's 3rd cast fires its three projectiles at the current target **and the enemies to its left and right**, sharing one hitbox so no target is hit twice (`Note - Karma`).

## G. Shurima — and the one gap the schema still has

Shurima needed **no per-unit bonus rows**: unlike Ionia, its trait is a blanket heal-and-Ascend with no per-champion text, so it stays in `tft-set9 → Origins`. Cassiopeia was already present as Noxus + Shurima and was left untouched.

**`Summon Shadow` generalised to `Summon`.** Zed's Shadow and Azir's Sand Soldier are the same archetype — a spawned unit that becomes a second action source. Same reasoning that retired `Box AOE`: a new action only when the *behaviour* is new. Zed's rows were retargeted onto the shared names (`Aim = Summon`, `Recipient = Enemies adjacent to Summon`).

**`First hit Projectile` finally has users.** It sat taxonomy-only through three origins; Taliyah's boulder (thrown *toward* a knocked-up enemy but landing on whatever it meets first) and each of Akshan's 6 shots are exactly it. **`Standard Laser` is now the only unused action.**

**New actions:** `Summon Attack` (a summoned unit, not the caster, performs the attack) and `Knock Back` — K'Sante's, where the **hitbox is the enemy he threw**: `Enemies in path` are whoever that flying body ploughs through. New effects: `Debuff → Max HP`, `Debuff → AD`, and `Status → Knock Off` (an execute — the target leaves the battlefield entirely, not a Stun).

### ⚠ Known gap: the schema cannot say *who performs* an action

It records what an action **aims at** and who the effect **lands on** — but not the **source**. This survived three origins by luck:

- **Zed's Shadow** attacks around *itself*, so the source was smuggled into `Aim Target = Summon`.
- **Azir's Sand Soldier** attacks **Azir's** current target. Source and aim are *different units*, so that hack has nowhere to go — his source rides in the **Action name** (`Summon Attack`) instead.

Two different smuggling routes for the same fact. The decision this pass was to accept it rather than widen the schema, so it is recorded as `Note - Action Source` in `Column Explain`. **A future pass should add a proper `Action Source` column** (`Self` / the summon) and put both on it — this is the same class of defect as finding B.1 (conflating aim with recipient), just one axis over.

**Scripts:** `.claude/scripts/tft-add-shurima.py` owns the Shurima rows plus the `Collision Types` text and the Aim/Recipient value lists; `.claude/scripts/tft-apply-comments.py` owns `Action Types`. Ownership is split deliberately — when both wrote the same cells they overwrote each other on every run. Both are idempotent: a second run reports zero changes.

**Scripts:** `.claude/scripts/tft-add-ionia.py` (the Ionia rows) and `.claude/scripts/tft-apply-comments.py` (this review pass). Both idempotent; run from repo root.
