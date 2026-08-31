"""Isolate the jamb seam: same crop, grid/bars disabled via monkeypatch."""
import bpy
import sys

sys.path.insert(0, "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2")
import common as C

_orig = C.add_round_window
def patched(bm, bay_x0, bay_x1, z_face, thickness, y0_wall, y1_wall,
            sill_y, springing_y, wall_mat, glass_mat, **kw):
    kw.pop('bar_mat', None)
    return _orig(bm, bay_x0, bay_x1, z_face, thickness, y0_wall, y1_wall,
                 sill_y, springing_y, wall_mat, glass_mat, bars=False, **kw)
C.add_round_window = patched

exec(open("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/church.py").read())
C.apply_clay_override([obj])
C.setup_clay_render(res=(700, 700), samples=24)
C.add_sun(energy=3.2, elevation_deg=42, azimuth_deg=125)
C.add_fill_light(energy=2.5, loc=(30, 10, 25))
C.add_camera("CamJamb", C.V(-6.75, 1.6, -27), C.V(-6.75, 6.05, -15.5), lens=24)
C.render_to("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/qc_jamb_nogrid.png")
