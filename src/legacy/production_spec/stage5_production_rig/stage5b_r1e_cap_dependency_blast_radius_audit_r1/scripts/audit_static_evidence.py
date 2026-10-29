from pathlib import Path
from collections import Counter, defaultdict, deque
import json, hashlib, re, sys
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(r'<HANDS_ROOT>')
S5=ROOT/'production_spec/stage5_production_rig'
S6=ROOT/'production_spec/stage6_deformation'
OUT=S5/'stage5b_r1e_cap_dependency_blast_radius_audit_r1'
FREEZE=S5/'stage5b_r1e_human_cap_authority_freeze_r1'
OLD={151,158,1061,1074,1076,2189,2192,2569,2577}
EXPECTED='c81dd96d6925ed402cdf0ba44c148d7a78c2c60640fe23fb6247fb729f346cc8'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def ref(p,locator,role):return {'path':str(p.relative_to(ROOT)),'locator':locator,'role':role,'sha256':sha(p)}
A=read(FREEZE/'THUMB_DISTAL_CAP_CANONICAL_AUTHORITY_R1.json')
payload={k:v for k,v in A.items() if k!='combined_authority_hash'}
assert hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()==A['combined_authority_hash']==EXPECTED
assert A['vertex_count']==37 and A['face_count']==25 and A['status']=='HUMAN_APPROVED_FROZEN'
NEW=set(A['vertex_ids'])
R3DIR=S6/'stage6b_r3_thumb_tip_ownership_boundary'
LAB=read(R3DIR/'R3_OWNERSHIP_LABELS.json')
RAWPATH=S5/'stage5b_r1e_endpoint_authority_review/_tmp/review_raw.json'
RAW=read(RAWPATH)
V=np.array(RAW['R1B']['v'])*1000;ED=RAW['R1B']['edges'];F=RAW['R1B']['faces']
assert RAW['R3']==LAB and len(V)==3416
assert ED==RAW['R1E']['edges'] and F==RAW['R1E']['faces']
ADJ=defaultdict(set)
for a,b in ED:ADJ[a].add(b);ADJ[b].add(a)
def hops(seeds):
 d={v:0 for v in seeds};q=deque(sorted(seeds))
 while q:
  v=q.popleft()
  for u in sorted(ADJ[v]):
   if u not in d:d[u]=d[v]+1;q.append(u)
 return d
def ring(seeds,n):return {v for v,d in hops(seeds).items() if d<=n}
BND=set(v for k in LAB['boundary_edges_R3'] for v in ED[k]);BD=hops(BND);OD=hops(OLD)
STRONG=set(LAB['THUMB_STRONG']);INDEX_STRONG=set(LAB['INDEX_STRONG'])
chains={k:np.array(v)*1000 for k,v in RAW['R2A_chains'].items()}
def axis_role(v,chain):
 p=V[v];lengths=np.linalg.norm(np.diff(chain,axis=0),axis=1);cum=np.r_[0,np.cumsum(lengths)];best=(1e30,0.)
 for i,(a,b) in enumerate(zip(chain,chain[1:])):
  ab=b-a;t=max(0.,min(1.,float(np.dot(p-a,ab)/np.dot(ab,ab))));d=float(np.linalg.norm(p-a-t*ab))
  if d<best[0]:best=(d,float(cum[i]+t*lengths[i]))
 return best,cum
ROLE={}
for v in sorted(OLD|NEW):
 (d,s),cum=axis_role(v,chains['THUMB'])
 ROLE[v]={'old_cap_role':v in OLD,'native_cap37_role':v in NEW,'historical_live_lateral_mm':d,'historical_live_arc_mm':s,
  'also_live_thumb_tube_anchor':d<=10.4735 and s>=float(cum[1]),
  'also_live_metacarpal_corridor_anchor':d<=.85*10.4735 and .30*float(cum[1])<=s<float(cum[1]),
  'also_nail_anchor':v in LAB['NAIL_THUMB'],'also_first_web_anchor':v in LAB['WEB']}
assert all(ROLE[v]['also_live_thumb_tube_anchor'] for v in OLD)
oldrows=[]
for v in sorted(OLD):
 oldrows.append({'vertex_id':v,'native_branch':'INDEX_SURFACE (settled, not re-adjudicated)','R2_label':LAB['R2'][v],'R3_label':LAB['R3'][v],
  'THUMB_STRONG':v in STRONG,'INDEX_STRONG':v in INDEX_STRONG,'roles':ROLE[v],
  'one_ring_R3_labels':[{'vertex_id':u,'R3_label':LAB['R3'][u],'THUMB_STRONG':u in STRONG} for u in sorted(ADJ[v])],
  'two_ring_R3_label_counts':dict(Counter(LAB['R3'][u] for u in ring({v},2))),
  'graph_distance_to_R3_boundary_hops':BD[v],'incident_final_cut_edge_ids':[k for k in LAB['boundary_edges_R3'] if v in ED[k]],
  'final_cut_participation':'HARD_SOURCE_PIN_AND_UNARY_SOURCE; no incident final THUMB/INDEX cut edge',
  'connectivity_closure_anchor_role':True,'connectivity_closure_relabelled_this_vertex':False,
  'closure_relabelling_evidence':'Historical closure converged in 1 round and retained 1 anchor-bearing THUMB component; pinned anchors cannot be relabelled by the documented closure rule',
  'exclusive_cause_of_neighbor_labels':'UNRESOLVED; old cap anchors overlap live tube anchors and no counterfactual solve is allowed'})
AMB=read(R3DIR/'R3_AMBIGUOUS_VERTEX_AUDIT.json');CA=read(R3DIR/'R3_CLASS_A_PRESERVATION_AUDIT.json');ISLAND=read(R3DIR/'R3_ISLAND_AUDIT.json')
influence={'execution':'CAP_DEPENDENCY_BLAST_RADIUS_AUDIT_R1','authority_hash':EXPECTED,'old_cap9_ids':sorted(OLD),'vertices':oldrows,
 'stored_data_sources':[ref(R3DIR/'R3_OWNERSHIP_LABELS.json','$.THUMB_STRONG,CAP,R3,boundary_edges_R3','Historical labels and sets, read only'),ref(RAWPATH,'$.R1B.v,edges,R2A_chains','Previously extracted frozen live geometry used only for static anchor-predicate audit'),ref(R3DIR/'scripts/r3_ownership.py','L176–220; L268–269; L350–450','Anchor union, fields, hard pins, mincut, ambiguous band, closure')],
 'is_only_anchor_set_affected':False,'dependency_paths':['old cap9 → THUMB_STRONG → dT unary field → global coupled mincut → labels → boundary → cut-sheet classification','old cap9 → R2 cap-centroid seed → R2 labels/domain → R3 candidate graph','old cap representative → R2A tip/IP-tail rig → live tube anchors and R3 geometry fields','old cap9 → closure anchor reachability and cap-exclusion validators'],
 'one_ring_union_ids':sorted(ring(OLD,1)),'one_ring_union_count':len(ring(OLD,1)),'two_ring_union_ids':sorted(ring(OLD,2)),'two_ring_union_count':len(ring(OLD,2)),
 'two_ring_native_index_THUMB_label_ids':sorted(v for v in ring(OLD,2) if LAB['R3'][v]=='THUMB'),
 'old_cap_all_already_live_tube_anchors':True,'replace_explicit_CAP_only_removed_effective_thumb_anchors':[],
 'replace_explicit_CAP_only_added_effective_thumb_anchors':sorted(NEW-STRONG),
 'replace_explicit_CAP_only_limitation':'Removing CAP union alone leaves all nine wrong anchors pinned by the old live tube; not a sufficient repair. The 6 additional cap37 pins and cap-derived R2/rig dependencies preclude a no-change proof.',
 'new_cap37_stored_R3_labels':dict(Counter(LAB['R3'][v] for v in NEW)),'new_cap37_already_strong_count':len(NEW&STRONG),
 'R3_changed_vs_R2_count':len(LAB['changed']),'R3_changed_vs_R2_ids':LAB['changed'],'changed34_not_claimed_as_counterfactual_cap_effect':True,
 'ambiguous_vertices_existing':AMB['ambiguous_vertices'],'ambiguous_set_input_contaminated':True,
 'closure_rounds_existing':ISLAND['connectivity_closure_rounds'],'closure_exact_counterfactual_effect':'UNRESOLVED; historical post-cut labels alone do not measure the changed-input solve',
 'sheet_split_existing':read(R3DIR/'R3_BOUNDARY_CONNECTEDNESS_AUDIT.json')['sheet_split'],'sheet_and_cut_counterfactual_changes':'UNRESOLVED',
 'class_A_geometry_authority':'UNCHANGED','class_A_six_edge_label_preservation_existing':CA['edges'],'class_A_gate_revalidation_required':True,
 'R3_revalidation_level':'R3_FULL_RECOMPUTE','R3_full_recompute_required':'YES','recompute_scope':'Global coupled THUMB/INDEX graph (historically 1008 candidate vertices), after inherited seed/rig/anchor semantics are reconciled; other digit authority not blanket-invalidated',
 'R3_boundary_likely_affected':'UNRESOLVED','boundary_reason':'At-risk global solve and changed anchor/seed semantics, but actual new labels/cut/sheet cannot be predicted without the forbidden counterfactual recompute',
 'historical_R3_status':'HISTORICALLY_HUMAN_APPROVED; REVALIDATION_REQUIRED_AFTER_CAP_AUTHORITY_CORRECTION',
 'causal_influence_radius':'UNBOUNDED_WITHIN_COUPLED_SOLVE; displayed 1/2-rings are observed neighborhoods, not a proven causal cutoff',
 'R3_runs':0,'Dijkstra_R3_field_runs':0,'mincut_runs':0,'graph_hops_only':True}
dump('R3_OLD_CAP9_INFLUENCE_RADIUS_AUDIT.json',influence)
# Region audit: never compute a new vector. Read historical delta and saved extracted vectors only.
D1=read(S5/'stage5b_r1a/STAGE5B_R1A_WEIGHT_DELTA_AUDIT.json');D2=read(S5/'stage5b_r1b/STAGE5B_R1B_WEIGHT_DELTA_AUDIT.json')
REG1=read(S5/'stage5b_r1a/_tmp/R1A_REGIONS.json');REG2=read(S5/'stage5b_r1b/_tmp/R1B_REGIONS.json')
d1={r['vertex']:r for r in D1['per_vertex_delta']};d2={r['vertex']:r for r in D2['per_vertex_delta']}
weights=[]
for v in sorted(OLD):
 assert v in d1 and v not in d2
 weights.append({'vertex_id':v,'native_branch':'INDEX_SURFACE','R1_before':d1[v]['before'],'R1A_after':d1[v]['after'],'R1B_actual_saved_extract':RAW['R1B']['w'][v],
  'R1B_cap_protected_and_not_reweighted':True,'first_explicit_old_cap_driven_skin_write':'Stage5B R1A',
  'R1_preexisting_wrong_thumb_drive':d1[v]['before_dominant']=='THUMB_IP_R','R1A_owner_override_needed':d1[v]['before_dominant']=='INDEX_MCP_R'})
region_rows=[]
for name,reg,changes,source in [('R1A',set(REG1['AUTH']),set(REG1['CHANGED']),S5/'stage5b_r1a/_tmp/R1A_REGIONS.json'),('R1B',set(REG2['AUTH']),set(REG2['CHANGED']),S5/'stage5b_r1b/_tmp/R1B_REGIONS.json')]:
 region_rows.append({'stage':name,'authorised_vertex_ids':sorted(reg),'changed_vertex_ids':sorted(changes),'old_cap_overlap':sorted(reg&OLD),'new_cap37_overlap':sorted(reg&NEW),'dependency_kind':'CAP-DERIVED OWNERSHIP/REGION AND THUMB FIELD; not every member proven exclusively cap-caused','source':ref(source,'$.AUTH,CHANGED','Stored masks; no re-selection')})
for st,fn in [('R1C','STAGE5B_R1C_AUTHORISED_WEIGHT_REGION.json'),('R1D','STAGE5B_R1D_AUTHORISED_DISTAL_WEIGHT_REGION.json'),('R1E','STAGE5B_R1E_AUTHORISED_WEIGHT_REGION.json')]:
 p=S5/('stage5b_'+st.lower())/fn;d=read(p)
 region_rows.append({'stage':st,'authorised_vertex_ids':d['authorised_vertices'],'changed_vertex_ids':d['changed_vertices'],
  'old_cap_overlap':sorted(set(d['authorised_vertices'])&OLD),'new_cap37_overlap':sorted(set(d['authorised_vertices'])&NEW),
  'future_reuse_status':'REBUILD_REQUIRED','historical_current_status':'HISTORICAL_ONLY; original failed-candidate verdict preserved','source':ref(p,'$.authorised_vertices,changed_vertices','Cap/R2/R3-derived repair regions')})
union=OLD|set(REG1['AUTH'])|set(REG2['AUTH'])|set(LAB['R2_domain'])
for rr in region_rows:union|=set(rr['authorised_vertex_ids'])
native=read(S5/'stage5b_r1e_thumb_distal_cap_native_branch_identity_audit_r1/_tmp/native_independent_partition.json')['labels']
dependent_driver={i for i,w in enumerate(RAW['R1B']['w']) if any(w.get(g,0)>0 for g in ['THUMB_CMC_R','THUMB_MCP_R','THUMB_IP_R'])}
review_scope=union|NEW|dependent_driver
no_driver=set(range(3416))-review_scope
newrows=[{'vertex_id':v,'R1B_weights':RAW['R1B']['w'][v],'R3_label':LAB['R3'][v],'R1B_changed':v in set(REG2['CHANGED']),'automatic_THUMB_IP_1_rule_authorized':False} for v in sorted(NEW)]
wa={'execution':'CAP_DEPENDENCY_BLAST_RADIUS_AUDIT_R1','old_cap9_vertices':weights,'new_cap37_current_historical_weights':newrows,
 'Stage5B_earliest_contaminated_stage':'Stage5B R1 (inherited cap-derived R2A deform bone tail/bind matrix); R1A is first explicit old-cap membership→ownership/weight write',
 'first_explicit_old_cap9_membership_write':'Stage5B R1A','preexisting_R1_thumb_IP_dominant_old_cap_count':sum(r['R1_preexisting_wrong_thumb_drive'] for r in weights),
 'R1_cap_ID_selector_used':False,'R1_rig_implementation_dependency':ref(S5/'stage5b_r1/scripts/s5b_r1_bind.py','L55–59; live bone head/tail extraction and seg_dist raw mu','Copies R2A cap-derived rig; R1 raw weights use live bone geometry'),
 'R1A_functions':[ref(S5/'stage5b_r1a/scripts/r1a_common.py','L417–483','cap override → distal/authorized/first-web masks'),ref(S5/'stage5b_r1a/scripts/s5b_r1a_build.py','L87–94,L121–180','R1A ownership/mask authorizes actual free vector writes')],
 'R1B_functions':[ref(S5/'stage5b_r1b/scripts/r1b_common.py','L127–149','Reuses cap-derived R1A masks'),ref(S5/'stage5b_r1b/scripts/s5b_r1b_build.py','L112–122,L205–217','Old cap protected, wrong driver retained')],
 'round_feature_dependency_matrix':{'R1':{'explicit_cap_THUMB_IP_1_rule':False,'cap-derived_rig_and_mu':True,'first_web_old_cap_exclusion':False,'normalization_math_itself':'INDEPENDENT'},
  'R1A':{'cap_ownership_override':True,'distal_mask':True,'weight_generation':True,'whitelist_and_free_budget':True,'nail_cap_semantic_union':True,'first_web_exclusion_and_boundary':True,'dominance_validator':True,'normalization_math_itself':'INDEPENDENT; authorized support/budget cap-dependent'},
  'R1B':{'cap_protection':True,'cap-derived_authorised_mask':True,'inherited_wrong_weights':True,'protected_drift_validator':True,'first_web_exclusion':True,'thumb_chain_dominance_validator':True,'normalization_math_itself':'INDEPENDENT; region/support cap-dependent'}},
 'region_sets':region_rows,'confirmed_contaminated_ids':sorted(OLD),'review_union_ids':sorted(review_scope),'review_union_count':len(review_scope),
 'review_union_rule':'Stored authorized/changed masks + R2 domain + old/new cap sets + actual nonzero THUMB driver carriers. Conservative dependency envelope; not a claim every member is wrong.',
 'no_cap_or_thumb_driver_dependency_proven_ids':sorted(no_driver),'no_cap_or_thumb_driver_dependency_proven_count':len(no_driver),
 'outside_region_proof':'Outside every stored write/ownership repair domain, no thumb deform bone carrier, not old/new cap; no old-cap specific region selector. These vector entries are reusable subject to byte/hash regression.',
 'middle_ring_little_frozen_group_proof':ref(S5/'stage5b_r1b/STAGE5B_R1B_PROTECTED_WEIGHT_DRIFT_AUDIT.json','$.frozen_four_finger_groups_drift=0','Verbatim independent group inheritance; does not exempt native INDEX old-cap sites'),
 'R1B_status':'FROZEN HISTORICAL PRODUCTION MASTER','R1B_rebuild_required':True,'R1C_rebuild_required':True,'R1D_rebuild_required':True,'R1E_rebuild_required':True,
 'rebuild_meaning':'New reconciled production weights/data needed before future reuse; historical candidate files need not be recreated or overwritten',
 'first_web_authority_dependency':'STATIC TARGETED REVALIDATION REQUIRED: R1A first-web membership was generated from cap-overridden ownership boundary with cap/nail exclusion; existing Human approval stays historical',
 'nail_face_authority':'UNAFFECTED; wrapper region/weight tests need revalidation, approved Stage4 nail mask is not rebuilt',
 'CMC_cage_geometry':'UNAFFECTED; R1E R3-filtered protection wrapper is revalidation-only',
 'CAP_WEIGHT_AUTHORITY':'NOT_YET_RECONCILED','new_cap37_THUMB_IP_1_inherited':False,'weights_written':0}
dump('STAGE5B_CAP_DEPENDENT_WEIGHT_REGION_AUDIT.json',wa)
edge=read(S5/'stage5b_r1e_endpoint_authority_review/R1E_EDGE5879_AUTHORITY_CONTEXT_AUDIT.json')
dump('EDGE5879_CAP_DEPENDENCY_AUDIT.json',{'edge_id':5879,'endpoints':[1551,3125],'dependency_verdict':'PARTLY_CAP_DERIVED',
 'numeric_observation_status':'NUMERIC_OBSERVATION_STILL_FACTUAL','defect_status':'WEIGHT_TRANSITION_PARTITIONING_DEFECT_RETAINED',
 'direct_old_cap_endpoint':False,'endpoints_R3':['THUMB','THUMB'],'cap_anchor_exemption_at_endpoints':False,
 'numeric_and_local_mechanism_evidence':edge,'direct_defect':'R1E wrist-heavy lateral/palm transition versus frozen first-web MCP driver; observed delta does not use strict-bound formula',
 'inherited_dependency':'R1E region/allowed-family/collar field uses R3; R3 and live rig are cap-derived. Therefore the generated field is partly cap-derived, but the frozen edge measurement and local mismatch are not invalidated by cap endpoint correction.',
 'r3_runs':0,'deformation_runs':0,'new_ratio_computations':0,'source':ref(S5/'stage5b_r1e_endpoint_authority_review/R1E_EDGE5879_AUTHORITY_CONTEXT_AUDIT.json','$.weights_R1B,weights_R1E,ratios','Binding saved numerical evidence'),
 'field_source':ref(S5/'stage5b_r1e/scripts/s5b_r1e_build.py','L342–411,L425–465','Cap/nail clamps, R3 collar share, live-axis lateral gate, relaxation')})
dump('_STATIC_AUDIT_DATA.json',{'vertex_positions_world_mm':V.tolist(),'native_labels':native,'old_cap9_ids':sorted(OLD),'new_cap37_ids':sorted(NEW),'observed_two_ring_ids':sorted(ring(OLD,2)),
 'R3_label_ids':LAB['R3'],'R3_boundary_edge_ids':LAB['boundary_edges_R3'],'edges':ED,'cap_dependent_review_region_ids':sorted(review_scope),'confirmed_contaminated_ids':sorted(OLD),'cap_independent_ids':sorted(no_driver)})
print(json.dumps({'authority_verified':True,'R3_old9_also_tube':True,'new37_unpinned_six':sorted(NEW-STRONG),'R3_full_recompute':'YES','R3_boundary_counterfactual':'UNRESOLVED','review_region_count':len(review_scope),'independent_vertex_count':len(no_driver),'first_explicit_skin_write':'R1A','earliest_cap_derived_skin':'R1','edge5879':'PARTLY_CAP_DERIVED','solver_runs':0}))
