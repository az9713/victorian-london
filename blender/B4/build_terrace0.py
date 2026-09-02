"""Batch B4 -- terrace0-3.glb / terrace0-4.glb: 1880s shopfront terrace module.
Ground floor: stallriser + big glazed shop window + recessed door/step,
fascia + blank cornice, empty iron sign bracket. Upper floors: sash-pair
windows. See blender/B4/parts.py for the shared geometry helpers.
QUICK=True renders a fast low-sample check pass (960x540, 16 samples) for
look-fix iteration; set QUICK=False for the final acceptance renders.
"""
import bpy
import sys

sys.path.insert(0, "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B4")
import common as C
import parts as P

QUICK = False

C.clear_scene()

variants = [(0, 3), (0, 4)]
objs = []

for variant, storeys in variants:
    obj, wall_top, parapet_top = P.build_module(variant, storeys)
    obj.location.x = 0.0
    objs.append((obj, storeys, wall_top, parapet_top))

for obj, storeys, wall_top, parapet_top in objs:
    C.export_glb([obj], C.MODELS_DIR + f"/terrace0-{storeys}.glb")

C.add_sun(elevation_deg=42, azimuth_deg=130, energy=3.2)
C.add_fill_light(loc=(-6, -9, 10), energy=300)
C.add_world_ambient()

C.setup_render('CYCLES', samples=(16 if QUICK else 32),
                res=((640, 360) if QUICK else (960, 540)), device='CPU')

eye = 1.6
for obj, storeys, wall_top, parapet_top in objs:
    # isolate: hide the other module while rendering this one
    for o2, _, _, _ in objs:
        o2.hide_render = (o2 is not obj)

    cam_face = C.add_camera("cam_face", C.V(0.0, eye, P.Z_FRONT - 9.0),
                             C.V(0.0, 4.2, P.Z_FRONT), lens=32)
    cam_34 = C.add_camera("cam_34", C.V(3.2, eye, P.Z_FRONT - 9.5),
                           C.V(-0.4, 4.4, P.Z_FRONT + 0.6), lens=32)
    cam_detail = C.add_camera("cam_detail", C.V(1.95, 1.15, P.Z_FRONT - 3.0),
                               C.V(1.75, 0.75, P.Z_FRONT), lens=40)
    cam_ctx = C.add_camera("cam_ctx", C.V(4.0, 8.0, P.Z_FRONT - 19.0),
                            C.V(0.2, wall_top * 0.55, P.Z_FRONT + 1.0), lens=24)

    backup = C.apply_clay_override([obj])
    for cam, name in ((cam_face, "face"), (cam_34, "34"), (cam_detail, "detail"),
                       (cam_ctx, "ctx")):
        bpy.context.scene.camera = cam
        suffix = "_quick" if QUICK else ""
        C.render_to(C.RENDER_DIR + f"/terrace0-{storeys}_{name}{suffix}.png")
    C.restore_materials([obj], backup)

    for cam in (cam_face, cam_34, cam_detail, cam_ctx):
        bpy.data.objects.remove(cam, do_unlink=True)

for o2, _, _, _ in objs:
    o2.hide_render = False

# --- r2 fix: top-down + back-3/4 renders, to verify roof coverage ---
# Top view: ortho camera exactly framing the 5x14 footprint (res aspect and
# ortho_scale both matched to 5:14) so the WHOLE image is the footprint --
# no sub-region math needed by the pixel checker. Transparent film so any
# gap reads unambiguously as alpha==0 regardless of world background color.
scene = bpy.context.scene
for obj, storeys, wall_top, parapet_top in objs:
    for o2, _, _, _ in objs:
        o2.hide_render = (o2 is not obj)

    cam_top = C.add_camera("cam_top", C.V(0.0, 30.0, 0.0), C.V(0.0, 0.0, 0.0), lens=35)
    cam_top.data.type = 'ORTHO'
    cam_top.data.ortho_scale = 14.0

    cam_back34 = C.add_camera(
        "cam_back34", C.V(4.5, parapet_top + 4.0, P.Z_BACK + 8.0),
        C.V(0.0, wall_top - 1.0, P.Z_BACK - 3.0), lens=32)

    backup = C.apply_clay_override([obj])

    prev_res = (scene.render.resolution_x, scene.render.resolution_y)
    prev_transparent = scene.render.film_transparent
    prev_color_mode = scene.render.image_settings.color_mode
    scene.render.resolution_x, scene.render.resolution_y = 250, 700
    scene.render.film_transparent = True
    scene.render.image_settings.color_mode = 'RGBA'
    scene.camera = cam_top
    C.render_to(C.RENDER_DIR + f"/terrace0-{storeys}_top.png")
    scene.render.resolution_x, scene.render.resolution_y = prev_res
    scene.render.film_transparent = prev_transparent
    scene.render.image_settings.color_mode = prev_color_mode

    scene.camera = cam_back34
    C.render_to(C.RENDER_DIR + f"/terrace0-{storeys}_back34.png")

    C.restore_materials([obj], backup)
    for cam in (cam_top, cam_back34):
        bpy.data.objects.remove(cam, do_unlink=True)

for o2, _, _, _ in objs:
    o2.hide_render = False

bpy.ops.wm.save_as_mainfile(
    filepath="C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B4/terrace0.blend")
print("DONE terrace0-3 / terrace0-4")
