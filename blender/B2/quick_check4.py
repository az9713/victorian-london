"""Re-test jamb crop with bars enabled + bumped weld tolerance."""
import bpy
import sys

sys.path.insert(0, "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2")
import common as C

exec(open("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/church.py").read())
C.apply_clay_override([obj])
C.setup_clay_render(res=(700, 700), samples=24)
C.add_sun(energy=3.2, elevation_deg=42, azimuth_deg=125)
C.add_fill_light(energy=2.5, loc=(30, 10, 25))
C.add_camera("CamJamb", C.V(-6.75, 1.6, -30), C.V(-6.75, 6.05, -15.5), lens=34)
C.render_to("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/qc_jamb3.png")
