# AI Agent Directives: Dino Park Tycoon (mobile)

Unity 6 (6000.6.7f1), URP 17.6. Target: Android first. Solo developer, so keep tasks small and end each task with "How to test".

## Game in one paragraph
Dinosaur park tycoon. Clash of Clans-style tilted camera (drag to pan, pinch to zoom, clamped to the map). Mountains border the map. Player clears trees/rocks by selecting an area, builds on a grid (1 cell = 2 m): cages, hatchery/lab, roads, canteen. Dinosaurs unlock by level, guests walk the roads. Endless expansion, daily rewards. Money mainly from ads (rewarded ads first), plus small extras.

## Folders
- Assets/Models, Materials, Animations: imported art (buildings, enclosures, roads, props, characters, environment, 6 dinosaurs)
- Assets/Models/Vehicles/Cars: 7 low-poly cars (Quaternius, CC0). Use for park shuttles/parking and road traffic
- Assets/Models/Trains: Kenney train kit, 103 pieces (tracks, locomotives, carriages, trams). Use for a park train ride
- Assets/Models/Town: Downtown City MegaKit free version (modular buildings, streets, sidewalks, props). FBX in Town/FBX, textures in Town/Textures
- Assets/Concepts: approved concept images and their prompts
- Assets/Scripts: reusable scripts from the old prototype (bird system, wind sway, pond, visitor AI, dinosaur habit AI, doors)
- Assets/Plugins/CW: Lean Touch (touch camera). NaughtyAttributes and Colorful Hierarchy are installed too
- .agents/rules and .agents/skills: domain rules and skills (touch, UI, ads/IAP, audio, FBX, performance, logcat, notifications)
- _Reference: old editor scripts, Blender generation scripts and the old AGENTS file. Not compiled, read-only reference

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
Components: CMP_Window, CMP_AC_Unit, CMP_Vent_Louver, CMP_Drain_Pipe, CMP_Wall_Lamp, CMP_Meter_Box, CMP_Solar_Panel (1.6 x 1.0 m).
Rules: wall parts face +Y with origin on the wall surface; rotate Z 0 back / 90 left / -90 right / 180 front. Solar panel origin on the roof surface. Use linked duplicates. No building should have a bare wall: give every side some windows, vents, AC, pipes or lamps from this kit before adding new one-off details.
