# Dino Park Tycoon: Gemini Prompt Updates (4 Nov 2026)

Revised prompts for four buildings. These replace the matching entries in `GEMINI_PROMPTS.md`. Each building has two prompts:
- **Full prompt**: paste into a new Gemini chat to regenerate from scratch.
- **Edit prompt**: attach your existing image, then paste. Use this first, it keeps what you liked.

Notes:
- The helipad letter H is the only lettering allowed (a painted marking). Signs stay blank.
- Suggested footprints changed: Hotel 6x4, VIP lodge 6x4, Mosasaurus tank 12x12, Hospital 7x5 (1 cell = 2 m). The tank is now about 24 m across, which suits a giant Mosasaurus but is a big chunk of the island. Tell me if you want it smaller.
- Hotel and VIP lodge no longer have roof planting. If you want greenery back later, add it as a separate upgrade item.
- Silhouette check: hotel is stepped, VIP is a wave roof, hospital is flat L-shape with helipad, tank is round. They should still read differently.

## 1. Luxury hotel

Suggested footprint: 6 x 4 cells (taller, 4 storeys plus rooftop).

### Full prompt

```text
Stylized semi-realistic hand-painted game asset for a mobile dinosaur park management game.

A painterly digital illustration of a low-poly 3D model: soft brush-painted surfaces, light wear and dirt in edges and corners, thin dark outline, slightly rounded and chamfered edges, clean readable silhouette, big simple shapes, no tiny clutter.

Camera: one three-quarter isometric view from the front-left, about 35 degrees above the ground. The whole object is centred, fully visible, and fully inside the frame with empty space around it. Nothing cropped.

Background: plain flat light-grey studio background, about #C8C9CC. No scenery, no ground texture, no horizon, no trees. Only a soft contact shadow directly under the object.

Lighting: soft daylight from the upper left, matte materials, no strong reflections, no glow except lamps.

Shared park visual language:
- Modern friendly eco-research dinosaur park.
- Warm cream concrete (#F4EDD8) with rounded corners.
- Honey-orange timber slats (#C79A63) used as an accent unless stated as the main material.
- Teal tinted glass (#8FCBCB).
- Charcoal-green painted steel frames (#3B4743).
- Amber lamps and trim lines (#FFAA33).
- Soft green roof or planting accents (#5E9B4A) only where stated.
- Dark-blue solar panels only where appropriate.
- Dinosaur footprint engravings on one key concrete surface.
- Blank cream signs, screens and plaques: no text, letters, numbers, logos or watermarks.
- Never neon, never bright red or bright blue roofs.

CRITICAL: This building must have a unique, instantly readable identity. Do not make it look like a generic park office, shop, laboratory or VIP building. Its silhouette, roofline, footprint, main material and hero feature must clearly communicate its function from a distance.

UNIQUE BUILDING IDENTITY:
Function: Luxury overnight guest hotel with a rooftop pool, lounge and helipad.
Player reads it as: A five-star resort hotel inside the dinosaur park.
Dominant silhouette: Tall terraced stepped building, wide at the bottom and getting smaller toward the top, with a long balcony on every floor and a small tower on top.
Footprint: Wide rectangle with a heavy cream concrete ground floor.
Roofline: Stepped terraces. Keep the existing stepped terrace roof design but remove all bushes, trees and planting from the terraces: clean cream concrete terrace floors only. The upper terrace holds a rooftop swimming pool and chill area. The very top tower roof is a helipad.
Primary material: Cream concrete with deep horizontal slab lines.
Secondary material: Honey timber balcony fronts, teal glass sliding doors, charcoal-green steel balcony rails.
Hero feature: A rooftop infinity pool with teal-blue water on the upper terrace, surrounded by sun loungers, umbrellas and a small timber lounge bar, with a round helipad with a large painted letter H on the tower roof above it.
Functional props: Wide balconies on every floor with railings, a grand canopy entrance with a luggage cart, a heavy cream concrete base with a projecting outer slab edge and a thick amber trim line around the ground floor, rooftop sun loungers and parasols, a small solar panel group, a blank cream sign above the entrance.
Mood: Luxurious, relaxed, premium, welcoming.
Exception to the no-letters rule: the helipad shows one painted letter H inside its circle, and nothing else has any letters.

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons (wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels) simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

### Edit prompt (attach the image)

```text
Edit this image. Keep the same style, camera, grey background and the stepped terrace building shape. Make these changes:
1. Make it a luxury resort hotel: one more storey, longer balconies on every floor.
2. Remove all bushes, trees and planting from the terraces. Leave clean cream concrete terrace floors.
3. Thicker, heavier cream concrete ground floor with a projecting outer slab edge and a thick amber trim line around it.
4. On the upper terrace add a rooftop infinity swimming pool with teal-blue water, sun loungers, umbrellas and a small timber lounge bar (a chill area).
5. On the very top tower roof add a round helipad with a large painted letter H inside the circle.
Keep signs blank. Do not change camera, background or lighting.
```

## 2. VIP lodge

Suggested footprint: 6 x 4 cells (two storeys).

### Full prompt

```text
Stylized semi-realistic hand-painted game asset for a mobile dinosaur park management game.

A painterly digital illustration of a low-poly 3D model: soft brush-painted surfaces, light wear and dirt in edges and corners, thin dark outline, slightly rounded and chamfered edges, clean readable silhouette, big simple shapes, no tiny clutter.

Camera: one three-quarter isometric view from the front-left, about 35 degrees above the ground. The whole object is centred, fully visible, and fully inside the frame with empty space around it. Nothing cropped.

Background: plain flat light-grey studio background, about #C8C9CC. No scenery, no ground texture, no horizon, no trees. Only a soft contact shadow directly under the object.

Lighting: soft daylight from the upper left, matte materials, no strong reflections, no glow except lamps.

Shared park visual language:
- Modern friendly eco-research dinosaur park.
- Warm cream concrete (#F4EDD8) with rounded corners.
- Honey-orange timber slats (#C79A63) used as an accent unless stated as the main material.
- Teal tinted glass (#8FCBCB).
- Charcoal-green painted steel frames (#3B4743).
- Amber lamps and trim lines (#FFAA33).
- Soft green roof or planting accents (#5E9B4A) only where stated.
- Dark-blue solar panels only where appropriate.
- Dinosaur footprint engravings on one key concrete surface.
- Blank cream signs, screens and plaques: no text, letters, numbers, logos or watermarks.
- Never neon, never bright red or bright blue roofs.

CRITICAL: This building must have a unique, instantly readable identity. Do not make it look like a generic park office, shop, laboratory or VIP building. Its silhouette, roofline, footprint, main material and hero feature must clearly communicate its function from a distance.

UNIQUE BUILDING IDENTITY:
Function: Premium two-storey lodge for VIP visitors.
Player reads it as: An elegant, luxurious two-storey glass lodge for important guests.
Dominant silhouette: Wide, horizontally curved two-storey building with a sweeping glass upper floor sitting on a solid ground floor.
Footprint: Wide and shallow with a curved front wall.
Roofline: Keep the same gently curved wave-like roof as the single-storey version, now sitting on top of the second storey. Remove all bushes, trees and planting from the roof: the roof is a clean cream concrete slab with a thin charcoal-green edge and a honey timber underside.
Primary material: Teal curved glass. The entire second storey is curved glass.
Secondary material: Cream concrete ground floor, honey timber vertical slats under the roof edge, charcoal-green steel frames.
Hero feature: A fully glass curved second-storey lounge under the wave roof, above a deep timber canopy entrance on the ground floor.
Functional props: Covered entrance with a carpet strip, a curved outdoor stair or ramp up to a second-floor terrace, two large ground planters, warm amber under-canopy lights, a blank cream sign, one AC unit and drain pipe on the side wall.
Mood: Calm, premium, elegant, welcoming.

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons (wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels) simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

### Edit prompt (attach the image)

```text
Edit this image. Keep the same style, camera, grey background and the same curved wave roof shape. Make these changes:
1. Make the building two storeys: solid cream concrete ground floor with the timber entrance canopy and glass entrance, and a second storey made entirely of curved teal glass.
2. Move the wave roof on top of the second storey.
3. Remove all bushes, trees and planting from the roof. Leave a clean cream concrete roof slab.
4. Keep the footprint sign pillar, the amber lights and the blank sign.
Do not change camera, background or lighting.
```

## 3. Mosasaurus tank (huge)

Suggested footprint: 12 x 12 cells (about 24 m across).

### Full prompt

```text
Stylized semi-realistic hand-painted game asset for a mobile dinosaur park management game.

A painterly digital illustration of a low-poly 3D model: soft brush-painted surfaces, light wear and dirt in edges and corners, thin dark outline, slightly rounded and chamfered edges, clean readable silhouette, big simple shapes, no tiny clutter.

Camera: one three-quarter isometric view from the front-left, about 35 degrees above the ground. The whole object is centred, fully visible, and fully inside the frame with empty space around it. Nothing cropped.

Background: plain flat light-grey studio background, about #C8C9CC. No scenery, no ground texture, no horizon, no trees. Only a soft contact shadow directly under the object.

Lighting: soft daylight from the upper left, matte materials, no strong reflections, no glow except lamps.

Shared park visual language:
- Modern friendly eco-research dinosaur park.
- Warm cream concrete (#F4EDD8) with rounded corners.
- Honey-orange timber slats (#C79A63) used as an accent unless stated as the main material.
- Teal tinted glass (#8FCBCB).
- Charcoal-green painted steel frames (#3B4743).
- Amber lamps and trim lines (#FFAA33).
- Soft green roof or planting accents (#5E9B4A) only where stated.
- Dark-blue solar panels only where appropriate.
- Dinosaur footprint engravings on one key concrete surface.
- Blank cream signs, screens and plaques: no text, letters, numbers, logos or watermarks.
- Never neon, never bright red or bright blue roofs.

CRITICAL: This building must have a unique, instantly readable identity. Do not make it look like a generic park office, shop, laboratory or VIP building. Its silhouette, roofline, footprint, main material and hero feature must clearly communicate its function from a distance.

UNIQUE BUILDING IDENTITY:
Function: Huge deep-water enclosure and viewing complex for a giant Mosasaurus.
Player reads it as: A massive aquarium big enough for a sea monster, with people tiny beside it.
Dominant silhouette: Very large, very wide round tank with a tall curved wall, much taller and much wider than the entrance, with a visible tiered viewing structure around it.
Footprint: Round, very large. The tank wall is about 4 times taller than the entrance door, and the whole tank is more than 20 times wider than the door, so the scale is obvious next to the small human-sized entrance.
Roofline: Open water on top surrounded by a wide two-level viewing walkway with railings. No solid roof over the water.
Primary material: Thick curved teal glass tank wall with large rounded viewing portals.
Secondary material: Cream concrete buttresses, honey timber viewing platforms, charcoal-green steel rails and frames.
Hero feature: A row of very large curved glass viewing portals in the tank wall, with two tiers of timber viewing platforms and a tall glass viewing tunnel entrance, so visitors can look into deep water.
Functional props: A small human-sized entrance door and stairs beside the tank to show scale, large pump and pipe housing, safety railings, a blank cream sign board, amber lamps on the buttresses, a small solar panel group on the lower roof.
Mood: Awe-inspiring, powerful, calm.

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons (wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels) simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

### Edit prompt (attach the image)

```text
Edit this image. Keep the same style, camera, grey background and round tank idea. Make these changes:
1. Make the whole tank MUCH bigger: about 4 times taller wall and more than 20 times wider than the small entrance door, so the entrance door looks tiny beside it.
2. Add a row of very large curved glass viewing portals and two tiers of timber viewing platforms with railings around the tank.
3. Add a tall glass viewing tunnel entrance and stairs up to the platforms.
4. Keep the big pump and pipe housing, the blank sign, and the amber lamps.
Do not change camera, background or lighting.
```

## 4. Hospital (large, two-storey)

Suggested footprint: 7 x 5 cells (two storeys).

### Full prompt

```text
Stylized semi-realistic hand-painted game asset for a mobile dinosaur park management game.

A painterly digital illustration of a low-poly 3D model: soft brush-painted surfaces, light wear and dirt in edges and corners, thin dark outline, slightly rounded and chamfered edges, clean readable silhouette, big simple shapes, no tiny clutter.

Camera: one three-quarter isometric view from the front-left, about 35 degrees above the ground. The whole object is centred, fully visible, and fully inside the frame with empty space around it. Nothing cropped.

Background: plain flat light-grey studio background, about #C8C9CC. No scenery, no ground texture, no horizon, no trees. Only a soft contact shadow directly under the object.

Lighting: soft daylight from the upper left, matte materials, no strong reflections, no glow except lamps.

Shared park visual language:
- Modern friendly eco-research dinosaur park.
- Warm cream concrete (#F4EDD8) with rounded corners.
- Honey-orange timber slats (#C79A63) used as an accent unless stated as the main material.
- Teal tinted glass (#8FCBCB).
- Charcoal-green painted steel frames (#3B4743).
- Amber lamps and trim lines (#FFAA33).
- Soft green roof or planting accents (#5E9B4A) only where stated.
- Dark-blue solar panels only where appropriate.
- Dinosaur footprint engravings on one key concrete surface.
- Blank cream signs, screens and plaques: no text, letters, numbers, logos or watermarks.
- Never neon, never bright red or bright blue roofs.

CRITICAL: This building must have a unique, instantly readable identity. Do not make it look like a generic park office, shop, laboratory or VIP building. Its silhouette, roofline, footprint, main material and hero feature must clearly communicate its function from a distance.

UNIQUE BUILDING IDENTITY:
Function: Large animal hospital and treatment centre.
Player reads it as: A big, serious hospital where even giant dinosaurs get healed.
Dominant silhouette: Large two-storey L-shaped medical block with a tall wide covered ambulance bay on one wing.
Footprint: L-shaped, much larger than a normal building.
Roofline: Flat roof with a large round helipad marking on one wing. The helipad shows a big painted letter H inside the circle.
Primary material: Pale sage-green panels over a cream concrete base.
Secondary material: Teal glass, charcoal-green frames, small amber trim lines.
Hero feature: A tall wide ambulance bay with a large treatment entrance on the ground floor, and a clear helipad with the letter H on the roof.
Functional props: Stretcher trolley, wide sliding door, large blank cream sign with a blank cross-shaped plaque, rooftop vent unit, small oxygen-tank rack, a second-floor row of windows with a covered walkway.
Mood: Calm, clean, medical, reassuring.
Exception to the no-letters rule: the helipad shows one painted letter H inside its circle, and nothing else has any letters.

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons (wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels) simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

### Edit prompt (attach the image)

```text
Edit this image. Keep the same style, camera, grey background, sage-green panels and the L-shape. Make these changes:
1. Make the hospital much bigger and two storeys tall, with a second row of windows.
2. Keep the wide covered ambulance bay on the ground floor, but make it taller and wider for big animals.
3. Add the letter H, large and clear, painted in the middle of the round helipad circle on the roof.
4. Keep the blank cross sign, AC unit and solar panels.
Do not change camera, background or lighting.
```
