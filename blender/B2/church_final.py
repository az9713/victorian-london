"""Acceptance renders for church.glb -- CLAY, Cycles CPU, per BRIEF-COMMON."""
import bpy
import sys

sys.path.insert(0, "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2")
import common as C

exec(open("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/church.py").read())

# Belt-and-braces clay: the view-layer material_override left small, deep-set
# openings (upper sash-scale glass) rendering near-black -- physically swap
# every material slot on the object itself so nothing can leak transmission.
C.apply_clay_override([obj])

C.setup_clay_render(res=(960, 540), samples=32)
C.add_sun(energy=3.2, elevation_deg=42, azimuth_deg=125)
C.add_fill_light(energy=2.5, loc=(30, 10, 25))
C.add_fill_light(name="Fill2", energy=1.8, loc=(-25, -15, 20))

shots = [
    # face: pulled back + retargeted at door mid-height (not portico apex)
    # so the whole door -- threshold to arch crown -- sits in frame between
    # the columns, per round-1 judge note.
    ("face", C.V(34, 1.6, 0), C.V(15.5, 3.3, 0), 26),
    ("34", C.V(28, 1.6, -22), C.V(11, 10, 0), 28),
    # detail: pulled back + wider lens so head AND sill are both in frame,
    # not just the arches (round-1 judge note).
    ("detail", C.V(-6.75, 1.6, -27), C.V(-6.75, 6.05, -15.5), 24),
    ("ctx", C.V(52, 12, -44), C.V(10, 23, 0), 22),
    # extra frame (COMMON allows more than the minimum): close on the belfry
    # balustrade + a corner pinnacle -- too small to read as "real, not a
    # solid box" from the pulled-back ctx alone.
    ("balustrade", C.V(20, 35.2, 8), C.V(12.5, 34.5, 3.7), 40),
]
for name, loc, target, lens in shots:
    C.add_camera("CamF_" + name, loc, target, lens=lens)
    C.render_to(f"C:/Users/USERNAME/Downloads/projects/victorian-london/blender/renders/B2/church_{name}.png")
