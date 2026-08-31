"""Shared helpers for batch B3 (rookery, viaduct-module, gy-flank, gaslamp, pillarbox).

Coordinate convention used by every build script in this batch:
    x = brief "x" (horizontal, world east-west-ish)
    y = brief "y" = HEIGHT, ground = 0
    z = brief "z" (horizontal depth/north-south-ish)
This matches the brief's own (x, height, z) language exactly. V() converts a
brief-space (x, y_height, z) triple into a Blender Z-up Vector so that, after
Blender's default glTF exporter (+Y up) conversion, the exported GLB's
(X, Y, Z) numbers equal the brief's (x, y, z) numbers with no surprises.
Blender internal: X_blender = x, Y_blender = -z, Z_blender = y_height.
"""
import bpy
import bmesh
import math
import os
from mathutils import Vector

PROJECT = "C:/Users/USERNAME/Downloads/projects/victorian-london"
MODELS_DIR = PROJECT + "/sandbox/assets/models"
RENDER_DIR = PROJECT + "/blender/renders/B3"

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RENDER_DIR, exist_ok=True)

MATERIAL_COLORS = {
    "brick":       (0.075, 0.055, 0.045, 1.0),
    "slate":       (0.11, 0.13, 0.15, 1.0),
    "stone":       (0.55, 0.51, 0.44, 1.0),
    "iron":        (0.045, 0.045, 0.05, 1.0),
    "glass":       (0.30, 0.36, 0.35, 0.35),
    "paint_dark":  (0.03, 0.045, 0.035, 1.0),
    "planks":      (0.16, 0.11, 0.075, 1.0),
    "postbox_red": (0.32, 0.03, 0.02, 1.0),
    "cobble":      (0.18, 0.18, 0.18, 1.0),
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
    if name == "postbox_red":
        bsdf.inputs["Roughness"].default_value = 0.5
    return mat


def new_object(name, bm, material_names):
    """material_names: list, in the order used by add_box's mat_idx params."""
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
        (0, 1, 2, 3),  # bottom (y0)
        (7, 6, 5, 4),  # top (y1)
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


def add_cylinder(bm, cx, cz, y0, y1, radius, segments=16, mat_idx=0,
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


def quarter_ellipse_arch(x_spring, y_spring, x_crown, y_crown, n=12):
    """Sample points (x, y) of a quarter-ellipse arch curve: vertical tangent
    at the springing (x_spring, y_spring), horizontal tangent at the crown
    (x_crown, y_crown). Used so two mirrored halves (adjoining viaduct piers)
    meet with a continuous smooth tangent exactly at the crown."""
    a = abs(x_crown - x_spring)
    b = abs(y_crown - y_spring)
    sign_x = 1 if x_crown > x_spring else -1
    pts = []
    for i in range(n + 1):
        t = (math.pi / 2) * i / n
        x = x_spring + sign_x * a * math.sin(t)
        y = y_spring + b * (1 - math.cos(t))
        pts.append((x, y))
    return pts


def add_swept_curve_wall(bm, pts, z0, z1, mat_idx=0):
    """Sweep a 2D arch profile pts=[(x,y), ...] along z from z0 to z1,
    building the curved barrel surface (used for arch soffit/extrados)."""
    n = len(pts)
    ring0 = [bm.verts.new(V(x, y, z0)) for (x, y) in pts]
    ring1 = [bm.verts.new(V(x, y, z1)) for (x, y) in pts]
    for i in range(n - 1):
        f = bm.faces.new((ring0[i], ring0[i + 1], ring1[i + 1], ring1[i]))
        f.material_index = mat_idx
    return ring0, ring1


def add_ring_face(bm, pts_inner, pts_outer, z, mat_idx=0, flip=False):
    """Flat annular arch-face band at fixed z between two matched profile
    curves (inner/outer radius of an arch ring), used for the visible arch
    face (voussoir order) seen face-on."""
    n = len(pts_inner)
    vi = [bm.verts.new(V(x, y, z)) for (x, y) in pts_inner]
    vo = [bm.verts.new(V(x, y, z)) for (x, y) in pts_outer]
    for i in range(n - 1):
        if flip:
            f = bm.faces.new((vi[i], vi[i + 1], vo[i + 1], vo[i]))
        else:
            f = bm.faces.new((vo[i], vo[i + 1], vi[i + 1], vi[i]))
        f.material_index = mat_idx
    return vi, vo


def add_bevel(obj, width=0.02, segments=2, angle_deg=35):
    mod = obj.modifiers.new("Bevel", 'BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(angle_deg)
    mod.harden_normals = False
    return mod


def shade_smooth_auto(obj, angle_deg=35):
    """Smooth-shade the object with an angle threshold: curved surfaces
    (cylinders, arches) read smooth, sharp features (box edges) stay
    faceted -- Blender 4.1+'s Shade Auto Smooth operator."""
    with bpy.context.temp_override(active_object=obj, object=obj,
                                    selected_objects=[obj],
                                    selected_editable_objects=[obj]):
        bpy.ops.object.shade_auto_smooth(angle=math.radians(angle_deg))


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
    # clear_scene() never touched the world, so every render before this
    # fix used Blender's near-black startup world with no ambient fill --
    # any recess, niche, or interior not directly hit by the sun/area
    # lights rendered pure black even though the geometry was correct.
    # A mid-grey world at full strength gives every enclosed surface a real
    # ambient bounce floor so the clay override can never read as an
    # unevidenced black hole.
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.45, 0.45, 0.48, 1.0)
        bg.inputs[1].default_value = 1.8
    # recessed/enclosed geometry (window reveals, niches, panel mouldings)
    # needs enough diffuse bounces to pick up any ambient at all -- default
    # is usually fine but this is cheap insurance against black pockets.
    if engine == 'CYCLES':
        scene.cycles.max_bounces = 8
        scene.cycles.diffuse_bounces = 6
    return scene


def add_sun(name="Sun", energy=3.0, angle_deg=45, elevation_deg=45, azimuth_deg=135):
    light_data = bpy.data.lights.new(name, type='SUN')
    light_data.energy = energy
    light_data.angle = math.radians(2.0)
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
    """Swap every material slot on the given objects to a single grey clay
    material, returning the data needed to restore originals."""
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
        if len(o.data.materials) == 0:
            o.data.materials.append(clay)
        else:
            # replace every slot in place (not clear+append) so no face's
            # material_index is left pointing past the end of the slot list
            for i in range(len(o.data.materials)):
                o.data.materials[i] = clay
    return backup


def restore_materials(objects, backup):
    for o in objects:
        if o.name not in backup:
            continue
        o.data.materials.clear()
        for m in backup[o.name]:
            o.data.materials.append(m)
