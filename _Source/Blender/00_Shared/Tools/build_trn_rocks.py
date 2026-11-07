"""Dino Park Tycoon - TRN_RockyHills / TRN_Boulders / TRN_CliffEdge builder.
Set BUILD = "hills" | "boulders" | "cliffs" before exec. Pivot: bottom centre on the ground (z=0).
Cliff pieces: 2 m wide modules, height 2 levels (2.0 m), tall piece 4 levels (4.0 m)."""
import os
exec(open(os.path.join(TOOLS, "trn_common.py")).read())
RESULTS = {}

GREYS = [(0.09,0.085,0.072),(0.17,0.16,0.14),(0.26,0.25,0.21),(0.40,0.38,0.33)]
MOSS  = [(0.07,0.15,0.013),(0.17,0.30,0.04),(0.26,0.42,0.07)]
def rock_mat(name, greys=GREYS, moss=MOSS, moss_amt=0.5):
    m, nt, bs = new_mat(name)
    tc = nt.nodes.new("ShaderNodeTexCoord"); obj = tc.outputs["Object"]
    n1 = noise_n(nt, obj, 2.5, 6, 0.6); rg = ramp(nt, greys); nt.links.new(n1.outputs["Fac"], rg.inputs[0])
    n2 = noise_n(nt, mapping(nt,obj,(3,3,12)), 2.0, 3, 0.5)
    col = mix(nt, rg.outputs[0], n2.outputs["Fac"], 0.35, 'SOFT_LIGHT')
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = 0.35
    col = mix(nt, col, maprange(nt, ao.outputs["AO"], 0.2, 1.0, 0.35, 1.0), 1.0, 'MULTIPLY')
    geo = nt.nodes.new("ShaderNodeNewGeometry"); sp = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Normal"], sp.inputs[0])
    n3 = noise_n(nt, obj, 4.0, 4, 0.6)
    mf = mathop(nt, maprange(nt, sp.outputs[2], 0.55, 0.85), maprange(nt, n3.outputs["Fac"], 0.5-moss_amt*0.25, 0.62-moss_amt*0.25))
    rm = ramp(nt, moss); nt.links.new(n1.outputs["Fac"], rm.inputs[0])
    col = mix(nt, col, rm.outputs[0], mf)
    so = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(obj, so.inputs[0])
    col = mix(nt, col, (0.16,0.10,0.05), maprange(nt, so.outputs[2], 0.18, 0.0, 0.0, 0.6))
    nt.links.new(col, bs.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.35; bp.inputs["Distance"].default_value = 0.03
    n4 = noise_n(nt, obj, 14, 5, 0.6); nt.links.new(n4.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs[0], bs.inputs["Normal"])
    bs.inputs["Roughness"].default_value = 0.9
    return m

def faceted_rock(bm, center, size, seed, K=11, subdiv=3, cracks=2, sink=0.08, dmin=0.62, boxy=0.0):
    rnd = random.Random(seed)
    res = bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0)
    planes = []
    for _ in range(K):
        n = Vector((rnd.gauss(0,1), rnd.gauss(0,1), rnd.gauss(0,1))).normalized()
        planes.append((n, rnd.uniform(dmin, 0.9)))
    if boxy > 0:
        for ax in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1)):
            n = (Vector(ax) + Vector((rnd.gauss(0,0.12),rnd.gauss(0,0.12),rnd.gauss(0,0.12)))).normalized()
            planes.append((n, rnd.uniform(1-boxy, 1-boxy*0.6)))
    cr = [(Vector((rnd.gauss(0,1), rnd.gauss(0,1), rnd.gauss(0,0.3))).normalized(), rnd.uniform(0.025,0.05)) for _ in range(cracks)]
    sx,sy,sz = size
    for v in res["verts"]:
        u = v.co.normalized(); r = 1.0
        for n,d in planes:
            c = u.dot(n)
            if c > 1e-3: r = min(r, d/c)
        r *= 1 + 0.035*noise.noise(u*3.0 + Vector((seed,0,0)))
        for cn,w in cr:
            a = abs(u.dot(cn))
            if a < w and u.z > -0.2: r *= 0.90 + 0.10*a/w
        p = u*r; p = Vector((p.x*sx, p.y*sy, p.z*sz))
        if p.z < -0.25*sz: p.z = -0.25*sz
        v.co = Vector(center) + p + Vector((0,0,0.25*sz - sink))
    return list({f for v in res["verts"] for f in v.link_faces})

def sand_disc(bm, r, ry=None, z=0.0):
    ry = ry or r*0.82
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=40, radius1=r, radius2=r*0.96, depth=0.05,
                                matrix=Matrix.Translation((0,0,z+0.025)) @ Matrix.Diagonal((1,ry/r,1,1)))
    return list({f for v in res["verts"] for f in v.link_faces})

def make_obj(name, coll, bm, mats, pos, src, extra=None, sharp=22):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    me.shade_smooth()
    try: me.set_sharp_from_angle(angle=math.radians(sharp))
    except Exception: pass
    a = me.attributes.get("freestyle_face") or me.attributes.new("freestyle_face",'BOOLEAN','FACE')
    a.data.foreach_set("value", [True]*len(me.polygons))
    ob = bpy.data.objects.new(name, me); ob.location = pos; coll.objects.link(ob)
    ob["source_image"] = src
    for k,v in (extra or {}).items(): ob[k] = v
    me.calc_loop_triangles(); return len(me.loop_triangles)

SANDC = [(0.40,0.27,0.12),(0.52,0.37,0.18),(0.62,0.47,0.25)]

if BUILD == "hills":
    coll = get_coll("TRN_RockyHills")
    mr = rock_mat("TRN_RockyHill_Rock", moss_amt=0.9); ms = painted2("TRN_RockyHill_Sand", SANDC, SANDC, streak=0.3, bump=0.05)
    # each hill: (base radius, [chunks: (x,y,z, sx,sy,sz, seed, layered)])
    HILLS = [
      (0.62, [(0,0,0, 0.55,0.48,0.42, 1, True)]),
      (0.70, [(-0.15,0,0, 0.40,0.38,0.36, 2, False),(0.22,0.05,0, 0.34,0.32,0.44, 3, False),(0.05,-0.18,0, 0.28,0.26,0.24, 4, False)]),
      (0.80, [(0,0,0, 0.62,0.55,0.85, 5, False),(0.35,-0.25,0, 0.28,0.25,0.26, 6, False)]),
      (0.85, [(0,0,0, 0.70,0.50,0.30, 7, True),(0.10,0.05,0.25, 0.55,0.40,0.26, 8, True),(0.18,0.08,0.45, 0.38,0.30,0.22, 9, True)]),
      (1.10, [(0,0,0, 0.85,0.75,0.55, 10, False),(-0.10,0.05,0.45, 0.62,0.55,0.50, 11, False),(0.05,0.0,0.85, 0.45,0.40,0.45, 12, False),(0.50,-0.35,0, 0.35,0.30,0.30, 13, False)]),
      (1.15, [(0,0,0, 0.95,0.85,1.35, 14, False),(0.55,-0.30,0, 0.40,0.35,0.55, 15, False),(-0.50,-0.20,0, 0.35,0.30,0.45, 16, False)]),
    ]
    x = -5.6
    for i,(br,chunks) in enumerate(HILLS):
        bm = bmesh.new(); bm.verts.layers.float.new("top"); bm.verts.layers.float.new("mask")
        fs = []
        for (cx,cy,cz,sx,sy,sz,sd,lay) in chunks:
            if lay:
                for k in range(3):
                    fs += faceted_rock(bm,(cx+0.03*k,cy,cz+k*sz*0.55),(sx*(1-0.12*k),sy*(1-0.1*k),sz*0.42),sd*10+k,K=10,subdiv=3,cracks=0,dmin=0.8)
            else:
                fs += faceted_rock(bm,(cx,cy,cz),(sx,sy,sz),sd)
        sd_f = sand_disc(bm, br)
        for f in sd_f: f.material_index = 1
        name = "TRN_RockyHill_%02d" % (i+1)
        RESULTS[name] = make_obj(name, coll, bm, [mr, ms], (x*0.7071,-x*0.7071,0), "TRN_RockyHills.jpg", {"footprint_m": round(2*br,2)})
        x += br + 0.55 + (HILLS[i+1][0] if i+1 < len(HILLS) else 0)

if BUILD == "boulders":
    coll = get_coll("TRN_Boulders")
    mr = rock_mat("TRN_Boulder_Rock", moss_amt=0.35)
    SETS = [
      ("TRN_Boulder_Pillar", [(0,0,0, 0.55,0.45,1.55, 21, 3),(0.30,-0.15,0, 0.28,0.25,0.35, 22, 0)]),
      ("TRN_Boulder_Block",  [(-0.25,0.05,0, 0.66,0.58,0.62, 23, 2),(0.45,-0.05,0, 0.48,0.48,0.42, 24, 1)]),
      ("TRN_Boulder_Round",  [(0,0,0, 0.62,0.60,0.62, 25, 3)]),
      ("TRN_Boulder_Split",  [(-0.30,0,0, 0.32,0.52,0.68, 26, 1),(0.30,0.02,0, 0.36,0.55,0.70, 27, 1)]),
    ]
    x = -3.0
    for name, chunks in SETS:
        bm = bmesh.new(); fs = []
        for (cx,cy,cz,sx,sy,sz,sd,ck) in chunks:
            fs += faceted_rock(bm,(cx,cy,cz),(sx,sy,sz),sd,K=(18 if "Round" in name else 10),cracks=ck,
                               dmin=(0.84 if "Round" in name else 0.62), boxy=(0.28 if "Block" in name else (0.18 if "Pillar" in name or "Split" in name else 0.0)))
        for _ in range(3):
            fs += faceted_rock(bm,(random.uniform(-0.5,0.5),random.uniform(-0.6,-0.4),0),(0.08,0.07,0.06),random.randint(100,999),K=8,subdiv=1,cracks=0,sink=0.01)
        RESULTS[name] = make_obj(name, coll, bm, [mr], (x*0.7071,-x*0.7071,0), "TRN_Boulders.jpg")
        x += 2.0

if BUILD == "cliffs":
    coll = get_coll("TRN_CliffEdge")
    m, nt, bs = new_mat("TRN_Cliff_Strata")
    tc = nt.nodes.new("ShaderNodeTexCoord"); obj = tc.outputs["Object"]
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type='BANDS'; wv.bands_direction='Z'
    wv.inputs["Scale"].default_value = 0.42; wv.inputs["Distortion"].default_value = 1.2; wv.inputs["Detail"].default_value = 3
    nt.links.new(obj, wv.inputs["Vector"])
    rw = ramp(nt, [(0.30,0.19,0.09),(0.48,0.33,0.18),(0.24,0.235,0.22),(0.55,0.40,0.22),(0.38,0.26,0.14)], [0.1,0.3,0.5,0.7,0.9])
    nt.links.new(wv.outputs["Fac"], rw.inputs[0])
    n2 = noise_n(nt, mapping(nt,obj,(4,4,1)), 3.0, 4, 0.6)
    col = mix(nt, rw.outputs[0], n2.outputs["Fac"], 0.35, 'SOFT_LIGHT')
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = 0.25
    col = mix(nt, col, maprange(nt, ao.outputs["AO"], 0.2, 1.0, 0.4, 1.0), 1.0, 'MULTIPLY')
    so = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(obj, so.inputs[0])
    col = mix(nt, col, (0.08,0.07,0.04), maprange(nt, so.outputs[2], 0.28, 0.12))
    nt.links.new(col, bs.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.4; bp.inputs["Distance"].default_value = 0.03
    nt.links.new(wv.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs[0], bs.inputs["Normal"]); bs.inputs["Roughness"].default_value = 0.9
    mgr = painted2("TRN_Cliff_GrassCap", [(0.10,0.21,0.02),(0.16,0.30,0.035),(0.23,0.39,0.05)], [(0.07,0.16,0.015),(0.12,0.24,0.025)], streak=0.4)

    def resample(pts, step=0.07, closed=True):
        out = []; n = len(pts)
        for i in range(n if closed else n-1):
            a = Vector(pts[i]); b = Vector(pts[(i+1)%n]); L = (b-a).length; k = max(1,int(L/step))
            for j in range(k): out.append(a.lerp(b, j/k))
        return out
    def arc(cx,cy,r,a0,a1,n=12): return [(cx+r*math.cos(a0+(a1-a0)*i/n), cy+r*math.sin(a0+(a1-a0)*i/n)) for i in range(n+1)]
    OUTL = {
      "TRN_Cliff_Straight":   ([(-1,-0.5),(1,-0.5),(1,0.5),(-1,0.5)], 2.0),
      "TRN_Cliff_OuterCorner":([(-1,-1),(1,-1),(1,0.0),(0.0,0.0),(0.0,1),(-1,1)], 2.0),
      "TRN_Cliff_InnerCorner":([(-1,-0.5)] + arc(0,-0.5,0.5,math.pi,0,14) + [(1,-0.5),(1,0.5),(-1,0.5)], 2.0),
      "TRN_Cliff_End":        ([(-1,-0.5),(0.5,-0.5)] + arc(0.5,0,0.5,-math.pi/2,math.pi/2,14)[1:-1] + [(0.5,0.5),(-1,0.5)], 2.0),
      "TRN_Cliff_Tall":       ([(-1,-0.5),(1,-0.5),(1,0.5),(-1,0.5)], 4.0),
    }
    x = -5.2
    for name,(pts,Hc) in OUTL.items():
        P = resample(pts); N = len(P)
        nrm = []
        for i in range(N):
            t = (P[(i+1)%N]-P[i-1]); t.normalize(); nrm.append(Vector((t.y,-t.x)))
        seed = len(name)
        bm = bmesh.new(); bm.verts.layers.float.new("top"); bm.verts.layers.float.new("mask")
        rings = []; nz = int(Hc/0.1)
        for k in range(nz+1):
            z = Hc*k/nz; band = int((z+0.07*nn(0,k,1.0,2))/0.3)
            ring = []
            for i,p in enumerate(P):
                off = 0.06*nn(band*1.7, seed, 1.0, band) + 0.014*nn(p.x*3+band, p.y*3, 1.0, 5) - (0.03 if z < 0.15 else 0.0)
                q = p + nrm[i]*off; ring.append(bm.verts.new((q.x,q.y,z)))
            rings.append(ring)
        walls = []
        for a,b in zip(rings[:-1],rings[1:]):
            for i in range(N):
                j=(i+1)%N; walls.append(bm.faces.new((a[i],a[j],b[j],b[i])))
        walls.append(bm.faces.new(list(reversed(rings[0]))))
        cb=[]; ct=[]
        for i,p in enumerate(P):
            drip = 0.24*max(0.0, nn(p.x*5, p.y*5, 1.0, seed+3)-0.0)
            q = p + nrm[i]*0.05; cb.append(bm.verts.new((q.x,q.y,Hc-0.04-drip)))
            q2 = p + nrm[i]*0.035; ct.append(bm.verts.new((q2.x,q2.y,Hc+0.07)))
        cap=[]
        for i in range(N):
            j=(i+1)%N
            cap.append(bm.faces.new((rings[-1][i],rings[-1][j],cb[j],cb[i])))
            cap.append(bm.faces.new((cb[i],cb[j],ct[j],ct[i])))
        cap.append(bm.faces.new(ct))
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        for f in cap: f.material_index = 1
        RESULTS[name] = make_obj(name, coll, bm, [m, mgr], (x*0.7071,-x*0.7071,0), "TRN_CliffEdge.jpg", {"height_m":Hc}, sharp=60)
        x += 2.6
