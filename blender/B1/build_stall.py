"""Asset 2: market-stall — sandbox/assets/models/stall.glb
Trestle stall, footprint ~2.4 x 1.2 m, counter ~0.9 m, canopy ridge ~2.1 m.
Two A-frame trestles (cross-halved legs + peg), top boards with gaps resting
on the trestle rails, side rail, canopy on two poles with visible ties,
produce boxes (crate-like) on the counter.
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
    quick_check, add_box, add_sphere, add_cyl, add_beam,
)

PLANKS, IRON, PLASTER = 0, 1, 2
MAT_NAMES = ["planks", "iron", "plaster"]

LEN, WID, COUNTER_H = 2.4, 1.0, 0.9
BOARD_T = 0.03


def build_trestle(bm, x0):
    """One A-frame trestle at local x=x0, legs splayed in Y, cross-halved at
    mid-height with a peg, plus a stretcher rail below the join."""
    top_y, bot_y = 0.42, 0.14
    # leg A: top -y to bottom +y ; leg B: top +y to bottom -y (they cross)
    legA_top = (x0, -top_y, COUNTER_H - 0.02)
    legA_bot = (x0, bot_y, 0.0)
    legB_top = (x0, top_y, COUNTER_H - 0.02)
    legB_bot = (x0, -bot_y, 0.0)
    add_beam(bm, legA_top, legA_bot, 0.05, 0.05, PLANKS)
    add_beam(bm, legB_top, legB_bot, 0.05, 0.05, PLANKS)
    # peg at the crossing point (legs cross halfway up -- cross-halved joint)
    cross_z = COUNTER_H * 0.42
    add_cyl(bm, (x0, 0, cross_z), 0.018, 0.018, 0.14, IRON, segments=6, axis='y')
    # stretcher rail low down, ties the splayed feet together (also the "side
    # rail" hand-rail the brief calls for)
    add_beam(bm, (x0, -bot_y, 0.18), (x0, bot_y, 0.18), 0.04, 0.03, PLANKS)
    # trestle head -- a short cross-piece the top boards actually rest on
    add_beam(bm, (x0, -0.16, COUNTER_H - 0.015), (x0, 0.16, COUNTER_H - 0.015), 0.09, 0.03, PLANKS)


def build_top_boards(bm):
    n = 5
    board_w = 0.19
    gap = 0.015
    total = n * board_w + (n - 1) * gap
    y0 = -total / 2.0
    for i in range(n):
        y = y0 + i * (board_w + gap) + board_w / 2.0
        add_box(bm, (0, y, COUNTER_H + BOARD_T / 2), (LEN, board_w, BOARD_T), PLANKS)


def build_canopy(bm):
    pole_h = 2.1
    pole_x = LEN / 2.0 + 0.08
    tops = []
    for sx in (-1, 1):
        x = sx * pole_x
        add_cyl(bm, (x, 0, pole_h / 2), 0.03, 0.03, pole_h, PLANKS, segments=8)
        # socket bracket where the pole meets the trestle head
        add_box(bm, (x, 0, COUNTER_H - 0.02), (0.10, 0.10, 0.10), IRON)
        tops.append(mathutils.Vector((x, 0, pole_h)))
    # sagging canvas: a few strips between the poles, dipping at mid-span
    n_strip = 6
    dip = 0.22
    prev_x = prev_z = None
    for i in range(n_strip + 1):
        t = i / n_strip
        x = tops[0].x + (tops[1].x - tops[0].x) * t
        sag = dip * math.sin(math.pi * t)
        z = pole_h - sag
        if prev_x is not None:
            add_box(bm, ((x + prev_x) / 2.0, 0, (z + prev_z) / 2.0),
                    (LEN / n_strip * 1.15, 1.10, 0.05), PLASTER)
        prev_x, prev_z = x, z
    # visible ties at both pole tops (small loops = thin torus-ish ring via
    # short fat cylinder) lashing the canvas to the pole
    for sx in (-1, 1):
        x = sx * pole_x
        add_cyl(bm, (x, 0, pole_h - 0.05), 0.045, 0.045, 0.03, IRON, segments=8, axis='x')


def build_crateish(bm, cx, cy, s=0.32):
    """A small produce-box stand-in on the counter -- boards + corner posts,
    not the full crate asset, kept cheap (this is a prop-on-a-prop)."""
    h = s * 0.8
    for cx2, cy2 in ((cx - s / 2, cy - s / 2), (cx + s / 2, cy - s / 2),
                     (cx - s / 2, cy + s / 2), (cx + s / 2, cy + s / 2)):
        add_box(bm, (cx2, cy2, COUNTER_H + BOARD_T + h / 2), (0.02, 0.02, h), PLANKS)
    for i in range(3):
        z = COUNTER_H + BOARD_T + 0.05 + i * (h - 0.1) / 2
        add_box(bm, (cx, cy, z), (s, s, 0.02), PLANKS)


def build():
    clear_scene()
    bm = bmesh.new()
    for x0 in (-LEN / 2 + 0.18, LEN / 2 - 0.18):
        build_trestle(bm, x0)
    build_top_boards(bm)
    build_canopy(bm)
    build_crateish(bm, -0.55, 0.0)
    build_crateish(bm, 0.15, -0.15, s=0.28)
    obj = new_mesh_object("stall", bm, material_names=MAT_NAMES)
    add_bevel(obj, width=0.006, segments=2)
    apply_all_transforms(obj)
    smart_uv(obj)
    return obj


def render_pass():
    setup_clay_render()
    add_ground_plane(size=6.0)
    add_sun()
    add_fill_sun()
    tgt = mathutils.Vector((0, 0, 1.1))
    add_camera("cam_face", (0, -3.6, 1.6), tgt, lens=45)
    render_to(os.path.join(RENDERS_DIR, "stall_face.png"))
    add_camera("cam_34", (2.6, -2.8, 1.6), tgt, lens=45)
    render_to(os.path.join(RENDERS_DIR, "stall_34.png"))
    add_camera("cam_detail", (LEN / 2 + 0.5, -0.6, 1.3),
               mathutils.Vector((LEN / 2 - 0.1, 0, 0.7)), lens=60)
    render_to(os.path.join(RENDERS_DIR, "stall_detail.png"))


if __name__ == "__main__":
    obj = build()
    bpy.ops.wm.save_as_mainfile(filepath="C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B1/stall.blend")
    if "--quick" in sys.argv:
        add_ground_plane(size=6.0)
        add_camera("cq", (2.6, -2.8, 1.6), mathutils.Vector((0, 0, 1.1)), lens=45)
        quick_check(os.path.join(RENDERS_DIR, "stall_quick.png"), res=800)
    else:
        render_pass()
        export_glb([obj], os.path.join(MODELS_DIR, "stall.glb"))
    print("STALL DONE")
