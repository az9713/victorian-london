"""Asset 4: barrel — sandbox/assets/models/barrel.glb
REBUILD (round 2, judge fail on this asset at 3): the round-1 stave "rods"
were collapsed to one straight cylinder per stave at the mean radius, which
poked past the chime at both ends (read as picket-fence tips) and had no
visible taper. This version follows the actual bulge profile per stave
segment, adds a proper croze + recessed head at the top end, separates the
bung from the middle hoop (they were coincident, reading as one lump), and
gives each hoop a riveted lap joint instead of a plain seamless ring.
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

PLANKS, IRON = 0, 1
MAT_NAMES = ["planks", "iron"]

# body profile: chime -> bilge -> chime, ending at 0.85 so a croze + head
# can sit above it (0.85 -> 0.90) instead of the chime being the top surface.
PROFILE = [
    (0.00, 0.06, 0.255, 0.275),
    (0.06, 0.22, 0.275, 0.315),
    (0.22, 0.68, 0.315, 0.330),  # bilge -- near-cylindrical belly
    (0.68, 0.80, 0.330, 0.275),
    (0.80, 0.85, 0.275, 0.255),
]
STAVE_SEGMENTS = 20
N_STAVES = 12


def radius_at(z):
    for z0, z1, r0, r1 in PROFILE:
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0) if z1 > z0 else 0
            return r0 + (r1 - r0) * t
    return PROFILE[-1][3]


def add_tube(bm, z0, z1, r_outer, r_inner, segments, mat_index):
    """A hollow standing collar (annulus top+bottom, not a solid disk) --
    add_cyl always caps solid, which can't make a rim with a visible hole,
    so the croze collar needs its own helper."""
    outer0, outer1, inner0, inner1 = [], [], [], []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        cx, sx = math.cos(a), math.sin(a)
        outer0.append(bm.verts.new((r_outer * cx, r_outer * sx, z0)))
        outer1.append(bm.verts.new((r_outer * cx, r_outer * sx, z1)))
        inner0.append(bm.verts.new((r_inner * cx, r_inner * sx, z0)))
        inner1.append(bm.verts.new((r_inner * cx, r_inner * sx, z1)))
    for i in range(segments):
        j = (i + 1) % segments
        # outer wall
        f = bm.faces.new((outer0[i], outer0[j], outer1[j], outer1[i]))
        f.material_index = mat_index
        # inner wall (reversed winding, faces inward)
        f = bm.faces.new((inner0[j], inner0[i], inner1[i], inner1[j]))
        f.material_index = mat_index
        # top annulus
        f = bm.faces.new((outer1[i], outer1[j], inner1[j], inner1[i]))
        f.material_index = mat_index
        # bottom annulus
        f = bm.faces.new((inner0[i], inner0[j], outer0[j], outer0[i]))
        f.material_index = mat_index


def add_rivet(bm, center, mat_index):
    """Cheap proud rivet nub -- same low-cost cone pattern used for the
    crate's nail heads (icospheres blow the tri budget at this count)."""
    ret = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=6,
                                 radius1=0.010, radius2=0.006, depth=0.010)
    verts = ret['verts']
    bmesh.ops.translate(bm, vec=center, verts=verts)
    for f in bm.faces:
        if all(v in verts for v in f.verts):
            f.material_index = mat_index


def build():
    clear_scene()
    bm = bmesh.new()
    for z0, z1, r0, r1 in PROFILE:
        add_cyl(bm, (0, 0, (z0 + z1) / 2), r0, r1, z1 - z0, PLANKS, segments=STAVE_SEGMENTS)

    # croze collar + recessed head at the top end
    add_tube(bm, 0.85, 0.895, 0.258, 0.232, STAVE_SEGMENTS, PLANKS)
    add_cyl(bm, (0, 0, 0.865), 0.232, 0.232, 0.02, PLANKS, segments=STAVE_SEGMENTS)  # the head itself

    # 3 iron hoops standing proud -- lower chime, bilge/mid, upper (below
    # the collar) -- none coincide with the bung now
    hoop_zs = (0.09, 0.45, 0.76)
    for hz in hoop_zs:
        r = radius_at(hz) + 0.018
        add_cyl(bm, (0, 0, hz), r, r, 0.045, IRON, segments=STAVE_SEGMENTS)
        # riveted lap joint: a small strap plate tangent to the hoop at a
        # fixed angle, with 2 proud rivet nubs -- not a seamless ring
        lap_r = r + 0.006
        add_cyl(bm, (lap_r, 0, hz), 0.012, 0.012, 0.07, IRON, segments=8, axis='y')
        add_rivet(bm, (lap_r + 0.014, 0, hz + 0.018), IRON)
        add_rivet(bm, (lap_r + 0.014, 0, hz - 0.018), IRON)

    # bung hole -- proud stub plug on the bilge, clear of every hoop
    bung_z = 0.58
    bung_r = radius_at(bung_z)
    add_cyl(bm, (bung_r - 0.01, 0, bung_z), 0.032, 0.032, 0.05, IRON, segments=8, axis='x')

    # stave joints: proud ridges following the ACTUAL bulge profile per
    # segment (not one straight rod at the mean radius -- that poked past
    # the chime at both ends, the round-1 "picket tip" defect).
    for i in range(N_STAVES):
        a = 2 * math.pi * i / N_STAVES
        cx, cy = math.cos(a), math.sin(a)
        for z0, z1, r0, r1 in PROFILE:
            r0p, r1p = r0 - 0.006, r1 - 0.006  # sit just proud of the surface
            add_cyl(bm, (cx * (r0p + r1p) / 2, cy * (r0p + r1p) / 2, (z0 + z1) / 2),
                    0.009, 0.009, z1 - z0, PLANKS, segments=6, axis='z')

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
    # pulled back so the WHOLE barrel (incl. the collar/head at z~0.9) is in
    # frame -- round-1 face/34 cropped the top.
    tgt = mathutils.Vector((0, 0, 0.45))
    add_camera("cam_face", (0, -2.4, 1.5), tgt, lens=50)
    render_to(os.path.join(RENDERS_DIR, "barrel_face.png"))
    add_camera("cam_34", (1.6, -2.0, 1.5), tgt, lens=50)
    render_to(os.path.join(RENDERS_DIR, "barrel_34.png"))
    add_camera("cam_detail", (0.55, -0.15, 0.62), mathutils.Vector((0.15, 0.0, 0.56)), lens=50)
    render_to(os.path.join(RENDERS_DIR, "barrel_detail.png"))


if __name__ == "__main__":
    obj = build()
    bpy.ops.wm.save_as_mainfile(filepath="C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B1/barrel.blend")
    if "--quick" in sys.argv:
        add_ground_plane(size=4.0)
        add_camera("cq", (1.6, -2.0, 1.5), mathutils.Vector((0, 0, 0.45)), lens=50)
        quick_check(os.path.join(RENDERS_DIR, "barrel_quick.png"), res=800)
    else:
        render_pass()
        export_glb([obj], os.path.join(MODELS_DIR, "barrel.glb"))
    print("BARREL DONE")
