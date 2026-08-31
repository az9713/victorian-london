import bpy, json, struct, base64

bpy.ops.wm.read_factory_settings(use_empty=True)
mesh = bpy.data.meshes.new("probe")
mesh.from_pydata([(0,0,0)], [], [])
obj = bpy.data.objects.new("probe", mesh)
obj.location = (1.0, 5.0, 0.0)  # Blender X=1, Y=5, Z=0
bpy.context.scene.collection.objects.link(obj)

out = r"C:\Users\USERNAME\Downloads\projects\victorian-london\blender\B2\axis_test.glb"
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB')

with open(out, 'rb') as f:
    data = f.read()
# parse glb header
assert data[:4] == b'glTF'
json_len = struct.unpack('<I', data[12:16])[0]
json_chunk = data[20:20+json_len].decode('utf-8')
gltf = json.loads(json_chunk)
print("NODE TRANSLATIONS:", [n.get('translation') for n in gltf['nodes']])
