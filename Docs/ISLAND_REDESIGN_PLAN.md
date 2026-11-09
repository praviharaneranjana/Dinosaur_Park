# Island redesign plan (from the 9 Nov 2026 phone test)

Source: 16 phone screenshots of the Android test build (Xperia, 43-60 fps) and the developer's review.
Branch: `feature/island-redesign` (off `feature/island-camera-foundation`).
Pipeline: Blender export -> `IslandImporter` -> `IslandPolish` (Assets/Editor/Island). All fixes go into the polish
steps so a re-run of `Dino Park > Island > Apply Polish Pass` rebuilds them.

## New world layout
The park sits on a small headland (peninsula) that pushes out from the mainland into the ocean.
The south side is flat mainland, not a mountain. A highway runs east-west along the mainland; through
traffic drives both ways and some cars turn north onto the park road, pass a grand entrance gate with the
park sign, and drive to the plaza. No mountain, no tunnel.

## Problems found and what changes

| # | Problem (screenshot) | Cause | Fix | Phase |
|---|---|---|---|---|
| 1 | Mountain + tunnel on the south side (4, 8) | `BuildMountainAndTunnel` | Replace with flat mainland ground, coastline curving away from the headland, trees, highway | 1 |
| 2 | No highway, no grand entrance | not built | 4-lane highway E-W, turn-off road, entrance gate (pillars, timber beam, brass "DINO PARK" sign, ticket booths, perimeter wall), through traffic + visitor cars | 1 |
| 3 | Palms lose their leaves when zoomed out | auto Mesh LOD simplifies the frond cards away | Palms (and other card-leaf trees) keep full-detail leaves; only cull tiny plants | 1 |
| 4 | Two water layers at the waterfall pool; river not aligned with the falls (11, 12, 14) | Polish river surface starts inside the Blender pool and sits at a different height; stair-step pool outline | One water surface: river starts at the pool rim at pool height; pool outline smoothed; curtain lip snapped to the stream end | 2 |
| 5 | River looks different from the rest; banks are bare (5, 7) | separate river colours; no bank dressing | Shared water palette with the sea; bank rocks (from `Downloads/cliff/stones.blend`), reeds, wet-sand edge | 2 |
| 6 | River "closes" before it reaches the sea (1, 5) | river surface stops above sea level, mouth narrows | Mouth widens into a delta and runs down to sea level under the surf | 2 |
| 7 | Jagged / pixel-step beach line; waves never reach the sand (2, 3, 6) | 3 m ocean grid + vertex-depth foam | Fine shore grid, foam from scene depth, swash band that runs up and back over the sand | 3 |
| 8 | No big waves at the cliffs; flat 2D-looking rocks under the cliffs (15, 16) | flat surf only; low-poly rock cards | Breaking surf + spray particles on cliff shores; replace with `stones.blend` rocks (decimated, LODs) | 3 |
| 9 | Brown mud strip left of the river (7, 8) | Blender ground paint | Repaint to grass, add trees | 4 |
| 10 | 3-4 small mud ponds under the cliffs (7) | separate mud puddles | One big mud wallow under the cliffs (real mud material, wet edge, footprints) | 4 |
| 11 | Grass looks painted; raised ground has no grass (1, 2) | flat texture, no grass on slopes | Grass detail texture (Mountain+2 Green1/Green2), denser grass cards on all land incl. hills | 4 |
| 12 | Dirt paths look wrong (4, 8) | flat brown paint | Restyle as packed-earth paths with edges | 4 |
| 13 | Cliff not the supplied cliff look (9, 10) | procedural cliff wall | Face built from `stones.blend` pieces with the riverbed rock texture | 5 |
| 14 | Sea stacks are flat triangles (15) | low-poly placeholder | Rebuild from `stones.blend` pieces | 5 |

## Source assets in Downloads (checked 9 Nov)
- `cliff/models(1)/stones.blend`: 4 sculpted rock blocks (74k-279k tris each) + `dry_riverbed_rock` 4K textures. Needs decimation to ~2-4k tris + LODs.
- `ocean/Water_Pack_Ozero.blend`: wave water mesh (216k tris) + `OCEAN+WATER/MAPS` (foam opacity, beach diffuse). Use the textures; mesh is too heavy.
- `Waterfall_Scene.blend`: small waterfall diorama (waterfall + river + fog materials, GrassyRocks textures). Use as the look target and texture source.
- `Mountain+2(1)/texture`: Green1/Green2 grass textures for the ground detail map.
- `riverpond`: only a skydome (not used).
Log every pack used in `ASSET_LICENSES.md` before it ships.

## Order
1. Mainland, highway, entrance, traffic, palm LOD fix. **Done 9 Nov** (`IslandPolish.Land.cs`).
2. Waterfall pool, river, banks, mouth. **Done 9 Nov** (`IslandPolish.River.cs`: one height-grid surface pool->sea, carved channel, uv0 fade into the sea; main fall from the stream lip).
3. Ocean shoreline, swash, cliff surf. **Done 9 Nov** (`IslandPolish.Shore.cs`, `DinoPark_Swash.shader`). Cause of the jagged beach: the island ground is ~3 m triangles reaching far out to sea and the beach was a flat shelf at sea level, so sea and sand z-fought along triangle edges. Fix: steeper profile through the waterline, flat ocean in the last 1.5 m of depth, soft ocean edge, and a 1 m swash sheet with a waterline lip that covers the cut. Rocks under the cliffs and the jagged cliff foot move to phase 5.
4. Ground: grass, mud wallow, paths. **Done 9 Nov** (`IslandPolish.Ground.cs`): wide brown areas in the ground texture become grass (morphological opening keeps thin paths), paths retoned to packed earth, four puddles merged into one 38 x 24 m wallow with a carved basin, grass-blade detail on the ground, grassy tops on rock mounds, 700 extra grass clumps, matte swamp water. Editor stats after this pass: 1.42M tris, 1860 draw calls in the full view; check fps on the phone in phase 6.
5. Cliffs and sea stacks from the stones kit. **Done 9 Nov** (`build_stones_kit.py` -> 4 rocks at 3k tris with a baked 2K albedo + normal atlas; `IslandPolish.Rocks.cs`): riverbed rock photo as the cliff face detail, ~150 rocks piled along the cliff foot, 58 coastal mounds and 226 low-poly boulders swapped for kit rocks, and the thin sand-painted ridge in the ground mesh on the north spit (the "flat triangle" stack) flattened with a real rock stack in its place. Left: a sand-textured steep ground slope on the plateau's north-east face.
6. Android build, phone check, evidence in `production/qa/evidence/`. **Done 9 Nov**: development build on Xperia 1 III (2560x1096), 52-60 fps after warm-up (one 2 s hitch on load), no Unity errors apart from the harmless Play Asset Delivery class probe. Open items: sand-textured steep slope on the plateau's north-east face; the falls pool reads very white near the plunge; rock tint vs cliff grey; confirm the stones model license.
