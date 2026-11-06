"""v02 terrain: heightfield composed from the camera-matched shapes + slope/zone painted material. exec after isl_v02_common."""
RES = 1.0
XS = np.arange(-150, 140 + 1e-6, RES); YS = np.arange(-175, 185 + 1e-6, RES)
X, Y = np.meshgrid(XS, YS); NY, NX = X.shape
def TERRAIN():
    sd_c = sdf(S["coast"], X, Y)
    base = 1.15 + 0.55*fbm(X, Y, 60, 3, 1) + 0.18*fbm(X, Y, 14, 2, 2)
    # hills
    for hl in S["hills"]:
        r = np.hypot(X - hl["c"][0], Y - hl["c"][1]); base += hl["h"]*np.exp(-(r/hl["r"])**2*2.2)
    hc = S["hill"]; sdh = sdf(hc["foot"], X, Y); rr = np.hypot(X - hc["c"][0], Y - hc["c"][1])
    dome = hc["h"]*sstep(-4, 22, sdh)*(0.75 + 0.25*fbm(X, Y, 9, 2, 3)); base += dome
    crag = np.hypot(X - hc["crag"][0], Y - hc["crag"][1]); base += 2.2*sstep(7, 3, crag)*sstep(-2, 6, sdh)
    # desert dunes
    sdd = sdf(S["desert"], X, Y); dmask = sstep(-3, 6, sdd)
    for du in S["dunes"]:
        r = np.hypot(X - du["c"][0], Y - du["c"][1]); base += dmask*du["h"]*np.exp(-(r/du["r"])**2*2.0)*(0.85 + 0.15*np.sin((X*0.6 + Y*0.35)))
    # beach band: wide sand except rocky coasts
    beach_w = 10.0 + 4.0*fbm(X, Y, 40, 2, 5) + 7.0*np.clip((X - 40)/40, 0, 1)*np.clip((60 - Y)/40, 0, 1)
    hl_ = SEA + (base - SEA)*sstep(0, beach_w, sd_c)
    off = np.maximum(-sd_c, 0); sea_floor = SEA - np.minimum(0.28*off + 0.012*off*off, 9.0) + 0.25*fbm(X, Y, 12, 2, 6)
    h = np.where(sd_c > 0, hl_, sea_floor)
    land = sd_c > 0
    # swamp / algae / dark pools / mud valley (low ground)
    sds = sdf(S["swamp"], X, Y); h = np.where(land, h + (0.55 - h)*sstep(-4, 6, sds)*0.85, h)
    for p in [S["algae"]] + S["dark_pools"]:
        sp = sdf(p, X, Y); h = h - (h - (-0.25))*sstep(-1.0, 2.0, sp)
    sdm = sdf(S["mud"], X, Y); h = np.where(land, h + (0.55 - h)*sstep(-5, 4, sdm), h)
    for p in S["puddles"]:
        sp = sdf(p, X, Y); h = h - 0.25*sstep(-0.5, 1.0, sp)
    # roads / plaza / pads : flatten
    hb = box_blur(h, 6); rm = np.zeros_like(h)
    for rd in S["roads"][:2] + S["roads"][3:]:
        d, _ = pline(rd["pts"], X, Y); rm = np.maximum(rm, sstep(rd["w"]/2 + 1.8, rd["w"]/2 - 0.2, d))
    for p in [S["plaza"]] + S["pads"]: rm = np.maximum(rm, sstep(-1.5, 1.0, sdf(p, X, Y)))
    h = np.where(land, h + (hb - h)*rm - 0.05*rm, h)
    pads_m = np.zeros_like(h)
    for p in [S["plaza"]] + S["pads"]: pads_m = np.maximum(pads_m, sstep(-1.5, 0.5, sdf(p, X, Y)))
    h = h + (1.25 - h)*pads_m
    # river channel
    rv = np.asarray(S["river"]); d, t = pline(rv, X, Y); wk = np.interp(t, np.linspace(0, 1, len(S["river_w"])), S["river_w"])
    wl = 0.05 - 0.5*t; hw = wk/2
    bed = wl - 0.35 - 0.75*(1 - np.clip(d/hw, 0, 1)**2)
    bank = sstep(hw + 4.5, hw, d)
    h = np.where(d < hw + 4.5, np.minimum(h, h + (np.maximum(bed, wl - 1.1) - h)*bank), h)
    RIVER_WL = (wl, d, hw)
    # pool under fall + lily pond
    for p, lvl in ((S["pool"], 0.05), (S["lily"], 0.20)):
        sp = sdf(p, X, Y); h = np.minimum(h, np.where(sp > -3, lvl - 0.2 - 1.0*sstep(-1, 5, sp), 1e9)*1 + 0) if False else h - (h - (lvl - 1.0))*sstep(-2.5, 3.0, sp)
    # headland + volcano
    sdhd = sdf(S["headland"], X, Y); hh = HV + 0.5*fbm(X, Y, 10, 3, 7)
    hdm = sstep(-1.0, 3.0, sdhd); h = np.where(sd_c > -2, h + (np.maximum(h, hh) - h)*hdm, h)
    cn = S["cone"]; r = np.hypot(X - cn["c"][0], Y - cn["c"][1]); R = cn["r"]*1.05; pk = cn["peak_h"]
    ang = np.arctan2(Y - cn["c"][1], X - cn["c"][0])
    gully = 1 + 0.07*np.sin(ang*13 + 0.7*fbm(X, Y, 6, 2, 8)*6)*sstep(0.15*R, 0.6*R, r)
    prof = (pk - HV)*np.clip(1 - r/R, 0, 1)**1.7*gully
    rim = 0.13*R; crater = np.where(r < rim, (rim - r)/rim, 0)
    prof = prof - (pk - HV)*0.16*crater**1.2*1.0
    h = h + prof*sstep(R, R*0.85, r)
    sdl = sdf(S["lava"], X, Y); h = h + 0.35*sstep(-1, 3, sdl)*(0.5 + 0.5*fbm(X, Y, 2.5, 2, 9))
    # plateau (high ground) with near-vertical cliffs
    sdp = sdf(S["plateau"], X, Y)
    hp = HP + 1.4*fbm(X, Y, 30, 3, 11) + 0.6*np.clip((-X - 40)/80, 0, 1) + 0.8*np.clip((Y - 90)/60, 0, 1)
    # plateau stream: upper ledge (+2.4 m) above the small cascade, channel carved
    st = np.asarray(S["plateau_stream"]); ds, ts = pline(st, X, Y)
    casc = st[3]; dirv = st[4] - st[2]; dirv = dirv/np.linalg.norm(dirv)
    sl = (X - casc[0])*dirv[0] + (Y - casc[1])*dirv[1]
    near_st = sstep(40, 15, ds)
    k = 0.4 + 14*sstep(2, 22, ds); hp = hp + 2.4*(1 - sstep(-k, k, sl))*near_st
    hp = hp - 0.9*sstep(2.2, 0.8, ds)
    cliff_m = sstep(-0.35, 0.9, sdp)
    h = h + (np.maximum(h, hp) - h)*cliff_m
    # ramp road cut into the cliff (rises 1 -> HP)
    rr_ = np.asarray(S["ramp_road"]); seg = rr_[:6]; dr, tr = pline(seg[:, :2], X, Y)
    L = np.cumsum([0] + [np.hypot(*(seg[i+1, :2] - seg[i, :2])) for i in range(len(seg) - 1)]); L = L/L[-1]
    zr = np.interp(tr, L, seg[:, 2])
    # earthen ramp wedge in the cliff gap: road surface + 6 m shoulders falling to the meadow
    wedge = sstep(11.0, 3.2, dr)*sstep(0.12, 0.3, tr)
    h = np.where(T_sd := sdp < 1.5, h + (np.maximum(h, zr - 0.6*sstep(3.2, 11.0, dr)*(zr - 1.2)) - h)*wedge, h + (np.minimum(h, zr) - h)*sstep(5.0, 3.2, dr))
    h = h + (zr - h)*sstep(4.0, 2.6, dr)*sstep(0.1, 0.2, tr)
    # waterfall notch: plateau lip at the fall, pool in front
    fx, fy = S["fall_base"]; nd = np.hypot(X - fx, Y - fy)
    return dict(h=h, sd_c=sd_c, sdp=sdp, sdhd=sdhd, r_cone=r, R=R, sdl=sdl, sds=sds, sdm=sdm, sdd=sdd, rm=rm, pads=pads_m, river=RIVER_WL, ds=ds, dr=dr)

CLS = ["short", "lush", "dry", "dirt", "rock", "mud", "sand", "desert", "basalt", "lava", "swamp", "pad"]
PAL = dict(short=((112,140,54),(146,166,76),(184,188,104)), lush=((46,84,32),(70,106,44),(98,130,58)), dry=((140,138,60),(176,166,82),(205,190,110)),
  dirt=((168,132,92),(198,164,120),(222,194,152)), rock=((82,76,68),(120,112,100),(160,152,138)), mud=((62,46,34),(92,70,50),(122,96,70)),
  sand=((205,180,130),(228,206,158),(244,228,190)), desert=((196,110,56),(222,140,76),(240,172,104)), basalt=((66,62,58),(104,98,92),(140,134,126)),
  lava=((18,15,14),(34,29,27),(54,47,43)), swamp=((34,54,26),(52,74,32),(76,96,44)), pad=((120,116,108),(150,146,138),(180,176,168)))
def weights(T, Z):
    h = T["h"]; gy, gx = np.gradient(h, RES); slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    land = T["sd_c"] > 0
    W = {c: np.zeros_like(h) for c in CLS}
    W["short"] += 1.0
    for k in ("sw_woods", "south_far", "south_far_e", "se_woods", "jungle", "s_belt_w", "s_belt_e"):
        W["lush"] += 1.6*sstep(-3, 6, sdf(S["forest"][k], X, Y))
    W["lush"] += 2.0*sstep(-0.5, 2, T["sdp"])
    for p in S["dry"]: W["dry"] += 1.6*sstep(-6, 8, sdf(p, X, Y))*(0.6 + 0.4*fbm(X, Y, 8, 2, 21))
    W["dry"] += 2.2*sstep(-1, 3, T["sdhd"])*sstep(T["R"]*1.05, T["R"]*0.9, T["r_cone"])*0 + 2.2*sstep(-1, 3, T["sdhd"])
    hill_m = sstep(-3, 10, sdf(S["hill"]["foot"], X, Y)); W["dry"] += 0.8*hill_m*(0.5 + 0.5*fbm(X, Y, 6, 2, 22))
    W["swamp"] += 3.0*sstep(-3, 5, T["sds"])
    W["mud"] += 4.0*sstep(-3, 3, T["sdm"])
    wl, d, hw = T["river"]; W["mud"] += 3.0*sstep(hw + 1.5, hw - 1.0, d); W["sand"] += 2.0*sstep(hw + 4.5, hw + 1.0, d)*(T["h"] < 1.4)
    W["desert"] += 4.0*sstep(-4, 6, T["sdd"])
    W["sand"] += 5.0*land*sstep(10.0, 5.0, T["sd_c"])*(h < 2.2)*(T["sdp"] < -1)*sstep(-2, -9, T["sdhd"])
    W["sand"] += 6.0*(~land)
    dm = np.zeros_like(h)
    for rd in S["roads"][:2] + S["roads"][3:]:
        d_, _ = pline(rd["pts"], X, Y); dm = np.maximum(dm, sstep(rd["w"]/2 + 0.35, rd["w"]/2 - 0.35, d_))
    dm = np.maximum(dm, sstep(-0.8, 0.8, sdf(S["plaza"], X, Y)))
    W["dirt"] += 14.0*dm; W["dirt"] += 6.0*sstep(4.4, 2.6, T["dr"]); W["dirt"] += 4.0*sstep(-2, 2, sdf(S["clearing"], X, Y))
    W["pad"] += 14.0*sstep(-0.3, 0.3, max([sdf(p, X, Y) for p in S["pads"]], key=lambda a: 0) if False else np.max([sdf(p, X, Y) for p in S["pads"]], axis=0))
    cone = sstep(T["R"]*1.05, T["R"]*0.8, T["r_cone"]); W["basalt"] += 8.0*cone
    W["lava"] += 9.0*sstep(-1, 2, T["sdl"]); W["basalt"] += 2.0*sstep(-6, 1, T["sdl"])
    for s_ in S["lava_streams"]:
        dl_, _ = pline([p[:2] for p in s_], X, Y); W["lava"] += 9.0*sstep(1.6, 0.4, dl_)*cone
    W["lava"] += 12.0*sstep(T["R"]*0.16, T["R"]*0.09, T["r_cone"])
    rock = sstep(38, 52, slope)*land*(1 - sstep(-3, 2, T["sdd"]))*(1 - cone*0.7)
    for c in CLS:
        if c != "rock": W[c] *= (1 - rock)
    W["rock"] += 10.0*rock + 3.0*sstep(-1.5, 0.5, -T["sdhd"])*sstep(2.5, 0.5, np.abs(T["sdhd"]))*sstep(1.0, 2.0, T["h"])
    tot = sum(W.values()) + 1e-6
    return {c: W[c]/tot for c in CLS}, slope

def ground_material():
    m = bpy.data.materials.get("ISL2_Ground") or bpy.data.materials.new("ISL2_Ground"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); N, L = nt.nodes, nt.links
    out = N.new("ShaderNodeOutputMaterial"); bs = N.new("ShaderNodeBsdfPrincipled"); L.new(bs.outputs[0], out.inputs[0])
    tc = N.new("ShaderNodeTexCoord"); obj = tc.outputs["Object"]
    def mp(scale):
        n = N.new("ShaderNodeMapping"); n.inputs["Scale"].default_value = scale; L.new(obj, n.inputs["Vector"]); return n.outputs[0]
    def noise(scale, detail=4, rough=0.6, vec=None):
        n = N.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail; n.inputs["Roughness"].default_value = rough
        L.new(vec or obj, n.inputs["Vector"]); return n.outputs["Fac"]
    def vor(scale, vec=None, feat='F1'):
        n = N.new("ShaderNodeTexVoronoi"); n.feature = feat; n.inputs["Scale"].default_value = scale; L.new(vec or obj, n.inputs["Vector"]); return n.outputs["Distance"]
    def M(op, a, b=None):
        n = N.new("ShaderNodeMath"); n.operation = op
        for i, x in enumerate((a, b)):
            if x is None: continue
            if isinstance(x, (int, float)): n.inputs[i].default_value = float(x)
            else: L.new(x, n.inputs[i])
        return n.outputs[0]
    def R(v, a, b, c=0.0, d=1.0):
        n = N.new("ShaderNodeMapRange"); n.clamp = True; L.new(v, n.inputs["Value"])
        for k_, x in (("From Min", a), ("From Max", b), ("To Min", c), ("To Max", d)): n.inputs[k_].default_value = x
        return n.outputs[0]
    def ramp3(cols, fac):
        r = N.new("ShaderNodeValToRGB"); e = r.color_ramp.elements; e.new(0.5)
        for el, c, p in zip(e, cols, (0.08, 0.5, 0.92)): el.color = (*lin(c), 1); el.position = p
        L.new(fac, r.inputs[0]); return r.outputs[0]
    blot = noise(0.09, 5, 0.6); fine = noise(0.9, 3, 0.55); streak = noise(0.5, 2, 0.5, vec=mp((0.3, 3.0, 1.0)))
    pat = R(M('ADD', M('ADD', M('MULTIPLY', blot, 0.55), M('MULTIPLY', fine, 0.25)), M('MULTIPLY', streak, 0.25)), 0.28, 0.82)
    # rock: vertical columns (Z-stretched voronoi) + strata
    col = R(vor(0.9, vec=mp((1.0, 1.0, 0.12)), feat='F1'), 0.0, 0.9)
    strata = noise(1.6, 3, 0.5, vec=mp((0.15, 0.15, 2.5)))
    rpat = R(M('ADD', M('MULTIPLY', col, 0.55), M('MULTIPLY', strata, 0.45)), 0.15, 0.85)
    # basalt / ash streaks running downhill
    apat = R(M('ADD', M('MULTIPLY', noise(0.7, 4, 0.6), 0.6), M('MULTIPLY', noise(2.5, 3, 0.5, vec=mp((1, 1, 0.3))), 0.4)), 0.25, 0.8)
    att = []
    for nm in ("gA", "gB", "gC"):
        a = N.new("ShaderNodeAttribute"); a.attribute_type = 'GEOMETRY'; a.attribute_name = nm
        s = N.new("ShaderNodeSeparateColor"); L.new(a.outputs["Color"], s.inputs[0]); att += [s.outputs[0], s.outputs[1], s.outputs[2], a.outputs["Alpha"]]
    edge = noise(0.35, 4, 0.55)
    ws = []
    for k, c in enumerate(CLS):
        w = M('ADD', att[k], M('MULTIPLY', M('SUBTRACT', M('ADD', edge, noise(0.25 + 0.05*k, 3, 0.5)), 1.0), 0.22))
        ws.append(R(w, 0.30, 0.62))
    tot = ws[0]
    for w in ws[1:]: tot = M('ADD', tot, w)
    tot = M('MAXIMUM', tot, 0.05); acc = None
    for k, c in enumerate(CLS):
        colr = ramp3(PAL[c], rpat if c == "rock" else (apat if c in ("basalt", "lava") else pat))
        wn = M('DIVIDE', ws[k], tot); sc = N.new("ShaderNodeVectorMath"); sc.operation = 'SCALE'; L.new(colr, sc.inputs[0]); L.new(wn, sc.inputs["Scale"])
        if acc is None: acc = sc.outputs[0]
        else:
            ad = N.new("ShaderNodeVectorMath"); ad.operation = 'ADD'; L.new(acc, ad.inputs[0]); L.new(sc.outputs[0], ad.inputs[1]); acc = ad.outputs[0]
    sz = N.new("ShaderNodeSeparateXYZ"); L.new(obj, sz.inputs[0])
    deep = N.new("ShaderNodeMix"); deep.data_type = 'RGBA'; deep.inputs[7].default_value = (*lin((22, 92, 112)), 1)
    L.new(R(sz.outputs[2], -0.6, -5.0), deep.inputs[0]); L.new(acc, deep.inputs[6])
    L.new(deep.outputs[2], bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.9
    rockw = M('DIVIDE', ws[CLS.index("rock")], tot)
    bp = N.new("ShaderNodeBump"); bp.inputs["Distance"].default_value = 0.08; L.new(M('ADD', M('MULTIPLY', rockw, 0.6), 0.25), bp.inputs["Strength"])
    L.new(M('ADD', M('MULTIPLY', rpat, rockw), M('MULTIPLY', noise(3.0, 4, 0.6), 0.5)), bp.inputs["Height"]); L.new(bp.outputs[0], bs.inputs["Normal"])
    lw = M('DIVIDE', ws[CLS.index("lava")], tot); crack = R(noise(1.4, 6, 0.7), 0.495, 0.505)
    dn = N.new("ShaderNodeTexNoise"); dn.inputs["Scale"].default_value = 0.6; dn.inputs["Detail"].default_value = 3; L.new(obj, dn.inputs["Vector"])
    dv = N.new("ShaderNodeVectorMath"); dv.operation = 'MULTIPLY_ADD'; L.new(dn.outputs["Color"], dv.inputs[0]); dv.inputs[1].default_value = (2.5, 2.5, 2.5); L.new(obj, dv.inputs[2])
    vcr = N.new("ShaderNodeTexVoronoi"); vcr.feature = 'DISTANCE_TO_EDGE'; vcr.inputs["Scale"].default_value = 0.32; L.new(dv.outputs[0], vcr.inputs["Vector"])
    cr = M('MULTIPLY', R(vcr.outputs["Distance"], 0.012, 0.0), R(noise(0.25, 2, 0.5), 0.5, 0.62))
    glow = N.new("ShaderNodeValToRGB"); glow.color_ramp.elements[0].color = (1.0, 0.14, 0.01, 1); glow.color_ramp.elements[1].color = (1.0, 0.45, 0.04, 1)
    L.new(noise(0.6, 3, 0.5), glow.inputs[0]); L.new(glow.outputs[0], bs.inputs["Emission Color"])
    L.new(M('MULTIPLY', M('MULTIPLY', M('POWER', lw, 2.0), cr), 8.0), bs.inputs["Emission Strength"])
    return m

def build_ground(name="ISL2_Ground"):
    T = TERRAIN(); h = T["h"]; Wt, slope = weights(T, None)
    C_ = coll("ISL2_Ground"); clear_coll(C_)
    verts = np.stack([X, Y, h], -1).reshape(-1, 3)
    idx = np.arange(NX*NY).reshape(NY, NX); f = np.stack([idx[:-1, :-1], idx[:-1, 1:], idx[1:, 1:], idx[1:, :-1]], -1).reshape(-1, 4)
    me = bpy.data.meshes.new(name); me.vertices.add(len(verts)); me.vertices.foreach_set("co", verts.ravel())
    me.loops.add(len(f)*4); me.loops.foreach_set("vertex_index", f.ravel()); me.polygons.add(len(f))
    me.polygons.foreach_set("loop_start", np.arange(0, len(f)*4, 4)); me.polygons.foreach_set("loop_total", np.full(len(f), 4))
    me.polygons.foreach_set("use_smooth", np.ones(len(f), bool)); me.update(); me.validate()
    for g, nm in enumerate(("gA", "gB", "gC")):
        ca = me.color_attributes.new(nm, 'FLOAT_COLOR', 'POINT'); ca.data.foreach_set("color", np.stack([Wt[CLS[g*4 + c]].ravel() for c in range(4)], -1).ravel().astype(np.float32))
    ob = bpy.data.objects.new(name, me); C_.objects.link(ob); me.materials.append(ground_material())
    np.save(ISL + r"\_v02_h.npy", h)
    return ob, T

def h_at(hv, x, y):
    i = np.clip((x - XS[0])/RES, 0, NX - 1.001); j = np.clip((y - YS[0])/RES, 0, NY - 1.001); i0, j0 = int(i), int(j); fu, fv = i - i0, j - j0
    return float(hv[j0, i0]*(1-fu)*(1-fv) + hv[j0, i0+1]*fu*(1-fv) + hv[j0+1, i0]*(1-fu)*fv + hv[j0+1, i0+1]*fu*fv)
