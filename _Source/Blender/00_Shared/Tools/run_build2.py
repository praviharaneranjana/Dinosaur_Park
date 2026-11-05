"""Runner v2: set BUILDER, BUILD, NAME, TGT, SCALE, (SAVE, GROUND_Z, RES) then exec.
Adds the 3-light lookdev rig and the inverted-hull ink outline to every v2 object that has none (skips smoke/mist volumes)."""
import bpy, json, time, traceback
from mathutils import Vector
TOOLS = r"D:\Unity Projects\Dinosaur_Park\Dinosaur_Park\_Source\Blender\00_Shared\Tools"
ROOT  = r"D:\Unity Projects\Dinosaur_Park\Dinosaur_Park\_Source\Blender"
_t0 = time.time(); _sc = bpy.context.scene; _info = {"name": NAME}
try:
    for _c in [c for c in bpy.data.collections if c.name.startswith("TRN_")]:
        for _o in list(_c.objects): bpy.data.objects.remove(_o, do_unlink=True)
        bpy.data.collections.remove(_c)
    bpy.data.orphans_purge(do_recursive=True)
    for _n in ('Cube',):
        _o = bpy.data.objects.get(_n)
        if _o: bpy.data.objects.remove(_o, do_unlink=True)
    _ns = {"TOOLS": TOOLS, "BUILD": BUILD}
    exec(compile(open(TOOLS + "\\" + BUILDER).read(), BUILDER, "exec"), _ns)
    for _f in ("trn_common.py","trn_hq.py","trn_hq2.py"):
        exec(compile(open(TOOLS + "\\" + _f).read(), _f, "exec"), _ns)
    _ns["render_setup"](globals().get("GROUND_Z", 0.0)); _ns["light_rig"]()
    for _c in [c for c in bpy.data.collections if c.name.startswith("TRN_")]:
        for _o in _c.objects:
            if _o.type != 'MESH' or _o.get('outline_done') or any(m.type == 'SOLIDIFY' for m in _o.modifiers): continue
            if any(s.material and ("Smoke" in s.material.name or "Mist" in s.material.name) for s in _o.material_slots): continue
            _ns["add_outline"](_o, globals().get("OUTLINE", 0.011))
    _cam = bpy.data.objects["Camera"]; _cam.data.type = "ORTHO"; _cam.data.clip_start = 0.1; _cam.data.clip_end = 200; _cam.data.ortho_scale = SCALE
    _t = Vector(TGT); _cam.location = _t + Vector((-8.5,-8.5,8.5)); _cam.rotation_euler = (_t-_cam.location).to_track_quat('-Z','Y').to_euler()
    _sc.render.resolution_x, _sc.render.resolution_y = globals().get("RES", (1800, 900))
    _sc.render.filepath = ROOT + r"\renders\terrain\%s.png" % NAME
    bpy.ops.render.render(write_still=True)
    if globals().get("SAVE"): bpy.ops.wm.save_as_mainfile(filepath=ROOT + "\\" + SAVE)
    _info.update(tris=_ns.get("RESULTS"), sec=round(time.time()-_t0,1), ok=True)
except Exception:
    _info.update(ok=False, err=traceback.format_exc()[-1800:])
open(ROOT + r"\renders\terrain\%s.json" % NAME, "w").write(json.dumps(_info))
result = _info
