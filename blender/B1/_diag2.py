import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (new_mesh_object, add_bevel, apply_all_transforms, clear_scene)
import bmesh
import build_stall as bs

def count(obj):
    deps = bpy.context.evaluated_depsgraph_get()
    eobj = obj.evaluated_get(deps)
    mesh = eobj.to_mesh()
    mesh.calc_loop_triangles()
    n = len(mesh.loop_triangles)
    eobj.to_mesh_clear()
    return n

# Build without the new canopy additions: monkeypatch build_canopy to a stub that
# only builds the old baseline (poles+sockets+ties+plain single-span sheet), skipping
# ridge rope/hem/tie-loops, to isolate their cost.
def build_canopy_old(bm):
    pole_h = 2.1
    pole_x = bs.LEN / 2.0 + 0.08
    attach_z = pole_h - 0.10
    for sx in (-1, 1):
        x = sx * pole_x
        bs.add_cyl(bm, (x, 0, pole_h / 2), 0.03, 0.03, pole_h, bs.PLANKS, segments=8)
        bs.add_cyl(bm, (x, 0, bs.COUNTER_H + 0.03), 0.055, 0.055, 0.09, bs.IRON, segments=10)
        bs.add_box(bm, (x, 0.10, bs.COUNTER_H - 0.01), (0.12, 0.03, 0.16), bs.IRON)
        for bz in (bs.COUNTER_H - 0.06, bs.COUNTER_H + 0.06):
            bs.add_cyl(bm, (x, 0.10, bz), 0.018, 0.018, 0.10, bs.IRON, segments=8, axis='y')
        az = math.atan2(-0.42, 0.45)
        bs.add_rope_wrap(bm, x, attach_z, bs.PLASTER, bs.IRON, seed=1 if sx < 0 else 2, cam_azimuth=az)
    n_steps = 16
    dip = 0.10
    thickness = 0.018
    y_half = 0.55
    top_v, bot_v = [], []
    for i in range(n_steps + 1):
        t = i / n_steps
        x = -pole_x + (2 * pole_x) * t
        sag = dip * math.sin(math.pi * t)
        zt = attach_z - sag
        zb = zt - thickness
        top_v.append((bm.verts.new((x, -y_half, zt)), bm.verts.new((x, y_half, zt))))
        bot_v.append((bm.verts.new((x, -y_half, zb)), bm.verts.new((x, y_half, zb))))
    for i in range(n_steps):
        tl0, tr0 = top_v[i]; tl1, tr1 = top_v[i + 1]
        bl0, br0 = bot_v[i]; bl1, br1 = bot_v[i + 1]
        bm.faces.new((tl0, tr0, tr1, tl1)).material_index = bs.PLASTER
        bm.faces.new((bl1, br1, br0, bl0)).material_index = bs.PLASTER
        bm.faces.new((tl0, tl1, bl1, bl0)).material_index = bs.PLASTER
        bm.faces.new((br0, br1, tr1, tr0)).material_index = bs.PLASTER
    bm.faces.new((top_v[0][0], top_v[0][1], bot_v[0][1], bot_v[0][0])).material_index = bs.PLASTER
    bm.faces.new((bot_v[-1][0], bot_v[-1][1], top_v[-1][1], top_v[-1][0])).material_index = bs.PLASTER

bs.build_canopy = build_canopy_old
obj = bs.build()
print("NO_NEW_ADDITIONS", count(obj))
