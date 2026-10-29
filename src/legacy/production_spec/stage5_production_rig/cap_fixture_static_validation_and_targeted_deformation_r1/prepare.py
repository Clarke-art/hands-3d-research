from qualification_common import *
dump('FROZEN_HASHES_BEFORE.json',inventory())
assert sha(CAND)==EXPECTED
saved=read(R2D/'R2_CANDIDATE_CLEAN_REOPEN_PAYLOAD.json')
assert digest(saved['weights'])==VECTOR
r3=read(ROOT/'audits/human_r3_fresh_result_authority_freeze_r1/FRESH_R3_OWNERSHIP_AUTHORITY_R1.json')
cap=read(AUTH/'CAP37_SKIN_DRIVER_AUTHORITY_R1.json'); old=read(AUTH/'OLD_CAP9_SKIN_CORRECTION_AUTHORITY_R1.json');web=read(AUTH/'FIRST_WEB_SKIN_WEIGHT_WRAPPER_R2.json')
cont=read(AUTH/'SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json')
capids=sorted(r['vertex_id'] for r in cap['per_vertex_surface_evidence'])
oldids=old['vertex_ids'];webids=web['membership']['vertex_ids']
boundary=r3['boundary']['edge_ids'];edges=saved['mesh']['edges']
collar=sorted({v for k in boundary for v in edges[k]})
adj={v:set() for v in range(len(saved['weights']))}
for a,b in edges: adj[a].add(b);adj[b].add(a)
def ring(ids,n):
    s=set(ids)
    for _ in range(n): s.update({b for a in list(s) for b in adj[a]})
    return sorted(s)
fixtures={
 'CAP37':{'core':capids,'region':cap['continuity_gate']['cap_2ring_vertex_ids'],'source':'CAP37_SKIN_DRIVER_AUTHORITY_R1.json'},
 'OLD_CAP9':{'core':oldids,'region':old['continuity_gate']['patch_vertex_ids'],'source':'OLD_CAP9_SKIN_CORRECTION_AUTHORITY_R1.json'},
 'FIRST_WEB':{'core':webids,'region':web['continuity_scope'],'source':'FIRST_WEB_SKIN_WEIGHT_WRAPPER_R2.json'},
 'FRESH_R3_TRANSITION_COLLAR':{'core':collar,'region':ring(collar,2),'boundary_edge_ids':boundary,'source':'FRESH_R3_OWNERSHIP_AUTHORITY_R1.json'},
 'EDGE5879':{'core':edges[5879],'region':read(AUTH/'EDGE5879_REBUILD_SCOPE_R1.json')['neighborhood_ids'],'source':'EDGE5879_REBUILD_SCOPE_R1.json'}}
for f in fixtures.values():
    f['core']=sorted(f['core']);f['region']=sorted(f['region']);s=set(f['region'])
    f['edge_ids']=[k for k,(a,b) in enumerate(edges) if a in s or b in s]
    f['face_ids']=[k for k,p in enumerate(saved['mesh']['faces']) if set(p)&s]
    f['all_vertices_face_ids']=[k for k,p in enumerate(saved['mesh']['faces']) if set(p)<=s]
poses=[{'case_id':n,'bone':b,'angle_deg':a,'rotation_sign':-1,'run_label':'TARGETED_ISOLATED_FLEXION'} for n,b,a in [('TH_IP_30','THUMB_IP_R',30),('TH_IP_45','THUMB_IP_R',45),('TH_MCP_45','THUMB_MCP_R',45)]]
cm=read(S6/'stage6b/STAGE6B_CASE_MATRIX.json')
for n in ['CMC_OPP_30','CMC_MCP_L3','FULL_OPP_L3']:
    row=next(c for c in cm['cases'] if c['case_id']==n)
    poses.append({'case_id':n,'cmc_quaternion_local':row['cmc_quaternion_local'],'mcp_deg':row['mcp_deg'],'ip_deg':row['ip_deg'],'rotation_sign':-1,'run_label':'TARGETED_DIAGNOSTIC_PROBE'})
cases=read(S6/'stage6a_r1b/STAGE6A_R1B_CASE_MATRIX.json')
dump('HISTORICAL_INDEX_CASE_SOURCE.json',cases)
ix=next(c for c in cases['cases'] if c['case_id']=='IDX_MCP_45')
assert ix['bone']=='INDEX_MCP_R' and ix['angle_deg']==45 and ix['sign']==-1
poses.append({'case_id':ix['case_id'],'bone':ix['bone'],'angle_deg':ix['angle_deg'],'rotation_sign':ix['sign'],'run_label':'TARGETED_INDEX_COMPATIBILITY_CONTROL'})
for f in fixtures.values(): f['pose_ids']=[p['case_id'] for p in poses]
debt=read(R2D/'R2_STATIC_BLOCKER_CLASSIFICATION.json')['edges'];mapping=[]
for row in debt:
    eid=row['edge_id'];a,b=edges[eid];groups=sorted(set(saved['weights'][a])|set(saved['weights'][b]))
    family='THUMB_IP_MCP_FIRST_WEB_INTERFACE' if 'THUMB_IP_R' in groups else 'THUMB_CMC_MCP_TRANSITION' if 'THUMB_MCP_R' in groups else 'THUMB_CMC_WRIST_TRANSITION'
    relevant=['TH_IP_30','TH_IP_45'] if 'THUMB_IP_R' in groups else []
    if 'THUMB_MCP_R' in groups: relevant+=['TH_MCP_45']
    relevant+=['CMC_OPP_30','CMC_MCP_L3','FULL_OPP_L3']
    local=ring([a,b],1)
    mapping.append({'debt_id':eid,'vertex_ids':[a,b],'mesh_region':family,'region_basis':'Frozen endpoint driver support; not new anatomy','frozen_labels':[r3['membership']['vertex_labels'].get(str(v),'OUTSIDE_BOUNDED_DOMAIN') for v in [a,b]],'driver_family':groups,'existing_fixture':'R1E six-pose thumb transition prequalification','core_fixture_context':[n for n,f in fixtures.items() if eid in f['edge_ids']],'historical_pose_ids':relevant,'local_patch_vertices':local,'local_patch_faces':[k for k,p in enumerate(saved['mesh']['faces']) if set(p)&set(local)],'static_metrics':row['R2_metrics'],'exact_donor_weights':all(saved['weights'][v]==read(R1D/'LIVE_SOURCE_DATA_R1.json')['R1B']['weights'][v] for v in [a,b]),'disposition':'PENDING_TARGETED_MEASUREMENT'})
dump('INHERITED_DEBT_DEFORMATION_MAPPING.json',{'total':16,'mapped':len(mapping),'rows':mapping})
sources=[S5/'stage5b_r1e_cap_dependency_blast_radius_audit_r1/CAP_CORRECTION_RECOVERY_SEQUENCE_R1.json',S5/'stage5b_r1d/scripts/s5b_r1d_prequal.py',S5/'stage5b_r1e/scripts/s5b_r1e_prequal.py',S5/'stage5b_r1e/scripts/s5b_r1e_common.py',S5/'stage5b_r1e_feasibility_audit/scripts/feas_audit.py',S5/'stage5b_r1e_feasibility_audit/scripts/feas_render.py',S5/'stage5b_r1e_feasibility_audit/R1E_EDGE5879_FORENSIC_AUDIT.json',S6/'stage6a/scripts/s6a_common.py',S6/'stage6a_r1b/scripts/s6a_r1b_run_cases.py',S6/'stage6a_r1b/STAGE6A_R1B_CASE_MATRIX.json',S6/'stage6b/STAGE6B_CASE_MATRIX.json',S6/'stage6b_r1b/scripts/s6b_r1b_run_cases.py',S6/'stage6b_r1c/scripts/r1c_pen_common.py']
dump('TARGETED_FIXTURE_MATRIX.json',{'phase':PHASE,'qualification_scope':'TARGETED ONLY','fixtures':fixtures,'poses':poses,'sources':{p.relative_to(ROOT).as_posix():sha(p) for p in sources},'selector_updates':['cap9 -> frozen cap37; old9 retained as native INDEX control','obsolete old R3 collar16 -> frozen fresh boundary20/collar and two-ring','no cut-component anatomical interpretation; fresh pure-face labels and mixed-band review'],'edge5879_historical_trigger':'CMC_MCP_L3','threshold_authority':'Stage6A Gate Amendment R2 via s5b_r1e_common; severe bind>=3mm and ratio>5; tear ratio>3 and posed>5mm; Stage6A R1B collapse area<=1e-12m2 or ratio<=1e-6','CMC_OPPOSITION_PASS':False,'full_Stage6A':False,'full_Stage6B':False,'true_cap_bound_recomputed':False})
print('Prepared five frozen fixtures, seven existing poses, 16 debt mappings; no deformation yet')
