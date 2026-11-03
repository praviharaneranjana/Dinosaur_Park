# Dino Park Tycoon: design decisions

Solo developer working with AI, 3-4 hours a day. Unity + Blender, models via Tripo (image-to-3D). Reference images are made in Gemini, then meshes are built in Blender.

## Scope (decided 2 Nov 2026)
Everything below is **V1**, the big-shot launch, not a "full game" later. He may cut things depending on development and time.

## Vision
- 3D dinosaur park tycoon, Clash of Clans-style camera. Mobile take on Jurassic Park-style management.
- Start with one animal in one enclosure. The player clears mountains, builds landing strips and water fountains.
- Dinosaurs differ in diet and danger. Gentle plant-eaters (e.g. long-neck sauropod) can be seen from safari vehicles without cages. Dangerous ones need stronger enclosures.
- Animals get hungry, need water, get sick, and go to a hospital for a day or two of healing.
- Genetics mini-game: pick pre-prepared parts, build and name your own dinosaur, keep it in a library.
- Water and flying animals too (sea park and sky animals are in V1).
- Endless play, no ending. Predator/plant hybrids in the lab at a stability cost.
- Random incidents answered by dispatching rescue/vet teams by vehicle or helicopter.
- Care depth is the goal: compete with Jurassic World: The Game on care depth, not dino count.
- First build: "Triceratops Valley".

## Monetization
Mainly ads (rewarded first), plus small extras. Remove-ads price: $4.99.

## Art
Style follows the Gemini isometric reference images (stylized isometric park assets). Palette and scale are in `AGENTS.md`.

## Still to build
Animals, roads, vehicles incl. helicopters (some buildings have helipads), labs, dino medical systems, waterfalls, tanks, trees/plants/flowers/grass.
