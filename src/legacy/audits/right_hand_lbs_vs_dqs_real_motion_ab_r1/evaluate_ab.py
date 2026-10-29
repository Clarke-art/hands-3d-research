import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
before=inputs()
verification=read(OUT/'DEFORMATION_MODE_VERIFICATION_R1.json')
assert verification['status']=='PASS' and sha(TEST)==verification['test_asset']['sha256']
bpy.ops.wm.open_mainfile(filepath=str(TEST),load_ui=False,use_scripts=False)
obs={'LBS':bpy.data.objects['A_LBS'],'DQS':bpy.data.objects['B_DQS']}
source_action=digest(action_payload(bpy.data.actions[ACTION]))
assert source_action==verification['source_action_payload_sha256']
initial_shape=core.shape_payload(obs['LBS'])
neutral();zero={label:coords(o) for label,o in obs.items()}
faces=[tuple(p.vertices) for p in obs['LBS'].data.polygons]
edges=np.array([list(e.vertices) for e in obs['LBS'].data.edges])
tris=np.array([[f[0],f[j],f[j+1]] for f in faces for j in range(1,len(f)-1)])
owners=np.array([i for i,f in enumerate(faces) for j in range(1,len(f)-1)])
def areas(v):
    a=np.linalg.norm(np.cross(v[tris[:,1]]-v[tris[:,0]],v[tris[:,2]]-v[tris[:,0]]),axis=1)*.5
    return np.bincount(owners,weights=a,minlength=len(faces))
A0={l:areas(v) for l,v in zero.items()}
def safety(label,v):
    aa=areas(v);length=np.linalg.norm(v[edges[:,0]]-v[edges[:,1]],axis=1)
    return {'NaN_Inf':int((~np.isfinite(v)).sum()),'collapsed_faces':int(((aa<=1e-12)|(aa/A0[label]<=1e-6)).sum()),'degenerate_edges':int((length<=1e-12).sum())}
def sync_check():
    a,b=rigs()
    assert all(np.array_equal(np.array(p.matrix),np.array(b.pose.bones[p.name].matrix)) for p in a.pose.bones),'A/B pose matrices differ'
def draw(label,pose,cams,sub):
    if all((OUT/sub/f'{label}__{pose}__{v}.png').exists() for v in cams):return []
    o=obs[label];V,F=m.evaluate(o,o.matrix_world)
    rr=m.Renderer(cams,sub);rr.sc.display.shading.shadow_intensity=0
    rr.draw(label,pose,V,F,list(cams));rr.dispose();return rr.records
# Camera data only, inherited from the unchanged BEFORE motion; no rejected candidate geometry is loaded.
fullcams=read(ROOT/'audits/first_web_real_motion_deformation_fix_r1/REAL_MOTION_MATCHED_CAMERAS_R1.json')['cameras']
rows=read(ROOT/'audits/pianovam_first_web_joint_contribution_isolation_r1/MACHINE_CHECK_R1.json')['frames']
closecams={str(r['frame']):copy.deepcopy(r['same_camera']) for r in rows if r['condition']=='BASELINE'}
for f in FRAMES:
    c=closecams[str(f)]
    c['FIRST_WEB_CLOSE']=copy.deepcopy(c['FIRST_WEB_OBLIQUE']);c['FIRST_WEB_CLOSE']['direction']=c['PALMAR_THENAR_CLOSE']['direction']
    c['PALMAR_CONTEXT']=copy.deepcopy(c['PALMAR_THENAR_CLOSE']);c['PALMAR_CONTEXT']['ortho_scale_m']=.23
regcams=m.cameras()
regcams={k:regcams[k] for k in ['PALMAR_FULL','THENAR_CLOSE','DORSAL_FULL']}
zero_close=copy.deepcopy(regcams['THENAR_CLOSE']);zero_close['ortho_scale_m']=.070
regcams['FIRST_WEB_CLOSE']=zero_close
dump('MATCHED_CAMERAS_R1.json',{'selected':closecams,'regression':regcams,'motion':fullcams,'camera_source':'Existing unchanged-source cameras reused verbatim for full motion. Selected third frontal close derived from existing center/scale. No DQS-dependent framing.','identical_settings':True})
records=[];reg=[];selected=[];checks={l:[] for l in obs}
for case in m.CASE_IDS:
    regression(case);sync_check()
    row={'case':case,'conditions':{}}
    for label,o in obs.items():
        v=coords(o);ch=safety(label,v);checks[label].append(ch)
        row['conditions'][label]={'corrective_natural_values':values(o),'minimum':ch,'renders':[f'{label.lower()}_regression/{label}__{case}__{k}.png' for k in regcams]}
        records+=draw(label,case,regcams,label.lower()+'_regression')
    row['ZERO_LBS_DQS_max_distance_mm']=float(np.linalg.norm(coords(obs['LBS'])-coords(obs['DQS']),axis=1).max()*1000) if case=='ZERO' else None
    neutral()
    row['ZERO_restore']={l:float(np.linalg.norm(coords(o)-zero[l],axis=1).max()*1000) for l,o in obs.items()}
    assert all(x==0 for x in row['ZERO_restore'].values())
    reg.append(row)
dump('REGRESSION_LBS_VS_DQS_R1.json',{'poses':reg,'scope':'Six approved ordinary solid-view poses; human-visible review pending','ZERO_restore':'PASS'})
for f in FRAMES:
    motion(f);sync_check()
    row={'frame':f,'source_observation_index':2*(f-1),'source_frame':690+2*(f-1),'source_time_seconds':11.5+(f-1)/30,'conditions':{}}
    for label,o in obs.items():
        row['conditions'][label]={'corrective_natural_values':values(o),'renders':[f'{label.lower()}_selected/{label}__F{f:03}__{k}.png' for k in closecams[str(f)]]}
        records+=draw(label,f'F{f:03}',closecams[str(f)],label.lower()+'_selected')
    selected.append(row)
dump('KEYFRAME_LBS_VS_DQS_R1.json',{'frames':selected,'source_timing_unchanged':True,'severity_census_run':False,'natural_approved_corrective':True})
motion_values=[]
for i in range(421):
    f=1+i//2;motion(f,(i%2)/2);sync_check()
    for label,o in obs.items():
        ch=safety(label,coords(o));ch['observation']=i;checks[label].append(ch)
    motion_values.append({'observation':i,'frame':1+i/2,'source_frame':690+i,'approved_corrective_value':values(obs['LBS'])})
    if i%2==0 and i<420:
        for label in obs:records+=draw(label,f'F{f:03}',fullcams[str(f)],label.lower()+'_motion')
        if f%30==0:print('AB_FULL_MOTION_PROGRESS',f,'/210',flush=True)
neutral()
restore={l:float(np.linalg.norm(coords(o)-zero[l],axis=1).max()*1000) for l,o in obs.items()}
assert all(x==0 for x in restore.values())
assert core.shape_payload(obs['LBS'])==initial_shape
assert digest(action_payload(bpy.data.actions[ACTION]))==source_action
assert inputs()==before and sha(TEST)==verification['test_asset']['sha256']
maximum={l:{k:max(r[k] for r in checks[l]) for k in ['NaN_Inf','collapsed_faces','degenerate_edges']} for l in obs}
assert all(x==0 for r in maximum.values() for x in r.values())
dump('MINIMUM_MACHINE_SAFETY_R1.json',{'status':'PASS','observations_per_condition':421,'approved_regression_poses':6,'maximum_counts':maximum,'ZERO_restore':'PASS','ZERO_restore_max_mm':restore,'ZERO_A_B_max_mm':float(np.linalg.norm(zero['LBS']-zero['DQS'],axis=1).max()*1000),'gross_visible_tearing':'PENDING_ORDINARY_VISUAL_REVIEW','no_complex_forensics':True,'checks':checks})
dump('APPROVED_CORRECTIVE_NATURAL_VALUES_R1.json',{'motion':motion_values,'forced_corrective_values':False})
dump('MATCHED_RENDER_VERIFICATION_R1.json',{'records':records,'complete_motion_frames_per_condition_per_view':210,'fps':30,'duration_seconds':7,'protected_asset_sha256':sha(TEST),'input_hashes_unchanged':before,'pose_matrices_identical_all_observations_and_regression':True,'action_sha256':source_action,'new_corrective_count':0,'no_source_asset_saved':True})
print('AB_ALL_EVALUATION_RENDER_PASS',maximum,flush=True)
