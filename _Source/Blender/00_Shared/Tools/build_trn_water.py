"""Dino Park Tycoon - TRN_Ponds / TRN_River / TRN_Waterfalls builder.  BUILD = "ponds" | "river" | "falls".
River tiles: 2x2 m, banks at z=0, bed -0.25, water level -0.08. Channels enter/exit at tile edge centres so tiles chain.
Waterfalls: small = 2x2 m footprint, 2.0 m drop; big = 4x3 m footprint, 3.0 m drop. Pivot bottom-front ground level."""
import os
_bw = BUILD; BUILD = "none"
exec(open(os.path.join(TOOLS, "build_trn_zones.py")).read())   # brings trn_common, rocks, water_volume, water_mat2, cyl, ...
BUILD = _bw
random.seed(23)
RESULTS = {}
BANK = [(0.30,0.17,0.07),(0.42,0.27,0.12),(0.52,0.36,0.17)]
BANK_S = [(0.16,0.08,0.03),(0.24,0.13,0.05),(0.32,0.19,0.08)]
OLIVE = [(0.10,0.15,0.03),(0.16,0.22,0.05),(0.22,0.30,0.08)]
WDEEP, WSHAL = (0.015,0.17,0.21), (0.08,0.38,0.40)
def reed_tuft(bm, hl, H, x, y, n=5, cat=True):
    fs_b, fs_c = [], []
    for _ in range(n):
        bx,by = x+random.uniform(-0.05,0.05), y+random.uniform(-0.05,0.05)
        fs_b += blade(bm,hl,bx,by,H(bx,by),random.uniform(0.15,0.32),0.02,random.uniform(0,6.28),random.uniform(0.05,0.3))
    if cat:
        for _ in range(2):
            bx,by = x+random.uniform(-0.04,0.04), y+random.uniform(-0.04,0.04); h = random.uniform(0.28,0.4)
            fs_c += cyl(bm,bx,by,H(bx,by),0.005,h,seg=4) + cyl(bm,bx,by,H(bx,by)+h-0.08,0.016,0.075,seg=6)
    return fs_b, fs_c

# ================================ PONDS ================================
if BUILD == "ponds":
    coll = get_coll("TRN_Ponds")
    mbank = painted2("TRN_Pond_Bank", BANK, BANK_S, mask_cols=OLIVE, streak=0.45, bump=0.2)
    mw = water_mat2("TRN_Pond_Water", WDEEP, WSHAL)
    mr = rock_mat("TRN_Pond_Rock", moss_amt=0.4)
    mbl = blade_mat("TRN_Pond_Reed", (0.06,0.12,0.02),(0.30,0.42,0.10),(0.20,0.30,0.06),1.0)
    mcat = flat_mat("TRN_Pond_Cattail", (0.14,0.06,0.02), 0.8)
    for k,(R0,sd,elong) in enumerate([(0.72,1,1.25),(1.0,2,1.5),(1.3,3,1.45)]):
        bm,tl,ml,hl = new_bm()
        NR, NA = 14, 64
        def rad(a): return R0*(1+0.14*nn(math.cos(a)*1.5, math.sin(a)*1.5, 1.0, sd))
        def P(t,a):
            r = rad(a)*t; return (r*math.cos(a)*elong**0.5, r*math.sin(a)/elong**0.5)
        def prof(t, a): # t: 0 centre -> 1 outer edge
            rim = 0.11 + 0.03*nn(math.cos(a)*3, math.sin(a)*3, 1.0, sd+5)
            if t < 0.72: return -0.10 + 0.04*t
            if t < 0.84: return -0.07 + (rim+0.07)*sstep(0.72,0.84,t)
            return rim*(1-sstep(0.84,1.0,t)) + 0.0
        rings=[]
        for i in range(NR+1):
            t = i/NR; ring=[]
            for j in range(NA):
                a = 2*math.pi*j/NA; x,y = P(max(t,0.02),a); v = bm.verts.new((x,y,prof(t,a))); v[tl]=1.0
                v[ml] = 1.0 if (0.86 < t < 0.97 and nn(math.cos(a)*2,math.sin(a)*2,1.0,sd+9) > 0.05) else 0.0
                ring.append(v)
            rings.append(ring)
        blk=[]
        for a_,b_ in zip(rings[:-1],rings[1:]):
            for j in range(NA):
                q=(j+1)%NA; blk.append(bm.faces.new((a_[j],a_[q],b_[q],b_[j])))
        blk.append(bm.faces.new(rings[0]))
        low=[]
        for v in rings[-1]:
            nv = bm.verts.new((v.co.x*0.98, v.co.y*0.98, -0.12)); nv[tl]=0.0; low.append(nv)
        for j in range(NA):
            q=(j+1)%NA; blk.append(bm.faces.new((rings[-1][j],low[j],low[q],rings[-1][q])))
        blk.append(bm.faces.new(list(reversed(low))))
        bmesh.ops.recalc_face_normals(bm, faces=blk)
        wv=[]
        for j in range(NA):
            a=2*math.pi*j/NA; x,y=P(0.80,a); v=bm.verts.new((x,y,-0.035)); v[ml]=0.25; wv.append(v)
        wf=[bm.faces.new(wv)]
        for f in wf: f.material_index = 1
        def Hp(x,y):
            a = math.atan2(y*elong**0.5, x/elong**0.5); r = math.hypot(x/elong**0.5, y*elong**0.5)
            return prof(min(1.0, r/rad(a)), a)
        rk=[]
        for n_ in range(3+k):
            a = random.uniform(0,6.28); x,y = P(0.9,a)
            rk += faceted_rock(bm,(x,y,Hp(x,y)-0.02),(0.12+0.05*k,0.10+0.04*k,0.08+0.03*k),90+k*10+n_,K=9,dmin=0.6,boxy=0.2,sink=0.02)
        for f in rk: f.material_index = 2
        bl,ct = [],[]
        for n_ in range(2+k):
            a = random.uniform(0,6.28); x,y = P(0.88,a); b_,c_ = reed_tuft(bm,hl,Hp,x,y,5,cat=(n_%2==0)); bl+=b_; ct+=c_
        for _ in range(8):
            a = random.uniform(0,6.28); x,y = P(random.uniform(0.86,0.98),a); bl += clump(bm,hl,Hp,x,y,3,0.04,0.08,0.03,0.012)
        for f in bl: f.material_index = 3
        for f in ct: f.material_index = 4
        name = ["TRN_Pond_Small","TRN_Pond_Medium","TRN_Pond_Large"][k]
        pos = row(k,3,3.2)
        RESULTS[name] = finish(name, coll, bm, len(blk), [mbank,mw,mr,mbl,mcat], pos, "TRN_Ponds.jpg", {"water_level_m":-0.035})

# ================================ RIVER ================================
if BUILD == "river":
    coll = get_coll("TRN_River")
    mbank = painted2("TRN_River_Bank", BANK, BANK_S, mask_cols=OLIVE, streak=0.45, bump=0.15)
    mw = water_mat2("TRN_River_Water", WDEEP, WSHAL)
    mr = rock_mat("TRN_River_Rock", moss_amt=0.3)
    mbl = blade_mat("TRN_River_Reed", (0.06,0.12,0.02),(0.30,0.42,0.10),(0.20,0.30,0.06),1.0)
    mcat = flat_mat("TRN_River_Cattail", (0.14,0.06,0.02), 0.8)
    msand = painted2("TRN_River_Sand", [(0.48,0.38,0.22),(0.60,0.50,0.32),(0.70,0.62,0.45)], [(0.22,0.15,0.08),(0.32,0.23,0.13)], mask_cols=OLIVE, streak=0.4, bump=0.05)
    ZW = -0.08
    def seg_d(px,py,ax,ay,bx,by):
        vx,vy = bx-ax,by-ay; t = clamp(((px-ax)*vx+(py-ay)*vy)/(vx*vx+vy*vy))
        return math.hypot(px-ax-vx*t, py-ay-vy*t)
    def poly_d(x,y,pts): return min(seg_d(x,y,*pts[i],*pts[i+1]) for i in range(len(pts)-1))
    def bezier(p0,p1,p2,n=16): return [((1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t*t*p2[0], (1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t*t*p2[1]) for t in [i/n for i in range(n+1)]]
    W = 0.30
    def channel(paths, w=W, depth=0.25):
        def H(x,y):
            d = min(poly_d(x,y,p) for p in paths)
            bed = -depth*(1-sstep(w*0.65, w*1.05, d))
            return bed + 0.008*nn(x,y,2,1)*sstep(w,w*1.4,d) + shoulder(x,y)*sstep(w*1.0,w*1.2,d)
        M = lambda x,y: sstep(0.45,0.6,nn(x,y,2.0,7)+0.5)*sstep(w*1.4,w*2.0,min(poly_d(x,y,p) for p in paths))
        R = lambda x,y: min(poly_d(x,y,p) for p in paths) < w*1.15
        return H,M,R
    def deco(bm,hl,H,R,k):
        bl,ct,rk=[],[],[]
        for _ in range(2):
            for t in range(40):
                x,y = random.uniform(-0.85,0.85),random.uniform(-0.85,0.85)
                if not R(x,y) and not R(x*0.8,y*0.8): break
            b_,c_ = reed_tuft(bm,hl,H,x,y,4); bl+=b_; ct+=c_
        for _ in range(4):
            for t in range(40):
                x,y = random.uniform(-0.85,0.85),random.uniform(-0.85,0.85)
                if not R(x,y): break
            res=bmesh.ops.create_icosphere(bm,subdivisions=1,radius=random.uniform(0.03,0.06),matrix=Matrix.Translation((x,y,H(x,y)+0.01))@Matrix.Diagonal((1,0.8,0.55,1)))
            rk+=list({f for v in res["verts"] for f in v.link_faces})
        return bl,ct,rk
    TILES = [
      ("TRN_River_Straight", [bezier((0,-1.1),(0.15,0),(0,1.1))], None),
      ("TRN_River_Bend",     [bezier((0,-1.1),(0.05,0.0),(1.1,0.05))], None),
      ("TRN_River_Junction", [bezier((-1.1,0),(0,0.1),(1.1,0)), bezier((0,0),(0.05,-0.5),(0,-1.1))], None),
      ("TRN_River_Spring",   [bezier((-0.45,0.45),(0.1,0.0),(0,-1.1))], "spring"),
      ("TRN_River_Mouth",    [bezier((-1.1,0.2),(-0.3,0.1),(0.3,0.0))], "mouth"),
    ]
    for k,(name,paths,kind) in enumerate(TILES):
        if kind == "mouth":
            def H(x,y, p=paths[0]):
                d = poly_d(x,y,p); fan = sstep(-0.2,0.9,x)
                beach = 0.04 - 0.30*sstep(0.2,0.95, x + 0.25*math.cos(y*2.2))
                ch = -0.25*(1-sstep(W*0.65,W*1.05,d))
                return min(ch, beach) + shoulder(x,y)*(1-fan)
            M = lambda x,y: 0.0
            R = lambda x,y, p=paths[0]: poly_d(x,y,p) < W*1.1 or x > -0.1
            mats = [msand,mw,mr,mbl,mcat]
        else:
            H,M,R = channel(paths)
            if kind == "spring":
                H0 = H
                def H(x,y,H0=H0):
                    e = ((x+0.45)/0.32)**2+((y-0.45)/0.3)**2
                    return min(H0(x,y), -0.25*(1-sstep(0.7,1.1,e)) + shoulder(x,y))
                R0 = R; R = lambda x,y,R0=R0: R0(x,y) or ((x+0.45)/0.32)**2+((y-0.45)/0.3)**2 < 1.15
            mats = [mbank,mw,mr,mbl,mcat]
        bm,tl,ml,hl = new_bm(); fs = build_hf(bm,H,60,60,mask=M,top_layer=tl,mask_layer=ml); nb=len(fs)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        for f in water_volume(bm, R, H, ZW, n=56, foam_w=0.06): f.material_index = 1
        bl,ct,rk = deco(bm,hl,H,R,k)
        if kind == "spring":
            for i,(x,y,s) in enumerate([(-0.75,0.72,0.26),(-0.45,0.85,0.22),(-0.85,0.40,0.2),(-0.55,0.62,0.16)]):
                rk += faceted_rock(bm,(x,y,0),(s,s*0.9,s*0.9),300+i,K=10,dmin=0.62,boxy=0.2,sink=0.02)
            sv=[]   # small falling water sheet from the rock pile into the spring pool
            for j in range(9):
                t=j/8; z = 0.32*(1-t)**1.6 + ZW*t; yy = 0.62 - 0.15*t
                for xx in (-0.60,-0.48):
                    v = bm.verts.new((xx, yy, z)); v[ml] = 0.6*t; sv.append(v)
            sf=[bm.faces.new((sv[2*j],sv[2*j+1],sv[2*j+3],sv[2*j+2])) for j in range(8)]
            for f in sf: f.material_index = 1
        for f in rk: f.material_index = 2
        for f in bl: f.material_index = 3
        for f in ct: f.material_index = 4
        RESULTS[name] = finish(name, coll, bm, nb, mats, row(k,5), "TRN_River.jpg", {"water_level_m":ZW,"bed_m":-0.25})

# ================================ WATERFALLS ================================
if BUILD == "falls":
    coll = get_coll("TRN_Waterfalls")
    GR = [(0.10,0.21,0.02),(0.16,0.30,0.035),(0.23,0.39,0.05)]
    CLIFF = [(0.14,0.09,0.05),(0.22,0.15,0.09),(0.30,0.22,0.14)]
    mg = painted2("TRN_Falls_Ground", GR, BANK_S, mask_cols=CLIFF, streak=0.4, bump=0.25, zrange=(-T,1.0))
    mw = water_mat2("TRN_Falls_Pool", WDEEP, WSHAL)
    mr = rock_mat("TRN_Falls_Rock", moss_amt=1.0)
    # falling water: vertical white streaks over teal, slightly emissive so it reads as bright
    m, nt, bs = new_mat("TRN_Falls_Sheet")
    tc = nt.nodes.new("ShaderNodeTexCoord"); n = noise_n(nt, mapping(nt, tc.outputs["Object"], (14,14,0.6)), 2.0, 4, 0.5)
    r = ramp(nt, [(0.08,0.36,0.40),(0.35,0.62,0.64),(0.92,0.96,0.96)], [0.35,0.55,0.75]); nt.links.new(n.outputs["Fac"], r.inputs[0])
    nt.links.new(r.outputs[0], bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.1
    bs.inputs["Emission Color"].default_value = (0.6,0.8,0.8,1); bs.inputs["Emission Strength"].default_value = 0.15
    msheet = m
    mfoam = flat_mat("TRN_Falls_Foam", (0.85,0.9,0.9), 0.6)
    for k,(name,SX,SY,HT,NW,pos) in enumerate([("TRN_Waterfall_Small",1.0,1.0,2.0,0.20,(-2.2,2.2,0)),("TRN_Waterfall_Big",2.0,1.5,3.0,0.30,(2.2,-2.2,0))]):
        YC = 0.10   # normalized y where the cliff face is
        def Hn(u,v):
            top = HT - (0.15 if abs(u) < NW else 0.0)
            cliff = sstep(YC-0.03, YC+0.05, v + 0.04*nn(u,v,4,k))
            base = 0.0
            e = (u/0.55)**2 + ((v+0.42)/0.38)**2
            pool = -0.22*(1-sstep(0.7,1.1,e))
            z = base*(1-cliff) + top*cliff
            return min(z, pool if cliff < 0.5 else z) + shoulder(u,v,0.08)*(1 if cliff < 0.5 else 0.5)
        Mn = lambda u,v: sstep(YC-0.04,YC,v)*(1-sstep(YC+0.06,YC+0.1,v))
        bm,tl,ml,hl = new_bm(); fs = build_hf(bm,Hn,64,72,mask=Mn,top_layer=tl,mask_layer=ml,wall_rings=(0.3,0.6)); nb=len(fs)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        poolR = lambda u,v: (u/0.55)**2 + ((v+0.42)/0.38)**2 < 1.05 or (abs(u) < NW and v > YC+0.06)
        Hw = lambda u,v: Hn(u,v) - (HT if v > YC else 0.0)
        wf = water_volume(bm, lambda u,v: (u/0.55)**2 + ((v+0.42)/0.38)**2 < 1.05, Hn, -0.05, n=56, foam_w=0.04)
        # channel water on top
        cv=[]; 
        for j in range(2):
            for i in range(2): cv.append(bm.verts.new(((i*2-1)*NW*0.95, YC+0.06 + j*(0.97-YC-0.06), HT-0.05)))
        wf.append(bm.faces.new((cv[0],cv[1],cv[3],cv[2])))
        for f in wf: f.material_index = 1
        # the falling sheet
        sv=[]; NS=14
        for j in range(NS+1):
            t=j/NS; z = (HT-0.05)*(1-t) + (-0.05)*t; vv = YC+0.06 - 0.10*math.sin(t*math.pi*0.5) - 0.08*t
            w = NW*0.95*(1+0.25*t)
            for i in range(3): sv.append(bm.verts.new(((i-1)*w, vv + 0.02*nn(i,j,1.0,3), z)))
        sh=[]
        for j in range(NS):
            for i in range(2): sh.append(bm.faces.new((sv[3*j+i],sv[3*j+i+1],sv[3*(j+1)+i+1],sv[3*(j+1)+i])))
        for f in sh: f.material_index = 3
        # splash foam and rocks
        fo=[]
        for _ in range(7):
            x = random.uniform(-NW*1.2, NW*1.2); y = YC - 0.18 + random.uniform(-0.08,0.06)
            fo += faceted_rock(bm,(x,y,-0.07),(0.12*(1+k*0.6),0.10*(1+k*0.6),0.07*(1+k*0.6)),700+k*20+_,K=8,subdiv=2,cracks=0,dmin=0.8,sink=0.0)
        for f in fo: f.material_index = 4
        rk=[]
        side = [(-0.62,-0.25),(-0.72,0.0),(0.62,-0.25),(0.72,0.0),(-0.45,-0.75),(0.5,-0.72)]
        for i,(u,v) in enumerate(side):
            s = 0.20 + 0.06*random.random()
            rk += faceted_rock(bm,(u,v,0),(s,s*0.9,s*1.0),800+k*30+i,K=10,dmin=0.62,boxy=0.2)
        if k == 1:
            for i,u in enumerate((-0.62,0.62)):
                for l in range(4):
                    rk += faceted_rock(bm,(u+0.03*l*(1 if u<0 else -1), YC-0.02, 0.2+l*0.62),(0.26,0.22,0.36),900+i*10+l,K=10,dmin=0.62,boxy=0.25,sink=0.0)
            rk += faceted_rock(bm,(0.05, YC+0.02, HT-0.5),(0.12,0.12,0.45),950,K=10,dmin=0.62,boxy=0.3,sink=0.0)
        for f in rk: f.material_index = 2
        # scale normalized footprint to real size
        for v in bm.verts: v.co.x *= SX; v.co.y *= SY
        RESULTS[name] = finish(name, coll, bm, nb, [mg,mw,mr,msheet,mfoam], pos, "TRN_Waterfalls.jpg", {"drop_m":HT, "footprint_m":"%gx%g"%(2*SX,2*SY), "vfx_socket":"SOCKET_Splash at pool"})
