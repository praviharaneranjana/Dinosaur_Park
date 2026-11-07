"""v02 scene: new scene ISL2_Main with the reference-matched camera (+ reference overlay), sun, sky."""
sc = bpy.data.scenes.get("ISL2_Main") or bpy.data.scenes.new("ISL2_Main")
bpy.context.window.scene = sc
sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x, sc.render.resolution_y = 2400, 1792; sc.render.resolution_percentage = 50
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
sc.render.fps = 24; sc.frame_start, sc.frame_end = 1, 240
cam_d = J["camera"]
cd = bpy.data.cameras.get("ISL2_RefCam") or bpy.data.cameras.new("ISL2_RefCam")
cd.lens = cam_d["lens"]; cd.sensor_width = cam_d["sensor"]; cd.sensor_fit = 'HORIZONTAL'; cd.clip_start = 1; cd.clip_end = 5000
cam = bpy.data.objects.get("ISL2_RefCam") or bpy.data.objects.new("ISL2_RefCam", cd)
if cam.name not in sc.collection.objects: sc.collection.objects.link(cam)
cam.location = cam_d["location"]; cam.rotation_euler = (math.radians(90 - cam_d["pitch_deg"]), 0, 0); sc.camera = cam
img = bpy.data.images.get("ISL_reference.jpg") or bpy.data.images.load(ROOT + r"\_Reference\ISL_reference.jpg", check_existing=True)
cd.show_background_images = True
bg = cd.background_images[0] if len(cd.background_images) else cd.background_images.new()
bg.image = img; bg.alpha = 0.5; bg.display_depth = 'FRONT'; bg.frame_method = 'FIT'; bg.show_background_image = True
sun_d = bpy.data.lights.get("ISL2_Sun") or bpy.data.lights.new("ISL2_Sun", 'SUN'); sun_d.energy = 4.2; sun_d.angle = math.radians(2.5); sun_d.color = (1.0, 0.96, 0.9)
sun = bpy.data.objects.get("ISL2_Sun") or bpy.data.objects.new("ISL2_Sun", sun_d)
if sun.name not in sc.collection.objects: sc.collection.objects.link(sun)
sun.rotation_euler = (math.radians(40), math.radians(-28), math.radians(-35))   # light from upper-left like the reference
w = bpy.data.worlds.get("ISL2_World") or bpy.data.worlds.new("ISL2_World"); sc.world = w; w.use_nodes = True
bgn = w.node_tree.nodes.get("Background"); bgn.inputs[0].default_value = (*lin((170, 205, 230)), 1); bgn.inputs[1].default_value = 0.85
try:
    sc.eevee.use_shadows = True
except Exception: pass
result = {"scene": sc.name}
