"""Original editable Pteranodon review model. Run with Blender 5.2 --background.
Fresh scene only; never reads, changes or overwrites the existing building files.
"""
import bpy, math, random, json, sys
from pathlib import Path
from mathutils import Vector, Matrix
from math import sin, cos, pi

OUT=Path(__file__).resolve().parent
random.seed(41)
scene=bpy.data.scenes.new('ANM_Pteranodon • model review')
bpy.context.window.scene=scene
geo=bpy.data.collections.new('01 • Pteranodon geometry'); scene.collection.children.link(geo)
rigcol=bpy.data.collections.new('02 • Animation rig'); scene.collection.children.link(rigcol)
studio=bpy.data.collections.new('03 • Studio — presentation only'); scene.collection.children.link(studio)
refcol=bpy.data.collections.new('04 • Reference — not for export'); scene.collection.children.link(refcol)

def linear(h):
    h=h.lstrip('#'); rgb=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(c/12.92 if c<.04045 else ((c+.055)/1.055)**2.4 for c in rgb)+(1,)

def mat(name,a,b=None,rough=.8):
    m=bpy.data.materials.new(name); m.diffuse_color=linear(a); m.use_nodes=True
    n=m.node_tree.nodes; l=m.node_tree.links; bs=n.get('Principled BSDF')
    bs.inputs['Roughness'].default_value=rough
    if b:
        noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=7; noise.inputs['Detail'].default_value=2.5; noise.inputs['Roughness'].default_value=.65
        ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.2; ramp.color_ramp.elements[0].color=linear(a); ramp.color_ramp.elements[1].position=.8; ramp.color_ramp.elements[1].color=linear(b)
        l.new(noise.outputs['Fac'],ramp.inputs[0]); l.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.09; bump.inputs['Distance'].default_value=.018
        l.new(noise.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs['Normal'],bs.inputs['Normal'])
    else: bs.inputs['Base Color'].default_value=linear(a)
    return m

skin=mat('Skin • warm ash / soft painted variation','#635E53','#827A6B')
dark=mat('Wing spar / beak edges • charcoal taupe','#504D44','#71695C')
cream=mat('Throat • warm ivory','#D5CCAB','#F0E6CB')
beak=mat('Beak • weathered warm grey','#817969','#ACA18B')
mouth=mat('Mouth seam • muted umber','#3B342B')
claw=mat('Claws • dark horn','#544E42')
orange=mat('Crest • ochre orange','#BE6115','#E58A23')
crestedge=mat('Crest edge • deep ochre','#AF6C2B')
eye=mat('Eyes • obsidian', '#191B16',rough=.26)
iris=mat('Iris • subdued amber', '#655236',rough=.4)
glint=mat('Eye glint', '#F5EEDB',rough=.2)
mem=mat('Membrane • painted sand','#BA996B','#D6BB89')
mn=mem.node_tree.nodes; ml=mem.node_tree.links
attr=mn.new('ShaderNodeVertexColor'); attr.layer_name='Wing paint'
bs=mn.get('Principled BSDF'); ml.new(attr.outputs['Color'],bs.inputs['Base Color'])
bs.inputs['Subsurface Weight'].default_value=.035
floorMat=mat('Studio • warm grey','#B9BAB7')

arm=bpy.data.armatures.new('Pteranodon skeleton'); rig=bpy.data.objects.new('RIG_Pteranodon',arm); rigcol.objects.link(rig)
bpy.context.view_layer.objects.active=rig; rig.select_set(True); bpy.ops.object.mode_set(mode='EDIT')
bone_defs={}
def bone(name,a,b,parent=None):
    e=arm.edit_bones.new(name); e.head=a; e.tail=b; e.align_roll(Vector((0,0,1)))
    if parent:e.parent=arm.edit_bones[parent]
    bone_defs[name]=(Vector(a),Vector(b),parent)
bone('root',(0,0,0),(0,0,.35))
bone('body',(0,.35,1.42),(0,-.25,1.67),'root')
bone('neck',(0,-.25,1.67),(0,-.53,1.98),'body')
bone('head',(0,-.53,1.98),(0,-1.12,1.77),'neck')
bone('jaw',(0,-.4,1.83),(0,-1.35,1.39),'head')
wing_pts={}
for side,s in [('L',1),('R',-1)]:
    pts=[(s*.23,-.27,1.69),(s*.69,.015,1.62),(s*1.16,-.17,1.78),(s*1.46,-.25,1.79),(s*2.09,-.015,1.59),(s*2.63,.25,1.37),(s*3.08,.56,1.2),(s*3.28,.71,1.14)]
    wing_pts[side]=[Vector(p) for p in pts]
    names=['upper_arm','forearm','hand','wing_1','wing_2','wing_3','wing_4']
    par='body'
    for i,n in enumerate(names): bone(n+'.'+side,pts[i],pts[i+1],par); par=n+'.'+side
    bone('thigh.'+side,(s*.16,.4,1.39),(s*.26,.63,1.14),'body')
    bone('shin.'+side,(s*.26,.63,1.14),(s*.27,.48,.98),'thigh.'+side)
    bone('foot.'+side,(s*.27,.48,.98),(s*.27,.29,.94),'shin.'+side)
bpy.ops.object.mode_set(mode='OBJECT'); rig.show_in_front=True; arm.display_type='OCTAHEDRAL'

def mesh(name,verts,faces,material,weights=None,sub=0):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update(); me.validate()
    ob=bpy.data.objects.new(name,me); geo.objects.link(ob); ob.data.materials.append(material)
    for p in me.polygons:p.use_smooth=True
    if weights:
        groups={}
        for i,w in enumerate(weights):
            for name,value in w.items():
                if value<=.0001:continue
                if name not in groups:groups[name]=ob.vertex_groups.new(name=name)
                groups[name].add([i],value,'REPLACE')
        mod=ob.modifiers.new('Anatomical deformation','ARMATURE'); mod.object=rig
    if sub:
        mod=ob.modifiers.new('Silhouette smoothing','SUBSURF'); mod.levels=sub; mod.render_levels=sub
    return ob

def cat(points,steps=5):
    arr=[Vector(p) for p in points]; out=[]
    for i in range(len(arr)-1):
        p0=arr[max(0,i-1)];p1=arr[i];p2=arr[i+1];p3=arr[min(len(arr)-1,i+2)]
        for j in range(steps):
            t=j/steps
            out.append((p1*2+(-p0+p2)*t+(p0*2-p1*5+p2*4-p3)*t*t+(-p0+p1*3-p2*3+p3)*t*t*t)*.5)
    out.append(arr[-1]);return out

def tube(name,points,radii,material,bn='body',sides=10,steps=4):
    path=cat([(*p,r) for p,r in zip(points,radii)],steps)
    vs=[];fs=[];ws=[]
    for i,p in enumerate(path):
        co=Vector(p[:3]); prev=Vector(path[max(i-1,0)][:3]); nxt=Vector(path[min(i+1,len(path)-1)][:3]); d=(nxt-prev).normalized()
        u=d.cross(Vector((0,1,0))).normalized()
        if u.length<.1:u=d.cross(Vector((1,0,0))).normalized()
        v=d.cross(u).normalized()
        for j in range(sides):
            a=2*pi*j/sides; vs.append(co+(u*cos(a)+v*sin(a))*max(p[3],.001))
            ws.append(bn(co) if callable(bn) else {bn:1})
    for i in range(len(path)-1):
        for j in range(sides):
            a=i*sides+j;b=i*sides+(j+1)%sides;fs.append((a,b,b+sides,a+sides))
    fs.append(tuple(reversed(range(sides))));fs.append(tuple((len(path)-1)*sides+j for j in range(sides)))
    return mesh(name,vs,fs,material,ws)

def loft(name,rings,material,weight='body',sides=24,steps=4):
    rows=cat(rings,steps);vs=[];fs=[];ws=[]
    for y,z,rx,rz in rows:
        for j in range(sides):
            a=2*pi*j/sides;co=Vector((max(rx,.001)*cos(a),y,z+max(rz,.001)*sin(a)))
            vs.append(co);ws.append(weight(co) if callable(weight) else {weight:1})
    for i in range(len(rows)-1):
        for j in range(sides):
            a=i*sides+j;b=i*sides+(j+1)%sides;fs.append((a,b,b+sides,a+sides))
    fs.extend([tuple(reversed(range(sides))),tuple((len(rows)-1)*sides+j for j in range(sides))])
    return mesh(name,vs,fs,material,ws)

def ellipsoid(name,loc,scale,material,bn='body',seg=20,rings=12):
    vs=[];fs=[]
    for i in range(rings+1):
        t=pi*max(.001,min(rings-.001,i))/rings
        for j in range(seg):
            a=2*pi*j/seg;vs.append((loc[0]+scale[0]*sin(t)*cos(a),loc[1]+scale[1]*sin(t)*sin(a),loc[2]+scale[2]*cos(t)))
    for i in range(rings):
        for j in range(seg):
            a=i*seg+j;b=i*seg+(j+1)%seg;fs.append((a,b,b+seg,a+seg))
    return mesh(name,vs,fs,material,[{bn:1} for v in vs])

def body_weights(co):
    t=max(0,min(1,(-co.y-.20)/.30));return {'body':1-t,'neck':t}

body=loft('Body • continuous chest neck back',[(.82,1.38,.015,.025),(.64,1.43,.13,.15),(.36,1.51,.235,.25),(.03,1.57,.285,.30),(-.24,1.65,.27,.30),(-.43,1.80,.18,.26),(-.54,1.98,.12,.15)],skin,body_weights)
bodymat=skin.copy();bodymat.name='Body paint • cream breast fading into ash';body.data.materials[0]=bodymat
paint=body.data.color_attributes.new(name='Body paint',type='FLOAT_COLOR',domain='POINT')
for a,v in zip(paint.data,body.data.vertices):
    c=v.co;edge=1.64+(-c.y)*.40 + .018*sin(c.x*55+c.y*38)
    t=max(0,min(1,(edge-c.z)/.085))*max(0,min(1,(.20-c.y)/.20))
    col=Vector(linear('#7D7566')[:3]).lerp(Vector(linear('#E6D9B8')[:3]),t)
    a.color=(*col,1)
pa=bodymat.node_tree.nodes.new('ShaderNodeVertexColor');pa.layer_name='Body paint';bodymat.node_tree.links.new(pa.outputs['Color'],bodymat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])

head=loft('Head • skull flowing into toothless upper beak',[(-.26,2.02,.07,.1),(-.40,2.055,.145,.19),(-.58,2.035,.175,.20),(-.75,1.94,.13,.145),(-.98,1.77,.09,.10),(-1.25,1.56,.058,.067),(-1.58,1.34,.025,.036),(-1.79,1.22,.0015,.003)],beak,'head',28,5)
jaw=loft('Jaw • separate articulated lower beak',[(-.41,1.85,.095,.045),(-.65,1.80,.126,.053),(-.92,1.63,.087,.044),(-1.25,1.465,.052,.029),(-1.55,1.325,.022,.018),(-1.785,1.215,.002,.003)],beak,'jaw',20,4)
for s in [-1,1]:
    tube('Mouth seam '+str(s),[(s*.124,-.60,1.845),(s*.096,-.9,1.68),(s*.061,-1.18,1.48),(s*.027,-1.55,1.25)],[.013,.011,.007,.002],mouth,'head',8,4)
    ellipsoid('Eye socket '+str(s),(s*.155,-.568,2.065),(.019,.067,.060),dark,'head')
    ellipsoid('Amber iris '+str(s),(s*.172,-.58,2.067),(.012,.035,.039),iris,'head')
    ellipsoid('Eye '+str(s),(s*.181,-.586,2.067),(.009,.025,.031),eye,'head')
    ellipsoid('Eye glint '+str(s),(s*.189,-.597,2.081),(.002,.006,.006),glint,'head',10,6)
    tube('Sculpted brow '+str(s),[(s*.147,-.66,2.099),(s*.176,-.594,2.13),(s*.142,-.51,2.12)],[.019,.024,.015],skin,'head',10,4)
    ellipsoid('Nostril '+str(s),(s*.111,-.846,1.92),(.006,.032,.014),dark,'head',12,8)

# A thin, rounded, swept crest; orange faces and darker perimeter, not a cone.
outline=[(-.70,2.12),(-.58,2.35),(-.40,2.61),(-.16,2.94),(.10,3.29),(.19,3.38),(.235,3.37),(.23,3.29),(.10,2.94),(-.04,2.57),(-.17,2.27),(-.23,2.05),(-.38,2.08),(-.51,2.13)]
vs=[];fs=[];N=len(outline);cy=-.16;cz=2.55
for s in [-1,1]:
    for shrink,width in [(1,.008),(.94,.036),(.68,.053)]:
        for y,z in outline:vs.append((s*width,cy+(y-cy)*shrink,cz+(z-cz)*shrink))
for side in range(2):
    k=side*3*N
    for r in range(2):
        for i in range(N):
            a=k+r*N+i;b=k+r*N+(i+1)%N;fs.append((a,b,b+N,a+N) if side else (a+N,b+N,b,a))
    fs.append(tuple(k+2*N+i for i in range(N)))
for i in range(N):fs.append((i,(i+1)%N,3*N+(i+1)%N,3*N+i))
crest=mesh('Crest • swept amber display blade',vs,fs,orange,[{'head':1} for v in vs],1)

# Low-profile pycnofibre clumps follow the nape, scapula and chest, not feathers.
for i in range(10):
    y=random.uniform(-.25,.48);x=random.uniform(-.13,.13);z=1.87-.22*(y+.25)
    tube('Nape tuft %02d'%i,[(x,y,z-.06),(x*.96,y+.055,z-.025),(x*.9,y+.14,z-.025)],[.028,.018,.0015],skin,'body',7,2)
for i in range(5):
    x=random.uniform(-.17,.17);y=random.uniform(-.29,-.13);z=1.40+random.uniform(-.035,.05)
    tube('Throat tuft %02d'%i,[(x,y,z+.06),(x,y+.018,z),(x*.95,y+.045,z-.028)],[.027,.023,.001],cream,'body',7,2)

wing_meshes=[]
wing_names=['upper_arm','forearm','hand','wing_1','wing_2','wing_3','wing_4']
def near_weights(p,side):
    distances=[]
    for bn in wing_names:
        name=bn+'.'+side;a,b,_=bone_defs[name];t=max(0,min(1,(p-a).dot(b-a)/(b-a).length_squared));d=(p-(a+(b-a)*t)).length
        distances.append((d,name))
    distances.sort();one,two=distances[:2]; ratio=max(0,min(.5,(.11-(two[0]-one[0]))/.22))
    return {one[1]:1-ratio,two[1]:ratio}

for side,s in [('L',1),('R',-1)]:
    pts=wing_pts[side]
    tube('Wing arm and finger • '+side,pts,[.085,.052,.041,.043,.024,.017,.011,.002],dark,lambda p:near_weights(p,side),12,5)
    ellipsoid('Shoulder muscle '+side,(s*.28,-.19,1.69),(.145,.12,.105),skin,'upper_arm.'+side)
    # Leading/trailing rows share span parameter; camber and soft paint are explicit geometry/data.
    leads=cat(pts,6)
    trails=cat([(s*.20,.61,1.23),(s*.48,.94,1.38),(s*.94,.89,1.67),(s*1.44,1.01,1.69),(s*2.04,1.04,1.53),(s*2.59,1.01,1.31),(s*3.04,.85,1.18),(s*3.28,.71,1.14)],6)
    verts=[];faces=[];weights=[];colors=[];nc=10
    for i,(a,b) in enumerate(zip(leads,trails)):
        u=i/(len(leads)-1)
        for j in range(nc+1):
            t=j/nc;co=a.lerp(b,t);co.z+=sin(t*pi)*.075*sin(pi*u)**.5
            verts.append(co)
            w=near_weights(a,side)
            rootfade=max(0,1-u/.28)*(t**1.5)*.92
            w={k:v*(1-rootfade) for k,v in w.items()};w['body']=rootfade
            weights.append(w)
            edge=(1-min(1,t/.17))*.65+max(0,(t-.9)/.1)*.20
            base=Vector(linear('#D5B884')[:3]); shade=Vector(linear('#84735B')[:3]);c=base.lerp(shade,edge)
            variation=.96+.045*sin(i*.7+j*1.8)+.025*sin(i*.21+j*3)
            colors.append((*[v*variation for v in c],1))
    for i in range(len(leads)-1):
        for j in range(nc):
            a=i*(nc+1)+j;faces.append((a,a+nc+1,a+nc+2,a+1) if s>0 else (a+1,a+nc+2,a+nc+1,a))
    ob=mesh('Wing membrane • '+side,verts,faces,mem,weights)
    attr=ob.data.color_attributes.new(name='Wing paint',type='FLOAT_COLOR',domain='POINT')
    for a,c in zip(attr.data,colors):a.color=c
    solid=ob.modifiers.new('Thin living membrane','SOLIDIFY');solid.thickness=.007
    sub=ob.modifiers.new('Soft membrane contour','SUBSURF');sub.levels=1;sub.render_levels=1
    wing_meshes.append(ob)
    # Three free clawed digits at the hand, kept anatomically separate from digit IV.
    for k in range(3):
        a=Vector((s*(1.37+k*.037),-.235,1.82));b=a+Vector((s*(-.065+k*.025),-.12-k*.018,.055));c=b+Vector((s*.065,-.042,-.015));d=c+Vector((s*.035,.023,-.040))
        tube('Free finger %d.%s'%(k+1,side),[a,b,c],[.025,.018,.010],skin,'hand.'+side,8,3)
        tube('Hand claw %d.%s'%(k+1,side),[c,d],[.013,.001],claw,'hand.'+side,8,3)
    tube('Hind leg '+side,[(s*.15,.41,1.42),(s*.25,.62,1.16),(s*.27,.48,.98)],[.095,.055,.034],skin,lambda p:{'thigh.'+side:1} if p.z>1.15 else {'shin.'+side:1},10,4)
    ellipsoid('Foot pad '+side,(s*.27,.435,.96),(.058,.09,.034),skin,'foot.'+side,16,8)
    for k in range(4):
        x=s*(.215+k*.035)
        tube('Toe %d.%s'%(k+1,side),[(x,.43,.96),(x+s*(k-1.5)*.013,.32,.94),(x+s*(k-1.5)*.016,.28,.93)],[.016,.013,.006],skin,'foot.'+side,7,3)
        tube('Foot claw %d.%s'%(k+1,side),[(x+s*(k-1.5)*.016,.29,.935),(x+s*(k-1.5)*.017,.26,.92)],[.008,.001],claw,'foot.'+side,6,2)

# Tiny tail and cruropatagium: no long dinosaur tail.
tube('Short tail',[(0,.63,1.43),(0,.84,1.39),(0,.93,1.36)],[.07,.035,.002],skin,'body',10,3)

# Reference packed in the file, kept out of the beauty renders.
refpath=Path('C:/Users/neran/Downloads/3d model images new/ANM_Pteranodon.jpg')
if refpath.exists():
    im=bpy.data.images.load(str(refpath));im.pack()
    ref=bpy.data.objects.new('REFERENCE • supplied ANM_Pteranodon',None);ref.empty_display_type='IMAGE';ref.data=im;ref.empty_display_size=4;ref.location=(0,4,2);ref.rotation_euler=(pi/2,0,0);ref.hide_render=True;refcol.objects.link(ref)
    refcol.hide_viewport=True

def studobj(name,data):
    ob=bpy.data.objects.new(name,data);studio.objects.link(ob);return ob

me=bpy.data.meshes.new('Studio ground');me.from_pydata([(-200,-200,0),(200,-200,0),(200,200,0),(-200,200,0)],[],[(0,1,2,3)])
ground=studobj('Ground • render only',me);ground.data.materials.append(floorMat)
def aim(ob,p): ob.rotation_euler=(Vector(p)-ob.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power,size in [('Key',(-3,-4,8),600,5),('Fill',(5,-1,5),250,5),('Rim',(1,5,7),450,4)]:
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=studobj(name,d);o.location=loc;aim(o,(0,0,1.5))
world=bpy.data.worlds.new('Soft grey studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.5,.5,.5,1);world.node_tree.nodes['Background'].inputs[1].default_value=.35;scene.world=world
camera=studobj('CAM • review',bpy.data.cameras.new('Orthographic review'));camera.data.type='ORTHO';scene.camera=camera
camera.location=(4,-7,6.5);aim(camera,(0,-.1,1.65));camera.data.ortho_scale=7.7
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1500;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.fps=24
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene.frame_start=1;scene.frame_end=960
for ob in bpy.context.selected_objects:ob.select_set(False)
body.select_set(True);bpy.context.view_layer.objects.active=body
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_perspective='CAMERA'
        area.spaces.active.shading.type='MATERIAL'
        area.spaces.active.overlay.show_overlays=False
scene['asset_status']='ART REVIEW / animation study — not yet a Unity production export'
scene['reference']='User-supplied ANM_Pteranodon.jpg; unseen surfaces reconstructed. Crest/color follow concept rather than proven fossil colors.'
scene['anatomy']='Single fourth-digit wing spar, three free clawed hand digits, toothless jaw, small hindfeet, no bat finger fan.'
rig['animation_notes']='Biomechanical animation studies; precise Pteranodon motion is reconstructed, not directly observed.'
stats={'blender':bpy.app.version_string,'mesh_objects':len([o for o in geo.objects if o.type=='MESH']),'base_triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in geo.objects if o.type=='MESH'),'wingspan_m':6.56,'bones':len(arm.bones)}
(OUT/'model_stats.json').write_text(json.dumps(stats,indent=2))
print('MODEL_STATS',json.dumps(stats))
file=OUT/'ANM_Pteranodon_review.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(file))
scene.render.filepath=str(OUT/'renders/01_three_quarter.png');bpy.ops.render.render(write_still=True)
