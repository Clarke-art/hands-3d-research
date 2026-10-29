"""Bound-only evaluation. Executes function ASTs, never legacy module bodies/suites.
Writes only this new output directory. No weights/geometry/rest-bone edits or blend save.
"""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy, math, heapq
from types import SimpleNamespace
from mathutils import Vector, Quaternion
run=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'RUN_A'
assert run in ['RUN_A','RUN_B']
gate=read(OUT/'PREREQUISITE_GATE_R1.json')
assert all(gate['checks'].values())
method=read(OUT/'HISTORICAL_TRUE_CAP_BOUND_METHOD_RECOVERY.json')
assert method['HISTORICAL_METHOD_RECOVERED'] and not method['unresolved']
authority=read(OUT/'CORRECTED_TRUE_CAP_SOURCE_TARGET_AUTHORITY.json')
cap=read(CAP_PATH);fresh=read(R3_PATH)
source=authority['source']['vertex_ids'];target=authority['target']['vertex_ids']
alltarget=authority['target']['all_exact_boundary_endpoints']
labels={int(k):v for k,v in fresh['membership']['vertex_labels'].items()}
web=set(fresh['FIRST_WEB21']['membership_vertex_ids'])
assert not(set(source)&set(fresh['old_cap9']['vertex_ids']))
bpy.ops.wm.open_mainfile(filepath=str(CAND),load_ui=False,use_scripts=False)
ob=bpy.data.objects['Hand  - Realistic'];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
ns={'bpy':bpy}
extract_reuse=reuse(S5/'targeted_rig_and_skin_data_rebuild_after_approval_r1/blender_extract.py',['mesh_payload','rig_payload','weights'],ns)
saved=read(CAND.parent/'R2_CANDIDATE_CLEAN_REOPEN_PAYLOAD.json')
before={'mesh':ns['mesh_payload'](ob),'rig':ns['rig_payload'](rig),'weights':ns['weights'](ob),'group_order':[g.name for g in ob.vertex_groups]}
livechecks={k:before[k]==saved[k] for k in before}
livechecks['weight_hash']=digest(before['weights'])==EXPECTED_WEIGHTS
bpy.ops.wm.open_mainfile(filepath=str(CORRECTED),load_ui=False,use_scripts=False)
livechecks['corrected_all21bones']=ns['rig_payload'](bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'])==before['rig']
assert all(livechecks.values()),livechecks
bpy.ops.wm.open_mainfile(filepath=str(CAND),load_ui=False,use_scripts=False)
ob=bpy.data.objects['Hand  - Realistic'];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
MW=ob.matrix_world.copy()
V0=[(<REDACTED_EMAIL>).copy() for v in ob.data.vertices]
EDGES=[tuple(e.vertices) for e in ob.data.edges]
POLY=[tuple(p.vertices) for p in ob.data.polygons]
MM=1000.
BIND=[(V0[a]-V0[b]).length*MM for a,b in EDGES]
assert all(x>0 for x in BIND)
ADJ={i:[] for i in range(len(V0))}
for a,b in EDGES: ADJ[a].append(b);ADJ[b].append(a)
ADJ={k:sorted(v) for k,v in ADJ.items()}
EDGE_INDEX={tuple(sorted(e)):i for i,e in enumerate(EDGES)}
assert len(EDGE_INDEX)==len(EDGES)
for edge in fresh['boundary']['edge_records']:
 assert sorted(EDGES[edge['edge_id']])==sorted(edge['vertex_ids'])
 assert [labels[v] for v in edge['vertex_ids']]==edge['labels']
C=SimpleNamespace()
reuse_ns={'bpy':bpy,'math':math,'MM':MM}
primitives=reuse(S5/'stage5b_r1e/scripts/s5b_r1e_common.py',['reset_pose','set_joint_rotation','update','evaluate','arc_of'],reuse_ns)
for name in ['reset_pose','set_joint_rotation','update','evaluate','arc_of']:setattr(C,name,reuse_ns[name])
CM6B={c['case_id']:c for c in read(S6/'stage6b/STAGE6B_CASE_MATRIX.json')['cases']}
pose_ns={'C':C,'CM6B':CM6B,'Quaternion':Quaternion,'Vector':Vector,'math':math}
pose_reuse=reuse(S5/'stage5b_r1e/scripts/s5b_r1e_prequal.py',['set_s6a','set_s6b'],pose_ns)
C.reset_pose(rig);C.update()
# Historical semantic function is preserved as a descriptive proxy, with corrected
# chain/cap/fresh bounded labels. No global ownership labels are invented.
LIVE={}
for digit,chain in {'THUMB':['THUMB_CMC_R','THUMB_MCP_R','THUMB_IP_R'],'INDEX':['INDEX_MCP_R','INDEX_PIP_R','INDEX_DIP_R']}.items():
 LIVE[digit]=[<REDACTED_EMAIL>[chain[0]].head_local]+[<REDACTED_EMAIL>[b].tail_local for b in chain]
arcs={d:[C.arc_of(chain,v) for v in V0] for d,chain in LIVE.items()}
XIJ={d:[0.] for d in LIVE}
for d,chain in LIVE.items():
 for i in range(len(chain)-1):XIJ[d].append(XIJ[d][-1]+(chain[i+1]-chain[i]).length*MM)
sT=[x[0] for x in arcs['THUMB']];dT=[x[1] for x in arcs['THUMB']]
sI=[x[0] for x in arcs['INDEX']]
s_MCP_T,s_IP_T=XIJ['THUMB'][1:3];s_PIP_I=XIJ['INDEX'][2]
MED=sorted(BIND)[len(BIND)//2]
tubeT=sorted(dT[v] for v,l in labels.items() if l=='THUMB' and s_MCP_T<=sT[v]<=s_IP_T)
baseT=sorted(dT[v] for v,l in labels.items() if l=='THUMB' and sT[v]<=s_MCP_T)
assert tubeT and baseT
R_TT_T=tubeT[len(tubeT)//2]
R_MAX_T=max(baseT[int(.95*(len(baseT)-1))],R_TT_T*1.25)
def semantic(v):
 if v in set(source):return 'DISTAL_CAP'
 if v in web:return 'FIRST_WEB'
 if labels.get(v)=='THUMB':
  if sT[v]>=s_IP_T-MED:return 'THUMB_DISTAL'
  if sT[v]>=s_MCP_T-MED:return 'THUMB_MCP_TRANSITION'
  return 'THUMB_CMC_TRANSITION' if dT[v]<=R_MAX_T else 'THENAR'
 if labels.get(v)=='INDEX':return 'INDEX_ROOT' if sI[v]<=s_PIP_I else 'INDEX_PHALANX'
 return 'OUTSIDE_BOUNDED_DOMAIN_UNASSIGNED'
SEM=[semantic(v) for v in range(len(V0))]
path_ns={'heapq':heapq,'ADJ':ADJ,'V0':V0,'MM':MM}
path_reuse=reuse(FEAS/'scripts/feas_audit.py',['dijkstra_with_pred','path_between'],path_ns)
def record(a,b,dist,pred):
 seq=path_ns['path_between'](pred,a,b);assert seq and seq[0]==a and seq[-1]==b
 eids=[EDGE_INDEX[tuple(sorted((u,v)))] for u,v in zip(seq,seq[1:])]
 lens=[BIND[e] for e in eids];length=sum(lens)
 assert math.isclose(length,dist[b],rel_tol=0.,abs_tol=1e-12),(a,b,length,dist[b])
 unknown=any(v not in labels for v in seq)
 return {'source_vertex':a,'target_vertex':b,'target_class':'INDEX_SIDE_EXACT_FRESH_R3_BOUNDARY' if b in target else 'THUMB_SIDE_EXACT_FRESH_R3_BOUNDARY_CONTEXT_ONLY',
 'vertex_sequence':seq,'edge_id_sequence':eids,'individual_edge_lengths_mm':lens,
 'total_path_length_mm':length,'Dijkstra_accumulated_distance_mm':dist[b],'path_sum_minus_Dijkstra_mm':length-dist[b],'semantic_region_sequence':[SEM[v] for v in seq],
 'semantic_label_role':'Corrected historical chain/ownership descriptive proxy, not new anatomy authority',
 'fresh_R3_ownership_sequence':[labels.get(v,'UNASSIGNED_OUTSIDE_BOUNDED_DOMAIN') for v in seq],
 'passes_through':{'cap37':any(v in source for v in seq),'thumb_distal':any(SEM[v]=='THUMB_DISTAL' for v in seq),'thumb_MCP_transition':any(SEM[v]=='THUMB_MCP_TRANSITION' for v in seq),'CMC_transition':any(SEM[v]=='THUMB_CMC_TRANSITION' for v in seq),'first_web':any(v in web for v in seq),'collar':any(v in alltarget for v in seq),'palm':None if unknown else False},
 'palm_membership_note':'No full palm map is approved by bounded fresh-R3. Null means unknown on any unassigned route vertex; no invented global wrist/palm labels.'}
allpaths=[]
for a in source:
 dist,pred=path_ns['dijkstra_with_pred']([a])
 for b in alltarget:allpaths.append(record(a,b,dist,pred))
primary=[p for p in allpaths if p['target_vertex'] in target]
primary.sort(key=lambda p:(p['total_path_length_mm'],p['source_vertex'],p['target_vertex']))
allpaths.sort(key=lambda p:(p['source_vertex'],p['target_vertex']))
assert len(primary)==len(source)*len(target)==703
lengths=sorted(p['total_path_length_mm'] for p in primary)
stats={'count':len(lengths),'min':lengths[0],'p05':lengths[int(.05*(len(lengths)-1))],'median':lengths[len(lengths)//2],'p95':lengths[int(.95*(len(lengths)-1))],'max':lengths[-1],'mean':sum(lengths)/len(lengths)}
graph_payload={'vertices_world_m':[list(v) for v in V0],'edges':[list(e) for e in EDGES],'metric':'WORLD_BIND_MESH_EDGE_LENGTH_MM','edge_lengths_mm':BIND}
static={'scope':'PRIMARY_CAP37_X_INDEX_SIDE_EXACT_FRESH_R3_BOUNDARY','source_count':len(source),'target_count':len(target),'source_set_hash':digest(source),'target_set_hash':digest(target),'graph_metric_hash':digest(graph_payload),'statistics_mm':stats,'paths':primary,'ten_shortest_distinct_endpoint_pairs':primary[:10],'global_shortest_path':primary[0],
 'all_exact_boundary_context_pair_count':len(allpaths),'all_exact_boundary_context_paths':allpaths,
 'path_tie_rule':'Historical strict relaxation du+w < stored-1e-16; stale queue cutoff +1e-15. Ascending numeric source IDs, target IDs and adjacency IDs; heap ordered (distance,vertex). Equal candidates retain first predecessor. No rounded values select paths.',
 'statistics_serialization':'All binary64 computed values serialized round-trip by Python JSON, allow_nan=false. No numerical rounding for deterministic comparison.'}
POSED={};transforms={};pose_states={}
for cid in method['bound_pose_ids']:
 if cid in ['TH_IP_30','TH_IP_45','TH_MCP_45']:
  bone='THUMB_MCP_R' if cid=='TH_MCP_45' else 'THUMB_IP_R'
  angle=45. if '45' in cid else 30.
  pose_ns['set_s6a'](rig,bone,angle)
 else:pose_ns['set_s6b'](rig,cid)
 C.update();V,P=C.evaluate(ob,MW);assert P==POLY
 POSED[cid]=V
 transforms[cid]={g:<REDACTED_EMAIL>[g]<REDACTED_EMAIL>[g].matrix_local.inverted()@rig.matrix_world.inverted() for g in ['WRIST_R','THUMB_CMC_R','THUMB_MCP_R','THUMB_IP_R','INDEX_MCP_R']}
 pose_states[cid]={b.name:{'location':list(b.location),'quaternion':list(b.rotation_quaternion),'scale':list(b.scale)} for b in rig.pose.bones}
 print(run,cid,'BOUND_RECOMPUTATION_PROBE geometry evaluated',flush=True)
def bounds_for(paths,V):
 rows=[]
 for p in paths:
  a,b=p['source_vertex'],p['target_vertex'];length=p['total_path_length_mm']
  delta=V[b]-V[a];d=delta.length*MM;ratio=d/length
  observed=max((V[EDGES[e][0]]-V[EDGES[e][1]]).length*MM/BIND[e] for e in p['edge_id_sequence'])
  assert ratio<=observed+1e-6
  rows.append({'source_vertex':a,'target_vertex':b,'bind_path_length_mm':length,'A_bind_world_m':list(V0[a]),'B_bind_world_m':list(V0[b]),'A_posed_world_m':list(V[a]),'B_posed_world_m':list(V[b]),'posed_endpoint_separation_mm':d,'strict_lower_bound':ratio,'source_displacement_mm':(V[a]-V0[a]).length*MM,'target_displacement_mm':(V[b]-V0[b]).length*MM,'observed_max_edge_ratio_on_fixed_path_context_only':observed})
 return rows
primary_by_pair={(p['source_vertex'],p['target_vertex']):p for p in primary}
topkeys={(p['source_vertex'],p['target_vertex']) for p in primary[:10]}
posed={}
for cid,V in POSED.items():
 rows=bounds_for(primary,V)
 toprows=[r for r in rows if (r['source_vertex'],r['target_vertex']) in topkeys]
 def worst(rs):return max(rs,key=lambda r:(r['strict_lower_bound'],-r['source_vertex'],-r['target_vertex']))
 posed[cid]={'probe_class':'BOUND_RECOMPUTATION_PROBE','pair_count':len(rows),'all_primary_pair_bounds':rows,'max_over_complete_703_pairs':worst(rows),'max_over_historical_semantic_top10_current_shortest_pairs':worst(toprows),'global_shortest_path_endpoint_bound':next(r for r in rows if (r['source_vertex'],r['target_vertex'])==(primary[0]['source_vertex'],primary[0]['target_vertex'])),'cap37_mean_displacement_mm':sum((V[a]-V0[a]).length*MM for a in source)/len(source),'pose_state':pose_states[cid],
 'pose_source':{'case_matrix':CM6B[cid]} if cid in CM6B else {'bone':'THUMB_MCP_R' if cid=='TH_MCP_45' else 'THUMB_IP_R','local_X_angle_deg':-45. if '45' in cid else -30.},
 'full_collar_actual_endpoint_context_max':max(bounds_for(allpaths,V),key=lambda r:r['strict_lower_bound'])}
# Recover all invalidated historical virtual recipes without assigning weights.
# Position B is algebraic LBS; source position A remains actual evaluated cap37.
samples=[]
for recipe in method['additional_numeric_families']['endpoint_sensitivity']['recipes']:
 cid=recipe['pose'];fraction=recipe['parameter_fraction'];g0=recipe['base_group'];g1=recipe['added_group']
 points={b:(1-fraction)*(transforms[cid][g0]@V0[b])+fraction*(transforms[cid][g1]@V0[b]) for b in alltarget}
 allrows=[]
 for p in allpaths:
  a,b=p['source_vertex'],p['target_vertex'];d=(POSED[cid][a]-points[b]).length*MM
  allrows.append([a,b,d,d/p['total_path_length_mm']])
 idxrows=[row for row in allrows if row[1] in target]
 samples.append({**recipe,'classification':'VIRTUAL_ENDPOINT_LBS_BOUND_RECOMPUTATION_PROBE_NOT_AUTHORITY','source_endpoint':'Actual evaluated R2 cap37, no one-hot IP substitution','pair_row_schema':['source_vertex','target_vertex','posed_endpoint_separation_mm','strict_lower_bound'],
 'all_primary_pair_bounds':idxrows,'all_exact_boundary_context_pair_bounds':allrows,'primary_pair_count':len(idxrows),'all_exact_boundary_pair_count':len(allrows),'max_primary_bound_row':max(idxrows,key=lambda r:r[3]),'max_all_exact_boundary_context_bound_row':max(allrows,key=lambda r:r[3]),'endpoint_trajectories':[{'vertex_id':b,'position_world_m':list(points[b]),'displacement_mm':(points[b]-V0[b]).length*MM} for b in alltarget]})
bound={'definition':method['mathematical_definition'],'summary_role':'Current R2 geometric/kinematic derived constraint only, no deformation verdict or biological/teaching angle limit.','per_pose':posed,'historical_endpoint_sensitivity_recomputed':samples,'sensitivity_sample_count':len(samples),'virtual_weight_assignments':0,'thresholds_or_downstream_recommendations_promoted':False}
C.reset_pose(rig);C.update()
after={'mesh':ns['mesh_payload'](ob),'rig':ns['rig_payload'](rig),'weights':ns['weights'](ob),'group_order':[g.name for g in ob.vertex_groups]}
assert before==after
assert sha(CAND)==EXPECTED_CAND and sha(CORRECTED)==EXPECTED_RIG
dump(run+'/STATIC_PATH_PAYLOAD.json',static)
dump(run+'/POSED_BOUND_PAYLOAD.json',bound)
dump(run+'/BOUND_GEOMETRY_CONTEXT.json',{'bind_world_m':[list(v) for v in V0],'posed_world_m':{k:[list(v) for v in vs] for k,vs in POSED.items()},'edges':[list(e) for e in EDGES],'faces':[list(p) for p in POLY],'semantic_proxy_labels':SEM,'fresh_labels':labels,'corrected_chains_world_m':{k:[list(v) for v in vs] for k,vs in LIVE.items()}})
dump(run+'/COMPUTATION_VERIFICATION.json',{'live_prerequisite_checks':livechecks,'static_path_payload_hash':digest(static),'bound_payload_hash':digest(bound),'source_set_hash':digest(source),'target_set_hash':digest(target),'graph_metric_hash':digest(graph_payload),'input_authority_hashes':authority['authority_hashes'],'reused_function_sources':[extract_reuse,primitives,pose_reuse,path_reuse],'zero_pose_restore_all_payload_exact':before==after,'production_hash_unchanged':sha(CAND)==EXPECTED_CAND,'production_writes':0,'skin_weight_mutations':0,'geometry_mutations':0,'rest_rig_mutations':0,'R3_solver_runs':0,'full_Stage6A_runs':0,'full_Stage6B_runs':0,'deformation_qualification_runs':0,'bound_probe_pose_count':len(POSED),'runtime':{'version':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode()},'execution':run})
print(run,'COMPLETE',json.dumps(stats),'path',digest(static),'bound',digest(bound),flush=True)
