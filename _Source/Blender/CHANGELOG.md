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

## 2026-11-05 — Island v02 (camera-matched rebuild)
- New file 02_Environment/Island/ISL_Main_v02.blend (scene ISL2_Main, camera ISL2_RefCam matches the reference; reference overlay on the camera, alpha 0 by default).
- Layout: 00_Shared/Tools/isl_layout_v02.py + isl_cam.py -> island_map_v02.json (grid 130x120 @ 2 m; ocean W/N/E, mainland continues south).
- Builder: build_island_v02.py (stages scene/ground/cliffs/water/ocean/props/plants/wind) with isl_v02_*.py modules.
- New assets (TRN2_*): CliffFace (rugged rock skirt), Waterfall_Tall (2-strand, 14 m) + Cascade_Small, Desert_MesaTall x3, Desert_Arch, Bridge_Wood, Pier_East/West, Stairs_Timber, FenceRing (posts only), Footprints, VolcanoSmoke; rock materials per kind (coast/ground/high/mud/desert/lava).
- PLN scatter ~1,500 plants with per-object random wind (isl_wind); darker tinted local material copies (PLN2_*).

## 2026-11-06 - Island v05 imported into Unity
- Source: `ISL_Main_v05.blend` (branch claude/island-realism-terrain-311e32). Exporter: `00_Shared/Tools/export_island_unity.py` (headless, never saves the blend):
  `blender -b ISL_Main_v05.blend --python export_island_unity.py -- <Unity>/Assets/Models/Environment/Island 4096`
- Procedural materials are baked (Cycles diffuse COLOR) to a vertex colour `BakeCol`; ground baked to `Textures/ISL_Ground_Albedo.png` (4K, top-down UV). Leaf-card transparent mixes are bypassed for the bake; leaf atlases are kept for alpha cut-out.
- One FBX per unique mesh (100: 15 props, 42 plants, ground, cliffs, ocean, 39 water pieces) + `island_layout.json` (2,260 placements as Blender world matrices) + axis probes.
- Unity: menu Dino Park > Island > Import Island From Blender Export (`Assets/Editor/Island/IslandImporter.cs`) builds materials (`Assets/Materials/Environment/Island`, shader `DinoPark/Environment/VertexColorLit`), prefabs (`Assets/Prefabs/Environment/Island`) and the `--- Island ---` group in `Island.unity`. Island turned 180 deg so north = +Z; IslandBounds = 290 x 360 m; terrain, cliffs and rocks have MeshColliders.
- Known gaps: ~10M triangles placed (trees are source/LOD0 meshes, no LODs yet), water is static (no scrolling waterfall shader), per-tree colour variation from Object Info is lost, the south edge of the ground is a straight cut.

## 2026-11-06 - Island v05 Unity polish pass (Unity-side, Blender to follow)
- Menu Dino Park > Island > Apply Polish Pass (runs automatically after Import). Code: Assets/Editor/Island/IslandPolish*.cs, textures generated in code (ProceduralTextures.cs, no third-party images).
- Ramp road flattened to an even grade, flat across; entrance road flattened; rocks/plants cleared off both.
- Plateau cliff rebuilt from the ground's 11 m contour: layered rock wall with ledges, joint blocks, moss (Blender TRN5 cliff disabled).
- Waterfalls rebuilt: two-layer curtains (streaks, glassy lip, foam base), radial plunge foam, spray + mist particles (Blender boil spheres/mist disabled). River and plateau stream rebuilt as flow-mapped surfaces along their centre lines; ponds/mud/swamp restyled.
- Ocean: wave mesh (Gerstner), depth from distance to shore, surf bands rolling onto the beach, shore foam.
- Wind sway on all plant materials (WindSettings component).
- Land side: south mountain range with forest, concrete tunnel portal + interior, asphalt road to the plaza, looping visitor cars (VehicleTraffic). Camera from the east (yaw -90, pitch 52, max 215 m). URP depth texture on.
- To do in Blender later: mountain + tunnel, proper river bed depth, pond outlines (stair-step edges), mobile LODs for trees.
