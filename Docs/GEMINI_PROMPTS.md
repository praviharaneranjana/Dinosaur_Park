# Dino Park Tycoon: Gemini Building Prompts

Version 2.1 (4 Nov 2026). Each prompt below is complete and copy-paste ready. Paste the whole code block into Gemini, nothing else.

## How to use

1. Copy one full code block (it includes the shared park style plus that building's unique identity).
2. Generate. If the result looks like a generic cream box, add: `Make the silhouette and roofline much more distinct. Keep the hero feature large.`
3. Run the silhouette test: fill the image black, shrink to about 64 px wide, ask three people what it is. Pass = 2 of 3.
4. Compare Tier A buildings side by side. If two look alike, regenerate one.
5. Save approved images and the prompt together in `Assets/Concepts/<BuildingName>/`.

Tier A = landmark (unique roofline, material and silhouette). Tier B = small service (unique silhouette and roofline). Footprints are suggested sizes in grid cells (1 cell = 2 m).

Already built in Blender, so no prompt needed: Souvenir shop (honey timber, awning) and Hangar/vehicle depot (barrel vault). Keep new buildings visually different from both.

## Index

1. Entrance gate and ticket booths (Tier A, 6 x 2 cells)
2. Administration building (Tier A, 4 x 3 cells)
3. VIP lounge (Tier A, 5 x 3 cells)
4. Hospital / vet station (Tier A, 5 x 4 cells)
5. Research center (Tier A, 5 x 4 cells)
6. Hatchery (Tier A, 4 x 4 cells)
7. Power station (Tier A, 4 x 4 cells)
8. Genetics lab (post-V1) (Tier A, 3 x 3 cells)
9. Hotel (post-V1) (Tier A, 5 x 3 cells)
10. Ice-cream kiosk (Tier B, 1 x 1 cell)
11. Cafe (Tier B, 3 x 3 cells)
12. Restroom (Tier B, 2 x 1 cells)
13. Water pump (Tier B, 2 x 2 cells)
14. Viewing deck (Tier B, 3 x 2 cells)
15. Bus stop (Tier B, 2 x 1 cells)
16. Mosasaurus tank (Tier A, 6 x 6 cells)
17. Pteranodon aviary (Tier A, 5 x 5 cells)

## 1. Entrance gate and ticket booths

Tier A. Suggested footprint: 6 x 2 cells.

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
- Soft green roof or planting accents (#5E9B4A).
- Dark-blue solar panels only where appropriate.
- Dinosaur footprint engravings on one key concrete surface.
- Blank cream signs, screens and plaques: no text, letters, numbers, logos or watermarks.
- Never neon, never bright red or bright blue roofs.

CRITICAL: This building must have a unique, instantly readable identity. Do not make it look like a generic park office, shop, laboratory or VIP building. Its silhouette, roofline, footprint, main material and hero feature must clearly communicate its function from a distance.

UNIQUE BUILDING IDENTITY:
Function: Park entrance, ticket booths and visitor arrival.
Player reads it as: The grand gateway to a living dinosaur park.
Dominant silhouette: Wide landmark gateway: a tall central arch flanked by two small ticket booths.
Footprint: Wide and shallow, symmetrical.
Roofline: Tall open arch canopy spanning the entrance, low flat roofs on the booths.
Primary material: Charcoal-green painted steel arch with warm cream concrete piers.
Secondary material: Honey timber slat panels on the booths, teal glass ticket windows.
Hero feature: A tall steel arch with a large blank rounded park sign and a dinosaur footprint engraved in one pier.
Functional props: Two ticket booths with serving windows, turnstile gates, amber lamps on the piers, planters.
Mood: Welcoming, grand, friendly.

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons (wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels) simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

## 2. Administration building

Tier A. Suggested footprint: 4 x 3 cells.

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
- Soft green roof or planting accents (#5E9B4A).
- Dark-blue solar panels only where appropriate.
- Dinosaur footprint engravings on one key concrete surface.
- Blank cream signs, screens and plaques: no text, letters, numbers, logos or watermarks.
- Never neon, never bright red or bright blue roofs.

CRITICAL: This building must have a unique, instantly readable identity. Do not make it look like a generic park office, shop, laboratory or VIP building. Its silhouette, roofline, footprint, main material and hero feature must clearly communicate its function from a distance.

UNIQUE BUILDING IDENTITY:
Function: Park administration and staff management.
Player reads it as: The organised headquarters of the dinosaur park.
Dominant silhouette: Tall upright two-storey rectangular block with a clean vertical entrance tower.
Footprint: Rectangular, compact, slightly taller than wide.
Roofline: Stepped flat roof with a raised entrance tower and a slim flagpole.
Primary material: Warm cream concrete.
Secondary material: Charcoal-green steel window frames and honey timber slats on the upper floor.
Hero feature: A tall central entrance tower with a blank rounded park sign and a slim flagpole.
Functional props: Wall-mounted blank schedule board, service door, roof ventilation unit, small staff entrance.
Mood: Organised, professional, welcoming.

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons (wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels) simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

## 3. VIP lounge

Tier A. Suggested footprint: 5 x 3 cells.

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
- Soft green roof or planting accents (#5E9B4A).
- Dark-blue solar panels only where appropriate.
- Dinosaur footprint engravings on one key concrete surface.
- Blank cream signs, screens and plaques: no text, letters, numbers, logos or watermarks.
- Never neon, never bright red or bright blue roofs.

CRITICAL: This building must have a unique, instantly readable identity. Do not make it look like a generic park office, shop, laboratory or VIP building. Its silhouette, roofline, footprint, main material and hero feature must clearly communicate its function from a distance.

UNIQUE BUILDING IDENTITY:
Function: Premium guest lounge for VIP visitors.
Player reads it as: A relaxed, luxurious place for important guests.
Dominant silhouette: Low, wide, horizontally curved building with a sweeping glass front.
Footprint: Wide and shallow, with a curved front wall.
Roofline: Gently curved wave-like roof with a planted roof garden.
Primary material: Teal curved glass.
Secondary material: Cream concrete base and honey timber vertical slats.
Hero feature: A large curved glass lounge wall beneath a deep timber canopy.
Functional props: Covered entrance, soft carpet strip, two large planters, warm amber under-canopy lights.
Mood: Calm, premium, welcoming.

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons (wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels) simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

## 4. Hospital / vet station

Tier A. Suggested footprint: 5 x 4 cells.

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
- Soft green roof or planting accents (#5E9B4A).
- Dark-blue solar panels only where appropriate.
- Dinosaur footprint engravings on one key concrete surface.
- Blank cream signs, screens and plaques: no text, letters, numbers, logos or watermarks.
- Never neon, never bright red or bright blue roofs.

CRITICAL: This building must have a unique, instantly readable identity. Do not make it look like a generic park office, shop, laboratory or VIP building. Its silhouette, roofline, footprint, main material and hero feature must clearly communicate its function from a distance.

UNIQUE BUILDING IDENTITY:
Function: Animal hospital and treatment centre.
Player reads it as: The place where sick dinosaurs get healed.
Dominant silhouette: Clean L-shaped medical block with a covered ambulance bay on one wing.
Footprint: L-shaped.
Roofline: Flat roof with a round helipad ring marking painted on one wing.
Primary material: Pale sage-green panels over a cream concrete base.
Secondary material: Teal glass, charcoal-green frames, small amber trim lines.
Hero feature: A large open ambulance bay with a wide treatment entrance and a blank rounded sign with a simple blank cross-shaped plaque.
Functional props: Stretcher trolley, wide sliding door, rooftop vent unit, small oxygen-tank rack.
Mood: Calm, clean, medical, reassuring.

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons (wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels) simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

## 5. Research center

Tier A. Suggested footprint: 5 x 4 cells.

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
- Soft green roof or planting accents (#5E9B4A).
- Dark-blue solar panels only where appropriate.
- Dinosaur footprint engravings on one key concrete surface.
- Blank cream signs, screens and plaques: no text, letters, numbers, logos or watermarks.
- Never neon, never bright red or bright blue roofs.

CRITICAL: This building must have a unique, instantly readable identity. Do not make it look like a generic park office, shop, laboratory or VIP building. Its silhouette, roofline, footprint, main material and hero feature must clearly communicate its function from a distance.

UNIQUE BUILDING IDENTITY:
Function: Science and research laboratory.
Player reads it as: A place of discovery and scientific work.
Dominant silhouette: Angular clustered lab volumes of different heights with a visible antenna.
Footprint: Clustered, irregular but tidy.
Roofline: Sawtooth roof with angled glazed north-lights.
Primary material: Glass and grey painted steel.
Secondary material: Cream concrete base, charcoal-green frames.
Hero feature: A tall slim antenna mast beside a small greenhouse-panel wing with angled glass.
Functional props: Roof antenna, exposed pipe run, greenhouse panels, sample crate, blank whiteboard panel.
Mood: Scientific, curious, modern.

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons (wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels) simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

## 6. Hatchery

Tier A. Suggested footprint: 4 x 4 cells.

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
- Soft green roof or planting accents (#5E9B4A).
- Dark-blue solar panels only where appropriate.
- Dinosaur footprint engravings on one key concrete surface.
- Blank cream signs, screens and plaques: no text, letters, numbers, logos or watermarks.
- Never neon, never bright red or bright blue roofs.

CRITICAL: This building must have a unique, instantly readable identity. Do not make it look like a generic park office, shop, laboratory or VIP building. Its silhouette, roofline, footprint, main material and hero feature must clearly communicate its function from a distance.

UNIQUE BUILDING IDENTITY:
Function: Egg incubation and baby dinosaur nursery.
Player reads it as: The warm, safe place where dinosaur eggs hatch.
Dominant silhouette: Low round building with a soft dome, like a nest.
Footprint: Round.
Roofline: Soft low dome with a small central skylight.
Primary material: Warm amber-cream plaster.
Secondary material: Teal glass egg room, honey timber door frame, charcoal-green steel ring at the base.
Hero feature: A glass-walled egg room with warm glowing nesting pods visible inside.
Functional props: Round nesting pods, warm amber lamps, small feeding trough, soft straw bedding mounds.
Mood: Warm, nurturing, gentle.

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons (wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels) simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

## 7. Power station

Tier A. Suggested footprint: 4 x 4 cells.

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
- Soft green roof or planting accents (#5E9B4A).
- Dark-blue solar panels only where appropriate.
- Dinosaur footprint engravings on one key concrete surface.
- Blank cream signs, screens and plaques: no text, letters, numbers, logos or watermarks.
- Never neon, never bright red or bright blue roofs.

CRITICAL: This building must have a unique, instantly readable identity. Do not make it look like a generic park office, shop, laboratory or VIP building. Its silhouette, roofline, footprint, main material and hero feature must clearly communicate its function from a distance.

UNIQUE BUILDING IDENTITY:
Function: Park power generation and distribution.
Player reads it as: The industrial power heart of the park.
Dominant silhouette: Industrial cluster of boxy volumes with chimney stacks and round tanks.
Footprint: Clustered.
Roofline: Flat roofs with two short stacks, roof vents and one round tank.
Primary material: Charcoal-green painted steel.
Secondary material: Cream concrete base, grey pipes and cable trays.
Hero feature: Two stacks and a large transformer box with a warning panel.
Functional props: Transformer boxes, thick pipes, small yellow-and-black hazard marks, service ladder, cable trays.
Mood: Industrial, practical, safe.

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons (wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels) simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

## 8. Genetics lab (post-V1)

Tier A. Suggested footprint: 3 x 3 cells.

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
- Soft green roof or planting accents (#5E9B4A).
- Dark-blue solar panels only where appropriate.
- Dinosaur footprint engravings on one key concrete surface.
- Blank cream signs, screens and plaques: no text, letters, numbers, logos or watermarks.
- Never neon, never bright red or bright blue roofs.

CRITICAL: This building must have a unique, instantly readable identity. Do not make it look like a generic park office, shop, laboratory or VIP building. Its silhouette, roofline, footprint, main material and hero feature must clearly communicate its function from a distance.

UNIQUE BUILDING IDENTITY:
Function: Dinosaur genetics laboratory.
Player reads it as: Where new dinosaurs are created.
Dominant silhouette: Tall vertical tower with a domed glass crown, narrow and dramatic.
Footprint: Small round or square base.
Roofline: Tall domed glass crown on a slim tower.
Primary material: Glass and charcoal-green steel.
Secondary material: Cream concrete base, grey pipes.
Hero feature: A tall glowing containment tube running up the tower with a soft teal-green glow.
Functional props: Containment tube, pipe manifold at the base, blank control panel, hazard marks.
Mood: Dramatic, scientific, mysterious but friendly.

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons (wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels) simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

## 9. Hotel (post-V1)

Tier A. Suggested footprint: 5 x 3 cells.

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
- Soft green roof or planting accents (#5E9B4A).
- Dark-blue solar panels only where appropriate.
- Dinosaur footprint engravings on one key concrete surface.
- Blank cream signs, screens and plaques: no text, letters, numbers, logos or watermarks.
- Never neon, never bright red or bright blue roofs.

CRITICAL: This building must have a unique, instantly readable identity. Do not make it look like a generic park office, shop, laboratory or VIP building. Its silhouette, roofline, footprint, main material and hero feature must clearly communicate its function from a distance.

UNIQUE BUILDING IDENTITY:
Function: Overnight guest hotel.
Player reads it as: A cosy place to sleep inside the dinosaur park.
Dominant silhouette: Terraced stepped building getting smaller toward the top, with balconies.
Footprint: Rectangular with stepped upper floors.
Roofline: Terraced stepped roofs with green planted terraces.
Primary material: Cream concrete with horizontal balcony bands.
Secondary material: Honey timber balcony fronts, teal glass doors, charcoal-green rails.
Hero feature: Stacked planted balconies stepping back toward the top with a canopy entrance.
Functional props: Canopy entrance, luggage cart, blank room-number plaques, balcony planters, amber lamps.
Mood: Cosy, relaxed, welcoming.

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons (wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels) simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

## 10. Ice-cream kiosk

Tier B. Suggested footprint: 1 x 1 cell.

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
- Soft green roof or planting accents (#5E9B4A).
- Dark-blue solar panels only where appropriate.
- Dinosaur footprint engravings on one key concrete surface.
- Blank cream signs, screens and plaques: no text, letters, numbers, logos or watermarks.
- Never neon, never bright red or bright blue roofs.

CRITICAL: This building must have a unique, instantly readable identity. Do not make it look like a generic park office, shop, laboratory or VIP building. Its silhouette, roofline, footprint, main material and hero feature must clearly communicate its function from a distance.

UNIQUE BUILDING IDENTITY:
Function: Ice-cream and cold treat kiosk.
Player reads it as: A small cheerful treat stand.
Dominant silhouette: Tiny round or hexagonal kiosk with a giant cone-shaped roof.
Footprint: Small round or hexagonal.
Roofline: Cone-like roof shaped like an oversized ice-cream scoop.
Primary material: Pastel painted panels with an amber stripe.
Secondary material: Honey timber counter and teal glass serving window.
Hero feature: An oversized scoop-like roof sitting on top.
Functional props: Serving counter, blank menu board, small freezer unit, two stools.
Mood: Friendly, playful, sweet.

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons (wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels) simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

## 11. Cafe

Tier B. Suggested footprint: 3 x 3 cells.

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
- Soft green roof or planting accents (#5E9B4A).
- Dark-blue solar panels only where appropriate.
- Dinosaur footprint engravings on one key concrete surface.
- Blank cream signs, screens and plaques: no text, letters, numbers, logos or watermarks.
- Never neon, never bright red or bright blue roofs.

CRITICAL: This building must have a unique, instantly readable identity. Do not make it look like a generic park office, shop, laboratory or VIP building. Its silhouette, roofline, footprint, main material and hero feature must clearly communicate its function from a distance.

UNIQUE BUILDING IDENTITY:
Function: Cafe and restaurant for rest and food.
Player reads it as: A relaxed place to sit down and eat.
Dominant silhouette: Open pavilion with a large floating canopy over outdoor seating.
Footprint: Square, open sides.
Roofline: Large butterfly canopy roof.
Primary material: Charcoal-green steel frame with a honey timber ceiling.
Secondary material: Teal glass serving wall, cream concrete floor slab.
Hero feature: A big canopy over outdoor tables with a serving window.
Functional props: Outdoor tables and benches, serving window, vent louvre, string lights.
Mood: Warm, social, relaxed.

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons (wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels) simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

## 12. Restroom

Tier B. Suggested footprint: 2 x 1 cells.

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
- Soft green roof or planting accents (#5E9B4A).
- Dark-blue solar panels only where appropriate.
- Dinosaur footprint engravings on one key concrete surface.
- Blank cream signs, screens and plaques: no text, letters, numbers, logos or watermarks.
- Never neon, never bright red or bright blue roofs.

CRITICAL: This building must have a unique, instantly readable identity. Do not make it look like a generic park office, shop, laboratory or VIP building. Its silhouette, roofline, footprint, main material and hero feature must clearly communicate its function from a distance.

UNIQUE BUILDING IDENTITY:
Function: Public restrooms.
Player reads it as: A simple, clearly marked facilities block.
Dominant silhouette: Very small simple block with a single sloped roof.
Footprint: Small rectangle.
Roofline: Mono-pitch roof sloping in one direction.
Primary material: Warm cream concrete.
Secondary material: Charcoal-green steel doors, honey timber screen panel.
Hero feature: A louvred vent grille above two clear door panels with blank pictogram plaques.
Functional props: Louvre vent, two doors with blank plaques, wall lamp, hand-wash station.
Mood: Simple, clean, functional.

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons (wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels) simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

## 13. Water pump

Tier B. Suggested footprint: 2 x 2 cells.

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
- Soft green roof or planting accents (#5E9B4A).
- Dark-blue solar panels only where appropriate.
- Dinosaur footprint engravings on one key concrete surface.
- Blank cream signs, screens and plaques: no text, letters, numbers, logos or watermarks.
- Never neon, never bright red or bright blue roofs.

CRITICAL: This building must have a unique, instantly readable identity. Do not make it look like a generic park office, shop, laboratory or VIP building. Its silhouette, roofline, footprint, main material and hero feature must clearly communicate its function from a distance.

UNIQUE BUILDING IDENTITY:
Function: Water pumping and enclosure water supply.
Player reads it as: The mechanical heart of the park's water system.
Dominant silhouette: Compact industrial structure with one large vertical water tank.
Footprint: Small square service footprint.
Roofline: Tank roof with pipe housing and a small control canopy.
Primary material: Charcoal-green painted steel.
Secondary material: Cream concrete base and grey pipes.
Hero feature: One large water tank connected to thick pipes and a valve wheel.
Functional props: Pressure gauge panel, control box with yellow-and-black hazard marks, pipe clamps, service ladder.
Mood: Practical, industrial, friendly.

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons (wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels) simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

## 14. Viewing deck

Tier B. Suggested footprint: 3 x 2 cells.

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
- Soft green roof or planting accents (#5E9B4A).
- Dark-blue solar panels only where appropriate.
- Dinosaur footprint engravings on one key concrete surface.
- Blank cream signs, screens and plaques: no text, letters, numbers, logos or watermarks.
- Never neon, never bright red or bright blue roofs.

CRITICAL: This building must have a unique, instantly readable identity. Do not make it look like a generic park office, shop, laboratory or VIP building. Its silhouette, roofline, footprint, main material and hero feature must clearly communicate its function from a distance.

UNIQUE BUILDING IDENTITY:
Function: Raised platform for watching dinosaurs.
Player reads it as: The best place to watch the animals.
Dominant silhouette: Low raised timber platform with railings and a small shade roof at one end.
Footprint: Rectangular platform with a ramp and stairs.
Roofline: Open railing with a small slanted shade canopy.
Primary material: Honey timber.
Secondary material: Charcoal-green steel posts and rails, teal glass panels.
Hero feature: A railing front with two fixed binoculars on posts.
Functional props: Fixed binoculars, benches, blank info plaque, amber post lights.
Mood: Open, calm, curious.

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons (wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels) simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

## 15. Bus stop

Tier B. Suggested footprint: 2 x 1 cells.

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
- Soft green roof or planting accents (#5E9B4A).
- Dark-blue solar panels only where appropriate.
- Dinosaur footprint engravings on one key concrete surface.
- Blank cream signs, screens and plaques: no text, letters, numbers, logos or watermarks.
- Never neon, never bright red or bright blue roofs.

CRITICAL: This building must have a unique, instantly readable identity. Do not make it look like a generic park office, shop, laboratory or VIP building. Its silhouette, roofline, footprint, main material and hero feature must clearly communicate its function from a distance.

UNIQUE BUILDING IDENTITY:
Function: Safari bus stop and visitor arrival.
Player reads it as: The place to board the safari bus.
Dominant silhouette: Small shelter with a curved canopy and a bench.
Footprint: Small rectangle.
Roofline: Curved canopy roof.
Primary material: Charcoal-green steel and honey timber.
Secondary material: Teal glass back panel.
Hero feature: A curved canopy with a blank route board panel.
Functional props: Bench, blank route board, wall lamp, bin.
Mood: Friendly, practical.

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons (wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels) simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

## 16. Mosasaurus tank

Tier A. Suggested footprint: 6 x 6 cells.

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
- Soft green roof or planting accents (#5E9B4A).
- Dark-blue solar panels only where appropriate.
- Dinosaur footprint engravings on one key concrete surface.
- Blank cream signs, screens and plaques: no text, letters, numbers, logos or watermarks.
- Never neon, never bright red or bright blue roofs.

CRITICAL: This building must have a unique, instantly readable identity. Do not make it look like a generic park office, shop, laboratory or VIP building. Its silhouette, roofline, footprint, main material and hero feature must clearly communicate its function from a distance.

UNIQUE BUILDING IDENTITY:
Function: Deep tank and glass viewing for the Mosasaurus.
Player reads it as: A big window into the deep sea.
Dominant silhouette: Round low tank building with a curved glass viewing wall and a walkway around the top.
Footprint: Round.
Roofline: Flat gallery roof around an open water surface, with a low canopy at the entrance.
Primary material: Teal curved glass tank wall.
Secondary material: Cream concrete rim, charcoal-green rails.
Hero feature: A tall curved glass wall with visible water and a viewing tunnel entrance.
Functional props: Viewing tunnel entrance, safety rails, pump housing, blank sign.
Mood: Awe-inspiring, calm.

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons (wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels) simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

## 17. Pteranodon aviary

Tier A. Suggested footprint: 5 x 5 cells.

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
- Soft green roof or planting accents (#5E9B4A).
- Dark-blue solar panels only where appropriate.
- Dinosaur footprint engravings on one key concrete surface.
- Blank cream signs, screens and plaques: no text, letters, numbers, logos or watermarks.
- Never neon, never bright red or bright blue roofs.

CRITICAL: This building must have a unique, instantly readable identity. Do not make it look like a generic park office, shop, laboratory or VIP building. Its silhouette, roofline, footprint, main material and hero feature must clearly communicate its function from a distance.

UNIQUE BUILDING IDENTITY:
Function: Large aviary for the Pteranodon.
Player reads it as: A giant open cage for a flying dinosaur.
Dominant silhouette: Tall tent-like mesh dome rising from a low base.
Footprint: Round or hexagonal.
Roofline: Tall mesh geodesic dome on thin steel poles.
Primary material: Charcoal-green steel mesh dome.
Secondary material: Cream concrete base ring, honey timber entry gate, perch posts.
Hero feature: A soaring steel-mesh dome with a central tall perch tree inside.
Functional props: Entry airlock gate, perch posts, feed station, blank sign.
Mood: Open, airy, awe-inspiring.

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons (wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels) simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

## Follow-up prompts

Fix a generic look:
```text
Redo this building with a much more distinct silhouette and roofline. Keep the same park style and palette. Keep the hero feature large and obvious. Do not change the camera, background or lighting.
```

Back and side views (after the front-left is approved):
```text
Using the same building, draw one clean three-quarter isometric view from the back-right at the same angle, scale, background and style. Keep the same materials and logical details. Plain but logical back and right side.
```

Silhouette check helper:
```text
Render this exact building as a flat solid black silhouette on a plain white background, same camera angle, no details.
```
