"""Dino Park Tycoon - TRN_LevelledPads + TRN_Slopes builder.
Sources: TRN_LevelledPads.jpg, TRN_Slopes.jpg.  Set BUILD = "pads" or "slopes" before exec.
Slopes climb one terrain level (LEVEL = 1.0 m) from x=-1 (low) to x=+1 (high)."""
import os
exec(open(os.path.join(TOOLS, "trn_common.py")).read())
random.seed(7)
RESULTS = {}

if BUILD == "pads":
    coll = get_coll("TRN_LevelledPads")
    # --- packed earth pad ---
    H = lambda x,y: 0.006*nn(x,y,1.2,1) + 0.003*nn(x,y,5,2) + shoulder(x,y,0.12)
    m = painted2("TRN_Pad_Earth_Body", [(0.30,0.15,0.05),(0.45,0.23,0.08),(0.57,0.34,0.13)],
                 [(0.17,0.08,0.03),(0.26,0.13,0.05),(0.34,0.19,0.08)], streak=0.6, streak_scale=(1,14,1), bump=0.1)
    bm,tl,ml,hl = new_bm(); fs = build_hf(bm,H,36,36,top_layer=tl,mask_layer=ml); nb=len(fs)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    RESULTS["TRN_Pad_Earth"] = finish("TRN_Pad_Earth",coll,bm,nb,[m],(-1.4,0,0),"TRN_LevelledPads.jpg",{"buildable":True})
    # --- gravel pad with cream concrete curb ---
    CW = 0.16
    def Hg(x,y):
        d = edge_d(x,y); inner = sstep(CW-0.01, CW+0.03, d)
        curb = 0.02 + shoulder(x,y,0.06) - 0.015*sstep(CW-0.05, CW, d)
        return curb*(1-inner) + (-0.035 + 0.006*nn(x,y,6,3))*inner
    mc = painted2("TRN_Pad_Curb", [(0.45,0.40,0.28),(0.57,0.52,0.38),(0.66,0.62,0.48)],
                  [(0.26,0.23,0.17),(0.36,0.32,0.24),(0.45,0.41,0.31)], streak=0.3, bump=0.12, scale=4)
    mg = gravel_mat("TRN_Pad_Gravel", [(0.10,0.10,0.10),(0.20,0.20,0.19),(0.32,0.32,0.30),(0.45,0.45,0.43)])
    bm,tl,ml,hl = new_bm(); fs = build_hf(bm,Hg,48,48,top_layer=tl,mask_layer=ml); nb=len(fs)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    for f in fs:
        c = f.calc_center_median()
        f.material_index = 1 if (edge_d(c.x,c.y) > CW+0.012 and f.normal.z > 0.5) else 0
    RESULTS["TRN_Pad_Gravel"] = finish("TRN_Pad_Gravel",coll,bm,nb,[mc,mg],(1.4,0,0),"TRN_LevelledPads.jpg",{"buildable":True})

if BUILD == "slopes":
    coll = get_coll("TRN_Slopes")
    TOPS = [(0.10,0.21,0.02),(0.16,0.30,0.035),(0.23,0.39,0.05)]
    SAND = [(0.40,0.27,0.12),(0.52,0.37,0.18),(0.62,0.47,0.25)]
    SOIL = [(0.10,0.045,0.018),(0.18,0.085,0.03),(0.26,0.13,0.05),(0.33,0.18,0.07)]
    def soil_mat(n): return painted2(n, TOPS, SOIL, mask_cols=SAND, streak=0.45, side_scale=(1.2,1.2,9), zrange=(-T,LEVEL))
    mbl = blade_mat("TRN_Slope_Blade", (0.10,0.21,0.018),(0.38,0.52,0.11),(0.26,0.40,0.06),0.1)
    def edge_sand(x,y,w=0.11): return 1-sstep(0.02,w,edge_d(x,y))
    # --- ramp ---
    prof = lambda x: LEVEL*sstep(-0.72, 0.62, x)
    H = lambda x,y: prof(x) + 0.008*nn(x,y,1.5,4) + shoulder(x,y)
    Mk = lambda x,y: max(edge_sand(x,y), 1-sstep(-0.86,-0.66,x), 0.8*(1-sstep(0.0,0.12,1-x)))
    bm,tl,ml,hl = new_bm(); fs = build_hf(bm,H,48,30,mask=Mk,top_layer=tl,mask_layer=ml); nb=len(fs)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces)); extra=[]
    for _ in range(30):
        y = random.uniform(-0.9,0.9); x = random.choice([-0.95,0.95,random.uniform(-0.9,0.9)])
        extra += clump(bm,hl,H,x,y if abs(x)<0.9 else y,3,0.04,0.08,0.03,0.014)
    for f in extra: f.material_index = 1
    RESULTS["TRN_Slope_Ramp"] = finish("TRN_Slope_Ramp",coll,bm,nb,[soil_mat("TRN_Slope_Ramp_Body"),mbl],(-2.6,0,0),"TRN_Slopes.jpg",{"rise_m":LEVEL,"rises_toward":"+X"})
    # --- valley (dip across the tile, high on both X edges) ---
    pv = lambda x: LEVEL - (LEVEL-0.12)*(1-sstep(0.22,0.78,abs(x)))
    Hv = lambda x,y: pv(x) + 0.008*nn(x,y,1.5,5) + shoulder(x,y)
    Mv = lambda x,y: max(edge_sand(x,y), 0.9*(1-sstep(0.06,0.24,abs(x)))*sstep(0.5,0.8,abs(y)), 0.8*(1-sstep(0.04,0.14,1-abs(x))))
    bm,tl,ml,hl = new_bm(); fs = build_hf(bm,Hv,56,30,mask=Mv,top_layer=tl,mask_layer=ml); nb=len(fs)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    RESULTS["TRN_Slope_Valley"] = finish("TRN_Slope_Valley",coll,bm,nb,[soil_mat("TRN_Slope_Valley_Body")],(0,0,0),"TRN_Slopes.jpg",{"rise_m":LEVEL})
    # --- stairs with timber sleepers and side stringers ---
    NS = 6; x0, x1 = -0.78, 0.78; step_w = (x1-x0)/NS
    def ps(x):
        if x <= x0: return 0.0
        if x >= x1: return LEVEL
        k = (x-x0)/step_w; i = math.floor(k); fr = k-i
        return LEVEL*(i + sstep(0.82,0.98,fr))/NS
    Hs = lambda x,y: ps(x) + 0.004*nn(x,y,3,6) + shoulder(x,y)
    Ms = lambda x,y: 1.0 if abs(y) < 0.62 else 0.0
    bm,tl,ml,hl = new_bm(); fs = build_hf(bm,Hs,120,30,mask=Ms,top_layer=tl,mask_layer=ml); nb=len(fs)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    tim = []
    for i in range(NS):
        xr = x0 + step_w*(i+0.9); zt = LEVEL*(i+1)/NS
        tim += box(bm,(xr-0.05, 0, zt-0.045),(0.13,1.18,0.11))
    L = math.hypot(x1-x0, LEVEL); ang = math.atan2(LEVEL, x1-x0)
    for yy in (-0.66,0.66):
        tim += box(bm,((x0+x1)/2, yy, LEVEL/2+0.06),(L+0.12,0.14,0.15), Matrix.Rotation(-ang,4,'Y'))
    for f in tim: f.material_index = 1
    tufts=[]
    for i in range(NS):
        for _ in range(3):
            x = x0+step_w*(i+random.uniform(0.1,0.6)); y = random.choice([-0.55,0.55])+random.uniform(-0.08,0.08)
            tufts += clump(bm,hl,Hs,x,y,3,0.04,0.07,0.03,0.014)
    for f in tufts: f.material_index = 2
    mt = painted2("TRN_Stair_Timber", [(0.035,0.04,0.035),(0.06,0.065,0.055),(0.09,0.09,0.075)],
                  [(0.03,0.032,0.028),(0.05,0.052,0.045)], streak=0.5, streak_scale=(12,1,1), bump=0.25, scale=6)
    RESULTS["TRN_Slope_Stairs"] = finish("TRN_Slope_Stairs",coll,bm,nb,[soil_mat("TRN_Slope_Stairs_Body"),mt,mbl],(2.6,0,0),"TRN_Slopes.jpg",{"rise_m":LEVEL,"steps":NS})
