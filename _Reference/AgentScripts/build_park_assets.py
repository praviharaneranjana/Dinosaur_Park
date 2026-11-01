import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler

# Base output paths
OUTPUT_DIR = r"D:\Unity Projects\Dinosaur_Park\Assets\Models"
BUILDINGS_DIR = os.path.join(OUTPUT_DIR, "Buildings")
ENCLOSURES_DIR = os.path.join(OUTPUT_DIR, "Enclosures")
PROPS_DIR = os.path.join(OUTPUT_DIR, "Props")
ROADS_DIR = os.path.join(OUTPUT_DIR, "Roads")

for d in [BUILDINGS_DIR, ENCLOSURES_DIR, PROPS_DIR, ROADS_DIR]:
    os.makedirs(d, exist_ok=True)

# -------------------------------------------------------------
# Material Management
# -------------------------------------------------------------
def get_or_create_material(name, color_rgba, metallic=0.0, roughness=0.5, emission_rgb=None, emission_strength=1.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color_rgba
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
        if emission_rgb:
            # Blender 4+ / 5+ emission color input
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = (*emission_rgb, 1.0)
                bsdf.inputs['Emission Strength'].default_value = emission_strength
            elif 'Emission' in bsdf.inputs:
                bsdf.inputs['Emission'].default_value = (*emission_rgb, 1.0)
    return mat

def setup_all_materials():
    # Palette definition from prompt document:
    # Off-white concrete (#F4EDD8)
    get_or_create_material("Mat_Concrete", (0.957, 0.929, 0.847, 1.0), metallic=0.0, roughness=0.85)
    # Timber slats (#C79A63)
    get_or_create_material("Mat_Timber", (0.780, 0.604, 0.388, 1.0), metallic=0.0, roughness=0.6)
    # Charcoal steel frames (#3B4743)
    get_or_create_material("Mat_CharcoalSteel", (0.231, 0.278, 0.263, 1.0), metallic=0.85, roughness=0.35)
    # Solid tinted teal glass (#8FCBCB)
    get_or_create_material("Mat_TealGlass", (0.561, 0.796, 0.796, 1.0), metallic=0.2, roughness=0.15)
    # Green living roof (#5E9B4A)
    get_or_create_material("Mat_LivingRoof", (0.369, 0.608, 0.290, 1.0), metallic=0.0, roughness=0.9)
    # Brass gold accent lights (#F2B84B)
    get_or_create_material("Mat_BrassGold", (0.949, 0.722, 0.294, 1.0), metallic=0.9, roughness=0.25, emission_rgb=(0.949, 0.722, 0.294), emission_strength=1.5)
    # Solar panel cell
    get_or_create_material("Mat_SolarPanel", (0.10, 0.16, 0.26, 1.0), metallic=0.5, roughness=0.2)
    # Amber glow for hatchery
    get_or_create_material("Mat_AmberGlow", (1.0, 0.65, 0.18, 1.0), metallic=0.1, roughness=0.2, emission_rgb=(1.0, 0.65, 0.18), emission_strength=3.0)
    # Road Asphalt
    get_or_create_material("Mat_RoadAsphalt", (0.18, 0.19, 0.20, 1.0), metallic=0.0, roughness=0.85)
    # Road Curbs / Markings
    get_or_create_material("Mat_RoadMarking", (0.85, 0.85, 0.82, 1.0), metallic=0.0, roughness=0.6)

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

def apply_mat(obj, mat_name):
    mat = bpy.data.materials.get(mat_name)
    if mat:
        if len(obj.data.materials) == 0:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat

def add_box(name, location, size, mat_name=None, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat_name:
        apply_mat(obj, mat_name)
    if parent:
        obj.parent = parent
    return obj

def add_cylinder(name, location, radius, depth, vertices=16, rotation=(0,0,0), mat_name=None, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=vertices, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat_name:
        apply_mat(obj, mat_name)
    if parent:
        obj.parent = parent
    return obj

# -------------------------------------------------------------
# Reusable Consistent Elements
# -------------------------------------------------------------
def create_standard_solar_panel(name, location, rotation=(0,0,0), parent=None):
    """
    Standardized solar panel unit: exactly 1.6m long x 1.0m wide x 0.05m thick.
    Ensures identical proportion across all small and large buildings.
    """
    # Outer frame
    frame = add_box(f"{name}_Frame", (0, 0, 0.02), (1.6, 1.0, 0.04), mat_name="Mat_CharcoalSteel")
    # Photovoltaic surface
    panel = add_box(f"{name}_Cells", (0, 0, 0.042), (1.52, 0.92, 0.01), mat_name="Mat_SolarPanel")
    panel.parent = frame
    
    # Sub-grid cells divider line
    line = add_box(f"{name}_Grid", (0, 0, 0.048), (0.02, 0.92, 0.005), mat_name="Mat_CharcoalSteel")
    line.parent = frame

    frame.location = location
    frame.rotation_euler = rotation
    if parent:
        frame.parent = parent
    return frame

def create_slat_panel(name, location, width, height, thickness=0.04, slat_count=8, parent=None):
    """Creates a modular timber slat screening wall."""
    container = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(container)
    container.location = location
    
    slat_w = (width / slat_count) * 0.7
    step = width / slat_count
    start_x = -width / 2.0 + step / 2.0
    for i in range(slat_count):
        x = start_x + i * step
        slat = add_box(f"{name}_slat_{i}", (x, 0, height/2.0), (slat_w, thickness, height), mat_name="Mat_Timber", parent=container)
    
    # Charcoal frame backer
    rail_top = add_box(f"{name}_rail_t", (0, 0, height - 0.03), (width, thickness * 1.5, 0.06), mat_name="Mat_CharcoalSteel", parent=container)
    rail_bot = add_box(f"{name}_rail_b", (0, 0, 0.03), (width, thickness * 1.5, 0.06), mat_name="Mat_CharcoalSteel", parent=container)
    
    if parent:
        container.parent = parent
    return container

# -------------------------------------------------------------
# 1. Entrance Gate (6 x 3 cells = 12m x 6m)
# -------------------------------------------------------------
def build_entrance_gate():
    clear_scene()
    setup_all_materials()
    root = bpy.data.objects.new("EntranceGate", None)
    bpy.context.scene.collection.objects.link(root)

    # Left Pylon with Ticket Pavilion (centered at X = -4.0m)
    pylon_l = add_box("Pylon_Left_Concrete", (-4.0, 0, 2.5), (3.0, 4.0, 5.0), mat_name="Mat_Concrete", parent=root)
    # Footprint relief on left pylon
    add_box("Pylon_L_Relief", (-5.52, 0, 2.5), (0.08, 1.2, 1.8), mat_name="Mat_CharcoalSteel", parent=root)

    # Right Pylon (angled cantilever support, centered at X = +4.0m)
    pylon_r = add_box("Pylon_Right_Concrete", (4.0, 0, 2.5), (2.4, 4.0, 5.0), mat_name="Mat_Concrete", parent=root)
    add_box("Pylon_R_Relief", (5.22, 0, 2.5), (0.08, 1.2, 1.8), mat_name="Mat_CharcoalSteel", parent=root)

    # Road Opening gap: between X = -2.5 and +2.8 (~5.3m clear vehicle roadway)
    
    # Ticket booth window inset into Left Pylon
    booth_win = add_box("TicketBooth_Window", (-2.48, 0, 2.2), (0.1, 2.4, 1.4), mat_name="Mat_TealGlass", parent=root)
    booth_shelf = add_box("TicketBooth_Counter", (-2.4, 0, 1.4), (0.4, 2.5, 0.1), mat_name="Mat_Timber", parent=root)
    
    # Timber slat accent band on ticket booth
    create_slat_panel("TicketBooth_Slats", (-2.5, 0, 0.2), width=2.4, height=1.1, slat_count=12, parent=root)
    create_slat_panel("TicketBooth_TopSlats", (-2.5, 0, 3.0), width=2.4, height=1.5, slat_count=12, parent=root)

    # Main Cantilevered Roof Canopy (12.4m wide x 6.2m deep x 0.8m thick) at Z = 5.2m
    canopy = add_box("Canopy_Slab", (0, 0, 5.2), (12.6, 6.2, 0.7), mat_name="Mat_Concrete", parent=root)
    # Living green roof top
    add_box("Canopy_GreenRoof", (0, 0, 5.6), (12.0, 5.6, 0.15), mat_name="Mat_LivingRoof", parent=root)
    # Front illuminated blank sign band
    add_box("Canopy_SignBand", (0, -3.12, 5.2), (11.6, 0.1, 0.5), mat_name="Mat_Concrete", parent=root)
    add_box("Canopy_SignFrame", (0, -3.14, 5.2), (11.8, 0.05, 0.55), mat_name="Mat_CharcoalSteel", parent=root)

    # Standardized Solar Panels on the roof (1.6m x 1.0m each, standard ratio!)
    for i in range(4):
        x_pos = -2.7 + i * 1.8
        create_standard_solar_panel(f"Roof_Solar_{i}", (x_pos, 0.5, 5.7), rotation=(math.radians(10), 0, 0), parent=root)

    # Gold Accent Lighting trim
    add_box("Trim_Gold_L", (-4.0, 0, 4.8), (3.05, 4.05, 0.08), mat_name="Mat_BrassGold", parent=root)
    add_box("Trim_Gold_R", (4.0, 0, 4.8), (2.45, 4.05, 0.08), mat_name="Mat_BrassGold", parent=root)

    # Interactive Ticket Pavilion Door (rear side of Left Pylon at Y = 2.0m, X = -3.8m)
    # Pivot point at hinge (X = -3.3, Y = 2.01, Z = 0)
    door_obj = add_box("Door_TicketPavilion", (-3.8, 2.02, 1.1), (0.9, 0.06, 2.2), mat_name="Mat_CharcoalSteel")
    # Door handle
    handle = add_box("Door_Handle", (-4.15, 2.06, 1.1), (0.05, 0.08, 0.25), mat_name="Mat_BrassGold", parent=door_obj)
    # Set door origin to right hinge (X = -3.35, Y = 2.02, Z = 0.0)
    bpy.context.view_layer.objects.active = door_obj
    bpy.ops.object.select_all(action='DESELECT')
    door_obj.select_set(True)
    # Move cursor to hinge
    bpy.context.scene.cursor.location = (-3.35, 2.02, 0.0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    door_obj.parent = root

    # Export FBX
    fbx_path = os.path.join(BUILDINGS_DIR, "EntranceGate.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported:", fbx_path)

# -------------------------------------------------------------
# 2. Hatchery (Egg Lab) (5 x 5 cells = 10m x 10m)
# -------------------------------------------------------------
def build_hatchery():
    clear_scene()
    setup_all_materials()
    root = bpy.data.objects.new("Hatchery", None)
    bpy.context.scene.collection.objects.link(root)

    # Base Charcoal Ring Footing (10.2m diameter, 0.5m height)
    add_cylinder("Base_Ring", (0, 0, 0.25), radius=5.1, depth=0.5, vertices=32, mat_name="Mat_CharcoalSteel", parent=root)

    # Lower Wall (Timber slat and concrete cylinder)
    add_cylinder("Lower_Wall_Concrete", (0, 0, 1.5), radius=4.8, depth=2.0, vertices=32, mat_name="Mat_Concrete", parent=root)
    # Continuous tinted teal window ring ribbon (Z: 2.5 to 3.7)
    add_cylinder("Window_Ribbon", (0, 0, 3.1), radius=4.6, depth=1.2, vertices=32, mat_name="Mat_TealGlass", parent=root)

    # Upper Dome Shell (smooth concrete)
    add_cylinder("Upper_Wall", (0, 0, 4.0), radius=4.3, depth=0.6, vertices=32, mat_name="Mat_Concrete", parent=root)
    # Central smooth dome
    bpy.ops.mesh.primitive_uv_sphere_add(radius=4.0, location=(0, 0, 3.0), segments=32, ring_count=16)
    dome = bpy.context.active_object
    dome.name = "Dome_Top"
    dome.scale = (1.0, 1.0, 0.55)
    bpy.ops.object.transform_apply(scale=True)
    apply_mat(dome, "Mat_Concrete")
    dome.location = (0, 0, 3.2)
    dome.parent = root

    # Glowing Amber Accent Trim Ring
    add_cylinder("Trim_AmberGlow", (0, 0, 2.5), radius=4.85, depth=0.08, vertices=32, mat_name="Mat_AmberGlow", parent=root)

    # Green living roof ring on terrace perimeter
    add_cylinder("LivingRoof_Terrace", (0, 0, 4.4), radius=3.8, depth=0.1, vertices=32, mat_name="Mat_LivingRoof", parent=root)

    # 3 Large Egg-Shaped Skylights on Roof with warm amber glow
    for idx, angle_deg in enumerate([60, 180, 300]):
        rad = math.radians(angle_deg)
        dist = 2.4
        x = math.cos(rad) * dist
        y = math.sin(rad) * dist
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.75, location=(x, y, 4.7), segments=16, ring_count=12)
        skylight = bpy.context.active_object
        skylight.name = f"Egg_Skylight_{idx}"
        skylight.scale = (0.9, 0.9, 1.3)
        bpy.ops.object.transform_apply(scale=True)
        skylight.rotation_euler = (math.radians(20) * math.sin(rad), -math.radians(20) * math.cos(rad), 0)
        apply_mat(skylight, "Mat_AmberGlow")
        skylight.parent = root

    # Solar Panels: Exact same standard 1.6m x 1.0m modular panels as other buildings!
    for idx, angle_deg in enumerate([0, 120, 240]):
        rad = math.radians(angle_deg)
        dist = 2.9
        x = math.cos(rad) * dist
        y = math.sin(rad) * dist
        create_standard_solar_panel(f"Hatchery_Solar_{idx}", (x, y, 4.6), rotation=(math.radians(15), 0, rad), parent=root)

    # Entrance Portal (Front at Y = -4.8m)
    portal = add_box("Entrance_Portal", (0, -4.9, 1.5), (3.6, 0.8, 3.0), mat_name="Mat_Concrete", parent=root)
    # Timber side accents
    add_box("Portal_Timber_L", (-1.9, -4.9, 1.5), (0.3, 0.85, 2.9), mat_name="Mat_Timber", parent=root)
    add_box("Portal_Timber_R", (1.9, -4.9, 1.5), (0.3, 0.85, 2.9), mat_name="Mat_Timber", parent=root)
    # Blank Sign board
    add_box("Hatchery_SignBoard", (0, -5.35, 2.8), (2.8, 0.08, 0.5), mat_name="Mat_Concrete", parent=root)

    # Interactive Sliding Curved Double Doors
    # Left Door leaf (slides in -X direction)
    door_l = add_box("Hatchery_Door_L", (-0.75, -4.88, 1.2), (1.4, 0.08, 2.4), mat_name="Mat_TealGlass")
    door_frame_l = add_box("Door_L_Frame", (-0.75, -4.88, 1.2), (1.42, 0.09, 2.42), mat_name="Mat_CharcoalSteel", parent=door_l)
    door_l.parent = root

    # Right Door leaf (slides in +X direction)
    door_r = add_box("Hatchery_Door_R", (0.75, -4.88, 1.2), (1.4, 0.08, 2.4), mat_name="Mat_TealGlass")
    door_frame_r = add_box("Door_R_Frame", (0.75, -4.88, 1.2), (1.42, 0.09, 2.42), mat_name="Mat_CharcoalSteel", parent=door_r)
    door_r.parent = root

    fbx_path = os.path.join(BUILDINGS_DIR, "Hatchery.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported:", fbx_path)

# -------------------------------------------------------------
# 3. Canteen (4 x 3 cells = 8m x 6m)
# -------------------------------------------------------------
def build_canteen():
    clear_scene()
    setup_all_materials()
    root = bpy.data.objects.new("Canteen", None)
    bpy.context.scene.collection.objects.link(root)

    # Base slab
    add_box("Canteen_BaseSlab", (0, 0, 0.1), (8.2, 6.2, 0.2), mat_name="Mat_Concrete", parent=root)

    # Enclosed main structure (back half of the footprint, Y: 0 to 2.8)
    main_body = add_box("Canteen_MainBody", (0, 1.2, 1.8), (7.6, 3.4, 3.2), mat_name="Mat_Concrete", parent=root)
    # Timber slat cladding on side walls
    create_slat_panel("Canteen_Slats_Left", (-3.85, 1.2, 0.2), width=3.2, height=3.0, slat_count=12, parent=root)
    create_slat_panel("Canteen_Slats_Right", (3.85, 1.2, 0.2), width=3.2, height=3.0, slat_count=12, parent=root)

    # Front glass facade & counter (Y = -0.5)
    counter = add_box("Serving_Counter", (0, -0.6, 0.6), (6.0, 0.8, 1.0), mat_name="Mat_Timber", parent=root)
    counter_top = add_box("Serving_Counter_Top", (0, -0.6, 1.12), (6.2, 0.9, 0.08), mat_name="Mat_CharcoalSteel", parent=root)
    
    # Floor-to-ceiling teal glass panels above counter
    add_box("Front_Glass_Facade", (0, -0.2, 2.4), (7.4, 0.1, 1.6), mat_name="Mat_TealGlass", parent=root)
    add_box("Glass_Frames", (0, -0.2, 2.4), (7.45, 0.14, 1.65), mat_name="Mat_CharcoalSteel", parent=root)

    # Menu boards above counter
    for i in range(3):
        x = -1.8 + i * 1.8
        add_box(f"Menu_Board_{i}", (x, -0.7, 2.6), (1.4, 0.06, 0.6), mat_name="Mat_Concrete", parent=root)

    # Cantilevered Roof Canopy (overhangs the front seating area, Y: -3.0 to 3.0)
    canopy = add_box("Canteen_Roof_Canopy", (0, -0.3, 3.5), (8.4, 6.4, 0.4), mat_name="Mat_Concrete", parent=root)
    add_box("Roof_LivingGreen", (0, 0.5, 3.75), (7.8, 3.6, 0.12), mat_name="Mat_LivingRoof", parent=root)

    # 4 Outdoor dining tables with stools attached under front canopy (Y = -2.0)
    for i in range(4):
        tx = -2.8 + i * 1.85
        # Table
        table = add_box(f"Table_{i}", (tx, -2.1, 0.5), (0.9, 0.9, 0.08), mat_name="Mat_Timber", parent=root)
        table_leg = add_cylinder(f"Table_Leg_{i}", (tx, -2.1, 0.25), radius=0.06, depth=0.5, mat_name="Mat_CharcoalSteel", parent=root)
        # Stools
        stool_1 = add_cylinder(f"Stool_{i}_A", (tx, -2.7, 0.25), radius=0.2, depth=0.06, mat_name="Mat_Timber", parent=root)
        add_cylinder(f"Stool_Leg_{i}_A", (tx, -2.7, 0.12), radius=0.04, depth=0.24, mat_name="Mat_CharcoalSteel", parent=root)
        stool_2 = add_cylinder(f"Stool_{i}_B", (tx, -1.5, 0.25), radius=0.2, depth=0.06, mat_name="Mat_Timber", parent=root)
        add_cylinder(f"Stool_Leg_{i}_B", (tx, -1.5, 0.12), radius=0.04, depth=0.24, mat_name="Mat_CharcoalSteel", parent=root)

    # Standard Solar Panels (1.6m x 1.0m, identical proportion!)
    for i in range(3):
        x = -2.0 + i * 2.0
        create_standard_solar_panel(f"Canteen_Solar_{i}", (x, 0.5, 3.9), rotation=(math.radians(10), 0, 0), parent=root)

    # Interactive Staff Door at rear/side (X = 3.82, Y = 1.2)
    door = add_box("Canteen_StaffDoor", (3.82, 1.2, 1.1), (0.08, 1.0, 2.2), mat_name="Mat_CharcoalSteel")
    handle = add_box("Canteen_Door_Handle", (3.88, 0.85, 1.1), (0.08, 0.04, 0.2), mat_name="Mat_BrassGold", parent=door)
    # Set door hinge pivot to rear edge (Y = 1.7)
    bpy.context.view_layer.objects.active = door
    bpy.ops.object.select_all(action='DESELECT')
    door.select_set(True)
    bpy.context.scene.cursor.location = (3.82, 1.7, 0.0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    door.parent = root

    fbx_path = os.path.join(BUILDINGS_DIR, "Canteen.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported:", fbx_path)

# -------------------------------------------------------------
# 4. Automatic Enclosure Double Gate (2 cells wide = 4m x 3.5m tall)
# -------------------------------------------------------------
def build_automatic_gate():
    clear_scene()
    setup_all_materials()
    root = bpy.data.objects.new("AutomaticGate", None)
    bpy.context.scene.collection.objects.link(root)

    # Ground concrete footing & steel sliding track
    add_box("Gate_Footing", (0, 0, 0.15), (4.4, 0.8, 0.3), mat_name="Mat_Concrete", parent=root)
    add_box("Gate_Slide_Track", (0, 0, 0.32), (4.3, 0.2, 0.05), mat_name="Mat_CharcoalSteel", parent=root)

    # Left Concrete Pylon (X = -1.9m, 3.5m tall)
    pylon_l = add_box("Pylon_Left", (-1.9, 0, 1.8), (0.6, 0.7, 3.3), mat_name="Mat_Concrete", parent=root)
    # Sensor pod on Left Pylon
    add_box("Sensor_Pod_L", (-1.9, -0.38, 2.6), (0.25, 0.12, 0.3), mat_name="Mat_CharcoalSteel", parent=pylon_l)
    # Gold Safety Beacon on top of Left Pylon
    add_cylinder("Beacon_Light_L", (-1.9, 0, 3.6), radius=0.18, depth=0.3, mat_name="Mat_BrassGold", parent=pylon_l)

    # Right Concrete Pylon (X = +1.9m, 3.5m tall)
    pylon_r = add_box("Pylon_Right", (1.9, 0, 1.8), (0.6, 0.7, 3.3), mat_name="Mat_Concrete", parent=root)
    # Sensor pod on Right Pylon
    add_box("Sensor_Pod_R", (1.9, -0.38, 2.6), (0.25, 0.12, 0.3), mat_name="Mat_CharcoalSteel", parent=pylon_r)
    # Gold Safety Beacon on top of Right Pylon
    add_cylinder("Beacon_Light_R", (1.9, 0, 3.6), radius=0.18, depth=0.3, mat_name="Mat_BrassGold", parent=pylon_r)

    # Left Sliding Gate Leaf: spans X = -1.6m to -0.02m (1.58m wide x 3.0m tall)
    # Moves in -X direction when opening
    gate_l = add_box("AutoGate_Door_L", (-0.8, 0, 1.8), (1.58, 0.15, 2.8), mat_name="Mat_CharcoalSteel")
    # Vertical chunky bars inside left gate
    for i in range(5):
        bx = -0.55 + i * 0.28
        add_box(f"Gate_L_Bar_{i}", (bx, 0, 0), (0.06, 0.1, 2.5), mat_name="Mat_CharcoalSteel", parent=gate_l)
    # Teal viewing accent panel on gate
    add_box("Gate_L_TealAccent", (0.5, 0, 0.2), (0.35, 0.08, 2.0), mat_name="Mat_TealGlass", parent=gate_l)
    gate_l.parent = root

    # Right Sliding Gate Leaf: spans X = 0.02m to 1.6m (1.58m wide x 3.0m tall)
    # Moves in +X direction when opening
    gate_r = add_box("AutoGate_Door_R", (0.8, 0, 1.8), (1.58, 0.15, 2.8), mat_name="Mat_CharcoalSteel")
    for i in range(5):
        bx = -0.55 + i * 0.28
        add_box(f"Gate_R_Bar_{i}", (bx, 0, 0), (0.06, 0.1, 2.5), mat_name="Mat_CharcoalSteel", parent=gate_r)
    # Teal viewing accent panel on gate
    add_box("Gate_R_TealAccent", (-0.5, 0, 0.2), (0.35, 0.08, 2.0), mat_name="Mat_TealGlass", parent=gate_r)
    gate_r.parent = root

    fbx_path = os.path.join(ENCLOSURES_DIR, "AutomaticGate.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported:", fbx_path)

# -------------------------------------------------------------
# 5. Enclosure Fence Straight (1 cell = 2.0m long x 3.0m tall)
# -------------------------------------------------------------
def build_fence_straight():
    clear_scene()
    setup_all_materials()
    root = bpy.data.objects.new("Fence_Straight_2m", None)
    bpy.context.scene.collection.objects.link(root)

    # Concrete footing block (2.0m x 0.5m x 0.4m)
    add_box("Fence_Footing", (0, 0, 0.2), (2.0, 0.5, 0.4), mat_name="Mat_Concrete", parent=root)

    # Two thick charcoal steel posts at ends (X = -0.95m, +0.95m)
    add_box("Post_L", (-0.95, 0, 1.6), (0.16, 0.2, 2.8), mat_name="Mat_CharcoalSteel", parent=root)
    add_box("Post_R", (0.95, 0, 1.6), (0.16, 0.2, 2.8), mat_name="Mat_CharcoalSteel", parent=root)

    # Top & Mid & Bottom steel rails
    add_box("Rail_Top", (0, 0, 2.9), (1.9, 0.14, 0.12), mat_name="Mat_CharcoalSteel", parent=root)
    add_box("Rail_Mid", (0, 0, 1.8), (1.9, 0.12, 0.08), mat_name="Mat_CharcoalSteel", parent=root)
    add_box("Rail_Bot", (0, 0, 0.45), (1.9, 0.14, 0.10), mat_name="Mat_CharcoalSteel", parent=root)

    # Thick vertical steel bars
    for i in range(9):
        x = -0.75 + i * 0.185
        add_box(f"Vertical_Bar_{i}", (x, 0, 1.65), (0.05, 0.08, 2.4), mat_name="Mat_CharcoalSteel", parent=root)

    # Row of warm gold light caps along the top rail
    for i in range(7):
        x = -0.65 + i * 0.215
        add_box(f"Gold_Light_Cap_{i}", (x, 0, 3.02), (0.12, 0.15, 0.08), mat_name="Mat_BrassGold", parent=root)

    # Solid tinted teal accent strip below top rail
    add_box("Teal_Viewing_Strip", (0, 0, 2.65), (1.8, 0.05, 0.35), mat_name="Mat_TealGlass", parent=root)

    fbx_path = os.path.join(ENCLOSURES_DIR, "Fence_Straight_2m.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported:", fbx_path)

# -------------------------------------------------------------
# 6. Enclosure Fence Corner Post
# -------------------------------------------------------------
def build_fence_corner():
    clear_scene()
    setup_all_materials()
    root = bpy.data.objects.new("Fence_Corner_Post", None)
    bpy.context.scene.collection.objects.link(root)

    # Square concrete footing
    add_box("Corner_Footing", (0, 0, 0.25), (0.7, 0.7, 0.5), mat_name="Mat_Concrete", parent=root)

    # Tall extra-thick charcoal steel post (3.4m tall)
    add_box("Corner_Post_Steel", (0, 0, 1.8), (0.3, 0.3, 3.2), mat_name="Mat_CharcoalSteel", parent=root)

    # Rounded gold light cap on top
    add_cylinder("Beacon_Gold_Cap", (0, 0, 3.5), radius=0.18, depth=0.25, mat_name="Mat_BrassGold", parent=root)
    # Security camera pod
    add_box("Security_Camera_Pod", (0.15, 0.15, 3.2), (0.16, 0.16, 0.14), mat_name="Mat_CharcoalSteel", parent=root)

    # Two 90-degree steel rail stubs to connect cleanly to fence segments
    add_box("Rail_Stub_X", (0.25, 0, 2.9), (0.3, 0.12, 0.12), mat_name="Mat_CharcoalSteel", parent=root)
    add_box("Rail_Stub_Y", (0, 0.25, 2.9), (0.12, 0.3, 0.12), mat_name="Mat_CharcoalSteel", parent=root)

    fbx_path = os.path.join(ENCLOSURES_DIR, "Fence_Corner_Post.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported:", fbx_path)

# -------------------------------------------------------------
# 7. Modern Park Recycling Bin (0.9m tall)
# -------------------------------------------------------------
def build_recycling_bin():
    clear_scene()
    setup_all_materials()
    root = bpy.data.objects.new("RecyclingBin", None)
    bpy.context.scene.collection.objects.link(root)

    # Concrete footing base (0.15m height)
    add_box("Bin_Base", (0, 0, 0.08), (0.85, 0.45, 0.16), mat_name="Mat_Concrete", parent=root)

    # Charcoal Steel chassis frame (0.9m tall)
    add_box("Bin_Frame", (0, 0, 0.52), (0.84, 0.42, 0.74), mat_name="Mat_CharcoalSteel", parent=root)

    # Light timber slat front panel
    create_slat_panel("Bin_TimberFront", (0, -0.22, 0.16), width=0.76, height=0.64, slat_count=8, parent=root)

    # Top sorting openings (Green = Organic, Teal = Plastic/Cans, Gold = Paper/Glass)
    get_or_create_material("Mat_Bin_Green", (0.25, 0.70, 0.35, 1.0), roughness=0.3)
    get_or_create_material("Mat_Bin_Teal", (0.25, 0.75, 0.75, 1.0), roughness=0.3)
    get_or_create_material("Mat_Bin_Gold", (0.95, 0.75, 0.20, 1.0), roughness=0.3)

    for idx, (x, mat_c) in enumerate([(-0.25, "Mat_Bin_Green"), (0.0, "Mat_Bin_Teal"), (0.25, "Mat_Bin_Gold")]):
        # Ring rim
        add_cylinder(f"Aperture_Rim_{idx}", (x, 0, 0.90), radius=0.09, depth=0.03, mat_name=mat_c, parent=root)
        # Recessed slot hole
        add_cylinder(f"Aperture_Slot_{idx}", (x, 0, 0.89), radius=0.07, depth=0.05, mat_name="Mat_CharcoalSteel", parent=root)

    fbx_path = os.path.join(PROPS_DIR, "RecyclingBin.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported:", fbx_path)

# -------------------------------------------------------------
# 8. Modular Roads & Pathways (2 cells = 4m wide)
# -------------------------------------------------------------
def build_modular_roads():
    # Straight Road (4m wide x 4m long = 2x2 cells)
    clear_scene()
    setup_all_materials()
    root_s = bpy.data.objects.new("ModularRoad_Straight", None)
    bpy.context.scene.collection.objects.link(root_s)

    # Asphalt Surface (4.0m x 4.0m, Z = 0.05)
    add_box("Road_Surface", (0, 0, 0.025), (4.0, 4.0, 0.05), mat_name="Mat_RoadAsphalt", parent=root_s)
    # Curbs on left and right (X = -1.9, +1.9)
    add_box("Curb_L", (-1.9, 0, 0.06), (0.2, 4.0, 0.12), mat_name="Mat_Concrete", parent=root_s)
    add_box("Curb_R", (1.9, 0, 0.06), (0.2, 4.0, 0.12), mat_name="Mat_Concrete", parent=root_s)
    # Brass/Gold embedded lane marking dashes
    for y in [-1.2, 0.0, 1.2]:
        add_box(f"Lane_Marking_{y}", (0, y, 0.052), (0.12, 0.6, 0.005), mat_name="Mat_BrassGold", parent=root_s)

    fbx_path = os.path.join(ROADS_DIR, "ModularRoad_Straight.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported:", fbx_path)

    # 4-Way Road Intersection (4m x 4m)
    clear_scene()
    setup_all_materials()
    root_x = bpy.data.objects.new("ModularRoad_Cross", None)
    bpy.context.scene.collection.objects.link(root_x)
    add_box("Cross_Surface", (0, 0, 0.025), (4.0, 4.0, 0.05), mat_name="Mat_RoadAsphalt", parent=root_x)
    # 4 Corner curb blocks
    for cx, cy in [(-1.9, -1.9), (-1.9, 1.9), (1.9, -1.9), (1.9, 1.9)]:
        add_box(f"Corner_Curb_{cx}_{cy}", (cx, cy, 0.06), (0.2, 0.2, 0.12), mat_name="Mat_Concrete", parent=root_x)
    # Center round brass disc emblem
    add_cylinder("Center_Emblem", (0, 0, 0.052), radius=0.35, depth=0.005, mat_name="Mat_BrassGold", parent=root_x)

    fbx_path = os.path.join(ROADS_DIR, "ModularRoad_Cross.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported:", fbx_path)

# -------------------------------------------------------------
# Main Execution
# -------------------------------------------------------------
if __name__ == "__main__":
    print("=== BUILDING CORE PARK ASSETS IN BLENDER ===")
    build_entrance_gate()
    build_hatchery()
    build_canteen()
    build_automatic_gate()
    build_fence_straight()
    build_fence_corner()
    build_recycling_bin()
    build_modular_roads()
    print("=== ALL ASSETS GENERATED AND EXPORTED SUCCESSFULLY ===")
