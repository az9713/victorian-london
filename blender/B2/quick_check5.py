"""Isolate the remaining balustrade base black block after cornice merge."""
import bpy, sys
sys.path.insert(0, "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2")
import common as C
exec(open("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/church.py").read())
C.apply_clay_override([obj])
C.setup_clay_render(res=(900, 900), samples=32)
C.add_sun(energy=3.2, elevation_deg=42, azimuth_deg=125)
C.add_fill_light(energy=2.5, loc=(30, 10, 25))
C.add_camera("CamBal2", C.V(17, 35.6, 6), C.V(11.5, 34.9, 3.6), lens=55)
C.render_to("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/qc_bal2.png")
