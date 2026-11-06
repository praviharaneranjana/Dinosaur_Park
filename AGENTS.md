# AI Agent Directives: Dino Park Tycoon (mobile)

Unity 6 (6000.6.7f1), URP 17.6. Target: Android first. Solo developer, so keep tasks small and end each task with "How to test".

## Game in one paragraph
Dinosaur park tycoon. Clash of Clans-style tilted camera (drag to pan, pinch to zoom, clamped to the map). V1 is one island: ocean on three sides, and on the south (land) side a forested mountain with the visitor tunnel where cars and guests arrive (camera from the east side, clamped to the island); mountains stay as terrain. Player clears trees/rocks by selecting an area, builds on a grid (1 cell = 2 m): cages, hatchery/lab, roads, canteen. Dinosaurs unlock by level, guests walk the roads. Endless expansion, daily rewards. Money mainly from ads (rewarded ads first), plus small extras.

## Folders
- Assets/Models, Materials, Animations: imported art (buildings, enclosures, roads, props, characters, environment, 6 dinosaurs)
- Assets/Models/Vehicles/Cars: 7 low-poly cars (Quaternius, CC0). Use for park shuttles/parking and road traffic
- Assets/Models/Trains: Kenney train kit, 103 pieces (tracks, locomotives, carriages, trams). Use for a park train ride
- Assets/Models/Town: Downtown City MegaKit free version (modular buildings, streets, sidewalks, props). FBX in Town/FBX, textures in Town/Textures
- Assets/Concepts: approved concept images and their prompts
- Assets/Scripts: one assembly, `DinoPark.Runtime` (asmdef at the folder root; references Lean Touch and NaughtyAttributes). New systems go in `Assets/Scripts/<System>/` under namespace `DinoPark.<System>`. Old prototype scripts (bird system, wind sway, pond, visitor AI, dinosaur habit AI, doors; namespace `MiniGame`) live here too and are not yet data-driven
- Assets/Scripts/CameraControl: locked island camera (`IslandCameraRig`, `IslandBounds`, `IslandCameraConfig`, pure maths in `CameraFootprintMath`)
- Assets/Editor: editor tools. `Dino Park > Setup > Build Island Scene` rebuilds `Assets/Scenes/Island.unity` (placeholder island and ocean)
- Assets/Data: ScriptableObject data (camera config now; dinosaurs and buildings next)
- Assets/Tests/EditMode: NUnit tests (`DinoPark.Tests.EditMode`). Run: Window > General > Test Runner > EditMode
- Assets/Plugins/CW: Lean Touch (touch camera). NaughtyAttributes and Colorful Hierarchy are installed too
- .agents/rules and .agents/skills: domain rules and skills (touch, UI, ads/IAP, audio, FBX, performance, logcat, notifications)
- _Reference: old editor scripts, Blender generation scripts and the old AGENTS file. Not compiled, read-only reference

## Design docs (read before art or scope work)
- `Docs/DESIGN_BIBLE.md` art rules, palette, scale. `Docs/BUILDING_IDENTITY.md` per-building identity matrix. `Docs/V1_PLAN.md` V1 scope, schedule, cut order.
- Skills: `dino-park-art-bible`, `dino-park-building-identity`, `dino-park-v1-scope` in `.agents/skills`.
- Rule: same park, same palette, different architecture. Tier A landmarks need unique roofline + primary material + silhouette; Tier B small services need unique silhouette + roofline. Silhouette test (black, 64 px) before modelling.
- V1 is the revised test build (9 species, 1 island, 1 event), not the full vision.

## Studio framework (Claude Code Game Studios)
`.claude/` holds 49 agents and ~74 slash skills (installed 4 Nov 2026). Config: `project.yaml` (Unity 6000.6.7f1, C#, URP). Code root is `Assets/`. Framework `docs/` means our `Docs/`. Workflow: `/start` -> `/brainstorm` -> `/map-systems` -> `/design-system` -> `/create-architecture` -> `/create-epics` -> `/dev-story` -> `/code-review` -> `/story-done`; scope via `/scope-check` and `/gate-check` against `Docs/V1_PLAN.md`; device checks via `/perf-profile` and `/playtest-report`. Agents propose, the developer approves every file write. Not using Codex? Ignore `.codex`; Codex-style rules stay in `.agents/rules`.

## Principles
1. Unity 6 + URP only. No built-in pipeline calls.
2. Mobile performance first: pooled guests (30-50 on screen), simple grid pathfinding on roads, low triangle counts.
3. Touch: Lean Touch for pan/pinch. Ignore gameplay touches when the finger is over UI.
4. Inspector: use NaughtyAttributes ([Required], [ShowIf], [Button]) instead of custom editors.
5. Hierarchy: group with "=== Category ===" and "--- Subcategory ---" objects.
6. Dinosaurs and buildings are data (ScriptableObjects). Do not hard-code stats.
7. Check each asset's license before it ships (log in ASSET_LICENSES.md).

## Art standards
Palette: off-white concrete #F4EDD8, light timber #C79A63, charcoal steel #3B4743, teal glass #8FCBCB, living-roof green #5E9B4A, brass gold #F2B84B, amber glow #FFAA33. Never neon, never bright red/blue roofs.
Scale: 1 cell = 2.0 m. Solar panel 1.6 x 1.0 m everywhere. Doors 2.2-2.4 m high. Roads 4.0 m (2 cells).
Doors, gates and turnstiles are separate child objects with correct pivots; use InteractiveDoor.cs.
Model pivots at base center, flat bottom, no baked shadows.

## Imported kits: notes
- Town, car and train kits use a different style from the eco-park buildings. Keep them for background, entrances and transport, and recolor or restyle to the palette where they appear next to park buildings.
- Town textures are large (up to 4K, normal + ORM maps). Before building for mobile, set max texture size to 1024 or 2048 and compress, and use only the pieces that are placed.
- Log every new pack in ASSET_LICENSES.md.

## Building component kit (reuse on every building)
Blender kit in `_Source/Blender/SouvenirShop.blend`, collection CMP_Library, asset tag `building-component`. Full list and rules: `_Source/Blender/COMPONENTS.md`.
Components: CMP_Window, CMP_AC_Unit, CMP_Vent_Louver, CMP_Drain_Pipe, CMP_Wall_Lamp, CMP_Meter_Box, CMP_Solar_Panel (1.6 x 1.0 m). Extended kit (12 more, in `Hangar.blend`): CMP_Hazard_Post, CMP_Hazard_Sticker, CMP_Sign_Plaque, CMP_Windsock, CMP_Utility_Cabinet, CMP_Pipe_Elbow, CMP_Ground_Box, CMP_Roller_Door, CMP_Skylight_Curved, CMP_Grass_Tuft, CMP_Personnel_Door, CMP_Dino_Footprint. Kit parts are details and upgrades; they must never define a building's identity. Name sockets SOCKET_SolarPanel, SOCKET_ACUnit, SOCKET_MeterBox, SOCKET_WallLamp, SOCKET_Vent, SOCKET_Window.
Rules: wall parts face +Y with origin on the wall surface; rotate Z 0 back / 90 left / -90 right / 180 front. Solar panel origin on the roof surface. Use linked duplicates. No building should have a bare wall: give every side some windows, vents, AC, pipes or lamps from this kit before adding new one-off details.
