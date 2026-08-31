"""Asset 4: gaslamp.glb -- 2.40 m cast-iron Victorian street gas lamp.
Origin: base centre, ground y=0. Materials: iron, glass.
"""
import bpy
import bmesh
import math
import sys

sys.path.insert(0, "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B3")
import common as C

C.clear_scene()

IRON, GLASS = 0, 1

bm = bmesh.new()


def add_fluted_cylinder(cx, cz, y0, y1, r0, r1, flutes=10, depth=0.006,
                         segments=40, mat_idx=IRON):
    bottom, top = [], []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        wobble = depth * math.cos(flutes * a)
        rb = r0 + wobble
        rt = r1 + wobble
        bottom.append(bm.verts.new(C.V(cx + rb * math.cos(a), y0, cz + rb * math.sin(a))))
        top.append(bm.verts.new(C.V(cx + rt * math.cos(a), y1, cz + rt * math.sin(a))))
    for i in range(segments):
        j = (i + 1) % segments
        f = bm.faces.new((bottom[i], bottom[j], top[j], top[i]))
        f.material_index = mat_idx
    fb = bm.faces.new(list(reversed(bottom)))
    fb.material_index = mat_idx
    ft = bm.faces.new(top)
    ft.material_index = mat_idx


# ---- stepped base ----
C.add_box(bm, -0.15, 0.15, 0.0, 0.08, -0.15, 0.15, mat_idx=IRON)
C.add_box(bm, -0.10, 0.10, 0.08, 0.17, -0.10, 0.10, mat_idx=IRON)

# ---- fluted column, slight taper ----
COL_Y0, COL_Y1 = 0.17, 1.85
add_fluted_cylinder(0, 0, COL_Y0, COL_Y1, 0.058, 0.044, flutes=10, depth=0.007)

# collar rings top/bottom of column (cast-iron joints)
C.add_cylinder(bm, 0, 0, COL_Y0, COL_Y0 + 0.03, 0.07, segments=20, mat_idx=IRON)
C.add_cylinder(bm, 0, 0, COL_Y1 - 0.04, COL_Y1, 0.06, segments=20, mat_idx=IRON)

# ---- ladder bar: crossbar a lamplighter's ladder leans against ----
LADDER_Y = 1.20
C.add_cylinder(bm, 0, 0, LADDER_Y - 0.03, LADDER_Y + 0.04, 0.075, segments=20, mat_idx=IRON)
C.add_box(bm, -0.30, 0.30, LADDER_Y - 0.022, LADDER_Y + 0.022, -0.03, 0.03, mat_idx=IRON)

# ---- lantern: square glazed chamber on 4 corner posts ----
LAN_Y0, LAN_Y1 = 1.85, 2.25
HALF = 0.15
POST = 0.028
corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
for sx, sz in corners:
    cx = sx * (HALF - POST / 2)
    cz = sz * (HALF - POST / 2)
    C.add_box(bm, cx - POST / 2, cx + POST / 2, LAN_Y0, LAN_Y1,
              cz - POST / 2, cz + POST / 2, mat_idx=IRON)
# top and bottom perimeter frame rails
for y0, y1 in ((LAN_Y0, LAN_Y0 + 0.025), (LAN_Y1 - 0.03, LAN_Y1)):
    C.add_box(bm, -HALF, HALF, y0, y1, -HALF, -HALF + 0.02, mat_idx=IRON)
    C.add_box(bm, -HALF, HALF, y0, y1, HALF - 0.02, HALF, mat_idx=IRON)
    C.add_box(bm, -HALF, -HALF + 0.02, y0, y1, -HALF, HALF, mat_idx=IRON)
    C.add_box(bm, HALF - 0.02, HALF, y0, y1, -HALF, HALF, mat_idx=IRON)
# glass panes, 4 sides, inset between rails/posts
gy0, gy1 = LAN_Y0 + 0.03, LAN_Y1 - 0.035
gh = HALF - POST + 0.006
C.add_quad(bm, (-gh, gy0, -HALF + 0.004), (gh, gy0, -HALF + 0.004),
           (gh, gy1, -HALF + 0.004), (-gh, gy1, -HALF + 0.004), mat_idx=GLASS)
C.add_quad(bm, (HALF - 0.004, gy0, -gh), (HALF - 0.004, gy0, gh),
           (HALF - 0.004, gy1, gh), (HALF - 0.004, gy1, -gh), mat_idx=GLASS)
C.add_quad(bm, (gh, gy0, HALF - 0.004), (-gh, gy0, HALF - 0.004),
           (-gh, gy1, HALF - 0.004), (gh, gy1, HALF - 0.004), mat_idx=GLASS)
C.add_quad(bm, (-HALF + 0.004, gy0, gh), (-HALF + 0.004, gy0, -gh),
           (-HALF + 0.004, gy1, -gh), (-HALF + 0.004, gy1, gh), mat_idx=GLASS)

# door hinge knuckles on one corner post (front-left) -- the front face pane
# (at z=-HALF) is the door; hinge on its left edge (corner -1,-1)
hinge_cx, hinge_cz = -(HALF - POST / 2), -(HALF - POST / 2)
for hy in (LAN_Y0 + 0.06, LAN_Y0 + 0.20, LAN_Y1 - 0.06):
    C.add_cylinder(bm, hinge_cx - 0.02, hinge_cz - 0.015, hy - 0.015, hy + 0.015,
                    0.016, segments=8, mat_idx=IRON)
# latch/catch on the opposite (right) edge of the door face, mid height
latch_cx, latch_cz = (HALF - POST / 2), -(HALF - POST / 2) - 0.02
C.add_box(bm, latch_cx - 0.02, latch_cx + 0.025, LAN_Y0 + 0.14, LAN_Y0 + 0.19,
          latch_cz - 0.02, latch_cz + 0.02, mat_idx=IRON)

# gas jet + burner, visible through the glass
C.add_cylinder(bm, 0, 0, LAN_Y0 + 0.02, LAN_Y0 + 0.14, 0.012, segments=10, mat_idx=IRON)
C.add_cylinder(bm, 0, 0, LAN_Y0 + 0.14, LAN_Y0 + 0.18, 0.022, segments=10, mat_idx=IRON,
               radius_top=0.016)

# ---- vent cap: 4-sided pyramid with proud eave + louvre fins ----
CAP_Y0, CAP_Y1 = LAN_Y1, LAN_Y1 + 0.13
C.add_cylinder(bm, 0, 0, CAP_Y0, CAP_Y0 + 0.02, HALF + 0.03, segments=4, mat_idx=IRON)
C.add_cylinder(bm, 0, 0, CAP_Y0 + 0.02, CAP_Y1, HALF + 0.03, segments=4, mat_idx=IRON,
               radius_top=0.015)
# louvre fins around the cap base -- real gaps between them
n_fins = 10
for i in range(n_fins):
    a = 2 * math.pi * i / n_fins
    fx, fz = (HALF + 0.045) * math.cos(a), (HALF + 0.045) * math.sin(a)
    C.add_box(bm, fx - 0.012, fx + 0.012, CAP_Y0 - 0.03, CAP_Y0 + 0.01,
              fz - 0.012, fz + 0.012, mat_idx=IRON)
# finial knob
C.add_cylinder(bm, 0, 0, CAP_Y1, CAP_Y1 + 0.02, 0.02, segments=10, mat_idx=IRON)

obj = C.new_object("gaslamp", bm, ["iron", "glass"])
C.add_bevel(obj, width=0.004, segments=2)
C.smart_uv(obj)

bpy.context.view_layer.objects.active = obj
obj.select_set(True)

C.export_glb([obj], C.MODELS_DIR + "/gaslamp.glb")

# ---- render rig ----
C.add_sun(elevation_deg=48, azimuth_deg=135, energy=3.0)
C.add_fill_light(loc=(-1.0, -1.5, 1.6), energy=25)

eye = 1.6
cam_face = C.add_camera("cam_face", C.V(0.0, eye, 4.6), C.V(0, 1.15, 0), lens=40)
cam_34 = C.add_camera("cam_34", C.V(2.8, eye, 3.5), C.V(0, 1.15, 0), lens=40)
cam_detail = C.add_camera("cam_detail", C.V(0.55, 2.15, 0.55), C.V(0, 1.98, 0), lens=60)

C.setup_render('CYCLES', samples=32, res=(960, 540), device='CPU')

backup = C.apply_clay_override([obj])
for cam, name in ((cam_face, "face"), (cam_34, "34"), (cam_detail, "detail")):
    bpy.context.scene.camera = cam
    C.render_to(C.RENDER_DIR + f"/gaslamp_{name}.png")
C.restore_materials([obj], backup)

bpy.ops.wm.save_as_mainfile(
    filepath="C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B3/gaslamp.blend")
print("DONE gaslamp")
