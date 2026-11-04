---
name: dino-park-art-bible
description: Art rules for Dino Park Tycoon (stylized hand-painted low-poly mobile game). Use when creating or reviewing any concept, prompt, terrain tile, plant, animal sheet or 3D asset for the game.
---

# Dino Park Tycoon: Art Bible

Rule of the park: **Same park. Same palette. Different architecture.**

## Style
Stylized semi-realistic, hand-painted, low-poly-friendly. Warm, natural, friendly, believable. Not cartoon, not horror. Soft brush surfaces, rounded/chamfered edges, large simple shapes, no tiny clutter, matte except glass and water, thin dark outline only where it helps. Must read from the default isometric camera (front-left, ~35 degrees above ground).

## Palette
Cream concrete; honey-orange timber slats; teal glass; charcoal-green steel; amber lamps/trim; soft green roofs; dark-blue solar; grey pipes with clamps; small yellow-black hazard marks.

## Terrain
Modular tiles, same footprint and thickness, flat tops, clean sides, no baked shadows, no props on tiles. Starter set: short grass, lush clover grass, dry tan grass, dirt with pebbles, rocky ground, wet mud.

## Plants
Simplified leaf masses, few large clusters, clear silhouette, true relative growth stages, no ground or pots on asset sheets.

## Animals
Semi-realistic, scientifically plausible, painterly, friendly. Never cute-cartoon or movie-monster. Natural colors plus one bold display color. Sheet needs: full body nose to tail, neutral standing pose, clean three-quarter side view, clear head/neck/body/limbs/tail/feet/claws, separable parts where useful.

## Scale
Building footprints on the tile grid. Solar panel is always 1.6 x 1.0 m, 12 degree tilt. Wall kit parts face +Y with origin on wall; roof parts use local Z as normal; linked duplicates.

## Never
Text, letters, numbers or logos on signs (blank cream plaques only); copyrighted characters; strong reflections.

## Workflow
1. Check the idea against this file. 2. For buildings, also load dino-park-building-identity. 3. Concept in Gemini, then silhouette test, then Blender, then export.

## Studio framework hooks
- Source of truth is `Docs/DESIGN_BIBLE.md`. Do not run `/art-bible` to regenerate it; if asked, import this file instead.
- Reviews: ask `art-director` for style/silhouette review, `technical-artist` for triangle budget, textures and URP shader limits, `unity-shader-specialist` for shaders.
- Asset specs: `/asset-spec` for a new asset, `/asset-audit` before import. Log licenses in `ASSET_LICENSES.md`.
