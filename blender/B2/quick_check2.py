"""Quick check: tower corner + nave window jambs + fanlight, after fixes."""
import bpy
import sys

sys.path.insert(0, "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2")
import common as C

exec(open("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/church.py").read())
C.apply_clay_override([obj])
C.setup_clay_render(res=(700, 700), samples=24)
C.add_sun(energy=3.2, elevation_deg=42, azimuth_deg=125)
C.add_fill_light(energy=2.5, loc=(30, 10, 25))
C.add_camera("CamCorner", C.V(34, 1.6, 0), C.V(15.5, 3.3, 0), lens=26)
C.render_to("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/qc_towercorner.png")
C.add_camera("CamJamb", C.V(-6.75, 1.6, -27), C.V(-6.75, 6.05, -15.5), lens=24)
C.render_to("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/qc_jamb.png")

exec(open("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/ginpalace.py").read())
C.apply_clay_override([obj])
C.setup_clay_render(res=(700, 700), samples=24)
C.add_sun(energy=3.2, elevation_deg=45, azimuth_deg=140)
C.add_fill_light(energy=2.5, loc=(-25, 10, 15))
C.add_camera("CamFan", C.V(-13.5, 1.6, -8.95), C.V(-7.4, 1.5, -8.95), lens=30)
C.render_to("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/qc_fanlight.png")
