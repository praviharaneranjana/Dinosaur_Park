# Dino Park Tycoon: Building Identity Guide

Version 2.1 (4 Nov 2026). How buildings stay one park but never look the same. Part of DESIGN_BIBLE.md.

## 1. Rule

> Same park. Same palette. Different architecture.

A player should know a building's job from its silhouette before reading its name.

## 2. Two tiers (new in 2.1)

The original rule "no two buildings share roofline or primary material" is impossible for 17+ buildings with a 9-colour palette, and the first draft table already broke it (admin, restroom, souvenir shop and hospital all cream concrete, three flat roofs). So the rule is split:

- Tier A, landmarks (visitors navigate by them): must have a unique roofline AND a unique primary material AND a unique silhouette.
- Tier B, small services: must have a unique silhouette AND roofline. Primary material may repeat, but never next to the same-material neighbour in a typical layout.

Cream concrete is the shared plinth/base on most buildings. It only counts as a "primary material" for the admin building.

## 3. Identity block (fill in before any concept)

Function / Player reads it as / Dominant silhouette / Footprint / Roofline / Primary material / Secondary material / Hero feature / Functional props (2 to 4) / Mood.

## 4. Building matrix

### Tier A, landmarks

| Building | Silhouette | Roofline | Primary material | Hero feature | Reads as |
|---|---|---|---|---|---|
| Entrance gate + ticket booths | Wide gateway | Tall arch / canopy | Charcoal-green steel with cream piers | Arch with blank park sign | Park entrance |
| Administration | Tall upright two-storey block | Stepped flat roof + entrance tower | Cream concrete | Tower, flagpole, blank rounded sign | Headquarters |
| VIP lounge | Low, wide, curved | Wave roof with garden | Teal curved glass | Sweeping glass wall under timber canopy | Premium guests |
| Hospital / vet | L-shaped medical block | Flat roof with helipad ring | Pale sage panels over cream base | Ambulance bay + treatment entrance | Animal care |
| Research center | Angular clustered labs | Sawtooth | Glass and grey steel | Antenna, greenhouse panels, pipes | Science |
| Hatchery | Low round building | Soft dome | Warm amber-cream plaster | Glass egg room with nesting pods | Eggs and babies |
| Power station | Industrial cluster | Stacks, vents, tanks | Charcoal steel | Transformer boxes, hazard marks | Power |
| Vehicle depot (hangar) | Long arched shed | Barrel vault (R=5 m) | Cream base, green ribs | Roller door, windsock | Garage for bus, truck, jeep |
| Genetics lab (deferred) | Vertical tower | Domed glass crown | Glass and steel | Containment tube glow | Dino creation |

### Tier B, small services

| Building | Silhouette | Roofline | Primary material | Hero feature |
|---|---|---|---|---|
| Souvenir shop (built) | Small friendly box | Wide awning, green roof | Honey timber | Display windows, gift displays |
| Ice-cream kiosk | Tiny round or hex | Cone | Pastel painted panels, amber stripe | Oversized scoop roof |
| Cafe | Open pavilion | Big canopy | Steel frame, timber ceiling | Outdoor tables, serving window |
| Restroom | Very small block | Mono-pitch (single slope) | Cream concrete | Louvre vent, clear door panels |
| Water pump | Compact with one tall tank | Tank roof, pipe housing | Charcoal steel, grey pipes | Water tank, valve wheel |
| Viewing deck | Raised platform | Open rail, small shade | Timber | Railing, binoculars |
| Bus stop | Shelter | Curved canopy | Steel and timber | Blank route board |

## 5. Rules (revised)

1. Tier A buildings never share roofline or primary material.
2. Tier B buildings never share silhouette plus roofline.
3. One hero feature visible from default camera.
4. Functional buildings show visible equipment.
5. Commercial buildings show customer space.
6. Palette is for trim, glazing, roofs and details, not the whole identity.
7. Silhouette reads at icon size.
8. Black silhouette test before modelling (section 7).
9. Footprints align to tile grid.
10. Back and sides are logical, simpler allowed, but never bare: every side gets kit parts.
11. Use the same park-standard sizes for kit parts so building scale reads.

## 6. Kit parts (upgrades and details, never the identity)

Original 7 (SouvenirShop.blend): CMP_Window 0.8x1.0 m; CMP_AC_Unit 0.78x0.58x0.36; CMP_Vent_Louver 0.5x0.3; CMP_Drain_Pipe 2.8 m; CMP_Wall_Lamp; CMP_Meter_Box 0.4x0.55x0.14; CMP_Solar_Panel 1.6x1.0 m, 12 deg tilt.

Added with the Hangar (Hangar.blend): CMP_Hazard_Post, CMP_Hazard_Sticker, CMP_Sign_Plaque (blank), CMP_Windsock, CMP_Utility_Cabinet, CMP_Pipe_Elbow, CMP_Ground_Box, CMP_Roller_Door, CMP_Skylight_Curved, CMP_Grass_Tuft, CMP_Personnel_Door, CMP_Dino_Footprint.

Placement: wall parts face +Y with origin on wall; rotate Z back 0, left 90, right -90, front 180. Roof parts use local Z as normal. Linked duplicates (Alt+D).

Game roles: Solar = power upgrade; AC = comfort upgrade for visitor buildings; Wall lamp = night safety; Meter box = grid connection; Vent louvre = required on food and service buildings; Window = night glow; Drain pipe = rain/service detail.

Sockets per building: SOCKET_SolarPanel, SOCKET_ACUnit, SOCKET_MeterBox, SOCKET_WallLamp, SOCKET_Vent, SOCKET_Window (add as needed).

## 7. Silhouette test

1. Fill the concept black. 2. Remove colour and texture. 3. Shrink to about 64 px wide. 4. Ask: can I tell what this is? 5. Put the Tier A set side by side: any two that look alike, redesign.

Scoring: 3 testers, 3 seconds each, name the building. Pass = 2 of 3 correct.

## 8. Gemini concept prompt template

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

This is a building shell. Draw large glazing, doors and sign boards as part of the shell. Draw small wall add-ons (wall lamps, AC unit, vent louvre, meter box, drain pipe, roof solar panels) simply and clearly separate from the wall, because they will be modelled as swappable parts. Leave the back and right side plain but logical.

Show ONE clean model that a 3D artist can build from this single picture: logical on every side, symmetrical where a real one would be, simple volumes.
```

### Filled examples

Administration: Park administration and staff management. Reads as the organised headquarters. Tall upright two-storey block with vertical entrance tower. Rectangular, compact. Stepped flat roof, raised tower, slim flagpole. Primary warm cream concrete; secondary charcoal-green window frames and honey timber slats upstairs. Hero: tall central tower with blank rounded sign and flagpole. Props: schedule board, service door, roof vent unit, staff entrance. Mood: organised, welcoming.

VIP lounge: Premium guest lounge. Reads as relaxed luxury. Low wide horizontally curved with sweeping glass front. Wide shallow footprint, curved front. Wave roof with roof garden. Primary teal curved glass; secondary cream base and timber slats. Hero: large curved glass wall under deep timber canopy. Props: covered entrance, carpet strip, two planters, amber under-canopy lights. Mood: calm, premium.

Water pump: Water supply for enclosures. Reads as the mechanical heart of the water system. Compact industrial with one large vertical tank. Small service footprint. Tank roof, pipe housing, small control canopy. Primary charcoal-green steel; secondary cream base, grey pipes. Hero: large tank with thick pipes and valve wheel. Props: pressure gauge panel, hazard-marked control box, pipe clamps, ladder. Mood: practical, industrial, friendly.

## 9. Status of built buildings

| Building | File | Status | Identity check |
|---|---|---|---|
| Souvenir shop | SouvenirShop.blend | Built, ~7k tris, not exported | Passes: timber primary, awning. Teal storefront is glazing only, so no clash with VIP glass. |
| Hangar | Hangar.blend | Built, ~17k tris, not exported | Passes: only barrel-vault building. Not in the original V1 list, repurposed as vehicle depot. |
