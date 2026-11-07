"""Motion preview: rebuild each set in SETS, frame it, render FRAMES frames (every STEP) at RES into renders/plants/anim/PLN_<Set>_####.png"""
import bpy, json, os, time
TOOLS = r"D:\Unity Projects\Dinosaur_Park\Dinosaur_Park\_Source\Blender\00_Shared\Tools"
ROOT = r"D:\Unity Projects\Dinosaur_Park\Dinosaur_Park\_Source\Blender"
os.makedirs(os.path.join(ROOT, "renders", "plants", "anim"), exist_ok=True)
prog = {"done": [], "fail": {}, "t0": time.time()}
for S in SETS:
    g = {"BUILDER": "build_pln.py", "BUILD": S, "NAME": os.path.join("..", "plants", "anim", "_still_%s" % S), "GROUND_Z": 0.0,
         "VIEWS": [dict(suffix="", dir=(0.25, -1, 0.32), auto=True, res=RES, samples=8, pad=1.04)]}
    try:
        exec(open(os.path.join(TOOLS, "run_views.py")).read(), g)
        sc = bpy.context.scene; sc.frame_start = 1; sc.frame_end = FRAMES; sc.frame_step = STEP
        sc.render.resolution_x, sc.render.resolution_y = RES; sc.eevee.taa_render_samples = 12
        sc.render.image_settings.file_format = 'PNG'
        sc.render.filepath = os.path.join(ROOT, "renders", "plants", "anim", "PLN_%s_" % S)
        bpy.ops.render.render(animation=True); sc.frame_step = 1; sc.frame_set(1)
        prog["done"].append(S)
    except Exception as e:
        prog["fail"][S] = repr(e)
    prog["elapsed"] = round(time.time() - prog["t0"], 1)
    open(os.path.join(ROOT, "renders", "plants", "anim", "_progress.json"), "w").write(json.dumps(prog))
result = prog
