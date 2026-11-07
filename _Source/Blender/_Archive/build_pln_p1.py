"""Dino Park Tycoon - PLN plant sets v01.  BUILD = <Set> (e.g. "Broadleaf") builds collection PLN_<Set>.
Each variant = one mesh (pivot at the base centre, z up, -Y front) + ink outline child (woody parts) + optional *_Ground decal.
Motion: geometry-nodes 'PLN_Motion' (see pln_kit.py MOTION presets) - wind for land plants, travelling current for sea plants,
bob for floating plants, none for rigid wood / coral / cactus. Unity: WindData colour attribute (R bend, G flutter, B phase)."""
import os, math, random
from mathutils import Vector, Matrix, noise
_bp = BUILD; BUILD = "none"
for _f in ("trn_common.py", "trn_hq.py", "trn_hq2.py", "trn_anim.py", "pln_kit.py"):
    exec(open(os.path.join(TOOLS, _f)).read())
BUILD = _bp
RESULTS = {}; VIEW_HINT = None
rad = math.radians

# ------------------------------------------------------------------ palettes (linear)
LEAF_G   = [(0.025,0.075,0.02),(0.05,0.14,0.035),(0.09,0.22,0.05),(0.16,0.31,0.07)]
LEAF_GY  = [(0.05,0.12,0.02),(0.10,0.22,0.04),(0.20,0.35,0.06),(0.32,0.45,0.10)]
NEEDLE   = [(0.018,0.05,0.02),(0.035,0.09,0.03),(0.06,0.15,0.045),(0.11,0.22,0.07)]
FROND    = [(0.03,0.10,0.02),(0.07,0.20,0.04),(0.13,0.30,0.06),(0.24,0.42,0.09)]
BARK_GREY  = [(0.10,0.095,0.085),(0.17,0.16,0.145),(0.26,0.25,0.22),(0.36,0.35,0.31)]
BARK_BROWN = [(0.045,0.022,0.010),(0.09,0.048,0.022),(0.16,0.09,0.042),(0.25,0.15,0.075)]
BARK_RED   = [(0.06,0.022,0.010),(0.12,0.05,0.022),(0.20,0.09,0.04),(0.30,0.15,0.07)]
DEADWOOD   = [(0.16,0.15,0.13),(0.27,0.25,0.22),(0.40,0.38,0.34),(0.52,0.50,0.45)]
MOSS_P     = [(0.05,0.12,0.015),(0.10,0.22,0.03),(0.18,0.32,0.05)]
SOIL       = [(0.035,0.022,0.012),(0.06,0.04,0.022),(0.09,0.06,0.035)]
SAND       = [(0.45,0.32,0.17),(0.58,0.43,0.24),(0.70,0.55,0.33)]

def leaf_mat(name, pal, **kw):
    d = dict(scale=4.0, strokes=0.3, ao_amt=0.55, tint_amt=0.5, top=0.35, vein=0.6, rim=0.25, rough=0.6, spec=0.3, emit=0.05)
    d.update(kw); return plant_mat(name, pal, **d)
def flat_col(name, pal, **kw):
    d = dict(scale=3.0, strokes=0.2, ao_amt=0.35, tint_amt=0.3, top=0.3, rough=0.6, spec=0.3, emit=0.03)
    d.update(kw); return plant_mat(name, pal, **d)

class Row:
    """lays variants left->right along X (front = -Y), records the view frame"""
    def __init__(self, gap=0.6): self.x = 0.0; self.gap = gap; self.items = []
    def place(self, w, h):
        cx = self.x + w/2; self.items.append((cx, w, h)); self.x += w + self.gap; return (cx, 0.0, 0.0)
    def hint(self):
        global VIEW_HINT
        W = self.x - self.gap; H = max(h for _, _, h in self.items)
        for o in bpy.data.objects:
            if o.parent is None and any(o.name.startswith(n) for n in RESULTS): o.location.x -= W/2
        VIEW_HINT = (0.0, H*0.48, W, H)

def mk(P, coll, mats, pos, motion, outline=True, extra=None, ground=None, motion_scale=1.0):
    ob, tris = plant_finish(P, coll, mats, pos, SRC, motion, extra=extra, outline=outline, motion_scale=motion_scale)
    RESULTS[P.name] = tris
    if ground: ground_decal(P.name + "_Ground", coll, ob, *ground)
    return ob

def limb(P, start, d, L, r0, r1, key, depth, seed, tips, kids=3, spread=40, curve=0.2, segs=6, kid_len=0.6, kid_from=0.4,
         sides=8, rough=0.05, upb=0.15, wob=0.1, keep_tip=True):
    rnd = random.Random(seed)
    pts = path(start, d, L, segs, curve=curve, wob=wob, seed=seed*0.37)
    n = len(pts); radii = [r0 + (r1 - r0)*(i/(n-1)) for i in range(n)]
    tube(P, pts, radii, key, sides=sides, rough=rough, seed=seed)
    if depth <= 0 or kids <= 0:
        tips.append((pts[-1], (pts[-1] - pts[-2]).normalized(), L)); return pts
    for k in range(kids):
        t = kid_from + (1 - kid_from)*(k + 0.5)/kids + rnd.uniform(-0.05, 0.05)
        i = max(1, min(n - 2, int(t*(n-1)))); p = pts[i]; dd = (pts[i+1] - pts[i-1]).normalized()
        pp = dd.orthogonal().normalized(); p2 = dd.cross(pp)
        az = k*2.39996 + seed + rnd.uniform(-0.5, 0.5); sp = rad(spread*rnd.uniform(0.8, 1.2))
        nd = (dd*math.cos(sp) + (pp*math.cos(az) + p2*math.sin(az))*math.sin(sp) + UPZ*upb).normalized()
        rr = radii[i]*0.72
        limb(P, p, nd, L*kid_len*rnd.uniform(0.85, 1.1), rr, rr*0.3, key, depth - 1, seed*7 + k + 1, tips, kids, spread, curve,
             max(3, segs - 1), kid_len, kid_from, max(5, sides - 1), rough, upb, wob, keep_tip)
    if keep_tip: tips.append((pts[-1], (pts[-1] - pts[-2]).normalized(), L))
    return pts

def trunk(P, H, r0, r1, key, lean=(0.0, 0.0), segs=10, lobes=None, rough=0.06, seed=0, wob=0.04, sides=12, rings_fn=None, curve_pow=1.0):
    pts = []
    for i in range(segs + 1):
        t = i/segs; z = H*t
        pts.append(Vector((lean[0]*t**(1.6*curve_pow) + wob*noise.noise(Vector((t*2, seed, 0))), lean[1]*t**(1.6*curve_pow) + wob*noise.noise(Vector((seed, t*2, 1))), z)))
    radii = [r0 + (r1 - r0)*(i/segs)**0.7 for i in range(segs + 1)]
    tube(P, pts, radii, key, sides=sides, rough=rough, seed=seed, lobes=lobes, cap=True, rings_fn=rings_fn)
    return pts, radii

def frond(P, base, d, L, key, W=None, lobes=16, depth=0.75, arch=0.35, droop=0.5, fold=0.35, rachis_key=None, rr=0.012, tint=0.5, ao=1.0,
          cn=None, cnw=0.5, shape="lance", twist=0.0, flut=1.0, nu=2):
    """pinnate frond: leaf card with cut leaflets on an arching rachis"""
    W = W or L*0.32; d = Vector(d).normalized()
    side = d.cross(UPZ);  side = side if side.length > 1e-6 else Vector((1, 0, 0))
    up = side.normalized().cross(d).normalized()
    fs = leaf(P, Vector(base), d + UPZ*arch, up, L, W, key, shape=shape, lobes=lobes, lobe_depth=depth, fold=fold, droop=droop, curl=-0.05,
              tint=tint, ao=ao, cn=cn, cnw=cnw, twist=twist, flut=flut, nu=nu)
    if rachis_key:
        pts = []
        dd = (d + UPZ*arch).normalized()
        for j in range(9):
            t = j/8; pts.append(Vector(base) + dd*L*t - UPZ*droop*L*t*t + up*(-0.01))
        tube(P, pts, [rr*(1 - 0.7*j/8) for j in range(9)], rachis_key, sides=5, solid=False, bend=None, flutter=lambda t: t*0.6)
    return fs

# ================================================================== TREES
def build_Broadleaf(coll, row):
    mb = bark_mat("PLN_Broadleaf_Bark", BARK_GREY, crack=0.55, crack_scale=3.2)
    ml = leaf_mat("PLN_Broadleaf_Leaf", LEAF_G, rim=0.3)
    mi = flat_col("PLN_Broadleaf_LeafCore", [(0.012,0.04,0.012),(0.025,0.07,0.02)], vein=0.0, top=0.1)
    mp = leaf_mat("PLN_Broadleaf_Petal", [(0.62,0.58,0.45),(0.82,0.78,0.62),(0.95,0.93,0.80)], vein=0.25, rim=0.0, ao_amt=0.3, tipcol=(1,1,0.95), tip_amt=0.3)
    mc = flat_col("PLN_Broadleaf_FlowerCore", [(0.55,0.40,0.10),(0.80,0.62,0.20)])
    M = {"bark": mb, "leaf": ml, "core": mi, "petal": mp, "fcore": mc}
    # young
    P = Plant("PLN_Broadleaf_Young", 2.4, 0.7, seed=11)
    pts, rr = trunk(P, 1.55, 0.06, 0.035, "bark", lean=(0.05, 0.0), segs=8, seed=1)
    tips = []
    for k, (az, el) in enumerate(((0.4, 38), (2.6, 42), (4.4, 35))):
        limb(P, pts[-2], Vector((math.cos(az)*math.sin(rad(el)), math.sin(az)*math.sin(rad(el)), math.cos(rad(el)))), 0.45, 0.03, 0.012, "bark", 0, 20+k, tips)
    for i, (p, d, L) in enumerate(tips): clump(P, p + Vector((0, 0, 0.06)), 0.36, 22, "leaf", 0.30, 0.17, inner_key="core", seed=30+i, flat=0.8)
    clump(P, pts[-1] + Vector((0, 0, 0.3)), 0.42, 26, "leaf", 0.32, 0.18, inner_key="core", seed=39, flat=0.85)
    mk(P, coll, M, row.place(1.5, 2.4), "tree")
    # flowering
    P = Plant("PLN_Broadleaf_Flowering", 4.0, 1.7, seed=12)
    pts, rr = trunk(P, 1.6, 0.20, 0.13, "bark", segs=8, lobes=(5, 0.35, 0.35), seed=2)
    tips = []
    for k, az in enumerate((0.3, 1.9, 3.3, 4.8)):
        limb(P, pts[-2], Vector((math.cos(az)*0.65, math.sin(az)*0.65, 0.76)), 1.2, 0.10, 0.04, "bark", 1, 40+k, tips, kids=2, spread=35, kid_len=0.55)
    cents = []
    for i, (p, d, L) in enumerate(tips):
        c = p + Vector((0, 0, 0.12)); cents.append(c); clump(P, c, 0.62, 30, "leaf", 0.46, 0.27, inner_key="core", seed=60+i, flat=0.72)
    clump(P, Vector((0, 0, 3.25)), 0.8, 34, "leaf", 0.5, 0.29, inner_key="core", seed=79, flat=0.75)
    rnd = random.Random(5)
    for k in range(11):   # magnolia flowers sitting on the leaf mass
        c = rnd.choice(cents + [Vector((0, 0, 3.25))]); a = rnd.uniform(0, 6.28); e = rnd.uniform(0.2, 1.1)
        nr = Vector((math.cos(a)*math.cos(e), math.sin(a)*math.cos(e), math.sin(e))); fc = c + nr*0.66
        for j in range(6):
            aa = j*1.047 + rnd.uniform(-.1, .1); sd = nr.orthogonal().normalized(); sd2 = nr.cross(sd)
            dd = (nr*0.55 + (sd*math.cos(aa) + sd2*math.sin(aa))).normalized()
            leaf(P, fc, dd, nr, 0.13, 0.075, "petal", shape="petal", fold=0.5, curl=0.25, nv=4, bend=P.auto_bend(c), flut=0.4)
        ball(P, fc + nr*0.02, 0.03, "fcore", sub=1, bend=P.auto_bend(c))
    mk(P, coll, M, row.place(3.4, 4.0), "tree")
    # tall layered
    P = Plant("PLN_Broadleaf_Tall", 6.5, 2.0, seed=13)
    pts, rr = trunk(P, 4.6, 0.24, 0.10, "bark", lean=(0.1, 0.05), segs=12, lobes=(6, 0.4, 0.45), seed=3)
    tips = []
    for k, (h, az, L) in enumerate(((0.45, 0.5, 1.0), (0.58, 2.7, 1.15), (0.70, 4.6, 1.0), (0.82, 1.6, 0.9), (0.92, 3.8, 0.8))):
        i = int(h*12); limb(P, pts[i], Vector((math.cos(az)*0.75, math.sin(az)*0.75, 0.55)), L, rr[i]*0.55, 0.03, "bark", 1, 80+k, tips, kids=2, spread=30, kid_len=0.5)
    for i, (p, d, L) in enumerate(tips):
        clump(P, p + Vector((0, 0, 0.1)), 0.62, 28, "leaf", 0.5, 0.28, inner_key="core", seed=100+i, flat=0.45, polar_max=105, droop=0.4)
    for j, (z, r) in enumerate(((4.9, 1.0), (5.75, 0.85))):
        clump(P, Vector((0.12, 0.02, z)), r, 38, "leaf", 0.6, 0.33, inner_key="core", seed=120+j, flat=0.42, polar_max=110, droop=0.45)
    mk(P, coll, M, row.place(3.6, 6.4), "tree")
    # stub branches on the trunk are part of limb(); done

def conifer_tiers(P, z0, z1, r0, r1, key, ntier, per, L0, L1, seed, droop=0.35, trunk_r=lambda z: 0.05, tint=0.5):
    rnd = random.Random(seed)
    for t in range(ntier):
        f = t/max(1, ntier - 1); z = z0 + (z1 - z0)*f; L = L0 + (L1 - L0)*f; n = max(3, int(per - f*(per - 4)))
        for k in range(n):
            a = k*2*math.pi/n + t*0.9 + rnd.uniform(-0.2, 0.2)
            dirv = Vector((math.cos(a), math.sin(a), -0.15 - 0.25*rnd.random()))
            base = Vector((math.cos(a)*trunk_r(z)*0.5, math.sin(a)*trunk_r(z)*0.5, z))
            cn = Vector((0, 0, z - 0.4))
            Lk = L*rnd.uniform(0.85, 1.12); ao = 0.55 + 0.45*f
            leaf(P, base, dirv, UPZ, Lk, Lk*0.42, key, shape="spray", lobes=7, lobe_depth=0.6, fold=0.45, droop=droop, tint=tint + rnd.uniform(-.2, .2),
                 ao=ao, cn=cn, cnw=0.6, nv=6)
            for s in (-1, 1):
                b2 = base + dirv.normalized()*Lk*0.35
                d2 = (dirv.normalized() + Vector((-math.sin(a), math.cos(a), 0))*0.7*s + UPZ*0.15).normalized()
                leaf(P, b2, d2, UPZ, Lk*0.55, Lk*0.25, key, shape="spray", lobes=5, lobe_depth=0.6, fold=0.4, droop=droop*0.8, tint=tint + rnd.uniform(-.2, .2),
                     ao=ao*0.95, cn=cn, cnw=0.6, nv=5)

def cone_cluster(P, c, key, n=3, s=0.06, seed=0):
    rnd = random.Random(seed)
    for k in range(n):
        p = Vector(c) + Vector((rnd.uniform(-.05, .05), rnd.uniform(-.05, .05), -k*0.04))
        lathe(P, [(0.001, -s*1.5), (s*0.55, -s*1.2), (s*0.8, -s*0.5), (s*0.6, s*0.2), (0.001, s*0.5)], key, sides=8, center=p, ribs=(10, 0.18), solid=False,
              bend=P.auto_bend(p))

def build_Conifer(coll, row):
    mb = bark_mat("PLN_Conifer_Bark", BARK_RED, crack=0.75, crack_scale=4.5, stretch=(6, 6, 0.6))
    mn = leaf_mat("PLN_Conifer_Needles", NEEDLE, vein=0.5, rim=0.15, tipcol=(0.14,0.27,0.08), tip_amt=0.35, scale=6.0)
    mc = flat_col("PLN_Conifer_Cone", [(0.06,0.03,0.012),(0.14,0.07,0.03),(0.24,0.13,0.06)])
    M = {"bark": mb, "nd": mn, "cone": mc}
    P = Plant("PLN_Conifer_Young", 2.8, 0.8, seed=21)
    pts, rr = trunk(P, 2.7, 0.06, 0.012, "bark", segs=10, seed=4)
    conifer_tiers(P, 0.75, 2.55, 0.7, 0.2, "nd", 6, 5, 0.62, 0.22, 7, trunk_r=lambda z: 0.05)
    mk(P, coll, M, row.place(1.5, 2.8), "conifer")
    P = Plant("PLN_Conifer_Mature", 4.8, 1.4, seed=22)
    pts, rr = trunk(P, 4.7, 0.20, 0.02, "bark", segs=12, lobes=(5, 0.3, 0.3), seed=5)
    conifer_tiers(P, 0.55, 4.55, 1.3, 0.25, "nd", 10, 9, 1.25, 0.28, 8, trunk_r=lambda z: 0.18*(1 - z/4.8))
    for k, (z, a) in enumerate(((2.3, 0.4), (3.2, 2.8), (1.6, 4.5), (2.8, 5.6))):
        r = 1.1*(1 - (z - 0.5)/4.2) + 0.1; cone_cluster(P, (math.cos(a)*r*0.75, math.sin(a)*r*0.75, z - 0.15), "cone", 2, 0.06, k)
    mk(P, coll, M, row.place(2.8, 4.8), "conifer")
    P = Plant("PLN_Conifer_TallOld", 7.0, 1.3, seed=23)
    pts, rr = trunk(P, 6.7, 0.26, 0.04, "bark", segs=14, lobes=(6, 0.35, 0.4), seed=6, rough=0.09)
    tips = []
    for k, h in enumerate((0.22, 0.3, 0.36)):   # dead stubs on the bare lower trunk
        i = int(h*14); a = k*2.2 + 0.6
        limb(P, pts[i], Vector((math.cos(a), math.sin(a), -0.15)), 0.35, rr[i]*0.25, 0.01, "bark", 0, 140+k, tips, sides=5)
    conifer_tiers(P, 3.0, 6.3, 1.2, 0.3, "nd", 9, 9, 1.15, 0.3, 9, trunk_r=lambda z: 0.2*(1 - z/7.0))
    sp = path(Vector((0.02, 0, 6.6)), Vector((0.08, 0, 1)), 0.55, 4, wob=0.05, seed=3)   # broken dead top
    tube(P, sp, [0.045, 0.035, 0.025, 0.014, 0.004], "bark", sides=6)
    for k, (z, a) in enumerate(((4.2, 0.3), (5.1, 2.4), (5.6, 4.4), (4.7, 5.5), (3.6, 1.6))):
        r = 1.1*(1 - (z - 3.0)/3.6) + 0.15; cone_cluster(P, (math.cos(a)*r*0.7, math.sin(a)*r*0.7, z - 0.18), "cone", 2, 0.07, 10 + k)
    mk(P, coll, M, row.place(2.8, 7.2), "conifer")

def build_GiantTree(coll, row):
    mb = bark_mat("PLN_Giant_Bark", BARK_BROWN, crack=0.85, crack_scale=2.6, stretch=(4, 4, 0.5))
    ml = leaf_mat("PLN_Giant_Leaf", [(0.03,0.08,0.015),(0.07,0.16,0.03),(0.13,0.26,0.05),(0.22,0.36,0.08)], rim=0.35)
    mi = flat_col("PLN_Giant_Core", [(0.012,0.035,0.01),(0.025,0.06,0.018)], top=0.1)
    M = {"bark": mb, "leaf": ml, "core": mi}
    for nm, H, th, r0, spread_r, seed in (("PLN_GiantTree_Wide", 8.5, 4.6, 0.75, 3.4, 31), ("PLN_GiantTree_Tall", 11.0, 7.0, 0.8, 3.6, 32)):
        P = Plant(nm, H, spread_r, seed=seed)
        pts, rr = trunk(P, th, r0, r0*0.55, "bark", segs=14, lobes=(7, 0.8, 1.6), seed=seed, rough=0.07, sides=18, wob=0.08)
        tips = []
        for k in range(6 if seed == 31 else 5):
            a = k*1.15 + 0.3; i = 14 - (k % 2)
            limb(P, pts[i], Vector((math.cos(a)*0.8, math.sin(a)*0.8, 0.5 + 0.1*(k % 3))), spread_r*0.7, rr[i]*0.42, 0.06, "bark", 2, seed*10 + k, tips,
                 kids=2, spread=32, curve=0.12, kid_len=0.55, upb=0.25)
        for i, (p, d, L) in enumerate(tips):
            if L < 0.5: continue
            clump(P, p + Vector((0, 0, 0.15)), 0.9 + 0.25*((i*7) % 3)/2, 30, "leaf", 0.72, 0.4, inner_key="core", seed=seed*20 + i, flat=0.45, polar_max=100, droop=0.35)
        clump(P, pts[-1] + Vector((0, 0, 0.9)), 1.4, 42, "leaf", 0.8, 0.45, inner_key="core", seed=seed*20 + 99, flat=0.45, polar_max=100)
        mk(P, coll, M, row.place(spread_r*2.2, H), "tree_big", outline_th if False else True)

def build_Ginkgo(coll, row):
    mb = bark_mat("PLN_Ginkgo_Bark", BARK_GREY, crack=0.6, crack_scale=3.5)
    ml = leaf_mat("PLN_Ginkgo_Leaf", [(0.12,0.16,0.02),(0.26,0.30,0.04),(0.45,0.42,0.07),(0.62,0.38,0.05)], vein=0.2, rim=0.3, tint_amt=0.8,
                  tipcol=(0.70,0.38,0.05), tip_amt=0.25)
    mi = flat_col("PLN_Ginkgo_Core", [(0.05,0.07,0.01),(0.10,0.12,0.02)], top=0.1)
    M = {"bark": mb, "leaf": ml, "core": mi}
    for nm, H, th, r0, sr, nl, seed, lsize in (("PLN_Ginkgo_Young", 2.8, 1.5, 0.05, 0.9, 1, 41, 0.18), ("PLN_Ginkgo_Mature", 5.8, 2.2, 0.26, 2.3, 2, 42, 0.34)):
        P = Plant(nm, H, sr, seed=seed)
        pts, rr = trunk(P, th, r0, r0*0.6, "bark", segs=10, lobes=(5, 0.4, 0.4) if nl > 1 else None, seed=seed, wob=0.05)
        tips = []
        nb = 4 if nl > 1 else 4
        for k in range(nb):
            a = k*1.6 + 0.4; i = 10 - (k % 2)*2
            limb(P, pts[i], Vector((math.cos(a)*0.7, math.sin(a)*0.7, 0.7)), sr*0.75, rr[i]*0.5, 0.015, "bark", nl, seed*10 + k, tips, kids=2, spread=35, kid_len=0.6, upb=0.2, curve=0.1)
        for i, (p, d, L) in enumerate(tips):
            R = lsize*1.9; c = p + Vector((0, 0, R*0.25))
            clump(P, c, R, 22 if nl > 1 else 12, "leaf", lsize, lsize*0.95, shape="fan", flat=0.6, fold=0.15, droop=0.3, inner_key="core" if nl > 1 else None,
                  seed=seed*30 + i, tint=random.Random(i*13 + seed).uniform(0.15, 0.95))
        mk(P, coll, M, row.place(sr*2.3, H), "tree")

def prop_roots(P, top, n, R, key, r0, seed, h_top=0.6, arch=0.35, sides=6):
    rnd = random.Random(seed)
    for k in range(n):
        a = k*2*math.pi/n + rnd.uniform(-0.3, 0.3); rr = R*rnd.uniform(0.75, 1.1)
        p0 = Vector(top) + Vector((math.cos(a)*0.05, math.sin(a)*0.05, rnd.uniform(-0.1, 0.1)))
        end = Vector((math.cos(a)*rr, math.sin(a)*rr, -0.03)); pts = []
        for j in range(9):
            t = j/8; p = p0.lerp(end, t); p.z += arch*math.sin(math.pi*t)*(1 - t*0.4) * (h_top)
            pts.append(p)
        tube(P, pts, [r0*(1 - 0.45*j/8) for j in range(9)], key, sides=sides, bend=lambda t: 0.02, rough=0.08, seed=k)
        if rnd.random() < 0.5:   # secondary root branching off
            i = rnd.randint(3, 5); a2 = a + rnd.choice((-0.6, 0.6)); e2 = pts[i] + Vector((math.cos(a2)*rr*0.45, math.sin(a2)*rr*0.45, 0))
            e2.z = -0.03; p2 = [pts[i].lerp(e2, j/5) + Vector((0, 0, 0.12*math.sin(math.pi*j/5)*(1 - j/5))) for j in range(6)]
            tube(P, p2, [r0*0.55*(1 - 0.4*j/5) for j in range(6)], key, sides=5, bend=lambda t: 0.02)

def build_Mangrove(coll, row):
    mb = bark_mat("PLN_Mangrove_Bark", [(0.10,0.09,0.075),(0.18,0.16,0.13),(0.27,0.25,0.21),(0.36,0.34,0.29)], crack=0.5)
    ml = leaf_mat("PLN_Mangrove_Leaf", [(0.03,0.09,0.015),(0.07,0.18,0.03),(0.15,0.30,0.05),(0.28,0.40,0.08)], rim=0.35, spec=0.5, rough=0.4)
    mi = flat_col("PLN_Mangrove_Core", [(0.012,0.04,0.01),(0.03,0.07,0.02)], top=0.1)
    M = {"bark": mb, "leaf": ml, "core": mi}
    P = Plant("PLN_Mangrove_Small", 2.2, 0.8, seed=51)
    pts, rr = trunk(P, 1.25, 0.07, 0.05, "bark", segs=6, seed=7)
    prop_roots(P, Vector((0, 0, 0.55)), 7, 0.95, "bark", 0.035, 3, h_top=0.9, arch=0.25)
    tips = []
    for k in range(3):
        a = k*2.1; limb(P, pts[-2], Vector((math.cos(a)*0.6, math.sin(a)*0.6, 0.8)), 0.4, 0.04, 0.015, "bark", 0, 160+k, tips)
    for i, (p, d, L) in enumerate(tips): clump(P, p, 0.38, 22, "leaf", 0.26, 0.15, inner_key="core", seed=170+i, flat=0.8)
    clump(P, Vector((0, 0, 1.75)), 0.5, 30, "leaf", 0.3, 0.17, inner_key="core", seed=179, flat=0.85)
    mk(P, coll, M, row.place(2.0, 2.2), "tree")
    P = Plant("PLN_Mangrove_Big", 5.2, 2.3, seed=52)
    pts, rr = trunk(P, 2.8, 0.30, 0.18, "bark", segs=10, seed=8, rough=0.1, lobes=(5, 0.5, 0.6))
    prop_roots(P, Vector((0, 0, 1.0)), 12, 1.9, "bark", 0.07, 4, h_top=1.3, arch=0.25, sides=7)
    prop_roots(P, Vector((0, 0, 0.6)), 7, 1.3, "bark", 0.05, 5, h_top=0.8, arch=0.25)
    tips = []
    for k in range(5):
        a = k*1.26 + 0.2; limb(P, pts[-2 - (k % 2)], Vector((math.cos(a)*0.85, math.sin(a)*0.85, 0.45)), 1.6, 0.11, 0.03, "bark", 1, 180+k, tips, kids=2, spread=30, kid_len=0.5)
    rnd = random.Random(9)
    for i, (p, d, L) in enumerate(tips):
        clump(P, p + Vector((0, 0, 0.12)), 0.75, 30, "leaf", 0.5, 0.28, inner_key="core", seed=190+i, flat=0.5, polar_max=100)
        if L > 0.9 and rnd.random() < 0.8:   # hanging aerial roots
            for j in range(2):
                q = p - d*rnd.uniform(0.3, 0.8); hl = q.z*rnd.uniform(0.45, 0.85)
                hp = [q + Vector((0.02*math.sin(t*4 + j), 0, -hl*t)) for t in [x/6 for x in range(7)]]
                tube(P, hp, [0.012]*6 + [0.006], "bark", sides=5, solid=False)
    clump(P, Vector((0, 0, 4.2)), 1.1, 38, "leaf", 0.6, 0.33, inner_key="core", seed=199, flat=0.45, polar_max=105)
    mk(P, coll, M, row.place(4.4, 5.2), "tree")

def palm_crown(P, top, n, L, key, rk, seed, droop=0.55, arch=0.45, W=None, tint=0.5, lobes=22, depth=0.82, tilt=0.0):
    rnd = random.Random(seed); fs = []
    for k in range(n):
        a = k*2.39996 + rnd.uniform(-0.2, 0.2); up_ = (k % 3)*0.15 - 0.05 + tilt
        d = Vector((math.cos(a), math.sin(a), up_)); Lk = L*rnd.uniform(0.85, 1.1)
        fs += frond(P, Vector(top), d, Lk, key, W=(W or Lk*0.3), lobes=lobes, depth=depth, arch=arch*rnd.uniform(0.7, 1.2), droop=droop*rnd.uniform(0.8, 1.2),
                    fold=0.45, rachis_key=rk, rr=0.02*L, tint=tint + rnd.uniform(-0.2, 0.2), cn=Vector(top) - Vector((0, 0, 0.4*L)), cnw=0.45,
                    ao=0.6 + 0.4*min(1, max(0, up_ + 0.4)))
    return fs

def build_Palm(coll, row):
    mb = bark_mat("PLN_Palm_Trunk", [(0.14,0.12,0.09),(0.24,0.21,0.16),(0.36,0.32,0.25),(0.46,0.42,0.33)], crack=0.3, stretch=(2, 2, 3))
    mf = leaf_mat("PLN_Palm_Frond", FROND, vein=0.7, rim=0.2, tipcol=(0.30,0.40,0.10), tip_amt=0.35)
    mr = flat_col("PLN_Palm_Rachis", [(0.10,0.14,0.03),(0.20,0.24,0.06)])
    mc = flat_col("PLN_Palm_Coconut", [(0.06,0.06,0.015),(0.14,0.12,0.03),(0.25,0.20,0.06)], spec=0.4, rough=0.45)
    M = {"bark": mb, "frond": mf, "rachis": mr, "nut": mc}
    for nm, H, lean, nfr, L, seed, nuts in (("PLN_Palm_Short", 3.6, (0.35, 0.0), 12, 1.5, 61, 0), ("PLN_Palm_Coconut", 6.2, (0.75, 0.15), 14, 2.1, 62, 6)):
        P = Plant(nm, H, 1.6, seed=seed)
        ring = lambda t, a: 1 + 0.06*(abs(math.sin(t*math.pi*28)))**4
        pts, rr = trunk(P, H - 0.3, 0.16 if nuts else 0.12, 0.10 if nuts else 0.085, "bark", lean=lean, segs=16, seed=seed, sides=12, rings_fn=ring, curve_pow=0.8, wob=0.03)
        top = pts[-1] + Vector((0, 0, 0.05))
        palm_crown(P, top, nfr, L, "frond", "rachis", seed, droop=0.6, arch=0.55)
        rnd = random.Random(seed)
        for k in range(nuts): ball(P, top + Vector((math.cos(k*1.1)*0.13, math.sin(k*1.1)*0.13, -0.18 - 0.05*(k % 2))), 0.1, "nut", sub=2, squash=1.1, noise_amp=0.05)
        mk(P, coll, M, row.place(3.2 if nuts else 2.6, H), "palm")

def build_FernTree(coll, row):
    mb = bark_mat("PLN_FernTree_Trunk", BARK_BROWN, crack=0.6, crack_scale=6.0, stretch=(3, 3, 2.0))
    mf = leaf_mat("PLN_FernTree_Frond", FROND, vein=0.6, rim=0.2, tipcol=(0.32,0.40,0.10), tip_amt=0.3)
    md = leaf_mat("PLN_FernTree_DeadFrond", [(0.10,0.05,0.015),(0.20,0.11,0.03),(0.32,0.19,0.06)], vein=0.3)
    mr = flat_col("PLN_FernTree_Rachis", [(0.08,0.10,0.02),(0.16,0.20,0.05)])
    M = {"bark": mb, "frond": mf, "dead": md, "rachis": mr}
    for nm, H, L, nfr, seed in (("PLN_FernTree_Small", 1.8, 0.9, 10, 71), ("PLN_FernTree_Medium", 3.2, 1.4, 12, 72), ("PLN_FernTree_Tall", 4.8, 1.75, 14, 73)):
        P = Plant(nm, H, L, seed=seed)
        tr = lambda t, a: 1 + 0.10*abs(noise.noise(Vector((math.cos(a)*3, math.sin(a)*3, t*12))))
        pts, rr = trunk(P, H - 0.35, 0.13*H/3, 0.085*H/3, "bark", segs=12, seed=seed, lobes=(6, 0.5, 0.35*H/3), rings_fn=tr, sides=12)
        rnd = random.Random(seed)
        for k in range(int(10*H/3)):   # old frond bases
            t = rnd.uniform(0.35, 0.95); i = int(t*12); a = rnd.uniform(0, 6.28); p = pts[i]
            d = Vector((math.cos(a), math.sin(a), 0.6)).normalized()
            tube(P, [p, p + d*0.08*H/3, p + d*0.11*H/3 + Vector((0, 0, -0.02))], [rr[i]*0.25, rr[i]*0.18, 0.004], "bark", sides=5)
        top = pts[-1] + Vector((0, 0, 0.04))
        palm_crown(P, top, nfr, L, "frond", "rachis", seed, droop=0.55, arch=0.5, lobes=20, depth=0.7, W=L*0.34)
        for k in range(3):
            a = k*2.1; fiddlehead(P, top + Vector((math.cos(a)*0.05, math.sin(a)*0.05, 0.02)), Vector((math.cos(a)*0.3, math.sin(a)*0.3, 1)), 0.06*H/3 + 0.03, "rachis", r_tube=0.012)
        if H > 4:
            for k in range(3):
                a = k*2.0 + 0.8; d = Vector((math.cos(a), math.sin(a), -1.4))
                frond(P, top - Vector((0, 0, 0.1)), d, L*0.8, "dead", lobes=16, depth=0.6, arch=0.0, droop=0.15, fold=0.6, flut=0.5)
        mk(P, coll, M, row.place(L*1.9, H), "palm", motion_scale=0.7)

def cycad_trunk(P, H, R, key, seed):
    prof = []; n = 22
    for j in range(n + 1):
        t = j/n; r = R*(0.82 + 0.25*math.sin(math.pi*min(1.0, t*1.05))**0.6 - 0.25*t**3)
        prof.append((max(0.02, r), H*t))
    rings = []; sides = 22; ph = P.rnd.random()
    for j, (r, z) in enumerate(prof):
        ring = []
        for k in range(sides):
            a = 2*math.pi*k/sides
            dia = max(abs(math.sin(a*5.5 + z*13.0)), abs(math.sin(a*5.5 - z*13.0)))
            rr = r*(1 + 0.07*dia**3)
            ring.append(P.v((rr*math.cos(a), rr*math.sin(a), z), phase=ph))
        rings.append(ring)
    for j in range(n):
        for k in range(sides):
            P.face((rings[j][k], rings[j][(k+1) % sides], rings[j+1][(k+1) % sides], rings[j+1][k]), key, True)
    c = P.v((0, 0, H + 0.02))
    for k in range(sides): P.face((rings[-1][k], rings[-1][(k+1) % sides], c), key, True)

def build_Cycad(coll, row):
    mb = plant_mat("PLN_Cycad_Trunk", [(0.07,0.065,0.05),(0.15,0.14,0.11),(0.25,0.24,0.20),(0.36,0.35,0.30)], scale=6, strokes=0.3, ao_amt=0.2,
                   top=0.3, crack=0.0, edge=(0.55,0.52,0.45), edge_amt=0.8, geo_ao=0.6, rough=0.85, emit=0.0)
    mf = leaf_mat("PLN_Cycad_Frond", [(0.02,0.08,0.015),(0.05,0.16,0.03),(0.10,0.27,0.05),(0.18,0.37,0.07)], vein=0.7, rim=0.25, spec=0.45, rough=0.45)
    mr = flat_col("PLN_Cycad_Rachis", [(0.05,0.10,0.02),(0.12,0.20,0.04)])
    mc = plant_mat("PLN_Cycad_Cone", [(0.40,0.12,0.01),(0.70,0.27,0.03),(0.90,0.45,0.08)], scale=8, edge=(1.0,0.7,0.3), edge_amt=0.7, geo_ao=0.5, top=0.3, emit=0.05)
    M = {"bark": mb, "frond": mf, "rachis": mr, "cone": mc}
    for nm, H, R, L, nfr, seed, cone in (("PLN_Cycad_Small", 0.55, 0.2, 0.75, 12, 81, False), ("PLN_Cycad_Large", 1.15, 0.38, 1.35, 16, 82, True)):
        P = Plant(nm, H + L*0.5, 0.8, seed=seed)
        cycad_trunk(P, H, R, "bark", seed)
        top = Vector((0, 0, H))
        palm_crown(P, top, nfr, L, "frond", "rachis", seed, droop=0.45, arch=0.95, lobes=26, depth=0.85, W=L*0.28)
        if cone:
            pr = [(0.001, -0.02), (0.11, 0.05), (0.15, 0.18), (0.14, 0.32), (0.09, 0.44), (0.001, 0.52)]
            lathe(P, pr, "cone", sides=16, center=(0, 0, H), ribs=(14, 0.12), solid=True, bend=0.05)
            for k in range(2): fiddlehead(P, top + Vector((0.14*(k*2 - 1), 0.05, 0.25)), Vector((0.4*(k*2 - 1), 0, 1)), 0.06, "rachis", r_tube=0.012)
        mk(P, coll, M, row.place(L*1.8, H + L*0.6), "palm", motion_scale=0.35)

def gnarl_branches(P, pts, rr, key, seed, n, L, depth, kids, spread=45, broken=0.4):
    rnd = random.Random(seed); tips = []
    for k in range(n):
        i = rnd.randint(int(len(pts)*0.45), len(pts) - 2); a = k*2.3 + rnd.uniform(-.4, .4)
        d = Vector((math.cos(a), math.sin(a), rnd.uniform(0.2, 0.9))).normalized()
        limb(P, pts[i], d, L*rnd.uniform(0.7, 1.1), rr[i]*0.5, 0.008 if rnd.random() > broken else rr[i]*0.25, key, depth, seed*13 + k, tips,
             kids=kids, spread=spread, curve=0.05, wob=0.25, kid_len=0.55, sides=7, rough=0.12)
    return tips

def build_DeadTrees(coll, row):
    mb = bark_mat("PLN_Dead_Wood", DEADWOOD, crack=0.9, crack_scale=5.0, stretch=(7, 7, 0.45), edge=(0.75,0.72,0.66))
    mh = flat_col("PLN_Dead_Hole", [(0.01,0.008,0.006),(0.03,0.025,0.02)], top=0.0)
    M = {"bark": mb, "hole": mh}
    P = Plant("PLN_DeadTree_Twisted", 3.6, 1.4, seed=91)
    tw = lambda t, a: 1 + 0.18*abs(math.sin(a*2 + t*9))**3
    pts, rr = trunk(P, 2.6, 0.26, 0.09, "bark", lean=(0.25, 0.1), segs=14, lobes=(6, 0.8, 0.5), seed=9, rough=0.12, wob=0.18, sides=14, rings_fn=tw)
    gnarl_branches(P, pts, rr, "bark", 91, 5, 1.2, 2, 2)
    ball(P, pts[7] + Vector((0, -rr[7]*0.85, 0)), rr[7]*0.28, "hole", sub=2, squash=1.5, bend=0.05)
    mk(P, coll, M, row.place(2.8, 3.6), "deadwood")
    P = Plant("PLN_DeadTree_Broken", 3.4, 1.5, seed=92)
    pts, rr = trunk(P, 2.9, 0.24, 0.07, "bark", lean=(0.9, 0.0), segs=12, lobes=(5, 0.7, 0.5), seed=10, rough=0.14, wob=0.1, sides=14, rings_fn=tw)
    sp = path(Vector((-0.08, 0, 0.3)), Vector((-0.15, 0, 1)), 1.4, 6, wob=0.08, seed=4)   # snapped second stem
    tube(P, sp, [0.17 - 0.08*j/6 for j in range(7)], "bark", sides=12, rough=0.18, seed=3)
    for k in range(5):   # jagged splinters at the break
        a = k*1.25; tip = sp[-1] + Vector((math.cos(a)*0.06, math.sin(a)*0.06, 0.08 + 0.12*(k % 3)))
        tube(P, [sp[-1] + Vector((math.cos(a)*0.07, math.sin(a)*0.07, -0.05)), tip], [0.035, 0.002], "bark", sides=4)
    gnarl_branches(P, pts, rr, "bark", 92, 4, 1.0, 2, 2)
    ball(P, pts[5] + Vector((0, -rr[5]*0.8, 0)), rr[5]*0.35, "hole", sub=2, squash=2.0, bend=0.05)
    mk(P, coll, M, row.place(3.0, 3.6), "deadwood")

def build_StrippedTrees(coll, row):
    mb = bark_mat("PLN_Stripped_Bark", [(0.06,0.035,0.018),(0.12,0.075,0.04),(0.20,0.13,0.07),(0.30,0.21,0.12)], crack=0.85, crack_scale=5.5, stretch=(7, 7, 0.5))
    mg = bark_mat("PLN_Stripped_GreyBark", [(0.08,0.075,0.065),(0.15,0.14,0.12),(0.24,0.23,0.20),(0.33,0.32,0.28)], crack=0.7)
    mn = leaf_mat("PLN_Stripped_Needles", NEEDLE, vein=0.4, rim=0.2)
    ml = leaf_mat("PLN_Stripped_Leaf", LEAF_G, rim=0.25)
    M = {"bark": mb, "grey": mg, "nd": mn, "leaf": ml}
    P = Plant("PLN_Stripped_Conifer", 4.6, 1.2, seed=101)
    pts, rr = trunk(P, 4.4, 0.17, 0.015, "bark", segs=14, seed=11, rough=0.1, lobes=(5, 0.4, 0.35))
    rnd = random.Random(3); tips = []
    for k in range(26):
        t = 0.18 + 0.78*k/26; i = int(t*14); a = k*2.39996; L = 1.2*(1 - t)**0.8 + 0.15
        d = Vector((math.cos(a), math.sin(a), -0.25 + rnd.uniform(-0.15, 0.2)))
        limb(P, pts[i], d, L, rr[i]*0.35, 0.006, "bark", 1 if L > 0.6 else 0, 300 + k, tips, kids=2, spread=50, wob=0.2, kid_len=0.4, sides=5, rough=0.1, upb=-0.05)
    for j, (p, d, L) in enumerate(tips):
        if rnd.random() < 0.16:
            leaf(P, p - d*0.1, d + Vector((0, 0, -0.3)), UPZ, 0.28, 0.12, "nd", shape="spray", lobes=5, lobe_depth=0.6, fold=0.4, droop=0.3, nv=5)
    mk(P, coll, M, row.place(2.4, 4.6), "deadwood")
    P = Plant("PLN_Stripped_Broadleaf", 4.0, 1.7, seed=102)
    pts, rr = trunk(P, 1.9, 0.22, 0.12, "grey", lean=(0.15, 0), segs=10, seed=12, rough=0.12, lobes=(6, 0.6, 0.45), wob=0.1)
    tips = []
    for k in range(5):
        a = k*1.3 + 0.4; limb(P, pts[-2], Vector((math.cos(a)*0.75, math.sin(a)*0.75, 0.6)), 1.4, 0.11, 0.01, "grey", 2, 320 + k, tips, kids=2, spread=40, wob=0.25, kid_len=0.55, sides=7, rough=0.12)
    for j, (p, d, L) in enumerate(tips):
        if rnd.random() < 0.12:
            for q in range(3): leaf(P, p, d + Vector((rnd.uniform(-.6, .6), rnd.uniform(-.6, .6), -0.5)), UPZ, 0.14, 0.08, "leaf", fold=0.3, droop=0.3, nv=4)
    for k in range(3):  # a few leaf sprigs on the trunk like the reference
        a = k*2.1; p = pts[3 + k] + Vector((math.cos(a)*rr[3+k], math.sin(a)*rr[3+k], 0))
        for q in range(3): leaf(P, p, Vector((math.cos(a + q*0.5 - 0.5), math.sin(a + q*0.5 - 0.5), 0.2)), UPZ, 0.12, 0.07, "leaf", fold=0.3, droop=0.3, nv=4)
    mk(P, coll, M, row.place(3.2, 4.0), "deadwood")

# ================================================================== GROUND COVER
def soil_mat(name, pal=SOIL, moss=None):
    return plant_mat(name, pal, scale=5, strokes=0.4, ao_amt=0.2, top=0.2, rough=0.95, spec=0.1, emit=0.0, moss=moss, moss_amt=0.6 if moss else 0.0)

def bush_ball(P, c, R, key, inner, n_cl, leafL, leafW, seed, shape="round", flat=0.85, lobes=0, tint=None):
    rnd = random.Random(seed); c = Vector(c)
    for k in range(n_cl):
        f = (k + 0.5)/n_cl; pol = math.acos(1 - 1.6*f); az = k*2.39996
        nr = Vector((math.sin(pol)*math.cos(az), math.sin(pol)*math.sin(az), math.cos(pol)))
        cc = c + Vector((nr.x*R*0.62, nr.y*R*0.62, nr.z*R*0.55*flat))
        clump(P, cc, R*0.48, 20, key, leafL, leafW, shape=shape, flat=0.85, inner_key=inner, seed=seed*31 + k, lobes=lobes,
              tint=(rnd.uniform(0.2, 0.8) if tint is None else tint), polar_max=125)

def build_Bushes(coll, row):
    ml = leaf_mat("PLN_Bush_Leaf", LEAF_GY, rim=0.35, tipcol=(0.32,0.45,0.10), tip_amt=0.25)
    ml2 = leaf_mat("PLN_Bush_BerryLeaf", LEAF_G, rim=0.3, spec=0.4)
    ms = leaf_mat("PLN_Bush_SageLeaf", [(0.10,0.13,0.10),(0.20,0.25,0.19),(0.32,0.38,0.30),(0.45,0.50,0.40)], vein=0.4, rim=0.3)
    mi = flat_col("PLN_Bush_Core", [(0.012,0.035,0.01),(0.03,0.06,0.02)], top=0.1)
    mb = bark_mat("PLN_Bush_Stem", BARK_BROWN, crack=0.3)
    mr = plant_mat("PLN_Bush_Berry", [(0.20,0.01,0.01),(0.42,0.03,0.025),(0.62,0.08,0.05)], scale=8, rough=0.3, spec=0.6, top=0.4, emit=0.05)
    ms_ = soil_mat("PLN_Bush_Soil")
    M = {"leaf": ml, "bl": ml2, "sage": ms, "core": mi, "stem": mb, "berry": mr}
    P = Plant("PLN_Bush_Round", 1.1, 0.7, seed=201)
    for k in range(6):
        a = k*1.05; tube(P, path(Vector((0, 0, 0)), Vector((math.cos(a)*0.4, math.sin(a)*0.4, 1)), 0.35, 4, wob=0.15, seed=k), [0.025, 0.02, 0.015, 0.01, 0.006], "stem", sides=5)
    bush_ball(P, (0, 0, 0.55), 0.62, "leaf", "core", 9, 0.2, 0.13, 201)
    mk(P, coll, M, row.place(1.4, 1.1), "shrub", ground=(0.55, ms_, None, 1, 0.025, 6, ms_))
    P = Plant("PLN_Bush_Berry", 1.4, 0.7, seed=202)
    tips = []
    for k in range(7):
        a = k*0.9; limb(P, Vector((0, 0, 0)), Vector((math.cos(a)*0.35, math.sin(a)*0.35, 1)), 0.85, 0.025, 0.008, "stem", 1, 400 + k, tips, kids=2, spread=35, wob=0.2, sides=5)
    rnd = random.Random(4)
    for i, (p, d, L) in enumerate(tips):
        clump(P, p, 0.24, 14, "bl", 0.17, 0.07, shape="lance", flat=1.0, inner_key=None, seed=420 + i, polar_max=140, fold=0.35, droop=0.15)
        if rnd.random() < 0.7:
            for b in range(rnd.randint(3, 6)):
                ball(P, p + Vector((rnd.uniform(-.06, .06), rnd.uniform(-.06, .06), rnd.uniform(-.12, -.02))), 0.022, "berry", sub=1)
    clump(P, Vector((0, 0, 0.85)), 0.42, 26, "bl", 0.2, 0.08, shape="lance", flat=0.95, inner_key="core", seed=440, polar_max=125)
    mk(P, coll, M, row.place(1.4, 1.4), "shrub", ground=(0.45, ms_, None, 2, 0.025, 6, ms_))
    P = Plant("PLN_Bush_Sage", 0.8, 0.9, seed=203)
    rnd = random.Random(7)
    for k in range(26):
        a = k*2.39996 + rnd.uniform(-.2, .2); el = rnd.uniform(0.55, 1.3)
        d = Vector((math.cos(a)*math.cos(el), math.sin(a)*math.cos(el), math.sin(el)))
        frond(P, Vector((0, 0, 0.02)), d, rnd.uniform(0.5, 0.85), "sage", W=0.14, lobes=9, depth=0.75, arch=0.3, droop=0.18, fold=0.3, tint=rnd.random(),
              cn=Vector((0, 0, -0.2)), cnw=0.5)
    mk(P, coll, M, row.place(1.8, 0.8), "shrub", ground=(0.5, ms_, 0.75, 3, 0.025, 8, ms_))

def build_Ferns(coll, row):
    mf = leaf_mat("PLN_Fern_Frond", [(0.03,0.10,0.015),(0.07,0.20,0.03),(0.14,0.33,0.05),(0.28,0.48,0.08)], vein=0.7, rim=0.25, tipcol=(0.30,0.50,0.08), tip_amt=0.3)
    mr = flat_col("PLN_Fern_Rachis", [(0.06,0.12,0.02),(0.14,0.24,0.05)])
    mm = soil_mat("PLN_Fern_MossMound", SOIL, moss=MOSS_P)
    M = {"frond": mf, "rachis": mr}
    for nm, H, L, n, seed in (("PLN_Ferns_Small", 0.35, 0.42, 9, 211), ("PLN_Ferns_Medium", 0.6, 0.65, 12, 212), ("PLN_Ferns_Large", 0.95, 0.95, 16, 213)):
        P = Plant(nm, H, L, seed=seed); rnd = random.Random(seed)
        for k in range(n):
            a = k*2.39996 + rnd.uniform(-.2, .2); el = rnd.uniform(0.35, 0.95)
            d = Vector((math.cos(a)*math.cos(el), math.sin(a)*math.cos(el), math.sin(el)))
            frond(P, Vector((0, 0, 0.04)), d, L*rnd.uniform(0.8, 1.1), "frond", W=L*0.36, lobes=13, depth=0.72, arch=0.15, droop=0.55, fold=0.35, rachis_key="rachis",
                  rr=0.006, tint=rnd.random(), cn=Vector((0, 0, -0.1)), cnw=0.5, ao=0.6 + 0.4*el)
        for k in range(2 if H < 0.5 else 3):
            a = k*2.3; fiddlehead(P, Vector((math.cos(a)*0.03, math.sin(a)*0.03, 0.04)), Vector((math.cos(a)*0.2, math.sin(a)*0.2, 1)), 0.03 + H*0.03, "rachis", r_tube=0.007)
        mk(P, coll, M, row.place(L*1.9, H), "fern", ground=(L*0.4, mm, None, seed, 0.05 + 0.05*H, 0, mm))

def build_Flowers(coll, row):
    ml = leaf_mat("PLN_Flower_Leaf", LEAF_G, rim=0.3)
    mst = flat_col("PLN_Flower_Stem", [(0.04,0.10,0.02),(0.09,0.18,0.04)])
    mw = leaf_mat("PLN_Flower_DaisyPetal", [(0.60,0.60,0.56),(0.82,0.82,0.78),(0.95,0.95,0.92)], vein=0.25, rim=0.0, ao_amt=0.35)
    my = flat_col("PLN_Flower_DaisyEye", [(0.60,0.35,0.01),(0.85,0.60,0.05),(0.95,0.78,0.15)], spec=0.2)
    mbell = leaf_mat("PLN_Flower_Bell", [(0.10,0.03,0.25),(0.22,0.08,0.50),(0.38,0.18,0.70)], vein=0.4, rim=0.2, ao_amt=0.4)
    mpk = leaf_mat("PLN_Flower_SpikePetal", [(0.30,0.02,0.10),(0.55,0.08,0.22),(0.80,0.25,0.42)], vein=0.4, rim=0.2, ao_amt=0.4)
    mwood = bark_mat("PLN_Flower_Planter", [(0.25,0.10,0.02),(0.42,0.20,0.05),(0.60,0.32,0.10),(0.72,0.45,0.16)], crack=0.4, stretch=(0.5, 6, 0.5))
    msoil = soil_mat("PLN_Flower_Soil")
    M = {"leaf": ml, "stem": mst, "white": mw, "eye": my, "bell": mbell, "pink": mpk, "wood": mwood, "soil": msoil}
    def rosette(P, c, n, L, W, seed, shape="lance"):
        rnd = random.Random(seed)
        for k in range(n):
            a = k*2.39996 + rnd.uniform(-.2, .2); d = Vector((math.cos(a), math.sin(a), rnd.uniform(0.25, 0.6)))
            leaf(P, Vector(c), d, UPZ, L*rnd.uniform(0.8, 1.1), W, "leaf", shape=shape, fold=0.35, droop=0.35, tint=rnd.random(), cn=Vector(c) - Vector((0, 0, 0.1)), cnw=0.4)
    def daisy(P, base, h, seed, s=1.0):
        rnd = random.Random(seed); lean = Vector((rnd.uniform(-.15, .15), rnd.uniform(-.15, .15), 1)).normalized()
        sp = [Vector(base) + lean*h*t + Vector((0.02*math.sin(t*3 + seed), 0, 0)) for t in [j/5 for j in range(6)]]
        tube(P, sp, [0.006*s]*5 + [0.005*s], "stem", sides=5, solid=False, flutter=lambda t: t*0.3)
        top = sp[-1]; nr = (sp[-1] - sp[-2]).normalized().lerp(Vector((0, -0.4, 1)).normalized(), 0.5).normalized()
        for j in range(14):
            a = j*2*math.pi/14; sd = nr.orthogonal().normalized(); s2 = nr.cross(sd)
            d = (sd*math.cos(a) + s2*math.sin(a) + nr*0.1).normalized()
            leaf(P, top, d, nr, 0.055*s, 0.016*s, "white", shape="petal", nu=1, nv=3, fold=0.2, curl=-0.1, bend=P.auto_bend(top), flut=0.3)
        ball(P, top + nr*0.005, 0.018*s, "eye", sub=1, squash=0.55)
    def bell_stem(P, base, h, n, seed):
        rnd = random.Random(seed); a = rnd.uniform(0, 6.28); dd = Vector((math.cos(a), math.sin(a), 0))
        sp = [Vector(base) + UPZ*h*math.sin(t*1.4)/math.sin(1.4) + dd*h*0.45*t*t for t in [j/8 for j in range(9)]]
        tube(P, sp, [0.007]*8 + [0.004], "stem", sides=5, solid=False)
        for k in range(n):
            t = 0.55 + 0.45*k/max(1, n - 1); p = sp[int(t*8)]
            q = p - UPZ*0.03 + dd*0.01
            tube(P, [p, q], [0.003, 0.003], "stem", sides=4, solid=False, cap=False)
            pr = [(0.004, 0.0), (0.02, -0.012), (0.03, -0.04), (0.036, -0.07), (0.045, -0.085), (0.04, -0.09)]
            lathe(P, pr, "bell", sides=10, center=q, ribs=(5, 0.18), solid=False)
    def spike(P, base, h, seed):
        rnd = random.Random(seed); lean = Vector((rnd.uniform(-.1, .1), rnd.uniform(-.1, .1), 1)).normalized()
        sp = [Vector(base) + lean*h*t for t in [j/6 for j in range(7)]]
        tube(P, sp, [0.009]*6 + [0.004], "stem", sides=5, solid=False)
        for k in range(16):
            t = 0.45 + 0.55*k/16; p = Vector(base) + lean*h*t; a = k*2.39996; sz = 0.06*(1 - 0.6*(t - 0.45)/0.55)
            nr = Vector((math.cos(a), math.sin(a), 0.6)).normalized()
            for j in range(5):
                aa = j*1.2566; sd = nr.orthogonal().normalized(); s2 = nr.cross(sd)
                leaf(P, p, (nr*0.8 + (sd*math.cos(aa) + s2*math.sin(aa))*0.7).normalized(), nr, sz*0.7, sz*0.5, "pink", shape="petal", nu=1, nv=3, fold=0.4, curl=0.3, bend=P.auto_bend(p), flut=0.25)
    P = Plant("PLN_Flowers_Daisy", 0.4, 0.3, seed=221); rosette(P, (0, 0, 0.01), 12, 0.15, 0.05, 1, "ovate")
    for k in range(7):
        a = k*2.4; daisy(P, Vector((math.cos(a)*0.06, math.sin(a)*0.06, 0)), 0.18 + 0.12*((k*5) % 4)/3, k)
    mk(P, coll, M, row.place(0.6, 0.4), "flower", outline=False)
    P = Plant("PLN_Flowers_Bellflower", 0.55, 0.3, seed=222); rosette(P, (0, 0, 0.01), 9, 0.2, 0.08, 2, "ovate")
    for k in range(4): bell_stem(P, Vector((0.03*math.cos(k*1.6), 0.03*math.sin(k*1.6), 0)), 0.42 + 0.08*(k % 2), 3, 30 + k)
    mk(P, coll, M, row.place(0.6, 0.55), "flower", outline=False)
    P = Plant("PLN_Flowers_Spike", 0.8, 0.3, seed=223); rnd = random.Random(3)
    for k in range(10):
        a = k*2.39996; leaf(P, Vector((0, 0, 0)), Vector((math.cos(a)*0.35, math.sin(a)*0.35, 1)), UPZ, rnd.uniform(0.3, 0.45), 0.035, "leaf", shape="blade", fold=0.3, droop=0.2)
    for k in range(3): spike(P, Vector((0.04*math.cos(k*2.1), 0.04*math.sin(k*2.1), 0)), 0.62 + 0.12*(k % 2), 40 + k)
    mk(P, coll, M, row.place(0.6, 0.8), "flower", outline=False)
    # planter bed with mixed flowers
    P = Plant("PLN_Flowers_Bed", 0.55, 0.7, seed=224)
    BX, BY, BH, T = 0.6, 0.32, 0.2, 0.045
    for (cx, cy, sx, sy) in ((0, BY - T/2, BX, T/2), (0, -BY + T/2, BX, T/2), (BX - T/2, 0, T/2, BY), (-BX + T/2, 0, T/2, BY)):
        vs = [P.v((cx + dx*sx, cy + dy*sy, dz*BH), bend=0.0) for dz in (0, 1) for dy in (-1, 1) for dx in (-1, 1)]
        for q in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)): P.face([vs[i] for i in q], "wood", True)
    sv = [P.v((dx*(BX - T), dy*(BY - T), BH - 0.035 + 0.01*noise.noise(Vector((dx*3, dy*3, 0)))), bend=0.0) for dy in (-1, 1) for dx in (-1, 1)]
    P.face((sv[0], sv[1], sv[3], sv[2]), "soil")
    for k in range(5): daisy(P, Vector((-0.42 + 0.07*k, -0.12 + 0.05*(k % 3), BH - 0.03)), 0.12 + 0.03*(k % 2), 60 + k, 0.8)
    for k in range(3): bell_stem(P, Vector((-0.05 + 0.08*k, 0.05*(k % 2), BH - 0.03)), 0.25, 2, 70 + k)
    for k in range(3): spike(P, Vector((0.25 + 0.09*k, 0.06 - 0.06*(k % 2), BH - 0.03)), 0.42, 80 + k)
    for k in range(4): rosette(P, (-0.4 + 0.27*k, 0.1*(k % 2) - 0.05, BH - 0.03), 6, 0.09, 0.035, 90 + k, "ovate")
    mk(P, coll, M, row.place(1.4, 0.7), "flower")

def build_GrassPatches(coll, row):
    G1 = blade_mat("PLN_Grass_Short", (0.06,0.18,0.01), (0.40,0.75,0.08), (0.25,0.55,0.05), 1.0)
    G2 = blade_mat("PLN_Grass_Tall", (0.03,0.10,0.015), (0.22,0.38,0.08), (0.14,0.28,0.05), 1.0)
    G3 = blade_mat("PLN_Grass_Dry", (0.25,0.15,0.04), (0.75,0.55,0.25), (0.60,0.42,0.16), 1.0)
    G4 = blade_mat("PLN_Grass_Clover", (0.02,0.08,0.015), (0.10,0.30,0.05), (0.06,0.20,0.03), 1.0)
    for m in (G1, G2, G3, G4): m.use_backface_culling = False
    mcl = leaf_mat("PLN_Grass_CloverLeaf", [(0.02,0.08,0.02),(0.04,0.16,0.04),(0.08,0.26,0.07),(0.14,0.34,0.10)], vein=0.4, rim=0.4, rim_col=(0.3,0.5,0.25))
    mfl = leaf_mat("PLN_Grass_CloverFlower", [(0.35,0.10,0.25),(0.60,0.28,0.45),(0.85,0.55,0.70)], vein=0.0, rim=0.2, ao_amt=0.3)
    mst = flat_col("PLN_Grass_Stem", [(0.04,0.10,0.02),(0.09,0.18,0.04)])
    sg = soil_mat("PLN_Grass_SoilGreen", SOIL, moss=[(0.10,0.25,0.03),(0.18,0.38,0.05),(0.28,0.50,0.08)])
    sd = soil_mat("PLN_Grass_SoilDry", [(0.15,0.10,0.05),(0.25,0.17,0.09),(0.36,0.27,0.15)])
    sw = soil_mat("PLN_Grass_SoilWet", [(0.015,0.02,0.012),(0.03,0.04,0.025),(0.05,0.06,0.04)], moss=MOSS_P)
    M = {"g1": G1, "g2": G2, "g3": G3, "g4": G4, "cl": mcl, "fl": mfl, "st": mst}
    def patch(P, key, n, R, hmin, hmax, W, lean, seed, curl=0.0):
        rnd = random.Random(seed)
        for k in range(n):
            r = R*math.sqrt(rnd.random()); a = rnd.uniform(0, 6.28); h = rnd.uniform(hmin, hmax)*(1 - 0.35*r/R)
            blade(P, (r*math.cos(a), r*math.sin(a), 0.0), h, W, a + rnd.uniform(-.8, .8), rnd.uniform(*lean), key, segs=4, tint=rnd.random(), curl=curl, twist=rnd.uniform(-.6, .6))
    P = Plant("PLN_Grass_ShortLush", 0.14, 0.3, seed=231); patch(P, "g1", 150, 0.22, 0.07, 0.15, 0.022, (0.15, 0.5), 1)
    mk(P, coll, M, row.place(0.6, 0.2), "grass", outline=False, ground=(0.26, sg, None, 1, 0.03, 4, sg))
    P = Plant("PLN_Grass_Tall", 0.7, 0.3, seed=232); patch(P, "g2", 70, 0.18, 0.35, 0.7, 0.03, (0.2, 0.75), 2, curl=0.4)
    mk(P, coll, M, row.place(0.7, 0.7), "grass", outline=False, ground=(0.24, sd, None, 2, 0.03, 4, sd))
    P = Plant("PLN_Grass_Dry", 0.5, 0.3, seed=233); patch(P, "g3", 75, 0.2, 0.2, 0.48, 0.026, (0.3, 1.0), 3, curl=0.6)
    mk(P, coll, M, row.place(0.65, 0.5), "grass", outline=False, ground=(0.24, sd, None, 3, 0.03, 6, sd))
    P = Plant("PLN_Grass_Clover", 0.45, 0.3, seed=234); patch(P, "g4", 40, 0.2, 0.2, 0.42, 0.022, (0.1, 0.5), 4)
    rnd = random.Random(8)
    for k in range(16):
        r = 0.2*math.sqrt(rnd.random()); a = rnd.uniform(0, 6.28); h = rnd.uniform(0.06, 0.16); base = Vector((r*math.cos(a), r*math.sin(a), 0))
        top = base + Vector((0.01, 0, h)); tube(P, [base, top], [0.004, 0.003], "st", sides=4, solid=False)
        for j in range(3):
            aa = j*2.094 + a; leaf(P, top, Vector((math.cos(aa), math.sin(aa), 0.15)), UPZ, 0.045, 0.042, "cl", shape="clover", nu=2, nv=4, fold=0.15, flut=0.6)
    for k in range(4):
        a = k*1.6 + 0.3; base = Vector((0.1*math.cos(a), 0.1*math.sin(a), 0)); h = 0.25 + 0.05*k % 0.1
        top = base + Vector((0.01, 0, h)); tube(P, [base, base + Vector((0, 0, h*0.5)), top], [0.004, 0.004, 0.003], "st", sides=4, solid=False)
        for j in range(36):   # clover head of little florets
            u = (j + 0.5)/36; th = math.acos(1 - 2*u); ph_ = j*2.39996; nr = Vector((math.sin(th)*math.cos(ph_), math.sin(th)*math.sin(ph_), math.cos(th)))
            leaf(P, top + nr*0.012, nr, nr.orthogonal(), 0.022, 0.008, "fl", shape="petal", nu=1, nv=2, fold=0.3, flut=0.2)
    mk(P, coll, M, row.place(0.65, 0.45), "grass", outline=False, ground=(0.25, sw, None, 4, 0.03, 0, sw))

def build_Hedges(coll, row):
    mh = leaf_mat("PLN_Hedge_Leaf", [(0.015,0.05,0.012),(0.035,0.10,0.025),(0.07,0.18,0.04),(0.13,0.27,0.06)], rim=0.35, scale=6)
    mb = flat_col("PLN_Hedge_Body", [(0.008,0.03,0.008),(0.02,0.06,0.015),(0.04,0.10,0.025)], top=0.4, ao_amt=0.6)
    mw = bark_mat("PLN_Hedge_BasePlank", [(0.04,0.025,0.015),(0.08,0.05,0.03),(0.12,0.08,0.05),(0.16,0.11,0.07)], crack=0.3, stretch=(0.5, 5, 0.5))
    M = {"leaf": mh, "body": mb, "plank": mw}
    def hedge_body(P, segs, H, Wd, rounded_end=False):
        """segs: list of (x0,y0,x1,y1) centre lines; box body with rounded top edges + leaf cover"""
        rnd = random.Random(len(segs)*7 + int(rounded_end))
        for (x0, y0, x1, y1) in segs:
            dx, dy = x1 - x0, y1 - y0; Ls = math.hypot(dx, dy); ux, uy = dx/Ls, dy/Ls; nx, ny = -uy, ux
            NU, NV = max(6, int(Ls*14)), 12; prof = []
            for j in range(NV + 1):   # profile around: left side up, top, right side down
                s = j/NV; a = math.pi*s
                if s < 0.2: px, pz = -Wd/2, H*(s/0.2)*0.85
                elif s > 0.8: px, pz = Wd/2, H*((1 - s)/0.2)*0.85
                else:
                    q = (s - 0.2)/0.6; px = -Wd/2*math.cos(math.pi*q); pz = H*0.85 + H*0.15*math.sin(math.pi*q)
                prof.append((px, pz))
            grid = []
            for i in range(NU + 1):
                t = i/NU; cx, cy = x0 + dx*t, y0 + dy*t
                end_k = 1.0
                if rounded_end and t > 0.75: end_k = math.sqrt(max(0.0, 1 - ((t - 0.75)/0.25)**2))
                rowv = []
                for (px, pz) in prof:
                    nz_ = 1 + 0.06*noise.noise(Vector((cx*3, cy*3, pz*3)))
                    zz = pz*(end_k**0.35 if rounded_end else 1.0)
                    rowv.append(P.v((cx + nx*px*nz_, cy + ny*px*nz_, max(0.08, zz*nz_) if pz > 0.01 else 0.08), bend=min(1.0, pz/H), ao=0.6 + 0.4*pz/H))
                grid.append(rowv)
            for i in range(NU):
                for j in range(NV): P.face((grid[i][j], grid[i+1][j], grid[i+1][j+1], grid[i][j+1]), "body", True)
            for k in range(int(Ls*320)):   # leaf cover
                t = rnd.random(); s = rnd.uniform(0.02, 0.98); j = s*NV; j0 = min(NV - 1, int(j)); fj = j - j0
                px = prof[j0][0]*(1 - fj) + prof[j0+1][0]*fj; pz = prof[j0][1]*(1 - fj) + prof[j0+1][1]*fj; cx, cy = x0 + dx*t, y0 + dy*t
                if rounded_end and t > 0.75: pz *= math.sqrt(max(0.0, 1 - ((t - 0.75)/0.25)**2))**0.35
                if pz < 0.1: continue
                outn = Vector((nx*math.copysign(1, px) if abs(px) > Wd*0.3 else 0, ny*math.copysign(1, px) if abs(px) > Wd*0.3 else 0, 1 if pz > H*0.8 else 0.25)).normalized()
                base = Vector((cx + nx*px, cy + ny*px, pz)) + outn*0.01
                d = (outn.orthogonal()*rnd.uniform(-1, 1) + outn.cross(outn.orthogonal())*rnd.uniform(-1, 1) + outn*0.4).normalized()
                leaf(P, base, d, outn, 0.085, 0.05, "leaf", fold=0.25, droop=0.0, tint=rnd.random(), ao=0.55 + 0.45*pz/H, bend=min(1.0, pz/H), cn=base - outn*0.2, cnw=0.4, nv=3, nu=1, flut=0.8)
            # base plank
            vs = [P.v((x0 + ux*e*0.0 + dx*(1 if e else 0)*1.0 + nx*w*(Wd/2 + 0.06) + ux*(0.06 if e else -0.06),
                       y0 + dy*(1 if e else 0) + ny*w*(Wd/2 + 0.06) + uy*(0.06 if e else -0.06), z), bend=0.0)
                  for z in (0.0, 0.07) for w in (-1, 1) for e in (0, 1)]
            for q in ((0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)): P.face([vs[i] for i in q], "plank", True)
    P = Plant("PLN_Hedge_Straight", 0.9, 1.0, seed=241); hedge_body(P, [(-1.0, 0, 1.0, 0)], 0.9, 0.62)
    mk(P, coll, M, row.place(2.2, 0.95), "hedge")
    P = Plant("PLN_Hedge_Corner", 0.9, 1.0, seed=242); hedge_body(P, [(-1.0, -0.69, 0.69, -0.69), (0.69, -0.69, 0.69, 1.0)], 0.9, 0.62)
    mk(P, coll, M, row.place(2.2, 0.95), "hedge")
    P = Plant("PLN_Hedge_End", 0.9, 1.0, seed=243); hedge_body(P, [(-1.0, 0, 1.0, 0)], 0.9, 0.62, rounded_end=True)
    mk(P, coll, M, row.place(2.2, 0.95), "hedge")

def build_Horsetails(coll, row):
    ms = plant_mat("PLN_Horsetail_Stem", [(0.03,0.10,0.02),(0.06,0.18,0.035),(0.11,0.26,0.05)], scale=3, stretch=(4, 4, 0.5), strokes=0.3, top=0.3, emit=0.03)
    mn = flat_col("PLN_Horsetail_Node", [(0.30,0.20,0.06),(0.55,0.40,0.14)])
    mw = leaf_mat("PLN_Horsetail_Whorl", [(0.03,0.10,0.02),(0.07,0.20,0.04),(0.14,0.30,0.06)], vein=0.0, rim=0.2)
    mc = plant_mat("PLN_Horsetail_Cone", [(0.12,0.06,0.02),(0.28,0.16,0.06),(0.45,0.28,0.12)], scale=9, edge=(0.7,0.5,0.25), edge_amt=0.6, geo_ao=0.5)
    mm = soil_mat("PLN_Horsetail_Mud", [(0.015,0.012,0.008),(0.03,0.024,0.016),(0.05,0.04,0.026)], moss=MOSS_P)
    M = {"stem": ms, "node": mn, "wh": mw, "cone": mc}
    for nm, H, n, R, cones, seed in (("PLN_Horsetails_Small", 0.7, 16, 0.18, 0, 251), ("PLN_Horsetails_Large", 1.55, 18, 0.38, 6, 252)):
        P = Plant(nm, H, R, seed=seed); rnd = random.Random(seed)
        for k in range(n):
            r = R*math.sqrt(rnd.random()); a = rnd.uniform(0, 6.28); h = H*rnd.uniform(0.6, 1.0)
            base = Vector((r*math.cos(a), r*math.sin(a), 0)); lean = Vector((math.cos(a)*0.12*r/R, math.sin(a)*0.12*r/R, 1)).normalized()
            nseg = max(4, int(h/(0.11 if H < 1 else 0.17))); sr = 0.008 if H < 1 else 0.016
            pts = [base + lean*h*j/nseg for j in range(nseg + 1)]
            tube(P, pts, [sr]*nseg + [sr*0.6], "stem", sides=7, solid=False, bend=lambda t: t**1.5)
            for j in range(1, nseg):
                p = pts[j]; tube(P, [p - lean*0.006, p + lean*0.006], [sr*1.25, sr*1.25], "node", sides=7, solid=False, cap=False, bend=(j/nseg)**1.5)
                if j < nseg - (1 if cones and k < cones else 0):
                    for q in range(9 if H > 1 else 7):
                        aa = q*2*math.pi/(9 if H > 1 else 7) + j*0.4; d = Vector((math.cos(aa), math.sin(aa), 0.25 - 0.3*(j/nseg)))
                        blade(P, p, 0.0, 0, 0, 0, "wh") if False else leaf(P, p, d, UPZ, (0.07 if H < 1 else 0.16)*(1 - 0.5*j/nseg), 0.006 if H < 1 else 0.009, "wh",
                                                                            shape="blade", nu=1, nv=3, fold=0.0, droop=0.35, bend=(j/nseg)**1.5, flut=0.7)
            if cones and k < cones:
                lathe(P, [(0.001, 0), (sr*1.6, 0.02), (sr*2.2, 0.06), (sr*2.0, 0.1), (sr*1.2, 0.13), (0.001, 0.15)], "cone", sides=9, center=pts[-1], ribs=(9, 0.2), solid=False, bend=1.0)
        mk(P, coll, M, row.place(R*2.8 + 0.4, H), "reed", outline=False, ground=(R*1.25, mm, None, seed, 0.04, 6, mm), motion_scale=0.6)

def build_DesertPlants(coll, row):
    mc = plant_mat("PLN_Desert_Cactus", [(0.04,0.12,0.04),(0.08,0.22,0.07),(0.15,0.33,0.12),(0.25,0.42,0.18)], scale=3, stretch=(6, 6, 0.6), strokes=0.35,
                   edge=(0.45,0.60,0.35), edge_amt=0.7, geo_ao=0.5, top=0.35, rough=0.6, emit=0.02)
    mb = plant_mat("PLN_Desert_Barrel", [(0.06,0.14,0.08),(0.12,0.25,0.15),(0.22,0.36,0.24),(0.32,0.46,0.33)], scale=3, stretch=(5, 5, 1), strokes=0.3,
                   edge=(0.5,0.62,0.48), edge_amt=0.7, geo_ao=0.5, top=0.35, rough=0.6)
    mf = leaf_mat("PLN_Desert_Flower", [(0.35,0.04,0.18),(0.62,0.15,0.38),(0.85,0.40,0.60)], vein=0.3, rim=0.2, ao_amt=0.3)
    mtw = bark_mat("PLN_Desert_Twig", [(0.10,0.10,0.09),(0.18,0.18,0.16),(0.28,0.28,0.25),(0.38,0.38,0.34)], crack=0.3)
    ml = leaf_mat("PLN_Desert_ShrubLeaf", [(0.08,0.11,0.08),(0.17,0.22,0.16),(0.28,0.33,0.26),(0.40,0.44,0.36)], vein=0.2, rim=0.3)
    msd = soil_mat("PLN_Desert_Sand", SAND)
    M = {"cac": mc, "bar": mb, "fl": mf, "tw": mtw, "lf": ml}
    P = Plant("PLN_Desert_Saguaro", 2.3, 0.6, seed=261)
    prof = [(0.17, 0.0), (0.19, 0.08)] + [(0.2 - 0.02*t, 2.1*t) for t in [j/10 for j in range(2, 11)]] + [(0.13, 2.18), (0.06, 2.25), (0.001, 2.27)]
    lathe(P, prof, "cac", sides=24, ribs=(12, 0.12), solid=True, bend=0.0)
    for s, (z0, out, up) in ((-1, (0.75, 0.42, 0.95)), (1, (1.05, 0.36, 0.7))):
        p0 = Vector((0, 0, z0)); pts = [p0]
        for j in range(1, 12):
            t = j/11
            if t < 0.35: pts.append(p0 + Vector((s*out*t/0.35, 0, 0.08*t/0.35)))
            else: pts.append(p0 + Vector((s*out, 0, 0.08 + up*(t - 0.35)/0.65)) + Vector((-s*0.06*math.sin((t - 0.35)*3), 0, 0)))
        sm = [pts[0]] + [pts[i - 1].lerp(pts[i], 0.5) for i in range(1, len(pts))] + [pts[-1]]
        tube(P, sm, [0.11]*(len(sm) - 1) + [0.09], "cac", sides=18, ribs=(10, 0.12), bend=0.0)
    mk(P, coll, M, row.place(1.4, 2.3), None, ground=(0.35, msd, None, 1, 0.02, 4, msd))
    P = Plant("PLN_Desert_Barrel", 0.75, 0.4, seed=262)
    prof = [(0.25, 0.0), (0.33, 0.1), (0.37, 0.25), (0.36, 0.42), (0.30, 0.56), (0.20, 0.64), (0.06, 0.67), (0.001, 0.67)]
    lathe(P, prof, "bar", sides=28, ribs=(14, 0.11), solid=True, bend=0.0)
    for k in range(7):
        a = k*0.9; c = Vector((math.cos(a)*0.08, math.sin(a)*0.08, 0.66))
        for j in range(8):
            aa = j*0.785; d = Vector((math.cos(aa), math.sin(aa), 0.9))
            leaf(P, c, d, d.orthogonal(), 0.06, 0.025, "fl", shape="petal", nu=1, nv=3, fold=0.4, curl=0.3, bend=0.1, flut=0.3)
    mk(P, coll, M, row.place(0.95, 0.75), "flower", motion_scale=0.2, ground=(0.45, msd, None, 2, 0.02, 4, msd))
    P = Plant("PLN_Desert_Shrub", 0.9, 0.8, seed=263); tips = []
    for k in range(9):
        a = k*0.7; limb(P, Vector((0, 0, 0)), Vector((math.cos(a)*0.7, math.sin(a)*0.7, 0.8)), 0.6, 0.018, 0.006, "tw", 2, 500 + k, tips, kids=2, spread=40, wob=0.3, sides=5, kid_len=0.6)
    for i, (p, d, L) in enumerate(tips):
        if i % 2 == 0: clump(P, p, 0.08, 5, "lf", 0.065, 0.032, shape="ovate", flat=1.0, polar_max=150, seed=520 + i, fold=0.3)
    mk(P, coll, M, row.place(1.6, 0.9), "shrub", ground=(0.5, msd, 0.7, 3, 0.02, 6, msd))

def build_StumpsLogs(coll, row):
    mb = bark_mat("PLN_Log_Bark", [(0.05,0.03,0.015),(0.11,0.07,0.035),(0.19,0.12,0.06),(0.28,0.19,0.10)], crack=0.85, crack_scale=4.0, stretch=(5, 5, 0.5),
                  moss=MOSS_P, moss_amt=0.25)
    mb2 = bark_mat("PLN_Log_BarkOrange", [(0.18,0.07,0.02),(0.32,0.15,0.05),(0.46,0.25,0.09),(0.58,0.35,0.14)], crack=0.7, crack_scale=4.5, stretch=(5, 5, 0.5))
    mmossy = bark_mat("PLN_Log_BarkMossy", [(0.05,0.03,0.015),(0.11,0.07,0.035),(0.19,0.12,0.06),(0.28,0.19,0.10)], crack=0.7, moss=MOSS_P, moss_amt=0.9)
    # end grain: rings from LeafUV radius
    m, nt, bs = new_mat("PLN_Log_EndGrain"); uv = uvmap(nt, "LeafUV"); r = vlen(nt, vmul(nt, uv, (1, 1, 0)))
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = 'RINGS'; wv.inputs["Scale"].default_value = 3.0; wv.inputs["Distortion"].default_value = 3.0
    nt.links.new(vmul(nt, uv, (0.5, 0.5, 0)), wv.inputs["Vector"])
    rp = ramp(nt, [(0.35,0.17,0.06),(0.58,0.34,0.14),(0.72,0.48,0.24)]); nt.links.new(wv.outputs["Fac"], rp.inputs[0])
    col = mix(nt, rp.outputs[0], (0.25,0.12,0.05), maprange(nt, r, 0.82, 1.0))
    col = mix(nt, col, (0.20,0.09,0.03), maprange(nt, r, 0.12, 0.0))
    nt.links.new(col, bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.85
    mh = flat_col("PLN_Log_Hollow", [(0.02,0.012,0.006),(0.06,0.035,0.015)], top=0.0)
    mmo = plant_mat("PLN_Log_MossCap", [(0.05,0.13,0.015),(0.12,0.25,0.03),(0.22,0.38,0.06)], scale=9, strokes=0.4, top=0.4)
    M = {"bark": mb, "orange": mb2, "mossy": mmossy, "end": m, "hollow": mh, "moss": mmo}
    def cap(P, center, axis, R, key, sides=16, ring_v=None):
        """flat end-grain disc with polar LeafUV"""
        ax = Vector(axis).normalized(); a1 = ax.orthogonal().normalized(); a2 = ax.cross(a1)
        c = P.v(center, bend=0.0); ring = []
        for k in range(sides):
            a = 2*math.pi*k/sides; ring.append(P.v(Vector(center) + (a1*math.cos(a) + a2*math.sin(a))*R*(1 + 0.04*noise.noise(Vector((math.cos(a)*2, math.sin(a)*2, 0)))), bend=0.0))
        for k in range(sides):
            q = (k+1) % sides; a, b_ = 2*math.pi*k/sides, 2*math.pi*q/sides
            P.face((c, ring[k], ring[q]), key, True, [(0, 0), (math.cos(a), math.sin(a)), (math.cos(b_), math.sin(b_))])
    def roots(P, n, R, h, key, seed):
        rnd = random.Random(seed)
        for k in range(n):
            a = k*2*math.pi/n + rnd.uniform(-.3, .3)
            pts = [Vector((math.cos(a)*R*0.6, math.sin(a)*R*0.6, h)), Vector((math.cos(a)*R*1.05, math.sin(a)*R*1.05, h*0.35)), Vector((math.cos(a)*R*1.5, math.sin(a)*R*1.5, 0.02))]
            tube(P, pts, [R*0.35, R*0.25, R*0.1], key, sides=7, bend=0.0, rough=0.1)
    P = Plant("PLN_Stump_Short", 0.5, 0.4, seed=271)
    tube(P, [Vector((0, 0, 0)), Vector((0, 0, 0.2)), Vector((0, 0, 0.4))], [0.30, 0.27, 0.26], "orange", sides=18, cap=False, rough=0.06, lobes=(5, 0.4, 0.25), bend=0.0)
    roots(P, 5, 0.28, 0.18, "orange", 1); cap(P, (0, 0, 0.4), (0, 0, 1), 0.255, "end")
    mk(P, coll, M, row.place(1.0, 0.5), None)
    P = Plant("PLN_Stump_TallBroken", 1.2, 0.5, seed=272)
    prof_top = lambda a: 0.75 + 0.35*abs(math.sin(a*2.5)) + 0.1*math.sin(a*7)
    sides = 18; rings_ = []
    for j, (z, rr_) in enumerate(((0, 0.33), (0.25, 0.28), (0.5, 0.26), (0.7, 0.25))):
        rings_.append([P.v((rr_*math.cos(2*math.pi*k/sides)*(1 + 0.06*noise.noise(Vector((k, z*5, 0)))), rr_*math.sin(2*math.pi*k/sides)*(1 + 0.06*noise.noise(Vector((k, z*5, 0)))),
                            z if j < 3 else prof_top(2*math.pi*k/sides)), bend=0.0) for k in range(sides)])
    for j in range(3):
        for k in range(sides): P.face((rings_[j][k], rings_[j][(k+1) % sides], rings_[j+1][(k+1) % sides], rings_[j+1][k]), "mossy", True)
    inner = [P.v((0.2*math.cos(2*math.pi*k/sides), 0.2*math.sin(2*math.pi*k/sides), prof_top(2*math.pi*k/sides) - 0.06), bend=0.0) for k in range(sides)]
    for k in range(sides):
        q = (k+1) % sides; a, b_ = 2*math.pi*k/sides, 2*math.pi*q/sides
        P.face((rings_[3][k], rings_[3][q], inner[q], inner[k]), "end", True, [(math.cos(a), math.sin(a)), (math.cos(b_), math.sin(b_)), (0.75*math.cos(b_), 0.75*math.sin(b_)), (0.75*math.cos(a), 0.75*math.sin(a))])
    cap(P, (0, 0, 0.62), (0, 0, 1), 0.205, "end")
    roots(P, 5, 0.32, 0.2, "mossy", 2)
    mk(P, coll, M, row.place(1.1, 1.2), None)
    def log(P, L, R, key, hollow=False, seed=0, z=None):
        z = R*0.92 if z is None else z
        pts = [Vector((-L/2 + L*j/8, 0, z + 0.02*noise.noise(Vector((j*0.4, seed, 0))))) for j in range(9)]
        tube(P, pts, [R*(1 + 0.05*noise.noise(Vector((j, seed, 1)))) for j in range(9)], key, sides=18, cap=False, rough=0.05, seed=seed, bend=0.0)
        if hollow:
            tube(P, list(reversed(pts)), [R*0.78]*9, "hollow", sides=18, cap=False, solid=False, bend=0.0)
            for e, ax in ((pts[0], (-1, 0, 0)), (pts[-1], (1, 0, 0))):
                axv = Vector(ax); a1 = axv.orthogonal().normalized(); a2 = axv.cross(a1)
                o = [P.v(e + (a1*math.cos(2*math.pi*k/18) + a2*math.sin(2*math.pi*k/18))*R, bend=0.0) for k in range(18)]
                i_ = [P.v(e + (a1*math.cos(2*math.pi*k/18) + a2*math.sin(2*math.pi*k/18))*R*0.78, bend=0.0) for k in range(18)]
                for k in range(18):
                    q = (k+1) % 18; a, b_ = 2*math.pi*k/18, 2*math.pi*q/18
                    vs = (o[k], o[q], i_[q], i_[k]) if ax[0] > 0 else (o[q], o[k], i_[k], i_[q])
                    P.face(vs, "end", True, [(math.cos(a), math.sin(a)), (math.cos(b_), math.sin(b_)), (0.8*math.cos(b_), 0.8*math.sin(b_)), (0.8*math.cos(a), 0.8*math.sin(a))])
        else:
            cap(P, pts[0], (-1, 0, 0), R*1.0, "end"); cap(P, pts[-1], (1, 0, 0), R*1.0, "end")
        return pts
    P = Plant("PLN_Log_Cut", 0.6, 1.0, seed=273); log(P, 1.5, 0.27, "orange", seed=3)
    mk(P, coll, M, row.place(1.7, 0.6), None)
    P = Plant("PLN_Log_Hollow", 0.7, 1.0, seed=274); pts = log(P, 1.9, 0.32, "bark", hollow=True, seed=4)
    ball(P, Vector((0.25, -0.30, 0.42)), 0.13, "hollow", sub=2, squash=0.7, bend=0.0)   # side hole
    mk(P, coll, M, row.place(2.1, 0.7), None)
    P = Plant("PLN_Log_Mossy", 0.6, 1.0, seed=275); pts = log(P, 1.8, 0.28, "mossy", hollow=True, seed=5)
    tube(P, [Vector((0.2, 0, 0.45)), Vector((0.28, 0.02, 0.75)), Vector((0.3, 0.03, 0.88))], [0.07, 0.05, 0.03], "bark", sides=8, bend=0.0, rough=0.15)
    rnd = random.Random(5)
    for k in range(26):
        x = rnd.uniform(-0.8, 0.8); a = rnd.uniform(-1.1, 1.1); p = Vector((x, math.sin(a)*0.285, 0.258 + math.cos(a)*0.285))
        ball(P, p, rnd.uniform(0.05, 0.1), "moss", sub=2, squash=0.35, bend=0.0, noise_amp=0.25, seed=k)
    mk(P, coll, M, row.place(2.0, 0.9), None)

# ================================================================== WATER & SEA
def build_ReedsCattails(coll, row):
    G = blade_mat("PLN_Reed_Blade", (0.03,0.09,0.015), (0.20,0.36,0.08), (0.14,0.26,0.05), 1.0)
    GD = blade_mat("PLN_Reed_DryBlade", (0.18,0.12,0.03), (0.62,0.46,0.18), (0.48,0.34,0.12), 1.0)
    for m in (G, GD): m.use_backface_culling = False
    mh = plant_mat("PLN_Reed_CattailHead", [(0.06,0.025,0.01),(0.14,0.06,0.02),(0.24,0.12,0.05)], scale=12, stretch=(1, 1, 3), top=0.35, geo_ao=0.3, rough=0.9)
    ms = flat_col("PLN_Reed_Stalk", [(0.10,0.12,0.03),(0.20,0.22,0.06)])
    mm = soil_mat("PLN_Reed_Mud", [(0.02,0.018,0.012),(0.04,0.034,0.022),(0.065,0.055,0.038)])
    M = {"g": G, "dry": GD, "head": mh, "st": ms}
    P = Plant("PLN_Reeds", 1.5, 0.4, seed=281); rnd = random.Random(1)
    for k in range(70):
        r = 0.3*math.sqrt(rnd.random()); a = rnd.uniform(0, 6.28)
        blade(P, (r*math.cos(a), r*math.sin(a), 0), rnd.uniform(0.7, 1.45), 0.035, a + rnd.uniform(-.6, .6), rnd.uniform(0.05, 0.55), "g", segs=6, tint=rnd.random(), curl=0.3, twist=rnd.uniform(-.4, .4))
    mk(P, coll, M, row.place(1.2, 1.5), "reed", outline=False, ground=(0.4, mm, None, 1, 0.03, 0, mm))
    P = Plant("PLN_Cattails", 1.6, 0.4, seed=282); rnd = random.Random(2)
    for k in range(46):
        r = 0.28*math.sqrt(rnd.random()); a = rnd.uniform(0, 6.28); dry = rnd.random() < 0.25
        blade(P, (r*math.cos(a), r*math.sin(a), 0), rnd.uniform(0.6, 1.25)*(0.7 if dry else 1), 0.04, a + rnd.uniform(-.6, .6), rnd.uniform(0.15, 0.9 if dry else 0.6),
              "dry" if dry else "g", segs=6, tint=rnd.random(), curl=0.3)
    for k in range(7):
        a = k*0.9 + 0.3; r = 0.12*rnd.random(); h = rnd.uniform(1.15, 1.55); base = Vector((r*math.cos(a), r*math.sin(a), 0))
        lean = Vector((math.cos(a)*0.06, math.sin(a)*0.06, 1)).normalized()
        pts = [base + lean*h*j/8 for j in range(9)]
        tube(P, pts, [0.007]*8 + [0.004], "st", sides=5, solid=False, bend=lambda t: t**1.6)
        hb = base + lean*(h - 0.32)
        lathe(P, [(0.001, 0), (0.026, 0.015), (0.032, 0.05), (0.033, 0.18), (0.028, 0.22), (0.008, 0.235), (0.001, 0.24)], "head", sides=10, center=hb, solid=False,
              bend=((h - 0.2)/1.6)**1.6, axis=lean)
    mk(P, coll, M, row.place(1.2, 1.6), "reed", outline=False, ground=(0.4, mm, None, 2, 0.03, 0, mm))

def ribbon(P, base, d, L, W, key, segs=14, wave=0.35, wave_n=3.0, ruffle=0.25, twist=0.6, droop=0.0, seed=0, tint=0.5, bend_scale=1.0):
    """long wavy seaweed / kelp blade. bend grows along its own length (so the current travels up the blade)"""
    rnd = random.Random(seed); d = Vector(d).normalized(); side = d.cross(UPZ)
    side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
    ph = rnd.random(); rows = []; nu = 2
    for j in range(segs + 1):
        t = j/segs; w = W*max(0.06, SHAPES["strap"](t))*(1 + 0.15*math.sin(t*17 + seed))
        cen = Vector(base) + d*L*t + side*(wave*L*0.12*math.sin(t*wave_n*math.pi + seed)) - UPZ*droop*L*t*t
        tw = twist*math.sin(t*2.2 + seed); sd = side*math.cos(tw) + d.cross(side)*math.sin(tw)
        rowv = []
        for i in range(2*nu + 1):
            u = (i - nu)/nu; rf = ruffle*w*math.sin(t*30 + u*2 + seed)*abs(u)
            co = cen + sd*u*w + d.cross(sd).normalized()*rf
            rowv.append(P.v(co, bend=bend_scale*(0.15 + t)**1.3, flutter=t, phase=ph, tint=tint))
        rows.append(rowv)
    for j in range(segs):
        for i in range(2*nu):
            P.face((rows[j][i], rows[j][i+1], rows[j+1][i+1], rows[j+1][i]), key, False,
                   [((i - nu)/nu, j/segs), ((i + 1 - nu)/nu, j/segs), ((i + 1 - nu)/nu, (j + 1)/segs), ((i - nu)/nu, (j + 1)/segs)])

def build_Seaweed(coll, row):
    mg = leaf_mat("PLN_Seaweed_Green", [(0.06,0.09,0.01),(0.14,0.19,0.03),(0.25,0.30,0.06),(0.38,0.42,0.10)], vein=0.3, rim=0.3, spec=0.5, rough=0.35)
    mr = leaf_mat("PLN_Seaweed_Red", [(0.10,0.015,0.008),(0.22,0.04,0.015),(0.38,0.09,0.03),(0.52,0.17,0.06)], vein=0.3, rim=0.3, spec=0.5, rough=0.35)
    mb = plant_mat("PLN_Seaweed_Bladder", [(0.25,0.06,0.02),(0.45,0.14,0.05),(0.65,0.28,0.10)], scale=6, rough=0.3, spec=0.6, top=0.4)
    msd = soil_mat("PLN_Seaweed_Sand", SAND)
    mpb = plant_mat("PLN_Seaweed_Pebble", [(0.04,0.04,0.04),(0.12,0.11,0.10),(0.30,0.27,0.24)], scale=8)
    M = {"g": mg, "r": mr, "b": mb}
    P = Plant("PLN_Seaweed_Green", 0.95, 0.4, seed=291); rnd = random.Random(1)
    for k in range(15):
        a = rnd.uniform(0, 6.28); r = rnd.uniform(0, 0.15); d = Vector((math.cos(a)*0.25, math.sin(a)*0.25, 1))
        ribbon(P, (r*math.cos(a), r*math.sin(a), 0), d, rnd.uniform(0.55, 0.9), rnd.uniform(0.06, 0.09), "g", wave=0.5, ruffle=0.35, seed=k, tint=rnd.random())
    mk(P, coll, M, row.place(1.0, 0.95), "seaweed", outline=False, ground=(0.4, msd, None, 1, 0.03, 9, mpb))
    P = Plant("PLN_Seaweed_Red", 1.05, 0.4, seed=292); rnd = random.Random(2)
    for k in range(10):
        a = rnd.uniform(0, 6.28); r = rnd.uniform(0, 0.12); base = Vector((r*math.cos(a), r*math.sin(a), 0)); d = Vector((math.cos(a)*0.2, math.sin(a)*0.2, 1))
        ribbon(P, base, d, rnd.uniform(0.6, 1.0), rnd.uniform(0.045, 0.07), "r", wave=0.7, ruffle=0.3, twist=1.0, seed=10 + k, tint=rnd.random())
        st = [base + d.normalized()*0.9*t + Vector((0.05*math.sin(t*6 + k), 0, 0)) for t in [j/6 for j in range(7)]]
        tube(P, st, [0.006]*6 + [0.003], "r", sides=4, solid=False, bend=lambda t: (0.15 + t)**1.3)
        for j in range(3):
            t = rnd.uniform(0.3, 0.9); ball(P, base + d.normalized()*0.9*t + Vector((0.05*math.sin(t*6 + k) + 0.02, 0, 0)), 0.016, "b", sub=1, bend=(0.15 + t)**1.3, flutter=0.3)
    mk(P, coll, M, row.place(1.0, 1.05), "seaweed", outline=False, ground=(0.38, msd, None, 2, 0.03, 9, mpb))

def build_Kelp(coll, row):
    mk_ = leaf_mat("PLN_Kelp_Blade", [(0.18,0.08,0.01),(0.36,0.18,0.03),(0.55,0.32,0.07),(0.70,0.46,0.12)], vein=0.4, rim=0.35, spec=0.55, rough=0.3)
    ms = flat_col("PLN_Kelp_Stipe", [(0.15,0.06,0.01),(0.30,0.15,0.03)])
    mb = plant_mat("PLN_Kelp_Bladder", [(0.25,0.10,0.015),(0.48,0.24,0.04),(0.65,0.38,0.08)], scale=6, rough=0.3, spec=0.6, top=0.4)
    mr = plant_mat("PLN_Kelp_Rock", [(0.05,0.05,0.045),(0.12,0.115,0.10),(0.22,0.21,0.19),(0.32,0.31,0.28)], scale=3, moss=MOSS_P, moss_amt=0.5,
                   edge=(0.45,0.43,0.40), edge_amt=0.6, geo_ao=0.5)
    M = {"k": mk_, "st": ms, "b": mb, "rock": mr}
    for nm, H, n, rock_r, seed in (("PLN_Kelp_Small", 1.15, 4, 0.16, 301), ("PLN_Kelp_Large", 2.5, 7, 0.32, 302)):
        P = Plant(nm, H, 0.6, seed=seed); rnd = random.Random(seed)
        rk = ball(P, (0, 0, rock_r*0.25), rock_r, "rock", sub=3, squash=0.6, bend=0.0, noise_amp=0.35, seed=seed, solid=True)
        for k in range(n):
            a = k*2.39996; base = Vector((math.cos(a)*rock_r*0.3, math.sin(a)*rock_r*0.3, rock_r*0.75))
            h = H*rnd.uniform(0.75, 1.0) - rock_r; lean = Vector((math.cos(a)*0.25 + 0.15, math.sin(a)*0.25, 1)).normalized()
            st = [base + lean*h*t + Vector((0.06*math.sin(t*5 + k), 0.05*math.cos(t*4 + k), 0)) for t in [j/10 for j in range(11)]]
            hb = lambda t, h=h: ((base.z + h*t)/H + 0.1)**1.25
            tube(P, st, [0.012*H/1.2]*10 + [0.006], "st", sides=5, solid=False, bend=hb)
            for j in range(3 if H < 2 else 5):
                t = 0.25 + 0.7*j/(3 if H < 2 else 5) + rnd.uniform(-.04, .04); p = st[int(t*10)]
                ball(P, p, 0.022*H/1.2 + 0.01, "b", sub=1, squash=1.3, bend=hb(t), flutter=0.2)
                side = Vector((math.cos(a + j*2.1), math.sin(a + j*2.1), 0.9))
                ribbon(P, p, side, rnd.uniform(0.35, 0.55)*H/1.2, 0.07*H/1.2, "k", segs=12, wave=0.6, ruffle=0.3, twist=0.9, droop=0.15, seed=seed + k*7 + j,
                       tint=rnd.random(), bend_scale=1.0 + 0.4*t)
            ribbon(P, st[-1], lean + Vector((0.3, 0, 0)), 0.4*H/1.2, 0.07*H/1.2, "k", segs=12, wave=0.6, ruffle=0.3, seed=seed + k*7 + 6, tint=rnd.random(), bend_scale=1.4)
        mk(P, coll, M, row.place(1.4 if H > 2 else 1.0, H), "kelp", outline=True, motion_scale=H/2.5)

def build_Coral(coll, row):
    mp = plant_mat("PLN_Coral_Pink", [(0.45,0.10,0.08),(0.70,0.25,0.20),(0.88,0.45,0.38),(0.98,0.65,0.55)], scale=6, strokes=0.3, edge=(1.0,0.8,0.7), edge_amt=0.6, geo_ao=0.5, top=0.35, rough=0.6)
    mo = plant_mat("PLN_Coral_Brain", [(0.35,0.10,0.01),(0.62,0.24,0.04),(0.82,0.40,0.10),(0.95,0.60,0.25)], scale=5, strokes=0.25, edge=(1.0,0.78,0.45), edge_amt=0.8, geo_ao=0.8, top=0.3)
    mv = plant_mat("PLN_Coral_Fan", [(0.15,0.04,0.30),(0.30,0.10,0.55),(0.48,0.25,0.75),(0.62,0.42,0.88)], scale=6, strokes=0.3, vein=0.0, rim=0.3, top=0.3, rough=0.6)
    mvb = plant_mat("PLN_Coral_FanBranch", [(0.20,0.05,0.35),(0.35,0.12,0.55)], scale=5, edge=(0.6,0.4,0.85), edge_amt=0.5)
    mt = plant_mat("PLN_Coral_Table", [(0.01,0.18,0.15),(0.03,0.35,0.30),(0.10,0.55,0.48),(0.25,0.72,0.62)], scale=4, strokes=0.25, edge=(0.5,0.9,0.8), edge_amt=0.8, geo_ao=0.7, top=0.35, spec=0.4)
    msd = soil_mat("PLN_Coral_Sand", SAND); mpb = plant_mat("PLN_Coral_Pebble", [(0.10,0.09,0.08),(0.30,0.27,0.24),(0.55,0.50,0.45)], scale=8)
    M = {"pink": mp, "brain": mo, "fan": mv, "fb": mvb, "table": mt}
    P = Plant("PLN_Coral_Branching", 0.6, 0.35, seed=311); rnd = random.Random(1)
    def cbranch(p, d, L, r, depth, sd):
        pts = path(p, d, L, 5, curve=0.6, wob=0.12, seed=sd); tube(P, pts, [r, r*0.95, r*0.9, r*0.88, r*0.86, r*0.85], "pink", sides=8, bend=0.0)
        if depth > 0:
            for s in (-1, 1):
                i = rnd.randint(2, 4); dd = (pts[i+1] - pts[i]).normalized(); sdv = dd.cross(UPZ)
                sdv = sdv.normalized() if sdv.length > 1e-6 else Vector((1, 0, 0))
                cbranch(pts[i], (dd + sdv*0.8*s + UPZ*0.2).normalized(), L*0.6, r*0.85, depth - 1, sd*3 + s)
    for k in range(4):
        a = k*1.6; cbranch(Vector((math.cos(a)*0.05, math.sin(a)*0.05, 0)), Vector((math.cos(a)*0.5, math.sin(a)*0.5, 1)), 0.3, 0.035, 2, 10 + k)
    mk(P, coll, M, row.place(0.8, 0.6), None, ground=(0.32, msd, None, 1, 0.03, 6, mpb))
    P = Plant("PLN_Coral_Brain", 0.55, 0.35, seed=312)
    res = bmesh.ops.create_icosphere(P.bm, subdivisions=5, radius=1.0)
    for vt in res["verts"]:
        p = vt.co.copy(); n_ = noise.noise(p*2.2, noise_basis='PERLIN_ORIGINAL'); g = abs(math.sin(n_*14))
        rr = 0.33*(1 - 0.06*(1 - g)**2.5)
        vt.co = Vector((p.x*rr, p.y*rr, max(-0.05, p.z*rr*0.92 + 0.22)))
        vt[P.L["bend"]] = 0.0; vt[P.L["ao"]] = 0.5 + 0.5*g
    for fc in {f for v in res["verts"] for f in v.link_faces}:
        fc.material_index = P.slot("brain"); fc.smooth = True; P.solid.append(fc)
    mk(P, coll, M, row.place(0.8, 0.55), None, ground=(0.36, msd, None, 2, 0.03, 6, mpb))
    P = Plant("PLN_Coral_Fan", 0.6, 0.35, seed=313)
    fs = leaf(P, Vector((0, 0, 0.12)), Vector((0, 0, 1)), Vector((0, -1, 0)), 0.48, 0.3, "fan", shape="round", nu=6, nv=10, fold=0.0, wave=0.25, wave_n=9, flut=0.6, bend=0.0)
    for v in {v for f in fs for v in f.verts}: v[P.L["bend"]] = max(0.0, (v.co.z - 0.1)/0.5)**1.2
    rnd = random.Random(3)
    def fanvein(p, d, L, r, depth, sd):
        pts = path(p, d, L, 5, curve=0.2, wob=0.05, seed=sd, up=UPZ)
        pts = [Vector((q.x, -0.012, q.z)) for q in pts]
        tube(P, pts, [r*(1 - 0.5*j/5) for j in range(6)], "fb", sides=5, bend=lambda t: 0.0)
        if depth > 0:
            for s in (-1, 1): fanvein(pts[3], Vector((s*0.7, 0, 1)), L*0.6, r*0.65, depth - 1, sd*2 + s)
    tube(P, [Vector((0, 0, 0)), Vector((0, -0.005, 0.14))], [0.03, 0.022], "fb", sides=7, bend=0.0)
    fanvein(Vector((0, 0, 0.13)), Vector((0, 0, 1)), 0.32, 0.016, 3, 7)
    for o in P.bm.verts:
        if o[P.L["bend"]] == 0.0 and o.co.z > 0.15: o[P.L["bend"]] = max(0.0, (o.co.z - 0.1)/0.5)**1.2
    mk(P, coll, M, row.place(0.8, 0.6), "coral_fan", ground=(0.3, msd, None, 3, 0.03, 6, mpb))
    P = Plant("PLN_Coral_Table", 0.5, 0.45, seed=314)
    lathe(P, [(0.09, 0.0), (0.075, 0.12), (0.06, 0.25), (0.05, 0.33)], "table", sides=12, solid=True, bend=0.0, noise_amp=0.15, seed=1)
    for k, (z, R_, cx, cy) in enumerate(((0.38, 0.36, 0.02, 0.0), (0.24, 0.26, -0.12, 0.06), (0.15, 0.22, 0.14, -0.04))):
        prof = [(0.03, z - 0.035), (R_*0.6, z - 0.05), (R_, z - 0.02), (R_*1.02, z + 0.015), (R_*0.6, z + 0.03), (0.02, z + 0.04)]
        rings_ = []; sides = 26
        for (r, zz) in prof:
            ring = []
            for q in range(sides):
                a = 2*math.pi*q/sides; lob = 1 + 0.16*math.sin(a*5 + k) + 0.06*math.sin(a*11 + k*2)
                ring.append(P.v((cx + r*lob*math.cos(a), cy + r*lob*0.85*math.sin(a), zz + 0.02*math.sin(a*3 + k)*r/R_), bend=0.0))
            rings_.append(ring)
        for i in range(len(rings_) - 1):
            for q in range(sides): P.face((rings_[i][q], rings_[i][(q+1) % sides], rings_[i+1][(q+1) % sides], rings_[i+1][q]), "table", True)
        tube(P, [Vector((0, 0, 0.1)), Vector((cx*0.6, cy*0.6, z*0.6)), Vector((cx*0.8, cy*0.8, z - 0.02))], [0.06, 0.05, 0.04], "table", sides=10, bend=0.0)
    mk(P, coll, M, row.place(1.0, 0.5), None, ground=(0.38, msd, None, 4, 0.03, 6, mpb))

def build_ToxicBloom(coll, row):
    ml = leaf_mat("PLN_Toxic_Leaf", [(0.03,0.08,0.015),(0.07,0.15,0.03),(0.14,0.24,0.05),(0.26,0.33,0.08)], vein=0.6, rim=0.45, rim_col=(0.30,0.45,0.10),
                  spots=(26.0, (0.45,0.12,0.40), 0.7))
    ms = plant_mat("PLN_Toxic_Stem", [(0.06,0.12,0.02),(0.14,0.22,0.05),(0.24,0.32,0.09)], scale=10, edge=(0.4,0.5,0.2), edge_amt=0.6, geo_ao=0.5)
    mb = leaf_mat("PLN_Toxic_Bell", [(0.15,0.02,0.20),(0.32,0.06,0.42),(0.55,0.18,0.68),(0.75,0.38,0.85)], vein=0.4, rim=0.3, ao_amt=0.45, spec=0.5, rough=0.4)
    mt = flat_col("PLN_Toxic_Stamen", [(0.45,0.15,0.40),(0.85,0.45,0.75)], emit=0.15)
    M = {"leaf": ml, "stem": ms, "bell": mb, "st": mt}
    P = Plant("PLN_ToxicBloom", 1.0, 0.7, seed=321); rnd = random.Random(1)
    for k in range(13):
        a = k*2.39996; el = 0.12 + 0.25*(k % 3)/2
        leaf(P, Vector((0, 0, 0.04)), Vector((math.cos(a), math.sin(a), el)), UPZ, rnd.uniform(0.38, 0.52), 0.2, "leaf", shape="ovate", nu=3, nv=7, fold=0.35, droop=0.45, curl=-0.05,
             tint=rnd.random(), cn=Vector((0, 0, -0.2)), cnw=0.4, ao=0.65 + 0.35*el*2, wave=0.12, wave_n=5)
    sp = [Vector((0.02*math.sin(t*5), 0.015*math.cos(t*4), 0.62*t)) for t in [j/8 for j in range(9)]]
    tube(P, sp, [0.03, 0.028, 0.026, 0.024, 0.022, 0.02, 0.018, 0.016, 0.014], "stem", sides=9, rough=0.25, seed=2)
    for k in range(9):   # knobs on the stem
        t = rnd.uniform(0.15, 0.9); i = int(t*8); ball(P, sp[i] + Vector((rnd.uniform(-.025, .025), rnd.uniform(-.025, .025), 0)), 0.012, "stem", sub=1)
    top = sp[-1]
    for k in range(10):
        a = k*2.39996; e = -0.1 + 0.9*(k % 4)/3; nr = Vector((math.cos(a)*math.cos(e), math.sin(a)*math.cos(e), math.sin(e)))
        p = top + nr*0.17; q = p + Vector((0, 0, -0.05)) + nr*0.02
        tube(P, [top, p, q], [0.006, 0.005, 0.004], "stem", sides=4, solid=False, flutter=lambda t: t*0.3)
        pr = [(0.005, 0.0), (0.035, -0.015), (0.05, -0.05), (0.055, -0.09), (0.065, -0.11), (0.06, -0.12)]
        lathe(P, pr, "bell", sides=10, center=q, ribs=(5, 0.2), solid=False)
        for j in range(3):
            aa = j*2.1 + k; st = [q + Vector((math.cos(aa)*0.02*s, math.sin(aa)*0.02*s, -0.09 - 0.06*s)) for s in (0, 0.5, 1.0)]
            tube(P, st, [0.003, 0.0025, 0.002], "st", sides=3, solid=False, flutter=lambda t: t)
    mk(P, coll, M, row.place(1.3, 1.0), "flower")

def build_WaterPlants(coll, row):
    mp = leaf_mat("PLN_Water_LilyPad", [(0.03,0.10,0.02),(0.06,0.18,0.035),(0.12,0.28,0.06),(0.20,0.36,0.09)], vein=0.8, rim=0.4, rim_col=(0.22,0.40,0.10), spec=0.6, rough=0.25)
    mpe = leaf_mat("PLN_Water_LotusPetal", [(0.55,0.20,0.30),(0.80,0.45,0.55),(0.95,0.75,0.80)], vein=0.3, rim=0.0, ao_amt=0.3, tipcol=(0.85,0.30,0.50), tip_amt=0.5)
    my = flat_col("PLN_Water_LotusCore", [(0.70,0.45,0.02),(0.95,0.75,0.10)])
    md = leaf_mat("PLN_Water_Duckweed", [(0.04,0.12,0.02),(0.08,0.22,0.04),(0.15,0.32,0.06),(0.25,0.42,0.09)], vein=0.2, rim=0.35, spec=0.5, rough=0.3)
    mr = plant_mat("PLN_Water_Ring", [(0.03,0.25,0.30),(0.08,0.40,0.45)], scale=3, top=0.0, emit=0.1, rough=0.1, spec=0.6)
    M = {"pad": mp, "petal": mpe, "core": my, "duck": md}
    P = Plant("PLN_Water_LilyLotus", 0.3, 0.6, seed=331)
    N, R = 48, 0.5; c = P.v((0, 0, 0.012), bend=0.0, phase=0.3); rnd = random.Random(1)
    rings_ = []
    for rr in (0.35, 0.7, 0.92, 1.0):
        ring = []
        for q in range(N):
            a = 2*math.pi*q/N + 0.35
            if a > 2*math.pi - 0.2 + 0.35: a = 2*math.pi - 0.2 + 0.35
            k = 1 + 0.03*noise.noise(Vector((math.cos(a)*3, math.sin(a)*3, 0)))
            z = 0.012 + (0.012 if rr == 1.0 else 0.0) + 0.004*math.sin(a*4)*rr
            ring.append((P.v((R*rr*k*math.cos(a), R*rr*k*math.sin(a), z), bend=0.0, flutter=rr**3, phase=0.3, tint=rnd.random()), a, rr))
        rings_.append(ring)
    for q in range(N - 1):   # notch = the gap between q=N-1 and q=0
        P.face((c, rings_[0][q][0], rings_[0][q+1][0]), "pad", False, [(0, 0), (0.35*math.cos(rings_[0][q][1])*0 + 0.35, 0.0), (0.35, 0.0)])
        for i in range(3):
            P.face((rings_[i][q][0], rings_[i+1][q][0], rings_[i+1][q+1][0], rings_[i][q+1][0]), "pad", False,
                   [(0.0, rings_[i][q][2]), (0.0, rings_[i+1][q][2]), (0.0, rings_[i+1][q+1][2]), (0.0, rings_[i][q+1][2])])
    # radial veins via LeafUV.u = angular distance to the nearest vein
    for f in P.bm.faces:
        for lp in f.loops:
            v = lp.vert; a = math.atan2(v.co.y, v.co.x); vein = abs(((a*12/(2*math.pi)) % 1.0) - 0.5)*2
            lp[P.uv].uv = (1 - vein, math.hypot(v.co.x, v.co.y)/R)
    fc = Vector((0.12, -0.06, 0.02))
    for layer, (n, L, el) in enumerate(((8, 0.13, 0.35), (8, 0.12, 0.75), (6, 0.09, 1.15))):
        for j in range(n):
            a = j*2*math.pi/n + layer*0.4; d = Vector((math.cos(a)*math.cos(el), math.sin(a)*math.cos(el), math.sin(el)))
            leaf(P, fc, d, Vector((-math.cos(a)*math.sin(el), -math.sin(a)*math.sin(el), math.cos(el))), L, L*0.42, "petal", shape="petal", nu=2, nv=4, fold=0.45, curl=0.2,
                 bend=0.0, flut=0.15, phase=0.3)
    ball(P, fc + Vector((0, 0, 0.03)), 0.028, "core", sub=2, squash=0.6, bend=0.0, phase=0.3)
    ob = mk(P, coll, M, row.place(1.3, 0.3), "float", outline=False)
    _water_ring(ob, coll, 0.58, mr)
    P = Plant("PLN_Water_Duckweed", 0.1, 0.8, seed=332); rnd = random.Random(2)
    blobs = [(rnd.uniform(-0.45, 0.45), rnd.uniform(-0.3, 0.3)) for _ in range(9)]
    for k in range(150):
        bx, by = rnd.choice(blobs); x, y = bx + rnd.gauss(0, 0.11), by + rnd.gauss(0, 0.09); a = rnd.uniform(0, 6.28); r = rnd.uniform(0.05, 0.11)
        ph = rnd.random()
        for j in range(4):   # lobed rosette of round leaves
            aa = a + j*1.57 + rnd.uniform(-.3, .3)
            leaf(P, Vector((x, y, 0.012 + rnd.uniform(0, 0.012))), Vector((math.cos(aa), math.sin(aa), 0.08)), UPZ, r, r*0.8, "duck", shape="round", nu=1, nv=3, fold=0.1, curl=0.15,
                 bend=0.0, flut=0.3, phase=ph, tint=rnd.random())
    ob = mk(P, coll, M, row.place(1.4, 0.15), "float", outline=False)
    _water_ring(ob, coll, 0.72, mr, rx=0.68)

def _water_ring(parent, coll, r, mat, rx=None):
    P = Plant(parent.name + "_Ripple", 1.0, seed=7); rx = rx or r; N = 64
    for band, (r0, r1) in enumerate(((1.0, 1.035), (1.09, 1.11))):
        ring0, ring1 = [], []
        for q in range(N):
            a = 2*math.pi*q/N; k = 1 + 0.04*math.sin(a*3 + band)
            ring0.append(P.v((rx*r0*k*math.cos(a), r*r0*k*math.sin(a), 0.004), bend=0.0)); ring1.append(P.v((rx*r1*k*math.cos(a), r*r1*k*math.sin(a), 0.004), bend=0.0))
        for q in range(N):
            if band == 1 and (q % 16) > 10: continue
            P.face((ring0[q], ring1[q], ring1[(q+1) % N], ring0[(q+1) % N]), "r")
    ob, tris = plant_finish(P, coll, {"r": mat}, (0, 0, 0), SRC, "float", outline=False)
    ob.parent = parent; ob["export"] = "optional water ripple decal"

# ================================================================== dispatch
SETS = {"Broadleaf": build_Broadleaf, "Conifer": build_Conifer, "GiantTree": build_GiantTree, "Ginkgo": build_Ginkgo, "Mangrove": build_Mangrove,
        "Palm": build_Palm, "FernTree": build_FernTree, "Cycad": build_Cycad, "DeadTrees": build_DeadTrees, "StrippedTrees": build_StrippedTrees,
        "Bushes": build_Bushes, "Ferns": build_Ferns, "Flowers": build_Flowers, "GrassPatches": build_GrassPatches, "Hedges": build_Hedges,
        "Horsetails": build_Horsetails, "DesertPlants": build_DesertPlants, "StumpsLogs": build_StumpsLogs, "ReedsCattails": build_ReedsCattails,
        "Seaweed": build_Seaweed, "Kelp": build_Kelp, "Coral": build_Coral, "ToxicBloom": build_ToxicBloom, "WaterPlants": build_WaterPlants}
if BUILD in SETS:
    SRC = "PLN_%s.jpg" % BUILD
    coll = get_coll("PLN_%s" % BUILD)
    row = Row(gap=0.5)
    SETS[BUILD](coll, row)
    row.hint()
    sc = bpy.context.scene; sc.render.fps = 24; sc.frame_start = 1; sc.frame_end = 192
