"""Smoke test: validate common.py helpers end-to-end before real geometry."""
import bpy
import bmesh
import sys

sys.path.insert(0, "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2")
import common as C

C.clear_scene()

bm = bmesh.new()
v, faces = C.add_box(bm, -1, 1, 0, 2, -0.5, 0.5, mat_idx=0)
v2, faces2 = C.add_box(bm, -0.8, 0.8, 0.5, 1.2, 0.55, 0.6, mat_idx=1)
obj = C.new_object("SmokeTest", bm, ["stone", "glass"])
C.add_bevel(obj, width=0.02, segments=2)
C.smart_uv(obj)

C.bbox_and_tris([obj])

C.export_glb([obj], "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/smoketest.glb")

C.setup_render(engine='BLENDER_WORKBENCH', res=(640, 480))
scene = bpy.context.scene
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'MATERIAL'
C.add_camera("Cam", C.V(3, 1.2, -3), C.V(0, 1, 0), lens=35)
C.render_to("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/smoketest.png")

print("[smoketest] OK")
