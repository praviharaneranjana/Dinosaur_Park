"""Dino Park Tycoon - HQ terrain toolkit (v2 quality).
- curvature attribute 'curv' (+ convex edges, - cavities) baked per vertex -> edge highlights / cavity shadows
- painterly material: noise breakup, brush strokes, top light, edge wear, cavity dark, moss, dirt, speckle
- rock_hq(): fractured, chipped, cracked, wear-rounded rock from a dense icosphere
- render_setup(): EEVEE raytraced shadows + AO + ground shadow catcher matching the background
exec() after trn_common.py."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, noise

# ---------------- curvature ----------------
def bake_curvature(bm, layer_name="curv", passes=1, gain=6.0):
    bm.normal_update()
    cl = bm.verts.layers.float.get(layer_name) or bm.verts.layers.float.new(layer_name)
    vals = {}
    for v in bm.verts:
        es = v.link_edges
        if not es: vals[v] = 0.0; continue
        s = 0.0
        for e in es:
            d = v.co - e.other_vert(v).co; L = d.length
            if L > 1e-7: s += d.dot(v.normal)/L
        vals[v] = s/len(es)
    for _ in range(passes):
        nv = {}
        for v in bm.verts:
            es = v.link_edges
            nv[v] = (vals[v]*2 + sum(vals[e.other_vert(v)] for e in es)) / (2+len(es)) if es else vals[v]
        vals = nv
    for v in bm.verts: v[cl] = max(-1.0, min(1.0, vals[v]*gain))
    return cl

# ---------------- painterly material ----------------
def _n(nt, t): return nt.nodes.new(t)
def painterly(name, base, edge=(0.85,0.82,0.75), cavity=(0.03,0.025,0.02), moss=None, moss_amt=0.0,
              dirt=(0.16,0.10,0.05), dirt_h=0.18, scale=2.2, strokes=0.4, speckle=0.12, rough=0.88,
              edge_amt=0.35, cav_amt=0.9, toplight=0.35, bump=0.35, emission=None, wet=None, crack_lines=0.0, crack_scale=2.2):
    m, nt, bs = new_mat(name)
    tc = _n(nt,"ShaderNodeTexCoord"); obj = tc.outputs["Object"]
    geo = _n(nt,"ShaderNodeNewGeometry"); sn = _n(nt,"ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Normal"], sn.inputs[0]); nz = sn.outputs[2]
    so = _n(nt,"ShaderNodeSeparateXYZ"); nt.links.new(obj, so.inputs[0]); oz = so.outputs[2]
    cv = attr(nt, "curv")
    n1 = noise_n(nt, obj, scale, 8, 0.62); rb = ramp(nt, base); nt.links.new(n1.outputs["Fac"], rb.inputs[0])
    col = rb.outputs[0]
    nm = noise_n(nt, obj, scale*0.35, 3, 0.5)
    col = mix(nt, col, maprange(nt, nm.outputs["Fac"], 0.3, 0.7, 0.75, 1.2), 1.0, 'MULTIPLY')
    s1 = noise_n(nt, mapping(nt, obj, (1.5,9,1.5), 0.5), 3.0, 4, 0.55)
    s2 = noise_n(nt, mapping(nt, obj, (9,1.5,1.5), 1.9), 3.0, 4, 0.55)
    col = mix(nt, col, s1.outputs["Fac"], strokes, 'SOFT_LIGHT'); col = mix(nt, col, s2.outputs["Fac"], strokes*0.7, 'SOFT_LIGHT')
    col = mix(nt, col, (0.92,0.88,0.80), mathop(nt, maprange(nt, nz, 0.3, 1.0), toplight), 'SOFT_LIGHT')
    col = mix(nt, col, (0.35,0.33,0.32), maprange(nt, nz, -0.1, -0.8, 0.0, 0.6), 'MULTIPLY')
    if moss:
        nmo = noise_n(nt, obj, 3.5, 6, 0.65); rmo = ramp(nt, moss); nt.links.new(nmo.outputs["Fac"], rmo.inputs[0])
        mf = mathop(nt, maprange(nt, nz, 0.45, 0.8), maprange(nt, nmo.outputs["Fac"], 0.62-0.22*moss_amt, 0.70-0.22*moss_amt))
        mf = mathop(nt, mf, maprange(nt, cv, 0.5, 0.1, 0.4, 1.0))
        col = mix(nt, col, rmo.outputs[0], mf)
    col = mix(nt, col, dirt, maprange(nt, oz, dirt_h, 0.0, 0.0, 0.7))
    # edge wear highlight + cavity shadow (curvature) + AO
    ev = noise_n(nt, obj, 9, 4, 0.6)
    ef = mathop(nt, maprange(nt, cv, 0.18, 0.7), maprange(nt, ev.outputs["Fac"], 0.35, 0.6, 0.4, 1.0))
    col = mix(nt, col, edge, mathop(nt, ef, edge_amt))
    ao = _n(nt,"ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = 0.25; ao.samples = 16
    cf = mathop(nt, maprange(nt, cv, -0.06, -0.5), maprange(nt, ao.outputs["AO"], 1.0, 0.3), 'MAXIMUM')
    col = mix(nt, col, cavity, mathop(nt, cf, cav_amt))
    crack_h = None
    if crack_lines > 0:
        dn = noise_n(nt, obj, 2.5, 3, 0.5)
        va = _n(nt,"ShaderNodeVectorMath"); va.operation='ADD'; nt.links.new(obj, va.inputs[0]); nt.links.new(dn.outputs["Color"], va.inputs[1])
        vc = _n(nt,"ShaderNodeTexVoronoi"); vc.feature='DISTANCE_TO_EDGE'; vc.inputs["Scale"].default_value = crack_scale
        nt.links.new(va.outputs[0], vc.inputs["Vector"])
        cm = noise_n(nt, obj, 1.6, 2, 0.5)
        lines = mathop(nt, maprange(nt, vc.outputs["Distance"], 0.014, 0.0), maprange(nt, cm.outputs["Fac"], 0.46, 0.56))
        col = mix(nt, col, cavity, mathop(nt, lines, crack_lines))
        hl = mathop(nt, maprange(nt, vc.outputs["Distance"], 0.03, 0.014), maprange(nt, cm.outputs["Fac"], 0.46, 0.56))
        col = mix(nt, col, edge, mathop(nt, mathop(nt, hl, lines, 'SUBTRACT'), 0.25))
        crack_h = lines
    vs = _n(nt,"ShaderNodeTexVoronoi"); vs.inputs["Scale"].default_value = 55; nt.links.new(obj, vs.inputs["Vector"])
    sp = maprange(nt, vs.outputs["Distance"], 0.0, 0.12)
    col = mix(nt, col, cavity, mathop(nt, maprange(nt, sp, 0.2, 0.0), speckle))
    nt.links.new(col, bs.inputs["Base Color"])
    bp = _n(nt,"ShaderNodeBump"); bp.inputs["Strength"].default_value = bump; bp.inputs["Distance"].default_value = 0.02
    nb = noise_n(nt, obj, 16, 6, 0.6)
    hgt = mathop(nt, nb.outputs["Fac"], mathop(nt, sp, 0.4), 'ADD')
    if crack_h is not None: hgt = mathop(nt, hgt, mathop(nt, crack_h, 1.5), 'SUBTRACT')
    nt.links.new(hgt, bp.inputs["Height"]); nt.links.new(bp.outputs[0], bs.inputs["Normal"])
    if wet:
        nt.links.new(maprange(nt, n1.outputs["Fac"], 0.3, 0.7, wet[0], wet[1]), bs.inputs["Roughness"])
        bs.inputs["Specular IOR Level"].default_value = 0.7
    else:
        bs.inputs["Roughness"].default_value = rough
    if emission: emission(nt, bs, obj, cv)
    return m

# ---------------- HQ rock ----------------
def rock_hq(bm, center, size, seed, K=18, subdiv=5, dmin=0.55, dmax=0.9, boxy=0.0, cracks=3, crack_depth=0.06,
            chips=0.0, wear=1, strata=0, strata_depth=0.05, sink=0.06, flat_top=0.0, rot=0.0):
    rnd = random.Random(seed)
    res = bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0)
    vs = res["verts"]
    planes = []
    for _ in range(K):
        n = Vector((rnd.gauss(0,1), rnd.gauss(0,1), rnd.gauss(0,0.8))).normalized(); planes.append((n, rnd.uniform(dmin, dmax)))
    if boxy > 0:
        for ax in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1)):
            n = (Vector(ax)+Vector((rnd.gauss(0,0.1),rnd.gauss(0,0.1),rnd.gauss(0,0.1)))).normalized(); planes.append((n, rnd.uniform(1-boxy, 1-boxy*0.55)))
    if flat_top > 0: planes.append((Vector((rnd.gauss(0,0.08),rnd.gauss(0,0.08),1)).normalized(), 1-flat_top))
    cr = [(Vector((rnd.gauss(0,1), rnd.gauss(0,1), rnd.gauss(0,0.25))).normalized(), rnd.uniform(0.035,0.05)) for _ in range(cracks)]
    off = Vector((seed*1.37, seed*0.71, seed*2.13))
    for v in vs:
        u = v.co.normalized(); r = 1.0
        for n,d in planes:
            c = u.dot(n)
            if c > 1e-3: r = min(r, d/c)
        v.co = u*r
    # wear: soften facet edges (chamfer look)
    for _ in range(wear): bmesh.ops.smooth_vert(bm, verts=vs, factor=0.35, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    bm.normal_update()
    for v in vs:
        p = v.co; u = p.normalized(); nrm = v.normal
        dsp = 0.008*noise.noise(p*3.0+off) + 0.004*noise.noise(p*11.0+off)
        # voronoi chip network
        dists, pts = noise.voronoi(p*4.0+off, distance_metric='DISTANCE')
        edge = dists[1]-dists[0]
        dsp -= chips*max(0.0, 1-edge/0.05)
        for cn,w in cr:
            a = abs(u.dot(cn) + 0.04*noise.noise(p*6+off))
            if a < w and u.z > -0.35: dsp -= crack_depth*(1-(a/w)**2)
        if strata:
            ph = (p.z*strata + 0.15*noise.noise(p*2+off)) % 1.0
            dsp -= strata_depth*(1-min(1.0, ph/0.12))
        v.co = p + nrm*dsp
    sx,sy,sz = size
    R = Matrix.Rotation(rot,3,'Z')
    for v in vs:
        p = Vector((v.co.x*sx, v.co.y*sy, v.co.z*sz))
        if p.z < -0.28*sz: p.z = -0.28*sz + (p.z+0.28*sz)*0.15
        v.co = Vector(center) + R @ p + Vector((0,0,0.28*sz - sink))
    return list({f for v in vs for f in v.link_faces})

# ---------------- object finish with curvature ----------------
def make_obj_hq(name, coll, bm, mats, pos, src, extra=None, sharp=34):
    bake_curvature(bm)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    me.shade_smooth()
    if sharp:
        try: me.set_sharp_from_angle(angle=math.radians(sharp))
        except Exception: pass
    a = me.attributes.get("freestyle_face") or me.attributes.new("freestyle_face",'BOOLEAN','FACE')
    a.data.foreach_set("value", [True]*len(me.polygons))
    ob = bpy.data.objects.new(name, me); ob.location = pos; coll.objects.link(ob)
    ob["source_image"] = src; ob["quality"] = "v2_hq"
    for k,v in (extra or {}).items(): ob[k] = v
    me.calc_loop_triangles(); return len(me.loop_triangles)

# ---------------- render setup ----------------
def render_setup(ground_z=0.0, sun_rot=(48,0,-112), sun_e=2.3, bg=(0.78,0.79,0.80)):
    sc = bpy.context.scene; ee = sc.eevee
    sc.render.engine = 'BLENDER_EEVEE'
    ee.use_raytracing = True; ee.use_shadows = True; ee.shadow_ray_count = 2; ee.shadow_step_count = 8
    ee.use_fast_gi = True; ee.fast_gi_distance = 1.0; ee.taa_render_samples = 96
    sc.view_settings.view_transform = 'Standard'
    sun = bpy.data.objects.get("Light")
    sun.data.type = 'SUN'; sun.data.energy = sun_e; sun.data.angle = math.radians(6)
    sun.rotation_euler = tuple(math.radians(a) for a in sun_rot)
    w = sc.world; wn = w.node_tree; bgn = [n for n in wn.nodes if n.type=='BACKGROUND'][0]
    bgn.inputs["Strength"].default_value = 0.55
    gp = bpy.data.objects.get("_ShadowGround")
    if gp is None:
        me = bpy.data.meshes.new("_ShadowGround"); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=60); bm.to_mesh(me); bm.free()
        gp = bpy.data.objects.new("_ShadowGround", me); sc.collection.objects.link(gp)
        m, nt, bs = new_mat("_ShadowGround"); bs.inputs["Base Color"].default_value = (*[c*0.75 for c in bg],1); bs.inputs["Roughness"].default_value = 1.0
        me.materials.append(m)
    gp.location = (0,0,ground_z)
    sc.render.use_freestyle = True; sc.render.line_thickness_mode = 'ABSOLUTE'; sc.render.line_thickness = 1.2
    vl = bpy.context.view_layer; vl.use_freestyle = True
    fs = vl.freestyle_settings
    ls = fs.linesets[0] if fs.linesets else fs.linesets.new("Outline")
    for a in ("select_silhouette","select_border","select_crease","select_contour","select_suggestive_contour","select_ridge_valley","select_edge_mark","select_external_contour","select_material_boundary"):
        if hasattr(ls, a): setattr(ls, a, a=="select_external_contour")
    ls.select_by_face_marks = True; ls.face_mark_condition = 'ONE'; ls.face_mark_negation = 'INCLUSIVE'
    ls.linestyle.color = (0.05,0.04,0.035); ls.linestyle.thickness = 1.2
    return gp
