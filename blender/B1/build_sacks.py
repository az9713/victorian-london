"""Asset 5: sack-pile — sandbox/assets/models/sacks.glb
2-3 jute sacks, slumped under their own weight, tied necks, creases at
contact points. Material named "cloth" per brief override (not plaster).
"""
import bpy
import bmesh
import math
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

CLOTH = 0
MAT_NAMES = ["cloth"]

# stacked-frustum silhouette per sack: (z0, z1, r0, r1). Deliberately NOT a
# smooth monotonic taper -- a slight bulge/pinch pattern reads as a slumped,
# lumpy jute sack rather than a balloon.
SACK_PROFILE = [
    (0.00, 0.03, 0.22, 0.26),   # flattened footprint where it rests
    (0.03, 0.12, 0.26, 0.30),   # bulge just above the contact patch
    (0.12, 0.22, 0.30, 0.27),   # slight pinch -- a crease under its own weight
    (0.22, 0.34, 0.27, 0.29),   # belly
    (0.34, 0.42, 0.29, 0.19),   # shoulder narrowing
    (0.42, 0.50, 0.19, 0.07),   # neck
    (0.50, 0.55, 0.07, 0.045),  # gathered neck, about to be tied
]
SEGMENTS = 14


def build_sack(bm, cx, cy, scale, tilt_deg, twist_deg, squash):
    """One sack: lathe profile, then squash + tilt so it reads as slumped
    rather than standing perfectly upright."""
    before = set(bm.verts)
    for z0, z1, r0, r1 in SACK_PROFILE:
        add_cyl(bm, (0, 0, (z0 + z1) / 2), r0, r1, z1 - z0, CLOTH, segments=SEGMENTS)
    # tied neck knot -- a blunt gathered knob, not a sharp spike
    add_cyl(bm, (0, 0, 0.55 + 0.025), 0.05, 0.028, 0.045, CLOTH, segments=8)

    # collect every vert we just made (this sack only) to transform in place
    all_verts = set(bm.verts) - before

    # rotate/squash around the sack's own base first (no translation yet) so
    # we can measure how far the tilt drops it, then snap the lowest point
    # back to the ground and only THEN move it to (cx, cy) -- otherwise a
    # steep tilt rotates the sack up into the air or through the floor.
    local_mat = (mathutils.Matrix.Rotation(math.radians(tilt_deg), 4, 'X') @
                 mathutils.Matrix.Rotation(math.radians(twist_deg), 4, 'Z') @
                 mathutils.Matrix.Diagonal((squash[0] * scale, squash[1] * scale, scale, 1.0)))
    for v in all_verts:
        v.co = local_mat @ v.co
    min_z = min(v.co.z for v in all_verts)
    for v in all_verts:
        v.co.x += cx
        v.co.y += cy
        v.co.z -= min_z


def build():
    clear_scene()
    bm = bmesh.new()
    # three sacks, overlapping footprints, different tilt/twist/scale so the
    # pile reads as several distinct slumped bodies, not one repeated shape.
    build_sack(bm, -0.20, -0.08, 1.00, tilt_deg=58, twist_deg=20, squash=(1.05, 0.95))
    build_sack(bm, 0.20, 0.10, 0.88, tilt_deg=-68, twist_deg=-35, squash=(0.95, 1.08))
    build_sack(bm, 0.00, -0.30, 0.75, tilt_deg=42, twist_deg=95, squash=(1.10, 0.92))

    obj = new_mesh_object("sacks", bm, material_names=MAT_NAMES)
    add_bevel(obj, width=0.01, segments=2)
    apply_all_transforms(obj)
    bpy.ops.object.shade_smooth()
    smart_uv(obj)
    return obj


def render_pass():
    setup_clay_render()
    add_ground_plane(size=4.0)
    add_sun()
    add_fill_sun()
    tgt = mathutils.Vector((0, 0, 0.22))
    add_camera("cam_face", (0, -1.7, 1.3), tgt, lens=55)
    render_to(os.path.join(RENDERS_DIR, "sacks_face.png"))
    add_camera("cam_34", (1.2, -1.3, 1.3), tgt, lens=55)
    render_to(os.path.join(RENDERS_DIR, "sacks_34.png"))
    add_camera("cam_detail", (-0.9, -0.9, 0.75), mathutils.Vector((-0.2, -0.1, 0.25)), lens=45)
    render_to(os.path.join(RENDERS_DIR, "sacks_detail.png"))


if __name__ == "__main__":
    obj = build()
    bpy.ops.wm.save_as_mainfile(filepath="C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B1/sacks.blend")
    if "--quick" in sys.argv:
        add_ground_plane(size=4.0)
        add_camera("cq", (1.2, -1.3, 1.3), mathutils.Vector((0, 0, 0.22)), lens=55)
        quick_check(os.path.join(RENDERS_DIR, "sacks_quick.png"), res=800)
    else:
        render_pass()
        export_glb([obj], os.path.join(MODELS_DIR, "sacks.glb"))
    print("SACKS DONE")
