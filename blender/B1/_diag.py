import bpy, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_stall as bs

def count(obj):
    deps = bpy.context.evaluated_depsgraph_get()
    eobj = obj.evaluated_get(deps)
    mesh = eobj.to_mesh()
    mesh.calc_loop_triangles()
    n = len(mesh.loop_triangles)
    eobj.to_mesh_clear()
    return n

# baseline: comment out ridge rope / hem / tie loop calls via monkeypatch
import bmesh, math
orig_build_canopy = bs.build_canopy

obj = bs.build()
print("FULL", count(obj))
