"""v02 water: river ribbon, falls pool, lily pond, swamp pools, puddles, plateau stream, two-tier waterfall (new TRN2_Waterfall_Tall)."""
def catmull(pts, n=6):
    P = [np.asarray(p, float) for p in pts]; out = []
    for i in range(len(P) - 1):
        p0 = P[max(i-1, 0)]; p1 = P[i]; p2 = P[i+1]; p3 = P[min(i+2, len(P)-1)]
        for k in range(n):
            t = k/n; out.append(0.5*((2*p1) + (-p0+p2)*t + (2*p0-5*p1+4*p2-p3)*t*t + (-p0+3*p1-3*p2+p3)*t**3))
    out.append(P[-1]); return np.asarray(out)
def mesh_obj(name, verts, faces, mat, attrs=None, uv=None, coll_=None):
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces]); me.update()
    for nm, arr in (attrs or {}).items():
        a = me.attributes.new(nm, 'FLOAT', 'POINT'); a.data.foreach_set("value", np.asarray(arr, np.float32))
    if uv is not None:
        l = me.uv_layers.new(name="FlowUV"); lv = np.zeros(len(me.loops), int); me.loops.foreach_get("vertex_index", lv)
        l.data.foreach_set("uv", np.asarray(uv, np.float32)[lv].ravel())
    for p in me.polygons: p.use_smooth = True
    if mat: me.materials.append(ensure_mat(mat) if isinstance(mat, str) else mat)
    ob = bpy.data.objects.new(name, me); (coll_ or bpy.context.scene.collection).objects.link(ob); ob.visible_shadow = False; return ob
def ribbon(name, cl, widths, zfun, hgrid, mat, coll_, ncross=7, uvscale=0.25):
    cl = np.asarray(cl, float); n = len(cl); V = []; UVs = []; D = []; F = []; acc = 0.0
    for i in range(n):
        a = cl[max(i-1, 0)]; b = cl[min(i+1, n-1)]; t_ = b - a; t_ /= np.linalg.norm(t_) + 1e-9; nv = np.array([-t_[1], t_[0]])
        if i: acc += np.linalg.norm(cl[i] - cl[i-1])
        w = widths[i]; z = zfun(i/(n-1))
        for k in range(ncross):
            s = -1 + 2*k/(ncross-1); p = cl[i] + nv*s*w*0.5*(1.0 + 0.06*np.sin(acc*0.4 + k))
            V.append((p[0], p[1], z)); UVs.append((s, acc*uvscale)); D.append(0.02 + 0.23*(1 - abs(s)**1.8))
    for i in range(n - 1):
        for k in range(ncross - 1):
            a = i*ncross + k; F.append((a, a + ncross, a + ncross + 1, a + 1))
    return mesh_obj(name, V, F, mat, {"depth": D}, UVs, coll_)
def fill_water(name, poly, level, hgrid, mat, coll_, grow=2.0, step=0.6, extra=None):
    P = np.asarray(poly); x0, y0 = P.min(0) - grow - 1; x1, y1 = P.max(0) + grow + 1
    xs = np.arange(x0, x1, step); ys = np.arange(y0, y1, step); GX, GY = np.meshgrid(xs, ys)
    HB = np.vectorize(lambda a, b: h_at(hgrid, a, b))(GX, GY)
    inside = (sdf(poly, GX, GY) > -grow) & (HB < level + 0.25)
    ny, nx = GX.shape; idx = -np.ones((ny, nx), int); V = []; D = []
    for j in range(ny):
        for i in range(nx):
            if inside[j, i] or (j+1 < ny and inside[j+1, i]) or (i+1 < nx and inside[j, i+1]):
                idx[j, i] = len(V); V.append((GX[j, i], GY[j, i], level)); D.append(float(np.clip((level - h_at(hgrid, GX[j, i], GY[j, i]))*0.3, 0.0, 0.3)))
    F = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            q = (idx[j, i], idx[j, i+1], idx[j+1, i+1], idx[j+1, i])
            if min(q) >= 0 and inside[j, i]: F.append(q)
    at = {"depth": D}
    if extra: at.update({k: [f(v) for v in V] for k, f in extra.items()})
    return mesh_obj(name, V, F, mat, at, None, coll_)
def fall_sheet(name, top_xy, dirv, ztop, zbot, width, coll_, strands=((0.0, 1.0),), lip_out=0.6, seed=1):
    """vertical curtain: top lip at ztop, falls to zbot, bulging forward; attrs fallv/mask/depth + FlowUV like TRN_Waterfall_Big_Water."""
    rng = np.random.RandomState(seed); dirv = np.asarray(dirv, float)/np.linalg.norm(dirv); side = np.array([dirv[1], -dirv[0]])
    V = []; F = []; UV = []; FV = []; MK = []; DP = []
    for (off, wfac) in strands:
        base = len(V); nu, nv = 9, 26; w = width*wfac
        for j in range(nv + 1):
            t = j/nv; z = ztop + (zbot - ztop)*t
            fwd = lip_out*np.sqrt(t)*1.6 + 0.4*t
            for i in range(nu + 1):
                s = -0.5 + i/nu; wob = 0.12*np.sin(z*1.3 + i) + 0.06*rng.randn()
                p = np.asarray(top_xy) + side*(off + s*w*(1 + 0.25*t)) + dirv*(fwd + wob)
                V.append((p[0], p[1], z)); UV.append((s*2.0, (ztop - z)*0.47)); FV.append(min(0.95, 0.05 + 0.9*t)); MK.append(0.05 + 0.12*t); DP.append(0.12)
        for j in range(nv):
            for i in range(nu):
                a = base + j*(nu + 1) + i; F.append((a, a + 1, a + nu + 2, a + nu + 1))
    return mesh_obj(name, V, F, fall_material(), {"fallv": FV, "mask": MK, "depth": DP}, UV, coll_)
def fall_material():
    m = bpy.data.materials.get("TRN2_FallWater") or bpy.data.materials.new("TRN2_FallWater"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); N, L = nt.nodes, nt.links
    try: m.surface_render_method = 'BLENDED'
    except Exception: pass
    out = N.new("ShaderNodeOutputMaterial"); bs = N.new("ShaderNodeBsdfPrincipled"); L.new(bs.outputs[0], out.inputs[0])
    uv = N.new("ShaderNodeUVMap"); uv.uv_map = "FlowUV"
    tv = N.new("ShaderNodeValue"); tv.name = "time"; fc = tv.outputs[0].driver_add("default_value"); fc.driver.expression = "frame/24"
    mp = N.new("ShaderNodeMapping"); L.new(uv.outputs[0], mp.inputs["Vector"]); mp.inputs["Scale"].default_value = (5.0, 0.35, 1.0)
    cb = N.new("ShaderNodeCombineXYZ"); mul = N.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = -1.4; L.new(tv.outputs[0], mul.inputs[0]); L.new(mul.outputs[0], cb.inputs[1])
    L.new(cb.outputs[0], mp.inputs["Location"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0; nz.inputs["Detail"].default_value = 6; L.new(mp.outputs[0], nz.inputs["Vector"])
    r = N.new("ShaderNodeValToRGB"); r.color_ramp.elements[0].position = 0.2; r.color_ramp.elements[0].color = (*lin((120, 190, 215)), 1); r.color_ramp.elements[1].position = 0.55; r.color_ramp.elements[1].color = (0.97, 0.99, 1.0, 1)
    L.new(nz.outputs["Fac"], r.inputs[0]); L.new(r.outputs[0], bs.inputs["Base Color"]); L.new(r.outputs[0], bs.inputs["Emission Color"]); bs.inputs["Emission Strength"].default_value = 0.45
    sx = N.new("ShaderNodeSeparateXYZ"); L.new(uv.outputs[0], sx.inputs[0]); ab = N.new("ShaderNodeMath"); ab.operation = 'ABSOLUTE'; L.new(sx.outputs[0], ab.inputs[0])
    edge = N.new("ShaderNodeMapRange"); edge.inputs[1].default_value = 0.9; edge.inputs[2].default_value = 0.4; L.new(ab.outputs[0], edge.inputs[0])
    am = N.new("ShaderNodeMath"); am.operation = 'MULTIPLY'; L.new(edge.outputs[0], am.inputs[0]); am.inputs[1].default_value = 0.93
    L.new(am.outputs[0], bs.inputs["Alpha"]); bs.inputs["Roughness"].default_value = 0.3
    return m
def mist_volume(name, c, z, r, coll_, n=4, seed=3, dens=0.35):
    rng = np.random.RandomState(seed)
    m = bpy.data.materials.get("TRN2_Mist") or bpy.data.materials.new("TRN2_Mist"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial"); v = nt.nodes.new("ShaderNodeVolumePrincipled"); nt.links.new(v.outputs[0], o.inputs["Volume"]); v.inputs["Color"].default_value = (0.95, 0.97, 1.0, 1)
    tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.2; nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs[1].default_value = 0.4; mr.inputs[2].default_value = 0.7; mr.inputs[4].default_value = dens; nt.links.new(nz.outputs["Fac"], mr.inputs[0]); nt.links.new(mr.outputs[0], v.inputs["Density"])
    for k in range(n):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=r*rng.uniform(0.6, 1.0), location=(c[0] + rng.uniform(-r, r), c[1] + rng.uniform(-r*0.6, r*0.3), z + rng.uniform(0, r*0.6)))
        ob = bpy.context.active_object; ob.name = name + "_%d" % k; ob.data.materials.append(m)
        for cc in ob.users_collection: cc.objects.unlink(ob)
        coll_.objects.link(ob)
def mist(name, c, z, size, coll_, n=5, seed=2):
    rng = np.random.RandomState(seed); V = []; F = []
    for k in range(n):
        cx = c[0] + rng.uniform(-size*0.6, size*0.6); cy = c[1] + rng.uniform(-size*0.6, size*0.3); s = size*rng.uniform(0.6, 1.0); zz = z + rng.uniform(0, size*0.5)
        b = len(V); V += [(cx - s, cy, zz), (cx + s, cy, zz), (cx + s, cy, zz + s*1.3), (cx - s, cy, zz + s*1.3)]; F.append((b, b+1, b+2, b+3))
    ob = mesh_obj(name, V, F, "TRN_Falls_Spray4", None, None, coll_); ob.visible_shadow = False; return ob

def build_water(hgrid):
    C_ = coll("ISL2_Water"); clear_coll(C_); out = {}
    rv = catmull(S["river"], 6); ww = np.interp(np.linspace(0, 1, len(rv)), np.linspace(0, 1, len(S["river_w"])), S["river_w"])
    out["river"] = ribbon("ISL2_River", rv, ww*1.25, lambda t: 0.05 - 0.5*t + 0.02, hgrid, "TRN_River_Water3", C_)
    out["pool"] = fill_water("ISL2_FallsPool", S["pool"], 0.07, hgrid, "TRN_Waterfall_Big_Pool4", C_, grow=4.5)
    out["lily"] = fill_water("ISL2_LilyPond", S["lily"], 0.22, hgrid, "TRN_Waterfall_Big_Pool4", C_, grow=2.0)
    out["algae"] = fill_water("ISL2_SwampAlgae", S["algae"], -0.05, hgrid, "TRN_Swamp_Algae3", C_, grow=1.6, extra={"curv": lambda v: 0.5 + 0.5*math.sin(v[0]*0.7)*math.cos(v[1]*0.5)})
    for k, p in enumerate(S["dark_pools"]): fill_water(f"ISL2_SwampPool_{k}", p, -0.05, hgrid, "TRN_Swamp_PoolWater3", C_, grow=1.4)
    for k, p in enumerate(S["puddles"]): fill_water(f"ISL2_MudPuddle_{k}", p, h_at(hgrid, *np.mean(p, 0)) + 0.06, hgrid, "TRN_Swamp_PoolWater3", C_, grow=0.6, step=0.4)
    # plateau stream (upper part sits 2.4 m higher, small cascade at index 3)
    fb = np.asarray(S["fall_base"]); lip = fb + np.array([0.0, -1.6])
    st = catmull(S["plateau_stream"], 6)
    st = np.asarray([p for p in st if h_at(hgrid, *p) > HP - 2.5] + [lip]); nst = len(st); ci = 3*6
    zs = np.array([h_at(hgrid, *p) + 0.45 for p in st[:-1]]); zs = np.append(zs, zs[-1])
    zs = np.minimum.accumulate(zs)
    upper = st[:ci + 1]; lower = st[ci + 3:]
    out["stream_u"] = ribbon("ISL2_StreamUpper", upper, np.full(len(upper), 3.0), lambda t: zs[min(int(round(t*(len(upper)-1))), len(zs)-1)], hgrid, "TRN_River_Water3", C_)
    out["stream_l"] = ribbon("ISL2_StreamLower", lower, np.full(len(lower), 3.4), lambda t: zs[ci + 3 + min(int(round(t*(len(lower)-1))), len(lower)-1)], hgrid, "TRN_River_Water3", C_)
    d_small = st[ci + 3] - st[ci]; d_small = d_small/np.linalg.norm(d_small)
    out["cascade"] = fall_sheet("TRN2_Cascade_Small", st[ci], d_small, zs[ci], zs[ci + 3], 2.6, C_, lip_out=0.3, seed=4)
    # main fall: two strands like the reference
    lip_z = zs[-1]; dmain = np.array([0.0, -1.0])
    out["fall"] = fall_sheet("TRN2_Waterfall_Tall", lip, dmain, lip_z, -0.2, 6.5, C_, strands=((-1.8, 0.6), (2.3, 0.4)), lip_out=1.4, seed=7)
    out["lip_z"] = float(lip_z)
    mist_volume("TRN2_Waterfall_Mist", fb + np.array([0, -3.5]), 0.3, 3.2, C_, n=5, dens=0.45)
    mist_volume("TRN2_Cascade_Mist", st[ci + 3], zs[ci + 3] - 0.3, 1.2, C_, n=2, seed=5, dens=0.35)
    return out
