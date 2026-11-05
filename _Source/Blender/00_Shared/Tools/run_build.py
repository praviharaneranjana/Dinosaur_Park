"""Runner: set BUILDER, BUILD, NAME, TGT, SCALE, (SAVE, GROUND_Z, RES) then exec. Writes renders/terrain/<NAME>.png and <NAME>.json"""
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
    _ns = {"TOOLS": TOOLS, "BUILD": BUILD}
    exec(compile(open(TOOLS + "\\" + BUILDER).read(), BUILDER, "exec"), _ns)
    exec(compile(open(TOOLS + r"\trn_common.py").read(), "c", "exec"), _ns)
    exec(compile(open(TOOLS + r"\trn_hq.py").read(), "hq", "exec"), _ns)
    _ns["render_setup"](globals().get("GROUND_Z", 0.0))
    _cam = bpy.data.objects["Camera"]; _cam.data.ortho_scale = SCALE
    _t = Vector(TGT); _cam.location = _t + Vector((-8.5,-8.5,8.5)); _cam.rotation_euler = (_t-_cam.location).to_track_quat('-Z','Y').to_euler()
    _sc.render.resolution_x, _sc.render.resolution_y = globals().get("RES", (1800, 900))
    _sc.render.filepath = ROOT + r"\renders\terrain\%s.png" % NAME
    bpy.ops.render.render(write_still=True)
    if globals().get("SAVE"): bpy.ops.wm.save_as_mainfile(filepath=ROOT + "\\" + SAVE)
    _info.update(tris=_ns.get("RESULTS"), sec=round(time.time()-_t0,1), ok=True)
except Exception:
    _info.update(ok=False, err=traceback.format_exc()[-1500:])
open(ROOT + r"\renders\terrain\%s.json" % NAME, "w").write(json.dumps(_info))
result = _info
