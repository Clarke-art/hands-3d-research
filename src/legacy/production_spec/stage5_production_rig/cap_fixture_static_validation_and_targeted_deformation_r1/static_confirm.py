import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from qualification_common import *
import bpy,struct
assert sha(CAND)==EXPECTED
saved=read(R2D/'R2_CANDIDATE_CLEAN_REOPEN_PAYLOAD.json')
ns={'bpy':bpy}; reuse_functions(R1D/'blender_extract.py',['mesh_payload','rig_payload','weights'],ns)
bpy.ops.wm.open_mainfile(filepath=str(CAND),load_ui=False,use_scripts=False)
ob=bpy.data.objects['Hand  - Realistic'];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
live={'mesh':ns['mesh_payload'](ob),'rig':ns['rig_payload'](rig),'weights':ns['weights'](ob),'group_order':[g.name for g in ob.vertex_groups]}
checks={k:live[k]==saved[k] for k in live}
dump('STATIC_LIVE_REOPEN_PAYLOAD.json',live)
mat=read(OUT/'TARGETED_FIXTURE_MATRIX.json'); W=live['weights']
cap=read(AUTH/'CAP37_SKIN_DRIVER_AUTHORITY_R1.json');r3=read(ROOT/'audits/human_r3_fresh_result_authority_freeze_r1/FRESH_R3_OWNERSHIP_AUTHORITY_R1.json');cont=read(AUTH/'SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json')
f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
rows=[]
for r in cap['per_vertex_surface_evidence']:
    i=r['vertex_id'];s=r['corrected_thumb_projection']['arc_mm'];t=max(0,min(1,.5+(s-cap['rule']['s_IP_mm'])/(2*cap['rule']['h_mm'])))
    q=6*t**5-15*t**4+10*t**3
    expected={g:w for g,w in {'THUMB_IP_R':f32(q),'THUMB_MCP_R':f32(1-q)}.items() if w>0}
    rows.append({'vertex_id':i,'t':t,'expected':expected,'actual':W[i],'exact':W[i]==expected})
checks['cap37_count_and_membership']=len(rows)==37 and sorted(r['vertex_id'] for r in rows)==r3['cap37_preservation']['vertex_ids']
checks['cap37_quintic_exact_and_IP_dominant']=all(r['exact'] and W[r['vertex_id']]['THUMB_IP_R']>.5 for r in rows)
checks['cap37_not_forced_onehot']=any('THUMB_MCP_R' in W[r['vertex_id']] for r in rows)
old=mat['fixtures']['OLD_CAP9']['core'];web=mat['fixtures']['FIRST_WEB']['core']
checks['old9_native_INDEX_only']=len(old)==9 and all(not(set(W[i])-{'WRIST_R','INDEX_MCP_R','INDEX_PIP_R','INDEX_DIP_R'}) for i in old)
checks['web21_membership_exact']=web==r3['FIRST_WEB21']['membership_vertex_ids'] and len(web)==21
checks['web21_exact_IP_helper_zero_and_allowed_support']=all(not(set(W[i])-{'WRIST_R','THUMB_CMC_R','THUMB_MCP_R','INDEX_MCP_R'}) for i in web)
guard=[]
for key,label in r3['membership']['vertex_labels'].items():
    i=int(key);allowed={'WRIST_R','THUMB_CMC_R','THUMB_MCP_R','INDEX_MCP_R'} if i in web else set(cont['ownership_guard']['allowed_by_side'][label])
    if set(W[i])-allowed:guard.append(i)
checks['fresh_frozen962_guard_no_rerun']=len(r3['membership']['vertex_labels'])==962 and not guard
checks['fresh_boundary_exact']=mat['fixtures']['FRESH_R3_TRANSITION_COLLAR']['boundary_edge_ids']==r3['boundary']['edge_ids']
checks['edge5879_v1551_v3125_exact_saved']=live['mesh']['edges'][5879]==[1551,3125] and all(W[i]==saved['weights'][i] for i in [1551,3125])
corrected=S5/'human_thumb_kinematic_authority_correction_r1/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_THUMB_KINEMATIC_CORRECTED_R1.blend'
checks['corrected_source_hash']=sha(corrected)==cap['corrected_rig_sha256']
bpy.ops.wm.open_mainfile(filepath=str(corrected),load_ui=False,use_scripts=False)
corrected_rig=ns['rig_payload'](bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'])
checks['all21_bones_actual_equals_corrected_authority']=live['rig']==corrected_rig
checks['candidate_file_hash']=sha(CAND)==EXPECTED
checks['weight_vector_hash']=digest(W)==VECTOR
status='PASS' if all(checks.values()) else 'FAIL_CLOSED_STATIC_FIXTURE_DRIFT'
dump('CAP_FIXTURE_STATIC_CONFIRMATION.json',{'status':status,'checks':checks,'candidate_sha256':sha(CAND),'weight_vector_sha256':digest(W),'cap37_rows':rows,'old9_weights':{i:W[i] for i in old},'web21_weights':{i:W[i] for i in web},'edge5879_weights':{i:W[i] for i in [1551,3125]},'fresh_R3_violations':guard,'corrected_chain_bones':{k:v for k,v in live['rig']['bones'].items() if k.startswith('THUMB')},'production_writes':0,'deformation_runs':0})
assert status=='PASS',checks
print('STATIC FIXTURE PASS: live production payload exact, canonical cap37, old9 INDEX, web21, fresh962, corrected21bones; no poses')
