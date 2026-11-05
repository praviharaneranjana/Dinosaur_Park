# Changelog

## 2026-11-04
- TRN phase: all 13 terrain sets built as v01 in 01_Terrain (builders in 00_Shared/Tools, shared helpers trn_common.py).
- ValleyGround reworked after review: wet-chocolate mud with reflections, rough shadowed rock ground.

## 2026-11-04 (evening) - TRN v02
- Rebuilt 12 TRN sets at v02 quality following blender-skills-pack (blender-director > reference-image-match; environment-artist, hand-painted-style, stylized-style, isometric-style, materials, lighting, vfx-fx, qa-review). Brief: _Reference/TRN_reference_analysis_v02.md.
- New shared tools: trn_hq.py (curvature-baked edge wear/cavity shading, painterly material, HQ fractured rock), trn_hq2.py (painted water with depth colour + foam + ripple strokes, lava glow, mist/smoke volumes, ink outline hull), run_build2.py.
- CliffEdge: grass cap is a separate TRN_Cliff_*_Top object; swap its material to any TRN_Top_* (GrassShort, GrassLush, GrassDry, Dirt, Rock, Mud).
- Ink outlines are separate *_Outline child objects (optional for Unity export).
- v01 files kept untouched. ValleyGround stays v01 (approved).

## 2026-11-05 - TRN v03: Volcano, Desert, Swamp
- New builder `00_Shared/Tools/build_trn_v3b.py` (BUILD = volcano | desert | swamp), reuses v02/v03 helpers.
- Volcano: raised basalt plates with narrow glowing cracks (also on tile sides), blocky lava rocks with veins on ash discs, mini volcano = ridged cone with lava runnels + 7 rings of basalt shards + crater glow + smoke preview; mottled ash tile with 70 pebbles.
- Desert: barchan dunes (long windward ramp, sharp crest, steep slip face, horns), asymmetric wind ripples, saturated orange/pink sand; mesas from angular stacked slabs with dark/orange/pink/pale strata, cracks and fallen blocks.
- Swamp: black wet peat, 3D moss cushions, ~120 solid 3D leaves (each casts its own shadow), ferns, twigs, sprouts; side walls with moss drips; algae pool with irregular outline reaching the tile front so the water side shows, floating 3D algae rafts, animated water; reed marsh with glossy mud, irregular puddles, reeds and cattails.

## 2026-11-05 - TRN Waterfalls v04 (v03 kept)
- New `BUILD="falls4"` block in `00_Shared/Tools/build_trn_v3.py`; new runner `00_Shared/Tools/run_views.py` (multi-view + section renders). v03 `falls` block untouched.
- Same footprints (2x2 / 4x3), base-centre pivots, drops (2 m / 3 m), river in at back centre and out at front centre.
- Cliffs: warm grey-brown faceted stone faces (blended voronoi planes), chipped grass rims with stone lips and overhangs; big right bank = 4 shelves stepping down toward the pool, left bank = interlocking column; mossy ledges only.
- Lip: channel bed rises to a rounded rock ledge, water wraps it (one water mesh/material: feeder -> bend -> fall, attributes fallv/depth/mask, FlowUV).
- Big: spur rock left of centre at the brink (crown above the water, face below the lip), narrow left chute + broad right curtain with 3 unequal folds and separate impact lobes.
- Pool: irregular recessed shore with a grassy front bank and outflow channel; broken ripple arcs from each impact; alpha-cut churn patches on the water; bottom-heavy spray volumes (preview).
- Renders: renders/terrain/TRN_Waterfalls_v04.png, _sideBig, _topBig; anim/TRN_Waterfalls_v04_anim.gif.

## 2026-11-05 - PLN phase v01: all 24 plant sets
- New: `00_Shared/Tools/pln_kit.py` (plant toolkit: tube/branch/leaf/clump/frond/blade/lathe primitives, painterly plant + bark + grass materials,
  leaf-mass custom normals, WindData colour attribute, PLN_Motion geometry-nodes motion), `build_pln.py` (BUILD=<Set>), `run_pln_all.py`, `run_pln_anim.py`.
- Files: 04_Plants/PLN_<Set>_v01.blend (24). Renders: renders/plants/PLN_<Set>_v01.png, comparison sheets renders/plants/_cmp_0..5.jpg,
  motion preview renders/plants/anim/PLN_motion_preview.gif.
- Motion presets: tree / tree_big / conifer / palm / shrub / fern / grass / reed / flower / hedge / deadwood (wind sway + spatial gusts + leaf flutter),
  kelp / seaweed / coral_fan (underwater travelling wave), float (lily pad, duckweed bob + edge ripple); rigid: cacti, stumps, logs, branching/brain/table coral.
- Unity: per-vertex colour WindData (R bend, G flutter, B phase) for a wind/water vertex shader; GN modifier is Blender preview only.
- Optional children: *_Outline (ink hull, follows motion), *_Ground (soil/sand decal), *_Ripple (water ring).
