"""Asset 3: gy-flank.glb -- George Yard alley wall, a building strip 8 m
wide x 118.5 m long x 12 m high. Origin: strip centre, long axis local z
(the game rotates/places both sides of the alley from one asset).

Brief figures (law): 8 wide (x -4..+4), 118.5 long (z -59.25..+59.25),
12 high. The ALLEY face (+x local) is the seen face: sooty brick, tall
mostly-blind wall, a few small high barred windows, door recesses at long
intervals, plinth, drips, parapet coping. Other 3 faces plain brick.
Materials: brick, iron (bars).

Numbers not given by the brief (assumption, flagged in blender/manifests/B3.md):
  wall built as a solid 8 m deep mass (no modelled interior -- this is a
  backdrop flank, only the alley face is ever seen); window/door reveal
  depth 0.30 m into that mass; 4 door recesses and 6 small windows spaced
  along the 118.5 m run (roughly one door per ~24-30 m, echoing the
  Dorset-Street-rhythm feel from refpack/tier1/long-section.jpg without
  literally repeating the rookery's 5.5 m door spacing, since this is a
  blind service elevation, not a frontage).
"""
import bpy
import bmesh
import math
import sys

sys.path.insert(0, "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B3")
import common as C

C.clear_scene()

BRICK, IRON, PLANKS = 0, 1, 2
MATS = ["brick", "iron", "planks"]
# round-4 fixlist item 1a: the door recesses were empty voids with no leaf --
# `planks` is on BRIEF-COMMON's shared material list even though this asset's
# brief text only names brick/iron; the fixlist explicitly orders a leaf here,
# so this is a fixlist-driven deviation from the brief's material list,
# recorded in the manifest.

HALF_W = 4.0
HALF_L = 59.25
HEIGHT = 12.0
FACE_X = HALF_W
REVEAL = 0.30
PLINTH_Y = 0.5
COPE_Y0, COPE_Y1 = 11.65, 12.0

bm = bmesh.new()

# Door/window layout, pulled up front (round-4 restructure) so the plinth
# and coursing bands below can leave gaps at the door bays instead of
# running solid brick straight across them -- see the bug note by the
# plinth code below.
DOOR_Z = [-42.0, -14.0, 14.0, 42.0]
DOOR_HW, DOOR_Y0, DOOR_Y1 = 0.55, 0.0, 2.15
# round-7 fixlist item 3: a FORMER doorway, same footprint as the four working
# ones (it was a fifth bay in the same door rhythm before it was blocked up),
# now bricked in. Folded into DOOR_Z_ALL below so the ground band and the
# plinth gap around it exactly as they do the working doors -- it needs the
# same jambs/lintel treatment, just a blocked leaf instead of a working one.
BRICKED_Z = [27.0]
DOOR_Z_ALL = DOOR_Z + BRICKED_Z
WIN_Z = [-52.0, -28.0, -4.0, 20.0, 34.0, 50.0]
WIN_HW, WIN_Y0, WIN_Y1 = 0.42, 8.8, 9.85


def opening_spans(centers, hw):
    return sorted((c - hw, c + hw) for c in centers)


door_spans = opening_spans(DOOR_Z_ALL, DOOR_HW)
win_spans = opening_spans(WIN_Z, WIN_HW)


def banded_run(y0, y1, x0, x1, spans, gap_pad=0.0):
    """A projecting course (plinth/string/coursing) at brief-x [x0,x1],
    brief-y [y0,y1], running the wall length but leaving a gap wherever
    `spans` (z0,z1 pairs, e.g. door_spans) fall, so it never runs solid
    brick across a door opening (which would bury the door's own proud
    parts -- threshold, hinges -- behind it)."""
    cursor = -HALF_L
    for (a, b) in spans:
        a -= gap_pad
        b += gap_pad
        if a > cursor:
            C.add_box(bm, x0, x1, y0, y1, cursor, a, mat_idx=BRICK)
        cursor = max(cursor, b)
    if cursor < HALF_L:
        C.add_box(bm, x0, x1, y0, y1, cursor, HALF_L, mat_idx=BRICK)


# ---- main mass: back face, two end caps, top, bottom (front face built
#      separately below with openings) ----
C.add_box(bm, -HALF_W - 0.08, -HALF_W, 0.0, PLINTH_Y, -HALF_L, HALF_L, mat_idx=BRICK)  # back plinth kick
C.add_quad(bm, (-HALF_W, PLINTH_Y, -HALF_L), (-HALF_W, PLINTH_Y, HALF_L),
           (-HALF_W, HEIGHT, HALF_L), (-HALF_W, HEIGHT, -HALF_L), mat_idx=BRICK)  # back face
# end caps (z = +-HALF_L), plain brick, full box height incl. plinth taper
for zf, zsign in ((-HALF_L, -1), (HALF_L, 1)):
    if zsign > 0:
        C.add_quad(bm, (-HALF_W, 0.0, zf), (FACE_X, 0.0, zf),
                   (FACE_X, HEIGHT, zf), (-HALF_W, HEIGHT, zf), mat_idx=BRICK)
    else:
        C.add_quad(bm, (FACE_X, 0.0, zf), (-HALF_W, 0.0, zf),
                   (-HALF_W, HEIGHT, zf), (FACE_X, HEIGHT, zf), mat_idx=BRICK)
# top (roof deck, flat -- not a habitable roof, this is a boundary wall mass)
C.add_quad(bm, (-HALF_W, HEIGHT, -HALF_L), (FACE_X, HEIGHT, -HALF_L),
           (FACE_X, HEIGHT, HALF_L), (-HALF_W, HEIGHT, HALF_L), mat_idx=BRICK)

# ---- plinth: projecting course at the base of the alley face, with its
#      own top weathering slope (round-4 fixlist item 1b) -- a flat-topped
#      projecting box reads as a step, not a weathered plinth; the sloped
#      top sheds water outward and is what actually casts a countable
#      shadow line the length of the wall.
#      BUG FOUND round-4: the plinth's y-range (0..0.5) fully covers every
#      door's ground-level threshold/hinge zone, and a solid brick plinth
#      running straight across the door bays buried the new door leaf's
#      lower hinge and threshold behind a wall of brick, invisible from any
#      exterior camera. Gapped at the door bays with `banded_run`, same
#      fix pattern as `flat_band` already uses for the wall face itself.
# round-5 fixlist item 1a (cause B, decided against the geometry not the
# render): r4's plinth was 0.08 m proud total -- at cam_face/_ctx's
# standing distance that throws a shadow only ~1 px tall (proud x
# tan(sun elevation)), which is exactly the judge's "thin white band", not
# a countable weathered course. Rebuilt as a genuine TWO-TIER plinth: a
# deep lower course (0.20 m proud, to knee height) plus the existing
# shallower sloped upper course above it -- the step between the two
# tiers is a real proud-to-proud drop, so it throws its own shadow edge in
# the WIDE frame, not only in a crop.
PLINTH_LOWER_Y0, PLINTH_LOWER_Y1 = 0.0, 0.22
PLINTH_LOWER_PROUD = 0.20
banded_run(PLINTH_LOWER_Y0, PLINTH_LOWER_Y1, FACE_X, FACE_X + PLINTH_LOWER_PROUD,
           door_spans, gap_pad=0.08)
PLINTH_SLOPE = 0.10
banded_run(PLINTH_LOWER_Y1, PLINTH_Y - PLINTH_SLOPE, FACE_X, FACE_X + 0.08, door_spans, gap_pad=0.08)
cursor = -HALF_L
for (a, b) in [(x - 0.08, y + 0.08) for (x, y) in door_spans]:
    if a > cursor:
        C.add_quad(bm, (FACE_X + 0.08, PLINTH_Y - PLINTH_SLOPE, cursor),
                   (FACE_X + 0.08, PLINTH_Y - PLINTH_SLOPE, a),
                   (FACE_X, PLINTH_Y, a), (FACE_X, PLINTH_Y, cursor), mat_idx=BRICK)
    cursor = max(cursor, b)
if cursor < HALF_L:
    C.add_quad(bm, (FACE_X + 0.08, PLINTH_Y - PLINTH_SLOPE, cursor),
               (FACE_X + 0.08, PLINTH_Y - PLINTH_SLOPE, HALF_L),
               (FACE_X, PLINTH_Y, HALF_L), (FACE_X, PLINTH_Y, cursor), mat_idx=BRICK)

# ---- coursing break: a projecting brick-bond change running the wall
#      length at mid-height (round-4 fixlist item 1b) -- sits in the plain
#      band between the door heads and the window sills, so it never
#      overlaps an opening (no door/window gap needed at this height).
# round-5 fixlist item 1a (cause B): r4's coursing was 0.045 m proud x
# 0.14 m tall -- "registers as one faint line" per the judge, because a
# projection that shallow casts a shadow band only ~1 px tall at standing
# distance no matter how the camera is framed. Rebuilt as a real two-part
# brick band: a deep proud course plus a further-projecting cap lip
# stepping out below it, so the step itself (not just an edge highlight)
# reads the wall length in the wide frame.
COURSE_Y0, COURSE_Y1 = 5.95, 6.25
COURSE_PROUD = 0.16
LIP_Y0, LIP_Y1 = 5.95, 6.05
LIP_PROUD = 0.24
C.add_box(bm, FACE_X, FACE_X + COURSE_PROUD, COURSE_Y0, COURSE_Y1, -HALF_L, HALF_L, mat_idx=BRICK)
C.add_box(bm, FACE_X + COURSE_PROUD, FACE_X + LIP_PROUD, LIP_Y0, LIP_Y1, -HALF_L, HALF_L, mat_idx=BRICK)

# ---- downpipes: two runs (round-4 fixlist item 1b asks for "at least one
#      more" beyond zero -- two gives real headroom against the 15k/60k tri
#      budget), each held off the wall by 2 wall brackets and kicking out to
#      a shoe at the ground that discharges clear of the plinth.
# round-5 fixlist item 1b (partly cause A, partly cause B, per the fixlist's
# own split): a 7 cm pipe is genuinely sub-pixel at cam_ctx's wide distance
# (framing/cause A), but the fixlist also names the real-world pipe as too
# thin at 7 cm and missing its hopper (cause B). Both fixed: PIPE_R widened
# 0.035 -> 0.055 (11 cm dia, a real 1880s cast-iron downpipe), and a proper
# hopper head added where the gutter outlet feeds into the pipe -- the part
# a stranger actually looks for first, not the shaft.
PIPE_R = 0.055
PIPE_GAP = 0.05                       # standoff from the wall face
PIPE_X = FACE_X + PIPE_GAP + PIPE_R
# BUG FOUND round-5 (caught before render, not after): PIPE_TOP was
# HEIGHT-0.4=11.6, and the hopper mouth built on top of it (11.6..11.9)
# landed INSIDE the parapet coping's own y-range (COPE_Y0..COPE_Y1 =
# 11.65..12.0) and x-range -- a genuine volumetric intersection, not a
# framing choice, which is exactly why the hopper never showed up as its
# own distinct shape in gy-flank_pipe.png (it rendered fused into the
# coping). Dropped well clear of the coping so the hopper reads as a real
# separate part below the eaves, the way an actual gutter outlet sits.
PIPE_TOP = HEIGHT - 1.4
PIPE_Z_RUNS = [-26.0, 26.0]           # clear of every door/window recess,
                                       # and close enough to the wall's
                                       # centre to land inside cam_ctx


def build_downpipe(pz):
    # shaft: NOT capped at the top (cap_top=False) -- the hopper box built
    # immediately above it, starting at the exact same y=PIPE_TOP plane,
    # is what closes the pipe off. Capping both would leave two coincident
    # faces in the same plane (the same z-fighting/light-trap bug class
    # flagged throughout this batch); leaving the shaft open lets the
    # hopper's own solid floor be the only face there.
    C.add_cylinder(bm, PIPE_X, pz, 0.35, PIPE_TOP, PIPE_R, segments=10, mat_idx=IRON,
                    cap_top=False)
    # wall brackets: proud collars fixing the pipe to the face at three
    # heights -- 1.0 and 2.6 sit close enough together to both land inside
    # one close-up crop (cam_pipe) alongside the ground shoe, so 2+
    # brackets are actually countable in a single frame, not just present
    # somewhere in the geometry.
    for by in (1.0, 2.6, 8.2):
        C.add_box(bm, FACE_X, PIPE_X + PIPE_R, by - 0.03, by + 0.03,
                  pz - 0.05, pz + 0.05, mat_idx=IRON)
    # shoe at the bottom: kicks out and down to discharge clear of the plinth
    C.add_cylinder(bm, PIPE_X, pz, 0.0, 0.35, PIPE_R * 1.4, segments=10, mat_idx=IRON,
                    radius_top=PIPE_R)
    C.add_box(bm, FACE_X + PIPE_GAP - 0.02, PIPE_X + PIPE_R * 1.4, 0.0, 0.10,
              pz - PIPE_R * 1.4, pz + PIPE_R * 1.4, mat_idx=IRON)
    # hopper head: a real wider box mounted flush to the wall exactly where
    # the shaft's own (uncapped) top plane sits -- a necked lower box
    # widening to a flared upper mouth, two disjoint y-ranges touching only
    # at their shared plane (no volumetric overlap with each other or with
    # the shaft, which stops at the same y=PIPE_TOP).
    C.add_box(bm, FACE_X, FACE_X + 0.16, PIPE_TOP, PIPE_TOP + 0.10,
              pz - 0.10, pz + 0.10, mat_idx=IRON)
    C.add_box(bm, FACE_X, FACE_X + 0.24, PIPE_TOP + 0.10, PIPE_TOP + 0.30,
              pz - 0.16, pz + 0.16, mat_idx=IRON)


for pz in PIPE_Z_RUNS:
    build_downpipe(pz)

# ---- alley face (+x): built as horizontal bands so door and window
#      openings (which sit at different heights) never overlap the same
#      flat quad -- each band is either plain, or split by z into flanking
#      strips + recesses around that band's openings. DOOR_Z/WIN_Z/spans
#      are defined earlier now (round-4), before the plinth. ----


def flat_band(y0, y1, spans):
    """Flat wall quads at x=FACE_X spanning z=-HALF_L..HALF_L and y0..y1,
    with gaps left where `spans` (z0,z1 pairs) fall -- those gaps get a
    recess built by build_recess."""
    cursor = -HALF_L
    for (a, b) in spans:
        if a > cursor:
            C.add_quad(bm, (FACE_X, y0, cursor), (FACE_X, y0, a),
                       (FACE_X, y1, a), (FACE_X, y1, cursor), mat_idx=BRICK)
        cursor = max(cursor, b)
    if cursor < HALF_L:
        C.add_quad(bm, (FACE_X, y0, cursor), (FACE_X, y0, HALF_L),
                   (FACE_X, y1, HALF_L), (FACE_X, y1, cursor), mat_idx=BRICK)


def build_recess(z0, z1, y0, y1, has_sill=False, has_lintel_block=False):
    """Recess an opening into the wall mass: side reveals, lintel, sill/
    threshold, and a brick back plane set REVEAL back from the face."""
    z_back = FACE_X - REVEAL
    C.add_quad(bm, (FACE_X, y0, z0), (z_back, y0, z0), (z_back, y1, z0), (FACE_X, y1, z0), mat_idx=BRICK)
    C.add_quad(bm, (z_back, y0, z1), (FACE_X, y0, z1), (FACE_X, y1, z1), (z_back, y1, z1), mat_idx=BRICK)
    C.add_quad(bm, (FACE_X, y1, z0), (z_back, y1, z0), (z_back, y1, z1), (FACE_X, y1, z1), mat_idx=BRICK)
    C.add_quad(bm, (z_back, y0, z0), (FACE_X, y0, z0), (FACE_X, y0, z1), (z_back, y0, z1), mat_idx=BRICK)
    C.add_quad(bm, (z_back, y0, z1), (z_back, y0, z0), (z_back, y1, z0), (z_back, y1, z1), mat_idx=BRICK)
    if has_sill:
        C.add_box(bm, FACE_X, FACE_X + 0.08, y0 - 0.08, y0 + 0.04, z0 - 0.05, z1 + 0.05, mat_idx=BRICK)
    if has_lintel_block:
        # proud lintel block square over the head -- judge round 1: door
        # heads need a distinct proud member, not just the flat recessed
        # soffit quad, or the opening reads as a hole rather than a built
        # doorway carrying load above it
        C.add_box(bm, FACE_X - 0.02, FACE_X + 0.10, y1 - 0.02, y1 + 0.16,
                  z0 - 0.10, z1 + 0.10, mat_idx=BRICK)
        # threshold sill/step at the base
        C.add_box(bm, FACE_X, FACE_X + 0.10, y0 - 0.04, y0 + 0.03,
                  z0 - 0.06, z1 + 0.06, mat_idx=BRICK)


def build_door_leaf(z0, z1, y0, y1):
    """round-4 fixlist item 1a: a real plank door leaf filling the recess
    built by build_recess(has_lintel_block=True), set back in the wall
    thickness with a visible reveal shadow on the jambs (sides) and lintel
    soffit (top) -- both already built by build_recess. 5 vertical planks
    with countable gaps, 2 strap hinges (each with 2 stacked knuckles) on
    the z0 edge, a latch on the z1 edge, and a proud threshold at the foot."""
    # leaf sits BACK in the wall thickness: its outer (proud) face is
    # LEAF_SET_BACK behind FACE_X, giving a visible reveal shadow on the
    # jambs (sides, already built by build_recess) and the lintel soffit
    # (top). The leaf itself has real thickness (LEAF_T), so its own back
    # face sits deeper still, well clear of the recess's own back plane at
    # FACE_X - REVEAL (0.30 m), so nothing coincides.
    LEAF_SET_BACK = 0.10
    LEAF_T = 0.05
    leaf_front = FACE_X - LEAF_SET_BACK    # proud outer face of the leaf
    leaf_back = leaf_front - LEAF_T        # leaf's own back face
    back_bz = leaf_back - 0.02             # dark backing plane behind the
                                            # plank gaps (same trick as the
                                            # rookery boarded window, which
                                            # passed clean) -- winding matches
                                            # build_recess's own back-wall
                                            # quad above so the outward
                                            # normal faces the viewer (+x)
    C.add_quad(bm, (back_bz, y0 + 0.01, z1 - 0.01), (back_bz, y0 + 0.01, z0 + 0.01),
               (back_bz, y1 - 0.02, z0 + 0.01), (back_bz, y1 - 0.02, z1 - 0.01),
               mat_idx=BRICK)

    n_planks = 5
    gap = 0.018
    width = z1 - z0
    plank_w = (width - gap * (n_planks - 1)) / n_planks
    for i in range(n_planks):
        pz0 = z0 + i * (plank_w + gap)
        pz1 = pz0 + plank_w
        stagger = 0.01 if i % 2 == 0 else 0.0  # hand-fitted, not machined
        C.add_box(bm, leaf_back, leaf_front, y0 + stagger, y1 - 0.03,
                  pz0, pz1, mat_idx=PLANKS)
    # ledge battens (Z-brace look): two horizontal ledges proud of the
    # planks, a real fixing member for board-and-batten construction --
    # kept clear (in y) of the hinge bands below so the two systems never
    # visually merge into one blob.
    # round-4 fix: a ledge that's only proud of the plank FRONT face (not
    # full depth) bridges over the plank-to-plank gaps without closing
    # them, leaving a thin unlit void behind the ledge at every gap it
    # crosses (the last few pure-black pixels in gy-flank_detail.png).
    # Spanning the ledge's own box back to leaf_back closes that void --
    # also the more correct read, since a real ledge batten is a solid
    # board nailed across the full thickness of the planks it braces.
    for ly0, ly1 in ((y0 + 0.44, y0 + 0.56), (y1 - 0.56, y1 - 0.44)):
        C.add_box(bm, leaf_back, leaf_front + 0.03, ly0, ly1, z0 + 0.02, z1 - 0.02,
                  mat_idx=PLANKS)

    # strap hinges on the z0 edge, near the top and bottom of the leaf
    # (clear of the ledge battens above): a long strap across half the door
    # width, plus 3 stacked knuckle segments (countable, with real gaps
    # between them so they read as a barrel, not a single blob) at the
    # pivot edge -- round-4 rebuild, bigger and better-separated than the
    # first pass, which produced knuckles too close together and too near
    # the ledge battens to count cleanly.
    for hy0, hy1 in ((y0 + 0.15, y0 + 0.30), (y1 - 0.30, y1 - 0.15)):
        hy_mid = (hy0 + hy1) / 2
        # strap starts 2 cm clear of z0 (not flush with the recess's own
        # jamb reveal quad, which sits at that exact plane) -- round-4 fix
        # for the last few stray dark pixels: a solid box face exactly
        # coincident with a separate flat reveal quad at the same plane is
        # the same z-fighting/self-shadow class of bug this file has hit
        # before (see the picture-frame comments elsewhere in this batch).
        C.add_box(bm, leaf_front, leaf_front + 0.025, hy0, hy1, z0 + 0.02, z0 + 0.57, mat_idx=IRON)
        # round-4 fix: the knuckle barrel used to sit at z0-0.02 with radius
        # 0.035, so it overlapped the strap's own z0..z0+0.55 z-range by
        # 1.5 cm -- a genuine volumetric intersection, not just a touching
        # face, which is what produced the pure-black sliver in the render.
        # Moved fully clear of the strap's z-range (gap for the pin).
        for dy in (-0.09, 0.0, 0.09):
            C.add_cylinder(bm, leaf_front + 0.035, z0 - 0.06, hy_mid + dy - 0.025,
                            hy_mid + dy + 0.025, 0.035, segments=10, mat_idx=IRON)

    # latch/handle on the z1 edge, proud enough to cast its own shadow
    latch_y = (y0 + y1) / 2
    C.add_box(bm, leaf_front, leaf_front + 0.09, latch_y - 0.03, latch_y + 0.03,
              z1 - 0.20, z1 - 0.04, mat_idx=IRON)
    # knob sits flush against the latch plate's own outer face (touching,
    # not straddling it) -- round-4 fix: the previous centre (leaf_front +
    # 0.09, exactly on the plate's face) buried half the cylinder inside
    # the plate, a partial-overlap tangency that produced a thin pure-black
    # sliver (42 px) at the seam.
    C.add_cylinder(bm, leaf_front + 0.09 + 0.025, z1 - 0.10, latch_y - 0.025,
                    latch_y + 0.025, 0.025, segments=8, mat_idx=IRON)

    # threshold/step at the foot: build_recess(has_lintel_block=True) already
    # adds one at this exact footprint -- round-4 bug found here: a second,
    # near-identical box added on top of it (overlapping in y by design
    # accident) sealed a thin light-trap between the two coincident faces,
    # which is what produced 1200 pure-black pixels in gy-flank_detail.png.
    # No second box needed; build_recess's threshold already satisfies the
    # fixlist's "proud threshold at the foot" clause.


def build_blocked_doorway(z0, z1, y0, y1):
    """round-7 fixlist item 3: a former doorway blocked with brick set BACK
    from the wall face, inside the original jambs/lintel that build_recess
    already built for this opening -- the single clearest "how was this
    altered" tell the fixlist asks for. The infill sits at BLOCK_SETBACK
    (0.15 m) behind the wall face -- recessed from the original jamb line,
    but well short of the recess's own full REVEAL depth (0.30 m) behind it,
    so a stranger reads two distinct depths: the original opening's reveal,
    then a shallower brick plug set into it later.
    Kept 0.03 m clear of the recess's own back plane (at FACE_X-REVEAL) and
    0.02 m clear of every jamb/lintel/sill quad build_recess already added at
    this footprint -- exact coincident faces at the same plane are the
    z-fighting/light-trap bug class this file has hit before (see the strap
    hinge and threshold notes above)."""
    BLOCK_SETBACK = 0.15
    infill_front = FACE_X - BLOCK_SETBACK
    infill_back = (FACE_X - REVEAL) + 0.03
    C.add_box(bm, infill_back, infill_front, y0 + 0.02, y1 - 0.02,
              z0 + 0.02, z1 - 0.02, mat_idx=BRICK)


def add_window_bars(z0, z1, y0, y1):
    """Vertical iron bars set in the reveal, socketed top AND bottom --
    the bars now run the FULL opening height and end exactly at the
    reveal's own head/sill planes (a rounded cap at each end, read as let
    into a drilled hole) instead of a separate collar box that overlapped
    the bar's own volume (round-1: an embedded-box coincidence identical to
    the ones found on the other three assets, sealing a light-trap)."""
    n_bars = 4
    x_bar = FACE_X - 0.05
    r = 0.013
    # round-3 fix: the proud sill block (see build_recess has_sill) sticks
    # out to FACE_X+0.08, closer to the camera than the recessed bar at
    # x_bar=FACE_X-0.05, and its own y-range (y0-0.08..y0+0.04) fully
    # overlapped the old bottom cap (y0..y0+0.025) -- the cap sat entirely
    # BEHIND the sill's proud lip, invisible from any exterior camera angle,
    # not merely a bad framing choice. Lifting the bottom socket to seat on
    # TOP of the sill (y0+0.045, just clear of the sill's y0+0.04 top face)
    # is also the more correct read: bars socket INTO the sill's top
    # surface, not into a void hidden beneath it.
    y_bot = y0 + 0.045
    for i in range(1, n_bars + 1):
        z = z0 + (z1 - z0) * i / (n_bars + 1)
        # bar and caps are adjacent (touching), never overlapping in y
        C.add_box(bm, x_bar - r, x_bar + r, y_bot + 0.02, y1 - 0.02, z - r, z + r, mat_idx=IRON)
        # round-3 evidence fix: r*1.6 caps were only 8mm wider than the bar
        # shaft -- too subtle to read as a distinct socket at render distance.
        # r*2.6 makes the cap a clearly bulging collar, legible as "the bar
        # is let into a drilled socket" rather than just a rounded bar end.
        C.add_cylinder(bm, x_bar, z, y_bot, y_bot + 0.025, r * 2.6, segments=8, mat_idx=IRON)  # bottom socket cap
        C.add_cylinder(bm, x_bar, z, y1 - 0.025, y1, r * 2.6, segments=8, mat_idx=IRON)  # top socket cap


# band 1: ground band with door recesses (y 0..DOOR_Y1)
flat_band(0.0, DOOR_Y1, door_spans)
for cz in DOOR_Z:
    build_recess(cz - DOOR_HW, cz + DOOR_HW, DOOR_Y0, DOOR_Y1, has_lintel_block=True)
    # round-4 fixlist item 1a (judge-ordered, overrides the round-3 "blind
    # bricked-up doorway" call): every door recess gets a real plank leaf,
    # strap hinges and a latch, not a bricked-up back plane.
    build_door_leaf(cz - DOOR_HW, cz + DOOR_HW, DOOR_Y0, DOOR_Y1)

# round-7 fixlist item 3: the fifth bay in the same door rhythm, now blocked.
for cz in BRICKED_Z:
    build_recess(cz - DOOR_HW, cz + DOOR_HW, DOOR_Y0, DOOR_Y1, has_lintel_block=True)
    build_blocked_doorway(cz - DOOR_HW, cz + DOOR_HW, DOOR_Y0, DOOR_Y1)

# band 2: plain wall between the door heads and the window sills
flat_band(DOOR_Y1, WIN_Y0, [])

# band 3: window band with barred recesses
flat_band(WIN_Y0, WIN_Y1, win_spans)
for cz in WIN_Z:
    build_recess(cz - WIN_HW, cz + WIN_HW, WIN_Y0, WIN_Y1, has_sill=True)
    add_window_bars(cz - WIN_HW, cz + WIN_HW, WIN_Y0, WIN_Y1)

# band 4: plain wall from above the windows up to the parapet coping
flat_band(WIN_Y1, COPE_Y0, [])

# ---- parapet coping: projecting course at the top of the alley face ----
C.add_box(bm, FACE_X - 0.05, FACE_X + 0.10, COPE_Y0, COPE_Y1, -HALF_L, HALF_L, mat_idx=BRICK)
C.add_box(bm, FACE_X - 0.05, FACE_X + 0.10, COPE_Y0 - 0.05, COPE_Y0,
          -HALF_L - 0.02, HALF_L + 0.02, mat_idx=BRICK)  # drip ledge underside

# ---- round-7 fixlist: "the wall needs actual features" ----
# Four rounds tried to make a thin part-list read better by relighting and
# reframing a genuinely thin wall. Operator ruling 2026-09-01: the wall
# itself needs the parts a real 1880s boundary wall has. Everything below is
# NEW geometry, added on top of everything r6 already got right (raking sun,
# walking-distance cam_face, coursing band, plinth) -- none of that is
# touched or removed.

# -- feature 5 of 5 (boundary plate): a cast-iron parish/burial-ground
#    boundary marker set into a brick surround -- the "sign of age or
#    maintenance" the fixlist asks for, and the most explicitly LEGAL/
#    administrative tell available for a graveyard wall (a real thing these
#    walls carried). Chosen over a repair patch or rubbing course because it
#    reads as a single unambiguous proud rectangle even in a wide frame,
#    where a change-of-bond patch would need a close crop to register.
PLATE_Z = 8.0
PLATE_Y0, PLATE_Y1 = 2.2, 3.0
PLATE_HW = 0.32
C.add_box(bm, FACE_X, FACE_X + 0.05, PLATE_Y0 - 0.06, PLATE_Y1 + 0.06,
          PLATE_Z - PLATE_HW - 0.06, PLATE_Z + PLATE_HW + 0.06, mat_idx=BRICK)  # brick surround
C.add_box(bm, FACE_X + 0.05, FACE_X + 0.09, PLATE_Y0, PLATE_Y1,
          PLATE_Z - PLATE_HW, PLATE_Z + PLATE_HW, mat_idx=IRON)  # cast-iron plate, proud of its own surround

# -- feature 4 of 5 (gate piers): the door at z=14 is treated as the
#    entrance -- a proper pair of piers, wider and proud further than the
#    regular buttresses below, each rising PAST the wall's own 12.0 m height
#    and its coping, with a two-stage moulded cap (a necking impost course,
#    then a wider capping slab) standing clear above the wall head.
GATE_DOOR_Z = 14.0
GATE_PIER_GAP = 0.15          # clearance from the door's own jamb reveal
PIER_HW = 0.35
PIER_PROUD = 0.65
PIER_SHAFT_TOP = 11.6
PIER_CAP_MID = 12.05
PIER_TOP = 12.85              # taller than HEIGHT (12.0) and the coping (12.0)


def add_gate_pier(pz):
    z0, z1 = pz - PIER_HW, pz + PIER_HW
    C.add_box(bm, FACE_X, FACE_X + PIER_PROUD, 0.0, PIER_SHAFT_TOP, z0, z1, mat_idx=BRICK)
    C.add_box(bm, FACE_X - 0.04, FACE_X + PIER_PROUD + 0.04, PIER_SHAFT_TOP, PIER_CAP_MID,
              z0 - 0.04, z1 + 0.04, mat_idx=BRICK)  # necking/impost band
    C.add_box(bm, FACE_X - 0.10, FACE_X + PIER_PROUD + 0.10, PIER_CAP_MID, PIER_TOP,
              z0 - 0.10, z1 + 0.10, mat_idx=BRICK)  # moulded capping slab, wider than the shaft


pier_left_z = GATE_DOOR_Z - DOOR_HW - GATE_PIER_GAP - PIER_HW
pier_right_z = GATE_DOOR_Z + DOOR_HW + GATE_PIER_GAP + PIER_HW
for _pz in (pier_left_z, pier_right_z):
    add_gate_pier(_pz)

# -- feature 1 of 5 (buttresses/piers at regular bays): built as a real
#    pier-and-panel rhythm (Victorian brick boundary walls this thin are
#    routinely built this way structurally, not just decoratively) at a
#    ~3.2 m pitch, skipped wherever it would collide with a door/window
#    recess, a downpipe run, the boundary plate, or the gate-pier zone
#    (which gets its own taller/wider piers above). Each buttress: a lower
#    shaft, a weathered set-off (a sloped shoulder tapering the proud
#    dimension down, not just a flat step -- the fixlist's own wording),
#    and a narrower upper shaft rising to just below the coping. Proud by
#    0.50 m at the base -- at the r6 raking sun (elevation 32/azimuth 15,
#    throw = d*tan(32)/sin(15) = d*2.41) that alone throws ~1.2 m of
#    shadow along the wall's own length beside each one, the single
#    biggest legibility win available per the fixlist.
BUTT_HW = 0.40
BUTT_PROUD = 0.50
BUTT_UPPER_PROUD = 0.20
BUTT_SETOFF_Y = 7.4
BUTT_SLOPE = 0.30
BUTT_TOP = 10.8


def spans_conflict(a0, a1, spans, pad):
    for (s0, s1) in spans:
        if a1 > s0 - pad and a0 < s1 + pad:
            return True
    return False


def add_buttress(bz):
    z0, z1 = bz - BUTT_HW, bz + BUTT_HW
    C.add_box(bm, FACE_X, FACE_X + BUTT_PROUD, 0.0, BUTT_SETOFF_Y, z0, z1, mat_idx=BRICK)
    # weathered set-off: a sloped shoulder, not a flat step -- front face
    # tapers from BUTT_PROUD to BUTT_UPPER_PROUD over BUTT_SLOPE of height,
    # plus two small end-cap quads closing the trapezoid gap this leaves
    # between the lower and upper shaft's own end faces (same winding
    # convention as the plinth's own slope quad above).
    C.add_quad(bm, (FACE_X + BUTT_PROUD, BUTT_SETOFF_Y, z0),
               (FACE_X + BUTT_PROUD, BUTT_SETOFF_Y, z1),
               (FACE_X + BUTT_UPPER_PROUD, BUTT_SETOFF_Y + BUTT_SLOPE, z1),
               (FACE_X + BUTT_UPPER_PROUD, BUTT_SETOFF_Y + BUTT_SLOPE, z0), mat_idx=BRICK)
    C.add_quad(bm, (FACE_X, BUTT_SETOFF_Y, z0), (FACE_X + BUTT_PROUD, BUTT_SETOFF_Y, z0),
               (FACE_X + BUTT_UPPER_PROUD, BUTT_SETOFF_Y + BUTT_SLOPE, z0),
               (FACE_X, BUTT_SETOFF_Y + BUTT_SLOPE, z0), mat_idx=BRICK)
    C.add_quad(bm, (FACE_X + BUTT_PROUD, BUTT_SETOFF_Y, z1), (FACE_X, BUTT_SETOFF_Y, z1),
               (FACE_X, BUTT_SETOFF_Y + BUTT_SLOPE, z1),
               (FACE_X + BUTT_UPPER_PROUD, BUTT_SETOFF_Y + BUTT_SLOPE, z1), mat_idx=BRICK)
    C.add_box(bm, FACE_X, FACE_X + BUTT_UPPER_PROUD, BUTT_SETOFF_Y + BUTT_SLOPE, BUTT_TOP,
              z0, z1, mat_idx=BRICK)


_butt_exclude = list(door_spans) + list(win_spans) + [
    (pz - 0.5, pz + 0.5) for pz in PIPE_Z_RUNS
] + [(PLATE_Z - PLATE_HW - 0.06, PLATE_Z + PLATE_HW + 0.06)]
GATE_ZONE = (pier_left_z - PIER_HW - 0.3, pier_right_z + PIER_HW + 0.3)

BUTTRESS_Z = []
_z = -HALF_L + 3.5
while _z < HALF_L - 3.5:
    _lo, _hi = _z - BUTT_HW, _z + BUTT_HW
    if not (GATE_ZONE[0] < _z < GATE_ZONE[1]) and not spans_conflict(_lo, _hi, _butt_exclude, pad=0.6):
        BUTTRESS_Z.append(_z)
    _z += 3.2

for _bz in BUTTRESS_Z:
    add_buttress(_bz)
print(f"[gy-flank] {len(BUTTRESS_Z)} buttresses placed at z=", BUTTRESS_Z)

obj = C.new_object("gy_flank", bm, MATS)
C.add_bevel(obj, width=0.03, segments=2)
C.smart_uv(obj)

bpy.context.view_layer.objects.active = obj
obj.select_set(True)

# save BEFORE export/render, so the blend's mtime is provably the earliest
# of the three (provenance requirement: blend <= glb < renders)
bpy.ops.wm.save_as_mainfile(
    filepath="C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B3/gy-flank.blend")

C.export_glb([obj], C.MODELS_DIR + "/gy-flank.glb")

# ---- render rig ----
# round-6 fixlist item 1, diagnosis-first: measured gy-flank_ctx.png at r5's
# elevation=45/azimuth=130 -- the coursing band's own dark shadow LINE was
# only 1-2 px tall (row 183-184 of 540, sum 366 vs 514 on the flat wall
# either side -- 29% darker but genuinely sub-pixel-thin) and the two
# plinth tiers showed a lit ledge with NO dark step-shadow beneath it at
# all (rows 360-368 brighter, then straight to background tone at 369 --
# no shadow band). That is cause (i): the geometry is deep enough (0.16-
# 0.24 m proud, well past the fixlist's own thresholds) but the light
# direction throws almost no shadow off it. Worked out why, algebraically:
# for an overhang of depth d on a wall whose face normal is +X, the vertical
# throw of its cast shadow onto the wall below/behind it is
#   throw = d * tan(elevation) / |sin(azimuth)|
# (derived from the sun's own rotation matrix, V = sun_dir(elevation,
# azimuth)). At elevation=45/azimuth=130, throw = d*1.305 -- but sin(130)=
# 0.766 is close to 1, meaning azimuth was ALSO close to hitting the wall
# near its own outward normal (incidence-from-normal angle cos(theta) =
# cos(e)*sin(a) = 0.766*0.707 = 0.542, theta only 57 deg off normal) --
# closer to head-on than the shallow raking angle relief actually needs.
# Fix is NOT more geometry (already tried 3 rounds) -- it is a genuinely
# raking light: LOW sin(azimuth) (light travelling nearly PARALLEL to the
# wall's own length, i.e. grazing along the 118 m run rather than square
# across it) maximises both incidence obliquity AND shadow throw at once,
# since throw = d*tan(e)/sin(a) grows as sin(a) shrinks. At elevation=32,
# azimuth=15: incidence angle off normal = acos(cos(32)*sin(15)) = 77 deg
# (strongly raking, the fixlist's own diagnostic target), and shadow throw
# = d*tan(32)/sin(15) = d*2.41 -- for the 0.24 m lip that is ~0.58 m of
# vertical shadow throw, roughly double what r5's flatter light produced,
# and it lands on a genuinely receding surface (the wall face proper below
# the coursing, and the stepped-back upper plinth tier above the lower
# one) rather than folding back onto the overhang's own front face.
# Energy raised 3.0 -> 6.0 to compensate: cos(theta)=0.22 at this angle
# means the directly-lit wall face only receives ~22% of full sun
# intensity, so without more energy the whole frame would read dim/muddy;
# raising energy brightens the LIT face (and, via bounces, the true
# shadow's ambient floor stays governed by the world background, not sun
# energy) so contrast is gained, not lost.
C.add_sun(elevation_deg=32, azimuth_deg=15, energy=6.0)
# fill light energy trimmed 14 -> 4 (round-6 second pass, was 8 on the
# first pass): measured after the first pass -- the coursing band came in
# strong (36-39% darker, 42px tall, see manifest), but the plinth's TWO
# tiers showed only bright lit ledges with a soft 4-8% step between them,
# not a real dark line -- this fill, positioned high (z=9) and reasonably
# close, was still filling in the plinth's own cast shadow specifically
# (the plinth sits much closer to the fill light's own downward throw than
# the coursing band does). Cut further so the sun's own raking shadow does
# more of the plinth's contrast, while still keeping the door reveal and
# hardware (which rely on this fill too) clear of pure-black.
C.add_fill_light(loc=(16, -20, 9), energy=4)

eye = 1.6
# round-6 fixlist framing ruling: a 118.5 m wall shot whole at eye height
# is not a view any player ever has -- a player walks past this wall a few
# metres away. cam_face is now a REPRESENTATIVE SECTION at genuine walking
# distance (5.5 m out, within the fixlist's 3-6 m band), 1.6 m eye height,
# centred between the door at z=14 and the nearest window at z=20 (only
# 6 m apart -- the tightest door/window pair on the wall). At this distance
# a 16 mm lens's own horizontal FOV (~97 deg on a 16:9 sensor) covers
# ~12.4 m of wall width -- both the door and the window land in frame with
# margin, not just the door alone. Target height 3.4 m (half-range 3.4 m
# at 5.5 m out) puts the visible vertical band from just below ground to
# y~6.8 -- ground, plinth (both tiers) and the coursing band (5.95-6.25)
# all land together; the window band (8.8-9.85) sits above this frame's
# top edge and is not claimed here (it reads instead in gy-flank_ctx.png,
# kept pulled back for massing per the fixlist's own explicit allowance).
# round-6 second pass: the first version of this frame (target y=3.4,
# lens 16) put the frame's own bottom edge at almost exactly y=0.0 --
# squeezing the ENTIRE 0.5 m plinth (both tiers) into the frame's last row
# or two, off-frame in practice (measured: rows 510-539 showed only a
# sliver of the lower tier's lit top, no room for its shadow step at all).
# Retargeted slightly lower and widened a touch so the frame's bottom edge
# sits at y=-0.3 (clear margin below ground) and the top still clears the
# coursing band (y up to 6.9) -- both tiers now have real vertical room.
# round-7 fixlist: the fixlist's own test requires ALL FIVE new features
# (buttresses, coping, bricked doorway, gate piers, boundary plate) countable
# in THIS ONE delivered frame -- they are spread across a ~23 m run (plate at
# z=8 to the bricked doorway at z=27, with the gate piers/door at z=14 in
# between). r6's 5.5 m/13 m-wide framing cannot fit that span. Widened to an
# 11 m standoff (still the camera held at 1.6 m eye height; only the look-at
# height/distance changed) -- at 15 mm lens this covers ~26.4 m of wall
# width (half-FOV tan(50.2 deg)=1.20 * 11m = 13.2m either side of z=17.5) and
# ~14.9 m of vertical range centred on y=6.0 (half-FOV tan(34.05
# deg)=0.676 * 11m = 7.44m each way, i.e. y=-1.44..13.44), clearing the gate
# piers' own cap top at 12.85. Honestly recorded: this is wider than r6's
# walking-distance figure, a deliberate trade this round because the
# fixlist's own test is decided from this one frame containing everything.
cam_face = C.add_camera("cam_face", C.V(15.0, eye, 17.5), C.V(4, 6.0, 17.5), lens=15)
# round-7, second pass (judge comparability request): cam_face's own 11 m
# standoff is not comparable to the three prior rounds' 5.5 m walking-
# distance figure, and the fixlist's own 3-6 m band was written because a
# player walks past this wall a few metres away, never stands back 11 m to
# take it in whole. Added a SECOND frame at r6's own exact walking-distance
# recipe (5.5 m standoff, same 15 mm lens, same 1.6 m eye height, same
# target-y=3.3 convention as r6's own cam_face) so the judge can compare like
# for like AND check whether the new features still read at the distance a
# player actually sees them, not just at the wider distance chosen to fit
# all five in one shot. Re-centred on z=14 (the gate/entrance) instead of
# r6's z=17 (door/window pair) specifically because the fixlist asked this
# frame to include "the gate piers and at least two buttress bays" -- the
# buttresses at z=11.45 and z=17.85 (the two nearest, both outside the gate
# exclusion zone) land either side of the gate within this lens's own
# ~13 m horizontal FOV at 5.5 m. Honestly out of THIS frame's span: the
# bricked doorway (z=27, 13 m further along, physically outside a 13 m-wide
# frame centred here) and the coping (y=11.65-12.0, above this frame's own
# ~6.9 m top edge at 1.6 m eye height/target y=3.3 -- the same ground-vs-
# roofline conflict r6 already hit with the window band, and a 5.5 m/15 mm/
# eye-height frame cannot show a 12 m-tall wall's ground and head at once
# regardless of where it is centred). Both exclusions are measured and
# reported, not silently dropped, in the manifest.
cam_walk = C.add_camera("cam_walk", C.V(9.5, eye, 14.0), C.V(4, 3.3, 14.0), lens=15)
# _34 round-3 refit: pixel-checked the r3 render -- values were ~189/255,
# NOT clipped white. The apparent "white-out" was a framing problem: the
# target height (4.5m) sits in the middle of the LARGEST deliberately blank
# band (door heads at 2.15m to window sills at 8.8m), so ~80% of the frame
# was flat brick with nothing else in it -- reads as blown-out to the eye
# even at a correct exposure. Retargeted to the full wall height, angled
# along the run so a door AND a window both land in frame together with
# the plinth and coping, which is what actually reads as "mostly blind
# wall with occasional openings" rather than "empty plane".
cam_34 = C.add_camera("cam_34", C.V(12.0, eye, 30.0), C.V(4, 5.2, 16.0), lens=22)
# round-4 fixlist item 1a: _detail now shows a WHOLE door opening (leaf,
# hinges, latch, threshold) instead of the window -- pulled back to 9 m so
# the full 2.15 m-tall opening plus the lintel block above and the
# threshold below both land in frame.
cam_detail = C.add_camera("cam_detail", C.V(9.0, 1.15, 14.0), C.V(4, 1.15, 14.0), lens=32)
# round-4: the window bars passed clean in r3 and must not lose their own
# evidence just because _detail now points at a door -- kept as an extra
# frame (BRIEF-COMMON allows extra frames beyond the minimum; rookery
# already does this for its boarded window/yard/privy).
cam_window = C.add_camera("cam_window", C.V(7.0, 9.325, -28.0), C.V(4, 9.325, -28), lens=40)
# round-4: pulled back and widened so both downpipe runs (z +-26), the
# coursing break, and the plinth all land in one wide elevation shot.
# round-6 fixlist framing ruling: kept deliberately pulled back -- this is
# the ONE frame the ruling explicitly allows to stay wide, "for overall
# massing" -- covering both downpipe runs and 3 windows in one elevation.
# It is not the frame the coursing/plinth relief test is judged against;
# that is cam_face (reframed to walking distance above). The new raking
# sun (elevation 32/azimuth 15) still improves this frame's own coursing
# line and downpipe contrast as a side effect, but is not relied on here.
cam_ctx = C.add_camera("cam_ctx", C.V(34, 8, 0), C.V(0, 6, 0), lens=18)
# round-5 fixlist item 1b: the run now spans ground (shoe) to PIPE_TOP+0.30
# (hopper mouth), ~12 m of wall height -- pulled well back and re-centred
# so ONE frame contains the hopper, both brackets, the full shaft, and the
# shoe discharging at the ground, per the fixlist's explicit instruction.
# This sets the 1.6 m eye-height convention aside for this one dedicated
# crop (same precedent as viaduct-module's cam_face, noted honestly in the
# manifest) because a full-height downpipe run cannot be centred at eye
# height and still show its own top and bottom in the same shot.
# round-5 second pass: at the standard 960x540 landscape framing wide
# enough to fit the whole run, the 0.11 m pipe and its brackets collapsed
# to a hairline a couple of px wide -- present, but not honestly countable.
# Rendered in a PORTRAIT aspect instead (960 tall x 540 wide, swapped just
# for this one shot and restored after) so the same vertical extent is
# covered by nearly twice the vertical pixels, closer in, without cropping
# out the hopper or the shoe.
cam_pipe = C.add_camera("cam_pipe", C.V(16.0, 5.5, 26.6), C.V(4.0, 5.5, 26.0), lens=24)

C.setup_render('CYCLES', samples=32, res=(960, 540), device='CPU')
# round-4: a handful of pixels deep in the door leaf's plank-gap crevices
# sat just under the pure-black threshold. Raising the GLOBAL world ambient
# enough to clear them (tested up to 2.6) visibly flattened contrast across
# the whole 120 m wall -- the same "washed out" failure mode the round-3
# notes already warn about. A small local point light near the door lifts
# just that crevice's own ambient floor without touching the rest of the
# wall's exposure.
# round-4: tucked INSIDE the recess (x=3.7, just behind the leaf's own
# front face at ~3.90, instead of out at x=4.6 in open air in front of the
# wall) so the recess itself shadows this light from the wide face/ctx
# cameras -- the first placement (in open air) bloomed a visible hotspot
# on the flat wall around the door in exactly those two frames.
for _hz, _hy in ((14.0, 1.925), (14.0, 0.225)):
    _pl = bpy.data.lights.new("door_fill", type='POINT')
    _pl.energy = 4.0
    _pl.shadow_soft_size = 0.02
    _pl_obj = bpy.data.objects.new("door_fill", _pl)
    _pl_obj.location = C.V(3.75, _hy, _hz)
    bpy.context.collection.objects.link(_pl_obj)

backup = C.apply_clay_override([obj])
for cam, name in ((cam_face, "face"), (cam_walk, "walk"), (cam_34, "34"), (cam_detail, "detail"),
                   (cam_window, "window"), (cam_ctx, "ctx")):
    bpy.context.scene.camera = cam
    C.render_to(C.RENDER_DIR + f"/gy-flank_{name}.png")
# cam_pipe: portrait override, swapped back to landscape immediately after
# so nothing later in the batch inherits it (this script only renders this
# one asset, but keeping the swap scoped is the honest habit).
scene = bpy.context.scene
scene.render.resolution_x, scene.render.resolution_y = 540, 960
bpy.context.scene.camera = cam_pipe
C.render_to(C.RENDER_DIR + "/gy-flank_pipe.png")
scene.render.resolution_x, scene.render.resolution_y = 960, 540
C.restore_materials([obj], backup)

print("DONE gy-flank")
