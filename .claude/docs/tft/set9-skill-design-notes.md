# tft-set9-skill — design notes (the full reasoning)

The **why** behind the `tft-set9-skill` schema: what was decided, and what it was decided *against*. One section per note.

The sheet's `Design Notes` tab carries the one-line summary of each of these and links here. The tab was getting paragraph-sized cells, which a spreadsheet reads badly — so the summary stayed there (scannable) and the reasoning moved here (versioned, diffable).

**Source of truth:** the one-liners live in `.claude/scripts/tft-set9-skill-modularity/data/design-notes.csv` and are pushed by `sync.py`. This file is prose and is edited by hand.

For the schema's blow-by-blow review history see [set9-skill-schema-review.md](set9-skill-schema-review.md).

---

## Note — Kayle

**Passive breakpoints corrected.**

Uses the prose-correct gates Lvl 1-5 / 6-8 / 9+, fixing the old 'lvl < 7' drift.

## Note - Ionia Bonus

**Each Ionia unit's unique per-unit bonus is modelled as a skill step.**

Encoded as Passive / Game Start / Condition = If Ionia Active, Action = Cast, Recipient = Self, Category = Buff. It doubles in spirit form per the Ionia trait (3/6/9) - that trait scaling is trait data and lives in tft-set9 -> Origins, not here.

## Note - Yasuo

**The whirlwind's Stun has no duration in the source.**

tft-set9 -> Champions -> Skill Description states the whirlwind Stuns but never says for how long. Duration (s) is left as an em-dash rather than inventing a number.

## Note - Roster

**The Hero tab covers the FULL Set 9 roster — 9.0 and 9.5, all 75 champions.**

It was 9.0-only until 2026-07-17, with Fiora, Quinn and Xayah deliberately held out. That line had
already stopped being true before it was rewritten: 5 of the 64 champions in the tab (Nilah, Miss
Fortune, Neeko, Qiyana, Silco) are 9.5-only.

The source's `Sub-Set` column says which set each champion belongs to — `9.0`, `9.5`, or `9.0 & 9.5`.
`context.py --missing` compares against it, and `EXCLUDED_95` is now empty.

## Note - Projectile vs Laser

**Delivery is told apart by WHERE the hitbox spawns and whether it TRAVELS - not by shape. There are three modes.**

PROJECTILE: spawns on the unit and TRAVELS to the target - it has a projectile speed (Homing / First hit / Pierce / Burst). LASER: spawns on the unit, NO travel - it just extends toward the target (Standard Laser / Laser Shot / Current Target Laser). SPAWN AT TARGET: spawns on the TARGET, no travel at all - nothing crosses the gap, so nothing in between can be touched (Taliyah's active). This is why Jhin is a Pierce Projectile and not a laser (his shot travels), and why Irelia's frontal hit IS a Laser Shot (it does not travel - it just appears in front of her, pierces, and lands once).

## Note - Karma

**Her 3rd cast fires 3 projectiles, and they do NOT all go to the current target.**

One at the current target, one at the enemy to its LEFT, one at the enemy to its RIGHT - spreading them is what keeps the triple-cast from being overpowered. All 3 share a single hitbox, so a target already hit is not damaged again.

## Note - Auto-Attack

**Auto-Attack is itself a homing projectile.**

It is fired at the aim target and always lands on it — the same behaviour as Homing Projectile, which is why its Collision is Target-Only. It is kept as a separate Action only because it is the unit's default attack rather than an ability.

## Note - Action Source

**CLOSED (was a known gap): the schema now records who performs an action.**

Before the Action Source column, the source had to be smuggled: Zed's Shadow into Aim Target, Azir's Sand Soldier into a fake action called 'Summon Attack'. Sejuani broke both hacks - an ALLY performs her passive - so the column was added and both were fixed. 'Summon Attack' is retired: it is just Source=Summon + Auto-Attack.

## Note - Shurima

**Shurima has NO per-unit bonus, unlike Ionia.**

Its trait is a blanket heal-and-Ascend for every Shuriman, so there is no per-champion text to encode and no Passive bonus row. The trait itself lives in tft-set9 -> Origins.

## Note - Delivery vs Shape

**The Action column fuses TWO independent things: delivery and shape.**

DELIVERY = where the hitbox spawns and whether it travels (projectile / laser / spawn at target). SHAPE = what the hitbox is (single target / pierces a line / an X-hex circle). Circle AOE aimed at Current has the SAME delivery as Spawn At Target - it spawns on the target and nothing travels - and differs only in shape. Likewise Burst Projectile = travel + first-hit + circle. A future 'Action Template' pass should split these into their own columns; for now the Action name carries both.

## Note - Freljord / Piltover

**Neither has a per-unit bonus, unlike Ionia.**

Freljord's trait is a blanket ice storm and Piltover's is the T-Hex board mechanic - no per-champion text to encode, so no bonus rows. NOTE a source discrepancy: tft-set9 -> Origins claims Piltover has 5 natural units, but the Champions tab lists only 4 (Camille is absent from the source sheet entirely). Champions is what we encode from.

## Note - Shadow Isles / Targon

**Neither has a per-unit bonus, unlike Ionia.**

Shadow Isles shields its units after 12 damage events; Targon amplifies all healing and shielding team-wide. Both are blanket trait effects with no per-champion text to encode, so there are no bonus rows. The trait numbers live in tft-set9 -> Origins. Senna is Redeemer + Shadow Isles and is entered under her Origin 2, as Ekko was under Piltover.

## Note - Maokai

**His entire stat block is N/A in the source, so Range is an em-dash.**

tft-set9 -> Champions lists Health, Armor, MR, Mana, AD, AS and Range as 'N/A' for Maokai alone. Range is the only one this schema carries, and it is left blank rather than guessed at - the same rule as Yasuo's unstated Stun duration. If the source is ever filled in, this is the cell to update.

## Note - Cone: shape vs spread

**A cone is USUALLY not a hitbox - except Kassadin's and Nilah's 'Cone AOE'.**

Kassadin's 'Cone AOE' was the FIRST real cone collider, added in the Void review at the user's call ('it's actually a hitbox shape like a cone'). It overrides the old blanket rule. NILAH is the second: 'Attacks strike in a cone, dealing damage to up to 2 additional enemies' is ONE cone-shaped hitbox, so it is a Cone AOE triggered 'On Attack'. Her row used to say Spread=Cone AND Count=1, which the sheet's own rule forbids - a single instance has nothing to arrange. That contradiction is exactly how you tell the two apart: Spread=Cone REQUIRES Count>1 (Ashe's 8 arrows). If Count is 1, a cone is a shape, not a spread. The OTHER two cone-looking things are still NOT hitboxes: Two different things LOOK like a cone: (1) SPREAD = Cone ('Spread Types') - N separate hitboxes ARRANGED in a cone, each its own projectile. Ashe's 8 arrows: each stops on the first body in ITS lane, which is why a wide Ashe cone can still miss. (2) A SWEEPING hitbox - Gwen's Sweep Laser is a LINE that sweeps sideways through an arc, and the cone is just the shape its path leaves behind. An earlier version of this note claimed Gwen's cone was a real collider; that was wrong.

## Note - Viego / bad source text

**His row deliberately CONTRADICTS the source skill description. That is not an error.**

tft-set9 -> Champions says Viego deals his damage 'to the current target'. The user confirmed the real behaviour: 'It pierce and hit everybody, the description for skill here is wrong.' So he is a Laser Shot (Pierce-All) with Recipient = Enemies in path. This is the first row where the champion's own skill text is known to be WRONG. Flagged here so nobody later 'corrects' the row back to match the bad source.

## Note - Range

**This column is a NUMBER of hexes. It used to hold Frontliner/Backliner for 35 champions.**

The header always said 'Range' but the data disagreed with it: the first 35 champions stored a POSITION (Frontliner / Backliner) and the Shadow Isles / Targon 8 stored the real hex range from the source. The user's call: the header is right, so every champion is now backfilled from tft-set9 -> Champions -> Range and the position labels are gone. WARNING: Frontliner/Backliner exists NOWHERE in tft-set9 - it was somebody's judgement and it is not recoverable. If it is ever needed again it must come back as its OWN column and never into this one. Maokai is the single value not from the source (his whole stat block is N/A there); he is 1, melee, per the user.

## Note - Stacks

**A stack counter is an Effect Detail, NOT a column. Decided - do not re-open.**

Viego's stacking On-Hit Damage, Kalista's Impale and Aphelios' Chakram are all the same shape: a counter that does nothing itself and multiplies a later effect. It was proposed as a 4th axis deserving its own column, like Action Source and Count/Spread before it. The user's answer: 'Effect sound right to me' - it stays an Effect Detail. Recorded here so the question is not asked a third time.

## Note - Mid-action change (KNOWN GAP)

**The schema describes every action as if frozen at the moment of cast. Two champions break that.**

Gwen's Sweep Laser: the HITBOX MOVES while the action runs - Delivery says where a hitbox spawns and Shape says what it is, but neither can say it travels sideways. Soraka's stars: the AIM IS RE-EVALUATED between instances (Spread = Re-picked per instance), so the target can change mid-action. Same shape of gap, twice: something changes DURING the action, and every axis we have (Delivery / Shape / Collision / Count / Spread) assumes nothing does. Two cases is not enough to justify a column. A THIRD would settle it - watch for one.

## Note - Count vs Amount

**Count is how many times the ACTION FIRES. It is not how much the EFFECT grants.**

The trap: Kalista's active reads 'impale 6 spears', and that looks like Count 6. It is not - she fires ONE projectile which lands 6 stacks on impact, so Count = 1 and the 6 lives in Amount. Compare Akshan: his 6 shots are 6 SEPARATE projectiles, each its own hitbox, each able to miss independently - that is Count 6. Ask: could one of them miss while another hits? If yes it is Count. If the number can only ever be all-or-nothing, it is an Amount.

## Note - Condition is PER-EFFECT

**Condition is NOT part of the action block. A single effect row can be gated while its siblings are not.**

Soraka forced this: one cast heals the lowest-HP ally, and heals them AGAIN if they are below 50% HP. Same action, same target, same effect - one row gated, one not. While Condition was merged across the action it could only gate the WHOLE action, so the bonus heal had to be faked as a separate step; that was a workaround for a missing capability, not a modelling decision. Condition is now per-EFFECT-ROW. It may still LOOK merged on most champions - when every effect of an action shares one condition, merging the identical value is just display. The rule is that it CAN be split, and Soraka's is.

## Note - K'Sante

**His reposition CHASES the enemy he knocked back.**

He does not leap to a fixed hex: he follows the flying body. This used to sit in the Scaling column as prose ('chases the knocked-back target'), which is not a scaling - Scaling now has a fixed vocabulary, so the fact lives here instead of in a data cell.

## Note - Step is the order within ONE CAST

**Step 0 = passive / always-on. Steps 1..N = what happens when the champion casts, in order.**

A passive is not part of the cast sequence, so it is not step 1 - it is step 0. A champion with several passives numbers them 0.1, 0.2. Steps 1..N then read as the cast itself: Yasuo 1 whirlwind, 2 dash, 3 slash, 4 slam. WARNING: steps are REFERENCED by other cells ('Step 1 Aim target'), so renumbering means rewriting whatever points at them - Yasuo's three re-aims had to move from 'Step 2' to 'Step 1' when his passive left the sequence.

## Note - Count is PER-EFFECT

**Count and Spread sit on each effect ROW, not on the action. One step can fire 1 instance or 3, depending on a Condition.**

Karma forced it: her 1st cast fires ONE burst, her 3rd fires THREE at Current + Left + Right. Everything else about the two is identical - same action, same amount, same AOE - so they were always ONE action, split into two steps only because a merged Count could not say '1 here, 3 there'. Count/Spread left the merged action block to join Condition. An em-dash means the question does not apply: a Cast or a Leap projects nothing and fires exactly once by nature. Anything that CAN fire more than once keeps a number, Summon included (Azir has 3 Soldiers).

## Note - A Step is a MOMENT, not an action

**Step = one moment in the cast. Each ROW is one branch of it: condition -> action -> effect. Two rows of one step may run DIFFERENT actions.**

Karma was the easy case - both her branches fired the same action, so only Count/Spread had to go per-row. Swain, Azir, K'Sante, Kayle and Ahri switch ACTION on the condition (Swain casts if untransformed and bursts if not; Azir summons unless he already has 3 Soldiers). So Action, Collision, Aim Target and Trigger are per-ROW too, and the 'action block' is gone. MERGING NOW FOLLOWS THE VALUES: only Step and Skill Type merge across a whole step; every other column merges wherever consecutive rows happen to agree. A merge is now a display of the data, not a claim about it - which is the only way it survives a schema where any column may differ per row. NOTE: branches are not always exclusive. Ahri's wave is ADDITIONAL to her Circle AOE, so her first branch has no condition - writing 'if not 2nd cast' there would be a lie that reads as rigour.

## Note - A second step needs a second MOMENT

**If a step's Trigger is the same event as the step above it (both 'On Cast'), it is not a step - it is another effect of the one above.**

Round 8 said a Step is a MOMENT in the cast. This is the test that falls out of it, and four champions failed it: Shen, Orianna, Jayce and Viego each had a Step 2 triggered by 'On Cast', the same instant as their Step 1. A consequence gets its own step (Jayce's burst is 'After Cast'); a simultaneous effect does not. WARNING: collapsing a step RENUMBERS the ones below it, and steps are referenced by other cells ('Step 2 Aim target'). Check those references before renumbering - round 7 left three of them dangling by not doing so.

## Note - Empowered Attack (Maokai)

**Maokai's heal is not a passive. It is what his Empowered Attack DOES.**

He had it as a separate always-on step (0.2) with an 'If Empowered' condition - which is a workaround for a missing word, not a design. As a step it claimed he heals on attack whether or not he ever cast, and the condition existed only to take that claim back. The step is gone and the behaviour moved into the effect itself. This preserves the split settled in round 2: Orianna and Maokai get ONE empowered attack, spent on the next hit; Viego's stacks forever (On-Hit Damage). Maokai's now differs in WHAT it does, not in how long it lasts.

## Note - Void

**No per-unit bonus; four novel shapes resolved with the user.**

Void's trait is a team-wide Void Egg summon with no per-champion text, so there are no bonus rows (the Freljord / Piltover / Shadow Isles precedent). Bel'Veth is Empress + Void and enters under her Origin 2, as Senna did for Shadow Isles; Empress is a single-unit trait. Four shapes the taxonomy had never seen, resolved with the user: Kassadin's cone was first modelled as a Sweep Laser but the user corrected it in review to a real hitbox, Action 'Cone AOE'; Malzahar's between-two-portals zone is a horizontal Laser Shot, 1x3 hex; Vel'Koz's splitting bolt is composed as First hit Projectile + two Pierce Projectiles with Falloff per hit; Kai'Sa's 15/15/25 missiles use the new Spread 'Split across nearest N'. Cho'Gath's devour (+35 max HP per kill) is a 4th case of Note - Stacks and is modelled as Buff / Bonus HP + Scaling Stacking, consistent with that decision.

## Note - Yordle

**No per-unit bonus; Poppy & Kled already entered under their Origin 1; 4-star modelled per user.**

Yordle's trait is a blanket miss-chance effect, no per-champion text, so no bonus rows. Poppy (Demacia / Yordle) and Kled (Noxus / Yordle) were already entered under their Origin 1, as Senna was for Shadow Isles - Yordle adds no rows for them. Heimerdinger is Technogen / Yordle and enters under Yordle as Origin 2. 4-Star Upgrades modelled at the user's request: Tristana's every-10th-attack ricochet is a conditional Step (Trigger 'On 10th Attack', Condition 'If 4-Star'); Teemo's +1 explosion radius is carried in the AOE cell ('1 (2 at 4-Star)'), the Gwen descriptive-AOE precedent, rather than a separate row. Kled's own 4-star execute is NOT added - he is a pre-existing row and that would be a separate edit.

## Note - Action model (v1 lumped -> v2 axes -> Legacy action + lookup)

**The action's mechanics live in the 'Action Model' tab, one row per action; Hero holds only the name. The five axes were per-row Hero columns for one day and moved out.**

THE MODEL: an action = Apply {DirectApply | Hitbox} - Spawn {at-User | at-Target} - Motion {- static | Projectile | Arc | Forward N hex} - Behavior {First-Hit | Homing | Pierce | Returning, Projectile only} - Shape {1-hex | circle | cone | box | custom}. WHAT HAPPENED: v2 (0db5e27) replaced the lumped 'Action' column with those five axes AS HERO COLUMNS (36 cols). One day later they were collapsed back into a single 'Legacy action' key (32 cols) pointing at the 'Action Model' tab. WHY: the axes are FUNCTIONALLY DETERMINED BY THE ACTION'S NAME - verified on all 135 action rows, 23 names, zero exceptions once Auto-Attack is split. Per-row axes were therefore ~200 rows restating a 23-row lookup, with no way to stop the two drifting apart. Normalising it means an action is DEFINED once, in the tab, and Hero references it. The v2 work was not wasted: the axes are the tab's columns. WHAT STAYS PER-ROW, and why the lookup does not swallow them: Collision (Burst Projectile is First-Hit on 3 rows and Target-Only on 1), Offset, AOE (hex) (the SIZE of a Circle AOE is per row; its SHAPE is not), Count, Spread. LOCKED DECISIONS: (1) 'Auto-Attack' is NOT an action when the champion attacks - that is a TRIGGER ('On Attack'), and the action riding on it is 'Bonus on AA' (DirectApply, Collision None). The user's call, and they were right: 'On attack do action Auto-Attack' is circular, and Warwick proves it (On Attack -> Buff/HEAL - he is not attacking). 'Auto-Attack (ranged)' now means only a SUMMON really attacking (Azir's Sand Soldier, Soraka's Child of the Star); QuickAA is its own action (Bel'Veth PERFORMS N attacks). 'Auto-Attack (melee)' is RETIRED - zero rows. This replaced an earlier melee/ranged split, which was a PROXY for the same distinction (every melee AA row was a bonus) and is why that split looked like it held. (2) Shape moves to the tab; SIZE stays in Hero's AOE (hex). (3) Collision stays a Hero column, shown in the tab for reference only - where it varies the tab reads 'per row' and the Hero cell is the truth. (4) The tab's key must match Hero's cell EXACTLY, so champion parentheticals ('Sweep Laser (Gwen)') moved into 'Clarify more'; 'Leap' and 'Leap Behind' stay two rows (same axes, different intent). ENFORCED: sync.py VALIDATE fails if any Hero 'Legacy action' has no row in the tab. The tab is now a managed tab (data/action-model.csv), not hand-edited - it was hand-made and invisible to the tooling for a day, which is precisely how a doc drifts from the data unnoticed. Supersedes 'Note - Delivery vs Shape' and 'Note - Mid-action change (KNOWN GAP)'.

## Note - Charge moves its carrier (REVERSED: was a Charge/Move split)

**Charge is the reposition AND the hitbox, as of 2026-07-17.** The split below required a paired `Move` action that **only 1 of its 3 users ever had** — Sion. Gangplank's Dreadway and K'Sante's flying body never did, and nobody noticed for as long as the rule existed.

The user: *"I don't think move+charge is neccessary anymore, just lump it to charge."*

**I argued against it and was wrong on the evidence.** My case was that the split protects K'Sante — and it does, which is why the cost below is real. But when I actually counted the rows before defending the rule, it was being followed once in three. A rule honoured 1-in-3 is not carrying its weight; it is decoration that occasionally trips someone.

**The known cost, accepted rather than hidden:** K'Sante's carrier does **not** move under its own power — his `Knock Back` throws it — and `Charge` can no longer tell that apart from Sion charging in himself. If that distinction ever earns its keep it becomes a **second action**, not a column. It is written into the `Charge` row of the Action Model tab so the next person meets it there.

The 1-in-3 count cuts both ways and it is worth being honest about that: it could equally have meant two rows were *missing* a Move. What settled it was **who** the users are — a sailing ship and a thrown body are not repositioning themselves in any sense the sheet was capturing.

---

*The original reasoning, kept because the split was right for a year and the argument still explains what `Charge` is:*

**'Charge Into' and 'Knock Back' each hid a second action. Charge = a hitbox carried on a unit; Move = the reposition. The carrier need not be the caster.**

The user, on Sion: 'It should be 2 action combine: 1) Charge: apply hitbox on the user, if the user move into them, they're hit. BUT doesn't specify that using this make him move. 2) Move: make Sion move toward target hex.' Right - and the name 'Charge Into' was hiding the move inside it. K'SANTE IS THE SAME SHAPE and it is how the last Collision disagreement in the sheet got found: the Action Model tab said Knock Back = None (he is DirectApply - HE projects no hitbox) while the Hero row said Pierce-All. Both were right about a different half, which is the tell that one row was doing two jobs. The FLYING BODY is the hitbox, not K'Sante. So: Knock Back (DirectApply, None) smashes the target; a separate 'Charge' whose Action Source is 'Knocked-back enemy' hits everyone in the path. 'Charge' therefore has TWO carriers - Sion himself and K'Sante's victim - which is what makes it a real action rather than one champion's ability. Its Aim Target is '—' (an existing legal value, NOT a new one): the flying body does not aim, it goes where it was smashed. Motion on Charge is '—': the hitbox does not move ITSELF, its carrier does. That retired the 'Forward 3 hex' Motion value, which only Charge Into ever used.

## Note - Trigger Types tab

**The trigger vocabulary is a tab, and sync VALIDATE enforces it - a trigger cannot be invented without adding a row first.**

The user: 'I don't want you to add some random trigger. So let's make its own tab, so we know what trigger currently we have.' Parked for a day ('Don't do this yet'), then built. THE TAB IS NOT THE POINT - the ENFORCEMENT is: a list nobody checks drifts, which is exactly what happened to the Action Model tab while it was hand-maintained and invisible to the tooling. sync.py VALIDATE now fails on any Hero trigger with no row in 'Trigger Types', so the vocabulary cannot grow by accident. Seeded from the 27 triggers actually in use, never invented. Column Explain's Trigger cell used to list them by hand; it now points at the tab, because two copies of one vocabulary is how they drift apart. WARWICK named the subtle one: 'After Cast' means IMMEDIATELY after the cast animation (9 champions), but his stun waits out a 2.5s buff ('Gain 100% AS for 2.5 seconds. THEN, stun'), so it is 'On Cast Expire' - joining the existing On Shield Expire / On Bonus-HP Expire family. Leap->Move also renamed the trigger 'After Leap' -> 'After Move' on 7 rows; the Skill Description source text still says 'Leap' and is deliberately untouched.

## Note - Cast (s) sits in the Action block

**Cast time is an element of the ACTION, so its column lives at the end of Hero's Action block (after Collision) and merges per action. It is NOT in the Action Model tab.**

The user: 'Move this one inside "Action" tab too' - which I read as the Action Model TAB and acted on. Their correction: 'This isn't what I meant. I mean to move Cast inside a Action column inside Hero tab. The cast is one the element in each action, but it was rarely specify most of the time.' The complaint was POSITION, not ownership: Cast (s) was Hero's LAST column, marooned past the whole effect block, so it read as a property of the effect. It now closes the ACTION region and the 'Action' super-header covers it. Their earlier 'Cast is determine by action, we just didn't assign it yet' still holds and never conflicted: the cast time IS decided by the action, and most are unassigned - but that does not make it stop being a per-row column, because a Hero row IS an action instance. MERGED per action (it joined RUN_COLUMNS): '—' on an action-start row, blank on continuations, so one action shows one Cast cell however many effects it has. WHAT THE ROUND-TRIP THROUGH THE TAB COST, and why it is worth recording: while it lived in the tab, the three assigned times went ACTION-WIDE (Galio's 2s became every Cast's). Reverting restored them per-row from the last committed hero.csv - Galio 2, Garen 4, Lux 3, everything else '—'. Nothing was lost, but only because git had it.

## Note - AOE (hex) is a KEY, not prose

**Every AOE (hex) cell names a row in the 'AOE shape' tab: Circle N hex / Cone N hex / Box WxD. Cone N = widest 2N+1, depth N+1.**

The user: 'It is time we assign the meaning of AOE (hex) for each AOE shape. Make a new tab AOE shape.' The column had rotted into prose - '4 (1 hex at range 1, 3 at range 2)', '1x3 (horizontal)', 'X-shape', and 'Gwen-shaped', which was a POINTER to another champion's cell. No two cells said the same thing the same way. sync VALIDATE now fails on an AOE with no tab row, so it cannot drift back. NOTATION (the user's, confirmed): Cone N hex = widest row 2N+1, depth N+1 - so N is the spread to each side at the far edge, NOT the reach and NOT the total. Kassadin's old prose already described exactly Cone 1 hex, which is how we know the notation fits the data rather than replacing it. Box WxD = width x depth, hori x verti; FRACTIONS ARE REAL (a wave is 1.5 wide, Gwen's blade 0.1). IT IS THE HITBOX, not the area a moving hitbox covers: Gwen's blade is Box 0.1x2 even though her sweep traces a cone - the sweep is Motion=Arc on the action, not a shape (the user's call: 'keep Sweep Laser, just fix the AOE').

## Note - Wave is back (and why it is not a duplicate)

**Sona is a Wave: pierces like a Pierce Projectile but is a BOX (1.5 wide). Retired once as a duplicate - which it was, before Shape existed.**

Her source says 'Send a WAVE at the clustered enemy', and a wave is wide. She was modelled as a Pierce Projectile, whose Shape is 1-hex - a bolt - so her AOE '2' was a width the model had nowhere to put, contradicting its own action. The old note said 'Pierce Projectile replaced the old Wave, which was a duplicate of it': TRUE AT THE TIME and false now. That merge happened before Shape was an axis, when the two were identical; with Shape they differ exactly as a bolt differs from a wall of sound. This was the FIRST row that threatened the rule the whole lookup rests on - an action determines its own axes (135/135 rows). Bending it for Sona (Shape 'per row' for Pierce Projectile) would have made the tab lie about her. A second action costs one row and keeps the rule; the user chose that.

## Note - Teemo, and star-varying AOE

**A star-varying AOE is not a value - it is two BRANCHES of one step, gated by Condition. Teemo: 'If not 4-Star' -> Circle 1 hex, 'If 4-Star' -> Circle 2 hex.**

His AOE read '1 (2 at 4-Star)', which no single key can be, so it blocked making AOE a strict vocabulary. The user's answer sidestepped the notation problem instead of encoding around it: 'add new step 1 as alternative when he is 4 star, so he can set his AOE properly'. That is the shape the sheet ALREADY uses for alternatives - one Step is a MOMENT and its rows are branches (Swain transformed/not, Azir 3-soldiers/not, Karma 1st-2nd/3rd cast) - and 'If 4-Star' was already a Condition. Worth remembering the general form: if a cell needs an 'except when...', the except is usually a branch, not a parenthetical.

## Note - a cone anchors at its REAR edge

**Cone AOE Offset is 'rear edge', not 'front edge'. The origin sits at the narrow end and the shape grows away from it.**

The user, with the picture (xxx / x / o): 'Cone AOE should use rear edge too.' Every Cone row said 'front edge' because the Offset legend DEFINED 'front edge' as 'origin at the front - e.g. a cone projecting forward', using a cone as its own example. That example was the error, and it taught the mistake to every row that followed. 'rear edge' already meant 'origin at the back edge, shape extends forward', which is a cone exactly. 'front edge' now means origin at the FRONT with the shape extending BACKWARD, and has no user - kept as a legal anchor, not deleted.

## Note - Collision left Hero

**The ACTION decides the Collision; Hero has no such column.**

It was kept per-row for a REAL reason: `Burst Projectile` was `First-Hit` on three rows and `Target-Only` on one, which no per-action lookup can express. That last exception was **Urgot** — and he turned out not to be a Burst Projectile at all, but a Cone AOE ("fire a blast from the leg facing that direction"). With him moved, every action has exactly one Collision, so the column was restating the Action Model tab on all ~200 rows: the same drift risk the five axes had.

**If a future champion breaks it, they get their own action** — exactly how `Wave` and Nilah's `Cone AOE` happened. An action is a bundle of mechanics; a champion whose mechanics differ has a different action. That is the model working, not failing.

`collision-types.csv` stays: the Action Model tab's Collision column uses it, and `validate_data()` now checks *that* — a tab-against-tab check (`TAB_VOCAB`), new because with no Hero column left, nothing else would notice the taxonomy rotting.

## Note - sequencing is 'After Step N'

**A trigger names the STEP that must finish first, never an ability's flavour name.**

The user asked which triggers only one hero uses. The list found something sharper: the real test is whether `After X` names the **preceding step's action**. Six rows failed it — and two used *popular* triggers, which a one-hero test would never have caught:

| row | said | preceding step actually was |
|---|---|---|
| Yasuo step 2 | `After Whirlwind` | `Pierce Projectile` |
| Yasuo step 4 | `After Slash` | `Cast` |
| Shen step 2 | `After Shielding Allies` | `Cast` (it named the EFFECT) |
| Poppy step 2 | `After Cast (return)` | `Homing Projectile` |
| Aphelios step 2 | `After Cast` | `Homing Burst Projectile` |
| Qiyana step 2 | `After Move` | `Move Behind` |

`Whirlwind`, `Slash` and `Shielding Allies` are not actions, not effects, not anywhere in the sheet — flavour names for one champion's ability, which nothing could ever validate.

**Why not just fix the six to name their real action?** Because `After <Action>` cannot be a rule: nine champions run the same action in two different steps (Yasuo casts at step 0 *and* step 3), so `After Cast` is ambiguous for them by construction. A step number is not, and it reuses a referencing pattern the sheet already had — Aim Target's `Step N Aim target`. Eight triggers collapsed into `After Step N`.

## Note - Trigger = WHEN, Condition = ONLY-IF

**Never pack a state gate into the trigger. Sejuani and Kalista did; they are split now.**

Column Explain has said `Trigger = when; Condition = only-if` all along, and two rows broke it by welding the gate into the event:

- `On Ally Attack Chilled Enemy` → `On Ally Attack` + `If Target Chilled`
- `On Spears Lethal` → `On Attack` + `If skill can execute`

Split, both are ordinary rows built from vocabulary that already exists, and both triggers retire. The user's wording for Kalista's gate — *"If skill can execute"* — is better than the existing `If Kills Target`: it describes the skill's own gate rather than the outcome.

## Note - Design Notes live in the repo

**This tab keeps one-liners. The reasoning is in `.claude/docs/tft/set9-skill-design-notes.md`.**

The user: *"This tab is such a mess. Do we need this?"* — and it was, because the `Detail` column had grown paragraph-sized cells, which a spreadsheet displays badly. The notes themselves were asked for (*"put it in their own tab"*) and are worth keeping; the medium was wrong. So the decision stays visible while you read the sheet, and the argument behind it is one click away, in git, diffable.

## Note - a projectile and its burst are 2 parts

**The projectile has its own shape; the AOE it bursts into is a SEPARATE step. `Burst Projectile` hid the second one.**

The user: *"The projectile should have its own shape. NOT the shape of it bursting into AOE (Burst Projectile). It is 2 different part."*

This corrected a real error. Having found that `Wave` = `Pierce Projectile` + a box shape, I generalised it wrongly and read `Burst Projectile` as `First hit Projectile [Circle AOE]` — i.e. the projectile **is** a circle. It is not: it is a 1-hex bolt that **explodes into** one. Two hitboxes, one after the other.

**The conflation was already in the sheet.** `AOE (hex)` meant *the hitbox itself* for 8 actions (Circle AOE's circle, Gwen's blade, Malzahar's beam) but *the burst* for the 3 Burst ones — where the projectile's own 1-hex shape had nowhere to live at all.

**The split uses a pattern the sheet already had.** Vel'Koz was already modelling a projectile's impact as its own step:

```
step N    the projectile flies     AOE = its own shape   -> Movement/(setup)
step N+1  On Projectile Hit        AOE = the burst       -> the real effect
          src 'Step N Projectile'  Circle AOE
```

So `Burst Projectile` and `Homing Burst Projectile` retire. A name that hides a second hitbox is the same bug as `Wave` (a name hiding a shape) and `After Whirlwind` (a name for a step that isn't there).

**`Wave` retires too — and note the model was never wrong.** Wave was correct while Shape was per-ACTION: a box-shaped pierce genuinely needed its own action then. Now that a projectile's shape is per-row (`specify elsewhere`), the row carries it and Wave has nothing left to say. Sona is `Pierce Projectile` with `AOE = Box 1.5x2`.

**Teemo came out better.** His 4-star branch was on the projectile, but his upgrade is *"increase the **explosion** radius by 1 hex"* — so it belongs on the burst. After the split he fires one projectile and the branch sits where the difference actually is.

`Movement/(setup / daggers)` became `Movement/(setup)`: the delivery rows need it, and Katarina's daggers had no business being in the vocabulary — the same smell as `After Whirlwind`.

## Note - a delivery row applies nothing

**A projectile's own row reads `—` for its effect. It exists to hit; the burst that follows does the applying.**

The user: *"Movement in Effect is misleading. Get rid of it. Just put - inside. This projectile purpose is to hit the enemy, no effect apply."*

When the burst was split out, the projectile row needed *something*, and `Movement/(setup)` was the nearest existing thing — Effect Types even defines Movement as "a movement / setup step with no direct effect". But a projectile is not movement, and the cell was claiming a category it does not belong to. `—` says the true thing: **no effect**. Blank would be wrong, because blank means "same as the row above".

`validate_data()` skips the `(—, —)` pair for this: a row that applies nothing is not an undefined effect.

**Katarina keeps `Movement/(setup)`** (the user's call). Her step 1 looks the same shape — a `Cast` that applies nothing — but she really does throw something, so the setup is a real act rather than an absence. It leaves `(setup)` with one user, which is a smell worth remembering, but a one-champion effect is not the same mistake as a one-champion *vocabulary term* like `(setup / daggers)` was.

## Note - Karma's duplicate step (a bug this sheet is built to catch)

**Both of Karma's branches carried `Step = 1`, so they never merged — and her `Legacy action` cell showed empty.**

Invariant #2, committed by the migration that split her burst: it copied `Step` onto both branch rows. `remerge_hero` finds step boundaries by looking for a non-blank `Step`, so the second branch read as a NEW step; the two never merged into one block; and her second row's blank `Legacy action` — blank because it should inherit the row above — had nothing to inherit from. The user saw it as two bugs ("duplicate step 1", "this one is empty"); they were one.

The fix is one cell: blank `Step`/`Skill Type` on the branch row. **Never fill `Step` on a continuation row** — it is the one column whose blankness is load-bearing.

## Note - Zone AOE: a hitbox that stays

**Damage from BEING somewhere (`Zone AOE`) vs from HAVING BEEN HIT (`Circle AOE` + a status). The action says which the duration means.**

The user: *"Silco's skill make the hex become poison, enemy who stand on it take damage every 1 sec. But for Teemo, he throw a Circle AOE, enemy who get hit by the AOE become posion and take damage every 1 sec until the duration is expired."*

The difference is real and **testable**: walk out of Silco's chemicals and the damage stops; walk away from Teemo's poison and it keeps ticking, because that one rides on *you*. Silco's hitbox persists; Teemo's fires once and leaves a status behind.

**The sheet could not say which.** Both read `Circle AOE + Every Ns + duration` — and that duration silently meant two different things: the HITBOX's life for Silco, the VICTIM's status for Teemo. The same class of bug as `AOE (hex)` meaning both the hitbox and the burst it becomes.

`Zone AOE` fixes it **at the action**, which is where every other hitbox property already lives. No column has to carry the distinction:

```
Circle AOE (fires once) + an over-time effect  ->  the duration is the VICTIM'S status
Zone AOE   (persists)   + an over-time effect  ->  the duration is the ZONE'S life
```

**Teemo needed no change.** He was already right; only the ambiguity around him was wrong.

**And it was not just Silco.** Garen (*"spin like a beyblade for 4s"*) and Swain (a pulsing aura while transformed) are persistent hitboxes too, both wearing `Circle AOE`. A Zone's `Effect Recipient` is re-evaluated every tick — that is the whole point of it.

Silco also got the projectile split he was missing (*"Throw a vial"*): he is the same shape as Teemo — a projectile, then the thing it becomes — and the vial was not in the sheet at all.

**Flagged, not fixed:** Garen's cadence is `Every spin`, a flavour word where every other cadence is a real interval, and his source never states one. The user's call: leave it rather than invent a number.

## Note - a blank identity cell inherits the champion above

**sync's `fill_down` was whole-column, but an identity merge stops at the champion. It gave Illaoi the class of the champion above her.**

`sync_hero` compares merged columns by their EFFECTIVE values (blank = "same as above") and writes the filled value, letting the re-merge absorb the duplicate. That is right for the run columns, whose merges run down the whole sheet. It is **wrong for the identity block**, whose merges are bounded by the champion — `remerge_hero` merges `IDENTITY_BLOCK` from one champion-start to the next.

So a champion with genuinely no `Class 2` has a blank cell, and a whole-column fill_down read it as "same as above" and handed them the **previous champion's class**.

**It hid for the entire life of the sheet**, because for a champion already on the sheet both sides fill down identically and nothing is written. It only fires on an APPEND, where the sheet has no row yet: the two sides disagree and sync writes the filled value. Adding the 11 Set 9.5 champions gave Illaoi Graves' `Gunner`, and six champions Gangplank's `Reaver King` and Naafari's `Shurima`.

**Only the export round-trip catches this.** Sync reports 0 afterwards (the sheet equals what it wrote), and VALIDATE reads the CSV, not the sheet. Fixed: `fill_down(seq, starts)` resets at each champion for the identity block.

## Note - Delayed Blast (Twisted Fate)

**The bomb rides the VICTIM. `Action Source` is the `Delayed Blast` itself — not the caster, and not the victim, who does not explode.**

The user: *"Self doesn't sound right for Step2. It more like he attach bomb on you and that bomb explode 1.25 second later. Step1 attack target + give them explode status. Step2 the souce target explode."*

His step 2 was sourced from `Self`, which put the blast on **Twisted Fate**, four hexes away from where it actually goes off. The question this asks is the **same one Zone AOE vs Circle AOE asks**, and it is testable the same way: *where does it land if the victim moves during the 1.25s?* The cards are stuck to them, so it follows them.

Step 1 now applies `Status / Delayed Blast` — a new Effect Type. It is not `Mark` (a mark does nothing by itself; this one goes off).

**Then the user sharpened it again:** *"This is kinda confusing, use 'Delay blast' instead here."* — against `Step 1 Aim target`, which I had put in the source. They were right, and the reason is worth keeping: `Step 1 Aim target` names the **victim**, so the row read *"the victim explodes"*. The victim does not explode; **the bomb does**, and the victim is merely what it is stuck to. Source now names the thing that **acts**, exactly as Graves and Silco already did with `Step 1 Projectile`.

**The fuse lives in `Amount`, alone** (the user's call). It had briefly been in three cells — the status' `Amount`, its `Effect Duration`, and step 2's `Cast (s)` — all necessarily the same number, so they could only ever disagree by typo. The other two are `—`.

## Note - a summon that holds no hex

**`Summon (untethered)` (Spawn `—`): Naafiri's packmates float and occupy NO hex.**

The user: *"Where it was spawned, maybe is confusing. Because those summon just float around and didn't belong to any hex… Naafiri cast ability on target, summon 3 wolf, each wolf float around, then charge into target and deal damage."*

`Summon`'s Spawn is `at-Target`, so the sheet was saying **the wolves appear on the victim's hex**. But `at-User` is just as wrong: they are not on Naafiri's hex either. **Both values assume the summon takes a hex**, and these take none.

Hence a second action with `Spawn = —`, and `Aim Target = —` for the same reason: there is no hex to name.

**The `at-Target` decision stands** — it was the user's call, twice (`159caa8`), and it is right for summons that *do* occupy a hex (Azir's Sand Soldier). This is not a per-row exception to it: being ungridded is a property of the **action**, so it gets its own action. Same shape as `Wave` and Nilah's `Cone AOE`.

## Note - X [collision=Y] is a NAME, not a syntax

**An override rides in the action's own name and is a REAL Action Model row.**

The user, on Naafiri's wolves: *"The pierce all can be overwrite, but don't add new column, just put it in the same cell, 'Charge [collision=homing]'."* And their reason, which is the important half: *"the only reason I don't like putting collision column in hero tab is it was most of time useless."*

That is not an objection to per-row collision *information* — it is an objection to a **column that is redundant on ~200 rows**. So the exception rides in the action's name instead, and `Charge [collision=Target-Only]` is an actual row in the Action Model tab. Hero's cell stays a plain key; **nothing in the tooling had to learn a mini-language**; VALIDATE keeps working unchanged.

It is really the existing rule — *a champion whose mechanics differ from its action's gets its own action* — wearing the user's syntax. And their name is **better than an invented one**, because it says what it overrides instead of hiding it. (`Wave` and `Burst Projectile` were both retired for hiding things.)

**One correction to the proposal:** `homing` is not a Collision — it is a *Behavior*, and only for `Motion = Projectile`. A Charge is not a projectile. The collision meaning what they described is `Target-Only`: *"ONLY the unit being aimed at — nothing else on the way is touched."* The wolf tracking its target is already said by `Aim Target`.

**The cost, and its guard:** the name states the collision twice — in the name and in the row's own `Collision` cell — which is exactly the two-copies-of-one-fact trap. `validate_data()` therefore checks that a `X [collision=Y]` row's Collision cell **is** Y, and that `X` is a real action. Both were tested against a deliberately drifted row.

**A truly parsed override** (strip the brackets, validate the parts, allow it on any action) is a small step from here — but it would reopen the per-row axis overrides that v2→v3 deliberately closed, so it needs a reason.

## Note - Gilgamesh Projectile (Xayah)

**Her feathers are ranked BEHIND her (`Offset = rank -1`) and fan out through the target. It is its own action.**

The user: *"she create the projectile behind her back that line up in a row (projectile didn't create at herself)… Then each projectile is shoot at target and pierce through him. And potentially… it could hit several enemy behind the target."*

This one went through **both** modelling rules and is worth reading as a pair with them.

**First: an existing axis beats a new action.** I proposed a whole new projectile action. The user said use `Offset` — and they were right. `Offset` is precisely the column for *"the hitbox is not at its derived centre"*, and it already had an unused `detached +N` in its legend for exactly this kind of displacement. No new action needed.

**But the value could not be per-row, and that is the second rule.** `Pierce Projectile` **fixes** its Offset at `centred`. A per-row `rank -1` on Xayah was therefore **not an override — it was a contradiction**: it made the tab lie about Jhin, Sona and Quinn, who really are centred. The user reached the same place from the visual side — *"since how it look visually is so different from the other"* — and named it.

**So the general rule: before putting a value in a Hero cell, check whether the action FIXES that axis.** If it does, the row cannot override it; the champion needs their own action. `Spread` could not carry it either — Spread says where the instances **go** (they all converge on the target), and this is where they **start**.

**Why the rank is data and not decoration:** each feather starts in a different slot and they all converge on ONE target, so they arrive at different angles and carry on through at different angles — a neat rank **fans out** behind the target. That is testable, which is what earns it a place.

## Note - Offset is a KEY, not prose

**The anchor vocabulary is a tab (`Offset Types`), and VALIDATE enforces it.**

Offset was the **last geometry column with no reference tab**. `AOE (hex)`, `Trigger`, `Spread`, `Effect Recipient` and `Scaling Type` all had one; Offset had a legend buried in the Action Model tab's footer and nothing checking it.

It nearly got prose. The user, on Xayah: *"Could we just set Offset = spawn projectile behind her, and line them up in a row."* Half of that was right and better than my proposal (see Gilgamesh Projectile). The half that was not is the sentence itself:

- **Prose in an unchecked column is how `AOE (hex)` once held `Gwen-shaped`** and `4 (1 hex at range 1, 3 at range 2)`. Offset held exactly three clean values across every row that stated one — a sentence would have been the only prose in it, and nothing would ever have caught it.
- **It welds two facts into one cell**: where one hitbox starts, and how N of them are arranged. That is `On Ally Attack Chilled Enemy` again.

So the value is a **term** — `rank -1` — and the tab exists. Precedent for a single term naming an arrangement: `360° radial` in Spread Types. **When a column takes prose, the real bug is that it has no tab.**

`TAB_VOCAB` also checks the Action Model tab's **own** Offset column, because most anchors live there now and Hero's check cannot see a value no Hero row uses (`rank -1` is used by the action, not by a row).

## Note - who states the geometry ('—' vs 'default' vs 'unknown')

**Three different facts get three different values. While two of them shared the em-dash, no check could exist.**

The user: *"Isn't it better to use 'default' than the '-'?"*

This is the best call of the round and the reasoning generalises. I had adopted a rule — *if the action fixes the anchor, the Hero cell says `—`* — which was the majority convention already (~12 actions followed it; `Cone AOE` and `Charge` were the stragglers). **But it was unenforceable**, because `—` already meant *"this action projects no hitbox at all"*. One symbol, two facts:

| Action Model says | Hero cell must say |
|---|---|
| `—` (projects no hitbox) | `—` |
| a fixed value (Offset) / `1-hex` (Shape) | `default` |
| `per row` / a shape needing a size / `specify elsewhere` | a real value — or `unknown` |

**A row that had lost its size read identically to a row that never needed one.** Split them and the mapping is exact in both directions, so `validate_data()` can check every hitbox row — which it now does, for `Offset` and `AOE (hex)` alike, tested four ways.

**It found 13 bad rows immediately**, all pre-existing:

- **10 hitboxes with no size at all** — Swain's circle, Irelia's and Senna's and Viego's beams, Ahri's circle and wave, Kayle's wave, Nilah's cone and line. The sheet had been asserting *"these have no hitbox"*, which is **false**, in the one symbol that guaranteed nobody would ask.
- **2 summon bolts** (Azir, Soraka) → `1-hex`, the documented default projectile.
- **Sett's Grab & Slam** → `Box 3x1`, centred (the user: *"3x1, center at self"*). Not a gap at all: the tab was right and the row was empty.

**`unknown` is an admission, not a shape.** Those 10 sizes are simply not in the source — Swain *"deal circular AOE damage"*, Senna *"fire a massive beam"*, Nilah *"strikes in a line"* — and inventing numbers is the one thing this sheet has consistently refused (Yasuo's stun, Garen's cadence, Maokai's stat block). Now the gap is **visible on the tab** instead of hiding behind a symbol that means "not applicable", and closing one is editing a cell.

**The lesson, general form: when a rule cannot be checked, suspect the vocabulary before blaming the discipline.** `Cone AOE` and `Charge` did not drift because anyone was careless; they drifted because nothing *could* notice.

Also fixed here: `Custom AOE` had the inverse bug — the tab said `—` (no anchor) while its only Hero row said `centred`. It is `per row`, which is what it always meant.
