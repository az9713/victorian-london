# Reference pack — victorian-london (1880s Whitechapel/Spitalfields)

Two tiers. **Tier 1 (tier1/) = SPEC**: layout, counts, heights. **Tier 2 (tier2/) =
FIDELITY**: mood and material realism only. Where a Tier-2 cinematic disagrees with
Tier 1 about placement, count or height, **Tier 1 wins and the disagreement is not a
defect in the build.** Within Tier 1, **this text block outranks every drawn plate**;
generated drawings are not to scale. Authority order: this README → printed figures on
plates → nothing else. Never scale a distance off a plate.

Generation prompts (sidecar .json files in generations/) are **non-authoritative**.

## Spatial source of truth

**Datum:** +0.00 = street surface at the market plaza south-west corner.
**Ground:** LEVEL throughout the slice (Spitalfields is flat). No slopes, no stairs
outdoors except viaduct steps. This is a ruling, recorded 2026-08-30.
**Slice:** 350 m west-east × 300 m north-south.

### Landmark counts (complete list — nothing else is a landmark)

| # | Landmark | Count | Governing figures |
|---|---|---|---|
| L1 | Spitalfields Market building | 1 | plaza 100 m × 60 m; glass-and-iron roof, ridge +14.00; eaves +9.00 |
| L2 | Christ Church (spire) | 1 | spire top +50.00; nave roof +18.00; forecourt set back 12 m from street |
| L3 | Gin palace pub | 1 | 3 storeys; parapet +11.00; ground-floor front glazed, gas-lit |
| L4 | Railway viaduct | 1 | crosses full slice on north edge; arch opening 9.00 high × 18.00 span; deck +15.00 |
| L5 | Dorset St rookery tenement | 1 complex | 4 storeys; parapet +14.50; frontage 5.50; rear courtyard 3.70 wide |
| L6 | George Yard alley | 1 | width 4.00; walls both sides +12.00; exactly 1 gas lamp |
| L7 | Pillar box | 1 | on Commercial Street; height 1.40 |

### Streets (all widths building-face to building-face)

- **Commercial Street** (main, runs north-south on the west third): 18.00 wide.
- **Brick Lane** (north-south, east third): 11.00 wide.
- **Dorset Street** (west-east, centre): 11.00 wide.
- **George Yard** (alley, connects Dorset St to the viaduct street): 4.00 wide.
- Gas lamps: spacing 65 m on Commercial Street and Brick Lane; lamp height 2.40;
  George Yard has exactly 1. Fill terraces: 3–4 storeys, floor-to-floor 3.50,
  frontage 5.00, parapets +10.50 to +14.00.

### The route (in words — this outranks any plate that draws it differently)

Enter at Brick Lane north end → south to the market plaza east edge → west through
the market building → exit plaza west onto Dorset Street → west past the rookery
(L5) → George Yard (L6) north–south connects on the right → continue west to
Commercial Street → south on Commercial Street past the gin palace (L3, east side)
→ Christ Church (L2) faces Commercial Street from the west side → slice exit at
Commercial Street south end. The viaduct (L4) is always visible closing the north
edge. No crossing structure spans Commercial Street or Brick Lane; ONLY the viaduct
crosses, on the north edge, perpendicular to both.

## Congruence pass — run against every plate before first geometry

1. **Counts:** check each plate against the L1–L7 table. A plate showing 2 churches
   or 2 viaducts is wrong; regenerate or note as decorative.
2. **Route topology:** trace the route above in any plate that shows it; viaduct
   perpendicular to north-south streets, nothing else spans a street.
3. **Elevation:** ground is LEVEL by ruling; any plate implying slopes is overruled.
4. **Scale audit:** plates are presumed not to scale; only printed figures count,
   and where a printed figure contradicts this README, the README wins.
5. Contradictions found → fix by regenerating the plate or by adding a ruling here.

## Congruence log — pass run 2026-08-30 against the generated plates

- **site-plan.jpg:** counts OK (1 market, 1 church, 1 viaduct). CONTRADICTIONS:
  viaduct drawn as a CURVE — **ruling: the viaduct is STRAIGHT, west-east, on the
  north edge**; church drawn mid-plan next to the market — README placement (faces
  Commercial Street from the west side) wins; street names on the plan are invented
  and decorative; scale bar decorative.
- **long-section.jpg:** +50.00 / +18.00 / 3.50 / +0.00 / 9.00 printed correct.
  CONTRADICTION: viaduct arch span printed 14.00 — README says **18.00**, README
  wins. One garbled parapet figure near the terrace roof: ignore.
- **elev-market.jpg:** +14.00 ridge, +9.00 eaves correct. Imperial figures
  (12'6", 45'0") decorative.
- **elev-street.jpg:** gin palace present mid-strip, 3 storeys, +14.00 and +3.50
  printed correct; other figures partly garbled — decorative. Pub name on plate is
  decorative.
- **elev-church.jpg:** +50.00 total and +18.00 correct; remaining figures garbled —
  decorative.
- **materials.jpg / characters.jpg:** all 9 swatches / all 6 archetypes present;
  label typos decorative.
- **Elevation ruling confirmed:** every plate consistent with LEVEL ground.
- Tier-2 (hero, night-alley, gin-palace, viaduct): on-mood, approved for fidelity
  reference only.

## Tier map

- tier1/: site-plan, long-section (W-E through Dorset St), elevations (market front,
  Commercial St strip with gin palace, church west front), materials sheet,
  character sheet.
- tier2/: hero (APPROVED by operator 2026-08-30: day market), night alley, gin
  palace evening, viaduct street.
