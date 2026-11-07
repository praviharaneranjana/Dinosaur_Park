## 3D modelling workflow (Blender skills pack, 94 skills)

Skills live in `.claude/skills/` (source: github.com/arjun988/blender-skills, MIT).

When making ANY 3D model (building, terrain, plant, prop, vehicle, animal, person):

1. Read `blender-director` first and let it route to specialist skills. Index: `SKILLS_GUIDE.md`.
2. If a reference image exists, read `.claude/skills/references/reference-image-match.md` and finish the Reference Analysis before touching Blender.
3. Typical routing for Dino Park Tycoon:
   - Buildings: `environment-artist`, `hard-surface`, `archviz`, `prop-artist`
   - Terrain / plants: `environment-artist`, `vegetation-artist`, `biome-worlds`
   - Animals: `creature-artist`, `rigging`, `animation`
   - Vehicles: `vehicle-artist`
   - Look: `hand-painted-style`, `stylized-style`, `lowpoly-style`, `isometric-style`
   - Finish: `materials`, `uv-workflow`, `texture-workflow`, `lod-pipeline`, `collision-proxy`, `asset-optimization`, `unity-export`, `qa-review`
4. Drive Blender through the Blender MCP, not manual UI steps.
5. Run `qa-review` and `references/validation-checklist.md` before any export.

Precedence: where a skill disagrees with this project's own docs, the project wins.
Project docs = DESIGN_BIBLE.md, BUILDING_IDENTITY.md, BUILD_ORDER.md, V1_PLAN.md, building-component-kit.md
(scale, naming, tri budgets, export settings, kit parts linked not copied, blank signs only, palette).
