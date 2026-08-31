"""WIP check renders for ginpalace.py -- NOT final acceptance renders."""
import bpy
import sys

sys.path.insert(0, "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2")
import common as C

exec(open("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/ginpalace.py").read())

C.setup_render(engine='BLENDER_WORKBENCH', res=(640, 640))
scene = bpy.context.scene
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.show_shadows = True

shots = [
    ("face", C.V(-18, 1.6, 0), C.V(-5, 4, 0), 32),
    ("door_detail", C.V(-12, 1.6, -9), C.V(-7.4, 1.6, -8.95), 45),
    ("window_detail", C.V(-13, 1.7, 0), C.V(-7.4, 1.9, 0), 45),
    ("34", C.V(-16, 4, -13), C.V(0, 4, 0), 30),
    ("ctx", C.V(-24, 6, -20), C.V(0, 6, 0), 24),
]
for name, loc, target, lens in shots:
    C.add_camera("Cam_" + name, loc, target, lens=lens)
    C.render_to(f"C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B2/wip_ginpalace_{name}.png")
