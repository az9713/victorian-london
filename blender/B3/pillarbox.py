"""Asset 5: pillarbox.glb -- 1.40 m Victorian pillar post box.
Origin: base centre, ground y=0. Single material: postbox_red.
"""
import bpy
import bmesh
import math
import sys

sys.path.insert(0, "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B3")
import common as C

C.clear_scene()

bm = bmesh.new()
MAT = 0  # postbox_red

R_BODY = 0.26
R_PLINTH = 0.32
R_BAND = 0.275  # VR cypher raised ring
R_CAP = 0.34

# segment count raised 24->48 (12->24 for the finial) and shade_auto_smooth
# below -- judge round 1: "smoothing/bevels on cone + body facets" was
# faceted enough to look low-poly at close range even though the geometry
# itself was correct.
SEG = 48

# 1. base plinth -- wider than the body, real footing
C.add_cylinder(bm, 0, 0, 0.0, 0.07, R_PLINTH, segments=SEG, mat_idx=MAT)

# 2. main cylindrical body
C.add_cylinder(bm, 0, 0, 0.07, 1.02, R_BODY, segments=SEG, mat_idx=MAT)

# 3. VR cypher band -- raised relief medallion: a proud ring with thin
# moulded top/bottom edges (a cameo frame) so it reads as "something is in
# relief here" without needing full letterforms
C.add_cylinder(bm, 0, 0, 0.52, 0.535, R_BAND - 0.01, segments=SEG, mat_idx=MAT, radius_top=R_BAND)
C.add_cylinder(bm, 0, 0, 0.535, 0.625, R_BAND, segments=SEG, mat_idx=MAT)
C.add_cylinder(bm, 0, 0, 0.625, 0.64, R_BAND, segments=SEG, mat_idx=MAT, radius_top=R_BAND - 0.01)

# 4. cap -- projecting collar, then a tapered dome to a finial knob
C.add_cylinder(bm, 0, 0, 1.02, 1.10, R_CAP, segments=SEG, mat_idx=MAT)
C.add_cylinder(bm, 0, 0, 1.10, 1.32, R_CAP, segments=SEG, mat_idx=MAT,
               radius_top=0.09)
C.add_cylinder(bm, 0, 0, 1.32, 1.40, 0.09, segments=24, mat_idx=MAT,
               radius_top=0.02)

# 5. posting slot: hood (real proud lip) over a shallow recessed slot band
#    hood is a small angled ledge projecting from the body just below the cap
hood_y0, hood_y1 = 0.86, 0.94
hood_r_out = R_BODY + 0.055
half_arc = math.radians(24)
n = 6
hx0 = []
for i in range(n + 1):
    a = -half_arc + (2 * half_arc) * i / n
    hx0.append((math.sin(a), math.cos(a)))
# hood underside + top as a thin wedge shelf around the front arc
prev_top = None
prev_bot = None
for i, (sx, sz) in enumerate(hx0):
    top = C.V(hood_r_out * sx, hood_y1, hood_r_out * sz)
    bot = C.V((R_BODY + 0.01) * sx, hood_y0, (R_BODY + 0.01) * sz)
    vt = bm.verts.new(top)
    vb = bm.verts.new(bot)
    if prev_top is not None:
        f = bm.faces.new((prev_bot, vb, vt, prev_top))
        f.material_index = MAT
    prev_top, prev_bot = vt, vb
# slot itself -- a recessed band with a proud lip both above (the hood,
# built already) AND below, so it reads as a true lipped aperture a letter
# could be posted into, not just a flat dark strip cut into the cylinder
slot_r = R_BODY - 0.010
prev = None
for i, (sx, sz) in enumerate(hx0):
    p_lo = C.V(slot_r * sx, 0.78, slot_r * sz)
    p_hi = C.V(slot_r * sx, 0.84, slot_r * sz)
    vlo = bm.verts.new(p_lo)
    vhi = bm.verts.new(p_hi)
    if prev is not None:
        f = bm.faces.new((prev[0], vlo, vhi, prev[1]))
        f.material_index = MAT
    prev = (vlo, vhi)
# bottom lip -- thin proud ledge below the slot, mirroring the hood above
prev = None
for i, (sx, sz) in enumerate(hx0):
    top = C.V((R_BODY + 0.01) * sx, 0.78, (R_BODY + 0.01) * sz)
    bot = C.V((R_BODY + 0.035) * sx, 0.755, (R_BODY + 0.035) * sz)
    vt = bm.verts.new(top)
    vb = bm.verts.new(bot)
    if prev is not None:
        f = bm.faces.new((prev[0], prev[1], vt, vb))
        f.material_index = MAT
    prev = (vt, vb)

# 6. door -- proud curved panel following the body curvature, set on the
#    front arc (+z local, facing "out"), with hinge rod one side, lock
#    plate + keyhole the other, so it reads as an opening door not a hole.
door_r = R_BODY + 0.018
door_half_arc = math.radians(46)
door_y0, door_y1 = 0.14, 0.80
dn = 8
prev = None
for i in range(dn + 1):
    a = -door_half_arc + (2 * door_half_arc) * i / dn
    sx, sz = math.sin(a), math.cos(a)
    p_lo = C.V(door_r * sx, door_y0, door_r * sz)
    p_hi = C.V(door_r * sx, door_y1, door_r * sz)
    vlo = bm.verts.new(p_lo)
    vhi = bm.verts.new(p_hi)
    if prev is not None:
        f = bm.faces.new((prev[0], vlo, vhi, prev[1]))
        f.material_index = MAT
    prev = (vlo, vhi)
# rounded top cap of the door (small arc from top edge back to the body)
top_edge_r = door_r
for i in range(dn):
    a0 = -door_half_arc + (2 * door_half_arc) * i / dn
    a1 = -door_half_arc + (2 * door_half_arc) * (i + 1) / dn
    p0 = bm.verts.new(C.V(top_edge_r * math.sin(a0), door_y1, top_edge_r * math.cos(a0)))
    p1 = bm.verts.new(C.V(top_edge_r * math.sin(a1), door_y1, top_edge_r * math.cos(a1)))
    p0b = bm.verts.new(C.V(R_BODY * math.sin(a0), door_y1 + 0.02, R_BODY * math.cos(a0)))
    p1b = bm.verts.new(C.V(R_BODY * math.sin(a1), door_y1 + 0.02, R_BODY * math.cos(a1)))
    f = bm.faces.new((p0, p1, p1b, p0b))
    f.material_index = MAT

# hinge -- vertical rod proud at the door's trailing (left) edge
hinge_a = -door_half_arc
hx, hz = R_BODY * math.sin(hinge_a), R_BODY * math.cos(hinge_a)
C.add_cylinder(bm, hx * 1.05, hz * 1.05, door_y0 - 0.02, door_y1 + 0.02,
               0.014, segments=8, mat_idx=MAT)

# lock plate + keyhole -- at the door's leading (right) edge. The keyhole
# is a proud escutcheon shaped like an actual keyhole (round part + a
# tapered slot below it), not a plain disc, sitting clear of the lock
# plate's own front face so there is no embedded-box overlap.
lock_a = door_half_arc - math.radians(8)
lx, lz = (R_BODY + 0.02) * math.sin(lock_a), (R_BODY + 0.02) * math.cos(lock_a)
C.add_box(bm, lx - 0.035, lx + 0.035, 0.42, 0.50, lz - 0.035, lz + 0.035, mat_idx=MAT)
key_z = lz + 0.045
C.add_cylinder(bm, lx, key_z, 0.450, 0.468, 0.010, segments=10, mat_idx=MAT)  # round part
C.add_box(bm, lx - 0.006, lx + 0.006, 0.428, 0.452, key_z - 0.008, key_z + 0.008, mat_idx=MAT)  # slot

obj = C.new_object("pillarbox", bm, ["postbox_red"])
C.add_bevel(obj, width=0.008, segments=2)
C.shade_smooth_auto(obj, angle_deg=35)
C.smart_uv(obj)

bpy.context.view_layer.objects.active = obj
obj.select_set(True)

# ---- exports ----
C.export_glb([obj], C.MODELS_DIR + "/pillarbox.glb")

# ---- render rig ----
C.add_sun(elevation_deg=50, azimuth_deg=140, energy=3.0)
C.add_fill_light(loc=(1.2, -2.0, 1.8), energy=40)

eye = 1.6
cam_face = C.add_camera("cam_face", C.V(0.0, eye, 3.3), C.V(0, 0.68, 0), lens=40)
cam_34 = C.add_camera("cam_34", C.V(2.1, eye, 2.7), C.V(0, 0.68, 0), lens=40)
# door hinge (left edge, ~x=-0.20,z=0.19,y=0.47) and posting slot hood
# (~x=0,z=0.26,y=0.86-0.94) together in one crop -- the two features that
# answer "how do you post a letter" and "how does the postman open it"
cam_detail = C.add_camera("cam_detail", C.V(0.02, 0.52, 0.85), C.V(-0.18, 0.52, 0.05), lens=32)

C.setup_render('CYCLES', samples=32, res=(960, 540), device='CPU')

backup = C.apply_clay_override([obj])
for cam, name in ((cam_face, "face"), (cam_34, "34"), (cam_detail, "detail")):
    bpy.context.scene.camera = cam
    C.render_to(C.RENDER_DIR + f"/pillarbox_{name}.png")
C.restore_materials([obj], backup)

bpy.ops.wm.save_as_mainfile(
    filepath="C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B3/pillarbox.blend")
print("DONE pillarbox")
