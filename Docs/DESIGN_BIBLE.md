# Dino Park Tycoon: Design Bible

Version 2.1 (4 Nov 2026). Lives in `Docs/` of the Unity project. Single source of truth for art, world rules and building identity. Read this before generating any concept, model or texture.

Companion docs: BUILDING_IDENTITY.md (per-building matrix), V1_PLAN.md (scope and schedule), V2_CHANGELOG.md (what changed).

## 1. Vision and pillars

Calm, care-first dinosaur park management for mobile. Core fantasy: "I cleared a wild island, raised living dinosaurs, and built a park people love."

| Pillar | Meaning |
|---|---|
| Calm care | Care is the game. No stress timers, no lost progress. |
| Readable needs | Every problem shows why it happened and how to fix it. |
| Creative ownership | Player layouts, names, decoration. |
| Fair progression | No loot boxes, paid power or forced ads. |
| Mobile clarity | Everything readable at phone scale. |

## 2. The one rule

> Same park. Same palette. Different architecture.

Shared visual DNA (palette, materials, kit parts) makes buildings feel like one park. Silhouette, roofline, footprint, primary material, hero feature, props and mood make each building different.

## 3. Art direction

Stylized semi-realistic, hand-painted, low-poly-friendly. Warm, natural, friendly, believable. Not cartoon, not horror.

- Soft brush-painted surfaces, light edge wear.
- Simple readable silhouettes, large shapes, no tiny clutter.
- Slightly rounded and chamfered edges.
- Matte everywhere except glass and water.
- Thin dark outline only where it helps readability.
- Everything must read from the default isometric camera (front-left, about 35 degrees above ground).

## 4. Shared palette

| Element | Direction |
|---|---|
| Concrete | Warm cream #F4EDD8 |
| Timber | Honey-orange vertical slats #C79A63 |
| Glass | Teal tinted #8FCBCB |
| Steel | Charcoal-green painted #3B4743 |
| Lamps, trim | Amber glow #FFAA33, brass gold #F2B84B |
| Greenery | Soft green roofs, planting, stripes #5E9B4A |
| Solar | Dark blue |
| Pipes, controls | Grey with clamps |
| Hazard | Small yellow-and-black marks |

Palette is a language, not permission to make every building identical.

## 5. Terrain rules

- Modular tiles, snap edge to edge, same footprint and thickness.
- Flat clean tops, clean vertical sides.
- No baked cast shadows, no props standing on tiles.
- Natural earthy colors, simple painted variation.

Starter tiles: short green grass; lush grass with clover; dry tan grass; bare dirt with pebbles; grey rocky ground; wet mud with puddles.

## 6. Plant rules

Simplified leaf masses, few large clusters, clear silhouettes, natural greens with warm accents, growth stages at true relative size, no ground or pots on asset sheets. Conifer set: young slim, mature full, tall old with bare lower trunk (monkey-puzzle / podocarp feel, kept simple).

## 7. Animal rules

Semi-realistic, scientifically plausible, painterly, friendly. Never cute-cartoon, never movie-monster. Natural colors plus one bold display color. Simple scale or feather pattern. Matte.

Every animal sheet needs: clear head, neck, body, limbs, tail, feet, claws; neutral standing pose; clean three-quarter side view; full body nose to tail; separable head or parts where useful.

## 8. Scale and grid standards

- Grid: 1 cell = 2.0 m. Roads 4.0 m (2 cells). Doors 2.2 to 2.4 m high. Model pivots at base centre, flat bottom, no baked shadows.
- Building footprints align to the game tile grid.
- Never neon, never bright red or blue roofs.
- Park-standard solar panel: 1.6 x 1.0 m, 12 degree tilt. Use the same size on every building so building size reads clearly.
- Kit parts keep fixed real-world sizes (see BUILDING_IDENTITY.md section 6).
- Blender conventions: wall parts face +Y with origin on wall surface; roof parts use local Z as roof normal; place kit parts as linked duplicates.

## 9. Ocean and map

One island, ocean border, bounded pan camera, pinch zoom limited between close-building and full-island views, off-screen alert indicators at map edge. Ocean is visual and a boundary only in V1.

## 10. Asset checklist (every building)

1. Identity block filled in (BUILDING_IDENTITY.md section 3).
2. Black silhouette test passed at about 64 px.
3. Rooflines and primary material not shared with another important building.
4. One hero feature visible from default camera.
5. Back and side logical, simpler is fine.
6. Kit parts on every side, no bare walls.
7. Blank signs, no text, letters, numbers or logos.
8. Triangle budget noted and sockets named.
