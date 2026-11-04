---
name: dino-park-building-identity
description: Designs unique, instantly readable buildings for Dino Park Tycoon using the tiered identity rules, kit parts and Gemini prompt template. Use when concepting, prompting, reviewing or modelling any park building.
---

# Dino Park Tycoon: Building Identity

Same park, same palette, different architecture. A player should know the building's job from its silhouette.

## Steps
1. Fill the identity block: Function; Player reads it as; Dominant silhouette; Footprint; Roofline; Primary material; Secondary material; Hero feature; 2 to 4 functional props; Mood.
2. Decide the tier.
   - Tier A landmarks (entrance, admin, VIP, hospital, research, hatchery, power, depot, genetics): unique roofline AND primary material AND silhouette.
   - Tier B small services (shop, kiosk, cafe, restroom, pump, viewing deck, bus stop): unique silhouette AND roofline. Cream concrete is a shared plinth, not a primary material (except admin).
3. Check the matrix below for clashes.
4. Build the Gemini prompt: park prompt template + identity block. Building shell only; wall add-ons drawn simply and separate; back and right side plain but logical; blank signs.
5. Silhouette test: black fill, 64 px wide, 3 testers x 3 seconds, pass at 2 of 3. Compare Tier A set side by side.
6. Model the shell, add named sockets, then place kit parts on every side (no bare walls).

## Matrix (roofline / primary material)
Entrance: tall arch / charcoal steel + cream piers. Admin: stepped flat + tower / cream concrete. VIP: wave garden roof / teal curved glass. Hospital: flat with helipad ring, L-shape / pale sage panels. Research: sawtooth / glass and grey steel. Hatchery: low soft dome / amber-cream plaster. Power: stacks and tanks / charcoal steel. Depot (hangar, built): barrel vault R=5 m / cream base, green ribs. Genetics: tall tower, glass crown / glass and steel.
Tier B: Souvenir shop (built): awning + green roof / honey timber. Kiosk: cone / pastel panels. Cafe: big canopy / steel frame. Restroom: mono-pitch / cream concrete. Pump: tank roof / charcoal steel. Viewing deck: open rail / timber. Bus stop: curved canopy / steel and timber.

## Kit parts (details and upgrades only)
Original: Window 0.8x1.0, AC unit 0.78x0.58x0.36, Vent louvre 0.5x0.3, Drain pipe 2.8 m, Wall lamp, Meter box 0.4x0.55x0.14, Solar panel 1.6x1.0 (12 deg).
Hangar set: Hazard post, Hazard sticker, Sign plaque, Windsock, Utility cabinet, Pipe elbow, Ground box, Roller door, Curved skylight, Grass tuft, Personnel door, Dino footprint.
Wall rotation Z: back 0, left 90, right -90, front 180. Sockets: SOCKET_SolarPanel, SOCKET_ACUnit, SOCKET_MeterBox, SOCKET_WallLamp, SOCKET_Vent, SOCKET_Window.

Full details: BUILDING_IDENTITY.md and DESIGN_BIBLE.md.

## Studio framework hooks
- Run the silhouette and tier check with `art-director` before any model work; `technical-artist` signs off the triangle budget and sockets.
- Use `/asset-spec` for the per-building spec and `/design-system` for building gameplay roles (power, comfort, safety). Keep identity rules in `Docs/BUILDING_IDENTITY.md`.
- Hand finished shells to `unity-specialist` for prefab setup (pivot at base centre, Assets/Models, data in ScriptableObjects).
