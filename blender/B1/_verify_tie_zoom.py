"""Temporary verification render only -- zoom tightly on the tie wraps to
count wrap radii / crossing precisely. Not part of the delivered pipeline."""
import bpy
import sys
import os
import math
import mathutils

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import setup_clay_render, add_ground_plane, add_sun, add_fill_sun, add_camera, render_to, RENDERS_DIR

bpy.ops.wm.open_mainfile(filepath="C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B1/stall.blend")
setup_clay_render()
add_ground_plane(size=6.0)
add_sun()
add_fill_sun(energy=1.6)

LEN = 2.4
pole_x = LEN / 2.0 + 0.08
attach_z = 2.1 - 0.10
add_camera("cam_zoom", (pole_x + 0.28, -0.24, attach_z + 0.00),
           mathutils.Vector((pole_x, 0, attach_z - 0.05)), lens=60)
render_to(os.path.join(RENDERS_DIR, "_verify_tie_zoom.png"))
print("VERIFY DONE")
