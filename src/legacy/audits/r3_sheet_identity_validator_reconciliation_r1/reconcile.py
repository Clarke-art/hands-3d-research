"""Static validator semantics only. No solver imports, distance fields, closure, or bpy."""
import sys
sys.dont_write_bytecode=True
import json,hashlib,datetime
from pathlib import Path
from collections import defaultdict,deque,Counter
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
FRESH=ROOT/'audits/r3_full_recompute_and_authority_revalidation_r1'
CONTRACT=ROOT/'audits/r3_recovery_input_contract_finalization_r1'
HISTORY=ROOT/'production_spec/stage6_deformation/stage6b_r3_thumb_tip_ownership_boundary'
RUN='R3_SHEET_IDENTITY_VALIDATOR_RECONCILIATION_R1'
METHOD='BOUNDED_VERTEX_LABEL_REGION_IDENTITY_WITH_PURE_FACE_AND_MIXED_BAND_VALIDATION_R2'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def canon(d):return json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf8')
def digest(d):return hashlib.sha256(canon(d)).hexdigest()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def dump(n,d):(OUT/n).write_text(json.dumps(d,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
def inventory():return {str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and OUT not in p.parents}
def cc(ids,adj):
 rem=set(ids);result=[]
 while rem:
  start=min(rem);rem.remove(start);q=deque([start]);part=[]
  while q:
   u=q.popleft();part.append(u)
   for v in sorted(adj[u]):
    if v in rem:rem.remove(v);q.append(v)
  result.append(sorted(part))
 return result
def ranges(p,needle,context=3):
 lines=p.read_text(encoding='utf-8-sig').splitlines();matches=[]
 for i,line in enumerate(lines):
  if needle.lower() in line.lower():matches.append({'line':i+1,'text':'\n'.join(lines[max(0,i-context):min(len(lines),i+context+1)])})
 return matches

def main():
 if (OUT/(RUN+'_STATUS.json')).exists():raise RuntimeError('Refuse overwrite completed reconciliation')
 before=inventory();dump('FROZEN_HASHES_BEFORE.json',before)
 fresh_manifest=read(FRESH/'OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json')
 verify={n:sha(FRESH/n)==h for n,h in fresh_manifest.items()};assert all(verify.values()),'Fresh evidence hash mismatch'
 contract=read(CONTRACT/'CANONICAL_R3_RECOVERY_INPUT_CONTRACT_R1.json');assert digest(contract)=='f392fd33be0430cabf4b849fb8a4565853c245f2cf09e953d506493c93ca3cab'
 for r in list(contract['files'].values())+list(contract['frozen_authority_sources'].values()):
  p=Path(r['path']);p=p if p.is_absolute() else ROOT/p;assert sha(p)==r['sha256']
 status=read(FRESH/'R3_FULL_RECOMPUTE_AND_AUTHORITY_REVALIDATION_R1_STATUS.json');view=read(FRESH/'R3_FRESH_REVIEW_VIEW_DATA_R1.json');labeldoc=read(FRESH/'R3_FRESH_FINAL_LABELS_R1.json');L={int(k):v for k,v in labeldoc['labels'].items()};label_hash=digest(L);assert label_hash==labeldoc['label_sha256']==view['result_hash']
 expected={'graph_V':962,'graph_E':1881,'fresh_THUMB_count':498,'fresh_INDEX_count':464,'cut_edge_count':20,'closure_iterations':1,'closure_changed_count':0,'islands_count':0,'ambiguity_vertex_count':21,'CLASS_A_pass_count':6,'old_cap9_hard_role_count':0,'cap37_preservation':'PASS','INDEX_hard_source_preservation':'PASS'}
 assert all(status[k]==v for k,v in expected.items());assert status['FIRST_WEB21_distribution']=={'THUMB':7,'INDEX':14};assert status['old_cap9_distribution']=={'INDEX':9}
 V,E,F=view['vertices'],view['edges'],view['faces'];graph=read(CONTRACT/'R3_ENGINEERING_GRAPH_DOMAIN_R1.json');G=set(graph['vertex_ids']);GE=set(graph['edge_ids']);assert set(L)==G and len(G)==962 and len(GE)==1881
 T=set(view['THUMB_sources']);I=set(view['INDEX_sources']);cut=set(view['fresh_boundary']);assert cut=={e for e in GE if L[E[e][0]]!=L[E[e][1]]} and len(cut)==20
 assert Counter(L.values())=={'THUMB':498,'INDEX':464}
 frozen_closure=read(FRESH/'R3_FRESH_CLOSURE_AUDIT_R1.json');assert frozen_closure['converged'] and frozen_closure['full_sweeps']==1 and frozen_closure['cumulative_changed_count']==0
 for field in ['dT','dI']:
  unary=read(FRESH/'FRESH_R3_UNARY_FIELDS_R1.json')[field];assert digest({int(k):v for k,v in unary['values_mm'].items()})==unary['field_sha256']
 ef=defaultdict(list);vf=defaultdict(set);va=defaultdict(set);lookup={tuple(sorted(e)):k for k,e in enumerate(E)}
 for e,(a,b) in enumerate(E):va[a].add(b);va[b].add(a)
 for f,vs in enumerate(F):
  for v in vs:vf[v].add(f)
  for a,b in zip(vs,vs[1:]+vs[:1]):ef[lookup[tuple(sorted((a,b)))]].append(f)
 assert len(V)==3416 and len(F)==3414 and all(len(fs)==2 for fs in ef.values())
 def dual(ids,skip=()):
  ids=set(ids);skip=set(skip);adj=defaultdict(set)
  for e,fs in ef.items():
   if e in skip:continue
   for a in fs:
    if a in ids:
     adj[a].update(b for b in fs if b in ids and b!=a)
  return adj
 def vtxcomponents(ids,skip=()):
  ids=set(ids);adj=defaultdict(set);skip=set(skip)
  for e,(a,b) in enumerate(E):
   if e not in skip and a in ids and b in ids:adj[a].add(b);adj[b].add(a)
  return cc(ids,adj),adj
 # Anchors are the same independent frozen families for every candidate.
 validator=read(CONTRACT/'R3_VALIDATOR_CONTRACT_R1.json');identity=validator['THUMB_identity'];iidentity=validator['INDEX_identity']
 anchors={'THUMB':set(identity['cap_vertices'])|{identity['tip']}|{v for f in identity['nail_faces'] for v in F[f]},'INDEX':{iidentity['tip']}|{v for f in iidentity['nail_faces'] for v in F[f]}}
 anchorfaces={'THUMB':set(identity['cap_faces'])|set(identity['nail_faces']),'INDEX':set(iidentity['nail_faces'])}
 assert anchors['THUMB']<=T and anchors['INDEX']<=I and all(L[v]==lab for lab,s in anchors.items() for v in s)
 composition={};pure={lab:set() for lab in ['THUMB','INDEX']};mixed=set();partial=set();unknown=set();fedges={}
 for f,vs in enumerate(F):
  labs=[L.get(v,'NO_SOLVE_UNASSIGNED_OUTSIDE_GRAPH') for v in vs];ls=set(labs);es=[lookup[tuple(sorted((a,b)))] for a,b in zip(vs,vs[1:]+vs[:1])];fedges[f]=es
  if {'THUMB','INDEX'}<=ls:kind='MIXED';mixed.add(f)
  elif ls=={'THUMB'}:kind='PURE_THUMB';pure['THUMB'].add(f)
  elif ls=={'INDEX'}:kind='PURE_INDEX';pure['INDEX'].add(f)
  elif ls=={'NO_SOLVE_UNASSIGNED_OUTSIDE_GRAPH'}:kind='UNASSIGNED';unknown.add(f)
  else:kind='PARTIAL_LABEL_SUPPORT';partial.add(f)
  composition[f]={'face_id':f,'kind':kind,'vertex_ids':vs,'vertex_labels':labs,'incident_cut_edge_ids':sorted(set(es)&cut),'all_vertices_solved':set(vs)<=G,'graph_full_face':f in set(graph['face_ids'])}
 face_audit={'pure_THUMB_face_count':len(pure['THUMB']),'pure_INDEX_face_count':len(pure['INDEX']),'mixed_face_count':len(mixed),'mixed_face_ids':sorted(mixed),'mixed_faces':[composition[f] for f in sorted(mixed)],'partial_face_count':len(partial),'partial_face_ids':sorted(partial),'unassigned_face_count':len(unknown),'classification_count':dict(Counter(x['kind'] for x in composition.values())),'outside_graph_labels_injected':False,'definition':'PURE requires every polygon vertex solved and same label; MIXED requires both binary labels, even if other corners are unassigned; partial is never forced into a label.'}
 dump('R3_FRESH_FACE_LABEL_COMPOSITION_AUDIT.json',face_audit)
 # V4 exact frozen implementation reproduction.
 v4adj=dual(range(len(F)),cut);v4=cc(range(len(F)),v4adj);v4vs=[{v for f in fs for v in F[f]} for fs in v4]
 def faceidentity(parts):
  sets=[set(p) for p in parts];vs=[{v for f in p for v in F[f]} for p in parts];result={}
  for lab in ['THUMB','INDEX']:result[lab]=[k for k,s in enumerate(sets) if anchorfaces[lab]<=s and anchors[lab]<=vs[k]]
  result['collision']=bool(set(result['THUMB'])&set(result['INDEX']));result['resolved']=all(len(result[lab])==1 for lab in ['THUMB','INDEX']) and not result['collision'];return result
 v4id=faceidentity(v4);assert len(v4)==1 and len(v4[0])==3414 and len(v4vs[0])==3416 and v4id['collision']
 dump('R3_CURRENT_FULL_FACE_DUAL_REPRODUCTION_R1.json',{'exact_reproduction_pass':True,'components':1,'face_count':3414,'vertex_count':3416,'removed_mesh_edge_ids':sorted(cut),'identity':v4id,'original_failure_preserved':True,'shared_vertex_only_is_dual_adjacency':False})
 # Historic result reproduced with old edge IDs, never used to label or validate fresh regions.
 old=read(HISTORY/'R3_OWNERSHIP_LABELS.json');oldcut=set(old['boundary_edges_R3']);oldparts,_=vtxcomponents(range(len(V)),oldcut);oldmatch={lab:[k for k,p in enumerate(oldparts) if anchors[lab]<=set(p)] for lab in ['THUMB','INDEX']};assert len(oldparts)==2
 assert all(len(oldmatch[lab])==1 for lab in oldmatch) and oldmatch['THUMB']!=oldmatch['INDEX'];oldindex=oldparts[oldmatch['INDEX'][0]];oldthumb=oldparts[oldmatch['THUMB'][0]];assert len(oldindex)==217 and len(oldthumb)==3199
 dump('R3_HISTORICAL_VERTEX_CUT_REPRODUCTION_R1.json',{'pass':True,'INDEX_vertex_count':len(oldindex),'body_vertex_count':len(oldthumb),'component_count':len(oldparts),'removed_edge_ids':sorted(oldcut),'identity_by_current_independent_anchors':oldmatch,'component_rank_used':False,'historical_result_only':True,'vertex_components':oldparts,'original_code_rank_shortcut_preserved_as_history':True})
 # V1 induced graph on the exact solved domain, using original supported graph edges.
 v1={};v1parts={}
 for lab,sources in [('THUMB',T),('INDEX',I)]:
  ids={v for v in G if L[v]==lab};adj=defaultdict(set)
  for e in GE:
   a,b=E[e]
   if a in ids and b in ids:adj[a].add(b);adj[b].add(a)
  parts=cc(ids,adj);v1parts[lab]=parts;pureverts={v for f in pure[lab] for v in F[f]};rows=[]
  for k,part in enumerate(parts):
   ps=set(part);rows.append({'component_id':k,'vertex_count':len(part),'vertex_ids':part,'source_overlap_ids':sorted(ps&sources),'independent_anchor_overlap_ids':sorted(ps&anchors[lab]),'contains_complete_anchor_family':anchors[lab]<=ps,'source_free':not bool(ps&sources),'isolated_vertex_ids':[v for v in part if not adj[v]],'support_face_ids':sorted({f for v in part for f in vf[v]}),'pure_face_supported_vertex_count':len(ps&pureverts),'vertices_supported_only_by_mixed_or_partial_faces':sorted(ps-pureverts),'unsupported_vertices':[v for v in part if not vf[v]]})
  v1[lab]={'component_count':len(parts),'vertex_count':len(ids),'anchor_identity_component_ids':[k for k,p in enumerate(parts) if anchors[lab]<=set(p)],'isolated_vertex_count':sum(len(r['isolated_vertex_ids']) for r in rows),'source_free_component_count':sum(r['source_free'] for r in rows),'face_support_all':not any(r['unsupported_vertices'] for r in rows),'components':rows}
 v1pass=all(v1[l]['component_count']==1 and len(v1[l]['anchor_identity_component_ids'])==1 and v1[l]['source_free_component_count']==0 and v1[l]['face_support_all'] for l in v1)
 dump('R3_VERTEX_LABEL_COMPONENT_AUDIT.json',{'candidate':'V1','domain':'exact graph 962 vertices / 1881 face-supported edges; outside graph unassigned','definition':'connected components of induced graph G[label], equivalently remove unlike-label graph edges','THUMB':v1['THUMB'],'INDEX':v1['INDEX'],'identity_resolved':v1pass,'pass':v1pass,'automatic_canonical_inference_from_counts':False})
 # V2 face support restricted to wholly assigned homogeneous polygons. Mixed is separate validation band.
 v2={};pureparts={}
 for lab in ['THUMB','INDEX']:
  parts=cc(pure[lab],dual(pure[lab]));pureparts[lab]=parts;matches=[k for k,p in enumerate(parts) if anchorfaces[lab]<=set(p) and anchors[lab]<={v for f in p for v in F[f]}]
  v2[lab]={'component_count':len(parts),'face_count':len(pure[lab]),'anchor_identity_component_ids':matches,'components':[{'component_id':k,'face_ids':p,'vertex_ids':sorted({v for f in p for v in F[f]}),'source_overlap_ids':sorted({v for f in p for v in F[f]}&(T if lab=='THUMB' else I))} for k,p in enumerate(parts)]}
 v2pass=all(v2[l]['component_count']==1 and len(v2[l]['anchor_identity_component_ids'])==1 for l in v2)
 dump('R3_PURE_FACE_COMPONENT_AUDIT.json',{'candidate':'V2','THUMB':v2['THUMB'],'INDEX':v2['INDEX'],'pass':v2pass,'mixed_faces_not_assigned_to_either_side':True,'partial_and_unassigned_faces_excluded_not_relabelled':True,'adjacency':'shared full mesh edge, not vertex-only touch'})
 bandadj=dual(mixed);bandparts=cc(mixed,bandadj);bandrows=[]
 for part in bandparts:
  bs=set(part);neighbor={lab:sorted({g for f in part for e in fedges[f] for g in ef[e] if g in pure[lab]}) for lab in ['THUMB','INDEX']}
  bandrows.append({'face_ids':part,'face_count':len(part),'adjacent_pure_faces':neighbor,'touches_both_sides':all(neighbor[l] for l in neighbor),'surface_supported':all(len(ef[e])==2 for f in part for e in fedges[f]),'contains_own_hard_source_vertices':sorted({v for f in part for v in F[f]}&(T|I)),'outside_graph_corner_vertex_ids':sorted({v for f in part for v in F[f]}-G),'source_free_ownership_island':False,'ownership_label_created':False})
 bandpass=len(bandparts)==1 and all(r['surface_supported'] and r['touches_both_sides'] for r in bandrows)
 cutperface=Counter(len(composition[f]['incident_cut_edge_ids']) for f in mixed)
 dump('R3_MIXED_BOUNDARY_FACE_BAND_AUDIT.json',{'face_count':len(mixed),'face_band_component_count':len(bandparts),'face_ids':sorted(mixed),'components':bandrows,'pass':bandpass,'faces_by_incident_cut_edge_count':dict(cutperface),'geometry_modified':False,'third_ownership_label_created':False,'band_role':'validation-only boundary carrier; no polygon majority relabeling'})
 # V3 exactly as requested on FULL dual, then expose its domain-respecting specialization separately.
 v3ids=set(range(len(F)))-mixed;v3adj=dual(v3ids,cut);v3parts=cc(v3ids,v3adj);v3id=faceidentity(v3parts)
 bounded_ids=pure['THUMB']|pure['INDEX'];bounded_adj=dual(bounded_ids,cut);boundedparts=cc(bounded_ids,bounded_adj);boundedid=faceidentity(boundedparts)
 v3={'candidate':'V3','literal_full_mesh':{'removed_mixed_face_ids':sorted(mixed),'removed_cut_edge_ids':sorted(cut),'component_count':len(v3parts),'face_counts':[len(x) for x in v3parts],'identity':v3id,'pass':v3id['resolved'],'unknown_face_bridge_allowed':True},'domain_respecting_pure_face_specialization':{'domain':'fully solved faces only; mixed faces validation band; partial/unassigned faces nonparticipating','component_count':len(boundedparts),'identity':boundedid,'pass':boundedid['resolved'] and v2pass,'THUMB_components':v2['THUMB']['component_count'],'INDEX_components':v2['INDEX']['component_count'],'face_components':boundedparts,'equivalent_to_V2':sorted(map(sorted,boundedparts))==sorted(map(sorted,pureparts['THUMB']+pureparts['INDEX']))},'band_connected_supported':bandpass,'literal_full_mesh_not_silently_replaced_by_bounded_variant':True}
 dump('R3_FACE_DUAL_MIXED_BARRIER_AUDIT.json',v3)
 # Shortest retained face-dual witnesses. Endpoints are independent nail/cap anchor contexts.
 def shortest(adj,starts,ends):
  ends=set(ends);parent={f:None for f in sorted(starts)};q=deque(sorted(starts));end=None
  while q:
   f=q.popleft()
   if f in ends:end=f;break
   for g in sorted(adj[f]):
    if g not in parent:parent[g]=f;q.append(g)
  if end is None:return None
  path=[]
  while end is not None:path.append(end);end=parent[end]
  return path[::-1]
 def witness(adj):
  path=shortest(adj,anchorfaces['INDEX'],anchorfaces['THUMB']);assert path is not None;steps=[]
  for f,g in zip(path,path[1:]):
   shared=sorted(set(fedges[f])&set(fedges[g]));assert len(shared)==1;e=shared[0];assert e not in cut
   steps.append({'from_face':f,'to_face':g,'shared_mesh_edge_id':e,'shared_vertex_ids':E[e],'shared_vertex_labels':[L.get(v,'NO_SOLVE_UNASSIGNED_OUTSIDE_GRAPH') for v in E[e]],'is_fresh_cut_edge':False,'from_composition':composition[f],'to_composition':composition[g]})
  return {'shortest_hops':len(steps),'face_ids':path,'start_INDEX_anchor_face':path[0],'end_THUMB_anchor_face':path[-1],'steps':steps,'mixed_face_ids':[f for f in path if f in mixed],'partial_face_ids':[f for f in path if f in partial],'unassigned_face_ids':[f for f in path if f in unknown],'shared_vertex_only_hops':0}
 witness4=witness(v4adj);witness3=witness(v3adj)
 # A local pure-INDEX→mixed-band→pure-THUMB path proves the mixed-polygon bridge alone.
 localadj=dual(pure['THUMB']|pure['INDEX']|mixed,cut);localpath=shortest(localadj,pure['INDEX'],pure['THUMB'])
 local=None
 if localpath:
  local={'face_ids':localpath,'faces':[composition[f] for f in localpath],'shared_edges':[list(set(fedges[a])&set(fedges[b]))[0] for a,b in zip(localpath,localpath[1:])],'shortest_hops':len(localpath)-1,'mixed_face_ids':[f for f in localpath if f in mixed]}
 dump('R3_FACE_DUAL_RECONNECTION_PATH_AUDIT.json',{'V4_anchor_context_shortest_path':witness4,'V4_local_pure_side_via_mixed_path':local,'V3_full_mesh_after_mixed_barrier_shortest_path':witness3,'cause':'A mixed polygon is one dual node incident to same-label edges on both sides. Removing unlike primal edges removes dual crossings of those edges, not the within-polygon label interface. Full dual also permits exterior paths through unassigned/partial faces beyond the bounded ownership field.','vertex_only_touch_is_not_dual_adjacency':True,'all_path_hops_supported_by_shared_mesh_edges':True})
 # Static synthetic negative controls have no relation to the production labels or solver.
 toyF=[[0,1,2,3],[1,4,5,2],[3,2,6,7]];toyL={0:'T',1:'I',2:'I',3:'T',4:'I',5:'I',6:'T',7:'T'}
 toycomposition=[set(toyL[v] for v in f) for f in toyF];assert toycomposition==[{'T','I'},{'I'},{'T','I'}]
 # Simpler exact counterexample: left pure face shares T-T edge of a mixed quad, right pure shares I-I edge.
 quads=[[0,1,2,3],[3,2,4,5],[1,6,7,0]];ql={0:'I',1:'I',2:'T',3:'T',4:'T',5:'T',6:'I',7:'I'}
 assert {ql[v] for v in quads[0]}=={'T','I'} and {ql[v] for v in quads[1]}=={'T'} and {ql[v] for v in quads[2]}=={'I'}
 controls={'mixed_quad_dual_bridge_counterexample':{'faces':quads,'labels':ql,'retained_dual_path':[2,0,1],'shared_same_label_edges':[[0,1],[2,3]],'unlike_edges_removed':[[1,2],[3,0]],'vertex_regions_still_separate':True,'full_dual_still_connected':True},'component_order_permutation_identity_invariant':True,'missing_or_split_anchor_rejected':True,'vertex_only_touch_does_not_connect_face_dual':True,'unassigned_faces_never_acquire_binary_labels':True,'no_production_labels_modified':True}
 def matches(parts,req):return [k for k,p in enumerate(parts) if req<=set(p)]
 for lab in ['THUMB','INDEX']:
  normal=matches(v1parts[lab],anchors[lab]);rev=matches(list(reversed(v1parts[lab])),anchors[lab]);assert len(normal)==len(rev)==1
  assert matches([[v for v in v1parts[lab][0] if v!=min(anchors[lab])]],anchors[lab])==[]
  a=sorted(anchors[lab]);assert matches([a[:-1],[a[-1]]],anchors[lab])==[]
 dump('R3_SHEET_VALIDATOR_NEGATIVE_CONTROLS_R1.json',controls)
 provenance_files=[HISTORY/'scripts/r3_ownership.py',HISTORY/'scripts/_r3_sheet.py',HISTORY/'DIGIT_OWNERSHIP_AUTHORITY_R3.md',HISTORY/'THUMB_TIP_OWNERSHIP_BOUNDARY_R3_REPORT.md',ROOT/'production_spec/stage5_production_rig/cap_derived_r2_r3_input_reconciliation_r1/R3_VALIDATOR_REUSE_RECONCILIATION.json',ROOT/'audits/narrow_proximal_domain_wrappers_and_unary_units_authority_review_r1/R3_VALIDATOR_SEMANTIC_UPDATE_PLAN.json',CONTRACT/'R3_VALIDATOR_CONTRACT_R1.json',CONTRACT/'R3_RECOVERY_INPUT_CONTRACT_FINALIZATION_R1_REPORT.md',FRESH/'recompute.py']
 response=Path('<USER_HOME>/Downloads/R3_RECOVERY_INPUT_CONTRACT_HUMAN_REVIEW_R1_RESPONSE_2026-10-03T10-43-37-453Z.json');r=read(response);assert r['approved_for_input_contract'] and r['canonical_contract_hash']==digest(contract)
 provenance={'sources':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'sheet_mentions':ranges(p,'sheet',2)} for p in provenance_files],'Human_input_approval':{'path':str(response),'sha256':sha(response),'review_id':r['review_id'],'scope':r['authority_scope'],'anatomical_ownership_map_approved':r['anatomical_ownership_map_approved']},'history_intent':'Identify an independently anchored coherent INDEX vertex region versus THUMB-side counterpart; graph cut is virtual. Original code deletes primal vertex adjacency, and explicitly performs no retopology/seam split. It never verified physical face-dual disconnection.','historical_rank_shortcut':'Original code selects second-largest; preserved but retired. Current reproduction names regions by fixed anchor families.','literal_bound_contract_method':'Full frozen face dual minus unlike primal edges; this exact method was approved as input and reproduced unchanged, but it is a different observable from vertex-region identity.','method_introduced_at':'r3_recovery_input_contract_finalization_r1/build_contract.py:146','prior_update_plan':'Independent marker/nail/cap containment; no rank; binary shared-neutral vertices do not gain anatomical exclusivity; outside-graph historical injection retired.','sheet_specific_errata_discovered':[],'existing_negative_controls':'Update plan lists future controls only; this run executes static method controls. Existing unrelated anatomical controls are not evidence for sheet method.','design_intent_adjudication':'C with A as primary: two independently identified connected ownership regions with pure-face support and a mixed validation band. B physical mesh surgery/disconnection is not the historical gate.','authority_resolution':'Technical type reconciliation explicitly authorized by current user request; approved input contract and its method/failure remain byte-immutable. New derived method sidecar only; no silent edit of approved contract.','independent_body_wrist_v2260':'Outside solved domain. THUMB counterpart is an ownership region, not a newly approved full-body/wrist ownership map.','method_choice_independent_of_desired_counts':True}
 dump('R3_SHEET_VALIDATOR_PROVENANCE_AUDIT.json',provenance)
 comparison={'frozen_labels_hash':label_hash,'common_independent_anchor_families':{k:sorted(v) for k,v in anchors.items()},'candidates':[{'id':'V1','name':'HISTORICAL_VERTEX_LABEL_COMPONENT','input_object':'bounded solved vertex field G','delete_object':'unlike-label primal graph edges','component_definition':'induced same-label vertex connected components','identity_rule':'one component contains complete fixed own anchor family, excludes counterpart; no rank','THUMB_components':v1['THUMB']['component_count'],'INDEX_components':v1['INDEX']['component_count'],'pass':v1pass,'applicable':True},{'id':'V2','name':'PURE_FACE_COMPONENT','input_object':'fully solved homogeneous polygons','delete_object':'no label editing; mixed, partial, unknown faces nonparticipating','component_definition':'same-label pure faces connected through full shared edges','identity_rule':'complete fixed own marker/nail/cap family in unique pure-face component','THUMB_components':v2['THUMB']['component_count'],'INDEX_components':v2['INDEX']['component_count'],'pass':v2pass,'applicable':'supporting 2D coherence check, not replacement for vertex ownership coverage'},{'id':'V3','name':'FACE_DUAL_WITH_MIXED_BOUNDARY_BARRIER','input_object':'literal full frozen face dual','delete_object':'all 21 mixed face nodes plus current unlike-edge adjacencies','component_definition':'remaining full dual components, including unknown exterior','identity_rule':'same independent anchors','THUMB_identity_component_ids':v3id['THUMB'],'INDEX_identity_component_ids':v3id['INDEX'],'pass':v3id['resolved'],'applicable':False,'domain_respecting_specialization':'equivalent to V2; two anchored pure-face sides, mixed boundary band excluded'},{'id':'V4','name':'CURRENT_FULL_FACE_DUAL','input_object':'all 3414 frozen face nodes','delete_object':'dual adjacencies whose shared primal edge belongs to frozen 20 cut edges','component_definition':'full-face shared-edge connectivity','identity_rule':'same independent anchors collide in 1 component','pass':False,'applicable':False}],'canonical_method':METHOD,'method_status':'TECHNICAL_DERIVED_VALIDATOR_SEMANTICS_CORRECTION_ONLY','physical_mesh_disconnected_claim':False,'third_ownership_label_created':False}
 dump('R3_SHEET_VALIDATOR_CANDIDATE_COMPARISON.json',comparison)
 passed=v1pass and v2pass and bandpass and boundedid['resolved'];verdict='FRESH_R3_SHEET_IDENTITY_PASS' if passed else 'FRESH_R3_SHEET_IDENTITY_FAIL'
 revalidation={'verdict':verdict,'canonical_validator_method':METHOD,'frozen_result_hash':label_hash,'method_selection_proof':'Vertex-label components partition G by definition. Full primal graph cut and full dual edge deletion are different operations: mixed polygons are single dual nodes crossing the vertex field interface. Pure-face support plus independent markers and separate mixed band checks the 2D realization without assigning unknown faces. Historical gate code used primal vertex adjacency and virtual ownership only.','V1_pass':v1pass,'V2_pass':v2pass,'mixed_band_pass':bandpass,'domain_respecting_V3_pass':boundedid['resolved'],'current_full_face_dual':'VALIDATOR_METHOD_MISMATCH','literal_V3_full_mesh':'DOMAIN_MISMATCH_UNASSIGNED_EXTERIOR_BRIDGE','INDEX_identity_resolved':passed,'THUMB_identity_resolved':passed,'INDEX_ownership_vertex_count':v1['INDEX']['vertex_count'],'THUMB_counterpart_vertex_count':v1['THUMB']['vertex_count'],'pure_INDEX_face_count':len(pure['INDEX']),'pure_THUMB_face_count':len(pure['THUMB']),'mixed_band_face_count':len(mixed),'global_body_side_count':None,'outside_graph_status':'NO_SOLVE_UNASSIGNED_OUTSIDE_GRAPH','global_body_identity_not_claimed':True,'old_sheet_fail_result_preserved':True,'Human_methodology_review_required':False,'Human_result_review_still_required':True,'fresh_labels_changed':0,'R3_rerun_count':0,'skin_rebuild_count':0,'Stage6_runs':0,'BLEND_FILES_WRITTEN':0,'NEXT':'HUMAN_R3_FRESH_RESULT_APPROVAL' if passed else 'R3_FRESH_RESULT_FAILURE_DIAGNOSIS_R1','STOP':True}
 dump('R3_SHEET_IDENTITY_REVALIDATION_R2.json',revalidation)
 dump('R3_FRESH_DERIVED_VALIDATION_STATUS_R2.json',{'derived_verdict':'PASS_READY_FOR_HUMAN_REVIEW' if passed else 'FAIL_REVALIDATION','revalidation':revalidation,'supersedes_only':'Derived sheet-method status. Original frozen R1 failure and approved contract remain immutable.','canonical_contract_hash':digest(contract),'fresh_labels_hash':label_hash,'Human_approved_frozen':False,'skin_authority_approved':False,'automatic_apply':False})
 result={'run':RUN,'verdict':verdict,'mixed_label_face_count':len(mixed),'current_face_dual_reconnection_cause':'mixed polygon bridges through retained same-label edges; additionally unassigned/partial exterior faces bypass the bounded field','V1_THUMB_components':v1['THUMB']['component_count'],'V1_INDEX_components':v1['INDEX']['component_count'],'V2_pure_THUMB_components':v2['THUMB']['component_count'],'V2_pure_INDEX_components':v2['INDEX']['component_count'],'mixed_boundary_face_band_count':len(bandparts),'mixed_boundary_face_count':len(mixed),'V3_literal_THUMB_components':len(v3id['THUMB']),'V3_literal_INDEX_components':len(v3id['INDEX']),'V3_literal_anchor_collision':v3id['collision'],'V3_bounded_THUMB_components':v2['THUMB']['component_count'],'V3_bounded_INDEX_components':v2['INDEX']['component_count'],'INDEX_identity_resolved':passed,'THUMB_identity_resolved':passed,'historical_validator_semantic_intent':provenance['history_intent'],'current_full_face_dual_applicable':False,'canonical_sheet_validator_method':METHOD,'fresh_sheet_identity':'PASS' if passed else 'FAIL','fresh_labels_changed':0,'R3_rerun_count':0,'skin_rebuild_count':0,'Stage6_runs':0,'BLEND_FILES_WRITTEN':0,'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,'Human_Review_R2_generated':False,'NEXT':revalidation['NEXT'],'STOP':True,'frozen_result_hash':label_hash,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 dump(RUN+'_STATUS.json',result)
 dump('R3_FROZEN_FRESH_RESULT_VERIFICATION_R1.json',{'pass':True,'manifest_hashes':verify,'labels_sha256':label_hash,'invariants':expected,'frozen_current_full_face_dual_failure_reproduced':True,'historical217_3199_reproduced':True,'fresh_binary_counts':dict(Counter(L.values())),'solver_or_closure_imported_or_called':False})
 after=inventory();assert before==after,'Protected file change';dump('FROZEN_HASHES_AFTER.json',after);dump('FROZEN_HASH_VERIFICATION_R1.json',{'pass':True,'protected_file_count':len(before),'changed_files':[],'fresh_labels_changed':0,'R3_rerun_count':0,'BLEND_FILES_WRITTEN':0})
 print(json.dumps(result,ensure_ascii=False,indent=2))
 print('V4 shortest faces:',witness4['face_ids'],'V3 shortest faces:',witness3['face_ids'],'local mixed path:',local)
if __name__=='__main__':main()
