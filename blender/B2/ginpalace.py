"""Asset 2: ginpalace.glb -- 1880s gin palace (3-storey pub + rooms over).
Origin: footprint centre (world (76.5,188)) -> local x -7.5..+7.5 (depth,
east-west), z -10..+10 (frontage, north-south). FRONT = -x face (west, onto
Commercial Street). Parapet +11.00, floor-to-floor 3.5.
Materials: brick (0), paint_green (1), glass (2), slate (3), iron (4).
"""
import bpy
import bmesh
import math
import sys

sys.path.insert(0, "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2")
import common as C

C.clear_scene()

MAT_BRICK, MAT_GREEN, MAT_GLASS, MAT_SLATE, MAT_IRON = 0, 1, 2, 3, 4
MATS = ["brick", "paint_green", "glass", "slate", "iron"]

bm = bmesh.new()

# ---------------------------------------------------------------- geometry
X0, X1 = -7.5, 7.5      # depth (east-west)
Z0, Z1 = -10.0, 10.0    # frontage (north-south)
WALL_T = 0.35
F2F = 3.5
GROUND_TOP = F2F           # 3.5
FIRST_TOP = 2 * F2F        # 7.0
SECOND_TOP = 3 * F2F       # 10.5
PARAPET_TOP = 11.0

STALLRISER_Y = 0.85
FASCIA_Y0 = 3.1
FASCIA_Y1 = GROUND_TOP  # 3.5

# ---- plinth / pavement kick at the base of the side + rear walls ---------
C.add_box(bm, X0 - 0.05, X0, 0.0, 0.3, Z0, Z1, mat_idx=MAT_BRICK)
C.add_box(bm, X1, X1 + 0.05, 0.0, 0.3, Z0, Z1, mat_idx=MAT_BRICK)
C.add_box(bm, X0, X1, 0.0, 0.3, Z1, Z1 + 0.05, mat_idx=MAT_BRICK)

# ---- rear wall (east, x=X1, blank brick service elevation) ---------------
C.add_box(bm, X1 - WALL_T, X1, 0.0, SECOND_TOP, Z0, Z1, mat_idx=MAT_BRICK)

# ---- side walls (north z=Z0, south z=Z1): brick, 2 sash windows/floor -----
SIDE_SILL = [4.5, 8.0]
SIDE_HEAD = [6.1, 9.6]
side_centers = [-3.75, 3.75]
SIDE_W = 1.3
side_bays = [(c - SIDE_W / 2, c + SIDE_W / 2) for c in side_centers]
side_piers = [X0] + [e for pair in side_bays for e in pair] + [X1]
side_pier_ranges = [(side_piers[i], side_piers[i + 1]) for i in range(0, len(side_piers) - 1, 2)]

for z_face in (Z0, Z1):
    C.add_box(bm, X0, X1, 0.0, SECOND_TOP, z_face, z_face - WALL_T if z_face > 0 else z_face + WALL_T,
              mat_idx=MAT_BRICK)
    for floor in (0, 1):
        sill, head = SIDE_SILL[floor], SIDE_HEAD[floor]
        floor_y0 = GROUND_TOP if floor == 0 else FIRST_TOP
        for (bx0, bx1) in side_bays:
            C.add_rect_window(bm, bx0, bx1, z_face, WALL_T, floor_y0, SECOND_TOP, sill, head,
                               MAT_BRICK, MAT_GLASS, sill_mat=MAT_BRICK, bar_cols=1, bar_rows=2,
                               bar_mat=MAT_GREEN, meeting_rail_y=(sill + head) / 2)

# ---- west front wall: brick upper 2 floors, ground floor rebuilt below ---
C.add_box(bm, X0, X0 + WALL_T, GROUND_TOP, SECOND_TOP, Z0, Z1, mat_idx=MAT_BRICK)
FRONT_SILL = [4.5, 8.0]
FRONT_HEAD = [6.1, 9.6]
front_centers = [-7.5, -2.5, 2.5, 7.5]
FRONT_W = 1.3
front_bays = [(c - FRONT_W / 2, c + FRONT_W / 2) for c in front_centers]
for floor in (0, 1):
    sill, head = FRONT_SILL[floor], FRONT_HEAD[floor]
    for (bz0, bz1) in front_bays:
        C.add_rect_window_xface(bm, bz0, bz1, X0, WALL_T, GROUND_TOP, SECOND_TOP, sill, head,
                                 MAT_BRICK, MAT_GLASS, sill_mat=MAT_BRICK, bar_cols=1, bar_rows=2,
                                 bar_mat=MAT_GREEN, meeting_rail_y=(sill + head) / 2)

# ---- ground floor west shopfront: piers (green joinery) + 3 glazed bays +
#      corner entrance door w/ fanlight, all real through-thickness joinery -
DOOR_Z0, DOOR_Z1 = -9.6, -8.3
shop_edges = [Z0, -9.6, -8.3, -7.9, -2.9, -2.5, 2.5, 2.9, 7.9, 8.3, Z1]
# pier ranges (joinery mullions + end returns), skipping the door + 3 glazed bays
pier_ranges_shop = [(Z0, -9.6), (-8.3, -7.9), (-2.9, -2.5), (2.5, 2.9), (7.9, 8.3), (8.3, Z1)]
glazed_bays = [(-7.9, -2.9), (-2.5, 2.5), (2.9, 7.9)]

for (z0, z1) in pier_ranges_shop:
    C.add_box(bm, X0, X0 + WALL_T, 0.0, GROUND_TOP, z0, z1, mat_idx=MAT_GREEN)
for (bz0, bz1) in glazed_bays:
    C.add_rect_window_xface(bm, bz0, bz1, X0, WALL_T, 0.0, GROUND_TOP, STALLRISER_Y, FASCIA_Y0,
                             MAT_GREEN, MAT_GLASS, sill_mat=MAT_GREEN, bar_cols=3, bar_rows=2,
                             bar_mat=MAT_GREEN, glass_x_frac=0.55)

# corner entrance door (leaf, paint_green) + transom fanlight (glazed) above
DOOR_HEAD = 2.15
FANLIGHT_HEAD = 2.9
C.add_rect_window_xface(bm, DOOR_Z0, DOOR_Z1, X0, WALL_T, 0.0, GROUND_TOP, 0.02, DOOR_HEAD,
                         MAT_GREEN, MAT_GREEN, sill_mat=MAT_GREEN, bar_cols=1, bar_rows=1,
                         bar_mat=MAT_GREEN, glass_x_frac=0.55)
C.add_rect_window_xface(bm, DOOR_Z0, DOOR_Z1, X0, WALL_T, 0.0, GROUND_TOP, DOOR_HEAD, FANLIGHT_HEAD,
                         MAT_GREEN, MAT_GLASS, sill_mat=MAT_GREEN, bar_cols=4, bar_rows=1,
                         bar_mat=MAT_GREEN, glass_x_frac=0.5)
# door handle, proud of the recessed leaf
door_zc = (DOOR_Z0 + DOOR_Z1) / 2.0
x_leaf = X0 - WALL_T * 0.55
C.add_box(bm, x_leaf - 0.05, x_leaf - 0.02, 0.9, 1.05, door_zc + 0.25, door_zc + 0.32, mat_idx=MAT_IRON)

# fascia signboard cornice (projects above the shopfront fascia band)
C.add_box(bm, X0 - 0.08, X0 + WALL_T, GROUND_TOP, GROUND_TOP + 0.18, Z0 - 0.08, Z1 + 0.08, mat_idx=MAT_GREEN)

# gas lamp bracket + lantern box, cantilevered over the door
BRK_Y = 2.7
C.add_cylinder(bm, 0, 0, 0, 1, 0.03, segments=6, mat_idx=MAT_IRON) if False else None
bx0, bx1 = X0, X0 - 0.55
C.add_box(bm, bx1, bx0, BRK_Y - 0.03, BRK_Y + 0.03, door_zc - 0.03, door_zc + 0.03, mat_idx=MAT_IRON)
C.add_box(bm, bx1 - 0.02, bx1 + 0.15, BRK_Y - 0.35, BRK_Y + 0.02, door_zc - 0.03, door_zc + 0.03, mat_idx=MAT_IRON)
lx0, lx1 = bx1 - 0.22, bx1 + 0.05
C.add_box(bm, lx0, lx1, BRK_Y - 0.35, BRK_Y - 0.05, door_zc - 0.16, door_zc + 0.16, mat_idx=MAT_GLASS)
C.add_box(bm, lx0 - 0.02, lx1 + 0.02, BRK_Y - 0.05, BRK_Y + 0.02, door_zc - 0.18, door_zc + 0.18, mat_idx=MAT_IRON)

# ---- string course between ground and first floor, and parapet cornice ---
C.add_box(bm, X0 - 0.06, X1 + 0.06, GROUND_TOP + 0.18, GROUND_TOP + 0.3, Z0 - 0.06, Z1 + 0.06, mat_idx=MAT_BRICK)
C.add_box(bm, X0 - 0.08, X1 + 0.08, SECOND_TOP, PARAPET_TOP, Z0 - 0.08, Z1 + 0.08, mat_idx=MAT_BRICK)

# ---- roof: low mono-pitch slate slope behind the parapet ------------------
C.add_quad(bm, (X0 + 0.3, PARAPET_TOP - 0.1, Z0 + 0.2), (X1 - 0.1, PARAPET_TOP + 0.6, Z0 + 0.2),
           (X1 - 0.1, PARAPET_TOP + 0.6, Z1 - 0.2), (X0 + 0.3, PARAPET_TOP - 0.1, Z1 - 0.2),
           mat_idx=MAT_SLATE)

# ---- 2 chimney stacks with 3 pots each, behind the parapet toward the rear
for cz in (-4.0, 4.0):
    cx = X1 - 1.6
    C.add_box(bm, cx - 0.5, cx + 0.5, PARAPET_TOP, PARAPET_TOP + 1.3, cz - 0.4, cz + 0.4, mat_idx=MAT_BRICK)
    C.add_box(bm, cx - 0.6, cx + 0.6, PARAPET_TOP + 1.3, PARAPET_TOP + 1.5, cz - 0.5, cz + 0.5, mat_idx=MAT_BRICK)
    for pz in (cz - 0.25, cz, cz + 0.25):
        C.add_cylinder(bm, cx, pz, PARAPET_TOP + 1.5, PARAPET_TOP + 2.0, 0.12, segments=10, mat_idx=MAT_BRICK)

# ---------------------------------------------------------------- finalize
obj = C.new_object("ginpalace", bm, MATS)
C.add_bevel(obj, width=0.015, segments=2)
C.smart_uv(obj)
C.bbox_and_tris([obj])
C.export_glb([obj], C.MODELS_DIR + "/ginpalace.glb")
print("[ginpalace] pass 2 export complete")
