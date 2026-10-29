import sys
sys.dont_write_bytecode=True
from common import *
import numpy as np
N=read(OUT/'CURRENT_STAGE4C_NATIVE_SNAPSHOT_R1.json');S=read(OUT/'INDEPENDENT_DONOR_HISTORICAL_NATIVE_INPUTS_R1.json')['stages'];H=read(SOURCE/'HISTORICAL_OPERATION_RAM_REPLAY.json');A=H['final_ancestry'];J=np.array(read(SOURCE/'HISTORICAL_RSSF_COORDINATE_CORRESPONDENCE.json')['per_vertex_linear_part']);current=np.array(N['coordinates_world_m']);rest=np.array(S['STAGE4A_R2']['canonical_world_m']);don=np.array(S['OFFICIAL_L1']['canonical_world_m']);historical_current=np.array(read(SOURCE/'RAW_SOURCE_GEOMETRY.json')['stages']['STAGE4C_R2']['canonical_world_m'])
F=[p[1] for p in N['protected']['mesh']['faces']];E=[e[1] for e in N['protected']['mesh']['edges']]
core=read(FEAS/'PALMAR_ROOT_DEFECT_CORE_R1.json');normal=read(FEAS/'PALMAR_ROOT_EXCLUDED_NORMAL_CONTEXT_R1.json');lock=read(FEAS/'PALMAR_ROOT_HUMAN_TARGET_LOCK_R1.json')
lookup={}
for i,p in enumerate(S['STAGE4A_R2_BASE']['local_m']):lookup.setdefault(tuple(p),[]).append(i)
mapping={};independent_targets={};rest_targets={}
for i,p in enumerate(S['STAGE4A_R2']['local_m']):
 match=lookup.get(tuple(p),[])
 if len(match)!=1:continue
 bi=match[0];a=A[bi];assert abs(sum(a.values())-1)<1e-12
 q=sum((don[int(k)]*w for k,w in a.items()),np.zeros(3));mapping[i]=(bi,a);rest_targets[i]=q
 # Remote eligibility uses the incremental residual so already restored dorsal54 is never applied twice.
 independent_targets[i]=historical_current[i]+J[i]@(q-rest[i])
eligible={i for i,q in independent_targets.items() if np.linalg.norm(q-current[i])*1000>.0001}
adj=[set() for _ in current]
for a,b in E:adj[a].add(b);adj[b].add(a)
remain=set(eligible);components=[]
while remain:
 todo=[remain.pop()];c=set(todo)
 while todo:
  v=todo.pop();extra=adj[v]&remain;remain-=extra;c|=extra;todo.extend(extra)
 components.append(c)
selected=set().union(*(c for c in components if c&set(core['vertex_ids'])))
while selected:
 parents={int(k) for i in selected for k in mapping[i][1]};extra={i for i in eligible if set(map(int,mapping[i][1]))&parents}-selected
 if not extra:break
 selected|=extra
ids=sorted(selected);assert ids==ALLOWED,'FAIL_CLOSED_FORMAL_RESTORATION_REPRODUCTION: write set mismatch'
assert not selected&set(normal['vertex_ids'])
event=next(e for e in H['events'] if {v['vertex_id'] for v in e['new_vertices']}==selected)
assert event['label']=='CON1_MIDDLE_MCP@-1mm'
donedges={tuple(sorted(e)) for e in S['OFFICIAL_L1']['edges']}
rows=[];target=current.copy()
for i in ids:
 bi,a=mapping[i];witness=next(v for v in event['new_vertices'] if v['vertex_id']==bi)
 assert a==witness['L1_ancestry'];assert len(a)==2 and tuple(sorted(map(int,a))) in donedges
 assert np.array_equal(current[i],historical_current[i]),'palmar point already corrected; do not double restore'
 q=rest_targets[i];t=current[i]+J[i]@(q-rest[i]);target[i]=t
 rows.append({'vertex_id':i,'historical_base_vertex_id':bi,'L1_parent_weights':a,'historical_split_parent_witness':witness,'current_world_m':current[i].tolist(),'historical_engineered_rest_world_m':rest[i].tolist(),'donor_ancestry_rest_world_m':q.tolist(),'frozen_RSSF_linear_J':J[i].tolist(),'formal_target_world_m':t.tolist(),'delta_mm':((t-current[i])*1000).tolist(),'preexisting_dorsal_correction_at_this_vertex_mm':((current[i]-historical_current[i])*1000).tolist()})
# Probe is first read here, after all independent IDs and mathematical targets have been computed.
P=read(FEAS/'TEMP_PALMAR_ROOT_DONOR_TRANSFER_PROBE_R1.json');scope=read(FEAS/'PALMAR_ROOT_TRANSFER_SCOPE_R1.json')
assert P['moved_vertex_ids']==ids;assert np.array_equal(np.array(P['baseline_world_mm']),current*1000)
delta=np.linalg.norm(target[ids]*1000-np.array(P['world_mm'])[ids],axis=1);assert delta.max()<.0002,'FAIL_CLOSED_FORMAL_RESTORATION_REPRODUCTION: target diverges beyond native serialization witness'
dump('PALMAR_ROOT_FORMAL_WRITE_SET_R1.json',{'vertex_ids':ids,'APPROVED_FUTURE_WRITE_SET_COUNT':16,'human_approval_granted':False,'RECOMPUTED_WRITE_SET_COUNT':len(ids),'PROBE_WRITE_SET_COUNT':len(P['moved_vertex_ids']),'WRITE_SET_IDENTITY_MATCH_VS_PROBE':True,'core_write_ids':sorted(selected&set(core['vertex_ids'])),'ancestry_closure_ids':sorted(selected-set(core['vertex_ids'])),'transition_context_ids':[],'normal_locked_vertex_ids':normal['vertex_ids'],'independent_selection':'Nonzero source-shape residual components seeded by locked core, then exact ancestry closure; allowed scope assertion3348-3363; no mechanical neighborhood expansion','historical_event':event['label'],'all16_unmodified_by_previous_dorsal54':True})
dump('PALMAR_ROOT_FORMAL_TARGET_COORDINATES_R1.json',{'formula':'current_Stage4C + frozen_RSSF_J * (official_donor_ancestry_rest - historical_Stage4A_engineered_rest)','source_local_m':N['coordinates_local_m'],'source_world_mm':current*1000,'mathematical_target_world_mm':target*1000,'candidate_world_mm':target*1000,'faces':F,'edges':E,'vertex_ids':ids,'per_vertex':rows,'recomputed_before_probe_access':True,'mathematical_target_vs_saved_probe_max_mm':float(delta.max()),'serialization_equivalence_bound_mm':.0002,'free_optimization':False})
dump('PALMAR_ROOT_FORMAL_PROVENANCE_R1.json',{'status':'PASS','canonical_donor':'OFFICIAL_HAND_REALISTIC_MULTIRES_L1','donor_source':S['OFFICIAL_L1']['input'],'current_Stage4C_source':ref(CURRENT),'Stage2_equivalence_witness':S['STAGE2_L1']['input'],'independent_actual_L1_evaluation':ref(OUT/'INDEPENDENT_DONOR_HISTORICAL_NATIVE_INPUTS_R1.json'),'historical_ancestry':ref(SOURCE/'HISTORICAL_OPERATION_RAM_REPLAY.json'),'historical_graph_validation':read(SOURCE/'DONOR_TO_CURRENT_TOPOLOGY_CORRESPONDENCE_R1.json')['multires_graph_validation'],'RSSF_authority':ref(SOURCE/'HISTORICAL_RSSF_COORDINATE_CORRESPONDENCE.json'),'RSSF_authority_changed':False,'method':['EXACT_SUBDIVISION_GRAPH_ANCESTRY','HISTORICAL_SPLIT_EDGE_PARENTAGE','historical_parent_interpolation_weights','frozen_RSSF_per_vertex_linear_J'],'exact_unique_current_to_base_identity':True,'parent_edges_native_official_L1_verified':True,'donor_to_Stage2_exact':True,'target_authority_is_probe':False,'probe_read_purpose':'comparison after independent recomputation only','historical_pre_donor_assets':'ancestry/RSSF witnesses only; never application source','request':ref(REQUEST)})
dump('PALMAR_ROOT_HUMAN_TARGET_LOCK_R1.json',lock)
dump('PALMAR_ROOT_DEFECT_CORE_R1.json',core);dump('PALMAR_ROOT_EXCLUDED_NORMAL_CONTEXT_R1.json',normal)
print('Independent recompute16/16; math-to-saved-probe max',delta.max(),'mm; source current Stage4C',flush=True)
