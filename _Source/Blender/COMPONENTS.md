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
