import sys
sys.path.insert(0, "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B3")
import bpy
import common as C

bpy.ops.wm.open_mainfile(filepath="C:/Users/USERNAME/Downloads/projects/victorian-london/blender/B3/rookery.blend")
obj = bpy.data.objects["rookery"]
# first-floor window near bay_x(0), floor 1 (fy=3.5), sill at 3.5+FLOOR_H*0.30=4.55, lintel 3.5+FLOOR_H*0.78=6.23
door0_xc = -19.5 + (38.0/7)*0.5
cam = C.add_camera("cam_dbg", C.V(door0_xc-1.0, 5.3, -14.0), C.V(door0_xc, 5.3, -10.75), lens=55)
C.setup_render('CYCLES', samples=32, res=(960,540), device='CPU')
backup = C.apply_clay_override([obj])
bpy.context.scene.camera = cam
C.render_to(C.RENDER_DIR + "/debug_window.png")
C.restore_materials([obj], backup)
