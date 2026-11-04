# Dino Park Tycoon — Updated Game Design & Production Research  
**Version 2.1 — Revised V1 Scope, Art Bible, Building Identity Tiers, and Build Plan**  
**Date: 4 November 2026**

This document updates the original *Dino Park Tycoon: Game Design Research* with the agreed decisions:

- Build **one island**, not multiple islands, for the first release.
- Use an **ocean map border**, similar to a Clash-style bounded map.
- Reduce the animal roster to a testable first version.
- Build **one predator only**: Tyrannosaurus rex.
- Include one flying animal and one sea animal as contained showcase habitats.
- Limit baby animals to three land species.
- Reduce vehicles to a small background/support set.
- Include one polished random event.
- Add a clear **Art Bible** and building-identity system so every building has a unique architectural purpose.
- Treat the first release as a **friends-and-family playable test build**, not the full game.

---

## 1. Updated product vision

**Dino Park Tycoon** is a calm, care-first dinosaur park management game for mobile.

The player clears land, builds enclosures, cares for dinosaurs, welcomes visitors, earns money, and gradually grows a beautiful prehistoric island park.

The game should feel:

- Calm, readable, and rewarding
- Creative, with visible player ownership
- Fair, with no pay-to-win systems
- Mobile-first, with short meaningful sessions
- Beautiful, with a warm hand-painted eco-research park style

### Core fantasy

> “I cleared a wild island, raised living dinosaurs, and built a park people love.”

### Core loop

1. Prepare land.
2. Build an enclosure.
3. Place and care for an animal.
4. Welcome visitors.
5. Earn money and reputation.
6. Unlock new animals, buildings, and park areas.

### Design pillars

| Pillar | Meaning |
|---|---|
| Calm care | The player cares for animals; the game does not punish them with stress, lost progress, or unfair timers. |
| Readable needs | Every problem shows why it happened and what to fix. |
| Creative ownership | Players design layouts, name animals, decorate zones, and build a park that feels theirs. |
| Fair progression | No loot boxes, no paid power, no forced ads, no pay-to-win. |
| Mobile clarity | Buildings, animals, alerts, and controls must be understandable at phone scale. |

---

## 2. Revised Version 1 scope

### 2.1 What V1 includes

The first public-facing test version includes:

- One island map
- Ocean border and limited camera scroll
- Nine animal species
- Three baby-capable land species
- One predator species
- One sea-animal showcase habitat
- One flying-animal showcase habitat
- Essential visitor, food, care, and staff buildings
- Limited background vehicles
- One scripted major random event
- Basic economy, visitor rating, needs, and care systems
- Cloud save
- Optional rewarded ads
- One remove-ads purchase

### 2.2 What V1 does not include

The following are postponed until after the first test:

- Multiple islands
- Full sea park with multiple marine species
- Full sky park with multiple pterosaurs
- Velociraptor and Spinosaurus
- Full genetics lab and hybrid system
- Marketplace
- Global chat
- Friend park visits
- Contracts, seasons, and long-term live-ops events
- Photo mode
- First-person free walk
- Founder’s Legacy restart mode
- Full 19-incident system

These remain valuable roadmap features, but they should not block the first playable build.

---

## 3. Island, ocean, and map rules

### 3.1 One island

V1 uses one hand-crafted island.

The island should contain:

- A central buildable park area
- Several terrain types: grass, rocky ground, dirt, mud, forest, and shore
- One open-range area for large herbivores
- Standard paddocks for medium herbivores
- One heavy predator paddock
- One lagoon/tank area
- One aviary area
- Visitor entrance and main path network
- Service roads and staff areas

### 3.2 Ocean border

The ocean is a visual and functional boundary.

It should:

- Mark the edge of the playable map
- Prevent the camera from scrolling into empty space
- Create a beautiful horizon and sense of place
- Support arrival animation for visitors, supplies, or animals
- Later support a ferry dock, boat tour, or coastal expansion

The ocean should not require a full marine simulation in V1.

### 3.3 Map scroll rules

Use a bounded camera similar to mobile base-builders:

- The player can pan across the island.
- The camera stops at the ocean edge.
- The ocean remains visible beyond the island boundary.
- Pinch-zoom is limited between a close building view and a full-island overview.
- Important alerts remain visible through map-edge indicators.

---

## 4. Revised animal roster

V1 contains **nine species**.

| Group | Animal | Babies in V1? | Enclosure |
|---|---|---:|---|
| Land herbivore | Triceratops | Yes | Standard paddock |
| Land herbivore | Stegosaurus | Yes | Standard paddock |
| Land herbivore | Brachiosaurus | Yes | Open range |
| Land herbivore | Ankylosaurus | No | Standard paddock |
| Land herbivore | Maiasaura | No | Standard paddock |
| Land herbivore | Diplodocus | No | Open range |
| Predator | Tyrannosaurus rex | No | Heavy paddock |
| Flying reptile | Pteranodon | No | Aviary |
| Marine reptile | Mosasaurus | No | Deep tank/lagoon |

### 4.1 Why this roster works

- Six land herbivores provide enough variety for paddocks, herds, and open ranges.
- Three baby species are enough to test hatching, growth, naming, and visitor appeal.
- T. rex provides the predator fantasy without requiring three separate predator systems.
- Pteranodon gives the sky appeal without a full aviary system.
- Mosasaurus gives the sea appeal without a full marine park.
- The roster is large enough for marketing screenshots but small enough for one developer to polish.

### 4.2 Animals postponed

| Animal | Reason to postpone |
|---|---|
| Velociraptor | Requires roofed containment, fast AI, escape logic, and unique stealth/night behavior. |
| Spinosaurus | Requires semi-aquatic behavior, fish feeding, lagoon design, and separate water systems. |
| Additional marine reptiles | Each adds new tank, feeding, and visitor-viewing requirements. |
| Additional pterosaurs | Each adds new flight, aviary, and wind-system requirements. |

Velociraptor and Spinosaurus should be the first major post-launch animal update.

---

## 5. Baby animals

Only these species have babies in V1:

1. Triceratops
2. Stegosaurus
3. Brachiosaurus

### Baby system

- The player obtains an egg through purchase, reward, event, or breeding.
- The egg incubates in the hatchery.
- The player can name the baby.
- The baby hatches with a short welcome moment.
- The baby grows through baby → juvenile → adult.
- Babies increase visitor appeal, especially for family visitors.
- Baby animals stay near adults for herd species.

### Rules

- Adult-only species can still arrive as adults.
- No baby models are required for T. rex, Pteranodon, Mosasaurus, Ankylosaurus, Maiasaura, or Diplodocus in V1.
- Baby growth should be visible but not overly slow.
- Hatching should be a positive, shareable moment.

---

## 6. Buildings for V1

### 6.1 Essential buildings

| Building | Purpose | Priority |
|---|---|---|
| Entrance gate and ticket booth | Visitor arrival, tickets, park identity | Must have |
| Paths and plazas | Visitor movement | Must have |
| Benches, bins, lamps | Visitor comfort and cleanliness | Must have |
| Restrooms | Visitor need | Must have |
| Souvenir shop | Visitor spending | Must have |
| Ice-cream kiosk or café | Food and rest | Must have |
| Viewing deck | Animal viewing and rating | Must have |
| Standard paddock | Medium herbivores | Must have |
| Open range | Large herbivores and safari bus | Must have |
| Heavy predator paddock | T. rex | Must have |
| Feeder and water trough | Animal care | Must have |
| Shelter | Animal comfort and weather protection | Must have |
| Hospital or vet station | Animal treatment | Must have |
| Hatchery | Eggs and babies | Must have |
| Mosasaurus tank/lagoon | Sea showcase | Must have |
| Pteranodon aviary | Flying showcase | Must have |
| Bus stop | Visitor arrival and safari bus | Must have |

### 6.2 Strong additions

| Building | Purpose | Priority |
|---|---|---|
| Hotel | Overnight guests and night-cycle value | Add if time allows |
| Admin building | Park management identity and staff overview | Add if time allows |
| Research center | Later research-tree foundation | Add if time allows |
| Power station | Power and upgrade systems | Add if time allows |
| Vehicle depot (hangar) | Home for safari bus, supply truck, vet jeep; already built in Blender | Add if time allows |
| Helipad | Later rescue and tour systems | Defer |
| Feeding-show stadium | Lagoon event and visitor spectacle | Defer |
| Genetics lab | Hybrid creation | Defer |
| Landmark tower | Long-term goal and skyline | Defer |

### 6.3 Visitor activities in V1

- Watch animals from viewing decks
- Buy tickets
- Buy food and souvenirs
- Rest on benches
- Use restrooms
- Ride the safari bus through the open range
- Watch the Mosasaurus through glass
- Watch the Pteranodon in the aviary
- See baby dinosaurs near the hatchery
- Experience the one major random event

---

## 7. Vehicles

V1 uses a small vehicle set focused on life, movement, and support.

| Vehicle | Role | Priority |
|---|---|---|
| Safari bus | Drives visitors through the open range | Must have |
| Supply truck | Delivers food and shop stock | Must have |
| Vet jeep | Supports the random care event | Must have |
| Arrival bus or ferry | Brings visitors to the island | Strong addition |
| Helicopter | Rescue, tours, delivery | Defer |
| Plane | Distant arrival or map transition | Defer |
| Rescue truck | Major incidents | Defer |
| Boat tour | Lagoon activity | Defer |

Vehicles should mostly be background life in V1. The player should not need to manage complex schedules, fuel, repairs, or staff assignments yet.

---

## 8. One random event: T. rex fence stress

V1 should have **one excellent event**, not nineteen shallow ones.

### Event: T. rex fence stress / near-escape

**Goal:** Create tension, teach enclosure care, and produce a memorable moment without punishing the player.

### Flow

1. A warning appears: the T. rex is agitated.
2. The heavy paddock fence integrity begins to fall.
3. The player receives a clear alert with a map marker and timer.
4. The player chooses a response:
   - Send the vet jeep to calm the animal.
   - Reinforce or repair the fence.
   - Use food to distract the T. rex.
5. The chosen response has different cost, speed, and risk.
6. The event resolves.
7. A report card explains what happened, what it cost, and how to prevent it.

### Outcomes

| Response | Result |
|---|---|
| Quick correct response | T. rex calms; small cost; visitors impressed |
| Slow response | Fence damaged; repair cost; visitor rating drops |
| Ignored event | Staff handle it automatically at higher cost; no permanent progress loss |
| Best long-term fix | Better fence, more space, reliable food, and shelter reduce future risk |

### Event rules

- The event is telegraphed before it becomes dangerous.
- It does not occur in the first 10 minutes of a new park.
- It never deletes progress.
- Visitors may be scared but are never harmed.
- The event should be exciting but fair.

---

## 9. Art Bible

### 9.1 Overall art direction

**Style:** Stylized semi-realistic, hand-painted, low-poly-friendly mobile game art.

The world should feel warm, natural, friendly, and believable—not cartoonish and not horror-oriented.

### 9.2 Visual rules

- Use soft brush-painted surfaces.
- Use simple, readable silhouettes.
- Use slightly rounded and chamfered edges.
- Avoid tiny clutter and excessive detail.
- Use large readable shapes.
- Use natural earthy colors for terrain and animals.
- Use warm accent colors sparingly.
- Keep matte materials; avoid strong reflections except glass and water.
- Use thin dark outlines only where they improve readability.
- Keep every asset readable when viewed from the default isometric camera.

### 9.3 Shared park palette

The park uses a consistent eco-research palette:

| Element | Color direction |
|---|---|
| Concrete | Warm cream |
| Timber | Honey-orange vertical slats |
| Glass | Teal tinted |
| Steel | Charcoal-green painted frames |
| Lamps and trim | Amber glow |
| Green accents | Soft green roofs, planting, stripes |
| Solar panels | Dark blue |
| Pipes and controls | Grey with clamps |
| Hazard details | Small yellow-and-black marks |

The palette is a **shared visual language**, not a permission to make every building look identical.

### 9.4 Terrain rules

Terrain pieces must be modular.

- Tiles snap edge to edge.
- All tiles use the same footprint and thickness.
- Tops are flat and clean.
- Sides are clean vertical faces.
- No baked-in cast shadows.
- No props standing on modular tiles.
- Natural earthy colors.
- Simple painted texture variation.

Starter terrain tiles:

1. Plain short green grass
2. Lush deep-green grass with tiny clover flowers
3. Dry yellow-tan grass
4. Bare brown dirt with small pebbles
5. Grey rocky ground with flat stones in soil
6. Wet dark-brown mud with shallow puddles

### 9.5 Plant rules

Plants should use simplified leaf masses, not individual leaves.

- Use a few large readable leaf clusters.
- Keep silhouettes clear.
- Use natural greens with warm accents.
- Show growth stages at true relative size.
- Avoid ground, pots, and scenery in asset sheets.

Example: conifer set

- Young slim conifer
- Mature full conifer
- Tall old conifer with bare lower trunk

Use a prehistoric look inspired by monkey-puzzle or podocarp trees, but keep the shapes simple and readable.

### 9.6 Animal art rules

Animals should be:

- Semi-realistic and scientifically plausible
- Painterly and soft
- Friendly and readable
- Never cute-cartoon
- Never movie-monster
- Naturally colored, with one bold display color
- Built with clear anatomy
- Designed with simple scale or feather patterns
- Matte, not wet or glossy

Every animal needs:

- Clear head, neck, body, limbs, tail, feet, and claws
- A neutral standing pose for the concept sheet
- A clean three-quarter side view
- Full body visible from nose to tail tip
- Separate head or modular parts where useful for animation and hybrids

---

## 10. Building architecture identity

### 10.1 The core problem

The original building prompts create a consistent park style, but many buildings share the same basic architecture:

- Rounded cream concrete boxes
- Honey timber slats
- Teal glass
- Green roofs
- Solar panels
- Amber trim

That creates cohesion, but it also makes buildings hard to tell apart.

A player should recognize a building’s function from its silhouette before reading its name.

### 10.2 The solution

Use one rule:

> **Same park. Same palette. Different architecture.**

Every building shares the world’s visual DNA, but each has a unique:

- Silhouette
- Roofline
- Footprint
- Primary material
- Hero feature
- Functional props
- Mood

### 10.3 Building identity table

| Building | Dominant silhouette | Roofline | Primary material | Hero feature | Player reads it as |
|---|---|---|---|---|---|
| Administration | Tall, orderly, rectangular two-storey block | Stepped flat roof with entrance tower | Cream concrete | Central entrance tower, flagpole, blank park sign | Park headquarters |
| VIP lounge | Low, wide, horizontally curved building | Gently curved roof with garden | Teal curved glass | Sweeping glass lounge wall under timber canopy | Premium guest area |
| Souvenir shop | Small friendly retail box | Wide awning with green roof | Honey timber | Large display windows and gift displays | Place to buy things |
| Ice-cream kiosk | Tiny circular or hexagonal kiosk | Cone-like roof | Pastel painted panels with amber stripe | Oversized scoop-like roof shape | Treats and snacks |
| Café / restaurant | Open pavilion with seating | Large canopy | Timber, glass, cream concrete | Outdoor tables and serving window | Food and rest |
| Restroom | Very small simple block | Mono-pitch (single slope) roof | Cream concrete | Ventilation grille and clear door panels | Facilities |
| Hospital | L-shaped medical block with service bay | Flat roof with helipad ring | Pale sage panels over cream base | Ambulance bay and treatment entrance | Animal care |
| Research center | Angular science block or clustered labs | Sawtooth or angled roof | Concrete, glass, steel | Antenna, pipes, greenhouse panels | Science and discovery |
| Power station | Industrial clustered structure | Vents, stacks, tanks | Charcoal-green steel | Transformer boxes, pipes, warning markings | Power supply |
| Water pump | Compact mechanical structure | Tank and pipe housing | Steel and concrete | Large pipe, valve wheel, water tank | Water control |
| Hatchery | Low round incubation building | Soft dome | Warm amber-cream plaster | Glass egg room and nesting pods | Eggs and babies |
| Genetics lab | Tall vertical tower | Domed glass crown | Glass, steel, concrete | Containment tube and gene-tank glow | Dinosaur creation |
| Entrance gate | Wide landmark gateway | Tall arch or canopy | Concrete, steel, glass | Tall arch, ticket booths, park sign | Park entrance |

### 10.4 Architecture rules

1. Tier A landmarks (entrance, admin, VIP, hospital, research, hatchery, power, depot, genetics) never share a roofline or a primary material.
2. Tier B small services (shop, kiosk, cafe, restroom, pump, viewing deck, bus stop) never share silhouette plus roofline. Cream concrete is the shared plinth and does not count as a primary material except for the admin building.
3. Every building needs one hero feature visible from the default camera.
4. Functional buildings need visible equipment.
5. Commercial buildings need visible customer space.
6. Use the shared palette for trim, windows, roofs, and details—not for the entire building identity.
7. Every building silhouette must remain readable when reduced to a small icon.
8. Test each building as a black silhouette before modeling it.
9. Keep footprints aligned to the game’s tile grid.
10. Keep back and side views logical, even if they are visually simpler.

### 10.5 Silhouette test

Before creating a 3D model:

1. Make the building concept black.
2. Remove all color and texture.
3. Shrink it to approximately 64 pixels wide.
4. Ask: “Can I tell what this building is?”
5. If not, change the roofline, massing, or hero feature.

If the hospital, research center, admin building, and souvenir shop all look alike in silhouette, redesign them before production.

---

## 11. Updated Gemini prompt template

Use this template for every building concept.

```text
Stylized semi-realistic hand-painted game asset for a mobile dinosaur park management game.

A painterly digital illustration of a low-poly 3D model: soft brush-painted surfaces, light wear and dirt in edges and corners, thin dark outline, slightly rounded and chamfered edges, clean readable silhouette, big simple shapes, no tiny clutter.

Camera: one three-quarter isometric view from the front-left, about 35 degrees above the ground. The whole object is centred, fully visible, and fully inside the frame with empty space around it. Nothing cropped.

Background: plain flat light-grey studio background, about #C8C9CC. No scenery, no ground texture, no horizon, no trees. Only a soft contact shadow directly under the object.

Lighting: soft daylight from the upper left, matte materials, no strong reflections, no glow except lamps.

Shared park visual language:
- Modern friendly eco-research dinosaur park.
- Warm cream concrete with rounded corners.
- Honey-orange timber slats used as an accent, not the main material.
- Teal tinted glass.
- Charcoal-green painted steel frames.
- Amber lamps and trim lines.
- Soft green roof or planting accents.
- Dark-blue solar panels only where appropriate.
- Dinosaur footprint engravings on one key concrete surface.
- Blank cream signs, screens and plaques: no text, letters, numbers, logos or watermarks.

CRITICAL: This building must have a unique, instantly readable identity. Do not make it look like a generic park office, shop, laboratory or VIP building. Its silhouette, roofline, footprint, main material and hero feature must clearly communicate its function from a distance.

UNIQUE BUILDING IDENTITY:
Function: [BUILDING FUNCTION]
Player reads it as: [ONE-SENTENCE PLAYER IMPRESSION]
Dominant silhouette: [DESCRIBE OUTLINE]
Footprint: [SQUARE / LONG / L-SHAPED / ROUND / CLUSTERED]
Roofline: [FLAT / DOME / SAWTOOTH / CANOPY / TOWER / TANK]
Primary material: [MAIN MATERIAL]
Secondary material: [SUPPORTING MATERIAL]
Hero feature: [ONE LARGE MEMORABLE FEATURE]
Functional props: [2-4 SIMPLE PROPS THAT EXPLAIN THE FUNCTION]
Mood: [FRIENDLY / LUXURIOUS / INDUSTRIAL / MEDICAL / SCIENTIFIC]

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons—wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels—simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

### 11.1 Example: administration building

```text
UNIQUE BUILDING IDENTITY:
Function: Park administration and staff management.
Player reads it as: The organised headquarters of the dinosaur park.
Dominant silhouette: A tall, upright two-storey rectangular block with a clean vertical entrance tower.
Footprint: Rectangular, compact, slightly taller than wide.
Roofline: Mostly flat with a small raised entrance tower and a slim flagpole.
Primary material: Warm cream concrete.
Secondary material: Charcoal-green steel window frames and honey timber slats on the upper floor.
Hero feature: A tall central entrance tower with a blank rounded park sign and a slim flagpole.
Functional props: Wall-mounted schedule board, service door, roof ventilation unit, small staff entrance.
Mood: Organised, professional, welcoming.
```

### 11.2 Example: VIP lounge

```text
UNIQUE BUILDING IDENTITY:
Function: Premium guest lounge for VIP visitors.
Player reads it as: A relaxed, luxurious place for important guests.
Dominant silhouette: Low, wide, horizontally curved building with a sweeping glass front.
Footprint: Wide and shallow, with a curved front wall.
Roofline: Gently curved or wave-like roof with a planted roof garden.
Primary material: Teal curved glass.
Secondary material: Cream concrete base and honey timber vertical slats.
Hero feature: A large curved glass lounge wall beneath a deep timber canopy.
Functional props: Covered entrance, soft carpet strip, two large planters, warm amber under-canopy lights.
Mood: Calm, premium, welcoming.
```

### 11.3 Example: water pump

```text
UNIQUE BUILDING IDENTITY:
Function: Water pumping and enclosure water supply.
Player reads it as: The mechanical heart of the park’s water system.
Dominant silhouette: Compact industrial structure with one large vertical water tank.
Footprint: Small square or rectangular service footprint.
Roofline: Tank roof with pipe housing and a small control canopy.
Primary material: Charcoal-green painted steel.
Secondary material: Cream concrete base and grey pipes.
Hero feature: One large water tank connected to thick pipes and a valve wheel.
Functional props: Pressure gauge panel, control box with yellow-and-black hazard marks, pipe clamps, service ladder.
Mood: Practical, industrial, friendly.
```

---

## 12. Modular kit parts

Keep the original modular-part idea, but do not let it dominate building identity.

| Kit part | Role |
|---|---|
| Solar panel | Roof power upgrade |
| AC unit | Comfort upgrade for visitor buildings |
| Wall lamp | Night lighting and safety |
| Meter box | Power-grid connection |
| Vent louvre | Required for food and service buildings |
| Window | Visual variation and night glow |
| Drain pipe | Rain and service detail |

### Rules

- Kit parts are upgrades or functional details.
- They should not define the entire building.
- Each building still needs its own base architecture.
- Use named socket points in Blender, such as `SOCKET_SolarPanel`, `SOCKET_ACUnit`, and `SOCKET_MeterBox`.

---

## 13. Updated production plan

Assumption: approximately 5–6 focused hours per day, with AI-assisted concepting, modeling, coding, and iteration. At 3–4 hours per day, expect roughly 16–19 weeks.

### 13.1 Twelve-week build plan

| Weeks | Goal |
|---|---|
| 1–2 | Island terrain, ocean border, camera bounds, tile system, pathing, save system |
| 3–4 | Triceratops full loop: paddock, food, water, needs, sickness/care, visitor income |
| 5–6 | Stegosaurus, Brachiosaurus, open range, safari bus, babies and hatching |
| 7–8 | T. rex, heavy paddock, one random event, vet/hospital loop |
| 9–10 | Mosasaurus tank and Pteranodon aviary as contained showcase habitats |
| 11–12 | Shops, hotel if time allows, UI polish, onboarding, performance, friend testing |

### 13.2 Build order

1. Terrain and camera.
2. One animal and one enclosure.
3. Needs and care.
4. Visitors and money.
5. More herbivores and open range.
6. Babies and hatchery.
7. Predator and event.
8. Sea and sky showcases.
9. Shops, hotel, polish, and testing.

### 13.3 Cut order

If time becomes short, cut in this order:

1. Hotel
2. Pteranodon aviary
3. Mosasaurus tank
4. Safari bus route
5. Extra visitor types
6. Advanced decoration systems
7. Research center
8. Admin building

Do **not** cut:

- Cloud save
- Animal needs
- Visitor income
- Onboarding
- Performance optimization
- The Triceratops core loop

---

## 14. Testing plan

### 14.1 First test audience

Test with friends and family on different phones before public release.

Target:

- 5–10 different Android devices
- At least one low-end phone
- At least one older phone
- Different screen sizes
- Different internet conditions

### 14.2 What to observe

Ask testers to play for 10 minutes without explanation.

Track:

- Did they understand what to do in the first two minutes?
- Did they place or hatch the first animal quickly?
- Did they understand animal needs?
- Did they return the next day?
- Did the game run smoothly?
- Did anyone lose progress?
- Did they voluntarily watch a rewarded ad?
- What did they try to do that the game did not allow?
- Which buildings could they identify instantly?
- Which animals did they like most?

### 14.3 Success signals

A strong early test shows:

- Players understand the core loop without a long tutorial.
- Players return after the first day.
- The game runs acceptably on low-end phones.
- Players can identify building functions from their silhouettes.
- Players voluntarily engage with care actions.
- Players ask for more animals, decorations, or park space.

### 14.4 Warning signals

Stop adding content if:

- Players do not understand the first session.
- Day-1 retention is weak among friends.
- The game stutters or heats up on mid-range phones.
- Players lose progress.
- Players cannot tell buildings apart.
- The core care loop feels like chores rather than play.

---

## 15. Monetization for V1

### 15.1 Revenue model

- Optional rewarded ads only
- No interstitial ads during emergencies
- No forced ads
- No loot boxes
- No paid power
- No paid stability boosts
- One remove-ads purchase

### 15.2 Rewarded-ad placements

Use only optional, non-punishing placements:

- Double offline income
- Skip one terrain-clearing job
- Speed up one hospital stage
- Receive one temporary visitor boost
- Receive one free enrichment item
- Speed up the final minutes of an egg hatch

### 15.3 Rules

- The reward must be granted immediately when the ad ends.
- If an ad fails to load, hide the button.
- Cap ad frequency.
- Never show ads during an emergency event.
- Never show ads immediately after a purchase.
- Keep rewarded ads available after the remove-ads purchase.

---

## 16. Compliance and child safety

Dinosaur games attract children, so child safety remains a launch requirement.

### V1 requirements

- Neutral age screen at first launch
- Child-safe ad configuration where required
- No behavioral profiling for children
- No location tracking
- No open chat
- No public user-generated text
- Parental gate for purchases
- Clear privacy policy
- Account deletion route
- Accurate store age-rating and data-safety forms

### Audience recommendation

Use a **mixed-audience, child-safe-by-default** approach:

- General store listing
- Age screen at first launch
- Child mode with contextual, child-safe ads
- No social features for child accounts
- Purchases behind parental controls

This should be reviewed by a legal or compliance specialist before public launch.

---

## 17. Updated decisions

### Decided

- One island for V1.
- Ocean border with limited camera scroll.
- Nine animals in V1.
- Three baby-capable species: Triceratops, Stegosaurus, Brachiosaurus.
- One predator: T. rex.
- One flying animal: Pteranodon.
- One sea animal: adult Mosasaurus.
- One polished random event: T. rex fence stress.
- Limited vehicles: safari bus, supply truck, vet jeep, arrival bus/ferry.
- Essential buildings first; hotel and admin building only if time allows.
- Same park visual language, but unique architecture for every building.
- Twelve-week target for the friends-and-family test build.

### Still open

- Should the hotel be in the first test build or the first update?
- Should the Mosasaurus habitat include a feeding show or remain a viewing tank?
- Should the Pteranodon aviary be walk-in, viewing-only, or both?
- Should the admin building be functional in V1 or visual only?
- Should the first update after testing add Velociraptor, Spinosaurus, or the genetics lab first?

---

## 17a. V2.1 revisions and recommendations

**Fixed:** the V2 building table broke its own rules (admin, restroom, souvenir shop and hospital all cream concrete; admin, restroom and hospital all flat roofs). Rules are now tiered and the table corrected. See BUILDING_IDENTITY.md.

**Added:** the Hangar (already built) becomes the vehicle depot. Built so far: Souvenir shop ~7k tris, Hangar ~17k tris, neither exported to Unity. The extended 19-part kit lives in Hangar.blend. Park-standard solar panel is 1.6 x 1.0 m.

**Risk:** 17 must-have buildings with unique shells, 9 animals, vehicles and a full event is a lot for one developer. Keep Tier B shells very simple and reuse kit parts heavily.

**Recommendations on open questions**

| Question | Recommendation |
|---|---|
| Hotel in test build | First update |
| Mosasaurus feeding show | Viewing tank only in V1 |
| Pteranodon aviary | Viewing-only in V1, walk-in later |
| Admin building | Visual only in V1 |
| First post-V1 animal | Spinosaurus (reuses water tech), or Velociraptor if you prefer |

## 18. Final recommendation

Build the revised V1 as a **single-island, nine-animal, care-first park test**.

Do not try to build the full sea park, sky park, genetics system, social system, and endless content at once.

The first goal is not to make every feature. The first goal is to prove this:

> **A player opens the game, understands the park within two minutes, cares for a dinosaur, earns visitor income, and wants to return tomorrow.**

If that works, the sea park, aviary, genetics lab, predators, events, and social systems become strong updates. If it does not work, more content will not fix the core game.
