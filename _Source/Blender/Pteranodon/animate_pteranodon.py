"""Create editable, named anatomical motion studies and a marked review timeline."""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector, Matrix, Euler, Quaternion
from math import sin, cos, pi
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'ANM_Pteranodon_review.blend'))
scene=bpy.context.scene;rig=bpy.data.objects['RIG_Pteranodon'];arm=rig.data
geo=bpy.data.collections['01 • Pteranodon geometry']
rest={b.name:(b.head_local.copy(),b.tail_local.copy(),b.matrix_local.copy()) for b in arm.bones}
names=['upper_arm','forearm','hand','wing_1','wing_2','wing_3','wing_4']
def clamp(x):return max(0,min(1,x))
def ease(x):x=clamp(x);return x*x*(3-2*x)
def rot(axis,angle):return Matrix.Rotation(angle,4,axis)
def pivot(p,r):return Matrix.Translation(p)@r@Matrix.Translation(-p)

# Folding correction reduces membrane chord while keeping the inner attachment.
# The skeleton preserves segment length; the membrane gathers as the finger folds.
rig['membrane_fold']=0.0
for ob in geo.objects:
    if not ob.name.startswith('Wing membrane'):continue
    side=ob.name[-1];count=len(ob.data.vertices);cols=11;rows=count//cols
    ob.shape_key_add(name='Basis');key=ob.shape_key_add(name='Gather membrane for folded wing')
    for i in range(rows):
        a=ob.data.vertices[i*cols].co
        for j in range(cols):
            v=ob.data.vertices[i*cols+j].co;u=i/(rows-1);t=j/(cols-1)
            gather=.84*ease(u/.30)
            v2=a+(v-a)*(1-gather)
            v2.z+=sin(t*pi*5)*.022*ease(u/.2)*sin(pi*u)
            key.data[i*cols+j].co=v2
    drv=key.driver_add('value').driver;drv.type='AVERAGE';var=drv.variables.new();var.name='fold';var.type='SINGLE_PROP';var.targets[0].id=rig;var.targets[0].data_path='["membrane_fold"]'

def setmatrix(name,m):
    pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION';pb.matrix=m
    bpy.context.view_layer.update()

def setsegment(name,a,b,parent_transform):
    ra,rb,rm=rest[name];q=(rb-ra).rotation_difference(b-a)
    setmatrix(name,parent_transform@Matrix.Translation(a)@q.to_matrix().to_4x4()@Matrix.Translation(-ra)@rm)

def pose(fold=0,flap=0,lift=.65,pitch=0,bank=0,look=0,nod=0,jaw=0,legs=0,asym=0,tipflex=0):
    R=Matrix.Translation((0,0,lift));B=pivot(rest['body'][0],Euler((pitch,bank,0)).to_matrix().to_4x4())
    setmatrix('root',R@rest['root'][2]);setmatrix('body',R@B@rest['body'][2])
    N=pivot(rest['neck'][0],Euler((nod,0,look)).to_matrix().to_4x4())
    setmatrix('neck',R@B@N@rest['neck'][2]);setmatrix('head',R@B@N@rest['head'][2])
    J=pivot(rest['jaw'][0],rot('X',jaw))
    setmatrix('jaw',R@B@N@J@rest['jaw'][2])
    for side,s in [('L',1),('R',-1)]:
        shoulder=rest['upper_arm.'+side][0];cur=shoulder.copy()
        directions=[Vector((s*.22,.84,-.49)),Vector((s*.28,-.84,-.46)),Vector((s*.05,-.27,-.96)),Vector((s*.055,.52,.85)),Vector((s*.04,.52,.85)),Vector((s*.025,.52,.85)),Vector((s*.015,.52,.85))]
        F=pivot(shoulder,rot('Y',s*(flap+asym*s)))
        planted=None
        if fold>.96 and lift<-.35 and abs(pitch)<.02:
            # Two-link IK holds the hands on the floor while the forelimbs extend.
            hand_end=Vector((s*.55,-.36,.024-lift))
            hand_vec=directions[2].normalized()*(rest['hand.'+side][1]-rest['hand.'+side][0]).length
            wrist=hand_end-hand_vec;delta=wrist-shoulder;distance=delta.length
            la=(rest['upper_arm.'+side][1]-shoulder).length;lb=(rest['forearm.'+side][1]-rest['forearm.'+side][0]).length
            axis=delta.normalized();along=(la*la-lb*lb+distance*distance)/(2*distance)
            perpendicular=Vector((0,1,0));perpendicular=(perpendicular-axis*perpendicular.dot(axis)).normalized()
            elbow=shoulder+axis*along+perpendicular*math.sqrt(max(0,la*la-along*along))
            planted=[elbow,wrist,hand_end]
        for i,name in enumerate(names):
            bn=name+'.'+side;ra,rb,rm=rest[bn];rdir=(rb-ra).normalized();tdir=directions[i].normalized()
            # Spherical interpolation folds the base of the elongated fourth digit.
            q=rdir.rotation_difference(tdir);d=Quaternion().slerp(q,fold)@rdir
            if i>=3:d=rot('Y',s*tipflex).to_3x3()@d
            end=planted[i] if planted and i<3 else cur+d*(rb-ra).length
            setsegment(bn,cur,end,R@B@F);cur=end
        # Legs trail rearwards in flight and extend for the landing contact.
        hip=rest['thigh.'+side][0];cur=hip.copy()
        for i,name in enumerate(['thigh','shin','foot']):
            bn=name+'.'+side;ra,rb,rm=rest[bn];d=(rb-ra).normalized()
            flight=[Vector((s*.20,.88,-.42)),Vector((0,.85,-.53)),Vector((0,.98,-.20))][i].normalized()
            q=d.rotation_difference(flight);d=Quaternion().slerp(q,legs)@d
            end=cur+d*(rb-ra).length;setsegment(bn,cur,end,R@B);cur=end
    rig['membrane_fold']=fold

def key(frame):
    for p in rig.pose.bones:
        p.keyframe_insert('location',frame=frame,group=p.name)
        p.keyframe_insert('rotation_quaternion',frame=frame,group=p.name)
        p.keyframe_insert('scale',frame=frame,group=p.name)
    rig.keyframe_insert('["membrane_fold"]',frame=frame)

def params(kind,t):
    p={'legs':1,'lift':.65}
    if kind=='Soar':p.update(flap=.025*sin(2*pi*t),bank=.025*sin(2*pi*t),pitch=.012*sin(4*pi*t))
    elif kind=='Flap':p.update(flap=.53*sin(4*pi*t),tipflex=.15*cos(4*pi*t),lift=.85+.07*sin(4*pi*t-.6),pitch=.035*sin(4*pi*t))
    elif kind=='Bank':p.update(bank=.30*sin(2*pi*t),flap=.04*sin(4*pi*t),asym=.07*sin(2*pi*t),look=-.12*sin(2*pi*t))
    elif kind=='WindBalance':p.update(bank=.065*sin(4*pi*t),pitch=.05*sin(2*pi*t),flap=.12*sin(6*pi*t),asym=.10*sin(2*pi*t),lift=.75+.07*sin(2*pi*t))
    elif kind=='Land':
        descent=ease(t/.66);fold=ease((t-.66)/.31)
        p.update(lift=.65-1.57*descent,fold=fold,legs=1-ease(t/.53),pitch=.11*sin(pi*min(1,t/.65)),flap=.20*sin(pi*min(1,t/.65))*(1-fold))
    elif kind=='GroundIdle':p.update(lift=-.92,fold=1,legs=0,look=.10*sin(2*pi*t),nod=.025*sin(4*pi*t))
    elif kind=='FoldUnfold':
        f=.5+.5*cos(2*pi*t);p.update(lift=-.92+.08*(1-f),fold=f,legs=0)
    elif kind=='Eat':
        dip=ease(t/.28)*(1-ease((t-.5)/.3));swallow=sin(pi*clamp((t-.58)/.33))
        p.update(lift=-.92,fold=1,legs=0,nod=.40*dip-.25*swallow,jaw=.25*max(0,sin(pi*clamp(t/.60)))+.08*swallow)
    elif kind=='Takeoff':
        push=ease((t-.10)/.18);vault=ease((t-.28)/.32);unfold=ease((t-.30)/.28);air=ease((t-.38)/.34)
        p.update(lift=-.92-.07*sin(pi*clamp(t/.13))+.54*push+1.26*vault,fold=1-unfold,legs=ease((t-.28)/.30),pitch=0,flap=.48*sin(4*pi*clamp((t-.55)/.45))*air)
    return p

clips=[('Soar',96),('Flap',48),('Bank',96),('WindBalance',96),('Land',120),('GroundIdle',96),('FoldUnfold',96),('Eat',120),('Takeoff',120)]
rig.animation_data_create();start=1;manifest=[]
for kind,length in clips:
    rig.animation_data.action=None
    action=bpy.data.actions.new('ANM_Pteranodon_'+kind);action.use_fake_user=True;rig.animation_data.action=action
    # Sample motion densely enough for delayed shoulder/wrist motion and balance changes.
    for frame in sorted(set(list(range(1,length+1,3))+[length])):
        pose(**params(kind,(frame-1)/(length-1)));key(frame)
    rig.animation_data.action=None
    track=rig.animation_data.nla_tracks.new();track.name=kind
    strip=track.strips.new(kind,start,action);strip.action_frame_start=1;strip.action_frame_end=length;strip.extrapolation='NOTHING';strip.blend_type='REPLACE'
    manifest.append({'clip':kind,'start':start,'end':start+length-1,'action':action.name})
    scene.timeline_markers.new(kind,frame=start);start+=length
scene.frame_end=start-1
scene.frame_set(1)
notes=bpy.data.texts.new('READ ME • Pteranodon review')
notes.write('ANM_PTERANODON — ART REVIEW AND MOTION STUDIES\n\nUse the marked timeline to review nine clips. These are reconstructed movement studies, not production-approved animation. WindBalance represents facing a headwind/updraft; it is not unsupported stationary hovering in still air.\n\n'+ '\n'.join('%s: %d–%d'%(x['clip'],x['start'],x['end']) for x in manifest)+'\n\nSelect RIG_Pteranodon for Pose Mode. Named Actions and NLA strips are editable. Membrane fold corrective is driven by rig["membrane_fold"]. Original reference is packed in the file.\n\nRemaining production work: approval of shapes and colors, deformation/contact polish, mesh consolidation/LODs, UV texture bake, Unity export and mobile validation.\n')
(OUT/'animation_manifest.json').write_text(json.dumps(manifest,indent=2))
scene.camera.location=(4,-7,7.1);scene.camera.rotation_euler=(Vector((0,-.1,2.15))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=7.7
scene['animation_status']='9 editable biomechanical studies; contact/deformation polish pending art review'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ANM_Pteranodon_animated_review.blend'))
print('ANIMATION_MANIFEST',json.dumps(manifest))
if '--no-renders' in sys.argv:sys.exit(0)

# Fast visual checks of decisive poses. Multi-view beauty renders are a separate step.
scene.render.resolution_x=1100;scene.render.resolution_y=900;scene.cycles.samples=20
for name,frame,loc,target,scale in [
    ('pose_soar',1,(4,-7,7.1),(0,-.1,2.15),7.7),
    ('pose_folded',480,(5,-7,4.0),(0,-.05,1.05),3.8),
    ('pose_folded_side',480,(7,0,2.4),(0,-.15,1.1),3.8),
    ('pose_downstroke',115,(3,-7,5.5),(0,0,2.1),7.7),
    ('pose_launch',810,(6,-5,4.0),(0,0,1.7),6.5)]:
    scene.frame_set(frame);scene.camera.location=loc;scene.camera.rotation_euler=(Vector(target)-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=scale
    scene.render.filepath=str(OUT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
