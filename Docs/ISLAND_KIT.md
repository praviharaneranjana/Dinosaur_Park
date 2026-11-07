# Island build kit: reference zones to TRN / PLN sets

Reference: `Assets/Concepts/Island/approved.jpg` (Gemini, 5 Nov 2026). Source files: `_Source/Blender/01_Terrain` (TRN) and `_Source/Blender/04_Plants` (PLN). Registry: `_Source/Blender/MANIFEST.csv`. Latest version of each set wins (TRN v02 base; Volcano/Desert/Swamp v03; Waterfalls v04; PLN v01).

All sets are LOD0 source. No FBX has been exported to `Assets/Models` yet (no `Terrain/` or `Plants/` folder there). Tri counts below are far over a mobile budget until the LOD bake is done (see Risks).

## Zone map (reference image, north = top)

| Zone in image | TRN sets | PLN sets |
|---|---|---|
| North forest plateau with cliff rim | `TRN_CliffEdge_v02`, `TRN_RockyHills_v02` | `PLN_Conifer`, `PLN_GiantTree` (umbrella/baobab trees), `PLN_Broadleaf`, `PLN_Ginkgo`, `PLN_Cycad`, `PLN_DeadTrees` (bare snags) |
| Waterfall, river, pond (centre-north) | `TRN_Waterfalls_v04`, `TRN_River_v02`, `TRN_Ponds_v02` | `PLN_ReedsCattails`, `PLN_WaterPlants`, `PLN_Horsetails` |
| Swamp (west) | `TRN_SwampIsland_v03` | `PLN_Mangrove`, `PLN_FernTree`, `PLN_Ferns`, `PLN_ToxicBloom` (purple flowers), `PLN_Horsetails`, `PLN_Palm` |
| Mud flats with footprints (west-centre) | `TRN_ValleyGround_v01` | `PLN_StumpsLogs`; `CMP_Dino_Footprint` (component kit) |
| Volcano and lava field (north-east) | `TRN_VolcanoIsland_v03` | `PLN_DeadTrees`, `PLN_StrippedTrees`, `PLN_Palm` |
| Desert with red mesas (east) | `TRN_DesertIsland_v03` | `PLN_DesertPlants` (saguaro, barrel, shrub) |
| Central meadow (build area) | `TRN_ValleyGround_v01`, `TRN_Slopes_v02`, `TRN_LevelledPads_v02`, `TRN_Boulders_v02` | `PLN_GrassPatches`, `PLN_Bushes`, `PLN_Flowers`, `PLN_Broadleaf`, `PLN_Hedges` |
| Beaches and shoreline | `TRN_BeachShore_v03` | `PLN_Palm`, `PLN_StumpsLogs` (driftwood) |
| Coral reef and shallows | none | `PLN_Coral`, `PLN_Kelp`, `PLN_Seaweed` |
| Ocean | placeholder plane in `Island.unity` (water shader not built) | none |

Foreground tree belts (south) use `PLN_Broadleaf` + `PLN_Conifer` + `PLN_Bushes`. The dirt road is a road piece (`Assets/Models/Roads`), not terrain. The four cobble pads at the entrance are `TRN_LevelledPads`.

## Gaps (not covered by any TRN or PLN set)

1. Island base mesh / heightmap: the main landmass, cliff plateau, beach falloff and seabed. No set provides it. Needs its own task (suggest `TRN_IslandBase`, built to the 80 x 80 cell footprint, 160 m).
2. Wooden bridge over the river (north-centre).
3. Wooden piers (west and south-east beaches).
4. Round wooden corral fence (south-east).
5. Ocean water shader and shore foam.
6. Standing stones / ruins in the meadow (optional, cut first).

Items 2-4 belong in `06_Props`; the road and building pieces already exist.

## Folder readiness

| Folder | State |
|---|---|
| `_Source/Blender/01_Terrain`, `04_Plants` | Ready: 13 TRN + 24 PLN sets, builders in `00_Shared/Tools` |
| `_Source/Blender/02_Environment`, `06_Props` | Empty. Island base, bridge, piers, corral go here |
| `Assets/Models/Terrain`, `Assets/Models/Plants` | Do not exist yet. Create on first FBX export (`unity-export` skill) |
| `Assets/Scenes/Island.unity` | Placeholder island + ocean, rebuilt by `Dino Park > Setup > Build Island Scene` |
| `Assets/Data` | Camera config only. Add a zone/scatter config (ScriptableObject) before placing plants |

## Risks to settle before island assembly

- Triangle budget: single sets run 30k-150k tris (e.g. DesertIsland 150k, GiantTree 59k, Volcano_Mini 103k). A mobile island needs LODs and instancing; do the LOD bake (`lod-pipeline`, `asset-optimization`) per set before export.
- Plants carry per-vertex `WindData` (R bend, G flutter, B phase) for a wind shader that does not exist in Unity yet.
- Ink `*_Outline` child objects are optional; decide whether to ship them.
- Scale and pivots must follow `Docs/DESIGN_BIBLE.md` (1 cell = 2 m, base-centre pivot) at export.

## Suggested order for the island

1. `TRN_IslandBase` (heightmap, landmass, shore) in Blender.
2. Export TRN sets to `Assets/Models/Terrain`; assemble zones in the Island scene.
3. Water: river, ponds, waterfalls, ocean shader.
4. Export PLN sets; scatter by zone with a data-driven config.
5. Props (bridge, piers, corral), then clear-area rules for the player.
