"""Asset 3: crate — sandbox/assets/models/crate.glb
Slatted produce crate, ~0.6 x 0.4 x 0.35 m. Boards + gaps, corner battens,
nail heads, hand holes cut through the top end boards.
"""
import bpy
import bmesh
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    new_mesh_object, add_bevel, smart_uv, apply_all_transforms,
    setup_clay_render, add_sun, add_fill_sun, add_camera, render_to,
    export_glb, clear_scene, MODELS_DIR, RENDERS_DIR, get_shared_material,
    add_ground_plane, quick_check,
)

L, W, H = 0.60, 0.40, 0.35          # overall footprint length/width, height
BAT = 0.03                           # batten cross-section
BOARD_T = 0.014                      # board thickness
BOARD_H = 0.055                      # board face height
GAP = 0.012                          # gap between boards
NAIL_R = 0.012                       # clout-nail head, sized to actually read in render


def add_box(bm, center, size, mat_index):
    before = set(bm.faces)
    ret = bmesh.ops.create_cube(bm, size=1.0)
    verts = ret['verts']
    bmesh.ops.scale(bm, vec=size, verts=verts)
    bmesh.ops.translate(bm, vec=center, verts=verts)
    for f in bm.faces:
        if f not in before:
            f.material_index = mat_index


def add_nail(bm, center, mat_index):
    # a squat hex-segment cone reads as a proud nail head at this scale for a
    # fraction of an icosphere's tris (icosphere subdiv=1 is 80 tris; this is
    # ~16) -- needed to keep the whole crate under the prop 8k tri budget.
    before = set(bm.faces)
    ret = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8,
                                 radius1=NAIL_R, radius2=NAIL_R * 0.7, depth=NAIL_R * 0.9)
    verts = ret['verts']
    bmesh.ops.translate(bm, vec=center, verts=verts)
    for f in bm.faces:
        if f not in before:
            f.material_index = mat_index


def build():
    clear_scene()
    bm = bmesh.new()
    PLANKS, IRON = 0, 1

    hx, hy = L / 2.0, W / 2.0
    corners = [(hx - BAT / 2, hy - BAT / 2), (-hx + BAT / 2, hy - BAT / 2),
               (-hx + BAT / 2, -hy + BAT / 2), (hx - BAT / 2, -hy + BAT / 2)]
    for cx, cy in corners:
        add_box(bm, (cx, cy, H / 2), (BAT, BAT, H), PLANKS)

    # boards stacked up the height on all 4 sides, gap between boards + a gap
    # above the ground (crate stands proud, not flush) and below the rim.
    n_boards = int((H - 0.02) // (BOARD_H + GAP))
    start_z = 0.03
    long_len = L - 2 * BAT
    short_len = W - 2 * BAT
    hole_gap = 0.09  # hand-hole slot width

    for i in range(n_boards):
        z = start_z + i * (BOARD_H + GAP) + BOARD_H / 2
        is_top = (i == n_boards - 1)
        # long sides (front z=+hy row, back z=-hy row) run along X
        for sign in (1, -1):
            add_box(bm, (0, sign * (hy - BOARD_T / 2), z),
                    (long_len, BOARD_T, BOARD_H), PLANKS)
        # short (end) sides run along Y — topmost board gets a hand-hole gap
        for sign in (1, -1):
            cx = sign * (hx - BOARD_T / 2)
            if is_top:
                seg = (short_len - hole_gap) / 2.0
                for off in (1, -1):
                    add_box(bm, (cx, off * (hole_gap / 2 + seg / 2), z),
                            (BOARD_T, seg, BOARD_H), PLANKS)
            else:
                add_box(bm, (cx, 0, z), (BOARD_T, short_len, BOARD_H), PLANKS)

    # bottom boards, perpendicular to the long sides, resting on the battens
    n_bottom = 4
    for i in range(n_bottom):
        y = -hy + BAT + (i + 0.5) * ((W - 2 * BAT) / n_bottom)
        add_box(bm, (0, y, BOARD_T / 2), (L - 2 * BAT + 0.01, W / n_bottom - 0.02, BOARD_T), PLANKS)

    # nail heads: proud on the OUTER face of each board near the corner batten
    # it's nailed into (not embedded inside the batten, which is invisible).
    NAIL_PROUD = 0.004
    for i in range(n_boards):
        z = start_z + i * (BOARD_H + GAP) + BOARD_H / 2
        for sy in (1, -1):      # long-side (front/back) boards, face at y=sy*hy
            for sx in (1, -1):  # one nail near each end, into that corner batten
                nx = sx * (hx - BAT * 0.9)
                ny = sy * (hy + NAIL_PROUD)
                add_nail(bm, (nx, ny, z), IRON)
        for sx in (1, -1):      # short-side (end) boards, face at x=sx*hx
            for sy in (1, -1):
                nx = sx * (hx + NAIL_PROUD)
                ny = sy * (hy - BAT * 0.9)
                add_nail(bm, (nx, ny, z), IRON)

    obj = new_mesh_object("crate", bm, material_names=["planks", "iron"])
    add_bevel(obj, width=0.003, segments=1)  # segments=1 to stay under the 8k prop tri budget
    apply_all_transforms(obj)
    smart_uv(obj)
    return obj


def render_pass():
    setup_clay_render()
    add_ground_plane(size=3.0)
    add_sun()
    add_fill_sun()
    center = (0, 0, H / 2)
    import mathutils
    tgt = mathutils.Vector(center)
    # small prop (0.6 x 0.4 x 0.35 m): 1.6 m standing eye height per COMMON, but
    # pulled back to 2.0 m so the downward look angle is a natural ~35 deg
    # instead of foreshortening into the open top; lens 50 fills the frame.
    add_camera("cam_face", (0, -2.0, 1.6), tgt, lens=50)
    render_to(os.path.join(RENDERS_DIR, "crate_face.png"))
    add_camera("cam_34", (1.4, -1.6, 1.6), tgt, lens=50)
    render_to(os.path.join(RENDERS_DIR, "crate_34.png"))
    add_camera("cam_detail", (0.5, -0.5, 1.0), mathutils.Vector((L / 2 - 0.05, 0, H - 0.06)), lens=65)
    render_to(os.path.join(RENDERS_DIR, "crate_detail.png"))


if __name__ == "__main__":
    obj = build()
    bpy.ops.wm.save_as_mainfile(filepath="C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B1/crate.blend")
    render_pass()
    export_glb([obj], os.path.join(MODELS_DIR, "crate.glb"))
    print("CRATE DONE")
