"""Asset 1: rookery.glb -- Dorset Street tenement complex.
Origin: footprint centre as given by the brief (NOT recentred). Local:
front block z -10.75..-1.75 (9 deep), rear block z +1.95..+10.75, both
x -19.5..+18.5 (38 long); courtyard gap 3.7 m between; east court wall at
x +18.5..+19.5 closing the gap. Parapet +14.50, 4 storeys (floor-to-floor
3.5). FRONT = -z face (north, onto Dorset Street).
Materials: brick, slate, paint_dark, planks (boarded windows).

Door rhythm: brief specifies "every 5.5 m" across the exact 38 m frontage.
38 / 5.5 = 6.9, which does not divide evenly -- 7 full bays at 5.4286 m
each is used (closest whole-bay fit to the 5.5 m rhythm); recorded here as
an honest, small deviation from the literal figure.
"""
import bpy
import bmesh
import math
import sys

sys.path.insert(0, "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B3")
import common as C

C.clear_scene()

BRICK, SLATE, PAINT_DARK, PLANKS = 0, 1, 2, 3
MATS = ["brick", "slate", "paint_dark", "planks"]

FRONT_X0, FRONT_X1 = -19.5, 18.5
FRONT_LEN = FRONT_X1 - FRONT_X0  # 38.0
N_BAYS = 7
BAY_W = FRONT_LEN / N_BAYS       # 5.4286

FRONT_Z0, FRONT_Z1 = -10.75, -1.75   # front block depth (9 m)
REAR_Z0, REAR_Z1 = 1.95, 10.75       # rear block depth (8.8 m)
COURT_WALL_X0, COURT_WALL_X1 = 18.5, 19.5

FLOOR_H = 3.5
FLOOR_Y = [0.0, 3.5, 7.0, 10.5]
PARAPET_TOP = 14.5
WALL_TOP = 14.0
WALL_THICK = 0.35

bm = bmesh.new()


def bay_x(i):
    xc = FRONT_X0 + BAY_W * (i + 0.5)
    return xc


def wall_panel(face_z, x0, x1, y0, y1, mat=BRICK):
    if x1 <= x0 or y1 <= y0:
        return
    C.add_quad(bm, (x0, y0, face_z), (x1, y0, face_z), (x1, y1, face_z),
               (x0, y1, face_z), mat_idx=mat)


def door_zface(face_z, sign, xc, width=1.1, height=2.2, recess=WALL_THICK):
    # `sign` as passed in is the face's OUTWARD normal sign (-1 for both the
    # front block's street face and the rear block's courtyard face, since
    # both open toward decreasing z). Flipping it here once means every
    # offset below that reads "+sign" is outward/proud (steps, sill, handle)
    # and every "-sign" is inward/recessed (rz, jambs) -- was backwards
    # before this fix, which built doors and windows bulging OUT toward the
    # street instead of recessed into the wall (BRIEF-COMMON: openings sit
    # back in the wall thickness, never coplanar/proud).
    sign = -sign
    rz = face_z + sign * recess
    xl, xr = xc - width / 2, xc + width / 2
    y0, y1 = 0.28, 0.28 + height  # raised threshold
    # jambs
    C.add_quad(bm, (xl, y0, face_z), (xl, y0, rz), (xl, y1, rz), (xl, y1, face_z), mat_idx=BRICK)
    C.add_quad(bm, (xr, y0, rz), (xr, y0, face_z), (xr, y1, face_z), (xr, y1, rz), mat_idx=BRICK)
    # lintel soffit
    C.add_quad(bm, (xl, y1, face_z), (xr, y1, face_z), (xr, y1, rz), (xl, y1, rz), mat_idx=BRICK)
    # door leaf (proud, closed) + frame
    fz = rz - sign * 0.02
    C.add_box(bm, xl + 0.03, xr - 0.03, y0 + 0.02, y1 - 0.02,
              min(fz, fz - sign * 0.05), max(fz, fz - sign * 0.05), mat_idx=PAINT_DARK)
    C.add_cylinder(bm, xr - 0.12, rz - sign * 0.09, y0 + 1.0, y0 + 1.08, 0.02,
                    segments=8, mat_idx=PAINT_DARK)  # door handle/knob
    # worn steps projecting toward the street (outward, -sign direction)
    for k, (sy0, sy1) in enumerate(((0.0, 0.14), (0.14, 0.28))):
        depth = 0.30 - k * 0.10
        sz0 = face_z
        sz1 = face_z - sign * depth
        C.add_box(bm, xl - 0.05, xr + 0.05, sy0, sy1, min(sz0, sz1), max(sz0, sz1),
                  mat_idx=STONE if False else BRICK)


def window_zface(face_z, sign, xc, y_sill, y_lintel, width=1.1, recess=WALL_THICK,
                  boarded=False):
    # see door_zface for why this flip is needed -- same bug, same fix.
    sign = -sign
    xl, xr = xc - width / 2, xc + width / 2
    rz = face_z + sign * recess
    C.add_quad(bm, (xl, y_sill, face_z), (xl, y_sill, rz), (xl, y_lintel, rz),
               (xl, y_lintel, face_z), mat_idx=BRICK)
    C.add_quad(bm, (xr, y_sill, rz), (xr, y_sill, face_z), (xr, y_lintel, face_z),
               (xr, y_lintel, rz), mat_idx=BRICK)
    C.add_quad(bm, (xl, y_lintel, face_z), (xr, y_lintel, face_z), (xr, y_lintel, rz),
               (xl, y_lintel, rz), mat_idx=BRICK)
    C.add_box(bm, xl - 0.05, xr + 0.05, y_sill - 0.05, y_sill,
              min(face_z, face_z - sign * 0.08), max(face_z, face_z - sign * 0.08),
              mat_idx=BRICK)  # proud sill
    if boarded:
        bz = rz - sign * 0.01
        C.add_box(bm, xl + 0.02, xr - 0.02, y_sill + 0.03, y_lintel - 0.03,
                  min(bz, bz - sign * 0.03), max(bz, bz - sign * 0.03), mat_idx=PLANKS)
    else:
        C.add_quad(bm, (xl, y_sill, rz), (xr, y_sill, rz), (xr, y_lintel, rz),
                   (xl, y_lintel, rz), mat_idx=PAINT_DARK)  # dark glazing recess
        # simple sash glazing bars
        xm = xc
        ym = (y_sill + y_lintel) / 2
        bar_z = rz - sign * 0.015
        C.add_box(bm, xm - 0.015, xm + 0.015, y_sill, y_lintel,
                  min(bar_z, bar_z - sign * 0.01), max(bar_z, bar_z - sign * 0.01), mat_idx=PAINT_DARK)
        C.add_box(bm, xl, xr, ym - 0.015, ym + 0.015,
                  min(bar_z, bar_z - sign * 0.01), max(bar_z, bar_z - sign * 0.01), mat_idx=PAINT_DARK)


def string_course(face_z, x0, x1, y):
    C.add_box(bm, x0, x1, y - 0.06, y + 0.10, min(face_z, face_z - 0.06),
              max(face_z, face_z - 0.06), mat_idx=STONE if False else BRICK)


def build_facade(face_z, sign, x0, x1, has_doors, window_width, boarded_bays,
                  plainer=False):
    """One elevation of a block: ground floor doors (optional) + repeat
    windows above, string courses between floors, blank return panels."""
    n = N_BAYS if not plainer else 5
    bw = (x1 - x0) / n
    for i in range(n):
        xc = x0 + bw * (i + 0.5)
        xl, xr = xc - bw / 2, xc + bw / 2
        for fi, fy in enumerate(FLOOR_Y):
            y0, y1 = fy, fy + FLOOR_H
            if fi == 0 and has_doors:
                wall_panel(face_z, xl, xc - 0.65, y0, y1)
                wall_panel(face_z, xc + 0.65, xr, y0, y1)
                wall_panel(face_z, xc - 0.65, xc + 0.65, 2.5, y1)
                door_zface(face_z, sign, xc)
            else:
                ys = y0 + FLOOR_H * 0.30
                yl = y0 + FLOOR_H * 0.78
                wall_panel(face_z, xl, xc - window_width / 2, y0, y1)
                wall_panel(face_z, xc + window_width / 2, xr, y0, y1)
                wall_panel(face_z, xc - window_width / 2, xc + window_width / 2, y0, ys)
                wall_panel(face_z, xc - window_width / 2, xc + window_width / 2, yl, y1)
                window_zface(face_z, sign, xc, ys, yl, width=window_width,
                             boarded=(i, fi) in boarded_bays)
    for fy in FLOOR_Y[1:]:
        string_course(face_z, x0, x1, fy)


def roof_and_parapet(x0, x1, z0, z1, ridge_rise, n_chimneys, coping_gaps=()):
    """Parapet with coping (with intentional gaps), then a pitched slate
    roof set back behind it with a ridge and chimney stacks + pots."""
    C.add_box(bm, x0, x1, WALL_TOP, PARAPET_TOP, z0, z1, mat_idx=BRICK)
    n = N_BAYS
    bw = (x1 - x0) / n
    for i in range(n):
        if i in coping_gaps:
            continue
        xl = x0 + bw * i
        xr = x0 + bw * (i + 1)
        C.add_box(bm, xl - 0.03, xr + 0.03, PARAPET_TOP - 0.06, PARAPET_TOP,
                  z0 - 0.05, z1 + 0.05, mat_idx=BRICK)
    zc = (z0 + z1) / 2
    hz = (z1 - z0) / 2
    ridge_y = PARAPET_TOP + ridge_rise
    v_ridge_a = bm.verts.new(C.V(x0, ridge_y, zc))
    v_ridge_b = bm.verts.new(C.V(x1, ridge_y, zc))
    v_eave_z0_a = bm.verts.new(C.V(x0, PARAPET_TOP + 0.05, z0))
    v_eave_z0_b = bm.verts.new(C.V(x1, PARAPET_TOP + 0.05, z0))
    v_eave_z1_a = bm.verts.new(C.V(x0, PARAPET_TOP + 0.05, z1))
    v_eave_z1_b = bm.verts.new(C.V(x1, PARAPET_TOP + 0.05, z1))
    f1 = bm.faces.new((v_eave_z0_a, v_eave_z0_b, v_ridge_b, v_ridge_a))
    f1.material_index = SLATE
    f2 = bm.faces.new((v_ridge_a, v_ridge_b, v_eave_z1_b, v_eave_z1_a))
    f2.material_index = SLATE
    # ridge cap
    C.add_box(bm, x0, x1, ridge_y - 0.05, ridge_y + 0.08, zc - 0.12, zc + 0.12, mat_idx=SLATE)
    # chimney stacks with pots along the ridge
    for k in range(n_chimneys):
        cx = x0 + (x1 - x0) * (k + 0.5) / n_chimneys
        cy0, cy1 = ridge_y - 0.3, ridge_y + 1.1
        C.add_box(bm, cx - 0.4, cx + 0.4, cy0, cy1, zc - 0.35, zc + 0.35, mat_idx=BRICK)
        C.add_box(bm, cx - 0.48, cx + 0.48, cy1 - 0.1, cy1, zc - 0.43, zc + 0.43, mat_idx=STONE if False else BRICK)  # flaunching/cap
        for px, pz in ((-0.18, -0.12), (0.18, -0.12), (-0.18, 0.12), (0.18, 0.12)):
            C.add_cylinder(bm, cx + px, zc + pz, cy1, cy1 + 0.28, 0.09, segments=10, mat_idx=BRICK)


# =====================================================================
# FRONT BLOCK
# =====================================================================
boarded_front = {(1, 3), (5, 2), (3, 1)}
build_facade(FRONT_Z0, -1, FRONT_X0, FRONT_X1, has_doors=True, window_width=1.05,
             boarded_bays=boarded_front)
# blank return + side walls
wall_panel(FRONT_Z1, FRONT_X0, FRONT_X1, 0, WALL_TOP, mat=BRICK)  # onto courtyard side (plain)
for xw in (FRONT_X0, FRONT_X1):
    C.add_quad(bm, (xw, 0, FRONT_Z0), (xw, 0, FRONT_Z1), (xw, WALL_TOP, FRONT_Z1),
               (xw, WALL_TOP, FRONT_Z0), mat_idx=BRICK)
C.add_box(bm, FRONT_X0 - 0.1, FRONT_X1 + 0.1, 0.0, 0.25, FRONT_Z0 - 0.1, FRONT_Z1 + 0.1,
          mat_idx=BRICK)  # plinth
roof_and_parapet(FRONT_X0, FRONT_X1, FRONT_Z0, FRONT_Z1, ridge_rise=3.3, n_chimneys=4,
                  coping_gaps={2, 5})

# =====================================================================
# REAR BLOCK -- plainer, smaller windows, fewer bays, onto courtyard
# =====================================================================
# sign=-1 here too: the rear block's courtyard-facing wall also opens
# toward decreasing z (courtyard sits between the two blocks, at LOWER z
# than REAR_Z0), the same outward direction as the front block's street
# face. This was wrongly +1 -- harmless before the sign-flip fix inside
# door_zface/window_zface (the two bugs cancelled out), but wrong once that
# fix is in place, so it has to change together with it.
build_facade(REAR_Z0, -1, FRONT_X0, FRONT_X1, has_doors=False, window_width=0.8,
             boarded_bays=set(), plainer=True)
wall_panel(REAR_Z1, FRONT_X0, FRONT_X1, 0, WALL_TOP, mat=BRICK)
for xw in (FRONT_X0, FRONT_X1):
    C.add_quad(bm, (xw, 0, REAR_Z0), (xw, 0, REAR_Z1), (xw, WALL_TOP, REAR_Z1),
               (xw, WALL_TOP, REAR_Z0), mat_idx=BRICK)
C.add_box(bm, FRONT_X0 - 0.1, FRONT_X1 + 0.1, 0.0, 0.25, REAR_Z0 - 0.1, REAR_Z1 + 0.1,
          mat_idx=BRICK)
roof_and_parapet(FRONT_X0, FRONT_X1, REAR_Z0, REAR_Z1, ridge_rise=2.4, n_chimneys=2)

# =====================================================================
# EAST COURT WALL closing the gap
# =====================================================================
CW_TOP = 4.0
C.add_box(bm, COURT_WALL_X0, COURT_WALL_X1, 0.0, CW_TOP, FRONT_Z1, REAR_Z0, mat_idx=BRICK)
C.add_box(bm, COURT_WALL_X0 - 0.05, COURT_WALL_X1 + 0.05, CW_TOP, CW_TOP + 0.12,
          FRONT_Z1 - 0.05, REAR_Z0 + 0.05, mat_idx=BRICK)  # coping

# ---- courtyard privy lean-to against the court wall ----
PRIVY_X0, PRIVY_X1 = COURT_WALL_X0 - 1.6, COURT_WALL_X0 - 0.1
PRIVY_Z0, PRIVY_Z1 = FRONT_Z1 + 0.2, FRONT_Z1 + 1.6
PRIVY_Y_LOW, PRIVY_Y_HIGH = 0.0, 2.3
C.add_box(bm, PRIVY_X0, PRIVY_X1, PRIVY_Y_LOW, 1.9, PRIVY_Z0, PRIVY_Z1, mat_idx=PLANKS)
# lean-to roof: single pitched slope from wall (high) to front (low), post at front
v0 = bm.verts.new(C.V(PRIVY_X0, 1.9, PRIVY_Z0))
v1 = bm.verts.new(C.V(PRIVY_X1, PRIVY_Y_HIGH, PRIVY_Z0))
v2 = bm.verts.new(C.V(PRIVY_X1, PRIVY_Y_HIGH, PRIVY_Z1))
v3 = bm.verts.new(C.V(PRIVY_X0, 1.9, PRIVY_Z1))
f = bm.faces.new((v0, v1, v2, v3))
f.material_index = SLATE
C.add_cylinder(bm, PRIVY_X0 + 0.06, PRIVY_Z0 + 0.06, 0, 1.9, 0.05, segments=8, mat_idx=PLANKS)
C.add_cylinder(bm, PRIVY_X0 + 0.06, PRIVY_Z1 - 0.06, 0, 1.9, 0.05, segments=8, mat_idx=PLANKS)
# door in privy front (facing -x, toward courtyard open side)
C.add_box(bm, PRIVY_X0 - 0.03, PRIVY_X0 + 0.02, 0.05, 1.75,
          PRIVY_Z0 + 0.2, PRIVY_Z1 - 0.2, mat_idx=PAINT_DARK)

# ---- standpipe against the court wall ----
SP_X, SP_Z = COURT_WALL_X0 - 0.05, FRONT_Z1 + 2.4
C.add_cylinder(bm, SP_X, SP_Z, 0.0, 1.1, 0.045, segments=10, mat_idx=PAINT_DARK)
C.add_box(bm, SP_X - 0.06, SP_X + 0.02, 1.02, 1.10, SP_Z - 0.05, SP_Z + 0.20, mat_idx=PAINT_DARK)  # spout
C.add_cylinder(bm, SP_X - 0.02, SP_Z, 1.12, 1.18, 0.035, segments=8, mat_idx=PAINT_DARK)  # tap handle
C.add_box(bm, SP_X - 0.10, SP_X + 0.10, 0.0, 0.08, SP_Z - 0.10, SP_Z + 0.10, mat_idx=BRICK)  # base pad
# wall bracket fixing the standpipe
C.add_box(bm, COURT_WALL_X0 - 0.08, SP_X + 0.02, 0.55, 0.62, SP_Z - 0.03, SP_Z + 0.03,
          mat_idx=PAINT_DARK)

obj = C.new_object("rookery", bm, MATS)
C.add_bevel(obj, width=0.015, segments=2)
C.smart_uv(obj)

bpy.context.view_layer.objects.active = obj
obj.select_set(True)

C.export_glb([obj], C.MODELS_DIR + "/rookery.glb")

# ---- render rig ----
C.add_sun(elevation_deg=42, azimuth_deg=125, energy=3.2)
C.add_fill_light(loc=(-10, 8, 12), energy=350)

eye = 1.6
door0_xc = bay_x(0)
door1_xc = bay_x(1)
# face/34 were framed only 4.75 m from a ~18 m tall facade at lens=32 -- the
# vertical FOV at that distance is under 3 m, so the frame filled entirely
# with one window and nothing else (no door, no ground, no roofline) with
# no way to tell what it was. Pulled back to show a door plus the windows
# above it together, which is what a stranger needs to read "tenement".
cam_face = C.add_camera("cam_face", C.V(door0_xc, eye, FRONT_Z0 - 9.0), C.V(door0_xc, 3.8, FRONT_Z0),
                         lens=24)
cam_34 = C.add_camera("cam_34", C.V(door1_xc + 7.0, eye, FRONT_Z0 - 10.0),
                       C.V(door0_xc, 4.5, FRONT_Z0), lens=24)
# detail: the ground-floor door + its worn steps, close enough to read the
# reveal/frame/handle/step nosing as real geometry, not the whole facade.
cam_detail = C.add_camera("cam_detail", C.V(door0_xc + 0.9, 1.35, FRONT_Z0 - 2.6),
                           C.V(door0_xc, 1.2, FRONT_Z0), lens=38)
cam_ctx = C.add_camera("cam_ctx", C.V(35, 22, -28), C.V(0, 6, 2), lens=22)

C.setup_render('CYCLES', samples=32, res=(960, 540), device='CPU')

backup = C.apply_clay_override([obj])
for cam, name in ((cam_face, "face"), (cam_34, "34"), (cam_detail, "detail"),
                   (cam_ctx, "ctx")):
    bpy.context.scene.camera = cam
    C.render_to(C.RENDER_DIR + f"/rookery_{name}.png")
C.restore_materials([obj], backup)

bpy.ops.wm.save_as_mainfile(
    filepath="C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B3/rookery.blend")
print("DONE rookery build+export+render")
