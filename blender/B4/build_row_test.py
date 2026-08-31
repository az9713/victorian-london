"""Batch B4 -- row tiling check. Imports the exported GLBs (not the bmesh
build functions) so the check validates the actual round-tripped export,
placing terrace0-3, terrace1-3, terrace2-3 side by side at x = -5, 0, +5
(module width 5.00 exactly -> side walls meet at x = -7.5/-2.5/2.5/7.5).
Checks: no gaps, no protrusions crossing a module boundary, chimneys
alternating (V0 +x / V1 -x / V2 +x -> right/left/right along the row).
"""
import bpy
import sys

sys.path.insert(0, "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B4")
import common as C
import parts as P

C.clear_scene()

MODELS = C.MODELS_DIR
row = [
    ("terrace0-3.glb", -5.0),
    ("terrace1-3.glb", 0.0),
    ("terrace2-3.glb", 5.0),
]

imported = []
for fname, x_offset in row:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=MODELS + "/" + fname)
    after = set(bpy.data.objects) - before
    mesh_objs = [o for o in after if o.type == 'MESH']
    for o in mesh_objs:
        o.location.x += x_offset
    imported.append((fname, x_offset, mesh_objs))

# bounding-box check: each module's own width must be exactly 5.00
from mathutils import Vector

print("=== bounding box check ===")
for fname, x_offset, objs in imported:
    xs = []
    for o in objs:
        for corner in o.bound_box:
            xs.append((o.matrix_world @ Vector(corner)).x)
    if xs:
        width = max(xs) - min(xs)
        print(f"{fname}: x range [{min(xs):.3f}, {max(xs):.3f}] width={width:.3f} "
              f"(expected 5.000, centre offset {x_offset})")

C.add_sun(elevation_deg=38, azimuth_deg=128, energy=3.2)
C.add_fill_light(loc=(0, -12, 10), energy=500)
C.add_world_ambient()

C.setup_render('CYCLES', samples=32, res=(1280, 640), device='CPU')

all_mesh_objs = [o for _, _, objs in imported for o in objs]
backup = C.apply_clay_override(all_mesh_objs)

cam_row = C.add_camera("cam_row", C.V(1.0, 8.5, P.Z_FRONT - 21.0),
                        C.V(0.0, 6.0, P.Z_FRONT + 1.0), lens=22)
bpy.context.scene.camera = cam_row
C.render_to(C.RENDER_DIR + "/row_ctx.png")

# two closer passes straight down the row to inspect both joints
cam_join = C.add_camera("cam_join", C.V(-2.5, 3.0, P.Z_FRONT - 6.5),
                         C.V(0.0, 4.0, P.Z_FRONT + 1.0), lens=28)
bpy.context.scene.camera = cam_join
C.render_to(C.RENDER_DIR + "/row_joint_check.png")

# second joint: terrace0/terrace1 boundary at world x=-2.5, framed on the
# shopfront's fascia band specifically (the judge round-1 fail location --
# terrace0 spans world x [-7.5,-2.5], its fascia end is right at this line)
cam_join2 = C.add_camera("cam_join2", C.V(-2.5, 2.6, P.Z_FRONT - 4.5),
                          C.V(-2.5, 2.75, P.Z_FRONT + 1.0), lens=30)
bpy.context.scene.camera = cam_join2
C.render_to(C.RENDER_DIR + "/row_joint_check2_fascia.png")

C.restore_materials(all_mesh_objs, backup)

bpy.ops.wm.save_as_mainfile(
    filepath="C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B4/row_test.blend")
print("DONE row test")
