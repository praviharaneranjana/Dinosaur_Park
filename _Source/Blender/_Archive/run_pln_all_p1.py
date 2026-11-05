"""Batch: build + render + save every PLN set. Set SETS (list) before exec. Writes renders/plants/PLN_<Set>_v01.png and a progress json."""
import bpy, json, os, time
TOOLS = r"D:\Unity Projects\Dinosaur_Park\Dinosaur_Park\_Source\Blender\00_Shared\Tools"
ROOT = r"D:\Unity Projects\Dinosaur_Park\Dinosaur_Park\_Source\Blender"
prog = {"done": [], "fail": {}, "t0": time.time()}
os.makedirs(os.path.join(ROOT, "renders", "plants"), exist_ok=True)
for S in SETS:
    g = {"BUILDER": "build_pln.py", "BUILD": S, "NAME": os.path.join("..", "plants", "PLN_%s_v01" % S), "GROUND_Z": 0.0,
         "SAVE": os.path.join("04_Plants", "PLN_%s_v01.blend" % S),
         "VIEWS": [dict(suffix="", dir=(0.25, -1, 0.32), auto=True, res=(1600, 900), samples=32, pad=1.04)]}
    try:
        exec(open(os.path.join(TOOLS, "run_views.py")).read(), g)
        if g["result"].get("ok"): prog["done"].append([S, g["result"].get("tris"), g["result"].get("sec")])
        else: prog["fail"][S] = g["result"].get("err")
    except Exception as e:
        prog["fail"][S] = repr(e)
    prog["elapsed"] = round(time.time() - prog["t0"], 1)
    open(os.path.join(ROOT, "renders", "plants", "_progress.json"), "w").write(json.dumps(prog))
result = prog
