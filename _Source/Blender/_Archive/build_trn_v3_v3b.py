"""Dino Park Tycoon - TRN v03 water sets with animation. BUILD = falls | river | beach
Rivers flow +Y (back) -> -Y (front) unless noted. Channel half-width W = 0.36 m, water -0.05, bed -0.30 (relative to tile top).
Waterfalls take a river in at the back edge centre of the upper level and let it out at the front edge centre at ground level.
Water objects are separate children (*_Water / *_Sea / *_Swash) with a 'FlowUV' map for Unity scrolling shaders."""
import os
_bv3 = BUILD; BUILD = "none"
exec(open(os.path.join(TOOLS, "build_trn_v2.py")).read())
exec(open(os.path.join(TOOLS, "trn_anim.py")).read())
BUILD = _bv3
random.seed(303)
RESULTS = {}
W = 0.36; ZWR = -0.05; BED = -0.30
WATER = ((0.30,0.78,0.80),(0.10,0.55,0.64),(0.03,0.30,0.42))
ROCK3 = [(0.17,0.165,0.15),(0.22,0.21,0.19),(0.28,0.27,0.24),(0.34,0.33,0.30)]
def rock_mats(tag):
    mr = painterly("TRN_%s_Rock3" % tag, ROCK3, edge=(0.62,0.6,0.55), cavity=(0.015,0.014,0.012), moss=MOSS, moss_amt=0.6, scale=2.2,
                   strokes=0.35, crack_lines=0.7, crack_scale=2.6, toplight=0.4, wet=(0.25,0.6))
    mm = painterly("TRN_%s_Moss3" % tag, [(0.05,0.12,0.015),(0.10,0.22,0.03),(0.18,0.32,0.05),(0.26,0.40,0.07)], edge=(0.40,0.55,0.14),
                   cavity=(0.01,0.03,0.005), dirt_h=-9, scale=6, strokes=0.35, speckle=0.3, toplight=0.45)
    return mr, mm
def water_bm():
    bm = bmesh.new()
    for l in ("depth","fallv","top","mask","sd"): bm.verts.layers.float.new(l)
    return bm, bm.loops.layers.uv.new("FlowUV")
def rocks_object(name, coll, specs, mats, pos, src, parent=None):
    bm,tl,ml,hl = new_bm2(); groups = []
    for sp in specs:
        c, s, sd = sp[:3]; kw = sp[3] if len(sp) > 3 else {}
        groups.append(rock_hq(bm, center=c, size=s, seed=sd, K=kw.get("K",12), boxy=kw.get("boxy",0.22), flat_top=kw.get("flat",0.1),
                              subdiv=kw.get("sub",4), dmin=0.6, sink=kw.get("sink",0.04), rot=kw.get("rot", random.uniform(-0.7,0.7))))
    nb = len(bm.faces)
    mf = []
    for i,g in enumerate(groups): mf += moss_shell(bm, g, 900+i)
    for f in mf: f.material_index = 1
    RESULTS[name] = finish_hq(name, coll, bm, nb, mats, pos, src)
    return parent_to(name, parent) if parent else bpy.data.objects[name]

# =========================================================== WATERFALLS
if BUILD == "falls":
    coll = get_coll("TRN_Waterfalls")
    mg = painterly("TRN_Falls_Grass3", GRASS, edge=(0.45,0.58,0.16), cavity=(0.02,0.05,0.008), dirt=GRASS[0], dirt_h=-9, scale=1.8, strokes=0.6, toplight=0.35, speckle=0.06)
    mask_mix(mg, [(0.24,0.15,0.06),(0.32,0.21,0.09)], soft=0.1)
    mbl = blade_mat("TRN_Falls_Blade3", (0.08,0.18,0.015),(0.40,0.55,0.12),(0.26,0.40,0.06),1.0)
    mrock, mmoss = rock_mats("Falls")
    msheet = falls_sheet_mat("TRN_Falls_Sheet3", 2.2)
    mfoam = foam_mat("TRN_Falls_Foam3")
    mchan = water_flow_mat("TRN_Falls_ChannelWater3", *WATER, speed=0.9, depth_range=0.2)

    def waterfall(name, SX, SY, HT, yc, cw_lip, throw, pool, pos, big):
        px, py, prx, pry = pool; ZW = ZWR
        L = SY - yc
        def pool_e(x,y): return (((x-px)/prx)**2 + ((y-py)/pry)**2)*(1+0.2*nn(x,y,1.6,7))
        def Hb_real(x,y,u,v):
            e = pool_e(x,y); basin = 1-sstep(0.85,1.12,e)
            ch = (1-sstep(W*0.72, W*1.0, abs(x))) if y < py else 0.0
            w = max(basin, ch)
            z = 0.012*nn(x,y,1.5,3)*(1-w) + (BED+0.03*min(e,1.0))*w
            return z + shoulder(u,v,0.1)*(1-ch)
        Hb = lambda u,v: Hb_real(u*SX, v*SY, u, v)
        Hreal = lambda x,y: Hb_real(x, y, x/SX, y/SY)
        Mb = lambda u,v: (lambda x,y: sstep(0.85,1.0,pool_e(x,y))*(1-sstep(1.05,1.5,pool_e(x,y))) + 0.6*sstep(0.45,0.6,nn(x,y,2.5,9)+0.5))(u*SX, v*SY)
        # ---- base slab with pool + outflow channel
        bm,tl,ml,hl = new_bm2()
        fs = build_hf(bm, Hb, int(56*SX), int(56*SY), mask=Mb, top_layer=tl, mask_layer=ml, wall_rings=(0.3,0.6)); nb = len(fs)
        for v in bm.verts: v.co.x *= SX; v.co.y *= SY
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        for f in fs: f.material_index = 0 if sum(v[tl] for v in f.verts)/len(f.verts) > 0.5 else 1
        rnd = random.Random(11+big); tf = []
        for _ in range(int(60*SX*SY)):
            x, y = rnd.uniform(-SX*0.93, SX*0.93), rnd.uniform(-SY*0.93, yc-0.08)
            if pool_e(x,y) < 1.25 or (abs(x) < W*1.25 and y < py): continue
            tf += tuft(bm, hl, Hreal, x, y)
        for f in tf: f.material_index = 2
        RESULTS[name] = finish_hq(name, coll, bm, nb, [mg, soil_side(name+"_BaseSide", 0.0, wet=False), mbl], pos, "TRN_Waterfalls.jpg",
                                  {"drop_m":HT, "footprint_m":"%gx%g"%(2*SX,2*SY), "river_in":"back edge centre at z=%g"%HT, "river_out":"front edge centre at z=0"})
        base = bpy.data.objects[name]
        # ---- cliff block with channel (river in at back edge), rough face, grass drips, wet streak behind the fall
        def cw_at(y): return cw_lip + (W - cw_lip)*sstep(0.0, 0.8, clamp((y-yc)/L))
        def Hc_real(x,y,u,v):
            cw = cw_at(y); ch = 1-sstep(cw*0.86, cw*1.0, abs(x))
            z = (HT + 0.015*nn(x,y,1.5,11))*(1-ch) + (HT + BED + 0.04*(abs(x)/cw)**2)*ch
            z -= 0.05*sstep(-0.86,-1.0,v)*ch
            return z + shoulder(u,v,0.07)*(1-ch)
        cmap = lambda u,v: (u*SX, yc + (v+1)*0.5*L)
        Hc = lambda u,v: Hc_real(*cmap(u,v), u, v)
        Mc = lambda u,v: (lambda x,y: (1-sstep(cw_at(y)*1.0, cw_at(y)*1.35, abs(x))) + 0.5*sstep(0.5,0.62,nn(x,y,2.5,13)+0.5))(*cmap(u,v))
        bm,tl,ml,hl = new_bm2()
        fs = build_hf(bm, Hc, int(48*SX), max(16,int(30*L)), mask=Mc, top_layer=tl, mask_layer=ml, wall_rings=[i/24 for i in range(1,24)]); nb = len(fs)
        amp = 0.05 if big else 0.028
        for v in bm.verts:
            u0, v0 = v.co.x, v.co.y; x, y = cmap(u0, v0)
            if v[tl] < 0.5:
                nx = 1 if u0 > 0.995 else (-1 if u0 < -0.995 else 0); ny = -1 if v0 < -0.995 else 0
                if (nx or ny) and v.co.z < HT-0.04:
                    z = v.co.z
                    push = amp*(0.6*nn(0, z*2.6, 1.0, 21) + 0.4*nn(x*2.5, z*5, 1.0, 22)) - 0.018*sstep(0.6, 0.95, (z/0.35) % 1.0)
                    x += nx*push; y += ny*push
                v[ml] = 1.0 if (v0 < -0.995 and abs(x) < cw_lip*1.25) else 0.0
            v.co.x, v.co.y = x, y
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        for f in fs: f.material_index = 0 if sum(v[tl] for v in f.verts)/len(f.verts) > 0.5 else 1
        cn = name + "_Cliff"
        RESULTS[cn] = finish_hq(cn, coll, bm, nb, [mg, soil_side(name+"_CliffSide", HT, wet=True)], pos, "TRN_Waterfalls.jpg")
        parent_to(cn, base)
        # ---- water: pool + outflow, channel on top, three-layer falling sheet
        bm, uvl = water_bm(); dl = bm.verts.layers.float["depth"]; fl = bm.verts.layers.float["fallv"]
        region = lambda u,v: (lambda x,y: pool_e(x,y) < 1.1 or (abs(x) < W*1.05 and y < py))(u*SX, v*SY)
        pf = water_volume_hq(bm, region, Hb, ZW, n=int(60*max(SX,SY)))
        for v in bm.verts: v.co.x *= SX; v.co.y *= SY
        for f in pf:
            f.material_index = 0
            for lp in f.loops: lp[uvl].uv = (lp.vert.co.x/W, -lp.vert.co.y)
        WL = HT + ZWR; NU, NV = 10, 24; grid = []
        for j in range(NV+1):
            y = SY - L*j/NV; cw = cw_at(y)*0.97; row = []
            for i in range(NU+1):
                x = cw*(2*i/NU-1)
                vt = bm.verts.new((x, y, WL + 0.003*noise.noise(Vector((x*5, y*5, 1.0)))))
                vt[dl] = max(0.0, WL - Hc_real(x, y, x/SX, (y-yc)/L*2-1)); row.append(vt)
            grid.append(row)
        cf = [bm.faces.new((grid[j][i], grid[j+1][i], grid[j+1][i+1], grid[j][i+1])) for j in range(NV) for i in range(NU)]
        bot = []
        for v in grid[0]:
            b = bm.verts.new((v.co.x, v.co.y, HT + BED + 0.02)); b[dl] = 0.25; bot.append(b)
        cf += [bm.faces.new((grid[0][i], bot[i], bot[i+1], grid[0][i+1])) for i in range(NU)]
        for f in cf:
            f.material_index = 2
            for lp in f.loops: lp[uvl].uv = (lp.vert.co.x/max(0.05, cw_at(lp.vert.co.y)), SY - lp.vert.co.y)
        NS = 30; tmax = math.sqrt(2*(WL-ZW)/9.81)
        for layer,(dy, wm, uoff) in enumerate(((0.0,1.0,0.0),(-0.035,0.86,0.37),(0.025,0.95,0.71))):
            rows = []
            for j in range(NS+1):
                tt = j/NS; z = WL - (WL-ZW)*tt; tau = math.sqrt(2*max(0.0, WL-z)/9.81)
                y = yc + 0.02 - throw*(tau/tmax) + dy*min(1.0, tt*4)
                w = cw_lip*0.96*wm*(1+0.10*tt); rr = []
                for i in range(NU+1):
                    uu = 2*i/NU-1
                    x = w*uu + 0.012*noise.noise(Vector((uu*3, tt*6, layer)))
                    vt = bm.verts.new((x, y + 0.018*noise.noise(Vector((x*3, z*1.5, layer+5))), z)); vt[fl] = tt; vt[dl] = 0.1; rr.append(vt)
                rows.append(rr)
            for j in range(NS):
                for i in range(NU):
                    f = bm.faces.new((rows[j][i], rows[j][i+1], rows[j+1][i+1], rows[j+1][i])); f.material_index = 1
                    for lp in f.loops: lp[uvl].uv = (lp.vert.co.x/cw_lip + uoff, L + (WL - lp.vert.co.z))
        mpool = water_flow_mat(name+"_PoolWater", *WATER, speed=0.25, depth_range=0.22, rings=(0.0, yc-throw, 2.2 if big else 3.5))
        wn = name + "_Water"
        RESULTS[wn] = finish_hq(wn, coll, bm, 0, [mpool, msheet, mchan], pos, "TRN_Waterfalls.jpg",
                                {"unity":"scroll FlowUV.v: channel 0.9 m/s, fall 2.2 m/s, pool 0.25 m/s + ring ripples"}, outline=False)
        parent_to(wn, base)
        # ---- foam at the impact + drifting foam, mist volume (preview; Unity particle system in game)
        bm = bmesh.new(); rnd = random.Random(40+big); yi = yc - throw; wf = cw_lip*1.05
        for _ in range(int(60*(1+big))):
            x = rnd.uniform(-wf, wf)*rnd.uniform(0.6,1.0); y = yi + rnd.gauss(0, 0.07)*(1+0.5*big); s = rnd.uniform(0.035, 0.09)*(1+0.4*big)
            blob(bm, (x, y, ZW + s*0.12), (s*1.3, s, s*0.32), 2)
        for _ in range(int(18*(1+big))):
            x = rnd.uniform(-wf*0.9, wf*0.9); y = yi + rnd.uniform(-0.05, 0.05); s = rnd.uniform(0.04, 0.08)*(1+0.4*big)
            blob(bm, (x, y, ZW + s*0.5), (s, s*0.9, s*0.7), 2)
        for _ in range(int(16*(1+big))):
            a = rnd.uniform(0, 6.28); r = rnd.uniform(0.2, 0.5)*(1+0.8*big); x = r*math.cos(a)*1.4; y = yi + r*math.sin(a)*0.7 - 0.1
            if pool_e(x,y) > 0.9: continue
            s = rnd.uniform(0.025, 0.05); blob(bm, (x, y, ZW + 0.004), (s*1.6, s, s*0.25), 1)
        fn = name + "_Foam"; RESULTS[fn] = finish_hq(fn, coll, bm, 0, [mfoam], pos, "TRN_Waterfalls.jpg", outline=False); parent_to(fn, base)
        bm = bmesh.new(); blob(bm, (0.0, yi, 0.3*(1+0.3*big)), (wf*1.35, 0.35*(1+0.6*big), 0.5*(1+0.5*big)), 3)
        mn = name + "_Mist"; RESULTS[mn] = finish_hq(mn, coll, bm, 0, [mist_mat(name+"_MistVol", 7.0)], pos, "TRN_Waterfalls.jpg", {"export":"preview only - use a particle mist in Unity"}, outline=False)
        mo = parent_to(mn, base); mo.visible_shadow = False
        # ---- rocks (stacked, mossy, 3D moss caps)
        if not big:
            SP = [((-0.80,0.02,0.0),(0.34,0.31,0.38),501),((-0.74,-0.30,0.0),(0.31,0.29,0.29),502),((-0.84,-0.58,0.0),(0.23,0.22,0.19),503),
                  ((-0.78,0.0,0.34),(0.26,0.23,0.24),504),((-0.50,0.10,0.0),(0.23,0.17,0.55),505),((-0.52,0.10,0.5),(0.20,0.16,0.36),506),
                  ((0.78,-0.04,0.0),(0.33,0.30,0.41),511),((0.80,-0.40,0.0),(0.27,0.25,0.26),512),((0.50,0.10,0.0),(0.25,0.17,0.62),513),
                  ((0.76,-0.04,0.36),(0.23,0.21,0.24),514),((0.52,0.10,0.56),(0.18,0.16,0.31),515),
                  ((-0.56,-0.84,0.0),(0.21,0.18,0.14),521),((0.58,-0.82,0.0),(0.23,0.20,0.17),522),
                  ((-0.40,-0.62,-0.06),(0.13,0.12,0.10),523),((0.42,-0.60,-0.06),(0.12,0.10,0.08),524)]
        else:
            SP = []; sd = 600
            for s in (-1, 1):
                x0 = s*(cw_lip+0.36); z = 0.0
                for i,(a,b,c) in enumerate(((0.50,0.42,0.55),(0.46,0.40,0.62),(0.44,0.38,0.58),(0.40,0.35,0.55),(0.34,0.30,0.40))):
                    SP.append(((x0 + s*0.04*((i%2)*2-1), yc-0.12+0.04*(i%2), z),(a,b,c),sd,{"boxy":0.3,"flat":0.15})); sd += 1; z += c*0.95
                x1 = s*(cw_lip+0.98); z = 0.0
                for i,(a,b,c) in enumerate(((0.55,0.48,0.55),(0.48,0.42,0.55),(0.40,0.36,0.45))):
                    SP.append(((x1, yc-0.25-0.05*i, z),(a,b,c),sd,{"boxy":0.3,"flat":0.15})); sd += 1; z += c*0.9
                SP += [((s*1.65,-0.50,0.0),(0.30,0.28,0.30),sd),((s*1.45,-0.95,0.0),(0.26,0.24,0.22),sd+1),((s*0.78,-1.22,0.0),(0.22,0.20,0.16),sd+2),
                       ((s*(cw_lip+0.2), yc+0.25, HT),(0.20,0.18,0.16),sd+3)]; sd += 4
            SP.append(((0.08, yc-0.06, HT-0.80),(0.16,0.14,0.42),sd,{"boxy":0.3}))
        rocks_object(name+"_Rocks", coll, SP, [mrock, mmoss], pos, "TRN_Waterfalls.jpg", base)

    waterfall("TRN_Waterfall_Small", 1.0, 1.0, 2.0, 0.05, 0.30, 0.28, (0.0,-0.32,0.62,0.42), (-2.6,2.6,0), False)
    waterfall("TRN_Waterfall_Big",   2.0, 1.5, 3.0, 0.10, 0.95, 0.45, (0.0,-0.55,1.45,0.72), (2.6,-2.6,0), True)

# =========================================================== RIVER
if BUILD == "river":
    coll = get_coll("TRN_River")
    BANK = [(0.36,0.22,0.09),(0.46,0.31,0.14),(0.56,0.41,0.21)]
    mbank = painterly("TRN_River_Bank3", BANK, edge=(0.78,0.62,0.4), cavity=(0.07,0.04,0.015), dirt=BANK[0], dirt_h=-9, scale=2.0, strokes=0.6, speckle=0.15, toplight=0.35)
    mask_mix(mbank, [(0.20,0.26,0.07),(0.30,0.36,0.10)], soft=0.12)
    msand = painterly("TRN_River_Sand3", [(0.62,0.50,0.30),(0.72,0.60,0.38),(0.80,0.70,0.48)], edge=(0.92,0.86,0.70), cavity=(0.25,0.18,0.09), dirt_h=-9, scale=1.6, strokes=0.55, toplight=0.3)
    mside = soil_side("TRN_River_Side3", 0.0, wet=False)
    mbl = blade_mat("TRN_River_Reed3", (0.06,0.12,0.02),(0.32,0.46,0.10),(0.20,0.30,0.06),1.0)
    mcat = painterly("TRN_River_Cattail3", [(0.10,0.045,0.018),(0.16,0.07,0.025)], edge=(0.35,0.18,0.07), dirt_h=-9, scale=14)
    mpeb = painterly("TRN_River_Pebble3", [(0.30,0.25,0.19),(0.42,0.36,0.28),(0.52,0.46,0.37)], edge=(0.8,0.72,0.6), cavity=(0.05,0.04,0.03), dirt_h=-9, scale=8, strokes=0.2, toplight=0.4)
    mrock, mmoss = rock_mats("River")
    mflow = water_flow_mat("TRN_River_Water3", *WATER, speed=0.45, depth_range=0.25)
    msheet = falls_sheet_mat("TRN_River_SpringFall3", 1.6)
    mfoam = foam_mat("TRN_River_Foam3")
    def bez(p0,p1,p2,n=28): return [((1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t*t*p2[0], (1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t*t*p2[1]) for t in [i/n for i in range(n+1)]]
    def nearest(x, y, paths):
        best = (9.0, 0.0, 1, 0)
        for pi,p in enumerate(paths):
            acc = 0.0
            for i in range(len(p)-1):
                ax,ay = p[i]; bx,by = p[i+1]; vx,vy = bx-ax, by-ay; L2 = vx*vx+vy*vy; Lg = math.sqrt(L2)
                t = clamp(((x-ax)*vx+(y-ay)*vy)/L2); d = math.hypot(x-ax-vx*t, y-ay-vy*t)
                if d < best[0]: best = (d, acc+t*Lg, 1 if vx*(y-ay)-vy*(x-ax) > 0 else -1, pi)
                acc += Lg
        return best
    def chan(d):
        if d < W*0.78: z = BED + 0.05*(d/(W*0.78))**2
        else: z = (BED+0.05)*(1-sstep(W*0.78, W*1.0, d))
        return z + 0.012*sstep(W*0.95, W*1.03, d)*(1-sstep(W*1.05, W*1.3, d))
    SPR = (-0.50, 0.50, 0.34, 0.30)
    def spr_e(x,y): return (((x-SPR[0])/SPR[2])**2 + ((y-SPR[1])/SPR[3])**2)*(1+0.15*nn(x,y,2,5))
    TILES = [("TRN_River_Straight", [bez((0,1.1),(0.15,0.0),(0,-1.1))], None),
             ("TRN_River_Bend",     [bez((0,1.1),(0.05,0.0),(1.1,0.0))], None),
             ("TRN_River_Junction", [bez((-1.1,0),(0,0.1),(1.1,0)), bez((0,1.1),(0.05,0.5),(0,0.0))], None),
             ("TRN_River_Spring",   [bez((-0.40,0.40),(0.10,0.0),(0,-1.1))], "spring"),
             ("TRN_River_Mouth",    [bez((-1.1,0.15),(-0.3,0.05),(0.55,0.0))], "mouth")]
    for k,(name,paths,kind) in enumerate(TILES):
        def H(x,y, paths=paths, kind=kind):
            d = nearest(x,y,paths)[0]
            z = chan(d) + 0.010*nn(x,y,1.6,k)*sstep(W, W*1.4, d)
            if kind == "spring":
                e = spr_e(x,y); z = min(z, BED*(1-sstep(0.75,1.1,e)))
            if kind == "mouth":
                z = min(z, 0.03 - 0.33*sstep(0.15, 0.9, x + 0.22*math.cos(y*2.2)))
                return z + shoulder(x,y)*(1-sstep(-0.1, 0.6, x))*sstep(W*1.0, W*1.15, d)
            return z + shoulder(x,y)*sstep(W*1.0, W*1.15, d)
        M = lambda x,y,paths=paths: sstep(0.42,0.6,nn(x,y,2.0,7)+0.5)*sstep(W*1.3, W*2.0, nearest(x,y,paths)[0])
        bm,tl,ml,hl = new_bm2()
        fs = build_hf(bm, H, 84, 84, mask=M, top_layer=tl, mask_layer=ml, wall_rings=(0.15,0.35,0.6)); nb = len(fs)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        for f in fs: f.material_index = 0 if sum(v[tl] for v in f.verts)/len(f.verts) > 0.5 else 1
        rnd = random.Random(70+k); deco_b, deco_c, deco_p = [], [], []
        def on_bank(x,y,lo=1.25): return nearest(x,y,paths)[0] > W*lo and (kind != "mouth" or x < 0.0) and (kind != "spring" or spr_e(x,y) > 1.4)
        for _ in range(3):
            for _t in range(80):
                x,y = rnd.uniform(-0.85,0.85), rnd.uniform(-0.85,0.85)
                if on_bank(x,y) and nearest(x,y,paths)[0] < W*1.8: break
            for _ in range(6): deco_b += blade(bm,hl,x+rnd.uniform(-0.05,0.05),y+rnd.uniform(-0.05,0.05),H(x,y),rnd.uniform(0.14,0.3),0.02,rnd.uniform(0,6.28),rnd.uniform(0.05,0.3))
            for _ in range(2):
                bx,by = x+rnd.uniform(-0.04,0.04), y+rnd.uniform(-0.04,0.04); hh = rnd.uniform(0.28,0.4)
                deco_c += cyl(bm,bx,by,H(bx,by),0.005,hh,seg=5) + cyl(bm,bx,by,H(bx,by)+hh-0.08,0.017,0.075,seg=8)
        for _ in range(26):
            x,y = rnd.uniform(-0.88,0.88), rnd.uniform(-0.88,0.88)
            if on_bank(x,y,1.2): deco_b += tuft(bm,hl,H,x,y)
        for _ in range(12):
            x,y = rnd.uniform(-0.85,0.85), rnd.uniform(-0.85,0.85)
            if not on_bank(x,y,1.15): continue
            r = rnd.uniform(0.022,0.05)
            res = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r, matrix=Matrix.Translation((x,y,H(x,y)+r*0.15)) @ Matrix.Rotation(rnd.uniform(0,6),4,'Z') @ Matrix.Diagonal((1,0.8,0.55,1)))
            deco_p += list({f for v in res["verts"] for f in v.link_faces})
        for f in deco_b: f.material_index = 2
        for f in deco_c: f.material_index = 3
        for f in deco_p: f.material_index = 4
        mats = [msand if kind == "mouth" else mbank, mside, mbl, mcat, mpeb]
        RESULTS[name] = finish_hq(name, coll, bm, nb, mats, row(k,5,2.5), "TRN_River.jpg", {"water_level_m":ZWR, "bed_m":BED, "channel_half_width_m":W})
        base = bpy.data.objects[name]
        # water child with flow UVs
        bm, uvl = water_bm(); dl = bm.verts.layers.float["depth"]; fl = bm.verts.layers.float["fallv"]
        if kind == "mouth": R = lambda x,y: nearest(x,y,paths)[0] < W*1.05 or x > 0.1
        elif kind == "spring": R = lambda x,y: nearest(x,y,paths)[0] < W*1.05 or spr_e(x,y) < 1.1
        else: R = lambda x,y: nearest(x,y,paths)[0] < W*1.05
        wf = water_volume_hq(bm, R, H, ZWR, n=72)
        for f in wf:
            for lp in f.loops:
                d, s, sg, pi = nearest(lp.vert.co.x, lp.vert.co.y, paths)
                lp[uvl].uv = (sg*d/W, s if kind != "mouth" else s + max(0.0, lp.vert.co.x - 0.55))
        mats_w = [mflow]
        if kind == "spring":
            mats_w = [water_flow_mat("TRN_River_SpringPool3", *WATER, speed=0.3, depth_range=0.25, rings=(SPR[0]+0.02, SPR[1]+0.05, 5.0)), msheet]
            sv = []; NUs = 4
            for j in range(13):
                tt = j/12; z = 0.36*(1-tt)**1.5 + ZWR*tt; yy = 0.66 - 0.18*tt
                for i in range(NUs+1):
                    v = bm.verts.new((-0.60 + 0.18*i/NUs + 0.01*noise.noise(Vector((i,j,3.0))), yy, z)); v[fl] = tt; v[dl] = 0.1; sv.append(v)
            for j in range(12):
                for i in range(NUs):
                    f = bm.faces.new((sv[j*(NUs+1)+i], sv[j*(NUs+1)+i+1], sv[(j+1)*(NUs+1)+i+1], sv[(j+1)*(NUs+1)+i])); f.material_index = 1
                    for lp in f.loops: lp[uvl].uv = ((lp.vert.co.x+0.51)/0.09, 0.4 - lp.vert.co.z)
        wn = name + "_Water"
        RESULTS[wn] = finish_hq(wn, coll, bm, 0, mats_w, row(k,5,2.5), "TRN_River.jpg", {"unity":"scroll FlowUV.v at 0.45 m/s"}, outline=False)
        parent_to(wn, base)
        if kind == "spring":
            rocks_object(name+"_Rocks", coll, [((-0.78,0.74,0.0),(0.26,0.24,0.30),801),((-0.48,0.86,0.0),(0.22,0.2,0.26),802),((-0.86,0.40,0.0),(0.2,0.18,0.22),803),
                                                ((-0.62,0.70,0.30),(0.17,0.15,0.16),804),((-0.30,0.80,0.0),(0.15,0.13,0.14),805)], [mrock, mmoss], row(k,5,2.5), "TRN_River.jpg", base)
            bm = bmesh.new(); rnd2 = random.Random(9)
            for _ in range(10):
                s = rnd2.uniform(0.03,0.06); blob(bm, (-0.52+rnd2.uniform(-0.08,0.08), 0.47+rnd2.uniform(-0.05,0.05), ZWR+s*0.2), (s,s*0.85,s*0.5), 2)
            fn = name+"_Foam"; RESULTS[fn] = finish_hq(fn, coll, bm, 0, [mfoam], row(k,5,2.5), "TRN_River.jpg", outline=False); parent_to(fn, base)

# =========================================================== BEACH
if BUILD == "beach":
    coll = get_coll("TRN_BeachShore")
    DRY = [(0.62,0.50,0.30),(0.72,0.60,0.38),(0.80,0.70,0.48)]
    msand = painterly("TRN_Beach_Sand3", DRY, edge=(0.92,0.86,0.70), cavity=(0.25,0.18,0.09), dirt=DRY[0], dirt_h=-9, scale=1.6, strokes=0.55, speckle=0.12, toplight=0.3)
    mask_mix(msand, [(0.36,0.26,0.13),(0.45,0.34,0.18)], soft=0.1)
    mside = painterly("TRN_Beach_Side3", [(0.26,0.18,0.09),(0.36,0.26,0.14),(0.46,0.35,0.20)], edge=(0.62,0.5,0.32), cavity=(0.06,0.04,0.02), dirt=(0.14,0.1,0.05), dirt_h=-0.25, strokes=0.5,
                      bands=[(0.30,0.21,0.11),(0.42,0.31,0.17),(0.24,0.17,0.09)], band_scale=6)
    msea = sea_mat("TRN_Beach_Sea3", (0.30,0.80,0.76),(0.06,0.52,0.64),(0.02,0.24,0.40))
    mswash = swash_mat("TRN_Beach_Swash3")
    mshell = painterly("TRN_Beach_Shell3", [(0.55,0.32,0.26),(0.75,0.55,0.45)], edge=(0.95,0.85,0.8), dirt_h=-9, scale=20)
    ZW = -0.06
    def shore_tile(name, i, shore):
        Hs = lambda x,y: (0.04 - 0.30*sstep(-0.15,0.40, x - shore(y))) + 0.008*nn(x,y,2,6) + 0.005*math.sin((x*0.3+y)*26)*(1-sstep(-0.3,0.0,x-shore(y))) + shoulder(x,y)*(1 if x-shore(y) < -0.05 else 0.25)
        SD = lambda x,y: shore(y) + 0.063 - x
        Mw = lambda x,y: (1-sstep(0.0, 0.45, SD(x,y)))
        def shells(bm,hl):
            fs = []; rnd = random.Random(i)
            for _ in range(3):
                y = rnd.uniform(-0.65,0.65); x = shore(y) - rnd.uniform(0.5,0.85)
                res = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.032, matrix=Matrix.Translation((x,y,Hs(x,y)+0.006)) @ Matrix.Rotation(rnd.uniform(0,6),4,'Z') @ Matrix.Diagonal((1,0.8,0.32,1)))
                fs += list({f for v in res["verts"] for f in v.link_faces})
            return fs
        RESULTS[name] = tile_hq(name, coll, Hs, [msand, mside, mshell], row(i,4), "TRN_BeachShore.jpg", n=64, mask=Mw, details=[(2,shells)], extra={"sea_level_m":ZW, "sea_side":"+X"})
        base = bpy.data.objects[name]
        bm, uvl = water_bm()
        sf = water_volume_hq(bm, lambda x,y: x - shore(y) > -0.3, Hs, ZW, n=64)
        for f in sf:
            for lp in f.loops: lp[uvl].uv = (lp.vert.co.y, lp.vert.co.x)
        sn = name + "_Sea"; RESULTS[sn] = finish_hq(sn, coll, bm, 0, [msea], row(i,4), "TRN_BeachShore.jpg", {"unity":"waves: crest bands by depth + time"}, outline=False); parent_to(sn, base)
        # swash film (waves running up the sand and back)
        bm, uvl = water_bm(); sdl = bm.verts.layers.float["sd"]; N = 72; G = {}
        def V(i,j):
            if (i,j) not in G:
                x,y = plan_map(-1+2*i/N, -1+2*j/N); v = bm.verts.new((x, y, max(Hs(x,y), ZW) + 0.004)); v[sdl] = SD(x,y); G[(i,j)] = v
            return G[(i,j)]
        ff = []
        for i in range(N):
            for j in range(N):
                cs = [(-1+2*a/N, -1+2*b/N) for a,b in ((i,j),(i+1,j),(i+1,j+1),(i,j+1))]
                if all(-0.06 < SD(*plan_map(*c)) < 0.6 for c in cs): ff.append(bm.faces.new((V(i,j),V(i+1,j),V(i+1,j+1),V(i,j+1))))
        wn = name + "_Swash"; RESULTS[wn] = finish_hq(wn, coll, bm, 0, [mswash], row(i,4), "TRN_BeachShore.jpg", {"unity":"run-up mask: attribute sd vs time"}, outline=False)
        parent_to(wn, base).visible_shadow = False
    shore_tile("TRN_Beach_Straight", 0, lambda y: 0.05*math.sin(y*2.0))
    shore_tile("TRN_Beach_CurveA", 1, lambda y: 0.30*math.sin(y*1.6))
    shore_tile("TRN_Beach_CurveB", 2, lambda y: -0.25*math.sin(y*1.6+0.6)+0.1)
    # fence ring tile (unchanged design from v02)
    GR2 = [(0.20,0.26,0.10),(0.30,0.36,0.16)]
    mring = painterly("TRN_Beach_RingSand3", DRY, edge=(0.92,0.86,0.70), cavity=(0.25,0.18,0.09), dirt=DRY[0], dirt_h=-9, scale=1.6, strokes=0.55, toplight=0.3)
    mask_mix(mring, GR2, soft=0.12)
    mpost = wood_mat("TRN_Beach_Post3", ((0.05,0.055,0.045),(0.08,0.085,0.07),(0.12,0.12,0.10)))
    mbl = blade_mat("TRN_Beach_Grass3", (0.10,0.16,0.04),(0.42,0.48,0.22),(0.28,0.34,0.12),1.0)
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
            fs += tuft(bm,hl,Hc,s[0],s[1])
        return fs
    RESULTS["TRN_Beach_FenceRing"] = tile_hq("TRN_Beach_FenceRing", coll, Hc, [mring, mside, mpost, mbl], row(3,4), "TRN_BeachShore.jpg", n=56, mask=Mc, details=[(2,fence),(3,tufts)])
