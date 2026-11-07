"""Dino Park Tycoon - island v02 master runner (inside Blender). ns = {"STAGES": {...}}; exec(open(path).read(), ns)
Stages: scene, ground, cliffs, water, ocean, props, plants, wind. Layout first: python3 isl_layout_v02.py (VM)."""
import time
_T = r"D:\Unity Projects\Dinosaur_Park\Dinosaur_Park\_Source\Blender\00_Shared\Tools"
STAGES = globals().get("STAGES", {"ground", "cliffs", "water", "props", "plants"})
LOG = {}
for f in ("isl_v02_common.py", "isl_v02_terrain.py", "isl_v02_cliffs.py", "isl_v02_water.py", "isl_v02_props.py", "isl_v02_plants.py"):
    exec(compile(open(_T + "\\" + f).read(), f, "exec"), globals())
t0 = time.time()
if "scene" in STAGES: exec(compile(open(_T + "\\isl_v02_scene.py").read(), "scene", "exec"), globals())
if "ground" in STAGES:
    _ob, TERRAIN_CACHE = build_ground(); HG = TERRAIN_CACHE["h"]; LOG["ground"] = round(time.time() - t0, 1)
else:
    HG = np.load(ISL + r"\_v02_h.npy")
    if "plants" in STAGES: TERRAIN_CACHE = TERRAIN()
if "cliffs" in STAGES:
    Cc = coll("ISL2_Cliffs"); clear_coll(Cc); rr = S["ramp_road"]
    mid = [(rr[3][0] + rr[5][0])/2, (rr[3][1] + rr[5][1])/2]; rad = math.hypot(rr[3][0] - rr[5][0], rr[3][1] - rr[5][1])/2 + 3; fb = S["fall_base"]
    Cc.objects.link(build_cliff_skirt("TRN2_CliffFace_Plateau", S["plateau"], HG, skip=[(mid[0], mid[1], rad), (fb[0], fb[1], 6.5)])); LOG["cliffs"] = round(time.time() - t0, 1)
if "water" in STAGES: build_water(HG); LOG["water"] = round(time.time() - t0, 1)
if "ocean" in STAGES:
    on = {}; exec(open(_T + "\\isl_ocean.py").read(), on)
    on["TERRAIN"].update(shelf_slope=0.22, ramp_from=6.0, ramp_to=55.0, deep_m=16.0)
    on["TUNE"].update(streaks=0.0, crest_foam=0.0, breaker_reach=14.0, breaker_amp=0.18, amp_scale=0.6, sparkle=0.5, caustics=0.6, shore_foam=1.2, depth_ref=7.0, alpha_depth=2.0)
    on["COLORS"].update(shallow="#5ACFC6", mid="#229AB2", deep="#176E96", navy="#13457A", tropical="#2CD3C3", horizon_start="#164F86", horizon_end="#7FB3D1", sky="#9CC9E0")
    oc = coll("ISL2_Ocean"); clear_coll(oc); on["build_ocean"](oc, ISL + r"\island_map_v02.json", extent_m=(700, 700)); LOG["ocean"] = round(time.time() - t0, 1)
if "props" in STAGES: LOG["props_n"] = build_props(HG); LOG["props"] = round(time.time() - t0, 1)
if "plants" in STAGES: LOG["plants_n"] = build_plants(HG, globals().get("DENSITY", 1.0)); LOG["plants"] = round(time.time() - t0, 1)
if "wind" in STAGES:
    wn = {}; exec(open(_T + "\\isl_wind.py").read(), wn); wn["make_wind_control"]()
    objs = [o for o in bpy.data.collections["ISL2_Plants"].objects if o.get("motion")]
    wn["apply_wind_many"](objs, base_seed=100, strength=1.0); LOG["wind_n"] = len(objs); LOG["wind"] = round(time.time() - t0, 1)
result = LOG
