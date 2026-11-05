"""Dino Park Tycoon - shared terrain helpers (materials, noise, blades). exec() this before a TRN builder.
Conventions: tile 2x2 m, ground level z=0 at pivot (centre of top), bottom z=-T, Z up, -Y front."""
import bpy, bmesh, math, random
from mathutils import Matrix, Vector, noise
T = 0.4; R = 0.1; RC = 0.10; LEVEL = 1.0   # thickness, top shoulder radius, plan corner radius, one terrain level
def clamp(v,a=0.0,b=1.0): return max(a,min(b,v))
def sstep(e0,e1,x):
    t = clamp((x-e0)/(e1-e0)); return t*t*(3-2*t)
def nn(x,y,s,seed=0): return noise.noise(Vector((x*s+seed*17.3, y*s+seed*5.1, seed*3.7)))
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
def shoulder(x,y,r=R):
    d = edge_d(x,y)
    if d >= r: return 0.0
    q = r-d; return -(r-math.sqrt(max(0.0,r*r-q*q)))

def get_coll(name):
    c = bpy.data.collections.get(name)
    if c is None: c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    for o in list(c.objects):
        me = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if me and me.users == 0: bpy.data.meshes.remove(me)
    return c

# ---------- materials ----------
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
    nt.links.new(a, m.inputs[0])
    if isinstance(b,(int,float)): m.inputs[1].default_value = float(b)
    else: nt.links.new(b, m.inputs[1])
    return m.outputs[0]
def attr(nt, name):
    a = nt.nodes.new("ShaderNodeAttribute"); a.attribute_type='GEOMETRY'; a.attribute_name = name; return a.outputs["Fac"]

def painted2(name, top, side, mask_cols=None, rough=0.9, streak=0.4, bump=0.18, scale=2.2,
             side_scale=(7,7,1.3), zrange=(-T,-0.08), streak_scale=(1.6,10,1)):
    """Vertex attribute 'top' (1 top, 0 side) picks top vs side paint; attribute 'mask' blends in mask_cols (sand, dirt...)."""
    m, nt, bs = new_mat(name)
    tc = nt.nodes.new("ShaderNodeTexCoord"); obj = tc.outputs["Object"]
    n1 = noise_n(nt, obj, scale, 6, 0.62)
    rt = ramp(nt, top); nt.links.new(n1.outputs["Fac"], rt.inputs[0])
    n2 = noise_n(nt, mapping(nt,obj,streak_scale,0.7), 2.5, 3, 0.5)
    topc = mix(nt, rt.outputs[0], n2.outputs["Fac"], streak, 'SOFT_LIGHT')
    if mask_cols:
        rm = ramp(nt, mask_cols); nt.links.new(n1.outputs["Fac"], rm.inputs[0])
        f = maprange(nt, mathop(nt, attr(nt,"mask"), mathop(nt, n2.outputs["Fac"], 0.5, 'SUBTRACT'), 'ADD'), 0.35, 0.65)
        topc = mix(nt, topc, rm.outputs[0], f)
    n3 = noise_n(nt, mapping(nt,obj,side_scale), 2.0, 5, 0.6)
    rs = ramp(nt, side); nt.links.new(n3.outputs["Fac"], rs.inputs[0])
    col = mix(nt, rs.outputs[0], topc, maprange(nt, attr(nt,"top"), 0.35, 0.75))
    sepo = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(obj, sepo.inputs[0])
    col = mix(nt, col, maprange(nt, sepo.outputs[2], zrange[0], zrange[1], 0.6, 1.0), 1.0, 'MULTIPLY')
    nt.links.new(col, bs.inputs["Base Color"])
    n4 = noise_n(nt, obj, 22, 4, 0.6); bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump; bp.inputs["Distance"].default_value = 0.02
    nt.links.new(n4.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs[0], bs.inputs["Normal"])
    bs.inputs["Roughness"].default_value = rough
    return m
def gravel_mat(name, cols, scale=70):
    m, nt, bs = new_mat(name)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    v = nt.nodes.new("ShaderNodeTexVoronoi"); v.inputs["Scale"].default_value = scale
    nt.links.new(tc.outputs["Object"], v.inputs["Vector"])
    v2 = nt.nodes.new("ShaderNodeTexVoronoi"); v2.feature = 'DISTANCE_TO_EDGE'; v2.inputs["Scale"].default_value = scale
    nt.links.new(tc.outputs["Object"], v2.inputs["Vector"])
    r = ramp(nt, cols); nt.links.new(v.outputs["Color"], r.inputs[0])
    col = mix(nt, r.outputs[0], maprange(nt, v2.outputs["Distance"], 0.0, 0.12, 0.35, 1.0), 1.0, 'MULTIPLY')
    nt.links.new(col, bs.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.8; bp.inputs["Distance"].default_value = 0.01
    nt.links.new(maprange(nt, v2.outputs["Distance"], 0.0, 0.15), bp.inputs["Height"]); nt.links.new(bp.outputs[0], bs.inputs["Normal"])
    bs.inputs["Roughness"].default_value = 0.9
    return m
def blade_mat(name, root, tip, alt, hmax, z0=-0.03):
    m, nt, bs = new_mat(name)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n = noise_n(nt, tc.outputs["Object"], 5, 2, 0.5)
    r = ramp(nt, [root, tip]); nt.links.new(attr(nt,"blade_h"), r.inputs[0])
    col = mix(nt, r.outputs[0], alt, maprange(nt, n.outputs["Fac"], 0.42, 0.62, 0.0, 0.5))
    nt.links.new(col, bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.85
    return m
def flat_mat(name, c, rough=0.85):
    m, nt, bs = new_mat(name); bs.inputs["Base Color"].default_value = (*c,1); bs.inputs["Roughness"].default_value = rough
    return m

# ---------- heightfield block ----------
def axis_coords(n, a=-1.0, b=1.0):
    edge = [0.0,0.012,0.028,0.05,0.075]
    inner = [0.1 + 1.8*i/(n-1) for i in range(n)]
    u = edge + inner + [2.0-v for v in reversed(edge)]
    return [a + (b-a)*v/2.0 for v in u]
def build_hf(bm, H, nx, ny, mask=None, top_layer=None, mask_layer=None, wall_rings=(0.5,)):
    """Top surface z=H(x,y) on a rounded-corner 2x2 m footprint, vertical walls down to -T."""
    U = axis_coords(nx); V = axis_coords(ny); NX,NY = len(U),len(V)
    vg = []
    for x in U:
        col = []
        for y in V:
            px,py = plan_map(x,y); v = bm.verts.new((px,py,H(px,py)))
            v[top_layer] = 1.0; v[mask_layer] = mask(px,py) if mask else 0.0
            col.append(v)
        vg.append(col)
    fs = []
    for i in range(NX-1):
        for j in range(NY-1):
            fs.append(bm.faces.new((vg[i][j],vg[i+1][j],vg[i+1][j+1],vg[i][j+1])))
    per = [vg[i][0] for i in range(NX)] + [vg[NX-1][j] for j in range(1,NY)] + \
          [vg[i][NY-1] for i in range(NX-2,-1,-1)] + [vg[0][j] for j in range(NY-2,0,-1)]
    rings = [per]
    for f in list(wall_rings)+[1.0]:
        ring = []
        for v in per:
            z = v.co.z + (-T - v.co.z)*f
            nv = bm.verts.new((v.co.x, v.co.y, z)); nv[top_layer] = 0.0; nv[mask_layer] = 0.0; ring.append(nv)
        rings.append(ring)
    M = len(per)
    for a,b in zip(rings[:-1], rings[1:]):
        for k in range(M):
            q=(k+1)%M; fs.append(bm.faces.new((a[k],b[k],b[q],a[q])))
    fs.append(bm.faces.new(list(reversed(rings[-1]))))
    return fs
def blade(bm, hl, x,y,z, h, w, ang, lean):
    dx,dy = math.cos(ang), math.sin(ang); px,py = -dy, dx
    vs = [bm.verts.new((x-px*w/2, y-py*w/2, z-0.015)), bm.verts.new((x+px*w/2, y+py*w/2, z-0.015))]
    mo = lean*0.35*h
    vs += [bm.verts.new((x+dx*mo+px*w*0.32, y+dy*mo+py*w*0.32, z+0.55*h)), bm.verts.new((x+dx*mo-px*w*0.32, y+dy*mo-py*w*0.32, z+0.55*h))]
    vs.append(bm.verts.new((x+dx*lean*h, y+dy*lean*h, z+h*(1-0.25*lean))))
    for v,t in zip(vs,(0,0,0.55,0.55,1.0)): v[hl] = t
    return [bm.faces.new((vs[0],vs[1],vs[2],vs[3])), bm.faces.new((vs[3],vs[2],vs[4]))]
def clump(bm, hl, H, x,y, n, hmin,hmax, spread, wid, lean=(0.25,0.75)):
    fs = []
    for _ in range(n):
        a = random.uniform(0,6.283); r = random.uniform(0,spread)
        bx,by = x+math.cos(a)*r, y+math.sin(a)*r
        if max(abs(bx),abs(by)) > 0.97: continue
        fs += blade(bm,hl,bx,by,H(bx,by),random.uniform(hmin,hmax),wid,a+random.uniform(-0.6,0.6),random.uniform(*lean))
    return fs
def box(bm, center, size, rot=Matrix.Identity(4)):
    res = bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(center) @ rot @ Matrix.Diagonal((*size,1)))
    return list({f for v in res["verts"] for f in v.link_faces})

def finish(name, coll, bm, nblock, mats, pos, src, extra=None):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    me.shade_smooth()
    try: me.set_sharp_from_angle(angle=math.radians(50))
    except Exception: pass
    a = me.attributes.get("freestyle_face") or me.attributes.new("freestyle_face",'BOOLEAN','FACE')
    a.data.foreach_set("value", [i < nblock for i in range(len(me.polygons))])
    ob = bpy.data.objects.new(name, me); ob.location = pos; coll.objects.link(ob)
    ob["source_image"] = src; ob["tile_size_m"] = 2.0; ob["thickness_m"] = T
    for k,v in (extra or {}).items(): ob[k] = v
    me.calc_loop_triangles(); return len(me.loop_triangles)
def new_bm():
    bm = bmesh.new()
    return bm, bm.verts.layers.float.new("top"), bm.verts.layers.float.new("mask"), bm.verts.layers.float.new("blade_h")
