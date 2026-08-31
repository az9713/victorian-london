"""Acceptance renders for ginpalace.glb -- CLAY, Cycles CPU, per BRIEF-COMMON."""
import bpy
import sys

sys.path.insert(0, "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2")
import common as C

exec(open("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/ginpalace.py").read())

# Belt-and-braces clay: the view-layer material_override left the smaller,
# deeper-set upper sash openings rendering near-black -- physically swap
# every material slot on the object itself so nothing can leak transmission.
C.apply_clay_override([obj])

C.setup_clay_render(res=(960, 540), samples=32)
C.add_sun(energy=3.2, elevation_deg=45, azimuth_deg=140)
C.add_fill_light(energy=2.5, loc=(-25, 10, 15))
C.add_fill_light(name="Fill2", energy=1.8, loc=(20, -20, 12))

shots = [
    ("face", C.V(-16, 1.6, 0), C.V(-6.5, 3.5, 0), 32),
    ("34", C.V(-15, 1.7, -14), C.V(0, 4.5, 0), 28),
    # pulled back + retargeted at mid-height so the door AND the radiating
    # fanlight above it both sit in frame (round-1 judge: fanlight bars
    # weren't visible evidence).
    ("detail", C.V(-13.5, 1.6, -8.95), C.V(-7.4, 1.5, -8.95), 30),
    ("ctx", C.V(-24, 7, -21), C.V(0, 6, 0), 22),
]
for name, loc, target, lens in shots:
    C.add_camera("CamG_" + name, loc, target, lens=lens)
    C.render_to(f"C:/Users/USERNAME/Downloads/projects/victorian-london/blender/renders/B2/ginpalace_{name}.png")
