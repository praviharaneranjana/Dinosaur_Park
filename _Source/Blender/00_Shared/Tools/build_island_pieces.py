"""ISLAND stage 2: TRN hero pieces (collection instances of linked TRN objects), cliffs, waterfall, volcano, desert, rocks, rivers. exec after build_island.py (STAGE='none')."""
HV = np.load(ROOT + r"\02_Environment\Island\_hv.npy"); BANK = np.load(ROOT + r"\02_Environment\Island\_bank.npy")
SC = bpy.context.scene
LIBC = bpy.data.collections["ISL_LIB"]
PC = bpy.data.collections.get("ISL_Pieces") or bpy.data.collections.new("ISL_Pieces")
if PC.name not in SC.collection.children: SC.collection.children.link(PC)
for o in list(PC.objects): bpy.data.objects.remove(o, do_unlink=True)
rnd = random.Random(11)
_libc = {}
def lib_coll(name):
    if name in _libc: return _libc[name]
    c = bpy.data.collections.get("LIB_" + name) or bpy.data.collections.new("LIB_" + name)
    stack = [bpy.data.objects[name]]
    while stack:
        x = stack.pop()
        if x.name not in c.objects: c.objects.link(x)
        stack += list(x.children)
    _libc[name] = c; return c
def inst(name, x, y, z=None, rot=0.0, sx=1.0, sy=None, sz=None, tag=None):
    if z is None: z = h_at(HV, x, y)
    e = bpy.data.objects.new((tag or name) + ".inst", None); e.instance_type = 'COLLECTION'; e.instance_collection = lib_coll(name); e.empty_display_size = 0.4
    e.location = (x, y, z); e.rotation_euler = (0, 0, rot); e.scale = (sx, sx if sy is None else sy, sx if sz is None else sz); PC.objects.link(e); return e
def feat(t): return [f for f in J["features"] if f["type"] == t]
count = {}
def tally(k): count[k] = count.get(k, 0) + 1

# ---------------- cliffs along the plateau rim
fx, fy = FALL_XY()
N4 = ((0, 1), (0, -1), (1, 0), (-1, 0))
for (i, j) in J["cliff_rim"]:
    cx, cy = g2m(i+0.5, j+0.5)
    if abs(cx-fx) < 3.2 and abs(cy-fy) < 3.6: continue
    outs = [(di, dj) for di, dj in N4 if 0 <= i+di < W and 0 <= j+dj < H and hm[j+dj, i+di] < 3.0 and zone[j+dj, i+di] != ZID["ramp"]]
    if not outs: continue
    for di, dj in outs:
        nx_, ny_ = float(di), float(dj); ex, ey = cx + nx_*1.0, cy + ny_*1.0
        gz = min(h_at(HV, ex+nx_*2.0, ey+ny_*2.0), 1.0); z0 = max(gz - 0.35, -1.2)
        zs = (PLAT - 0.12 - z0)/4.0
        rot = math.atan2(nx_, -ny_) + math.radians(rnd.uniform(-3, 3))
        inst("TRN_Cliff_Tall", cx + nx_*0.30, cy + ny_*0.30, z0, rot, sx=rnd.uniform(0.98, 1.1), sy=rnd.uniform(1.0, 1.25), sz=zs, tag="CLIFF"); tally("cliff")

# ---------------- waterfall (big, stretched to the 4 m plateau)
inst("TRN_Waterfall_Big", fx, fy, 0.0, 0.0, sx=1.0, sy=1.0, sz=PLAT/3.0, tag="WATERFALL"); tally("waterfall")

# ---------------- volcano cone + lava plates + lava rocks
for f in feat("volcano_cone"):
    vx, vy = g2m(f["x"], f["y"]); inst("TRN_Volcano_Mini", vx, vy, h_at(HV, vx, vy)-0.1, math.radians(15), sx=5.8, sy=5.6, sz=2.35, tag="VOLCANO"); tally("volcano")
lava = np.argwhere(zone == ZID["lava"])
for (j, i) in lava[::2]:
    x, y = g2m(i+0.5, j+0.5); inst("TRN_Volcano_LavaPlates", x, y, h_at(HV, x, y)-0.03, math.radians(90*rnd.randint(0, 3)), sx=2.0, sy=2.0, sz=1.0, tag="LAVA"); tally("lava")
bas = np.argwhere(zone == ZID["basalt"])
for k in range(34):
    j, i = bas[rnd.randrange(len(bas))]; x, y = g2m(i+rnd.random(), j+rnd.random()); n = rnd.choice(["TRN_LavaRock_Tall", "TRN_LavaRock_Small", "TRN_LavaRock_Low", "TRN_LavaRock_Cube"])
    inst(n, x, y, None, rnd.uniform(0, 6.28), sx=rnd.uniform(1.4, 3.2), tag="LAVAROCK"); tally("lavarock")

# ---------------- desert
for f in feat("mesa_big") + feat("mesa_small") + feat("mesa_front"):
    x, y = g2m(f["x"], f["y"]); s = {"mesa_big": 6.0, "mesa_small": 4.0, "mesa_front": 5.2}[f["type"]]*f.get("scale", 1.0)
    inst("TRN_Desert_Mesa_Small", x, y, None, rnd.uniform(0, 6.28), sx=s, sz=s*1.1, tag="MESA"); tally("mesa")
for f in feat("arch"):
    x, y = g2m(f["x"], f["y"]); inst("TRN_Desert_Mesa_Arch", x, y, None, math.radians(-25), sx=4.6, sz=5.0, tag="ARCH"); tally("arch")
des = np.argwhere(zone == ZID["desert"])
pts = []
for k in range(70):
    j, i = des[rnd.randrange(len(des))]; x, y = g2m(i+rnd.random(), j+rnd.random())
    if all((x-a)**2 + (y-b)**2 > 36 for a, b in pts): pts.append((x, y))
for x, y in pts[:26]:
    n = rnd.choice(["TRN_Desert_DuneLow", "TRN_Desert_DuneHigh", "TRN_Desert_DuneRidge"]); s = rnd.uniform(3.0, 5.2)
    inst(n, x, y, None, rnd.uniform(0, 6.28), sx=s, sz=s*rnd.uniform(0.7, 1.0), tag="DUNE"); tally("dune")
for k, (x, y) in enumerate(pts[26:40]):
    inst("TRN_Desert_Ripples", x, y, None, rnd.uniform(0, 6.28), sx=3.2, sz=1.0, tag="RIPPLE"); tally("ripple")

# ---------------- rocks: hills, boulders on rocky coasts + cliff feet
rock = np.argwhere(zone == ZID["rock"])
for (j, i) in rock[::2]:
    x, y = g2m(i+rnd.random(), j+rnd.random()); n = "TRN_RockyHill_0%d" % rnd.randint(1, 6); s = rnd.uniform(2.0, 3.2)
    inst(n, x, y, None, rnd.uniform(0, 6.28), sx=s, sz=s*rnd.uniform(0.9, 1.4), tag="HILLROCK"); tally("hillrock")
cand = np.argwhere(((zone == ZID["sand"]) | (zone == ZID["basalt"])) & (dw <= 3.0) & (hm < 1.5))
for k in range(70):
    j, i = cand[rnd.randrange(len(cand))]; x, y = g2m(i+rnd.random(), j+rnd.random())
    if zone[j, i] != ZID["basalt"] and not (i > 62 and j > 30) and not (i < 20 and j > 38) and rnd.random() < 0.7: continue
    n = rnd.choice(["TRN_Boulder_Split", "TRN_Boulder_Round", "TRN_Boulder_Pillar", "TRN_Boulder_Block"]); s = rnd.uniform(1.6, 3.4)
    inst(n, x, y, None, rnd.uniform(0, 6.28), sx=s, sz=s*rnd.uniform(0.8, 1.2), tag="BOULDER"); tally("boulder")
for f in feat("stone_circle"):
    x, y = g2m(f["x"], f["y"])
    for a in range(9):
        t = a/9*6.283; inst(rnd.choice(["TRN_Boulder_Block", "TRN_Boulder_Round", "TRN_Boulder_Split"]), x+math.cos(t)*5.0, y+math.sin(t)*3.4, None, rnd.uniform(0, 6.28), sx=rnd.uniform(1.8, 2.5), tag="CIRCLE"); tally("circle")
for f in feat("fence_ring"):
    x, y = g2m(f["x"], f["y"]); inst("TRN_Beach_FenceRing", x, y, None, math.radians(10), sx=6.0, sy=6.0, sz=2.0, tag="FENCE"); tally("fence")

# ---------------- ponds + swamp (TRN tiles scaled to patches)
pc = np.argwhere(zone == ZID["pond"])
if len(pc):
    j, i = pc.mean(0); x, y = g2m(i+0.5, j+0.5); inst("TRN_Pond_Large", x, y, h_at(BANK, x, y)-0.25, math.radians(-8), sx=3.3, sy=3.0, sz=1.6, tag="POND"); tally("pond")
swp = np.argwhere(zone == ZID["swamp_water"])
if len(swp):
    sel = []
    for (j, i) in swp[rnd.sample(range(len(swp)), min(len(swp), 60))]:
        x, y = g2m(i+0.5, j+0.5)
        if all((x-a)**2 + (y-b)**2 > 25 for a, b in sel): sel.append((x, y))
    for x, y in sel[:6]:
        inst("TRN_Swamp_Pool", x, y, -0.05, rnd.uniform(0, 6.28), sx=rnd.uniform(2.4, 3.6), sz=1.0, tag="SWAMPPOOL"); tally("swamppool")
sw = np.argwhere(zone == ZID["swamp"])
for k in range(22):
    j, i = sw[rnd.randrange(len(sw))]; x, y = g2m(i+rnd.random(), j+rnd.random()); inst(rnd.choice(["TRN_Swamp_MossGround", "TRN_Swamp_ReedMarsh"]), x, y, h_at(HV, x, y)-0.02, math.radians(90*rnd.randint(0, 3)), sx=rnd.uniform(2.0, 3.0), sz=1.0, tag="SWAMPTILE"); tally("swamptile")

# ---------------- river water ribbons (TRN_River_Water3 material; UV FlowUV, attribute depth)
def water_ribbon(name, pts, half, mat, zfun):
    verts, faces, uvs, dep = [], [], [], []
    acc = 0.0; prev = None; n = len(pts)
    for k, (x, y) in enumerate(pts):
        a = pts[max(k-1, 0)]; b = pts[min(k+1, n-1)]; tx, ty = b[0]-a[0], b[1]-a[1]; L = math.hypot(tx, ty) or 1; tx, ty = tx/L, ty/L; nx_, ny_ = -ty, tx
        if prev: acc += math.hypot(x-prev[0], y-prev[1])
        prev = (x, y); z = zfun(x, y)
        wv = half*(0.85 + 0.15*math.sin(k*0.7))
        for s in (-1, -0.5, 0, 0.5, 1):
            verts.append((x+nx_*wv*s, y+ny_*wv*s, z)); uvs.append((s, acc)); dep.append(0.02 + 0.23*(1 - abs(s)**1.8))
    for k in range(n-1):
        for c in range(4): faces.append((k*5+c, (k+1)*5+c, (k+1)*5+c+1, k*5+c+1))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    uv = me.uv_layers.new(name="FlowUV")
    for p in me.polygons:
        for li, vi in zip(p.loop_indices, p.vertices): uv.data[li].uv = uvs[vi]
    at = me.attributes.new("depth", 'FLOAT', 'POINT'); at.data.foreach_set("value", dep)
    me.materials.append(bpy.data.materials[mat]); ob = bpy.data.objects.new(name, me); PC.objects.link(ob); return ob
def zriver(x, y): return max(h_at(BANK, x, y) - 0.10, SEA + 0.06)
rl = river_lines()
for k, ln in enumerate(rl):
    pts = ln[::2] if len(ln) > 40 else ln
    if k == 0: pts = [p for p in pts if p[1] > fy+1.0]
    else: pts = [p for p in pts if p[1] < fy-1.6]
    if len(pts) > 2: water_ribbon("ISL_River_%d" % k, pts, 2.2, "TRN_River_Water3", zriver); tally("river_ribbon")
result = count
