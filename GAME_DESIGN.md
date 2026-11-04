# Dino Park Tycoon: design decisions

Solo developer working with AI, 3-4 hours a day. Unity + Blender, models via Tripo (image-to-3D). Reference images are made in Gemini, then meshes are built in Blender.

## Scope
**Revised 4 Nov 2026 (supersedes the 2 Nov "everything is V1" decision).** V1 is a friends-and-family playable test build: one island with an ocean border, nine species (6 land herbivores, T. rex as the only predator, Pteranodon in an aviary, Mosasaurus in a tank), babies for Triceratops/Stegosaurus/Brachiosaurus, one random event (T. rex fence stress), optional rewarded ads plus one remove-ads purchase. Everything else in the Vision list below is the roadmap, not V1.
Full plan: `Docs/V1_PLAN.md`. Art and building rules: `Docs/DESIGN_BIBLE.md`, `Docs/BUILDING_IDENTITY.md`. What changed and why: `Docs/V2_CHANGELOG.md`.

Original 2 Nov scope (kept for history): everything discussed was V1, the big-shot launch, and he may cut things depending on development and time.

## Vision (roadmap; V1 subset is in Scope above)
- 3D dinosaur park tycoon, Clash of Clans-style camera. Mobile take on Jurassic Park-style management.
- Start with one animal in one enclosure. The player clears mountains, builds landing strips and water fountains.
- Dinosaurs differ in diet and danger. Gentle plant-eaters (e.g. long-neck sauropod) can be seen from safari vehicles without cages. Dangerous ones need stronger enclosures.
- Animals get hungry, need water, get sick, and go to a hospital for a day or two of healing.
- Genetics mini-game: pick pre-prepared parts, build and name your own dinosaur, keep it in a library.
- Water and flying animals too (sea park and sky animals are in V1).
- Endless play, no ending. Predator/plant hybrids in the lab at a stability cost.
- Random incidents answered by dispatching rescue/vet teams by vehicle or helicopter.
- Care depth is the goal: compete with Jurassic World: The Game on care depth, not dino count.
- First build: the V1 island test, with the Triceratops core loop first (Triceratops Valley is the first playable milestone).

## Process
Studio framework installed 4 Nov 2026 (Claude Code Game Studios, `.claude/`, config in `project.yaml`). Stage starts at Concept in the framework; existing `Docs/` already covers art bible, building identity and V1 plan, so adopt them with `/adopt` and skip `/art-bible`. System GDDs go in `design/gdd/`. Decision log stays here; update it when a decision changes.

## Monetization
Mainly ads (rewarded first), plus small extras. Remove-ads price: $4.99.

## Art
Style follows the Gemini isometric reference images. Rule: same park, same palette, different architecture. Palette and scale: `AGENTS.md` and `Docs/DESIGN_BIBLE.md`. Per-building identity (tiers, rooflines, materials): `Docs/BUILDING_IDENTITY.md`.

## Still to build
Animals, roads, vehicles incl. helicopters (some buildings have helipads), labs, dino medical systems, waterfalls, tanks, trees/plants/flowers/grass.

## Camera (decided 4 Nov 2026)
Tilted perspective camera (pitch 50, FOV 30), drag to pan, pinch to zoom, mouse wheel in the editor. The view is locked to the island plus an ocean margin (default 16 m): the screen can never show past the playable area, and fully zoomed out the whole island plus margin fits on screen. Island size is a placeholder (160 x 160 m = 80 x 80 cells) until the Blender island exists. Camera yaw is 0 so the grid is screen-aligned; a 45 degree diamond view would need rotated bounds and is not built.
