"""Asset 2: market-stall — sandbox/assets/models/stall.glb
Trestle stall, footprint ~2.4 x 1.2 m, counter ~0.9 m, canopy ridge ~2.1 m.
Two A-frame trestles (cross-halved legs + peg), top boards with gaps resting
on the trestle rails, side rail, canopy on two poles with visible ties,
produce boxes (crate-like) on the counter.
"""
import bpy
import bmesh
import math
import os
import sys
import random
import mathutils

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    new_mesh_object, add_bevel, smart_uv, apply_all_transforms,
    setup_clay_render, add_sun, add_fill_sun, add_camera, render_to,
    export_glb, clear_scene, MODELS_DIR, RENDERS_DIR, add_ground_plane,
    quick_check, add_box, add_sphere, add_cyl, add_beam,
)
from build_crate import add_crate

PLANKS, IRON, PLASTER = 0, 1, 2
MAT_NAMES = ["planks", "iron", "plaster"]

LEN, WID, COUNTER_H = 2.4, 1.0, 0.9
BOARD_T = 0.03


def build_trestle(bm, x0):
    """One A-frame trestle at local x=x0, legs splayed in Y, cross-halved at
    mid-height with a peg, plus a stretcher rail below the join."""
    top_y, bot_y = 0.42, 0.14
    # leg A: top -y to bottom +y ; leg B: top +y to bottom -y (they cross)
    legA_top = (x0, -top_y, COUNTER_H - 0.02)
    legA_bot = (x0, bot_y, 0.0)
    legB_top = (x0, top_y, COUNTER_H - 0.02)
    legB_bot = (x0, -bot_y, 0.0)
    add_beam(bm, legA_top, legA_bot, 0.05, 0.05, PLANKS)
    add_beam(bm, legB_top, legB_bot, 0.05, 0.05, PLANKS)
    # peg at the crossing point (legs cross halfway up -- cross-halved joint)
    # -- fattened from the round-1 size (0.018 r) so it actually reads at
    # render distance, plus a small square washer against each leg face
    # r6: root cause of stall_34's true-black pixels, finally found by
    # raycasting the exact camera ray in Python (not guessing from renders):
    # cross_z was COUNTER_H*0.42=0.378, but the legs (top_y=0.42/bot_y=0.14,
    # z 0.0-0.88) actually cross in Y at z = z_top*bot_y/(top_y+bot_y) =
    # 0.88*0.14/0.56 = 0.22 -- 0.158 m below where the peg/washers were
    # placed. The peg never covered the real joint; the two beams'
    # uncovered interpenetration seam there produced a sealed, zero-light
    # sliver from a narrow range of angles that no amount of fill light or
    # samples (tried up to 128 + a second fill + 5x world strength -- none
    # moved the pixel count) could reach, because it has no aperture at all.
    cross_z = (COUNTER_H - 0.02) * bot_y / (top_y + bot_y)
    add_cyl(bm, (x0, 0, cross_z), 0.03, 0.03, 0.16, IRON, segments=8, axis='y')
    # r6: enlarged from a small square washer (0.06x0.012x0.06) to an iron
    # strap plate -- the two crossed legs are separate, non-boolean meshes
    # that don't perfectly interpenetrate along their shared seam, leaving a
    # hairline gap that read as true black from any angle showing through it
    # (see cross_z fix above). A real strap-plate bracket bolted across the
    # joint is period-appropriate ironwork AND physically covers the seam
    # above and below the peg, instead of chasing a camera angle that hides
    # it. Centred slightly above cross_z (0.28 vs 0.22) and shortened to
    # 0.44 m tall so it stays clear of the ground (0.62 m centred on 0.22
    # ran from z=-0.09 to 0.53, poking 9 cm below the floor).
    plate_z = 0.28
    plate_h = 0.44
    for sy in (-1, 1):
        add_box(bm, (x0, sy * 0.06, plate_z), (0.20, 0.03, plate_h), IRON)
        # bolt nubs -- a bare slab reads as a placeholder, not fixed
        # hardware. Four proud rivet/bolt heads through the plate face,
        # same pattern as the canopy-pole socket clamp's bolt nubs above.
        for dx in (-0.06, 0.06):
            for dz in (-0.15, 0.15):
                add_cyl(bm, (x0 + dx, sy * 0.06, plate_z + dz), 0.012, 0.012,
                        0.05, IRON, segments=8, axis='y')
    # stretcher rail low down, ties the splayed feet together (also the "side
    # rail" hand-rail the brief calls for)
    add_beam(bm, (x0, -bot_y, 0.18), (x0, bot_y, 0.18), 0.04, 0.03, PLANKS)
    # trestle head -- a short cross-piece the top boards actually rest on
    add_beam(bm, (x0, -0.16, COUNTER_H - 0.015), (x0, 0.16, COUNTER_H - 0.015), 0.09, 0.03, PLANKS)


def build_top_boards(bm):
    n = 5
    board_w = 0.19
    gap = 0.015
    total = n * board_w + (n - 1) * gap
    y0 = -total / 2.0
    for i in range(n):
        y = y0 + i * (board_w + gap) + board_w / 2.0
        add_box(bm, (0, y, COUNTER_H + BOARD_T / 2), (LEN, board_w, BOARD_T), PLANKS)


def rope_from_curve(bm, points, radii, radius, mat_index, bevel_res=2, use_caps=True):
    """Build a genuinely round, smooth rope strand through `points` using a
    Blender curve + bevel (the native way to loft a round tube), then merge
    its evaluated mesh into the working bmesh. Round 2-4 all built the tie
    out of straight `add_beam`/rod segments -- even with a round N-gon
    cross-section, a CHAIN of short straight segments still reads as a
    string of linked hardware pieces (visible facet kinks at every joint).
    A curve's native bevel interpolates the profile smoothly along the
    spline instead of faceting at each point, which is what actually reads
    as a continuous strand of cord. `radii` is a per-point multiplier on
    `radius` (1.0 = full thickness), used to taper the tail to a thin end."""
    curve = bpy.data.curves.new("_rope_tmp", 'CURVE')
    curve.dimensions = '3D'
    spline = curve.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for i, p in enumerate(points):
        spline.points[i].co = (p[0], p[1], p[2], 1.0)
        spline.points[i].radius = radii[i]
    curve.bevel_depth = radius
    curve.bevel_resolution = bevel_res
    curve.use_fill_caps = use_caps
    curve.resolution_u = 1  # POLY spline -- no extra interpolation between our own points
    obj = bpy.data.objects.new("_rope_tmp_obj", curve)
    bpy.context.collection.objects.link(obj)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(eval_obj)
    before = set(bm.faces)
    bm.from_mesh(mesh)
    for f in bm.faces:
        if f not in before:
            f.material_index = mat_index
    bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.meshes.remove(mesh)
    bpy.data.curves.remove(curve)


def add_rope_wrap(bm, pole_x, attach_z, canvas_mat, rope_mat, pole_r=0.03, seed=1,
                   cam_azimuth=-math.pi / 4):
    """A tied lashing where the canvas end wraps the canopy pole. Round 4
    gave two near-identical uniform stacked rings with no tail -- the
    builder checked "does it read as rope" and saw intent, not pixels. R5
    fixlist demands COUNTABLE properties, so this rebuild hand-sets the
    three wrap radii (not random ranges that can converge to near-identical
    values), forces a genuine depth crossing between two wraps via an
    angle-modulated radius (guaranteed, not hoped-for), and ends in a free
    tail long enough to be measured against the pole diameter."""
    rnd = random.Random(seed)
    # gathered canvas: irregular bunched fabric pulled toward the pole -- a
    # handful of unevenly sized, unevenly spaced lobes, not a uniform ring of
    # identical washers.
    n_lobes = 4
    gather_h = 0.15
    for i in range(n_lobes):
        a = 2 * math.pi * i / n_lobes + rnd.uniform(-0.3, 0.3)
        lobe_r = pole_r + rnd.uniform(0.014, 0.030)
        h = gather_h * rnd.uniform(0.7, 1.15)
        cx, cy = pole_x + lobe_r * math.cos(a), lobe_r * math.sin(a)
        top_r = rnd.uniform(0.012, 0.020)
        bot_r = rnd.uniform(0.006, 0.012)
        z0 = attach_z + rnd.uniform(-0.02, 0.015)
        add_cyl(bm, (cx, cy, z0), top_r, bot_r, h, canvas_mat, segments=5)

    rope_w = 0.011
    z_top = attach_z + gather_h * 0.08

    # -- fixlist 1a: THREE wrap radii, hand-set so each pair differs by
    # >=20% of the pole diameter (2*pole_r = 0.06 m) as literally countable
    # loop widths: 0.048 / 0.082 / 0.064 m -> pairwise deltas of 0.034 (57%),
    # 0.018 (30%), 0.016 (27%) of pole diameter.
    # r5 2nd pass: the first z-spacing (0.02/0.045/0.078 m) plus large tilt
    # amplitudes (0.45/-0.55/0.30 * radius) made the vertical bands overlap
    # everywhere, not just at the designed crossing -- the three wraps blurred
    # into one continuous helix (only 2 loops were actually countable in the
    # render). Wider z spacing + smaller tilt keeps the three rings visually
    # SEPARATE, so the one designed crossing (the r2 amplitude bump, below)
    # reads as a distinct event rather than the whole thing looking fused.
    r1_base, tilt1, z1 = pole_r + 0.055, 0.18, z_top - 0.005
    span1 = math.radians(300)
    # crossing wrap 2 in front of / behind wrap 1 -- phase set so the peak
    # of its radius bulge (below) faces the tie camera (azimuth ~-45 deg
    # from the pole), not hidden around the back.
    phase1 = cam_azimuth - span1 / 2.0
    r2_base, tilt2, z2 = pole_r + 0.010, -0.20, z_top - 0.065
    span2 = math.radians(320)
    phase2 = phase1 + math.radians(35)
    crossing_center = phase1 + span1 * 0.5  # faces the camera
    r2_amp = 0.052  # (base+amp)=0.092 > r1_base=0.085 -- radius order swaps at the crossing angle only
    r3_base, tilt3, z3 = pole_r + 0.032, 0.15, z_top - 0.125
    span3 = math.radians(260)
    # r5 3rd pass: chaining phase3 off phase2's END put wrap 3's arc on the
    # BACK of the pole (18-278 deg vs a ~317 deg camera azimuth) -- only a
    # tiny sliver was visible, not a countable third loop. End wrap 3's arc
    # AT the camera azimuth instead, so its full loop -- and the knot/tail
    # that departs from its end -- both face the lens.
    phase3 = cam_azimuth - span3

    def build_wrap_pts(r_of_a, phase, span, z_center, tilt, n_seg=22):
        pts = []
        for i in range(n_seg + 1):
            t = i / n_seg
            a = phase + span * t
            r = r_of_a(a)
            z = z_center + math.sin(a - phase) * tilt * r
            pts.append((pole_x + r * math.cos(a), r * math.sin(a), z))
        return pts

    pts1 = build_wrap_pts(lambda a: r1_base, phase1, span1, z1, tilt1)
    pts2 = build_wrap_pts(lambda a: r2_base + r2_amp * math.cos(a - crossing_center),
                           phase2, span2, z2, tilt2)
    pts3 = build_wrap_pts(lambda a: r3_base, phase3, span3, z3, tilt3)
    radii1 = [1.0] * len(pts1)
    radii2 = [1.0] * len(pts2)
    radii3 = [1.0] * len(pts3)

    # fixlist 1c: free tail, departing the wraps and drooping under gravity.
    # End-to-end length from the departure point to the tip is ~0.19 m,
    # comfortably over the 2x-pole-diameter target (0.12 m), and short
    # enough to stay in the same tie-camera crop (widened slightly below).
    # r5 2nd pass: the first version drifted the tail toward +x,+y, which
    # put it BEHIND the pole from the tie camera's viewpoint (camera sits at
    # x=pole_x+0.52, y=-0.50) -- occluded, invisible in the render. Swing it
    # toward the camera instead (+x away from pole centre, -y toward the
    # lens) so it hangs clear and visible while still dropping under gravity.
    tail0 = pts3[-1]
    tail1 = (tail0[0] + 0.050, tail0[1] - 0.030, tail0[2] - 0.080)
    tail2 = (tail1[0] + 0.030, tail1[1] - 0.020, tail1[2] - 0.065)
    tail3 = (tail2[0] + 0.015, tail2[1] - 0.010, tail2[2] - 0.045)
    tail_radii = [0.85, 0.6, 0.35]

    rope_from_curve(bm, pts1, radii1, rope_w, rope_mat, bevel_res=2)
    rope_from_curve(bm, pts2, radii2, rope_w, rope_mat, bevel_res=2)
    rope_from_curve(bm, pts3 + [tail1, tail2, tail3], radii3 + tail_radii,
                     rope_w, rope_mat, bevel_res=2)

    # knot bulge at the point the tail leaves the wraps -- kept as its own
    # cluster, NOT merged into the wrap geometry, so the tail's departure
    # point is visible. r4's icospheres (subdivisions=1, flat-shaded) read
    # as a faceted crystal/gem, not a knot -- smooth-shade this cluster.
    before = set(bm.faces)
    for i in range(3):
        off = (rnd.uniform(-0.012, 0.012), rnd.uniform(-0.012, 0.012), rnd.uniform(-0.010, 0.010))
        kr = rope_w * rnd.uniform(1.2, 1.6)
        add_sphere(bm, (tail0[0] + off[0], tail0[1] + off[1], tail0[2] + off[2]),
                   kr, rope_mat, subdivisions=2)
    for f in bm.faces:
        if f not in before:
            f.smooth = True


def sim_canopy_sheet(pole_x, y_half, attach_z, support_x, n_steps_x=26, n_steps_y=5,
                      frames=60):
    """r7 TECHNIQUE CHANGE (blender/fixlists/B1-r7.md): the canopy was a
    hand-modelled sine/cell sag -- a lathe-style function, same defect class
    as the sack body, and the r6 judge read it as sheet-metal/origami with
    no curve anywhere. This builds a flat quad grid, pins the FULL-WIDTH
    edge at each pole (the canvas is genuinely clamped there) and only the
    CENTRELINE vertex at the 3 interior ridge ties (a point grommet, not a
    seam), then lets gravity sag it. Returns the baked, already-deformed
    mesh object -- thickness/hem/grommets are added by the caller."""
    scene = bpy.context.scene
    bm = bmesh.new()
    xs = [-pole_x + (2 * pole_x) * i / n_steps_x for i in range(n_steps_x + 1)]
    ys = [-y_half + (2 * y_half) * j / n_steps_y for j in range(n_steps_y + 1)]
    ny = len(ys)
    grid = [[bm.verts.new((x, y, attach_z)) for y in ys] for x in xs]
    for i in range(n_steps_x):
        for j in range(n_steps_y):
            bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
    mesh = bpy.data.meshes.new("_canopy_sheet_tmp")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("_canopy_sheet_tmp", mesh)
    bpy.context.collection.objects.link(obj)

    vg = obj.vertex_groups.new(name="Pin")
    pin_idx = []
    j_centre = min(range(ny), key=lambda j: abs(ys[j]))
    for i, x in enumerate(xs):
        is_pole = abs(x + pole_x) < 1e-6 or abs(x - pole_x) < 1e-6
        is_interior = any(abs(x - sx) < 1e-6 for sx in support_x[1:-1])
        if is_pole:
            for j in range(ny):
                pin_idx.append(i * ny + j)
        elif is_interior:
            pin_idx.append(i * ny + j_centre)
    vg.add(pin_idx, 1.0, 'REPLACE')

    cloth_mod = obj.modifiers.new("Cloth", 'CLOTH')
    cs = cloth_mod.settings
    cs.quality = 8
    cs.mass = 0.15
    cs.tension_stiffness = 30
    cs.compression_stiffness = 4
    cs.shear_stiffness = 8
    cs.bending_stiffness = 3
    cs.vertex_group_mass = "Pin"
    cs.pin_stiffness = 1.0
    coll = cloth_mod.collision_settings
    coll.distance_min = 0.002

    # r7: a bare gravity sag between symmetric pins settles perfectly
    # mirror-symmetric in Y -- real canvas ripples unevenly. A weak
    # turbulence field breaks that symmetry so the free edges wobble.
    bpy.ops.object.effector_add(type='TURBULENCE', location=(0, 0, attach_z - 0.3))
    turb = bpy.context.active_object
    turb.field.strength = 0.5
    turb.field.size = 0.5
    turb.field.flow = 0.4
    turb.field.noise = 2.0

    scene.frame_start = 1
    scene.frame_end = frames
    scene.frame_set(1)
    for f in range(1, frames + 1):
        scene.frame_set(f)

    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    baked_mesh = bpy.data.meshes.new_from_object(ev)
    baked_obj = bpy.data.objects.new("_canopy_baked", baked_mesh)
    baked_obj.matrix_world = obj.matrix_world.copy()
    bpy.context.collection.objects.link(baked_obj)

    # pin verify: the pole-edge + interior-centre pins must not have moved.
    before = [grid_pt for grid_pt in ((x, y, attach_z) for i, x in enumerate(xs) for y in ys)]
    max_delta = 0.0
    for idx in pin_idx:
        bx, by, bz = before[idx]
        av = baked_mesh.vertices[idx].co
        d = ((av.x - bx) ** 2 + (av.y - by) ** 2 + (av.z - bz) ** 2) ** 0.5
        max_delta = max(max_delta, d)
    print(f"[canopy] PIN VERIFY max delta = {max_delta:.6f} m "
          f"({'OK' if max_delta < 0.001 else 'FAIL -- pin moved'})")

    bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.objects.remove(turb, do_unlink=True)
    return baked_obj, xs, ys, ny


def build_canopy(bm):
    """A continuous swept, sagging canvas sheet with real thickness (round 2
    rebuild -- the flat unrotated panel segments used before left visible
    seams and were the source of the black-rod render artifact the judge
    flagged; a single swept surface has neither problem).

    r6 fixlist 2a REBUILD: the single-span sine sag read as "a rigid moulded
    panel", not cloth -- one smooth dip end to end. This version sags the
    canvas in 4 separate catenary-like cells between 5 support points (the
    2 poles + 3 interior ridge tie points) -- each cell returns to baseline
    at its own support, so 4 distinct dips are visible instead of one
    continuous curve. The two long free edges get a rolled hem bead with
    real thickness, and the 3 interior tie points get a proud grommet
    button, both integrated directly into the sheet's own vertex grid
    (r6 2nd pass: separate rope-curve objects for these, even at a cheap
    point count, cost 200-400 tris each once this object's mesh-wide Bevel
    modifier -- angle_limit=80 deg, see build() -- added its own chamfers on
    top; a 132-tri headroom on an 8,000 budget cannot absorb that. Folding
    the hem/grommet geometry into the sheet's existing faces instead of
    spawning new curve objects keeps the added cost to the sheet's own
    per-vertex rate, not a separate part's fixed overhead)."""
    pole_h = 2.1
    pole_x = LEN / 2.0 + 0.08
    attach_z = pole_h - 0.10   # canvas end wraps the pole BELOW its tip
    for sx in (-1, 1):
        x = sx * pole_x
        add_cyl(bm, (x, 0, pole_h / 2), 0.03, 0.03, pole_h, PLANKS, segments=8)
        # socket CLAMP where the pole meets the trestle head (round 3: a bare
        # cube read as a placeholder block, not a fitting) -- a collar ring
        # around the pole, a flat backing plate against the trestle head, and
        # two proud bolt nubs clamping them together.
        add_cyl(bm, (x, 0, COUNTER_H + 0.03), 0.055, 0.055, 0.09, IRON, segments=10)
        add_box(bm, (x, 0.10, COUNTER_H - 0.01), (0.12, 0.03, 0.16), IRON)
        for bz in (COUNTER_H - 0.06, COUNTER_H + 0.06):
            add_cyl(bm, (x, 0.10, bz), 0.018, 0.018, 0.10, IRON, segments=8, axis='y')
        # tie wraps (r4 fixlist): a continuous curved rope strand wound
        # irregularly around the pole -- see add_rope_wrap docstring. Each
        # pole gets its own seed so the two ties are distinct wraps, not
        # mirrored clones of the same geometry.
        # cam_azimuth: the tie camera (render_pass) sits at pole_x+0.45,-0.42
        # relative to the +x pole -- point the designed depth-crossing (see
        # add_rope_wrap) at that bearing so it actually faces the lens.
        az = math.atan2(-0.42, 0.45)
        add_rope_wrap(bm, x, attach_z, PLASTER, IRON, seed=1 if sx < 0 else 2,
                       cam_azimuth=az)

    N_SUPPORTS = 5   # 2 poles + 3 interior tie points -- 4 sag cells between them
    support_x = [-pole_x + (2 * pole_x) * i / (N_SUPPORTS - 1) for i in range(N_SUPPORTS)]
    y_half = 0.55

    # r7 TECHNIQUE CHANGE: sim the sheet instead of hand-modelling a sine/
    # cell sag (see sim_canopy_sheet's docstring). The catenary sag is now a
    # solver output, not an authored curve.
    baked_obj, xs, ys, ny = sim_canopy_sheet(pole_x, y_half, attach_z, support_x)
    vs = baked_obj.data.vertices

    # Hem bead: built from the SIM'S OWN boundary rows (undecimated, so it
    # follows whatever ripple the solver actually produced), using the same
    # rope-curve+bevel technique already proven for the pole tie wraps above
    # (round cross-section -- cheap under this object's 80 deg Bevel
    # modifier, unlike a sharp-cornered part; see add_rope_wrap's docstring).
    # r6's 0.010 m bead read as a knife edge and scored ABSENT -- this one is
    # more than double that.
    # r7 2nd pass: a hem curve sampled at every grid column (41 points) with
    # bevel_res=3 cost ~1,280 tris for the two edges combined -- more than
    # the whole rest of the canopy rebuild. The catenary + ripple the solver
    # produced is low-frequency; every 3rd column is still plenty to trace
    # it, and bevel_res=2 (an octagon, still round enough to read as rolled
    # cord under the 80 deg Bevel modifier) roughly halves the remaining cost.
    HEM_R = 0.024
    for j_edge in (0, ny - 1):
        pts = [tuple(vs[i * ny + j_edge].co) for i in range(0, len(xs), 3)]
        if (len(xs) - 1) % 3 != 0:
            pts.append(tuple(vs[(len(xs) - 1) * ny + j_edge].co))
        rope_from_curve(bm, pts, [1.0] * len(pts), HEM_R, PLASTER, bevel_res=2)

    # 3 ridge grommets at the interior supports, at the sim's own settled z
    # (== attach_z there, since those rows are pinned -- verified above).
    j_centre = min(range(ny), key=lambda j: abs(ys[j]))
    for x in support_x[1:-1]:
        i_closest = min(range(len(xs)), key=lambda i: abs(xs[i] - x))
        gz = vs[i_closest * ny + j_centre].co.z
        add_cyl(bm, (x, 0, gz + 0.008), 0.020, 0.020, 0.014, IRON, segments=5)

    # Sheet thickness: Solidify (no zero-thickness plane) roughly doubles the
    # face count, so decimate the flat single-surface drape FIRST, leaving
    # deliberate headroom for the doubling plus the hem/grommets above --
    # measured against the batch's actual remaining budget in build().
    raw_tris = sum(len(p.vertices) - 2 for p in baked_obj.data.polygons)
    print(f"[canopy] raw sim sheet tris (pre-decimate, pre-solidify): {raw_tris}")
    target_pre_solidify = 420
    bpy.context.view_layer.objects.active = baked_obj
    if raw_tris > target_pre_solidify:
        dec = baked_obj.modifiers.new("Decimate", 'DECIMATE')
        dec.decimate_type = 'COLLAPSE'
        dec.ratio = target_pre_solidify / max(raw_tris, 1)
        bpy.ops.object.modifier_apply(modifier="Decimate")
    sol = baked_obj.modifiers.new("Solidify", 'SOLIDIFY')
    sol.thickness = 0.018
    sol.offset = -1.0
    sol.use_rim = True
    bpy.ops.object.modifier_apply(modifier="Solidify")
    print(f"[canopy] sheet tris after decimate+solidify: "
          f"{sum(len(p.vertices) - 2 for p in baked_obj.data.polygons)}")

    for p in baked_obj.data.polygons:
        p.material_index = PLASTER
    bm.from_mesh(baked_obj.data)
    bpy.data.objects.remove(baked_obj, do_unlink=True)


def build():
    clear_scene()
    bm = bmesh.new()
    for x0 in (-LEN / 2 + 0.18, LEN / 2 - 0.18):
        build_trestle(bm, x0)
    build_top_boards(bm)
    build_canopy(bm)
    # real produce crates (round 2: the placeholder corner-post boxes are
    # replaced with the actual crate geometry, embedded without nails to
    # protect the stall's own tri budget -- they're invisible at this scale)
    counter_top = COUNTER_H + BOARD_T
    add_crate(bm, origin=(-0.55, 0.0, counter_top), scale=0.55, with_nails=False,
              plank_idx=PLANKS, iron_idx=IRON)
    add_crate(bm, origin=(0.15, -0.15, counter_top), scale=0.45, with_nails=False,
              plank_idx=PLANKS, iron_idx=IRON)
    obj = new_mesh_object("stall", bm, material_names=MAT_NAMES)
    # angle_limit raised to 80 deg (from COMMON's 35 deg default): the new
    # round-cross-section rope rods (hex/pentagon facets, ~60-72 deg dihedral)
    # already read as smooth cord and don't need a chamfer loop added on top
    # of every facet edge -- at the default 35 deg threshold the bevel
    # modifier was adding one on every rod segment, which is what pushed the
    # tri count to ~8,760 (over the 8k prop budget) for a feature that's
    # already round. Genuine hard corners (boards, X-cross beams, boxes,
    # ~90 deg dihedral) stay above 80 deg and still get their light-catching
    # bevel.
    add_bevel(obj, width=0.006, segments=1, angle_limit=math.radians(80))
    apply_all_transforms(obj)
    # r7 safety net: the canopy's actual added cost (sim grid + hem curves +
    # grommets, all measured at build time by sim_canopy_sheet's prints) is
    # harder to predict exactly than a hand-authored sheet was -- if the
    # evaluated total (Bevel included) still overshoots the 8,000 prop
    # budget, decimate the WHOLE object down to budget rather than guess at
    # the sheet's share in advance. Re-measured and printed either way.
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    ev_mesh = ev.to_mesh()
    tri_count = sum(len(p.vertices) - 2 for p in ev_mesh.polygons)
    ev.to_mesh_clear()
    print(f"[stall] evaluated tri count (with Bevel): {tri_count}")
    attempt = 0
    while tri_count > 7800 and attempt < 4:
        attempt += 1
        dec = obj.modifiers.new(f"BudgetDecimate{attempt}", 'DECIMATE')
        dec.decimate_type = 'COLLAPSE'
        dec.ratio = min(0.95, 7500.0 / tri_count)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=f"BudgetDecimate{attempt}")
        dg = bpy.context.evaluated_depsgraph_get()
        ev = obj.evaluated_get(dg)
        ev_mesh = ev.to_mesh()
        tri_count = sum(len(p.vertices) - 2 for p in ev_mesh.polygons)
        ev.to_mesh_clear()
        print(f"[stall] evaluated tri count after budget decimate pass {attempt}: {tri_count}")
    if tri_count > 8000:
        print(f"[stall] WARNING: still over budget after {attempt} decimate passes: {tri_count}")
    smart_uv(obj)
    return obj


def render_pass():
    setup_clay_render()
    add_ground_plane(size=6.0)
    add_sun()
    # r4 fixlist: "Zero pure-black regions allowed" -- the enclosed pocket
    # behind the X-crossing peg (stall_detail.png) measured true RGB(0,0,0)
    # at COMMON's default fill energy (0.5), fully occluded from both suns.
    # Bumped locally (stall only, not touching COMMON's shared default used
    # by every other asset) so bounce light reaches into that crevice.
    add_fill_sun(energy=1.6)
    # round 3: cam_face/cam_34 cropped the pole tips + tie wraps (z=1.95-2.1)
    # -- at lens 45 on a 960x540 frame the vertical half-FOV is only ~12.7 deg,
    # so a target of z=1.1 at 3.6 m tops out near z=1.9. Retarget higher and
    # pull back so the whole canopy (poles to 2.1 m) is in frame.
    tgt = mathutils.Vector((0, 0, 1.3))
    add_camera("cam_face", (0, -4.3, 1.7), tgt, lens=45)
    render_to(os.path.join(RENDERS_DIR, "stall_face.png"))
    add_camera("cam_34", (3.1, -3.3, 1.7), tgt, lens=45)
    render_to(os.path.join(RENDERS_DIR, "stall_34.png"))
    # detail: re-aimed at the ACTUAL X-crossing peg (trestle at x=LEN/2-0.18).
    # r6: peg_z was COUNTER_H*0.42=0.378, which is NOT where the legs (top_y
    # 0.42/bot_y 0.14, z 0-0.88) actually cross in Y -- see build_trestle's
    # r6 comment. Traced stall_34's true-black pixels to this exact bug via
    # a Python raycast against the saved .blend: the peg/washers were
    # covering empty air 0.158 m above the real joint, leaving the two
    # crossing beams' interpenetration seam uncovered and, from a narrow
    # range of angles, sealed with zero light path (confirmed by testing up
    # to 128 samples, a second fill light, and 5x world strength -- none
    # changed the pixel count, because there was no aperture to reach at
    # all). Fixing cross_z in build_trestle to the true intersection also
    # moves the peg here -- this camera target follows it so cam_detail
    # keeps framing the actual joint instead of the old wrong height.
    # r6 fixlist 2b: RE-AIMED. The r5 crop (0.15, -0.85, lens=50) sat too
    # close and too square-on to the plate face -- only one flat face with
    # its bolts was visible, no second leg, which is a failed render (the
    # frame's job is to show the cross-halved joint, not just the bracket
    # bolted over it). Pulled back to y=-1.3 and widened to lens=38, target
    # moved to the strap-plate's own centre (plate_z=0.28, matching
    # build_trestle) so BOTH crossing legs are visible passing through the
    # plate in one frame, not just the plate's front face.
    # r6 2nd pass: the first re-aim (0.05, -1.3) was too CENTRED on the
    # trestle's own X=x0 plane -- both legs live at the same world X, so a
    # camera looking almost straight down that plane's normal (small X
    # offset relative to its Y distance) foreshortens the X-crossing into a
    # single near-vertical smear, exactly like the failed r5 crop. The wide
    # shots read the X because they view it OBLIQUELY (camera at x=0,
    # trestle at x=+-1.02, y=-4.3 -- a large X-offset-to-distance ratio).
    # Widen the X offset here to preserve that obliqueness at detail range.
    peg_x = LEN / 2 - 0.18
    plate_z = 0.28
    add_camera("cam_detail", (peg_x + 0.24, -1.15, plate_z + 0.02),
               mathutils.Vector((peg_x, 0, plate_z)), lens=40)
    render_to(os.path.join(RENDERS_DIR, "stall_detail.png"))
    # round 3 re-fix: dedicated close-up on the pole-head tie wrap -- at
    # face/34 distance the lashing is only ~20px, not enough to evidence
    # "IN FRAME" per the fixlist, so this is a 4th delivered frame.
    pole_x = LEN / 2.0 + 0.08
    attach_z = 2.1 - 0.10
    # r5: widened/retargeted down + pulled back slightly (was target z-0.05,
    # pos z+0.02) so the new free tail (drooping ~0.19 m below the wraps) is
    # fully in frame, not cropped out as it was when the tail existed but
    # dropped straight out of the bottom of the r4 crop.
    add_camera("cam_tie", (pole_x + 0.52, -0.50, attach_z + 0.00),
               mathutils.Vector((pole_x, 0, attach_z - 0.14)), lens=48)
    render_to(os.path.join(RENDERS_DIR, "stall_tie.png"))
    # r7: cam_hem was dropped when this function was rewritten for the cloth
    # sim canopy, leaving the r6 zigzag-panel stall_hem.png on disk as stale
    # evidence of the OLD geometry. Re-added, framed on the near long hem
    # edge (y=-0.55) centred on the middle interior support (x=0) and pulled
    # back/widened just enough to keep all 3 interior grommets
    # (x=-0.64, 0, 0.64) in one frame, per the fixlist.
    add_camera("cam_hem", (0.0, -1.85, 2.75), mathutils.Vector((0.0, -0.30, 1.95)), lens=38)
    render_to(os.path.join(RENDERS_DIR, "stall_hem.png"))


if __name__ == "__main__":
    obj = build()
    bpy.ops.wm.save_as_mainfile(filepath="C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B1/stall.blend")
    if "--quick" in sys.argv:
        add_ground_plane(size=6.0)
        add_camera("cq", (3.1, -3.3, 1.7), mathutils.Vector((0, 0, 1.3)), lens=45)
        quick_check(os.path.join(RENDERS_DIR, "stall_quick.png"), res=800)
        peg_x, peg_z = LEN / 2 - 0.18, COUNTER_H * 0.42
        add_camera("cq2", (peg_x + 0.55, -0.55, peg_z + 0.15),
                   mathutils.Vector((peg_x, 0, peg_z)), lens=55)
        quick_check(os.path.join(RENDERS_DIR, "stall_quick_peg.png"), res=800)
        pole_x = LEN / 2.0 + 0.08
        attach_z = 2.1 - 0.10
        add_camera("cq3", (pole_x + 0.45, -0.42, attach_z + 0.02),
                   mathutils.Vector((pole_x, 0, attach_z - 0.05)), lens=55)
        quick_check(os.path.join(RENDERS_DIR, "stall_quick_tie.png"), res=800)
    else:
        render_pass()
        export_glb([obj], os.path.join(MODELS_DIR, "stall.glb"))
    print("STALL DONE")
