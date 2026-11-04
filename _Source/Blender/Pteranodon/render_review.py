import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'ANM_Pteranodon_animated_review.blend'))
scene=bpy.context.scene;cam=scene.camera
geo=bpy.data.collections['01 • Pteranodon geometry']

# Final visual corrections identified from the side/grounded renders.
for ob in geo.objects:
    if ob.name.startswith(('Mouth seam','Shoulder muscle')):
        ob.hide_render=True;ob.hide_set(True)
    if ob.name.startswith('Jaw •'):
        for v in ob.data.vertices:
            t=max(0,min(1,(-v.co.y-.41)/1.38));v.co.z+=.028*math.sin(math.pi*t)
    if ob.name.startswith('Wing membrane'):
        m=ob.active_material;n=m.node_tree.nodes;l=m.node_tree.links
        if not n.get('Painted membrane variation'):
            mix=n.new('ShaderNodeMixRGB');mix.name='Painted membrane variation';mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.22
            attr=next(x for x in n if x.type=='VERTEX_COLOR');noise=next(x for x in n if x.type=='TEX_NOISE')
            l.new(attr.outputs['Color'],mix.inputs[1]);l.new(noise.outputs['Fac'],mix.inputs[2]);l.new(mix.outputs[0],n.get('Principled BSDF').inputs['Base Color'])

scene.frame_set(1)
def camera(loc,target,scale):
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
camera((5,-7,6.1),(0,-.12,2.15),7.4)
scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.cycles.samples=28
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False
scene.render.filepath=str(OUT/'renders/final_hero.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ANM_Pteranodon.blend'))
bpy.ops.render.render(write_still=True)
views=[
 ('front',(0,-10,3.5),(0,0,2.0),7.2,1),
 ('back',(0,10,4.2),(0,0,2.0),7.2,1),
 ('left_side',(-10,0,3.0),(0,-.25,2.1),4.2,1),
 ('right_side',(10,0,3.0),(0,-.25,2.1),4.2,1),
 ('top',(0,0,12),(0,0,1.7),7.4,1),
 ('underside',(0,-.01,-8),(0,0,2.0),7.4,1),
 ('grounded',(5,-7,3.6),(0,-.05,1.1),3.8,480),
 ('grounded_side',(8,0,2.2),(0,-.1,1.1),3.8,480),
 ('takeoff_push',(8,0,2.5),(0,-.05,1.25),4.2,797),
 ('feeding',(6,-5,3.4),(0,-.1,1),4.2,689)
]
scene.render.resolution_x=1000;scene.render.resolution_y=800;scene.cycles.samples=18
for name,loc,target,scale,frame in views:
    scene.frame_set(frame);camera(loc,target,scale)
    ground=bpy.data.objects['Ground • render only'];ground.hide_render=name=='underside'
    scene.render.filepath=str(OUT/'renders'/('view_'+name+'.png'));bpy.ops.render.render(write_still=True)
print('REVIEW_VIEWS_COMPLETE')
