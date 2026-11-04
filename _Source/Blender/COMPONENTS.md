# Reusable building component kit (Blender)

Source file: `_Source/Blender/SouvenirShop.blend`, collection **CMP_Library** (row at y = 9, hidden from renders).
Every item is a marked asset with tag `building-component`, so it shows in the Asset Browser. Notes also live in the text block `CMP_README`.

## Components
| Name | Size | Use |
|---|---|---|
| CMP_Window | 0.8 w x 1.0 h m, charcoal frame, timber sill, mullion + transom | Plain walls |
| CMP_AC_Unit | 0.78 w x 0.58 h x 0.36 d m, on wall brackets | Back/side walls |
| CMP_Vent_Louver | 0.5 w x 0.3 h m | Above AC, service walls |
| CMP_Drain_Pipe | 2.8 m tall, clamps, hopper, outlet | Wall corners |
| CMP_Wall_Lamp | Sconce with amber glow tube | Next to doors/windows |
| CMP_Meter_Box | 0.4 w x 0.55 h x 0.14 d m, conduit running up | Service walls |
| CMP_Solar_Panel | 1.6 x 1.0 m (park standard), 12 deg tilted frame | Every roof |

## Placement rules
- Wall components face **+Y**, origin **on the wall surface** (drain pipe: origin at the pipe bottom).
- Rotate Z: back wall 0, left wall (-X) 90, right wall (+X) -90, front wall (-Y) 180.
- CMP_Solar_Panel: origin on the **roof surface** under the panel centre, low edge faces -Y.
- Place with **linked duplicates (Alt+D)** so copies share mesh data and one fix updates all.
- Name placed copies `<Building>_<Wall>_<Component>`, e.g. `SS_Back_AC`.

## Used on the souvenir shop
- Back wall (+Y): 2 windows, lamp, AC unit, louver vent, drain pipe.
- Left wall (-X): window, meter box, vent, lamp, drain pipe.
- Roof: 2 x CMP_Solar_Panel (SS_Roof_Solar_A/B).


## Added with the Hangar (Hangar.blend, collection CMP_Library, tag "building-component")
Same rules as above: wall components face +Y with origin on the wall surface; roof parts have local Z = roof normal.
- CMP_Hazard_Post: 0.22 x 0.06 x 3.3 m yellow/black jamb guard (packed texture HG_HazardStripe), origin bottom-back
- CMP_Hazard_Sticker: 0.26 m square warning plate
- CMP_Sign_Plaque: 2.3 x 0.62 m cream pill sign with green rim (blank, add text per building)
- CMP_Windsock: 3.9 m pole, 5-band orange/white sock pointing local +X, origin at base
- CMP_Utility_Cabinet: 2.2 x 0.45 x 1.6 m rounded cream housing (bevel modifier) to hang AC/vent/meter on
- CMP_Pipe_Elbow: 0.8 m wall-to-ground L pipe, origin at the top wall clamp (set z = ground + 0.76)
- CMP_Ground_Box: 0.32 x 0.22 x 0.21 m junction box, origin bottom centre
- CMP_Roller_Door: shutter housing, part-lowered slats, guide rails for a 3.8 x 3.4 m opening, origin bottom centre of opening
- CMP_Skylight_Curved: 2.5 x 2.8 m curved glass skylight for R=5 m arched roofs (rotate about Y by 90 - angle)
- CMP_Grass_Tuft: 5-blade tuft ~0.2 m for green roofs, origin at base
- CMP_Personnel_Door: 1.0 x 2.2 m steel door with frame (1.2 x 2.32), vision panel, push bar, kick plate
- CMP_Dino_Footprint: ~1.1 m three-toe footprint decal, toes point +Y

## Hangar (scene "Hangar" in Hangar.blend)
Arched 10 x 12 m hangar, 3 bays, R=5 m arch, slab top z=0.15. Front: roller door, hazard posts, sign, lamps, glow strip, utility cabinet with AC/vent/meter/pipes, windsock, ramp with footprint. Back: personnel door, 2 windows, lamp, attic vent, AC, meter. Left: 2 windows + vent on the timber band. Roof: 2 skylights, 16 solar panels, 70 grass tufts. ~17k triangles before bevels. Build script: text block hangar_lib.py.

## Game roles and sockets (added 4 Nov 2026)
Kit parts are upgrades or functional details, never the building's identity (see `Docs/BUILDING_IDENTITY.md`).
- Solar = power upgrade. AC unit = comfort upgrade for visitor buildings. Wall lamp = night safety. Meter box = grid connection. Vent louvre = required on food and service buildings. Window = night glow. Drain pipe = rain/service detail.
- Name sockets on every building shell: SOCKET_SolarPanel, SOCKET_ACUnit, SOCKET_MeterBox, SOCKET_WallLamp, SOCKET_Vent, SOCKET_Window.
- Hangar is now the V1 vehicle depot (barrel-vault roofline, only arched building). Souvenir shop and Hangar are not exported to Unity yet.
