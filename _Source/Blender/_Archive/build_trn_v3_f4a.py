"""Dino Park Tycoon - TRN v03 water sets with animation. BUILD = falls | falls4 | river | beach
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

# =========================================================== WATERFALLS v04 (BUILD = falls4) - v03 "falls" block above is kept unchanged
# Same footprints (2x2 / 4x3), base-centre pivots, drops (2 m / 3 m) and river in/out as v03.
# Lip: the channel bed rises to a rounded rock ledge (radius RB) and the water surface wraps it with radius RW, then falls.
# Water is ONE object/material per waterfall: feeder + bend + fall share FlowUV (v = metres along flow, fall stretched x0.5 so it reads faster)
# and attributes fallv (0 calm -> 1 impact), depth, mask (fold crease).  Pool, churn and spray are separate children.
if BUILD == "falls4":
    coll = get_coll("TRN_Waterfalls")
    STONE = [(0.15,0.125,0.095),(0.21,0.18,0.14),(0.28,0.245,0.19),(0.36,0.315,0.25)]
    MOSS4 = [(0.05,0.12,0.015),(0.10,0.22,0.03),(0.16,0.33,0.045),(0.24,0.42,0.07)]
    RB, RW = 0.15, 0.22
    def hash01(*k):
        s = 0.0
        for i, a in enumerate(k): s += a*(12.9898 + 31.7*i)
        return (math.sin(s)*43758.5453) % 1.0
    def facet(s, z, seed, cell):
        """broad irregular stone planes: a random tilted plane per voronoi cell (cell id = nearest feature point)"""
        q = Vector((s/cell, z/(cell*1.25), seed*3.1))
        d, pts = noise.voronoi(q, distance_metric='DISTANCE'); p = pts[0]
        h1, h2, h3 = hash01(p.x, p.y, p.z), hash01(p.y, p.z, p.x), hash01(p.z, p.x, p.y)
        return clamp((h1-0.5)*1.4 + (h2-0.5)*(q.x-p.x)*1.1 + (h3-0.5)*(q.y-p.y)*1.1, -1.0, 1.0)
    def stone_side(name, top_z, wet=True):
        m = painterly(name, STONE, edge=(0.52,0.47,0.40), cavity=(0.03,0.025,0.018), dirt=(0.09,0.07,0.05), dirt_h=0.25, scale=0.9, strokes=0.45,
                      crack_lines=0.45, crack_scale=1.2, toplight=0.4, edge_amt=0.5, cav_amt=0.85, bump=0.25)
        nt = m.node_tree; bs = [n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'][0]; src = bs.inputs["Base Color"].links[0].from_socket
        obj = objco(nt); s = sep(nt, obj); dn = noise_n(nt, obj, 3.5, 3, 0.55)
        lim = mathop(nt, mathop(nt, maprange(nt, dn.outputs["Fac"], 0.5, 0.75, 0.0, 0.14), -1.0), top_z - 0.03, 'ADD')
        band = maprange(nt, mathop(nt, s[2], lim, 'SUBTRACT'), -0.005, 0.005)
        gr = ramp(nt, [(0.08,0.18,0.02),(0.15,0.30,0.04)]); nt.links.new(dn.outputs["Fac"], gr.inputs[0])
        col = mix(nt, src, gr.outputs[0], band)
        if wet:
            col = mix(nt, col, (0.36,0.33,0.30), mathop(nt, attr(nt, "mask"), 0.9), 'MULTIPLY')
            nt.links.new(maprange(nt, attr(nt, "mask"), 0.0, 1.0, 0.85, 0.3), bs.inputs["Roughness"])
        nt.links.new(col, bs.inputs["Base Color"]); return m
    def water4_mat(name, speed=0.9):
        m, nt, bs = new_mat(name); t = time_out(nt); uv = uvmap(nt); obj = objco(nt)
        a = attr(nt, "fallv"); d = attr(nt, "depth"); cr = attr(nt, "mask"); au = mathop(nt, sep(nt, uv)[0], 0.0, 'ABSOLUTE')
        body = ramp(nt, [(0.15,0.47,0.50),(0.12,0.45,0.47),(0.065,0.34,0.36),(0.085,0.39,0.40)], [0.0,0.3,0.62,1.0]); nt.links.new(a, body.inputs[0])
        col = mix(nt, body.outputs[0], (0.03,0.20,0.26), mathop(nt, maprange(nt, d, 0.08, 0.3, 0.0, 0.55), maprange(nt, a, 0.3, 0.15)))
        nb = noise4(nt, obj, mathop(nt, t, 0.04), 0.8, 2, 0.5)
        col = mix(nt, col, maprange(nt, nb.outputs["Fac"], 0.3, 0.7, 0.82, 1.18), 1.0, 'MULTIPLY')
        col = mix(nt, col, (0.02,0.13,0.16), mathop(nt, cr, 0.5))
        col = mix(nt, col, (0.42,0.74,0.74), mathop(nt, maprange(nt, au, 0.78, 1.0), maprange(nt, a, 0.2, 0.5, 0.2, 0.7)))
        f1 = vadd(nt, uv, comb(nt, 0.0, mathop(nt, t, -speed), 0.0))
        s1 = noise4(nt, vmul(nt, f1, (3.0, 0.9, 1.0)), mathop(nt, t, 0.1), 1.8, 4, 0.55)
        hl = mathop(nt, maprange(nt, s1.outputs["Fac"], 0.60, 0.66), maprange(nt, s1.outputs["Fac"], 0.73, 0.67), 'MINIMUM')
        hl = mathop(nt, hl, maprange(nt, a, 0.36, 0.2))
        col = mix(nt, col, (0.62,0.86,0.86), mathop(nt, hl, 0.55))
        s2 = noise4(nt, vmul(nt, f1, (15.0, 0.45, 1.0)), mathop(nt, t, 0.25), 1.6, 5, 0.6)
        thr = maprange(nt, a, 0.2, 1.0, 0.72, 0.55)
        st = maprange(nt, mathop(nt, s2.outputs["Fac"], thr, 'SUBTRACT'), 0.0, 0.07)
        st = mathop(nt, st, maprange(nt, a, 0.2, 0.4))
        col = mix(nt, col, (0.93,0.97,0.97), mathop(nt, st, 0.9))
        s3 = noise4(nt, vmul(nt, f1, (38.0, 1.2, 1.0)), mathop(nt, t, 0.4), 1.6, 2, 0.5)
        col = mix(nt, col, (0.80,0.93,0.93), mathop(nt, mathop(nt, maprange(nt, s3.outputs["Fac"], 0.63, 0.70), maprange(nt, a, 0.5, 0.8)), 0.45))
        ch = noise4(nt, obj, mathop(nt, t, 0.6), 5.0, 4, 0.6)
        col = mix(nt, col, (0.95,0.98,0.98), mathop(nt, maprange(nt, a, 0.86, 1.0), maprange(nt, ch.outputs["Fac"], 0.35, 0.55)))
        lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
        col = mix(nt, col, (0.70,0.86,0.88), mathop(nt, lw.outputs["Facing"], 0.12))
        nt.links.new(col, bs.inputs["Base Color"])
        nt.links.new(maprange(nt, a, 0.1, 0.5, 0.16, 0.32), bs.inputs["Roughness"]); bs.inputs["Specular IOR Level"].default_value = 0.45
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.15; bp.inputs["Distance"].default_value = 0.01
        nt.links.new(mathop(nt, st, hl, 'ADD'), bp.inputs["Height"]); nt.links.new(bp.outputs[0], bs.inputs["Normal"])
        return m
    def pool4_mat(name, impacts, front_y, back_y):
        m, nt, bs = new_mat(name); t = time_out(nt); uv = uvmap(nt); obj = objco(nt); d = attr(nt, "depth")
        rd = ramp(nt, [(0.17,0.50,0.50),(0.08,0.37,0.40),(0.035,0.22,0.28)], [0.0,0.45,1.0]); nt.links.new(maprange(nt, d, 0.0, 0.25), rd.inputs[0])
        nb = noise4(nt, obj, mathop(nt, t, 0.03), 0.9, 2, 0.5)
        col = mix(nt, rd.outputs[0], maprange(nt, nb.outputs["Fac"], 0.3, 0.7, 0.85, 1.15), 1.0, 'MULTIPLY')
        calm = maprange(nt, sep(nt, obj)[1], front_y, back_y, 0.25, 1.0)
        f1 = vadd(nt, uv, comb(nt, 0.0, mathop(nt, t, -0.22), 0.0))
        s1 = noise4(nt, vmul(nt, f1, (4.0, 0.8, 1.0)), mathop(nt, t, 0.1), 1.8, 5, 0.6)
        col = mix(nt, col, (0.70,0.90,0.90), mathop(nt, mathop(nt, maprange(nt, s1.outputs["Fac"], 0.62, 0.69), calm), 0.45))
        flat = vmul(nt, obj, (1.0, 1.0, 0.0))
        gate = maprange(nt, noise4(nt, flat, mathop(nt, t, 0.3), 3.5, 2, 0.5).outputs["Fac"], 0.44, 0.58)
        tot = None
        for (cx, cy, s, rs) in impacts:
            loc = vadd(nt, flat, comb(nt, -cx, -cy, 0.0))
            wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = 'RINGS'; wv.rings_direction = 'SPHERICAL'
            wv.inputs["Scale"].default_value = rs; wv.inputs["Distortion"].default_value = 2.5; wv.inputs["Detail"].default_value = 2.0
            nt.links.new(loc, wv.inputs["Vector"]); nt.links.new(mathop(nt, t, -4.0), wv.inputs["Phase Offset"])
            rl = mathop(nt, maprange(nt, wv.outputs["Fac"], 0.84, 0.95), maprange(nt, vlen(nt, loc), s*1.7, s*0.45))
            tot = rl if tot is None else mathop(nt, tot, rl, 'MAXIMUM')
        tot = mathop(nt, tot, gate)
        col = mix(nt, col, (0.90,0.96,0.96), mathop(nt, tot, 0.8))
        lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
        col = mix(nt, col, (0.70,0.86,0.88), mathop(nt, lw.outputs["Facing"], 0.12))
        nt.links.new(col, bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.12; bs.inputs["Specular IOR Level"].default_value = 0.45
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.15; bp.inputs["Distance"].default_value = 0.01
        nt.links.new(tot, bp.inputs["Height"]); nt.links.new(bp.outputs[0], bs.inputs["Normal"])
        return m
    def churn4_mat(name):
        m, nt, bs = new_mat(name); t = time_out(nt); obj = objco(nt); sd = attr(nt, "sd")
        n = noise4(nt, vadd(nt, obj, comb(nt, 0.0, 0.0, mathop(nt, t, -0.2))), mathop(nt, t, 0.8), 9.0, 5, 0.62)
        n2 = noise4(nt, obj, mathop(nt, t, 0.5), 3.2, 3, 0.5)
        r = ramp(nt, [(0.50,0.72,0.73),(0.84,0.93,0.94),(1.0,1.0,1.0)], [0.3,0.5,0.68]); nt.links.new(n.outputs["Fac"], r.inputs[0])
        nt.links.new(r.outputs[0], bs.inputs["Base Color"])
        al = maprange(nt, mathop(nt, sd, mathop(nt, mathop(nt, n2.outputs["Fac"], 0.5, 'SUBTRACT'), 0.9), 'ADD'), 0.18, 0.42)
        nt.links.new(al, bs.inputs["Alpha"])
        bs.inputs["Roughness"].default_value = 0.5
        bs.inputs["Emission Color"].default_value = (0.85,0.93,0.95,1); bs.inputs["Emission Strength"].default_value = 0.12
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.6; bp.inputs["Distance"].default_value = 0.02
        nt.links.new(n.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs[0], bs.inputs["Normal"])
        return m
    def spray4_mat(name, density=3.5):
        m, nt, bs = new_mat(name); out = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]; nt.nodes.remove(bs)
        pv = nt.nodes.new("ShaderNodeVolumePrincipled"); pv.inputs["Color"].default_value = (0.96,0.98,0.99,1)
        t = time_out(nt); tc = nt.nodes.new("ShaderNodeTexCoord"); gen = tc.outputs["Generated"]
        n = noise4(nt, vadd(nt, tc.outputs["Object"], comb(nt, 0.0, 0.0, mathop(nt, t, -0.35))), mathop(nt, t, 0.35), 3.2, 5, 0.6)
        rad = vlen(nt, vmul(nt, vadd(nt, gen, comb(nt, -0.5, -0.5, 0.0)), (1.0, 1.0, 0.0)))
        dens = mathop(nt, maprange(nt, n.outputs["Fac"], 0.40, 0.68), maprange(nt, rad, 0.5, 0.12))
        dens = mathop(nt, mathop(nt, dens, maprange(nt, sep(nt, gen)[2], 0.12, 0.95, 1.0, 0.0)), density)
        nt.links.new(dens, pv.inputs["Density"]); nt.links.new(pv.outputs[0], out.inputs["Volume"])
        return m
    def rocks4(name, specs, mats, pos, parent):
        bm,tl,ml,hl = new_bm2(); groups = []
        for (c, s, sd, kw) in specs:
            groups.append(rock_hq(bm, center=c, size=s, seed=sd, K=kw.get("K",10), boxy=kw.get("boxy",0.42), flat_top=kw.get("flat",0.18),
                                  subdiv=4, dmin=kw.get("dmin",0.7), sink=kw.get("sink",0.12), rot=kw.get("rot",0.0), wear=1))
        nb = len(bm.faces); mf = []
        for i,g in enumerate(groups): mf += moss_shell(bm, g, 900+i, nz_min=0.62, thr=0.15)
        for f in mf: f.material_index = 1
        RESULTS[name] = finish_hq(name, coll, bm, nb, mats, pos, "TRN_Waterfalls.jpg")
        return parent_to(name, parent)

    mg = painterly("TRN_Falls_Grass4", GRASS, edge=(0.45,0.58,0.16), cavity=(0.02,0.05,0.008), dirt=GRASS[0], dirt_h=-9, scale=1.8, strokes=0.6, toplight=0.35, speckle=0.06)
    mask_mix(mg, [(0.24,0.205,0.16),(0.32,0.28,0.22)], soft=0.08)
    mgb = painterly("TRN_Falls_BaseGrass4", GRASS, edge=(0.45,0.58,0.16), cavity=(0.02,0.05,0.008), dirt=GRASS[0], dirt_h=-9, scale=1.8, strokes=0.6, toplight=0.35, speckle=0.06)
    mask_mix(mgb, [(0.16,0.11,0.06),(0.22,0.16,0.09)], soft=0.1)
    mbl = blade_mat("TRN_Falls_Blade4", (0.08,0.18,0.015),(0.40,0.55,0.12),(0.26,0.40,0.06),1.0)
    mrock = painterly("TRN_Falls_Rock4", STONE, edge=(0.55,0.50,0.42), cavity=(0.025,0.02,0.015), moss=MOSS4[:3], moss_amt=0.3, scale=1.6,
                      strokes=0.4, crack_lines=0.45, crack_scale=2.0, toplight=0.45, edge_amt=0.5, bump=0.25)
    mmoss = painterly("TRN_Falls_Moss4", MOSS4, edge=(0.40,0.55,0.14), cavity=(0.01,0.03,0.005), dirt_h=-9, scale=6, strokes=0.35, speckle=0.3, toplight=0.45)
    mchurn = churn4_mat("TRN_Falls_Churn4"); mspray = spray4_mat("TRN_Falls_Spray4")

    def waterfall4(name, SX, SY, HT, yc, cw_lip, pool, pos, big, streams, throw, amp, cell):
        px, py, prx, pry = pool; ZW = ZWR; L = SY - yc; WL = HT + ZWR
        yk = yc + RB; zk = HT - 0.12 - RB; y1 = yk - RW
        def pool_e(x,y): return (((x-px)/prx)**2 + ((y-py)/pry)**2)*(1+0.24*nn(x,y,1.4,7)+0.10*nn(x,y,4.0,8))
        # ---------------- base slab: pool recessed into a grassy bank, outflow channel to the front edge centre
        def Hb_real(x,y,u,v):
            e = pool_e(x,y); basin = 1-sstep(0.85,1.08,e)
            ch = (1-sstep(W*0.72, W*1.0, abs(x))) if y < py else 0.0
            w = max(basin, ch); lip = 0.025*sstep(1.0,1.15,e)*(1-sstep(1.15,1.45,e))*(1-ch)
            z = (0.012*nn(x,y,1.5,3) - 0.02*sstep(1.6,1.05,e))*(1-w) + lip + (BED+0.03*min(e,1.0))*w
            return z + shoulder(u,v,0.1)*(1-ch)
        Hb = lambda u,v: Hb_real(u*SX, v*SY, u, v)
        Hreal = lambda x,y: Hb_real(x, y, x/SX, y/SY)
        Mb = lambda u,v: (lambda x,y: sstep(0.88,1.0,pool_e(x,y))*(1-sstep(1.05,1.25,pool_e(x,y))) + 0.35*sstep(0.55,0.65,nn(x,y,2.5,9)+0.5))(u*SX, v*SY)
        bm,tl,ml,hl = new_bm2()
        fs = build_hf(bm, Hb, int(56*SX), int(56*SY), mask=Mb, top_layer=tl, mask_layer=ml, wall_rings=(0.3,0.6)); nb = len(fs)
        for v in bm.verts: v.co.x *= SX; v.co.y *= SY
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        for f in fs: f.material_index = 0 if sum(v[tl] for v in f.verts)/len(f.verts) > 0.5 else 1
        rnd = random.Random(11+big); tf = []
        for _ in range(int(55*SX*SY)):
            x, y = rnd.uniform(-SX*0.93, SX*0.93), rnd.uniform(-SY*0.93, yc-0.08)
            if pool_e(x,y) < 1.2 or (abs(x) < W*1.25 and y < py): continue
            tf += tuft(bm, hl, Hreal, x, y)
        for f in tf: f.material_index = 2
        RESULTS[name] = finish_hq(name, coll, bm, nb, [mgb, soil_side(name+"_BaseSide", 0.0, wet=False), mbl], pos, "TRN_Waterfalls.jpg",
                                  {"version":"v04", "drop_m":HT, "footprint_m":"%gx%g"%(2*SX,2*SY), "river_in":"back edge centre at z=%g"%HT, "river_out":"front edge centre at z=0"})
        base = bpy.data.objects[name]
        # ---------------- cliff block: channel + raised rounded rock lip, chipped grass rims, faceted stone faces
        def cw_at(y): return cw_lip + (W - cw_lip)*sstep(0.0, 0.8, clamp((y-yc)/L))
        def bed_z(y):
            if y >= yk: return HT+BED + (HT-0.12-(HT+BED))*sstep(yk+0.45, yk, y)
            dy = yk - y; return zk + math.sqrt(max(0.0, RB*RB - dy*dy))
        def chip(x,y,u,v): return sstep(0.56, 0.8, nn(x,y,2.4,17+big)+0.5)*(1-sstep(0.02, 0.13, edge_d(u,v)))
        def Hc_real(x,y,u,v):
            cw = cw_at(y); ch = 1-sstep(cw*0.86, cw*1.0, abs(x))
            top = HT + 0.015*nn(x,y,1.5,11) - 0.11*chip(x,y,u,v)
            z = top*(1-ch) + (bed_z(y) + 0.04*(abs(x)/cw)**2)*ch
            return z + shoulder(u,v,0.06)*(1-ch)
        cmap = lambda u,v: (u*SX, yc + (v+1)*0.5*L)
        Hc = lambda u,v: Hc_real(*cmap(u,v), u, v)
        Mc = lambda u,v: (lambda x,y: clamp(max(1-sstep(cw_at(y), cw_at(y)*1.22, abs(x)), sstep(0.25,0.6,chip(x,y,u,v)), 0.4*sstep(0.55,0.65,nn(x,y,2.5,13)+0.5))))(*cmap(u,v))
        NR = 50 if big else 34
        bm,tl,ml,hl = new_bm2()
        fs = build_hf(bm, Hc, int(48*SX), max(24,int(60*L)), mask=Mc, top_layer=tl, mask_layer=ml, wall_rings=[i/NR for i in range(1,NR)]); nb = len(fs)
        for v in bm.verts:
            u0, v0 = v.co.x, v.co.y; x, y = cmap(u0, v0)
            if v[tl] < 0.5:
                z = v.co.z
                side = 'F' if v0 < -0.995 else ('B' if v0 > 0.995 else ('R' if u0 > 0.995 else ('L' if u0 < -0.995 else None)))
                if side:
                    ztop = Hc_real(x, y, u0, v0)
                    if z < ztop - 0.02:
                        f = facet(x if side in 'FB' else y, z, {'F':1,'B':2,'R':3,'L':4}[side] + 10*big, cell)
                        rim = sstep(ztop-0.03, ztop-0.14, z); bf = sstep(-0.05, 0.3, z)
                        over = 0.035*rim*(1-sstep(ztop-0.30, ztop-0.6, z))
                        if side == 'F' and abs(x) > cw_lip + 0.12: push = amp*(0.35+0.65*f)*rim*bf - over
                        else: push = -amp*0.5*(1+f)*rim*bf - over
                        x += {'R':1,'L':-1}.get(side,0)*push; y += {'F':-1,'B':1}.get(side,0)*push
                    v[ml] = 1.0 if (side == 'F' and abs(x) < cw_lip*1.2) else 0.0
            v.co.x, v.co.y = x, y
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        for f in fs: f.material_index = 0 if sum(v[tl] for v in f.verts)/len(f.verts) > 0.5 else 1
        cn = name + "_Cliff"
        RESULTS[cn] = finish_hq(cn, coll, bm, nb, [mg, stone_side(name+"_CliffStone", HT, wet=True)], pos, "TRN_Waterfalls.jpg")
        parent_to(cn, base)
        # ---------------- water: feeder (with spur hole) + per-stream bend & fall, one material
        bm, uvl = water_bm(); dl, fl, crl = (bm.verts.layers.float[k] for k in ("depth","fallv","mask"))
        hole = [(s["gap"], s["hole"]) for s in streams if "hole" in s]
        def in_hole(x,y): return any(((x-hx)/rx)**2 + ((y-hy)/ry)**2 < 1.0 for _, (hx,hy,rx,ry) in hole)
        NU, NV = 40 if big else 14, 30; grid = []
        for j in range(NV+1):
            y = SY - (SY-yk)*j/NV; cw = cw_at(y)*0.97; row = []
            for i in range(NU+1):
                x = cw*(2*i/NU-1)
                vt = bm.verts.new((x, y, WL + 0.002*noise.noise(Vector((x*5, y*5, 1.0)))))
                vt[dl] = max(0.0, WL - (bed_z(y) + 0.04*(abs(x)/max(cw,0.05))**2)); vt[fl] = 0.25*(1-clamp((y-yk)/0.8))**2; row.append(vt)
            grid.append(row)
        for j in range(NV):
            for i in range(NU):
                q = (grid[j][i], grid[j][i+1], grid[j+1][i+1], grid[j+1][i]); c = sum((p.co for p in q), Vector())/4
                if in_hole(c.x, c.y): continue
                f = bm.faces.new(q)
                for lp in f.loops: lp[uvl].uv = (lp.vert.co.x/max(0.05, cw_at(lp.vert.co.y)), SY - lp.vert.co.y)
        v_arc = SY - yk; v_fall = v_arc + RW*math.pi/2; NA, NS = 7, 36
        zb = ZW - 0.02
        for s in streams:
            x0, x1, NUs = s["x0"], s["x1"], s["nu"]
            folds = s.get("folds", []); k0 = s.get("k", 1.0); spread = s.get("spread", (0.0, 0.0))
            def kf(x): return k0 + sum((k-k0)*math.exp(-((x-c)/sg)**2) for (c,sg,k,b) in folds)
            def ridge(x): return clamp(sum(math.exp(-((x-c)/sg)**2) for (c,sg,k,b) in folds)) if folds else 0.6
            def bulge(x): return sum(b*math.exp(-((x-c)/sg)**2) for (c,sg,k,b) in folds)
            rows = []
            for j in range(NA + NS + 1):
                rr = []
                for i in range(NUs+1):
                    uu = i/NUs; x = x0 + (x1-x0)*uu
                    if j <= NA:
                        ph = (math.pi/2)*j/NA; y = yk - RW*math.sin(ph); z = zk + RW*math.cos(ph)
                        a = 0.25 + 0.15*j/NA; vv = v_arc + RW*ph; dep = 0.07
                    else:
                        tt = (j-NA)/NS; z = zk - (zk - zb)*tt
                        x = x + (spread[0]*(1-uu) + spread[1]*uu)*tt**1.3
                        y = y1 - throw*kf(x0 + (x1-x0)*uu)*tt**1.1 - bulge(x0 + (x1-x0)*uu)*math.sin(math.pi*min(1.0, tt*1.25)) \
                            + 0.012*noise.noise(Vector((x*3, z*1.5, x0*7)))
                        a = 0.4 + 0.6*tt; vv = v_fall + 0.5*(zk - z); dep = 0.12
                    vt = bm.verts.new((x, y, z)); vt[fl] = a; vt[dl] = dep; vt[crl] = (1-ridge(x0 + (x1-x0)*uu))*(1.0 if j > NA else 0.3)
                    rr.append((vt, 2*uu-1, vv))
                rows.append(rr)
            for j in range(NA + NS):
                for i in range(NUs):
                    q = (rows[j][i], rows[j][i+1], rows[j+1][i+1], rows[j+1][i]); f = bm.faces.new([p[0] for p in q])
                    for lp, p in zip(f.loops, q): lp[uvl].uv = (p[1], p[2])
            # side skirts over the lip (water thickness between surface arc and rock arc) so the side view shows no gap
            for xe, ue in ((x0, -1.0), (x1, 1.0)):
                prev = None
                for j in range(NA+1):
                    ph = (math.pi/2)*j/NA
                    a_ = bm.verts.new((xe, yk - RW*math.sin(ph), zk + RW*math.cos(ph))); b_ = bm.verts.new((xe, yk - RB*math.sin(ph)*0.98, zk + RB*math.cos(ph)*0.98))
                    for vt in (a_, b_): vt[fl] = 0.3; vt[dl] = 0.07
                    if prev:
                        f = bm.faces.new((prev[0], a_, b_, prev[1]))
                        for lp in f.loops: lp[uvl].uv = (ue, v_arc + RW*ph)
                    prev = (a_, b_)
        impacts = [s["impact"] for s in streams for _ in [0]] + [l for s in streams for l in s.get("lobes", [])]
        # pool + outflow
        pf = water_volume_hq(bm, lambda u,v: (lambda x,y: pool_e(x,y) < 1.06 or (abs(x) < W*1.05 and y < py))(u*SX, v*SY), Hb, ZW, n=int(60*max(SX,SY)))
        for f in pf:
            for v in f.verts: v.tag = True
        for v in bm.verts:
            if v.tag: v.co.x *= SX; v.co.y *= SY; v.tag = False
        for f in pf:
            f.material_index = 1
            for lp in f.loops: lp[uvl].uv = (lp.vert.co.x/W, -lp.vert.co.y)
        mwater = water4_mat(name+"_Water4", 0.9)
        mpool = pool4_mat(name+"_Pool4", [(ix, iy, s_, 3.0 if big else 4.0) for (ix,iy,s_) in impacts], -SY, yc)
        wn = name + "_Water"
        RESULTS[wn] = finish_hq(wn, coll, bm, 0, [mwater, mpool], pos, "TRN_Waterfalls.jpg",
                                {"unity":"one water shader: scroll FlowUV.v ~0.9 (fall v stretched x0.5); fallv 0..1 = calm->impact; mask = fold crease; pool rings from impact points"}, outline=False)
        parent_to(wn, base)
        # ---------------- churn: low uneven white patches under each stream (on the water), spray volumes above them
        bm, uvl2 = water_bm(); sdl = bm.verts.layers.float["sd"]; rnd = random.Random(40+big)
        for k_, (ix, iy, s_) in enumerate(impacts):
            for rep in range(2 if big else 1):
                cx = ix + (rnd.uniform(-0.06, 0.06) if rep else 0); cy = iy + (rnd.uniform(-0.05, 0.08) if rep else 0)
                rx, ry = s_*(1.0 if not rep else 0.7), s_*0.62*(1.0 if not rep else 0.75); N = 32
                c = bm.verts.new((cx, cy, ZW + 0.035 + 0.02*rnd.random())); c[sdl] = 1.0; rings_ = []
                for rr_ in (0.45, 0.8, 1.0):
                    ring = []
                    for i in range(N):
                        an = 2*math.pi*i/N; k = 1 + 0.28*noise.noise(Vector((math.cos(an)*2, math.sin(an)*2, k_*3.1+rep)))
                        v_ = bm.verts.new((cx + rx*rr_*k*math.cos(an), cy + ry*rr_*k*math.sin(an), ZW + 0.006 + 0.03*(1-rr_*rr_) + 0.008*noise.noise(Vector((an*3, rr_*5, k_)))))
                        v_[sdl] = 1 - rr_; ring.append(v_)
                    rings_.append(ring)
                for i in range(N): bm.faces.new((c, rings_[0][i], rings_[0][(i+1)%N]))
                for ra, rb_ in zip(rings_[:-1], rings_[1:]):
                    for i in range(N): bm.faces.new((ra[i], rb_[i], rb_[(i+1)%N], ra[(i+1)%N]))
        fn = name + "_Churn"; RESULTS[fn] = finish_hq(fn, coll, bm, 0, [mchurn], pos, "TRN_Waterfalls.jpg", {"unity":"alpha-cut foam, attribute sd = centre->rim"}, outline=False); parent_to(fn, base)
        bm = bmesh.new()
        for (ix, iy, s_, h_) in [(s["impact"][0], s["impact"][1], s["impact"][2], s["spray_h"]) for s in streams]:
            blob(bm, (ix, iy, ZW + h_*0.45), (s_*1.25, s_*0.95, h_*0.55), 3)
        mn = name + "_Mist"; RESULTS[mn] = finish_hq(mn, coll, bm, 0, [mspray], pos, "TRN_Waterfalls.jpg", {"export":"preview only - use a particle spray in Unity"}, outline=False)
        parent_to(mn, base).visible_shadow = False
        return base, dict(y1=y1, yk=yk, zk=zk, WL=WL)

    # ----------------------------------------------------- SMALL: one ribbon, one splash
    pos_s, pos_b = (-2.17, -1.25, 0.0), (1.99, 1.15, 0.0)
    cwk = (0.26 + (W-0.26)*sstep(0.0, 0.8, RB/0.95))*0.97
    base_s, ks = waterfall4("TRN_Waterfall_Small", 1.0, 1.0, 2.0, 0.05, 0.26, (0.0,-0.30,0.60,0.40), pos_s, False,
                            [dict(x0=-cwk, x1=cwk, nu=14, k=1.0, spread=(-0.03, 0.03), impact=(0.0, -0.13, 0.26), spray_h=0.42)],
                            throw=0.10, amp=0.035, cell=0.75)
    SPs = [((-0.64,-0.06,-0.08),(0.30,0.26,0.36),501,{}), ((-0.80,-0.44,-0.06),(0.24,0.22,0.25),502,{"rot":0.5}), ((-0.52,-0.72,-0.05),(0.15,0.13,0.13),503,{}),
           ((0.62,-0.10,-0.08),(0.29,0.25,0.34),511,{"rot":-0.4}), ((0.78,-0.50,-0.06),(0.22,0.20,0.23),512,{}), ((0.42,-0.76,-0.05),(0.14,0.12,0.12),513,{"rot":0.8})]
    rocks4("TRN_Waterfall_Small_Rocks", SPs, [mrock, mmoss], pos_s, base_s)
    # ----------------------------------------------------- BIG: spur left of centre, narrow chute left, folded curtain right
    XS = -0.38; cwb = (0.95 + (W-0.95)*sstep(0.0, 0.8, RB/1.4))*0.97; xa, xb = XS + 0.12, cwb
    folds = [(xa+0.20, 0.15, 1.00, 0.05), (xa+0.55, 0.17, 1.30, 0.10), (xa+0.95, 0.15, 0.82, 0.035)]
    y1b = 0.10 + RB - RW; TB = 0.42
    lobes = [(c + 0.02, y1b - TB*k - b*0.3, 0.22 + 0.05*i) for i,(c,sg,k,b) in enumerate(folds)]
    base_b, kb = waterfall4("TRN_Waterfall_Big", 2.0, 1.5, 3.0, 0.10, 0.95, (-0.10,-0.50,1.35,0.66), pos_b, True,
        [dict(x0=-cwb, x1=XS-0.12, nu=10, k=1.05, spread=(-0.07, 0.0), impact=((-cwb+XS-0.12)/2 - 0.03, y1b - TB*1.05, 0.24), spray_h=0.7,
              folds=[((-cwb+XS-0.12)/2, 0.12, 1.12, 0.03)], gap=True, hole=(XS, 0.10+0.10, 0.09, 0.15)),
         dict(x0=xa, x1=xb, nu=40, k=0.92, spread=(0.0, 0.12), folds=folds, impact=(xa+0.55, y1b - TB*1.1, 0.42), lobes=lobes, spray_h=0.95)],
        throw=TB, amp=0.07, cell=0.5)
    SPb = [  # spur: crown above the feeder at the brink + stone face below the lip
           ((XS, 0.10+0.09, 3.0-0.42),(0.26,0.30,0.45),601,{"boxy":0.35,"flat":0.12,"sink":0.04}),
           ((XS, 0.10-0.03, 3.0-1.70),(0.20,0.15,1.02),602,{"boxy":0.4,"flat":0.0,"sink":0.0,"rot":0.1}),
           # left bank: tall interlocking column hugging the cliff
           ((-1.36,0.02,-0.10),(0.42,0.30,0.75),611,{"rot":0.15}), ((-1.30,0.05,0.74),(0.37,0.27,0.68),612,{"rot":-0.2}),
           ((-1.34,0.08,1.56),(0.34,0.24,0.60),613,{"rot":0.3}), ((-1.18,0.09,2.30),(0.22,0.17,0.30),614,{}),
           ((-1.58,-0.58,-0.10),(0.30,0.26,0.28),615,{"rot":0.6}), ((-1.22,-1.06,-0.08),(0.22,0.20,0.18),616,{}), ((-1.72,-1.08,-0.08),(0.19,0.17,0.15),617,{}),
           # right bank: shelves stepping outward and down toward the pool
           ((1.42, 0.02,-0.10),(0.50,0.30,1.95),621,{"flat":0.3,"boxy":0.5}), ((1.48,-0.32,-0.10),(0.50,0.34,1.36),622,{"flat":0.3,"boxy":0.5,"rot":0.1}),
           ((1.44,-0.66,-0.10),(0.50,0.34,0.84),623,{"flat":0.3,"boxy":0.5,"rot":-0.1}), ((1.38,-1.00,-0.10),(0.46,0.32,0.44),624,{"flat":0.3,"boxy":0.5}),
           ((1.15,-0.12,2.38),(0.24,0.20,0.22),625,{}), ((1.18,-1.18,0.25),(0.14,0.12,0.12),626,{})]
    rocks4("TRN_Waterfall_Big_Rocks", SPb, [mrock, mmoss], pos_b, base_b)

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
                x,y = plan_map(-1+2*i/N, -1+2*j/N); v = bm.verts.new((x, y, max(Hs(x,y), ZW) + 0.016)); v[sdl] = SD(x,y); G[(i,j)] = v
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
