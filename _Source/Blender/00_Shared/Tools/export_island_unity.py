"""Export the island (ISL_Main_v05) to Unity.

    blender -b ISL_Main_v05.blend --python export_island_unity.py -- <UnityProject>/Assets/Models/Environment/Island [groundTexSize]

Never saves the .blend. What it writes into the output folder:
  Meshes/<key>.fbx   one FBX per UNIQUE mesh (props and plants are linked duplicates, so ~57 kit
                     meshes + ground, cliffs, water and ocean), at identity transform.
  Textures/*.png     ISL_Ground_Albedo (top-down bake of the procedural ground) + leaf atlases.
  _Probe/*.fbx       three axis probes; the Unity importer reads them to learn the axis/scale
                     conversion, so placements never depend on guessing FBX axis rules.
  island_layout.json meshes, materials and one placement (Blender world matrix) per object.

Procedural Blender shaders do not exist in Unity, so every material is baked (Cycles, diffuse
COLOR pass) into a vertex colour attribute "BakeCol" (sRGB in the FBX). The ground gets a texture
instead because its splat detail is finer than its vertices. Unity side:
Assets/Shaders/Environment/DinoPark_VertexColorLit.shader + Assets/Editor/IslandImporter.cs.
"""
import bpy, bmesh, json, os, re, sys, time
import numpy as np
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = os.path.abspath(argv[0]) if argv else os.path.abspath("IslandExport")
GROUND_TEX = int(argv[1]) if len(argv) > 1 else 4096
for sub in ("Meshes", "Textures", "_Probe"):
    os.makedirs(os.path.join(OUT, sub), exist_ok=True)

T0 = time.time()
def log(*a):
    print(f"[ISL_EXPORT {time.time()-T0:6.1f}s]", *a, flush=True)

sc = bpy.context.scene
vl = bpy.context.view_layer
GROUPS = {"ISL2_Ground": "Ground", "ISL2_Cliffs": "Cliffs", "ISL2_Ocean": "Ocean",
          "ISL2_Water": "Water", "ISL2_Props": "Props", "ISL2_Plants": "Plants"}
SHARED = {"Props", "Plants"}          # linked duplicates -> one FBX per mesh datablock
DOUBLE_SIDED = re.compile(r"Leaf|Frond|Grass|Fern|Reed|Blade|Petal|LilyPad|Lotus|Whorl|Clover|Seaweed|Kelp", re.I)

def key_of(s):
    return re.sub(r"[^A-Za-z0-9_]+", "_", s).strip("_")

# ---------------------------------------------------------------- 1. collect placements
objects, meshes = [], {}
for cname, group in GROUPS.items():
    col = bpy.data.collections.get(cname)
    if not col:
        log("missing collection", cname); continue
    for o in col.all_objects:
        if o.type != 'MESH' or o.hide_render:
            continue
        key = key_of(o.data.name if group in SHARED else o.name)
        if key not in meshes:
            meshes[key] = {"key": key, "group": group, "rep": o.name,
                           "materials": [s.material.name if s.material else "" for s in o.material_slots]}
        objects.append({"n": o.name, "k": key, "g": group,
                        "m": [o.matrix_world[r][c] for r in range(4) for c in range(4)]})
log(f"{len(objects)} objects, {len(meshes)} unique meshes")

sun = next((o for o in sc.objects if o.type == 'LIGHT' and o.data.type == 'SUN'), None)
sun_info = None
if sun:
    d = sun.matrix_world.to_3x3() @ Vector((0, 0, -1))   # direction the light travels
    sun_info = {"dir": list(d.normalized()), "color": list(sun.data.color), "strength": sun.data.energy}

# ---------------------------------------------------------------- 2. material table + bake prep
def out_node(mt):
    return next((n for n in mt.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output),
                next((n for n in mt.nodes if n.type == 'OUTPUT_MATERIAL'), None))

def srgb_to_lin(c):
    c = np.asarray(c)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

used = {m for info in meshes.values() for m in info["materials"] if m}
group_of_mat = {}
for info in meshes.values():
    for m in info["materials"]:
        group_of_mat.setdefault(m, info["group"])

mat_table = {}
for name in sorted(used):
    m = bpy.data.materials[name]
    entry = {"name": name, "kind": "opaque", "alpha": 1.0, "texture": "",
             "doubleSided": bool(DOUBLE_SIDED.search(name)), "smoothness": 0.1}
    mt = m.node_tree
    if mt is None:
        mat_table[name] = entry; continue
    on = out_node(mt)
    surf_linked = on is not None and on.inputs['Surface'].is_linked
    vol_linked = on is not None and on.inputs['Volume'].is_linked
    bsdf = next((n for n in mt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    g = group_of_mat.get(name)
    if vol_linked and not surf_linked:
        entry.update(kind="mist", alpha=0.18, smoothness=0.0)
    elif g in ("Water", "Ocean") and "Seabed" not in name and "Horizon" not in name:
        a = 0.8
        if "Foam" in name: a = 0.75
        if "Fall" in name: a = 0.85
        if "Mud" in name or "Algae" in name: a = 0.95
        if "Ocean_Water" in name: a = 0.85
        entry.update(kind="water", alpha=a, smoothness=0.85)
    # alpha-card textures (leaf atlases)
    for img_node in [n for n in mt.nodes if n.type == 'TEX_IMAGE' and n.image and n.image.size[0] > 0]:
        alpha_used = any(l.from_socket.name == 'Alpha' for l in mt.links if l.from_node == img_node)
        img = img_node.image
        tex_name = key_of(os.path.splitext(img.name)[0]) + ".png"
        tex_path = os.path.join(OUT, "Textures", tex_name)
        if not os.path.exists(tex_path):
            try:
                img.save(filepath=tex_path)
            except Exception as e:
                log("image save failed", img.name, e)
        if alpha_used:
            entry.update(kind="cutout", texture="Textures/" + tex_name, doubleSided=True)
        # bake prep: replace the image colour with its mean opaque colour (card corners sit on
        # transparent texels, so a raw vertex bake would come out dark)
        px = np.array(img.pixels[:], dtype=np.float32).reshape(-1, 4)
        sel = px[px[:, 3] > 0.5] if (px[:, 3] > 0.5).any() else px
        lin = srgb_to_lin(sel[:, :3]) if img.colorspace_settings.name.lower().startswith("srgb") else sel[:, :3]
        avg = lin.mean(axis=0)
        rgb = mt.nodes.new('ShaderNodeRGB'); rgb.outputs[0].default_value = (*avg, 1.0)
        for l in [l for l in mt.links if l.from_node == img_node and l.from_socket.name == 'Color']:
            to = l.to_socket; mt.links.remove(l); mt.links.new(rgb.outputs[0], to)
    # bake prep: opaque, so transparency does not darken the baked colour.
    # Leaf cards mix to a Transparent BSDF by texture alpha: bypass that mix.
    for mix in [n for n in mt.nodes if n.type == 'MIX_SHADER']:
        ins = [mix.inputs[1], mix.inputs[2]]
        src = [s.links[0].from_socket if s.is_linked else None for s in ins]
        kinds = [s.node.type if s else None for s in src]
        if 'BSDF_TRANSPARENT' in kinds:
            keep = src[1] if kinds[0] == 'BSDF_TRANSPARENT' else src[0]
            if keep is None:
                continue
            for l in list(mix.outputs[0].links):
                to = l.to_socket; mt.links.remove(l); mt.links.new(keep, to)
    if bsdf is not None:
        for l in list(bsdf.inputs['Alpha'].links):
            mt.links.remove(l)
        bsdf.inputs['Alpha'].default_value = 1.0
    mat_table[name] = entry

# ---------------------------------------------------------------- 3. isolate export copies
for cname in GROUPS:
    col = bpy.data.collections.get(cname)
    if col and col.name in sc.collection.children:
        sc.collection.children.unlink(col)
exp = bpy.data.collections.new("UNITY_EXPORT"); sc.collection.children.link(exp)

sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = 2
sc.render.bake.use_selected_to_active = False
sc.render.bake.margin = 4

def make_copy(info):
    src = bpy.data.objects[info["rep"]]
    me = src.data.copy(); me.name = info["key"]
    for i, s in enumerate(src.material_slots):        # object-linked slots -> data slots
        if i < len(me.materials): me.materials[i] = s.material
        else: me.materials.append(s.material)
    ob = bpy.data.objects.new(info["key"], me)
    exp.objects.link(ob)
    ob.matrix_world = src.matrix_world               # bake in place (world-space noise lines up)
    return ob

def select_only(ob):
    vl.update()
    for o in list(bpy.context.selected_objects):
        if o is not None: o.select_set(False)
    ob.select_set(True); vl.objects.active = ob

def strip_colors(me):
    for a in list(me.color_attributes):
        me.color_attributes.remove(a)

def new_bakecol(me, fill_white=False):
    strip_colors(me)
    ca = me.color_attributes.new("BakeCol", 'BYTE_COLOR', 'CORNER')
    me.color_attributes.active_color = ca
    try:
        me.color_attributes.render_color_index = me.color_attributes.active_color_index
    except Exception:
        pass
    if fill_white:
        ca.data.foreach_set("color", [1.0] * (len(ca.data) * 4))
    return ca

def bake_vertex(ob):
    me = ob.data
    mats = [m for m in me.materials if m]
    if mats and all(mat_table.get(m.name, {}).get("kind") == "mist" for m in mats):
        new_bakecol(me, fill_white=True); return
    new_bakecol(me)
    select_only(ob)
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, target='VERTEX_COLORS', use_clear=True)

def bake_ground(ob):
    me = ob.data
    co = np.empty(len(me.vertices) * 3, dtype=np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    x0, x1, y0, y1 = float(co[:, 0].min()), float(co[:, 0].max()), float(co[:, 1].min()), float(co[:, 1].max())
    uv = me.uv_layers.new(name="UVMap")
    vi = np.empty(len(me.loops), dtype=np.int32); me.loops.foreach_get("vertex_index", vi)
    u = (co[vi, 0] - x0) / (x1 - x0); v = (co[vi, 1] - y0) / (y1 - y0)
    uv.data.foreach_set("uv", np.stack([u, v], 1).ravel())
    me.uv_layers.active = uv
    img = bpy.data.images.new("ISL_Ground_Albedo", GROUND_TEX, GROUND_TEX, alpha=False)
    mt = me.materials[0].node_tree
    node = mt.nodes.new('ShaderNodeTexImage'); node.image = img
    for n in mt.nodes: n.select = False
    node.select = True; mt.nodes.active = node
    select_only(ob)
    sc.cycles.samples = 4
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, target='IMAGE_TEXTURES', use_clear=True, margin=8)
    sc.cycles.samples = 2
    img.filepath_raw = os.path.join(OUT, "Textures", "ISL_Ground_Albedo.png"); img.file_format = 'PNG'
    img.save()
    mat_table[me.materials[0].name].update(texture="Textures/ISL_Ground_Albedo.png", kind="ground")
    new_bakecol(me, fill_white=True)                 # shader multiplies by vertex colour
    return [x0, x1, y0, y1]

def export_fbx(ob, path):
    select_only(ob)
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'MESH'},
        apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL', axis_forward='-Z', axis_up='Y',
        bake_space_transform=True, use_mesh_modifiers=False, mesh_smooth_type='FACE',
        colors_type='SRGB', prioritize_active_color=True, use_tspace=False, add_leaf_bones=False,
        bake_anim=False, path_mode='STRIP', embed_textures=False, use_custom_props=False)

ONLY = set(os.environ.get("ISL_ONLY", "").split(",")) - {""}
ground_rect = None
order = sorted(meshes.items(), key=lambda kv: kv[1]["group"])
for i, (key, info) in enumerate(order):
    if ONLY and info["group"] not in ONLY and key not in ONLY:
        continue
    ob = make_copy(info)
    me = ob.data
    info["tris"] = sum(len(p.vertices) - 2 for p in me.polygons)
    try:
        if info["group"] == "Ground":
            ground_rect = bake_ground(ob)
        else:
            bake_vertex(ob)
    except Exception as e:
        log("BAKE FAILED", key, repr(e))
    ob.matrix_world = Matrix.Identity(4)
    export_fbx(ob, os.path.join(OUT, "Meshes", key + ".fbx"))
    info["file"] = "Meshes/" + key + ".fbx"
    log(f"{i+1}/{len(meshes)} {info['group']:7s} {key} tris={info['tris']}")
    bpy.data.objects.remove(ob); bpy.data.meshes.remove(me)

# ---------------------------------------------------------------- 4. axis probes
for axis, p in (("X", (10, 0, 0)), ("Y", (0, 20, 0)), ("Z", (0, 0, 30))):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.25)
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(p))
    me = bpy.data.meshes.new("AxisProbe_" + axis); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("AxisProbe_" + axis, me); exp.objects.link(ob)
    export_fbx(ob, os.path.join(OUT, "_Probe", "AxisProbe_" + axis + ".fbx"))

# ---------------------------------------------------------------- 5. layout json
for info in meshes.values():
    info.pop("rep", None)
layout = {"source": bpy.data.filepath, "exported": time.strftime("%Y-%m-%d %H:%M"),
          "probe": {"X": [10, 0, 0], "Y": [0, 20, 0], "Z": [0, 0, 30]},
          "groundRect": ground_rect, "sun": sun_info,
          "meshes": list(meshes.values()), "materials": list(mat_table.values()), "objects": objects}
if not ONLY:
    with open(os.path.join(OUT, "island_layout.json"), "w") as f:
        json.dump(layout, f, indent=0)
log("DONE", OUT)
print("ISL_EXPORT_RESULT " + json.dumps({"meshes": len(meshes), "objects": len(objects), "out": OUT}))
