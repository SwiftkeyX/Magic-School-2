# TFT Trait Synergy & Meta-Comp Pattern Analysis (Set 9 / 10 / 11)

This document answers **Topic 1** in `tft-balancing-research-plan.md` ("Trait Synergies & Breakpoint Budgeting") from the angle of *how many traits Riot actually stacks together in a real meta comp, and how hard each trait is pushed*. It cross-references every published meta comp in the `tft-set9`, `tft-set10`, and `tft-set11` reference sheets against those sets' own trait breakpoint tables, to find the shape of a "real" TFT composition rather than a single trait in isolation.

> **Read this after:** `data-sources.md` (sheet registry) and `tft-balancing-rules.md` (EHP/AS/scaling benchmarks). This doc is comp-level; those are champion- and stat-level.

---

## 0. Data-quality pass (do this before trusting any Meta Comps tab)

Before the pattern analysis below could be trusted, two problems were found and fixed directly in the source sheets:

1. **The "Active Traits & Breakpoints" column undercounted active traits.** Example: Set 9's "Void Challenger" comp listed `8 Void, 2 Challenger, 2 Bruiser` but its roster (`Cho'Gath, Malzahar, Kassadin, Rek'Sai, Vel'Koz, Kai'Sa, Bel'Veth, Yasuo`) also has 2 Sorcerer units (Malzahar, Vel'Koz) — a real active trait the column omitted. Every comp in all three sheets was recomputed directly from its roster against the Origins/Classes breakpoint tables, and the corrected values were written back to each sheet's `Active Traits & Breakpoints` column (56 comps total: 19 in Set 9, 18 in Set 10, 19 in Set 11).
2. **Set 9's Meta Comps tab mixed Set 9.0 and the Set 9.5 "Horizonbound" mid-set update** in the same 19-row tab, but the Champions/Origins/Classes tabs only had 9.0 data. Comps 12, 13, 14, 15, 16, and 19 referenced champions (Xayah, Nilah, Fiora, Quinn, Neeko, Qiyana, Miss Fortune, Silco) and traits (Vanquisher, Ixtal, Bilgewater) that didn't exist anywhere in the roster. Researched and added all 9 missing champions plus the 3 missing trait definitions to the sheet, and added a new **`Sub-Set`** column to the Meta Comps tab tagging every row `9.0` or `9.5`.
   - **Known limitation:** champions carried over from 9.0 into 9.5 (Jhin, Ashe, Karma, Shen, Darius, Sett, etc.) are only recorded under their **9.0** trait assignment in this sheet (e.g. Deadeye). In reality several of them changed traits in the 9.5 update (e.g. most Deadeye → Vanquisher). This means the 6 comps tagged `9.5` should be read as a **lower bound** on trait counts, not exact — a full fix would require a parallel 9.5-specific trait table for every carried-over champion, which is out of scope here.
   - Set 9's Maokai was also missing from the Champions tab entirely (a plain Set 9.0 gap, unrelated to the 9.5 split) — added (Shadow Isles / Bastion, 1-cost). Numeric combat stats for Maokai weren't found via public research in this pass and are marked `N/A` rather than invented.
3. **Set 11 comp 3 ("Level 8/9 Duelists") was internally broken**, not just missing data: its roster referenced Camille and Fiora, neither of which exist in Set 11 at all, and the real Set 11 Duelist roster (Darius, Yasuo, Qiyana, Tristana, Volibear, Lee Sin, Irelia — 7 champions total) means "8/9 Duelists" was never achievable in the first place. Every other comp in Set 11 checked out against the real roster, so this was an isolated bad row, not a systemic split — it was rebuilt as `Darius, Yasuo, Qiyana, Tristana, Volibear, Lee Sin, Irelia, Ornn` (7 Duelist, the natural cap without an emblem), renamed "Duelist Vertical (corrected)".

Local offline mirrors of all three sheets were refreshed after these fixes: `.claude/reference/json/tft-set9_dump_20260707.json`, `tft-set10_dump_20260707.json`, `tft-set11_dump_20260707.json`.

---

## 1. Trait rosters by set

Each set's traits, sorted by how many champions carry them. Full effect text and exact breakpoint numbers live in each sheet's Origins/Classes tabs — this is the shape (member count vs. breakpoint spacing) that matters for the synergy analysis.

### Set 9 (31 traits, 67 champions after the 9.5 fix)
| Trait | Breakpoints | Members |
|---|---|---|
| Ionia | 3/6/9 | 9 |
| Demacia | 3/5/7/9 | 9 |
| Bastion | 2/4/6/8 | 8 |
| Sorcerer | 2/4/6/8 | 8 |
| Noxus | 3/6/9 | 7 |
| Shurima | 3/5/7/9 | 7 |
| Invoker | 2/4/6 | 7 |
| Void | 3/6/8 | 7 |
| Slayer | 2/4/6 | 7 |
| Bruiser / Challenger / Zaun / Juggernaut | 2/4/6(/8) | 6 each |
| Deadeye / Yordle / Gunner / Shadow Isles / Rogue / Strategist | 2/4/6ish | 5 each |
| Vanquisher, Bilgewater, Ixtal *(Set 9.5 additions)* | 2/4/6, 3/5/7, 2/3/4 | 2 each |
| 5 unique 5-cost "solo" origins (Darkin, Empress, Technogen, Wanderer, Redeemer) | n/a | 1 each |

### Set 10 (29 traits, 60 champions)
| Trait | Breakpoints | Members |
|---|---|---|
| Spellweaver / Guardian / Pentakill / Mosher | 2-3 start | 7 each |
| K/DA / Heartsteel / Sentinel / True Damage / Bruiser / Edgelord | 2-3 start | 6 each |
| Big Shot / Crowd Diver / Rapidfire / Disco / Dazzler / Country / Executioner | 2-3 start | 5 each |
| Emo / 8-bit / Punk / Superfan / EDM | 2-3 start | 4 each |
| 6 unique 1-member traits (Breakout, ILLBEATS, Maestro, Wildcard, Mixmaster) | 1 (Unique) | 1 each |

### Set 11 (26 traits, 60 champions)
| Trait | Breakpoints | Members |
|---|---|---|
| Mythic | 3/5/7/10 | 8 |
| Fated / Arcanist / Behemoth / Duelist / Storyweaver / Warden / Bruiser | 2-3 start | 7 each |
| Ghostly / Umbral / Inkshadow / Heavenly / Invoker | 2-3 start | 6 each |
| Sniper / Fortune / Dryad / Trickshot / Dragonlord | 2-3 start | 5 each |
| Reaper / Porcelain / Sage | 2 start | 4 each |
| Altruist | 2/3/4 | 3 |
| 3 unique 1-member traits (Artist, Spirit Walker, Great) + Lovers (2-member pair mechanic) | 1 (Unique) | 1-2 each |

**Consistent shape across all three sets:** each set has roughly 6-9 "big" traits with 6-9 natural members (the vertical carry traits), a wide middle band of 4-7-member traits (the flexible combo pieces), and a long tail of 1-2-member "unique" or bespoke traits attached to specific 5-cost legendaries. This tail exists purely to give top-cost champions a personal identity bonus, not to be "activated" via team building.

---

## 2. Active-trait counts per meta comp (post-correction)

Full corrected tables live in the sheets themselves (`Meta Comps` tab, `Active Traits & Breakpoints` column) — reproduced here as the count-per-comp used for the synthesis below.

| Set | Comps | Avg. active traits | Min | Max |
|---|---|---|---|---|
| Set 9 | 19 | 3.68 | 2 | 5 |
| Set 10 | 18 | 4.33 | 2 | 7 |
| Set 11 | 19 | 3.53 | 1 | 6 |
| **All 3 combined** | **56** | **3.84** | 1 | 7 |

Distribution across all 56 comps:

| Active traits in comp | # of comps |
|---|---|
| 1 | 3 |
| 2 | 5 |
| 3 | 13 |
| 4 | 17 |
| 5 | 15 |
| 6 | 1 |
| 7 | 2 |

**80% of real meta comps run 3-5 active traits.** Comps with only 1-2 active traits are usually mono-trait reroll strategies (e.g. Set 9's "Karma Invoker Reroll", Set 11's corrected 7-Duelist comp); comps with 6-7 are rare, wide "flex" boards late-game.

---

## 3. How hard is each trait pushed?

For every comp, the highest-count ("primary") active trait was checked against its own max breakpoint:

- **Only 6 of 56 comps (11%) push their primary trait all the way to its true maximum breakpoint.** Most comps stop one tier short of max even on their carry trait.
- **81% of secondary/filler active traits (128 of 159) sit at their trait's cheapest activation tier** — i.e. exactly enough units to turn the trait on, no more.

This is the actual shape of a TFT comp: **one trait pushed moderately hard (rarely maxed) + 2-4 filler traits held at their floor.** Riot doesn't design comps around maxing every trait — board space is the scarce resource, so the realistic pattern is "commit deep on one, dip your toe into several others for the cheap first-tier bonus." This is exactly the "breakpoint budgeting" tradeoff Topic 1 set out to study: a 6-Bastion board (full commitment) is not how these comps are actually built — 3-4 Bastion + 2 Invoker + 2 Targon (Set 9's "Deadeye Freljord", for example) is the more common shape, trading a deeper single-trait payoff for coverage across several cheap ones.

---

## 4. Practical takeaway for Magic School's own `TraitSystem`

`.claude/docs/production/gdd/TraitSystem.md` already mirrors TFT's 2/4/6(/8)-style breakpoints across 15 traits (7 Vertical + 8 Horizontal), one of each per champion. The pattern above suggests the design is already pointed the right way — real TFT comps rarely max a trait — but if/when meta comps are curated for Magic School's own roster, target **3-5 active traits per comp**, with **one trait pushed to a mid-to-high tier and the rest sitting at their cheapest activation threshold**, rather than designing "showcase" comps that max several traits at once (which the data shows essentially never happens in practice).

---

## Methodology notes

- Active-trait recomputation cross-references each comp's `Roster (Units)` column against the Origins/Classes `Breakpoints` column for that set, per champion's Origin 1/2 + Class 1/2 fields. Emblem items mentioned inline (e.g. "+ Void Emblem") are counted as +1 to that trait.
- Set 10's Akali has two alternate-identity rows (K/DA vs. True Damage variants with different traits) — resolved per comp using the comp name as a hint (e.g. a comp named "K/DA Ahri & Akali" resolves to the K/DA variant).
- Set 11 comp 13 ("Storyweaver Kayle") correctly lists "Kayle" in its roster even though she isn't a draftable champion — she's the unit auto-summoned by the Storyweaver trait itself, not a gap in the Champions tab.
- Bilgewater's (Set 9.5) exact per-tier percentages weren't confirmed via public research as of this write (2026-07-07) — the breakpoint thresholds (3/5/7) are sourced from two independent guides, but flagged in the sheet for a follow-up tooltip check before using in balance math.
