"""Build the mobile rock kit from the sculpted stones.blend (Downloads/cliff).

Run headless:
  blender -b <stones.blend> --factory-startup --python build_stones_kit.py -- <project root> <riverbed diff jpg>

For each of the 4 sculpted rocks (74k-279k tris): decimate a copy to ~3k tris, unwrap all lows into
one shared UV space, bake albedo (from the riverbed rock texture) and tangent normals (sculpt detail)
from the high meshes into one 2048 atlas, put the pivot at the base centre, export one FBX per rock.
Also writes a grey, mean-0.5 tileable rock detail map from the riverbed photo for cliff faces.
Outputs:
  Assets/Models/Environment/Rocks/ENV_Stone_0N.fbx
  Assets/Textures/Environment/Rocks/T_Stones_Albedo.png, T_Stones_Normal.png
  Assets/Textures/Environment/Island/T_RiverbedRock_Detail.png
  _Source/Blender/02_Environment/ENV_Stones_v01.blend (lows only)
"""
import os
import sys

import bpy
import bmesh
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
ROOT, DIFF = argv[0], argv[1]
MODELS = os.path.join(ROOT, "Assets", "Models", "Environment", "Rocks")
TEX = os.path.join(ROOT, "Assets", "Textures", "Environment", "Rocks")
ISL_TEX = os.path.join(ROOT, "Assets", "Textures", "Environment", "Island")
SRC = os.path.join(ROOT, "_Source", "Blender", "02_Environment")
for d in (MODELS, TEX, ISL_TEX, SRC):
    os.makedirs(d, exist_ok=True)

TARGET_TRIS = 3000
ATLAS = 2048

scene = bpy.context.scene

# The blend points at a "New folder/stone/textures" that does not ship with it: relink to the
# folder the diffuse map came from, and drop the displacement (its map is missing).
tex_dir = os.path.dirname(DIFF)
for img in bpy.data.images:
    name = os.path.basename(bpy.path.abspath(img.filepath))
    if name and os.path.exists(os.path.join(tex_dir, name)):
        img.filepath = os.path.join(tex_dir, name)
        img.reload()
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    out = next((n for n in mat.node_tree.nodes if n.type == 'OUTPUT_MATERIAL'), None)
    if out is not None:
        for link in list(out.inputs['Displacement'].links):
            mat.node_tree.links.remove(link)
print("KIT images", [(i.name, i.has_data or os.path.exists(bpy.path.abspath(i.filepath))) for i in bpy.data.images])

highs =sorted([o for o in scene.objects if o.type == 'MESH' and o.name.startswith("Cube")], key=lambda o: o.name)
print("KIT highs", [(o.name, len(o.data.polygons)) for o in highs])


def select_only(objs, active=None):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = active or objs[0]


# ---- apply transforms on the highs so lows and highs share space
select_only(highs)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# ---- lows
lows = []
for i, h in enumerate(highs):
    low = h.copy()
    low.data = h.data.copy()
    low.name = f"ENV_Stone_{i + 1:02d}"
    low.data.name = low.name
    scene.collection.objects.link(low)
    tris = sum(len(p.vertices) - 2 for p in low.data.polygons)
    mod = low.modifiers.new("Decimate", 'DECIMATE')
    mod.ratio = min(1.0, TARGET_TRIS / max(tris, 1))
    select_only([low])
    bpy.ops.object.modifier_apply(modifier=mod.name)
    mod = low.modifiers.new("Tri", 'TRIANGULATE')
    bpy.ops.object.modifier_apply(modifier=mod.name)
    for p in low.data.polygons:
        p.use_smooth = True
    low.data.materials.clear()
    lows.append(low)
    print("KIT low", low.name, len(low.data.polygons))

# ---- shared UV atlas
for low in lows:
    while low.data.uv_layers:
        low.data.uv_layers.remove(low.data.uv_layers[0])
    low.data.uv_layers.new(name="UVMap")
select_only(lows)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.004, scale_to_bounds=False)
bpy.ops.uv.pack_islands(margin=0.004)
bpy.ops.object.mode_set(mode='OBJECT')

# ---- bake targets
albedo = bpy.data.images.new("T_Stones_Albedo", ATLAS, ATLAS, alpha=False)
normal = bpy.data.images.new("T_Stones_Normal", ATLAS, ATLAS, alpha=False)
normal.colorspace_settings.name = 'Non-Color'
bake_mat = bpy.data.materials.new("M_Stones_Bake")
bake_mat.use_nodes = True
tex_node = bake_mat.node_tree.nodes.new('ShaderNodeTexImage')
bake_mat.node_tree.nodes.active = tex_node
for low in lows:
    low.data.materials.append(bake_mat)

scene.render.engine = 'CYCLES'
scene.cycles.samples = 4
scene.cycles.device = 'CPU'
scene.render.bake.use_selected_to_active = True
scene.render.bake.cage_extrusion = 0.08
scene.render.bake.max_ray_distance = 0.4
scene.render.bake.margin = 8
scene.render.bake.use_clear = False


def bake(kind, image):
    tex_node.image = image
    for h, low in zip(highs, lows):
        select_only([h, low], active=low)
        if kind == 'DIFFUSE':
            scene.render.bake.use_pass_direct = False
            scene.render.bake.use_pass_indirect = False
            scene.render.bake.use_pass_color = True
            bpy.ops.object.bake(type='DIFFUSE')
        else:
            scene.render.bake.normal_space = 'TANGENT'
            bpy.ops.object.bake(type='NORMAL')
        print("KIT baked", kind, low.name)


# fill backgrounds so untouched texels are neutral
albedo.pixels.foreach_set(np.tile(np.array([0.45, 0.42, 0.38, 1.0], dtype=np.float32), ATLAS * ATLAS))
normal.pixels.foreach_set(np.tile(np.array([0.5, 0.5, 1.0, 1.0], dtype=np.float32), ATLAS * ATLAS))
bake('DIFFUSE', albedo)
bake('NORMAL', normal)
for img in (albedo, normal):
    img.filepath_raw = os.path.join(TEX, img.name + ".png")
    img.file_format = 'PNG'
    img.save()

# ---- pivots at base centre, then export
for low in lows:
    me = low.data
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    base = ((min(xs) + max(xs)) * 0.5, (min(ys) + max(ys)) * 0.5, min(zs))
    for v in me.vertices:
        v.co.x -= base[0]
        v.co.y -= base[1]
        v.co.z -= base[2]
    low.location = (0.0, 0.0, 0.0)
    low.data.materials.clear()
    m = bpy.data.materials.get("M_Stones") or bpy.data.materials.new("M_Stones")
    low.data.materials.append(m)
    select_only([low])
    bpy.ops.export_scene.fbx(filepath=os.path.join(MODELS, low.name + ".fbx"), use_selection=True, object_types={'MESH'},
                             apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL', axis_forward='-Z', axis_up='Y',
                             bake_space_transform=True, use_mesh_modifiers=False, mesh_smooth_type='FACE',
                             use_tspace=True, add_leaf_bones=False, bake_anim=False, path_mode='STRIP',
                             embed_textures=False, use_custom_props=False)
    print("KIT exported", low.name, [round(d, 2) for d in low.dimensions])

# ---- cliff detail map: riverbed photo -> grey, mean 0.5, 1024 (tileable source)
src = bpy.data.images.load(DIFF)
src.scale(1024, 1024)
px = np.array(src.pixels[:], dtype=np.float32).reshape(-1, 4)
lum = px[:, 0] * 0.3 + px[:, 1] * 0.59 + px[:, 2] * 0.11
lum = 0.5 + (lum - lum.mean()) * (0.22 / max(lum.std(), 1e-4))
lum = np.clip(lum, 0.0, 1.0)
out = np.stack([lum, lum, lum, np.ones_like(lum)], axis=1).ravel()
detail = bpy.data.images.new("T_RiverbedRock_Detail", 1024, 1024, alpha=False)
detail.pixels.foreach_set(out)
detail.filepath_raw = os.path.join(ISL_TEX, "T_RiverbedRock_Detail.png")
detail.file_format = 'PNG'
detail.save()
print("KIT detail map written")

# ---- keep only the lows in the source file
for h in highs:
    bpy.data.objects.remove(h, do_unlink=True)
for o in list(scene.objects):
    if o not in lows:
        bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.outliner.orphans_purge(do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(SRC, "ENV_Stones_v01.blend"), compress=True)
print("KIT done")
