import bpy, sys, glob, os
d = "C:/Users/USERNAME/Downloads/projects/victorian-london/blender/renders/B3"
pattern = sys.argv[-1] if sys.argv[-1].endswith(".png") or "*" in sys.argv[-1] else "gy-flank_*.png"
for f in sorted(glob.glob(os.path.join(d, pattern))):
    img = bpy.data.images.load(f)
    px = list(img.pixels)
    n = len(px) // 4
    blacks = 0
    minsum = 999
    for i in range(n):
        r, g, b = px[i*4], px[i*4+1], px[i*4+2]
        s = (r+g+b) * 255
        if s < 15:
            blacks += 1
        if s < minsum:
            minsum = s
    print(f"{os.path.basename(f):35s} blackpx={blacks:6d}  minsum={minsum:.1f}")
    bpy.data.images.remove(img)
