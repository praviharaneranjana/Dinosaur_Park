"""Dino Park Tycoon - zone sets: TRN_VolcanoIsland / TRN_SwampIsland / TRN_DesertIsland / TRN_BeachShore.
Set BUILD = "volcano" | "swamp" | "desert" | "beach". These are zones on the ONE island, not separate islands.
Tiles: 2x2 m, pivot centre of top (z=0). Props/rocks: pivot bottom centre on ground. Smoke for the volcano is a Unity VFX, not modelled."""
import os
_b = BUILD; BUILD = "none"
exec(open(os.path.join(TOOLS, "build_trn_rocks.py")).read())     # faceted_rock, rock_mat, sand_disc, make_obj + trn_common
BUILD = _b
random.seed(11)
RESULTS = {}
def row(i, n, gap=2.6): t = (i-(n-1)/2)*gap; return (t*0.7071, -t*0.7071, 0)
def tile_obj(name, coll, H, mats, pos, src, n=48, mask=None, details=(), extra=None):
    bm,tl,ml,hl = new_bm(); fs = build_hf(bm,H,n,n,mask=mask,top_layer=tl,mask_layer=ml); nb = len(fs)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    for idx, fn in details:
        for f in fn(bm,hl): f.material_index = idx
    return finish(name, coll, bm, nb, mats, pos, src, extra)
def edge_fade(x,y,a=0.08,b=0.35): return sstep(a,b,edge_d(x,y))

def lava_mat(name, base, glow=(1.0,0.22,0.02), scale=1.3, width=0.016, strength=2.2):
    m, nt, bs = new_mat(name)
    tc = nt.nodes.new("ShaderNodeTexCoord"); obj = tc.outputs["Object"]
    n1 = noise_n(nt, obj, 3, 6, 0.6); rb = ramp(nt, base); nt.links.new(n1.outputs["Fac"], rb.inputs[0])
    vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.feature='DISTANCE_TO_EDGE'; vo.inputs["Scale"].default_value = scale
    vo.inputs["Randomness"].default_value = 0.9
    nd = noise_n(nt, obj, 4, 3, 0.5)
    vin = nt.nodes.new("ShaderNodeVectorMath"); vin.operation='ADD'
    nt.links.new(obj, vin.inputs[0]); nt.links.new(nd.outputs["Color"], vin.inputs[1]); vs = nt.nodes.new("ShaderNodeVectorMath"); vs.operation='SCALE'
    nt.links.new(vin.outputs[0], vs.inputs[0]); vs.inputs["Scale"].default_value = 1.0
    nt.links.new(vs.outputs[0], vo.inputs["Vector"])
    crack = mathop(nt, maprange(nt, vo.outputs["Distance"], width, 0.0), maprange(nt, n1.outputs["Fac"], 0.42, 0.55), "MULTIPLY")
    halo = maprange(nt, vo.outputs["Distance"], width*4, 0.0)
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = 0.3
    col = mix(nt, rb.outputs[0], maprange(nt, ao.outputs["AO"], 0.2, 1.0, 0.4, 1.0), 1.0, 'MULTIPLY')
    col = mix(nt, col, (0.22,0.06,0.012), mathop(nt, halo, 0.6))
    col = mix(nt, col, glow, crack)
    nt.links.new(col, bs.inputs["Base Color"])
    nt.links.new(crack, bs.inputs["Emission Strength"]) if False else None
    es = mathop(nt, crack, strength); bs.inputs["Emission Color"].default_value = (*glow,1)
    nt.links.new(es, bs.inputs["Emission Strength"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.5; bp.inputs["Distance"].default_value = 0.03
    nt.links.new(maprange(nt, vo.outputs["Distance"], 0.0, 0.12), bp.inputs["Height"]); nt.links.new(bp.outputs[0], bs.inputs["Normal"])
    bs.inputs["Roughness"].default_value = 0.85
    return m
def water_mat2(name, deep, shallow, foam=(0.9,0.95,0.95), algae=None):
    m, nt, bs = new_mat(name)
    tc = nt.nodes.new("ShaderNodeTexCoord"); obj = tc.outputs["Object"]
    n1 = noise_n(nt, mapping(nt,obj,(1,3,1),0.6), 2.5, 4, 0.55)
    r = ramp(nt, [deep, shallow]); nt.links.new(n1.outputs["Fac"], r.inputs[0])
    col = r.outputs[0]
    if algae:
        n2 = noise_n(nt, obj, 3.0, 5, 0.6)
        col = mix(nt, col, algae, maprange(nt, n2.outputs["Fac"], 0.56, 0.6))
    n3 = noise_n(nt, mapping(nt,obj,(1,4,1),0.6), 6, 3, 0.5)
    ff = mathop(nt, attr(nt,"mask"), maprange(nt, n3.outputs["Fac"], 0.35, 0.6, 0.5, 1.2))
    col = mix(nt, col, foam, maprange(nt, ff, 0.45, 0.7))
    nt.links.new(col, bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.04
    bs.inputs["Specular IOR Level"].default_value = 0.8
    return m
def sandstone_mat(name):
    m, nt, bs = new_mat(name)
    tc = nt.nodes.new("ShaderNodeTexCoord"); obj = tc.outputs["Object"]
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type='BANDS'; wv.bands_direction='Z'
    wv.inputs["Scale"].default_value = 0.9; wv.inputs["Distortion"].default_value = 1.5; nt.links.new(obj, wv.inputs["Vector"])
    r = ramp(nt, [(0.40,0.14,0.05),(0.58,0.26,0.10),(0.52,0.22,0.18),(0.66,0.36,0.17)], [0.15,0.4,0.6,0.85])
    nt.links.new(wv.outputs["Fac"], r.inputs[0])
    geo = nt.nodes.new("ShaderNodeNewGeometry"); sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Normal"], sp.inputs[0])
    col = mix(nt, r.outputs[0], (0.66,0.40,0.18), maprange(nt, sp.outputs[2], 0.75, 0.95, 0.0, 0.6))
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = 0.3
    col = mix(nt, col, maprange(nt, ao.outputs["AO"], 0.2, 1.0, 0.45, 1.0), 1.0, 'MULTIPLY')
    nt.links.new(col, bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.9
    return m

def water_volume(bm, region, H, zw, n=40, foam_w=0.08):
    """Water top at zw over region (H<zw), plus side skirts on tile borders. 'mask' layer = foam near shore."""
    ml = bm.verts.layers.float["mask"]; fs = []
    U = [-1+2*i/n for i in range(n+1)]
    vt = {}
    def V(i,j):
        if (i,j) not in vt:
            x,y = plan_map(U[i],U[j]); v = bm.verts.new((x,y,zw)); d = zw - H(x,y)
            v[ml] = 1-sstep(0.0, foam_w, d); vt[(i,j)] = v
        return vt[(i,j)]
    inside = lambda i,j: region((U[i]+U[i+1])/2,(U[j]+U[j+1])/2) and H((U[i]+U[i+1])/2,(U[j]+U[j+1])/2) < zw
    for i in range(n):
        for j in range(n):
            if inside(i,j): fs.append(bm.faces.new((V(i,j),V(i+1,j),V(i+1,j+1),V(i,j+1))))
    for i in range(n):          # skirts on -Y (j=0) and -X (i=0) and +Y, +X borders
        for (a,b,ok) in (((i,0),(i+1,0),inside(i,0)),((i,n),(i+1,n),inside(i,n-1)),((0,i),(0,i+1),inside(0,i)),((n,i),(n,i+1),inside(n-1,i))):
            if not ok: continue
            va,vb = V(*a),V(*b)
            za = H(va.co.x,va.co.y); zb = H(vb.co.x,vb.co.y)
            la = bm.verts.new((va.co.x,va.co.y,min(za,zw))); lb = bm.verts.new((vb.co.x,vb.co.y,min(zb,zw)))
            fs.append(bm.faces.new((va,vb,lb,la)))
    return fs

def frond(bm, hl, x,y,z, ang, L, droop=0.5, w=0.05):
    fs=[]; n=8; dx,dy = math.cos(ang),math.sin(ang); px,py=-dy,dx
    pts=[]
    for k in range(n+1):
        t=k/n; pts.append(Vector((x+dx*L*t, y+dy*L*t, z+L*(0.55*t - droop*t*t))))
    for k in range(n):
        a,b = pts[k],pts[k+1]; t=k/n; ww = w*(1-t*0.8)*(0.6 if k==0 else 1)
        for s in (-1,1):
            tip = (a+b)/2 + Vector((px*s*ww*2.2+dx*ww, py*s*ww*2.2+dy*ww, -0.01))
            va,vb,vc = bm.verts.new(a),bm.verts.new(b),bm.verts.new(tip)
            va[hl]=t; vb[hl]=t; vc[hl]=min(1,t+0.4)
            fs.append(bm.faces.new((va,vb,vc)))
    return fs
def fern(bm, hl, H, x,y, n=7, L=0.32):
    fs=[]; z=H(x,y)
    for k in range(n): fs += frond(bm,hl,x,y,z, k*2*math.pi/n+random.uniform(-0.3,0.3), L*random.uniform(0.8,1.2))
    return fs
def leaf(bm, H, x,y, L=0.05):
    a=random.uniform(0,6.28); z=H(x,y)+0.006; vs=[]
    for (u,v) in [(-1,0),(-0.4,0.42),(0.4,0.38),(1,0),(0.4,-0.38),(-0.4,-0.42)]:
        vs.append(bm.verts.new((x+(u*math.cos(a)-v*0.45*math.sin(a))*L, y+(u*math.sin(a)+v*0.45*math.cos(a))*L, z)))
    return [bm.faces.new(vs)]
def cyl(bm, x,y,z0, r, h, seg=6, tilt=(0,0)):
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r*0.9, depth=h,
        matrix=Matrix.Translation((x,y,z0+h/2)) @ Matrix.Rotation(tilt[0],4,'X') @ Matrix.Rotation(tilt[1],4,'Y'))
    return list({f for v in res["verts"] for f in v.link_faces})

# =============================== VOLCANO ===============================
if BUILD == "volcano":
    coll = get_coll("TRN_VolcanoIsland")
    ASH_T = [(0.035,0.033,0.03),(0.06,0.057,0.052),(0.09,0.085,0.078)]
    ASH_S = [(0.03,0.022,0.016),(0.05,0.036,0.025),(0.08,0.055,0.035)]
    mash = painted2("TRN_Ash_Body", ASH_T, ASH_S, streak=0.5, bump=0.2)
    mpb = painted2("TRN_Ash_Pebble", [(0.08,0.075,0.07),(0.14,0.13,0.12)], [(0.05,0.05,0.045),(0.08,0.075,0.07)], bump=0.05, scale=10)
    Ha = lambda x,y: 0.012*nn(x,y,1.5,1)*edge_fade(x,y) + shoulder(x,y)
    def peb(bm,hl):
        fs=[]
        for _ in range(26):
            x,y=random.uniform(-0.85,0.85),random.uniform(-0.85,0.85); r=random.uniform(0.012,0.035)
            res=bmesh.ops.create_icosphere(bm,subdivisions=1,radius=r,matrix=Matrix.Translation((x,y,Ha(x,y)+r*0.1))@Matrix.Diagonal((1,0.8,0.5,1)))
            fs+=list({f for v in res["verts"] for f in v.link_faces})
        return fs
    RESULTS["TRN_Volcano_Ash"] = tile_obj("TRN_Volcano_Ash",coll,Ha,[mash,mpb],row(0,4),"TRN_VolcanoIsland.jpg",details=[(1,peb)])
    # cracked lava plates: python voronoi grooves so plates read in silhouette
    seeds = [(random.uniform(-1,1),random.uniform(-1,1)) for _ in range(13)]
    def Hl(x,y):
        ds = sorted(math.hypot(x-sx,y-sy) for sx,sy in seeds)
        g = ds[1]-ds[0]; plate = 0.03*nn(x,y,2.0,3) + 0.02*(1-sstep(0,0.5,ds[0]))
        return (plate - 0.06*(1-sstep(0.0,0.05,g)))*edge_fade(x,y,0.02,0.2) + shoulder(x,y)
    mlv = lava_mat("TRN_Lava_Plate", [(0.012,0.011,0.01),(0.03,0.026,0.022),(0.05,0.04,0.033)], scale=0.9, width=0.03, strength=2.5)
    RESULTS["TRN_Volcano_LavaPlates"] = tile_obj("TRN_Volcano_LavaPlates",coll,Hl,[mlv],row(1,4),"TRN_VolcanoIsland.jpg",n=70)
    # lava rocks + mini volcano (props on ash discs)
    mrock = lava_mat("TRN_Lava_Rock", [(0.012,0.011,0.01),(0.03,0.026,0.022),(0.06,0.045,0.035)], scale=1.4, width=0.02, strength=2.5)
    mdisc = painted2("TRN_Ash_Disc", ASH_T, ASH_T, bump=0.1)
    ROCKS = [("TRN_LavaRock_Small",(0.38,0.34,0.36),41,0.6),("TRN_LavaRock_Low",(0.62,0.48,0.40),42,0.85),
             ("TRN_LavaRock_Tall",(0.42,0.40,0.85),43,0.7),("TRN_LavaRock_Cube",(0.40,0.38,0.42),44,0.62)]
    for k,(name,sz,sd,dr) in enumerate(ROCKS):
        bm = bmesh.new(); bm.verts.layers.float.new("top"); bm.verts.layers.float.new("mask")
        faceted_rock(bm,(0,0,0),sz,sd,K=10,cracks=2,dmin=0.6,boxy=0.25)
        for f in sand_disc(bm, dr, z=-0.03): f.material_index = 1
        pos = row(k,4); pos = (pos[0]-1.6, pos[1]-1.6, 0)
        RESULTS[name] = make_obj(name, coll, bm, [mrock, mdisc], pos, "TRN_VolcanoIsland.jpg")
    # mini volcano cone with crater
    bm = bmesh.new(); bm.verts.layers.float.new("top"); bm.verts.layers.float.new("mask")
    SEG, NR = 28, 12; rings = []
    for k in range(NR+1):
        t = k/NR; h = t*1.0; base_r = 0.95*(1-t)**1.25 + 0.2*t
        ring = []
        for i in range(SEG):
            a = 2*math.pi*i/SEG
            ridge = 0.11*abs(math.sin(a*7 + 1.5*nn(t*2, i*0.3, 1.0, 7)))*(1-t)
            r = base_r + ridge + 0.03*nn(math.cos(a)*3, math.sin(a)*3, 1.0, k)
            ring.append(bm.verts.new((r*math.cos(a), r*math.sin(a), h)))
        rings.append(ring)
    crater = [bm.verts.new((0.11*math.cos(2*math.pi*i/SEG), 0.11*math.sin(2*math.pi*i/SEG), 0.82)) for i in range(SEG)]
    for ra, rb in zip(rings[:-1]+[rings[-1]], rings[1:]+[crater]):
        for i in range(SEG):
            j = (i+1) % SEG; bm.faces.new((ra[i], ra[j], rb[j], rb[i]))
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(crater)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    for f in sand_disc(bm, 1.3, z=-0.03): f.material_index = 1
    RESULTS["TRN_Volcano_Mini"] = make_obj("TRN_Volcano_Mini", coll, bm, [mrock, mdisc], (row(3,4)[0]+1.0, row(3,4)[1]+1.0, 0), "TRN_VolcanoIsland.jpg", {"vfx_socket":"SOCKET_Smoke at crater (0,0,0.9)"}, sharp=40)

# =============================== SWAMP ===============================
if BUILD == "swamp":
    coll = get_coll("TRN_SwampIsland")
    PEAT_T = [(0.012,0.013,0.008),(0.022,0.025,0.014),(0.035,0.04,0.02)]
    PEAT_S = [(0.012,0.010,0.006),(0.022,0.018,0.010),(0.035,0.028,0.016)]
    MOSSM = [(0.03,0.06,0.01),(0.055,0.11,0.016),(0.09,0.17,0.025)]
    mpeat = painted2("TRN_Swamp_Peat", PEAT_T, PEAT_S, mask_cols=MOSSM, streak=0.4, bump=0.2)
    mfern = blade_mat("TRN_Swamp_Fern", (0.03,0.08,0.01),(0.15,0.33,0.05),(0.08,0.2,0.03),1.0)
    mleaf = painted2("TRN_Swamp_Leaf", [(0.12,0.05,0.015),(0.22,0.10,0.03)], [(0.12,0.05,0.015),(0.22,0.10,0.03)], bump=0.02, scale=12)
    Hm = lambda x,y: 0.015*nn(x,y,1.6,2)*edge_fade(x,y) + shoulder(x,y)
    Mm = lambda x,y: sstep(0.5,0.6,nn(x,y,2.4,9)+0.5)
    def ferns(bm,hl):
        fs=[]
        for (x,y) in [(-0.55,0.6),(0.55,0.35),(-0.15,-0.55),(0.65,-0.6)]: fs += fern(bm,hl,Hm,x,y)
        return fs
    def leaves(bm,hl):
        fs=[]
        for _ in range(34): fs += leaf(bm,Hm,random.uniform(-0.85,0.85),random.uniform(-0.85,0.85),random.uniform(0.035,0.06))
        return fs
    RESULTS["TRN_Swamp_MossGround"] = tile_obj("TRN_Swamp_MossGround",coll,Hm,[mpeat,mfern,mleaf],row(0,3),"TRN_SwampIsland.jpg",mask=Mm,details=[(1,ferns),(2,leaves)])
    # algae pool
    def Hp(x,y):
        d = edge_d(x,y); basin = 1-sstep(0.10,0.30,d)
        return -0.16*(1-basin) + 0.01*nn(x,y,2,4) + shoulder(x,y)
    Mp = lambda x,y: sstep(0.5,0.62,nn(x,y,2.5,12)+0.5)*(1-sstep(0.1,0.25,edge_d(x,y)))
    mpw = water_mat2("TRN_Swamp_PoolWater", (0.02,0.07,0.035), (0.06,0.16,0.08), foam=(0.12,0.22,0.08), algae=(0.12,0.24,0.04))
    def pool(bm,hl): return water_volume(bm, lambda x,y: edge_d(x,y) > 0.09, Hp, -0.04, n=40, foam_w=0.03)
    RESULTS["TRN_Swamp_Pool"] = tile_obj("TRN_Swamp_Pool",coll,Hp,[mpeat,mpw],row(1,3),"TRN_SwampIsland.jpg",mask=Mp,details=[(1,pool)])
    # reed marsh
    MARSH_T = [(0.035,0.03,0.022),(0.06,0.05,0.035),(0.09,0.075,0.05)]
    mmarsh = painted2("TRN_Swamp_Marsh", MARSH_T, [(0.03,0.025,0.018),(0.05,0.04,0.03)], streak=0.5, bump=0.1, rough=0.25)
    PUD = [(-0.35,0.35,0.22,0.12),(0.45,0.10,0.18,0.10),(0.05,-0.45,0.16,0.09),(-0.6,-0.3,0.1,0.06)]
    def Hr(x,y):
        z = 0.015*nn(x,y,1.8,5)
        for (cx,cy,rx,ry) in PUD:
            e = ((x-cx)/rx)**2+((y-cy)/ry)**2; w = 1-sstep(0.8,1.3,e); z = z*(1-w) - 0.03*w
        return z*edge_fade(x,y) + shoulder(x,y)
    mrw = water_mat2("TRN_Swamp_MarshWater", (0.12,0.16,0.20), (0.30,0.38,0.45))
    mreed = blade_mat("TRN_Swamp_Reed", (0.10,0.07,0.03),(0.40,0.30,0.14),(0.30,0.22,0.10),1.0)
    mcat = flat_mat("TRN_Swamp_Cattail", (0.12,0.06,0.025), 0.8)
    def in_pud(x,y): return any(((x-cx)/rx)**2+((y-cy)/ry)**2 < 1.25 for (cx,cy,rx,ry) in PUD)
    def marsh_water(bm,hl): return water_volume(bm, in_pud, Hr, -0.014, n=60, foam_w=0.02)
    def reeds(bm,hl):
        fs=[]
        for _ in range(16):
            x,y = random.uniform(-0.8,0.8),random.uniform(-0.8,0.8)
            fs += blade(bm,hl,x,y,Hr(x,y),random.uniform(0.25,0.5),0.022,random.uniform(0,6.28),random.uniform(0.0,0.12))
        return fs
    def cattails(bm,hl):
        fs=[]
        for _ in range(7):
            x,y = random.uniform(-0.8,0.8),random.uniform(-0.8,0.8); h = random.uniform(0.35,0.5)
            fs += cyl(bm,x,y,Hr(x,y),0.006,h,seg=4)
            fs += cyl(bm,x,y,Hr(x,y)+h-0.1,0.018,0.09,seg=6)
        return fs
    RESULTS["TRN_Swamp_ReedMarsh"] = tile_obj("TRN_Swamp_ReedMarsh",coll,Hr,[mmarsh,mrw,mreed,mcat],row(2,3),"TRN_SwampIsland.jpg",n=56,details=[(1,marsh_water),(2,reeds),(3,cattails)])

# =============================== DESERT ===============================
if BUILD == "desert":
    coll = get_coll("TRN_DesertIsland")
    SAND_O = [(0.50,0.20,0.06),(0.62,0.30,0.10),(0.72,0.40,0.15)]
    SAND_P = [(0.55,0.24,0.16),(0.66,0.33,0.22),(0.75,0.45,0.30)]
    SIDE_O = [(0.36,0.13,0.04),(0.46,0.19,0.07),(0.55,0.26,0.10)]
    mo = painted2("TRN_Desert_Sand", SAND_O, SIDE_O, streak=0.5, bump=0.08)
    mp = painted2("TRN_Desert_SandPink", SAND_P, SIDE_O, streak=0.5, bump=0.08)
    Hrip = lambda x,y: (0.012*math.sin((x*0.6+y*0.8)*16 + 1.2*nn(x,y,1.5,3)) + 0.01*nn(x,y,1.2,4))*edge_fade(x,y) + shoulder(x,y)
    RESULTS["TRN_Desert_Ripples"] = tile_obj("TRN_Desert_Ripples",coll,Hrip,[mo],row(0,4),"TRN_DesertIsland.jpg",n=60)
    def dune(x,y, h, cx, amp, freq, lee=0.22, wind=1.1):
        crest = cx + amp*math.sin(y*freq)
        d = x - crest
        return h*(1-sstep(0.0,lee,d)) if d > 0 else h*sstep(-wind,0.0,d)
    H2 = lambda x,y: dune(x,y,0.16,0.15,0.25,1.4)*edge_fade(x,y,0.05,0.4) + shoulder(x,y)
    H3 = lambda x,y: dune(x,y,0.42,0.05,0.35,1.7,0.3,1.3)*edge_fade(x,y,0.04,0.3) + shoulder(x,y)
    H4 = lambda x,y: dune(y,x,0.34,0.10,0.3,1.3,0.28,1.2)*edge_fade(x,y,0.04,0.3) + shoulder(x,y)
    RESULTS["TRN_Desert_DuneLow"]  = tile_obj("TRN_Desert_DuneLow", coll,H2,[mp],row(1,4),"TRN_DesertIsland.jpg",n=56)
    RESULTS["TRN_Desert_DuneHigh"] = tile_obj("TRN_Desert_DuneHigh",coll,H3,[mo],row(2,4),"TRN_DesertIsland.jpg",n=56)
    RESULTS["TRN_Desert_DuneRidge"]= tile_obj("TRN_Desert_DuneRidge",coll,H4,[mo],row(3,4),"TRN_DesertIsland.jpg",n=56)
    mss = sandstone_mat("TRN_Desert_Sandstone"); mds = painted2("TRN_Desert_Disc", SAND_O, SAND_O, bump=0.05)
    for k,(name,stacks,dr) in enumerate([("TRN_Desert_Mesa_Small",[(0,0,0.55,0.48,5)],0.95),
                                         ("TRN_Desert_Mesa_Arch",[(-0.45,0,0.45,0.55,5),(0.50,0.05,0.48,0.58,5)],1.3)]):
        bm = bmesh.new(); bm.verts.layers.float.new("top"); bm.verts.layers.float.new("mask")
        for si,(cx,cy,sx,sy,nl) in enumerate(stacks):
            for l in range(nl):
                s = 1 - 0.07*l + 0.05*random.uniform(-1,1)
                faceted_rock(bm,(cx+random.uniform(-0.04,0.04),cy,l*0.17),(sx*s,sy*s,0.10),500+k*50+si*10+l,K=9,subdiv=3,cracks=1,dmin=0.7,boxy=0.3,sink=0.0)
        if len(stacks) == 2:
            for l in range(2):
                faceted_rock(bm,(0.02,0.02,5*0.17+l*0.15),(0.95-0.08*l,0.62,0.09),777+l,K=9,subdiv=3,cracks=1,dmin=0.7,boxy=0.3,sink=0.0)
        for f in sand_disc(bm, dr, z=-0.03): f.material_index = 1
        pos = row(k,2,3.2); pos = (pos[0]-2.0, pos[1]-2.0, 0)
        RESULTS[name] = make_obj(name, coll, bm, [mss, mds], pos, "TRN_DesertIsland.jpg")

# =============================== BEACH ===============================
if BUILD == "beach":
    coll = get_coll("TRN_BeachShore")
    SAND = [(0.48,0.38,0.22),(0.60,0.50,0.32),(0.70,0.62,0.45)]
    SIDE = [(0.22,0.15,0.08),(0.32,0.23,0.13),(0.42,0.32,0.19)]
    msand = painted2("TRN_Beach_Sand", SAND, SIDE, streak=0.45, bump=0.06)
    msea = water_mat2("TRN_Beach_Sea", (0.02,0.22,0.30), (0.12,0.50,0.52))
    mshell = flat_mat("TRN_Beach_Shell", (0.55,0.32,0.25), 0.6)
    ZW = -0.06
    def shore_tile(name, i, shore):
        Hs = lambda x,y: (0.04 - 0.30*sstep(-0.15,0.35, x - shore(y))) + 0.008*nn(x,y,2,6) + shoulder(x,y)*(1 if x - shore(y) < 0 else 0.3)
        def sea(bm,hl): return water_volume(bm, lambda x,y: x - shore(y) > -0.25, Hs, ZW, n=48, foam_w=0.05)
        def shells(bm,hl):
            fs=[]
            for _ in range(2):
                y = random.uniform(-0.6,0.6); x = shore(y) - random.uniform(0.4,0.7)
                res=bmesh.ops.create_icosphere(bm,subdivisions=1,radius=0.03,matrix=Matrix.Translation((x,y,Hs(x,y)+0.005))@Matrix.Diagonal((1,0.8,0.35,1)))
                fs+=list({f for v in res["verts"] for f in v.link_faces})
            return fs
        RESULTS[name] = tile_obj(name,coll,Hs,[msand,msea,mshell],row(i,4),"TRN_BeachShore.jpg",n=56,details=[(1,sea),(2,shells)],extra={"sea_level_m":ZW,"sea_side":"+X"})
    shore_tile("TRN_Beach_Straight", 0, lambda y: 0.05*math.sin(y*2.0))
    shore_tile("TRN_Beach_CurveA", 1, lambda y: 0.30*math.sin(y*1.6))
    shore_tile("TRN_Beach_CurveB", 2, lambda y: -0.25*math.sin(y*1.6+0.6)+0.1)
    # sand circle with post-and-rail fence ring, grassy rim
    GRASS = [(0.20,0.26,0.10),(0.30,0.36,0.16)]
    mring = painted2("TRN_Beach_RingSand", SAND, SIDE, mask_cols=GRASS, streak=0.4, bump=0.05)
    mpost = painted2("TRN_Beach_Post", [(0.05,0.055,0.045),(0.09,0.095,0.08)], [(0.05,0.055,0.045),(0.09,0.095,0.08)], streak=0.5, streak_scale=(1,1,12), bump=0.2, scale=6)
    Hc = lambda x,y: 0.01*nn(x,y,1.5,8)*edge_fade(x,y) + shoulder(x,y)
    Mc = lambda x,y: 1-sstep(0.05,0.3,edge_d(x,y))
    def fence(bm,hl):
        fs=[]; N=16; Rr=0.62; pts=[]
        for k in range(N):
            a = 2*math.pi*k/N; x,y = Rr*math.cos(a), Rr*math.sin(a); pts.append((x,y))
            fs += cyl(bm,x,y,Hc(x,y)-0.02,0.04,0.32+0.04*random.uniform(-1,1),seg=7)
        for k in range(N):
            (x0,y0),(x1,y1) = pts[k],pts[(k+1)%N]; L = math.hypot(x1-x0,y1-y0); a = math.atan2(y1-y0,x1-x0)
            for zr in (0.12,0.24):
                fs += box(bm,((x0+x1)/2,(y0+y1)/2,zr),(L,0.035,0.04),Matrix.Rotation(a,4,'Z'))
        return fs
    def tufts(bm,hl):
        fs=[]
        for _ in range(14):
            t = random.uniform(-0.9,0.9); s = random.choice([(t,-0.9),(t,0.9),(-0.9,t),(0.9,t)])
            fs += clump(bm,hl,Hc,s[0],s[1],3,0.04,0.08,0.03,0.012)
        return fs
    mbl = blade_mat("TRN_Beach_GrassBlade", (0.10,0.16,0.04),(0.40,0.46,0.20),(0.28,0.34,0.12),1.0)
    RESULTS["TRN_Beach_FenceRing"] = tile_obj("TRN_Beach_FenceRing",coll,Hc,[mring,mpost,mbl],row(3,4),"TRN_BeachShore.jpg",mask=Mc,details=[(1,fence),(2,tufts)])
