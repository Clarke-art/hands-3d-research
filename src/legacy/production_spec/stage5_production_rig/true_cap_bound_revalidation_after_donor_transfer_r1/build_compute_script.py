"""Copy the frozen historical computation, changing only intake and adding audit outputs.
Numeric path, pose, actual-bound and virtual-recipe code remains byte-for-byte identical.
"""
import sys
sys.dont_write_bytecode=True
from common import *
original=(OLD/'compute_bound.py').read_text(encoding='utf-8-sig')
start=original.index('bpy.ops.wm.open_mainfile(filepath=str(CAND)')
end=original.index('MW=ob.matrix_world.copy()',start)
replacement='''ns={'bpy':bpy}
extract_reuse=reuse(S5/'targeted_rig_and_skin_data_rebuild_after_approval_r1/blender_extract.py',['mesh_payload','rig_payload','weights'],ns)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=str(OLD_CAND),load_ui=False,use_scripts=False)
oldob=bpy.data.objects['Hand  - Realistic'];oldrig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
saved=read(OLD_CAND.parent/'R2_CANDIDATE_CLEAN_REOPEN_PAYLOAD.json')
old_live={'mesh':ns['mesh_payload'](oldob),'rig':ns['rig_payload'](oldrig),'weights':ns['weights'](oldob),'group_order':[g.name for g in oldob.vertex_groups]}
assert all(old_live[k]==saved[k] for k in old_live)
OLD_V0=[(<REDACTED_EMAIL>).copy() for v in oldob.data.vertices]
old_raw_entries=[[[g.group,float(g.weight)] for g in v.groups] for v in oldob.data.vertices]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=str(CORRECTED),load_ui=False,use_scripts=False)
corrected_live=ns['rig_payload'](bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=str(CAND),load_ui=False,use_scripts=False)
ob=bpy.data.objects['Hand  - Realistic'];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
before={'mesh':ns['mesh_payload'](ob),'rig':ns['rig_payload'](rig),'weights':ns['weights'](ob),'group_order':[g.name for g in ob.vertex_groups]}
stored_entries_before=[[[g.group,float(g.weight)] for g in v.groups] for v in ob.data.vertices]
livechecks={'current_weight_hash':digest(before['weights'])==EXPECTED_WEIGHTS,
 'all_weight_vectors_exact_old':before['weights']==old_live['weights'],
 'all_raw_entries_and_zeros_exact_old':stored_entries_before==old_raw_entries,
 'group_order_exact_old':before['group_order']==old_live['group_order'],
 'corrected_all21bones':before['rig']==old_live['rig']==corrected_live,
 'protected_mesh_except_positions_exact_old':all(before['mesh'][k]==old_live['mesh'][k] for k in before['mesh'] if k not in ['positions_local_m','positions_world_mm']),
 'current_asset_SHA256':sha(CAND)==EXPECTED_CAND,'old_R2_SHA256':sha(OLD_CAND)==EXPECTED_OLD,'corrected_rig_SHA256':sha(CORRECTED)==EXPECTED_RIG}
assert all(livechecks.values()),livechecks
'''
script=original[:start]+replacement+original[end:]
needle="allpaths=[]\nfor a in source:"
insert='''# Supplemental predecessor-choice audit never changes the historical relaxation rule.
def tie_status(seq,dist,coordinates):
 choices=[]
 for v in seq[1:]:
  equal=[u for u in ADJ[v] if u in dist and abs(dist[u]+(coordinates[u]-coordinates[v]).length*MM-dist[v])<=1e-16]
  if len(equal)>1:choices.append({'vertex_id':v,'equivalent_predecessors':equal})
 return {'status':'RELAXATION_EQUIVALENT_MULTIPLE_PREDECESSORS' if choices else 'NO_RELAXATION_EQUIVALENT_MULTIPLE_PREDECESSOR_ON_SELECTED_PATH',
         'tie_vertices':choices,'tolerance_mm':1e-16,'selected_predecessor_rule':'Frozen first strict-relaxation winner; audit does not select a different path.'}
old_ns={'heapq':heapq,'ADJ':ADJ,'V0':OLD_V0,'MM':MM}
old_path_reuse=reuse(FEAS/'scripts/feas_audit.py',['dijkstra_with_pred','path_between'],old_ns)
OLD_BIND=[(OLD_V0[a]-OLD_V0[b]).length*MM for a,b in EDGES]
old_graph={'vertices_world_m':[list(v) for v in OLD_V0],'edges':[list(e) for e in EDGES],'metric':'WORLD_BIND_MESH_EDGE_LENGTH_MM','edge_lengths_mm':OLD_BIND}
assert digest(old_graph)==EXPECTED_OLD_GRAPH
old_saved_paths={(p['source_vertex'],p['target_vertex']):p for p in read(OLD/'RUN_A/STATIC_PATH_PAYLOAD.json')['all_exact_boundary_context_paths']}
old_ties={};current_ties={}
for a in source:
 old_dist,old_pred=old_ns['dijkstra_with_pred']([a])
 for b in alltarget:
  seq=old_ns['path_between'](old_pred,a,b)
  savedpath=old_saved_paths[(a,b)]
  eids=[EDGE_INDEX[tuple(sorted((u,v)))] for u,v in zip(seq,seq[1:])]
  assert seq==savedpath['vertex_sequence'] and eids==savedpath['edge_id_sequence']
  assert sum(OLD_BIND[e] for e in eids)==savedpath['total_path_length_mm']
  old_ties[(a,b)]=tie_status(seq,old_dist,OLD_V0)
allpaths=[]
for a in source:'''
assert script.count(needle)==1
script=script.replace(needle,insert)
needle="for b in alltarget:allpaths.append(record(a,b,dist,pred))"
replacement="""for b in alltarget:
  p=record(a,b,dist,pred)
  current_ties[(a,b)]=tie_status(p['vertex_sequence'],dist,V0)
  allpaths.append(p)"""
assert script.count(needle)==1;script=script.replace(needle,replacement)
needle="assert before==after"
script=script.replace(needle,"assert before==after\nassert stored_entries_before==[[[g.group,float(g.weight)] for g in v.groups] for v in ob.data.vertices]")
needle="dump(run+'/STATIC_PATH_PAYLOAD.json',static)"
insert="""dump(run+'/GRAPH_METRIC_PAYLOAD.json',graph_payload)
dump(run+'/OLD_GRAPH_METRIC_REPLAY_PAYLOAD.json',old_graph)
dump(run+'/SOURCE_TARGET_LIVE_COORDINATES.json',{'source_ids':source,'target_ids':target,'context_ids':alltarget,
 'old_world_m':{str(v):list(OLD_V0[v]) for v in sorted(set(source)|set(alltarget))},
 'current_world_m':{str(v):list(V0[v]) for v in sorted(set(source)|set(alltarget))},
 'old_local_m':{str(v):old_live['mesh']['positions_local_m'][v] for v in sorted(set(source)|set(alltarget))},
 'current_local_m':{str(v):before['mesh']['positions_local_m'][v] for v in sorted(set(source)|set(alltarget))}})
dump(run+'/PATH_TIE_AUDIT.json',{'classification':'SUPPLEMENTAL_NON_MUTATING_DIAGNOSTIC',
 'old_bind_graph_replay_matches_all1406_historical_paths':True,
 'records':[{'source_vertex':a,'target_vertex':b,'old_tie_status':old_ties[(a,b)],'current_tie_status':current_ties[(a,b)]} for a in source for b in alltarget]})
dump(run+'/STATIC_PATH_PAYLOAD.json',static)"""
assert script.count(needle)==1;script=script.replace(needle,insert)
(OUT/'compute_bound.py').write_text(script,encoding='utf-8')
# Verify the complete original numeric sections were retained exactly.
sections={
 'graph_build':('MW=ob.matrix_world.copy()','POSED={};transforms={};pose_states={}'),
 'pose_and_bounds_and_120_recipes':('POSED={};transforms={};pose_states={}',"C.reset_pose(rig);C.update()\nafter="),
}
checks={}
for name,(a,b) in sections.items():
 old_section=original[original.index(a):original.index(b)]
 current_section=script[script.index(a):script.index(b)]
 # Graph section includes added tie diagnostics and expanded append, so verify numeric
 # graph/metric and historic record()/sorting/statistic substrings separately.
 if name=='pose_and_bounds_and_120_recipes':checks[name]=old_section==current_section
checks['original_graph_metric_build']=original[original.index('MW=ob.matrix_world.copy()'):original.index('C=SimpleNamespace()')]==script[script.index('MW=ob.matrix_world.copy()'):script.index('C=SimpleNamespace()')]
checks['original_path_record_definition']=original[original.index('def record('):original.index('allpaths=[]')]==script[script.index('def record('):script.index('# Supplemental predecessor-choice audit')]
checks['original_sort_statistics_and_graph_hash']=original[original.index('primary=[p for p in allpaths'):original.index('POSED={};transforms={};pose_states={}')]==script[script.index('primary=[p for p in allpaths'):script.index('POSED={};transforms={};pose_states={}')]
dump('METHOD_IMPLEMENTATION_REUSE_VERIFICATION_R1.json',{'status':'PASS' if all(checks.values()) else 'FAIL_CLOSED_TRUE_CAP_METHOD_INCOMPATIBILITY','checks':checks,
 'frozen_historical_source':ref(OLD/'compute_bound.py'),'current_implementation':ref(OUT/'compute_bound.py'),'changes':'Current-vs-old clean intake; non-mutating tie diagnostic and graph/endpoint exports only. Numeric pose/actual bounds/120 recipes unchanged.'})
assert all(checks.values()),checks
print('FROZEN NUMERIC METHOD SECTIONS EXACTLY RETAINED',flush=True)
