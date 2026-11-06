"""isl_ocean.py - Dino Park Tycoon island ocean (Blender 5.x, EEVEE, hand-painted stylized look).

Usage inside Blender (standalone module, needs only bpy + numpy):
    ns = {}; exec(open(path).read(), ns)
    objs = ns["build_ocean"](coll, json_path)          # builds ISL_Ocean, ISL_Seabed, ISL_Ocean_Horizon
    ns["set_ocean_preset"]("calm")                      # live preset switch ("calm" | "tropical" | "stormy")
    ns["setup_eevee_water"](scene)                      # optional render flags, never called automatically

Everything animated is driven by scene time (frame/24): the wave modifier uses the Scene Time node,
shaders use a driver Value node (same technique as trn_anim.time_out) - no keyframes, runs forever.
"""
import bpy, math, random, json
import numpy as np

# =====================================================================================
# TUNABLES (edit here, or change at runtime and call apply_tunables())
# =====================================================================================
TUNE = dict(
    # waves (geometry nodes)
    amp_scale=1.0,        # global wave height multiplier
    speed_scale=0.35,     # stylised speed (1.0 = physical deep-water speed)
    phase_jitter=2.4,     # rad, position-noise phase offset ("every place moves differently")
    amp_var=0.5,          # 0..1 amplitude modulation by low-frequency position noise
    steepness=0.6,        # Gerstner horizontal push (crest sharpness)
    breaker_amp=0.28,     # m, shoreward-travelling breaker height
    breaker_len=11.0,     # m between breakers
    breaker_period=5.5,   # s
    breaker_reach=30.0,   # m from shore where breakers fade out
    swash_lift=0.10,      # m, extra rise/fall of water edge
    swash_period=6.5,     # s
    swash_reach=3.2,      # m, how far the swash foam front travels
    edge_start=0.80,      # fraction of half-extent where waves fade to calm at mesh border
    # look (shader)
    depth_ref=9.0,        # m, depth where colour reaches full deep navy
    alpha_shallow=0.30,   # water opacity at the shore
    alpha_deep=0.96,      # water opacity in deep water
    alpha_depth=3.2,      # m, depth where alpha reaches alpha_deep
    foam_strength=1.0,    # global foam multiplier
    shore_foam=1.0,       # shoreline lines/swash
    crest_foam=0.8,       # wave crest foam
    crest_lo=0.50, crest_hi=0.78,   # normalised crest height thresholds
    streaks=0.55,         # open-water foam streaks
    caustics=0.8,         # moving light lines in shallows
    sparkle=1.0,          # glints
    roughness=0.12, bump=0.10,
    reef_tint=0.85,       # extra tropical turquoise over reef/shelf
    tint_var=0.10,        # large scale colour variation
    fade_start=0.80,      # border colour fade into horizon colour
    horizon_far=3.5,      # skirt fades into sky colour at this many half-extents
)
COLORS = dict(            # sRGB hex
    shallow="#6FD0CF", mid="#2FA3B5", deep="#1A7A95", navy="#0F4C8A",
    tropical="#2FE3D0", reef_dark="#14A3A6", foam="#FFFFFF", caustic="#F2FFE6",
    sky="#BFE8F5", sparkle="#FFFBEA", horizon_start="#1B63A0", horizon_end="#BFE6F4",
    sand_a="#E8D2A2", sand_b="#D9BE86", sand_deep="#35708A", sea_floor="#0F3E69",
)
TERRAIN = dict(           # depth model: depth(shore_m)
    shelf_slope=0.035,    # m depth per m offshore on the shelf
    deep_m=14.0,          # open-sea depth
    ramp_from=30.0, ramp_to=190.0,    # shelf -> deep transition (m from shore)
    reef_raise=0.5,       # reef makes the sea floor shallower by this fraction
    reef_blur=3, seabed_relief=1.0,
)
MESH = dict(
    fine_m=1.0, far_m=8.0, grow=1.15, fine_margin_m=26.0, cut_inside_m=6.0,
    seabed_fine_m=3.0, seabed_far_m=16.0, seabed_grow=1.2, horizon_m=4000.0,
)
PRESETS = {
    "tropical": (dict(), dict()),
    "calm": (dict(amp_scale=0.45, speed_scale=0.28, breaker_amp=0.14, streaks=0.25, crest_foam=0.3,
                  sparkle=0.8, alpha_shallow=0.22, bump=0.07, swash_reach=2.2),
             dict()),
    "stormy": (dict(amp_scale=2.3, speed_scale=0.5, breaker_amp=0.6, streaks=1.0, crest_foam=1.2, crest_lo=0.40,
                    shore_foam=1.4, sparkle=0.3, alpha_shallow=0.5, alpha_deep=1.0, bump=0.2, caustics=0.3,
                    reef_tint=0.4, roughness=0.2, swash_reach=5.0, breaker_period=4.2),
               dict(shallow="#5FA7A8", mid="#2F7F90", deep="#1D5C75", navy="#0A2B4D", tropical="#3FA9A0",
                    horizon_start="#173F63", horizon_end="#8FA4B0", sky="#9DB0B8")),
}
_BASE_TUNE = dict(TUNE); _BASE_COLORS = dict(COLORS)
WAVE_LAMBDAS = [38.0, 24.0, 15.0, 9.5, 6.2]     # m
WAVE_AMPS = [0.50, 0.34, 0.20, 0.11, 0.06]      # m at amp_scale 1 (deep water)
GN_NAME = "ISL_Ocean_Waves"

# =====================================================================================
# node helpers (work in shader and geometry node trees)
# =====================================================================================
def _lin(h):
    h = h.lstrip('#'); c = [int(h[i:i+2], 16)/255.0 for i in (0, 2, 4)]
    return tuple(((x+0.055)/1.055)**2.4 if x > 0.04045 else x/12.92 for x in c)

class _B:
    def __init__(s, nt): s.nt = nt; s.nodes = nt.nodes; s.links = nt.links
    def _in(s, sock, v):
        if v is None: return
        if isinstance(v, (int, float)): sock.default_value = float(v)
        elif isinstance(v, tuple): sock.default_value = v if len(v) == 4 or sock.type != 'RGBA' else v
        else: s.links.new(v, sock)
    def val(s, key):
        nm = "P_" + key; n = s.nodes.get(nm)
        if n is None:
            n = s.nodes.new("ShaderNodeValue"); n.name = nm; n.label = key
            n.outputs[0].default_value = TUNE[key]
        return n.outputs[0]
    def rgb(s, key):
        nm = "C_" + key; n = s.nodes.get(nm)
        if n is None:
            n = s.nodes.new("ShaderNodeRGB"); n.name = nm; n.label = key
            n.outputs[0].default_value = (*_lin(COLORS[key]), 1.0)
        return n.outputs[0]
    def m(s, op, a, b=None, c=None, clamp=False):
        n = s.nodes.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
        for i, v in enumerate((a, b, c)): s._in(n.inputs[i], v)
        return n.outputs[0]
    def v(s, op, a, b=None, scale=None):
        n = s.nodes.new("ShaderNodeVectorMath"); n.operation = op
        s._in(n.inputs[0], a)
        if b is not None: s._in(n.inputs[1], b)
        if scale is not None: n.inputs["Scale"].default_value = scale
        return n.outputs["Value"] if op in ('DOT_PRODUCT', 'LENGTH', 'DISTANCE') else n.outputs[0]
    def comb(s, x=0.0, y=0.0, z=0.0):
        c = s.nodes.new("ShaderNodeCombineXYZ")
        for i, val in enumerate((x, y, z)): s._in(c.inputs[i], val)
        return c.outputs[0]
    def sep(s, vec):
        n = s.nodes.new("ShaderNodeSeparateXYZ"); s.links.new(vec, n.inputs[0]); return n.outputs[0], n.outputs[1], n.outputs[2]
    def mr(s, val, a, b, c=0.0, d=1.0, smooth=False):
        n = s.nodes.new("ShaderNodeMapRange"); n.clamp = True
        if smooth: n.interpolation_type = 'SMOOTHSTEP'
        s._in(n.inputs["Value"], val); s._in(n.inputs["From Min"], a); s._in(n.inputs["From Max"], b)
        s._in(n.inputs["To Min"], c); s._in(n.inputs["To Max"], d); return n.outputs[0]
    def mix(s, a, b, fac, blend='MIX'):
        n = s.nodes.new("ShaderNodeMix"); n.data_type = 'RGBA'; n.blend_type = blend
        s._in(n.inputs[0], fac)
        for i, v in ((6, a), (7, b)):
            if isinstance(v, tuple): n.inputs[i].default_value = (*v, 1.0)
            else: s.links.new(v, n.inputs[i])
        return n.outputs[2]
    def noise(s, vec, w, scale, detail=2, rough=0.5):
        n = s.nodes.new("ShaderNodeTexNoise"); n.noise_dimensions = '4D'
        s._in(n.inputs["Scale"], scale); s._in(n.inputs["Detail"], detail); s._in(n.inputs["Roughness"], rough)
        s.links.new(vec, n.inputs["Vector"]); s._in(n.inputs["W"], w); return n
    def vor(s, vec, w, scale, feature='DISTANCE_TO_EDGE'):
        n = s.nodes.new("ShaderNodeTexVoronoi"); n.voronoi_dimensions = '4D'; n.feature = feature
        s._in(n.inputs["Scale"], scale); s.links.new(vec, n.inputs["Vector"]); s._in(n.inputs["W"], w); return n
    def ramp(s, cols, pos, name=None):
        r = s.nodes.new("ShaderNodeValToRGB"); el = r.color_ramp.elements
        while len(el) < len(cols): el.new(0.5)
        for e, c, p in zip(el, cols, pos): e.position = p; e.color = (*c, 1.0)
        if name: r.name = name
        return r
    def attr(s, name):
        a = s.nodes.new("ShaderNodeAttribute"); a.attribute_type = 'GEOMETRY'; a.attribute_name = name; return a.outputs["Fac"]

def _time(nt):
    """seconds at 24 fps via a simple-expression driver (same technique as trn_anim.time_out)"""
    v = nt.nodes.new("ShaderNodeValue"); v.label = "Time"
    fc = v.outputs[0].driver_add("default_value"); fc.driver.type = 'SCRIPTED'; fc.driver.expression = "frame/24.0"
    return v.outputs[0]

def _new_mat(name):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bs.outputs[0], out.inputs[0]); return m, nt, bs, out

def _set_blend(m):
    for a, v in (("surface_render_method", 'BLENDED'), ("use_transparency_overlap", False), ("show_transparent_back", False),
                 ("use_transparent_shadow", False), ("use_backface_culling", False)):
        try: setattr(m, a, v)
        except Exception: pass

# =====================================================================================
# terrain fields from island_map JSON
# =====================================================================================
def _blur(a):
    p = np.pad(a, 1, mode='edge'); a = (p[:-2, 1:-1] + 2*p[1:-1, 1:-1] + p[2:, 1:-1])/4.0
    p = np.pad(a, 1, mode='edge'); return (p[1:-1, :-2] + 2*p[1:-1, 1:-1] + p[1:-1, 2:])/4.0

class _Fields:
    def __init__(self, json_path):
        d = json.load(open(json_path))
        z = np.array(d["zone"], dtype=np.int32); dl = np.array(d["dist_land"], dtype=float); dw = np.array(d["dist_water"], dtype=float)
        self.cell = float(d["cell_m"]); self.ox, self.oy = d["origin_cell"]; self.ny, self.nx = z.shape
        sea = np.isin(z, (0, 1, 19))
        S = np.where(sea, (np.maximum(dl, 0.5) - 0.5)*self.cell, -(np.maximum(dw, 1.0) - 0.5)*self.cell)
        self.S = _blur(_blur(S))
        R = (z == 19).astype(float)
        for _ in range(int(TERRAIN["reef_blur"])): R = _blur(R)
        self.R = np.clip(R*2.4, 0, 1)
        self.half = (self.nx*self.cell/2.0, self.ny*self.cell/2.0)
    def _bil(self, A, X, Y):
        u = X/self.cell + self.ox; v = Y/self.cell + self.oy
        cu = np.clip(u, 0, self.nx-1); cv = np.clip(v, 0, self.ny-1)
        i0 = np.minimum(np.floor(cu).astype(int), self.nx-2); j0 = np.minimum(np.floor(cv).astype(int), self.ny-2)
        fx = cu - i0; fy = cv - j0
        val = (A[j0, i0]*(1-fx)*(1-fy) + A[j0, i0+1]*fx*(1-fy) + A[j0+1, i0]*(1-fx)*fy + A[j0+1, i0+1]*fx*fy)
        return val, np.hypot(u-cu, v-cv)*self.cell
    def shore(self, X, Y):
        v, e = self._bil(self.S, X, Y); return np.where(v > 0, v + e, v)
    def reef(self, X, Y):
        v, e = self._bil(self.R, X, Y); return np.clip(v*np.clip(1.0 - e/30.0, 0, 1), 0, 1)
    def depth(self, S, R):
        s = np.maximum(S, 0.0); a, b = TERRAIN["ramp_from"], TERRAIN["ramp_to"]
        t = np.clip((s - a)/(b - a), 0, 1); sm = t*t*(3 - 2*t); dm = TERRAIN["deep_m"]
        d = np.minimum(dm, TERRAIN["shelf_slope"]*s + (dm - 0.9)*sm)
        return d*(1.0 - TERRAIN["reef_raise"]*R)

def _axis(half_fine, half_total, h0, h1, g):
    pos = [0.0]; step = h0
    while pos[-1] < half_total - 1e-6:
        nx = min(pos[-1] + step, half_total)
        if half_total - nx < 0.35*step: nx = half_total
        pos.append(nx)
        if pos[-1] >= half_fine - 1e-6: step = min(h1, step*g)
    p = np.array(pos); return np.concatenate([-p[:0:-1], p])

def _grid_object(name, xs, ys, F, zfun, cut_in, coll, smooth=True):
    NX, NY = len(xs), len(ys)
    X, Y = np.meshgrid(xs, ys)                      # (NY, NX)
    S = F.shore(X, Y); R = F.reef(X, Y); D = F.depth(S, R)
    gx = np.abs(np.diff(xs)); gy = np.abs(np.diff(ys))
    cx = np.maximum(np.concatenate([[gx[0]], gx]), np.concatenate([gx, [gx[-1]]]))
    cy = np.maximum(np.concatenate([[gy[0]], gy]), np.concatenate([gy, [gy[-1]]]))
    C = np.maximum(cx[None, :], cy[:, None])
    i = np.arange(NX-1)[None, :]; j = np.arange(NY-1)[:, None]
    Smax = np.maximum.reduce([S[:-1, :-1], S[:-1, 1:], S[1:, :-1], S[1:, 1:]])
    keep = Smax > -cut_in
    base = (j*NX + i)[keep]
    faces = np.stack([base, base+1, base+1+NX, base+NX], axis=1)
    used = np.unique(faces); remap = -np.ones(NX*NY, dtype=np.int64); remap[used] = np.arange(len(used))
    faces = remap[faces]
    Z = zfun(S, D)
    co = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)[used]
    me = bpy.data.meshes.new(name)
    me.from_pydata(co.tolist(), [], faces.tolist()); me.update()
    for nm, arr in (("shore", S), ("depth", D), ("reef", R), ("cell", C)):
        at = me.attributes.new(nm, 'FLOAT', 'POINT'); at.data.foreach_set("value", arr.ravel()[used].astype(np.float32))
    try: me.shade_smooth()
    except Exception:
        me.polygons.foreach_set("use_smooth", [True]*len(me.polygons))
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
    return ob

# =====================================================================================
# geometry nodes: waves
# =====================================================================================
def _build_waves_group(hx, hy, rng):
    old = bpy.data.node_groups.get(GN_NAME)
    if old: bpy.data.node_groups.remove(old)
    ng = bpy.data.node_groups.new(GN_NAME, 'GeometryNodeTree')
    ng.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N = ng.nodes; L = ng.links; b = _B(ng)
    gin = N.new("NodeGroupInput"); gout = N.new("NodeGroupOutput")
    pos = N.new("GeometryNodeInputPosition").outputs[0]
    st = N.new("GeometryNodeInputSceneTime"); T = b.m('DIVIDE', st.outputs["Frame"], 24.0)
    def named(nm):
        n = N.new("GeometryNodeInputNamedAttribute"); n.data_type = 'FLOAT'; n.inputs["Name"].default_value = nm; return n.outputs["Attribute"]
    shore, depth, cell = named("shore"), named("depth"), named("cell")
    px, py, _pz = b.sep(pos)
    xy0 = b.v('MULTIPLY', pos, (1.0, 1.0, 0.0))
    # border fade
    er = b.m('MAXIMUM', b.m('MULTIPLY', b.m('ABSOLUTE', px), 1.0/hx), b.m('MULTIPLY', b.m('ABSOLUTE', py), 1.0/hy))
    edge = b.m('SUBTRACT', 1.0, b.mr(er, b.val("edge_start"), 1.0, 0.0, 1.0, smooth=True))
    # low-frequency position noises (colour output = 3 decorrelated channels)
    ph_a = b.noise(xy0, b.m('MULTIPLY', T, 0.02), 0.012, 2, 0.5); ph_b = b.noise(xy0, b.m('ADD', b.m('MULTIPLY', T, 0.02), 17.0), 0.012, 2, 0.5)
    am_a = b.noise(xy0, b.m('ADD', b.m('MULTIPLY', T, 0.015), 31.0), 0.008, 2, 0.5); am_b = b.noise(xy0, b.m('ADD', b.m('MULTIPLY', T, 0.015), 53.0), 0.008, 2, 0.5)
    phc = list(b.sep(ph_a.outputs["Color"])) + list(b.sep(ph_b.outputs["Color"]))
    amc = list(b.sep(am_a.outputs["Color"])) + list(b.sep(am_b.outputs["Color"]))
    th0 = rng.uniform(0, 2*math.pi)
    Zs = None; Xs = None; Ys = None; Q2 = None
    def acc(cur, new): return new if cur is None else b.m('ADD', cur, new)
    for i, (lam, a0) in enumerate(zip(WAVE_LAMBDAS, WAVE_AMPS)):
        lam *= rng.uniform(0.88, 1.15)
        th = th0 + (rng.uniform(-1.1, 1.1) if i < 4 else rng.uniform(0, 2*math.pi))
        dx, dy = math.cos(th), math.sin(th); k = 2*math.pi/lam; c0 = math.sqrt(9.81*lam/(2*math.pi))
        proj = b.m('MULTIPLY_ADD', px, dx, b.m('MULTIPLY', py, dy))
        jit = b.m('MULTIPLY', b.m('SUBTRACT', phc[i], 0.5), b.m('MULTIPLY', b.val("phase_jitter"), 2.0))
        tt = b.m('MULTIPLY', b.m('MULTIPLY', T, b.val("speed_scale")), k*c0)
        ph = b.m('ADD', b.m('SUBTRACT', b.m('MULTIPLY', proj, k), tt), b.m('ADD', jit, rng.uniform(0, 6.28)))
        var = b.val("amp_var")
        mod = b.mr(amc[i], 0.25, 0.75, b.m('SUBTRACT', 1.0, var), b.m('ADD', 1.0, b.m('MULTIPLY', var, 0.9)))
        dfac = b.mr(depth, 0.0, 0.2*lam, 0.1, 1.0, smooth=True)
        lod = b.mr(cell, lam/7.0, lam/3.2, 1.0, 0.0)
        amp = b.m('MULTIPLY', b.m('MULTIPLY', b.m('MULTIPLY', b.m('MULTIPLY', mod, dfac), lod), edge), b.m('MULTIPLY', b.val("amp_scale"), a0))
        zi = b.m('MULTIPLY', amp, b.m('SINE', ph))
        hp = b.m('MULTIPLY', b.m('MULTIPLY', amp, b.m('COSINE', ph)), b.val("steepness"))
        Zs = acc(Zs, zi); Xs = acc(Xs, b.m('MULTIPLY', hp, dx)); Ys = acc(Ys, b.m('MULTIPLY', hp, dy)); Q2 = acc(Q2, b.m('MULTIPLY', amp, amp))
    # shoreward breakers + swash lift (phase shared with the shader foam lines)
    nj = b.noise(xy0, b.m('MULTIPLY', T, 0.04), 0.05, 2, 0.5)
    jb = b.m('MULTIPLY', b.m('SUBTRACT', nj.outputs["Fac"], 0.5), 7.5)
    phb = b.m('ADD', b.m('ADD', b.m('MULTIPLY', shore, b.m('DIVIDE', 6.28319, b.val("breaker_len"))),
                         b.m('MULTIPLY', T, b.m('DIVIDE', 6.28319, b.val("breaker_period")))), jb)
    raw = b.mr(b.m('SINE', phb), -1.0, 1.0)
    reach = b.val("breaker_reach")
    env = b.m('MULTIPLY', b.mr(shore, 0.4, 3.0, 0.0, 1.0, smooth=True),
              b.mr(shore, b.m('MULTIPLY', reach, 0.45), reach, 1.0, 0.0, smooth=True))
    ba = b.m('MULTIPLY', b.m('MULTIPLY', env, edge), b.val("breaker_amp"))
    zb = b.m('MULTIPLY', ba, b.m('POWER', raw, 2.5))
    sw = b.m('SINE', b.m('ADD', b.m('MULTIPLY', T, b.m('DIVIDE', 6.28319, b.val("swash_period"))), b.m('MULTIPLY', jb, 0.7)))
    la = b.m('MULTIPLY', b.m('MULTIPLY', b.mr(shore, 0.0, 3.0, 1.0, 0.0, smooth=True), edge), b.val("swash_lift"))
    zl = b.m('MULTIPLY', la, sw)
    Zt = b.m('ADD', b.m('ADD', b.m('MULTIPLY', Zs, edge), zb), zl)
    rms = b.m('SQRT', b.m('ADD', b.m('ADD', Q2, b.m('MULTIPLY', ba, ba)), b.m('MULTIPLY', la, la)))
    wh = b.m('DIVIDE', Zt, b.m('MAXIMUM', b.m('MULTIPLY', rms, 1.5), 0.03), clamp=False)
    off = b.comb(b.m('MULTIPLY', Xs, edge), b.m('MULTIPLY', Ys, edge), Zt)
    sp = N.new("GeometryNodeSetPosition"); L.new(gin.outputs[0], sp.inputs["Geometry"]); L.new(off, sp.inputs["Offset"])
    sa = N.new("GeometryNodeStoreNamedAttribute"); sa.data_type = 'FLOAT'; sa.domain = 'POINT'
    L.new(sp.outputs["Geometry"], sa.inputs["Geometry"]); sa.inputs["Name"].default_value = "wh"; L.new(wh, sa.inputs["Value"])
    L.new(sa.outputs["Geometry"], gout.inputs[0])
    return ng

# =====================================================================================
# materials
# =====================================================================================
def _water_material(hx, hy, wind):
    m, nt, bs, out = _new_mat("ISL_Ocean_Water"); b = _B(nt); P, C = b.val, b.rgb
    t = _time(nt); obj = nt.nodes.new("ShaderNodeTexCoord").outputs["Object"]
    xy = b.v('MULTIPLY', obj, (1.0, 1.0, 0.0)); sx, sy, _ = b.sep(obj)
    s, d, r, h = b.attr("shore"), b.attr("depth"), b.attr("reef"), b.attr("wh")
    # ---- depth colour
    dn = b.mr(d, 0.0, P("depth_ref"), 0.0, 1.0)
    rd = b.ramp([_lin(COLORS[k]) for k in ("shallow", "mid", "deep", "navy")], [0.0, 0.22, 0.55, 1.0], name="R_depth")
    nt.links.new(dn, rd.inputs[0]); col = rd.outputs[0]
    # large-scale colour variation
    nv = b.noise(xy, b.m('MULTIPLY', t, 0.02), 0.025, 3, 0.5).outputs["Fac"]
    var = P("tint_var"); col = b.mix(col, b.mr(nv, 0.3, 0.7, b.m('SUBTRACT', 1.0, var), b.m('ADD', 1.0, var)), 1.0, 'MULTIPLY')
    # tropical turquoise over reef / shelf + darker reef patches
    shelf = b.mr(s, 12.0, 75.0, 1.0, 0.0)
    trop = b.m('MULTIPLY', b.m('MAXIMUM', r, b.m('MULTIPLY', shelf, 0.5)), P("reef_tint"))
    trop = b.m('MULTIPLY', trop, b.m('SUBTRACT', 1.0, b.m('MULTIPLY', dn, 0.6)))
    col = b.mix(col, C("tropical"), trop)
    npatch = b.noise(xy, b.m('MULTIPLY', t, 0.03), 0.11, 4, 0.55).outputs["Fac"]
    col = b.mix(col, C("reef_dark"), b.m('MULTIPLY', b.m('MULTIPLY', r, b.mr(npatch, 0.42, 0.58)), 0.55))
    # ---- caustics (moving light lines, shallows)
    wv = b.v('ADD', xy, b.comb(b.m('MULTIPLY', t, 0.3), b.m('MULTIPLY', t, 0.17), 0.0))
    v1 = b.vor(wv, b.m('MULTIPLY', t, 0.35), 0.55); v2 = b.vor(b.v('ADD', xy, (7.3, 3.1, 0.0)), b.m('ADD', b.m('MULTIPLY', t, -0.45), 9.0), 0.95)
    caus = b.m('MAXIMUM', b.mr(v1.outputs["Distance"], 0.10, 0.0), b.m('MULTIPLY', b.mr(v2.outputs["Distance"], 0.09, 0.0), 0.8))
    cw = b.m('MULTIPLY', b.mr(d, 3.0, 0.15, 0.0, 1.0), b.mr(s, 0.0, 1.5))
    col = b.mix(col, C("caustic"), b.m('MULTIPLY', b.m('MULTIPLY', caus, cw), b.m('MULTIPLY', P("caustics"), 0.4)))
    # ---- shore foam: swash front + lace + contact line + travelling breaker lines
    nsw = b.noise(xy, b.m('ADD', b.m('MULTIPLY', t, 0.05), 3.0), 0.09, 2, 0.5).outputs["Fac"]
    cyc = b.mr(b.m('SINE', b.m('ADD', b.m('MULTIPLY', t, b.m('DIVIDE', 6.28319, P("swash_period"))), b.m('MULTIPLY', nsw, 7.0))), -1.0, 1.0)
    f = b.m('ADD', 0.4, b.m('MULTIPLY', cyc, P("swash_reach")))
    xx = b.m('SUBTRACT', s, f)
    rag = b.noise(xy, b.m('MULTIPLY', t, 0.3), 1.4, 3, 0.55).outputs["Fac"]
    ragm = b.mr(rag, 0.30, 0.52)
    front = b.m('MULTIPLY', b.m('MULTIPLY', b.mr(xx, -0.05, 0.10), b.mr(xx, 1.0, 0.35)), ragm)
    lacev = b.vor(xy, b.m('MULTIPLY', t, 0.5), 1.5)
    lace = b.m('MULTIPLY', b.m('MULTIPLY', b.mr(lacev.outputs["Distance"], 0.12, 0.02), b.mr(xx, 0.0, -2.4)), b.mr(s, -0.3, 0.2))
    contact = b.m('MULTIPLY', b.mr(s, 1.0, 0.0), b.mr(rag, 0.28, 0.5))
    nj = b.noise(xy, b.m('MULTIPLY', t, 0.04), 0.05, 2, 0.5).outputs["Fac"]
    jb = b.m('MULTIPLY', b.m('SUBTRACT', nj, 0.5), 7.5)
    phb = b.m('ADD', b.m('ADD', b.m('MULTIPLY', s, b.m('DIVIDE', 6.28319, P("breaker_len"))),
                         b.m('MULTIPLY', t, b.m('DIVIDE', 6.28319, P("breaker_period")))), jb)
    raw = b.mr(b.m('SINE', phb), -1.0, 1.0)
    envs = b.m('MULTIPLY', b.mr(s, 0.0, 1.2), b.mr(s, P("breaker_reach"), b.m('MULTIPLY', P("breaker_reach"), 0.3)))
    lines = b.m('MULTIPLY', b.mr(b.m('ADD', raw, b.m('MULTIPLY', b.m('SUBTRACT', rag, 0.5), 0.6)), 0.90, 0.98), envs)
    shoreF = b.m('MULTIPLY', b.m('MAXIMUM', b.m('MAXIMUM', b.m('MULTIPLY', front, 0.95), b.m('MULTIPLY', lace, 0.8)),
                                 b.m('MAXIMUM', b.m('MULTIPLY', contact, 0.8), b.m('MULTIPLY', lines, 0.9))), P("shore_foam"))
    # ---- crest foam + open-water streaks
    ncr = b.noise(xy, b.m('MULTIPLY', t, 0.4), 0.6, 3, 0.5).outputs["Fac"]
    cf = b.m('MULTIPLY', b.m('MULTIPLY', b.mr(h, P("crest_lo"), P("crest_hi")), b.mr(ncr, 0.28, 0.5)),
             b.m('MULTIPLY', P("crest_foam"), b.mr(d, 0.3, 2.5, 0.4, 1.0)))
    wx, wy = wind; px_ = b.m('SUBTRACT', b.m('MULTIPLY', sy, wx), b.m('MULTIPLY', sx, wy)); al = b.m('MULTIPLY_ADD', sx, wx, b.m('MULTIPLY', sy, wy))
    sv = b.comb(b.m('MULTIPLY', px_, 1.0), b.m('MULTIPLY', b.m('SUBTRACT', al, b.m('MULTIPLY', t, 0.6)), 0.12), 0.0)
    sn1 = b.noise(sv, b.m('MULTIPLY', t, 0.05), 0.9, 4, 0.55).outputs["Fac"]
    sv2 = b.comb(b.m('MULTIPLY', px_, 1.7), b.m('MULTIPLY', b.m('SUBTRACT', al, b.m('MULTIPLY', t, 0.9)), 0.2), 3.0)
    sn2 = b.noise(sv2, b.m('MULTIPLY', t, 0.07), 0.9, 3, 0.5).outputs["Fac"]
    stk = b.m('MULTIPLY', b.m('MAXIMUM', b.mr(sn1, 0.60, 0.68), b.m('MULTIPLY', b.mr(sn2, 0.62, 0.69), 0.7)),
              b.m('MULTIPLY', b.mr(d, 2.5, 9.0, 0.35, 1.0), P("streaks")))
    F = b.m('MULTIPLY', b.m('MAXIMUM', b.m('MAXIMUM', shoreF, cf), stk), P("foam_strength"), clamp=True)
    col = b.mix(col, C("foam"), F)
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
    col = b.mix(col, C("sky"), b.m('MULTIPLY', lw.outputs["Facing"], 0.22))
    # ---- sparkles
    sv3 = b.vor(xy, b.m('MULTIPLY', t, 0.9), 2.0, 'F1')
    star = b.mr(sv3.outputs["Distance"], 0.10, 0.02)
    gate = b.mr(b.noise(xy, b.m('MULTIPLY', t, 0.2), 0.35, 2, 0.5).outputs["Fac"], 0.45, 0.62)
    spk = b.m('MULTIPLY', b.m('MULTIPLY', star, gate), b.m('MULTIPLY', b.mr(h, -0.1, 0.5, 0.25, 1.0), P("sparkle")))
    # ---- alpha
    a0 = b.mr(d, 0.0, P("alpha_depth"), P("alpha_shallow"), P("alpha_deep"), smooth=True)
    a0 = b.m('MULTIPLY', a0, b.m('SUBTRACT', 1.0, b.m('MULTIPLY', r, 0.2)))
    alpha = b.m('MAXIMUM', a0, b.m('MULTIPLY', F, 0.97), clamp=True)
    alpha = b.m('MAXIMUM', alpha, b.m('MULTIPLY', spk, 0.5), clamp=True)
    # ---- principled
    L = nt.links
    L.new(col, bs.inputs["Base Color"]); L.new(alpha, bs.inputs["Alpha"])
    L.new(b.mr(F, 0.0, 1.0, P("roughness"), 0.85), bs.inputs["Roughness"])
    bs.inputs["Specular IOR Level"].default_value = 0.6
    ec = b.mix(col, C("sparkle"), b.mr(spk, 0.0, 0.5))
    L.new(ec, bs.inputs["Emission Color"])
    em = b.m('ADD', b.m('MULTIPLY', spk, 3.0), b.m('MULTIPLY', b.m('MULTIPLY', caus, cw), b.m('MULTIPLY', P("caustics"), 0.12)))
    L.new(em, bs.inputs["Emission Strength"])
    rip = b.noise(xy, b.m('MULTIPLY', t, 0.45), 1.1, 3, 0.55).outputs["Fac"]
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Distance"].default_value = 0.2
    L.new(P("bump"), bp.inputs["Strength"]); L.new(b.m('MAXIMUM', rip, b.m('MULTIPLY', F, 0.8)), bp.inputs["Height"]); L.new(bp.outputs[0], bs.inputs["Normal"])
    # ---- border fade into emissive horizon colour
    er = b.m('MAXIMUM', b.m('MULTIPLY', b.m('ABSOLUTE', sx), 1.0/hx), b.m('MULTIPLY', b.m('ABSOLUTE', sy), 1.0/hy))
    fade = b.mr(er, P("fade_start"), 1.0, 0.0, 1.0, smooth=True)
    emi = nt.nodes.new("ShaderNodeEmission"); L.new(C("horizon_start"), emi.inputs["Color"])
    ms = nt.nodes.new("ShaderNodeMixShader"); L.new(fade, ms.inputs[0]); L.new(bs.outputs[0], ms.inputs[1]); L.new(emi.outputs[0], ms.inputs[2])
    L.new(ms.outputs[0], out.inputs["Surface"])
    _set_blend(m); return m

def _seabed_material(hx, hy):
    m, nt, bs, out = _new_mat("ISL_Seabed"); b = _B(nt); P, C = b.val, b.rgb; L = nt.links
    t = _time(nt); obj = nt.nodes.new("ShaderNodeTexCoord").outputs["Object"]; xy = b.v('MULTIPLY', obj, (1.0, 1.0, 0.0))
    s, d, r = b.attr("shore"), b.attr("depth"), b.attr("reef")
    n1 = b.noise(xy, 0.0, 0.7, 5, 0.6).outputs["Fac"]
    sand = b.ramp([_lin(COLORS["sand_a"]), _lin(COLORS["sand_b"])], [0.3, 0.7], name="R_sand"); L.new(n1, sand.inputs[0])
    dn = b.mr(d, 0.0, 11.0, 0.0, 1.0)
    col = b.mix(sand.outputs[0], C("sand_deep"), b.mr(dn, 0.0, 0.35), 'MIX')
    col = b.mix(col, C("sea_floor"), b.mr(dn, 0.3, 0.9))
    # coral / algae patches on reef
    n2 = b.noise(xy, 0.0, 0.33, 4, 0.55).outputs["Fac"]
    cor = b.ramp([(0.80, 0.30, 0.25), (0.22, 0.45, 0.16), (0.45, 0.22, 0.45), (0.90, 0.55, 0.15)], [0.15, 0.4, 0.62, 0.85], name="R_coral")
    L.new(b.noise(xy, 4.0, 0.9, 2, 0.5).outputs["Fac"], cor.inputs[0])
    col = b.mix(col, cor.outputs[0], b.m('MULTIPLY', b.mr(n2, 0.40, 0.56), b.m('MULTIPLY', r, 0.95)))
    # caustics on the floor
    wv = b.v('ADD', xy, b.comb(b.m('MULTIPLY', t, 0.3), b.m('MULTIPLY', t, 0.17), 0.0))
    v1 = b.vor(wv, b.m('MULTIPLY', t, 0.35), 0.55); v2 = b.vor(b.v('ADD', xy, (7.3, 3.1, 0.0)), b.m('ADD', b.m('MULTIPLY', t, -0.45), 9.0), 0.95)
    caus = b.m('MAXIMUM', b.mr(v1.outputs["Distance"], 0.12, 0.0), b.m('MULTIPLY', b.mr(v2.outputs["Distance"], 0.10, 0.0), 0.8))
    cw = b.m('MULTIPLY', b.mr(d, 4.0, 0.2, 0.0, 1.0), b.mr(s, 0.0, 1.0))
    col = b.mix(col, C("caustic"), b.m('MULTIPLY', b.m('MULTIPLY', caus, cw), b.m('MULTIPLY', P("caustics"), 0.7)))
    L.new(col, bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 1.0; bs.inputs["Specular IOR Level"].default_value = 0.0
    return m

def _horizon_material(hx, hy):
    m, nt, bs, out = _new_mat("ISL_Ocean_Horizon"); nt.nodes.remove(bs); b = _B(nt); P, C = b.val, b.rgb
    obj = nt.nodes.new("ShaderNodeTexCoord").outputs["Object"]; sx, sy, _ = b.sep(obj)
    er = b.m('MAXIMUM', b.m('MULTIPLY', b.m('ABSOLUTE', sx), 1.0/hx), b.m('MULTIPLY', b.m('ABSOLUTE', sy), 1.0/hy))
    f = b.mr(er, 1.0, P("horizon_far"), 0.0, 1.0, smooth=True)
    col = b.mix(C("horizon_start"), C("horizon_end"), f)
    em = nt.nodes.new("ShaderNodeEmission"); nt.links.new(col, em.inputs["Color"]); nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m

# =====================================================================================
# public API
# =====================================================================================
def _purge(names):
    for n in names:
        ob = bpy.data.objects.get(n)
        if ob:
            me = ob.data; bpy.data.objects.remove(ob, do_unlink=True)
            if me and me.users == 0: bpy.data.meshes.remove(me)

def apply_tunables():
    """push the current TUNE / COLORS dicts into existing ocean materials and the wave node group"""
    trees = [bpy.data.node_groups.get(GN_NAME)] + [getattr(bpy.data.materials.get(n), "node_tree", None)
             for n in ("ISL_Ocean_Water", "ISL_Seabed", "ISL_Ocean_Horizon")]
    for nt in trees:
        if nt is None: continue
        for n in nt.nodes:
            if n.name.startswith("P_") and n.name[2:] in TUNE: n.outputs[0].default_value = TUNE[n.name[2:]]
            elif n.name.startswith("C_") and n.name[2:] in COLORS: n.outputs[0].default_value = (*_lin(COLORS[n.name[2:]]), 1.0)
            elif n.name == "R_depth":
                for e, k in zip(n.color_ramp.elements, ("shallow", "mid", "deep", "navy")): e.color = (*_lin(COLORS[k]), 1.0)
            elif n.name == "R_sand":
                for e, k in zip(n.color_ramp.elements, ("sand_a", "sand_b")): e.color = (*_lin(COLORS[k]), 1.0)

def set_ocean_preset(name):
    """'calm' | 'tropical' (default) | 'stormy'. Resets to the base look, applies the preset, updates a built ocean live."""
    if name not in PRESETS: raise ValueError("unknown preset %r, use %s" % (name, list(PRESETS)))
    TUNE.update(_BASE_TUNE); COLORS.update(_BASE_COLORS)
    tu, co = PRESETS[name]; TUNE.update(tu); COLORS.update(co); apply_tunables(); return name

def setup_eevee_water(scene, refraction=False, samples=64):
    """Optional EEVEE flags for the water (Blender 5.x). Not called by build_ocean."""
    try: scene.render.engine = 'BLENDER_EEVEE'
    except Exception: pass
    ee = scene.eevee
    for a, v in (("use_shadows", True), ("taa_render_samples", samples), ("use_raytracing", bool(refraction)), ("use_fast_gi", False)):
        try: setattr(ee, a, v)
        except Exception: pass
    m = bpy.data.materials.get("ISL_Ocean_Water")
    if m:
        _set_blend(m)
        for a, v in (("use_screen_refraction", bool(refraction)), ("use_raytrace_refraction", bool(refraction))):
            try: setattr(m, a, v)
            except Exception: pass

def build_ocean(coll, json_path, extent_m=(520, 460), sea_z=-0.45, seed=7):
    """Builds ISL_Ocean (wave modifier), ISL_Seabed, ISL_Ocean_Horizon in `coll` (None = scene collection). Returns dict."""
    rng = random.Random(seed)
    if coll is None: coll = bpy.context.scene.collection
    F = _Fields(json_path); hx, hy = extent_m[0]/2.0, extent_m[1]/2.0
    _purge(("ISL_Ocean", "ISL_Seabed", "ISL_Ocean_Horizon"))
    fx, fy = F.half[0] + MESH["fine_margin_m"], F.half[1] + MESH["fine_margin_m"]
    xs = _axis(fx, hx, MESH["fine_m"], MESH["far_m"], MESH["grow"]); ys = _axis(fy, hy, MESH["fine_m"], MESH["far_m"], MESH["grow"])
    ocean = _grid_object("ISL_Ocean", xs, ys, F, lambda S, D: np.full_like(S, sea_z), MESH["cut_inside_m"], coll)
    ng = _build_waves_group(hx, hy, rng)
    md = ocean.modifiers.new("OceanWaves", 'NODES'); md.node_group = ng
    ocean.location = (0, 0, 0); ocean.visible_shadow = False
    wa = rng.uniform(0, 2*math.pi); wind = (math.cos(wa), math.sin(wa))
    wm = _water_material(hx, hy, wind); ocean.data.materials.append(wm)
    # seabed
    sxs = _axis(fx, hx, MESH["seabed_fine_m"], MESH["seabed_far_m"], MESH["seabed_grow"]); sys_ = _axis(fy, hy, MESH["seabed_fine_m"], MESH["seabed_far_m"], MESH["seabed_grow"])
    rel = TERRAIN["seabed_relief"]
    seabed = _grid_object("ISL_Seabed", sxs, sys_, F, lambda S, D: sea_z - 0.05 - D*rel + np.minimum(S, 0)*0.0, MESH["cut_inside_m"], coll)
    seabed.data.materials.append(_seabed_material(hx, hy)); seabed.visible_shadow = True
    # horizon skirt
    fr = MESH["horizon_m"]
    co = [(-hx, -hy, sea_z), (hx, -hy, sea_z), (hx, hy, sea_z), (-hx, hy, sea_z), (-fr, -fr, sea_z), (fr, -fr, sea_z), (fr, fr, sea_z), (-fr, fr, sea_z)]
    fc = [(4, 5, 1, 0), (5, 6, 2, 1), (6, 7, 3, 2), (7, 4, 0, 3)]
    hm = bpy.data.meshes.new("ISL_Ocean_Horizon"); hm.from_pydata(co, [], fc); hm.update()
    hor = bpy.data.objects.new("ISL_Ocean_Horizon", hm); coll.objects.link(hor); hor.visible_shadow = False
    hm.materials.append(_horizon_material(hx, hy))
    for ob in (ocean, seabed, hor): ob["generator"] = "isl_ocean"
    apply_tunables()
    return dict(ocean=ocean, seabed=seabed, horizon=hor, waves=ng, materials=dict(water=wm, seabed=seabed.data.materials[0], horizon=hm.materials[0]),
                verts=dict(ocean=len(ocean.data.vertices), seabed=len(seabed.data.vertices)))
