"""ISLAND stage 3: scatter PLN plants per scatter_regions, per-object random wind (isl_wind). exec after build_island.py."""
import glob
HV = np.load(ROOT + r"\02_Environment\Island\_hv.npy")
SC = bpy.context.scene
PC = bpy.data.collections.get("ISL_Plants") or bpy.data.collections.new("ISL_Plants")
if PC.name not in SC.collection.children: SC.collection.children.link(PC)
for o in list(PC.objects): bpy.data.objects.remove(o, do_unlink=True)
rnd = random.Random(23)
CAP = globals().get("CAP", 1.0)        # global density multiplier
TREE_CAP = globals().get("TREE_CAP", 650)
SKIP = ("Outline", "_Ground", "_Ripple", "Light", "LGT_", "Camera", "_ShadowGround")
LIB = {}
def lib(kind):
    if kind in LIB: return LIB[kind]
    p = glob.glob(ROOT + r"\04_Plants\PLN_%s_v01.blend" % kind)
    names = []
    if p:
        with bpy.data.libraries.load(p[0], link=True) as (src, dst):
            names = [n for n in src.objects if not any(s in n for s in SKIP)]
            dst.objects = names
    LIB[kind] = [o for o in names if hasattr(o, 'name')]
    return LIB[kind]
def pip(x, y, poly):
    c = False; n = len(poly); j = n-1
    for i in range(n):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj-xi)*(y-yi)/(yj-yi + 1e-12) + xi: c = not c
        j = i
    return c
def area(poly): return abs(sum(poly[i][0]*poly[(i+1) % len(poly)][1] - poly[(i+1) % len(poly)][0]*poly[i][1] for i in range(len(poly))))/2*CELL*CELL
RAD = dict(GiantTree=5.0, Broadleaf=2.6, Conifer=2.2, Ginkgo=2.4, FernTree=1.6, Palm=2.2, Cycad=1.4, Mangrove=2.0, DeadTrees=2.0, StrippedTrees=2.0, Bushes=1.0, Hedges=1.5,
           Ferns=0.8, Horsetails=0.7, Flowers=0.5, GrassPatches=0.6, ReedsCattails=0.6, StumpsLogs=1.0, DesertPlants=1.5, WaterPlants=1.0, ToxicBloom=1.0, Coral=0.9, Kelp=0.9, Seaweed=0.7)
TREES = {"GiantTree", "Broadleaf", "Conifer", "Ginkgo", "FernTree", "Palm", "Cycad", "Mangrove", "DeadTrees", "StrippedTrees"}
def pick(kind, zname):
    L = lib(kind)
    if not L: return None
    if kind == "GrassPatches":
        want = {"grass_short": ["ShortLush", "Clover"], "grass_lush": ["Tall", "ShortLush"], "grass_dry": ["Dry"], "plateau": ["Tall", "ShortLush"]}.get(zname, ["ShortLush"])
        L2 = [o for o in L if any(w in o.name for w in want)]; L = L2 or L
    if kind == "Flowers": L = [o for o in L if "Bed" not in o.name] or L
    return rnd.choice(L)
placed = []; grid = {}
def free(x, y, r):
    cx, cy = int(x//4), int(y//4)
    for a in range(cx-2, cx+3):
        for b in range(cy-2, cy+3):
            for (px, py, pr) in grid.get((a, b), ()):
                if (px-x)**2 + (py-y)**2 < (r+pr)**2*0.55: return False
    return True
def mark(x, y, r): grid.setdefault((int(x//4), int(y//4)), []).append((x, y, r))
for f in J["features"]:   # keep clear around structures
    if f["type"] in ("waterfall_big", "bridge", "start_plaza", "stone_circle", "volcano_cone", "fence_ring", "bridge_stairs", "pier"):
        x, y = g2m(f["x"], f["y"]); mark(x, y, 3.0)
water_z = SEA
stats = {}; made = []
trees_left = TREE_CAP
order = sorted(J["scatter_regions"], key=lambda r: r["name"] == "grass_tufts")
for reg in order:
    poly = reg["poly"]; n = int(area(poly)/100*reg["per_100m2"]*CAP)
    zs = {ZID[z] for z in reg["only_zones"]}
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    kinds = list(reg["mix"]); wts = [reg["mix"][k] for k in kinds]
    if reg["name"] == "grass_tufts": n = min(n, 260)
    got = 0; tries = 0
    while got < n and tries < n*12:
        tries += 1
        gx = rnd.uniform(min(xs), max(xs)); gy = rnd.uniform(min(ys), max(ys))
        if not pip(gx, gy, poly): continue
        ci, cj = int(gx), int(gy)
        if not (0 <= ci < W and 0 <= cj < H) or zone[cj, ci] not in zs: continue
        kind = rnd.choices(kinds, wts)[0]
        if kind in TREES and trees_left <= 0: continue
        r = RAD.get(kind, 1.0); x, y = g2m(gx, gy)
        if not free(x, y, r): continue
        src = pick(kind, ZN[int(zone[cj, ci])])
        if not src: continue
        z = h_at(HV, x, y)
        if zone[cj, ci] in (ZID["swamp_water"], ZID["pond"]): z = max(z, SEA) + 0.0
        ob = bpy.data.objects.new(src.name + "_i", src.data)
        ob.location = (x, y, z); ob.rotation_euler = (0, 0, rnd.uniform(0, 6.283)); s = rnd.uniform(0.82, 1.22)
        if kind == "GiantTree": s *= 1.0
        ob.scale = (s, s, s*rnd.uniform(0.92, 1.12))
        mo = src.get("motion")
        if mo: ob["motion"] = mo
        ob["pln_kind"] = kind; ob["region"] = reg["name"]
        PC.objects.link(ob); made.append(ob); mark(x, y, r); got += 1
        if kind in TREES: trees_left -= 1
    stats[reg["name"]] = got
import importlib
wns = {}; exec(open(TOOLS + r"\isl_wind.py").read(), wns)
wns["make_wind_control"]()
wns["apply_wind_many"](made, base_seed=100, strength=1.0)
# scatter list for Unity
sl = [dict(k=o["pln_kind"], n=o.name, x=round(o.location.x, 2), y=round(o.location.y, 2), z=round(o.location.z, 2), rz=round(o.rotation_euler.z, 2), s=round(o.scale.x, 2)) for o in made]
json.dump(sl, open(ROOT + r"\02_Environment\Island\island_scatter_v01.json", "w"))
result = dict(total=len(made), stats=stats)
