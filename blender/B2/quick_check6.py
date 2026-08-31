"""Confirm letterbox-slot occlusion theory: ambient world light only, no sun/fill."""
import bpy, sys
sys.path.insert(0, "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2")
import common as C
exec(open("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/church.py").read())
C.apply_clay_override([obj])
C.setup_clay_render(res=(900, 900), samples=32)
# deliberately NOT calling add_sun / add_fill_light -- ambient world only
C.add_camera("CamBal3", C.V(17, 35.6, 6), C.V(11.5, 34.9, 3.6), lens=55)
C.render_to("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/qc_bal_ambient.png")
