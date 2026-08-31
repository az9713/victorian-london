"""Asset 3: crate — sandbox/assets/models/crate.glb
Slatted produce crate, ~0.6 x 0.4 x 0.35 m. Boards + gaps, corner battens,
nail heads, hand holes cut through an end board.
REBUILD (round 2): the hand-hole was previously the topmost board split in
two, open to the sky above -- illegible as a hole. Now it's a proper bounded
rectangle (strip above + strip below + two side segments) cut into a board
one row below the top, with a complete uncut board above it.
Geometry factored into add_crate() so build_stall.py can embed real crates
as produce boxes instead of placeholder corner-post props.
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
    ret = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8,
                                 radius1=NAIL_R, radius2=NAIL_R * 0.7, depth=NAIL_R * 0.9)
    verts = ret['verts']
    bmesh.ops.translate(bm, vec=center, verts=verts)
    for f in bm.faces:
        if all(v in verts for v in f.verts):
            f.material_index = mat_index


def add_crate(bm, origin=(0.0, 0.0, 0.0), scale=1.0, with_nails=True,
               plank_idx=0, iron_idx=1):
    """Build one crate's geometry into bm, offset by origin and uniformly
    scaled. with_nails=False skips the (relatively expensive) nail heads --
    used when a crate is a small embedded prop (e.g. on the stall counter)
    where they'd be invisible anyway, to protect the parent's tri budget."""
    ox, oy, oz = origin
    s = scale
    hx, hy = (L / 2.0) * s, (W / 2.0) * s
    bat = BAT * s
    board_t = BOARD_T * s
    board_h = BOARD_H * s
    gap = GAP * s

    def p(x, y, z):
        return (ox + x, oy + y, oz + z)

    corners = [(hx - bat / 2, hy - bat / 2), (-hx + bat / 2, hy - bat / 2),
               (-hx + bat / 2, -hy + bat / 2), (hx - bat / 2, -hy + bat / 2)]
    for cx, cy in corners:
        add_box(bm, p(cx, cy, H * s / 2), (bat, bat, H * s), plank_idx)

    n_boards = int((H * s - 0.02 * s) // (board_h + gap))
    start_z = 0.03 * s
    long_len = L * s - 2 * bat
    short_len = W * s - 2 * bat
    hole_gap = 0.09 * s          # hand-hole slot width
    hole_strip = 0.012 * s        # material left above/below the hole
    hole_row = max(0, n_boards - 2)  # one row below the top -- top row stays
                                      # a complete, uncut board (the frame)

    for i in range(n_boards):
        z = start_z + i * (board_h + gap) + board_h / 2
        has_hole = with_nails and (i == hole_row) and n_boards >= 2
        # long sides (front/back) run along local X
        for sign in (1, -1):
            add_box(bm, p(0, sign * (hy - board_t / 2), z),
                    (long_len, board_t, board_h), plank_idx)
        # short (end) sides run along local Y
        for sign in (1, -1):
            cx = sign * (hx - board_t / 2)
            if has_hole:
                seg = (short_len - hole_gap) / 2.0
                for off in (1, -1):
                    add_box(bm, p(cx, off * (hole_gap / 2 + seg / 2), z),
                            (board_t, seg, board_h), plank_idx)
                # bounded hole: strip above + strip below, so the hole is a
                # closed rectangle, not open to whatever's above the board
                add_box(bm, p(cx, 0, z + board_h / 2 - hole_strip / 2),
                        (board_t, hole_gap, hole_strip), plank_idx)
                add_box(bm, p(cx, 0, z - board_h / 2 + hole_strip / 2),
                        (board_t, hole_gap, hole_strip), plank_idx)
            else:
                add_box(bm, p(cx, 0, z), (board_t, short_len, board_h), plank_idx)

    n_bottom = 4
    for i in range(n_bottom):
        y = -hy + bat + (i + 0.5) * ((W * s - 2 * bat) / n_bottom)
        add_box(bm, p(0, y, board_t / 2),
                (L * s - 2 * bat + 0.01 * s, W * s / n_bottom - 0.02 * s, board_t), plank_idx)

    if with_nails:
        nail_proud = 0.004 * s
        for i in range(n_boards):
            z = start_z + i * (board_h + gap) + board_h / 2
            for sy in (1, -1):
                for sx in (1, -1):
                    nx = sx * (hx - bat * 0.9)
                    ny = sy * (hy + nail_proud)
                    add_nail(bm, p(nx, ny, z), iron_idx)
            for sx in (1, -1):
                for sy in (1, -1):
                    nx = sx * (hx + nail_proud)
                    ny = sy * (hy - bat * 0.9)
                    add_nail(bm, p(nx, ny, z), iron_idx)


def build():
    clear_scene()
    bm = bmesh.new()
    add_crate(bm, origin=(0, 0, 0), scale=1.0, with_nails=True)
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
    # detail: straight at the end face so the hand-hole is unambiguous
    hole_z = 0.03 + (int((H - 0.02) // (BOARD_H + GAP)) - 2) * (BOARD_H + GAP) + BOARD_H / 2
    add_camera("cam_detail", (0.75, 0.0, hole_z + 0.02), mathutils.Vector((0, 0, hole_z)), lens=60)
    render_to(os.path.join(RENDERS_DIR, "crate_detail.png"))


if __name__ == "__main__":
    obj = build()
    bpy.ops.wm.save_as_mainfile(filepath="C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B1/crate.blend")
    render_pass()
    export_glb([obj], os.path.join(MODELS_DIR, "crate.glb"))
    print("CRATE DONE")
