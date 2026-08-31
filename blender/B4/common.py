"""Shared helpers for batch B4 (terrace facade modules terrace0-3 .. terrace2-4).
Coordinate convention (matches B1/B3): brief-space (x, y_height, z_depth) ->
Blender Z-up via V(). FRONT = -z local (outward normal of the street face
points toward -z). Ground y=0. x = frontage (module width, -2.5..+2.5),
z = depth (-7.0..+7.0, front at z=-7.0).
Blender internal: X_blender = x, Y_blender = -z, Z_blender = y_height.
"""
import bpy
import bmesh
import math
import os
from mathutils import Vector

PROJECT = "C:/Users/USERNAME/Downloads/projects/victorian-london"
MODELS_DIR = PROJECT + "/sandbox/assets/models"
RENDER_DIR = PROJECT + "/blender/renders/B4"

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RENDER_DIR, exist_ok=True)

# ---- shared PBR material NAMES (binding, per BRIEF-COMMON / B4 brief) ----
MATERIAL_COLORS = {
    "brick":       (0.085, 0.060, 0.048, 1.0),  # sooted London stock brick
    "slate":       (0.11, 0.13, 0.15, 1.0),
    "glass":       (0.30, 0.36, 0.35, 0.35),
    "planks":      (0.17, 0.115, 0.075, 1.0),
    "paint_green": (0.045, 0.13, 0.085, 1.0),   # variant0 shopfront joinery
    "paint_dark":  (0.035, 0.045, 0.04, 1.0),   # variant1/2 doors
    "iron":        (0.045, 0.045, 0.05, 1.0),
}

CLAY_GREY = (0.62, 0.6, 0.58, 1.0)


def V(x, y, z):
    """Brief-space (x, y_height, z_depth) -> Blender Z-up Vector."""
    return Vector((x, -z, y))


def clear_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras,
                 bpy.data.lights, bpy.data.images):
        for b in list(coll):
            if b.users == 0:
                coll.remove(b)


def get_material(name):
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    color = MATERIAL_COLORS.get(name, (0.5, 0.5, 0.5, 1.0))
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.75
    if name == "glass":
        bsdf.inputs["Alpha"].default_value = 0.35
        bsdf.inputs["Roughness"].default_value = 0.15
        bsdf.inputs["Transmission Weight"].default_value = 0.6
        mat.blend_method = 'BLEND'
    if name == "iron":
        bsdf.inputs["Metallic"].default_value = 0.75
        bsdf.inputs["Roughness"].default_value = 0.35
    return mat


def new_object(name, bm, material_names):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    for mname in material_names:
        mesh.materials.append(get_material(mname))
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def add_box(bm, x0, x1, y0, y1, z0, z1, mat_idx=0):
    """Axis-aligned box in brief space (x, y=height, z=depth). Outward normals."""
    if x0 > x1:
        x0, x1 = x1, x0
    if y0 > y1:
        y0, y1 = y1, y0
    if z0 > z1:
        z0, z1 = z1, z0
    v = [
        bm.verts.new(V(x0, y0, z0)), bm.verts.new(V(x1, y0, z0)),
        bm.verts.new(V(x1, y0, z1)), bm.verts.new(V(x0, y0, z1)),
        bm.verts.new(V(x0, y1, z0)), bm.verts.new(V(x1, y1, z0)),
        bm.verts.new(V(x1, y1, z1)), bm.verts.new(V(x0, y1, z1)),
    ]
    faces_idx = [
        (0, 1, 2, 3),  # bottom
        (7, 6, 5, 4),  # top
        (0, 4, 5, 1),  # z0 face
        (1, 5, 6, 2),  # x1 face
        (2, 6, 7, 3),  # z1 face
        (3, 7, 4, 0),  # x0 face
    ]
    faces = []
    for f in faces_idx:
        face = bm.faces.new([v[i] for i in f])
        face.material_index = mat_idx
        faces.append(face)
    return v, faces


def add_quad(bm, p0, p1, p2, p3, mat_idx=0):
    """p0..p3 are (x,y,z) brief-space tuples, wound CCW as seen from the
    outward normal side."""
    verts = [bm.verts.new(V(*p)) for p in (p0, p1, p2, p3)]
    face = bm.faces.new(verts)
    face.material_index = mat_idx
    return face


def add_tri(bm, p0, p1, p2, mat_idx=0):
    verts = [bm.verts.new(V(*p)) for p in (p0, p1, p2)]
    face = bm.faces.new(verts)
    face.material_index = mat_idx
    return face


def add_cylinder(bm, cx, cz, y0, y1, radius, segments=12, mat_idx=0,
                  radius_top=None, cap_bottom=True, cap_top=True):
    """Vertical cylinder / frustum in brief space. cx,cz = centre, y0..y1 height."""
    if radius_top is None:
        radius_top = radius
    bottom = []
    top = []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        bx = cx + radius * math.cos(a)
        bz = cz + radius * math.sin(a)
        tx = cx + radius_top * math.cos(a)
        tz = cz + radius_top * math.sin(a)
        bottom.append(bm.verts.new(V(bx, y0, bz)))
        top.append(bm.verts.new(V(tx, y1, tz)))
    for i in range(segments):
        j = (i + 1) % segments
        f = bm.faces.new((bottom[i], bottom[j], top[j], top[i]))
        f.material_index = mat_idx
    if cap_bottom:
        f = bm.faces.new(list(reversed(bottom)))
        f.material_index = mat_idx
    if cap_top:
        f = bm.faces.new(top)
        f.material_index = mat_idx
    return bottom, top


def add_horiz_cylinder(bm, x0, x1, cy, cz, radius, segments=10, mat_idx=0):
    """Cylinder with its axis along x (brief space), from x0 to x1."""
    ring0 = []
    ring1 = []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        oy = cy + radius * math.cos(a)
        oz = cz + radius * math.sin(a)
        ring0.append(bm.verts.new(V(x0, oy, oz)))
        ring1.append(bm.verts.new(V(x1, oy, oz)))
    for i in range(segments):
        j = (i + 1) % segments
        f = bm.faces.new((ring0[i], ring1[i], ring1[j], ring0[j]))
        f.material_index = mat_idx
    f = bm.faces.new(list(reversed(ring0)))
    f.material_index = mat_idx
    f = bm.faces.new(ring1)
    f.material_index = mat_idx
    return ring0, ring1


def add_bevel(obj, width=0.02, segments=2, angle_deg=35):
    mod = obj.modifiers.new("Bevel", 'BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(angle_deg)
    mod.harden_normals = False
    return mod


def smart_uv(obj):
    bpy.context.view_layer.objects.active = obj
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    with bpy.context.temp_override(active_object=obj, object=obj,
                                    selected_objects=[obj],
                                    selected_editable_objects=[obj]):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
        bpy.ops.object.mode_set(mode='OBJECT')


def export_glb(objects, filepath, apply_modifiers=True):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    with bpy.context.temp_override(selected_objects=objects,
                                    selected_editable_objects=objects,
                                    active_object=objects[0]):
        bpy.ops.export_scene.gltf(
            filepath=filepath,
            use_selection=True,
            export_apply=apply_modifiers,
            export_yup=True,
            export_materials='EXPORT',
            export_image_format='NONE',
        )
    print(f"[export] wrote {filepath}")


def setup_render(engine='CYCLES', samples=32, res=(960, 540), device='CPU'):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES' if engine == 'CYCLES' else 'BLENDER_WORKBENCH'
    scene.render.resolution_x = res[0]
    scene.render.resolution_y = res[1]
    scene.render.image_settings.file_format = 'PNG'
    if engine == 'CYCLES':
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True
        scene.cycles.device = device
    return scene


def add_sun(name="Sun", energy=3.0, angle_deg=2.0, elevation_deg=45, azimuth_deg=135):
    light_data = bpy.data.lights.new(name, type='SUN')
    light_data.energy = energy
    light_data.angle = math.radians(angle_deg)
    obj = bpy.data.objects.new(name, light_data)
    bpy.context.collection.objects.link(obj)
    obj.rotation_euler = (math.radians(90 - elevation_deg), 0, math.radians(azimuth_deg))
    return obj


def add_fill_light(name="Fill", energy=1.2, loc=(0, -10, 8)):
    light_data = bpy.data.lights.new(name, type='AREA')
    light_data.energy = energy
    light_data.size = 6
    obj = bpy.data.objects.new(name, light_data)
    obj.location = loc
    bpy.context.collection.objects.link(obj)
    return obj


def add_camera(name, loc_blender, look_at_blender, lens=35):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    obj = bpy.data.objects.new(name, cam_data)
    obj.location = loc_blender
    bpy.context.collection.objects.link(obj)
    direction = (look_at_blender - obj.location)
    rot_quat = direction.to_track_quat('-Z', 'Y')
    obj.rotation_euler = rot_quat.to_euler()
    bpy.context.scene.camera = obj
    return obj


def render_to(filepath):
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)
    print(f"[render] wrote {filepath}")


def apply_clay_override(objects):
    clay = bpy.data.materials.get("_clay_override")
    if clay is None:
        clay = bpy.data.materials.new("_clay_override")
        clay.use_nodes = True
        bsdf = clay.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = CLAY_GREY
        bsdf.inputs["Roughness"].default_value = 0.85
    backup = {}
    for o in objects:
        if o.type != 'MESH':
            continue
        backup[o.name] = list(o.data.materials)
        o.data.materials.clear()
        o.data.materials.append(clay)
    return backup


def restore_materials(objects, backup):
    for o in objects:
        if o.name not in backup:
            continue
        o.data.materials.clear()
        for m in backup[o.name]:
            o.data.materials.append(m)
