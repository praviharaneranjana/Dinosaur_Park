"""v02 cliff faces: rugged rock skirts built along the plateau edge (new asset family TRN2_CliffFace). exec after terrain."""
def cliff_material(name="TRN2_CliffRock", dark=False):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); N, L = nt.nodes, nt.links
    out = N.new("ShaderNodeOutputMaterial"); bs = N.new("ShaderNodeBsdfPrincipled"); L.new(bs.outputs[0], out.inputs[0])
    tc = N.new("ShaderNodeTexCoord")
    def mp(sc):
        n = N.new("ShaderNodeMapping"); n.inputs["Scale"].default_value = sc; L.new(tc.outputs["Object"], n.inputs["Vector"]); return n.outputs[0]
    def noise(sc, det, vec):
        n = N.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = sc; n.inputs["Detail"].default_value = det; L.new(vec, n.inputs["Vector"]); return n.outputs["Fac"]
    def attr(nm):
        a = N.new("ShaderNodeAttribute"); a.attribute_type = 'GEOMETRY'; a.attribute_name = nm; return a.outputs["Fac"]
    def M(op, a, b):
        n = N.new("ShaderNodeMath"); n.operation = op
        for i, x in enumerate((a, b)):
            if isinstance(x, (int, float)): n.inputs[i].default_value = x
            else: L.new(x, n.inputs[i])
        return n.outputs[0]
    v = N.new("ShaderNodeTexVoronoi"); v.inputs["Scale"].default_value = 0.6; L.new(mp((1, 1, 0.18)), v.inputs["Vector"])
    strata = noise(2.2, 4, mp((0.2, 0.2, 3.0))); grain = noise(3.5, 6, tc.outputs["Object"])
    f = M('ADD', M('ADD', M('MULTIPLY', v.outputs["Distance"], 0.5), M('MULTIPLY', strata, 0.35)), M('MULTIPLY', grain, 0.3))
    f = M('MULTIPLY', f, M('ADD', M('MULTIPLY', attr("cav"), 0.7), 0.45))
    r = N.new("ShaderNodeValToRGB"); e = r.color_ramp.elements; e.new(0.45)
    cols = [(40, 38, 36), (96, 92, 86), (150, 142, 130)] if dark else [(58, 52, 46), (122, 112, 98), (176, 166, 150)]
    for el, c, p in zip(e, cols, (0.15, 0.5, 0.95)): el.color = (*lin(c), 1); el.position = p
    L.new(f, r.inputs[0])
    moss = N.new("ShaderNodeMix"); moss.data_type = 'RGBA'; moss.inputs[7].default_value = (*lin((70, 98, 44)), 1)
    mf = M('MULTIPLY', M('MULTIPLY', attr("top"), 1.4), N.new("ShaderNodeTexNoise").outputs["Fac"])
    nn = mf.node.inputs[1].links[0].from_node; nn.inputs["Scale"].default_value = 1.2; L.new(tc.outputs["Object"], nn.inputs["Vector"])
    L.new(M('POWER', mf, 3.0), moss.inputs[0]); L.new(r.outputs[0], moss.inputs[6])
    wet = N.new("ShaderNodeMix"); wet.data_type = 'RGBA'; wet.blend_type = 'MULTIPLY'; wet.inputs[7].default_value = (0.55, 0.55, 0.55, 1)
    L.new(attr("wet"), wet.inputs[0]); L.new(moss.outputs[2], wet.inputs[6]); L.new(wet.outputs[2], bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = 0.88
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.6; bp.inputs["Distance"].default_value = 0.25
    L.new(M('ADD', v.outputs["Distance"], M('MULTIPLY', grain, 0.4)), bp.inputs["Height"]); L.new(bp.outputs[0], bs.inputs["Normal"])
    return m

def build_cliff_skirt(name, poly, hgrid, skip=(), seed=3, step=0.5, zstep=0.5, outward_off=0.25, dark=False, max_rows=60):
    rng = np.random.RandomState(seed); P = np.asarray(poly, float); n = len(P)
    pts = []; s_acc = 0.0
    for i in range(n):
        a = P[i]; b = P[(i+1) % n]; l = np.hypot(*(b - a)); k = max(1, int(l/step))
        for j in range(k): pts.append(a + (b - a)*j/k)
    pts = np.asarray(pts)
    keep = np.ones(len(pts), bool)
    for (cx, cy, rad) in skip: keep &= np.hypot(pts[:, 0] - cx, pts[:, 1] - cy) > rad
    tang = np.roll(pts, -1, 0) - np.roll(pts, 1, 0); tang /= np.linalg.norm(tang, axis=1, keepdims=True) + 1e-9
    nor = np.stack([tang[:, 1], -tang[:, 0]], 1)
    test = pts + nor*1.0; flip = pip(poly, test[:, 0], test[:, 1]); nor[flip] *= -1          # outward
    sacc = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    # column profile
    colw = 3.4; ph = sacc/colw + 0.8*np.sin(sacc*0.13) + 0.5*np.sin(sacc*0.41 + 1.3)
    cid = np.floor(ph).astype(int)
    col = np.abs((ph % 1.0)*2 - 1); col = np.sqrt(np.clip(col, 0, 1))
    big = 0.5 + 0.5*np.sin(sacc*0.05 + 2.0)*np.cos(sacc*0.021)
    verts, faces, A_cav, A_top, A_wet = [], [], [], [], []
    runs = []; cur = []
    for i in range(len(pts)):
        if keep[i]: cur.append(i)
        elif cur: runs.append(cur); cur = []
    if cur: runs.append(cur)
    for run in runs:
        if len(run) < 4: continue
        base_idx = len(verts); ncol = len(run); nrow = None
        cols_v = []
        for i in run:
            p = pts[i]; nv = nor[i]
            zt_ = h_at(hgrid, *(p - nv*2.2)); zb_ = h_at(hgrid, *(p + nv*2.6)) - 1.0
            if zt_ - zb_ < 2.0: zt_ = zb_ + 2.0
            cols_v.append((p, nv, zb_, zt_))
        nrow = int(min(max_rows, max(4, np.ceil(max(c[3] - c[2] for c in cols_v)/zstep))))
        for ci, (p, nv, zb_, zt_) in enumerate(cols_v):
            i = run[ci]
            jag = 0.35*np.sin(sacc[i]*0.9) + 0.25*np.sin(sacc[i]*2.3 + 1.0)
            for r_ in range(nrow + 1):
                t = r_/nrow; z = zb_ + (zt_ + jag*0.6 - zb_)*t
                ledge = 0.35*np.sin(z*1.7 + sacc[i]*0.05) + 0.25*np.sin(z*4.1 + sacc[i]*0.3)
                bh = 2.2 + 1.2*((cid[i]*7) % 3)/2.0; blk = int(np.floor((z + cid[i]*1.3)/bh))
                hsh = ((blk*928371 + cid[i]*364479) % 1000)/1000.0
                d = outward_off + 2.3*col[i]*(0.55 + 0.45*big[i]) + 0.9*hsh + 0.3*ledge + 2.4*big[i]*np.sin(np.pi*t)*0.6 - 1.1*t**2 + 2.6*(1 - t)**4 + 0.12*rng.randn()
                d = max(d, -0.3)
                q = p + nv*d; verts.append((q[0], q[1], z))
                A_cav.append(float(np.clip(0.35 + col[i]*0.65 + 0.3*ledge, 0, 1))); A_top.append(float(t)); A_wet.append(float(np.clip((0.6 - z)/1.5, 0, 1)))
        for ci in range(ncol - 1):
            for r_ in range(nrow):
                a = base_idx + ci*(nrow + 1) + r_; b = a + (nrow + 1)
                faces.append((a, b, b + 1, a + 1))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    for nm, arr in (("cav", A_cav), ("top", A_top), ("wet", A_wet)):
        at = me.attributes.new(nm, 'FLOAT', 'POINT'); at.data.foreach_set("value", np.asarray(arr, np.float32))
    for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new(name, me); me.materials.append(cliff_material("TRN2_CliffRock_Dark" if dark else "TRN2_CliffRock", dark))
    # make normals face outward (consistent): recalc
    import bmesh
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    return ob
