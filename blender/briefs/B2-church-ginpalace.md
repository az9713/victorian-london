# Batch B2 — Christ Church + gin palace
Read blender/BRIEF-COMMON.md first. You own blender/B2/.
Plates: refpack/tier1/elev-church.jpg, refpack/tier1/elev-street.jpg (look only).
Figures below are law.

## Asset 1: church (L2) — sandbox/assets/models/church.glb
Hawksmoor-style English Baroque parish church (Christ Church Spitalfields is the
model). Origin: centre of the combined footprint at world (24, 207.5) → local
coords: nave spans local x -15..+7, z -15.5..+15.5; tower local x +7..+15,
z -4..+4. y=0 ground. FRONT (entrance face) = +x face of the tower (east,
toward Commercial Street).
- Nave: 22 x 31 m, walls to +13, pitched slate roof ridge +18 (W-E ridge),
  parapet at eaves, 4 tall round-headed windows per long side with reveals,
  sills, arched heads; plinth course at base.
- Tower: 8 x 8 m to +35: west-portico face reads as the front — broad Tuscan
  portico porch (4 columns, entablature, arch) at ground on the +x face, door
  recessed behind it; belfry stage with louvred openings near the top; clock
  face band; cornices dividing stages.
- Spire: pyramidal/broach spire from +35 to apex +50 (matches greybox cone,
  4-sided), small lucarne openings on alternating faces, weathervane finial.
- Materials: plaster (Portland stone reads pale — use "stone"), slate roof,
  paint_dark doors.

## Asset 2: ginpalace (L3) — sandbox/assets/models/ginpalace.glb
Origin footprint centre world (76.5, 188), 15 x 20 m (x east-west depth 15,
z north-south frontage 20), FRONT = -x face (west, onto Commercial Street).
3 storeys, parapet +11.00, floor-to-floor 3.5.
1880s gin palace (think The Ten Bells): ground floor = glazed pub front along the
FULL west frontage: stallriser plinth, big plate-glass windows in ornate joinery
(glazing bars real geometry), corner entrance door set back in reveal with fanlight,
fascia signboard band with cornice above (blank board — no text), gas lamp bracket
over the door (bracket + lantern box). Upper floors: brick, sash windows with
sills/lintels/reveals (4 per floor on front, 2 on sides), parapet cornice, 2
chimney stacks with 3 pots each on the roof behind the parapet.
Materials: brick, paint_green joinery, glass, slate roof slope behind parapet.

Deliver: 2 assets, clay renders per COMMON (church gets the context frame),
manifest blender/manifests/B2.md.
