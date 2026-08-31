"""Asset 4: barrel — sandbox/assets/models/barrel.glb
Wooden cask ~0.9 m tall. Staved bulge profile (chime -> bilge -> chime), 3
iron hoops standing proud, chime bevel at both ends, bung hole on the bilge.
"""
import bpy
import bmesh
import os
import sys
import mathutils

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    new_mesh_object, add_bevel, smart_uv, apply_all_transforms,
    setup_clay_render, add_sun, add_fill_sun, add_camera, render_to,
    export_glb, clear_scene, MODELS_DIR, RENDERS_DIR, add_ground_plane,
    quick_check, add_cyl,
)

PLANKS, IRON = 0, 1
MAT_NAMES = ["planks", "iron"]

H = 0.90
# (z0, z1, r0, r1) stacked frustum segments approximating the barrel bulge:
# chime (narrow rim) -> quarter -> bilge (widest, mid) -> quarter -> chime.
PROFILE = [
    (0.00, 0.06, 0.255, 0.275),
    (0.06, 0.22, 0.275, 0.315),
    (0.22, 0.68, 0.315, 0.330),  # bilge -- near-cylindrical belly
    (0.68, 0.84, 0.330, 0.275),
    (0.84, 0.90, 0.275, 0.255),
]
STAVE_SEGMENTS = 20


def build():
    clear_scene()
    bm = bmesh.new()
    for z0, z1, r0, r1 in PROFILE:
        add_cyl(bm, (0, 0, (z0 + z1) / 2), r0, r1, z1 - z0, PLANKS, segments=STAVE_SEGMENTS)

    def radius_at(z):
        for z0, z1, r0, r1 in PROFILE:
            if z0 <= z <= z1:
                t = (z - z0) / (z1 - z0) if z1 > z0 else 0
                return r0 + (r1 - r0) * t
        return PROFILE[-1][3]

    # 3 iron hoops standing proud -- near each chime + the bilge
    for hz in (0.09, 0.45, 0.81):
        r = radius_at(hz) + 0.018
        add_cyl(bm, (0, 0, hz), r, r, 0.045, IRON, segments=STAVE_SEGMENTS)

    # bung hole -- a small proud stub plug on the bilge face
    bung_r = radius_at(0.45)
    add_cyl(bm, (bung_r - 0.01, 0, 0.45), 0.032, 0.032, 0.05, IRON, segments=8, axis='x')

    # stave joints: thin proud ridges, one per visible stave -- real geometry,
    # not reliant on facet shading. ONE cylinder per stave spanning the full
    # height (not one per profile segment) to stay under the prop 8k tri
    # budget -- a straight rod at the belly's mean radius reads fine at this
    # scale even though it doesn't hug the exact bulge curve.
    import math as _m
    n_visible_staves = 12
    r_mean = sum((r0 + r1) / 2.0 for _, _, r0, r1 in PROFILE) / len(PROFILE)
    for i in range(n_visible_staves):
        a = 2 * _m.pi * i / n_visible_staves
        cx, cy = _m.cos(a), _m.sin(a)
        add_cyl(bm, (cx * (r_mean - 0.006), cy * (r_mean - 0.006), H / 2),
                0.010, 0.010, H, PLANKS, segments=6, axis='z')

    obj = new_mesh_object("barrel", bm, material_names=MAT_NAMES)
    add_bevel(obj, width=0.006, segments=1)  # segments=1 to stay under the 8k prop tri budget
    apply_all_transforms(obj)
    bpy.ops.object.shade_smooth()
    smart_uv(obj)
    return obj


def render_pass():
    setup_clay_render()
    add_ground_plane(size=4.0)
    add_sun()
    add_fill_sun()
    tgt = mathutils.Vector((0, 0, 0.45))
    add_camera("cam_face", (0, -1.9, 1.4), tgt, lens=55)
    render_to(os.path.join(RENDERS_DIR, "barrel_face.png"))
    add_camera("cam_34", (1.3, -1.5, 1.4), tgt, lens=55)
    render_to(os.path.join(RENDERS_DIR, "barrel_34.png"))
    add_camera("cam_detail", (0.45, -0.35, 0.5), mathutils.Vector((0.30, 0, 0.45)), lens=70)
    render_to(os.path.join(RENDERS_DIR, "barrel_detail.png"))


if __name__ == "__main__":
    obj = build()
    bpy.ops.wm.save_as_mainfile(filepath="C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B1/barrel.blend")
    if "--quick" in sys.argv:
        add_ground_plane(size=4.0)
        add_camera("cq", (1.3, -1.5, 1.4), mathutils.Vector((0, 0, 0.45)), lens=55)
        quick_check(os.path.join(RENDERS_DIR, "barrel_quick.png"), res=800)
    else:
        render_pass()
        export_glb([obj], os.path.join(MODELS_DIR, "barrel.glb"))
    print("BARREL DONE")
