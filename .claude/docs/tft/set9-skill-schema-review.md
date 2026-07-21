# TFT Set9-Skill — Schema Review: what the simplification broke

Comparison of the **old (intended)** vs the **simplified (second)** skill-analysis schema in the `tft-set9-skill` sheet ("TFT Set9 Skill Research"), and a ranked list of what the simplification broke. Source is the Google Sheet in [tft-reference-sheets.md](tft-reference-sheets.md), read via the project's `google-service-credential.json` service account.

> **Note on tabs.** Sections A–C below are a **historical** comparison. The two schemas they analyse —
> `Hero (old)` (gid 0) and the simplified `Hero` (gid 1893725546) — have since been **deleted** from the
> sheet, along with their column-explain tabs. Only the corrected model survives. The sheet's **current**
> 7 tabs are:

| Tab | id (gid) | Role |
|---|---|---|
| `Hero` | 416141206 | The corrected model — the live one (29-col long). See §I: this tab *is* the former `Hero (template)`, promoted. |
| `Column Explain` | 1026992711 | Column legend. Was `Column Explain (corrected)`. |
| `Action Types` | 60401606 | Each delivery archetype + its collision behaviour |
| `Effect Types` | 1336270564 | Each Effect Category → Detail, with a definition |
| `Collision Types` | 582387810 | Each collision's contact set vs effect recipient |
| `Action Templates` | 1145130824 | Each Action decomposed into Delivery × Collision × Shape |
| `Spread Types` | — | Each `Spread` pattern: how multiple instances of one Action are arranged |

> ⚠ **The old `Hero` gid (930376992) is dead.** Promoting the template model deleted that tab
> (see §I), so any *external* link pinned to that gid is broken. Nothing in code breaks: every
> script addresses tabs **by name**.

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

The `Hero` tab is filled **one origin at a time**. Current coverage — 43 champions, 137 effect rows:

| Origin | Champions | Rows |
|---|---|---|
| Demacia | Kayle, Poppy, Galio, Garen, Sona, Jarvan IV, Lux | 2–18 |
| Noxus | Cassiopeia, Samira, Kled, Swain, Darius, Katarina, Sion | 19–39 |
| Ionia | Irelia, Jhin, Sett, Zed, Karma, Shen, Yasuo, Ahri | 40–71 |
| Shurima | Renekton, Taliyah, Akshan, Azir, Nasus, K'Sante | 72–96 |
| Freljord | Ashe, Lissandra, Sejuani | 97–105 |
| Piltover | Orianna, Vi, Ekko, Jayce | 106–115 |
| Shadow Isles | Viego, Maokai, Kalista, Gwen, Senna | 116–129 |
| Targon | Soraka, Taric, Aphelios | 130–138 |

Dual-origin champions are counted once, under their first origin: **Cassiopeia** is Noxus + Shurima; **Ekko** is Zaun + Piltover (so he is already present for whenever Zaun's turn comes); **Senna** is Redeemer + Shadow Isles.

⚠ **Source-data discrepancy:** `tft-set9 → Origins` claims Piltover has **5** natural units, but the `Champions` tab lists only 4 — Camille is absent from the source sheet entirely. `Champions` is what we encode from.

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

### 1. Delivery is a question of where the hitbox spawns, and whether it travels

The model had no definition, so it guessed — and put Jhin's line shot under `Laser Shot`. The rule started as a two-way projectile-vs-laser split on **travel speed**, and the Shurima pass then completed it into **three modes** (see §G): the real discriminator is *where the hitbox spawns*, and only then whether it travels.

| | Spawns | Travels? | Actions |
|---|---|---|---|
| **Projectile** | on the unit | **yes** — has a projectile speed | `Homing` / `First hit` / `Pierce` / `Burst` |
| **Laser** | on the unit | no — extends toward the target | `Standard Laser` / `Laser Shot` / `Current Target Laser` |
| **Spawn At Target** | **on the target** | no — nothing crosses the gap | `Spawn At Target` |

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

### `Spawn At Target` — the third delivery mode

Reviewing the Shurima rows, the user rejected `Homing Projectile` for **Taliyah's active**: *"it was a hitbox spawn directly at enemy's hex."* Correct, and it was not a one-off mislabel — it exposed a **missing leg in the delivery taxonomy** (§F.1). Nothing is fired and nothing travels, because the hitbox spawns on the **target**, not on the caster. That fits neither existing mode.

So the two-way rule became three-way, and the discriminator is now stated properly: **where the hitbox spawns**, and only then whether it travels. Collision is `Target-Only` — nothing crosses the gap, so nothing in between *can* be touched.

Checked and deliberately **not** changed: **Cassiopeia**. Her source text is silent on delivery ("Deal magic damage to the current target and Wound them"), which is exactly the ambiguity that produced the Taliyah error — but the user confirmed something really does fly, so she stays a `Homing Projectile`. **Taliyah's passive boulder also stays `First hit Projectile`**: that one *is* thrown, and lands on whatever it meets first. Only her active moved.

## H. `Action Source` — closing the §G gap

The gap logged in §G was not survivable a third time. **Sejuani's** passive reads *"whenever an **ally** attacks a Chilled enemy, **they** deal bonus true damage"* — the **ally** performs the action. Zed's source could hide in `Aim Target` (his shadow attacks around itself) and Azir's in a fake action name (`Summon Attack`), but Sejuani's source is neither her nor her summon. There was nowhere left to put it.

So the schema gained a **27th column, `Action Source`** (`Self` / `Summon` / `Ally`), inserted before `Action` and backfilled `Self` — the default must never be blank, or a blank reads as *unknown* rather than *the caster*. Three columns now answer three genuinely different questions:

| Column | Question |
|---|---|
| **Action Source** | **who performs it** |
| Aim Target | what it points at |
| Effect Recipient | who the effect lands on |

**Both hacks were undone.** Zed's shadow-slash becomes `Source=Summon, Aim=Self` — his step 3 and step 4 are now *identical* (`Circle AOE`, aim Self, enemies in area) and distinguishable **only** by the Source column, which is exactly the point. And **`Summon Attack` was retired**: it existed solely to smuggle the source into an action name, and the Sand Soldier simply **auto-attacks**, so `Source=Summon` + `Auto-Attack` says it plainly. Same reasoning that retired `Box AOE` — no action whose only job is to encode something a column now carries.

**New terms:** `Status → Chill`, `Attack → True Damage`, `Debuff → Damage Amplification`, `Buff → Empowered Attack`. *Sunder* is not a new effect — it is the existing `Debuff → DEF` under another name, so it became an alias in that row's definition rather than a duplicate.

### Aim Target is absolute

A correction the user caught in review. Zed's shadow-AOE was written `Aim = Self` — meaning *self as seen by the summon*, i.e. **relative to the Action Source**. That implicit reading is exactly what this schema exists to stamp out. **`Aim Target` is absolute**: `Self` always means the champion, so the shadow's AOE is aimed at `Summon`. Source and Aim still say different things (*who acts* vs *where it lands*); for Zed they coincide, for Azir they do not.

## I. Action Templates — the third leaked axis

The `Action` column was fusing **two** axes, and a **third** had been leaking into free text.

**The evidence, not the theory:** multiplicity was smuggled into `Scaling` as prose in four separate places — Ashe `×8 arrows in a cone`, Akshan `×6 shots`, Karma `×3 bursts`, Azir `all 3 Soldiers strike at once`. That is precisely the failure mode `Action Source` had before it earned a column: a real, recurring axis leaking into whatever free-text field was nearest, because nothing structured would hold it.

So an Action is not a primitive. It is a **composition**:

```
Action  =  Delivery  ×  Collision  ×  Shape        …and then  × Count × Spread
```

This makes the user's two earlier observations fall out as structure rather than trivia: `Burst Projectile` **is** `First hit Projectile + Circle AOE`, and `Circle AOE` **does** have the same *delivery* as `Spawn At Target`, differing only in *shape*.

The model was trialled in new tabs so nothing that already worked could break (the user's call): an `Action Templates` reference tab, and a `Hero (template)` copy carrying `Count` and `Spread`. Ashe became `First hit Projectile / Count 8 / Spread Cone`; Karma's `Current + Left + Right` spread became a *defined pattern* rather than a footnote.

**Ahri was re-encoded.** The user described her second-cast wave as a 360° eruption from her own body with a hitbox large enough to reach the whole board. That is not aimed at the current target, which is how it was encoded. She is now `Aim = Self`, `Spread = 360° radial`, `Recipient = All enemies`.

### I.1 The template model is now canonical

The user reviewed the trial and signed off: *"I am satisfied with the Hero (template) tab. Let's use this one from now on. Also delete the old Hero tab."* So `tft-promote-template.py` **renamed** `Hero (template)` → `Hero` and deleted the old tab.

**Renamed, not copied back.** Copying the template's values into the old tab would have preserved its gid, but it would also have meant rebuilding by hand the ~570 vertical merges (champion identity blocks, per-action blocks) that make the tab readable — and a merge rebuilt by hand is exactly the kind of thing that goes wrong quietly. The rename keeps the sheet the user actually reviewed, merges and all. The cost is the dead gid, noted at the top of this doc.

`Count`/`Spread` are now first-class `Hero` columns in `HERO_COLUMNS` and `ACTION_BLOCK` (`tft/sheet.py`), so every script resolves them like any other column. Because `append_champions()` fills rows **by column name** and knows nothing about them, a newly-added region would otherwise land with both cells blank — and blank reads as *"unknown"*, not *"fires once"*. `backfill_hero()` closes that: it fills only the blanks with `COUNT_DEFAULT` / `SPREAD_DEFAULT`, so a region script that sets them itself is never overwritten, and one that forgets cannot leave a hole.

### I.2 `Spread` earned its own tab

`Spread` began as a block bolted onto the bottom of `Action Templates`. The user rejected that placement — *"Dedicate new tab to it"* — and was right: **Spread is orthogonal to the Action, not a property of one.** Ashe (`Cone`) and Akshan (`Same target`) fire the *exact same* Action, `First hit Projectile`, and differ only in arrangement. Filing it under `Action Templates` asserted the opposite.

Writing the definitions out properly surfaced two distinctions the footnote had been hiding:

- **`Same target` vs `Current + Left + Right` differ in hitbox count, not just geometry.** Akshan's 6 shots are 6 separate hitboxes — one target, hit 6 times. Karma's 3 share **one** hitbox, so an enemy caught by two of them is not damaged twice.
- **Ashe's cone is an emergent shape, not a hitbox.** There is no cone collider: each arrow is its own `First hit Projectile` stopping on the first body in *its* lane — which is why a wide cone can still miss.

### Scripts

Each tab has **one owner** — when two scripts wrote the same cells they overwrote each other on every run, a bug that bit twice:

| Tab | Owner |
|---|---|
| `Action Types`, `Column Explain` notes, comment replies | `tft-apply-comments.py` |
| `Collision Types`, `Condition` list | `tft-add-shurima.py` |
| `Hero` schema + rows, `Effect Types`, the Aim/Recipient/Trigger lists | `tft-add-freljord-piltover.py` *(latest pass wins)* |
| `Action Templates`, `Spread Types`, the `Hero` Count/Spread invariant | `tft-action-templates.py` |
| The `Hero (template)` → `Hero` promotion *(one-off, idempotent)* | `tft-promote-template.py` |
| The `Column Explain` **value lists** (Trigger · Condition · Aim Target · Effect Recipient) | `tft-add-shadowisles-targon.py` *(the latest origin pass)* |

## J. Shadow Isles + Targon

8 champions: **Shadow Isles** (Viego, Maokai, Kalista, Gwen, Senna) and **Targon** (Soraka, Taric, Aphelios). Both rosters match `tft-set9 → Origins` exactly — 5 and 3 natural units, no discrepancy of the kind Piltover had. Neither trait has a per-unit bonus (Shadow Isles shields after 12 damage events; Targon amplifies healing team-wide), so there are **no bonus rows** — the Freljord/Piltover precedent, not Ionia's.

**The first pass since `Count`/`Spread` became canonical — and the model held.** Kalista's 6 spears, Gwen's 3 snips and Soraka's 5 stars are all `Count > 1`, and all three encode with the **existing** `Same target` spread. No new `Spread` value was needed for data the model had never seen. Multiplicity did not leak back into `Scaling` once.

Most of the rest reused existing terms too — `Clustered` turned out to be exactly Aphelios' *"largest group of enemies"*, and Senna's beam is the second real user of `Laser Shot`, damaging the enemies it pierces **and** shielding the allies it pierces in one action (Sona's precedent). What was genuinely new:

| Kind | New value | Introduced by |
|---|---|---|
| Action | `Cone Slash` | Gwen |
| Effect | `Buff → Mana` (flat, on an event — distinct from per-second `Mana Regen`) | Maokai |
| Effect | `Status → Impale` (stacks; pays out when **removed**) | Kalista |
| Effect | `Buff → Damage Redirect` | Taric |
| Effect | `Buff → Chakram` (a stack *resource*, not a stat) | Aphelios |
| Trigger | `On Enemy Cast` · `On Spear Removal` | Maokai · Kalista |
| Condition | `If Lethal` · `If Ally Below 50% HP` | Kalista · Soraka |
| Aim Target | `Farthest` · `Nearest enemy to the healed ally` | Senna · Soraka |

### J.1 `Cone` — superseded, see §K.1

The first ruling here was that Gwen's cone is a real collider. **That was wrong** — she is a sweeping laser. See §K.1.

### J.2 Source gap — Maokai

`tft-set9 → Champions` lists Maokai's **entire** stat block as `N/A`, Range included. `Range` is left as an em-dash rather than guessed — the Yasuo rule (the source is silent, so the sheet says so). Recorded as `Note - Maokai`.

### J.3 Ownership consolidation (see §K for the review round that followed)

The `Column Explain` value lists were split across two scripts — `tft-add-freljord-piltover.py` held Trigger/Aim/Recipient, `tft-add-shurima.py` held Condition. They did not yet fight (different keys), but this pass adds values to **all four**, and a third writer would have restarted the exact overwrite-each-other bug that bit twice. All four now have a single owner: the latest origin pass.

All share the tooling's shared helper (now `.claude/scripts/tft-set9-skill-modularity/sheet.py`), which resolves **columns by header name, never by index**. That is not cosmetic: every script addressed cells as `r[14]`, and inserting `Action Source` mid-table would have silently redirected every one of those writes into the wrong column. The header lookup kills the whole class of bug.

**Idempotence is the acceptance test.** Run all three scripts twice; the second pass must report **zero changes**. That is what caught both cell-fighting bugs.

**Scripts:** `.claude/scripts/tft-add-ionia.py` (the Ionia rows) and `.claude/scripts/tft-apply-comments.py` (this review pass). Both idempotent; run from repo root.

## K. Review round 2 — three corrections to the model itself

The user's review of the Shadow Isles / Targon pass corrected the **model**, not just cells. Applied by `.claude/scripts/tft-review-round2.py`.

### K.1 A cone is never a hitbox — and hitboxes can MOVE

*"Her cone is a laser hitbox. But got swept in cone shape. So it didn't spawn as a cone hitbox but it was a laser that got swept to look like the cone."*

This is better than either option that was offered, and it kills `Cone Slash`. Gwen is now **`Sweep Laser`**: laser delivery (spawns on her, no travel), Pierce-All, Shape = `Line — SWEPT through an arc`. The cone is only the shape the moving line leaves behind.

**A cone is therefore never a collider anywhere in this sheet.** Two things merely look like one:

- **Spread = Cone** — N *separate* hitboxes arranged in a cone, each its own projectile. Ashe's 8 arrows; each stops on the first body in *its* lane, which is why a wide Ashe cone **can** miss.
- **A sweeping hitbox** — Gwen. One line, moving.

⚠ The earlier `Note - Cone: shape vs spread` taught the opposite (that Shape = Cone is a real collider). It was **rewritten, not amended** — a doc that teaches a falsehood is worse than no doc.

**The gap this opens:** nothing in the schema can say a hitbox **moves while the action runs**. `Delivery` says where it spawns, `Shape` says what it is, `Count`/`Spread` say how many and where — none say it travels sideways. Carried in the Shape text and flagged in `Action Model`. One case does not justify a column; **a second swept action would**. This is the same shape of finding as `Action Source` and `Count`/`Spread` before they earned columns.

### K.2 `Perm` was a Duration wearing a Cadence's clothes

*"Cadence means the application time of the effect. The stack has application time 1, but it stays permanent. I think Cadence = 1, and Duration = permanent."*

Exactly right. A permanent buff is applied **once** and simply never expires: `Cadence = Once`, `Duration = Permanent`. `Perm` is removed from the Cadence value list, which is now strictly `Once / Over Time`.

This was **never** a Shadow Isles problem: **14 rows** carried `Cadence = Perm` and **12 predate the pass** — every Ionia bonus passive, plus Samira's DEF shred and Kled's Attack Speed. The error was always in the sheet; Viego is only where it became visible.

### K.3 `Empowered Attack` was covering two mechanics

*"Orianna only has 1 empowered attack that's used up the moment she attacks next. Viego stacks the empowered attack and his stack never goes away, which means every attack got empowered."*

Two mechanics, one name — which is what Q2 suspected but could not settle from the source text:

| | Effect | Champions |
|---|---|---|
| One attack, then spent | `Buff → Empowered Attack` *(definition tightened)* | Orianna, Maokai |
| **Every** attack, while it lasts | `Buff → On-Hit Damage` *(new)* | Viego (Permanent), Aphelios (7s) |

### K.4 `Action Types` + `Action Templates` → `Action Model`

*"What is the difference between Action Template and Action Types?"* — **not enough to justify two tabs.** They described the same 18 actions, agreed on Action/Collision/Cadence, contradicted each other on nothing, and `Templates` was simply the more precise (it splits the Action into Delivery × Shape). Two tabs describing one thing is how they drift.

Merged into **`Action Model`**: `Action | Delivery | Collision | Shape | Cadence | What it does | Clarify more`. Built as a **new** tab with both originals left intact — the user's call ("merge them as a new tab, preventing accident"), and the same play as `Hero (template)`: prove it, then promote and delete the old two.

### K.5 Corrections to my own errors

- **Viego is a `Laser Shot`, not a `Cast`.** But `Laser Shot` is Pierce-All, and the source says he damages only "the current target". The row deliberately holds that disagreement visible (`Collision = Pierce-All`, `Recipient = Same to Aim Target`) rather than silently widening who he damages. Asked as **Q8**.
- **`Farthest` was never a new value.** Q7 claimed it was; **Akshan (row 77) already used it**. It was merely undocumented. `Farthest` (whole board) and `Farthest (within N hex)` (bounded — Zed 2, Yasuo 3) are both real and both stay.
- **Maokai's Range = 1** — his stat block is `N/A` in the source; the user confirmed melee.

## L. Rounds 3–4 — the model stops pretending actions are frozen

### L.1 The gap that showed up twice: something changes *during* the action

Every axis in this schema — `Delivery`, `Shape`, `Collision`, `Count`, `Spread` — describes an action as if it were **frozen at the instant of cast**. Two champions broke that, in two different ways:

| Champion | What changes mid-action | How it is carried |
|---|---|---|
| **Gwen** | the **hitbox moves** — a laser sweeping through an arc | in the `Shape` text (`Line — SWEPT through an arc`) |
| **Soraka** | the **aim is re-evaluated** — each of 5 stars re-picks the enemy closest to the healed ally | new spread `Re-picked per instance` |

Same shape of gap, twice. **Two cases is not enough to justify a column, so none was built** — but it is no longer a coincidence, and a third would settle it. Recorded as `Note - Mid-action change (KNOWN GAP)` so the third one gets noticed when it arrives.

This is the same way `Action Source` and `Count`/`Spread` each announced themselves: a real recurring axis, leaking into whatever field was nearest, until enough cases accumulated to earn a column.

### L.2 `Range` was a real range all along — the data was wrong, not the header

The column read `Range`, but 35 of 43 champions stored a **position** (`Frontliner`/`Backliner`) in it. The 8 Shadow Isles / Targon champions stored the actual hex range from the source. The user's call: **the header is right**. All 43 are now backfilled from `tft-set9 → Champions → Range`.

⚠ **What that discarded is not recoverable.** `Frontliner`/`Backliner` appears **nowhere** in `tft-set9` — it was a human judgement. Ranges can be rebuilt from the source at any time; those labels cannot. If the classification is ever wanted back it must return as its **own column** and never into this one. Recorded as `Note - Range`.

### L.3 Decided and closed: a stack counter is an Effect, not an axis

Viego's stacking `On-Hit Damage`, Kalista's `Impale` and Aphelios' `Chakram` are the same shape — a counter that does nothing itself and multiplies a later effect — and were proposed as a 4th axis deserving a column. **User: "Effect sound right to me."** They stay Effect Details. Recorded as `Note - Stacks` so it is not re-litigated.

### L.4 The source text can be wrong

`tft-set9` says Viego damages "the current target". He does not — **"It pierces and hits everybody, the description for skill here is wrong."** His row now knowingly contradicts the source (`Pierce-All`, `Enemies in path`). Since every other number in the sheet is traceable to that column, the contradiction is flagged as `Note - Viego / bad source text`, so nobody later "corrects" the row back to match the bad source.

### L.6 Round 5 — `Count` is not an `Amount`, and `Condition` is per-effect

**Kalista is `Count 1`, not 6.** *"It was a projectile that when hit, the enemy got +6 impale."* One projectile; six **stacks**. I had read "impale 6 spears" as six action instances.

That is a misuse of the column, and a tempting one — so it now has a test:

> **Could one of them miss while another hits?**
> If yes, it is a `Count` (Akshan's 6 shots are 6 separate projectiles, each its own hitbox). If the number is all-or-nothing on a single impact, it is an **`Amount`** (Kalista's 6 spears land together or not at all).

Recorded as `Note - Count vs Amount`.

**`Condition` is now PER-EFFECT, not per-action.** *"This are the same heal, so it should be combined into same step."* Soraka's base heal and her below-50%-HP bonus heal are one cast on one ally — but `Condition` sat in the **merged action block**, so it could only gate a *whole* action. That is the only reason the bonus heal had been faked as a separate step: a workaround for a missing capability, not a modelling decision.

`Condition` is removed from `ACTION_BLOCK` (`tft/sheet.py`) and is no longer merged. A condition gating a whole action simply repeats down its rows; one gating a single effect sits on that row alone. Recorded as `Note - Condition is PER-EFFECT`.

### L.7 `Action Model` promoted; the two old tabs deleted

*"I already see the Action Model. Sound good, use this one from now on. Delete the old one."* Done — `Action Types` and `Action Templates` are gone, and the code that wrote them is stripped from `tft-apply-comments.py` and `tft-action-templates.py`. `tft-action-model.py` is the sole owner of the action taxonomy; `tft-action-templates.py` now owns only `Spread Types` and the Count/Spread invariant on `Hero`.

The delete is guarded: `promote()` refuses to drop the old tabs unless `Action Model` is present and fully populated.

### L.8 Round 6 — `Scaling` was the last free-text field, and it leaked

**35 rows carry a `Scaling` value and 27 are distinct.** That ratio is the tell: it was prose, not a vocabulary. Sorting the values showed the column fusing **four** different things:

| What it actually was | Example | Where it belongs |
|---|---|---|
| a real **modifier** | `stacking`, `decaying 20/13/0%/s`, `per Chakram equipped` | this is Scaling |
| a **duration** | `rest of combat` (Sona), `until next cast` (Ahri) | `Duration` |
| **multiplicity** | `×8 arrows in a cone` (Ashe) | `Count` / `Spread` |
| prose that isn't scaling | `redirected onto Taric himself` | nowhere — `Effect Types` already defines it |

Fixed the way this sheet always fixes it: **split the column.** `Scaling Type` is a 10-value vocabulary (new `Scaling Types` tab) and `Scaling` keeps the specifics — the same `Effect Category` / `Effect Detail` idiom sitting two columns to its left.

⚠ **The Ashe row is the finding.** `×8 arrows in a cone` is exactly the multiplicity `Count`/`Spread` was built to eliminate — and it **survived that cleanup**, because the fix only rewrote each action's *first* row and never its continuation rows. It was the last leak in the sheet, and it sat there undetected for three rounds.

### L.9 `Re-picked per instance` was a bad spread value

*"The rest is spread but this one isn't."* Correct. The other four spreads answer **where** the instances go (a geometry). That one answered **when** the aim is decided — which is why no name for it was ever going to sit right in that column.

Renamed to **`Each to its own target`**: a where-answer, so it belongs in the family. The re-picking is now the point of its Clarify text, not of its name. The underlying mid-action gap (§L.1) is unchanged.

### L.10 `Column Explain` had become half decision-log

20 of its 41 rows were Notes. A **column legend** ("what does this cell mean") and a **decision log** ("why is the schema this shape, what did we rule out") are different documents, and mixing them buries the legend.

All 20 moved to a new **`Design Notes`** tab. `Column Explain` is back to one row per column.

**This broke idempotence, which is the point of running twice.** Seven scripts appended notes to `Column Explain`; once the notes were gone, their "already present?" check could never be satisfied, so they re-added them on every run. Fixed by routing every script through one `sync_notes()` helper (`tft/sheet.py`) pointed at the new tab — one writer, one place.

### L.5 Kalista's condition was redundant

Lethal is the *only* thing that pulls a spear, so `Trigger = On Spears Lethal` says it and `Condition = If Lethal` said it twice. Condition collapsed to an em-dash; `If Lethal` removed from the value list.

---

## M. Rounds 7–9 — what a *Step* actually is

Three rounds that all answer one question, because the user kept asking it from different angles: **what is a Step?** The answer the sheet now gives:

> **A Step is a MOMENT in the cast. Each ROW is one branch of it: condition → action → effect.**

Everything in §M falls out of that sentence.

### M.1 Round 7 — a passive is not part of the cast

*"Isn't it weird to have Passive as Step 1? Passive should be Step 0."* If `Step` is the order of events **within one cast**, then a passive is not in that sequence at all. **15 champions opened with a passive at Step 1; 19 renumbered in total.**

`Count`/`Spread` also became **per-effect** here. Karma's 1st cast fires ONE burst and her 3rd fires THREE — from the same action. A merged `Count` cannot say that, and *that limitation was the only reason those had ever been two steps.* A schema limit had been mistaken for a design fact.

⚠ **Renumbering is the most dangerous edit in this sheet.** Steps are *referenced* by other cells (`Step 2 Aim target`), so renumbering one means rewriting whatever points at it. Round 7 broke three things at once by not doing so — a stale `("Azir","1")` key overwrote his Summon, Irelia's *"insert if no step 4"* guard fired twice and duplicated a row, and Yasuo's three re-aims pointed at the wrong step. **A step number is a POSITION, not an IDENTITY. Never key on one, never guard on one.**

### M.2 Round 8 — the action block dissolves

*"Same step, but with if-else condition"*, on five champions. They were right, and it costs more than Karma did. Karma's two branches fired the **same** action; these five fire **different** ones:

| Champion | branch A | branch B |
|---|---|---|
| Swain | not transformed → `Cast` (gain HP) | already transformed → `Circle AOE` burst |
| Azir | fewer than 3 Soldiers → `Summon` | already 3 → they all `Auto-Attack` |
| K'Sante | target at edge → knock off | not at edge → `Leap` after it |
| Kayle | Lvl 1–5 → `Auto-Attack` | Lvl 6+ → `Pierce Projectile` |
| Ahri | every cast → `Circle AOE` | 2nd cast → **also** a `Pierce Projectile` |

So `Action`, `Collision`, `Aim Target` and `Trigger` cannot be properties of the **step** any more. The merged action block is gone: only `Step` and `Skill Type` span a step, and **everything else merges by VALUE RUN** — wherever consecutive rows happen to agree.

**A merge is now a *display of* the data, not a *claim about* it.** That is the only form of merging that survives a schema where any column may differ per row.

**Not all branches are exclusive.** Ahri's wave is *additional* to her Circle AOE, not instead of it, so her first branch keeps an em-dash rather than a false `If not 2nd Cast`. Encoding an either/or where the game has an *and* would be a lie that reads as rigour.

### M.3 Round 9 — the test that falls out of it

If a Step is a moment, then **two steps triggered by the same event are one step.** Applying that test found four more champions whose Step 2 fired on `On Cast` — the same instant as Step 1:

| Champion | Step 1 | Step 2 (collapsed up) |
|---|---|---|
| Shen | shields himself | shields the lowest-HP allies |
| Orianna | shields an ally | empowers her own next attack |
| Jayce | buffs his attack speed | buffs adjacent allies' AP |
| Viego | fires his beam | stacks his on-hit damage |

A *consequence* still earns its own step — Jayce's burst is `After Cast`, so it survives as Step 2.

### M.4 Karma's actions were wrong, and the source text is what misled me

*"1st, 2nd cast: do circle AOE. 3rd cast: do Pierce Projectile. The description is misleading, but believe me on this one."*

Round 7 had collapsed Karma on the explicit claim that her branches were *"the same action, same amount, same AOE — they only ever differed by Count and Spread."* **The first half of that was false.** The collapse still stands, but for a better reason than the one given: round 8 later established that the rows of one step may run *different actions*, which is exactly what her correction describes.

Collision and shape came from `Action Model`, not from guesswork: `Pierce Projectile` is Pierce-All / Line, so her 3rd cast hits `Enemies in path` and its AOE is an em-dash — **a line has no circle radius.**

### M.5 Maokai's heal was never a passive

He had it as a separate always-on step (`0.2`) gated by `If Empowered`. That step **claimed he heals on attack whether or not he ever cast** — which is false — and the condition existed only to take the claim back. *A condition that exists to undo its own Step number is a workaround for a missing word, not a design.*

The word now exists: a new Effect Detail, **`Empowered Attack (Maokai)`** — the next auto-attack also heals. This preserves the split settled in round 2: Orianna and Maokai get ONE empowered attack, spent on the next hit; Viego's stacks forever (`On-Hit Damage`). Maokai's now differs in **what it does**, not in how long it lasts.

### M.6 Swain's burn was never a step either

Same shape as Maokai. It ticks for as long as he is transformed, whether or not he casts again — so it is `Step 0`, `Passive`. Its `Condition` stays an em-dash because the Trigger `When Transformed` already says it (the §L.5 Kalista rule: the sheet does not say a thing twice). **Flagged to the user in case they want the Condition column filled literally — which would mean bringing Kalista's back too.**

---

## N. The tooling bugs — three cell-fights, all the same shape

Every one of these was caught by the same test, and by nothing else:

> **Run every script TWICE. The second run must report ZERO changes.**

### N.1 `tft-add-ionia.py` was crashing on every single run

It wrote to the `Action Types` tab that **round 6 deleted**, so it raised `WorksheetNotFound` every time. **The crash was load-bearing** — it aborted the function before two further staleness bugs could fire, which is why nobody had seen them:

- It rewrote the `Column Explain` value lists that `tft-add-shadowisles-targon.py` owns. Two scripts, one cell, overwriting each other for ever.
- Its `Effect Types` row was keyed `("Movement","(summon)")`, but `tft-apply-comments.py` had renamed that category to `Summon` (a summon is not a repositioning). **The key never matched, so the row was re-appended on every run** and then renamed — the tab grew 37 → 38 → 39 before it was caught.

**Lesson: a declared block must state CURRENT truth.** A declaration written under one version of the schema silently rots when another script changes what it declares.

### N.2 The filled-value trick is fatal on `Step`

Round 8 established a rule for converging rewrites: *write the FILLED value into a continuation row, and let the re-merge absorb the duplicate.* That is right for every column **except `Step`** — because `Step` is what `remerge()` reads to find the step **boundaries**.

Writing `"1"` into a continuation row instead of a blank made that row look like a **new step start**. The re-merge then refused to merge it away, round 7's renumber saw *two steps both numbered 1*, and renumbered everything below them — which round 9 undid on its next run. **A stable, infinite fight**, invisible to any check except running twice.

`Step` and `Skill Type` are now compared **raw** and written **literally**. A blank continuation row must genuinely *be* blank.

### N.3 A reply key is a SUBSTRING, and a short one grabs the wrong comment

Round 9's match key `"same step"` also matched Soraka's *"This are the same heal, so it should be combine into same step"* — a comment answered back in round 5. It collected a reply about Shen and Jayce that had nothing to do with it. The reply was deleted by hand and a guard added.

**Match keys are substrings of the comment's own text, and a mismatch fails SILENTLY.** Longer keys must be listed first, and any already-answered comment whose text contains a shorter key must be listed *ahead* of it with its existing reply body, so it matches there and is skipped.

---

## O. The consolidation — 17 scripts became 1

The user asked the question that ended §N: **"is checking those scripts necessary? I thought it was one-time use?"**

They were right, and the answer was uncomfortable. Look again at the three bugs in §N:

| Bug | Real, or self-inflicted? |
|---|---|
| `tft-add-ionia` crashing on a deleted tab | **Real** — Ionia's reference rows were never written. |
| The round 7 ↔ round 9 renumber fight (§N.2) | **Self-inflicted** — no fight if round 7 were retired. |
| The `add-ionia` ↔ `apply-comments` duplicate row (§N.1) | **Self-inflicted** — same. |

**Two of the three bugs existed only because the scripts were re-run.** Each `tft-review-roundN.py` is a *migration*: it patches the sheet from state N-1 to state N. Once applied, it has no further work — but the acceptance discipline re-ran it anyway, on every pass, for ever. **A one-shot migration cannot fight anything if it is never run again.**

The suite had reached **17 scripts, 5,257 lines, and ~13 minutes** per acceptance run — to describe one 132-row table.

### The new shape

The sheet's state was verified correct at round 9, so **the sheet became the source of truth, and then the truth moved into the repo:**

```
.claude/scripts/tft-set9-skill-modularity/
  README.md    the entry point: "edit a CSV, run sync.py"
  sheet.py     helpers: cols(), remerge_hero(), post_replies()
  export.py    sheet -> data/*.csv        (snapshot)
  sync.py      data/*.csv -> sheet        (THE one writer) + validate
  data/*.csv   the source of truth, one file per tab
  archive/     the 17 retired scripts — kept for history, never run
```

It is a self-contained folder on purpose. `data/` and `archive/` are generic names, and
`.claude/scripts/` is shared with other work — namespacing them is what stops a future collision.

**The folder is named for its job, not for the game.** Other scripts in this repo also touch TFT data
(`sheet_sync.py`, `balance_report.py`, `push_stats_to_sheet.py`), but they are a different task. A
bare `tft/` would have claimed a namespace it does not own; `tft-set9-skill-modularity/` claims only
the sheet it actually writes.

**5,007 lines retired. 523 lines live. ~13 minutes → 68 seconds.**

### Why a CSV is enough

**Merges are DERIVED from the values, never stored.** `remerge_hero()` reconstructs all three layers — the champion identity block, the `Step`/`Skill Type` span, and the value-run merges on `Trigger`…`Aim Target` — from the cell values alone. So a flat table fully describes the sheet.

**A blank cell is data.** A merged cell reads back `""` on every row but its first, so a continuation row exports as a genuine empty string and is written back as one. They round-trip exactly.

### The gate that made it safe

The whole refactor rested on one cheap, decisive check:

> **Export the sheet, then run the sync. It must report ZERO cells changed on its FIRST run.**

A zero-diff first run proves the CSV reproduces the sheet *exactly* — the export is lossless and the writer is faithful. Any non-zero diff would have meant the round-trip lost something. **It passed, and nothing was archived until it did.** The sheet was never at risk: a zero-diff sync writes nothing.

### What this buys

A review round used to mean **a new 300-line patch script** that would then be re-run for ever. It now means: **edit the CSV, run one script.** The git diff shows exactly which cells moved — which is the thing a patch script could never show.

And the "two scripts fight over one cell" bug is no longer something the tests catch. **It is something the architecture forbids.**

---

## P. `Role` normalised, `Damage Type` split out (2026-07-21)

The user's question was short: *"The role column in set9 and set10 should only use Tank/Fighter/Mage/Marksman/Assassin following Archetype Review tab. Is that make sense?"*

It did, and the reason it did is that `Role` was the one identity column that could not be **compared across the two sets**:

| Tab | What `Role` held |
|---|---|
| `Hero set 9` | Carry 41 · Tank 23 · Support 11 — **3 values** |
| `Hero set 10` | APTank 14 · ADFighter 8 · ADCarry 5 · ADTank 5 · ADCaster 5 · APCaster 5 · … — **13 values** |

Sixteen strings describing five actual jobs. The `Dashboard` tab has shipped a **Role dropdown filter** since round 14 that could not answer *"show me every Marksman"*, because no such value existed in either set.

### P.1 This reverses D4 — for the second time, and in the other direction

D4 said **"leave `Role` alone as imported source data."** Round 11d had already partly reversed it: `Role` turned out to predict 13 of the user's 17 reviewed champions where the damage proxy predicted 2, so the column stopped being ignored and became the *primary signal*. The distinction drawn then was *"Role is still not written to, but it is now read."*

That distinction is now gone. **`Role` is written to, and is no longer refreshable from source.** It holds the user's reviewed judgement — his 14 corrections and his four flat disagreements with the source (Warwick, Urgot in both sets, and Olaf are Fighters where the source says Tank; Nilah is a Marksman despite being melee at range 2).

### P.2 The derivation became circular, and not harmlessly

`build_archetype_review.py`'s `role()` **read** the imported column. Writing its own output back into its input made it self-feeding — and the failure would not have been a stable no-op:

> Its ranged branch tested `role.startswith("AD")` against source strings like `ADCaster`. Against a normalised `Marksman` that test fails, the champion falls through to be re-judged on class, and **Mage and Marksman flip on a rebuild.** Only the `"Tank" in role` test happens to be idempotent.

So `role()` is now a passthrough, and `CLASS_FN`, `function()`, `is_assassin()` and `USER_ROLE` were **deleted rather than left unused**. This file has already been bitten by a mapping that outlived its vocabulary — `Strategist → Support` kept resolving to a role that no longer existed and sent Teemo to Marksman. **Dead code that still computes a plausible answer is the dangerous kind.**

### P.3 `Snipe Backline` lost its guard silently

The tag excluded Senna with `"Support" not in ch["role"]`. Removing `Support` from the vocabulary made that test **vacuously true for every champion** — the kind of break that raises nothing and changes an output. It was found by grepping for readers of the old vocabulary before the write, not after.

Asked, the user's answer was **yes, Senna belongs** (4 tags → 5). The data had argued the same all along: her beam is `235/250/2000% AD`, the highest of the group, against Akshan's `125%` — and he had called Akshan a sniper. She and Set 10 Lux are otherwise identical rows (Laser Shot, Pierce-All, aim `Farthest`).

### P.4 Damage type had to be kept, because only one set ever stated it

Collapsing sixteen strings onto five nouns throws away the `AD`/`AP` prefix — and **that prefix is the only place either set states a champion's damage type.** `Scaling Type` does not: it holds `Derived` / `Stacking` / `Per Tick`. Recovering it otherwise means regexing `% AD` / `% AP` out of `Amount`.

So it became its own identity column, and the schema went **32 → 33 columns**, `Damage Type` sitting at index 3 directly after `Role`.

**Set 10's values are stated** (read off the prefix before it was overwritten). **Set 9's are derived** — the stat the champion's *ability damage* scales on, meaning an `Attack` category effect row. Utility scaling is deliberately ignored, which is the whole rule: Warwick's only AP number is a `30/35/40% AP` heal and Kled's is an Attack Speed buff, and both deal their damage with auto-attacks.

**The derivation was tested against Set 10 before being trusted on Set 9, where the answer was already stated: 59 of 60.** The single miss is Olaf, and he misses for the honest reason — his ability deals no scaled damage at all, so the rule had nothing to read and fell through to a utility number. That is why the seven Set 9 champions in the same position are **hand calls** (Orianna, Maokai, Taric → AP; Kled, Warwick → AD; Cho'Gath and Ryze → `—`) rather than being handed to a fallback heuristic. **A rule that abstains is worth more than one that always answers.**

`—` is an answer here, not a gap: Cho'Gath scales on `12% of the target's max HP` and Ryze on `150/200/300%` of his own Armor + MR.

### P.5 What was lost, stated plainly

`Role` + `Damage Type` + `Range` reconstruct almost all of Set 10's strings. **`HighMana` (5 champions) and `Crit` (1) have nowhere to go** — Max Mana is not a Hero-tab column. Flagged to the user before the write; he accepted the drop.

### P.6 A column insert breaks every index that was not a name

Invariant #1 says columns are addressed **by name**. Three readers had drifted from it, and inserting at index 3 shifted everything after it:

| Reader | What it would have done |
|---|---|
| `flatten.py` `ACTION_COL = 15` | read `Aim Target` as the action name → **all 462 rows lose their `Action group`** |
| `build_archetype_review.py` `r[7]`, `r[8]` | read a Class as the Range and the Range as the Summary |
| `build_roster_json.py` `range(32)` | every field after `Role` off by one |

`flatten.py`'s two constants are now **derived from the header**; the archetype reads go through the existing header map. `build_roster_json.py` keeps its positional tuple, which is legitimate — it is checked against the header on load, which is what a positional map needs to be safe.

### P.7 The sheet-side lesson: an insert shifts merges *mid-batch*

`insertDimension` and the super-header merge repair **cannot share a batch**. Google applies requests in order and shifts existing merges as part of the insert, so an `unmergeCells` naming the pre-insert span (`14–24`) then addresses a range that is no longer a whole merged block, and the API rejects the **entire** batch:

```
[400]: Invalid requests[1].unmergeCells: You must select all cells in a merged range
```

Batches being atomic made that failure safe — nothing landed, verified before retrying. Split into two phases, the auto-shift turned out to be correct on both tabs (`14–24, 24–32` → `15–25, 25–33`), so phase 2 is an assertion rather than a repair. **It is kept as an assertion**, because a half-covered banner silently swallows every later write to the columns beneath it (invariant #8) and the symptom is slow to recognise.
