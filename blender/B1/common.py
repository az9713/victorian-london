"""Shared helpers for batch B1 (Spitalfields market + props).
Import with bpy.data preferred over bpy.ops per BRIEF-COMMON. Run headless:
"C:\\Users\\USERNAME\\tools\\blender-4.4.2-windows-x64\\blender.exe" -b -t 4 -P <script>.py
"""
import bpy
import bmesh
import math
import os
import mathutils
from mathutils import Vector

MODELS_DIR = "C:/Users/USERNAME/Downloads/projects/victorian-london/sandbox/assets/models"
RENDERS_DIR = "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/renders/B1"
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RENDERS_DIR, exist_ok=True)

# ---- shared PBR material NAMES (binding — no other names, no image textures) ----
MAT_COLORS = {
    "brick": (0.28, 0.16, 0.10, 1.0),        # sooted London stock brick, dark
    "slate": (0.16, 0.18, 0.21, 1.0),
    "cobble": (0.35, 0.35, 0.36, 1.0),
    "planks": (0.30, 0.20, 0.12, 1.0),
    "plaster": (0.75, 0.72, 0.65, 1.0),
    "iron": (0.06, 0.06, 0.07, 1.0),
    "glass": (0.55, 0.65, 0.68, 0.35),
    "paint_dark": (0.05, 0.15, 0.10, 1.0),   # dark green painted timber
    "paint_green": (0.08, 0.22, 0.14, 1.0),
    "stone": (0.72, 0.69, 0.60, 1.0),
    "cloth": (0.55, 0.47, 0.30, 1.0),        # jute sacking, used as neutral cloth override
}

_mat_cache = {}


def get_shared_material(name):
    """Return (create once) the shared material with the exact binding name."""
    if name in _mat_cache:
        return _mat_cache[name]
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        color = MAT_COLORS.get(name, (0.6, 0.6, 0.6, 1.0))
        if bsdf:
            bsdf.inputs["Base Color"].default_value = color
            bsdf.inputs["Roughness"].default_value = 0.75 if name != "glass" else 0.05
            if "Metallic" in bsdf.inputs:
                bsdf.inputs["Metallic"].default_value = 1.0 if name == "iron" else 0.0
            if name == "glass" and "Transmission Weight" in bsdf.inputs:
                bsdf.inputs["Transmission Weight"].default_value = 0.9
                mat.blend_method = 'BLEND'
        mat.diffuse_color = color
    _mat_cache[name] = mat
    return mat


CLAY_COLOR = (0.62, 0.62, 0.62, 1.0)


def get_clay_material():
    mat = bpy.data.materials.get("__clay_override")
    if mat is None:
        mat = bpy.data.materials.new("__clay_override")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = CLAY_COLOR
            bsdf.inputs["Roughness"].default_value = 0.85
    return mat


def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for block_coll in (bpy.data.meshes, bpy.data.curves):
        for block in list(block_coll):
            if block.users == 0:
                block_coll.remove(block)


def new_mesh_object(name, bm, material_names=None):
    """Build a mesh object from a bmesh, assign material slots by name list
    (bmesh face.material_index selects into this list), free the bmesh."""
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.calc_normals_split() if hasattr(mesh, "calc_normals_split") else None
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if material_names:
        for mn in material_names:
            mesh.materials.append(get_shared_material(mn))
    return obj


def add_box(bm, center, size, mat_index):
    """Axis-aligned box centred at `center` with full (x,y,z) `size`."""
    before = set(bm.faces)
    ret = bmesh.ops.create_cube(bm, size=1.0)
    verts = ret['verts']
    bmesh.ops.scale(bm, vec=size, verts=verts)
    bmesh.ops.translate(bm, vec=center, verts=verts)
    for f in bm.faces:
        if f not in before:
            f.material_index = mat_index


def add_sphere(bm, center, radius, mat_index, subdivisions=1):
    before = set(bm.faces)
    ret = bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=radius)
    verts = ret['verts']
    bmesh.ops.translate(bm, vec=center, verts=verts)
    for f in bm.faces:
        if f not in before:
            f.material_index = mat_index


def add_cyl(bm, center, radius1, radius2, height, mat_index, segments=10, axis='z'):
    """Cylinder/cone, axis-aligned, centred at `center`. axis picks which world
    axis the height runs along ('z' for uprights, 'x'/'y' for lying down)."""
    before = set(bm.faces)
    ret = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                                 radius1=radius1, radius2=radius2, depth=height)
    verts = ret['verts']
    if axis == 'x':
        bmesh.ops.rotate(bm, cent=(0, 0, 0), verts=verts,
                          matrix=mathutils.Matrix.Rotation(math.radians(90), 3, 'Y'))
    elif axis == 'y':
        bmesh.ops.rotate(bm, cent=(0, 0, 0), verts=verts,
                          matrix=mathutils.Matrix.Rotation(math.radians(90), 3, 'X'))
    bmesh.ops.translate(bm, vec=center, verts=verts)
    for f in bm.faces:
        if f not in before:
            f.material_index = mat_index


def add_beam(bm, p0, p1, w, h, mat_index):
    """Rectangular box (w x h cross-section) running between two 3D points.
    Used for trusses, glazing bars, downpipes, ties, gutters, gate rails."""
    p0 = mathutils.Vector(p0)
    p1 = mathutils.Vector(p1)
    d = p1 - p0
    length = d.length
    if length < 1e-6:
        return
    zaxis = d.normalized()
    up = mathutils.Vector((0, 0, 1))
    if abs(zaxis.dot(up)) > 0.99:
        up = mathutils.Vector((1, 0, 0))
    xaxis = zaxis.cross(up).normalized()
    yaxis = xaxis.cross(zaxis).normalized()
    hw, hh = w / 2.0, h / 2.0
    corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
    v0 = [bm.verts.new(p0 + xaxis * cx + yaxis * cy) for cx, cy in corners]
    v1 = [bm.verts.new(p1 + xaxis * cx + yaxis * cy) for cx, cy in corners]
    faces = []
    n = 4
    for i in range(n):
        j = (i + 1) % n
        faces.append(bm.faces.new((v0[i], v0[j], v1[j], v1[i])))
    faces.append(bm.faces.new(v0[::-1]))
    faces.append(bm.faces.new(v1))
    for f in faces:
        f.material_index = mat_index
    return faces


def add_prism_xz(bm, points, y0, y1, mat_index):
    """Extrude a closed (x,z) polygon along Y from y0 to y1. Wall runs along X,
    thickness along Y — use for long-wall arches/piers (profile in the X-Z plane)."""
    n = len(points)
    v0 = [bm.verts.new((px, y0, pz)) for px, pz in points]
    v1 = [bm.verts.new((px, y1, pz)) for px, pz in points]
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append(bm.faces.new((v0[i], v0[j], v1[j], v1[i])))
    faces.append(bm.faces.new(v0[::-1]))
    faces.append(bm.faces.new(v1))
    for f in faces:
        f.material_index = mat_index
    return faces


def add_prism_yz(bm, points, x0, x1, mat_index):
    """Extrude a closed (y,z) polygon along X from x0 to x1. Wall runs along Y,
    thickness along X — use for short (end)-wall arches/piers and roof gables."""
    n = len(points)
    v0 = [bm.verts.new((x0, py, pz)) for py, pz in points]
    v1 = [bm.verts.new((x1, py, pz)) for py, pz in points]
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append(bm.faces.new((v0[i], v0[j], v1[j], v1[i])))
    faces.append(bm.faces.new(v0[::-1]))
    faces.append(bm.faces.new(v1))
    for f in faces:
        f.material_index = mat_index
    return faces


def add_bevel(obj, width=0.02, segments=2, angle_limit=math.radians(35)):
    mod = obj.modifiers.new("Bevel", 'BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = angle_limit
    mod.harden_normals = True
    return mod


def smart_uv(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)


def join_objects(objs, name):
    if not objs:
        return None
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    result = bpy.context.view_layer.objects.active
    result.name = name
    return result


def apply_all_transforms(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def look_at(cam_obj, target):
    direction = (target - cam_obj.location)
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()


def setup_clay_render(res_x=960, res_y=540, samples=32):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.film_transparent = False
    # AgX flattens a near-monochrome clay scene into low contrast; Standard keeps
    # the bevels + shadows readable, which is the point of a clay pass.
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.view_layers[0].material_override = get_clay_material()
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        # darker than the clay material itself so the silhouette reads against it
        bg.inputs[0].default_value = (0.30, 0.32, 0.36, 1.0)
        bg.inputs[1].default_value = 1.0


def add_ground_plane(size=4.0, material="stone"):
    """A simple ground plane so props/buildings get a contact shadow instead of
    floating in the clay renders. z=0 is ground per BRIEF-COMMON."""
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = "ground_plane"
    obj.data.materials.append(get_shared_material(material))
    return obj


def clear_material_override():
    bpy.context.scene.view_layers[0].material_override = None


def add_sun(name="Sun", energy=4.5, angle=(math.radians(55), 0, math.radians(35))):
    light_data = bpy.data.lights.new(name, type='SUN')
    light_data.energy = energy
    light_data.angle = math.radians(2.0)
    light_obj = bpy.data.objects.new(name, light_data)
    light_obj.rotation_euler = angle
    bpy.context.collection.objects.link(light_obj)
    return light_obj


def add_fill_sun(name="Fill", energy=0.5, angle=(math.radians(110), 0, math.radians(-60))):
    light_data = bpy.data.lights.new(name, type='SUN')
    light_data.energy = energy
    light_data.angle = math.radians(4.0)
    light_obj = bpy.data.objects.new(name, light_data)
    light_obj.rotation_euler = angle
    bpy.context.collection.objects.link(light_obj)
    return light_obj


def add_camera(name, location, target, lens=35):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    cam_obj = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = location
    look_at(cam_obj, target)
    bpy.context.scene.camera = cam_obj
    return cam_obj


def quick_check(path, res=640):
    """Fast Workbench look-fix render, no lights/materials needed. Use between
    build passes to LOOK before committing to a slow Cycles clay pass."""
    scene = bpy.context.scene
    prev_engine = scene.render.engine
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'MATERIAL'
    scene.render.resolution_x = res
    scene.render.resolution_y = res
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    scene.render.engine = prev_engine


def render_to(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def export_glb(objs, filepath):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        use_selection=True,
        export_format='GLB',
        export_apply=True,
        export_yup=True,
    )
