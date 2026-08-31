# Batch B3 — rookery, viaduct module, George Yard flank, gas lamp, pillar box
Read blender/BRIEF-COMMON.md first. You own blender/B3/.
Plates: refpack/tier1/long-section.jpg, refpack/tier2/viaduct.jpg,
refpack/tier2/night-alley.jpg (look only). Figures below are law.

## Asset 1: rookery (L5) — sandbox/assets/models/rookery.glb
Dorset Street tenement complex. Origin at world (171.5, 166.25), y=0.
Local: front block z -10.75..-1.75 (9 deep), rear block z +1.95..+10.75,
both x -19.5..+18.5 (38 long); courtyard gap 3.7 m between; east court wall at
x +18.5..+19.5 closing the gap. Parapet +14.50, 4 storeys (floor-to-floor 3.5).
FRONT = -z face (north, onto Dorset Street).
Decayed 1880s common lodging house: soot-black brick, plinth, door every 5.5 m
(frontage rhythm) each with worn steps + reveal, sash windows (some with boards),
string courses, parapet with missing coping bits, chimney stacks along the ridge
line, rear block plainer with smaller windows onto the courtyard, courtyard privy
lean-to + standpipe against the court wall.
Materials: brick, slate, paint_dark, planks (boarded windows).

## Asset 2: viaduct-module (L4) — sandbox/assets/models/viaduct-module.glb
ONE 22 m module, repeated 16x by the game along the north edge. Origin at pier
centre (world x = pier centre, z=10), y=0. Module: brick pier 4 wide (x -2..+2,
z -6..+6), then HALF an 18 m arch opening each side (the arch crown spans between
modules): build pier + springing + half-arches so tiled modules form full
segmental brick arches, opening 9.00 high at the crown, 18.00 span. Deck structure
+9..+15 (z -7..+7): brick spandrel walls, stone string course, parapet on both
deck edges +15..+16.2, weep drips. Soot-black London stock brick, arch rings
visible (2-3 recessed brick orders), pier plinth. Refuges/recesses in pier faces.
Materials: brick, stone.

## Asset 3: gy-flank — sandbox/assets/models/gy-flank.glb
George Yard alley wall building strip: 8 wide x 118.5 long x 12 high. Origin at
strip centre, long axis local z (game rotates/places both sides). The ALLEY face
(+x local) is the one seen: sooty brick, tall mostly-blind wall with a few small
high windows (barred), door recesses at long intervals, plinth, drips, parapet
coping. Other faces plain brick. Materials: brick, iron (bars).

## Asset 4: gaslamp — sandbox/assets/models/gaslamp.glb
2.40 m cast-iron street gas lamp: stepped base, fluted column, ladder bar (the
crossbar lamplighters lean ladders on), square glazed lantern with door + vent
cap, gas jet inside. Materials: iron, glass. Origin at base centre.

## Asset 5: pillarbox (L7) — sandbox/assets/models/pillarbox.glb
1.40 m Victorian pillar box: cylindrical body, posting slot under a projecting
cap, door with hinge + lock plate, VR cypher band (raised relief ring band is
fine, no text), base plinth. Material: paint_dark (game binds postbox red? no —
name it "postbox_red"). Origin base centre.

Deliver: 5 assets, clay renders per COMMON (rookery + viaduct get context
frames), manifest blender/manifests/B3.md.
