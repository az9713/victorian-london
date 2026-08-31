# Batch B1 — Spitalfields market building + market props
Read blender/BRIEF-COMMON.md first. You own blender/B1/.
Plates: refpack/tier1/elev-market.jpg (look), refpack/tier2/hero.jpg (mood).
Only PRINTED figures on plates count; these figures below win over everything.

## Asset 1: market (L1) — sandbox/assets/models/market.glb
Origin at footprint centre (world 234.5, 150), y=0 ground. Footprint 84 x 44 m
(x along ridge, west-east). Eaves +9.00, glass-and-iron gable roof, ridge +14.00
running west-east. 12 m wide entrance openings centred on the short (east + west)
walls. Two rows of interior iron columns (at local z = -10 and +10, every 12 m).
Victorian market hall construction (1880s, think old Spitalfields/Covent Garden):
- Perimeter: brick piers + plinth, large segmental-arched openings between piers
  along the long walls (open market frontage), arch bricks visible.
- Entrances: wide segmental arch with keystone, cast-iron gates IMPLIED by posts +
  hinge plates (gates open), threshold step worn.
- Roof: iron trusses visible from inside (bottom chords + struts under the glass),
  glazing bars as real geometry on the roof planes (material glass between iron
  ribs), ridge ventilation lantern (raised clerestory strip along the ridge with
  its own mini-roof), eaves gutter + downpipes at corners feeding to ground.
- Materials: brick piers/plinth, iron columns/trusses/glazing bars, glass roof,
  slate on the lantern roof if any solid roof strips.
- Columns: cast-iron with base, shaft, simple capital, bracket where truss lands.

## Asset 2: market-stall — stall.glb (origin centre, ~2.4 x 1.2 m)
Trestle stall: two A-frame trestles, thick top boards with gaps, canvas canopy on
two poles with visible ties, side rail, produce boxes on top (empty crates ok).

## Asset 3: crate — crate.glb (~0.6 m)
Boards with thickness + gaps, corner battens, nail heads, hand holes both ends.

## Asset 4: barrel — barrel.glb (~0.9 m tall)
Staves with joints, 3 iron hoops standing proud, chime ends, bung hole.

## Asset 5: sack-pile — sacks.glb (~1 m spread)
2-3 jute sacks, slumped under their own weight, tied necks, creases at contact.

Props use planks/iron/plaster material names (sacks: plaster is fine as neutral
cloth — name the material "cloth" instead, the game will bind it).
Deliver: 5 assets exported, clay renders per COMMON, manifest blender/manifests/B1.md.
