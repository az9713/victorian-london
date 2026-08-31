"""Asset 3: gy-flank.glb -- George Yard alley wall building strip.
8 wide (x -4..4) x 118.5 long (z -59.25..59.25) x 12 high. Origin: strip
centre. The alley face (+x local) carries the detail: sooty brick, tall
mostly-blind wall, a few small high barred windows, door recesses at long
intervals, plinth, weep drips, parapet coping. Other faces plain brick.
Materials: brick, iron (bars).
"""
import bpy
import bmesh
import math
import sys

sys.path.insert(0, "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B3")
import common as C

C.clear_scene()

BRICK, IRON = 0, 1

HALF_X = 4.0
HALF_Z = 59.25
WALL_TOP = 11.7
PARAPET_TOP = 12.0
FACE_X = HALF_X          # alley face plane
RECESS_X = HALF_X - 0.35  # back of window/door reveals

N_BAYS = 15
BAY_W = (2 * HALF_Z) / N_BAYS  # 7.9
types = ["blank"] * N_BAYS
for i in (2, 7, 12):
    types[i] = "window"
for i in (4, 10):
    types[i] = "door"

bm = bmesh.new()


def bay_bounds(i):
    z0 = -HALF_Z + i * BAY_W
    z1 = z0 + BAY_W
    return z0, z1


def build_window(z0, z1):
    zc = (z0 + z1) / 2
    hw = 0.5
    sill, lintel = 8.4, 9.6
    zl, zr = zc - hw, zc + hw
    # flanking plain panels
    C.add_quad(bm, (FACE_X, 0, z0), (FACE_X, 0, zl), (FACE_X, WALL_TOP, zl),
               (FACE_X, WALL_TOP, z0), mat_idx=BRICK)
    C.add_quad(bm, (FACE_X, 0, zr), (FACE_X, 0, z1), (FACE_X, WALL_TOP, z1),
               (FACE_X, WALL_TOP, zr), mat_idx=BRICK)
    # below sill / above lintel panels
    C.add_quad(bm, (FACE_X, 0, zl), (FACE_X, 0, zr), (FACE_X, sill, zr),
               (FACE_X, sill, zl), mat_idx=BRICK)
    C.add_quad(bm, (FACE_X, lintel, zl), (FACE_X, lintel, zr), (FACE_X, WALL_TOP, zr),
               (FACE_X, WALL_TOP, zl), mat_idx=BRICK)
    # reveal jambs
    C.add_quad(bm, (FACE_X, sill, zl), (RECESS_X, sill, zl), (RECESS_X, lintel, zl),
               (FACE_X, lintel, zl), mat_idx=BRICK)
    C.add_quad(bm, (RECESS_X, sill, zr), (FACE_X, sill, zr), (FACE_X, lintel, zr),
               (RECESS_X, lintel, zr), mat_idx=BRICK)
    # lintel soffit + sill
    C.add_quad(bm, (RECESS_X, lintel, zl), (RECESS_X, lintel, zr), (FACE_X, lintel, zr),
               (FACE_X, lintel, zl), mat_idx=BRICK)
    C.add_quad(bm, (FACE_X, sill, zl), (FACE_X, sill, zr), (RECESS_X, sill, zr),
               (RECESS_X, sill, zl), mat_idx=BRICK)
    C.add_box(bm, RECESS_X - 0.02, FACE_X + 0.04, sill - 0.03, sill, zl - 0.03, zr + 0.03,
               mat_idx=BRICK)  # proud sill drip lip
    # back (blocked-dark) panel
    C.add_quad(bm, (RECESS_X, sill, zl), (RECESS_X, sill, zr), (RECESS_X, lintel, zr),
               (RECESS_X, lintel, zl), mat_idx=BRICK)
    # iron bars
    n_bars = 3
    for k in range(1, n_bars + 1):
        zb = zl + (zr - zl) * k / (n_bars + 1)
        C.add_cylinder(bm, RECESS_X + 0.08, zb, sill + 0.04, lintel - 0.04, 0.014,
                       segments=8, mat_idx=IRON)


def build_door(z0, z1):
    zc = (z0 + z1) / 2
    hw = 0.55
    lintel = 2.3
    zl, zr = zc - hw, zc + hw
    C.add_quad(bm, (FACE_X, 0, z0), (FACE_X, 0, zl), (FACE_X, WALL_TOP, zl),
               (FACE_X, WALL_TOP, z0), mat_idx=BRICK)
    C.add_quad(bm, (FACE_X, 0, zr), (FACE_X, 0, z1), (FACE_X, WALL_TOP, z1),
               (FACE_X, WALL_TOP, zr), mat_idx=BRICK)
    C.add_quad(bm, (FACE_X, lintel, zl), (FACE_X, lintel, zr), (FACE_X, WALL_TOP, zr),
               (FACE_X, WALL_TOP, zl), mat_idx=BRICK)
    C.add_quad(bm, (FACE_X, 0, zl), (RECESS_X, 0, zl), (RECESS_X, lintel, zl),
               (FACE_X, lintel, zl), mat_idx=BRICK)
    C.add_quad(bm, (RECESS_X, 0, zr), (FACE_X, 0, zr), (FACE_X, lintel, zr),
               (RECESS_X, lintel, zr), mat_idx=BRICK)
    C.add_quad(bm, (RECESS_X, lintel, zl), (RECESS_X, lintel, zr), (FACE_X, lintel, zr),
               (FACE_X, lintel, zl), mat_idx=BRICK)
    C.add_quad(bm, (RECESS_X, 0, zl), (RECESS_X, 0, zr), (RECESS_X, lintel, zr),
               (RECESS_X, lintel, zl), mat_idx=BRICK)  # blocked-up back panel
    C.add_box(bm, RECESS_X - 0.02, FACE_X + 0.02, 0.0, 0.08, zl - 0.05, zr + 0.05,
              mat_idx=BRICK)  # worn threshold step


def build_blank(z0, z1):
    C.add_quad(bm, (FACE_X, 0, z0), (FACE_X, 0, z1), (FACE_X, WALL_TOP, z1),
               (FACE_X, WALL_TOP, z0), mat_idx=BRICK)


for i in range(N_BAYS):
    z0, z1 = bay_bounds(i)
    if types[i] == "window":
        build_window(z0, z1)
    elif types[i] == "door":
        build_door(z0, z1)
    else:
        build_blank(z0, z1)

# ---- other faces: plain back, two end caps, top parapet slab ----
C.add_quad(bm, (-HALF_X, 0, HALF_Z), (-HALF_X, 0, -HALF_Z),
           (-HALF_X, WALL_TOP, -HALF_Z), (-HALF_X, WALL_TOP, HALF_Z), mat_idx=BRICK)

for zc in (-HALF_Z, HALF_Z):
    C.add_quad(bm, (-HALF_X, 0, zc), (HALF_X, 0, zc), (HALF_X, WALL_TOP, zc),
               (-HALF_X, WALL_TOP, zc), mat_idx=BRICK)

# ---- plinth along the alley face ----
C.add_box(bm, FACE_X, FACE_X + 0.14, 0.0, 0.4, -HALF_Z, HALF_Z, mat_idx=BRICK)

# ---- weep drip below parapet, alley face ----
C.add_box(bm, FACE_X, FACE_X + 0.03, WALL_TOP - 0.06, WALL_TOP - 0.03,
          -HALF_Z, HALF_Z, mat_idx=BRICK)

# ---- parapet slab capping the whole strip, with proud coping on alley edge ----
C.add_box(bm, -HALF_X, HALF_X, WALL_TOP, PARAPET_TOP, -HALF_Z, HALF_Z, mat_idx=BRICK)
C.add_box(bm, FACE_X - 0.04, FACE_X + 0.06, PARAPET_TOP - 0.05, PARAPET_TOP,
          -HALF_Z, HALF_Z, mat_idx=BRICK)  # coping lip, proud

obj = C.new_object("gy_flank", bm, ["brick", "iron"])
C.add_bevel(obj, width=0.015, segments=2)
C.smart_uv(obj)

bpy.context.view_layer.objects.active = obj
obj.select_set(True)

C.export_glb([obj], C.MODELS_DIR + "/gy-flank.glb")

# ---- render rig: a window bay, a door bay, and a pulled-back context shot
#      of the full 118.5 m strip (over 4 m -> ctx required by COMMON) ----
C.add_sun(elevation_deg=45, azimuth_deg=140, energy=3.0)
C.add_fill_light(loc=(6, -10, 8), energy=80)

eye = 1.6
# window bay 2 centre
wz0, wz1 = bay_bounds(2)
wzc = (wz0 + wz1) / 2
cam_face = C.add_camera("cam_face", C.V(3.2, eye, wzc), C.V(0, 8.5, wzc), lens=40)
cam_34 = C.add_camera("cam_34", C.V(3.0, eye, wzc + 2.5), C.V(FACE_X, 8.7, wzc), lens=40)
cam_detail = C.add_camera("cam_detail", C.V(2.0, 9.2, wzc + 1.0), C.V(FACE_X, 9.0, wzc),
                           lens=55)
cam_ctx = C.add_camera("cam_ctx", C.V(12, 10, -75), C.V(2, 5, 60), lens=24)

C.setup_render('CYCLES', samples=32, res=(960, 540), device='CPU')

backup = C.apply_clay_override([obj])
for cam, name in ((cam_face, "face"), (cam_34, "34"), (cam_detail, "detail"),
                   (cam_ctx, "ctx")):
    bpy.context.scene.camera = cam
    C.render_to(C.RENDER_DIR + f"/gy-flank_{name}.png")
C.restore_materials([obj], backup)

bpy.ops.wm.save_as_mainfile(
    filepath="C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B3/gy_flank.blend")
print("DONE gy-flank")
