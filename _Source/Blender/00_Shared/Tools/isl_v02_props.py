"""v02 props: rocks by kind, mesas/arch (new TRN2), fence ring (no base), bridge, piers, stairs, driftwood, dead trees, smoke, footprints."""
import bmesh
from mathutils import Vector, Matrix, Euler
RND = random.Random(42)
def mat_simple(name, cols, scale=1.2, bump=0.4, zband=None, moss=None, wet=None, rough=0.85):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); N, L = nt.nodes, nt.links
    out = N.new("ShaderNodeOutputMaterial"); bs = N.new("ShaderNodeBsdfPrincipled"); L.new(bs.outputs[0], out.inputs[0]); bs.inputs["Roughness"].default_value = rough
    tc = N.new("ShaderNodeTexCoord"); src = tc.outputs["Object"]
    if zband:
        mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (zband[0], zband[0], zband[1]); L.new(src, mp.inputs["Vector"]); src2 = mp.outputs[0]
    else: src2 = src
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = 5; L.new(src2, nz.inputs["Vector"])
    vr = N.new("ShaderNodeTexVoronoi"); vr.inputs["Scale"].default_value = scale*1.6; L.new(tc.outputs["Object"], vr.inputs["Vector"])
    mx = N.new("ShaderNodeMath"); mx.operation = 'MULTIPLY_ADD'; L.new(vr.outputs["Distance"], mx.inputs[0]); mx.inputs[1].default_value = 0.35; L.new(nz.outputs["Fac"], mx.inputs[2])
    r = N.new("ShaderNodeValToRGB"); e = r.color_ramp.elements; e.new(0.5)
    for el, c, p in zip(e, cols, (0.25, 0.55, 0.9)): el.color = (*lin(c), 1); el.position = p
    L.new(mx.outputs[0], r.inputs[0]); col = r.outputs[0]
    if moss:
        sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Normal"], sep.inputs[0])
        mr = N.new("ShaderNodeMapRange"); mr.inputs[1].default_value = 0.45; mr.inputs[2].default_value = 0.85; L.new(sep.outputs[2], mr.inputs[0])
        mm = N.new("ShaderNodeMix"); mm.data_type = 'RGBA'; mm.inputs[7].default_value = (*lin(moss), 1)
        f2 = N.new("ShaderNodeMath"); f2.operation = 'MULTIPLY'; L.new(mr.outputs[0], f2.inputs[0]); L.new(nz.outputs["Fac"], f2.inputs[1])
        L.new(f2.outputs[0], mm.inputs[0]); L.new(col, mm.inputs[6]); col = mm.outputs[2]
    if wet is not None:
        gp = N.new("ShaderNodeNewGeometry"); sp = N.new("ShaderNodeSeparateXYZ"); L.new(gp.outputs["Position"], sp.inputs[0])
        mr = N.new("ShaderNodeMapRange"); mr.inputs[1].default_value = wet + 0.8; mr.inputs[2].default_value = wet - 0.2; L.new(sp.outputs[2], mr.inputs[0])
        mm = N.new("ShaderNodeMix"); mm.data_type = 'RGBA'; mm.blend_type = 'MULTIPLY'; mm.inputs[7].default_value = (0.45, 0.45, 0.45, 1)
        L.new(mr.outputs[0], mm.inputs[0]); L.new(col, mm.inputs[6]); col = mm.outputs[2]
    L.new(col, bs.inputs["Base Color"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump; L.new(mx.outputs[0], bp.inputs["Height"]); L.new(bp.outputs[0], bs.inputs["Normal"])
    return m
MATS = {}
def rock_mats():
    MATS["coast"] = mat_simple("TRN2_Rock_Coast", [(52, 50, 48), (92, 86, 80), (138, 130, 120)], 0.9, 0.6, wet=-0.2)
    MATS["ground"] = mat_simple("TRN2_Rock_Ground", [(96, 94, 90), (146, 142, 134), (190, 186, 176)], 1.1, 0.5, moss=(120, 130, 70))
    MATS["high"] = mat_simple("TRN2_Rock_High", [(74, 70, 64), (122, 116, 104), (166, 158, 144)], 1.0, 0.5, moss=(70, 100, 44))
    MATS["circle"] = MATS["ground"]; MATS["mud"] = mat_simple("TRN2_Rock_Mud", [(70, 66, 60), (120, 114, 104), (165, 158, 146)], 1.0, 0.5, wet=0.6)
    MATS["desert"] = mat_simple("TRN2_Rock_Desert", [(120, 58, 34), (170, 92, 56), (214, 140, 96)], 0.8, 0.5, zband=(0.4, 3.0))
    MATS["lava"] = mat_simple("TRN2_Rock_Lava", [(16, 15, 15), (36, 34, 33), (64, 60, 58)], 1.4, 0.8)
    MATS["sandstone"] = mat_simple("TRN2_Sandstone", [(150, 62, 34), (196, 102, 62), (230, 150, 104)], 0.6, 0.7, zband=(0.25, 4.5))
    MATS["wood"] = mat_simple("TRN2_Wood", [(64, 44, 28), (104, 74, 48), (140, 106, 72)], 2.0, 0.3, zband=(3.0, 0.4))
    MATS["fp"] = mat_simple("TRN2_Footprint", [(36, 28, 22), (52, 40, 30), (70, 56, 42)], 2.0, 0.2, rough=0.4)
ROCK_MESH = dict(coast=["TRN_Boulder_Round", "TRN_Boulder_Split", "TRN_Boulder_Block", "TRN_RockyHill_02", "TRN_RockyHill_05"],
                 ground=["TRN_Boulder_Round", "TRN_Boulder_Split", "TRN_Boulder_Block"], high=["TRN_Boulder_Round", "TRN_Boulder_Split", "TRN_RockyHill_03"],
                 circle=["TRN_Boulder_Pillar", "TRN_Boulder_Block"], mud=["TRN_RockyHill_04", "TRN_Boulder_Split"],
                 desert=["TRN_Boulder_Round", "TRN_Boulder_Block"], lava=["TRN_LavaRock_Tall", "TRN_LavaRock_Small", "TRN_LavaRock_Low", "TRN_LavaRock_Cube"])
def mesh_size(me):
    co = np.zeros(len(me.vertices)*3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3); return co.min(0), co.max(0)
def place_mesh(src_name, C_, loc, size, rotz=None, tilt=8, mat=None, squash=(1, 1, 1), name=None, keep_mat=False):
    src = bpy.data.objects[src_name] if src_name in bpy.data.objects else ensure_trn(src_name); me = src.data; lo, hi = mesh_size(me); ext = max(hi[0] - lo[0], hi[1] - lo[1], 1e-3)
    ob = bpy.data.objects.new(name or (src_name.replace("TRN_", "R2_") + "_i"), me); C_.objects.link(ob)
    s = size/ext; ob.scale = (s*squash[0], s*squash[1], s*squash[2])
    ob.rotation_euler = (math.radians(RND.uniform(-tilt, tilt)), math.radians(RND.uniform(-tilt, tilt)), RND.uniform(0, 6.283) if rotz is None else rotz)
    ob.location = (loc[0], loc[1], loc[2] - lo[2]*s*squash[2])
    if mat and not keep_mat:
        for sl in ob.material_slots: sl.link = 'OBJECT'; sl.material = mat
    return ob
def rocks(C_, hgrid):
    n = 0
    for r in S["rocks"]:
        k = r["kind"]; c = r["c"]
        if k == "circle":
            rad = 5.5
            for a in range(9):
                t = a/9*6.283; x, y = c[0] + rad*math.cos(t), c[1] + rad*0.9*math.sin(t)
                place_mesh(RND.choice(ROCK_MESH["circle"]), C_, (x, y, h_at(hgrid, x, y) - 0.2), r["size"]*RND.uniform(0.8, 1.2), tilt=6, mat=MATS["circle"], squash=(0.8, 0.8, 1.4)); n += 1
            continue
        for i in range(r["n"]):
            a = RND.uniform(0, 6.283); d = r["spread"]*math.sqrt(RND.random()); x, y = c[0] + d*math.cos(a), c[1] + d*math.sin(a)
            sz = r["size"]*RND.uniform(0.55, 1.5); z = h_at(hgrid, x, y) - sz*0.18
            place_mesh(RND.choice(ROCK_MESH[k]), C_, (x, y, z), sz, mat=None if k == "lava" else MATS[k], squash=(1, RND.uniform(0.7, 1.1), RND.uniform(0.55, 1.0)), keep_mat=(k == "lava")); n += 1
    # cliff-foot talus along the plateau south edge, and the headland rocky coast / rock line
    P = np.asarray(S["plateau"][:17]); seg = np.cumsum([0] + [np.hypot(*(P[i+1] - P[i])) for i in range(len(P) - 1)])
    for i in range(70):
        s = RND.uniform(0, seg[-1]); k = np.searchsorted(seg, s) - 1; k = min(max(k, 0), len(P) - 2); t = (s - seg[k])/(seg[k+1] - seg[k])
        p = P[k] + (P[k+1] - P[k])*t; tg = (P[k+1] - P[k])/np.linalg.norm(P[k+1] - P[k]); nv = np.array([tg[1], -tg[0]])
        if pip(S["plateau"], *(p + nv*2)): nv = -nv
        q = p + nv*RND.uniform(2.5, 7.0); sz = RND.uniform(1.2, 3.2)
        if np.hypot(*(q - np.asarray(S["fall_base"]))) < 6: continue
        place_mesh(RND.choice(ROCK_MESH["high"]), C_, (q[0], q[1], h_at(hgrid, *q) - sz*0.2), sz, mat=MATS["high"], squash=(1, 0.9, 0.7)); n += 1
    HD = np.asarray(S["headland"]); m = len(HD)
    for i in range(m):
        a = HD[i]; b = HD[(i+1) % m]; L_ = np.hypot(*(b - a)); east = a[0] > S["cone"]["c"][0] - 5 and a[1] > S["headland"][-6][1] - 4
        south = a[1] < S["cone"]["c"][1] - 12
        if not (east or south): continue
        for j in range(int(L_/(3.5 if east else 5.0))):
            p = a + (b - a)*(j + RND.random())/max(1, int(L_/(3.5 if east else 5.0))); sz = RND.uniform(3.0, 6.0) if east else RND.uniform(1.4, 3.0)
            place_mesh(RND.choice(ROCK_MESH["coast"]), C_, (p[0], p[1], h_at(hgrid, *p) - sz*(0.35 if east else 0.25)), sz, mat=MATS["coast"] if east else MATS["ground"], squash=(1, 1, RND.uniform(0.6, 1.1))); n += 1
    return n
# ---------------- mesas / arch (new procedural TRN2 assets) ----------------
def mesa_mesh(name, h, w, seed):
    rng = np.random.RandomState(seed); segs = 56; rows = int(h/0.25); V = []; F = []
    lay = rng.uniform(0.7, 1.4, 60); edges = np.cumsum(lay); r0 = w/2; ph = rng.uniform(0, 6.28, 6)
    for j in range(rows + 1):
        z = h*j/rows; li = int(np.searchsorted(edges, z)); fz = (z - (edges[li-1] if li else 0))/lay[li]
        taper = 1 - 0.10*(z/h) - 0.35*max(0.0, z/h - 0.85)**1.5*3 + 0.18*max(0.0, 0.18 - z/h)
        lip = 0.975 + 0.025*math.sin(math.pi*fz) + 0.03*math.sin(li*2.3 + ph[3])
        for i in range(segs):
            a = 2*math.pi*i/segs; ca, sa = math.cos(a), math.sin(a)
            sq = (abs(ca)**3.5 + abs(sa)**3.5)**(-1/3.5)
            wob = 1 + 0.07*math.sin(2*a + ph[0]) + 0.05*math.sin(3*a + ph[1]) + 0.04*math.sin(7*a + ph[2] + li*0.6)
            r = r0*taper*lip*wob*sq; V.append((r*ca*1.1, r*sa*0.9, z))
    for j in range(rows):
        for i in range(segs):
            a = j*segs + i; b = j*segs + (i + 1) % segs; F.append((a, b, b + segs, a + segs))
    top = len(V); V.append((0, 0, h + 0.05)); F += [(rows*segs + i, rows*segs + (i + 1) % segs, top) for i in range(segs)]
    me = bpy.data.meshes.new(name); me.from_pydata(V, [], F); me.update()
    for p_ in me.polygons: p_.use_smooth = True
    return me
def arch_mesh(name, h, w, seed):
    rng = np.random.RandomState(seed); V = []; F = []; segs = 20; n = 36
    for k in range(n + 1):
        t = k/n; rad = 1.3 + 1.6*(abs(2*t - 1))**3 + 0.12*math.sin(k*1.7); H = h - rad
        px, pz = -w/2*math.cos(math.pi*t), H*math.sin(math.pi*t)
        tx, tz = w/2*math.pi*math.sin(math.pi*t), H*math.pi*math.cos(math.pi*t); L_ = math.hypot(tx, tz); tx, tz = tx/L_, tz/L_
        nx_, nz_ = -tz, tx
        for i in range(segs):
            a = 2*math.pi*i/segs; lip = 1 + 0.07*math.sin(pz*3.2 + i*0.3); rr = rad*lip
            V.append((px + rr*math.cos(a)*nx_, rr*math.sin(a)*1.25, pz + rr*math.cos(a)*nz_))
    for k in range(n):
        for i in range(segs):
            a = k*segs + i; b = k*segs + (i + 1) % segs; F.append((a, b, b + segs, a + segs))
    me = bpy.data.meshes.new(name); me.from_pydata(V, [], F); me.update(); return me
def mesas(C_, hgrid):
    out = []
    for k, m in enumerate(S["mesas"]):
        x, y = m["c"]; z = h_at(hgrid, x, y) - 0.6
        if m["kind"] == "arch":
            me = arch_mesh("TRN2_Desert_Arch", m["h"], m["w"], 5 + k); ob = bpy.data.objects.new("TRN2_Desert_Arch", me); ob.rotation_euler = (0, 0, math.radians(-30))
        else:
            me = mesa_mesh("TRN2_Desert_MesaTall_%d" % k, m["h"] + 0.6, m["w"], 11 + k); ob = bpy.data.objects.new("TRN2_Desert_MesaTall_%d" % k, me); ob.rotation_euler = (0, 0, RND.uniform(0, 6.28))
        me.materials.append(MATS["sandstone"]); ob.location = (x, y, z); C_.objects.link(ob); out.append(ob)
    return out
# ---------------- wood structures ----------------
def box(V, F, c, sx, sy, sz, rotz=0.0):
    b = len(V); cs, sn = math.cos(rotz), math.sin(rotz)
    for dx, dy, dz in ((-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)):
        x, y = dx*sx/2, dy*sy/2; V.append((c[0] + x*cs - y*sn, c[1] + x*sn + y*cs, c[2] + dz*sz/2))
    F += [(b, b+1, b+2, b+3), (b+4, b+7, b+6, b+5), (b, b+4, b+5, b+1), (b+1, b+5, b+6, b+2), (b+2, b+6, b+7, b+3), (b+3, b+7, b+4, b)]
def wood_obj(name, V, F, C_):
    me = bpy.data.meshes.new(name); me.from_pydata(V, [], F); me.update(); me.materials.append(MATS["wood"]); ob = bpy.data.objects.new(name, me); C_.objects.link(ob); return ob
def bridge(C_, hgrid):
    a, b = np.asarray(S["bridge"]); d = b - a; L_ = np.linalg.norm(d); u = d/L_; rot = math.atan2(u[1], u[0]); deck = max(h_at(hgrid, *a), h_at(hgrid, *b)) + 0.5
    V, F = [], []; n = int(L_/0.5)
    for i in range(n):
        p = a + u*(i + 0.5)*L_/n; arch_ = 0.6*math.sin(math.pi*(i + 0.5)/n); box(V, F, (p[0], p[1], deck + arch_), 0.42, 4.2, 0.16, rot)
    for side in (-1, 1):
        nv = np.array([-u[1], u[0]])*side*2.0
        for i in range(0, n + 1, 4):
            p = a + u*i*L_/n + nv; arch_ = 0.6*math.sin(math.pi*i/n); box(V, F, (p[0], p[1], deck + arch_ + 0.45), 0.22, 0.22, 1.2, rot)
            box(V, F, (p[0], p[1], deck - 0.9), 0.3, 0.3, 2.4, rot)
        for i in range(n):
            p = a + u*(i + 0.5)*L_/n + nv; arch_ = 0.6*math.sin(math.pi*(i + 0.5)/n); box(V, F, (p[0], p[1], deck + arch_ + 1.0), L_/n + 0.02, 0.14, 0.14, rot)
    return wood_obj("TRN2_Bridge_Wood", V, F, C_)
def pier(C_, pts, hgrid, tee=True, nm="TRN2_Pier"):
    a, b = np.asarray(pts); d = b - a; L_ = np.linalg.norm(d); u = d/L_; rot = math.atan2(u[1], u[0]); z = SEA + 0.9; V, F = [], []
    n = int(L_/0.45)
    for i in range(n):
        p = a + u*(i + 0.5)*L_/n; box(V, F, (p[0], p[1], z), 0.38, 2.6, 0.12, rot)
    for i in range(0, n, 5):
        for s in (-1, 1):
            p = a + u*i*L_/n + np.array([-u[1], u[0]])*s*1.2; box(V, F, (p[0], p[1], z - 1.5), 0.26, 0.26, 3.2, rot)
    if tee:
        for j in range(-6, 7):
            p = b + np.array([-u[1], u[0]])*j*0.45; box(V, F, (p[0], p[1], z), 2.8, 0.4, 0.12, rot)
    return wood_obj(nm, V, F, C_)
def stairs(C_, hgrid):
    a = np.asarray(S["stairs"][0]); b = np.asarray(S["stairs"][1]); d = b - a; L_ = np.linalg.norm(d); u = d/L_; rot = math.atan2(u[1], u[0])
    z0 = h_at(hgrid, *a); z1 = HP + 0.1; n = int((z1 - z0)/0.32); V, F = [], []
    for i in range(n):
        t = (i + 0.5)/n; p = a + d*t; box(V, F, (p[0], p[1], z0 + (z1 - z0)*t - 0.15), L_/n + 0.05, 1.8, 0.3, rot)
        if i % 3 == 0:
            for s in (-1, 1):
                q = p + np.array([-u[1], u[0]])*s*0.95; box(V, F, (q[0], q[1], z0 + (z1 - z0)*t + 0.45), 0.12, 0.12, 1.1, rot)
    for s in (-1, 1):
        for i in range(n):
            t = (i + 0.5)/n; q = a + d*t + np.array([-u[1], u[0]])*s*0.95; box(V, F, (q[0], q[1], z0 + (z1 - z0)*t + 1.0), L_/n + 0.05, 0.09, 0.09, rot)
    return wood_obj("TRN2_Stairs_Timber", V, F, C_)
def fence_ring(C_, hgrid):
    src = ensure_trn("TRN_Beach_FenceRing"); me = src.data.copy(); me.name = "TRN2_FenceRing_Posts"
    if me.library: pass
    bm = bmesh.new(); bm.from_mesh(me); keep = {i for i, m in enumerate(me.materials) if m and ("Post" in m.name)}
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index not in keep], context='FACES'); bm.to_mesh(me); bm.free()
    lo, hi = mesh_size(me); cx, cy = (lo[0] + hi[0])/2, (lo[1] + hi[1])/2; r0 = (hi[0] - lo[0])/2
    ob = bpy.data.objects.new("TRN2_FenceRing", me); C_.objects.link(ob); s = S["fence_ring"]["r"]/max(r0, 1e-3)
    c = S["fence_ring"]["c"]; ob.scale = (s, s*0.95, max(1.0, s*0.35)); ob.location = (c[0] - cx*s, c[1] - cy*s*0.95, h_at(hgrid, *c) - lo[2]*ob.scale[2] - 0.05)
    return ob
PLN_KIND = {"PLN_Log": "StumpsLogs", "PLN_Stump": "StumpsLogs", "PLN_DeadTree": "DeadTrees", "PLN_Stripped": "StrippedTrees", "PLN_Water": "WaterPlants"}
def ensure_pln(name):
    if name in bpy.data.objects: return
    kind = next(v for k, v in PLN_KIND.items() if name.startswith(k))
    with bpy.data.libraries.load(ROOT + r"\04_Plants\PLN_%s_v01.blend" % kind, link=True) as (src, dst): dst.objects = [name]
def plant_mesh_obj(src_name, C_, loc, size, mat=None, tilt=0, rotz=None):
    ensure_pln(src_name)
    return place_mesh(src_name, C_, loc, size, rotz=rotz, tilt=tilt, mat=mat, keep_mat=mat is None, name=src_name + "_i")
def footprints(C_, hgrid):
    V, F = [], []
    for k, p in enumerate(S["footprints"]):
        x, y = p; nxt = S["footprints"][min(k + 1, len(S["footprints"]) - 1)]; ang = math.atan2(nxt[1] - y, nxt[0] - x) if k + 1 < len(S["footprints"]) else 0
        side = 0.6 if k % 2 else -0.6; cx_, cy_ = x - math.sin(ang)*side, y + math.cos(ang)*side; z = h_at(hgrid, cx_, cy_) + 0.03
        for toe in (-0.45, 0, 0.45):
            ta = ang + toe; L_ = 0.9 if toe == 0 else 0.7
            q = (cx_ + math.cos(ta)*L_*0.6, cy_ + math.sin(ta)*L_*0.6, z); box(V, F, q, L_, 0.28, 0.06, ta)
        box(V, F, (cx_ - math.cos(ang)*0.2, cy_ - math.sin(ang)*0.2, z), 0.7, 0.6, 0.06, ang)
    me = bpy.data.meshes.new("TRN2_Footprints"); me.from_pydata(V, [], F); me.update(); me.materials.append(MATS["fp"]); ob = bpy.data.objects.new("TRN2_Footprints", me); C_.objects.link(ob); return ob
def smoke(C_):
    cn = S["cone"]; top = (cn["c"][0] + 1.0, cn["c"][1] + 1.0, cn["peak_h"] - 1.0)
    m = bpy.data.materials.get("TRN2_Smoke") or bpy.data.materials.new("TRN2_Smoke"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial"); v = nt.nodes.new("ShaderNodeVolumePrincipled"); nt.links.new(v.outputs[0], o.inputs["Volume"])
    v.inputs["Color"].default_value = (0.85, 0.85, 0.86, 1)
    tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.22; nz.inputs["Detail"].default_value = 4
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"]); mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs[1].default_value = 0.45; mr.inputs[2].default_value = 0.75; mr.inputs[4].default_value = 0.32
    nt.links.new(nz.outputs["Fac"], mr.inputs[0]); nt.links.new(mr.outputs[0], v.inputs["Density"])
    obs = []
    for k in range(9):
        t = k/8; r = 2.2 + 6.5*t; loc = (top[0] + 30*t**1.25, top[1] + 16*t**1.2, top[2] + 3.0 + 17*t)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=r, location=loc); ob = bpy.context.active_object; ob.name = "TRN2_VolcanoSmoke_%d" % k
        ob.scale = (1.0, 1.0, 0.8); ob.data.materials.append(m)
        for c in ob.users_collection: c.objects.unlink(ob)
        C_.objects.link(ob); obs.append(ob)
    ld = bpy.data.lights.get("ISL2_CraterGlow") or bpy.data.lights.new("ISL2_CraterGlow", 'POINT'); ld.energy = 30000; ld.color = (1.0, 0.45, 0.12); ld.shadow_soft_size = 3
    lo = bpy.data.objects.get("ISL2_CraterGlow") or bpy.data.objects.new("ISL2_CraterGlow", ld); lo.location = (cn["c"][0], cn["c"][1], cn["peak_h"] + 1.0)
    if lo.name not in C_.objects: C_.objects.link(lo)
    return obs
def build_props(hgrid):
    rock_mats(); C_ = coll("ISL2_Props"); clear_coll(C_); n = {}
    n["rocks"] = rocks(C_, hgrid); mesas(C_, hgrid); bridge(C_, hgrid); pier(C_, S["piers"][0], hgrid, True, "TRN2_Pier_East"); pier(C_, S["piers"][1], hgrid, False, "TRN2_Pier_West")
    stairs(C_, hgrid); fence_ring(C_, hgrid); footprints(C_, hgrid); smoke(C_)
    for p in S["driftwood"]:
        plant_mesh_obj(RND.choice(["PLN_Log_Mossy", "PLN_Log_Hollow", "PLN_Log_Cut"]), C_, (p[0], p[1], h_at(hgrid, *p) - 0.1), RND.uniform(3.5, 5.0))
    for p in S["dead_trees"]:
        plant_mesh_obj(RND.choice(["PLN_DeadTree_Twisted", "PLN_DeadTree_Broken", "PLN_Stripped_Broadleaf"]), C_, (p[0], p[1], h_at(hgrid, *p) - 0.2), RND.uniform(3.5, 5.0))
    return n
