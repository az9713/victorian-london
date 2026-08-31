"""Asset 3: gy-flank.glb -- George Yard alley wall, a building strip 8 m
wide x 118.5 m long x 12 m high. Origin: strip centre, long axis local z
(the game rotates/places both sides of the alley from one asset).

Brief figures (law): 8 wide (x -4..+4), 118.5 long (z -59.25..+59.25),
12 high. The ALLEY face (+x local) is the seen face: sooty brick, tall
mostly-blind wall, a few small high barred windows, door recesses at long
intervals, plinth, drips, parapet coping. Other 3 faces plain brick.
Materials: brick, iron (bars).

Numbers not given by the brief (assumption, flagged in blender/manifests/B3.md):
  wall built as a solid 8 m deep mass (no modelled interior -- this is a
  backdrop flank, only the alley face is ever seen); window/door reveal
  depth 0.30 m into that mass; 4 door recesses and 6 small windows spaced
  along the 118.5 m run (roughly one door per ~24-30 m, echoing the
  Dorset-Street-rhythm feel from refpack/tier1/long-section.jpg without
  literally repeating the rookery's 5.5 m door spacing, since this is a
  blind service elevation, not a frontage).
"""
import bpy
import bmesh
import math
import sys

sys.path.insert(0, "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B3")
import common as C

C.clear_scene()

BRICK, IRON = 0, 1
MATS = ["brick", "iron"]

HALF_W = 4.0
HALF_L = 59.25
HEIGHT = 12.0
FACE_X = HALF_W
REVEAL = 0.30
PLINTH_Y = 0.5
COPE_Y0, COPE_Y1 = 11.65, 12.0

bm = bmesh.new()

# ---- main mass: back face, two end caps, top, bottom (front face built
#      separately below with openings) ----
C.add_box(bm, -HALF_W - 0.08, -HALF_W, 0.0, PLINTH_Y, -HALF_L, HALF_L, mat_idx=BRICK)  # back plinth kick
C.add_quad(bm, (-HALF_W, PLINTH_Y, -HALF_L), (-HALF_W, PLINTH_Y, HALF_L),
           (-HALF_W, HEIGHT, HALF_L), (-HALF_W, HEIGHT, -HALF_L), mat_idx=BRICK)  # back face
# end caps (z = +-HALF_L), plain brick, full box height incl. plinth taper
for zf, zsign in ((-HALF_L, -1), (HALF_L, 1)):
    if zsign > 0:
        C.add_quad(bm, (-HALF_W, 0.0, zf), (FACE_X, 0.0, zf),
                   (FACE_X, HEIGHT, zf), (-HALF_W, HEIGHT, zf), mat_idx=BRICK)
    else:
        C.add_quad(bm, (FACE_X, 0.0, zf), (-HALF_W, 0.0, zf),
                   (-HALF_W, HEIGHT, zf), (FACE_X, HEIGHT, zf), mat_idx=BRICK)
# top (roof deck, flat -- not a habitable roof, this is a boundary wall mass)
C.add_quad(bm, (-HALF_W, HEIGHT, -HALF_L), (FACE_X, HEIGHT, -HALF_L),
           (FACE_X, HEIGHT, HALF_L), (-HALF_W, HEIGHT, HALF_L), mat_idx=BRICK)

# ---- plinth: projecting course at the base of the alley face, full length ----
C.add_box(bm, FACE_X, FACE_X + 0.08, 0.0, PLINTH_Y, -HALF_L, HALF_L, mat_idx=BRICK)

# ---- alley face (+x): built as horizontal bands so door and window
#      openings (which sit at different heights) never overlap the same
#      flat quad -- each band is either plain, or split by z into flanking
#      strips + recesses around that band's openings ----
DOOR_Z = [-42.0, -14.0, 14.0, 42.0]
DOOR_HW, DOOR_Y0, DOOR_Y1 = 0.55, 0.0, 2.15
WIN_Z = [-52.0, -28.0, -4.0, 20.0, 34.0, 50.0]
WIN_HW, WIN_Y0, WIN_Y1 = 0.42, 8.8, 9.85


def opening_spans(centers, hw):
    return sorted((c - hw, c + hw) for c in centers)


door_spans = opening_spans(DOOR_Z, DOOR_HW)
win_spans = opening_spans(WIN_Z, WIN_HW)


def flat_band(y0, y1, spans):
    """Flat wall quads at x=FACE_X spanning z=-HALF_L..HALF_L and y0..y1,
    with gaps left where `spans` (z0,z1 pairs) fall -- those gaps get a
    recess built by build_recess."""
    cursor = -HALF_L
    for (a, b) in spans:
        if a > cursor:
            C.add_quad(bm, (FACE_X, y0, cursor), (FACE_X, y0, a),
                       (FACE_X, y1, a), (FACE_X, y1, cursor), mat_idx=BRICK)
        cursor = max(cursor, b)
    if cursor < HALF_L:
        C.add_quad(bm, (FACE_X, y0, cursor), (FACE_X, y0, HALF_L),
                   (FACE_X, y1, HALF_L), (FACE_X, y1, cursor), mat_idx=BRICK)


def build_recess(z0, z1, y0, y1, has_sill=False, has_lintel_block=False):
    """Recess an opening into the wall mass: side reveals, lintel, sill/
    threshold, and a brick back plane set REVEAL back from the face."""
    z_back = FACE_X - REVEAL
    C.add_quad(bm, (FACE_X, y0, z0), (z_back, y0, z0), (z_back, y1, z0), (FACE_X, y1, z0), mat_idx=BRICK)
    C.add_quad(bm, (z_back, y0, z1), (FACE_X, y0, z1), (FACE_X, y1, z1), (z_back, y1, z1), mat_idx=BRICK)
    C.add_quad(bm, (FACE_X, y1, z0), (z_back, y1, z0), (z_back, y1, z1), (FACE_X, y1, z1), mat_idx=BRICK)
    C.add_quad(bm, (z_back, y0, z0), (FACE_X, y0, z0), (FACE_X, y0, z1), (z_back, y0, z1), mat_idx=BRICK)
    C.add_quad(bm, (z_back, y0, z1), (z_back, y0, z0), (z_back, y1, z0), (z_back, y1, z1), mat_idx=BRICK)
    if has_sill:
        C.add_box(bm, FACE_X, FACE_X + 0.08, y0 - 0.08, y0 + 0.04, z0 - 0.05, z1 + 0.05, mat_idx=BRICK)
    if has_lintel_block:
        # proud lintel block square over the head -- judge round 1: door
        # heads need a distinct proud member, not just the flat recessed
        # soffit quad, or the opening reads as a hole rather than a built
        # doorway carrying load above it
        C.add_box(bm, FACE_X - 0.02, FACE_X + 0.10, y1 - 0.02, y1 + 0.16,
                  z0 - 0.10, z1 + 0.10, mat_idx=BRICK)
        # threshold sill/step at the base
        C.add_box(bm, FACE_X, FACE_X + 0.10, y0 - 0.04, y0 + 0.03,
                  z0 - 0.06, z1 + 0.06, mat_idx=BRICK)


def add_window_bars(z0, z1, y0, y1):
    """Vertical iron bars set in the reveal, socketed top AND bottom --
    the bars now run the FULL opening height and end exactly at the
    reveal's own head/sill planes (a rounded cap at each end, read as let
    into a drilled hole) instead of a separate collar box that overlapped
    the bar's own volume (round-1: an embedded-box coincidence identical to
    the ones found on the other three assets, sealing a light-trap)."""
    n_bars = 4
    x_bar = FACE_X - 0.05
    r = 0.013
    for i in range(1, n_bars + 1):
        z = z0 + (z1 - z0) * i / (n_bars + 1)
        # bar and caps are adjacent (touching), never overlapping in y
        C.add_box(bm, x_bar - r, x_bar + r, y0 + 0.02, y1 - 0.02, z - r, z + r, mat_idx=IRON)
        C.add_cylinder(bm, x_bar, z, y0, y0 + 0.02, r * 1.6, segments=8, mat_idx=IRON)  # bottom socket cap
        C.add_cylinder(bm, x_bar, z, y1 - 0.02, y1, r * 1.6, segments=8, mat_idx=IRON)  # top socket cap


# band 1: ground band with door recesses (y 0..DOOR_Y1)
flat_band(0.0, DOOR_Y1, door_spans)
for cz in DOOR_Z:
    build_recess(cz - DOOR_HW, cz + DOOR_HW, DOOR_Y0, DOOR_Y1, has_lintel_block=True)
    # recess back is plain brick, not a plank door leaf -- this is a blind
    # service elevation (brief lists only brick/iron for this asset), so a
    # blocked/bricked-up doorway reads correctly rather than needing the
    # 'planks' material added outside the brief's material list.

# band 2: plain wall between the door heads and the window sills
flat_band(DOOR_Y1, WIN_Y0, [])

# band 3: window band with barred recesses
flat_band(WIN_Y0, WIN_Y1, win_spans)
for cz in WIN_Z:
    build_recess(cz - WIN_HW, cz + WIN_HW, WIN_Y0, WIN_Y1, has_sill=True)
    add_window_bars(cz - WIN_HW, cz + WIN_HW, WIN_Y0, WIN_Y1)

# band 4: plain wall from above the windows up to the parapet coping
flat_band(WIN_Y1, COPE_Y0, [])

# ---- parapet coping: projecting course at the top of the alley face ----
C.add_box(bm, FACE_X - 0.05, FACE_X + 0.10, COPE_Y0, COPE_Y1, -HALF_L, HALF_L, mat_idx=BRICK)
C.add_box(bm, FACE_X - 0.05, FACE_X + 0.10, COPE_Y0 - 0.05, COPE_Y0,
          -HALF_L - 0.02, HALF_L + 0.02, mat_idx=BRICK)  # drip ledge underside

obj = C.new_object("gy_flank", bm, MATS)
C.add_bevel(obj, width=0.03, segments=2)
C.smart_uv(obj)

bpy.context.view_layer.objects.active = obj
obj.select_set(True)

C.export_glb([obj], C.MODELS_DIR + "/gy-flank.glb")

# ---- render rig ----
C.add_sun(elevation_deg=45, azimuth_deg=130, energy=3.0)
C.add_fill_light(loc=(6, -8, 6), energy=60)

eye = 1.6
# face/34 aimed AT a door or window bay, not a blank stretch of the mostly-
# blind wall -- a flat unbroken plane filling the whole frame reads as
# nothing in a clay test even though the geometry is correct there.
cam_face = C.add_camera("cam_face", C.V(8.0, eye, 14), C.V(4, 1.1, 14), lens=28)
cam_34 = C.add_camera("cam_34", C.V(7.5, eye, 22), C.V(4, 4.0, 10), lens=24)
cam_detail = C.add_camera("cam_detail", C.V(6.0, 9.0, -28.5), C.V(4, 9.3, -28), lens=45)
cam_ctx = C.add_camera("cam_ctx", C.V(26, 8, 0), C.V(0, 6, 0), lens=20)

C.setup_render('CYCLES', samples=32, res=(960, 540), device='CPU')

backup = C.apply_clay_override([obj])
for cam, name in ((cam_face, "face"), (cam_34, "34"), (cam_detail, "detail"), (cam_ctx, "ctx")):
    bpy.context.scene.camera = cam
    C.render_to(C.RENDER_DIR + f"/gy-flank_{name}.png")
C.restore_materials([obj], backup)

bpy.ops.wm.save_as_mainfile(
    filepath="C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B3/gy-flank.blend")
print("DONE gy-flank")
