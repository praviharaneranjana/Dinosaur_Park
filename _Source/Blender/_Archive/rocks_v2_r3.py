"""Dino Park Tycoon - rocks v2 HQ: BUILD = "boulders" | "hills" | "cliffs" (exec with TOOLS)."""
import os
exec(open(os.path.join(TOOLS, "trn_common.py")).read())
exec(open(os.path.join(TOOLS, "trn_hq.py")).read())
random.seed(5)
RESULTS = {}
ROCK = [(0.055,0.053,0.048),(0.11,0.105,0.093),(0.18,0.17,0.15),(0.26,0.25,0.22)]
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
    mr = painterly("TRN_Rock_HQ", ROCK, moss=MOSS, moss_amt=0.35, scale=2.0)
    md = painterly("TRN_Rock_Soil", [(0.10,0.07,0.04),(0.17,0.12,0.07),(0.24,0.18,0.11)], edge_amt=0, cav_amt=0.3, speckle=0.3, moss=MOSS, moss_amt=0.2)
    SPEC = [
      ("TRN_Boulder_Pillar", [dict(center=(0,0,0), size=(0.50,0.42,1.55), seed=21, K=12, boxy=0.22, dmin=0.6, cracks=4, crack_depth=0.09, flat_top=0.08),
                               dict(center=(-0.32,-0.12,0), size=(0.26,0.24,0.40), seed=22, K=12, boxy=0.2, cracks=1),
                               dict(center=(0.36,0.10,0), size=(0.20,0.18,0.26), seed=23, K=10, cracks=0)]),
      ("TRN_Boulder_Block",  [dict(center=(-0.30,0.05,0), size=(0.62,0.56,0.62), seed=31, K=10, boxy=0.30, cracks=3, crack_depth=0.08, flat_top=0.12),
                               dict(center=(0.42,-0.08,0), size=(0.46,0.46,0.44), seed=32, K=10, boxy=0.30, cracks=2, flat_top=0.1),
                               dict(center=(0.05,0.45,0), size=(0.35,0.30,0.35), seed=33, K=10, boxy=0.25, cracks=1)]),
      ("TRN_Boulder_Round",  [dict(center=(0,0,0), size=(0.62,0.60,0.62), seed=41, K=26, dmin=0.8, dmax=0.95, cracks=4, crack_depth=0.05, wear=3),
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
