"""WIP check renders for church.py -- NOT final acceptance renders."""
import bpy
import sys

sys.path.insert(0, "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2")
import common as C

exec(open("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/church.py").read())

C.setup_render(engine='BLENDER_WORKBENCH', res=(640, 640))
scene = bpy.context.scene
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.show_shadows = True

shots = [
    ("face", C.V(30, 1.6, 0), C.V(0, 8, 0), 35),
    ("portico_detail", C.V(20, 1.6, 0), C.V(15.5, 6, 0), 45),
    ("flank_detail", C.V(-6, 1.6, -22), C.V(-6, 5, -15.5), 45),
    ("belfry_detail", C.V(20, 30, 5), C.V(11, 30, 0), 50),
    ("ctx", C.V(50, 12, -42), C.V(10, 22, 0), 24),
]
for name, loc, target, lens in shots:
    C.add_camera("Cam_" + name, loc, target, lens=lens)
    C.render_to(f"C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/wip_church_{name}.png")
