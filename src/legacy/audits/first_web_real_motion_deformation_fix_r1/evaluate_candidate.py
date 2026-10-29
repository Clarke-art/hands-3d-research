import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
tag=sys.argv[sys.argv.index('--tag')+1] if '--tag' in sys.argv else 'WEIGHT_1'
path=CANDIDATE if tag=='FINAL' else OUT/f'RIGHT_HAND_REAL_MOTION_WEIGHT_ITERATION_{tag[-1]}_DESIGN_ONLY.blend'
assert path.exists()
inputs=check_inputs()
ob,rig=load(SOURCE);native=m.product_payload(ob,rig);oldshape=core.shape_payload(ob);source_actions=actions()
Vzero_before=Varray(ob)
fullcams={};affected=read(FIX/'CORRECTIVE_KEY_R1.json')['changed_vertex_ids']
directions={'PALMAR_MOTION':[-.38183954,-.92405248,.0180442],'OBLIQUE_MOTION':[.19980031,-.93906146,.27972043]}
def ensure_dir(n):(OUT/n).mkdir(exist_ok=True)
if not (OUT/'REAL_MOTION_MATCHED_CAMERAS_R1.json').exists():
    for f in range(1,211):
        motion(rig,f);V=Varray(ob)
        center=V[affected].mean(axis=0)
        wrist=np.array(list(<REDACTED_EMAIL>['WRIST_R'].head));down=wrist-center;down/=np.linalg.norm(down)
        fullcams[str(f)]={'PALMAR_MOTION':{'center':list(center+down*.014),'direction':directions['PALMAR_MOTION'],'ortho_scale_m':.11,'resolution':[640,640]},
            'OBLIQUE_MOTION':{'center':list(center),'direction':directions['OBLIQUE_MOTION'],'ortho_scale_m':.100,'resolution':[640,640]}}
    dump('REAL_MOTION_MATCHED_CAMERAS_R1.json',{'cameras':fullcams,'authority':'Centers computed only from BEFORE source motion; AFTER uses exact same per-frame cameras. No candidate-dependent reframing.'})
else:fullcams=read(OUT/'REAL_MOTION_MATCHED_CAMERAS_R1.json')['cameras']
closecams=read(ROOT/'audits/pianovam_first_web_joint_contribution_isolation_r1/MACHINE_CHECK_R1.json')['frames']
closecams={str(r['frame']):r['same_camera'] for r in closecams}
regcams=m.cameras()
regviews=['PALMAR_FULL','DORSAL_FULL','THENAR_CLOSE']
regression_records=[];selected_records=[];motion_records=[];allchecks={};regression_points={}
for label,asset in [('BEFORE',SOURCE),(tag,path)]:
    ob,rig=load(asset)
    protected=m.product_payload(ob,rig);saved_shape=core.shape_payload(ob)
    assert actions()==source_actions
    for k in native:
        if k!='weights':assert protected[k]==native[k],k
    assert saved_shape['keys'][:len(oldshape['keys'])]==oldshape['keys']
    assert saved_shape['drivers'][:len(oldshape['drivers'])]==oldshape['drivers']
    V0=Varray(ob);F=[tuple(f.vertices) for f in ob.data.polygons];E=np.array([list(e.vertices) for e in ob.data.edges])
    tri=np.array([[f[0],f[j],f[j+1]] for f in F for j in range(1,len(f)-1)])
    # Only minimum finite/area/length gates; no hidden intersections, normal-dot or edge census.
    def safety(V):
        areas=np.linalg.norm(np.cross(V[tri[:,1]]-V[tri[:,0]],V[tri[:,2]]-V[tri[:,0]]),axis=1)/2
        lengths=np.linalg.norm(V[E[:,0]]-V[E[:,1]],axis=1)
        return {'NaN_Inf':int((~np.isfinite(V)).sum()),'collapsed_triangles':int(((areas<=1e-12)|(areas/A0<=1e-6)).sum()),
            'degenerate_edges':int((lengths<=1e-12).sum()),'gross_tearing_severe_stretch':int(((length0>=.003)&(lengths/length0>5)).sum())}
    A0=np.linalg.norm(np.cross(V0[tri[:,1]]-V0[tri[:,0]],V0[tri[:,2]]-V0[tri[:,0]]),axis=1)/2
    length0=np.linalg.norm(V0[E[:,0]]-V0[E[:,1]],axis=1)
    current_checks=[]
    sub=f'{label.lower()}_selected';ensure_dir(sub)
    for f in FRAMES:
        motion(rig,f);V,faces=m.evaluate(ob,ob.matrix_world)
        rr=m.Renderer(closecams[str(f)],sub);rr.sc.display.shading.shadow_intensity=0
        if label!='BEFORE' or not (OUT/sub/f'{label}__F{f:03}__PALMAR_THENAR_CLOSE.png').exists():rr.draw(label,f'F{f:03}',V,faces,list(closecams[str(f)]))
        selected_records.extend(rr.records);rr.dispose()
    sub=f'{label.lower()}_regression';ensure_dir(sub)
    rr=m.Renderer(regcams,sub);rr.sc.display.shading.shadow_intensity=0
    regression_points[label]={}
    for case in m.CASE_IDS:
        regression(rig,case);V,faces=m.evaluate(ob,ob.matrix_world);VA=np.array([list(v) for v in V])
        check=safety(VA);check['case']=case
        if label!='BEFORE' or not (OUT/sub/f'{label}__{case}__PALMAR_FULL.png').exists():rr.draw(label,case,V,faces,regviews)
        regression_points[label][case]=VA.tolist()
        check['pose_corrective_values']={k.name:float(k.value) for k in ob.data.shape_keys.key_blocks[1:]}
        neutral(rig);restore=float(np.linalg.norm(Varray(ob)-V0,axis=1).max()*1000)
        check['ZERO_restore_max_mm']=restore;check['ZERO_restore']='PASS' if restore==0 else 'FAIL'
        assert restore==0
        current_checks.append(check)
    regression_records.extend(rr.records);rr.dispose()
    sub=f'{label.lower()}_motion';ensure_dir(sub)
    # Complete 421-observation check, including the 211 endpoint retained by the source Action.
    previous_q={};bone_flips=0;jumps=0
    for i in range(421):
        motion(rig,1+i//2,(i%2)/2);V=Varray(ob)
        check=safety(V);check['observation_index']=i;check['source_frame']=690+i
        current_checks.append(check)
        q={n:rig.pose.bones[n].rotation_quaternion.copy() for n in native['rest'] if rig.data.bones[n].use_deform}
        if previous_q:
            jumps+=int(any(math.degrees(a.rotation_difference(q[n]).angle)>90 for n,a in previous_q.items()))
        previous_q=q
        if i%2==0 and i<420:
            f=1+i//2
            # render every 30-fps video frame, with the two exact matched source cameras
            rr=m.Renderer(fullcams[str(f)],sub);rr.sc.display.shading.shadow_intensity=0
            if label!='BEFORE' or not (OUT/sub/f'{label}__F{f:03}__PALMAR_MOTION.png').exists():
                Vs,faces=m.evaluate(ob,ob.matrix_world);rr.draw(label,f'F{f:03}',Vs,faces,list(fullcams[str(f)]))
            motion_records.extend(rr.records);rr.dispose()
            if f%30==0:print('FULL_MOTION_PROGRESS',label,f,'/210',flush=True)
    neutral(rig)
    assert np.linalg.norm(Varray(ob)-V0,axis=1).max()==0
    assert m.product_payload(ob,rig)==protected and core.shape_payload(ob)==saved_shape and actions()==source_actions
    counts={k:max(r[k] for r in current_checks) for k in ['NaN_Inf','collapsed_triangles','degenerate_edges','gross_tearing_severe_stretch']}
    # Bone flip semantics unchanged; same saved Action is checked against source hashes.
    allchecks[label]={'minimum_max_counts':counts,'bone_flip_count':read(PREV/'PIANOVAM_AXIS_CORRECTED_ACTION_R1.json')['TEMPORAL_CONTINUITY']['BONE_FLIP_COUNT'],
        'catastrophic_motion_jump_count':jumps,'ZERO_restore':'PASS','zero_before_after_max_mm':float(np.linalg.norm(V0-Vzero_before,axis=1).max()*1000),
        'gross_penetration_visual':'PENDING_ORDINARY_SOLID_REVIEW','checks':current_checks}
    print('CANDIDATE_EVALUATED',label,counts,'JUMPS',jumps,flush=True)
dump(f'{tag}_MINIMUM_SAFETY_R1.json',{'candidate_path':path.relative_to(ROOT).as_posix(),'candidate_sha256':sha(path),'results':allchecks,
    'input_hashes_unchanged':check_inputs()==inputs,'actions_exact':source_actions,
    'basis_vertex_position_writes':0,'forbidden_forensic_runs':0})
dump(f'{tag}_MATCHED_RENDERS_R1.json',{'selected_records':selected_records,'regression_records':regression_records,'motion_records':motion_records,
    'full_video_frames_per_view':210,'fps':30,'duration_seconds':7,'same_source_421_observations':True})
dump(f'{tag}_REGRESSION_POINTS_R1.json',regression_points)
print('FULL_CANDIDATE_REVIEW_READY',tag,flush=True)
