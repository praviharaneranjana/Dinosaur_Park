"""
Dino Park Tycoon - TRN_ValleyGround builder (source / high-detail version)
Source image : _Reference/New/TRN_ValleyGround.jpg
Tile         : 2.0 x 2.0 m, 0.4 m thick, pivot = centre of top face, Z up, edges flat so tiles snap.
Tiles        : TRN_Grass_Short, TRN_Grass_Lush, TRN_Grass_Dry, TRN_Dirt_Pebbles, TRN_Rock_Grey, TRN_Mud_Wet
Run inside Blender: exec(open(r"<path>/build_trn_valleyground.py").read())
Re-running rebuilds the collection TRN_ValleyGround from scratch (deterministic, seed 42).
Game mesh: baked later from this source onto a low-poly tile (see BUILD_ORDER.md).
"""
import bpy, bmesh, math, random
from mathutils import Matrix, Vector, noise

sc = bpy.context.scene
coll = bpy.data.collections.get("TRN_ValleyGround")
if coll is None:
    coll = bpy.data.collections.new("TRN_ValleyGround"); sc.collection.children.link(coll)
for o in list(coll.objects):
    me = o.data; bpy.data.objects.remove(o, do_unlink=True)
    if me and me.users == 0: bpy.data.meshes.remove(me)

T = 0.4; R = 0.1
def clamp(v,a=0.0,b=1.0): return max(a,min(b,v))
def sstep(e0,e1,x):
    t = clamp((x-e0)/(e1-e0)); return t*t*(3-2*t)
def nn(x,y,s,seed=0): return noise.noise(Vector((x*s+seed*17.3, y*s+seed*5.1, seed*3.7)))
RC = 0.10   # plan-view corner radius (rounded vertical corners)
def plan_map(x,y):
    ax,ay = abs(x),abs(y)
    if ax > 1-RC and ay > 1-RC:
        dx,dy = ax-(1-RC), ay-(1-RC); L = math.hypot(dx,dy)
        if L > 0: f = max(dx,dy)/L; dx*=f; dy*=f
        return math.copysign(1-RC+dx,x), math.copysign(1-RC+dy,y)
    return x,y
def edge_d(x,y):
    ax,ay = abs(x),abs(y)
    if ax > 1-RC and ay > 1-RC: return max(0.0, RC-math.hypot(ax-(1-RC), ay-(1-RC)))
    return max(0.0, min(1-ax, 1-ay))
def shoulder(x,y):
    d = edge_d(x,y)
    if d >= R: return 0.0
    q = R-d; return -(R-math.sqrt(max(0.0,R*R-q*q)))
def corner_free(x,y): return 1-sstep(0.78,0.9,min(abs(x),abs(y)))

# ---------------- mud features ----------------
def puddle_e(x,y,p):
    cx,cy,rx,ry,sd = p
    return (((x-cx)/rx)**2 + ((y-cy)/ry)**2)*(1+0.25*nn(x,y,4,sd))
PUDDLES = [(0.12,0.48,0.40,0.22,11),(0.12,-0.22,0.34,0.23,12),(-0.60,0.18,0.16,0.10,13)]
PRINTS  = [(-0.52,-0.45,math.radians(-20),1.55),(0.56,-0.62,math.radians(-70),1.4)]   # x, y, heading, scale
def seg_s(px,py,ax,ay,bx,by,r):
    vx,vy = bx-ax,by-ay; L2 = vx*vx+vy*vy
    t = clamp(((px-ax)*vx+(py-ay)*vy)/L2)
    return math.hypot(px-(ax+vx*t), py-(ay+vy*t))/(r*(1-0.4*t))
def print_s(x,y,pr):
    cx,cy,hd,sz = pr; c,s_ = math.cos(-hd), math.sin(-hd)
    u = ((x-cx)*c - (y-cy)*s_)/sz; v = ((x-cx)*s_ + (y-cy)*c)/sz
    s = math.hypot(u/0.105, v/0.125)
    for a in (-32,0,32):
        ar = math.radians(a); L = 0.20 if a==0 else 0.17
        s = min(s, seg_s(u,v,0,0.07,math.sin(ar)*L,0.07+math.cos(ar)*L,0.055))
    return s

# ---------------- height fields ----------------
def h_short(x,y): return 0.012*nn(x,y,1.5,1)+0.006*nn(x,y,4,2)
def h_lush(x,y):  return 0.018*nn(x,y,1.3,3)+0.008*nn(x,y,5,4)
def h_dry(x,y):   return 0.016*nn(x,y,1.6,5)+0.009*nn(x,y,5,6)
def h_dirt(x,y):  return 0.014*nn(x,y,1.2,7)+0.006*nn(x,y,6,8)
def h_rock(x,y):  return 0.05*nn(x,y,1.4,9)+0.025*nn(x,y,4.5,10)-0.035*abs(nn(x,y,3.2,24))
def h_mud(x,y):
    z = 0.020*nn(x,y,1.5,15)+0.008*nn(x,y,5,16)
    for p in PUDDLES:
        w = 1-sstep(0.85,1.35,puddle_e(x,y,p)); z = z*(1-w) - 0.04*w
    for pr in PRINTS:
        s = print_s(x,y,pr); w = 1-sstep(0.5,1.0,s)
        z = z*(1-w) - 0.046*w + 0.007*sstep(0.95,1.2,s)*(1-sstep(1.3,1.9,s))
    return z
HF = dict(short=h_short,lush=h_lush,dry=h_dry,dirt=h_dirt,rock=h_rock,mud=h_mud)
def height(kind,x,y):
    d = edge_d(x,y); f = sstep(0.04,0.30,d)
    z = HF[kind](x,y)*f + shoulder(x,y)
    if kind == "rock": z -= 0.06*max(0.0, nn(x,y,5,21)-0.2)*clamp(1-d/0.16)*corner_free(x,y)
    if kind == "dirt": z -= 0.03*max(0.0, nn(x,y,4,22)-0.35)*clamp(1-d/0.12)*corner_free(x,y)
    return z

# ---------------- materials ----------------
def new_mat(name):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bs.outputs[0], out.inputs[0]); return m, nt, bs
def ramp(nt, cols, pos=None):
    r = nt.nodes.new("ShaderNodeValToRGB"); el = r.color_ramp.elements
    while len(el) < len(cols): el.new(0.5)
    pos = pos or [0.25+0.5*i/(len(cols)-1) for i in range(len(cols))]
    for e,c,p in zip(el,cols,pos): e.position = p; e.color = (*c,1)
    return r
def noise_n(nt, vec, scale, detail=5, rough=0.6):
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = detail; n.inputs["Roughness"].default_value = rough
    nt.links.new(vec, n.inputs["Vector"]); return n
def mapping(nt, vec, scale=(1,1,1), rotz=0.0):
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = scale
    mp.inputs["Rotation"].default_value = (0,0,rotz); nt.links.new(vec, mp.inputs["Vector"]); return mp.outputs[0]
def mix(nt, a, b, fac=1.0, blend='MIX'):
    m = nt.nodes.new("ShaderNodeMix"); m.data_type='RGBA'; m.blend_type = blend
    if isinstance(fac,float): m.inputs[0].default_value = fac
    else: nt.links.new(fac, m.inputs[0])
    for i,s in ((6,a),(7,b)):
        if isinstance(s,tuple): m.inputs[i].default_value = (*s,1)
        else: nt.links.new(s, m.inputs[i])
    return m.outputs[2]
def maprange(nt, val, a, b, c=0.0, d=1.0):
    r = nt.nodes.new("ShaderNodeMapRange"); nt.links.new(val, r.inputs["Value"])
    r.inputs["From Min"].default_value=a; r.inputs["From Max"].default_value=b
    r.inputs["To Min"].default_value=c; r.inputs["To Max"].default_value=d; return r.outputs[0]
def mathop(nt, a, b, op='MULTIPLY'):
    m = nt.nodes.new("ShaderNodeMath"); m.operation = op
    nt.links.new(a, m.inputs[0]); nt.links.new(b, m.inputs[1]); return m.outputs[0]

def painted(name, top, side, rough=0.9, streak=0.35, bump=0.18, scale=2.2, rough_var=None, rim=0.22, rimcol=(1,1,0.9), lowdark=None):
    """Hand-painted look: top colour ramp + brush streaks, side ramp with vertical strokes,
    light rim on the rounded shoulder, darker toward the tile bottom."""
    m, nt, bs = new_mat(name)
    tc = nt.nodes.new("ShaderNodeTexCoord"); obj = tc.outputs["Object"]
    n1 = noise_n(nt, obj, scale, 6, 0.62)
    rt = ramp(nt, top); nt.links.new(n1.outputs["Fac"], rt.inputs[0])
    n2 = noise_n(nt, mapping(nt,obj,(1.6,10,1),0.7), 2.5, 3, 0.5)
    topc = mix(nt, rt.outputs[0], n2.outputs["Fac"], streak, 'SOFT_LIGHT')
    n3 = noise_n(nt, mapping(nt,obj,(7,7,1.3)), 2.0, 5, 0.6)
    rs = ramp(nt, side); nt.links.new(n3.outputs["Fac"], rs.inputs[0])
    geo = nt.nodes.new("ShaderNodeNewGeometry"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Normal"], sep.inputs[0]); nz = sep.outputs[2]
    col = mix(nt, rs.outputs[0], topc, maprange(nt, nz, 0.55, 0.85))
    rimf = mathop(nt, maprange(nt, nz, 0.45, 0.72), maprange(nt, nz, 0.97, 0.86))
    col = mix(nt, col, rimcol, mathop(nt, rimf, maprange(nt, n1.outputs["Fac"], 0.3, 0.7, rim*0.5, rim)), 'SOFT_LIGHT')
    sepo = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(obj, sepo.inputs[0])
    col = mix(nt, col, maprange(nt, sepo.outputs[2], -T, -0.08, 0.6, 1.0), 1.0, 'MULTIPLY')
    low = None
    if lowdark:
        low = maprange(nt, sepo.outputs[2], lowdark[0], lowdark[1])
        col = mix(nt, col, (0.45,0.40,0.36), mathop(nt, low, mathop(nt, maprange(nt, nz, 0.5, 0.8), low, 'MINIMUM'), 'MAXIMUM'), 'MULTIPLY')
    nt.links.new(col, bs.inputs["Base Color"])
    n4 = noise_n(nt, obj, 22, 4, 0.6); bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump; bp.inputs["Distance"].default_value = 0.02
    nt.links.new(n4.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs[0], bs.inputs["Normal"])
    if rough_var:
        rv = maprange(nt, n1.outputs["Fac"], 0.3, 0.7, rough_var[0], rough_var[1])
        if low is not None: rv = mathop(nt, rv, maprange(nt, low, 0, 1, 1.0, 0.35))
        nt.links.new(rv, bs.inputs["Roughness"])
    else: bs.inputs["Roughness"].default_value = rough
    return m
def blade_mat(name, root, tip, alt, hmax):
    m, nt, bs = new_mat(name)
    tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    r = ramp(nt, [root, tip]); nt.links.new(maprange(nt, sep.outputs[2], -0.03, hmax), r.inputs[0])
    n = noise_n(nt, tc.outputs["Object"], 5, 2, 0.5)
    col = mix(nt, r.outputs[0], alt, maprange(nt, n.outputs["Fac"], 0.42, 0.62, 0.0, 0.5))
    nt.links.new(col, bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.85
    return m
def flat_mat(name, c, rough=0.85, spec=0.5):
    m, nt, bs = new_mat(name); bs.inputs["Base Color"].default_value = (*c,1)
    bs.inputs["Roughness"].default_value = rough; bs.inputs["Specular IOR Level"].default_value = spec
    return m
def water_mat(name):
    m, nt, bs = new_mat(name)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n = noise_n(nt, mapping(nt, tc.outputs["Object"], (1.5,6,1), 0.5), 3.0, 4, 0.55)
    r = ramp(nt, [(0.09,0.06,0.04),(0.17,0.12,0.08),(0.30,0.25,0.19),(0.72,0.70,0.64)], [0.36,0.58,0.72,0.80])
    nt.links.new(n.outputs["Fac"], r.inputs[0]); nt.links.new(r.outputs[0], bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = 0.015; bs.inputs["Specular IOR Level"].default_value = 1.0
    return m

# ---------------- geometry ----------------
def axis_coords(n):
    edge = [-1.0,-0.988,-0.972,-0.95,-0.925]
    inner = [-0.9 + 1.8*i/(n-1) for i in range(n)]
    return edge + inner + [-v for v in reversed(edge)]
def build_block(bm, kind, n):
    U = axis_coords(n); N = len(U)
    vg = [[bm.verts.new((*plan_map(x,y), height(kind,*plan_map(x,y)))) for y in U] for x in U]
    fs = []
    for i in range(N-1):
        for j in range(N-1):
            fs.append(bm.faces.new((vg[i][j],vg[i+1][j],vg[i+1][j+1],vg[i][j+1])))
    per = [vg[i][0] for i in range(N)] + [vg[N-1][j] for j in range(1,N)] + \
          [vg[i][N-1] for i in range(N-2,-1,-1)] + [vg[0][j] for j in range(N-2,0,-1)]
    rings = [per]
    for z in (-T*0.55, -T):
        ring = []
        for v in per:
            x,y = v.co.x, v.co.y; k = 0.0
            if kind=="rock" and z > -T+0.01: k = 0.012*max(0.0,nn(x,y,6,23)+0.3)
            ring.append(bm.verts.new((x*(1-k), y*(1-k), z)))
        rings.append(ring)
    M = len(per)
    for a,b in zip(rings[:-1], rings[1:]):
        for k in range(M):
            q=(k+1)%M; fs.append(bm.faces.new((a[k],b[k],b[q],a[q])))
    fs.append(bm.faces.new(list(reversed(rings[-1]))))
    return fs
def mark(faces, idx):
    for f in faces: f.material_index = idx
def blade(bm, x,y,z, h, w, ang, lean):
    dx,dy = math.cos(ang), math.sin(ang); px,py = -dy, dx
    bl = bm.verts.new((x-px*w/2, y-py*w/2, z-0.015)); br = bm.verts.new((x+px*w/2, y+py*w/2, z-0.015))
    mo = lean*0.35*h
    ml = bm.verts.new((x+dx*mo-px*w*0.32, y+dy*mo-py*w*0.32, z+0.55*h)); mr = bm.verts.new((x+dx*mo+px*w*0.32, y+dy*mo+py*w*0.32, z+0.55*h))
    tp = bm.verts.new((x+dx*lean*h, y+dy*lean*h, z+h*(1-0.25*lean)))
    return [bm.faces.new((bl,br,mr,ml)), bm.faces.new((ml,mr,tp))]
def clump(bm, kind, x,y, n, hmin,hmax, spread, wid, lean=(0.25,0.75)):
    fs = []
    for _ in range(n):
        a = random.uniform(0,6.283); r = random.uniform(0,spread)
        bx,by = x+math.cos(a)*r, y+math.sin(a)*r
        if max(abs(bx),abs(by)) > 0.985: continue
        fs += blade(bm,bx,by,height(kind,bx,by),random.uniform(hmin,hmax),wid,a+random.uniform(-0.6,0.6),random.uniform(*lean))
    return fs
def fringe(bm, kind, count, hmin, hmax, wid):
    fs = []
    for side in range(4):
        for _ in range(count):
            t = random.uniform(-0.9,0.9); inset = random.uniform(0.008,0.05)
            x,y,out = [(t,-1+inset,-math.pi/2),(1-inset,t,0.0),(t,1-inset,math.pi/2),(-1+inset,t,math.pi)][side]
            fs += blade(bm,x,y,height(kind,x,y),random.uniform(hmin,hmax),wid,out+random.uniform(-0.7,0.7),random.uniform(0.35,0.85))
    return fs
def scatter_pts(n, lim=0.86):
    return [(random.uniform(-lim,lim), random.uniform(-lim,lim)) for _ in range(n)]
def pebble(bm, kind, x,y, r, embed=0.15, flat=(0.45,0.65)):
    z = height(kind,x,y)
    res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r,
        matrix=Matrix.Translation((x,y,z+r*embed)) @ Matrix.Rotation(random.uniform(0,6.28),4,'Z') @ Matrix.Diagonal((1,random.uniform(0.7,1.0),random.uniform(*flat),1)))
    return list({f for v in res["verts"] for f in v.link_faces})
def slab(bm, kind, cx,cy, r, ang, sd):
    z = height(kind,cx,cy); n = 10; rb=[]; rt=[]; ri=[]
    for k in range(n):
        a = 2*math.pi*k/n; rr = r*(0.70+0.65*(nn(math.cos(a)*1.7,math.sin(a)*1.7,1.6,sd)+0.5))
        lx,ly = math.cos(a)*rr, math.sin(a)*rr*(0.45+0.4*((sd*37)%10)/10)
        x = cx + lx*math.cos(ang)-ly*math.sin(ang); y = cy + lx*math.sin(ang)+ly*math.cos(ang)
        zt = max(z, height(kind,x,y)) + 0.02 + 0.03*((sd*13)%7)/7 + 0.025*(lx/max(r,0.01))*(((sd*7)%3)-1)
        rb.append(bm.verts.new((x,y,zt-0.08))); rt.append(bm.verts.new((x,y,zt)))
        ri.append(bm.verts.new((cx+(x-cx)*0.8, cy+(y-cy)*0.8, zt+0.016+0.006*nn(x,y,9,sd))))
    fs=[]
    for k in range(n):
        q=(k+1)%n
        fs.append(bm.faces.new((rb[k],rb[q],rt[q],rt[k]))); fs.append(bm.faces.new((rt[k],rt[q],ri[q],ri[k])))
    fs.append(bm.faces.new(ri)); return fs
def clover(bm, kind, x,y, L, rot):
    fs=[]; z = height(kind,x,y)+0.014
    shape = [(0,0),(0.35,-0.36),(0.8,-0.46),(1.0,-0.2),(0.86,0),(1.0,0.2),(0.8,0.46),(0.35,0.36)]
    for k in range(3):
        a = rot + k*2.094 + random.uniform(-0.2,0.2); vs=[]
        for (u,v) in shape:
            vs.append(bm.verts.new((x+(u*math.cos(a)-v*math.sin(a))*L, y+(u*math.sin(a)+v*math.cos(a))*L, z+0.3*u*L)))
        fs.append(bm.faces.new(vs))
    return fs
def water(bm, p, z=-0.022):
    cx,cy,rx,ry,sd = p; vs=[]
    for k in range(32):
        a = 2*math.pi*k/32; r = 1.0
        for _ in range(4):
            x = cx+math.cos(a)*rx*r; y = cy+math.sin(a)*ry*r
            r = math.sqrt(1.02/(1+0.25*nn(x,y,4,sd)))
        vs.append(bm.verts.new((cx+math.cos(a)*rx*r, cy+math.sin(a)*ry*r, z)))
    return [bm.faces.new(vs)]

def tile(name, kind, n, mats, details, pos):
    bm = bmesh.new(); blk = build_block(bm, kind, n); nb = len(blk)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    for f in bm.faces: f.material_index = 0
    for idx, fn in details: mark(fn(bm), idx)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    me.shade_smooth()
    try: me.set_sharp_from_angle(angle=math.radians(50))
    except Exception: pass
    # freestyle outline only on the block (not on grass blades)
    a = me.attributes.get("freestyle_face") or me.attributes.new("freestyle_face",'BOOLEAN','FACE')
    a.data.foreach_set("value", [i < nb for i in range(len(me.polygons))])
    ob = bpy.data.objects.new(name, me); ob.location = pos; coll.objects.link(ob)
    ob["source_image"] = "TRN_ValleyGround.jpg"; ob["tile_size_m"] = 2.0; ob["thickness_m"] = T
    me.calc_loop_triangles(); return len(me.loop_triangles)

# ---------------- tile recipes ----------------
random.seed(42)
RESULTS = {}
G = 2.7
P = [(-G, G/2,0),(0,G/2,0),(G,G/2,0),(-G,-G/2,0),(0,-G/2,0),(G,-G/2,0)]

mb = painted("TRN_Grass_Short_Body", [(0.10,0.21,0.02),(0.16,0.30,0.035),(0.23,0.39,0.05)], [(0.05,0.12,0.01),(0.08,0.16,0.013),(0.11,0.21,0.017)], streak=0.45)
ml = blade_mat("TRN_Grass_Short_Blade", (0.10,0.21,0.018),(0.38,0.52,0.11),(0.26,0.40,0.06),0.12)
def d_short(bm):
    fs=[]
    for (x,y) in scatter_pts(34): fs += clump(bm,"short",x,y,4,0.05,0.10,0.035,0.014)
    fs += fringe(bm,"short",7,0.05,0.09,0.014); return fs
RESULTS["TRN_Grass_Short"] = tile("TRN_Grass_Short","short",40,[mb,ml],[(1,d_short)],P[0])

mb = painted("TRN_Grass_Lush_Body", [(0.006,0.075,0.008),(0.012,0.13,0.012),(0.025,0.19,0.02)], [(0.003,0.045,0.005),(0.007,0.075,0.008),(0.011,0.10,0.011)], streak=0.55, rimcol=(0.6,1,0.5))
ml = blade_mat("TRN_Grass_Lush_Blade", (0.006,0.08,0.008),(0.09,0.36,0.06),(0.03,0.22,0.025),0.12)
mc = painted("TRN_Clover_Leaf", [(0.03,0.20,0.03),(0.05,0.28,0.045),(0.08,0.33,0.05)], [(0.03,0.20,0.03),(0.05,0.28,0.045)], streak=0.2, bump=0.05, scale=9, rim=0.0)
mf = flat_mat("TRN_Clover_Flower", (0.82,0.72,0.74), 0.7)
def d_lush(bm):
    fs=[]
    for (x,y) in scatter_pts(260): fs += clump(bm,"lush",x,y,4,0.05,0.10,0.04,0.017)
    fs += fringe(bm,"lush",36,0.05,0.12,0.016); return fs
CL = [(-0.45,-0.05,10),(0.45,0.25,9),(-0.05,-0.55,7),(0.15,0.65,3),(-0.6,0.45,3),(0.65,-0.45,4),(0.62,0.62,1)]
def d_clover(bm):
    fs=[]
    for (cx,cy,k) in CL:
        for _ in range(k):
            fs += clover(bm,"lush",cx+random.uniform(-0.17,0.17),cy+random.uniform(-0.17,0.17),random.uniform(0.045,0.065),random.uniform(0,6.28))
    return fs
def d_flower(bm):
    fs=[]
    for (x,y) in [(-0.33,0.06),(-0.55,-0.14),(0.40,0.36),(0.56,0.16),(-0.08,-0.44),(0.22,-0.18),(0.64,-0.36)]:
        fs += pebble(bm,"lush",x,y,0.03,2.2,(0.8,0.95))
    return fs
RESULTS["TRN_Grass_Lush"] = tile("TRN_Grass_Lush","lush",40,[mb,ml,mc,mf],[(1,d_lush),(2,d_clover),(3,d_flower)],P[1])

mb = painted("TRN_Grass_Dry_Body", [(0.28,0.30,0.07),(0.55,0.30,0.06),(0.66,0.44,0.10),(0.75,0.55,0.15)], [(0.12,0.07,0.03),(0.20,0.11,0.047),(0.27,0.17,0.07)], streak=0.4)
ml = blade_mat("TRN_Grass_Dry_Blade", (0.40,0.22,0.04),(0.82,0.60,0.18),(0.64,0.40,0.08),0.2)
mg = blade_mat("TRN_Grass_Dry_GreenBlade", (0.02,0.05,0.01),(0.09,0.16,0.035),(0.06,0.12,0.025),0.15)
def d_dry(bm):
    fs=[]
    for (x,y) in scatter_pts(165): fs += clump(bm,"dry",x,y,14,0.08,0.20,0.07,0.024,(0.15,0.5))
    fs += fringe(bm,"dry",34,0.08,0.18,0.022); return fs
def d_dry_g(bm):
    fs=[]
    for (x,y) in scatter_pts(8): fs += clump(bm,"dry",x,y,6,0.08,0.15,0.03,0.014)
    return fs
RESULTS["TRN_Grass_Dry"] = tile("TRN_Grass_Dry","dry",40,[mb,ml,mg],[(1,d_dry),(2,d_dry_g)],P[2])

mb = painted("TRN_Dirt_Body", [(0.19,0.085,0.03),(0.30,0.14,0.055),(0.40,0.20,0.08)], [(0.10,0.045,0.018),(0.15,0.065,0.025),(0.21,0.10,0.04)], streak=0.5)
mp = painted("TRN_Dirt_Pebble", [(0.36,0.27,0.18),(0.52,0.42,0.30)], [(0.24,0.17,0.11),(0.32,0.24,0.16)], streak=0.1, bump=0.05, scale=12, rim=0.0)
def d_peb(bm):
    fs=[]
    for (x,y) in scatter_pts(18): fs += pebble(bm,"dirt",x,y,random.uniform(0.02,0.045))
    for (x,y) in [(-0.45,0.10),(0.1,-0.55),(0.55,0.4)]: fs += pebble(bm,"dirt",x,y,0.06)
    return fs
RESULTS["TRN_Dirt_Pebbles"] = tile("TRN_Dirt_Pebbles","dirt",40,[mb,mp],[(1,d_peb)],P[3])

mb = painted("TRN_Rock_Body", [(0.085,0.085,0.08),(0.15,0.15,0.14),(0.22,0.22,0.20)], [(0.045,0.045,0.043),(0.085,0.085,0.08),(0.13,0.13,0.12)], streak=0.35, bump=0.5, rimcol=(0.9,0.9,0.85), lowdark=(-0.02,-0.07))
ms = painted("TRN_Rock_Slab", [(0.15,0.15,0.14),(0.21,0.21,0.195),(0.27,0.27,0.25)], [(0.05,0.05,0.048),(0.08,0.08,0.075)], streak=0.3, bump=0.3, scale=5, rim=0.35)
SLABS = [(-0.42,0.18,0.30,0.3),(0.12,0.58,0.24,0.1),(-0.18,-0.30,0.20,-0.4),(0.58,0.30,0.15,0.6),(-0.62,0.58,0.12,0.2),(0.48,-0.42,0.13,-0.2),(-0.62,-0.55,0.10,1.0),(0.20,0.05,0.09,0.8)]
def d_slab(bm):
    fs=[]
    for i,(x,y,r,a) in enumerate(SLABS): fs += slab(bm,"rock",x,y,r,a,30+i)
    for (x,y) in scatter_pts(24): fs += pebble(bm,"rock",x,y,random.uniform(0.02,0.055),0.05)
    return fs
RESULTS["TRN_Rock_Grey"] = tile("TRN_Rock_Grey","rock",60,[mb,ms],[(1,d_slab)],P[4])

mb = painted("TRN_Mud_Body", [(0.05,0.019,0.009),(0.09,0.036,0.016),(0.14,0.058,0.026)], [(0.03,0.013,0.007),(0.05,0.022,0.011),(0.08,0.035,0.017)], streak=0.5, bump=0.1, rough_var=(0.05,0.16), rimcol=(1,0.85,0.7), lowdark=(-0.012,-0.04))
mw = water_mat("TRN_Mud_Water")
def d_water(bm):
    fs=[]
    for p in PUDDLES: fs += water(bm,p)
    return fs
RESULTS["TRN_Mud_Wet"] = tile("TRN_Mud_Wet","mud",64,[mb,mw],[(1,d_water)],P[5])

w = sc.world; w.use_nodes = True; wn = w.node_tree; wn.nodes.clear()
wo = wn.nodes.new("ShaderNodeOutputWorld"); bg = wn.nodes.new("ShaderNodeBackground")
lp = wn.nodes.new("ShaderNodeLightPath"); mx = wn.nodes.new("ShaderNodeMix"); mx.data_type='RGBA'
tc = wn.nodes.new("ShaderNodeTexCoord"); sp = wn.nodes.new("ShaderNodeSeparateXYZ"); rp = wn.nodes.new("ShaderNodeValToRGB")
wn.links.new(tc.outputs["Generated"], sp.inputs[0]); wn.links.new(sp.outputs[2], rp.inputs[0])
rp.color_ramp.elements[0].position=0.45; rp.color_ramp.elements[0].color=(0.35,0.32,0.28,1)
rp.color_ramp.elements[1].position=0.62; rp.color_ramp.elements[1].color=(1.4,1.45,1.5,1)
mx.inputs[7].default_value=(0.78,0.79,0.80,1); wn.links.new(rp.outputs[0], mx.inputs[6])
wn.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0])
wn.links.new(mx.outputs[2], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 0.75
wn.links.new(bg.outputs[0], wo.inputs[0])
