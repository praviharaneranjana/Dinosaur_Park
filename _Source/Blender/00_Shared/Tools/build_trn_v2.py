"""Dino Park Tycoon - TRN v02 HQ builder (blender-skills-pack workflow; see _Reference/TRN_reference_analysis_v02.md).
BUILD = pads | slopes | volcano | swamp | desert | beach | ponds | river | falls
Tiles 2x2 m, 0.4 m thick, pivot centre of top (z=0). Props pivot bottom-centre."""
import os
exec(open(os.path.join(TOOLS, "trn_common.py")).read())
exec(open(os.path.join(TOOLS, "trn_hq.py")).read())
exec(open(os.path.join(TOOLS, "trn_hq2.py")).read())
RESULTS = {}
random.seed(77)
def row(i, n, gap=2.6, off=(0,0)): t = (i-(n-1)/2)*gap; return (t*0.7071+off[0], -t*0.7071+off[1], 0)
def edge_fade(x,y,a=0.08,b=0.35): return sstep(a,b,edge_d(x,y))
ROCK = [(0.13,0.125,0.11),(0.16,0.153,0.135),(0.20,0.19,0.168),(0.24,0.23,0.20)]
MOSS = [(0.035,0.07,0.01),(0.08,0.15,0.02),(0.15,0.25,0.04)]
GRASS = [(0.10,0.21,0.02),(0.16,0.30,0.035),(0.23,0.39,0.05)]
GRASS_S = [(0.05,0.12,0.01),(0.08,0.16,0.013),(0.11,0.21,0.017)]
SOIL_B = [(0.20,0.09,0.03),(0.30,0.15,0.055),(0.16,0.07,0.025),(0.36,0.19,0.07),(0.24,0.12,0.045)]
SAND = [(0.40,0.28,0.13),(0.50,0.37,0.19),(0.60,0.47,0.27)]

def tile_hq(name, coll, H, mats, pos, src, n=56, mask=None, details=(), extra=None, side_mat=1, nx=None):
    bm,tl,ml,hl = new_bm2()
    fs = build_hf(bm,H,nx or n,n,mask=mask,top_layer=tl,mask_layer=ml); nb = len(fs)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    for f in fs:
        f.material_index = 0 if sum(v[tl] for v in f.verts)/len(f.verts) > 0.5 else side_mat
    for idx, fn in details:
        for f in fn(bm, hl): f.material_index = idx
    return finish_hq(name, coll, bm, nb, mats, pos, src, extra)

def wood_mat(name, cols=((0.035,0.04,0.034),(0.055,0.06,0.05),(0.085,0.09,0.075))):
    return painterly(name, list(cols), edge=(0.30,0.30,0.26), cavity=(0.01,0.01,0.008), dirt=(0.06,0.05,0.03), dirt_h=0.05,
                     scale=5, strokes=0.6, speckle=0.15, crack_lines=0.6, crack_scale=6, toplight=0.3)

def chunky_box(bm, center, size, rotz=0.0, roty=0.0, seed=0, bevel=0.025, wobble=0.008):
    res = bmesh.ops.create_cube(bm, size=1.0)
    vs = res["verts"]
    for v in vs: v.co = Vector((v.co.x*size[0], v.co.y*size[1], v.co.z*size[2]))
    edges = list({e for v in vs for e in v.link_edges})
    bres = bmesh.ops.bevel(bm, geom=list(vs)+edges, offset=bevel, segments=2, affect='EDGES', profile=0.6)
    allv = list({v for f in bres["faces"] for v in f.verts} | set(vs))
    allv = [v for v in allv if v.is_valid]
    allv = list({v for v in bm.verts if v.is_valid and v.select or False}) or allv
    fs = list({f for v in allv for f in v.link_faces})
    vv = list({v for f in fs for v in f.verts})
    R = Matrix.Translation(center) @ Matrix.Rotation(rotz,4,'Z') @ Matrix.Rotation(roty,4,'Y')
    for v in vv:
        p = v.co + Vector((0,0,0)); p += Vector((noise.noise(p*7+Vector((seed,0,0))), noise.noise(p*7+Vector((0,seed,0))), noise.noise(p*7+Vector((0,0,seed)))))*wobble
        v.co = R @ p
    return fs

# ====================================================== PADS
if BUILD == "pads":
    coll = get_coll("TRN_LevelledPads")
    E = [(0.30,0.16,0.06),(0.40,0.23,0.09),(0.50,0.32,0.14)]
    me_top = painterly("TRN_PadEarth_Top", E, edge=(0.70,0.52,0.30), cavity=(0.08,0.04,0.015), dirt=E[0], dirt_h=-1, scale=1.6, strokes=0.7, speckle=0.1, crack_lines=0.55, crack_scale=1.3, toplight=0.3)
    me_side = painterly("TRN_PadEarth_Side", [(0.20,0.10,0.04),(0.28,0.15,0.06),(0.36,0.21,0.09)], edge=(0.55,0.40,0.24), cavity=(0.05,0.025,0.01), dirt=(0.10,0.05,0.02), dirt_h=-0.25, strokes=0.5)
    def He(x,y):
        z = 0.006*nn(x,y,1.2,1) + 0.003*nn(x,y,6,2)
        # long shallow cracks (reference: 2-3 grooves)
        for (a,b,c,w) in ():
            d = abs(a*x + b*y + c)/math.hypot(a,b) + 0.02*nn(x,y,6,9)
            z -= 0.02*(1-sstep(0.0,w,d))*sstep(0.1,0.3,edge_d(x,y))
        chip = 0.04*max(0.0, nn(x,y,5,21)-0.25)*clamp(1-edge_d(x,y)/0.14)
        return z*edge_fade(x,y,0.02,0.2) + shoulder(x,y,0.12) - chip
    RESULTS["TRN_Pad_Earth"] = tile_hq("TRN_Pad_Earth", coll, He, [me_top, me_side], (-1.5,1.5,0), "TRN_LevelledPads.jpg", n=72, extra={"buildable":True})
    CW = 0.16
    def Hg(x,y):
        d = edge_d(x,y); inner = sstep(CW-0.005, CW+0.025, d)
        curb = 0.025 + shoulder(x,y,0.07) - 0.02*sstep(CW-0.045, CW, d) + 0.004*nn(x,y,8,3)
        return curb*(1-inner) + (-0.04 + 0.006*nn(x,y,6,4))*inner
    mc_top = painterly("TRN_PadCurb", [(0.48,0.44,0.33),(0.58,0.54,0.42),(0.66,0.62,0.50)], edge=(0.85,0.82,0.72), cavity=(0.10,0.09,0.07), dirt=(0.22,0.19,0.13), dirt_h=-0.15, scale=3, strokes=0.35, crack_lines=0.35, crack_scale=3)
    mg = painterly("TRN_PadGravelBed", [(0.05,0.05,0.048),(0.08,0.08,0.076),(0.11,0.11,0.105)], edge=(0.4,0.4,0.38), cavity=(0.01,0.01,0.01), dirt_h=-1, scale=14, strokes=0.2, speckle=0.5)
    mp = painterly("TRN_PadPebble", [(0.16,0.16,0.15),(0.24,0.24,0.22),(0.34,0.34,0.32),(0.42,0.41,0.38)], edge=(0.7,0.7,0.66), cavity=(0.02,0.02,0.02), dirt_h=-1, scale=9, strokes=0.15, toplight=0.4)
    def pebbles(bm, hl):
        fs = []; rnd = random.Random(4)
        for _ in range(950):
            x,y = rnd.uniform(-0.83,0.83), rnd.uniform(-0.83,0.83); r = rnd.uniform(0.018,0.04)
            res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r, matrix=Matrix.Translation((x,y,Hg(x,y)+r*0.2)) @ Matrix.Rotation(rnd.uniform(0,6.28),4,'Z') @ Matrix.Diagonal((1,rnd.uniform(0.6,1),rnd.uniform(0.45,0.7),1)))
            fs += list({f for v in res["verts"] for f in v.link_faces})
        return fs
    bm,tl,ml,hl = new_bm2(); fs = build_hf(bm,Hg,64,64,top_layer=tl,mask_layer=ml); nb=len(fs)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    for f in fs:
        c = f.calc_center_median()
        f.material_index = 1 if (edge_d(c.x,c.y) > CW+0.012 and f.normal.z > 0.5) else 0
    for f in pebbles(bm, hl): f.material_index = 2
    RESULTS["TRN_Pad_Gravel"] = finish_hq("TRN_Pad_Gravel", coll, bm, nb, [mc_top, mg, mp], (1.5,-1.5,0), "TRN_LevelledPads.jpg", {"buildable":True})

# ====================================================== SLOPES
if BUILD == "slopes":
    coll = get_coll("TRN_Slopes")
    mtop = painterly("TRN_Slope_Grass", GRASS, edge=(0.45,0.58,0.16), cavity=(0.02,0.05,0.008), dirt=GRASS[0], dirt_h=-1, scale=1.8, strokes=0.65, toplight=0.35, speckle=0.06)
    mask_mix(mtop, SAND, soft=0.12)
    mside = painterly("TRN_Slope_Soil", [(0.26,0.13,0.05),(0.33,0.18,0.07),(0.40,0.23,0.10)], edge=(0.62,0.44,0.26), cavity=(0.05,0.025,0.01), dirt=(0.12,0.06,0.02), dirt_h=-0.2,
                      strokes=0.5, bands=SOIL_B, band_scale=4.5, crack_lines=0.3, crack_scale=2, toplight=0.2)
    mbl = blade_mat("TRN_Slope_Blade", (0.08,0.18,0.015),(0.40,0.55,0.12),(0.26,0.40,0.06),1.0)
    def edge_sand(x,y,w=0.12): return 1-sstep(0.02,w,edge_d(x,y))
    def lip(bm, hl, H, count=30):
        fs=[]
        for side in range(4):
            for _ in range(count):
                t = random.uniform(-0.9,0.9); s = random.uniform(0.005,0.03)
                x,y,out = [(t,-1+s,-math.pi/2),(1-s,t,0.0),(t,1-s,math.pi/2),(-1+s,t,math.pi)][side]
                fs += blade(bm,hl,x,y,H(x,y),random.uniform(0.05,0.11),0.02,out+random.uniform(-0.6,0.6),random.uniform(0.6,1.0))
        return fs
    # ramp
    prof = lambda x: LEVEL*sstep(-0.72, 0.62, x)
    H = lambda x,y: prof(x) + 0.008*nn(x,y,1.5,4) + shoulder(x,y)
    Mk = lambda x,y: max(edge_sand(x,y), 1-sstep(-0.86,-0.66,x), 0.85*(1-sstep(0.0,0.10,1-x)))
    def d_ramp(bm,hl):
        fs = lip(bm,hl,H,22)
        for _ in range(25):
            x,y = random.uniform(-0.8,0.8), random.uniform(-0.8,0.8); fs += clump(bm,hl,H,x,y,4,0.04,0.08,0.03,0.016)
        return fs
    RESULTS["TRN_Slope_Ramp"] = tile_hq("TRN_Slope_Ramp", coll, H, [mtop, mside, mbl], row(0,3), "TRN_Slopes.jpg", n=40, nx=64, mask=Mk, details=[(2,d_ramp)], extra={"rise_m":LEVEL})
    pv = lambda x: LEVEL - (LEVEL-0.12)*(1-sstep(0.22,0.78,abs(x)))
    Hv = lambda x,y: pv(x) + 0.008*nn(x,y,1.5,5) + shoulder(x,y)
    Mv = lambda x,y: max(edge_sand(x,y), 0.95*(1-sstep(0.05,0.22,abs(x)))*sstep(0.45,0.85,abs(y)), 0.85*(1-sstep(0.03,0.12,1-abs(x))))
    def d_val(bm,hl): return lip(bm,hl,Hv,22)
    RESULTS["TRN_Slope_Valley"] = tile_hq("TRN_Slope_Valley", coll, Hv, [mtop, mside, mbl], row(1,3), "TRN_Slopes.jpg", n=40, nx=72, mask=Mv, details=[(2,d_val)], extra={"rise_m":LEVEL})
    # stairs
    NS = 6; x0, x1 = -0.80, 0.80; sw = (x1-x0)/NS
    def ps(x):
        if x <= x0: return 0.0
        if x >= x1: return LEVEL
        k = (x-x0)/sw; i = math.floor(k); fr = k-i
        return LEVEL*(i + sstep(0.84,0.99,fr))/NS
    Hs = lambda x,y: ps(x) + 0.006*nn(x,y,3,6) + shoulder(x,y)
    Ms = lambda x,y: (1.0 if abs(y) < 0.58 else 0.0) * (0.6 + 0.4*sstep(0.4,0.6,nn(x,y,3,8)+0.5))
    mw = wood_mat("TRN_Stair_Sleeper")
    def d_stairs(bm, hl):
        fs = []
        for i in range(NS):
            xr = x0 + sw*(i+0.92); zt = LEVEL*(i+1)/NS
            fs += chunky_box(bm, (xr-0.05, 0.0, zt-0.05), (0.15,1.16,0.12), rotz=random.uniform(-0.03,0.03), seed=i*3)
        L = math.hypot(x1-x0, LEVEL); ang = math.atan2(LEVEL, x1-x0)
        for k,yy in enumerate((-0.66,0.66)):
            fs += chunky_box(bm, ((x0+x1)/2, yy, LEVEL/2+0.07), (L+0.14,0.15,0.16), roty=-ang, seed=40+k)
        return fs
    def d_tufts(bm, hl):
        fs = lip(bm,hl,Hs,18)
        for i in range(NS):
            for _ in range(4):
                x = x0+sw*(i+random.uniform(0.05,0.7)); y = random.choice([-0.5,0.5,-0.2,0.25])+random.uniform(-0.08,0.08)
                fs += clump(bm,hl,Hs,x,y,4,0.04,0.08,0.03,0.016)
        return fs
    RESULTS["TRN_Slope_Stairs"] = tile_hq("TRN_Slope_Stairs", coll, Hs, [mtop, mside, mw, mbl], row(2,3), "TRN_Slopes.jpg", n=40, nx=120, mask=Ms, details=[(2,d_stairs),(3,d_tufts)], extra={"rise_m":LEVEL,"steps":NS})

# ====================================================== VOLCANO
if BUILD == "volcano":
    coll = get_coll("TRN_VolcanoIsland")
    BAS = [(0.018,0.017,0.016),(0.03,0.028,0.026),(0.045,0.041,0.037),(0.06,0.055,0.05)]
    ASH = [(0.07,0.067,0.063),(0.10,0.097,0.09),(0.14,0.135,0.125)]
    mash = painterly("TRN_Volc_Ash", ASH, edge=(0.25,0.24,0.22), cavity=(0.01,0.01,0.01), dirt=(0.05,0.03,0.02), dirt_h=-0.25, scale=1.8, strokes=0.6, speckle=0.35)
    mash_s = painterly("TRN_Volc_AshSide", [(0.035,0.025,0.02),(0.06,0.04,0.03),(0.09,0.06,0.04)], edge=(0.25,0.18,0.12), cavity=(0.01,0.008,0.006), dirt=(0.03,0.02,0.015), dirt_h=-0.2, strokes=0.5, speckle=0.3)
    Ha = lambda x,y: (0.012*nn(x,y,1.5,1)+0.005*nn(x,y,6,2))*edge_fade(x,y) + shoulder(x,y)
    def d_ashpeb(bm,hl):
        fs=[]
        for _ in range(40):
            x,y=random.uniform(-0.85,0.85),random.uniform(-0.85,0.85); r=random.uniform(0.012,0.04)
            res=bmesh.ops.create_icosphere(bm,subdivisions=1,radius=r,matrix=Matrix.Translation((x,y,Ha(x,y)+r*0.15))@Matrix.Diagonal((1,0.8,0.5,1)))
            fs+=list({f for v in res["verts"] for f in v.link_faces})
        return fs
    RESULTS["TRN_Volcano_Ash"] = tile_hq("TRN_Volcano_Ash", coll, Ha, [mash, mash_s, mash], row(0,4,2.6,(0,0)), "TRN_VolcanoIsland.jpg", n=48, details=[(2,d_ashpeb)])
    # lava plates: domed basalt plates, each its own tone, glowing deep cracks
    rs = random.Random(9); seeds = [(rs.uniform(-1,1), rs.uniform(-1,1)) for _ in range(12)]
    def plate_info(x,y):
        ds = sorted((math.hypot(x-sx,y-sy), i) for i,(sx,sy) in enumerate(seeds))
        return ds[1][0]-ds[0][0], ds[0][1]
    def Hl(x,y):
        g, pid = plate_info(x+0.04*nn(x,y,3,4), y+0.04*nn(x,y,3,5))
        dome = 0.035*sstep(0.0, 0.32, g) + 0.012*nn(x,y,2.5,pid)
        crack = -0.085*(1-sstep(0.0, 0.05, g))
        return (dome + crack + 0.01*((pid*37)%7)/7)*edge_fade(x,y,0.02,0.16) + shoulder(x,y)
    mpl = painterly("TRN_Volc_Plate", BAS, edge=(0.22,0.18,0.15), cavity=(0.006,0.004,0.003), dirt=(0.25,0.08,0.02), dirt_h=-0.28, scale=2.2, strokes=0.5, speckle=0.3, toplight=0.45,
                    emission=glow_emission(strength=7.0))
    mpl_s = painterly("TRN_Volc_PlateSide", [(0.03,0.02,0.015),(0.05,0.03,0.02),(0.10,0.04,0.015)], edge=(0.45,0.2,0.06), cavity=(0.01,0.006,0.004), dirt=(0.3,0.09,0.02), dirt_h=-0.25, strokes=0.5,
                      emission=glow_emission(strength=4.0, attr_name="glow"))
    bm,tl,ml,hl = new_bm2(); gl = bm.verts.layers.float["glow"]
    fs = build_hf(bm,Hl,84,84,top_layer=tl,mask_layer=ml); nb=len(fs)
    for v in bm.verts:
        if v[tl] > 0.5:
            g,_ = plate_info(v.co.x+0.04*nn(v.co.x,v.co.y,3,4), v.co.y+0.04*nn(v.co.x,v.co.y,3,5)); v[gl] = 1-sstep(0.0, 0.06, g)
        else:
            v[gl] = 0.0
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    for f in fs: f.material_index = 0 if sum(v[tl] for v in f.verts)/len(f.verts) > 0.5 else 1
    RESULTS["TRN_Volcano_LavaPlates"] = finish_hq("TRN_Volcano_LavaPlates", coll, bm, nb, [mpl, mpl_s], row(1,4), "TRN_VolcanoIsland.jpg")
    # lava rocks with glowing veins
    mlr = painterly("TRN_Volc_LavaRock", BAS, edge=(0.25,0.2,0.16), cavity=(0.005,0.004,0.003), dirt=(0.25,0.08,0.02), dirt_h=0.12, scale=2.0, strokes=0.45, speckle=0.25, toplight=0.4,
                    emission=glow_emission(strength=5.0, lines=1.6))
    mdisc = painterly("TRN_Volc_AshDisc", ASH, edge_amt=0.0, cav_amt=0.3, dirt_h=-1, speckle=0.4, strokes=0.4)
    def ash_disc(bm, r, seed):
        N=48; c=bm.verts.new((0,0,0.02)); ring=[]; lip=[]
        for i in range(N):
            a=2*math.pi*i/N; k=1+0.12*noise.noise(Vector((math.cos(a)*2,math.sin(a)*2,seed)))
            ring.append(bm.verts.new((r*k*math.cos(a), r*0.85*k*math.sin(a), 0.02))); lip.append(bm.verts.new((r*k*1.05*math.cos(a), r*0.85*k*1.05*math.sin(a), 0.0)))
        return [bm.faces.new((c,ring[i],ring[(i+1)%N])) for i in range(N)] + [bm.faces.new((ring[i],lip[i],lip[(i+1)%N],ring[(i+1)%N])) for i in range(N)]
    ROCKS = [("TRN_LavaRock_Small",[dict(center=(0,0,0),size=(0.36,0.32,0.34),seed=301,K=11,boxy=0.25,flat_top=0.1)],0.55),
             ("TRN_LavaRock_Low",[dict(center=(0,0,0),size=(0.60,0.48,0.38),seed=302,K=12,boxy=0.2,flat_top=0.12)],0.8),
             ("TRN_LavaRock_Tall",[dict(center=(0,0,0),size=(0.40,0.38,0.85),seed=303,K=13,boxy=0.18)],0.65),
             ("TRN_LavaRock_Cube",[dict(center=(0,0,0),size=(0.40,0.36,0.40),seed=304,K=10,boxy=0.3,flat_top=0.12)],0.6)]
    for k,(name,parts,dr) in enumerate(ROCKS):
        bm,tl,ml,hl = new_bm2()
        for p in parts: rock_hq(bm, **p)
        for f in ash_disc(bm, dr, 500+k): f.material_index = 1
        RESULTS[name] = make_obj_hq(name, coll, bm, [mlr, mdisc], row(k,4,2.0,(-1.7,-1.7)), "TRN_VolcanoIsland.jpg")
    # mini volcano: ridged flanks, lava runnels, crater glow, smoke preview volume
    bm,tl,ml,hl = new_bm2(); gl = bm.verts.layers.float["glow"]
    SEG, NR = 48, 22; rings=[]
    for k in range(NR+1):
        t=k/NR; h=t*1.05; base=1.0*(1-t)**1.3 + 0.2*t; ring=[]
        for i in range(SEG):
            a=2*math.pi*i/SEG
            ridge = 0.12*abs(math.sin(a*6 + 1.2*nn(t*2,i*0.2,1.0,7)))**0.6*(1-t)
            r = base + ridge + 0.035*nn(math.cos(a)*3, math.sin(a)*3, 1.0, k)
            v = bm.verts.new((r*math.cos(a), r*math.sin(a), h))
            run = max(0.0, 1-abs(math.sin(a*3+0.5))*6)   # three lava runnels down the flanks
            v[gl] = (run*(1-t)**0.3*0.9 if t < 0.95 else 0) + (0.0 if t < 0.92 else 0.7)
            ring.append(v)
        rings.append(ring)
    crater=[]
    for i in range(SEG):
        a=2*math.pi*i/SEG; v=bm.verts.new((0.12*math.cos(a),0.12*math.sin(a),0.86)); v[gl]=1.0; crater.append(v)
    fs=[]
    for ra,rb in zip(rings[:-1]+[rings[-1]], rings[1:]+[crater]):
        for i in range(SEG):
            j=(i+1)%SEG; fs.append(bm.faces.new((ra[i],ra[j],rb[j],rb[i])))
    fs.append(bm.faces.new(list(reversed(rings[0])))); fs.append(bm.faces.new(crater))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    for f in ash_disc(bm, 1.35, 777): f.material_index = 1
    msm = volume_mat("TRN_Volc_SmokePreview", (0.55,0.55,0.56), 2.5, 2.5)
    sm=[]
    for (cx,cy,cz,s) in ((0,0,1.25,0.22),(0.08,0.05,1.55,0.30),(0.18,0.1,1.9,0.36),(0.25,0.2,2.25,0.40)):
        sm += blob(bm,(cx,cy,cz),(s,s*0.9,s*0.8),2)
    for f in sm: f.material_index = 2
    RESULTS["TRN_Volcano_Mini"] = make_obj_hq("TRN_Volcano_Mini", coll, bm, [mlr, mdisc, msm], row(3,4,2.6,(1.0,1.0)), "TRN_VolcanoIsland.jpg", {"vfx_socket":"SOCKET_Smoke (0,0,0.9); smoke mesh is preview only"}, sharp=45)

# ====================================================== SWAMP
if BUILD == "swamp":
    coll = get_coll("TRN_SwampIsland")
    PEAT = [(0.010,0.011,0.007),(0.018,0.019,0.012),(0.03,0.031,0.02)]
    mpeat = painterly("TRN_Swamp_Peat", PEAT, edge=(0.12,0.12,0.08), cavity=(0.003,0.003,0.002), dirt=PEAT[0], dirt_h=-1, scale=2.2, strokes=0.55, speckle=0.3, wet=(0.18,0.55), toplight=0.25)
    mask_mix(mpeat, [(0.03,0.07,0.01),(0.07,0.14,0.02),(0.12,0.22,0.03)], soft=0.1)
    mpside = painterly("TRN_Swamp_PeatSide", [(0.012,0.010,0.006),(0.022,0.018,0.011),(0.035,0.028,0.017)], edge=(0.12,0.1,0.06), cavity=(0.003,0.003,0.002), dirt=(0.01,0.01,0.006), dirt_h=-0.2, strokes=0.5, wet=(0.25,0.5))
    mmoss = painterly("TRN_Swamp_Moss", [(0.03,0.07,0.01),(0.07,0.15,0.02),(0.13,0.25,0.035),(0.2,0.33,0.05)], edge=(0.32,0.48,0.10), cavity=(0.005,0.015,0.002), dirt_h=-1, scale=7, strokes=0.4, speckle=0.25, toplight=0.4)
    mleaf = [painterly("TRN_Swamp_Leaf%d" % i, c, edge=e, cavity=(0.03,0.015,0.005), dirt_h=-1, scale=12, strokes=0.3, speckle=0.1, edge_amt=0.3) for i,(c,e) in enumerate((
        ([(0.16,0.07,0.02),(0.24,0.11,0.03)],(0.45,0.25,0.08)), ([(0.30,0.14,0.03),(0.40,0.20,0.05)],(0.6,0.38,0.12)), ([(0.08,0.04,0.015),(0.13,0.06,0.02)],(0.3,0.16,0.06))))]
    mfern = blade_mat("TRN_Swamp_Fern", (0.02,0.06,0.008),(0.16,0.34,0.05),(0.08,0.2,0.03),1.0)
    mtwig = painterly("TRN_Swamp_Twig", [(0.06,0.035,0.015),(0.10,0.06,0.025)], edge=(0.3,0.2,0.1), dirt_h=-1, scale=10)
    Hm = lambda x,y: (0.016*nn(x,y,1.6,2)+0.006*nn(x,y,5,3))*edge_fade(x,y) + shoulder(x,y)
    Mm = lambda x,y: sstep(0.52,0.62,nn(x,y,2.4,9)+0.5) + (1-sstep(0.03,0.16,edge_d(x,y)))*sstep(0.45,0.55,nn(x,y,5,10)+0.5)
    def curled_leaf(bm, x, y, L, z0):
        a=random.uniform(0,6.28); curl=random.uniform(0.15,0.45); vs=[]
        for (u,v) in [(-1,0),(-0.55,0.36),(0,0.46),(0.55,0.34),(1,0),(0.55,-0.34),(0,-0.46),(-0.55,-0.36)]:
            lift = curl*abs(v)*L*1.4 + 0.25*curl*max(0,u)*L
            vs.append(bm.verts.new((x+(u*math.cos(a)-v*0.5*math.sin(a))*L, y+(u*math.sin(a)+v*0.5*math.cos(a))*L, z0+lift)))
        c = bm.verts.new((x, y, z0+0.004)); return [bm.faces.new((c, vs[i], vs[(i+1)%8])) for i in range(8)]
    def frond2(bm, hl, x,y,z, ang, L):
        fs=[]; n=12; dx,dy=math.cos(ang),math.sin(ang); px,py=-dy,dx
        pts=[Vector((x+dx*L*t, y+dy*L*t, z+L*(0.6*t-0.55*t*t))) for t in [k/n for k in range(n+1)]]
        for k in range(n):
            a,b=pts[k],pts[k+1]; t=k/n; ww=0.045*(1-t*0.75)
            for s in (-1,1):
                tip=(a+b)/2+Vector((px*s*ww*2.4+dx*ww*0.8, py*s*ww*2.4+dy*ww*0.8, -0.012))
                va,vb,vc=bm.verts.new(a),bm.verts.new(b),bm.verts.new(tip); va[hl]=t; vb[hl]=t; vc[hl]=min(1,t+0.35)
                fs.append(bm.faces.new((va,vb,vc)))
        return fs
    def d_moss(bm,hl):
        fs=[]; rnd=random.Random(5)
        for _ in range(26):
            x,y=rnd.uniform(-0.85,0.85),rnd.uniform(-0.85,0.85)
            if Mm(x,y) < 0.3 and rnd.random() < 0.6: continue
            s=rnd.uniform(0.06,0.16)
            res=bmesh.ops.create_icosphere(bm,subdivisions=3,radius=1,matrix=Matrix.Translation((x,y,Hm(x,y)-s*0.12))@Matrix.Diagonal((s,s*rnd.uniform(0.7,1),s*0.38,1)))
            for v in res["verts"]: v.co += v.co.normalized()*0.0 + Vector((0,0,0.012*noise.noise(v.co*25)))
            fs+=list({f for v in res["verts"] for f in v.link_faces})
        return fs
    def d_leaves(bm,hl):
        out={2:[],3:[],4:[]}; rnd=random.Random(6)
        for _ in range(85):
            x,y=rnd.uniform(-0.88,0.88),rnd.uniform(-0.88,0.88); k=rnd.choice((2,3,3,4))
            out[k] += curled_leaf(bm,x,y,rnd.uniform(0.035,0.06),Hm(x,y)+0.006)
        return out
    def d_ferns(bm,hl):
        fs=[]
        for (x,y) in [(-0.58,0.62),(0.58,0.38),(-0.18,-0.55),(0.66,-0.62),(-0.68,-0.05)]:
            z=Hm(x,y)
            for k in range(9): fs += frond2(bm,hl,x,y,z,k*2*math.pi/9+random.uniform(-0.25,0.25),random.uniform(0.26,0.38))
        return fs
    def d_twigs(bm,hl):
        fs=[]
        for _ in range(9):
            x,y=random.uniform(-0.8,0.8),random.uniform(-0.8,0.8); a=random.uniform(0,3.14); L=random.uniform(0.12,0.25)
            fs += box(bm,(x,y,Hm(x,y)+0.008),(L,0.012,0.012),Matrix.Rotation(a,4,'Z'))
        return fs
    bm,tl,ml,hl = new_bm2(); fs = build_hf(bm,Hm,64,64,mask=Mm,top_layer=tl,mask_layer=ml); nb=len(fs)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    for f in fs: f.material_index = 0 if sum(v[tl] for v in f.verts)/len(f.verts) > 0.5 else 1
    for f in d_moss(bm,hl): f.material_index = 5
    for k,lst in d_leaves(bm,hl).items():
        for f in lst: f.material_index = k
    for f in d_ferns(bm,hl): f.material_index = 6
    for f in d_twigs(bm,hl): f.material_index = 7
    RESULTS["TRN_Swamp_MossGround"] = finish_hq("TRN_Swamp_MossGround", coll, bm, nb, [mpeat, mpside]+mleaf+[mmoss, mfern, mtwig], row(0,3), "TRN_SwampIsland.jpg")
    # organic algae pool (not square): basin follows a noisy blob, mossy overhang banks
    def pond_e(x,y): return ((x/0.80)**2 + ((y+0.02)/0.74)**2) * (1+0.22*nn(x,y,2.2,31))
    def Hp(x,y):
        e = pond_e(x,y); basin = 1-sstep(0.85,1.15,e)
        z = (0.012*nn(x,y,2,4))*(1-basin) - 0.17*basin
        return z*edge_fade(x,y,0.02,0.12) + shoulder(x,y)
    Mp = lambda x,y: sstep(0.95,1.25,pond_e(x,y))*sstep(0.4,0.6,nn(x,y,3,12)+0.5)
    mpool = water_hq("TRN_Swamp_PoolWater", (0.07,0.17,0.08),(0.035,0.11,0.05),(0.015,0.05,0.025), foam=(0.35,0.5,0.25), strokes=0.35, ripple='swirl', depth_range=0.16,
                     algae=[(0.10,0.22,0.03),(0.18,0.34,0.06)], sky=(0.45,0.6,0.5), shore_foam=0.5)
    def d_pool(bm,hl): return water_volume_hq(bm, lambda x,y: pond_e(x,y) < 1.12, Hp, -0.05, n=60)
    def d_algae(bm,hl):
        fs=[]; rnd=random.Random(13)
        for _ in range(7):
            cx,cy=rnd.uniform(-0.5,0.5),rnd.uniform(-0.45,0.45)
            if pond_e(cx,cy) > 0.7: continue
            N=14; c=bm.verts.new((cx,cy,-0.046)); ring=[]
            for i in range(N):
                a=2*math.pi*i/N; r=rnd.uniform(0.05,0.13)*(1+0.3*noise.noise(Vector((math.cos(a)*2,math.sin(a)*2,cx*9))))
                ring.append(bm.verts.new((cx+r*math.cos(a), cy+r*0.8*math.sin(a), -0.046)))
            fs += [bm.faces.new((c,ring[i],ring[(i+1)%N])) for i in range(N)]
        return fs
    RESULTS["TRN_Swamp_Pool"] = tile_hq("TRN_Swamp_Pool", coll, Hp, [mpeat, mpside, mpool, mmoss], row(1,3), "TRN_SwampIsland.jpg", n=64, mask=Mp,
                                        details=[(2,d_pool),(3,d_algae),(3,d_moss.__class__ and (lambda bm,hl: []))])
    # reed marsh: glossy grey mud, blue sky puddles, reeds + cattails
    MUD = [(0.035,0.03,0.022),(0.06,0.05,0.035),(0.09,0.075,0.05)]
    mmud = painterly("TRN_Swamp_MarshMud", MUD, edge=(0.25,0.22,0.17), cavity=(0.01,0.008,0.006), dirt=MUD[0], dirt_h=-1, scale=2.0, strokes=0.55, speckle=0.2, wet=(0.08,0.3), toplight=0.3)
    mmud_s = painterly("TRN_Swamp_MarshSide", [(0.025,0.02,0.015),(0.04,0.033,0.024)], edge=(0.2,0.17,0.13), dirt_h=-0.2, strokes=0.5, wet=(0.15,0.35))
    mpw = water_hq("TRN_Swamp_MarshWater", (0.16,0.24,0.32),(0.10,0.17,0.25),(0.06,0.11,0.17), strokes=0.35, ripple='rings', depth_range=0.04, sky=(0.5,0.62,0.72), shore_foam=0.2)
    mreed = blade_mat("TRN_Swamp_Reed", (0.10,0.07,0.03),(0.45,0.36,0.16),(0.32,0.25,0.10),1.0)
    mcat = painterly("TRN_Swamp_Cattail", [(0.10,0.045,0.018),(0.16,0.07,0.025)], edge=(0.35,0.18,0.07), dirt_h=-1, scale=14)
    PUD = [(-0.35,0.38,0.24,0.13),(0.45,0.12,0.2,0.11),(0.05,-0.45,0.18,0.1),(-0.6,-0.3,0.12,0.07),(0.6,0.6,0.1,0.06)]
    def in_pud(x,y,k=1.0): return min((((x-cx)/rx)**2+((y-cy)/ry)**2)*(1+0.25*nn(x,y,4,int(cx*10))) for (cx,cy,rx,ry) in PUD) < k
    def Hr(x,y):
        z = 0.016*nn(x,y,1.8,5)+0.006*nn(x,y,6,6)
        for (cx,cy,rx,ry) in PUD:
            e=(((x-cx)/rx)**2+((y-cy)/ry)**2)*(1+0.25*nn(x,y,4,int(cx*10))); w=1-sstep(0.8,1.3,e); z=z*(1-w)-0.03*w
        return z*edge_fade(x,y) + shoulder(x,y)
    def d_mw(bm,hl): return water_volume_hq(bm, lambda x,y: in_pud(x,y,1.15), Hr, -0.012, n=64, skirt=False)
    def d_reeds(bm,hl):
        fs=[]; rnd=random.Random(21)
        for _ in range(9):
            cx,cy=rnd.uniform(-0.75,0.75),rnd.uniform(-0.75,0.75)
            for _ in range(5): fs += blade(bm,hl,cx+rnd.uniform(-0.05,0.05),cy+rnd.uniform(-0.05,0.05),Hr(cx,cy),rnd.uniform(0.22,0.48),0.024,rnd.uniform(0,6.28),rnd.uniform(0.0,0.18))
        return fs
    def d_cat(bm,hl):
        fs=[]; rnd=random.Random(22)
        for _ in range(8):
            x,y=rnd.uniform(-0.75,0.75),rnd.uniform(-0.75,0.75); h=rnd.uniform(0.38,0.55); tilt=(rnd.uniform(-0.12,0.12),rnd.uniform(-0.12,0.12))
            fs += cyl(bm,x,y,Hr(x,y),0.006,h,seg=5,tilt=tilt)
            fs += cyl(bm,x+math.sin(tilt[1])*(h-0.06),y-math.sin(tilt[0])*(h-0.06),Hr(x,y)+h-0.11,0.02,0.10,seg=8)
        return fs
    RESULTS["TRN_Swamp_ReedMarsh"] = tile_hq("TRN_Swamp_ReedMarsh", coll, Hr, [mmud, mmud_s, mpw, mreed, mcat], row(2,3), "TRN_SwampIsland.jpg", n=64,
                                             details=[(2,d_mw),(3,d_reeds),(4,d_cat)])

# ====================================================== DESERT
if BUILD == "desert":
    coll = get_coll("TRN_DesertIsland")
    SO = [(0.50,0.18,0.05),(0.62,0.28,0.09),(0.72,0.38,0.14)]
    SP = [(0.55,0.22,0.15),(0.66,0.31,0.21),(0.75,0.43,0.30)]
    SS = [(0.34,0.12,0.035),(0.44,0.18,0.06),(0.52,0.24,0.09)]
    ms = painterly("TRN_Desert_Sand", SO, edge=(0.85,0.55,0.28), cavity=(0.18,0.06,0.02), dirt=SO[0], dirt_h=-1, scale=1.6, strokes=0.6, speckle=0.15, toplight=0.4, edge_amt=0.4)
    mp = painterly("TRN_Desert_SandPink", SP, edge=(0.85,0.6,0.5), cavity=(0.2,0.07,0.05), dirt=SP[0], dirt_h=-1, scale=1.6, strokes=0.6, speckle=0.15, toplight=0.4)
    mside = painterly("TRN_Desert_Side", SS, edge=(0.7,0.42,0.2), cavity=(0.12,0.04,0.012), dirt=(0.25,0.08,0.02), dirt_h=-0.25, strokes=0.5, speckle=0.35)
    Hrip = lambda x,y: (0.014*math.sin((x*0.6+y*0.8)*15 + 1.4*nn(x,y,1.5,3)) + 0.01*nn(x,y,1.2,4))*edge_fade(x,y) + shoulder(x,y)
    RESULTS["TRN_Desert_Ripples"] = tile_hq("TRN_Desert_Ripples", coll, Hrip, [ms, mside], row(0,4), "TRN_DesertIsland.jpg", n=84)
    def dune(x,y,h,cx,amp,freq,lee=0.22,wind=1.1):
        crest = cx + amp*math.sin(y*freq); d = x-crest
        base = h*(1-sstep(0.0,lee,d)) if d > 0 else h*sstep(-wind,0.0,d)
        return base + 0.006*math.sin((x*0.9+y*0.4)*22)*sstep(-wind,0.0,d)*(1 if d < 0 else 0)
    H2 = lambda x,y: dune(x,y,0.16,0.15,0.25,1.4)*edge_fade(x,y,0.05,0.4) + shoulder(x,y)
    H3 = lambda x,y: dune(x,y,0.42,0.05,0.35,1.7,0.3,1.3)*edge_fade(x,y,0.04,0.3) + shoulder(x,y)
    H4 = lambda x,y: dune(y,x,0.34,0.10,0.3,1.3,0.28,1.2)*edge_fade(x,y,0.04,0.3) + shoulder(x,y)
    RESULTS["TRN_Desert_DuneLow"]  = tile_hq("TRN_Desert_DuneLow",  coll, H2, [mp, mside], row(1,4), "TRN_DesertIsland.jpg", n=72)
    RESULTS["TRN_Desert_DuneHigh"] = tile_hq("TRN_Desert_DuneHigh", coll, H3, [ms, mside], row(2,4), "TRN_DesertIsland.jpg", n=72)
    RESULTS["TRN_Desert_DuneRidge"]= tile_hq("TRN_Desert_DuneRidge",coll, H4, [ms, mside], row(3,4), "TRN_DesertIsland.jpg", n=72)
    BANDS = [(0.48,0.17,0.06),(0.66,0.34,0.13),(0.55,0.20,0.17),(0.78,0.52,0.24),(0.60,0.26,0.10),(0.70,0.40,0.30)]
    mstone = painterly("TRN_Desert_Sandstone", [(0.52,0.22,0.08),(0.62,0.30,0.12),(0.72,0.40,0.18)], edge=(0.95,0.72,0.42), cavity=(0.12,0.04,0.015), dirt=(0.4,0.15,0.05), dirt_h=0.1,
                       scale=2.0, strokes=0.4, crack_lines=0.6, crack_scale=2.5, bands=BANDS, band_scale=5.5, toplight=0.45, edge_amt=0.5)
    mdisc = painterly("TRN_Desert_Disc", SO, edge_amt=0.0, cav_amt=0.3, dirt_h=-1, strokes=0.5, speckle=0.15)
    def sand_disc2(bm, r, seed):
        N=56; c=bm.verts.new((0,0,0.03)); ring=[]; lip=[]
        for i in range(N):
            a=2*math.pi*i/N; k=1+0.06*noise.noise(Vector((math.cos(a)*2,math.sin(a)*2,seed)))
            ring.append(bm.verts.new((r*k*math.cos(a), r*0.85*k*math.sin(a), 0.03))); lip.append(bm.verts.new((r*k*1.04*math.cos(a), r*0.85*k*1.04*math.sin(a), 0.0)))
        return [bm.faces.new((c,ring[i],ring[(i+1)%N])) for i in range(N)] + [bm.faces.new((ring[i],lip[i],lip[(i+1)%N],ring[(i+1)%N])) for i in range(N)]
    MESAS = [("TRN_Desert_Mesa_Small", [(0,0,0.66,0.58,5)], None, 1.05),
             ("TRN_Desert_Mesa_Arch", [(-0.55,0,0.55,0.66,5),(0.58,0.04,0.58,0.70,5)], True, 1.55)]
    for k,(name,stacks,arch,dr) in enumerate(MESAS):
        bm,tl,ml,hl = new_bm2()
        for si,(cx,cy,sx,sy,nl) in enumerate(stacks):
            for l in range(nl):
                s = 1 - 0.06*l + 0.06*random.uniform(-1,1)
                rock_hq(bm, center=(cx+random.uniform(-0.06,0.06),cy+random.uniform(-0.05,0.05),l*0.23), size=(sx*s,sy*s,0.15), seed=600+k*50+si*10+l,
                        K=10, boxy=0.32, flat_top=0.25, dmin=0.62, sink=0.0, rot=random.uniform(-0.2,0.2))
        if arch:
            for l in range(2):
                rock_hq(bm, center=(0.02,0.02,5*0.23+l*0.2), size=(1.25-0.12*l,0.74,0.13), seed=777+l, K=10, boxy=0.32, flat_top=0.25, sink=0.0)
        for f in sand_disc2(bm, dr, 900+k): f.material_index = 1
        RESULTS[name] = make_obj_hq(name, coll, bm, [mstone, mdisc], row(k,2,3.4,(-2.1,-2.1)), "TRN_DesertIsland.jpg", sharp=30)

# ====================================================== BEACH
if BUILD == "beach":
    coll = get_coll("TRN_BeachShore")
    DRY = [(0.62,0.50,0.30),(0.72,0.60,0.38),(0.80,0.70,0.48)]
    msand = painterly("TRN_Beach_Sand", DRY, edge=(0.92,0.86,0.70), cavity=(0.25,0.18,0.09), dirt=DRY[0], dirt_h=-1, scale=1.6, strokes=0.55, speckle=0.12, toplight=0.3)
    mask_mix(msand, [(0.36,0.26,0.13),(0.45,0.34,0.18)], soft=0.1)          # wet sand band
    mside = painterly("TRN_Beach_Side", [(0.26,0.18,0.09),(0.36,0.26,0.14),(0.46,0.35,0.20)], edge=(0.62,0.5,0.32), cavity=(0.06,0.04,0.02), dirt=(0.14,0.1,0.05), dirt_h=-0.25, strokes=0.5, bands=[(0.30,0.21,0.11),(0.42,0.31,0.17),(0.24,0.17,0.09)], band_scale=6)
    msea = water_hq("TRN_Beach_Sea", (0.30,0.78,0.74),(0.06,0.50,0.62),(0.02,0.22,0.38), strokes=0.4, ripple='swirl', depth_range=0.24, sky=(0.75,0.92,0.95), shore_foam=1.0)
    mshell = painterly("TRN_Beach_Shell", [(0.55,0.32,0.26),(0.75,0.55,0.45)], edge=(0.95,0.85,0.8), dirt_h=-1, scale=20)
    ZW = -0.06
    def shore_tile(name, i, shore):
        Hs = lambda x,y: (0.04 - 0.30*sstep(-0.15,0.40, x - shore(y))) + 0.008*nn(x,y,2,6) + 0.005*math.sin((x*0.3+y)*26)*(1-sstep(-0.3,0.0,x-shore(y))) + shoulder(x,y)*(1 if x-shore(y) < -0.05 else 0.25)
        Mw = lambda x,y: (1-sstep(-0.30,-0.02, -(x-shore(y))-0.0))*sstep(-0.5,-0.25,x-shore(y)) if x-shore(y) < 0 else 1.0
        def sea(bm,hl): return water_volume_hq(bm, lambda x,y: x - shore(y) > -0.3, Hs, ZW, n=60)
        def shells(bm,hl):
            fs=[]; rnd=random.Random(i)
            for _ in range(3):
                y = rnd.uniform(-0.65,0.65); x = shore(y) - rnd.uniform(0.45,0.8)
                res=bmesh.ops.create_icosphere(bm,subdivisions=2,radius=0.032,matrix=Matrix.Translation((x,y,Hs(x,y)+0.006))@Matrix.Rotation(rnd.uniform(0,6),4,'Z')@Matrix.Diagonal((1,0.8,0.32,1)))
                fs+=list({f for v in res["verts"] for f in v.link_faces})
            return fs
        RESULTS[name] = tile_hq(name, coll, Hs, [msand, mside, msea, mshell], row(i,4), "TRN_BeachShore.jpg", n=64, mask=Mw, details=[(2,sea),(3,shells)], extra={"sea_level_m":ZW,"sea_side":"+X"})
    shore_tile("TRN_Beach_Straight", 0, lambda y: 0.05*math.sin(y*2.0))
    shore_tile("TRN_Beach_CurveA", 1, lambda y: 0.30*math.sin(y*1.6))
    shore_tile("TRN_Beach_CurveB", 2, lambda y: -0.25*math.sin(y*1.6+0.6)+0.1)
    GR2 = [(0.20,0.26,0.10),(0.30,0.36,0.16)]
    mring = painterly("TRN_Beach_RingSand", DRY, edge=(0.92,0.86,0.70), cavity=(0.25,0.18,0.09), dirt=DRY[0], dirt_h=-1, scale=1.6, strokes=0.55, toplight=0.3)
    mask_mix(mring, GR2, soft=0.12)
    mpost = wood_mat("TRN_Beach_Post", ((0.05,0.055,0.045),(0.08,0.085,0.07),(0.12,0.12,0.10)))
    mbl = blade_mat("TRN_Beach_Grass", (0.10,0.16,0.04),(0.42,0.48,0.22),(0.28,0.34,0.12),1.0)
    Hc = lambda x,y: 0.01*nn(x,y,1.5,8)*edge_fade(x,y) + shoulder(x,y)
    Mc = lambda x,y: (1-sstep(0.04,0.3,edge_d(x,y)))*sstep(0.35,0.55,nn(x,y,3,4)+0.5) + (1-sstep(0.02,0.1,edge_d(x,y)))
    def fence(bm,hl):
        fs=[]; N=16; Rr=0.62; pts=[]
        for k in range(N):
            a=2*math.pi*k/N; x,y=Rr*math.cos(a), Rr*math.sin(a); pts.append((x,y))
            fs += chunky_box(bm,(x,y,Hc(x,y)+0.15),(0.08,0.08,0.36+0.05*random.uniform(-1,1)),rotz=a,seed=k,bevel=0.018)
        for k in range(N):
            (x0,y0),(x1,y1)=pts[k],pts[(k+1)%N]; L=math.hypot(x1-x0,y1-y0); a=math.atan2(y1-y0,x1-x0)
            for zr in (0.12,0.25): fs += chunky_box(bm,((x0+x1)/2,(y0+y1)/2,zr),(L,0.04,0.045),rotz=a,seed=100+k,bevel=0.01,wobble=0.004)
        return fs
    def tufts(bm,hl):
        fs=[]
        for _ in range(22):
            t=random.uniform(-0.9,0.9); s=random.choice([(t,-0.9),(t,0.9),(-0.9,t),(0.9,t)])
            fs += clump(bm,hl,Hc,s[0],s[1],4,0.04,0.09,0.03,0.014)
        return fs
    RESULTS["TRN_Beach_FenceRing"] = tile_hq("TRN_Beach_FenceRing", coll, Hc, [mring, mside, mpost, mbl], row(3,4), "TRN_BeachShore.jpg", n=56, mask=Mc, details=[(2,fence),(3,tufts)])

# ====================================================== PONDS
if BUILD == "ponds":
    coll = get_coll("TRN_Ponds")
    BANK = [(0.20,0.12,0.055),(0.28,0.18,0.09),(0.37,0.26,0.14)]
    mbank = painterly("TRN_Pond_Bank", BANK, edge=(0.72,0.56,0.36), cavity=(0.06,0.03,0.012), dirt=(0.16,0.09,0.04), dirt_h=-0.06, scale=2.4, strokes=0.55, speckle=0.15, toplight=0.35, crack_lines=0.25, crack_scale=3)
    mask_mix(mbank, [(0.08,0.16,0.02),(0.14,0.26,0.04)], soft=0.1)
    mw = water_hq("TRN_Pond_Water", (0.12,0.45,0.40),(0.04,0.30,0.30),(0.015,0.14,0.15), strokes=0.55, ripple='swirl', depth_range=0.10, sky=(0.7,0.88,0.88), shore_foam=0.5)
    mr = painterly("TRN_Pond_Stone", ROCK, edge=(0.55,0.53,0.48), cavity=(0.02,0.018,0.015), moss=MOSS, moss_amt=0.4, scale=2.0, strokes=0.3, crack_lines=0.5)
    mbl = blade_mat("TRN_Pond_Reed", (0.06,0.12,0.02),(0.32,0.46,0.10),(0.20,0.30,0.06),1.0)
    mcat = painterly("TRN_Pond_Cattail", [(0.10,0.045,0.018),(0.16,0.07,0.025)], edge=(0.35,0.18,0.07), dirt_h=-1, scale=14)
    for k,(R0,sd,elong) in enumerate([(0.72,1,1.25),(1.0,2,1.5),(1.3,3,1.45)]):
        bm,tl,ml,hl = new_bm2(); dl = bm.verts.layers.float["depth"]
        NR, NA = 18, 80
        def rad(a, R0=R0, sd=sd): return R0*(1+0.15*nn(math.cos(a)*1.5, math.sin(a)*1.5, 1.0, sd) + 0.05*nn(math.cos(a)*4, math.sin(a)*4, 1.0, sd+2))
        def P(t,a, elong=elong, rad=rad): r = rad(a)*t; return (r*math.cos(a)*elong**0.5, r*math.sin(a)/elong**0.5)
        def prof(t,a, sd=sd):
            rim = 0.12 + 0.035*nn(math.cos(a)*3, math.sin(a)*3, 1.0, sd+5)
            if t < 0.70: return -0.13 + 0.06*t
            if t < 0.84: return -0.09 + (rim+0.09)*sstep(0.70,0.84,t)
            return rim*(1-sstep(0.84,1.0,t))
        rings=[]
        for i in range(NR+1):
            t=i/NR; ring=[]
            for j in range(NA):
                a=2*math.pi*j/NA; x,y=P(max(t,0.02),a); v=bm.verts.new((x,y,prof(t,a))); v[tl]=1.0
                v[ml] = sstep(0.84,0.9,t)*(1-sstep(0.95,1.0,t))*sstep(-0.15,0.35,nn(math.cos(a)*2.2,math.sin(a)*2.2,1.0,sd+9))
                ring.append(v)
            rings.append(ring)
        blk=[]
        for a_,b_ in zip(rings[:-1],rings[1:]):
            for j in range(NA):
                q=(j+1)%NA; blk.append(bm.faces.new((a_[j],a_[q],b_[q],b_[j])))
        blk.append(bm.faces.new(rings[0]))
        low=[]
        for v in rings[-1]:
            nv=bm.verts.new((v.co.x*0.985, v.co.y*0.985, -0.14)); nv[tl]=0.0; low.append(nv)
        for j in range(NA):
            q=(j+1)%NA; blk.append(bm.faces.new((rings[-1][j],low[j],low[q],rings[-1][q])))
        blk.append(bm.faces.new(list(reversed(low))))
        bmesh.ops.recalc_face_normals(bm, faces=blk)
        # water: polar disc inside the basin with depth attribute
        ZWp = -0.04; wr=[]
        for i in range(1, 13):
            t = 0.80*i/12; ring=[]
            for j in range(NA):
                a=2*math.pi*j/NA; x,y=P(t,a); v=bm.verts.new((x,y,ZWp+0.003*noise.noise(Vector((x*6,y*6,sd))))); v[dl]=max(0.0, ZWp-prof(t,a)); ring.append(v)
            wr.append(ring)
        c=bm.verts.new((0,0,ZWp)); c[dl]=ZWp-prof(0,0)
        wf=[bm.faces.new((c,wr[0][j],wr[0][(j+1)%NA])) for j in range(NA)]
        for a_,b_ in zip(wr[:-1],wr[1:]):
            for j in range(NA):
                q=(j+1)%NA; wf.append(bm.faces.new((a_[j],b_[j],b_[q],a_[q])))
        for f in wf: f.material_index = 1
        def Hp(x,y, elong=elong, rad=rad, prof=prof):
            a = math.atan2(y*elong**0.5, x/elong**0.5); r = math.hypot(x/elong**0.5, y*elong**0.5)
            return prof(min(1.0, r/rad(a)), a)
        rk=[]; rnd=random.Random(30+k)
        for n_ in range(4+2*k):
            a=rnd.uniform(0,6.28); x,y=P(rnd.uniform(0.84,0.93),a); s=0.09+0.04*k
            rk += rock_hq(bm, center=(x,y,Hp(x,y)-0.02), size=(s*1.4,s,s*0.55), seed=400+k*20+n_, K=10, boxy=0.3, flat_top=0.25, sink=0.02, subdiv=4, rot=a)
        for f in rk: f.material_index = 2
        bl,ct=[],[]
        for n_ in range(2+k):
            a=rnd.uniform(0,6.28); x,y=P(0.86,a)
            for _ in range(7): bl += blade(bm,hl,x+rnd.uniform(-0.06,0.06),y+rnd.uniform(-0.06,0.06),Hp(x,y),rnd.uniform(0.15,0.34),0.022,rnd.uniform(0,6.28),rnd.uniform(0.05,0.35))
            if n_%2==0:
                for _ in range(2):
                    bx,by=x+rnd.uniform(-0.04,0.04),y+rnd.uniform(-0.04,0.04); h=rnd.uniform(0.3,0.42)
                    ct += cyl(bm,bx,by,Hp(bx,by),0.005,h,seg=5) + cyl(bm,bx,by,Hp(bx,by)+h-0.09,0.017,0.08,seg=8)
        for _ in range(14):
            a=rnd.uniform(0,6.28); x,y=P(rnd.uniform(0.86,0.99),a); bl += clump(bm,hl,Hp,x,y,4,0.04,0.08,0.03,0.014)
        for f in bl: f.material_index = 3
        for f in ct: f.material_index = 4
        name = ["TRN_Pond_Small","TRN_Pond_Medium","TRN_Pond_Large"][k]
        RESULTS[name] = finish_hq(name, coll, bm, len(blk), [mbank,mw,mr,mbl,mcat], row(k,3,3.3), "TRN_Ponds.jpg", {"water_level_m":ZWp})

# ====================================================== RIVER
if BUILD == "river":
    coll = get_coll("TRN_River")
    BANK = [(0.36,0.20,0.08),(0.46,0.29,0.13),(0.56,0.38,0.19)]
    mbank = painterly("TRN_River_Bank", BANK, edge=(0.78,0.6,0.38), cavity=(0.07,0.035,0.012), dirt=BANK[0], dirt_h=-1, scale=2.0, strokes=0.6, speckle=0.12, toplight=0.35)
    mask_mix(mbank, [(0.16,0.20,0.05),(0.24,0.30,0.08)], soft=0.12)
    mside = painterly("TRN_River_Side", [(0.22,0.11,0.04),(0.30,0.16,0.06),(0.38,0.22,0.09)], edge=(0.6,0.42,0.24), cavity=(0.05,0.025,0.01), dirt=(0.1,0.05,0.02), dirt_h=-0.25, strokes=0.5, bands=SOIL_B, band_scale=6)
    mw = water_hq("TRN_River_Water", (0.32,0.78,0.80),(0.08,0.55,0.68),(0.03,0.30,0.46), strokes=0.6, ripple='flow', depth_range=0.2, sky=(0.75,0.9,0.95), shore_foam=1.0)
    msand = painterly("TRN_River_Sand", [(0.62,0.50,0.30),(0.72,0.60,0.38),(0.80,0.70,0.48)], edge=(0.92,0.86,0.70), cavity=(0.25,0.18,0.09), dirt_h=-1, scale=1.6, strokes=0.55, toplight=0.3)
    mr = painterly("TRN_River_Stone", [(0.30,0.24,0.18),(0.40,0.33,0.25),(0.50,0.42,0.33)], edge=(0.8,0.7,0.58), cavity=(0.05,0.04,0.03), moss=MOSS, moss_amt=0.25, scale=3, strokes=0.3)
    mbl = blade_mat("TRN_River_Reed", (0.06,0.12,0.02),(0.32,0.46,0.10),(0.20,0.30,0.06),1.0)
    mcat = painterly("TRN_River_Cattail", [(0.10,0.045,0.018),(0.16,0.07,0.025)], edge=(0.35,0.18,0.07), dirt_h=-1, scale=14)
    ZW = -0.08; W = 0.30
    def seg_d(px,py,ax,ay,bx,by):
        vx,vy=bx-ax,by-ay; t=clamp(((px-ax)*vx+(py-ay)*vy)/(vx*vx+vy*vy)); return math.hypot(px-ax-vx*t, py-ay-vy*t)
    def poly_d(x,y,pts): return min(seg_d(x,y,*pts[i],*pts[i+1]) for i in range(len(pts)-1))
    def bez(p0,p1,p2,n=18): return [((1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t*t*p2[0], (1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t*t*p2[1]) for t in [i/n for i in range(n+1)]]
    TILES = [("TRN_River_Straight",[bez((0,-1.1),(0.15,0),(0,1.1))],None),
             ("TRN_River_Bend",[bez((0,-1.1),(0.05,0.0),(1.1,0.05))],None),
             ("TRN_River_Junction",[bez((-1.1,0),(0,0.1),(1.1,0)),bez((0,0),(0.05,-0.5),(0,-1.1))],None),
             ("TRN_River_Spring",[bez((-0.45,0.45),(0.1,0.0),(0,-1.1))],"spring"),
             ("TRN_River_Mouth",[bez((-1.1,0.2),(-0.3,0.1),(0.3,0.0))],"mouth")]
    for k,(name,paths,kind) in enumerate(TILES):
        dd = lambda x,y,paths=paths: min(poly_d(x,y,p) for p in paths)
        if kind == "mouth":
            def H(x,y, dd=dd):
                beach = 0.04 - 0.30*sstep(0.2,0.95, x + 0.25*math.cos(y*2.2))
                ch = -0.25*(1-sstep(W*0.65,W*1.05,dd(x,y)))
                return min(ch, beach) + shoulder(x,y)*(1-sstep(-0.2,0.9,x))
            M = lambda x,y: 0.0; R = lambda x,y,dd=dd: dd(x,y) < W*1.1 or x > -0.1
            mats = [msand, mside, mw, mr, mbl, mcat]
        else:
            def H(x,y, dd=dd, kind=kind):
                d = dd(x,y); bed = -0.25*(1-sstep(W*0.62, W*1.0, d))
                z = bed + 0.008*nn(x,y,2,1)*sstep(W,W*1.4,d) + shoulder(x,y)*sstep(W*1.0,W*1.2,d)
                if kind == "spring":
                    e=((x+0.45)/0.32)**2+((y-0.45)/0.3)**2; z = min(z, -0.25*(1-sstep(0.7,1.1,e)) + shoulder(x,y))
                return z
            M = lambda x,y,dd=dd: sstep(0.42,0.6,nn(x,y,2.0,7)+0.5)*sstep(W*1.3,W*2.0,dd(x,y))
            R = (lambda x,y,dd=dd: dd(x,y) < W*1.15) if kind != "spring" else (lambda x,y,dd=dd: dd(x,y) < W*1.15 or ((x+0.45)/0.32)**2+((y-0.45)/0.3)**2 < 1.15)
            mats = [mbank, mside, mw, mr, mbl, mcat]
        def d_water(bm,hl,R=R,H=H): return water_volume_hq(bm, R, H, ZW, n=64)
        def d_rocks(bm,hl,R=R,H=H,kind=kind,k=k):
            fs=[]; rnd=random.Random(50+k)
            for _ in range(6):
                for t in range(60):
                    x,y=rnd.uniform(-0.85,0.85),rnd.uniform(-0.85,0.85)
                    if not R(x,y): break
                res=bmesh.ops.create_icosphere(bm,subdivisions=2,radius=rnd.uniform(0.03,0.06),matrix=Matrix.Translation((x,y,H(x,y)+0.01))@Matrix.Diagonal((1,0.8,0.55,1)))
                fs+=list({f for v in res["verts"] for f in v.link_faces})
            if kind == "spring":
                for i,(x,y,s) in enumerate([(-0.75,0.72,0.26),(-0.45,0.86,0.22),(-0.86,0.40,0.2),(-0.58,0.62,0.15)]):
                    fs += rock_hq(bm, center=(x,y,0), size=(s,s*0.9,s*0.9), seed=820+i, K=10, boxy=0.25, flat_top=0.1, subdiv=4)
            return fs
        def d_fall(bm,hl,kind=kind):
            if kind != "spring": return []
            dl=bm.verts.layers.float["depth"]; sv=[]
            for j in range(11):
                t=j/10; z=0.34*(1-t)**1.6+ZW*t; yy=0.62-0.16*t
                for xx in (-0.62,-0.54,-0.46):
                    v=bm.verts.new((xx,yy,z)); v[dl]=0.02 if t>0.8 else 0.25; sv.append(v)
            return [bm.faces.new((sv[3*j+i],sv[3*j+i+1],sv[3*(j+1)+i+1],sv[3*(j+1)+i])) for j in range(10) for i in range(2)]
        def d_reeds(bm,hl,R=R,H=H,k=k):
            fs_b=[]; rnd=random.Random(70+k)
            for _ in range(3):
                for t in range(60):
                    x,y=rnd.uniform(-0.85,0.85),rnd.uniform(-0.85,0.85)
                    if not R(x,y) and not R(x*0.85,y*0.85): break
                for _ in range(6): fs_b += blade(bm,hl,x+rnd.uniform(-0.05,0.05),y+rnd.uniform(-0.05,0.05),H(x,y),rnd.uniform(0.14,0.3),0.02,rnd.uniform(0,6.28),rnd.uniform(0.05,0.3))
            return fs_b
        RESULTS[name] = tile_hq(name, coll, H, mats, row(k,5,2.5), "TRN_River.jpg", n=64, mask=M,
                                details=[(2,d_water),(2,d_fall),(3,d_rocks),(4,d_reeds)], extra={"water_level_m":ZW,"bed_m":-0.25})

# ====================================================== WATERFALLS
if BUILD == "falls":
    coll = get_coll("TRN_Waterfalls")
    mg = painterly("TRN_Falls_Grass", GRASS, edge=(0.45,0.58,0.16), cavity=(0.02,0.05,0.008), dirt=GRASS[0], dirt_h=-1, scale=1.8, strokes=0.6, toplight=0.35)
    mcl = painterly("TRN_Falls_Cliff", [(0.20,0.13,0.07),(0.27,0.18,0.10),(0.34,0.24,0.14)], edge=(0.6,0.46,0.3), cavity=(0.04,0.025,0.012), dirt=(0.1,0.06,0.03), dirt_h=-0.25,
                    strokes=0.55, crack_lines=0.4, crack_scale=1.6, toplight=0.2)
    mpool = water_hq("TRN_Falls_Pool", (0.40,0.80,0.80),(0.12,0.55,0.62),(0.04,0.32,0.42), strokes=0.6, ripple='rings', depth_range=0.2, sky=(0.8,0.93,0.95), shore_foam=0.8)
    mr = painterly("TRN_Falls_Rock", ROCK, edge=(0.55,0.53,0.48), cavity=(0.02,0.018,0.015), moss=MOSS, moss_amt=1.0, scale=2.0, strokes=0.3, crack_lines=0.6, crack_scale=2.6)
    # falling water sheet: vertical streaks, bright, slightly transparent
    m, nt, bs = new_mat("TRN_Falls_Sheet")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n1 = noise_n(nt, mapping(nt, tc.outputs["Object"], (16,16,0.5)), 2.0, 5, 0.55)
    r = ramp(nt, [(0.10,0.45,0.50),(0.40,0.72,0.75),(0.85,0.96,0.97),(1,1,1)], [0.3,0.5,0.66,0.8]); nt.links.new(n1.outputs["Fac"], r.inputs[0])
    nt.links.new(r.outputs[0], bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.08
    bs.inputs["Emission Color"].default_value = (0.7,0.88,0.9,1); bs.inputs["Emission Strength"].default_value = 0.25
    nt.links.new(maprange(nt, n1.outputs["Fac"], 0.25, 0.5, 0.55, 1.0), bs.inputs["Alpha"])
    try: m.surface_render_method = 'BLENDED'
    except Exception: pass
    msheet = m
    mfoam = painterly("TRN_Falls_Foam", [(0.78,0.86,0.88),(0.92,0.96,0.97),(1,1,1)], edge=(1,1,1), cavity=(0.55,0.68,0.72), dirt_h=-1, scale=6, strokes=0.3, toplight=0.4, edge_amt=0.6, cav_amt=0.5)
    mmist = volume_mat("TRN_Falls_Mist", (0.95,0.97,0.98), 10.0, 3.5)
    for k,(name,SX,SY,HT,NW,pos) in enumerate([("TRN_Waterfall_Small",1.0,1.0,2.0,0.20,(-2.3,2.3,0)),("TRN_Waterfall_Big",2.0,1.5,3.0,0.30,(2.3,-2.3,0))]):
        YC = 0.10
        def Hn(u,v, HT=HT, NW=NW):
            top = HT - (0.15 if abs(u) < NW else 0.0)
            cliff = sstep(YC-0.03, YC+0.05, v + 0.04*nn(u,v,4,k))
            e = (u/0.55)**2 + ((v+0.42)/0.38)**2*(1+0.15*nn(u,v,3,k+4))
            pool = -0.22*(1-sstep(0.7,1.1,e))
            z = top*cliff
            return (min(z, pool) if cliff < 0.5 else z) + shoulder(u,v,0.08)*(1 if cliff < 0.5 else 0.5)
        Mn = lambda u,v: sstep(YC-0.04,YC,v)*(1-sstep(YC+0.06,YC+0.1,v))
        bm,tl,ml,hl = new_bm2()
        fs = build_hf(bm,Hn,70,80,mask=Mn,top_layer=tl,mask_layer=ml,wall_rings=(0.3,0.6)); nb=len(fs)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        for f in fs:
            avg_t = sum(v[tl] for v in f.verts)/len(f.verts); avg_m = sum(v[ml] for v in f.verts)/len(f.verts)
            f.material_index = 1 if (avg_t < 0.5 or avg_m > 0.4 or f.normal.z < 0.5) else 0
        wf = water_volume_hq(bm, lambda u,v: (u/0.55)**2 + ((v+0.42)/0.38)**2 < 1.05, Hn, -0.05, n=60)
        dl = bm.verts.layers.float["depth"]; cv=[]
        for j in range(2):
            for i in range(2):
                vv = bm.verts.new(((i*2-1)*NW*0.95, YC+0.06 + j*(0.97-YC-0.06), HT-0.05)); vv[dl]=0.12; cv.append(vv)
        wf.append(bm.faces.new((cv[0],cv[1],cv[3],cv[2])))
        for f in wf: f.material_index = 2
        sh=[]
        for layer,(ofs,wm) in enumerate(((0.0,1.0),(0.03,0.82),(-0.025,0.6))):
            sv=[]; NS_=18
            for j in range(NS_+1):
                t=j/NS_; z=(HT-0.05)*(1-t)+(-0.05)*t; vv=YC+0.06+ofs - 0.10*math.sin(t*math.pi*0.5) - 0.09*t
                w=NW*0.95*wm*(1+0.28*t)
                for i in range(4): sv.append(bm.verts.new((((i/3)*2-1)*w, vv+0.015*nn(i,j,1.0,layer+3), z)))
            for j in range(NS_):
                for i in range(3): sh.append(bm.faces.new((sv[4*j+i],sv[4*j+i+1],sv[4*(j+1)+i+1],sv[4*(j+1)+i])))
        for f in sh: f.material_index = 3
        fo=[]; rnd=random.Random(700+k)
        for _ in range(14+8*k):
            x=rnd.uniform(-NW*1.3,NW*1.3); y=YC-0.16+rnd.uniform(-0.10,0.08); s=rnd.uniform(0.06,0.12)*(1+k*0.5)
            fo += blob(bm,(x,y,-0.04+s*0.3),(s,s*0.85,s*0.55),2)
        for f in fo: f.material_index = 4
        mi=[]
        for _ in range(5+3*k):
            x=rnd.uniform(-NW*1.2,NW*1.2); y=YC-0.12+rnd.uniform(-0.12,0.06); s=rnd.uniform(0.14,0.24)*(1+k*0.5)
            mi += blob(bm,(x,y,0.05+s*0.6),(s,s*0.8,s*0.9),2)
        for f in mi: f.material_index = 5
        rk=[]
        side = [(-0.62,-0.22),(-0.74,0.0),(0.62,-0.22),(0.74,0.0),(-0.45,-0.75),(0.5,-0.72),(-0.25,-0.85),(0.3,-0.86)]
        for i,(u,v) in enumerate(side):
            s=0.17+0.07*rnd.random()
            rk += rock_hq(bm, center=(u,v,0), size=(s,s*0.9,s*1.05), seed=800+k*30+i, K=11, boxy=0.2, flat_top=0.1, subdiv=4)
        cols = 3 if k == 0 else 4
        for i,u in enumerate((-NW-0.17,NW+0.17)):
            for l in range(cols):
                rk += rock_hq(bm, center=(u+0.03*l*(1 if u<0 else -1), YC-0.03, 0.15+l*(HT-0.3)/cols), size=(0.20,0.18,(HT/cols)*0.62), seed=900+k*20+i*10+l, K=11, boxy=0.28, flat_top=0.15, sink=0.0, subdiv=4)
        if k == 1: rk += rock_hq(bm, center=(0.05, YC+0.02, HT-0.55), size=(0.12,0.12,0.45), seed=950, K=11, boxy=0.3, sink=0.0, subdiv=4)
        for f in rk: f.material_index = 6
        for v in bm.verts: v.co.x *= SX; v.co.y *= SY
        RESULTS[name] = finish_hq(name, coll, bm, nb, [mg, mcl, mpool, msheet, mfoam, mmist, mr], pos, "TRN_Waterfalls.jpg",
                                  {"drop_m":HT, "footprint_m":"%gx%g"%(2*SX,2*SY), "vfx_socket":"SOCKET_Splash at pool; mist mesh is preview only"})
