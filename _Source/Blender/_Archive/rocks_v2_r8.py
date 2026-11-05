"""Dino Park Tycoon - rocks v2 HQ: BUILD = "boulders" | "hills" | "cliffs" (exec with TOOLS)."""
import os
exec(open(os.path.join(TOOLS, "trn_common.py")).read())
exec(open(os.path.join(TOOLS, "trn_hq.py")).read())
random.seed(5)
RESULTS = {}
ROCK = [(0.13,0.125,0.11),(0.16,0.153,0.135),(0.20,0.19,0.168),(0.24,0.23,0.20)]
MOSS = [(0.035,0.07,0.01),(0.08,0.15,0.02),(0.15,0.25,0.04)]
def row(i,n,gap): t=(i-(n-1)/2)*gap; return (t*0.7071,-t*0.7071,0)
def soil_patch(bm, r, seed, z=0.0):
    """irregular dirt/moss patch under a rock so it sits in the ground (reference style)"""
    rnd = random.Random(seed); N=40; ring=[]; c = bm.verts.new((0,0,z+0.012))
    for i in range(N):
        a=2*math.pi*i/N; rr = r*(0.8+0.35*noise.noise(Vector((math.cos(a)*1.7,math.sin(a)*1.7,seed))))
        ring.append(bm.verts.new((rr*math.cos(a), rr*math.sin(a)*0.85, z+0.004)))
    fs=[bm.faces.new((c,ring[i],ring[(i+1)%N])) for i in range(N)]
    return fs

if BUILD == "boulders":
    coll = get_coll("TRN_Boulders")
    mr = painterly("TRN_Rock_HQ", ROCK, edge=(0.55,0.53,0.48), cavity=(0.02,0.018,0.015), moss=MOSS, moss_amt=0.35, scale=2.0, strokes=0.3, crack_lines=0.9, crack_scale=2.4)
    md = painterly("TRN_Rock_Soil", [(0.10,0.07,0.04),(0.17,0.12,0.07),(0.24,0.18,0.11)], edge_amt=0, cav_amt=0.3, speckle=0.3, moss=MOSS, moss_amt=0.2)
    SPEC = [
      ("TRN_Boulder_Pillar", [dict(center=(0,0,0), size=(0.50,0.42,1.55), seed=21, K=12, boxy=0.22, dmin=0.6, cracks=2, crack_depth=0.05, flat_top=0.08),
                               dict(center=(-0.32,-0.12,0), size=(0.26,0.24,0.40), seed=22, K=12, boxy=0.2, cracks=1),
                               dict(center=(0.36,0.10,0), size=(0.20,0.18,0.26), seed=23, K=10, cracks=0)]),
      ("TRN_Boulder_Block",  [dict(center=(-0.30,0.05,0), size=(0.62,0.56,0.62), seed=31, K=10, boxy=0.30, cracks=1, crack_depth=0.05, flat_top=0.12),
                               dict(center=(0.42,-0.08,0), size=(0.46,0.46,0.44), seed=32, K=10, boxy=0.30, cracks=2, flat_top=0.1),
                               dict(center=(0.05,0.45,0), size=(0.35,0.30,0.35), seed=33, K=10, boxy=0.25, cracks=1)]),
      ("TRN_Boulder_Round",  [dict(center=(0,0,0), size=(0.62,0.60,0.62), seed=41, K=26, dmin=0.8, dmax=0.95, cracks=2, crack_depth=0.05, wear=3),
                               dict(center=(-0.55,-0.25,0), size=(0.09,0.08,0.07), seed=42, K=10, subdiv=3, cracks=0)]),
      ("TRN_Boulder_Split",  [dict(center=(-0.31,0,0), size=(0.32,0.55,0.70), seed=51, K=14, boxy=0.18, cracks=2, rot=0.05),
                               dict(center=(0.33,0.02,0), size=(0.36,0.58,0.72), seed=52, K=14, boxy=0.18, cracks=2, rot=-0.05),
                               dict(center=(0.15,-0.62,0), size=(0.08,0.07,0.06), seed=53, K=8, subdiv=3, cracks=0)]),
    ]
    for i,(name,parts) in enumerate(SPEC):
        bm = bmesh.new(); bm.verts.layers.float.new("top"); bm.verts.layers.float.new("mask")
        for p in parts: rock_hq(bm, **p)
        for f in soil_patch(bm, 0.85, 60+i): f.material_index = 1
        RESULTS[name] = make_obj_hq(name, coll, bm, [mr, md], row(i,4,2.2), "TRN_Boulders.jpg")

SAND = [(0.40,0.28,0.13),(0.50,0.37,0.19),(0.60,0.47,0.27)]
def sand_disc_hq(bm, r, seed, ry=None):
    ry = ry or r*0.85; N=56; rnd=random.Random(seed)
    c = bm.verts.new((0,0,0.03)); rim=[]; lip=[]
    for i in range(N):
        a=2*math.pi*i/N; k = 1+0.06*noise.noise(Vector((math.cos(a)*2,math.sin(a)*2,seed)))
        rim.append(bm.verts.new((r*k*math.cos(a), ry*k*math.sin(a), 0.03)))
        lip.append(bm.verts.new((r*k*1.03*math.cos(a), ry*k*1.03*math.sin(a), 0.0)))
    fs=[bm.faces.new((c,rim[i],rim[(i+1)%N])) for i in range(N)]
    fs+=[bm.faces.new((rim[i],lip[i],lip[(i+1)%N],rim[(i+1)%N])) for i in range(N)]
    return fs

if BUILD == "hills":
    coll = get_coll("TRN_RockyHills")
    mr = painterly("TRN_Hill_Rock_HQ", ROCK, edge=(0.55,0.53,0.48), cavity=(0.02,0.018,0.015), moss=MOSS, moss_amt=1.0, scale=2.0, strokes=0.3, crack_lines=0.7, crack_scale=2.8)
    ms = painterly("TRN_Hill_Sand", SAND, edge_amt=0.0, cav_amt=0.4, speckle=0.25, toplight=0.1, strokes=0.35)
    S = dict(K=12, boxy=0.15)
    HILLS = [
      (0.70, [dict(center=(0,0,0), size=(0.58,0.50,0.30), seed=101, strata=5, strata_depth=0.06, flat_top=0.15, **S),
              dict(center=(0.04,0.02,0.22), size=(0.48,0.42,0.30), seed=102, K=22, dmin=0.8, dmax=0.95, wear=2)]),
      (0.75, [dict(center=(-0.20,0.05,0), size=(0.38,0.34,0.34), seed=111, cracks=0, **S), dict(center=(0.20,0.10,0), size=(0.32,0.30,0.44), seed=112, cracks=0, **S),
              dict(center=(0.02,-0.22,0), size=(0.30,0.26,0.24), seed=113, **S), dict(center=(-0.35,-0.25,0), size=(0.14,0.12,0.12), seed=114, subdiv=4, **S)]),
      (0.85, [dict(center=(0,0.05,0), size=(0.62,0.56,0.95), seed=121, K=16, dmin=0.7, cracks=0, wear=2), dict(center=(0.30,-0.30,0), size=(0.30,0.28,0.32), seed=122, **S),
              dict(center=(-0.35,-0.22,0), size=(0.24,0.22,0.22), seed=123, **S)]),
      (0.90, [dict(center=(0,0.05,0), size=(0.72,0.48,0.32), seed=131, strata=4, strata_depth=0.05, flat_top=0.2, rot=0.3, **S),
              dict(center=(0.10,0.10,0.25), size=(0.56,0.38,0.30), seed=132, strata=4, strata_depth=0.05, flat_top=0.2, rot=0.3, **S),
              dict(center=(0.20,0.12,0.48), size=(0.38,0.28,0.26), seed=133, strata=3, strata_depth=0.05, flat_top=0.2, rot=0.3, **S)]),
      (1.15, [dict(center=(0,0,0), size=(0.88,0.78,0.60), seed=141, flat_top=0.15, cracks=0, K=12, boxy=0.25),
              dict(center=(-0.12,0.08,0.50), size=(0.64,0.56,0.52), seed=142, flat_top=0.18, cracks=0, K=12, boxy=0.25),
              dict(center=(0.04,0.04,0.95), size=(0.44,0.40,0.42), seed=143, flat_top=0.2, K=12, boxy=0.25),
              dict(center=(0.52,-0.40,0), size=(0.36,0.30,0.30), seed=144, **S), dict(center=(-0.55,-0.30,0), size=(0.30,0.26,0.36), seed=145, **S)]),
      (1.20, [dict(center=(0,0,0), size=(0.95,0.85,1.40), seed=151, K=16, dmin=0.62, cracks=0, boxy=0.12, flat_top=0.1),
              dict(center=(0.58,-0.28,0), size=(0.40,0.35,0.60), seed=152, **S), dict(center=(-0.55,-0.25,0), size=(0.38,0.32,0.50), seed=153, **S),
              dict(center=(0.10,-0.62,0), size=(0.22,0.20,0.20), seed=154, **S)]),
    ]
    x = -4.9
    for i,(br,parts) in enumerate(HILLS):
        bm = bmesh.new(); bm.verts.layers.float.new("top"); bm.verts.layers.float.new("mask")
        for p in parts: rock_hq(bm, **p)
        for f in sand_disc_hq(bm, br, 200+i): f.material_index = 1
        name = "TRN_RockyHill_%02d" % (i+1)
        RESULTS[name] = make_obj_hq(name, coll, bm, [mr, ms], (x*0.7071,-x*0.7071,0), "TRN_RockyHills.jpg", {"footprint_m": round(2*br,2)})
        x += br + 0.30 + (HILLS[i+1][0] if i+1 < len(HILLS) else 0)

if BUILD == "cliffs":
    coll = get_coll("TRN_CliffEdge")
    STRATA = [(0.36,0.24,0.13),(0.46,0.33,0.19),(0.26,0.25,0.23),(0.52,0.39,0.24),(0.40,0.29,0.17),(0.33,0.31,0.28)]
    mc = painterly("TRN_Cliff_Strata_HQ", [(0.34,0.24,0.14),(0.42,0.31,0.19),(0.50,0.38,0.24)], edge=(0.72,0.62,0.46), cavity=(0.05,0.035,0.02),
                   dirt=(0.07,0.06,0.035), dirt_h=0.3, strokes=0.35, crack_lines=0.5, crack_scale=1.6, bands=STRATA, band_scale=3.2, toplight=0.2)
    # swappable top surfaces = the six ValleyGround grounds (same palettes as build_trn_valleyground.py)
    SURF = {
      "GrassShort": dict(base=[(0.10,0.21,0.02),(0.16,0.30,0.035),(0.23,0.39,0.05)], edge=(0.42,0.56,0.14), cavity=(0.02,0.05,0.008)),
      "GrassLush":  dict(base=[(0.006,0.075,0.008),(0.012,0.13,0.012),(0.025,0.19,0.02)], edge=(0.10,0.38,0.08), cavity=(0.002,0.02,0.003)),
      "GrassDry":   dict(base=[(0.28,0.30,0.07),(0.55,0.30,0.06),(0.66,0.44,0.10),(0.75,0.55,0.15)], edge=(0.85,0.70,0.35), cavity=(0.10,0.06,0.02)),
      "Dirt":       dict(base=[(0.19,0.085,0.03),(0.30,0.14,0.055),(0.40,0.20,0.08)], edge=(0.55,0.38,0.22), cavity=(0.05,0.025,0.01)),
      "Rock":       dict(base=[(0.085,0.085,0.08),(0.15,0.15,0.14),(0.22,0.22,0.20)], edge=(0.45,0.44,0.40), cavity=(0.02,0.02,0.018)),
      "Mud":        dict(base=[(0.05,0.019,0.009),(0.09,0.036,0.016),(0.14,0.058,0.026)], edge=(0.30,0.16,0.08), cavity=(0.015,0.006,0.003), wet=(0.06,0.2)),
    }
    TOPMAT = {}
    for k,v in SURF.items():
        TOPMAT[k] = painterly("TRN_Top_"+k, v["base"], edge=v["edge"], cavity=v["cavity"], dirt=v["base"][0], dirt_h=-1,
                              strokes=0.45, speckle=0.08, toplight=0.35, edge_amt=0.45, wet=v.get("wet"))
        TOPMAT[k].use_fake_user = True
    DEMO = {"TRN_Cliff_Straight":"GrassShort","TRN_Cliff_OuterCorner":"GrassLush","TRN_Cliff_InnerCorner":"GrassDry","TRN_Cliff_End":"Dirt","TRN_Cliff_Tall":"GrassShort"}
    def resample(pts, step=0.05):
        out=[]; n=len(pts)
        for i in range(n):
            a=Vector(pts[i]); b=Vector(pts[(i+1)%n]); L=(b-a).length; k=max(1,int(L/step))
            for j in range(k): out.append(a.lerp(b,j/k))
        return out
    def arc(cx,cy,r,a0,a1,n=16): return [(cx+r*math.cos(a0+(a1-a0)*i/n), cy+r*math.sin(a0+(a1-a0)*i/n)) for i in range(n+1)]
    def rounded(pts, r=0.08):
        """round convex corners of an outline a little"""
        out=[]; n=len(pts)
        for i in range(n):
            p0,p1,p2 = Vector(pts[i-1]),Vector(pts[i]),Vector(pts[(i+1)%n])
            a=(p0-p1).normalized(); b=(p2-p1).normalized()
            out += [tuple(p1+a*r), tuple(p1+(a+b).normalized()*r*0.42), tuple(p1+b*r)]
        return out
    OUTL = {
      "TRN_Cliff_Straight":    (rounded([(-1,-0.5),(1,-0.5),(1,0.5),(-1,0.5)]), 2.0),
      "TRN_Cliff_OuterCorner": (rounded([(-1,-1),(1,-1),(1,0.0),(0.0,0.0),(0.0,1),(-1,1)]), 2.0),
      "TRN_Cliff_InnerCorner": ([(-1,-0.5)] + arc(0,-0.5,0.55,math.pi,0,20)[1:-1] + [(1,-0.5),(1,0.5),(-1,0.5)], 2.0),
      "TRN_Cliff_End":         ([(-1,-0.5),(0.5,-0.5)] + arc(0.5,0,0.5,-math.pi/2,math.pi/2,18)[1:-1] + [(0.5,0.5),(-1,0.5)], 2.0),
      "TRN_Cliff_Tall":        (rounded([(-1,-0.5),(1,-0.5),(1,0.5),(-1,0.5)]), 4.0),
    }
    x = -5.2
    for name,(pts,Hc) in OUTL.items():
        P = resample(pts); N=len(P); seed=len(name)
        nrm=[]
        for i in range(N):
            t=(P[(i+1)%N]-P[i-1]); t.normalize(); nrm.append(Vector((t.y,-t.x)))
        bm = bmesh.new(); bm.verts.layers.float.new("top"); bm.verts.layers.float.new("mask")
        nz_ = int(Hc/0.035); rings=[]
        bands = []; z=0
        rb = random.Random(seed)
        while z < Hc: h=rb.uniform(0.14,0.48); bands.append((z,z+h,rb.uniform(-0.06,0.06))); z+=h
        for k in range(nz_+1):
            z = Hc*k/nz_; ring=[]
            b = next((bb for bb in bands if bb[0]<=z<=bb[1]), bands[-1]); fr=(z-b[0])/max(1e-4,b[1]-b[0])
            for i,p in enumerate(P):
                bulge = 0.022*min(1.0, 4*fr*(1-fr))**0.35 - 0.03*(1-min(1.0,fr/0.06))
                off = b[2] + bulge + 0.018*noise.noise(Vector((p.x*3,p.y*3,z*2+seed))) + 0.03*noise.noise(Vector((p.x*0.8,p.y*0.8,b[0]*3+seed)))
                if z < 0.18: off -= 0.03*(1-z/0.18)
                q = p + nrm[i]*off; ring.append(bm.verts.new((q.x,q.y,z)))
            rings.append(ring)
        walls=[]
        for a,b2 in zip(rings[:-1],rings[1:]):
            for i in range(N):
                j=(i+1)%N; walls.append(bm.faces.new((a[i],a[j],b2[j],b2[i])))
        walls.append(bm.faces.new(list(reversed(rings[0]))))
        WALLTOP = [v.co.copy() for v in rings[-1]]
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        pos = (x*0.7071,-x*0.7071,0)
        RESULTS[name] = make_obj_hq(name, coll, bm, [mc], pos, "TRN_CliffEdge.jpg", {"height_m":Hc}, sharp=70)
        wall_ob = bpy.data.objects[name]
        topring = [Vector((v.x, v.y, v.z)) for v in [rv.co.copy() for rv in []]] if False else None
        # ---- swappable TOP: separate object, one material slot (pick any TRN_Top_* surface) ----
        bm = bmesh.new(); bm.verts.layers.float.new("top"); bm.verts.layers.float.new("mask")
        wr = [bm.verts.new(c) for c in WALLTOP]
        cb=[]; cm=[]; ct=[]
        for i,p in enumerate(P):
            drip = 0.30*max(0.0, noise.noise(Vector((p.x*4.5,p.y*4.5,seed+3)))-0.0)**0.8 + 0.08*max(0.0,noise.noise(Vector((p.x*13,p.y*13,seed))))
            q=p+nrm[i]*0.06; cb.append(bm.verts.new((q.x,q.y,Hc-0.05-drip)))
            q=p+nrm[i]*0.065; cm.append(bm.verts.new((q.x,q.y,Hc+0.03)))
            q=p+nrm[i]*0.03; ct.append(bm.verts.new((q.x,q.y,Hc+0.08)))
        cap=[]
        for i in range(N):
            j=(i+1)%N
            cap.append(bm.faces.new((wr[i],wr[j],cb[j],cb[i])))
            cap.append(bm.faces.new((cb[i],cb[j],cm[j],cm[i])))
            cap.append(bm.faces.new((cm[i],cm[j],ct[j],ct[i])))
        top = bm.faces.new(ct); cap.append(top)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bmesh.ops.triangulate(bm, faces=[top])
        surf = DEMO[name]
        tn = name + "_Top"
        RESULTS[tn] = make_obj_hq(tn, coll, bm, [TOPMAT[surf]], pos, "TRN_CliffEdge.jpg",
                                  {"top_surface": surf, "swap_with": "any TRN_Top_* material (GrassShort, GrassLush, GrassDry, Dirt, Rock, Mud)"}, sharp=70)
        top_ob = bpy.data.objects[tn]; top_ob.parent = wall_ob; top_ob.location = (0,0,0)
        x += 2.6
