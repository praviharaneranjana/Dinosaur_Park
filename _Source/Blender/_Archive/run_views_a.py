"""Runner v3: set BUILDER, BUILD, NAME, VIEWS, (SAVE, GROUND_Z, ENGINE) then exec.
Builds like run_build2 (lookdev rig + ink outlines) and renders several camera views.
VIEWS = [dict(suffix, dir=(x,y,z) camera direction from target, target, scale, res, samples, clip=None (section: clip at target plane), only=None (name substrings))]"""
import bpy, json, time, traceback, os
from mathutils import Vector
TOOLS = globals().get("TOOLS_DIR", r"D:\Unity Projects\Dinosaur_Park\Dinosaur_Park\_Source\Blender\00_Shared\Tools")
ROOT  = globals().get("ROOT_DIR", r"D:\Unity Projects\Dinosaur_Park\Dinosaur_Park\_Source\Blender")
_t0 = time.time(); _sc = bpy.context.scene; _info = {"name": NAME, "views": []}
try:
    for _c in [c for c in bpy.data.collections if c.name.startswith("TRN_")]:
        for _o in list(_c.objects): bpy.data.objects.remove(_o, do_unlink=True)
        bpy.data.collections.remove(_c)
    bpy.data.orphans_purge(do_recursive=True)
    _o = bpy.data.objects.get('Cube')
    if _o: bpy.data.objects.remove(_o, do_unlink=True)
    _ns = {"TOOLS": TOOLS, "BUILD": BUILD}
    exec(compile(open(os.path.join(TOOLS, BUILDER)).read(), BUILDER, "exec"), _ns)
    for _f in ("trn_common.py","trn_hq.py","trn_hq2.py"):
        exec(compile(open(os.path.join(TOOLS, _f)).read(), _f, "exec"), _ns)
    _ns["render_setup"](globals().get("GROUND_Z", 0.0)); _ns["light_rig"]()
    if globals().get("ENGINE"): _sc.render.engine = ENGINE
    for _c in [c for c in bpy.data.collections if c.name.startswith("TRN_")]:
        for _o in _c.objects:
            if _o.type != 'MESH' or _o.get('outline_done') or any(m.type == 'SOLIDIFY' for m in _o.modifiers): continue
            if any(s.material and ("Smoke" in s.material.name or "Mist" in s.material.name or "Spray" in s.material.name) for s in _o.material_slots): continue
            _ns["add_outline"](_o, globals().get("OUTLINE", 0.011))
    _cam = bpy.data.objects.get("Camera")
    if _cam is None:
        _cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera")); _sc.collection.objects.link(_cam)
    _sc.camera = _cam; _cam.data.type = "ORTHO"; _cam.data.clip_end = 200
    _saved = False
    for _v in VIEWS:
        _hidden = []
        if _v.get("only"):
            for _o in _sc.objects:
                if _o.type == 'MESH' and not _o.name.startswith("_") and not any(k in _o.name for k in _v["only"]):
                    if not _o.hide_render: _o.hide_render = True; _hidden.append(_o)
        _t = Vector(_v["target"]); _d = Vector(_v["dir"]).normalized(); _D = 30.0
        _cam.location = _t + _d*_D; _cam.rotation_euler = (_t-_cam.location).to_track_quat('-Z','Y').to_euler()
        _cam.data.ortho_scale = _v["scale"]; _cam.data.clip_start = (_D + _v["clip"]) if _v.get("clip") is not None else 0.1
        _sc.render.resolution_x, _sc.render.resolution_y = _v.get("res", (1800, 1000))
        try: _sc.eevee.taa_render_samples = _v.get("samples", 48)
        except Exception: pass
        _sc.render.filepath = os.path.join(ROOT, "renders", "terrain", "%s%s.png" % (NAME, _v["suffix"]))
        bpy.ops.render.render(write_still=True); _info["views"].append(_v["suffix"])
        for _o in _hidden: _o.hide_render = False
        if not _saved and globals().get("SAVE"):
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, SAVE)); _saved = True
    _info.update(tris=_ns.get("RESULTS"), sec=round(time.time()-_t0,1), ok=True)
except Exception:
    _info.update(ok=False, err=traceback.format_exc()[-1800:])
open(os.path.join(ROOT, "renders", "terrain", "%s.json" % NAME), "w").write(json.dumps(_info))
result = _info
