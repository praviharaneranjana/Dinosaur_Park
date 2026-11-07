"""Dino Park Tycoon - TRN v03 land zones: BUILD = volcano | desert | swamp  (see _Reference/TRN_reference_analysis_v02.md)"""
import os
_bv3b = BUILD; BUILD = "none"
exec(open(os.path.join(TOOLS, "build_trn_v3.py")).read())
BUILD = _bv3b
random.seed(404)
RESULTS = {}

def side_drip(name, pal, drip_pal, top_z, drip=0.18, edge=(0.4,0.3,0.2), wet=None, streaks=0.5):
    """vertical side wall: base palette, vertical streaks, moss/grass drips hanging from top_z"""
    m = painterly(name, pal, edge=edge, cavity=tuple(c*0.25 for c in pal[0]), dirt=tuple(c*0.6 for c in pal[0]), dirt_h=-0.2,
                  strokes=0.6, crack_lines=0.3, crack_scale=1.6, toplight=0.15, wet=wet)
    nt = m.node_tree; bs = [n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'][0]
    src = bs.inputs["Base Color"].links[0].from_socket
    obj = objco(nt); s = sep(nt, obj)
    vs = noise_n(nt, vmul(nt, obj, (9.0, 9.0, 0.7)), 2.0, 3, 0.5)
    col = mix(nt, src, maprange(nt, vs.outputs["Fac"], 0.3, 0.7, 0.7, 1.15), streaks, 'MULTIPLY')
    dn = noise_n(nt, obj, 4.0, 3, 0.55)
    lim = mathop(nt, mathop(nt, maprange(nt, dn.outputs["Fac"], 0.45, 0.75, 0.0, drip), -1.0), top_z - 0.025, 'ADD')
    band = maprange(nt, mathop(nt, s[2], lim, 'SUBTRACT'), -0.005, 0.005)
    gr = ramp(nt, drip_pal); nt.links.new(dn.outputs["Fac"], gr.inputs[0])
    nt.links.new(mix(nt, col, gr.outputs[0], band), bs.inputs["Base Color"])
    return m

def slab_layer(bm, cx, cy, z0, th, rx, ry, seed, rot=0.0, corners=9):
    """one sandstone/basalt layer: angular irregular outline, near-vertical side with a slight lip, flat top"""
    rnd = random.Random(seed); N = 40
    ang = sorted(rnd.uniform(0, 2*math.pi) for _ in range(corners)); rr = [rnd.uniform(0.82, 1.1) for _ in range(corners)]
    def outline(t):
        a = 2*math.pi*t; k = 0
        while k < corners and ang[k] < a: k += 1
        i0, i1 = (k-1) % corners, k % corners; a0, a1 = ang[i0], ang[i1]
        if a1 <= a0: a1 += 2*math.pi
        aa = a if a >= a0 else a + 2*math.pi; f = (aa-a0)/(a1-a0)
        p0 = Vector((math.cos(a0)*rr[i0], math.sin(a0)*rr[i0])); p1 = Vector((math.cos(a1)*rr[i1], math.sin(a1)*rr[i1]))
        return p0.lerp(p1, f)
    pts = [outline(i/N) for i in range(N)]
    rings = []
    for (hf, rf) in ((0.0,0.965),(0.12,0.99),(0.5,1.0),(0.88,1.0),(1.0,0.975)):
        ring = []
        for i in range(N):
            lx, ly = pts[i].x*rx*rf, pts[i].y*ry*rf
            x = cx + lx*math.cos(rot) - ly*math.sin(rot); y = cy + lx*math.sin(rot) + ly*math.cos(rot)
            z = z0 + th*hf + (0.006*noise.noise(Vector((x*5, y*5, z0*3+seed))) if 0 < hf < 1 else 0.0)
            ring.append(bm.verts.new((x, y, z)))
        rings.append(ring)
    fs = []
    for a_, b_ in zip(rings[:-1], rings[1:]):
        for i in range(N):
            j = (i+1) % N; fs.append(bm.faces.new((a_[i], a_[j], b_[j], b_[i])))
    c = bm.verts.new((cx, cy, z0+th+0.004)); fs += [bm.faces.new((rings[-1][i], rings[-1][(i+1)%N], c)) for i in range(N)]
    cb = bm.verts.new((cx, cy, z0)); fs += [bm.faces.new((rings[0][(i+1)%N], rings[0][i], cb)) for i in range(N)]
    return fs

def disc(bm, r, seed, ry=None, z=0.02, wob=0.12):
    ry = ry or r*0.85; N = 56; c = bm.verts.new((0, 0, z)); ring = []; lip = []
    for i in range(N):
        a = 2*math.pi*i/N; k = 1+wob*noise.noise(Vector((math.cos(a)*2, math.sin(a)*2, seed)))
        ring.append(bm.verts.new((r*k*math.cos(a), ry*k*math.sin(a), z))); lip.append(bm.verts.new((r*k*1.04*math.cos(a), ry*k*1.04*math.sin(a), 0.0)))
    return [bm.faces.new((c, ring[i], ring[(i+1)%N])) for i in range(N)] + [bm.faces.new((ring[i], lip[i], lip[(i+1)%N], ring[(i+1)%N])) for i in range(N)]

def scatter_pebbles(bm, H, n, rmin, rmax, seed, lim=0.86, avoid=None):
    fs = []; rnd = random.Random(seed)
    for _ in range(n):
        x, y = rnd.uniform(-lim, lim), rnd.uniform(-lim, lim)
        if avoid and avoid(x, y): continue
        r = rnd.uniform(rmin, rmax)
        res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r, matrix=Matrix.Translation((x, y, H(x,y)+r*0.12)) @ Matrix.Rotation(rnd.uniform(0,6.28),4,'Z') @ Matrix.Diagonal((1, rnd.uniform(0.6,1), rnd.uniform(0.4,0.65), 1)))
        fs += list({f for v in res["verts"] for f in v.link_faces})
    return fs

# ====================================================================== VOLCANO
if BUILD == "volcano":
    coll = get_coll("TRN_VolcanoIsland")
    BAS = [(0.010,0.009,0.008),(0.020,0.018,0.016),(0.032,0.028,0.025),(0.048,0.042,0.037)]
    ASH = [(0.045,0.043,0.040),(0.068,0.065,0.060),(0.095,0.091,0.085)]
    LAVA = ((0.45,0.04,0.005),(1.0,0.24,0.02),(1.0,0.52,0.10))
    mash = painterly("TRN_Volc_Ash3", ASH, edge=(0.20,0.19,0.17), cavity=(0.008,0.008,0.007), dirt=(0.035,0.022,0.014), dirt_h=-9, scale=0.9, strokes=1.0, speckle=0.55, toplight=0.3, bands=[(0.04,0.038,0.035),(0.075,0.07,0.064),(0.05,0.047,0.043),(0.10,0.095,0.088)], band_scale=1.2)
    mash_s = side_drip("TRN_Volc_AshSide3", [(0.030,0.020,0.014),(0.050,0.032,0.021),(0.075,0.048,0.030)], [(0.06,0.057,0.053),(0.09,0.086,0.08)], 0.0, drip=0.05, edge=(0.30,0.17,0.08))
    mpeb = painterly("TRN_Volc_Pebble3", BAS, edge=(0.24,0.21,0.19), cavity=(0.005,0.005,0.004), dirt_h=-9, scale=8, toplight=0.45)
    Ha = lambda x,y: (0.022*nn(x,y,1.2,1)+0.008*nn(x,y,5,2))*edge_fade(x,y) + shoulder(x,y)
    RESULTS["TRN_Volcano_Ash"] = tile_hq("TRN_Volcano_Ash", coll, Ha, [mash, mash_s, mpeb], row(0,4,2.6), "TRN_VolcanoIsland.jpg", n=56,
                                         details=[(2, lambda bm,hl: scatter_pebbles(bm, Ha, 70, 0.010, 0.05, 3))])
    # --- lava plates: raised basalt plates (each its own height/tone), charred rims, deep glowing cracks; cracks also glow on the sides
    rs = random.Random(9); seeds = [(rs.uniform(-1.05,1.05), rs.uniform(-1.05,1.05)) for _ in range(14)]
    def pinfo(x,y):
        ds = sorted((math.hypot(x-sx, y-sy), i) for i,(sx,sy) in enumerate(seeds)); return ds[1][0]-ds[0][0], ds[0][1]
    def Hl(x,y):
        g, pid = pinfo(x+0.035*nn(x,y,3,4), y+0.035*nn(x,y,3,5))
        top = 0.055 + 0.03*((pid*37) % 7)/7 + 0.012*nn(x,y,3,pid)
        return top*sstep(0.006, 0.042, g) - 0.07*(1-sstep(0.0, 0.016, g)) + shoulder(x,y)
    mpl = painterly("TRN_Volc_Plate3", BAS, edge=(0.34,0.18,0.08), cavity=(0.004,0.003,0.002), dirt=(0.22,0.07,0.015), dirt_h=-9, scale=2.2, strokes=0.5, speckle=0.3,
                    toplight=0.5, edge_amt=0.7, emission=glow_emission(LAVA, strength=6.0))
    mpl_s = painterly("TRN_Volc_PlateSide3", [(0.02,0.014,0.01),(0.04,0.025,0.015),(0.08,0.035,0.012)], edge=(0.40,0.18,0.05), cavity=(0.006,0.004,0.003),
                      dirt=(0.25,0.07,0.012), dirt_h=-0.28, strokes=0.5, emission=glow_emission(LAVA, strength=3.5, lines=1.3))
    bm,tl,ml,hl = new_bm2(); gl = bm.verts.layers.float["glow"]
    fs = build_hf(bm, Hl, 120, 120, top_layer=tl, mask_layer=ml, wall_rings=(0.25,0.5,0.75)); nb = len(fs)
    for v in bm.verts:
        if v[tl] > 0.5:
            g,_ = pinfo(v.co.x+0.035*nn(v.co.x,v.co.y,3,4), v.co.y+0.035*nn(v.co.x,v.co.y,3,5)); v[gl] = 1-sstep(0.0, 0.022, g)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    for f in fs: f.material_index = 0 if sum(v[tl] for v in f.verts)/len(f.verts) > 0.5 else 1
    RESULTS["TRN_Volcano_LavaPlates"] = finish_hq("TRN_Volcano_LavaPlates", coll, bm, nb, [mpl, mpl_s], row(1,4,2.6), "TRN_VolcanoIsland.jpg")
    # --- big blocky lava rocks with thin glowing veins on ash patches
    mlr = painterly("TRN_Volc_LavaRock3", BAS, edge=(0.17,0.10,0.055), cavity=(0.004,0.003,0.002), dirt=(0.22,0.06,0.012), dirt_h=0.08, scale=2.0, strokes=0.45,
                    speckle=0.25, toplight=0.55, edge_amt=0.45, emission=glow_emission(LAVA, strength=4.0, lines=1.5))
    mdisc = painterly("TRN_Volc_AshDisc3", [(0.022,0.021,0.02),(0.035,0.033,0.031),(0.05,0.047,0.044)], edge_amt=0.0, cav_amt=0.3, dirt_h=-9, speckle=0.5, strokes=0.5)
    ROCKS = [("TRN_LavaRock_Small", (0.48,0.42,0.42), 311, 0.70), ("TRN_LavaRock_Low", (0.80,0.60,0.46), 312, 0.95),
             ("TRN_LavaRock_Tall", (0.52,0.48,1.05), 313, 0.80), ("TRN_LavaRock_Cube", (0.52,0.46,0.52), 314, 0.75)]
    for k,(name,size,sd,dr) in enumerate(ROCKS):
        bm,tl,ml,hl = new_bm2()
        rock_hq(bm, center=(0,0,0), size=size, seed=sd, K=11, boxy=0.55, flat_top=0.14, dmin=0.78, sink=0.03, subdiv=5, cracks=2, crack_depth=0.03)
        for f in disc(bm, dr, 500+k, wob=0.18): f.material_index = 1
        for f in scatter_pebbles(bm, lambda x,y: 0.02, 10, 0.02, 0.05, 60+k, lim=dr*0.9, avoid=lambda x,y: math.hypot(x,y) < size[0]*0.9): f.material_index = 1
        RESULTS[name] = make_obj_hq(name, coll, bm, [mlr, mdisc], row(k,4,2.3,(-1.8,-1.8)), "TRN_VolcanoIsland.jpg")
    # --- mini volcano: glowing core cone wrapped in jagged basalt shards, lava in the gaps, crater glow, smoke preview
    mcore = painterly("TRN_Volc_Core3", BAS, edge=(0.17,0.10,0.055), cavity=(0.004,0.003,0.002), dirt_h=-9, scale=2.0, toplight=0.5, emission=glow_emission(LAVA, strength=4.5))
    msm = volume_mat("TRN_Volc_Smoke3", (0.62,0.62,0.63), 7.0, 2.6)
    bm,tl,ml,hl = new_bm2(); gl = bm.verts.layers.float["glow"]
    SEG, NR = 64, 18; rings = []
    def runnel(a, t): return (1-sstep(0.0, 0.10, abs(math.sin(a*2.5 + 0.6 + 0.5*noise.noise(Vector((a, t*3, 7)))))))*sstep(0.15, 0.6, t)
    for k in range(NR+1):
        t = k/NR; h = t*1.42; ring = []
        for i in range(SEG):
            a = 2*math.pi*i/SEG
            ridge = 0.13*abs(noise.noise(Vector((math.cos(a)*3, math.sin(a)*3, t*2)))) + 0.05*noise.noise(Vector((a*4, t*6, 3)))
            r = (0.88*(1-t)**1.35 + 0.15*t)*(1 + ridge - 0.12*runnel(a, t))
            v = bm.verts.new((r*math.cos(a), r*math.sin(a), h + 0.02*noise.noise(Vector((a*3, t*5, 1)))))
            v[gl] = min(1.0, 0.95*runnel(a, t) + sstep(0.86, 1.0, t)); ring.append(v)
        rings.append(ring)
    crater = []
    for i in range(SEG):
        a = 2*math.pi*i/SEG; v = bm.verts.new((0.11*math.cos(a), 0.11*math.sin(a), 1.30)); v[gl] = 1.0; crater.append(v)
    core = []
    for ra, rb in zip(rings, rings[1:]+[crater]):
        for i in range(SEG):
            j = (i+1) % SEG; core.append(bm.faces.new((ra[i], ra[j], rb[j], rb[i])))
    core.append(bm.faces.new(crater))
    shards = []
    for lvl in range(7):
        t = lvl/7.0; z = t*1.30; r = 0.88*(1-t)**1.35 + 0.15*t; n = max(5, int(17 - lvl*2))
        for j in range(n):
            a = 2*math.pi*j/n + lvl*0.45 + random.uniform(-0.12, 0.12)
            if runnel(a, t+0.08) > 0.25: continue     # keep lava runnels open
            s = 1 - 0.10*lvl
            shards += rock_hq(bm, center=(r*0.92*math.cos(a), r*0.92*math.sin(a), max(0.0, z-0.05)), size=(0.22*s, 0.17*s, 0.46*s),
                              seed=1000+lvl*20+j, K=10, boxy=0.45, dmin=0.7, sink=0.0, subdiv=4, rot=a)
    for i in range(8):
        a = 2*math.pi*i/8; shards += rock_hq(bm, center=(0.16*math.cos(a), 0.16*math.sin(a), 1.22), size=(0.08,0.07,0.16), seed=1200+i, K=8, boxy=0.35, sink=0.0, subdiv=3, rot=a)
    for f in core: f.material_index = 1
    for f in disc(bm, 1.35, 777, wob=0.15): f.material_index = 2
    sm = []
    for (cx,cy,cz,s) in ((0,0,1.55,0.20),(0.06,0.04,1.82,0.28),(0.16,0.08,2.15,0.34),(0.25,0.16,2.5,0.40),(0.36,0.22,2.85,0.42)):
        sm += blob(bm, (cx,cy,cz), (s, s*0.9, s*0.8), 2)
    for f in sm: f.material_index = 3
    RESULTS["TRN_Volcano_Mini"] = make_obj_hq("TRN_Volcano_Mini", coll, bm, [mlr, mcore, mdisc, msm], row(3,4,2.6,(1.0,1.0)), "TRN_VolcanoIsland.jpg",
                                              {"vfx_socket":"SOCKET_Smoke (0,0,1.32); smoke mesh is preview only"}, sharp=40)

# ====================================================================== DESERT
if BUILD == "desert":
    coll = get_coll("TRN_DesertIsland")
    SO = [(0.66,0.24,0.06),(0.78,0.36,0.11),(0.88,0.50,0.20)]
    SP = [(0.70,0.30,0.22),(0.80,0.42,0.32),(0.88,0.55,0.42)]
    SS = [(0.40,0.12,0.03),(0.50,0.18,0.055),(0.60,0.26,0.09)]
    def sandmat(name, pal):
        return painterly(name, pal, edge=(0.95,0.62,0.32), cavity=(0.30,0.09,0.03), dirt=pal[0], dirt_h=-9, scale=1.3, strokes=0.75, speckle=0.12,
                         toplight=0.15, edge_amt=0.2, cav_amt=0.7, bump=0.12)
    ms, mp = sandmat("TRN_Desert_Sand3", SO), sandmat("TRN_Desert_SandPink3", SP)
    mside = side_drip("TRN_Desert_Side3", SS, [(0.70,0.30,0.09),(0.80,0.40,0.14)], 0.0, drip=0.04, edge=(0.8,0.45,0.2), streaks=0.35)
    def Hrip(x,y):
        r = ((x*0.6 + y*0.8)*5.5 + 0.35*nn(x,y,1.4,3)) % 1.0
        saw = sstep(0.0, 0.78, r) - sstep(0.78, 1.0, r)            # gentle windward, steep lee ripple
        return (0.016*saw + 0.010*nn(x,y,1.2,4))*edge_fade(x,y,0.04,0.25) + shoulder(x,y)
    RESULTS["TRN_Desert_Ripples"] = tile_hq("TRN_Desert_Ripples", coll, Hrip, [ms, mside], row(0,4,2.6), "TRN_DesertIsland.jpg", n=110)
    def barchan(x, y, h, cx, amp, freq, phase, wind, lee, horn=0.35):
        crest = cx + amp*math.cos(y*freq + phase); d = x - crest
        if d < 0: z = h*max(0.0, 1+d/wind)**1.25*sstep(-wind, -wind*0.6, d)**0.3     # long windward ramp up to a sharp crest
        else: z = h*max(0.0, 1-d/lee)**1.15*(1 - 0.25*sstep(lee*0.5, lee, d))      # steep straight slip face
        ripple = 0.004*math.sin((x*0.8+y*0.5)*30 + 2*nn(x,y,2,9))*(1 if d < -0.1 else 0)
        return z*(1-horn*y*y) + ripple
    def rot(x, y, a): c, s = math.cos(a), math.sin(a); return x*c - y*s, x*s + y*c
    H2 = lambda x,y: barchan(*rot(x,y,0.5), 0.30, 0.25, 0.30, 1.6, 0.4, 1.4, 0.42)*edge_fade(x,y,0.03,0.30) + shoulder(x,y)
    H3 = lambda x,y: barchan(*rot(x,y,-0.35), 0.62, 0.12, 0.40, 1.9, 0.0, 1.5, 0.45)*edge_fade(x,y,0.03,0.26) + shoulder(x,y)
    H4 = lambda x,y: barchan(*rot(x,y,1.2), 0.55, 0.18, 0.34, 1.5, 0.8, 1.4, 0.42)*edge_fade(x,y,0.03,0.26) + shoulder(x,y)
    RESULTS["TRN_Desert_DuneLow"]   = tile_hq("TRN_Desert_DuneLow",   coll, H2, [mp, mside], row(1,4,2.6), "TRN_DesertIsland.jpg", n=96)
    RESULTS["TRN_Desert_DuneHigh"]  = tile_hq("TRN_Desert_DuneHigh",  coll, H3, [ms, mside], row(2,4,2.6), "TRN_DesertIsland.jpg", n=96)
    RESULTS["TRN_Desert_DuneRidge"] = tile_hq("TRN_Desert_DuneRidge", coll, H4, [ms, mside], row(3,4,2.6), "TRN_DesertIsland.jpg", n=96)
    # --- layered sandstone mesas: each layer dark base -> pink stripe -> orange -> pale top, cracked, worn edges
    TH = 0.18
    mstone = painterly("TRN_Desert_Sandstone3", [(0.58,0.24,0.08),(0.68,0.32,0.12),(0.78,0.42,0.18)], edge=(0.98,0.76,0.48), cavity=(0.10,0.03,0.01),
                       dirt=(0.35,0.12,0.04), dirt_h=0.05, scale=2.2, strokes=0.45, crack_lines=0.8, crack_scale=2.4, toplight=0.3, edge_amt=0.3)
    nt = mstone.node_tree; bs = [n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'][0]; src = bs.inputs["Base Color"].links[0].from_socket
    oz = sep(nt, objco(nt))[2]
    lay = ramp(nt, [(0.34,0.10,0.04),(0.34,0.10,0.04),(0.82,0.45,0.40),(0.86,0.52,0.46),(0.72,0.31,0.09),(0.80,0.40,0.13),(0.93,0.64,0.33)], [0.0,0.08,0.14,0.27,0.34,0.7,0.9])
    nt.links.new(mathop(nt, mathop(nt, oz, 1.0/TH), 1.0, 'FRACT'), lay.inputs[0])
    nt.links.new(mix(nt, lay.outputs[0], src, 0.35, 'SOFT_LIGHT'), bs.inputs["Base Color"])
    mdisc = painterly("TRN_Desert_Disc3", SO, edge_amt=0.0, cav_amt=0.3, dirt_h=-9, strokes=0.6, speckle=0.15)
    def mesa(name, stacks, bridge, dr, pos, seed):
        bm,tl,ml,hl = new_bm2(); rnd = random.Random(seed); k = 0
        for (cx, cy, rx, ry, nl) in stacks:
            for l in range(nl):
                s = 1 - 0.075*l + rnd.uniform(-0.04, 0.04)
                slab_layer(bm, cx + rnd.uniform(-0.05,0.05), cy + rnd.uniform(-0.04,0.04), l*TH, TH*rnd.uniform(0.94,1.0), rx*s, ry*s, seed+k, rnd.uniform(-0.3,0.3)); k += 1
            if l == 0:
                for q in range(3):
                    aq = rnd.uniform(0, 6.28); rock_hq(bm, center=(cx+math.cos(aq)*rx*1.05, cy+math.sin(aq)*ry*1.05, 0.0), size=(0.13,0.11,0.12), seed=seed+90+q+k*7, K=8, boxy=0.6, dmin=0.8, sink=0.0, subdiv=3)
        if bridge:
            z0, layers = bridge
            for l in range(layers):
                slab_layer(bm, 0.02, 0.03, z0 + l*TH, TH, 1.12 - 0.10*l, 0.62 - 0.05*l, seed+50+l, rnd.uniform(-0.1,0.1), corners=11)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        nb = len(bm.faces)
        for f in disc(bm, dr, seed, wob=0.08): f.material_index = 1
        RESULTS[name] = finish_hq(name, coll, bm, nb, [mstone, mdisc], pos, "TRN_DesertIsland.jpg")
    mesa("TRN_Desert_Mesa_Small", [(0, 0, 0.62, 0.54, 5)], None, 1.05, row(0,2,3.6,(-2.2,-2.2)), 600)
    mesa("TRN_Desert_Mesa_Arch", [(-0.58, 0.0, 0.48, 0.60, 4), (0.60, 0.05, 0.52, 0.64, 4)], (4*TH, 2), 1.6, row(1,2,3.6,(-2.2,-2.2)), 700)

# ====================================================================== SWAMP
if BUILD == "swamp":
    coll = get_coll("TRN_SwampIsland")
    PEAT = [(0.008,0.009,0.006),(0.015,0.016,0.010),(0.026,0.027,0.017)]
    MOSS3 = [(0.03,0.07,0.01),(0.07,0.15,0.02),(0.13,0.25,0.035),(0.20,0.33,0.05)]
    mpeat = painterly("TRN_Swamp_Peat3", PEAT, edge=(0.10,0.10,0.07), cavity=(0.002,0.002,0.0015), dirt=PEAT[0], dirt_h=-9, scale=2.4, strokes=0.6, speckle=0.35, wet=(0.12,0.5), toplight=0.25)
    mask_mix(mpeat, MOSS3[:3], soft=0.1)
    mside = side_drip("TRN_Swamp_Side3", [(0.010,0.009,0.006),(0.020,0.017,0.010),(0.032,0.027,0.016)], MOSS3[1:], 0.0, drip=0.16, edge=(0.12,0.10,0.07), wet=(0.2,0.5))
    mmoss = painterly("TRN_Swamp_Moss3", MOSS3, edge=(0.34,0.50,0.11), cavity=(0.004,0.012,0.002), dirt_h=-9, scale=9, strokes=0.35, speckle=0.35, toplight=0.45, bump=0.6)
    mleaf = [painterly("TRN_Swamp_Leaf3_%d" % i, c, edge=e, cavity=(0.02,0.01,0.004), dirt_h=-9, scale=14, strokes=0.3, speckle=0.12, edge_amt=0.45, toplight=0.35)
             for i,(c,e) in enumerate((([(0.14,0.06,0.018),(0.22,0.10,0.028)],(0.42,0.24,0.08)),
                                       ([(0.28,0.13,0.03),(0.38,0.19,0.05)],(0.60,0.38,0.12)),
                                       ([(0.07,0.035,0.012),(0.12,0.055,0.018)],(0.28,0.15,0.06))))]
    mfern = blade_mat("TRN_Swamp_Fern3", (0.015,0.05,0.006),(0.18,0.38,0.06),(0.09,0.22,0.03),1.0)
    mtwig = painterly("TRN_Swamp_Twig3", [(0.05,0.03,0.013),(0.09,0.055,0.022)], edge=(0.28,0.18,0.09), dirt_h=-9, scale=10)
    mgr = blade_mat("TRN_Swamp_Sprout3", (0.02,0.06,0.008),(0.16,0.34,0.05),(0.09,0.2,0.03),1.0)

    def leaf3(bm, H, x, y, L, seed):
        rnd = random.Random(seed); a = rnd.uniform(0, 6.28); curl = rnd.uniform(0.25, 0.7); lift = rnd.uniform(0.0, 0.5)
        z0 = H(x, y) + 0.005; NU, NV = 8, 4; grid = []
        for i in range(NU+1):
            u = -1 + 2*i/NU; w = 0.42*math.sqrt(max(0.0, 1-u*u))*(1-0.15*u); row_ = []
            for j in range(NV+1):
                v = -1 + 2*j/NV; lx, ly = u*L, v*w*L
                lz = curl*abs(v)*w*L*1.3 + lift*L*0.35*((u+1)/2)**2 + 0.004*noise.noise(Vector((u*3, v*3, seed)))
                row_.append(bm.verts.new((x + lx*math.cos(a) - ly*math.sin(a), y + lx*math.sin(a) + ly*math.cos(a), z0 + lz)))
            grid.append(row_)
        fs = [bm.faces.new((grid[i][j], grid[i+1][j], grid[i+1][j+1], grid[i][j+1])) for i in range(NU) for j in range(NV)]
        res = bmesh.ops.solidify(bm, geom=fs, thickness=0.0035)
        return list({f for g in res["geom"] if isinstance(g, bmesh.types.BMFace) for f in [g]} | set(fs))
    def cushion(bm, H, x, y, s, seed):
        res = bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
        off = Vector((seed*0.37, seed*0.11, 0))
        for v in res["verts"]:
            p = v.co.copy(); r = 1 + 0.18*noise.noise(p*2.2 + off) + 0.07*noise.noise(p*7 + off)
            q = p*r; v.co = Vector((x + q.x*s, y + q.y*s*0.85, H(x,y) - s*0.16 + max(-0.1, q.z)*s*0.42))
        return list({f for v in res["verts"] for f in v.link_faces})
    def frond3(bm, hl, x, y, z, ang, L, arch=0.6):
        fs = []; n = 14; dx, dy = math.cos(ang), math.sin(ang); px, py = -dy, dx
        pts = [Vector((x+dx*L*t, y+dy*L*t, z + L*(arch*t - 0.62*t*t))) for t in [k/n for k in range(n+1)]]
        for k in range(n):
            a, b = pts[k], pts[k+1]; t = k/n; ww = 0.055*(1-t*0.8)*(0.5 if k == 0 else 1.0)
            for s in (-1, 1):
                tip = (a+b)/2 + Vector((px*s*ww*2.4 + dx*ww*0.9, py*s*ww*2.4 + dy*ww*0.9, -0.014))
                va, vb, vc = bm.verts.new(a), bm.verts.new(b), bm.verts.new(tip); va[hl] = t; vb[hl] = t; vc[hl] = min(1, t+0.35)
                fs.append(bm.faces.new((va, vb, vc)))
        return fs
    def fern(bm, hl, H, x, y, n=10, L=0.40):
        fs = []; z = H(x,y)
        for k in range(n): fs += frond3(bm, hl, x, y, z, k*2*math.pi/n + random.uniform(-0.25,0.25), L*random.uniform(0.8,1.15), random.uniform(0.5,0.8))
        return fs
    def twig(bm, H, x, y, L, a, seed):
        fs = []; pts = []
        for i in range(6):
            t = i/5; px_ = x + math.cos(a)*L*t + 0.02*noise.noise(Vector((t*3, seed, 0))); py_ = y + math.sin(a)*L*t + 0.02*noise.noise(Vector((seed, t*3, 0)))
            pts.append((px_, py_, H(px_, py_) + 0.008))
        for i in range(5):
            (x0,y0,z0),(x1,y1,z1) = pts[i], pts[i+1]; seg = math.hypot(x1-x0, y1-y0)
            fs += box(bm, ((x0+x1)/2, (y0+y1)/2, (z0+z1)/2), (seg*1.05, 0.011, 0.011), Matrix.Rotation(math.atan2(y1-y0, x1-x0), 4, 'Z'))
        return fs
    def dress(bm, hl, H, rng, avoid, n_leaf, n_moss, ferns, n_twig, n_sprout, moss_mask=None):
        """returns {material_index: faces}"""
        out = {2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}
        for i in range(n_leaf):
            for _t in range(30):
                x, y = rng.uniform(-0.9, 0.9), rng.uniform(-0.9, 0.9)
                if not avoid(x, y): break
            out[rng.choice((2,3,3,4))] += leaf3(bm, H, x, y, rng.uniform(0.045, 0.085), 3000+i)
        for i in range(n_moss):
            for _t in range(40):
                x, y = rng.uniform(-0.88, 0.88), rng.uniform(-0.88, 0.88)
                if not avoid(x, y) and (moss_mask is None or moss_mask(x, y) > 0.3 or rng.random() < 0.2): break
            out[5] += cushion(bm, H, x, y, rng.uniform(0.05, 0.15), i)
        for (x, y) in ferns: out[6] += fern(bm, hl, H, x, y)
        for i in range(n_twig):
            for _t in range(30):
                x, y = rng.uniform(-0.8, 0.8), rng.uniform(-0.8, 0.8)
                if not avoid(x, y): break
            out[7] += twig(bm, H, x, y, rng.uniform(0.12, 0.28), rng.uniform(0, 3.14), i)
        for i in range(n_sprout):
            for _t in range(30):
                x, y = rng.uniform(-0.88, 0.88), rng.uniform(-0.88, 0.88)
                if not avoid(x, y): break
            out[8] += tuft(bm, hl, H, x, y, n=3, hmin=0.03, hmax=0.07)
        return out
    MATS = lambda extra: [mpeat, mside] + mleaf + [mmoss, mfern, mtwig, mgr] + extra
    # --- 1 moss ground: black wet soil, moss cushions, leaf litter (every leaf 3D + own shadow), ferns, twigs, sprouts
    Hm = lambda x,y: (0.016*nn(x,y,1.6,2)+0.006*nn(x,y,5,3))*edge_fade(x,y) + shoulder(x,y)
    Mm = lambda x,y: sstep(0.5,0.6,nn(x,y,2.4,9)+0.5) + (1-sstep(0.02,0.14,edge_d(x,y)))*sstep(0.45,0.55,nn(x,y,5,10)+0.5)
    bm,tl,ml,hl = new_bm2(); fs = build_hf(bm, Hm, 72, 72, mask=Mm, top_layer=tl, mask_layer=ml); nb = len(fs)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    for f in fs: f.material_index = 0 if sum(v[tl] for v in f.verts)/len(f.verts) > 0.5 else 1
    for k, lst in dress(bm, hl, Hm, random.Random(5), lambda x,y: False, 120, 22, [(-0.6,0.62),(0.6,0.42),(-0.2,-0.58),(0.66,-0.64)], 12, 30, Mm).items():
        for f in lst: f.material_index = k
    RESULTS["TRN_Swamp_MossGround"] = finish_hq("TRN_Swamp_MossGround", coll, bm, nb, MATS([]), row(0,3), "TRN_SwampIsland.jpg")
    # --- 2 algae pool: irregular water body reaching the front edges (water visible on the tile sides), mossy banks, floating algae rafts
    def pond_e(x,y): return (((x-0.06)/0.98)**2 + ((y+0.12)/0.92)**2)*(1+0.30*nn(x,y,1.8,31))
    def Hp(x,y):
        e = pond_e(x,y); basin = 1-sstep(0.8,1.08,e)
        return (0.014*nn(x,y,2,4))*(1-basin) - 0.22*basin + shoulder(x,y)*(1-basin)
    Mp = lambda x,y: sstep(0.9,1.2,pond_e(x,y))*sstep(0.35,0.55,nn(x,y,3,12)+0.5) + sstep(1.0,1.15,pond_e(x,y))*0.6
    ZP = -0.035
    mpool = water_hq("TRN_Swamp_PoolWater3", (0.07,0.17,0.08),(0.035,0.11,0.05),(0.015,0.05,0.025), foam=(0.14,0.26,0.10), strokes=0.4, ripple='swirl', depth_range=0.18,
                     algae=[(0.10,0.22,0.03),(0.18,0.34,0.06)], sky=(0.45,0.6,0.5), shore_foam=0.4)
    malg = painterly("TRN_Swamp_Algae3", [(0.10,0.22,0.03),(0.18,0.33,0.06),(0.26,0.42,0.09)], edge=(0.4,0.55,0.15), cavity=(0.02,0.05,0.01), dirt_h=-9, scale=8, strokes=0.3, toplight=0.4)
    bm,tl,ml,hl = new_bm2(); fs = build_hf(bm, Hp, 72, 72, mask=Mp, top_layer=tl, mask_layer=ml); nb = len(fs)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    for f in fs: f.material_index = 0 if sum(v[tl] for v in f.verts)/len(f.verts) > 0.5 else 1
    onbank = lambda x,y: pond_e(x,y) < 1.12
    for k, lst in dress(bm, hl, Hp, random.Random(15), onbank, 40, 14, [(-0.78,0.78)], 4, 16).items():
        for f in lst: f.material_index = k
    wf = water_volume_hq(bm, lambda x,y: pond_e(x,y) < 1.06, Hp, ZP, n=72)
    for f in wf: f.material_index = 9
    rafts = []; rnd = random.Random(13)
    for _ in range(9):
        cx, cy = rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.5)
        if pond_e(cx, cy) > 0.7: continue
        N = 16; c = bm.verts.new((cx, cy, ZP+0.006)); ring = []
        for i in range(N):
            a = 2*math.pi*i/N; r = rnd.uniform(0.06, 0.16)*(1+0.35*noise.noise(Vector((math.cos(a)*2, math.sin(a)*2, cx*9))))
            ring.append(bm.verts.new((cx + r*math.cos(a), cy + r*0.8*math.sin(a), ZP+0.004)))
        tri = [bm.faces.new((c, ring[i], ring[(i+1)%N])) for i in range(N)]
        res = bmesh.ops.solidify(bm, geom=tri, thickness=0.006)
        rafts += tri + [g for g in res["geom"] if isinstance(g, bmesh.types.BMFace)]
    for f in rafts: f.material_index = 10
    RESULTS["TRN_Swamp_Pool"] = finish_hq("TRN_Swamp_Pool", coll, bm, nb, MATS([mpool, malg]), row(1,3), "TRN_SwampIsland.jpg", {"water_level_m": ZP})
    # --- 3 reed marsh: glossy grey-brown mud with lumps, irregular sky-blue puddles, reeds and cattails
    MUD = [(0.030,0.026,0.019),(0.052,0.044,0.031),(0.08,0.068,0.046)]
    mmud = painterly("TRN_Swamp_MarshMud3", MUD, edge=(0.25,0.22,0.17), cavity=(0.008,0.007,0.005), dirt=MUD[0], dirt_h=-9, scale=2.0, strokes=0.6, speckle=0.25, wet=(0.04,0.22), toplight=0.35)
    mpw = water_hq("TRN_Swamp_MarshWater3", (0.16,0.24,0.32),(0.10,0.17,0.25),(0.06,0.11,0.17), strokes=0.35, ripple='rings', depth_range=0.04, sky=(0.5,0.62,0.72), shore_foam=0.2)
    mreed = blade_mat("TRN_Swamp_Reed3", (0.10,0.07,0.03),(0.45,0.36,0.16),(0.32,0.25,0.10),1.0)
    mcat = painterly("TRN_Swamp_Cattail3", [(0.10,0.045,0.018),(0.16,0.07,0.025)], edge=(0.35,0.18,0.07), dirt_h=-9, scale=14)
    PUD = [(-0.35,0.38,0.26,0.14,1),(0.45,0.12,0.22,0.12,2),(0.05,-0.45,0.2,0.11,3),(-0.6,-0.3,0.13,0.08,4),(0.6,0.6,0.11,0.07,5),(-0.05,0.05,0.09,0.06,6)]
    def pud_e(x,y): return min((((x-cx)/rx)**2+((y-cy)/ry)**2)*(1+0.35*nn(x,y,3.5,sd)) for (cx,cy,rx,ry,sd) in PUD)
    def Hr(x,y):
        z = 0.016*nn(x,y,1.8,5) + 0.008*nn(x,y,6,6) + 0.012*max(0.0, nn(x,y,4,8)-0.3)
        w = 1-sstep(0.8,1.3,pud_e(x,y)); z = z*(1-w) - 0.03*w
        return z*edge_fade(x,y) + shoulder(x,y)
    bm,tl,ml,hl = new_bm2(); fs = build_hf(bm, Hr, 72, 72, top_layer=tl, mask_layer=ml); nb = len(fs)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    for f in fs: f.material_index = 0 if sum(v[tl] for v in f.verts)/len(f.verts) > 0.5 else 1
    for f in water_volume_hq(bm, lambda x,y: pud_e(x,y) < 1.15, Hr, -0.012, n=72, skirt=False): f.material_index = 2
    rnd = random.Random(21); rd, ct = [], []
    for _ in range(10):
        cx, cy = rnd.uniform(-0.78,0.78), rnd.uniform(-0.78,0.78)
        for _ in range(6): rd += blade(bm, hl, cx+rnd.uniform(-0.05,0.05), cy+rnd.uniform(-0.05,0.05), Hr(cx,cy), rnd.uniform(0.22,0.5), 0.024, rnd.uniform(0,6.28), rnd.uniform(0.0,0.18))
    for _ in range(9):
        x, y = rnd.uniform(-0.75,0.75), rnd.uniform(-0.75,0.75); h = rnd.uniform(0.38,0.56); tilt = (rnd.uniform(-0.12,0.12), rnd.uniform(-0.12,0.12))
        ct += cyl(bm, x, y, Hr(x,y), 0.006, h, seg=5, tilt=tilt) + cyl(bm, x+math.sin(tilt[1])*(h-0.06), y-math.sin(tilt[0])*(h-0.06), Hr(x,y)+h-0.11, 0.02, 0.10, seg=8)
    for f in rd: f.material_index = 3
    for f in ct: f.material_index = 4
    for f in scatter_pebbles(bm, Hr, 14, 0.015, 0.035, 77, avoid=lambda x,y: pud_e(x,y) < 1.2): f.material_index = 5
    mside2 = side_drip("TRN_Swamp_MarshSide3", [(0.022,0.018,0.012),(0.036,0.029,0.019),(0.05,0.04,0.026)], MUD, 0.0, drip=0.05, edge=(0.2,0.17,0.13), wet=(0.1,0.4))
    RESULTS["TRN_Swamp_ReedMarsh"] = finish_hq("TRN_Swamp_ReedMarsh", coll, bm, nb, [mmud, mside2, mpw, mreed, mcat, mtwig], row(2,3), "TRN_SwampIsland.jpg")
