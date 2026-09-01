import bpy, sys
name = sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=f"C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B3/{name}.blend")
depsgraph = bpy.context.evaluated_depsgraph_get()
total = 0
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    eo = obj.evaluated_get(depsgraph)
    me = eo.to_mesh()
    me.calc_loop_triangles()
    total += len(me.loop_triangles)
    eo.to_mesh_clear()
print(f"TRIS {name}: {total}")
