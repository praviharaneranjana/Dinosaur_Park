"""Render a short preview loop of the current scene: set NAME, FRAMES (end), STEP, RES before exec."""
import bpy, json, time
ROOT = r"D:\Unity Projects\Dinosaur_Park\Dinosaur_Park\_Source\Blender"
sc = bpy.context.scene; t0 = time.time()
old = (sc.render.resolution_x, sc.render.resolution_y, sc.eevee.taa_render_samples)
sc.frame_start = 1; sc.frame_end = FRAMES; sc.frame_step = STEP
sc.render.resolution_x, sc.render.resolution_y = RES; sc.eevee.taa_render_samples = 16
sc.render.image_settings.file_format = 'PNG'
sc.render.filepath = ROOT + r"\renders\terrain\anim\%s_" % NAME
bpy.ops.render.render(animation=True)
sc.render.resolution_x, sc.render.resolution_y, sc.eevee.taa_render_samples = old
sc.frame_set(1)
open(ROOT + r"\renders\terrain\anim\%s.json" % NAME, "w").write(json.dumps({"sec": round(time.time()-t0,1)}))
result = {"sec": round(time.time()-t0,1)}
