import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_stall as bs

def count(obj):
    deps = bpy.context.evaluated_depsgraph_get()
    eobj = obj.evaluated_get(deps)
    mesh = eobj.to_mesh()
    mesh.calc_loop_triangles()
    n = len(mesh.loop_triangles)
    eobj.to_mesh_clear()
    return n

orig = bs.build_canopy

def make_variant(skip_ridge, skip_hem, skip_tie):
    def variant(bm):
        pole_h = 2.1
        pole_x = bs.LEN / 2.0 + 0.08
        attach_z = pole_h - 0.10
        for sx in (-1, 1):
            x = sx * pole_x
            bs.add_cyl(bm, (x, 0, pole_h / 2), 0.03, 0.03, pole_h, bs.PLANKS, segments=8)
            bs.add_cyl(bm, (x, 0, bs.COUNTER_H + 0.03), 0.055, 0.055, 0.09, bs.IRON, segments=10)
            bs.add_box(bm, (x, 0.10, bs.COUNTER_H - 0.01), (0.12, 0.03, 0.16), bs.IRON)
            for bz in (bs.COUNTER_H - 0.06, bs.COUNTER_H + 0.06):
                bs.add_cyl(bm, (x, 0.10, bz), 0.018, 0.018, 0.10, bs.IRON, segments=8, axis='y')
            az = math.atan2(-0.42, 0.45)
            bs.add_rope_wrap(bm, x, attach_z, bs.PLASTER, bs.IRON, seed=1 if sx < 0 else 2, cam_azimuth=az)
        ridge_z = attach_z + 0.05
        if not skip_ridge:
            ridge_pts = [(-pole_x, 0, ridge_z), (-pole_x*0.5,0,ridge_z-0.012),(0,0,ridge_z-0.018),(pole_x*0.5,0,ridge_z-0.012),(pole_x,0,ridge_z)]
            bs.rope_from_curve(bm, ridge_pts, [1.0]*5, 0.012, bs.IRON, bevel_res=2)
        N_SUPPORTS=5
        support_x=[-pole_x+(2*pole_x)*i/(N_SUPPORTS-1) for i in range(N_SUPPORTS)]
        def cell_sag(tg,dip):
            cellf = tg*(N_SUPPORTS-1); cell=min(int(cellf),N_SUPPORTS-2); sl=cellf-cell
            return dip*math.sin(math.pi*sl)
        n_steps=14; dip=0.10; thickness=0.018; y_half=0.55
        top_v, bot_v = [], []
        for i in range(n_steps+1):
            t=i/n_steps; x=-pole_x+(2*pole_x)*t; sag=cell_sag(t,dip)
            zt=attach_z-sag; zb=zt-thickness
            top_v.append((bm.verts.new((x,-y_half,zt)), bm.verts.new((x,y_half,zt))))
            bot_v.append((bm.verts.new((x,-y_half,zb)), bm.verts.new((x,y_half,zb))))
        for i in range(n_steps):
            tl0,tr0=top_v[i]; tl1,tr1=top_v[i+1]; bl0,br0=bot_v[i]; bl1,br1=bot_v[i+1]
            bm.faces.new((tl0,tr0,tr1,tl1)).material_index=bs.PLASTER
            bm.faces.new((bl1,br1,br0,bl0)).material_index=bs.PLASTER
            bm.faces.new((tl0,tl1,bl1,bl0)).material_index=bs.PLASTER
            bm.faces.new((br0,br1,tr1,tr0)).material_index=bs.PLASTER
        bm.faces.new((top_v[0][0],top_v[0][1],bot_v[0][1],bot_v[0][0])).material_index=bs.PLASTER
        bm.faces.new((bot_v[-1][0],bot_v[-1][1],top_v[-1][1],top_v[-1][0])).material_index=bs.PLASTER
        if not skip_hem:
            HEM_SEGS=6
            for sy in (-1,1):
                hem_pts=[]
                for i in range(HEM_SEGS+1):
                    t=i/HEM_SEGS; x=-pole_x+(2*pole_x)*t; sag=cell_sag(t,dip)
                    hem_pts.append((x, sy*y_half, attach_z-sag-thickness*0.5))
                bs.rope_from_curve(bm, hem_pts, [1.0]*len(hem_pts), 0.024, bs.PLASTER, bevel_res=2)
        if not skip_tie:
            for x in support_x[1:-1]:
                bs.add_tie_loop(bm, x, ridge_z-0.004, attach_z-0.002, bs.IRON)
    return variant

for label, flags in [("base_only", (True,True,True)), ("ridge_only",(False,True,True)),
                      ("hem_only",(True,False,True)), ("tie_only",(True,True,False)),
                      ("all",(False,False,False))]:
    bs.build_canopy = make_variant(*flags)
    obj = bs.build()
    print(label, count(obj))
