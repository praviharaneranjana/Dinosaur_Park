"""Dino Park Tycoon - ISLAND builder v01 (runs inside Blender). exec with STAGE set: "ground" | "water" | "pieces" | "plants" | "all".
Reads 02_Environment/Island/island_map_v01.json (made by isl_layout.py). 1 grid cell = 2 m; Blender X=(gx-48)*2, Y=(gy-36)*2, +Y north."""
import bpy, bmesh, json, math, os, random
import numpy as np
from mathutils import Vector, Matrix
ROOT = r"D:\Unity Projects\Dinosaur_Park\Dinosaur_Park\_Source\Blender"
TOOLS = ROOT + r"\00_Shared\Tools"
J = json.load(open(ROOT + r"\02_Environment\Island\island_map_v01.json"))
W, H = J["grid"]; CELL = J["cell_m"]; SEA = J["sea_level_m"]; PLAT = J["plateau_m"]
ZID = J["zones"]; ZN = {v: k for k, v in ZID.items()}
zone = np.array(J["zone"]); hm = np.array(J["height_m"], float); dw = np.array(J["dist_water"], float); dl = np.array(J["dist_land"], float)
OX, OY = W//2, H//2
RES = 1.0
XS = np.arange(-W*CELL/2, W*CELL/2 + 1e-6, RES); YS = np.arange(-H*CELL/2, H*CELL/2 + 1e-6, RES); NX, NY = len(XS), len(YS)
GX = (XS/CELL + OX)[None, :].repeat(NY, 0); GY = (YS/CELL + OY)[:, None].repeat(NX, 1)
XM = XS[None, :].repeat(NY, 0); YM = YS[:, None].repeat(NX, 1)
def g2m(gx, gy): return ((gx-OX)*CELL, (gy-OY)*CELL)
def sstep(a, b, x): t = np.clip((x-a)/(b-a), 0, 1); return t*t*(3-2*t)
def samp(a, gx, gy):
    u = np.clip(gx-0.5, 0, W-1.001); v = np.clip(gy-0.5, 0, H-1.001); i0 = u.astype(int); j0 = v.astype(int); fu = u-i0; fv = v-j0
    return a[j0, i0]*(1-fu)*(1-fv) + a[j0, i0+1]*fu*(1-fv) + a[j0+1, i0]*(1-fu)*fv + a[j0+1, i0+1]*fu*fv
def blur(a, n=1):
    for _ in range(n):
        p = np.pad(a, 1, mode="edge"); a = (p[:-2,1:-1] + 2*p[1:-1,1:-1] + p[2:,1:-1])/4; p = np.pad(a, 1, mode="edge"); a = (p[1:-1,:-2] + 2*p[1:-1,1:-1] + p[1:-1,2:])/4
    return a
def zmask(*names): return np.isin(zone, [ZID[n] for n in names]).astype(float)
def seg_dist(px, py, pts):
    d = np.full(px.shape, 1e9); t_best = np.zeros(px.shape)
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        dx, dy = x1-x0, y1-y0; L2 = dx*dx+dy*dy+1e-9; t = np.clip(((px-x0)*dx + (py-y0)*dy)/L2, 0, 1)
        dd = np.hypot(px-(x0+t*dx), py-(y0+t*dy)); m = dd < d; d = np.where(m, dd, d)
    return d
def smooth_poly(pts, n=8):
    pts = [Vector((p[0], p[1], 0)) for p in pts]; out = []
    for i in range(len(pts)-1):
        p0 = pts[max(i-1, 0)]; p1 = pts[i]; p2 = pts[i+1]; p3 = pts[min(i+2, len(pts)-1)]
        for k in range(n):
            t = k/n; out.append(0.5*((2*p1) + (-p0+p2)*t + (2*p0-5*p1+4*p2-p3)*t*t + (-p0+3*p1-3*p2+p3)*t**3))
    out.append(pts[-1]); return [(v.x, v.y) for v in out]
def river_lines():
    return [[g2m(*p) for p in smooth_poly(r)] for r in J["rivers"]]

# ------------------------------------------------------------------ terrain height
def terrain_height():
    h0 = hm.copy()
    vol = zmask("basalt", "lava") > 0
    h0[vol] = 0.55*np.clip(hm[vol]/8.0, 0, 1)*2.0          # volcano is the TRN_Volcano_Mini model on a gentle mound
    land = zmask("ocean", "shelf", "reef") == 0
    hard = zmask("plateau", "cliff") > 0
    sf = np.where(hard, 1.0, sstep(0.0, 3.6, dw))
    hl = np.where(land, SEA + (h0-SEA)*sf, 0)
    dd = np.minimum(dl, 14.0); hs = SEA - (0.30*dd + 0.07*dd*dd); hs = np.maximum(hs, -9.0)
    base = np.where(land, hl, hs)
    hv = samp(blur(base, 1) if False else base, GX, GY)
    # plateau edges stay crisp: blend between lightly and strongly smoothed
    hv = 0.55*hv + 0.45*samp(blur(base, 1), GX, GY)
    rng = np.random.RandomState(5)
    undul = 0.12*np.sin(XM*0.11+1.3)*np.cos(YM*0.09+0.4) + 0.07*np.sin(XM*0.31)*np.sin(YM*0.27+2.0)
    inland = sstep(1.0, 4.0, samp(dw, GX, GY)); hv = hv + undul*inland*(samp(zmask("grass_short","grass_lush","grass_dry","jungle","swamp","plateau"), GX, GY) > 0.5)
    # hills (zone rock) get extra bumps
    rock = samp(blur(zmask("rock"), 2), GX, GY); hv += 0.35*rock*(0.6+0.4*np.sin(XM*0.8)*np.cos(YM*0.7))
    bank = hv.copy()
    # rivers
    for k, ln in enumerate(river_lines()):
        d = seg_dist(XM, YM, ln); hw = 2.4
        f = 1 - sstep(hw*0.65, hw+1.5, d); hv = hv + ((bank - 0.34) - hv)*f
    # ponds / pools
    for nm, dep in (("pond", 0.42), ("swamp_water", 0.36)):
        m = samp(blur(zmask(nm), 2), GX, GY); hv = hv - dep*sstep(0.18, 0.7, m)
    # waterfall notch + pool (cliff piece replaces plateau face there)
    fx, fy = FALL_XY()
    nx_ = (np.abs(XM-fx) < 2.6) & (YM > fy-1.7) & (YM < fy+1.42)
    hv = np.where(nx_ & (hv > 0.5), np.minimum(hv, 0.0) - 0.6, hv)
    pool = np.exp(-(((XM-fx)/3.2)**2 + ((YM-(fy-2.3))/3.0)**2)); hv = hv - 0.45*pool
    return hv, bank
def FALL_XY(): 
    f = [f for f in J["features"] if f["type"] == "waterfall_big"][0]; return g2m(f["x"], f["y"])

# ------------------------------------------------------------------ ground materials / weights
CLS = ["short","lush","dry","dirt","rock","mud","sand","desert","basalt","lava","swamp","pad"]
ZCLS = dict(ocean="sand", shelf="sand", sand="sand", grass_short="short", grass_lush="lush", grass_dry="dry", dirt="dirt", rock="rock", mud="mud", plateau="lush", cliff="rock",
            swamp="swamp", swamp_water="mud", desert="desert", basalt="basalt", lava="lava", river="sand", pond="mud", jungle="lush", reef="sand", pad="pad", ramp="dirt")
PAL = dict(short=((0.30,0.46,0.12),(0.42,0.62,0.18),(0.55,0.72,0.24)), lush=((0.10,0.26,0.07),(0.20,0.40,0.12),(0.32,0.52,0.18)),
 dry=((0.45,0.38,0.14),(0.64,0.55,0.22),(0.80,0.70,0.36)), dirt=((0.30,0.20,0.10),(0.44,0.31,0.16),(0.58,0.44,0.24)),
 rock=((0.26,0.25,0.23),(0.40,0.39,0.36),(0.55,0.54,0.50)), mud=((0.07,0.05,0.03),(0.13,0.09,0.06),(0.22,0.16,0.11)),
 sand=((0.62,0.52,0.32),(0.78,0.68,0.45),(0.90,0.82,0.60)), desert=((0.48,0.20,0.07),(0.66,0.32,0.12),(0.82,0.48,0.22)),
 basalt=((0.015,0.015,0.015),(0.035,0.033,0.032),(0.075,0.068,0.062)), lava=((0.2,0.02,0.0),(0.8,0.2,0.02),(1.0,0.5,0.1)),
 swamp=((0.03,0.05,0.02),(0.09,0.16,0.04),(0.18,0.30,0.08)), pad=((0.28,0.28,0.27),(0.42,0.42,0.40),(0.58,0.58,0.55)))
def ground_material():
    m = bpy.data.materials.get("ISL_Ground") or bpy.data.materials.new("ISL_Ground"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); N, L = nt.nodes, nt.links
    out = N.new("ShaderNodeOutputMaterial"); bs = N.new("ShaderNodeBsdfPrincipled"); L.new(bs.outputs[0], out.inputs[0])
    tc = N.new("ShaderNodeTexCoord"); obj = tc.outputs["Object"]
    def noise(scale, detail=4, rough=0.6, w=None, vec=None):
        n = N.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail; n.inputs["Roughness"].default_value = rough
        L.new(vec or obj, n.inputs["Vector"]); return n.outputs["Fac"]
    def mapv(scale):
        mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = scale; L.new(obj, mp.inputs["Vector"]); return mp.outputs[0]
    def math_(op, a, b=None):
        n = N.new("ShaderNodeMath"); n.operation = op; 
        for i, x in enumerate((a, b)):
            if x is None: continue
            if isinstance(x, (int, float)): n.inputs[i].default_value = float(x)
            else: L.new(x, n.inputs[i])
        return n.outputs[0]
    def rmap(v, a, b, c=0.0, d=1.0, clamp=True):
        n = N.new("ShaderNodeMapRange"); n.clamp = clamp; L.new(v, n.inputs["Value"])
        for k, x in (("From Min", a), ("From Max", b), ("To Min", c), ("To Max", d)): n.inputs[k].default_value = x
        return n.outputs[0]
    # painterly pattern: big blotches + horizontal brush streaks
    blot = noise(0.35, 5, 0.6); fine = noise(3.2, 3, 0.5); streak = noise(1.6, 2, 0.5, vec=mapv((0.35, 3.5, 1.0)))
    pat = math_('ADD', math_('ADD', math_('MULTIPLY', blot, 0.55), math_('MULTIPLY', fine, 0.25)), math_('MULTIPLY', streak, 0.30))
    pat = rmap(pat, 0.25, 0.85)
    def ramp3(cols, fac):
        r = N.new("ShaderNodeValToRGB"); e = r.color_ramp.elements; e.new(0.5)
        for el, c, p in zip(e, cols, (0.1, 0.5, 0.9)): el.color = (*[x**2.2 for x in c], 1); el.position = p
        L.new(fac, r.inputs[0]); return r.outputs[0]
    attrs = []
    for nm in ("gA", "gB", "gC"):
        a = N.new("ShaderNodeAttribute"); a.attribute_type = 'GEOMETRY'; a.attribute_name = nm
        s = N.new("ShaderNodeSeparateColor"); L.new(a.outputs["Color"], s.inputs[0]); alpha = a.outputs["Alpha"]
        attrs += [s.outputs[0], s.outputs[1], s.outputs[2], alpha]
    edge = noise(1.1, 4, 0.55, vec=mapv((1, 1, 0.5)))
    ws = []
    for k, c in enumerate(CLS):
        w = math_('ADD', attrs[k], math_('MULTIPLY', math_('SUBTRACT', math_('ADD', edge, noise(0.7 + 0.13*k, 3, 0.5)), 1.0), 0.28))
        ws.append(rmap(w, 0.32, 0.62))
    tot = ws[0]
    for w in ws[1:]: tot = math_('ADD', tot, w)
    tot = math_('MAXIMUM', tot, 0.05)
    acc = None
    for k, c in enumerate(CLS):
        col = ramp3(PAL[c], pat)
        wn = math_('DIVIDE', ws[k], tot)
        sc = N.new("ShaderNodeVectorMath"); sc.operation = 'SCALE'; L.new(col, sc.inputs[0]); L.new(wn, sc.inputs["Scale"])
        if acc is None: acc = sc.outputs[0]
        else:
            ad = N.new("ShaderNodeVectorMath"); ad.operation = 'ADD'; L.new(acc, ad.inputs[0]); L.new(sc.outputs[0], ad.inputs[1]); acc = ad.outputs[0]
    sepz = N.new("ShaderNodeSeparateXYZ"); L.new(obj, sepz.inputs[0]); z = sepz.outputs[2]
    deep = N.new("ShaderNodeMix"); deep.data_type = 'RGBA'; deep.inputs[7].default_value = (0.02, 0.17, 0.26, 1); L.new(rmap(z, -0.7, -6.5, 0.0, 1.0), deep.inputs[0]); L.new(acc, deep.inputs[6])
    L.new(deep.outputs[2], bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.92
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.25; bp.inputs["Distance"].default_value = 0.05; L.new(noise(9, 4, 0.6), bp.inputs["Height"]); L.new(bp.outputs[0], bs.inputs["Normal"])
    lava_w = math_('DIVIDE', ws[CLS.index("lava")], tot); crack = rmap(noise(2.6, 5, 0.65), 0.52, 0.60)
    glow = N.new("ShaderNodeValToRGB"); glow.color_ramp.elements[0].color = (0.7, 0.07, 0.01, 1); glow.color_ramp.elements[1].color = (1.0, 0.65, 0.12, 1); L.new(rmap(noise(2.6, 5, 0.65), 0.45, 0.62), glow.inputs[0])
    L.new(glow.outputs[0], bs.inputs["Emission Color"]); L.new(math_('MULTIPLY', math_('MULTIPLY', lava_w, crack), 5.0), bs.inputs["Emission Strength"])
    return m

def build_ground():
    hv, bank = terrain_height()
    coll = bpy.data.collections.get("ISL_Ground") or bpy.data.collections.new("ISL_Ground")
    if coll.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(coll)
    for o in list(coll.objects): bpy.data.objects.remove(o, do_unlink=True)
    verts = np.stack([XM, YM, hv], -1).reshape(-1, 3)
    idx = np.arange(NX*NY).reshape(NY, NX); f = np.stack([idx[:-1,:-1], idx[:-1,1:], idx[1:,1:], idx[1:,:-1]], -1).reshape(-1, 4)
    me = bpy.data.meshes.new("ISL_Ground"); me.vertices.add(len(verts)); me.vertices.foreach_set("co", verts.ravel())
    me.loops.add(len(f)*4); me.loops.foreach_set("vertex_index", f.ravel()); me.polygons.add(len(f))
    me.polygons.foreach_set("loop_start", np.arange(0, len(f)*4, 4)); me.polygons.foreach_set("loop_total", np.full(len(f), 4)); me.polygons.foreach_set("use_smooth", np.ones(len(f), bool))
    me.update(); me.validate()
    wts = np.zeros((len(CLS), NY, NX))
    base = np.zeros((len(CLS), H, W))
    for zn_, cn in ZCLS.items():
        base[CLS.index(cn)] += (zone == ZID[zn_])
    for k in range(len(CLS)): wts[k] = samp(blur(base[k], 2), GX, GY)
    wts = wts/np.maximum(wts.sum(0, keepdims=True), 1e-6)
    # painted overrides: river bed edges stay sandy, volcano mound basalt
    for g, name in enumerate(("gA", "gB", "gC")):
        ca = me.color_attributes.new(name, 'FLOAT_COLOR', 'POINT'); arr = np.stack([wts[g*4+c].ravel() for c in range(4)], -1)
        ca.data.foreach_set("color", arr.ravel())
    ob = bpy.data.objects.new("ISL_Ground", me); coll.objects.link(ob); me.materials.append(ground_material())
    ob["note"] = "heightfield 1 m; weights gA(short,lush,dry,dirt) gB(rock,mud,sand,desert) gC(basalt,lava,swamp,pad)"
    return ob, hv, bank

def h_at(hv, x, y):
    i = np.clip((x-XS[0])/RES, 0, NX-1.001); j = np.clip((y-YS[0])/RES, 0, NY-1.001); i0, j0 = int(i), int(j); fu, fv = i-i0, j-j0
    return float(hv[j0,i0]*(1-fu)*(1-fv) + hv[j0,i0+1]*fu*(1-fv) + hv[j0+1,i0]*(1-fu)*fv + hv[j0+1,i0+1]*fu*fv)

if STAGE in ("ground", "all"):
    ISL_OB, ISL_HV, ISL_BANK = build_ground()
    np.save(ROOT + r"\02_Environment\Island\_hv.npy", ISL_HV); np.save(ROOT + r"\02_Environment\Island\_bank.npy", ISL_BANK)
    result = {"verts": NX*NY, "hmin": float(ISL_HV.min()), "hmax": float(ISL_HV.max())}
