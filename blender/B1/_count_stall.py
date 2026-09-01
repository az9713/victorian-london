import bpy
bpy.ops.wm.open_mainfile(filepath="stall.blend")
obj = bpy.data.objects["stall"]
deps = bpy.context.evaluated_depsgraph_get()
eobj = obj.evaluated_get(deps)
mesh = eobj.to_mesh()
mesh.calc_loop_triangles()
print("STALL_TRI_COUNT", len(mesh.loop_triangles))
eobj.to_mesh_clear()
