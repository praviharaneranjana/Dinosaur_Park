import bpy
import bmesh
import math
import os

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
    get_or_create_material("Mat_Concrete", (0.957, 0.929, 0.847, 1.0), metallic=0.0, roughness=0.85)
    get_or_create_material("Mat_Timber", (0.780, 0.604, 0.388, 1.0), metallic=0.0, roughness=0.6)
    get_or_create_material("Mat_CharcoalSteel", (0.231, 0.278, 0.263, 1.0), metallic=0.85, roughness=0.35)
    get_or_create_material("Mat_TealGlass", (0.561, 0.796, 0.796, 1.0), metallic=0.2, roughness=0.15)
    get_or_create_material("Mat_LivingRoof", (0.369, 0.608, 0.290, 1.0), metallic=0.0, roughness=0.9)
    get_or_create_material("Mat_BrassGold", (0.949, 0.722, 0.294, 1.0), metallic=0.9, roughness=0.25, emission_rgb=(0.949, 0.722, 0.294), emission_strength=1.5)
    get_or_create_material("Mat_SolarPanel", (0.10, 0.16, 0.26, 1.0), metallic=0.5, roughness=0.2)
    get_or_create_material("Mat_AmberGlow", (1.0, 0.65, 0.18, 1.0), metallic=0.1, roughness=0.2, emission_rgb=(1.0, 0.65, 0.18), emission_strength=3.0)
    get_or_create_material("Mat_RoadAsphalt", (0.18, 0.19, 0.20, 1.0), metallic=0.0, roughness=0.85)
    get_or_create_material("Mat_RoadMarking", (0.85, 0.85, 0.82, 1.0), metallic=0.0, roughness=0.6)
    get_or_create_material("Mat_SoilDark", (0.25, 0.20, 0.15, 1.0), metallic=0.0, roughness=0.95)
    get_or_create_material("Mat_FoliageBush", (0.28, 0.52, 0.22, 1.0), metallic=0.0, roughness=0.8)

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

def create_standard_solar_panel(name, location, rotation=(0,0,0), parent=None):
    frame = add_box(f"{name}_Frame", (0, 0, 0.02), (1.6, 1.0, 0.04), mat_name="Mat_CharcoalSteel")
    panel = add_box(f"{name}_Cells", (0, 0, 0.042), (1.52, 0.92, 0.01), mat_name="Mat_SolarPanel", parent=frame)
    line = add_box(f"{name}_Grid", (0, 0, 0.048), (0.02, 0.92, 0.005), mat_name="Mat_CharcoalSteel", parent=frame)
    frame.location = location
    frame.rotation_euler = rotation
    if parent:
        frame.parent = parent
    return frame

def create_slat_panel(name, location, width, height, thickness=0.04, slat_count=8, parent=None):
    container = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(container)
    container.location = location
    slat_w = (width / slat_count) * 0.7
    step = width / slat_count
    start_x = -width / 2.0 + step / 2.0
    for i in range(slat_count):
        x = start_x + i * step
        add_box(f"{name}_slat_{i}", (x, 0, height/2.0), (slat_w, thickness, height), mat_name="Mat_Timber", parent=container)
    add_box(f"{name}_rail_t", (0, 0, height - 0.03), (width, thickness * 1.5, 0.06), mat_name="Mat_CharcoalSteel", parent=container)
    add_box(f"{name}_rail_b", (0, 0, 0.03), (width, thickness * 1.5, 0.06), mat_name="Mat_CharcoalSteel", parent=container)
    if parent:
        container.parent = parent
    return container

# -------------------------------------------------------------
# 1. Research Lab (4 x 4 cells = 8m x 8m)
# -------------------------------------------------------------
def build_research_lab():
    clear_scene()
    setup_materials()
    root = bpy.data.objects.new("ResearchLab", None)
    bpy.context.scene.collection.objects.link(root)

    # Base Concrete Slab (8.2m x 8.2m x 0.2m)
    add_box("Lab_BaseSlab", (0, 0, 0.1), (8.2, 8.2, 0.2), mat_name="Mat_Concrete", parent=root)

    # Main 2-story building block (X: -4 to 1.5, Y: -4 to 4, Z: 0.2 to 5.4)
    main_volume = add_box("Lab_MainBody", (-1.2, 0, 2.7), (5.6, 7.8, 5.0), mat_name="Mat_Concrete", parent=root)
    # Timber slat panels on ground floor flanks
    create_slat_panel("Lab_Slat_FrontL", (-3.0, -3.95, 0.2), width=1.6, height=2.2, slat_count=8, parent=root)
    create_slat_panel("Lab_Slat_FrontR", (0.6, -3.95, 0.2), width=1.6, height=2.2, slat_count=8, parent=root)

    # Horizontal Band of Solid Tinted Teal Glass on 2nd Floor (Front & Sides)
    add_box("Lab_GlassRibbon_Front", (-1.2, -3.92, 3.8), (5.4, 0.1, 1.4), mat_name="Mat_TealGlass", parent=root)
    add_box("Lab_GlassRibbon_Frame", (-1.2, -3.94, 3.8), (5.5, 0.15, 1.45), mat_name="Mat_CharcoalSteel", parent=root)
    # Amber glowing trim line below ribbon
    add_box("Lab_AmberTrim", (-1.2, -3.96, 3.0), (5.5, 0.06, 0.08), mat_name="Mat_AmberGlow", parent=root)

    # Lower Roof Wing (Right side for Drone Landing Pad: X: 2.2m, Y: -1.0m, Z: 3.2m)
    drone_roof = add_box("Lab_DroneWing", (2.6, 0, 1.6), (2.8, 6.0, 3.0), mat_name="Mat_Concrete", parent=root)
    # Drone Pad Platform & Circle
    add_box("DronePad_Base", (2.6, 0, 3.15), (2.4, 2.4, 0.1), mat_name="Mat_CharcoalSteel", parent=root)
    add_cylinder("DronePad_Circle", (2.6, 0, 3.21), radius=0.9, depth=0.01, mat_name="Mat_RoadMarking", parent=root)
    # Drone Pad "H"
    add_box("DronePad_H_L", (2.3, 0, 3.22), (0.1, 0.8, 0.01), mat_name="Mat_RoadMarking", parent=root)
    add_box("DronePad_H_R", (2.9, 0, 3.22), (0.1, 0.8, 0.01), mat_name="Mat_RoadMarking", parent=root)
    add_box("DronePad_H_M", (2.6, 0, 3.22), (0.6, 0.1, 0.01), mat_name="Mat_RoadMarking", parent=root)

    # Floating Flat Entrance Canopy (Front at X = -1.2, Y = -4.8, Z = 2.4)
    canopy = add_box("Lab_EntranceCanopy", (-1.2, -4.5, 2.4), (2.4, 1.4, 0.15), mat_name="Mat_Concrete", parent=root)
    # Thin support posts
    add_cylinder("Canopy_Post_L", (-2.2, -5.0, 1.2), radius=0.05, depth=2.4, mat_name="Mat_CharcoalSteel", parent=root)
    add_cylinder("Canopy_Post_R", (-0.2, -5.0, 1.2), radius=0.05, depth=2.4, mat_name="Mat_CharcoalSteel", parent=root)

    # Rooftop Green Roof & Standard Solar Panels (Top of main block at Z = 5.2m)
    add_box("Lab_LivingRoof", (-1.2, 0, 5.25), (5.2, 7.4, 0.1), mat_name="Mat_LivingRoof", parent=root)
    for i in range(3):
        for j in range(2):
            px = -2.6 + j * 1.8
            py = -2.0 + i * 2.0
            create_standard_solar_panel(f"Lab_Solar_{i}_{j}", (px, py, 5.4), rotation=(math.radians(10), 0, 0), parent=root)

    # Chunky Satellite Dish on roof corner (X = 0.5, Y = 2.4, Z = 5.5)
    dish_base = add_cylinder("SatDish_Base", (0.5, 2.4, 5.4), radius=0.4, depth=0.3, mat_name="Mat_Concrete", parent=root)
    dish_stem = add_cylinder("SatDish_Stem", (0.5, 2.4, 5.8), radius=0.08, depth=0.6, mat_name="Mat_CharcoalSteel", parent=root)
    # Curved Dish
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.7, location=(0.5, 2.4, 6.3), segments=16, ring_count=10)
    dish = bpy.context.active_object
    dish.name = "SatDish_Bowl"
    dish.scale = (1.0, 0.35, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    dish.rotation_euler = (math.radians(35), 0, math.radians(-25))
    apply_mat(dish, "Mat_Concrete")
    dish.parent = root

    # Interactive Double Sliding Entrance Doors (at X = -1.2, Y = -3.95, Z: 0.2 to 2.4)
    door_l = add_box("ResearchLab_Door_L", (-1.65, -3.92, 1.2), (0.9, 0.06, 2.2), mat_name="Mat_TealGlass")
    door_frame_l = add_box("Lab_Door_L_Frame", (-1.65, -3.92, 1.2), (0.92, 0.08, 2.22), mat_name="Mat_CharcoalSteel", parent=door_l)
    door_l.parent = root

    door_r = add_box("ResearchLab_Door_R", (-0.75, -3.92, 1.2), (0.9, 0.06, 2.2), mat_name="Mat_TealGlass")
    door_frame_r = add_box("Lab_Door_R_Frame", (-0.75, -3.92, 1.2), (0.92, 0.08, 2.22), mat_name="Mat_CharcoalSteel", parent=door_r)
    door_r.parent = root

    fbx_path = os.path.join(BUILDINGS_DIR, "ResearchLab.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported:", fbx_path)

# -------------------------------------------------------------
# 2. Ranger Station with Lookout & Drone Pad (3 x 3 cells = 6m x 6m)
# -------------------------------------------------------------
def build_ranger_station():
    clear_scene()
    setup_materials()
    root = bpy.data.objects.new("RangerStation", None)
    bpy.context.scene.collection.objects.link(root)

    # Base Concrete Pad (6.2m x 6.2m x 0.2m)
    add_box("Ranger_BasePad", (0, 0, 0.1), (6.2, 6.2, 0.2), mat_name="Mat_Concrete", parent=root)

    # Ground Modular Container (X: -1.5m, Y: -0.5m, Z = 1.4m, Size: 3.2m x 4.4m x 2.6m)
    body = add_box("Ranger_Body_Ground", (-1.2, -0.6, 1.4), (3.2, 4.4, 2.6), mat_name="Mat_CharcoalSteel", parent=root)
    # Timber slat infill on walls
    create_slat_panel("Ranger_Slat_Front", (-1.2, -2.82, 0.2), width=3.0, height=2.4, slat_count=10, parent=root)
    create_slat_panel("Ranger_Slat_Side", (-2.82, -0.6, 0.2), width=4.0, height=2.4, slat_count=12, parent=root)

    # Upper Roof Terrace with Green Roof & Drone Landing Pad
    add_box("Ranger_TerraceRoof", (-1.2, -0.6, 2.75), (3.2, 4.4, 0.15), mat_name="Mat_LivingRoof", parent=root)
    # Small Drone Pad on Roof
    add_box("Ranger_DronePad", (-1.2, -1.8, 2.85), (1.8, 1.8, 0.05), mat_name="Mat_CharcoalSteel", parent=root)
    add_cylinder("Ranger_DroneCircle", (-1.2, -1.8, 2.88), radius=0.7, depth=0.01, mat_name="Mat_RoadMarking", parent=root)

    # Standard Solar Panels (1.6m x 1.0m unit, matching ratio!)
    create_standard_solar_panel("Ranger_Solar_1", (-1.2, 0.6, 3.0), rotation=(math.radians(12), 0, 0), parent=root)

    # Tall Square Lookout Tower (X: 1.8m, Y: 1.0m, Height: 8.5m)
    # 4 Steel Column Legs
    for lx, ly in [(0.8, 0.0), (0.8, 2.0), (2.6, 0.0), (2.6, 2.0)]:
        add_box(f"Tower_Leg_{lx}_{ly}", (lx, ly, 3.4), (0.2, 0.2, 6.6), mat_name="Mat_CharcoalSteel", parent=root)
    # Cross braces
    for z in [2.0, 4.0, 5.8]:
        add_box(f"Tower_Brace_X1_{z}", (1.7, 0.0, z), (1.8, 0.1, 0.1), mat_name="Mat_CharcoalSteel", parent=root)
        add_box(f"Tower_Brace_X2_{z}", (1.7, 2.0, z), (1.8, 0.1, 0.1), mat_name="Mat_CharcoalSteel", parent=root)
        add_box(f"Tower_Brace_Y1_{z}", (0.8, 1.0, z), (0.1, 1.8, 0.1), mat_name="Mat_CharcoalSteel", parent=root)
        add_box(f"Tower_Brace_Y2_{z}", (2.6, 1.0, z), (0.1, 1.8, 0.1), mat_name="Mat_CharcoalSteel", parent=root)

    # Enclosed Observation Cabin on top of tower (Z: 6.8 to 8.6)
    cabin_floor = add_box("Lookout_Floor", (1.7, 1.0, 6.75), (2.2, 2.2, 0.2), mat_name="Mat_Concrete", parent=root)
    # Tinted Teal 360-degree glass cabin
    add_box("Lookout_Glass_Cabin", (1.7, 1.0, 7.6), (2.0, 2.0, 1.5), mat_name="Mat_TealGlass", parent=root)
    add_box("Lookout_Cabin_Frame", (1.7, 1.0, 7.6), (2.05, 2.05, 1.55), mat_name="Mat_CharcoalSteel", parent=root)
    # Overhanging flat roof
    add_box("Lookout_Roof", (1.7, 1.0, 8.45), (2.4, 2.4, 0.2), mat_name="Mat_Concrete", parent=root)
    # Brass gold beacon cap
    add_cylinder("Lookout_Beacon", (1.7, 1.0, 8.7), radius=0.15, depth=0.3, mat_name="Mat_BrassGold", parent=root)

    # Exterior Steel Stairs linking Ground to 1st Floor Roof
    stair_rail = add_box("Stairs_Stringer", (0.5, -1.0, 1.4), (0.1, 2.2, 0.1), mat_name="Mat_CharcoalSteel", parent=root)
    for i in range(8):
        sz = 0.35 + i * 0.3
        sy = -2.0 + i * 0.25
        add_box(f"Stair_Tread_{i}", (0.5, sy, sz), (0.8, 0.25, 0.05), mat_name="Mat_CharcoalSteel", parent=root)

    # Interactive Staff Entry Door (Front at X = -1.2, Y = -2.85, Z: 0.2 to 2.4)
    # Hinge on right side (X = -0.7)
    door = add_box("RangerStation_Door", (-1.2, -2.84, 1.2), (0.9, 0.06, 2.2), mat_name="Mat_CharcoalSteel")
    handle = add_box("Ranger_Door_Handle", (-1.55, -2.88, 1.2), (0.05, 0.06, 0.2), mat_name="Mat_BrassGold", parent=door)
    bpy.context.view_layer.objects.active = door
    bpy.ops.object.select_all(action='DESELECT')
    door.select_set(True)
    bpy.context.scene.cursor.location = (-0.75, -2.84, 0.0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    door.parent = root

    fbx_path = os.path.join(BUILDINGS_DIR, "RangerStation.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported:", fbx_path)

# -------------------------------------------------------------
# 3. Automated Dinosaur Feeder (1 x 1 cell = 2m x 2m)
# -------------------------------------------------------------
def build_automated_feeder():
    clear_scene()
    setup_materials()
    root = bpy.data.objects.new("AutomatedFeeder", None)
    bpy.context.scene.collection.objects.link(root)

    # Concrete Footing Boots
    for x, y in [(-0.6, -0.6), (-0.6, 0.6), (0.6, -0.6), (0.6, 0.6)]:
        add_box(f"Feeder_Boot_{x}_{y}", (x, y, 0.15), (0.3, 0.3, 0.3), mat_name="Mat_Concrete", parent=root)
        # Stout charcoal legs
        add_box(f"Feeder_Leg_{x}_{y}", (x, y, 0.8), (0.15, 0.15, 1.0), mat_name="Mat_CharcoalSteel", parent=root)

    # Steel Hopper Body (Z: 1.3 to 2.4)
    add_box("Hopper_Body", (0, 0, 1.8), (1.5, 1.5, 1.0), mat_name="Mat_CharcoalSteel", parent=root)
    # Angled chute funnel
    add_box("Hopper_Funnel", (0, 0, 1.15), (0.7, 0.7, 0.3), mat_name="Mat_CharcoalSteel", parent=root)
    # Feed delivery chute pipe extending forward
    add_box("Feed_Chute", (0, 0.5, 0.9), (0.4, 0.6, 0.3), mat_name="Mat_CharcoalSteel", parent=root)

    # Concrete Trough Basin in front (Z: 0 to 0.5)
    trough = add_box("Feed_Trough_Basin", (0, 0.9, 0.25), (1.4, 0.8, 0.5), mat_name="Mat_Concrete", parent=root)
    # Green plants / Food chunks in trough
    add_box("Feed_Foliage", (0, 0.9, 0.42), (1.2, 0.6, 0.1), mat_name="Mat_LivingRoof", parent=root)

    # Mini Solar Panel on Hopper top (0.8m x 0.5m)
    add_box("Feeder_Solar", (0, 0, 2.35), (0.9, 0.6, 0.04), mat_name="Mat_SolarPanel", parent=root)
    # Brass Gold Status Light
    add_cylinder("Feeder_Status_Light", (0, 0.76, 1.8), radius=0.08, depth=0.1, rotation=(math.radians(90), 0, 0), mat_name="Mat_BrassGold", parent=root)

    fbx_path = os.path.join(ENCLOSURES_DIR, "AutomatedFeeder.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported:", fbx_path)

# -------------------------------------------------------------
# 4. Panoramic Viewing Wall (1 cell = 2.0m wide x 3.0m tall)
# -------------------------------------------------------------
def build_viewing_wall():
    clear_scene()
    setup_materials()
    root = bpy.data.objects.new("ViewingWall", None)
    bpy.context.scene.collection.objects.link(root)

    # Concrete footing block & low step
    add_box("ViewingWall_Footing", (0, 0, 0.2), (2.0, 0.6, 0.4), mat_name="Mat_Concrete", parent=root)
    # Heavy off-white concrete portal frame
    add_box("ViewingWall_Pillar_L", (-0.9, 0, 1.7), (0.2, 0.4, 2.6), mat_name="Mat_Concrete", parent=root)
    add_box("ViewingWall_Pillar_R", (0.9, 0, 1.7), (0.2, 0.4, 2.6), mat_name="Mat_Concrete", parent=root)
    add_box("ViewingWall_Beam_Top", (0, 0, 2.9), (2.0, 0.4, 0.2), mat_name="Mat_Concrete", parent=root)

    # Large tinted teal viewing panel in the middle
    add_box("ViewingWall_TealGlass", (0, 0, 1.6), (1.6, 0.08, 2.2), mat_name="Mat_TealGlass", parent=root)
    add_box("ViewingWall_GlassFrame", (0, 0, 1.6), (1.64, 0.12, 2.24), mat_name="Mat_CharcoalSteel", parent=root)
    # Timber lean rail for visitors
    add_box("Visitor_Lean_Rail", (0, -0.25, 1.1), (1.8, 0.12, 0.06), mat_name="Mat_Timber", parent=root)

    fbx_path = os.path.join(ENCLOSURES_DIR, "ViewingWall.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported:", fbx_path)

# -------------------------------------------------------------
# 5. Modern Park Lamp Post & Park Bench
# -------------------------------------------------------------
def build_props():
    # Lamp Post (3.5m tall)
    clear_scene()
    setup_materials()
    root_l = bpy.data.objects.new("ModernLampPost", None)
    bpy.context.scene.collection.objects.link(root_l)

    # Concrete Base Block
    add_box("Lamp_ConcreteBase", (0, 0, 0.2), (0.45, 0.45, 0.4), mat_name="Mat_Concrete", parent=root_l)
    # Charcoal Steel Pole
    add_cylinder("Lamp_Pole", (0, 0, 1.8), radius=0.08, depth=3.2, mat_name="Mat_CharcoalSteel", parent=root_l)
    # Curved Arched Arm
    add_cylinder("Lamp_Arm", (0.35, 0, 3.4), radius=0.06, depth=0.7, rotation=(0, math.radians(60), 0), mat_name="Mat_CharcoalSteel", parent=root_l)
    # Round Brass Gold LED Lamp Head
    add_cylinder("Lamp_Head", (0.65, 0, 3.35), radius=0.22, depth=0.12, mat_name="Mat_BrassGold", parent=root_l)
    # Mini Solar Panel on Pole
    add_box("Lamp_Solar", (-0.15, 0, 2.6), (0.4, 0.3, 0.03), mat_name="Mat_SolarPanel", parent=root_l)

    fbx_path = os.path.join(PROPS_DIR, "ModernLampPost.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported:", fbx_path)

    # Park Bench (1.8m wide)
    clear_scene()
    setup_materials()
    root_b = bpy.data.objects.new("ParkBench", None)
    bpy.context.scene.collection.objects.link(root_b)

    # Concrete Side Legs (X: -0.85m, +0.85m)
    for x in [-0.85, 0.85]:
        add_box(f"Bench_Leg_{x}", (x, 0, 0.35), (0.16, 0.6, 0.7), mat_name="Mat_Concrete", parent=root_b)
        # Charcoal Armrest
        add_box(f"Bench_Armrest_{x}", (x, 0, 0.72), (0.14, 0.55, 0.05), mat_name="Mat_CharcoalSteel", parent=root_b)

    # Light Timber Slats for Seat (4 slats)
    for i in range(4):
        y = -0.18 + i * 0.12
        add_box(f"Seat_Slat_{i}", (0, y, 0.45), (1.6, 0.09, 0.04), mat_name="Mat_Timber", parent=root_b)
    # Light Timber Slats for Backrest (3 slats)
    for i in range(3):
        z = 0.58 + i * 0.12
        add_box(f"Back_Slat_{i}", (0, 0.22, z), (1.6, 0.04, 0.09), mat_name="Mat_Timber", parent=root_b)

    fbx_path = os.path.join(PROPS_DIR, "ParkBench.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported:", fbx_path)

    # Planter (1 x 1 cell = 2m x 2m)
    clear_scene()
    setup_materials()
    root_p = bpy.data.objects.new("Planter", None)
    bpy.context.scene.collection.objects.link(root_p)

    add_box("Planter_ConcreteBox", (0, 0, 0.3), (2.0, 2.0, 0.6), mat_name="Mat_Concrete", parent=root_p)
    add_box("Planter_TimberRim", (0, 0, 0.62), (2.05, 2.05, 0.05), mat_name="Mat_Timber", parent=root_p)
    add_box("Planter_Soil", (0, 0, 0.58), (1.7, 1.7, 0.05), mat_name="Mat_SoilDark", parent=root_p)
    # Bush/Shrub center cluster
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.65, location=(0, 0, 0.95))
    bush = bpy.context.active_object
    bush.name = "Planter_Bush"
    apply_mat(bush, "Mat_FoliageBush")
    bush.parent = root_p

    fbx_path = os.path.join(PROPS_DIR, "Planter.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported:", fbx_path)

# -------------------------------------------------------------
# 6. Complete Modular Road Kit (Straight, Corner, TJunction, End, Walkways)
# -------------------------------------------------------------
def build_road_kit():
    # Corner (4m x 4m = 2x2 cells)
    clear_scene()
    setup_materials()
    root_c = bpy.data.objects.new("ModularRoad_Corner", None)
    bpy.context.scene.collection.objects.link(root_c)
    add_box("Road_Surface", (0, 0, 0.025), (4.0, 4.0, 0.05), mat_name="Mat_RoadAsphalt", parent=root_c)
    # Outer Curbs (along X = -1.9 and Y = 1.9)
    add_box("Curb_Outer_X", (-1.9, 0, 0.06), (0.2, 4.0, 0.12), mat_name="Mat_Concrete", parent=root_c)
    add_box("Curb_Outer_Y", (0, 1.9, 0.06), (4.0, 0.2, 0.12), mat_name="Mat_Concrete", parent=root_c)
    # Corner Inner curb
    add_box("Curb_Inner", (1.9, -1.9, 0.06), (0.2, 0.2, 0.12), mat_name="Mat_Concrete", parent=root_c)
    # Curved Lane Line
    add_cylinder("Curve_Line", (-1.9, 1.9, 0.052), radius=1.9, depth=0.005, vertices=24, mat_name="Mat_BrassGold", parent=root_c)

    fbx_path = os.path.join(ROADS_DIR, "ModularRoad_Corner.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported:", fbx_path)

    # T-Junction (4m x 4m)
    clear_scene()
    setup_materials()
    root_t = bpy.data.objects.new("ModularRoad_TJunction", None)
    bpy.context.scene.collection.objects.link(root_t)
    add_box("Road_Surface", (0, 0, 0.025), (4.0, 4.0, 0.05), mat_name="Mat_RoadAsphalt", parent=root_t)
    # Top curb continuous along Y = +1.9
    add_box("Curb_Top", (0, 1.9, 0.06), (4.0, 0.2, 0.12), mat_name="Mat_Concrete", parent=root_t)
    # Bottom corner curbs
    add_box("Curb_Bot_L", (-1.9, -1.9, 0.06), (0.2, 0.2, 0.12), mat_name="Mat_Concrete", parent=root_t)
    add_box("Curb_Bot_R", (1.9, -1.9, 0.06), (0.2, 0.2, 0.12), mat_name="Mat_Concrete", parent=root_t)

    fbx_path = os.path.join(ROADS_DIR, "ModularRoad_TJunction.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported:", fbx_path)

    # Road End / Cul-de-sac (4m x 4m)
    clear_scene()
    setup_materials()
    root_e = bpy.data.objects.new("ModularRoad_End", None)
    bpy.context.scene.collection.objects.link(root_e)
    add_box("Road_Surface", (0, 0, 0.025), (4.0, 4.0, 0.05), mat_name="Mat_RoadAsphalt", parent=root_e)
    add_box("Curb_L", (-1.9, 0, 0.06), (0.2, 4.0, 0.12), mat_name="Mat_Concrete", parent=root_e)
    add_box("Curb_R", (1.9, 0, 0.06), (0.2, 4.0, 0.12), mat_name="Mat_Concrete", parent=root_e)
    add_box("Curb_End", (0, 1.9, 0.06), (4.0, 0.2, 0.12), mat_name="Mat_Concrete", parent=root_e)

    fbx_path = os.path.join(ROADS_DIR, "ModularRoad_End.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported:", fbx_path)

    # Pedestrian Walkway / Plaza Paver (2m x 2m = 1 cell)
    clear_scene()
    setup_materials()
    root_p = bpy.data.objects.new("PedestrianPath_Straight", None)
    bpy.context.scene.collection.objects.link(root_p)
    add_box("Path_ConcretePaver", (0, 0, 0.02), (2.0, 2.0, 0.04), mat_name="Mat_Concrete", parent=root_p)
    # Timber edging slats on edges (X: -0.98, +0.98)
    add_box("Edge_L", (-0.95, 0, 0.035), (0.1, 2.0, 0.07), mat_name="Mat_Timber", parent=root_p)
    add_box("Edge_R", (0.95, 0, 0.035), (0.1, 2.0, 0.07), mat_name="Mat_Timber", parent=root_p)

    fbx_path = os.path.join(ROADS_DIR, "PedestrianPath_Straight.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported:", fbx_path)

if __name__ == "__main__":
    print("=== BUILDING ENVIRONMENT ASSETS & ROAD KIT ===")
    build_research_lab()
    build_ranger_station()
    build_automated_feeder()
    build_viewing_wall()
    build_props()
    build_road_kit()
    print("=== ENVIRONMENT ASSETS COMPLETE ===")
