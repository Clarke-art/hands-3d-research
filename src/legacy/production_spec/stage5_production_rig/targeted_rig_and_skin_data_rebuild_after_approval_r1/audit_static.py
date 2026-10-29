from common import *
import math
from collections import Counter
POST=read(OUT/'CANDIDATE_CLEAN_REOPEN_PAYLOAD_R1.json');SOURCES=read(OUT/'LIVE_SOURCE_DATA_R1.json')
DONOR_W=SOURCES['R1B']['weights'];W=POST['weights'];EDGES=POST['mesh']['edges']
AUTH=read(OUT/'AUTHORIZED_WEIGHT_WRITE_SET_R1.json');GEN=read(OUT/'DETERMINISTIC_WEIGHT_GENERATION_R1.json')
CONT=read(PROPOSAL/'SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json');ENV=read(PROPOSAL/'SKIN_REBUILD_ENVELOPE_R1.json')
CAP=read(PROPOSAL/'CAP37_SKIN_DRIVER_AUTHORITY_R1.json');OLD=read(PROPOSAL/'OLD_CAP9_SKIN_CORRECTION_AUTHORITY_R1.json')
WEB=read(PROPOSAL/'FIRST_WEB_SKIN_WEIGHT_WRAPPER_R2.json');EDGE=read(PROPOSAL/'EDGE5879_REBUILD_SCOPE_R1.json')
R3=read(ROOT/'audits/human_r3_fresh_result_authority_freeze_r1/FRESH_R3_OWNERSHIP_AUTHORITY_R1.json')
LABEL={int(k):v for k,v in R3['membership']['vertex_labels'].items()}
SETS={k:set(AUTH[k]) for k in ['SAFE_REUSE','TARGETED_REVALIDATION','REBUILD_REQUIRED']}
WRITE=SETS['REBUILD_REQUIRED'];CHECK=set(ENV['vertex_ids']);CAPIDS={x['vertex_id'] for x in CAP['per_vertex_surface_evidence']};WEBIDS=set(WEB['membership']['vertex_ids']);OLDIDS=set(OLD['vertex_ids'])
adj={i:set() for i in range(3416)};incident={i:[] for i in range(3416)}
for eid,(i,j) in enumerate(EDGES):adj[i].add(j);adj[j].add(i);incident[i].append(eid);incident[j].append(eid)
def classification(i):return next(k for k,s in SETS.items() if i in s)
def diff(a,b):
    groups=sorted(set(a)|set(b));ds={g:abs(a.get(g,0)-b.get(g,0)) for g in groups}
    return {'L_inf':max(ds.values(),default=0),'L1':sum(ds.values()),'per_group':ds}
def edge_metric(eid):
    i,j=EDGES[eid];a=diff(DONOR_W[i],DONOR_W[j]);b=diff(W[i],W[j])
    return {'edge_id':eid,'vertex_ids':[i,j],'classifications':[classification(i),classification(j)],
      'frozen_sides':[LABEL.get(i,'OUTSIDE_BOUNDED_R3'),LABEL.get(j,'OUTSIDE_BOUNDED_R3')],
      'before':a,'after':b,'L_inf_delta':b['L_inf']-a['L_inf'],'L1_delta':b['L1']-a['L1'],
      'THUMB_IP_jump':abs(W[i].get('THUMB_IP_R',0)-W[j].get('THUMB_IP_R',0)),
      'THUMB_MCP_jump':abs(W[i].get('THUMB_MCP_R',0)-W[j].get('THUMB_MCP_R',0)),
      'touches_authorized_write':i in WRITE or j in WRITE}
changed=[];changes=[];entry_count=0;max_delta=0
for i in range(3416):
    groups=sorted(set(DONOR_W[i])|set(W[i]));entries=[]
    for g in groups:
        before=DONOR_W[i].get(g,0);after=W[i].get(g,0)
        if before!=after:entries.append({'group':g,'before':before,'after':after,'delta':after-before});max_delta=max(max_delta,abs(after-before))
    if entries:
        changed.append(i);entry_count+=len(entries);changes.append({'vertex_id':i,'classification':classification(i),'changed_groups':entries})
changedset=set(changed);outside=changedset-WRITE
assert not outside,'FAIL_CLOSED outside authorized write'
for name in ['SAFE_REUSE','TARGETED_REVALIDATION']:
    setids=SETS[name];rows=[{'vertex_id':i,'exact_equal':W[i]==DONOR_W[i],'R1B_vector_sha256':digest(DONOR_W[i]),'candidate_vector_sha256':digest(W[i])} for i in sorted(setids)]
    assert all(x['exact_equal'] for x in rows)
    namefile='SAFE_REUSE_EXACT_COPY_AUDIT_R1.json' if name=='SAFE_REUSE' else 'TARGETED_REVALIDATION_COPY_AUDIT_R1.json'
    dump(namefile,{'status':'PASS','expected_count':len(setids),'exact_copied_count':len(setids),'drift_count':0,
      'normalization_or_pruning_applied':False,'per_vertex':rows,'source_R1B_sha256':sha(DONOR),'candidate_sha256':sha(CANDIDATE)})
dump('WEIGHT_DELTA_CENSUS_R1.json',{'status':'PASS_AUTHORIZED_WRITE_SCOPE','candidate_vs':'Frozen R1B donor',
 'changed_vertex_count':len(changed),'unchanged_count':3416-len(changed),'changed_group_entries_count':entry_count,'max_absolute_delta':max_delta,
 'changed_vertex_ids':changed,'outside_approved_write_count':len(outside),'outside_approved_write_ids':sorted(outside),
 'SAFE_REUSE_drift_count':len(changedset&SETS['SAFE_REUSE']),'TARGETED_REVALIDATION_drift_count':len(changedset&SETS['TARGETED_REVALIDATION']),
 'REBUILD_REQUIRED_expected':244,'REBUILD_REQUIRED_evaluated':GEN['evaluated_count'],'REBUILD_REQUIRED_changed_count':len(changedset&WRITE),
 'evaluated_but_numerically_unchanged_ids':sorted(WRITE-changedset),'per_vertex_delta':changes})
mathviol={'weight_sum':[],'negative_weight':[],'NaN_Inf':[],'nondeform_group':[],'TIP_helper':[],'influence_count':[]}
tol=CONT['normalization']['absolute_tolerance']
for i,w in enumerate(W):
    if abs(sum(w.values())-1)>tol:mathviol['weight_sum'].append({'vertex_id':i,'sum':sum(w.values())})
    if any(x<0 for x in w.values()):mathviol['negative_weight'].append(i)
    if any(not math.isfinite(x) for x in w.values()):mathviol['NaN_Inf'].append(i)
    if set(w)-set(CONT['deform_bones']):mathviol['nondeform_group'].append(i)
    if any(w.get(g,0)!=0 for g in CONT['helpers']['names']):mathviol['TIP_helper'].append(i)
    if len([v for v in w.values() if v>0])>CONT['max_influences']:mathviol['influence_count'].append(i)
leaks=[]
for i,side in LABEL.items():
    allowed=set(WEB['allowed_deform_groups'] if i in WEBIDS else CONT['ownership_guard']['allowed_by_side'][side])
    forbidden={g:x for g,x in W[i].items() if g not in allowed and x>CONT['ownership_guard']['forbidden_weight']}
    if forbidden:
        leaks.append({'vertex_id':i,'classification':classification(i),'side':side,'forbidden_groups':forbidden,
          'maximum_forbidden_weight':max(forbidden.values()),'copied_exactly':W[i]==DONOR_W[i],
          'flag':'TARGETED_VALIDATION_FLAG' if i in SETS['TARGETED_REVALIDATION'] else 'IMMUTABLE_SAFE_COPY_FLAG',
          'new_violation':any(DONOR_W[i].get(g,0)!=x for g,x in forbidden.items())})
assert all(x['copied_exactly'] and not x['new_violation'] for x in leaks)
web_ip=[i for i in WEBIDS if W[i].get('THUMB_IP_R',0)!=0]
cap_family=[i for i in CAPIDS if set(W[i])-set(CAP['allowed_cap_deform_groups'])]
old_family=[i for i in OLDIDS if set(W[i])-set(OLD['allowed_deform_groups'])]
gates=CONT['static_edge_gates'];edgescope=[eid for eid,(i,j) in enumerate(EDGES) if i in CHECK or j in CHECK]
all_edges=[edge_metric(eid) for eid in edgescope];blockers=[];copyflags=[];regressions=[];cert=[]
for r in all_edges:
    i,j=r['vertex_ids'];ex=[]
    if r['after']['L_inf']>gates['max_single_group_jump_proposal']:ex.append('SINGLE_GROUP_JUMP_GT_0_5')
    if r['after']['L1']>gates['max_L1_jump_proposal']:ex.append('L1_JUMP_GT_1')
    # Immutable donor seam regressions are recorded independently. They cannot
    # be used to tune weights in this candidate-only round.
    if r['L_inf_delta']>tol or r['L1_delta']>tol:regressions.append(r)
    if ex:
        b={**r,'reasons':ex,'blocking':True,'copy_only_flag':not r['touches_authorized_write']}
        blockers.append(b)
        if not r['touches_authorized_write']:
            copyflags.append({**r,'flag':'TARGETED_VALIDATION_FLAG','policy':'Copy-only entries cannot be edited in this phase'})
            cert.append({'type':'IMMUTABLE_EDGE_EXCEEDS_APPROVED_GATE','edge_id':r['edge_id'],'vertices':[i,j],
                 'immutable_endpoint_vectors':[W[i],W[j]],'L_inf':r['after']['L_inf'],'L1':r['after']['L1'],
                 'proof':'Both endpoints outside244 must remain exact R1B copies. Therefore no legal244-only reconstruction can change this edge metric.'})
        for u,v in [(i,j),(j,i)]:
            if u in WRITE and v not in WRITE and u in LABEL:
                allowed=set(WEB['allowed_deform_groups'] if u in WEBIDS else CONT['ownership_guard']['allowed_by_side'][LABEL[u]])
                for g,x in W[v].items():
                    if g not in allowed and x>gates['max_single_group_jump_proposal']:
                        cert.append({'type':'FORBIDDEN_GROUP_ZERO_VS_IMMUTABLE_NEIGHBOR','edge_id':r['edge_id'],'write_vertex':u,'immutable_vertex':v,
                          'group':g,'required_write_weight':0,'immutable_neighbor_weight':x,
                          'minimum_possible_group_jump':x,'gate_limit':gates['max_single_group_jump_proposal'],
                          'proof':'Approved side/wrapper forbids this group at the write vertex; immutable neighbor has the shown fixed positive weight. Every legal candidate exceeds the group jump gate, regardless of solver/parameters.'})
for leak in leaks:
    cert.append({'type':'IMMUTABLE_FORBIDDEN_POSITIVE_WEIGHT','vertex_id':leak['vertex_id'],'classification':leak['classification'],
       'forbidden_groups':leak['forbidden_groups'],'required_maximum':0,
       'proof':'Strict guard requires zero; approved exact-copy scope forbids removing even this historical micro-weight this round.'})
assert cert,'Expected hard scope conflict evidence for fail-closed outcome'
dump('STATIC_SCOPE_CONFLICT_CERTIFICATE_R1.json',{'status':'FAIL_CLOSED','new_authority_created':False,
 'proof_scope':'Approved exact-copy/write and strict static gates only; no anatomy or deformation assumptions',
 'continuity_impossibility_witnesses':cert,'witness_count':len(cert),
 'remedy_not_executed':'Would require later explicit write-scope/support/acceptance reconciliation or permitted qualification. No edits to current approval, membership, protected vectors or rig.'})
dump('SKIN_CONTINUITY_STATIC_CHECK_R1.json',{'status':'FAIL_CLOSED_REBUILD_OR_STATIC_INTEGRITY','candidate_static_pass':False,
 'weight_math':{'status':'PASS' if all(not v for v in mathviol.values()) else 'FAIL','violations':mathviol,'sum_tolerance':tol,
      'max_sum_error':max(abs(sum(w.values())-1) for w in W),'max_influences':max(len(w) for w in W)},
 'ownership_guard':{'strict_forbidden_weight_limit':0,'illegal_cross_digit_leakage_vertex_count':len(leaks),
     'illegal_cross_digit_leakage_entry_count':sum(len(x['forbidden_groups']) for x in leaks),
     'above_1e_6_vertex_count':sum(x['maximum_forbidden_weight']>1e-6 for x in leaks),
     'above_1e_8_vertex_count':sum(x['maximum_forbidden_weight']>1e-8 for x in leaks),
     'new_violation_count':sum(x['new_violation'] for x in leaks),'per_vertex':leaks,
     'note':'All nonzero forbidden values are historical exact-copy residues; strict contract is zero, so do not silently loosen tolerance or edit copy-only values.'},
 'FIRST_WEB_THUMB_IP_violation_ids':sorted(web_ip),'cap37_driver_family_violation_ids':sorted(cap_family),
 'old_cap9_driver_family_violation_ids':sorted(old_family),
 'continuity_edge_count_checked':len(all_edges),'approved_max_single_group_jump':gates['max_single_group_jump_proposal'],
 'approved_max_L1_jump':gates['max_L1_jump_proposal'],'edge_metric_comparison':'Exact saved float32 values evaluated in Python double; no unapproved gate relaxation',
 'continuity_static_blocker_count':len(blockers),'with_write_blocker_count':sum(x['touches_authorized_write'] for x in blockers),
 'copy_only_blocker_count':len(copyflags),'blockers':blockers,'copy_only_TARGETED_VALIDATION_FLAGs':copyflags,
 'regression_increase_edges_count':len(regressions),'regression_increase_edges':regressions,'all_checked_edges':all_edges,
 'no_one_ring_driver_swap':'FAIL where blockers show disjoint or severe single-group partitions',
 'projection_tie_seam_policy':'Approved fixed profile evaluated on corrected projection; actual adjacent-edge metrics checked, no anatomy relabeling.',
 'candidate_deformation_pass':False,'deformation_runs':0,'R3_reruns':0,'full_Stage6_runs':0,
 'write_scope_expanded':False,'outside_writes':0,'flagged_copy_only_vectors_modified':False})
def continuity_for_vertices(seed):
    ei=sorted(set(eid for i in seed for eid in incident[i]));records=[edge_metric(eid) for eid in ei]
    bad=[r for r in records if r['after']['L_inf']>gates['max_single_group_jump_proposal'] or r['after']['L1']>gates['max_L1_jump_proposal']]
    return {'incident_edge_count':len(records),'max_after_L_inf':max((r['after']['L_inf'] for r in records),default=0),
      'max_after_L1':max((r['after']['L1'] for r in records),default=0),'blocker_count':len(bad),
      'status':'PASS_STATIC_ABSOLUTE_GATES' if not bad else 'FAIL_STATIC_CONTINUITY_GATE','edge_records':records}
def vertex_rows(seed):
    return [{'vertex_id':i,'classification':classification(i),'before':DONOR_W[i],'after':W[i],'changed':i in changedset,
      'dominant_before':max(DONOR_W[i],key=DONOR_W[i].get),'dominant_after':max(W[i],key=W[i].get),
      'neighbor_evidence':[{'vertex_id':j,'classification':classification(j),'side':LABEL.get(j,'OUTSIDE_BOUNDED_R3'),
        'candidate_vector':W[j],'before_vector':DONOR_W[j],'driver_families':sorted({g.split('_')[0] for g in W[j]}),
        'weight_gradient':diff(W[i],W[j]),'neighbor_dominant':max(W[j],key=W[j].get)} for j in sorted(adj[i])],
      'continuity_metric':continuity_for_vertices({i})} for i in sorted(seed)]
caprows=vertex_rows(CAPIDS)
dump('CAP37_WEIGHT_REBUILD_RESULT_R1.json',{'rule_evaluation_status':'PASS','evaluated_count':37,'actual_changed_count':len(CAPIDS&changedset),
 'authority_sha256':sha(PROPOSAL/'CAP37_SKIN_DRIVER_AUTHORITY_R1.json'),'IP_MCP_only':not cap_family,
 'IP_distribution':{'min':min(W[i].get('THUMB_IP_R',0) for i in CAPIDS),'max':max(W[i].get('THUMB_IP_R',0) for i in CAPIDS)},
 'MCP_distribution':{'min':min(W[i].get('THUMB_MCP_R',0) for i in CAPIDS),'max':max(W[i].get('THUMB_MCP_R',0) for i in CAPIDS)},
 'IP_exact_one_hot_count':sum(W[i]=={'THUMB_IP_R':1.0} for i in CAPIDS),'all37_one_hot':False,
 'one_hot_reason':'Only mathematical quintic plateau; no membership one-hot override',
 'one_ring_continuity':continuity_for_vertices(CAPIDS),'per_vertex_before_after':caprows,'pose_tuning_runs':0})
oldrows=vertex_rows(OLDIDS);oldsource={x['vertex_id']:x for x in OLD['per_vertex_evidence']}
for r in oldrows:
    r['frozen_INDEX_witness_evidence']=oldsource[r['vertex_id']]['clean_INDEX_witnesses']
    r['driver_family_pass']=set(r['after'])<=set(OLD['allowed_deform_groups'])
    r['INDEX_MCP_one_hot']=r['after']=={'INDEX_MCP_R':1.0}
dump('OLD_CAP9_WEIGHT_REBUILD_RESULT_R1.json',{'rule_evaluation_status':'PASS','evaluated_count':9,'actual_changed_count':len(OLDIDS&changedset),
 'historical_THUMB_override_retired':not old_family,'one_hot_INDEX_MCP_assumed':False,'INDEX_MCP_one_hot_count':sum(r['INDEX_MCP_one_hot'] for r in oldrows),
 'authority_sha256':sha(PROPOSAL/'OLD_CAP9_SKIN_CORRECTION_AUTHORITY_R1.json'),'one_ring_continuity':continuity_for_vertices(OLDIDS),
 '9_of_9_before_after_neighbor_metrics_present':len(oldrows)==9,'per_vertex':oldrows})
dump('FIRST_WEB_WEIGHT_REBUILD_RESULT_R1.json',{'status':'PASS_WRAPPER_AND_WRITE_PERMISSION','authority_sha256':sha(PROPOSAL/'FIRST_WEB_SKIN_WEIGHT_WRAPPER_R2.json'),
 'membership_count':21,'membership_changed':False,'rebuild_evaluated_count':len(WEBIDS&WRITE),'copy_only_exact_count':len(WEBIDS-WRITE),
 'authorized_write_ids':sorted(WEBIDS&WRITE),'actual_changed_count':len(WEBIDS&changedset),'actual_changed_ids':sorted(WEBIDS&changedset),
 'allowed_groups':WEB['allowed_deform_groups'],'THUMB_IP_violation_count':len(web_ip),
 'three_way_continuity_scope':WEB['continuity_scope'],'one_ring_continuity':continuity_for_vertices(WEBIDS),'per_vertex':vertex_rows(WEBIDS),
 'labels_to_one_hot':False,'copy_only_vectors_modified':False})
edgeids=set(EDGE['neighborhood_ids']);metric5879=edge_metric(5879)
dump('EDGE5879_WEIGHT_REBUILD_RESULT_R1.json',{'scope_applied':True,'authority_sha256':sha(PROPOSAL/'EDGE5879_REBUILD_SCOPE_R1.json'),
 'edge_id':5879,'endpoints':EDGE['endpoints'],'before':[DONOR_W[i] for i in EDGE['endpoints']],
 'after':[W[i] for i in EDGE['endpoints']],'endpoint_changed':{str(i):i in changedset for i in EDGE['endpoints']},
 'authorized_neighborhood_write_ids':sorted(edgeids&WRITE),'evaluated_neighborhood_write_count':len(edgeids&WRITE),
 'copy_only_neighborhood_ids':sorted(edgeids-WRITE),'copy_only_neighborhood_exact':all(W[i]==DONOR_W[i] for i in edgeids-WRITE),
 'edge_static_metric':metric5879,'approved_neighborhood_continuity':continuity_for_vertices(edgeids),
 'static_partition_comparison':'Only saved candidate skin-vector differences measured; no pose metric or deformation improvement claim',
 'historical_R1E_CMC_MCP_L3_ratio':EDGE['historical_R1E_CMC_MCP_L3_ratio'],'old_R1E_vectors_used_as_base':False,
 'targeted_deformation_pass':False,'pose_test_or_tuning_loop_runs':0})
mesh_keys=['positions_local_m','positions_world_mm','edges','faces','UV_layers','face_material_indices','material_slots']
geomchecks={k:POST['mesh'][k]==SOURCES['STAGE4C']['mesh'][k] for k in mesh_keys}
rigcheck=POST['rig']==SOURCES['CORRECTED']['rig']
originchecks={k:POST['mesh'][k]==SOURCES['CORRECTED']['mesh'][k] for k in ['matrix_world','matrix_local','matrix_parent_inverse','location','rotation_mode','rotation_euler','scale','parent']}
assert all(geomchecks.values()) and rigcheck and all(originchecks.values())
binding=POST['mesh']['modifiers'];assert len(binding)==1 and binding[0]['type']=='ARMATURE' and binding[0]['object']=='RIGHT_HAND_PRODUCTION_RIG' and not binding[0]['use_bone_envelopes']
dump('RIG_AND_GEOMETRY_NO_DRIFT_AUDIT_R1.json',{'status':'PASS','frozen_Stage4C_geometry_checks':geomchecks,'corrected_rig_full_snapshot_exact':rigcheck,
 'all21_bones_head_tail_matrix_parent_deform_pose_values_unchanged':True,'IP_head_preserved':True,
 'corrected_5_slots_preserved_via_exact_bone_local_frames_and_endpoints':True,'origin_and_object_hierarchy_checks':originchecks,
 'geometry_delta':0,'topology_delta':0,'UV_delta':0,'material_assignment_delta':0,'bone_delta_vs_corrected':0,'joint_delta_vs_corrected':0,
 'deform_bones':16,'TIP_helpers_nondeform':5,'all_vertices_TIP_weight_zero':not mathviol['TIP_helper'],
 'new_binding_modifier':binding,'mesh_reparented':False,'bind_method':'Armature modifier with aligned frozen spaces, origin/hierarchy unchanged; no transform apply',
 'zero_pose_deformation_evaluated':False,'Stage6_runs':0})
stat={'phase':PHASE,'Human_approval_verified':True,'proposal_bundle_hash_verified':True,'R3_authority_hash_verified':True,'corrected_rig_hash_verified':True,
 'candidate_blend_path':str(CANDIDATE),'candidate_blend_hash':sha(CANDIDATE),
 'SAFE_REUSE_expected':2401,'SAFE_REUSE_exact_copied':2401,'TARGETED_REVALIDATION_expected':771,'TARGETED_REVALIDATION_unchanged_copied':771,
 'REBUILD_REQUIRED_expected':244,'REBUILD_REQUIRED_evaluated':GEN['evaluated_count'],'actual_changed_vertex_count':len(changed),
 'outside_approved_write_count':0,'SAFE_REUSE_drift_count':0,'TARGETED_REVALIDATION_drift_count':0,
 'cap37_rebuild_count':37,'cap37_actual_changed_count':len(CAPIDS&changedset),'old_cap9_rebuild_count':9,
 'FIRST_WEB_actual_changed_count':len(WEBIDS&changedset),'edge5879_scope_applied':True,
 'v1551_changed':1551 in changedset,'v3125_changed':3125 in changedset,
 'weight_sum_violations':len(mathviol['weight_sum']),'negative_weight_violations':len(mathviol['negative_weight']),
 'NaN_Inf_violations':len(mathviol['NaN_Inf']),'influence_count_violations':len(mathviol['influence_count']),
 'TIP_helper_influence_violations':len(mathviol['TIP_helper']),'illegal_cross_digit_leakage_violations':len(leaks),
 'illegal_cross_digit_leakage_above_1e6':sum(x['maximum_forbidden_weight']>1e-6 for x in leaks),'new_illegal_leakage_violations':0,
 'FIRST_WEB_THUMB_IP_violations':len(web_ip),'continuity_static_blocker_count':len(blockers),
 'geometry_delta':0,'topology_delta':0,'bone_joint_delta_vs_corrected_rig':0,'save_reopen_verified':True,
 'candidate_verdict':'FAIL_CLOSED_REBUILD_OR_STATIC_INTEGRITY','candidate_static_pass':False,'candidate_deformation_pass':False,
 'historical_blend_writes':0,'candidate_blend_writes':1,'Stage6_runs':0,'pose_deformation_runs':0,'R3_reruns':0,
 'strict_bound_recomputations':0,'production_promotion':False,'write_scope_expanded':False,
 'NEXT':'NONE_FAIL_CLOSED_STATIC_GATE_RECONCILIATION_REQUIRED','STOP':True}
dump('TARGETED_RIG_AND_SKIN_DATA_REBUILD_AFTER_APPROVAL_R1_STATUS.json',stat)
print(json.dumps({k:stat[k] for k in ['actual_changed_vertex_count','illegal_cross_digit_leakage_violations','continuity_static_blocker_count','candidate_verdict','NEXT','STOP']},indent=2))
