"""v02 plants: PLN scatter per reference region, sized to the camera-matched scale, per-object random wind (isl_wind)."""
import glob
PR = random.Random(77)
SKIP = ("Outline", "_Ground", "_Ripple", "Light", "LGT_", "Camera", "_ShadowGround")
_LIB = {}
def kind_objs(kind):
    if kind in _LIB: return _LIB[kind]
    p = ROOT + r"\04_Plants\PLN_%s_v01.blend" % kind
    with bpy.data.libraries.load(p, link=True) as (src, dst):
        names = [n for n in src.objects if not any(s in n for s in SKIP)]
        dst.objects = names
    objs = [o for o in names if hasattr(o, "name")]
    _LIB[kind] = objs; return objs
HEIGHT = dict(Broadleaf=(9, 13), Conifer=(11, 17), GiantTree=(18, 24), Ginkgo=(9, 12), Palm=(8, 12), FernTree=(5, 7.5), Cycad=(2.5, 4), Mangrove=(6, 9),
              Bushes=(1.6, 3.0), Ferns=(1.0, 1.8), ReedsCattails=(1.4, 2.2), Flowers=(0.7, 1.1), Horsetails=(1.3, 2.0), DesertPlants=(1.2, 5.0),
              WaterPlants=(0.3, 0.4), ToxicBloom=(0.9, 1.4), GrassPatches=(0.5, 0.9), Cycad_s=(2, 3), StumpsLogs=(1, 2))
SPACING = dict(Broadleaf=4.5, Conifer=3.6, GiantTree=10, Ginkgo=4.0, Palm=3.5, FernTree=2.6, Cycad=2.0, Mangrove=3.5, Bushes=1.8, Ferns=1.2, ReedsCattails=1.0,
               Flowers=0.8, Horsetails=1.0, DesertPlants=4.0, WaterPlants=1.4, ToxicBloom=1.0, GrassPatches=2.2, StumpsLogs=3)
TREES = {"Broadleaf", "Conifer", "GiantTree", "Ginkgo", "Palm", "FernTree", "Mangrove"}
def excl_mask(hgrid):
    T_ = TERRAIN_CACHE
    gy, gx = np.gradient(hgrid); slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    bad = (slope > 24) | (T_["rm"] > 0.3) | (T_["pads"] > 0.2) | (T_["dr"] < 5.5) | (T_["sd_c"] < 1.0)
    wl, d, hw = T_["river"]; bad |= d < hw + 1.2
    for p in [S["pool"], S["lily"]]: bad |= sdf(p, X, Y) > -1.0
    for p in [S["algae"]] + S["dark_pools"]: bad |= sdf(p, X, Y) > -5.0
    for rd in S["roads"]:
        dd, _ = pline(rd["pts"], X, Y); bad |= dd < rd["w"]/2 + 1.2
    cn = S["cone"]; bad |= np.hypot(X - cn["c"][0], Y - cn["c"][1]) < cn["r"]*0.95
    bad |= sdf(S["lava"], X, Y) > -1.0; bad |= sdf(S["clearing"], X, Y) > -1.0
    return bad
def is_bad(bad, x, y):
    i = int(round((x - XS[0])/RES)); j = int(round((y - YS[0])/RES))
    if not (0 <= i < NX and 0 <= j < NY): return True
    return bool(bad[j, i])
GRID = {}
def free(x, y, r):
    cx, cy = int(x//6), int(y//6)
    for a in range(cx - 2, cx + 3):
        for b in range(cy - 2, cy + 3):
            for (px, py, pr) in GRID.get((a, b), ()):
                if (px - x)**2 + (py - y)**2 < ((r + pr)*0.5)**2: return False
    return True
def mark(x, y, r): GRID.setdefault((int(x//6), int(y//6)), []).append((x, y, r))
MADE = []
TINT = dict(Broadleaf=(0.62, 0.72, 0.55), Conifer=(0.6, 0.7, 0.6), GiantTree=(0.7, 0.78, 0.62), Palm=(0.8, 0.85, 0.7), FernTree=(0.75, 0.82, 0.68),
            Mangrove=(0.62, 0.7, 0.55), Bushes=(0.66, 0.74, 0.58), Ferns=(0.72, 0.8, 0.62), Cycad=(0.75, 0.82, 0.65), GrassPatches=(0.85, 0.88, 0.75))
_TM = {}
def tinted(mat, k):
    key = (mat.name, k)
    if key in _TM: return _TM[key]
    m = mat.copy(); m.name = "PLN2_" + mat.name.replace("PLN_", "") + "_" + k
    nt = m.node_tree if m.use_nodes else None
    if nt:
        for bsdf in [n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED']:
            inp = bsdf.inputs["Base Color"]; mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs[0].default_value = 1.0
            mix.inputs[7].default_value = (*TINT[k], 1)
            if inp.links: src_ = inp.links[0].from_socket; nt.links.new(src_, mix.inputs[6])
            else: mix.inputs[6].default_value = inp.default_value
            nt.links.new(mix.outputs[2], inp)
    _TM[key] = m; return m
def tint_slots(ob, kind):
    if kind not in TINT: return
    for sl in ob.material_slots:
        if sl.material and not any(w in sl.material.name for w in ("Trunk", "Bark", "Wood", "Outline", "Ink", "Flower", "Petal", "Fruit", "Berry")):
            mt = tinted(sl.material, kind); sl.link = 'OBJECT'; sl.material = mt
def plant(kind, x, y, hgrid, C_, pick=None, hscale=1.0):
    objs = kind_objs(kind)
    if pick: objs = [o for o in objs if any(p in o.name for p in pick)] or objs
    if kind == "Broadleaf" and PR.random() < 0.85: objs = [o for o in objs if "Flowering" not in o.name] or objs
    src = PR.choice(objs); me = src.data
    co = np.zeros(len(me.vertices)*3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3); zext = max(co[:, 2].max() - co[:, 2].min(), 1e-3)
    lo, hi = HEIGHT.get(kind, (1, 2)); th = PR.uniform(lo, hi)*hscale
    if kind == "DesertPlants": th = {"Saguaro": PR.uniform(3.5, 5.0), "Barrel": PR.uniform(0.8, 1.2)}.get(next((k for k in ("Saguaro", "Barrel") if k in src.name), ""), PR.uniform(1.2, 1.8))
    s = th/zext; ob = bpy.data.objects.new(src.name + "_i", me); C_.objects.link(ob)
    ob.scale = (s*PR.uniform(0.9, 1.1), s*PR.uniform(0.9, 1.1), s); ob.rotation_euler = (math.radians(PR.uniform(-3, 3)), math.radians(PR.uniform(-3, 3)), PR.uniform(0, 6.283))
    z = h_at(hgrid, x, y) - co[:, 2].min()*s - 0.05
    if kind == "WaterPlants": z = 0.22
    ob.location = (x, y, z); mo = src.get("motion")
    if mo: ob["motion"] = mo
    ob["pln_kind"] = kind; tint_slots(ob, kind); MADE.append(ob); return ob
def scatter(region_poly, mix, n_target, hgrid, bad, C_, clusters=None, cluster_r=9.0, pick=None, hscale=1.0, allow_bad=False, extra_ok=None):
    P = np.asarray(region_poly); x0, y0 = P.min(0); x1, y1 = P.max(0); kinds = list(mix); w = [mix[k] for k in kinds]; got = 0; tries = 0
    centers = None
    if clusters:
        centers = []
        for _ in range(clusters*20):
            x, y = PR.uniform(x0, x1), PR.uniform(y0, y1)
            if pip(region_poly, x, y) and not is_bad(bad, x, y): centers.append((x, y))
            if len(centers) >= clusters: break
    while got < n_target and tries < n_target*25:
        tries += 1
        if centers:
            cx, cy = PR.choice(centers); a = PR.uniform(0, 6.283); d = cluster_r*math.sqrt(PR.random()); x, y = cx + d*math.cos(a), cy + d*math.sin(a)
        else:
            x, y = PR.uniform(x0, x1), PR.uniform(y0, y1)
        if not pip(region_poly, x, y): continue
        if not allow_bad and is_bad(bad, x, y): continue
        if extra_ok and not extra_ok(x, y): continue
        k = PR.choices(kinds, w)[0]; r = SPACING.get(k, 2.0)
        if not free(x, y, r): continue
        plant(k, x, y, hgrid, C_, pick.get(k) if pick else None, hscale); mark(x, y, r); got += 1
    return got
def build_plants(hgrid, density=1.0):
    C_ = coll("ISL2_Plants"); clear_coll(C_); GRID.clear(); MADE.clear(); bad = excl_mask(hgrid); st = {}; F = S["forest"]; D = density
    # mark rocks / props so plants keep clear
    for o in bpy.data.collections["ISL2_Props"].objects: mark(o.location.x, o.location.y, 2.5)
    # plateau: ginkgo cluster (front middle), giants, dense mixed forest, edge bushes
    gk = [(-60, 72), (-48, 66)]
    for gx_, gy_ in gk:
        for _ in range(7):
            x, y = gx_ + PR.uniform(-7, 7), gy_ + PR.uniform(-5, 5)
            if pip(F["plateau"], x, y) and not is_bad(bad, x, y) and free(x, y, 3.5): plant("Ginkgo", x, y, hgrid, C_); mark(x, y, 3.5)
    st["giant"] = scatter(F["plateau"], {"GiantTree": 1}, int(6*D), hgrid, bad, C_, extra_ok=lambda x, y: y > 78)
    st["plateau"] = scatter(F["plateau"], {"Broadleaf": .38, "Conifer": .34, "FernTree": .06, "Palm": .05, "Bushes": .1, "Ferns": .07}, int(330*D), hgrid, bad, C_)
    st["plateau_under"] = scatter(F["plateau"], {"Bushes": .5, "Ferns": .5}, int(120*D), hgrid, bad, C_)
    # jungle between falls and volcano, swamp, beach palms
    st["jungle"] = scatter(F["jungle"], {"Palm": .55, "FernTree": .2, "Cycad": .15, "Ferns": .1}, int(55*D), hgrid, bad, C_)
    st["swamp"] = scatter(F["swamp"], {"Mangrove": .1, "Palm": .1, "FernTree": .05, "ReedsCattails": .5, "Horsetails": .15, "Ferns": .1}, int(130*D), hgrid, bad, C_)
    st["palms_w"] = scatter(F["palms_w"], {"Palm": 1}, int(26*D), hgrid, bad, C_, allow_bad=False)
    st["palms_sw"] = scatter(F["palms_sw"], {"Palm": 1}, int(8*D), hgrid, bad, C_)
    st["palms_e"] = scatter(F["palms_e"], {"Palm": .85, "Bushes": .15}, int(18*D), hgrid, bad, C_)
    # purple flowers patch (swamp south edge)
    pf = [(-128, 12), (-112, 12), (-112, 3), (-128, 3)]
    st["purple"] = scatter(F["swamp"], {"ToxicBloom": .5, "Flowers": .5}, int(30*D), hgrid, bad, C_, extra_ok=lambda x, y: y < S["swamp"][-3][1] + 14, pick={"Flowers": ["Bellflower", "Spike"]})
    # woods (clumped like the reference)
    st["sw_woods"] = scatter(F["sw_woods"], {"Broadleaf": .7, "Conifer": .1, "Bushes": .2}, int(110*D), hgrid, bad, C_, clusters=6, cluster_r=13)
    st["belt_w"] = scatter(F["s_belt_w"], {"Broadleaf": .7, "Bushes": .3}, int(30*D), hgrid, bad, C_)
    st["belt_e"] = scatter(F["s_belt_e"], {"Broadleaf": .65, "Conifer": .1, "Bushes": .25}, int(30*D), hgrid, bad, C_)
    st["se_woods"] = scatter(F["se_woods"], {"Broadleaf": .6, "Bushes": .25, "Palm": .15}, int(40*D), hgrid, bad, C_, clusters=3, cluster_r=8)
    st["south_far"] = scatter(F["south_far"], {"Broadleaf": .6, "Bushes": .35, "Conifer": .05}, int(85*D), hgrid, bad, C_, clusters=16, cluster_r=6)
    st["south_far_e"] = scatter(F["south_far_e"], {"Broadleaf": .55, "Bushes": .4, "Conifer": .05}, int(50*D), hgrid, bad, C_, clusters=10, cluster_r=6)
    # meadow sparse: single trees, bushes
    meadow = [(-100, -60), (60, -60), (60, 60), (-100, 60)]
    st["meadow"] = scatter(meadow, {"Broadleaf": .2, "Bushes": .55, "Flowers": .1, "StumpsLogs": .05, "Ferns": .1}, int(40*D), hgrid, bad, C_)
    # desert, headland, lily pads
    st["desert"] = scatter(F["desert"], {"DesertPlants": 1}, int(26*D), hgrid, bad, C_)
    st["headland"] = scatter(F["headland"], {"Bushes": .5, "Ferns": .2, "Palm": .3}, int(14*D), hgrid, bad, C_)
    st["lily"] = scatter(S["lily"], {"WaterPlants": 1}, 14, hgrid, bad, C_, allow_bad=True, pick={"WaterPlants": ["LilyLotus"]})
    st["algae_pads"] = scatter(S["algae"], {"WaterPlants": 1}, 10, hgrid, bad, C_, allow_bad=True, pick={"WaterPlants": ["Duckweed"]})
    # grass tufts: style chosen by ground zone
    def tuft_ok(style):
        return lambda x, y: True
    big = [(-150, -110), (128, -110), (128, 176), (-150, 176)]
    st["tufts"] = 0
    for _ in range(int(700*D)):
        x, y = PR.uniform(-140, 120), PR.uniform(-105, 120)
        if is_bad(bad, x, y) or not free(x, y, 1.0): continue
        if sdf(S["desert"], x, y) > 0 or sdf(S["swamp"], x, y) > 0: continue
        dry = any(sdf(p, x, y) > -3 for p in S["dry"]) or sdf(S["headland"], x, y) > 0 or sdf(S["hill"]["foot"], x, y) > 0
        lush = any(sdf(F[k], x, y) > 0 for k in ("sw_woods", "south_far", "south_far_e", "jungle")) or sdf(F["plateau"], x, y) > 0
        style = ["Dry"] if dry else (["Tall", "ShortLush"] if lush else ["ShortLush", "Clover"])
        plant("GrassPatches", x, y, hgrid, C_, style); mark(x, y, 1.0); st["tufts"] += 1
    return st
