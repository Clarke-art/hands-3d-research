from pathlib import Path
from collections import Counter,defaultdict,deque
import json,hashlib,sys
sys.stdout.reconfigure(encoding='utf-8')
R=Path(r'<HANDS_ROOT>');S5=R/'production_spec/stage5_production_rig';S6=R/'production_spec/stage6_deformation';O=S5/'stage5b_r1e_cap_dependency_blast_radius_audit_r1'
def j(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ev(path,locator,claim):return {'path':path,'locator':locator,'claim':claim,'sha256':hashlib.sha256((R/path).read_bytes()).hexdigest()}
W=j(O/'STAGE5B_CAP_DEPENDENT_WEIGHT_REGION_AUDIT.json');I=j(O/'CAP_DIRECT_REFERENCE_AUDIT.json');HASH=j(O/'R3_OLD_CAP9_INFLUENCE_RADIUS_AUDIT.json')['authority_hash']
lineage=[('Stage6A R1','stage6a','Stage5B R1A','scripts/s6a_common.py','L19–20'),('Stage6A R1A','stage6a_r1a','Stage5B R1B','scripts/s6a_common.py','L20–21'),('Stage6A R1B','stage6a_r1b','Stage5B R1C','scripts/s6a_r1b_build_harness.py','L34–36'),('Stage6B R1','stage6b','Stage5B R1B','scripts/s6b_common.py','L44–48'),('Stage6B R1B','stage6b_r1b','Stage5B R1C','scripts/s6b_r1b_build_harness.py','L29–30')]
stage6=[]
for label,folder,skin,src,loc in lineage:
 rows=[
  {'result_kind':'abstract_pose_definition_angles_and_case_matrix','dependency_class':'NO_CAP_DEPENDENCY','contamination':'NONE','numeric_status':'REUSABLE TEST INTENT','qualification_action':'Retain canonical angle/case requirements; do not rerun now'},
  {'result_kind':'pose_world_axes_and_LBS_transforms','dependency_class':'DERIVED_DEPENDENCY','contamination':'IMPLEMENTATION_CONTAMINATION','numeric_status':'NUMERIC_OBSERVATION_STILL_FACTUAL','qualification_action':'Thumb IP local frame and cap-derived rig must be reconciled; canonical angles are not world-transform independence'},
  {'result_kind':'skin_weights_and_harness_payload','dependency_class':'TRANSITIVE_DEPENDENCY','contamination':'IMPLEMENTATION_CONTAMINATION','numeric_status':'Historical exact skin/harness payload retained','qualification_action':'Build a new reconciled harness only after rig/weight authorities approved'},
  {'result_kind':'actual_deformation_geometry_edge_stretch_and_displacement','dependency_class':'TRANSITIVE_DEPENDENCY','contamination':'IMPLEMENTATION_CONTAMINATION','numeric_status':'NUMERIC_OBSERVATION_STILL_FACTUAL','qualification_action':'New production requires new measurements; old numbers remain true for old input'},
  {'result_kind':'global_severe_edge_threshold_definition','dependency_class':'NO_CAP_DEPENDENCY','contamination':'NONE','numeric_status':'Threshold constants unchanged','qualification_action':'Retain independent arithmetic threshold; measured geometry still cap-dependent'},
  {'result_kind':'distal_cap_specific_metric_region_and_nail_cap_distance','dependency_class':'DIRECT_DEPENDENCY','contamination':'VALIDATOR_CONTAMINATION','numeric_status':'Historical fixed-ID numbers factual; TRUE_THUMB_CAP interpretation invalid','qualification_action':'Use explicit cap37 in future metric fixtures; no threshold selector'},
  {'result_kind':'self_intersection_raw_triangle_pairs_depth','dependency_class':'TRANSITIVE_DEPENDENCY','contamination':'IMPLEMENTATION_CONTAMINATION','numeric_status':'NUMERIC_OBSERVATION_STILL_FACTUAL','qualification_action':'Keep old pair/depth evidence; rerun on future reconciled geometry'},
  {'result_kind':'self_intersection_digit_or_cap_region_classifier','dependency_class':'DERIVED_DEPENDENCY','contamination':'VALIDATOR_CONTAMINATION','numeric_status':'Classifier labels are not independent anatomical proof','qualification_action':'R1A/R2 ownership-derived buckets and severity interpretation need revalidation'},
  {'result_kind':'R3_collar_metrics','dependency_class':'NO_CAP_DEPENDENCY','contamination':'NONE IN THIS HISTORICAL FULL SUITE','numeric_status':'NOT_APPLICABLE: these full suites precede R3; R3 used in later R1E targeted audits','qualification_action':'Do not retroactively claim these runs consumed R3'},
  {'result_kind':'freeze_status_qualification_and_recommendation','dependency_class':'TRANSITIVE_DEPENDENCY','contamination':'REPORTING_ONLY_CONTAMINATION','numeric_status':'Historical Human approval/verdict remains factual','qualification_action':'QUALIFICATION_VERDICT_NEEDS_REVALIDATION for corrected production; no new PASS/FAIL issued'}]
 stage6.append({'stage':label,'historical_skin_source':skin,'source_evidence':ev(f'production_spec/stage6_deformation/{folder}/{src}',loc,'Executable assignments override stale header comments'),
  'results':rows,'qualification_status':'QUALIFICATION_VERDICT_NEEDS_REVALIDATION','future_remediation':'TIER_4 FULL DEFORMATION REQUALIFICATION','suite_run_now':False})
dump('STAGE6_CAP_DEPENDENCY_AUDIT.json',{'execution':'CAP_DEPENDENCY_BLAST_RADIUS_AUDIT_R1','stages':stage6,
 'later_R1D_R1E_targeted_prequalification':{'R1D':'R2 labels + cap-derived live rig + reconciled-from-R1B field','R1E':'R3 labels/collar + old-cap anchor clamp + cap-derived live rig; R3 collar metrics directly derived','self_intersection_classifier':'R2/R3-derived semantic buckets; raw triangle intersections still recorded fixed-geometry facts'},
 'historical_harness_header_errata_not_rewritten':'Stage6A R1B and Stage6B R1B builder comments say older master; operative code selects R1C. Audit follows code and existing candidate hash, not filename/header.',
 'scope_distinction':['NUMERIC_OBSERVATION_STILL_FACTUAL','ANATOMICAL_INTERPRETATION_INVALIDATED','QUALIFICATION_VERDICT_NEEDS_REVALIDATION'],
 'Stage6A_qualification_status':'QUALIFICATION_VERDICT_NEEDS_REVALIDATION','Stage6B_qualification_status':'QUALIFICATION_VERDICT_NEEDS_REVALIDATION','Stage6_runs':0})
baseline={'execution':'CAP_DEPENDENCY_BLAST_RADIUS_AUDIT_R1','earliest_cap_authority_point':'Stage5A R2A old distal-cap selector/representative (R2 earlier tip-selection is predecessor evidence, not retroactively rewritten)',
 'earliest_cap_derived_production_data_change':'Stage5A R2A: THUMB_TIP_R.head/.tail, THUMB_IP_R.tail and align_roll for IP/TIP',
 'earliest_skin_implementation_dependency':'Stage5B R1 via actual R2A bind bone geometry','first_explicit_cap_membership_skin_write':'Stage5B R1A',
 'earliest_safe_rebuild_baseline':'Frozen Stage4C_R2 unskinned geometry/RSSF/nail/topology plus independently approved Stage5A hierarchy/origin/unrelated heads; exclude cap-derived R2A distal endpoint/frame slots pending targeted kinematic reconciliation',
 'full_R2A_rig_unconditional_reuse':False,'local_rig_dependency_revalidation_required':True,'local_rig_rebuild_condition':'Only if separate kinematic authority review determines a slot/frame change; membership freeze is not bone-driver approval',
 'unaffected_inheritable_assets':['Stage4A topology/UV/material/CMC cage geometry','Stage4B RSSF pose geometry','Stage4C approved nail face mask','Stage5A parent hierarchy and deform/nondeform group contract','Stage5A wrist/origin, CMC/MCP/IP heads and non-thumb joint heads not cap-derived'],
 'conditional_assets':{'R2A_THUMB_TIP_and_IP_tail_roll':'DIRECT CAP REPRESENTATIVE DEPENDENCY: targeted authority/kinematic revalidation before reuse','Stage5B_R1A_FIRST_WEB_21_membership_wrapper':'DIRECT cap-overridden ownership-boundary and cap-exclusion dependency; static targeted revalidation, not blanket first-web redesign','nail_weight_and_ownership_wrapper':'Revalidate cap/nail/ownership gates, approved Stage4 nail authority remains unchanged','R1E_CMC_cage_protection_wrapper':'Uses R3 label filter; static wrapper revalidation, cage geometry authority unchanged'},
 'R1B_preservation_and_reuse':{'status':'FROZEN HISTORICAL PRODUCTION MASTER','copy_non_cap_dependent_vector_entries':True,'candidate_rebuild_required':True,'original_file_overwrite_allowed':False,'verified_independent_vertex_count':W['no_cap_or_thumb_driver_dependency_proven_count']},
 'source_evidence':[ev('production_spec/stage5_production_rig/stage5a_r2a/scripts/s5a_r2a_build.py','L163–190,L245–260','REP old cap → real bone endpoint/frame writes'),ev('production_spec/stage5_production_rig/stage5b_r1/scripts/s5b_r1_bind.py','L206–210,L282,L344','Live actual bone positions influence weight generation'),ev('production_spec/stage5_production_rig/stage5b_r1a/scripts/r1a_common.py','L428–483','Explicit cap ownership drives skin and first-web selector')],
 'bone_hierarchy_or_joint_heads_reopened':False,'all_changes_deferred':True}
dump('EARLIEST_SAFE_REBUILD_BASELINE_AUDIT.json',baseline)
approvals=[{'approval':'Stage4 topology/RSSF/nail/CMC cage geometry','classification':'UNAFFECTED_HUMAN_APPROVAL','scope':'Independent upstream authority, no old-cap input'},
 {'approval':'Stage5A hierarchy/origin and unrelated heads','classification':'UNAFFECTED_HUMAN_APPROVAL','scope':'Preserved independent slots'},
 {'approval':'Historical THUMB_TIP stable-cap landmark/IP-tail frame','classification':'REVALIDATION_REQUIRED','scope':'Direct old-cap representative dependency'},
 {'approval':'OLD_CAP9 anatomical membership','classification':'SUPERSEDED_BY_CAP_CORRECTION','scope':'Settled native INDEX_SURFACE finding'},
 {'approval':'R1A/R1B cap-dependent skin, first-web selector wrapper','classification':'REVALIDATION_REQUIRED','scope':'Historical Human approval remains, no automatic corrected-data qualification'},
 {'approval':'R3 ownership','classification':'REVALIDATION_REQUIRED','scope':'HISTORICALLY_HUMAN_APPROVED; corrected anchor/seed/frame solve needed'},
 {'approval':'Stage6A R1A qualification','classification':'REVALIDATION_REQUIRED','scope':'Approval of old harness remains historical; future changed production needs qualification'},
 {'approval':'Manual/cap correction/boundary/five-vertex/cap37 freeze','classification':'UNAFFECTED_HUMAN_APPROVAL','scope':'Corrective approval chain unaffected; cap37 frozen hash preserved'},
 {'approval':'Earlier Q4=REMOVE five-vertex response','classification':'SUPERSEDED_BY_CAP_CORRECTION','scope':'Already superseded by exact final matching response; not reused'},
 {'approval':'R1C/R1D/R1E historical candidate verdicts','classification':'HISTORICAL_VERDICT_PRESERVED','scope':'No implied Human approval, no new PASS/FAIL issued'}]
dump('HUMAN_APPROVAL_DEPENDENCY_SCOPE_AUDIT.json',{'approvals':approvals,'original_responses_modified':False})
nodes=[];edges=[]
def node(id,label,cls,tier,dimension,status):nodes.append({'id':id,'label':label,'dependency_class':cls,'remediation_tier':tier,'contamination_dimension':dimension,'status':status})
def edge(a,b,type,evidence,counterfactual=False):edges.append({'from':a,'to':b,'edge_type':type,'evidence':evidence,'is_counterfactual_result':counterfactual})
node('UPSTREAM','Stage4 geometry / RSSF / nail / CMC cage','NO_CAP_DEPENDENCY','TIER_0','NONE','FROZEN INDEPENDENT')
node('OLD_CAP9','OLD_CAP9 / old R2A cap authority','DIRECT_DEPENDENCY','TIER_0','AUTHORITY_CONTAMINATION','SUPERSEDED_CONTAMINATED')
node('NEW_CAP37','NEW_CAP37 explicit frozen authority','NO_CAP_DEPENDENCY','TIER_0','NONE','HUMAN_APPROVED_FROZEN')
node('R2A_CAP_RIG','R2A TIP/IP-tail/frame slots','DERIVED_DEPENDENCY','TIER_2','IMPLEMENTATION_CONTAMINATION','TARGETED KINEMATIC REVALIDATION REQUIRED')
node('R1_SKIN','Stage5B R1 skin / bind matrices','DERIVED_DEPENDENCY','TIER_3','IMPLEMENTATION_CONTAMINATION','CAP-DERIVED RIG INPUT')
node('R1A_MASKS','R1A ownership / regions / first-web wrapper','DERIVED_DEPENDENCY','TIER_2','AUTHORITY_CONTAMINATION','RECOMPUTE/REVALIDATE')
node('R1A_SKIN','R1A skin: first explicit cap membership write','DERIVED_DEPENDENCY','TIER_3','IMPLEMENTATION_CONTAMINATION','HISTORICAL ONLY FOR CAP-DEPENDENT REUSE')
node('R1B_SKIN','R1B skin: protected cap carry-over','DERIVED_DEPENDENCY','TIER_3','IMPLEMENTATION_CONTAMINATION','FROZEN HISTORICAL MASTER')
node('R2_OWNERSHIP','R2 cap-centroid seed / domain','DIRECT_DEPENDENCY','TIER_2','AUTHORITY_CONTAMINATION','RECOMPUTE DERIVED INPUTS')
node('THUMB_STRONG_R3','THUMB_STRONG_R3: cap + live tube','DIRECT_DEPENDENCY','TIER_2','AUTHORITY_CONTAMINATION','OLD9 REDUNDANTLY PINNED')
node('R3_LABELS','R3 fields / mincut / closure / labels','DERIVED_DEPENDENCY','TIER_2','AUTHORITY_CONTAMINATION','R3_FULL_RECOMPUTE REQUIRED')
node('R3_BOUNDARY','R3 boundary / sheet / ambiguous / CLASS_A gates','DERIVED_DEPENDENCY','TIER_2','VALIDATOR_CONTAMINATION','COUNTERFACTUAL CHANGE UNRESOLVED')
for st in ['R1C','R1D','R1E']:node(st+'_SKIN',st+' candidate skin','DERIVED_DEPENDENCY','TIER_3','IMPLEMENTATION_CONTAMINATION','REBUILD REQUIRED FOR FUTURE REUSE; OLD VERDICT RETAINED')
node('STAGE6A','Stage6A harness / results / qualification','TRANSITIVE_DEPENDENCY','TIER_4','VALIDATOR_CONTAMINATION','NUMBERS RETAINED; REQUALIFY FUTURE DATA')
node('STAGE6B','Stage6B harness / results / qualification','TRANSITIVE_DEPENDENCY','TIER_4','VALIDATOR_CONTAMINATION','NUMBERS RETAINED; REQUALIFY FUTURE DATA')
node('CAP_VALIDATORS','Cap / dominance / drift / nail-cap / SI classifiers','VALIDATION_ONLY_DEPENDENCY','TIER_1','VALIDATOR_CONTAMINATION','RECONCILE FIXTURES / SEMANTICS')
node('STRICT_BOUNDS','Strict-bound/cap-to-collar audits','DIRECT_DEPENDENCY','TIER_2','AUTHORITY_CONTAMINATION','ANATOMICAL INTERPRETATION INVALIDATED')
node('ENDPOINT_REVIEWS','Endpoint authority reviews / recommendations','TRANSITIVE_DEPENDENCY','TIER_1','REPORTING_ONLY_CONTAMINATION','CAP-ENDPOINT CONCLUSIONS SUPERSEDED')
node('EDGE5879','edge5879 local weight partition defect','DERIVED_DEPENDENCY','TIER_1','IMPLEMENTATION_CONTAMINATION','PARTLY_CAP_DERIVED; NUMERIC EVIDENCE RETAINED')
node('MANUAL_REVIEWS','Manual anatomical / cap correction Human chain','DIRECT_DEPENDENCY','TIER_0','REPORTING_ONLY_CONTAMINATION','CORRECTIVE PROVENANCE; APPROVALS RETAINED')
node('STATUS_REPORTS','Freeze/status/report qualification propagation','TRANSITIVE_DEPENDENCY','TIER_1','REPORTING_ONLY_CONTAMINATION','HISTORICAL FACTS; CURRENT REUSE QUALIFICATION REQUIRES REVIEW')
edge('UPSTREAM','OLD_CAP9','DIRECT_INPUT','R2A selector uses posed geometry/nearest-chain domain; upstream geometry itself not contaminated')
edge('OLD_CAP9','R2A_CAP_RIG','DIRECT_INPUT','s5a_r2a_build.py L163–190,L245–260')
edge('R2A_CAP_RIG','R1_SKIN','WEIGHT_AUTHORITY','s5b_r1_bind.py live BH/BT mu distances')
edge('OLD_CAP9','R1A_MASKS','DIRECT_INPUT','r1a_common.py L428–483')
edge('R1_SKIN','R1A_SKIN','DIRECT_INPUT','s5b_r1a_build.py reads R1 weights and frozen groups')
edge('R1A_MASKS','R1A_SKIN','WEIGHT_AUTHORITY','R1A authorised masks/free-budget vector writes')
edge('R1A_MASKS','R1B_SKIN','WEIGHT_AUTHORITY','r1b_common.py L127–149 cap/ownership/protected exclusion')
edge('R1A_SKIN','R1B_SKIN','DIRECT_INPUT','R1B reads R1A; old cap excluded from modification')
edge('OLD_CAP9','R2_OWNERSHIP','DIRECT_INPUT','s6br1b_common.py L177–181 cap-centroid seed')
edge('R2A_CAP_RIG','THUMB_STRONG_R3','DIRECT_INPUT','R3 live bone polyline tube, all old9 also tube anchors')
edge('OLD_CAP9','THUMB_STRONG_R3','DIRECT_INPUT','r3_ownership.py L176–220 CAP union')
edge('THUMB_STRONG_R3','R3_LABELS','DERIVED_LABEL','R3 distance fields + INF hard pins + pairwise mincut + closure')
edge('R2_OWNERSHIP','R3_LABELS','DERIVED_LABEL','R3 initial R2 domain/list and candidate graph')
edge('R3_LABELS','R3_BOUNDARY','DERIVED_LABEL','Derived cut edges and sheet / ambiguous / CLASS_A validation')
for st in ['R1C','R1D']:edge('R2_OWNERSHIP',st+'_SKIN','WEIGHT_AUTHORITY',st+' ownership repair/interpolation or distal continuity')
for st in ['R1C','R1D','R1E']:edge('R1B_SKIN',st+'_SKIN','DIRECT_INPUT','Each candidate rebased from frozen R1B, not serially from failed prior candidate')
edge('R3_LABELS','R1E_SKIN','WEIGHT_AUTHORITY','R1E allowed family/region and live-axis profiles')
edge('R3_BOUNDARY','R1E_SKIN','WEIGHT_AUTHORITY','R1E palm_share collar valley')
edge('OLD_CAP9','R1E_SKIN','WEIGHT_AUTHORITY','CAP clamp excludes old cap from palm share')
edge('R1A_SKIN','STAGE6A','DIRECT_INPUT','Stage6A R1 source R1A')
edge('R1B_SKIN','STAGE6A','DIRECT_INPUT','Stage6A R1A source R1B')
edge('R1C_SKIN','STAGE6A','DIRECT_INPUT','Stage6A R1B source R1C (operative code override)')
edge('R1B_SKIN','STAGE6B','DIRECT_INPUT','Stage6B R1 source R1B')
edge('R1C_SKIN','STAGE6B','DIRECT_INPUT','Stage6B R1B source R1C (operative code override)')
edge('OLD_CAP9','CAP_VALIDATORS','VALIDATION_ONLY','Cap fixture / nail-cap metrics / semantic protection gates')
edge('R3_LABELS','CAP_VALIDATORS','VALIDATION_ONLY','Ownership bucket / R3 collar metrics / no-touch guards')
edge('OLD_CAP9','STRICT_BOUNDS','DIRECT_INPUT','old nine endpoint A vertices and claimed true-cap path')
edge('R3_BOUNDARY','STRICT_BOUNDS','DIRECT_INPUT','exact R3 collar endpoint B')
edge('R1E_SKIN','STRICT_BOUNDS','DIRECT_INPUT','Historical posed endpoints/motion at fixed vertex IDs')
edge('STRICT_BOUNDS','ENDPOINT_REVIEWS','REPORTING_REFERENCE','13.1646/5.9643/6.5160 and legality/mesh-limit decisions')
edge('R1E_SKIN','EDGE5879','DIRECT_INPUT','Saved edge1551–3125 weights and actual ratio11.0412867')
edge('OLD_CAP9','MANUAL_REVIEWS','REPORTING_REFERENCE','Old cap is audit target, never a truth/selector source for native corrective identity')
edge('MANUAL_REVIEWS','NEW_CAP37','HUMAN_APPROVAL','Native region → E → five-vertex approval → explicit membership freeze')
for src in ['STAGE6A','STAGE6B','CAP_VALIDATORS','STRICT_BOUNDS','R3_LABELS']:edge(src,'STATUS_REPORTS','REPORTING_REFERENCE','Inherited measurement/gate/verdict; scope-specific review needed')
# The recovery DAG is separate from historical provenance: no backwards current-authority edge creates a cycle.
ids={n['id'] for n in nodes};indeg={x:0 for x in ids};adj=defaultdict(list)
for e in edges:assert e['from'] in ids and e['to'] in ids;indeg[e['to']]+=1;adj[e['from']].append(e['to'])
queue=deque(sorted(k for k,v in indeg.items() if v==0));order=[]
while queue:
 x=queue.popleft();order.append(x)
 for v in adj[x]:
  indeg[v]-=1
  if indeg[v]==0:queue.append(v)
assert len(order)==len(nodes),'Historical dependency graph must remain a DAG'
graph={'graph_id':'CAP_DEPENDENCY_GRAPH_R1','authority_hash':HASH,'graph_kind':'HISTORICAL_DEPENDENCY_PROVENANCE_DAG','nodes':nodes,'edges':edges,'acyclic':True,'topological_order':order,
 'dependency_edges_are_source_provenance_not_quantified_counterfactual_effects':True,'artifact_inventory':'CAP_DIRECT_REFERENCE_AUDIT.json','artifact_counting_unit':'Unique existing file; component nodes counted separately, never mixed into artifact counts'}
dump('CAP_DEPENDENCY_DAG.json',graph)
dump('CAP_DEPENDENCY_GRAPH_R1.json',graph)
tiers={'tier_definitions':{'TIER_0':'NO ACTION on independent assets or retain historical/corrective provenance','TIER_1':'STATIC REVALIDATION ONLY of fixtures/semantics/report current-use eligibility','TIER_2':'RECOMPUTE DERIVED AUTHORITY/input context; no blend rebuild yet','TIER_3':'REBUILD WEIGHTS / DATA after independent authority gates','TIER_4':'FULL DEFORMATION REQUALIFICATION after rebuilt production'},
 'counting_unit':'Unique preexisting file from inventory; one future-reuse remediation tier per artifact, not rewrite instructions',
 'tier_counts':I['remediation_tier_counts'],'artifact_assignments':[{'path':x['path'],'tier':x['remediation_tier'],'dependency_class':x['dependency_class']} for x in I['artifact_classification']],
 'component_tiers':[{'node_id':n['id'],'tier':n['remediation_tier'],'status':n['status']} for n in nodes],
 'historical_files_overwritten':False,'actions_executed':False}
dump('CAP_CORRECTION_REMEDIATION_TIERS.json',tiers)
steps=[
 {'step':1,'task':'CAP_DERIVED_THUMB_KINEMATIC_AUTHORITY_REVALIDATION_R1','tier':'TIER_1','purpose':'Resolve R2A old-cap representative → THUMB_TIP/IP-tail/roll authority dependency and preserve unrelated hierarchy/heads','gate':'No automatic tip/bone endpoint from cap37 membership; obtain separate kinematic/driver authority if change is required','depends_on':[]},
 {'step':2,'task':'CAP_DERIVED_R2_R3_INPUT_RECONCILIATION_R1','tier':'TIER_2','purpose':'Reconcile native digit seed, live tube anchors, old-cap overlap and first-web/nail/cage wrapper semantics','gate':'Removing explicit CAP union alone must not leave old9 pinned as tube anchors; cap37 remains exact hash','depends_on':[1]},
 {'step':3,'task':'R3_FULL_RECOMPUTE_AND_AUTHORITY_REVALIDATION_R1','tier':'TIER_2','purpose':'Recompute coupled two-digit fields/mincut/closure/labels/boundary/sheet and validate CLASS_A/R2 comparisons','gate':'Separate authority review; no inherited no-change assumption','depends_on':[2]},
 {'step':4,'task':'CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1','tier':'TIER_2','purpose':'Resolve thumb cap skin driver values, native INDEX old9 corrections and region/whitelist/protection conflicts','gate':'No automatic THUMB_IP_R=1 vector inheritance to cap37; preserve independently verified other-region vectors','depends_on':[1,3]},
 {'step':5,'task':'TARGETED_RIG_AND_SKIN_DATA_REBUILD_AFTER_APPROVAL','tier':'TIER_3','purpose':'If kinematic slots change, update only approved slots; build corrected skin from clean unskinned baseline plus proven independent weight entries','gate':'New separate candidate, original R1B and R1C/D/E stay historical; no R1F created by this audit','depends_on':[4]},
 {'step':6,'task':'CAP_FIXTURE_STATIC_VALIDATION_AND_TARGETED_DEFORMATION','tier':'TIER_1 → TIER_4','purpose':'Update explicit cap/ownership fixtures, test former old9 region, true cap37, first-web continuity, edge5879 and corrected collar','gate':'Numeric/semantic checks pass before full qualification; old bound is not an anatomy constraint','depends_on':[5]},
 {'step':7,'task':'TRUE_CAP_BOUND_RECOMPUTE_AFTER_DEPENDENCY_RECONCILIATION','tier':'TIER_2','purpose':'Compute new true-cap endpoint/path bounds only against settled rig/ownership/skin semantics','gate':'Static fixtures and targeted checks passed; R3, skin driver and rebuilt endpoint data fixed; strict-bound recompute is not run here','depends_on':[3,4,5,6]},
 {'step':8,'task':'FULL_STAGE6A_REQUALIFICATION','tier':'TIER_4','purpose':'Full isolated-flexion suite and independent-region regression on new production','gate':'Historical approval remains; new qualification required','depends_on':[6]},
 {'step':9,'task':'FULL_STAGE6B_REQUALIFICATION','tier':'TIER_4','purpose':'Full opposition/contact/self-intersection/severe-edge qualification with corrected semantics','gate':'No cap-bound-based legacy recommendation carried forward without recomputed evidence','depends_on':[7,8]}]
dump('CAP_CORRECTION_RECOVERY_SEQUENCE_R1.json',{'sequence_id':'CAP_CORRECTION_RECOVERY_SEQUENCE_R1','steps':steps,'reason_not_mechanically_R3_first':'R3 live tube/axis inputs and R2 cap-centroid seed depend on actual old-cap-derived R2A rig; resolving input authority precedes a meaningful solve',
 'NEXT':steps[0]['task'],'executed_steps':[],'production_rebuild_started':False,'strict_bound_recompute_timing':'After steps3–5 dependency reconciliation, before endpoint-anatomy final qualification; may run alongside full Stage6A after targeted static checks','STOP':True})
print(json.dumps({'DAG_nodes':len(nodes),'DAG_edges':len(edges),'acyclic':True,'stage6_skin_sources':[(a,c) for a,b,c,d,e in lineage],'NEXT':steps[0]['task'],'rebuild_started':False}))
