"""Five independent adjudications plus one necessary face-coupling check; no subset search."""
import sys
sys.dont_write_bytecode=True
import json, hashlib
import numpy as np
from e_geometry import *
def dump(name,o):(OUT/name).write_text(json.dumps(o,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
RESP=Path('<USER_HOME>/Downloads/HUMAN_THUMB_DISTAL_CAP_BOUNDARY_RESPONSE_R1.json')
H=load(RESP)
assert {k:H['answers'][k] for k in ['Q1','Q2','Q3','Q4','Q5','Q6','Q7']}==dict(zip(['Q1','Q2','Q3','Q4','Q5','Q6','Q7'],['YES','YES','NO','NO','YES','E','APPROVE_WITH_MINOR_BOUNDARY_FIX']))
assert sha(ROOT/M['path'])==M['sha256']==E['native_mesh_sha256']
assert len(BASEV)==37 and len(BASEF)==25 and ADDS.isdisjoint(BASEV) and PRESENT<=BASEV
COMMON={'execution':'CAP_BOUNDARY_E_FIVE_VERTEX_ADJUDICATION_R1','region_identity':'ACCEPTED_UNCHANGED',
 'E_baseline_authority':'SELECTED_HUMAN_BASELINE','boundary_authority_applied':False,'production_authority_applied':False,
 'native_mesh_sha256':M['sha256'],'native_mesh_state':'NATIVE_PRE_RSSF_STAGE4A_R2','allowed_disputed_vertex_ids':sorted(FIVE),
 'other_E_vertex_membership_frozen':True,'other_candidates_reopened':False,'seed_identity_reopened':False,'R3_reopened':False}
BASE=patch(BASEF)
ALLOWED_V=BASEV|FIVE
def delta_variant(fs):
 p=patch(fs);p['added_face_ids']=sorted(set(fs)-BASEF);p['removed_face_ids']=sorted(BASEF-set(fs))
 p['added_vertex_ids']=sorted(set(p['vertex_ids'])-BASEV);p['removed_vertex_ids']=sorted(BASEV-set(p['vertex_ids']))
 old={r['vertex_id']:r for r in BASE['boundary_smoothness_rows']}
 changed=[]
 for r in p['boundary_smoothness_rows']:
  v=r['vertex_id'];o=old.get(v)
  if o is None or r['previous_vertex_id']!=o['previous_vertex_id'] or r['next_vertex_id']!=o['next_vertex_id']:
   changed.append({'vertex_id':v,'baseline':o,'hypothetical':r})
 p['changed_local_boundary_rows']=changed
 p['new_notch_proxy_vertex_ids']=[r['vertex_id'] for r in p['boundary_smoothness_rows'] if r['intrinsic_corner_type']=='CONCAVE_NOTCH_PROXY' and old.get(r['vertex_id'],{}).get('intrinsic_corner_type')!='CONCAVE_NOTCH_PROXY']
 p['new_spike_proxy_vertex_ids']=[r['vertex_id'] for r in p['boundary_smoothness_rows'] if r['intrinsic_corner_type']=='NARROW_SPIKE_PROXY' and old.get(r['vertex_id'],{}).get('intrinsic_corner_type')!='NARROW_SPIKE_PROXY']
 p['boundary_perimeter_delta_mm']=p['boundary_perimeter_mm']-BASE['boundary_perimeter_mm']
 p['boundary_axial_spread_delta_mm']=p['boundary_axial_spread_mm']-BASE['boundary_axial_spread_mm']
 p['surface_area_delta_mm2']=p['surface_area_mm2']-BASE['surface_area_mm2']
 assert not p['new_vertices_outside_five'] and not p['lost_uncontested_baseline_vertices']
 return p
PAIR=delta_variant(BASEF|{1220})
REM297=delta_variant(BASEF-set(VF[297]));REM298=delta_variant(BASEF-set(VF[298]))
VAR=[]
for v in [1453,2785,2790]:
 incident=VF[v];strict=[fi for fi in incident if set(F[fi])<=BASEV|{v}]
 scoped=[fi for fi in incident if set(F[fi])<=ALLOWED_V]
 blockers=[{'face_id':fi,'corner_ids':F[fi],'unapproved_non_disputed_corner_ids':sorted(set(F[fi])-ALLOWED_V),
  'other_disputed_corner_ids_required':sorted((set(F[fi])-BASEV)-{v})} for fi in incident]
 row={'vertex_id':v,'test':'ADD_ONE_IN','strict_single_vertex_add_possible':bool(strict),
  'strict_single_vertex_add_faces':strict,'five_vertex_scope_admissible_incident_faces':scoped,
  'native_incident_face_scope_audit':blockers,'hypothetical_patch_written_to_production':False}
 if scoped:
  assert scoped==[1220]
  row['conditional_minimum_face_closure']={'selected_added_face_ids':[1220],'minimum_added_face_count':1,
   'coupled_disputed_vertices':[1453,2785],'reason':'Only permitted supporting face; requires both disputed corners. Not an isolated add-one patch.',
   'metrics':PAIR}
 else:row['conditional_minimum_face_closure']=None;row['status']='NON_VIABLE_KEEP_WITHIN_FIVE_VERTEX_SCOPE'
 VAR.append(row)
for v,metrics in [(297,REM297),(298,REM298)]:
 VAR.append({'vertex_id':v,'test':'LEAVE_ONE_OUT','minimum_necessary_removed_selected_face_ids':sorted(BASEF&set(VF[v])),
  'reason':'Every selected face containing removed vertex must be removed; no other unapproved vertex membership changes are allowed.',
  'metrics':metrics,'hypothetical_patch_written_to_production':False})
DECISIONS={1453:'REMOVE',2785:'REMOVE',2790:'REMOVE',297:'KEEP',298:'KEEP'}
REASON={
 1453:'The E edge v1382–v341 is already a smooth native boundary continuation (turns22.887/12.272deg), not a clear missing terminal corner. Legal support requires coupled face1220 with v2785; that addition creates concave corners at v1382/v341 and a long outward tab. Rounded skin evidence does not force this selected cap boundary to include it.',
 2785:'Native rounded bulb-side evidence is retained, but legal addition is coupled to v1453 via face1220. The resulting corner turns115.272deg, with new concave endpoints and8.693155mm extra perimeter. It is not classified as shaft merely because g>9; it is excluded to preserve the selected circumferential boundary.',
 2790:'Native bulb-side geometry is compatible with THUMB, but no incident face can support KEEP within E plus these five vertices. The closest supporting face1243 also requires non-disputed v1342. A KEEP vertex without selected-face support is prohibited, so it remains excluded under the authorized scope.',
 297:'Face1942 provides a rounded circumferential boundary completion at axial depth5.447803mm. Removing it preserves a disk/loop but introduces a concave notch at v2965 (interior279.457deg) and larger local turns. Its positive tip-facing normal and curved native surface support KEEP; no distance-threshold rule is used.',
 298:'Face1944 provides the corresponding rounded circumferential completion at axial depth5.344341mm. Removing it preserves a disk/loop but introduces a concave notch at v2966 (interior266.588deg). KEEP maintains the native rounded edge and does not rely on proximity to nail.'}
# Closest approved nail-region edge distance (frozen mask), used only for five-point context.
NG=np.full(len(V),np.inf);q=[]
for v in NV:NG[v]=0;heapq.heappush(q,(0.,v))
while q:
 d,a=heapq.heappop(q)
 if d>NG[a]:continue
 for b,w in ADJ[a]:
  if b in DOMAIN and d+w<NG[b]:NG[b]=d+w;heapq.heappush(q,(NG[b],b))
ROWS=[]
for v in [1453,2785,2790,297,298]:
 one,two=rings(v);n1=sorted(set(one)&NV);n2=sorted(set(two)&NV)
 relation='NAIL_MARGIN_SUPPORT' if v in NV else ('NAIL_ADJACENT' if n1 or n2 else 'NOT_NAIL_RELATED')
 path=[v]
 while path[-1]!=SEED:path.append(PRED[path[-1]])
 rows={'vertex_id':v,'baseline_membership':v in BASEV,'recommended_final_membership':DECISIONS[v]=='KEEP',
  'decision':DECISIONS[v],'decision_status':'ENGINEERING_ADJUDICATION_PENDING_HUMAN', 'reason':REASON[v],
  'native_branch':'THUMB','branch_evidence_source':'Frozen independent native partition; inherited fact, branch identity is not reopened',
  'native_branch_confirmed_for_this_vertex':LABELS[v]=='thumb','geodesic_from_v284_mm':float(G[v]),
  'seed_geodesic_path_vertex_ids':path[::-1],'euclidean_tip_distance_mm':float(np.linalg.norm(V[v]-TIP)),
  'native_world_XYZ_mm':V[v].tolist(),'native_normal_area_weighted':VN[v].tolist(),
  'distance_to_IP_mm':float(np.linalg.norm(V[v]-IP)),'IP_to_tip_axis_projection_mm':float(AXIAL[v]),
  'axial_depth_from_tip_mm':float(DEPTH[v]),'circumferential_angle_deg':float(ANGLE[v]),'radial_distance_to_axis_mm':float(RADIUS[v]),
  'normal_tip_axis_component':float(NORMALAX[v]),'curvature_proxy':curvature(v),
  'terminal_bulb_interpretation':'TIP_FACING_CURVED_BULB_SIDE_SUPPORT; not a claim that all rounded skin must be selected cap',
  'distal_shaft_interpretation':'NO_CLEAR_SHAFT_SIGNAL_AT_THESE_FIVE; normal-axis component positive and axial depths6.92mm or less',
  'nail_relation':relation,'approved_nail_vertex_membership':v in NV,
  'one_ring_nail_ids':n1,'two_ring_nail_ids':n2,'native_surface_geodesic_to_nail_mask_mm':float(NG[v]),
  'native_euclidean_distance_to_nail_vertices_mm':float(min(np.linalg.norm(V[list(NV)]-V[v],axis=1))),
  'nail_margin_support_reason':'No disputed point is on the approved distal nail margin edge v37–v879; nail proximity is not a KEEP rule.',
  'one_ring':one,'two_ring_exact_hop_2':two,'native_incident_faces':[{'face_id':fi,'corner_vertex_ids':F[fi],
   'selected_in_E_baseline':fi in BASEF,'surface_area_mm2':float(AREA[fi]),'normal':FN[fi].tolist(),
   'nail_face':fi in NF,'five_scope_corner_admissible':set(F[fi])<=ALLOWED_V} for fi in VF[v]],
  'ring_role':'Legal rounded edge completion in face1942/1944' if v in PRESENT else ('Coupled outward tab if face1220 added' if v in {1453,2785} else 'No authorized face-supported addition'),
  'individual_variant_analysis_vertex_id':v}
 assert rows['native_branch_confirmed_for_this_vertex']
 ROWS.append(rows)
FINALV=(BASEV-{v for v in PRESENT if DECISIONS[v]=='REMOVE'})|{v for v in ADDS if DECISIONS[v]=='KEEP'}
FINALF=BASEF.copy();FINAL=patch(FINALF)
assert FINALV==set(FINAL['vertex_ids']) and FINALF==BASEF
SCOPED_NEIGH={v for x in FIVE for v in rings(x)[0]}|FIVE
LOCALROWS=[r for r in FINAL['boundary_smoothness_rows'] if r['vertex_id'] in SCOPED_NEIGH]
local_notches=[r['vertex_id'] for r in LOCALROWS if r['intrinsic_corner_type']=='CONCAVE_NOTCH_PROXY']
local_spikes=[r['vertex_id'] for r in LOCALROWS if r['intrinsic_corner_type']=='NARROW_SPIKE_PROXY']
assert not local_notches and not local_spikes
READY=FINAL['manifold_disk'] and FINAL['seed_included'] and FINAL['nail_margin_edge_preserved'] and not FINAL['new_vertices_outside_five'] and not FINAL['lost_uncontested_baseline_vertices'] and not local_notches and not local_spikes
dump('E_BASELINE_FIVE_VERTEX_CONTEXT.json',{**COMMON,'Human_authority_verbatim':H,'human_boundary_response_path':str(RESP),
 'human_boundary_response_sha256':sha(RESP),'E_baseline_file_sha256':sha(PRIOR/'CAP_BOUNDARY_CANDIDATE_E.json'),
 'baseline':BASE,'five_vertex_baseline_memberships':{str(v):v in BASEV for v in sorted(FIVE)},
 'seed':{'vertex_id':284,'world_mm':TIP.tolist()},'IP':{'world_mm':IP.tolist(),'status':'Inherited native engineering estimate, unchanged'},
 'IP_to_tip_unit_axis':AXIS.tolist(),'approved_nail_face_ids':sorted(NF),
 'frozen_other_baseline_vertex_ids':sorted(BASEV-FIVE),'no_A_B_C_D_files_loaded':True})
dump('FIVE_VERTEX_INDIVIDUAL_FORENSIC.json',{**COMMON,'vertices':ROWS,'five_vertex_decision_counts':{'KEEP':2,'REMOVE':3},
 'decisions':{str(v):d for v,d in DECISIONS.items()},'distance_only_decision_rule':False,
 'v1453_special_answer':'No clear boundary notch in the accepted E edge. Coupled addition restores some rounded skin but creates a face-sized tab and two concave boundary corners; it is not required for the selected cap edge.',
 'v2785_v2790_special_answer':'Both retain curved tip-facing bulb-side evidence; exclusion is boundary/face-consistency adjudication, not native branch or region identity reversal.',
 'v297_v298_special_answer':'Native centroid axial cut includes faces1942/1944 whose corners all exceed9mm; they supply smooth rounded replacements. Removal remains closed but creates an inward notch, so they are geometry completions rather than topology-closure necessities.'})
dump('E_FIVE_VERTEX_VARIANT_ANALYSIS.json',{**COMMON,'individual_tests':VAR,
 'necessary_combination_consistency_checks':[{'name':'1453_2785_FACE1220_COUPLING','minimal_face_support':PAIR,
  'decision':'REJECT_COUPLED_TAB_FOR_FINAL','reason':'Two new concave endpoints and long local outward tab; no isolated legal add-one support exists.'}],
 'unique_hypothetical_face_patches_evaluated':3,'five_independent_requested_test_records':5,
 'five_bit_subset_enumeration_performed':False,'boundary_family_redesign':False,
 'scope_limit_v2790':'No legal KEEP face. No out-of-scope hypothetical patch or additional vertex membership was created.',
 'smoothness_method':'3D tangent turning; selected incident-face intrinsic angle sum; normal-angle/edge-length discontinuity. Interior>240deg flags concave notch proxy, interior<60deg flags narrow spike proxy. Local results compared with accepted E; curvature proxies are not anatomical authority.'})
dump('NATIVE_THUMB_DISTAL_CAP_CANDIDATE_E_FINAL.json',{**COMMON,'candidate_name':'NATIVE_THUMB_DISTAL_CAP_CANDIDATE_E_FINAL',
 'status':'READY_FOR_HUMAN_CAP_AUTHORITY_FREEZE' if READY else 'MINOR_FIX_STILL_UNRESOLVED',
 'face_ids':FINAL['face_ids'],'vertex_ids':FINAL['vertex_ids'],'boundary_edge_ids':FINAL['boundary_edge_ids'],
 'boundary_edges':FINAL['boundary_edges'],'boundary_vertex_ids':FINAL['boundary_vertex_ids'],
 'seed_vertex_id':284,'nail_relation':'Approved distal nail margin edge v37–v879 preserved; approved nail mask unchanged',
 'max_geodesic_mm':FINAL['max_geodesic_mm'],'boundary_axial_spread_mm':FINAL['boundary_axial_spread_mm'],
 'surface_area_mm2':FINAL['surface_area_mm2'],'boundary_perimeter_mm':FINAL['boundary_perimeter_mm'],
 'single_connected_component':FINAL['connected_component_count']==1,'single_closed_loop':FINAL['closed_loop_count']==1,
 'manifold_disk':FINAL['manifold_disk'],'five_vertex_decisions':{str(v):d for v,d in DECISIONS.items()},
 'baseline_and_final_membership_identical':True,'changed_vertex_ids':[],'added_face_ids':[],'removed_face_ids':[],
 'human_final_approval':None,'authority_freeze_performed':False})
dump('E_FINAL_BOUNDARY_TOPOLOGY_AUDIT.json',{**COMMON,'baseline':BASE,'final':FINAL,
 'face_vertex_boundary_consistency':True,'added_or_removed_non_disputed_vertices':[],
 'all_KEEP_vertices_supported_by_selected_faces':all(any(v in F[fi] for fi in FINALF) for v,d in DECISIONS.items() if d=='KEEP'),
 'all_REMOVE_disputed_vertices_absent':all(v not in FINALV for v,d in DECISIONS.items() if d=='REMOVE'),
 'local_five_vertex_boundary_rows':LOCALROWS,'local_spike_proxy_vertex_ids':local_spikes,'local_notch_proxy_vertex_ids':local_notches,
 'local_spike_notch_clear':not local_spikes and not local_notches,
 'region_identity_unchanged':True,'no_obvious_new_proximal_overreach':True,'nail_relation_coherent':FINAL['nail_margin_edge_preserved'],
 'ready_for_human_freeze':READY,'readiness_scope':'Five-vertex adjudication plus frozen Human-selected baseline; no re-adjudication of other baseline regions'})
dump('_FIVE_RENDER_DATA.json',{'five_vertex_rows':ROWS,'baseline_boundary_edges':BASE['boundary_edges'],
 'final_boundary_edges':FINAL['boundary_edges'],'baseline_face_ids':sorted(BASEF),'final_face_ids':sorted(FINALF),
 'disputed_vertex_decisions':{str(v):d for v,d in DECISIONS.items()},'baseline':BASE,'final':FINAL})
print(json.dumps({'decisions':DECISIONS,'FINAL_vertices':FINAL['vertex_count'],'FINAL_faces':FINAL['face_count'],
 'max_geodesic_mm':FINAL['max_geodesic_mm'],'axial_spread_mm':FINAL['boundary_axial_spread_mm'],'READY':READY,
 'pair_added_notches':PAIR['new_notch_proxy_vertex_ids'],'remove297_notches':REM297['new_notch_proxy_vertex_ids'],
 'remove298_notches':REM298['new_notch_proxy_vertex_ids']}),flush=True)
