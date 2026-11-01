import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler

OUTPUT_DIR = r"D:\Unity Projects\Dinosaur_Park\Assets\Models\CyberDrone"
os.makedirs(OUTPUT_DIR, exist_ok=True)

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

def setup_cyber_materials():
    # Matte Black / Carbon Aerodynamic Chassis
    get_or_create_material("Mat_CyberChassis", (0.05, 0.05, 0.06, 1.0), metallic=0.85, roughness=0.28)
    # Dark Gunmetal Structural Steel
    get_or_create_material("Mat_Gunmetal", (0.12, 0.13, 0.15, 1.0), metallic=0.9, roughness=0.35)
    # Cockpit Tinted Glass
    get_or_create_material("Mat_CockpitGlass", (0.04, 0.08, 0.10, 1.0), metallic=0.2, roughness=0.08)
    # Luminous Cyan / Turquoise Neon Energy (Emissive Bloom)
    get_or_create_material("Mat_CyanNeon", (0.0, 0.96, 0.88, 1.0), metallic=0.0, roughness=0.1, emission_rgb=(0.0, 0.96, 0.88), emission_strength=5.0)
    # Neon White Headlight / Runway Light
    get_or_create_material("Mat_NeonWhite", (0.95, 0.98, 1.0, 1.0), metallic=0.0, roughness=0.1, emission_rgb=(0.95, 0.98, 1.0), emission_strength=4.0)
    # Dark Chrome Beaded Spheres for Arches
    get_or_create_material("Mat_DarkChrome", (0.10, 0.11, 0.13, 1.0), metallic=0.98, roughness=0.12)
    # Dark Lunar / Asteroid Rock
    get_or_create_material("Mat_AsteroidRock", (0.07, 0.07, 0.08, 1.0), metallic=0.1, roughness=0.92)
    # Runway Deck
    get_or_create_material("Mat_RunwayDeck", (0.04, 0.04, 0.05, 1.0), metallic=0.7, roughness=0.3)

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

# -------------------------------------------------------------
# 1. Sci-Fi Cyber Quad-Rotor Drone Car
# -------------------------------------------------------------
def build_cyber_drone_car():
    clear_scene()
    setup_cyber_materials()
    root = bpy.data.objects.new("SciFi_Drone_Car", None)
    bpy.context.scene.collection.objects.link(root)

    # Main Aerodynamic Chassis Fuselage (Length: 4.4m, Width: 1.9m, Height: 0.85m)
    # Center Body
    body = add_box("Fuselage_Main", (0, 0, 0.5), (1.8, 4.2, 0.65), mat_name="Mat_CyberChassis", parent=root)
    # Sloped Nose Hood
    nose = add_box("Fuselage_Nose", (0, 1.8, 0.42), (1.5, 1.2, 0.45), rotation=(math.radians(-15), 0, 0), mat_name="Mat_CyberChassis", parent=root)
    # Front Lower Splitter
    add_box("Front_Splitter", (0, 2.3, 0.2), (1.9, 0.6, 0.06), mat_name="Mat_Gunmetal", parent=root)
    # Canards
    add_box("Canard_L", (-1.0, 2.0, 0.3), (0.35, 0.4, 0.03), rotation=(0, math.radians(-15), math.radians(20)), mat_name="Mat_Gunmetal", parent=root)
    add_box("Canard_R", (1.0, 2.0, 0.3), (0.35, 0.4, 0.03), rotation=(0, math.radians(15), math.radians(-20)), mat_name="Mat_Gunmetal", parent=root)

    # Sleek Cockpit Canopy (Tinted Glass)
    canopy = add_box("Cockpit_Canopy", (0, 0.1, 0.88), (1.1, 1.9, 0.45), rotation=(math.radians(10), 0, 0), mat_name="Mat_CockpitGlass", parent=root)
    # Roof Air Intake Scoop
    add_box("Roof_Intake", (0, -0.6, 1.08), (0.55, 0.8, 0.18), mat_name="Mat_CyberChassis", parent=root)

    # Rear Aerodynamic GT Wing / Spoiler
    # Swan-neck Stanchions
    add_box("Wing_Pillar_L", (-0.7, -1.8, 1.0), (0.06, 0.3, 0.6), rotation=(math.radians(-20), 0, 0), mat_name="Mat_Gunmetal", parent=root)
    add_box("Wing_Pillar_R", (0.7, -1.8, 1.0), (0.06, 0.3, 0.6), rotation=(math.radians(-20), 0, 0), mat_name="Mat_Gunmetal", parent=root)
    # Wing Airfoil Blade (2.4m wide)
    wing = add_box("Rear_GT_Wing", (0, -2.0, 1.3), (2.4, 0.45, 0.06), rotation=(math.radians(-12), 0, 0), mat_name="Mat_CyberChassis", parent=root)
    # Wing Endplates
    add_box("Endplate_L", (-1.22, -2.0, 1.3), (0.04, 0.55, 0.3), mat_name="Mat_Gunmetal", parent=root)
    add_box("Endplate_R", (1.22, -2.0, 1.3), (0.04, 0.55, 0.3), mat_name="Mat_Gunmetal", parent=root)

    # Headlights & Underside Neon Accents
    add_box("Headlight_L", (-0.65, 2.2, 0.45), (0.3, 0.08, 0.06), mat_name="Mat_NeonWhite", parent=root)
    add_box("Headlight_R", (0.65, 2.2, 0.45), (0.3, 0.08, 0.06), mat_name="Mat_NeonWhite", parent=root)
    add_box("Underglow_Neon_L", (-0.92, 0, 0.22), (0.04, 3.2, 0.04), mat_name="Mat_CyanNeon", parent=root)
    add_box("Underglow_Neon_R", (0.92, 0, 0.22), (0.04, 3.2, 0.04), mat_name="Mat_CyanNeon", parent=root)

    # 4 Outrigger Quad-Rotor Ducted Thruster Pods
    # Positions: Front-Left, Front-Right, Rear-Left, Rear-Right
    rotor_offsets = [
        ("FL", -1.55, 1.35, 0.45, math.radians(8), math.radians(-12)),
        ("FR", 1.55, 1.35, 0.45, math.radians(8), math.radians(12)),
        ("RL", -1.65, -1.35, 0.55, math.radians(-6), math.radians(-10)),
        ("RR", 1.65, -1.35, 0.55, math.radians(-6), math.radians(10))
    ]

    for code, px, py, pz, tilt_p, tilt_r in rotor_offsets:
        # Structural Carbon/Steel Arm linking to chassis
        arm_dir = 1.0 if px > 0 else -1.0
        add_box(f"RotorArm_{code}", (px*0.55, py, pz - 0.05), (abs(px)*0.9, 0.25, 0.12), rotation=(tilt_p, tilt_r, 0), mat_name="Mat_Gunmetal", parent=root)

        # Ducted Fan Cowling (Cylinder with hole / bevel)
        duct = add_cylinder(f"Duct_Cowling_{code}", (px, py, pz), radius=0.68, depth=0.32, vertices=24, rotation=(tilt_p, tilt_r, 0), mat_name="Mat_CyberChassis", parent=root)

        # Inner Aerodynamic Ring
        inner = add_cylinder(f"Duct_Inner_{code}", (px, py, pz), radius=0.56, depth=0.34, vertices=24, rotation=(tilt_p, tilt_r, 0), mat_name="Mat_Gunmetal", parent=root)

        # Luminous Glowing Cyan Energy Torus Ring (The signature look!)
        bpy.ops.mesh.primitive_torus_add(location=(px, py, pz), major_radius=0.66, minor_radius=0.06, major_segments=24, minor_segments=12, rotation=(tilt_p, tilt_r, 0))
        glow_ring = bpy.context.active_object
        glow_ring.name = f"Neon_Thrust_Ring_{code}"
        apply_mat(glow_ring, "Mat_CyanNeon")
        glow_ring.parent = root

        # Rotating Fan Blades (Child object for rotation animation in Unity)
        fan_root = bpy.data.objects.new(f"RotorBlades_{code}", None)
        bpy.context.scene.collection.objects.link(fan_root)
        fan_root.location = (px, py, pz)
        fan_root.rotation_euler = (tilt_p, tilt_r, 0)
        fan_root.parent = root

        # Center spinner hub
        add_cylinder(f"FanHub_{code}", (0, 0, 0), radius=0.14, depth=0.22, vertices=16, mat_name="Mat_Gunmetal", parent=fan_root)
        # 4 Turbine blades
        for b in range(4):
            ang = math.radians(b * 90)
            add_box(f"Blade_{code}_{b}", (0, 0, 0), (0.08, 0.52, 0.03), rotation=(0, 0, ang), mat_name="Mat_CyberChassis", parent=fan_root)

    fbx_path = os.path.join(OUTPUT_DIR, "SciFi_Drone_Car.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported Sci-Fi Drone Car:", fbx_path)

# -------------------------------------------------------------
# 2. Monumental Beaded Arch Portal (The Giant Sphere-Studded Arch)
# -------------------------------------------------------------
def build_monumental_beaded_arch():
    clear_scene()
    setup_cyber_materials()
    root = bpy.data.objects.new("Monumental_Beaded_Arch", None)
    bpy.context.scene.collection.objects.link(root)

    # Arch dimensions: Height: 24m, Outer Width: 18m, Clear inner span: 12m, Arch tube radius: 2.2m
    arch_radius = 8.0
    tube_radius = 2.0
    num_steps = 32  # Steps along the arch curve (0 to 180 degrees)
    beads_per_ring = 14 # Beads around tube cross section

    # Base Foundation Footings (Pillars extending down into bedrock)
    add_box("Footing_L", (-arch_radius, 0, 2.5), (4.5, 4.5, 5.0), mat_name="Mat_AsteroidRock", parent=root)
    add_box("Footing_R", (arch_radius, 0, 2.5), (4.5, 4.5, 5.0), mat_name="Mat_AsteroidRock", parent=root)

    # Core Arch Backbone Tube (Smooth dark structural interior)
    # We will build the beaded surface using instances of dark chrome spheres arranged in rings!
    # Left vertical leg (Z: 0 to 12m at X = -arch_radius)
    # Right vertical leg (Z: 0 to 12m at X = arch_radius)
    # Semi-circle top arch (from angle 0 to 180 deg)

    # Generate beads for left column (Z: 2m to 12m)
    for z in range(2, 13, 1):
        for b in range(beads_per_ring):
            ang = math.radians(b * (360 / beads_per_ring))
            bx = -arch_radius + math.cos(ang) * tube_radius
            by = math.sin(ang) * tube_radius
            bz = float(z)
            # Add bead sphere
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.42, location=(bx, by, bz), segments=10, ring_count=6)
            bead = bpy.context.active_object
            apply_mat(bead, "Mat_DarkChrome")
            bead.parent = root

    # Generate beads for right column (Z: 2m to 12m)
    for z in range(2, 13, 1):
        for b in range(beads_per_ring):
            ang = math.radians(b * (360 / beads_per_ring))
            bx = arch_radius + math.cos(ang) * tube_radius
            by = math.sin(ang) * tube_radius
            bz = float(z)
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.42, location=(bx, by, bz), segments=10, ring_count=6)
            bead = bpy.context.active_object
            apply_mat(bead, "Mat_DarkChrome")
            bead.parent = root

    # Generate beads for curved arch crown (Angle: 0 to 180 degrees)
    for s in range(num_steps + 1):
        theta = math.radians(s * (180.0 / num_steps))
        # Center of tube cross section at this station
        cx = arch_radius * math.cos(theta)
        cz = 12.0 + arch_radius * math.sin(theta)
        normal_x = math.cos(theta)
        normal_z = math.sin(theta)

        for b in range(beads_per_ring):
            phi = math.radians(b * (360 / beads_per_ring))
            # Offset in normal plane
            radial_y = math.sin(phi) * tube_radius
            radial_xz = math.cos(phi) * tube_radius

            bx = cx + normal_x * radial_xz
            by = radial_y
            bz = cz + normal_z * radial_xz

            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.42, location=(bx, by, bz), segments=10, ring_count=6)
            bead = bpy.context.active_object
            apply_mat(bead, "Mat_DarkChrome")
            bead.parent = root

    # Join beads together into a unified mesh to ensure low draw calls and high performance in Unity!
    bpy.ops.object.select_all(action='DESELECT')
    for child in root.children:
        if "Sphere" in child.name:
            child.select_set(True)
    if bpy.context.selected_objects:
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
        bpy.ops.object.join()
        joined_beads = bpy.context.active_object
        joined_beads.name = "Arch_Beaded_Shell"
        joined_beads.parent = root

    fbx_path = os.path.join(OUTPUT_DIR, "Monumental_Beaded_Arch.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported Monumental Beaded Arch:", fbx_path)

# -------------------------------------------------------------
# 3. Sci-Fi Launch Ramp Runway (with Glowing Neon Rails)
# -------------------------------------------------------------
def build_scifi_launch_ramp():
    clear_scene()
    setup_cyber_materials()
    root = bpy.data.objects.new("SciFi_Launch_Ramp", None)
    bpy.context.scene.collection.objects.link(root)

    # Runway Deck: Length 40m, Width 8m
    # Elevated cantilever ramp starting at Y = -40, ending at Y = 0 (the jump lip!)
    add_box("Ramp_Deck", (0, -20.0, 4.0), (8.0, 40.0, 0.4), mat_name="Mat_RunwayDeck", parent=root)
    # Tilted take-off kicker lip at the edge (Y = -2.0 to 0.0)
    add_box("Ramp_Kicker_Lip", (0, -1.0, 4.25), (8.0, 2.5, 0.35), rotation=(math.radians(6), 0, 0), mat_name="Mat_RunwayDeck", parent=root)

    # Dual Glowing Neon Cyan Guide Rail Strips along both edges
    add_box("Neon_Rail_L", (-3.85, -20.0, 4.4), (0.2, 40.0, 0.25), mat_name="Mat_CyanNeon", parent=root)
    add_box("Neon_Rail_R", (3.85, -20.0, 4.4), (0.2, 40.0, 0.25), mat_name="Mat_CyanNeon", parent=root)

    # White Runway Center Dash Striping
    for y in range(-38, -2, 4):
        add_box(f"Runway_Dash_{y}", (0, float(y), 4.22), (0.35, 1.8, 0.01), mat_name="Mat_NeonWhite", parent=root)

    # Heavy Steel Support Trusses underneath
    for py in [-35, -25, -15]:
        # Pier Column
        add_box(f"Ramp_Pier_{py}", (0, py, 1.8), (7.4, 1.2, 3.8), mat_name="Mat_Gunmetal", parent=root)

    # Edge Barrier Caps
    add_box("Edge_Barrier_L", (-3.95, -20.0, 4.5), (0.25, 40.0, 0.6), mat_name="Mat_Gunmetal", parent=root)
    add_box("Edge_Barrier_R", (3.95, -20.0, 4.5), (0.25, 40.0, 0.6), mat_name="Mat_Gunmetal", parent=root)

    fbx_path = os.path.join(OUTPUT_DIR, "SciFi_Launch_Ramp.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported Sci-Fi Launch Ramp:", fbx_path)

# -------------------------------------------------------------
# 4. Asteroid Bedrock Terrain Clustered Crags
# -------------------------------------------------------------
def build_asteroid_terrain():
    clear_scene()
    setup_cyber_materials()
    root = bpy.data.objects.new("Asteroid_Crag_Terrain", None)
    bpy.context.scene.collection.objects.link(root)

    # Jagged cliff base
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -2.0))
    crag = bpy.context.active_object
    crag.name = "Crag_Mesh"
    crag.scale = (24.0, 24.0, 5.0)
    bpy.ops.object.transform_apply(scale=True)
    # Add displace or bevel for rocky feel
    mod = crag.modifiers.new(name="Bevel", type='BEVEL')
    mod.width = 1.2
    mod.segments = 2
    apply_mat(crag, "Mat_AsteroidRock")
    crag.parent = root

    fbx_path = os.path.join(OUTPUT_DIR, "Asteroid_Crag_Terrain.fbx")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=True)
    print("Exported Asteroid Crag Terrain:", fbx_path)

if __name__ == "__main__":
    print("=== BUILDING SCI-FI CYBER DRONE & BEADED ARCH ASSETS ===")
    build_cyber_drone_car()
    build_monumental_beaded_arch()
    build_scifi_launch_ramp()
    build_asteroid_terrain()
    print("=== ALL ASSETS GENERATED SUCCESSFULLY ===")
