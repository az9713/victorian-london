"""Asset 1: market (L1) — sandbox/assets/models/market.glb
1880s Spitalfields-style glass-and-iron market hall. Footprint 84 x 44 m,
eaves +9.00, ridge +14.00 (running west-east = local X). Origin: footprint
centre, ground z=0. Local X = 84 m long axis, Local Y = 44 m depth (world
north-south), Local Z = height. Exported with export_yup so world X=east,
Y=up, Z=north-south — matches sandbox/layout.js MB centred at (234.5,150).
"""
import bpy
import bmesh
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    new_mesh_object, add_bevel, smart_uv, apply_all_transforms,
    setup_clay_render, add_sun, add_fill_sun, add_camera, render_to,
    export_glb, clear_scene, MODELS_DIR, RENDERS_DIR, add_ground_plane,
    quick_check, add_box, add_sphere, add_cyl, add_beam, add_prism_xz,
    add_prism_yz,
)

X_HALF, Y_HALF = 42.0, 22.0
EAVE_Z, RIDGE_Z = 9.0, 14.0
PLINTH_H = 0.6
PIER_W, PIER_T = 1.4, 0.9
BAY = 12.0
OVERHANG = 0.8  # eave overhang past the wall face, real geometry per COMMON
ROOF_SLOPE = (RIDGE_Z - EAVE_Z) / Y_HALF
EAVE_TIP_Z = EAVE_Z - ROOF_SLOPE * OVERHANG  # roof continues its own pitch past the wall
ENTRANCE_HALF = 6.0  # brief: 12 m wide entrance -> +-6.0 CLEAR opening
JAMB_Y = ENTRANCE_HALF + PIER_W / 2.0  # jamb pier centre so the clear gap is exactly 12 m
BRICK, IRON, GLASS, SLATE, STONE = 0, 1, 2, 3, 4
MAT_NAMES = ["brick", "iron", "glass", "slate", "stone"]


def roof_z(y):
    """Height of the gable roof at depth y (y in [-Y_HALF, Y_HALF])."""
    t = abs(y) / Y_HALF
    return RIDGE_Z - (RIDGE_Z - EAVE_Z) * t


def arch_profile(u_left, u_right, z_spring, z_crown, z_top, n=8):
    """Closed polygon: curved (parabolic) soffit from spring to spring bulging
    to z_crown at mid-span, capped flat at z_top. Returned as list of (u,z)."""
    pts = []
    for i in range(n + 1):
        t = i / n
        u = u_left + (u_right - u_left) * t
        z = z_spring + 4.0 * (z_crown - z_spring) * t * (1 - t)
        pts.append((u, z))
    pts.append((u_right, z_top))
    pts.append((u_left, z_top))
    return pts


def build_pier_long(bm, x, y_outer, sign_y):
    """Pier on a long wall (runs along X), outer face at y_outer, thickness
    into the building by sign_y."""
    y0, y1 = (y_outer, y_outer - sign_y * PIER_T) if sign_y > 0 else (y_outer - sign_y * PIER_T, y_outer)
    yc = (y0 + y1) / 2.0
    add_box(bm, (x, yc, PLINTH_H / 2), (PIER_W + 0.3, PIER_T + 0.3, PLINTH_H), BRICK)
    add_box(bm, (x, yc, (PLINTH_H + EAVE_Z) / 2), (PIER_W, PIER_T, EAVE_Z - PLINTH_H), BRICK)


def build_pier_short(bm, y, x_outer, sign_x):
    x0, x1 = (x_outer, x_outer - sign_x * PIER_T) if sign_x > 0 else (x_outer - sign_x * PIER_T, x_outer)
    xc = (x0 + x1) / 2.0
    add_box(bm, (xc, y, PLINTH_H / 2), (PIER_T + 0.3, PIER_W + 0.3, PLINTH_H), BRICK)
    add_box(bm, (xc, y, (PLINTH_H + EAVE_Z) / 2), (PIER_T, PIER_W, EAVE_Z - PLINTH_H), BRICK)


def build_long_wall(bm, sign_y):
    y_outer = sign_y * Y_HALF
    xs = [-X_HALF + i * BAY for i in range(int(2 * X_HALF / BAY) + 1)]  # -42..42 step 12
    for x in xs:
        build_pier_long(bm, x, y_outer, sign_y)
    y0 = y_outer - sign_y * 0.05
    y1 = y_outer - sign_y * PIER_T
    for i in range(len(xs) - 1):
        u_left = xs[i] + PIER_W / 2
        u_right = xs[i + 1] - PIER_W / 2
        pts = arch_profile(u_left, u_right, 4.8, 6.8, EAVE_Z)
        add_prism_xz(bm, pts, min(y0, y1), max(y0, y1), BRICK)


def build_short_wall(bm, sign_x):
    x_outer = sign_x * X_HALF
    ys = [-Y_HALF, -14, -JAMB_Y, JAMB_Y, 14, Y_HALF]
    for y in ys:
        build_pier_short(bm, y, x_outer, sign_x)
    x0 = x_outer - sign_x * 0.05
    x1 = x_outer - sign_x * PIER_T
    xlo, xhi = min(x0, x1), max(x0, x1)
    for i in range(len(ys) - 1):
        v_left = ys[i] + PIER_W / 2
        v_right = ys[i + 1] - PIER_W / 2
        is_entrance = (ys[i] == -JAMB_Y and ys[i + 1] == JAMB_Y)
        if is_entrance:
            pts = arch_profile(v_left, v_right, 2.6, 7.5, EAVE_Z)
        else:
            pts = arch_profile(v_left, v_right, 4.8, 6.8, EAVE_Z)
        add_prism_yz(bm, pts, xlo, xhi, BRICK)
    # keystone on the entrance crown
    kz = 7.5 + 0.35
    add_box(bm, (x_outer - sign_x * PIER_T / 2, 0, kz), (PIER_T + 0.15, 0.7, 0.5), BRICK)
    # gate posts + hinge plates + threshold — inside the true 12 m CLEAR
    # opening (jamb pier centre is at JAMB_Y so the inner face sits at
    # ENTRANCE_HALF exactly, per brief figure).
    clear_half = ENTRANCE_HALF
    post_y = clear_half - 0.2
    post_h = 2.6
    for sy in (-1, 1):
        py = sy * post_y
        add_cyl(bm, (x_outer - sign_x * PIER_T / 2, py, post_h / 2), 0.09, 0.09, post_h, IRON, axis='z')
        for hz in (0.9, 2.0):
            add_box(bm, (x_outer - sign_x * (PIER_T / 2 - 0.05), py - sy * 0.14, hz),
                    (0.05, 0.28, 0.10), IRON)
    add_box(bm, (x_outer - sign_x * 0.3, 0, 0.08), (0.7, clear_half * 2 - 0.2, 0.16), STONE)
    # radiating iron ribs across the glazed gable-end screen above the entrance
    apex = (x_outer, 0, RIDGE_Z)
    for yv in (-20, -13, -6.5, 0, 6.5, 13, 20):
        base = (x_outer, yv, roof_z(yv))
        add_beam(bm, base, apex, 0.10, 0.10, IRON)
    gable_pts = [(-Y_HALF, EAVE_Z), (0, RIDGE_Z), (Y_HALF, EAVE_Z),
                 (Y_HALF, EAVE_Z - 0.15), (0, RIDGE_Z - 0.15), (-Y_HALF, EAVE_Z - 0.15)]
    gx = x_outer - sign_x * (PIER_T + 0.08)
    add_prism_yz(bm, gable_pts, min(gx, gx - sign_x * 0.15), max(gx, gx - sign_x * 0.15), GLASS)


COLUMN_XS = [-30, -18, -6, 6, 18, 30]  # SAME x as the interior truss stations
                                        # (BAY=12 apart) so the bracket lands
                                        # on an actual truss, not empty air.


def build_columns(bm):
    for x in COLUMN_XS:
        for y in (-10, 10):
            add_cyl(bm, (x, y, 0.09), 0.40, 0.40, 0.18, IRON, segments=12)       # base plate, wide + proud
            add_cyl(bm, (x, y, 0.18 + 0.10), 0.20, 0.16, 0.20, IRON, segments=12)  # base taper into shaft
            add_cyl(bm, (x, y, 0.48 + 4.0), 0.14, 0.14, 8.0, IRON, segments=12)  # shaft
            add_cyl(bm, (x, y, 8.5), 0.14, 0.26, 0.22, IRON, segments=12)        # capital, flares out
            add_cyl(bm, (x, y, 8.72), 0.26, 0.26, 0.10, IRON, segments=12)       # capital abacus (flat neck)
            add_cyl(bm, (x, y, 8.88), 0.24, 0.44, 0.30, IRON, segments=12)       # bracket flare, overlaps the
                                                                                   # truss bottom tie at EAVE_Z


def build_trusses(bm):
    xs = [-X_HALF + i * BAY for i in range(int(2 * X_HALF / BAY) + 1)]
    for x in xs:
        add_beam(bm, (x, -Y_HALF, EAVE_Z), (x, Y_HALF, EAVE_Z), 0.14, 0.18, IRON)  # bottom tie
        for sy in (-1, 1):
            add_beam(bm, (x, sy * Y_HALF, EAVE_Z), (x, 0, RIDGE_Z), 0.10, 0.14, IRON)  # rafter chord
            for yv in (sy * 7, sy * 14):
                add_beam(bm, (x, yv, EAVE_Z), (x, yv, roof_z(yv)), 0.06, 0.06, IRON)  # queen strut
            add_beam(bm, (x, sy * 5.5, EAVE_Z), (x, sy * 11, roof_z(sy * 11) - 0.4), 0.05, 0.05, IRON)  # diag brace


def build_roof(bm):
    # eave overhang: the roof plane keeps its own pitch OVERHANG past the wall
    # face instead of stopping flush at it -- real drip edge, per COMMON.
    y_tip = Y_HALF + OVERHANG
    profile = [(-y_tip, EAVE_TIP_Z), (-Y_HALF, EAVE_Z), (0, RIDGE_Z),
               (Y_HALF, EAVE_Z), (y_tip, EAVE_TIP_Z),
               (y_tip, EAVE_TIP_Z - 0.15), (Y_HALF, EAVE_Z - 0.15),
               (0, RIDGE_Z - 0.15), (-Y_HALF, EAVE_Z - 0.15), (-y_tip, EAVE_TIP_Z - 0.15)]
    add_prism_yz(bm, profile, -X_HALF, X_HALF, GLASS)
    xs = list(range(-39, 40, 6))
    for x in xs:
        for sy in (-1, 1):
            add_beam(bm, (x, sy * 0.3, roof_z(sy * 0.3) + 0.05),
                      (x, sy * y_tip, EAVE_TIP_Z + 0.05), 0.08, 0.05, IRON)
    for yv in (-18, -13, -8, 8, 13, 18):
        add_beam(bm, (-X_HALF, yv, roof_z(yv) + 0.06), (X_HALF, yv, roof_z(yv) + 0.06), 0.08, 0.05, IRON)
    add_beam(bm, (-X_HALF, 0, RIDGE_Z + 0.08), (X_HALF, 0, RIDGE_Z + 0.08), 0.12, 0.08, IRON)


def build_lantern(bm):
    x0, x1 = -34.0, 34.0
    y0, y1 = -1.6, 1.6
    z0, z1 = RIDGE_Z, RIDGE_Z + 1.2
    add_box(bm, (0, y0 + 0.06, (z0 + z1) / 2), (x1 - x0, 0.12, z1 - z0), GLASS)
    add_box(bm, (0, y1 - 0.06, (z0 + z1) / 2), (x1 - x0, 0.12, z1 - z0), GLASS)
    for x in (x0, x1):
        add_box(bm, (x, 0, (z0 + z1) / 2), (0.14, y1 - y0, z1 - z0), IRON)
    cap = [(y0, z1), (0, z1 + 0.6), (y1, z1), (y1, z1 - 0.12), (0, z1 + 0.48), (y0, z1 - 0.12)]
    add_prism_yz(bm, cap, x0, x1, SLATE)


def build_gutters_downpipes(bm):
    # gutter sits under the drip edge at the overhang tip, not inside the wall
    y_tip = Y_HALF + OVERHANG
    for sign_y in (-1, 1):
        y_gutter = sign_y * (y_tip - 0.12)
        add_beam(bm, (-X_HALF, y_gutter, EAVE_TIP_Z + 0.10),
                  (X_HALF, y_gutter, EAVE_TIP_Z + 0.10), 0.22, 0.16, IRON)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x = sx * (X_HALF - 0.3)
            y = sy * (y_tip - 0.12)
            add_cyl(bm, (x, y, EAVE_TIP_Z / 2), 0.06, 0.06, EAVE_TIP_Z, IRON, segments=8)
            add_box(bm, (x, y, EAVE_TIP_Z + 0.10), (0.22, 0.22, 0.3), IRON)


def build():
    clear_scene()
    bm = bmesh.new()
    build_long_wall(bm, 1)
    build_long_wall(bm, -1)
    build_short_wall(bm, 1)
    build_short_wall(bm, -1)
    build_columns(bm)
    build_trusses(bm)
    build_roof(bm)
    build_lantern(bm)
    build_gutters_downpipes(bm)
    obj = new_mesh_object("market", bm, material_names=MAT_NAMES)
    add_bevel(obj, width=0.02, segments=2)
    apply_all_transforms(obj)
    smart_uv(obj)
    return obj


def render_pass():
    setup_clay_render(res_x=960, res_y=540)
    add_ground_plane(size=100.0, material="stone")
    add_sun(energy=4.5)
    add_fill_sun(energy=0.5)
    import mathutils
    # face: short-wall entrance elevation (this is the grand facade on the
    # reference plate), eye height, standing well back of the 44 m span.
    add_camera("cam_face", (65, 0, 1.6), mathutils.Vector((0, 0, 7)), lens=22)
    render_to(os.path.join(RENDERS_DIR, "market_face.png"))
    # 34: outside both wall planes (X_HALF=42, Y_HALF=22) so it can't clip a
    # pier -- a corner view showing the long-wall arcade + entrance together.
    add_camera("cam_34", (55, -38, 1.6), mathutils.Vector((20, -10, 6)), lens=22)
    render_to(os.path.join(RENDERS_DIR, "market_34.png"))
    # detail: the entrance -- gate post + hinge plates + threshold -- the
    # richest joined/moves-opens/fixed cluster on this asset. Framed tight and
    # low so the (opaque-in-clay) roof/gable glass stays out of frame.
    add_camera("cam_detail", (52, -8, 1.7), mathutils.Vector((40, 0, 1.8)), lens=38)
    render_to(os.path.join(RENDERS_DIR, "market_detail.png"))
    add_camera("cam_ctx", (70, -60, 20), mathutils.Vector((0, 0, 7)), lens=24)
    render_to(os.path.join(RENDERS_DIR, "market_ctx.png"))
    # interior: eye height, standing just inside one entrance looking down the
    # nave -- the only frame that shows the trusses and columns the brief asks
    # for "visible from inside". Extra frame, on top of COMMON's minimum 3.
    add_camera("cam_interior", (X_HALF - 3, 0, 1.6), mathutils.Vector((-X_HALF + 3, 0, 6)), lens=24)
    render_to(os.path.join(RENDERS_DIR, "market_interior.png"))


if __name__ == "__main__":
    obj = build()
    bpy.ops.wm.save_as_mainfile(filepath="C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B1/market.blend")
    if "--quick" in sys.argv:
        import mathutils
        add_ground_plane(size=100.0, material="stone")
        add_camera("c1", (60, -55, 25), mathutils.Vector((0, 0, 6)), lens=28)
        quick_check(os.path.join(RENDERS_DIR, "market_quick.png"), res=800)
        add_camera("c2", (60, 0, 12), mathutils.Vector((0, 0, 7)), lens=28)
        quick_check(os.path.join(RENDERS_DIR, "market_quick_end.png"), res=800)
        add_camera("c3", (0, 0, 4.5), mathutils.Vector((30, 0, 8)), lens=24)
        quick_check(os.path.join(RENDERS_DIR, "market_quick_inside.png"), res=800)
        add_camera("c4", (48, 4, 2.2), mathutils.Vector((41, 5.6, 2.0)), lens=50)
        quick_check(os.path.join(RENDERS_DIR, "market_quick_gate.png"), res=800)
    else:
        render_pass()
        export_glb([obj], os.path.join(MODELS_DIR, "market.glb"))
    print("MARKET DONE")
