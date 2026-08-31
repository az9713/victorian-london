"""Shared helpers for batch B2 (church, ginpalace).

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
RENDER_DIR = PROJECT + "/blender/renders/B2"

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RENDER_DIR, exist_ok=True)

MATERIAL_COLORS = {
    "brick":       (0.075, 0.055, 0.045, 1.0),
    "slate":       (0.11, 0.13, 0.15, 1.0),
    "stone":       (0.72, 0.68, 0.58, 1.0),
    "iron":        (0.045, 0.045, 0.05, 1.0),
    "glass":       (0.30, 0.36, 0.35, 0.35),
    "paint_dark":  (0.03, 0.045, 0.035, 1.0),
    "paint_green": (0.035, 0.11, 0.06, 1.0),
    "planks":      (0.16, 0.11, 0.075, 1.0),
    "plaster":     (0.55, 0.50, 0.42, 1.0),
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
    return mat


def new_object(name, bm, material_names):
    """material_names: list, in the order used by add_box's mat_idx params.
    Geometry is assembled from many independent add_box/add_quad calls whose
    touching faces share COINCIDENT but not merged vertices -- weld them
    first (merge by distance) so shared edges are manifold. Without this the
    bevel modifier treats every box-to-box seam as a boundary edge and
    renders it as a dark crack."""
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
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


def add_tri(bm, p0, p1, p2, mat_idx=0):
    verts = [bm.verts.new(V(*p)) for p in (p0, p1, p2)]
    face = bm.faces.new(verts)
    face.material_index = mat_idx
    return face


def add_cylinder(bm, cx, cz, y0, y1, radius, segments=16, mat_idx=0,
                  radius_top=None, cap_bottom=True, cap_top=True,
                  angle_start=0.0, angle_end=2 * math.pi):
    """Vertical cylinder / frustum in brief space. cx,cz = centre, y0..y1 height.
    angle_start/end let you build a partial (arc) shell, capped with radial
    end faces at both open ends when the sweep is not a full circle."""
    if radius_top is None:
        radius_top = radius
    full = abs((angle_end - angle_start) - 2 * math.pi) < 1e-6
    n = segments if full else segments
    bottom = []
    top = []
    steps = n if full else n
    count = steps if full else steps + 1
    for i in range(count):
        a = angle_start + (angle_end - angle_start) * i / steps
        bx = cx + radius * math.cos(a)
        bz = cz + radius * math.sin(a)
        tx = cx + radius_top * math.cos(a)
        tz = cz + radius_top * math.sin(a)
        bottom.append(bm.verts.new(V(bx, y0, bz)))
        top.append(bm.verts.new(V(tx, y1, tz)))
    ring = count if full else count - 1
    for i in range(ring):
        j = (i + 1) % count if full else i + 1
        f = bm.faces.new((bottom[i], bottom[j], top[j], top[i]))
        f.material_index = mat_idx
    if full:
        if cap_bottom:
            f = bm.faces.new(list(reversed(bottom)))
            f.material_index = mat_idx
        if cap_top:
            f = bm.faces.new(top)
            f.material_index = mat_idx
    return bottom, top


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


def setup_clay_render(res=(960, 540), samples=32):
    """Cycles CPU clay pass via view-layer material override (matches the
    sibling batches' convention) -- Standard view transform keeps bevels and
    shadows readable instead of AgX flattening a near-monochrome scene."""
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = res[0]
    scene.render.resolution_y = res[1]
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    clay = bpy.data.materials.get("_clay_override")
    if clay is None:
        clay = bpy.data.materials.new("_clay_override")
        clay.use_nodes = True
        bsdf = clay.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = CLAY_GREY
        bsdf.inputs["Roughness"].default_value = 0.85
    scene.view_layers[0].material_override = clay
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    scene.world = world
    # bright, near-neutral sky as ambient fill -- a clay pass needs geometry
    # to read evenly even where the key sun can't reach a recessed reveal;
    # a near-black default world crushes those reveals to unreadable black.
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.55, 0.58, 0.62, 1.0)
        bg.inputs[1].default_value = 1.3
    return scene


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


def add_round_window(bm, bay_x0, bay_x1, z_face, thickness, y0_wall, y1_wall,
                      sill_y, springing_y, wall_mat, glass_mat,
                      seg=8, glass_z_frac=0.5, sill_proud=0.06, sill_mat=None):
    """One round-headed window bay, punched through a wall facing +/-z.

    Caller is responsible for the piers either side (this only fills the
    bay's own x-range: base spandrel below the sill, the arched reveal +
    glazing, and the spandrel above the arch crown up to y1_wall). z_face is
    the wall's outward z coordinate; thickness extends toward the building
    interior (sign inferred from z_face). Real through-void with a curved
    reveal -- not a decal.
    """
    sign = 1.0 if z_face >= 0 else -1.0
    z_outer = z_face
    z_inner = z_face - sign * thickness
    z_glass = z_face - sign * thickness * glass_z_frac
    half_w = (bay_x1 - bay_x0) / 2.0
    bx_c = (bay_x0 + bay_x1) / 2.0
    crown_y = springing_y + half_w
    sill_mat = wall_mat if sill_mat is None else sill_mat

    # base spandrel (below sill) -- ties this bay's wall to full thickness
    add_box(bm, bay_x0, bay_x1, y0_wall, sill_y, z_outer, z_inner, mat_idx=wall_mat)
    # proud sill ledge, projecting past the outer face to shed water
    add_box(bm, bay_x0 - 0.05, bay_x1 + 0.05, sill_y - sill_proud, sill_y,
            z_outer + sign * 0.05, z_inner, mat_idx=sill_mat)
    # spandrel above the arch crown, up to the eave/parapet line
    add_box(bm, bay_x0, bay_x1, crown_y, y1_wall, z_outer, z_inner, mat_idx=wall_mat)

    # arch reveal: curved tunnel from outer face to inner face, springing_y
    # to crown_y, jambs (straight sides) below springing_y down to sill_y
    prev_o, prev_i = None, None
    pts = []
    for i in range(seg + 1):
        a = math.pi * i / seg  # 0..pi, 0 = left springing, pi = right springing
        lx = bx_c - half_w * math.cos(a)
        ly = springing_y + half_w * math.sin(a)
        pts.append((lx, ly))
    # straight jambs, sill_y -> springing_y, at each end of the arc
    left_x, right_x = bay_x0, bay_x1
    vo_l0 = bm.verts.new(V(left_x, sill_y, z_outer))
    vi_l0 = bm.verts.new(V(left_x, sill_y, z_inner))
    vo_l1 = bm.verts.new(V(left_x, springing_y, z_outer))
    vi_l1 = bm.verts.new(V(left_x, springing_y, z_inner))
    f = bm.faces.new((vi_l0, vo_l0, vo_l1, vi_l1))
    f.material_index = wall_mat
    vo_r0 = bm.verts.new(V(right_x, sill_y, z_outer))
    vi_r0 = bm.verts.new(V(right_x, sill_y, z_inner))
    vo_r1 = bm.verts.new(V(right_x, springing_y, z_outer))
    vi_r1 = bm.verts.new(V(right_x, springing_y, z_inner))
    f = bm.faces.new((vo_r0, vi_r0, vi_r1, vo_r1))
    f.material_index = wall_mat
    # curved arch reveal
    prev_o = vo_l1
    prev_i = vi_l1
    for (lx, ly) in pts[1:]:
        vo = bm.verts.new(V(lx, ly, z_outer))
        vi = bm.verts.new(V(lx, ly, z_inner))
        f = bm.faces.new((prev_i, vi, vo, prev_o))
        f.material_index = wall_mat
        prev_o, prev_i = vo, vi

    # glazing: rectangular light below springing + fan above (real thin pane
    # set back in the reveal, not coplanar with the outer wall face)
    add_quad(bm, (left_x, sill_y, z_glass), (right_x, sill_y, z_glass),
             (right_x, springing_y, z_glass), (left_x, springing_y, z_glass),
             mat_idx=glass_mat)
    apex = bm.verts.new(V(bx_c, springing_y, z_glass))
    prev = bm.verts.new(V(pts[0][0], pts[0][1], z_glass))
    for (lx, ly) in pts[1:]:
        cur = bm.verts.new(V(lx, ly, z_glass))
        f = bm.faces.new((apex, cur, prev))
        f.material_index = glass_mat
        prev = cur


def add_rect_window(bm, bay_x0, bay_x1, z_face, thickness, y0_wall, y1_wall,
                     sill_y, head_y, wall_mat, glass_mat, sill_mat=None,
                     sill_proud=0.06, bar_cols=1, bar_rows=1, bar_w=0.05,
                     bar_mat=None, meeting_rail_y=None, glass_z_frac=0.5):
    """One rectangular window/door bay, punched through a wall facing +/-z.
    Fills the bay's own x-range only (spandrels above/below + reveal jambs +
    glazing); caller builds the piers either side. bar_cols/bar_rows split
    the light with real proud glazing-bar geometry (sash meeting rail via
    meeting_rail_y). Set head_y == y1_wall and sill_y == y0_wall to leave
    top/bottom spandrels degenerate (a full-height door bay)."""
    sign = 1.0 if z_face >= 0 else -1.0
    z_outer = z_face
    z_inner = z_face - sign * thickness
    z_glass = z_face - sign * thickness * glass_z_frac
    z_bar = z_face - sign * thickness * (glass_z_frac - 0.06)
    sill_mat = wall_mat if sill_mat is None else sill_mat
    bar_mat = wall_mat if bar_mat is None else bar_mat

    if sill_y > y0_wall:
        add_box(bm, bay_x0, bay_x1, y0_wall, sill_y, z_outer, z_inner, mat_idx=wall_mat)
        add_box(bm, bay_x0 - 0.05, bay_x1 + 0.05, sill_y - sill_proud, sill_y,
                z_outer + sign * 0.05, z_inner, mat_idx=sill_mat)
    if head_y < y1_wall:
        add_box(bm, bay_x0, bay_x1, head_y, y1_wall, z_outer, z_inner, mat_idx=wall_mat)

    # reveal jambs (left, right) + lintel/sill-edge reveal (top, bottom)
    add_quad(bm, (bay_x0, sill_y, z_inner), (bay_x0, sill_y, z_outer),
             (bay_x0, head_y, z_outer), (bay_x0, head_y, z_inner), mat_idx=wall_mat)
    add_quad(bm, (bay_x1, sill_y, z_outer), (bay_x1, sill_y, z_inner),
             (bay_x1, head_y, z_inner), (bay_x1, head_y, z_outer), mat_idx=wall_mat)
    add_quad(bm, (bay_x0, head_y, z_outer), (bay_x1, head_y, z_outer),
             (bay_x1, head_y, z_inner), (bay_x0, head_y, z_inner), mat_idx=wall_mat)
    add_quad(bm, (bay_x0, sill_y, z_inner), (bay_x1, sill_y, z_inner),
             (bay_x1, sill_y, z_outer), (bay_x0, sill_y, z_outer), mat_idx=wall_mat)

    # glazing pane(s), set back in the reveal
    add_quad(bm, (bay_x0, sill_y, z_glass), (bay_x1, sill_y, z_glass),
             (bay_x1, head_y, z_glass), (bay_x0, head_y, z_glass), mat_idx=glass_mat)

    # proud glazing bars: vertical mullions + horizontal bars (+ sash meeting rail)
    w = bay_x1 - bay_x0
    h = head_y - sill_y
    for c in range(1, bar_cols):
        bx = bay_x0 + w * c / bar_cols
        add_box(bm, bx - bar_w / 2, bx + bar_w / 2, sill_y, head_y,
                z_bar, z_bar - sign * 0.02, mat_idx=bar_mat)
    for r in range(1, bar_rows):
        by = sill_y + h * r / bar_rows
        add_box(bm, bay_x0, bay_x1, by - bar_w / 2, by + bar_w / 2,
                z_bar, z_bar - sign * 0.02, mat_idx=bar_mat)
    if meeting_rail_y is not None:
        add_box(bm, bay_x0, bay_x1, meeting_rail_y - bar_w * 0.6,
                meeting_rail_y + bar_w * 0.6, z_bar, z_bar - sign * 0.02,
                mat_idx=bar_mat)
    # frame proud of the wall face all round (reads as real joinery, not a
    # hole in the brick)
    fw = 0.06
    for (a0, a1, b0, b1) in (
        (bay_x0 - fw, bay_x0, sill_y, head_y),
        (bay_x1, bay_x1 + fw, sill_y, head_y),
        (bay_x0 - fw, bay_x1 + fw, head_y, head_y + fw),
        (bay_x0 - fw, bay_x1 + fw, sill_y - fw, sill_y),
    ):
        add_box(bm, a0, a1, b0, b1, z_outer + sign * 0.02, z_outer - sign * 0.06,
                mat_idx=bar_mat)


def add_round_door(bm, bay_x0, bay_x1, z_face, thickness, y0_wall, y1_wall,
                    door_y1, wall_mat, door_mat, seg=8, door_z_frac=0.55,
                    threshold_h=0.03):
    """One round-headed doorway, punched through a wall facing +/-z, floor to
    door_y1 (springing), round head above to the crown. Fills a threshold
    (not a sill -- floor-level), the curved reveal, spandrel above the
    crown, and a recessed door leaf with a proud plate/pull so it reads as
    an opening door, not a hole."""
    sign = 1.0 if z_face >= 0 else -1.0
    z_outer = z_face
    z_inner = z_face - sign * thickness
    z_door = z_face - sign * thickness * door_z_frac
    half_w = (bay_x1 - bay_x0) / 2.0
    bx_c = (bay_x0 + bay_x1) / 2.0
    crown_y = door_y1 + half_w

    # low stone threshold, proud of the floor
    add_box(bm, bay_x0 - 0.05, bay_x1 + 0.05, 0.0, threshold_h,
            z_outer + sign * 0.05, z_inner, mat_idx=wall_mat)
    # spandrel above the arch crown
    add_box(bm, bay_x0, bay_x1, crown_y, y1_wall, z_outer, z_inner, mat_idx=wall_mat)

    pts = []
    for i in range(seg + 1):
        a = math.pi * i / seg
        lx = bx_c - half_w * math.cos(a)
        ly = door_y1 + half_w * math.sin(a)
        pts.append((lx, ly))
    left_x, right_x = bay_x0, bay_x1
    vo_l0 = bm.verts.new(V(left_x, threshold_h, z_outer))
    vi_l0 = bm.verts.new(V(left_x, threshold_h, z_inner))
    vo_l1 = bm.verts.new(V(left_x, door_y1, z_outer))
    vi_l1 = bm.verts.new(V(left_x, door_y1, z_inner))
    f = bm.faces.new((vi_l0, vo_l0, vo_l1, vi_l1))
    f.material_index = wall_mat
    vo_r0 = bm.verts.new(V(right_x, threshold_h, z_outer))
    vi_r0 = bm.verts.new(V(right_x, threshold_h, z_inner))
    vo_r1 = bm.verts.new(V(right_x, door_y1, z_outer))
    vi_r1 = bm.verts.new(V(right_x, door_y1, z_inner))
    f = bm.faces.new((vo_r0, vi_r0, vi_r1, vo_r1))
    f.material_index = wall_mat
    prev_o, prev_i = vo_l1, vi_l1
    for (lx, ly) in pts[1:]:
        vo = bm.verts.new(V(lx, ly, z_outer))
        vi = bm.verts.new(V(lx, ly, z_inner))
        f = bm.faces.new((prev_i, vi, vo, prev_o))
        f.material_index = wall_mat
        prev_o, prev_i = vo, vi

    # door leaf: rectangular below springing + arched fanlight fill above,
    # set back in the reveal; two leaves implied by a proud centre stile
    add_quad(bm, (left_x, threshold_h, z_door), (right_x, threshold_h, z_door),
             (right_x, door_y1, z_door), (left_x, door_y1, z_door), mat_idx=door_mat)
    apex = bm.verts.new(V(bx_c, door_y1, z_door))
    prev = bm.verts.new(V(pts[0][0], pts[0][1], z_door))
    for (lx, ly) in pts[1:]:
        cur = bm.verts.new(V(lx, ly, z_door))
        f = bm.faces.new((apex, cur, prev))
        f.material_index = door_mat
        prev = cur
    # centre stile (where the two leaves meet) + a plate/pull proud of the face
    add_box(bm, bx_c - 0.03, bx_c + 0.03, threshold_h, door_y1,
            z_door + sign * 0.02, z_door - sign * 0.02, mat_idx=door_mat)
    pull_y = threshold_h + (door_y1 - threshold_h) * 0.45
    add_box(bm, bx_c - half_w * 0.35 - 0.05, bx_c - half_w * 0.35 + 0.05,
            pull_y - 0.06, pull_y + 0.06,
            z_door + sign * 0.05, z_door + sign * 0.02, mat_idx=door_mat)


def add_rect_window_xface(bm, bay_z0, bay_z1, x_face, thickness, y0_wall, y1_wall,
                           sill_y, head_y, wall_mat, glass_mat, sill_mat=None,
                           sill_proud=0.06, bar_cols=1, bar_rows=1, bar_w=0.05,
                           bar_mat=None, meeting_rail_y=None, glass_x_frac=0.5,
                           frame=True):
    """X-facing counterpart of add_rect_window (wall faces +/-x; the opening's
    horizontal extent runs along z, thickness along x). Used for the gin
    palace's west shopfront/upper sashes. Built entirely with add_box/add_quad
    (both already axis-agnostic via V()) -- never raw Vector() -- to avoid the
    axis-swap bug that hit the church door."""
    sign = 1.0 if x_face >= 0 else -1.0
    x_outer = x_face
    x_inner = x_face - sign * thickness
    x_glass = x_face - sign * thickness * glass_x_frac
    x_bar = x_face - sign * thickness * (glass_x_frac - 0.06)
    sill_mat = wall_mat if sill_mat is None else sill_mat
    bar_mat = wall_mat if bar_mat is None else bar_mat

    if sill_y > y0_wall:
        add_box(bm, x_outer, x_inner, y0_wall, sill_y, bay_z0, bay_z1, mat_idx=wall_mat)
        add_box(bm, x_outer + sign * 0.05, x_inner, sill_y - sill_proud, sill_y,
                bay_z0 - 0.05, bay_z1 + 0.05, mat_idx=sill_mat)
    if head_y < y1_wall:
        add_box(bm, x_outer, x_inner, head_y, y1_wall, bay_z0, bay_z1, mat_idx=wall_mat)

    # reveal jambs (top, bottom) + lintel/sill-edge reveal (left, right)
    add_quad(bm, (x_inner, sill_y, bay_z0), (x_outer, sill_y, bay_z0),
             (x_outer, head_y, bay_z0), (x_inner, head_y, bay_z0), mat_idx=wall_mat)
    add_quad(bm, (x_outer, sill_y, bay_z1), (x_inner, sill_y, bay_z1),
             (x_inner, head_y, bay_z1), (x_outer, head_y, bay_z1), mat_idx=wall_mat)
    add_quad(bm, (x_outer, head_y, bay_z0), (x_outer, head_y, bay_z1),
             (x_inner, head_y, bay_z1), (x_inner, head_y, bay_z0), mat_idx=wall_mat)
    add_quad(bm, (x_inner, sill_y, bay_z0), (x_inner, sill_y, bay_z1),
             (x_outer, sill_y, bay_z1), (x_outer, sill_y, bay_z0), mat_idx=wall_mat)

    # glazing pane, set back in the reveal
    add_quad(bm, (x_glass, sill_y, bay_z0), (x_glass, sill_y, bay_z1),
             (x_glass, head_y, bay_z1), (x_glass, head_y, bay_z0), mat_idx=glass_mat)

    w = bay_z1 - bay_z0
    h = head_y - sill_y
    for c in range(1, bar_cols):
        bz = bay_z0 + w * c / bar_cols
        add_box(bm, x_bar, x_bar - sign * 0.02, sill_y, head_y,
                bz - bar_w / 2, bz + bar_w / 2, mat_idx=bar_mat)
    for r in range(1, bar_rows):
        by = sill_y + h * r / bar_rows
        add_box(bm, x_bar, x_bar - sign * 0.02, by - bar_w / 2, by + bar_w / 2,
                bay_z0, bay_z1, mat_idx=bar_mat)
    if meeting_rail_y is not None:
        add_box(bm, x_bar, x_bar - sign * 0.02, meeting_rail_y - bar_w * 0.6,
                meeting_rail_y + bar_w * 0.6, bay_z0, bay_z1, mat_idx=bar_mat)
    if frame:
        fw = 0.06
        for (b0, b1, c0, c1) in (
            (bay_z0 - fw, bay_z0, sill_y, head_y),
            (bay_z1, bay_z1 + fw, sill_y, head_y),
            (bay_z0 - fw, bay_z1 + fw, head_y, head_y + fw),
            (bay_z0 - fw, bay_z1 + fw, sill_y - fw, sill_y),
        ):
            add_box(bm, x_outer - sign * 0.02, x_outer + sign * 0.06, c0, c1,
                    b0, b1, mat_idx=bar_mat)


def add_round_door_xface(bm, bay_z0, bay_z1, x_face, thickness, y0_wall, y1_wall,
                          door_y1, wall_mat, door_mat, seg=8, door_x_frac=0.55,
                          threshold_h=0.03):
    """X-facing counterpart of add_round_door (front door on a +/-x wall)."""
    sign = 1.0 if x_face >= 0 else -1.0
    x_outer = x_face
    x_inner = x_face - sign * thickness
    x_door = x_face - sign * thickness * door_x_frac
    half_w = (bay_z1 - bay_z0) / 2.0
    zc = (bay_z0 + bay_z1) / 2.0
    crown_y = door_y1 + half_w

    add_box(bm, x_outer + sign * 0.05, x_inner, 0.0, threshold_h,
            bay_z0 - 0.05, bay_z1 + 0.05, mat_idx=wall_mat)
    add_box(bm, x_outer, x_inner, crown_y, y1_wall, bay_z0, bay_z1, mat_idx=wall_mat)

    pts = []
    for i in range(seg + 1):
        a = math.pi * i / seg
        lz = zc - half_w * math.cos(a)
        ly = door_y1 + half_w * math.sin(a)
        pts.append((lz, ly))
    vo_l0 = bm.verts.new(V(x_outer, threshold_h, bay_z0))
    vi_l0 = bm.verts.new(V(x_inner, threshold_h, bay_z0))
    vo_l1 = bm.verts.new(V(x_outer, door_y1, bay_z0))
    vi_l1 = bm.verts.new(V(x_inner, door_y1, bay_z0))
    f = bm.faces.new((vi_l0, vo_l0, vo_l1, vi_l1)); f.material_index = wall_mat
    vo_r0 = bm.verts.new(V(x_outer, threshold_h, bay_z1))
    vi_r0 = bm.verts.new(V(x_inner, threshold_h, bay_z1))
    vo_r1 = bm.verts.new(V(x_outer, door_y1, bay_z1))
    vi_r1 = bm.verts.new(V(x_inner, door_y1, bay_z1))
    f = bm.faces.new((vo_r0, vi_r0, vi_r1, vo_r1)); f.material_index = wall_mat
    prev_o, prev_i = vo_l1, vi_l1
    for (lz, ly) in pts[1:]:
        vo = bm.verts.new(V(x_outer, ly, lz))
        vi = bm.verts.new(V(x_inner, ly, lz))
        f = bm.faces.new((prev_o, vo, vi, prev_i)); f.material_index = wall_mat
        prev_o, prev_i = vo, vi

    add_quad(bm, (x_door, threshold_h, bay_z0), (x_door, threshold_h, bay_z1),
             (x_door, door_y1, bay_z1), (x_door, door_y1, bay_z0), mat_idx=door_mat)
    apex = bm.verts.new(V(x_door, door_y1, zc))
    prev = bm.verts.new(V(x_door, pts[0][1], pts[0][0]))
    for (lz, ly) in pts[1:]:
        cur = bm.verts.new(V(x_door, ly, lz))
        f = bm.faces.new((apex, prev, cur)); f.material_index = door_mat
        prev = cur
    add_box(bm, x_door + 0.02, x_door - 0.02, threshold_h, door_y1, zc - 0.03, zc + 0.03, mat_idx=door_mat)
    pull_y = threshold_h + (door_y1 - threshold_h) * 0.45
    add_box(bm, x_door + 0.05, x_door - 0.05, pull_y - 0.06, pull_y + 0.06,
            zc + half_w * 0.35 - 0.05, zc + half_w * 0.35 + 0.05, mat_idx=door_mat)


def bbox_and_tris(objects):
    """Print combined bounding box (brief-space x,y,z) and total tri count."""
    xs, ys, zs = [], [], []
    tris = 0
    for o in objects:
        if o.type != 'MESH':
            continue
        for v in o.bound_box:
            world = o.matrix_world @ Vector(v)
            xs.append(world.x)
            ys.append(-world.y)  # back to brief z
            zs.append(world.z)   # brief y (height)
        for p in o.data.polygons:
            n = len(p.vertices)
            tris += max(0, n - 2)
    print(f"[bbox] x[{min(xs):.2f},{max(xs):.2f}] "
          f"height[{min(zs):.2f},{max(zs):.2f}] z[{min(ys):.2f},{max(ys):.2f}] "
          f"tris~{tris}")
