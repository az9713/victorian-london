import bpy
img = bpy.data.images.load("C:/Users/USERNAME/Downloads/projects/victorian-london/blender/renders/B3/gy-flank_detail.png")
w, h = img.size
px = list(img.pixels)
for y in range(h):
    for x in range(w):
        i = (y*w+x)*4
        r,g,b = px[i],px[i+1],px[i+2]
        if (r+g+b)*255 < 15:
            print(x, h-1-y)  # flip y since image data is bottom-up
