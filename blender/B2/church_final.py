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
    ("face", C.V(26, 1.6, 0), C.V(15.5, 8, 0), 32),
    ("34", C.V(28, 1.6, -22), C.V(11, 10, 0), 28),
    ("detail", C.V(-6.75, 1.6, -25), C.V(-6.75, 6.0, -15.5), 32),
    ("ctx", C.V(52, 12, -44), C.V(10, 23, 0), 22),
]
for name, loc, target, lens in shots:
    C.add_camera("CamF_" + name, loc, target, lens=lens)
    C.render_to(f"C:/Users/USERNAME/Downloads/projects/victorian-london/blender/renders/B2/church_{name}.png")
