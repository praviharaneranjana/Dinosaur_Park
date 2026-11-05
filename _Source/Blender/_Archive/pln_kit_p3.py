"""Dino Park Tycoon - PLN plant kit v01.  exec after trn_common.py, trn_hq.py, trn_hq2.py, trn_anim.py.

Every plant is ONE mesh object (+ optional ink-outline child for woody/solid parts, + optional *_Ground decal child).
Per-vertex data (kept on the mesh, exported to Unity as the colour attribute 'WindData' = R bend, G flutter, B phase):
  bend    0 at the root -> ~1 at the crown / tip   (how far the main sway moves this vertex)
  flutter 0 at a leaf / petal base -> 1 at its tip (fast small leaf motion)
  phase   0..1 random per part                      (so leaves / fronds / blades never move in lock-step)
  tint, ao                                          (painted colour variation / leaf-mass self-shadow, used by the materials)
Motion in Blender = geometry-nodes modifier 'PLN_Motion' driven by Scene Time (no keyframes, loops forever, renders in EEVEE).
Motion presets (MOTION dict) give each plant family its own behaviour: wind sway + gusts, leaf flutter, underwater
travelling waves (kelp / seaweed), floating bob (lily pads, duckweed), or rigid (logs, stumps, coral, cactus).
"""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, noise

PL_LAYERS = ("bend", "flutter", "phase", "tint", "ao", "cnx", "cny", "cnz", "cnw")
UPZ = Vector((0, 0, 1))

# ---------------------------------------------------------------- motion presets (metres / Hz-ish)
#            amp   gust  freq  wave_k flutter bob   droop
MOTION = {
    "tree":      (0.10, 0.9, 0.9, 0.0, 0.030, 0.0, 1.0),
    "tree_big":  (0.16, 0.9, 0.6, 0.0, 0.035, 0.0, 1.0),
    "conifer":   (0.08, 0.8, 0.8, 0.0, 0.020, 0.0, 1.0),
    "palm":      (0.22, 1.0, 0.8, 0.0, 0.060, 0.0, 1.0),
    "shrub":     (0.04, 0.9, 1.3, 0.0, 0.025, 0.0, 1.0),
    "fern":      (0.05, 0.9, 1.2, 0.0, 0.040, 0.0, 1.0),
    "grass":     (0.07, 1.2, 1.9, 0.0, 0.020, 0.0, 1.0),
    "reed":      (0.12, 1.1, 1.4, 0.0, 0.030, 0.0, 1.0),
    "flower":    (0.05, 1.0, 1.7, 0.0, 0.030, 0.0, 1.0),
    "hedge":     (0.004, 0.5, 1.0, 0.0, 0.010, 0.0, 0.0),
    "deadwood":  (0.015, 0.6, 1.2, 0.0, 0.0,   0.0, 0.0),
    "kelp":      (0.34, 0.5, 0.45, 1.5, 0.070, 0.0, 1.0),
    "seaweed":   (0.15, 0.5, 0.6, 2.6, 0.050, 0.0, 1.0),
    "coral_fan": (0.03, 0.4, 0.5, 1.0, 0.010, 0.0, 0.0),
    "float":     (0.0,  0.0, 1.0, 0.0, 0.006, 0.010, 0.0),
}

def make_motion_group():
    ng = bpy.data.node_groups.get("PLN_Motion")
    if ng: return ng
    ng = bpy.data.node_groups.new("PLN_Motion", 'GeometryNodeTree')
    itf = ng.interface
    itf.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    for nm, dv in (("Amp",0.1),("Gust",0.9),("Freq",1.0),("WaveK",0.0),("Flutter",0.03),("Bob",0.0),("Droop",1.0),("DirX",1.0),("DirY",0.25)):
        s = itf.new_socket(nm, in_out='INPUT', socket_type='NodeSocketFloat'); s.default_value = dv
    itf.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N = ng.nodes; Lk = ng.links
    gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
    def M(op, a, b=None, c=None):
        n = N.new("ShaderNodeMath"); n.operation = op
        for i, x in enumerate((a, b, c)):
            if x is None: continue
            if isinstance(x, (int, float)): n.inputs[i].default_value = float(x)
            else: Lk.new(x, n.inputs[i])
        return n.outputs[0]
    def A(name):
        n = N.new("GeometryNodeInputNamedAttribute"); n.data_type = 'FLOAT'; n.inputs["Name"].default_value = name; return n.outputs["Attribute"]
    def VM(op, a, b=None, s=None):
        n = N.new("ShaderNodeVectorMath"); n.operation = op; Lk.new(a, n.inputs[0])
        if b is not None:
            if isinstance(b, tuple): n.inputs[1].default_value = b
            else: Lk.new(b, n.inputs[1])
        if s is not None:
            if isinstance(s, (int, float)): n.inputs["Scale"].default_value = s
            else: Lk.new(s, n.inputs["Scale"])
        return n.outputs[0]
    def NZ(vec, w, scale, detail=2.0):
        n = N.new("ShaderNodeTexNoise"); n.noise_dimensions = '4D'; n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail
        Lk.new(vec, n.inputs["Vector"]); Lk.new(w, n.inputs["W"]); return n
    st = N.new("GeometryNodeInputSceneTime").outputs["Seconds"]
    pos = N.new("GeometryNodeInputPosition").outputs[0]
    sp = N.new("ShaderNodeSeparateXYZ"); Lk.new(pos, sp.inputs[0]); pz = sp.outputs[2]
    bend, flut, ph = A("bend"), A("flutter"), A("phase")
    t = M('MULTIPLY', st, gi.outputs["Freq"])
    ph6 = M('MULTIPLY', ph, 6.2832)
    kz = M('MULTIPLY', pz, gi.outputs["WaveK"])
    w1 = M('SINE', M('SUBTRACT', M('ADD', M('MULTIPLY', t, 6.2832*0.55), M('MULTIPLY', ph6, 0.35)), kz))
    w2 = M('SINE', M('SUBTRACT', M('ADD', M('MULTIPLY', t, 6.2832*0.92), M('MULTIPLY', ph6, 0.6)), M('MULTIPLY', kz, 1.3)))
    gn = NZ(VM('SCALE', pos, s=0.22), M('MULTIPLY', st, M('MULTIPLY', gi.outputs["Freq"], 0.32)), 1.0)
    g = M('MULTIPLY', M('SUBTRACT', gn.outputs[0], 0.5), 2.0)
    gg = M('MULTIPLY', g, gi.outputs["Gust"])
    ab = M('MULTIPLY', gi.outputs["Amp"], bend)
    ox = M('MULTIPLY', ab, M('ADD', M('ADD', M('MULTIPLY', w1, 0.6), gg), 0.22))
    oy = M('MULTIPLY', ab, M('MULTIPLY', w2, 0.45))
    dx, dy = gi.outputs["DirX"], gi.outputs["DirY"]
    rx = M('SUBTRACT', M('MULTIPLY', ox, dx), M('MULTIPLY', oy, dy))
    ry = M('ADD', M('MULTIPLY', ox, dy), M('MULTIPLY', oy, dx))
    hs = M('ADD', M('MULTIPLY', rx, rx), M('MULTIPLY', ry, ry))
    oz = M('MULTIPLY', M('DIVIDE', hs, M('MAXIMUM', M('MULTIPLY', pz, 2.0), 0.3)), M('MULTIPLY', gi.outputs["Droop"], -1.0))
    bob = M('MULTIPLY', gi.outputs["Bob"], M('SINE', M('ADD', M('MULTIPLY', st, 1.3), ph6)))
    oz = M('ADD', oz, bob)
    cm = N.new("ShaderNodeCombineXYZ"); Lk.new(rx, cm.inputs[0]); Lk.new(ry, cm.inputs[1]); Lk.new(oz, cm.inputs[2])
    fl = NZ(VM('ADD', VM('SCALE', pos, s=3.0), None) if False else VM('SCALE', pos, s=3.0), M('ADD', M('MULTIPLY', st, M('MULTIPLY', gi.outputs["Freq"], 2.2)), ph6), 1.0)
    fv = VM('SCALE', VM('SUBTRACT', fl.outputs["Color"], (0.5, 0.5, 0.5)), s=M('MULTIPLY', M('MULTIPLY', flut, gi.outputs["Flutter"]), 2.0))
    off = VM('ADD', cm.outputs[0], fv)
    spn = N.new("GeometryNodeSetPosition"); Lk.new(gi.outputs["Geometry"], spn.inputs["Geometry"]); Lk.new(off, spn.inputs["Offset"])
    Lk.new(spn.outputs[0], go.inputs[0])
    return ng

def add_motion(ob, preset, scale=1.0):
    if preset is None: return None
    ng = make_motion_group(); md = ob.modifiers.new("PLN_Motion", 'NODES'); md.node_group = ng
    vals = MOTION[preset]
    for nm, v in zip(("Amp","Gust","Freq","WaveK","Flutter","Bob","Droop"), vals):
        sock = [s for s in ng.interface.items_tree if getattr(s, "name", "") == nm and s.in_out == 'INPUT'][0]
        val = float(v*scale if nm in ("Amp",) else v)
        try: getattr(md.properties.inputs, sock.identifier).value = val
        except Exception: md[sock.identifier] = val
    ob["motion"] = preset
    return md

# ---------------------------------------------------------------- plant container
class Plant:
    def __init__(self, name, H, R=1.0, seed=1):
        self.name = name; self.H = H; self.R = R; self.rnd = random.Random(seed)
        self.bm = bmesh.new()
        for l in PL_LAYERS: self.bm.verts.layers.float.new(l)
        self.L = {l: self.bm.verts.layers.float[l] for l in PL_LAYERS}
        self.uv = self.bm.loops.layers.uv.new("LeafUV")
        self.keys = []; self.solid = []
    def slot(self, key):
        if key not in self.keys: self.keys.append(key)
        return self.keys.index(key)
    def auto_bend(self, co):
        z = max(0.0, co[2])/self.H; r = math.hypot(co[0], co[1])/max(self.R, 0.1)
        return min(1.6, z**1.6 + 0.3*r*z)
    def v(self, co, bend=None, flutter=0.0, phase=0.0, tint=0.5, ao=1.0, cn=None, cnw=0.0):
        vt = self.bm.verts.new(co); L = self.L
        vt[L["bend"]] = self.auto_bend(co) if bend is None else bend
        vt[L["flutter"]] = flutter; vt[L["phase"]] = phase; vt[L["tint"]] = tint; vt[L["ao"]] = ao
        if cn is not None:
            vt[L["cnx"]], vt[L["cny"]], vt[L["cnz"]] = cn.x, cn.y, cn.z; vt[L["cnw"]] = cnw
        return vt
    def face(self, vs, key, solid=False, uvs=None):
        try: f = self.bm.faces.new(vs)
        except ValueError: return None
        f.material_index = self.slot(key); f.smooth = True
        if uvs:
            for lp, uv in zip(f.loops, uvs): lp[self.uv].uv = uv
        if solid: self.solid.append(f)
        return f

# ---------------------------------------------------------------- primitives
def frames(pts):
    n = len(pts); T = []
    for i in range(n):
        d = pts[min(i+1, n-1)] - pts[max(i-1, 0)]
        T.append(d.normalized() if d.length > 1e-9 else UPZ.copy())
    ref = UPZ if abs(T[0].z) < 0.95 else Vector((1, 0, 0))
    Nn = T[0].cross(ref).normalized(); out = []
    for i in range(n):
        Nn = (Nn - T[i]*Nn.dot(T[i]))
        Nn = Nn.normalized() if Nn.length > 1e-9 else T[i].orthogonal().normalized()
        out.append((T[i], Nn, T[i].cross(Nn)))
    return out

def tube(P, pts, radii, key, sides=8, solid=True, bend=None, rough=0.0, seed=0, lobes=None, cap=True, tint=0.5, phase=None, flutter=None, base_cap=False, ribs=None, rings_fn=None):
    """generalised cylinder along pts. lobes=(n, amp, h): buttress / flare lobes near the base. bend: None=auto | float | callable(t)"""
    fr = frames(pts); rings = []; n = len(pts); ph = P.rnd.random() if phase is None else phase
    for i, (p, (T, Nn, B)) in enumerate(zip(pts, fr)):
        t = i/(n-1); ring = []
        for k in range(sides):
            a = 2*math.pi*k/sides; r = radii[i]
            if lobes:
                nl, amp, h = lobes; fall = max(0.0, 1 - (p.z - pts[0].z)/h)**2
                r *= 1 + amp*fall*(abs(math.cos(nl*a/2))**3)
            if rough: r *= 1 + rough*noise.noise(Vector((math.cos(a)*1.3 + seed, math.sin(a)*1.3, p.z*2.2 + i*0.13)))
            if ribs: r *= 1 - ribs[1]*(1 - abs(math.cos(ribs[0]*a/2)))
            if rings_fn: r *= rings_fn(t, a)
            co = p + (Nn*math.cos(a) + B*math.sin(a))*r
            b = bend(t) if callable(bend) else bend
            ring.append(P.v(co, bend=b, phase=ph, tint=tint, flutter=(flutter(t) if callable(flutter) else (flutter or 0.0))))
        rings.append(ring)
    fs = []
    for i in range(n-1):
        for k in range(sides):
            q = (k+1) % sides
            f = P.face((rings[i][k], rings[i][q], rings[i+1][q], rings[i+1][k]), key, solid)
            if f: fs.append(f)
    if cap and radii[-1] > 1e-4:
        tip = pts[-1] + fr[-1][0]*radii[-1]*0.4
        b = bend(1.0) if callable(bend) else bend
        c = P.v(tip, bend=b, phase=ph, tint=tint)
        for k in range(sides):
            f = P.face((rings[-1][k], rings[-1][(k+1) % sides], c), key, solid)
            if f: fs.append(f)
    if base_cap:
        c = P.v(pts[0] - fr[0][0]*0.01, bend=(bend(0.0) if callable(bend) else bend), phase=ph, tint=tint)
        for k in range(sides):
            f = P.face((rings[0][(k+1) % sides], rings[0][k], c), key, solid)
            if f: fs.append(f)
    return fs

def path(start, d, length, segs=6, curve=0.0, wob=0.0, seed=0, up=None):
    """curved branch centre-line: starts along d, bends toward 'up' by curve (negative = droop)"""
    up = up or UPZ; pts = [Vector(start)]; d = Vector(d).normalized(); step = length/segs
    for i in range(segs):
        t = (i+1)/segs
        d = (d + up*curve*step*1.6 + Vector((noise.noise(Vector((seed, t*3, 0))), noise.noise(Vector((t*3, seed, 1))), noise.noise(Vector((0, seed, t*3)))))*wob).normalized()
        pts.append(pts[-1] + d*step)
    return pts

def _norm_profile(fn):
    m = max(fn(i/200) for i in range(201)) or 1.0
    return lambda t: fn(t)/m
SHAPES = {
    "ovate":   _norm_profile(lambda t: (t**0.55)*((1-t)**0.85)),
    "round":   _norm_profile(lambda t: (t**0.45)*((1-t)**0.55)),
    "lance":   _norm_profile(lambda t: (t**0.5)*((1-t)**1.3)),
    "petal":   _norm_profile(lambda t: (t**0.4)*((1-t)**0.45)),
    "blade":   lambda t: max(0.02, (1-t)**0.75),
    "strap":   lambda t: max(0.03, 0.75 + 0.25*math.sin(t*math.pi*0.9) - 0.7*t**4),
    "spray":   _norm_profile(lambda t: (t**0.35)*((1-t)**0.9)),
    "fan":     lambda t: max(0.04, 0.08 + 0.92*t**1.1),
    "heart":   _norm_profile(lambda t: (t**0.3)*((1-t)**0.35)),
    "clover":  _norm_profile(lambda t: (t**0.8)*((1-t)**0.35)),
}
def leaf(P, base, d, up, L, W, key, shape="ovate", nu=2, nv=5, fold=0.25, curl=0.0, droop=0.0, tint=0.5, phase=None, flut=1.0,
         bend=None, ao=1.0, cn=None, cnw=0.0, lobes=0, lobe_depth=0.55, wave=0.0, wave_n=6.0, twist=0.0):
    """one 3D leaf / petal / frond card. lobes>0 = pinnate leaflets cut into the outline (ferns, palms, conifer sprays)."""
    d = Vector(d).normalized(); up = Vector(up)
    side = d.cross(up)
    if side.length < 1e-6: side = d.orthogonal()
    side.normalize(); upn = side.cross(d).normalized()
    ph = P.rnd.random() if phase is None else phase
    prof = SHAPES[shape]; b0 = P.auto_bend(base) if bend is None else bend
    grid = []; nvv = nv if not lobes else max(nv, lobes*4)
    for j in range(nvv+1):
        t = j/nvv; w = W*max(0.05 if j == 0 else 0.015, prof(t))
        if lobes:
            s = abs(math.sin(t*math.pi*lobes))**0.7
            w *= (1 - lobe_depth) + lobe_depth*s
        tw = twist*t; ct, st_ = math.cos(tw), math.sin(tw)
        row = []
        for i in range(2*nu+1):
            u = (i - nu)/nu
            su = side*ct + upn*st_; uu = upn*ct - side*st_
            wv = wave*w*math.sin(t*wave_n*math.pi + u*1.2)*abs(u)
            off = d*(L*t) + su*(u*w) + uu*(fold*abs(u)*w + curl*L*t*t + wv) - UPZ*droop*L*t*t
            co = base + off
            nrm = None
            if cn is not None: nrm = (co - cn).normalized()
            row.append(P.v(co, bend=b0 + (0.15*t if bend is None else 0.0), flutter=flut*t, phase=ph, tint=tint, ao=ao, cn=nrm, cnw=cnw))
        grid.append(row)
    fs = []
    for j in range(nvv):
        for i in range(2*nu):
            uvs = [((i-nu)/nu, j/nvv), ((i+1-nu)/nu, j/nvv), ((i+1-nu)/nu, (j+1)/nvv), ((i-nu)/nu, (j+1)/nvv)]
            f = P.face((grid[j][i], grid[j][i+1], grid[j+1][i+1], grid[j+1][i]), key, False, uvs)
            if f: fs.append(f)
    return fs

def clump(P, c, R, n, key, leafL, leafW, shape="ovate", flat=0.7, polar_max=118, fold=0.3, droop=0.25, tint=None, cnw=0.75,
          inner_key=None, lobes=0, seed=0, ao_lo=0.62, shingle=0.45, nv=5):
    """layered leaf mass: n big leaves shingled over an ellipsoid shell (outward + downward), custom normals from the
    mass centre (soft painted dome shading), optional dark inner core so no sky shows through."""
    rnd = random.Random(seed); c = Vector(c); fs = []
    tc = rnd.uniform(0.25, 0.75) if tint is None else tint
    cnc = c - Vector((0, 0, R*flat*0.35))
    for k in range(n):
        f = (k + 0.5)/n; pol = math.radians(polar_max)*math.sqrt(f)*rnd.uniform(0.92, 1.04)
        az = k*2.39996 + rnd.uniform(-0.25, 0.25)
        nr = Vector((math.sin(pol)*math.cos(az), math.sin(pol)*math.sin(az), math.cos(pol)))
        pos = c + Vector((nr.x*R, nr.y*R, nr.z*R*flat))*rnd.uniform(0.72, 0.9)
        dm = Vector((math.cos(pol)*math.cos(az), math.sin(pol*0 + 1)*0 + math.cos(pol)*math.sin(az), -math.sin(pol)))
        if dm.length < 1e-6: dm = Vector((math.cos(az), math.sin(az), 0))
        d = (dm.normalized() + nr*shingle + Vector((rnd.uniform(-.15, .15), rnd.uniform(-.15, .15), 0))).normalized()
        L = leafL*rnd.uniform(0.85, 1.15)*(1 + 0.25*math.sin(pol))
        ao = ao_lo + (1-ao_lo)*(0.5 + 0.5*nr.z)
        fs += leaf(P, pos - d*L*0.12, d, nr, L, leafW*rnd.uniform(0.85, 1.15), key, shape=shape, fold=fold, droop=droop*rnd.uniform(0.6, 1.3),
                   tint=min(1, max(0, tc + rnd.uniform(-0.18, 0.18))), ao=ao, cn=cnc, cnw=cnw, bend=P.auto_bend(c), lobes=lobes, nv=nv)
    if inner_key:
        res = bmesh.ops.create_icosphere(P.bm, subdivisions=2, radius=1.0)
        b0 = P.auto_bend(c); ph = rnd.random()
        for vt in res["verts"]:
            p = vt.co.copy(); vt.co = c + Vector((p.x*R*0.74, p.y*R*0.74, p.z*R*flat*0.7 - R*flat*0.08))
            vt[P.L["bend"]] = b0; vt[P.L["phase"]] = ph; vt[P.L["tint"]] = 0.1; vt[P.L["ao"]] = 0.35 + 0.3*max(0.0, p.z)
            nrm = (vt.co - cnc).normalized(); vt[P.L["cnx"]], vt[P.L["cny"]], vt[P.L["cnz"]] = nrm.x, nrm.y, nrm.z; vt[P.L["cnw"]] = 0.9
        for fc in {f for v in res["verts"] for f in v.link_faces}:
            fc.material_index = P.slot(inner_key); fc.smooth = True; fs.append(fc)
    return fs

def blade(P, base, H, W, ang, lean, key, segs=4, tint=0.5, curl=0.0, bend_scale=1.0, flut=0.6, twist=0.0):
    """grass / reed blade: tapered, curving away by lean, bend = (t)^1.7 of its own length"""
    d0 = Vector((math.cos(ang), math.sin(ang), 0)); ph = P.rnd.random(); rows = []
    side = Vector((-d0.y, d0.x, 0))
    for j in range(segs+1):
        t = j/segs; w = W*max(0.06, (1-t)**0.8)
        p = Vector(base) + UPZ*H*(t - 0.5*lean*lean*t*t) + d0*H*lean*t*t
        sd = side*math.cos(twist*t) + d0*math.sin(twist*t)
        b = bend_scale*t**1.7
        rows.append((P.v(p - sd*w/2, bend=b, flutter=flut*t, phase=ph, tint=tint), P.v(p + sd*w/2 + UPZ*curl*w*t, bend=b, flutter=flut*t, phase=ph, tint=tint)))
    fs = []
    for j in range(segs):
        f = P.face((rows[j][0], rows[j][1], rows[j+1][1], rows[j+1][0]), key, False,
                   [(-1, j/segs), (1, j/segs), (1, (j+1)/segs), (-1, (j+1)/segs)])
        if f: fs.append(f)
    return fs

def lathe(P, prof, key, sides=16, center=(0, 0, 0), ribs=None, solid=True, bend=None, tint=0.5, phase=None, noise_amp=0.0, seed=0, axis=None):
    """surface of revolution: prof = [(r, z)...] bottom->top. ribs=(n, depth) gives cactus / pumpkin ribs."""
    c = Vector(center); ph = P.rnd.random() if phase is None else phase; rings = []
    R = Matrix.Identity(3)
    if axis is not None:
        ax = Vector(axis).normalized(); R = UPZ.rotation_difference(ax).to_matrix()
    for (r, z) in prof:
        ring = []
        for k in range(sides):
            a = 2*math.pi*k/sides; rr = r
            if ribs: rr *= 1 - ribs[1]*(1 - abs(math.cos(ribs[0]*a/2)))**1.0
            if noise_amp: rr *= 1 + noise_amp*noise.noise(Vector((math.cos(a)*2 + seed, math.sin(a)*2, z*3)))
            co = c + R @ Vector((rr*math.cos(a), rr*math.sin(a), z))
            ring.append(P.v(co, bend=(bend(z) if callable(bend) else bend), phase=ph, tint=tint))
        rings.append(ring)
    fs = []
    for i in range(len(rings)-1):
        for k in range(sides):
            q = (k+1) % sides
            f = P.face((rings[i][k], rings[i][q], rings[i+1][q], rings[i+1][k]), key, solid)
            if f: fs.append(f)
    for idx, flip in ((0, True), (-1, False)):
        r, z = prof[idx]
        if r > 1e-4:
            cv = P.v(c + R @ Vector((0, 0, z)), bend=(bend(z) if callable(bend) else bend), phase=ph, tint=tint); rg = rings[idx]
            for k in range(sides):
                vs = (rg[(k+1) % sides], rg[k], cv) if flip else (rg[k], rg[(k+1) % sides], cv)
                f = P.face(vs, key, solid)
                if f: fs.append(f)
    return fs

def ball(P, c, r, key, sub=2, squash=1.0, bend=None, tint=0.5, solid=False, noise_amp=0.0, seed=0, phase=None, flutter=0.0):
    res = bmesh.ops.create_icosphere(P.bm, subdivisions=sub, radius=1.0); c = Vector(c)
    b = P.auto_bend(c) if bend is None else bend; ph = P.rnd.random() if phase is None else phase
    for vt in res["verts"]:
        p = vt.co.copy(); k = 1 + noise_amp*noise.noise(p*2.5 + Vector((seed, 0, 0)))
        vt.co = c + Vector((p.x*r*k, p.y*r*k, p.z*r*squash*k))
        L = P.L; vt[L["bend"]] = b; vt[L["phase"]] = ph; vt[L["tint"]] = tint; vt[L["ao"]] = 1.0; vt[L["flutter"]] = flutter
    fs = list({f for v in res["verts"] for f in v.link_faces})
    for f in fs:
        f.material_index = P.slot(key); f.smooth = True
        if solid: P.solid.append(f)
    return fs

def fiddlehead(P, base, d, R, key, turns=1.6, r_tube=0.012, bend=None):
    """coiled young frond (crozier)"""
    d = Vector(d).normalized(); side = d.cross(UPZ)
    if side.length < 1e-6: side = Vector((1, 0, 0))
    side.normalize(); up = side.cross(d).normalized(); pts = []
    n = 22
    for i in range(n+1):
        t = i/n; a = turns*2*math.pi*t; rr = R*(1 - 0.75*t)
        pts.append(Vector(base) + up*(rr*math.sin(a)) + d*(rr*(1 - math.cos(a))*0.6 + R*0.8*t) )
    return tube(P, pts, [r_tube*(1 - 0.6*i/n) for i in range(n+1)], key, sides=6, solid=False, bend=bend)

# ---------------------------------------------------------------- materials
def plant_mat(name, pal, scale=3.0, stretch=(1, 1, 1), strokes=0.3, ao_amt=0.5, tint_amt=0.45, top=0.35, vein=0.0, rim=0.0, rim_col=None,
              crack=0.0, crack_scale=3.0, crack_stretch=(1, 1, 0.35), edge=None, edge_amt=0.0, rough=0.75, spec=0.25, emit=0.04,
              spots=None, moss=None, moss_amt=0.0, geo_ao=0.0, tipcol=None, tip_amt=0.0, base_dark=0.0):
    m, nt, bs = new_mat(name)
    tc = nt.nodes.new("ShaderNodeTexCoord"); obj = tc.outputs["Object"]
    geo = nt.nodes.new("ShaderNodeNewGeometry"); nz = sep(nt, geo.outputs["Normal"])[2]
    uv = uvmap(nt, "LeafUV"); us = sep(nt, uv); au = mathop(nt, us[0], 0.0, 'ABSOLUTE'); vv = us[1]
    n1 = noise_n(nt, mapping(nt, obj, stretch), scale, 5, 0.6)
    f = mathop(nt, n1.outputs["Fac"], mathop(nt, mathop(nt, attr(nt, "tint"), 0.5, 'SUBTRACT'), tint_amt), 'ADD')
    rp = ramp(nt, pal); nt.links.new(f, rp.inputs[0]); col = rp.outputs[0]
    if strokes:
        s1 = noise_n(nt, mapping(nt, obj, (stretch[0]*2.5, stretch[1]*2.5, stretch[2]*0.6)), scale*1.6, 4, 0.55)
        col = mix(nt, col, s1.outputs["Fac"], float(strokes), 'SOFT_LIGHT')
    if tipcol is not None and tip_amt:
        col = mix(nt, col, tipcol, mathop(nt, maprange(nt, vv, 0.45, 1.0), float(tip_amt)))
    if vein:
        vl = mathop(nt, maprange(nt, au, 0.09, 0.0), maprange(nt, vv, 0.02, 0.15))
        col = mix(nt, col, mathop(nt, col, 0.55) if False else (0.0, 0.0, 0.0), mathop(nt, vl, float(vein*0.35)))
    if rim:
        rc = rim_col or tuple(min(1.0, c*1.35) for c in pal[-1])
        col = mix(nt, col, rc, mathop(nt, maprange(nt, au, 0.7, 1.0), float(rim)))
    if crack:
        vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.feature = 'DISTANCE_TO_EDGE'; vo.inputs["Scale"].default_value = crack_scale
        dn = noise_n(nt, obj, 2.5, 3, 0.5)
        nt.links.new(vadd(nt, mapping(nt, obj, crack_stretch), vmul(nt, dn.outputs["Color"], (0.25, 0.25, 0.25))), vo.inputs["Vector"])
        col = mix(nt, col, (0.02, 0.015, 0.01), mathop(nt, maprange(nt, vo.outputs["Distance"], 0.05, 0.0), float(crack)))
        col = mix(nt, col, (1.0, 0.95, 0.85), mathop(nt, maprange(nt, vo.outputs["Distance"], 0.16, 0.07), float(crack*0.12)), 'SOFT_LIGHT')
    if spots:
        sc_, scol, amt = spots
        vs = nt.nodes.new("ShaderNodeTexVoronoi"); vs.inputs["Scale"].default_value = sc_; nt.links.new(obj, vs.inputs["Vector"])
        col = mix(nt, col, scol, mathop(nt, maprange(nt, vs.outputs["Distance"], 0.22, 0.12), float(amt)))
    if moss:
        nm = noise_n(nt, obj, 3.0, 5, 0.65); rm = ramp(nt, moss); nt.links.new(nm.outputs["Fac"], rm.inputs[0])
        col = mix(nt, col, rm.outputs[0], mathop(nt, maprange(nt, nz, 0.35, 0.8), maprange(nt, nm.outputs["Fac"], 0.62 - 0.25*moss_amt, 0.7 - 0.25*moss_amt)))
    if edge and edge_amt:
        col = mix(nt, col, edge, mathop(nt, maprange(nt, attr(nt, "curv"), 0.15, 0.6), float(edge_amt)))
    if base_dark:
        col = mix(nt, col, (0.02, 0.02, 0.015), mathop(nt, maprange(nt, sep(nt, obj)[2], 0.12, 0.0), float(base_dark)))
    aof = maprange(nt, attr(nt, "ao"), 0.0, 1.0, 1.0 - ao_amt, 1.06)
    if geo_ao:
        ao = nt.nodes.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = 0.3; ao.samples = 12
        aof = mathop(nt, aof, maprange(nt, ao.outputs["AO"], 0.0, 1.0, 1.0 - geo_ao, 1.0))
    col = mix(nt, col, aof, 1.0, 'MULTIPLY') if False else mix(nt, col, (0, 0, 0), mathop(nt, mathop(nt, aof, -1.0), 1.0, 'ADD'))
    if top:
        col = mix(nt, col, (0.95, 0.95, 0.82), mathop(nt, maprange(nt, nz, 0.15, 1.0), float(top)), 'SOFT_LIGHT')
    nt.links.new(col, bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = rough; bs.inputs["Specular IOR Level"].default_value = spec
    if emit:
        nt.links.new(col, bs.inputs["Emission Color"]); bs.inputs["Emission Strength"].default_value = emit
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.25; bp.inputs["Distance"].default_value = 0.01
    nt.links.new(n1.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs[0], bs.inputs["Normal"])
    m.use_backface_culling = False
    return m

def bark_mat(name, pal, crack=0.8, crack_scale=4.0, stretch=(5.0, 5.0, 0.8), moss=None, moss_amt=0.0, edge=(0.6, 0.55, 0.48)):
    return plant_mat(name, pal, scale=2.2, stretch=stretch, strokes=0.45, ao_amt=0.15, tint_amt=0.2, top=0.25, crack=crack, crack_scale=crack_scale,
                     crack_stretch=(stretch[0]*0.22, stretch[1]*0.22, stretch[2]*0.6), edge=edge, edge_amt=0.35, rough=0.85, spec=0.15, emit=0.0,
                     moss=moss, moss_amt=moss_amt, geo_ao=0.45)

# ---------------------------------------------------------------- finish
def plant_finish(P, coll, mats, pos, src, motion, extra=None, outline=True, outline_th=0.009, motion_scale=1.0):
    """bmesh -> mesh object with materials, custom (leaf-mass) normals, WindData colour attribute, motion modifier and an
    ink-outline child (solid/woody faces only, same motion so it follows)."""
    bm = P.bm; bake_curvature(bm)
    solid_idx = set(f.index for f in P.solid if f.is_valid) if False else None
    for f in bm.faces: f.tag = False
    for f in P.solid:
        if f.is_valid: f.tag = True
    sol = [f for f in P.solid if f.is_valid]
    if sol: bmesh.ops.recalc_face_normals(bm, faces=sol)
    tagged = [f.tag for f in bm.faces]
    ob_bm = bm.copy() if (outline and any(tagged)) else None
    bm.normal_update()
    L = P.L; nrm = []
    for v in bm.verts:
        w = v[L["cnw"]]
        if w > 0:
            cnv = Vector((v[L["cnx"]], v[L["cny"]], v[L["cnz"]])); n = (v.normal*(1-w) + cnv*w)
            nrm.append(n.normalized() if n.length > 1e-6 else v.normal.copy())
        else: nrm.append(v.normal.copy())
    me = bpy.data.meshes.new(P.name); bm.to_mesh(me); bm.free()
    for k in P.keys: me.materials.append(mats[k])
    me.shade_smooth()
    try: me.normals_split_custom_set_from_vertices(nrm)
    except Exception as e: print("custom normals:", e)
    _wind_color(me)
    for nm in ("cnx", "cny", "cnz", "cnw"):
        a = me.attributes.get(nm)
        if a: me.attributes.remove(a)
    ob = bpy.data.objects.new(P.name, me); ob.location = pos; coll.objects.link(ob)
    ob["source_image"] = src; ob["outline_done"] = True; ob["version"] = "v01"; ob["unity_wind"] = "colour attribute WindData: R bend, G flutter, B phase"
    for k, v in (extra or {}).items(): ob[k] = v
    add_motion(ob, motion, motion_scale)
    if ob_bm is not None:
        bmesh.ops.delete(ob_bm, geom=[f for f, t in zip(list(ob_bm.faces), tagged) if not t], context='FACES')
        om = bpy.data.meshes.new(P.name + "_Outline"); ob_bm.to_mesh(om); ob_bm.free(); om.shade_smooth()
        for nm in ("cnx", "cny", "cnz", "cnw", "tint", "ao"):
            a = om.attributes.get(nm)
            if a: om.attributes.remove(a)
        om.materials.append(hidden_mat()); om.materials.append(outline_mat())
        oo = bpy.data.objects.new(P.name + "_Outline", om); coll.objects.link(oo); oo.parent = ob
        oo["outline_done"] = True; oo["export"] = "optional ink hull"; oo.visible_shadow = False
        md = oo.modifiers.new("NPR_Outline", 'SOLIDIFY'); md.thickness = outline_th; md.offset = 1.0; md.use_flip_normals = True
        md.use_rim = False; md.material_offset = 1; md.use_quality_normals = True
        dg = bpy.context.evaluated_depsgraph_get(); sm = bpy.data.meshes.new_from_object(oo.evaluated_get(dg))
        b2 = bmesh.new(); b2.from_mesh(sm)
        bmesh.ops.delete(b2, geom=[f for f in b2.faces if f.material_index == 0], context='FACES')
        for f in b2.faces: f.material_index = 0
        b2.to_mesh(sm); b2.free()
        oo.modifiers.remove(md); oo.data = sm; bpy.data.meshes.remove(om)
        sm.materials.clear(); sm.materials.append(outline_mat()); sm.name = P.name + "_Outline"
        add_motion(oo, motion, motion_scale)
    me.calc_loop_triangles(); return ob, len(me.loop_triangles)

def _wind_color(me):
    n = len(me.vertices)
    if not n: return
    def get(nm):
        a = me.attributes.get(nm); vals = [0.0]*n
        if a: a.data.foreach_get("value", vals)
        return vals
    b, f, p = get("bend"), get("flutter"), get("phase")
    ca = me.color_attributes.new("WindData", 'BYTE_COLOR', 'POINT'); flat = []
    for i in range(n): flat += [min(1.0, b[i]/1.6), min(1.0, f[i]), p[i] % 1.0, 1.0]
    ca.data.foreach_set("color", flat)

def ground_decal(name, coll, parent, r, mat, rx=None, seed=0, h=0.03, pebbles=0, peb_mat=None):
    """optional flat soil / sand patch under a plant (separate child so it can be dropped in game)"""
    P = Plant(name, 1.0, seed=seed); rx = rx or r; N = 40; c = P.v((0, 0, h), bend=0.0)
    ring = []; lip = []
    for i in range(N):
        a = 2*math.pi*i/N; k = 1 + 0.12*noise.noise(Vector((math.cos(a)*2, math.sin(a)*2, seed)))
        ring.append(P.v((rx*k*math.cos(a)*0.85, r*k*math.sin(a)*0.85, h*0.8 + 0.01*noise.noise(Vector((a, seed, 2)))), bend=0.0))
        lip.append(P.v((rx*k*math.cos(a), r*k*math.sin(a), 0.0), bend=0.0))
    for i in range(N):
        P.face((c, ring[i], ring[(i+1) % N]), "g"); P.face((ring[i], lip[i], lip[(i+1) % N], ring[(i+1) % N]), "g")
    rnd = random.Random(seed)
    for _ in range(pebbles):
        a = rnd.uniform(0, 6.28); rr = rnd.uniform(0.2, 0.85)
        ball(P, (rx*rr*math.cos(a), r*rr*math.sin(a), h*0.9), rnd.uniform(0.01, 0.025), "p", sub=1, squash=0.6, bend=0.0, noise_amp=0.2)
    ob, tris = plant_finish(P, coll, {"g": mat, "p": peb_mat or mat}, (0, 0, 0), parent.get("source_image", ""), None, outline=False)
    ob.parent = parent; ob["export"] = "optional ground decal"
    return ob
