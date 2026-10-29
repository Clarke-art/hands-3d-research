import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from blender_common import *
pre=read(P/'READONLY_PREFLIGHT.json');B=read(P/'SOURCE_BINDINGS.json');tl=read(P/'PERFORMANCE_TIMELINE.json');payloads=read(P/'APPROVED_ACTION_PAYLOADS.json')
assert pre['pass_'] and read(P/'AUDIO_INTEGRATION.json')['pass_']
assert not DEST.exists() and not (P/'CANDIDATE_COMMIT.json').exists()
for b in B.values():assert sha(b['manifest']['path'])==b['manifest']['sha256']
# Work only in memory. Never save to, or modify the on-disk source Blends.
rm=B['R']['manifest'];lm=B['L']['manifest']
bpy.ops.wm.open_mainfile(filepath=rm['path'],load_ui=False,use_scripts=False)
sc=bpy.data.scenes[rm['scene']];bpy.context.window.scene=sc
sc.name='STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_DESIGN_ONLY'
mapping={'R':rm['mapping'].copy()};pivotmap=rm['key_pivots'].copy()
need=tuple(lm['mapping'].values())+tuple(lm['key_pivots'].values())
with bpy.data.libraries.load(lm['path'],link=False) as (a,b):b.objects=list(need)
loaded=dict(zip(need,b.objects))
assert all(loaded.values())
for ob in loaded.values():sc.collection.objects.link(ob)
mapping['L']={k:loaded[n].name for k,n in lm['mapping'].items()}
leftpivots={ki:loaded[n] for ki,n in lm['key_pivots'].items()}
lr=bpy.data.objects[mapping['L']['rig']];lmsh=bpy.data.objects[mapping['L']['mesh']]
assert next(m for m in lmsh.modifiers if m.type=='ARMATURE').object==lr
assert lr.parent==bpy.data.objects[mapping['L']['root']] and lmsh.parent==lr
for f in lmsh.data.shape_keys.animation_data.drivers:
    for variable in f.driver.variables:
        for target in variable.targets:
            if target.id:assert target.id==lr,('LEFT_CORRECTIVE_DRIVER_TARGET_MISMATCH',target.id.name)
actions={}
def copied_action(ob,side,label):
    ad=ob.animation_data;old=ad.action;slot=ad.action_slot.identifier
    assert digest(action_payload(old))==pre['hands'][side]['actions'][label]['payload_sha256']
    new=old.copy();new.name='DESIGN_ONLY_STAGE_C_'+side+'_'+label
    shift=B[side]['shift_frames']
    for f in curves(new):
        for k in f.keyframe_points:
            k.co.x+=shift;k.handle_left.x+=shift;k.handle_right.x+=shift
    ad.action=new;ad.action_slot=next(s for s in new.slots if s.identifier==slot)
    time_roundoff=0.
    for source_curve,copy_curve in zip(curves(old),curves(new)):
        assert source_curve.data_path==copy_curve.data_path and source_curve.array_index==copy_curve.array_index and source_curve.extrapolation==copy_curve.extrapolation
        assert len(source_curve.keyframe_points)==len(copy_curve.keyframe_points)
        for a,z in zip(source_curve.keyframe_points,copy_curve.keyframe_points):
            assert a.co.y==z.co.y and a.interpolation==z.interpolation=='LINEAR' and a.easing==z.easing
            for field in ['co','handle_left','handle_right']:
                av,zv=getattr(a,field),getattr(z,field)
                time_roundoff=max(time_roundoff,abs(zv.x-av.x-shift))
                assert av.y==zv.y
    assert time_roundoff<=.00005,('ACTION_TIME_ORIGIN_FLOAT32_ROUNDOFF',time_roundoff)
    actions[side+'_'+label]=dict(object=ob.name,action=new.name,slot=slot,source_action=old.name,source_payload_sha256=digest(payloads[side+'_'+label]),time_origin_shift_frames=shift,time_float32_roundoff_frames=time_roundoff,scale=1,all_keyframe_values_and_interpolation_exactly_unchanged=True)
for side in ['R','L']:
    for k in ['root','rig']:copied_action(bpy.data.objects[mapping[side][k]],side,k)
    pm=rm['key_pivots'] if side=='R' else {ki:ob.name for ki,ob in leftpivots.items()}
    for ki,name in pm.items():copied_action(bpy.data.objects[name],side,ki)
settime(sc,0);keyobs=keys(sc)
for ki,pv in leftpivots.items():
    assert ki not in pivotmap
    for ob in keyobs[int(ki)]:
        world=ob.matrix_world.copy();ob.parent=pv;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=pv.matrix_world.inverted()@world
    pivotmap[ki]=pv.name
assert all([digest(geometry(ob)) for ob in keyobs[ki]]==pre['hands']['R']['keyboard_geometry_sha256'][str(ki)] for ki in range(88))
assert len(pivotmap)==13
# There is only one mesh set per frozen key; each animated key has exactly one
# pivot and one Action owner. Append no keyboard from the left source.
assert sum(len(obs) for obs in keyobs.values())==sum(len(k['geometry']) for k in c.KEYS)
assert len([ob for ob in sc.objects if ob.type=='ARMATURE'])==2
sc.render.fps=60;sc.render.fps_base=1;sc.frame_start=1;sc.frame_end=357
sc['DESIGN_ONLY']=True;sc['HUMAN_APPROVAL_PENDING']=True;sc['PHASE']='MINUET_STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_PERFORMANCE';sc['NEW_MOTION_SOLVER_CALLS']=0
sc['MUSIC_TIME']='T_MUSIC=(frame-1)/60-0.35';sc['SOURCE_RIGHT_SHA256']=rm['sha256'];sc['SOURCE_LEFT_SHA256']=lm['sha256']
if sc.sequence_editor:
    assert len(sc.sequence_editor.strips)==0
seq=sc.sequence_editor_create();sound=seq.strips.new_sound('ONE_SHARED_23_NOTE_GRAND',str(P/'piano_performance.wav'),channel=1,frame_start=1)
sound.volume=1.;sound.sound.pack()
# Fit all actual approved hand motion and the required keyboard region in each
# camera analytically before saving the sole candidate. No hand is repositioned.
refs={s:dict(np.load(P/(s+'_approved_reference.npz'))) for s in ['R','L']}
bounds=[]
for A in refs.values():
    v=A['verts'];lo=v.min(axis=(0,1));hi=v.max(axis=(0,1));bounds.extend([[x,y,z] for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]])
for ki in pivotmap:
    for ob in keyobs[int(ki)]:bounds.extend([list(<REDACTED_EMAIL>) for v in ob.data.vertices])
points=np.array(bounds);center=(points.min(axis=0)+points.max(axis=0))/2;x=float(center[0]);target=Vector((x,float(center[1]),.012))
cameras={};camparams={}
for view,eye in [('TEACHING',(x,-.65,.67)),('OVERHEAD',(x,float(center[1]),.9)),('SIDE_OBLIQUE',(x+.12,-.65,.29))]:
    data=bpy.data.cameras.new('STAGE_C_'+view);data.type='ORTHO';data.clip_start=.001;data.clip_end=10
    ob=bpy.data.objects.new('STAGE_C_'+view,data);sc.collection.objects.link(ob);ob.location=eye;ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
    local=(points-np.array(ob.location))@np.array(ob.rotation_euler.to_matrix())
    mid=(local.min(axis=0)+local.max(axis=0))/2
    ob.location+=ob.rotation_euler.to_matrix()@Vector((float(mid[0]),float(mid[1]),0))
    span=local.max(axis=0)-local.min(axis=0);data.ortho_scale=float(max(span[0],span[1]*16/9)*1.12)
    cameras[view]=ob.name;camparams[view]=dict(matrix_world=[list(v) for v in ob.matrix_world],ortho_scale=data.ortho_scale,all_motion_and_target_keys_framing_margin=0.12)
sc.camera=bpy.data.objects[cameras['TEACHING']];sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.render.use_persistent_data=True
def preservation():
    result={}
    for side in ['R','L']:
        A=refs[side];err={k:0. for k in ['root','rig_world','joint_basis','joint_rotation_deg','verts_mm','pads_mm','skin_pads_mm','key_angles_rad']}
        settime(sc,0)
        assert hand_structure(bpy.data.objects[mapping[side]['mesh']],bpy.data.objects[mapping[side]['rig']])==pre['hands'][side]['structure_sha256']
        for i,tm in enumerate(A['music_times']):
            v=pose(sc,mapping[side],side,float(tm+LEAD))
            for k in ['root','rig_world','joint_basis']:err[k]=max(err[k],float(np.max(abs(v[k]-A[k][i]))))
            # Actual basis matrices and quaternions, not Euler proxies.
            qa=v['joint_quat'];qb=A['joint_quat'][i];dot=np.abs(np.sum(qa*qb,axis=1)/(np.linalg.norm(qa,axis=1)*np.linalg.norm(qb,axis=1)))
            err['joint_rotation_deg']=max(err['joint_rotation_deg'],float(np.max(np.degrees(2*np.arccos(np.clip(dot,0,1))))))
            for k in ['verts','pads','skin_pads']:err[k+'_mm']=max(err[k+'_mm'],float(np.max(np.linalg.norm(v[k]-A[k][i],axis=1))*1000))
            for ki in B[side]['manifest']['key_pivots']:
                err['key_angles_rad']=max(err['key_angles_rad'],abs(bpy.data.objects[pivotmap[ki]].rotation_euler.x-A['key_angles'][i,int(ki)]))
            if i%250==0:print('APPROVED_MOTION_PARITY',side,i,len(A['music_times']),flush=True)
        assert max(err[k] for k in ['verts_mm','pads_mm','skin_pads_mm'])<.03 and err['joint_basis']<1e-5 and err['joint_rotation_deg']<.01 and err['root']<1e-5 and err['key_angles_rad']<1e-5,('MOTION_PRESERVATION_FAILED',side,err)
        result[side]=dict(samples=len(A['music_times']),max_errors=err,action_curves_preserved_up_to_origin_shift=True,unchanged_mesh_rig_weights_corrective_driver_structure=True)
    return result
parity=preservation()
# Normal visible spatial overlap bound only, no forensic vertex collision pass.
separation=[];contacts=[];combined=[]
for i in range(357):
    tm=i/60-LEAD;rp=pose(sc,mapping['R'],'R',i/60);lp=pose(sc,mapping['L'],'L',i/60)
    separation.append(float((rp['verts'][:,0].min()-lp['verts'][:,0].max())*1000))
    combined.append((tm,rp['pads'],lp['pads']))
for n in tl['notes']:
    for tm in [n['source_on_sec'],n['source_on_sec']+.035,(n['source_on_sec']+n['source_off_sec'])/2,n['source_off_sec']-.00001,n['source_off_sec']+.07]:
        v=pose(sc,mapping[n['hand']],n['hand'],tm+LEAD);ki=n['key_index'];pv=bpy.data.objects[pivotmap[str(ki)]];k=c.KEYS[ki]
        for label,pt in [('pad',v['pads'][n['finger']-1]),('skin',v['skin_pads'][n['finger']-1])]:
            inv=np.array(pv.matrix_world.inverted()@Vector(pt))+np.array(k['press_pivot']);sur=k['key_top_playable_surface'];dist=[np.linalg.norm(inv[:2]-np.clip(inv[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']])) for s in sur];j=int(np.argmin(dist))
            contacts.append(dict(note_id=n['note_id'],music_time=tm,type=label,gap_mm=float((inv[2]-sur[j]['z'])*1000),horizontal_mm=float(dist[j]*1000),angle_rad=pv.rotation_euler.x))
dump('MOTION_PARITY_PRESAVE.json',dict(pass_=True,hands=parity))
overlap_frames=[i for i,gap in enumerate(separation) if gap<=0]
dump('SPATIAL_ENVELOPE_PRECHECK.json',dict(minimum_x_envelope_gap_mm=min(separation),minimum_gap_frame=1+int(np.argmin(separation)),overlap_frames_1based=[i+1 for i in overlap_frames],meaning='Whole-hand axis envelope overlap is a conservative screen, not a surface collision finding. Inspect normal product views before committing candidate.'))
if not (P/'VISUAL_PREFLIGHT.json').exists():
    preview_frames=sorted(set([round(.39*60)+1,round(4.7*60)+1,round(5.08*60)+1,1+int(np.argmin(separation))]))
    for frame in preview_frames:
        sc.frame_set(frame)
        for view,name in cameras.items():
            folder=P/'_previews';folder.mkdir(exist_ok=True);sc.camera=bpy.data.objects[name];sc.render.filepath=str(folder/f'{view}_{frame:04d}.png');bpy.ops.render.render(write_still=True)
    dump('VISUAL_PREFLIGHT_REQUIRED.json',dict(candidate_saved=False,preview_frames=preview_frames,cameras=cameras,minimum_x_envelope_gap_mm=min(separation),motion_parity=parity))
    print('STOP_BEFORE_SAVE_PRODUCT_SPATIAL_PREVIEW_READY',flush=True)
    raise SystemExit(0)
assert read(P/'VISUAL_PREFLIGHT.json')['pass_'] and read(P/'VISUAL_PREFLIGHT.json')['source_sha256']=={s:B[s]['manifest']['sha256'] for s in B}
# Four approved static scenes inside the source remain unchanged as well.
sm=read(ROOT/'audits/piano_hand_static_posture_clearance_refinement_r2/STATIC_SCENE_MANIFEST_R2.json')
for label,info in sm['mapping'].items():
    bpy.context.window.scene=bpy.data.scenes[info['scene']];bpy.context.view_layer.update()
    assert digest(h.core(bpy.data.objects[info['mesh']],bpy.data.objects[info['rig']]))==rm['static_four_core_sha256'][label]
bpy.context.window.scene=sc;settime(sc,0)
dump('IN_MEMORY_INTEGRATION_GATE.json',dict(pass_=True,parity=parity,candidate_count_before_save=0,minimum_cross_hand_x_separation_mm=min(separation),coordinate_transform='IDENTITY',single_keyboard=True,single_key_ownership=True,actions=actions))
dump('CANDIDATE_COMMIT.json',dict(candidate_count=1,state='SOLE_CANDIDATE_SAVE_STARTED',NEW_MOTION_SOLVER_CALLS=0))
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
man=dict(path=str(DEST),sha256=sha(DEST),scene=sc.name,mapping=mapping,key_pivots=pivotmap,actions=actions,cameras=cameras,camera_parameters=camparams,frames=357,fps=60,lead_sec=LEAD,render_engine=sc.render.engine,source_sha256={s:B[s]['manifest']['sha256'] for s in B})
dump('SCENE_MANIFEST.json',man)
bpy.ops.wm.open_mainfile(filepath=str(DEST),load_ui=False,use_scripts=False);sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
reopened=preservation()
assert len(sc.sequence_editor.strips)==1 and sc.sequence_editor.strips[0].frame_start==1
dump('APPROVED_MOTION_PARITY.json',dict(pass_=True,before_save=parity,after_reopen=reopened,root_translation_threshold_mm=.03,joint_rotation_threshold_deg=.01,actual_skin_threshold_mm=.03,limitation='Trajectory/skin preservation comparison; no exhaustive collision qualification.'))
dump('JOINT_SCENE_FUNCTIONAL.json',dict(pass_=True,unique_note_count=23,unique_key_action_owners=len(pivotmap),single_keyboard_mesh_count=sum(len(v) for v in keys(sc).values()),two_armatures=True,minimum_cross_hand_x_separation_mm=min(separation),new_hand_coordinate_transform='IDENTITY',single_audio_strip=True,contacts=contacts,source_chord_and_repeated_key_curves_identical=True,original_static_four_scenes_unchanged=True))
dump('CANDIDATE_COMMIT.json',dict(candidate_count=1,state='SOLE_CANDIDATE_SAVED_REOPENED_AND_VERIFIED',sha256=man['sha256'],NEW_MOTION_SOLVER_CALLS=0))
print('ONE_DUAL_HAND_CANDIDATE_SAVED_REOPENED_VERIFIED',man['sha256'],flush=True)
