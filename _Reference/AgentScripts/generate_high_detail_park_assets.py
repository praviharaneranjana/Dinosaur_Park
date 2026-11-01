import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler

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
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = (*emission_rgb, 1.0)
                bsdf.inputs['Emission Strength'].default_value = emission_strength
            elif 'Emission' in bsdf.inputs:
                bsdf.inputs['Emission'].default_value = (*emission_rgb, 1.0)
    return mat

def setup_materials():
    get_or_create_material("Mat_Concrete", (0.957, 0.929, 0.847, 1.0), metallic=0.0, roughness=0.82)
    get_or_create_material("Mat_Timber", (0.780, 0.604, 0.388, 1.0), metallic=0.0, roughness=0.55)
    get_or_create_material("Mat_CharcoalSteel", (0.231, 0.278, 0.263, 1.0), metallic=0.88, roughness=0.32)
    get_or_create_material("Mat_TealGlass", (0.561, 0.796, 0.796, 1.0), metallic=0.2, roughness=0.12)
    get_or_create_material("Mat_LivingRoof", (0.369, 0.608, 0.290, 1.0), metallic=0.0, roughness=0.9)
    get_or_create_material("Mat_BrassGold", (0.949, 0.722, 0.294, 1.0), metallic=0.92, roughness=0.22, emission_rgb=(0.949, 0.722, 0.294), emission_strength=1.6)
    get_or_create_material("Mat_SolarPanel", (0.10, 0.16, 0.26, 1.0), metallic=0.6, roughness=0.18)
    get_or_create_material("Mat_AmberGlow", (1.0, 0.65, 0.18, 1.0), metallic=0.1, roughness=0.2, emission_rgb=(1.0, 0.65, 0.18), emission_strength=3.2)
    get_or_create_material("Mat_RoadAsphalt", (0.18, 0.19, 0.20, 1.0), metallic=0.0, roughness=0.88)
    get_or_create_material("Mat_RoadYellow", (0.92, 0.75, 0.15, 1.0), metallic=0.0, roughness=0.6)
    get_or_create_material("Mat_RoadWhite", (0.90, 0.90, 0.88, 1.0), metallic=0.0, roughness=0.6)
    get_or_create_material("Mat_SoilDark", (0.24, 0.19, 0.14, 1.0), metallic=0.0, roughness=0.95)
    get_or_create_material("Mat_FoliageBush", (0.28, 0.52, 0.22, 1.0), metallic=0.0, roughness=0.8)
    get_or_create_material("Mat_HVAC_Grey", (0.45, 0.47, 0.48, 1.0), metallic=0.5, roughness=0.45)
    get_or_create_material("Mat_ParasolFabric", (0.92, 0.88, 0.78, 1.0), metallic=0.0, roughness=0.75)
    get_or_create_material("Mat_Bin_Green", (0.22, 0.68, 0.32, 1.0), roughness=0.3)
    get_or_create_material("Mat_Bin_Teal", (0.22, 0.72, 0.72, 1.0), roughness=0.3)
    get_or_create_material("Mat_Bin_Gold", (0.92, 0.72, 0.18, 1.0), roughness=0.3)

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

def add_box(name, location, size, mat_name=None, parent=None, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
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

def add_bevel_modifier(obj, width=0.03, segments=2):
    mod = obj.modifiers.new(name="Bevel", type='BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(35)

# -------------------------------------------------------------
# Detailed Architectural Sub-components
# -------------------------------------------------------------
def create_detailed_solar_panel(name, location, rotation=(0,0,0), parent=None):
    """
    Standard modular 1.6m x 1.0m solar panel with mounting rack,
    beveled charcoal aluminum frame, sub-grid cells, and junction box.
    """
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    root.location = location
    root.rotation_euler = rotation

    # Frame
    frame = add_box(f"{name}_Frame", (0, 0, 0.04), (1.6, 1.0, 0.05), mat_name="Mat_CharcoalSteel", parent=root)
    # Glass Photovoltaic Cells
    cells = add_box(f"{name}_Cells", (0, 0, 0.062), (1.52, 0.92, 0.012), mat_name="Mat_SolarPanel", parent=root)
    # Busbars / Grid Dividers
    add_box(f"{name}_Grid_V", (0, 0, 0.069), (0.015, 0.92, 0.005), mat_name="Mat_CharcoalSteel", parent=root)
    add_box(f"{name}_Grid_H1", (-0.38, 0, 0.069), (0.74, 0.012, 0.005), mat_name="Mat_CharcoalSteel", parent=root)
    add_box(f"{name}_Grid_H2", (0.38, 0, 0.069), (0.74, 0.012, 0.005), mat_name="Mat_CharcoalSteel", parent=root)
    
    # Mounting Tilt Legs
    add_box(f"{name}_Leg_L", (-0.6, -0.3, -0.05), (0.05, 0.05, 0.18), mat_name="Mat_CharcoalSteel", parent=root)
    add_box(f"{name}_Leg_R", (0.6, -0.3, -0.05), (0.05, 0.05, 0.18), mat_name="Mat_CharcoalSteel", parent=root)

    if parent:
        root.parent = parent
    return root

def create_hvac_chiller_unit(name, location, size=(1.4, 0.9, 0.7), parent=None):
    """Rooftop air conditioning / ventilation chiller unit with fan grilles."""
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    root.location = location

    # Main Cabinet
    cab = add_box(f"{name}_Cab", (0, 0, size[2]/2.0), size, mat_name="Mat_HVAC_Grey", parent=root)
    # Fan Grille 1
    add_cylinder(f"{name}_Fan1", (-size[0]*0.24, 0, size[2] + 0.02), radius=size[1]*0.32, depth=0.04, vertices=16, mat_name="Mat_CharcoalSteel", parent=root)
    # Fan Grille 2
    add_cylinder(f"{name}_Fan2", (size[0]*0.24, 0, size[2] + 0.02), radius=size[1]*0.32, depth=0.04, vertices=16, mat_name="Mat_CharcoalSteel", parent=root)
    # Side Louvres
    add_box(f"{name}_Louvre", (0, size[1]/2.0 + 0.01, size[2]*0.5), (size[0]*0.8, 0.02, size[2]*0.6), mat_name="Mat_CharcoalSteel", parent=root)

    if parent:
        root.parent = parent
    return root

def create_timber_slat_facade(name, location, width, height, slat_w=0.07, gap=0.03, depth=0.04, parent=None):
    """Generates realistic slatted timber screening."""
    container = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(container)
    container.location = location

    pitch = slat_w + gap
    count = int(width / pitch)
    start_x = -((count - 1) * pitch) / 2.0

    for i in range(count):
        x = start_x + i * pitch
        add_box(f"{name}_slat_{i}", (x, 0, height/2.0), (slat_w, depth, height), mat_name="Mat_Timber", parent=container)

    # Top & bottom retaining rails
    add_box(f"{name}_rail_t", (0, 0, height - 0.025), (width, depth*1.4, 0.05), mat_name="Mat_CharcoalSteel", parent=container)
    add_box(f"{name}_rail_b", (0, 0, 0.025), (width, depth*1.4, 0.05), mat_name="Mat_CharcoalSteel", parent=container)

    if parent:
        container.parent = parent
    return container

def create_umbrella_table(name, location, parent=None):
    """Detailed cafe dining set: Round timber table, 4 chairs, and open parasol umbrella."""
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    root.location = location

    # Center Pedestal Table
    add_cylinder(f"{name}_Base", (0, 0, 0.04), radius=0.35, depth=0.04, mat_name="Mat_CharcoalSteel", parent=root)
    add_cylinder(f"{name}_Pole", (0, 0, 0.42), radius=0.04, depth=0.76, mat_name="Mat_CharcoalSteel", parent=root)
    add_cylinder(f"{name}_TableTop", (0, 0, 0.8), radius=0.65, depth=0.06, vertices=20, mat_name="Mat_Timber", parent=root)

    # Parasol Umbrella
    add_cylinder(f"{name}_UmbrellaPole", (0, 0, 1.5), radius=0.025, depth=1.6, mat_name="Mat_Timber", parent=root)
    bpy.ops.mesh.primitive_cone_add(radius1=1.25, depth=0.45, vertices=16, location=(0, 0, 2.35))
    cone = bpy.context.active_object
    cone.name = f"{name}_Canopy"
    cone.rotation_euler = (math.radians(180), 0, 0)
    apply_mat(cone, "Mat_ParasolFabric")
    cone.parent = root

    # 4 Cafe Chairs
    for i in range(4):
        ang = math.radians(i * 90 + 45)
        cx = math.cos(ang) * 0.95
        cy = math.sin(ang) * 0.95
        # Seat
        add_cylinder(f"{name}_ChairSeat_{i}", (cx, cy, 0.45), radius=0.22, depth=0.04, mat_name="Mat_Timber", parent=root)
        # Legs
        add_cylinder(f"{name}_ChairLeg_{i}", (cx, cy, 0.22), radius=0.03, depth=0.44, mat_name="Mat_CharcoalSteel", parent=root)
        # Curved Backrest
        bx = math.cos(ang) * 1.12
        by = math.sin(ang) * 1.12
        add_box(f"{name}_ChairBack_{i}", (bx, by, 0.65), (0.32, 0.04, 0.3), rotation=(0, 0, ang), mat_name="Mat_Timber", parent=root)

    if parent:
        root.parent = parent
    return root

# -------------------------------------------------------------
# 1. Entrance Gate & Ticket Pavilion (High Detail)
# -------------------------------------------------------------
def build_entrance_gate():
    clear_scene()
    setup_materials()
    root = bpy.data.objects.new("EntranceGate", None)
    bpy.context.scene.collection.objects.link(root)

    # Left Pylon: Tapered concrete with ticket booth cavity
    pylon_l = add_box("Pylon_Left_Concrete", (-4.2, 0, 2.6), (2.8, 4.4, 5.2), mat_name="Mat_Concrete", parent=root)
    # Embossed Dino Footprints on left pylon
    add_box("Dino_Footprint_L1", (-5.62, 0.6, 2.2), (0.05, 0.6, 0.7), mat_name="Mat_CharcoalSteel", parent=root)
    add_box("Dino_Footprint_L2", (-5.62, -0.6, 3.4), (0.05, 0.6, 0.7), mat_name="Mat_CharcoalSteel", parent=root)

    # Right Pylon: Angled trapezoid concrete
    pylon_r = add_box("Pylon_Right_Concrete", (4.2, 0, 2.6), (2.4, 4.4, 5.2), mat_name="Mat_Concrete", parent=root)
    add_box("Dino_Footprint_R1", (5.42, 0.4, 2.8), (0.05, 0.6, 0.7), mat_name="Mat_CharcoalSteel", parent=root)

    # Ticket Booth embedded in Left Pylon (facing road, X: -2.8 to -1.5, Y: -1.4 to 1.4)
    booth_base = add_box("TicketBooth_Plinth", (-2.7, 0, 0.6), (1.4, 2.8, 1.2), mat_name="Mat_Concrete", parent=root)
    create_timber_slat_facade("TicketBooth_LowerSlats", (-2.68, 0, 0.05), width=2.6, height=1.1, depth=0.03, parent=root)

    # Wrap-around Teal Glass Window with Steel Frame & Pass-through shelf
    add_box("TicketBooth_Glass", (-2.65, 0, 1.8), (0.08, 2.4, 1.2), mat_name="Mat_TealGlass", parent=root)
    add_box("TicketBooth_Mullion_V1", (-2.62, -0.8, 1.8), (0.12, 0.06, 1.25), mat_name="Mat_CharcoalSteel", parent=root)
    add_box("TicketBooth_Mullion_V2", (-2.62, 0.8, 1.8), (0.12, 0.06, 1.25), mat_name="Mat_CharcoalSteel", parent=root)
    add_box("TicketBooth_Counter", (-2.5, 0, 1.2), (0.45, 2.6, 0.08), mat_name="Mat_Timber", parent=root)
    # Upper timber transom slats
    create_timber_slat_facade("TicketBooth_UpperSlats", (-2.68, 0, 2.5), width=2.6, height=1.8, depth=0.03, parent=root)

    # Main Sweeping Cantilevered Roof Canopy (13.6m wide x 6.8m deep x 0.85m thick)
    canopy = add_box("Canopy_Slab", (0, 0, 5.4), (13.6, 6.8, 0.85), mat_name="Mat_Concrete", parent=root)
    # Fascia Trim & Recessed Living Roof Bed
    add_box("Canopy_LivingRoof", (0, 0, 5.85), (13.0, 6.2, 0.16), mat_name="Mat_LivingRoof", parent=root)

    # Grand Dimensional Front Signboard: "DINO PARK" 3D Sign Banner
    add_box("Sign_BackingPlate", (0, -3.42, 5.4), (12.2, 0.1, 0.75), mat_name="Mat_CharcoalSteel", parent=root)
    add_box("Sign_Frame_Gold", (0, -3.43, 5.4), (12.35, 0.06, 0.85), mat_name="Mat_BrassGold", parent=root)
    add_box("Sign_Face_Plate", (0, -3.45, 5.4), (12.0, 0.04, 0.65), mat_name="Mat_Concrete", parent=root)
    # 3D Dimensional "DINO PARK" extruded emblem block
    add_box("Sign_Emblem_Block", (0, -3.49, 5.4), (6.5, 0.06, 0.45), mat_name="Mat_BrassGold", parent=root)

    # 4 Standard Modular Solar Panels on Canopy Roof (Exact scale ratio!)
    for i in range(4):
        x = -2.8 + i * 1.85
        create_detailed_solar_panel(f"Gate_Solar_{i}", (x, 0.8, 5.95), rotation=(math.radians(10), 0, 0), parent=root)

    # HVAC Unit on Canopy Roof
    create_hvac_chiller_unit("Gate_HVAC", (4.2, -1.0, 5.9), size=(1.5, 0.9, 0.7), parent=root)

    # Brass Accent Trim lighting bands
    add_box("Trim_Gold_Band_L", (-4.2, 0, 4.9), (2.85, 4.45, 0.1), mat_name="Mat_BrassGold", parent=root)
    add_box("Trim_Gold_Band_R", (4.2, 0, 4.9), (2.45, 4.45, 0.1), mat_name="Mat_BrassGold", parent=root)

    # Interactive Staff/Ticketing Door at rear of Left Pylon (Y = 2.2m)
    door_obj = add_box("Door_TicketPavilion", (-4.0, 2.22, 1.15), (0.95, 0.07, 2.3), mat_name="Mat_CharcoalSteel")
    handle = add_box("Door_Handle", (-4.35, 2.27, 1.15), (0.05, 0.08, 0.25), mat_name="Mat_BrassGold", parent=door_obj)
    # Set pivot to hinge
    bpy.context.view_layer.objects.active = door_obj
    bpy.ops.object.select_all(action='DESELECT')
    door_obj.select_set(True)
    bpy.context.scene.cursor.location = (-3.5, 2.22, 0.0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    door_obj.parent = root

    fbx_path = os.path.join(BUILDINGS_DIR, "EntranceGate.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported High-Detail:", fbx_path)

# -------------------------------------------------------------
# 2. Canteen & Terrace Cafe (High Detail)
# -------------------------------------------------------------
def build_canteen():
    clear_scene()
    setup_materials()
    root = bpy.data.objects.new("Canteen", None)
    bpy.context.scene.collection.objects.link(root)

    # Main Building Structure (8m wide x 6m deep)
    # Base Concrete Slab
    add_box("Canteen_BaseSlab", (0, 0, 0.1), (8.4, 6.4, 0.2), mat_name="Mat_Concrete", parent=root)

    # Indoor Kitchen & Service Hall (back half, Y: 0.2 to 3.0)
    add_box("Kitchen_Volume", (0, 1.5, 1.7), (7.8, 3.0, 3.2), mat_name="Mat_Concrete", parent=root)
    # Timber slat cladding on left and right walls
    create_timber_slat_facade("Canteen_Slats_Left", (-3.95, 1.5, 0.2), width=3.0, height=3.1, parent=root)
    create_timber_slat_facade("Canteen_Slats_Right", (3.95, 1.5, 0.2), width=3.0, height=3.1, parent=root)

    # Front Serving Counter & Order Station
    add_box("Counter_Body", (0, 0.0, 0.6), (6.4, 0.9, 1.0), mat_name="Mat_Timber", parent=root)
    add_box("Counter_Top", (0, 0.0, 1.12), (6.6, 1.0, 0.08), mat_name="Mat_CharcoalSteel", parent=root)

    # Recessed Tinted Teal Glass Facade with Charcoal Steel Mullions
    add_box("Canteen_Glass_Front", (0, 0.35, 2.3), (7.6, 0.08, 1.5), mat_name="Mat_TealGlass", parent=root)
    for i in range(5):
        gx = -3.0 + i * 1.5
        add_box(f"Glass_Mullion_{i}", (gx, 0.35, 2.3), (0.1, 0.12, 1.55), mat_name="Mat_CharcoalSteel", parent=root)

    # Hanging Menu Boards with Brass Accent Lights
    for i in range(3):
        mx = -1.8 + i * 1.8
        add_box(f"Menu_Board_{i}", (mx, -0.1, 2.5), (1.4, 0.05, 0.6), mat_name="Mat_Concrete", parent=root)
        add_cylinder(f"Menu_Light_{i}", (mx, -0.2, 2.85), radius=0.08, depth=0.1, rotation=(math.radians(90), 0, 0), mat_name="Mat_BrassGold", parent=root)

    # Overhanging Canopy Roof with Parapet & Living Roof
    add_box("Canteen_Roof_Canopy", (0, -0.5, 3.5), (8.6, 7.2, 0.4), mat_name="Mat_Concrete", parent=root)
    add_box("Canteen_LivingRoof", (0, 0.8, 3.75), (8.0, 4.0, 0.15), mat_name="Mat_LivingRoof", parent=root)

    # 4 Modular Solar Panels on Rooftop
    for i in range(3):
        sx = -2.0 + i * 2.0
        create_detailed_solar_panel(f"Canteen_Solar_{i}", (sx, 1.2, 3.9), rotation=(math.radians(12), 0, 0), parent=root)

    # Rooftop HVAC Chiller Unit
    create_hvac_chiller_unit("Canteen_HVAC", (2.8, 1.5, 3.9), size=(1.6, 1.0, 0.75), parent=root)

    # Expansive Outdoor Wooden Dining Deck in Front (Y: -1.0 to -5.5)
    deck = add_box("Dining_Deck", (0, -3.2, 0.1), (9.0, 4.6, 0.18), mat_name="Mat_Timber", parent=root)
    # Deck low perimeter planter edge
    add_box("Deck_Edge_L", (-4.4, -3.2, 0.3), (0.3, 4.6, 0.4), mat_name="Mat_Concrete", parent=root)
    add_box("Deck_Edge_R", (4.4, -3.2, 0.3), (0.3, 4.6, 0.4), mat_name="Mat_Concrete", parent=root)
    add_box("Deck_Edge_F", (0, -5.4, 0.3), (9.0, 0.3, 0.4), mat_name="Mat_Concrete", parent=root)

    # 4 Complete Parasol Dining Table Sets with Chairs on the Deck!
    create_umbrella_table("Table_Set_1", (-2.4, -2.2, 0.2), parent=root)
    create_umbrella_table("Table_Set_2", (2.4, -2.2, 0.2), parent=root)
    create_umbrella_table("Table_Set_3", (-2.4, -4.2, 0.2), parent=root)
    create_umbrella_table("Table_Set_4", (2.4, -4.2, 0.2), parent=root)

    # Interactive Staff Door at Side (X = 3.95, Y = 1.5)
    door = add_box("Canteen_StaffDoor", (3.95, 1.5, 1.15), (0.08, 1.0, 2.25), mat_name="Mat_CharcoalSteel")
    handle = add_box("Canteen_Door_Handle", (4.01, 1.1, 1.15), (0.06, 0.05, 0.2), mat_name="Mat_BrassGold", parent=door)
    bpy.context.view_layer.objects.active = door
    bpy.ops.object.select_all(action='DESELECT')
    door.select_set(True)
    bpy.context.scene.cursor.location = (3.95, 2.0, 0.0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    door.parent = root

    fbx_path = os.path.join(BUILDINGS_DIR, "Canteen.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported High-Detail:", fbx_path)

# -------------------------------------------------------------
# 3. Research Lab (High Detail)
# -------------------------------------------------------------
def build_research_lab():
    clear_scene()
    setup_materials()
    root = bpy.data.objects.new("ResearchLab", None)
    bpy.context.scene.collection.objects.link(root)

    # Main 2-story building (8.4m wide x 8.4m deep x 5.6m tall)
    add_box("Lab_BaseSlab", (0, 0, 0.1), (8.6, 8.6, 0.2), mat_name="Mat_Concrete", parent=root)

    # Ground Floor Structure
    add_box("Ground_Floor_Core", (-0.8, 0, 1.4), (6.4, 8.0, 2.6), mat_name="Mat_Concrete", parent=root)
    create_timber_slat_facade("Lab_FrontSlats_L", (-2.8, -4.05, 0.2), width=2.0, height=2.4, parent=root)
    create_timber_slat_facade("Lab_FrontSlats_R", (1.2, -4.05, 0.2), width=2.0, height=2.4, parent=root)

    # Second Floor Projecting Volume (Cantilevered charcoal steel frame)
    add_box("Second_Floor_Volume", (-0.8, 0, 4.0), (6.8, 8.2, 2.4), mat_name="Mat_Concrete", parent=root)
    add_box("Upper_Frame_Charcoal", (-0.8, -4.12, 4.0), (7.0, 0.25, 2.5), mat_name="Mat_CharcoalSteel", parent=root)

    # Front Panoramic Ribbon Windows with Charcoal Steel Mullions
    add_box("Upper_Teal_Glass", (-0.8, -4.1, 4.0), (6.6, 0.08, 1.8), mat_name="Mat_TealGlass", parent=root)
    for i in range(5):
        mx = -3.2 + i * 1.6
        add_box(f"Upper_Mullion_{i}", (mx, -4.15, 4.0), (0.1, 0.15, 1.85), mat_name="Mat_CharcoalSteel", parent=root)

    # Amber Glowing Accent Lines
    add_box("Upper_Amber_Trim", (-0.8, -4.2, 3.0), (6.8, 0.08, 0.1), mat_name="Mat_AmberGlow", parent=root)

    # Entrance Portal with Flat Cantilevered Canopy
    add_box("Entrance_Canopy", (-0.8, -4.8, 2.5), (2.6, 1.6, 0.16), mat_name="Mat_Concrete", parent=root)
    add_cylinder("Canopy_Pillar_L", (-1.9, -5.4, 1.25), radius=0.06, depth=2.5, mat_name="Mat_CharcoalSteel", parent=root)
    add_cylinder("Canopy_Pillar_R", (0.3, -5.4, 1.25), radius=0.06, depth=2.5, mat_name="Mat_CharcoalSteel", parent=root)

    # Lower Wing: Dedicated Drone Landing Pad Platform (Right side, X = 2.8m)
    add_box("Drone_Wing_Structure", (2.8, 0, 1.6), (2.4, 6.0, 3.0), mat_name="Mat_Concrete", parent=root)
    add_box("Drone_Pad_Deck", (2.8, 0, 3.15), (2.2, 4.4, 0.12), mat_name="Mat_CharcoalSteel", parent=root)
    # Painted Helipad Circle & "H"
    add_cylinder("Drone_Ring", (2.8, 0, 3.22), radius=1.0, depth=0.01, mat_name="Mat_RoadWhite", parent=root)
    add_box("Drone_H_1", (2.4, 0, 3.23), (0.12, 1.0, 0.01), mat_name="Mat_RoadWhite", parent=root)
    add_box("Drone_H_2", (3.2, 0, 3.23), (0.12, 1.0, 0.01), mat_name="Mat_RoadWhite", parent=root)
    add_box("Drone_H_Bar", (2.8, 0, 3.23), (0.7, 0.12, 0.01), mat_name="Mat_RoadWhite", parent=root)
    # Corner Warning Strobe Lights on Drone Pad
    for cx, cy in [(1.8, -1.8), (1.8, 1.8), (3.8, -1.8), (3.8, 1.8)]:
        add_cylinder(f"Strobe_{cx}_{cy}", (cx, cy, 3.25), radius=0.06, depth=0.1, mat_name="Mat_AmberGlow", parent=root)

    # Main Rooftop: Living Roof + Full Solar Array
    add_box("Roof_LivingGreen", (-0.8, 0, 5.3), (6.4, 7.8, 0.15), mat_name="Mat_LivingRoof", parent=root)
    for i in range(3):
        for j in range(2):
            px = -2.2 + j * 2.0
            py = -2.2 + i * 2.2
            create_detailed_solar_panel(f"Lab_Solar_{i}_{j}", (px, py, 5.45), rotation=(math.radians(12), 0, 0), parent=root)

    # Large Parabolic Satellite Dish on Roof (Gimbal base, dish bowl, sub-reflector)
    dish_base = add_box("Dish_Mount", (1.2, 2.6, 5.55), (0.9, 0.9, 0.4), mat_name="Mat_Concrete", parent=root)
    dish_arm = add_cylinder("Dish_Yoke", (1.2, 2.6, 5.95), radius=0.1, depth=0.5, mat_name="Mat_CharcoalSteel", parent=root)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.85, location=(1.2, 2.6, 6.5), segments=20, ring_count=12)
    dish = bpy.context.active_object
    dish.name = "Dish_Bowl"
    dish.scale = (1.0, 0.35, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    dish.rotation_euler = (math.radians(35), 0, math.radians(-30))
    apply_mat(dish, "Mat_Concrete")
    dish.parent = root

    # Rooftop HVAC Unit
    create_hvac_chiller_unit("Lab_HVAC", (-2.6, 2.4, 5.45), size=(1.6, 1.0, 0.8), parent=root)

    # Interactive Automatic Sliding Double Doors
    door_l = add_box("ResearchLab_Door_L", (-1.3, -4.02, 1.25), (0.95, 0.07, 2.3), mat_name="Mat_TealGlass")
    add_box("Door_L_Frame", (-1.3, -4.02, 1.25), (0.97, 0.09, 2.32), mat_name="Mat_CharcoalSteel", parent=door_l)
    door_l.parent = root

    door_r = add_box("ResearchLab_Door_R", (-0.3, -4.02, 1.25), (0.95, 0.07, 2.3), mat_name="Mat_TealGlass")
    add_box("Door_R_Frame", (-0.3, -4.02, 1.25), (0.97, 0.09, 2.32), mat_name="Mat_CharcoalSteel", parent=door_r)
    door_r.parent = root

    fbx_path = os.path.join(BUILDINGS_DIR, "ResearchLab.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported High-Detail:", fbx_path)

# -------------------------------------------------------------
# 4. Hatchery (Egg Lab) (High Detail)
# -------------------------------------------------------------
def build_hatchery():
    clear_scene()
    setup_materials()
    root = bpy.data.objects.new("Hatchery", None)
    bpy.context.scene.collection.objects.link(root)

    # Concrete Footing & Base Ring
    add_cylinder("Hatchery_Footing", (0, 0, 0.15), radius=5.3, depth=0.3, vertices=32, mat_name="Mat_Concrete", parent=root)
    add_cylinder("Hatchery_BaseRing", (0, 0, 0.45), radius=5.1, depth=0.35, vertices=32, mat_name="Mat_CharcoalSteel", parent=root)

    # Lower Wall Cylinder with Timber Slat Panel insets
    add_cylinder("Hatchery_LowerWall", (0, 0, 1.6), radius=4.85, depth=2.0, vertices=32, mat_name="Mat_Concrete", parent=root)

    # 360-Degree Ribbon Window with 16 Charcoal Steel Mullions
    add_cylinder("Hatchery_TealRibbon", (0, 0, 3.1), radius=4.7, depth=1.1, vertices=32, mat_name="Mat_TealGlass", parent=root)
    for i in range(16):
        ang = math.radians(i * (360/16))
        mx = math.cos(ang) * 4.75
        my = math.sin(ang) * 4.75
        add_box(f"Ribbon_Mullion_{i}", (mx, my, 3.1), (0.1, 0.14, 1.15), rotation=(0, 0, ang), mat_name="Mat_CharcoalSteel", parent=root)

    # Amber Glowing Accent Ring
    add_cylinder("Hatchery_AmberTrim", (0, 0, 2.5), radius=4.9, depth=0.08, vertices=32, mat_name="Mat_AmberGlow", parent=root)

    # Upper Concrete Dome Cap
    bpy.ops.mesh.primitive_uv_sphere_add(radius=4.5, location=(0, 0, 3.2), segments=32, ring_count=16)
    dome = bpy.context.active_object
    dome.name = "Hatchery_Dome"
    dome.scale = (1.0, 1.0, 0.52)
    bpy.ops.object.transform_apply(scale=True)
    apply_mat(dome, "Mat_Concrete")
    dome.parent = root

    # 4 Large Inset Glowing Amber Egg Skylights
    for idx, deg in enumerate([45, 135, 225, 315]):
        rad = math.radians(deg)
        dist = 2.5
        x = math.cos(rad) * dist
        y = math.sin(rad) * dist
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.75, location=(x, y, 4.8), segments=16, ring_count=12)
        egg = bpy.context.active_object
        egg.name = f"Egg_Skylight_{idx}"
        egg.scale = (0.85, 0.85, 1.25)
        bpy.ops.object.transform_apply(scale=True)
        egg.rotation_euler = (math.radians(22) * math.sin(rad), -math.radians(22) * math.cos(rad), 0)
        apply_mat(egg, "Mat_AmberGlow")
        egg.parent = root

    # Roof Terrace with Living Grass & Modular Solar Panels
    add_cylinder("Roof_GreenTerrace", (0, 0, 4.5), radius=3.7, depth=0.1, vertices=32, mat_name="Mat_LivingRoof", parent=root)
    for idx, deg in enumerate([0, 90, 180, 270]):
        rad = math.radians(deg)
        dist = 3.1
        sx = math.cos(rad) * dist
        sy = math.sin(rad) * dist
        create_detailed_solar_panel(f"Hatchery_Solar_{idx}", (sx, sy, 4.65), rotation=(math.radians(12), 0, rad), parent=root)

    # Entrance Portal (Front at Y = -4.9m)
    portal = add_box("Portal_Frame", (0, -4.95, 1.5), (3.8, 0.8, 3.0), mat_name="Mat_Concrete", parent=root)
    # Timber side louvres
    add_box("Portal_Timber_L", (-2.0, -4.95, 1.5), (0.35, 0.85, 2.9), mat_name="Mat_Timber", parent=root)
    add_box("Portal_Timber_R", (2.0, -4.95, 1.5), (0.35, 0.85, 2.9), mat_name="Mat_Timber", parent=root)
    # Illuminated Sign Band
    add_box("Hatchery_SignPlate", (0, -5.4, 2.85), (3.0, 0.08, 0.55), mat_name="Mat_Concrete", parent=root)
    add_box("Hatchery_SignFrame", (0, -5.42, 2.85), (3.1, 0.05, 0.6), mat_name="Mat_BrassGold", parent=root)

    # Interactive Curved Sliding Double Doors
    door_l = add_box("Hatchery_Door_L", (-0.8, -4.9, 1.25), (1.4, 0.08, 2.4), mat_name="Mat_TealGlass")
    add_box("Hatchery_Door_L_Frame", (-0.8, -4.9, 1.25), (1.42, 0.1, 2.42), mat_name="Mat_CharcoalSteel", parent=door_l)
    door_l.parent = root

    door_r = add_box("Hatchery_Door_R", (0.8, -4.9, 1.25), (1.4, 0.08, 2.4), mat_name="Mat_TealGlass")
    add_box("Hatchery_Door_R_Frame", (0.8, -4.9, 1.25), (1.42, 0.1, 2.42), mat_name="Mat_CharcoalSteel", parent=door_r)
    door_r.parent = root

    fbx_path = os.path.join(BUILDINGS_DIR, "Hatchery.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported High-Detail:", fbx_path)

# -------------------------------------------------------------
# 5. Ranger Station with Observation Watchtower (High Detail)
# -------------------------------------------------------------
def build_ranger_station():
    clear_scene()
    setup_materials()
    root = bpy.data.objects.new("RangerStation", None)
    bpy.context.scene.collection.objects.link(root)

    # Concrete Foundation (6.4m x 6.4m)
    add_box("Ranger_Foundation", (0, 0, 0.1), (6.4, 6.4, 0.2), mat_name="Mat_Concrete", parent=root)

    # Ground Floor Modular Container (X: -1.4m, Y: -0.6m, Z: 1.4m)
    add_box("Container_Ground", (-1.4, -0.6, 1.4), (3.4, 4.6, 2.6), mat_name="Mat_CharcoalSteel", parent=root)
    create_timber_slat_facade("Ranger_FrontSlats", (-1.4, -2.92, 0.2), width=3.2, height=2.4, parent=root)
    create_timber_slat_facade("Ranger_SideSlats", (-3.12, -0.6, 0.2), width=4.2, height=2.4, parent=root)

    # Upper Deck with Green Roof & Drone Landing Pad
    add_box("Ranger_Terrace", (-1.4, -0.6, 2.75), (3.4, 4.6, 0.15), mat_name="Mat_LivingRoof", parent=root)
    add_box("Ranger_DronePad_Plate", (-1.4, -1.8, 2.85), (2.0, 2.0, 0.06), mat_name="Mat_CharcoalSteel", parent=root)
    add_cylinder("Ranger_DroneRing", (-1.4, -1.8, 2.89), radius=0.75, depth=0.01, mat_name="Mat_RoadWhite", parent=root)
    create_detailed_solar_panel("Ranger_Solar", (-1.4, 0.8, 3.0), rotation=(math.radians(12), 0, 0), parent=root)

    # High-Rise Steel Lattice Observation Tower (Height: 9.0m, X: 1.8m, Y: 1.0m)
    for lx, ly in [(0.7, -0.1), (0.7, 2.1), (2.9, -0.1), (2.9, 2.1)]:
        # Heavy Box Columns
        add_box(f"Tower_Column_{lx}_{ly}", (lx, ly, 3.8), (0.22, 0.22, 7.4), mat_name="Mat_CharcoalSteel", parent=root)
    # Horizontal & Diagonal Steel Trusses across 3 Tiers
    for z in [2.2, 4.4, 6.6]:
        add_box(f"Truss_H_X1_{z}", (1.8, -0.1, z), (2.2, 0.12, 0.12), mat_name="Mat_CharcoalSteel", parent=root)
        add_box(f"Truss_H_X2_{z}", (1.8, 2.1, z), (2.2, 0.12, 0.12), mat_name="Mat_CharcoalSteel", parent=root)
        add_box(f"Truss_H_Y1_{z}", (0.7, 1.0, z), (0.12, 2.2, 0.12), mat_name="Mat_CharcoalSteel", parent=root)
        add_box(f"Truss_H_Y2_{z}", (2.9, 1.0, z), (0.12, 2.2, 0.12), mat_name="Mat_CharcoalSteel", parent=root)

    # Observation Deck Platform (Z = 7.5m)
    add_box("Lookout_Deck", (1.8, 1.0, 7.55), (2.8, 2.8, 0.2), mat_name="Mat_Timber", parent=root)
    # Perimeter Handrails
    add_box("Deck_Rail_X1", (1.8, -0.35, 8.1), (2.7, 0.06, 0.9), mat_name="Mat_CharcoalSteel", parent=root)
    add_box("Deck_Rail_X2", (1.8, 2.35, 8.1), (2.7, 0.06, 0.9), mat_name="Mat_CharcoalSteel", parent=root)

    # 360-Degree Panoramic Glass Cabin (Z: 7.6 to 9.2m)
    add_box("Lookout_Glass_Cabin", (1.8, 1.0, 8.4), (2.3, 2.3, 1.5), mat_name="Mat_TealGlass", parent=root)
    add_box("Lookout_Cabin_Frame", (1.8, 1.0, 8.4), (2.35, 2.35, 1.55), mat_name="Mat_CharcoalSteel", parent=root)
    # Overhanging Pyramid Roof
    add_box("Lookout_Roof_Overhang", (1.8, 1.0, 9.25), (2.7, 2.7, 0.25), mat_name="Mat_Concrete", parent=root)
    # Rotating Brass Beacon Light
    add_cylinder("Tower_Beacon", (1.8, 1.0, 9.55), radius=0.18, depth=0.35, mat_name="Mat_BrassGold", parent=root)

    # External Steel Stairs linking Ground to 1st Floor Deck
    for i in range(10):
        sz = 0.3 + i * 0.25
        sy = -2.2 + i * 0.26
        add_box(f"Stair_Step_{i}", (0.35, sy, sz), (0.9, 0.26, 0.06), mat_name="Mat_CharcoalSteel", parent=root)
    add_box("Stair_Handrail", (0.35, -1.0, 1.8), (0.05, 3.0, 0.8), mat_name="Mat_CharcoalSteel", parent=root)

    # Interactive Staff Entry Door (Front at X = -1.4, Y = -2.94)
    door = add_box("RangerStation_Door", (-1.4, -2.94, 1.25), (0.95, 0.07, 2.3), mat_name="Mat_CharcoalSteel")
    handle = add_box("Ranger_Handle", (-1.75, -2.98, 1.25), (0.05, 0.06, 0.2), mat_name="Mat_BrassGold", parent=door)
    bpy.context.view_layer.objects.active = door
    bpy.ops.object.select_all(action='DESELECT')
    door.select_set(True)
    bpy.context.scene.cursor.location = (-0.95, -2.94, 0.0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    door.parent = root

    fbx_path = os.path.join(BUILDINGS_DIR, "RangerStation.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported High-Detail:", fbx_path)

# -------------------------------------------------------------
# 6. Automatic Gate (High Detail)
# -------------------------------------------------------------
def build_automatic_gate():
    clear_scene()
    setup_materials()
    root = bpy.data.objects.new("AutomaticGate", None)
    bpy.context.scene.collection.objects.link(root)

    # Concrete Footing & Ground Guide Rail Track
    add_box("Gate_Footing", (0, 0, 0.15), (4.8, 0.9, 0.3), mat_name="Mat_Concrete", parent=root)
    add_box("Gate_Track_Steel", (0, 0, 0.32), (4.6, 0.22, 0.06), mat_name="Mat_CharcoalSteel", parent=root)

    # Heavy Pylons with Chamfered Caps (Left: X = -2.1, Right: X = 2.1)
    for px, side in [(-2.1, "L"), (2.1, "R")]:
        pylon = add_box(f"Pylon_{side}", (px, 0, 1.9), (0.75, 0.85, 3.5), mat_name="Mat_Concrete", parent=root)
        # Steel Base Boot Collars
        add_box(f"Pylon_Base_Boot_{side}", (px, 0, 0.4), (0.85, 0.95, 0.3), mat_name="Mat_CharcoalSteel", parent=pylon)
        # Sensor Housing Pod
        add_box(f"Sensor_Pod_{side}", (px, -0.45, 2.7), (0.3, 0.15, 0.35), mat_name="Mat_CharcoalSteel", parent=pylon)
        # Warning Beacon Light
        add_cylinder(f"Beacon_Light_{side}", (px, 0, 3.8), radius=0.2, depth=0.35, mat_name="Mat_BrassGold", parent=pylon)

    # Left Sliding Gate Leaf: X = -0.9m (1.75m wide x 3.0m tall)
    gate_l = add_box("AutoGate_Door_L", (-0.9, 0, 1.85), (1.75, 0.16, 2.9), mat_name="Mat_CharcoalSteel")
    # Lower Impact Barrier Skirt
    add_box("Gate_L_Skirt", (0, 0, -1.0), (1.7, 0.18, 0.8), mat_name="Mat_CharcoalSteel", parent=gate_l)
    # Chunky Vertical Security Bars
    for i in range(6):
        bx = -0.65 + i * 0.26
        add_box(f"Gate_L_Bar_{i}", (bx, 0, 0.3), (0.07, 0.1, 1.8), mat_name="Mat_CharcoalSteel", parent=gate_l)
    # Tinted Teal Inspection Viewing Glass
    add_box("Gate_L_TealGlass", (0.55, 0, 0.3), (0.4, 0.08, 1.6), mat_name="Mat_TealGlass", parent=gate_l)
    gate_l.parent = root

    # Right Sliding Gate Leaf: X = 0.9m (1.75m wide x 3.0m tall)
    gate_r = add_box("AutoGate_Door_R", (0.9, 0, 1.85), (1.75, 0.16, 2.9), mat_name="Mat_CharcoalSteel")
    add_box("Gate_R_Skirt", (0, 0, -1.0), (1.7, 0.18, 0.8), mat_name="Mat_CharcoalSteel", parent=gate_r)
    for i in range(6):
        bx = -0.65 + i * 0.26
        add_box(f"Gate_R_Bar_{i}", (bx, 0, 0.3), (0.07, 0.1, 1.8), mat_name="Mat_CharcoalSteel", parent=gate_r)
    add_box("Gate_R_TealGlass", (-0.55, 0, 0.3), (0.4, 0.08, 1.6), mat_name="Mat_TealGlass", parent=gate_r)
    gate_r.parent = root

    fbx_path = os.path.join(ENCLOSURES_DIR, "AutomaticGate.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported High-Detail:", fbx_path)

# -------------------------------------------------------------
# 7. Automated Feeder (High Detail)
# -------------------------------------------------------------
def build_automated_feeder():
    clear_scene()
    setup_materials()
    root = bpy.data.objects.new("AutomatedFeeder", None)
    bpy.context.scene.collection.objects.link(root)

    # Splayed Legs with Concrete Foundation Pads
    for x, y in [(-0.65, -0.65), (-0.65, 0.65), (0.65, -0.65), (0.65, 0.65)]:
        add_box(f"Feeder_Shoe_{x}_{y}", (x, y, 0.15), (0.35, 0.35, 0.3), mat_name="Mat_Concrete", parent=root)
        add_box(f"Feeder_Leg_{x}_{y}", (x, y, 0.85), (0.16, 0.16, 1.1), mat_name="Mat_CharcoalSteel", parent=root)

    # Cross Stretchers
    add_box("Feeder_Stretcher_X1", (0, -0.65, 0.8), (1.2, 0.08, 0.08), mat_name="Mat_CharcoalSteel", parent=root)
    add_box("Feeder_Stretcher_X2", (0, 0.65, 0.8), (1.2, 0.08, 0.08), mat_name="Mat_CharcoalSteel", parent=root)

    # Steel Hopper Bin (Tapered geometry)
    add_box("Hopper_Bin", (0, 0, 1.95), (1.6, 1.6, 1.1), mat_name="Mat_CharcoalSteel", parent=root)
    add_box("Hopper_Cone", (0, 0, 1.25), (0.8, 0.8, 0.35), mat_name="Mat_CharcoalSteel", parent=root)
    # Dispensing Chute Funnel
    add_box("Chute_Funnel", (0, 0.6, 0.95), (0.45, 0.7, 0.35), rotation=(math.radians(25), 0, 0), mat_name="Mat_CharcoalSteel", parent=root)

    # Concrete Feed Basin in front
    add_box("Feed_Basin", (0, 1.1, 0.3), (1.5, 0.9, 0.6), mat_name="Mat_Concrete", parent=root)
    add_box("Feed_Foliage_Layer", (0, 1.1, 0.5), (1.3, 0.7, 0.15), mat_name="Mat_LivingRoof", parent=root)

    # Mini Solar Panel on Hopper Roof
    add_box("Feeder_Solar", (0, 0, 2.53), (0.9, 0.6, 0.04), mat_name="Mat_SolarPanel", parent=root)
    # Status Beacon
    add_cylinder("Feeder_Beacon", (0, 0.82, 1.95), radius=0.09, depth=0.12, rotation=(math.radians(90), 0, 0), mat_name="Mat_BrassGold", parent=root)

    fbx_path = os.path.join(ENCLOSURES_DIR, "AutomatedFeeder.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported High-Detail:", fbx_path)

# -------------------------------------------------------------
# 8. Complete Modular Roads Kit (with Yellow Markings & Crosswalks)
# -------------------------------------------------------------
def build_road_kit():
    # 1. Straight Road (4m wide x 4m long)
    clear_scene()
    setup_materials()
    root_s = bpy.data.objects.new("ModularRoad_Straight", None)
    bpy.context.scene.collection.objects.link(root_s)
    add_box("Road_Surface", (0, 0, 0.025), (4.0, 4.0, 0.05), mat_name="Mat_RoadAsphalt", parent=root_s)
    # Beveled Concrete Curbs
    add_box("Curb_L", (-1.9, 0, 0.07), (0.2, 4.0, 0.14), mat_name="Mat_Concrete", parent=root_s)
    add_box("Curb_R", (1.9, 0, 0.07), (0.2, 4.0, 0.14), mat_name="Mat_Concrete", parent=root_s)
    # Yellow Center Divider Dashes
    for y in [-1.2, 0.0, 1.2]:
        add_box(f"Lane_Yellow_{y}", (0, y, 0.052), (0.14, 0.6, 0.005), mat_name="Mat_RoadYellow", parent=root_s)
    # White Edge Boundary Lines
    add_box("Line_Edge_L", (-1.65, 0, 0.052), (0.08, 4.0, 0.005), mat_name="Mat_RoadWhite", parent=root_s)
    add_box("Line_Edge_R", (1.65, 0, 0.052), (0.08, 4.0, 0.005), mat_name="Mat_RoadWhite", parent=root_s)

    fbx_path = os.path.join(ROADS_DIR, "ModularRoad_Straight.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)

    # 2. 4-Way Cross Intersection with Zebra Pedestrian Crosswalks!
    clear_scene()
    setup_materials()
    root_x = bpy.data.objects.new("ModularRoad_Cross", None)
    bpy.context.scene.collection.objects.link(root_x)
    add_box("Cross_Surface", (0, 0, 0.025), (4.0, 4.0, 0.05), mat_name="Mat_RoadAsphalt", parent=root_x)
    # 4 Corner Curbs
    for cx, cy in [(-1.9, -1.9), (-1.9, 1.9), (1.9, -1.9), (1.9, 1.9)]:
        add_box(f"Curb_{cx}_{cy}", (cx, cy, 0.07), (0.2, 0.2, 0.14), mat_name="Mat_Concrete", parent=root_x)
    # Zebra Stripes along entrances
    for sx in [-1.2, -0.6, 0.0, 0.6, 1.2]:
        add_box(f"Zebra_N_{sx}", (sx, 1.6, 0.052), (0.25, 0.45, 0.005), mat_name="Mat_RoadWhite", parent=root_x)
        add_box(f"Zebra_S_{sx}", (sx, -1.6, 0.052), (0.25, 0.45, 0.005), mat_name="Mat_RoadWhite", parent=root_x)
    for sy in [-1.2, -0.6, 0.0, 0.6, 1.2]:
        add_box(f"Zebra_E_{sy}", (1.6, sy, 0.052), (0.45, 0.25, 0.005), mat_name="Mat_RoadWhite", parent=root_x)
        add_box(f"Zebra_W_{sy}", (-1.6, sy, 0.052), (-0.45, 0.25, 0.005), mat_name="Mat_RoadWhite", parent=root_x)
    # Central Brass Disc Emblem
    add_cylinder("Center_Emblem", (0, 0, 0.052), radius=0.45, depth=0.005, mat_name="Mat_BrassGold", parent=root_x)

    fbx_path = os.path.join(ROADS_DIR, "ModularRoad_Cross.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)

    # 3. 90-Degree Curved Road Corner
    clear_scene()
    setup_materials()
    root_c = bpy.data.objects.new("ModularRoad_Corner", None)
    bpy.context.scene.collection.objects.link(root_c)
    add_box("Corner_Surface", (0, 0, 0.025), (4.0, 4.0, 0.05), mat_name="Mat_RoadAsphalt", parent=root_c)
    add_box("Curb_Outer_X", (-1.9, 0, 0.07), (0.2, 4.0, 0.14), mat_name="Mat_Concrete", parent=root_c)
    add_box("Curb_Outer_Y", (0, 1.9, 0.07), (4.0, 0.2, 0.14), mat_name="Mat_Concrete", parent=root_c)
    add_box("Curb_Inner", (1.9, -1.9, 0.07), (0.2, 0.2, 0.14), mat_name="Mat_Concrete", parent=root_c)
    # Yellow Curve Track
    add_cylinder("Yellow_Curve", (-1.9, 1.9, 0.052), radius=1.9, depth=0.005, vertices=24, mat_name="Mat_RoadYellow", parent=root_c)

    fbx_path = os.path.join(ROADS_DIR, "ModularRoad_Corner.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)

    # 4. Road Turnaround / Dead-End (ModularRoad_End)
    clear_scene()
    setup_materials()
    root_e = bpy.data.objects.new("ModularRoad_End", None)
    bpy.context.scene.collection.objects.link(root_e)
    add_box("End_Surface", (0, 0, 0.025), (4.0, 4.0, 0.05), mat_name="Mat_RoadAsphalt", parent=root_e)
    add_box("Curb_L", (-1.9, 0, 0.07), (0.2, 4.0, 0.14), mat_name="Mat_Concrete", parent=root_e)
    add_box("Curb_R", (1.9, 0, 0.07), (0.2, 4.0, 0.14), mat_name="Mat_Concrete", parent=root_e)
    add_box("Curb_End", (0, 1.9, 0.07), (4.0, 0.2, 0.14), mat_name="Mat_Concrete", parent=root_e)
    # End Zebra marking
    for sx in [-1.2, -0.6, 0.0, 0.6, 1.2]:
        add_box(f"Zebra_{sx}", (sx, 1.4, 0.052), (0.25, 0.45, 0.005), mat_name="Mat_RoadWhite", parent=root_e)

    fbx_path = os.path.join(ROADS_DIR, "ModularRoad_End.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)

    # 5. Parking Bay Section (4m x 4m with 2 marked diagonal/perpendicular parking stalls)
    clear_scene()
    setup_materials()
    root_p = bpy.data.objects.new("ModularRoad_Parking", None)
    bpy.context.scene.collection.objects.link(root_p)
    add_box("Park_Surface", (0, 0, 0.025), (4.0, 4.0, 0.05), mat_name="Mat_RoadAsphalt", parent=root_p)
    add_box("Curb_Back", (0, 1.9, 0.07), (4.0, 0.2, 0.14), mat_name="Mat_Concrete", parent=root_p)
    # White Parking Bay Dividers
    for px in [-1.9, 0.0, 1.9]:
        add_box(f"Stall_Line_{px}", (px, 0.5, 0.052), (0.1, 2.8, 0.005), mat_name="Mat_RoadWhite", parent=root_p)

    fbx_path = os.path.join(ROADS_DIR, "ModularRoad_Parking.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported High-Detail Roads Kit")

if __name__ == "__main__":
    print("=== STARTING HIGH-DETAIL ARCHITECTURAL 3D ASSETS BUILD ===")
    build_entrance_gate()
    build_canteen()
    build_research_lab()
    build_hatchery()
    build_ranger_station()
    build_automatic_gate()
    build_automated_feeder()
    build_road_kit()
    print("=== HIGH-DETAIL ARCHITECTURAL 3D ASSETS COMPLETE ===")
