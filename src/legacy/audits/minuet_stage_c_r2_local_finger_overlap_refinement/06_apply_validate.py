import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from blender_local import *
from mathutils import Quaternion
policy=read(P/'LOCAL_CORRECTION_POLICY.json');lock=read(P/'LOCAL_CORRECTION_POLICY_LOCK.json')
assert sha(P/'LOCAL_CORRECTION_POLICY.json')==lock['policy_sha256']
assert all(sha(P/n)==s for n,s in lock['scripts'].items())
assert not DEST.exists() and not (P/'CANDIDATE_COMMIT.json').exists(),'ONE_NEW_LOCAL_REFINEMENT_CANDIDATE_ONLY'
man=read(C1/'SCENE_MANIFEST.json');assert sha(man['path'])==lock['source_candidate_sha256']
tl=read(C1/'PERFORMANCE_TIMELINE.json');rois=read(P/'LOCAL_SKIN_ROI_WITH_NEIGHBOR.json')
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
mapping=man['mapping'];rig=bpy.data.objects[mapping['R']['rig']];bone=rig.pose.bones[policy['target_bone']];original=rig.animation_data.action
targetpath='pose.bones["RING_MCP_R"].rotation_quaternion'
fc={f.array_index:f for f in curves(original) if f.data_path==targetpath};assert len(fc)==4
oldpayload=payload(original)
unaffected={name:digest(payload(bpy.data.objects[name].animation_data.action)) for name in [mapping['R']['root'],mapping['L']['root'],mapping['L']['rig']]+list(man['key_pivots'].values())}
def frozen(mesh,rig):
    v=h.core(mesh,rig);v.pop('pose_state');v['armature_object'].pop('animation')
    for b in v['corrective_geometry_and_driver']['blocks']:b['settings'].pop('value',None)
    return digest(v)
settime(sc,0);struct={s:frozen(bpy.data.objects[mapping[s]['mesh']],bpy.data.objects[mapping[s]['rig']]) for s in ['R','L']}
actual_cameras={view:dict(matrix_world=np.array(bpy.data.objects[name].matrix_world).tolist(),ortho_scale=bpy.data.objects[name].data.ortho_scale) for view,name in man['cameras'].items()}
start,end=policy['presentation_support_sec'];a,b=policy['plateau_sec'];amplitude=policy['maximum_delta_deg']
def smoother(u):return u*u*u*(10+u*(-15+6*u))
def correction(t):
    if t<=start or t>=end:return 0.
    if t<a:return amplitude*smoother((t-start)/(a-start))
    if t>b:return amplitude*smoother((end-t)/(end-b))
    return amplitude
sourceframes=sorted({float(k.co.x) for f in fc.values() for k in f.keyframe_points})
alltimes=np.unique(np.round(np.r_[np.arange(357)/60,[(f-1)/60 for f in sourceframes],np.arange(start,end+1e-8,1/240),start,a,b,end,*[[n['note_on'],n['note_on']+.035,(n['note_on']+n['note_off'])/2,n['note_off']-.00001,n['note_off'],n['note_off']+.07] for n in tl['notes']]],9))
alltimes=alltimes[(alltimes>=0)&(alltimes<=5.95)]
baseline={s:{k:[] for k in ['root','basis','V','pads','skin_pads']} for s in ['R','L']};basekeys=[]
for i,t in enumerate(alltimes):
    for s in ['R','L']:
        v=snapshot(sc,mapping[s],s,float(t))
        for k in baseline[s]:baseline[s][k].append(v[k])
    basekeys.append([bpy.data.objects[name].rotation_euler.x for name in man['key_pivots'].values()])
    if i%300==0:print('R1_READONLY_REFERENCE',i,len(alltimes),flush=True)
baseline={s:{k:np.array(v) for k,v in rows.items()} for s,rows in baseline.items()};basekeys=np.array(basekeys)
np.savez_compressed(P/'BASELINE_REFERENCE.npz',times=alltimes,keys=basekeys,**{s+'_'+k:v for s,row in baseline.items() for k,v in row.items()})
# One closed-form local module, not a refit of the global motion. Only one
# MCP quaternion channel group is updated on the copied Action.
new=original.copy();new.name='DESIGN_ONLY_STAGE_C_R2_LOCAL_RING_MCP_SPREAD';slot=rig.animation_data.action_slot.identifier
newfc={f.array_index:f for f in curves(new) if f.data_path==targetpath}
axis=Vector(c.SETUPS['R','RING'][3]);sampleframes=sorted(set(sourceframes)|{1+60*float(t) for t in np.r_[np.arange(start,end+1e-8,1/240),start,a,b,end]})
maximum_delta=0
for frame in sampleframes:
    t=(frame-1)/60
    if t<start-1e-10 or t>end+1e-10:continue
    delta=correction(t);maximum_delta=max(maximum_delta,abs(delta));raw=Quaternion(tuple(fc[i].evaluate(frame) for i in range(4)));value=Quaternion(axis,math.radians(delta))@raw
    if delta==0:value=raw
    for index in range(4):
        curve=newfc[index];existing=next((k for k in curve.keyframe_points if abs(k.co.x-frame)<1e-5),None)
        if existing:existing.co.y=value[index]
        else:existing=curve.keyframe_points.insert(frame,value[index],options={'FAST'})
        existing.interpolation='LINEAR'
for f in newfc.values():f.update()
rig.animation_data.action=new;rig.animation_data.action_slot=next(s for s in new.slots if s.identifier==slot)
newpayload=payload(new)
assert [v for v in oldpayload if v['path']!=targetpath]==[v for v in newpayload if v['path']!=targetpath]
assert all(digest(payload(bpy.data.objects[name].animation_data.action))==s for name,s in unaffected.items())
settime(sc,0);assert all(frozen(bpy.data.objects[mapping[s]['mesh']],bpy.data.objects[mapping[s]['rig']])==struct[s] for s in ['R','L'])
target_index=[b.name for b in rig.pose.bones].index(policy['target_bone'])
other=np.array([j for j in range(len(rig.pose.bones)) if j!=target_index]);camera=bpy.data.objects[man['cameras']['OVERHEAD']]
def validate():
    metrics=dict(left_skin_max_mm=0.,right_outside_skin_max_mm=0.,root_matrix_max=0.,non_target_joint_basis_max=0.,key_angle_max_rad=0.,non_ring_pad_max_mm=0.,inside_ring_pad_max_mm=0.,active_marker_gap_abs_max_mm=0.,active_skin_gap_abs_max_mm=0.,active_horizontal_max_mm=0.)
    relation=[];contacts=[]
    for i,t in enumerate(alltimes):
        poses={s:snapshot(sc,mapping[s],s,float(t)) for s in ['R','L']}
        for s,v in poses.items():
            old=baseline[s];metrics['root_matrix_max']=max(metrics['root_matrix_max'],float(np.max(abs(v['root']-old['root'][i]))))
            cols=other if s=='R' else np.arange(len(v['basis']));metrics['non_target_joint_basis_max']=max(metrics['non_target_joint_basis_max'],float(np.max(abs(v['basis'][cols]-old['basis'][i,cols]))))
            if s=='L':metrics['left_skin_max_mm']=max(metrics['left_skin_max_mm'],float(np.max(np.linalg.norm(v['V']-old['V'][i],axis=1))*1000))
            elif t<start-1e-8 or t>end+1e-8:metrics['right_outside_skin_max_mm']=max(metrics['right_outside_skin_max_mm'],float(np.max(np.linalg.norm(v['V']-old['V'][i],axis=1))*1000))
            if s=='R':
                metrics['non_ring_pad_max_mm']=max(metrics['non_ring_pad_max_mm'],float(np.max(np.linalg.norm(v['pads'][[0,1,2,4]]-old['pads'][i,[0,1,2,4]],axis=1))*1000))
                metrics['inside_ring_pad_max_mm']=max(metrics['inside_ring_pad_max_mm'],float(np.linalg.norm(v['pads'][3]-old['pads'][i,3])*1000))
        currentkeys=np.array([bpy.data.objects[name].rotation_euler.x for name in man['key_pivots'].values()]);metrics['key_angle_max_rad']=max(metrics['key_angle_max_rad'],float(np.max(abs(currentkeys-basekeys[i]))))
        if start<=t<=end:
            rel=local_relation(poses['R']['V'],rois,camera);neighbor=local_relation(poses['R']['V'],{'MIDDLE':rois['RING'],'RING':rois['LITTLE']},camera)
            relation.append(dict(presentation_sec=float(t),music_sec=float(t-.35),correction_deg=correction(t),**rel,ring_little_patch_pairs=neighbor['intersecting_patch_triangle_pairs']))
        for n in tl['notes']:
            if n['note_on']-1e-9<=t<n['note_off']-1e-9:
                s=n['hand'];j=n['finger']-1;v=poses[s];angle=bpy.data.objects[man['key_pivots'][str(n['key_index'])]].rotation_euler.x;k=c.KEYS[n['key_index']]
                marker=contact(v['pads'][j],k,angle);skin=contact(v['skin_pads'][j],k,angle);before=contact(baseline[s]['skin_pads'][i,j],k,angle)
                metrics['active_marker_gap_abs_max_mm']=max(metrics['active_marker_gap_abs_max_mm'],abs(marker['gap_mm']));metrics['active_skin_gap_abs_max_mm']=max(metrics['active_skin_gap_abs_max_mm'],abs(skin['gap_mm']));metrics['active_horizontal_max_mm']=max(metrics['active_horizontal_max_mm'],marker['horizontal_mm'],skin['horizontal_mm'])
                contacts.append(dict(note_id=n['note_id'],hand=s,finger=j+1,presentation_sec=float(t),marker=marker,skin=skin,source_skin=before))
        if i%300==0:print('LOCAL_CANDIDATE_VALIDATION',i,len(alltimes),flush=True)
    bad=[r for r in relation if r['intersecting_patch_triangle_pairs'] or r['ring_little_patch_pairs']]
    dump('IN_MEMORY_VALIDATION.json',dict(metrics=metrics,relation=relation,contacts=contacts,local_bad_samples=bad,sole_bone='RING_MCP_R',motion_solver_calls=0,actual_keyframe_values_outside_scope_unmodified=True,samples=len(alltimes)))
    assert metrics['left_skin_max_mm']<.001 and metrics['right_outside_skin_max_mm']<.001 and metrics['root_matrix_max']==0 and metrics['non_target_joint_basis_max']==0 and metrics['key_angle_max_rad']==0 and metrics['non_ring_pad_max_mm']<.001,('NON_TARGET_PRESERVATION_FAILED',metrics)
    assert metrics['active_marker_gap_abs_max_mm']<=3 and metrics['active_skin_gap_abs_max_mm']<=3 and metrics['active_horizontal_max_mm']<.03,('ACTIVE_CONTACT_FAILED',metrics)
    assert not bad,('LOCAL_PATCH_INTERSECTION_REMAINS',[(r['presentation_sec'],r['correction_deg'],r['intersecting_patch_triangle_pairs']) for r in bad[:12]])
    return dict(pass_=True,metrics=metrics,local_bad_samples=0,samples=len(alltimes),contact_samples=len(contacts),all23_note_ids=sorted(set(c['note_id'] for c in contacts)),maximum_delta_deg=maximum_delta)
validation=validate()
# Read-only local pose previews of the single locked trajectory. Stop before
# the sole candidate save if a product precommit review has not been recorded.
if not (P/'ANIMATED_PRECOMMIT_VISUAL_REVIEW.json').exists():
    for t in [.78,.90,1.05,1.40,1.55,1.80,1.94,2.10]:
        settime(sc,t)
        for view,name in man['cameras'].items():
            sc.camera=bpy.data.objects[name];folder=P/'locked_preview';folder.mkdir(exist_ok=True);sc.render.filepath=str(folder/f'{view}_{round(t*60):04d}.png');bpy.ops.render.render(write_still=True)
    dump('PRECOMMIT_GATE.json',dict(pass_=True,candidate_saved=False,locked_policy_sha256=lock['policy_sha256'],validation=validation,only_one_locked_trajectory=True))
    print('LOCKED_TRAJECTORY_PRECOMMIT_READY_NO_SAVED_CANDIDATE',flush=True);raise SystemExit(0)
assert read(P/'ANIMATED_PRECOMMIT_VISUAL_REVIEW.json')['pass_']
sc.name='STAGE_C_R2_LOCAL_FINGER_OVERLAP_DESIGN_ONLY';sc['DESIGN_ONLY']=True;sc['HUMAN_APPROVAL_PENDING']=True;sc['LOCAL_REFINEMENT_POLICY_SHA256']=lock['policy_sha256'];sc['SOURCE_C1_SHA256']=man['sha256'];sc['MOTION_SOLVER_CALLS']=0
sc.camera=bpy.data.objects[man['cameras']['TEACHING']];settime(sc,0)
dump('CANDIDATE_COMMIT.json',dict(count=1,state='SOLE_LOCKED_LOCAL_CANDIDATE_SAVE_STARTED',policy_sha256=lock['policy_sha256']))
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
newman=dict(man,path=str(DEST),sha256=sha(DEST),scene=sc.name,source_C1_sha256=man['sha256'],actual_camera_parameters=actual_cameras,local_action=new.name,local_policy_sha256=lock['policy_sha256'],candidate_count=1)
dump('SCENE_MANIFEST.json',newman)
bpy.ops.wm.open_mainfile(filepath=str(DEST),load_ui=False,use_scripts=False);sc=bpy.data.scenes[newman['scene']];bpy.context.window.scene=sc;camera=bpy.data.objects[newman['cameras']['OVERHEAD']]
post=validate();dump('SAVED_CANDIDATE_VALIDATION.json',dict(pass_=True,before_save=validation,after_reopen=post,source_protection_pending_final_hash_check=True))
dump('CANDIDATE_COMMIT.json',dict(count=1,state='SOLE_LOCKED_LOCAL_CANDIDATE_SAVED_REOPENED_VERIFIED',sha256=newman['sha256'],policy_sha256=lock['policy_sha256'],motion_solver_calls=0))
print('ONE_LOCAL_CANDIDATE_SAVED_REOPENED_VERIFIED',flush=True)
