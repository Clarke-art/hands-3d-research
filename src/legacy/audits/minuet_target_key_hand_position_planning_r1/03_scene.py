import bpy,sys,ast,importlib.util,math,re
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
from stage_common import *
from mathutils import Matrix,Vector
spec=importlib.util.spec_from_file_location('identity',ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
for file,names in [(ROOT/'audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/04_hands.py',['intrinsic']),
                   (ROOT/'audits/piano_hand_static_to_dynamic_transition_r1/02_scene_verify.py',['rename_normalize','structural','linear'])]:
    tree=ast.parse(file.read_text(encoding='utf8'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(file),'exec'))
sm=read(o.STATIC/'STATIC_SCENE_MANIFEST_R2.json');source=o.STATIC/'STATIC_POSTURE_REFINED_CANDIDATE_R2.blend'
assert sha(source)==sm['candidate_sha256']
dest=P/'STAGE_A_RIGHT_TARGET_KEY_DESIGN_PROVISIONAL_R1.blend';assert not dest.exists()
lock=read(P/'PLANNING_LOCK.json');assert all(sha(P/n)==v for n,v in lock['scripts'].items())
A=np.load(P/'motion.npz');tl=read(P/'PERFORMANCE_TIMELINE.json')
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
static={}
for label,info in sm['mapping'].items():
    bpy.context.window.scene=bpy.data.scenes[info['scene']];bpy.context.view_layer.update()
    static[label]=digest(h.core(bpy.data.objects[info['mesh']],bpy.data.objects[info['rig']]))
info=sm['mapping']['R1'];src=bpy.data.scenes[info['scene']];bpy.context.window.scene=src
for ob in src.objects:ob['STAGE_A_COPY_TOKEN']=ob.name
bpy.ops.scene.new(type='FULL_COPY');sc=bpy.context.scene
copied={ob['STAGE_A_COPY_TOKEN']:ob for ob in sc.objects if 'STAGE_A_COPY_TOKEN' in ob}
for ob in list(src.objects)+list(sc.objects):
    if 'STAGE_A_COPY_TOKEN' in ob:del ob['STAGE_A_COPY_TOKEN']
sc.name='STAGE_A_RIGHT_ONLY_DESIGN_PROVISIONAL_R1'
mapping={k:copied[info[k]].name for k in ['root','rig','mesh']}
rig=bpy.data.objects[mapping['rig']];rt=bpy.data.objects[mapping['root']];mesh=bpy.data.objects[mapping['mesh']]
structure=structural(mesh,rig);base=rt.matrix_world.copy();rig.animation_data_clear();rt.animation_data_clear();rt.rotation_mode='QUATERNION'
for i,t in enumerate(A['times']):
    f=1+t*60;rt.matrix_world=Matrix.Translation(Vector(A['R_delta'][i]))@base
    for prop in ['location','rotation_quaternion']:rt.keyframe_insert(data_path=prop,frame=f)
    for j,d in enumerate(c.DIGITS):
        for name,rot in zip(c.SETUPS['R',d][0],c.joint_mats('R',d,A['R_q'][i,j])):
            b=rig.pose.bones[name];b.rotation_mode='QUATERNION';quat=Matrix(rot).to_quaternion()
            if i and b.rotation_quaternion.dot(quat)<0:quat.negate()
            b.rotation_quaternion=quat;b.keyframe_insert(data_path='rotation_quaternion',frame=f,group=d)
rig.animation_data.action.name='DESIGN_PROVISIONAL_STAGE_A_RIGHT_JOINTS'
rt.animation_data.action.name='DESIGN_PROVISIONAL_STAGE_A_RIGHT_ROOT';linear(rig);linear(rt)
keygeometry={};pivotmap={}
for k in c.KEYS:
    obs=[v for v in sc.objects if v.type=='MESH' and v.get('FROZEN_KEY_INDEX')==k['key_index']]
    assert len(obs)==len(k['geometry'])
    keygeometry[str(k['key_index'])]=digest([{'v':[list(v.co) for v in ob.data.vertices],'p':[list(p.vertices) for p in ob.data.polygons]} for ob in sorted(obs,key=lambda x:x.name)])
    for ob in obs:ob.color=(.86,.85,.80,1) if k['color']=='WHITE' else (.025,.028,.032,1)
    if not any(n['key_index']==k['key_index'] for n in tl['notes']):continue
    pivot=bpy.data.objects.new('STAGE_A_KEY_'+str(k['midi_note']),None);sc.collection.objects.link(pivot);pivot.location=k['press_pivot']
    for ob in obs:
        world=ob.matrix_world.copy();ob.parent=pivot;ob.matrix_parent_inverse=Matrix.Identity(4)
        ob.matrix_basis=Matrix.Translation(-Vector(k['press_pivot']))@world
    for i,t in enumerate(A['times']):
        pivot.rotation_euler.x=float(A['key_angles'][i,k['key_index']]);pivot.keyframe_insert(data_path='rotation_euler',index=0,frame=1+t*60)
    linear(pivot);pivotmap[str(k['key_index'])]=pivot.name
x=float(np.mean([c.KEYS[n['key_index']]['key_center'][0] for n in tl['notes']]))
cameras={}
for view,eye,target,scale in [('TEACHING',(x,-.53,.58),(x,.014,.014),.47),
    ('SIDE_OBLIQUE',(x+.07,-.53,.24),(x,.025,.004),.47),('OVERHEAD',(x,.008,.82),(x,.008,0),.47)]:
    data=bpy.data.cameras.new('STAGE_A_'+view);data.type='ORTHO';data.ortho_scale=scale;data.clip_start=.001;data.clip_end=10
    ob=bpy.data.objects.new('STAGE_A_'+view,data);sc.collection.objects.link(ob);ob.location=eye
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();cameras[view]=ob.name
sc['DESIGN_PROVISIONAL']=True;sc['HUMAN_APPROVAL_PENDING']=True;sc['RIGHT_ONLY_TECHNICAL_VALIDATION']=True
sc.render.fps=60;sc.frame_start=1;sc.frame_end=math.ceil(tl['presentation_duration_sec']*60)
sc.camera=bpy.data.objects[cameras['TEACHING']];sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100
sc.frame_set(1);bpy.context.preferences.filepaths.save_version=0
for label,info in sm['mapping'].items():
    bpy.context.window.scene=bpy.data.scenes[info['scene']];bpy.context.view_layer.update()
    assert digest(h.core(bpy.data.objects[info['mesh']],bpy.data.objects[info['rig']]))==static[label]
bpy.context.window.scene=sc;bpy.ops.wm.save_as_mainfile(filepath=str(dest))
bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False)
for label,info in sm['mapping'].items():
    bpy.context.window.scene=bpy.data.scenes[info['scene']];bpy.context.view_layer.update()
    assert digest(h.core(bpy.data.objects[info['mesh']],bpy.data.objects[info['rig']]))==static[label]
sc=bpy.data.scenes['STAGE_A_RIGHT_ONLY_DESIGN_PROVISIONAL_R1'];bpy.context.window.scene=sc
assert structural(bpy.data.objects[mapping['mesh']],bpy.data.objects[mapping['rig']])==structure
arrays={'times':A['times']};Vs=[];pads=[];skinpads=[];keyangles=[];fkerr=0;keyerr=0
for i,t in enumerate(A['times']):
    f=1+t*60;nf=math.floor(f+1e-8);sc.frame_set(nf,subframe=max(0,f-nf));bpy.context.view_layer.update()
    rr=bpy.data.objects[mapping['rig']];ob=bpy.data.objects[mapping['mesh']];V,_=h.coords(ob)
    pp=np.array([list(<REDACTED_EMAIL>[r['distal_frame']].matrix@Vector(r['local_pad_point'])) for r in c.MARKERS['R']])
    fkerr=max(fkerr,float(np.max(np.linalg.norm(pp-(o.worldpads('R',A['R_q'][i])+A['R_delta'][i]),axis=1))*1000))
    Vs.append(V);pads.append(pp);skinpads.append(V[[r['mesh_vertex'] for r in c.MARKERS['R']]])
    aa=np.zeros(88)
    for ki,name in pivotmap.items():
        pv=bpy.data.objects[name];aa[int(ki)]=pv.rotation_euler.x;k=c.KEYS[int(ki)]
        for g in k['geometry']:
            obj=next(v for v in pv.children if g['name'] in v.name)
            actual=np.array([list(<REDACTED_EMAIL>) for v in obj.data.vertices])
            expected=o.keytransform(k['midi_note'],g['vertices'],aa[int(ki)])
            keyerr=max(keyerr,float(np.max(np.linalg.norm(actual-expected,axis=1))*1000))
    keyangles.append(aa)
assert fkerr<.03 and keyerr<.03,('BAKE_PARITY_FAILED',fkerr,keyerr)
for k in c.KEYS:
    obs=[v for v in sc.objects if v.type=='MESH' and v.get('FROZEN_KEY_INDEX')==k['key_index']]
    assert keygeometry[str(k['key_index'])]==digest([{'v':[list(v.co) for v in ob.data.vertices],'p':[list(p.vertices) for p in ob.data.polygons]} for ob in sorted(obs,key=lambda x:x.name)])
np.savez_compressed(P/'evaluated.npz',times=A['times'],R_verts=Vs,R_pads=pads,R_skin_pads=skinpads,key_angles=keyangles)
dump('SCENE_MANIFEST.json',dict(path=str(dest),sha256=sha(dest),scene=sc.name,mapping=mapping,cameras=cameras,
    key_pivots=pivotmap,static_four_core_sha256=static,four_static_scenes_unchanged=True,
    hand_structure_unchanged=True,all_88_key_geometry_unchanged=True,left_in_performance_scene=False,
    candidate_count=1,save_reopen_verified=True,actual_pad_vs_FK_max_mm=fkerr,
    actual_key_world_parity_max_mm=keyerr,key_angle_parity_max_rad=float(np.max(abs(np.array(keyangles)-A['key_angles']))),
    frames=sc.frame_end,render_engine=sc.render.engine))
print('ONE_RIGHT_ONLY_SCENE_READBACK',fkerr,keyerr,flush=True)
