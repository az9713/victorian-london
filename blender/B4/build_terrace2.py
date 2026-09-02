"""Batch B4 -- terrace2-3.glb / terrace2-4.glb: 1880s warehouse terrace module.
Ground floor: wide segmental-arch cart entrance, dark open reveal, folded
cart-door leaves. Floor 2: loading door with strap hinges + projecting
hoist beam, knee brace, pulley wheel, hanging chain. Other upper floors:
small square windows. See blender/B4/parts.py for shared geometry helpers.
QUICK=True renders a fast low-sample check pass for look-fix iteration;
set QUICK=False for the final acceptance renders.
"""
import bpy
import sys

sys.path.insert(0, "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B4")
import common as C
import parts as P

QUICK = False

C.clear_scene()

variants = [(2, 3), (2, 4)]
objs = []

for variant, storeys in variants:
    obj, wall_top, parapet_top = P.build_module(variant, storeys)
    obj.location.x = 0.0
    objs.append((obj, storeys, wall_top, parapet_top))

for obj, storeys, wall_top, parapet_top in objs:
    C.export_glb([obj], C.MODELS_DIR + f"/terrace2-{storeys}.glb")

C.add_sun(elevation_deg=42, azimuth_deg=130, energy=3.2)
C.add_fill_light(loc=(-6, -9, 10), energy=300)
C.add_world_ambient()

C.setup_render('CYCLES', samples=(16 if QUICK else 32),
                res=((640, 360) if QUICK else (960, 540)), device='CPU')

eye = 1.6
for obj, storeys, wall_top, parapet_top in objs:
    for o2, _, _, _ in objs:
        o2.hide_render = (o2 is not obj)

    cam_face = C.add_camera("cam_face", C.V(0.0, eye, P.Z_FRONT - 9.5),
                             C.V(0.0, 4.5, P.Z_FRONT), lens=32)
    cam_34 = C.add_camera("cam_34", C.V(3.3, eye, P.Z_FRONT - 10.0),
                           C.V(-0.4, 4.7, P.Z_FRONT + 0.6), lens=32)
    # detail: side-on view of the beam's projecting length + pulley wheel +
    # knee brace, angled so the "sticks out from the wall" read is legible
    cam_detail = C.add_camera("cam_detail", C.V(2.7, 7.35, P.Z_FRONT - 2.2),
                               C.V(0.0, 7.05, P.Z_FRONT - 1.0), lens=32)
    cam_ctx = C.add_camera("cam_ctx", C.V(4.0, 8.0, P.Z_FRONT - 19.0),
                            C.V(0.2, wall_top * 0.55, P.Z_FRONT + 1.0), lens=24)

    backup = C.apply_clay_override([obj])
    for cam, name in ((cam_face, "face"), (cam_34, "34"), (cam_detail, "detail"),
                       (cam_ctx, "ctx")):
        bpy.context.scene.camera = cam
        suffix = "_quick" if QUICK else ""
        C.render_to(C.RENDER_DIR + f"/terrace2-{storeys}_{name}{suffix}.png")
    C.restore_materials([obj], backup)

    for cam in (cam_face, cam_34, cam_detail, cam_ctx):
        bpy.data.objects.remove(cam, do_unlink=True)

for o2, _, _, _ in objs:
    o2.hide_render = False

# --- r2 fix: top-down + back-3/4 renders, to verify roof coverage ---
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
    C.render_to(C.RENDER_DIR + f"/terrace2-{storeys}_top.png")
    scene.render.resolution_x, scene.render.resolution_y = prev_res
    scene.render.film_transparent = prev_transparent
    scene.render.image_settings.color_mode = prev_color_mode

    scene.camera = cam_back34
    C.render_to(C.RENDER_DIR + f"/terrace2-{storeys}_back34.png")

    C.restore_materials([obj], backup)
    for cam in (cam_top, cam_back34):
        bpy.data.objects.remove(cam, do_unlink=True)

for o2, _, _, _ in objs:
    o2.hide_render = False

bpy.ops.wm.save_as_mainfile(
    filepath="C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B4/terrace2.blend")
print("DONE terrace2-3 / terrace2-4")
