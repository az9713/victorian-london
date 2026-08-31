# Batch B4 — terrace facade modules (the fill housing of the whole slice)
Read blender/BRIEF-COMMON.md first. You own blender/B4/.
Plates: refpack/tier1/elev-street.jpg, refpack/tier2/hero.jpg (look only).
Figures below are law. These 6 modules replace ~250 greybox boxes — they carry
the streetscape, so the same bar applies as to any landmark (NO tiering).

## The 6 assets: terrace<V>-<S>.glb, V in {0,1,2}, S in {3,4}
sandbox/assets/models/terrace0-3.glb … terrace2-4.glb
Module footprint EXACTLY 5.00 (frontage, local x) x 14.00 (depth, local z).
Origin footprint centre, y=0. FRONT = -z face. Heights: 3-storey variant total
11.25 m to parapet; 4-storey 13.25 m (floor-to-floor 3.50, the game scales
residual ±7%). Flat-ish slate roof sloping back behind the front parapet.
Modules tile side by side: side walls MUST be exactly on x = ±2.5, plain brick,
flush (no protrusions crossing the boundary), so a row reads as a terrace.

1880s East End brick terraces with shops below (Wentworth St flavour):
- Variant 0 "shopfront": ground floor shop — stallriser, shop window with glazing
  bars set in reveal, recessed door with step, fascia board + cornice (blank),
  iron bracket for a hanging sign (empty bracket). Sash windows above.
- Variant 1 "house": front door with fanlight + 2 worn steps + railings stub,
  sash window beside, sash pairs above, plinth, string course.
- Variant 2 "warehouse": wide segmental-arch cart entrance (door implied open,
  dark reveal), loading door on floor 2 with hoist beam + wheel above, small
  windows, dirtier brick.
All: window reveals + sills + brick lintels/arches, parapet with coping, ONE
chimney stack with 2-3 clay pots per module at the party-wall line (offset so
tiled neighbours alternate), downpipe on the front, soot streaking implied by
geometry wear (chipped plinth, a missing coping brick on some).
Variants must be DISTINGUISHABLE IN CLAY (different openings/roofline furniture,
not just different textures).
Materials: brick, slate, glass, planks, paint_green (variant0 joinery),
paint_dark (variant1/2 doors), iron.

Deliver: 6 assets, clay renders per COMMON, manifest blender/manifests/B4.md.
