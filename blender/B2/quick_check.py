"""Quick single-frame Cycles checks: one ginpalace sash, one church flank door."""
import bpy
import sys

sys.path.insert(0, "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2")
import common as C

exec(open("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/ginpalace.py").read())
C.apply_clay_override([obj])
C.setup_clay_render(res=(700, 700), samples=24)
C.add_sun(energy=3.2, elevation_deg=45, azimuth_deg=140)
C.add_fill_light(energy=2.5, loc=(-25, 10, 15))
C.add_camera("CamSash", C.V(-11, 1.7, -3.75), C.V(-7.4, 5.3, -3.75), lens=30)
C.render_to("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/qc_sash.png")

exec(open("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/church.py").read())
C.apply_clay_override([obj])
C.setup_clay_render(res=(700, 700), samples=24)
C.add_sun(energy=3.2, elevation_deg=42, azimuth_deg=125)
C.add_fill_light(energy=2.5, loc=(30, 10, 25))
door_zc = (-15.5 + -4.0) / 2.0
C.add_camera("CamFlank", C.V(NX1 + 8, 1.6, door_zc), C.V(NX1 + WALL_T, 1.6, door_zc), lens=30)
C.render_to("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/qc_flankdoor.png")
