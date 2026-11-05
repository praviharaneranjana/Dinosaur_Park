"""Dino Park Tycoon - animated water / foam / mist materials (TRN v03). exec after trn_common, trn_hq, trn_hq2.
All water uses a UV map 'FlowUV' (U across the stream, V along the flow in metres) so Unity can scroll the same UVs."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, noise

def vadd(nt, a, b):
    n = nt.nodes.new("ShaderNodeVectorMath"); n.operation = 'ADD'; nt.links.new(a, n.inputs[0]); nt.links.new(b, n.inputs[1]); return n.outputs[0]
def vmul(nt, a, s):
    n = nt.nodes.new("ShaderNodeVectorMath"); n.operation = 'MULTIPLY'; nt.links.new(a, n.inputs[0]); n.inputs[1].default_value = s; return n.outputs[0]
def vlen(nt, v):
    n = nt.nodes.new("ShaderNodeVectorMath"); n.operation = 'LENGTH'; nt.links.new(v, n.inputs[0]); return n.outputs["Value"]
def comb(nt, x=0.0, y=0.0, z=0.0):
    c = nt.nodes.new("ShaderNodeCombineXYZ")
    for i, val in enumerate((x, y, z)):
        if isinstance(val, (int, float)): c.inputs[i].default_value = val
        else: nt.links.new(val, c.inputs[i])
    return c.outputs[0]
def sep(nt, v):
    s = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(v, s.inputs[0]); return s.outputs
def noise4(nt, vec, w, scale, detail=4, rough=0.55):
    n = nt.nodes.new("ShaderNodeTexNoise"); n.noise_dimensions = '4D'
    n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail; n.inputs["Roughness"].default_value = rough
    nt.links.new(vec, n.inputs["Vector"])
    if isinstance(w, (int, float)): n.inputs["W"].default_value = w
    else: nt.links.new(w, n.inputs["W"])
    return n
def uvmap(nt, name="FlowUV"):
    u = nt.nodes.new("ShaderNodeUVMap"); u.uv_map = name; return u.outputs["UV"]
def objco(nt):
    return nt.nodes.new("ShaderNodeTexCoord").outputs["Object"]
def set_blend(m):
    for a, v in (("surface_render_method", 'BLENDED'), ("use_transparent_shadow", True)):
        try: setattr(m, a, v)
        except Exception: pass

def water_flow_mat(name, shallow, mid, deep, speed=0.45, foam=(0.97,0.99,1.0), strokes=0.8, depth_range=0.22,
                   sky=(0.78,0.92,0.96), edge_foam=0.9, rings=None, ring_speed=0.6):
    """flowing water: depth colour, two layers of white strokes scrolling along FlowUV.v, bank foam, optional impact rings"""
    m, nt, bs = new_mat(name)
    t = time_out(nt); uv = uvmap(nt); obj = objco(nt)
    d = attr(nt, "depth")
    rd = ramp(nt, [shallow, mid, deep], [0.0, 0.45, 1.0]); nt.links.new(maprange(nt, d, 0.0, depth_range), rd.inputs[0])
    col = rd.outputs[0]
    nb = noise4(nt, obj, mathop(nt, t, 0.05), 1.3, 3, 0.5)
    col = mix(nt, col, maprange(nt, nb.outputs["Fac"], 0.3, 0.7, 0.85, 1.15), 1.0, 'MULTIPLY')
    f1 = vadd(nt, uv, comb(nt, 0.0, mathop(nt, t, -speed), 0.0))
    s1 = noise4(nt, vmul(nt, f1, (4.0, 0.8, 1.0)), mathop(nt, t, 0.12), 1.8, 5, 0.6)
    f2 = vadd(nt, uv, comb(nt, 0.0, mathop(nt, t, -speed*1.7), 0.0))
    s2 = noise4(nt, vmul(nt, f2, (8.0, 1.5, 1.0)), mathop(nt, t, 0.2), 1.8, 3, 0.5)
    st = mathop(nt, maprange(nt, s1.outputs["Fac"], 0.60, 0.69), maprange(nt, s2.outputs["Fac"], 0.63, 0.70), 'MAXIMUM')
    col = mix(nt, col, foam, mathop(nt, st, strokes))
    au = mathop(nt, sep(nt, uv)[0], 0.0, 'ABSOLUTE')
    ef = mathop(nt, maprange(nt, au, 0.80, 0.99), maprange(nt, s2.outputs["Fac"], 0.42, 0.58))
    sf = mathop(nt, maprange(nt, d, 0.025, 0.0), maprange(nt, s1.outputs["Fac"], 0.4, 0.55))
    col = mix(nt, col, foam, mathop(nt, mathop(nt, ef, sf, 'MAXIMUM'), edge_foam))
    hgt = st
    if rings:
        cx, cy, rs = rings
        loc = vmul(nt, vadd(nt, obj, comb(nt, -cx, -cy, 0.0)), (1.0, 1.0, 0.0))
        wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = 'RINGS'; wv.rings_direction = 'SPHERICAL'
        wv.inputs["Scale"].default_value = rs; wv.inputs["Distortion"].default_value = 2.0; wv.inputs["Detail"].default_value = 2.0
        nt.links.new(loc, wv.inputs["Vector"]); nt.links.new(mathop(nt, t, -ring_speed*6.0), wv.inputs["Phase Offset"])
        lv = vlen(nt, loc)
        rl = mathop(nt, maprange(nt, wv.outputs["Fac"], 0.86, 0.96), maprange(nt, lv, 1.3, 0.12))
        col = mix(nt, col, foam, mathop(nt, rl, 0.85))
        ch = noise4(nt, obj, mathop(nt, t, 0.8), 7.0, 4, 0.6)
        col = mix(nt, col, foam, mathop(nt, maprange(nt, lv, 0.4, 0.05), maprange(nt, ch.outputs["Fac"], 0.35, 0.55)))
        hgt = mathop(nt, hgt, rl, 'MAXIMUM')
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
    col = mix(nt, col, sky, mathop(nt, lw.outputs["Facing"], 0.2))
    nt.links.new(col, bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = 0.03; bs.inputs["Specular IOR Level"].default_value = 0.85
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.2; bp.inputs["Distance"].default_value = 0.01
    nt.links.new(hgt, bp.inputs["Height"]); nt.links.new(bp.outputs[0], bs.inputs["Normal"])
    return m

def falls_sheet_mat(name, speed=2.2):
    m, nt, bs = new_mat(name); t = time_out(nt); uv = uvmap(nt)
    f1 = vadd(nt, uv, comb(nt, 0.0, mathop(nt, t, -speed), 0.0))
    n1 = noise4(nt, vmul(nt, f1, (10.0, 0.55, 1.0)), mathop(nt, t, 0.3), 1.4, 6, 0.6)
    f2 = vadd(nt, uv, comb(nt, 0.0, mathop(nt, t, -speed*1.35), 0.0))
    n2 = noise4(nt, vmul(nt, f2, (22.0, 1.0, 1.0)), mathop(nt, t, 0.5), 1.4, 3, 0.5)
    fv = attr(nt, "fallv")
    base = ramp(nt, [(0.10,0.50,0.56),(0.35,0.72,0.76),(0.80,0.94,0.95),(1,1,1)], [0.25,0.5,0.68,0.82]); nt.links.new(n1.outputs["Fac"], base.inputs[0])
    col = mix(nt, base.outputs[0], (1,1,1), maprange(nt, n2.outputs["Fac"], 0.6, 0.7))
    col = mix(nt, col, (1,1,1), maprange(nt, fv, 0.72, 1.0, 0.0, 0.85))
    col = mix(nt, col, (0.9,0.98,1.0), maprange(nt, fv, 0.0, 0.08, 0.5, 0.0))
    nt.links.new(col, bs.inputs["Base Color"])
    nt.links.new(mathop(nt, maprange(nt, n1.outputs["Fac"], 0.28, 0.5, 0.45, 1.0), maprange(nt, fv, 0.85, 1.0, 1.0, 0.65)), bs.inputs["Alpha"])
    bs.inputs["Roughness"].default_value = 0.05
    bs.inputs["Emission Color"].default_value = (0.75,0.9,0.92,1); bs.inputs["Emission Strength"].default_value = 0.2
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.3; bp.inputs["Distance"].default_value = 0.01
    nt.links.new(n2.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs[0], bs.inputs["Normal"])
    set_blend(m); return m

def foam_mat(name):
    m, nt, bs = new_mat(name); t = time_out(nt); obj = objco(nt)
    n = noise4(nt, vadd(nt, obj, comb(nt, 0.0, 0.0, mathop(nt, t, -0.15))), mathop(nt, t, 0.7), 7.0, 5, 0.62)
    r = ramp(nt, [(0.60,0.76,0.80),(0.86,0.94,0.96),(1.0,1.0,1.0)], [0.3,0.5,0.7]); nt.links.new(n.outputs["Fac"], r.inputs[0])
    nt.links.new(r.outputs[0], bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = 0.45
    bs.inputs["Emission Color"].default_value = (0.85,0.93,0.95,1); bs.inputs["Emission Strength"].default_value = 0.15
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.7; bp.inputs["Distance"].default_value = 0.02
    nt.links.new(n.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs[0], bs.inputs["Normal"])
    return m

def mist_mat(name, density=6.0):
    m, nt, bs = new_mat(name); out = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]; nt.nodes.remove(bs)
    pv = nt.nodes.new("ShaderNodeVolumePrincipled"); pv.inputs["Color"].default_value = (0.96,0.98,0.99,1)
    t = time_out(nt); tc = nt.nodes.new("ShaderNodeTexCoord")
    n = noise4(nt, vadd(nt, tc.outputs["Object"], comb(nt, 0.0, 0.0, mathop(nt, t, -0.3))), mathop(nt, t, 0.35), 3.2, 5, 0.6)
    g = vlen(nt, vadd(nt, tc.outputs["Generated"], comb(nt, -0.5, -0.5, -0.5)))
    dens = mathop(nt, mathop(nt, maprange(nt, n.outputs["Fac"], 0.42, 0.68), maprange(nt, g, 0.5, 0.12)), density)
    nt.links.new(dens, pv.inputs["Density"]); nt.links.new(pv.outputs[0], out.inputs["Volume"])
    return m

def sea_mat(name, shallow, mid, deep, depth_range=0.24, foam=(0.97,0.99,1.0)):
    """sea: depth colour, drifting swirl strokes, wave crests that travel toward the shore (vary along the beach and over time)"""
    m, nt, bs = new_mat(name); t = time_out(nt); obj = objco(nt)
    d = attr(nt, "depth")
    rd = ramp(nt, [shallow, mid, deep], [0.0, 0.45, 1.0]); nt.links.new(maprange(nt, d, 0.0, depth_range), rd.inputs[0])
    col = rd.outputs[0]
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = 'BANDS'
    wv.inputs["Scale"].default_value = 2.2; wv.inputs["Distortion"].default_value = 7.0; wv.inputs["Detail"].default_value = 3.0
    nt.links.new(obj, wv.inputs["Vector"]); nt.links.new(mathop(nt, t, 0.7), wv.inputs["Phase Offset"])
    nm = noise4(nt, obj, mathop(nt, t, 0.1), 2.0, 2, 0.5)
    col = mix(nt, col, foam, mathop(nt, mathop(nt, maprange(nt, wv.outputs["Fac"], 0.80, 0.93), maprange(nt, nm.outputs["Fac"], 0.42, 0.6)), 0.4))
    nw = noise4(nt, vmul(nt, obj, (0.6, 1.4, 0.0)), mathop(nt, t, 0.1), 1.0, 2, 0.5)
    ph = mathop(nt, mathop(nt, mathop(nt, d, 24.0), mathop(nt, t, 0.5), 'ADD'), mathop(nt, nw.outputs["Fac"], 1.2), 'ADD')
    f = mathop(nt, ph, 1.0, 'FRACT')
    gate = maprange(nt, noise4(nt, vmul(nt, obj, (2.0, 2.0, 0.0)), mathop(nt, t, 0.25), 1.5, 3, 0.5).outputs["Fac"], 0.42, 0.58)
    crest = mathop(nt, mathop(nt, mathop(nt, maprange(nt, f, 0.0, 0.05), maprange(nt, f, 0.16, 0.05)), gate), maprange(nt, d, 0.22, 0.05))
    col = mix(nt, col, foam, crest)
    col = mix(nt, col, foam, mathop(nt, maprange(nt, d, 0.02, 0.0), maprange(nt, nm.outputs["Fac"], 0.35, 0.55)))
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
    col = mix(nt, col, (0.78,0.92,0.96), mathop(nt, lw.outputs["Facing"], 0.2))
    nt.links.new(col, bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = 0.03; bs.inputs["Specular IOR Level"].default_value = 0.85
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.2; bp.inputs["Distance"].default_value = 0.01
    nt.links.new(mathop(nt, wv.outputs["Fac"], crest, 'ADD'), bp.inputs["Height"]); nt.links.new(bp.outputs[0], bs.inputs["Normal"])
    return m

def swash_mat(name, reach0=0.06, amp=0.46):
    """thin wave film on the sand: runs up and back (sine + noise, different along the shore every time), white foam front + bubbly lace"""
    m, nt, bs = new_mat(name); t = time_out(nt); obj = objco(nt)
    sd = attr(nt, "sd"); sy = sep(nt, obj)[1]
    nzs = noise4(nt, comb(nt, 0.0, mathop(nt, sy, 1.3), 0.0), mathop(nt, t, 0.07), 1.0, 2, 0.5)
    ph = mathop(nt, mathop(nt, t, 1.05), mathop(nt, nzs.outputs["Fac"], 6.0), 'ADD')
    s01 = mathop(nt, maprange(nt, mathop(nt, ph, 0.0, 'SINE'), -1.0, 1.0), 1.7, 'POWER')
    n2 = noise4(nt, comb(nt, 0.0, mathop(nt, sy, 2.6), 0.0), mathop(nt, t, 0.15), 1.0, 2, 0.5)
    reach = mathop(nt, mathop(nt, s01, mathop(nt, maprange(nt, n2.outputs["Fac"], 0.3, 0.7, 0.55, 1.15), amp)), reach0, 'ADD')
    diff = mathop(nt, reach, sd, 'SUBTRACT')
    cov = maprange(nt, diff, 0.0, 0.015)
    vb = nt.nodes.new("ShaderNodeTexVoronoi"); vb.voronoi_dimensions = '4D'; vb.feature = 'DISTANCE_TO_EDGE'
    vb.inputs["Scale"].default_value = 18.0; nt.links.new(obj, vb.inputs["Vector"]); nt.links.new(mathop(nt, t, 0.6), vb.inputs["W"])
    lace = maprange(nt, vb.outputs["Distance"], 0.08, 0.0)
    front = mathop(nt, maprange(nt, diff, 0.0, 0.03), maprange(nt, diff, 0.13, 0.05))
    nf = noise4(nt, vmul(nt, obj, (3.0, 3.0, 0.0)), mathop(nt, t, 0.5), 2.0, 3, 0.5)
    foamf = mathop(nt, mathop(nt, front, maprange(nt, nf.outputs["Fac"], 0.28, 0.45)), mathop(nt, mathop(nt, cov, lace), 0.9), 'MAXIMUM')
    nt.links.new(mix(nt, (0.32,0.78,0.78), (1,1,1), foamf), bs.inputs["Base Color"])
    nt.links.new(mathop(nt, mathop(nt, cov, 0.7), foamf, 'MAXIMUM'), bs.inputs["Alpha"])
    bs.inputs["Roughness"].default_value = 0.05
    set_blend(m); return m

def moss_shell(bm, faces, seed, thick=0.022, nz_min=0.45, thr=-0.1, drape=0.035):
    """raised 3D moss cap on the upward faces of a rock, with a hanging lip"""
    bm.normal_update()
    sel = []
    for f in faces:
        if not f.is_valid or f.normal.z < nz_min: continue
        c = f.calc_center_median()
        if noise.noise(c*3.0 + Vector((seed*0.37, 0, 0))) + (f.normal.z - 0.75)*0.8 < thr: continue
        sel.append(f)
    if not sel: return []
    res = bmesh.ops.duplicate(bm, geom=sel)
    nf = [g for g in res["geom"] if isinstance(g, bmesh.types.BMFace)]
    nv = [g for g in res["geom"] if isinstance(g, bmesh.types.BMVert)]
    bm.normal_update()
    for v in nv:
        v.co += v.normal*thick*(0.7+0.6*abs(noise.noise(v.co*11))) + Vector((0, 0, thick*0.3))
    be = [e for e in {e for f in nf for e in f.edges} if e.is_boundary]
    ext = bmesh.ops.extrude_edge_only(bm, edges=be)
    for g in ext["geom"]:
        if isinstance(g, bmesh.types.BMVert): g.co.z -= drape*(0.6 + 0.8*abs(noise.noise(g.co*9)))
    return nf + [g for g in ext["geom"] if isinstance(g, bmesh.types.BMFace)]

def soil_side(name, top_z, wet=True):
    """soil wall: strata bands, cracks, grass drips hanging from top_z, optional wet streak (vertex attr 'mask')"""
    m = painterly(name, [(0.24,0.14,0.07),(0.31,0.19,0.10),(0.38,0.25,0.14)], edge=(0.62,0.46,0.3), cavity=(0.04,0.025,0.012),
                  dirt=(0.10,0.06,0.03), dirt_h=-0.15, strokes=0.6, crack_lines=0.35, crack_scale=1.4, toplight=0.2, bands=SOIL_B, band_scale=2.2)
    nt = m.node_tree; bs = [n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'][0]
    src = bs.inputs["Base Color"].links[0].from_socket
    obj = objco(nt); s = sep(nt, obj)
    dn = noise_n(nt, obj, 3.5, 3, 0.55)
    lim = mathop(nt, mathop(nt, maprange(nt, dn.outputs["Fac"], 0.5, 0.75, 0.0, 0.18), -1.0), top_z - 0.03, 'ADD')
    band = maprange(nt, mathop(nt, s[2], lim, 'SUBTRACT'), -0.005, 0.005)
    gr = ramp(nt, [(0.08,0.18,0.02),(0.14,0.28,0.04)]); nt.links.new(dn.outputs["Fac"], gr.inputs[0])
    col = mix(nt, src, gr.outputs[0], band)
    if wet:
        w = attr(nt, "mask")
        col = mix(nt, col, (0.30,0.26,0.24), mathop(nt, w, 0.85), 'MULTIPLY')
        nt.links.new(maprange(nt, w, 0.0, 1.0, 0.85, 0.12), bs.inputs["Roughness"])
    nt.links.new(col, bs.inputs["Base Color"])
    return m

def tuft(bm, hl, H, x, y, n=4, hmin=0.04, hmax=0.09):
    fs = []
    for _ in range(n):
        a = random.uniform(0, 6.28); r = random.uniform(0, 0.03); bx, by = x+math.cos(a)*r, y+math.sin(a)*r
        fs += blade(bm, hl, bx, by, H(bx, by), random.uniform(hmin, hmax), 0.015, a+random.uniform(-0.6, 0.6), random.uniform(0.25, 0.75))
    return fs
def parent_to(child_name, parent_ob):
    c = bpy.data.objects[child_name]; c.parent = parent_ob; c.location = (0, 0, 0); return c
