"""HQ toolkit part 2 (blender-skills-pack: hand-painted-style, stylized-style NPR outline, vfx-fx, lighting).
exec after trn_common.py + trn_hq.py."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, noise

# ---------- NPR inverted-hull outline (Unity-portable; stylized-style/npr-shaders.md) ----------
def outline_mat():
    m = bpy.data.materials.get("MAT_Outline_Ink")
    if m: return m
    m = bpy.data.materials.new("MAT_Outline_Ink"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (0.035,0.028,0.022,1)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); geo = nt.nodes.new("ShaderNodeNewGeometry")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(geo.outputs["Backfacing"], mx.inputs[0]); nt.links.new(em.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    m.use_backface_culling = True
    try: m.surface_render_method = 'DITHERED'
    except Exception: pass
    return m
def hidden_mat():
    m = bpy.data.materials.get("MAT_Outline_HiddenSrc")
    if m: return m
    m = bpy.data.materials.new("MAT_Outline_HiddenSrc"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); tr = nt.nodes.new("ShaderNodeBsdfTransparent"); nt.links.new(tr.outputs[0], out.inputs[0])
    for a,v in (("surface_render_method",'DITHERED'),("use_transparent_shadow",True)):
        try: setattr(m, a, v)
        except Exception: pass
    return m
def add_outline(ob, thickness=0.011, vgroup=None):
    me = ob.data; me.materials.append(outline_mat())
    md = ob.modifiers.new("NPR_Outline", 'SOLIDIFY')
    md.thickness = thickness; md.offset = 1.0; md.use_flip_normals = True; md.use_rim = False
    md.material_offset = 99; md.use_quality_normals = True
    if vgroup: md.vertex_group = vgroup; md.thickness_vertex_group = 0.0
    return md

# ---------- three-light lookdev rig (lighting + lookdev-rig.md) ----------
def light_rig():
    sc = bpy.context.scene
    for nm, rot, e, sh in (("LGT_Fill_Sun",(60,0,70),0.55,False),("LGT_Rim_Sun",(70,0,150),1.1,False)):
        ob = bpy.data.objects.get(nm)
        if ob is None:
            ld = bpy.data.lights.new(nm,'SUN'); ob = bpy.data.objects.new(nm, ld); sc.collection.objects.link(ob)
        ob.data.energy = e; ob.data.use_shadow = sh; ob.data.color = (0.85,0.9,1.0) if "Fill" in nm else (1.0,0.95,0.85)
        ob.rotation_euler = tuple(math.radians(a) for a in rot)
    sc.render.use_freestyle = False   # inverted hull replaces freestyle

# ---------- painterly with mask/top attributes for tiles ----------
def mask_mix(m, mask_cols, attr_name="mask", soft=0.15):
    """blend a second painted palette over an existing painterly material where vertex attr is high"""
    nt = m.node_tree; bs = [n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'][0]
    src = bs.inputs["Base Color"].links[0].from_socket
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n = noise_n(nt, tc.outputs["Object"], 4.0, 6, 0.6)
    r = ramp(nt, mask_cols); nt.links.new(n.outputs["Fac"], r.inputs[0])
    f = maprange(nt, mathop(nt, attr(nt, attr_name), mathop(nt, n.outputs["Fac"], 0.5, 'SUBTRACT'), 'ADD'), 0.5-soft, 0.5+soft)
    nt.links.new(mix(nt, src, r.outputs[0], f), bs.inputs["Base Color"])
    return m

# ---------- water (vfx-fx / materials) ----------
def water_hq(name, shallow, mid, deep, foam=(0.95,0.98,0.98), strokes=0.55, ripple='swirl', depth_range=0.25, algae=None, sky=(0.75,0.88,0.95), shore_foam=1.0):
    m, nt, bs = new_mat(name)
    tc = nt.nodes.new("ShaderNodeTexCoord"); obj = tc.outputs["Object"]
    d = attr(nt, "depth")
    rd = ramp(nt, [shallow, mid, deep], [0.0, 0.45, 1.0]); nt.links.new(maprange(nt, d, 0.0, depth_range), rd.inputs[0])
    col = rd.outputs[0]
    nb = noise_n(nt, obj, 1.2, 3, 0.5); col = mix(nt, col, maprange(nt, nb.outputs["Fac"], 0.3, 0.7, 0.85, 1.15), 1.0, 'MULTIPLY')
    if algae:
        na = noise_n(nt, obj, 2.6, 6, 0.62); ra = ramp(nt, algae); nt.links.new(na.outputs["Fac"], ra.inputs[0])
        col = mix(nt, col, ra.outputs[0], maprange(nt, na.outputs["Fac"], 0.58, 0.62))
    # painted wave strokes
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = 'RINGS' if ripple == 'rings' else 'BANDS'
    wv.inputs["Scale"].default_value = 2.2 if ripple != 'flow' else 3.0
    wv.inputs["Distortion"].default_value = 9.0 if ripple == 'swirl' else 4.0
    wv.inputs["Detail"].default_value = 3.0; wv.inputs["Detail Scale"].default_value = 1.5
    nt.links.new(mathop(nt, time_out(nt), 0.9), wv.inputs["Phase Offset"])
    nt.links.new(mapping(nt, obj, (1,1,1) if ripple != 'flow' else (1,0.35,1)), wv.inputs["Vector"])
    nm = noise_n(nt, obj, 2.0, 2, 0.5)
    lines = mathop(nt, maprange(nt, wv.outputs["Fac"], 0.80, 0.94), maprange(nt, nm.outputs["Fac"], 0.42, 0.6))
    col = mix(nt, col, foam, mathop(nt, lines, strokes))
    # shore foam: thin bands by depth + breakup
    nf = noise_n(nt, obj, 7.0, 3, 0.6)
    band1 = maprange(nt, d, 0.018, 0.0)
    bz = mathop(nt, mathop(nt, d, 22.0), mathop(nt, nf.outputs["Fac"], 0.6), 'ADD')
    band2 = mathop(nt, maprange(nt, mathop(nt, mathop(nt, bz, 1.0, 'FRACT'), 0.5, 'SUBTRACT'), -0.06, 0.0), maprange(nt, d, 0.09, 0.03))
    sf = mathop(nt, mathop(nt, band1, band2, 'MAXIMUM'), maprange(nt, nf.outputs["Fac"], 0.35, 0.55), 'MULTIPLY')
    col = mix(nt, col, foam, mathop(nt, sf, shore_foam))
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
    col = mix(nt, col, sky, mathop(nt, lw.outputs["Facing"], 0.22))
    nt.links.new(col, bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = 0.035; bs.inputs["Specular IOR Level"].default_value = 0.85
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.15; bp.inputs["Distance"].default_value = 0.01
    nt.links.new(wv.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs[0], bs.inputs["Normal"])
    return m

def water_volume_hq(bm, region, H, zw, n=56, wave=0.004, skirt=True):
    dl = bm.verts.layers.float.get("depth") or bm.verts.layers.float.new("depth")
    U = [-1+2*i/n for i in range(n+1)]; vt = {}; fs = []
    def V(i,j):
        if (i,j) not in vt:
            x,y = plan_map(U[i],U[j]); z = zw + wave*noise.noise(Vector((x*5,y*5,0.3)))
            v = bm.verts.new((x,y,z)); v[dl] = max(0.0, zw - H(x,y)); vt[(i,j)] = v
        return vt[(i,j)]
    cen = lambda i,j: ((U[i]+U[i+1])/2,(U[j]+U[j+1])/2)
    inside = lambda i,j: region(*cen(i,j)) and H(*cen(i,j)) < zw
    for i in range(n):
        for j in range(n):
            if inside(i,j): fs.append(bm.faces.new((V(i,j),V(i+1,j),V(i+1,j+1),V(i,j+1))))
    if skirt:
        for i in range(n):
            for (a,b,ok) in (((i,0),(i+1,0),inside(i,0)),((i,n),(i+1,n),inside(i,n-1)),((0,i),(0,i+1),inside(0,i)),((n,i),(n,i+1),inside(n-1,i))):
                if not ok: continue
                va,vb = V(*a),V(*b)
                la = bm.verts.new((va.co.x,va.co.y,min(H(va.co.x,va.co.y),zw))); lb = bm.verts.new((vb.co.x,vb.co.y,min(H(vb.co.x,vb.co.y),zw)))
                la[dl] = 0.3; lb[dl] = 0.3
                fs.append(bm.faces.new((va,vb,lb,la)))
    return fs

def volume_mat(name, color=(0.92,0.95,0.96), density=6.0, noise_scale=3.0):
    m, nt, bs = new_mat(name); out = [n for n in nt.nodes if n.type=='OUTPUT_MATERIAL'][0]; nt.nodes.remove(bs)
    pv = nt.nodes.new("ShaderNodeVolumePrincipled"); pv.inputs["Color"].default_value = (*color,1)
    tc = nt.nodes.new("ShaderNodeTexCoord"); n = noise_n(nt, tc.outputs["Object"], noise_scale, 5, 0.6)
    gr = nt.nodes.new("ShaderNodeTexGradient"); gr.gradient_type = 'SPHERICAL'; nt.links.new(tc.outputs["Generated"], gr.inputs["Vector"]) if False else None
    nt.links.new(mathop(nt, maprange(nt, n.outputs["Fac"], 0.42, 0.7), density), pv.inputs["Density"])
    nt.links.new(pv.outputs[0], out.inputs["Volume"])
    return m
def blob(bm, center, size, subdiv=3):
    res = bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0, matrix=Matrix.Translation(center) @ Matrix.Diagonal((*size,1)))
    return list({f for v in res["verts"] for f in v.link_faces})

# ---------- emission by vertex attribute (lava) ----------
def glow_emission(ramp_cols=((0.55,0.06,0.01),(1.0,0.32,0.03),(1.0,0.78,0.25)), strength=6.0, attr_name="glow", lines=None):
    def fn(nt, bs, obj, cv):
        g = attr(nt, attr_name)
        if lines is not None:
            dn = noise_n(nt, obj, 2.5, 3, 0.5)
            vsc = nt.nodes.new("ShaderNodeVectorMath"); vsc.operation='SCALE'; nt.links.new(dn.outputs["Color"], vsc.inputs[0]); vsc.inputs["Scale"].default_value = 0.25
            va = nt.nodes.new("ShaderNodeVectorMath"); va.operation='ADD'; nt.links.new(obj, va.inputs[0]); nt.links.new(vsc.outputs[0], va.inputs[1])
            vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.feature='DISTANCE_TO_EDGE'; vo.inputs["Scale"].default_value = lines
            nt.links.new(va.outputs[0], vo.inputs["Vector"])
            cm = noise_n(nt, obj, 1.5, 2, 0.5)
            g = mathop(nt, g, mathop(nt, maprange(nt, vo.outputs["Distance"], 0.03, 0.0), maprange(nt, cm.outputs["Fac"], 0.42, 0.55)), 'MAXIMUM')
        r = ramp(nt, list(ramp_cols), [0.0, 0.5, 1.0]); nt.links.new(g, r.inputs[0])
        nt.links.new(r.outputs[0], bs.inputs["Emission Color"])
        nt.links.new(mathop(nt, maprange(nt, g, 0.25, 1.0), strength), bs.inputs["Emission Strength"])
        # charred halo + glow tint into base colour
        src = bs.inputs["Base Color"].links[0].from_socket
        c1 = mix(nt, src, (0.30,0.09,0.02), maprange(nt, g, 0.05, 0.35, 0.0, 0.85))
        c2 = mix(nt, c1, r.outputs[0], maprange(nt, g, 0.45, 0.8))
        nt.links.new(c2, bs.inputs["Base Color"])
    return fn

# ---------- tile finish with curvature + outline group ----------
def finish_hq(name, coll, bm, nblock, mats, pos, src, extra=None, outline=True, sharp=50, outline_th=0.011):
    """Tile/prop object + separate ink-outline child built ONLY from the solid block faces (first nblock faces),
    so thin parts (blades, water sheets, foam, leaves) never get a coincident hull."""
    bake_curvature(bm)
    ob_bm = bm.copy() if outline else None
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    me.shade_smooth()
    try: me.set_sharp_from_angle(angle=math.radians(sharp))
    except Exception: pass
    ob = bpy.data.objects.new(name, me); ob.location = pos; coll.objects.link(ob)
    ob["source_image"] = src; ob["quality"] = "v2_hq"; ob["outline_done"] = True
    for k,v in (extra or {}).items(): ob[k] = v
    if outline:
        faces = list(ob_bm.faces)
        bmesh.ops.delete(ob_bm, geom=faces[nblock:], context='FACES')
        om = bpy.data.meshes.new(name + "_Outline"); ob_bm.to_mesh(om); ob_bm.free()
        om.shade_smooth()
        oo = bpy.data.objects.new(name + "_Outline", om); coll.objects.link(oo); oo.parent = ob
        oo["outline_done"] = True; oo["export"] = "optional (ink outline hull; Unity can use an outline shader instead)"
        add_outline(oo, outline_th)
        # hull only: hide the source surface of the outline object
        om.materials.clear(); om.materials.append(hidden_mat()); om.materials.append(outline_mat())
        md = oo.modifiers["NPR_Outline"]; md.material_offset = 1; md.use_rim = False
        # bake to a static shell-only mesh (drop the source surface) -> clean hull, portable to Unity
        dg = bpy.context.evaluated_depsgraph_get()
        sm = bpy.data.meshes.new_from_object(oo.evaluated_get(dg))
        b2 = bmesh.new(); b2.from_mesh(sm)
        bmesh.ops.delete(b2, geom=[f for f in b2.faces if f.material_index == 0], context='FACES')
        for f in b2.faces: f.material_index = 0
        b2.to_mesh(sm); b2.free()
        oo.modifiers.remove(md); oo.data = sm; bpy.data.meshes.remove(om)
        sm.materials.clear(); sm.materials.append(outline_mat()); sm.name = name + "_Outline"
        oo.visible_shadow = False
    me.calc_loop_triangles(); return len(me.loop_triangles)
def new_bm2():
    bm = bmesh.new()
    for l in ("top","mask","blade_h","depth","glow"): bm.verts.layers.float.new(l)
    return bm, bm.verts.layers.float["top"], bm.verts.layers.float["mask"], bm.verts.layers.float["blade_h"]

def cyl(bm, x,y,z0, r, h, seg=6, tilt=(0,0)):
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r*0.9, depth=h,
        matrix=Matrix.Translation((x,y,z0+h/2)) @ Matrix.Rotation(tilt[0],4,'X') @ Matrix.Rotation(tilt[1],4,'Y'))
    return list({f for v in res["verts"] for f in v.link_faces})


def time_out(nt, mult=1.0):
    """seconds at 24 fps, via a simple-expression driver (no python autorun needed)"""
    v = nt.nodes.new("ShaderNodeValue"); v.label = "Time"
    fc = v.outputs[0].driver_add("default_value"); fc.driver.type = 'SCRIPTED'
    fc.driver.expression = "frame/24.0*%g" % mult
    return v.outputs[0]
