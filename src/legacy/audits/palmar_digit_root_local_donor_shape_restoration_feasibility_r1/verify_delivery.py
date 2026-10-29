import sys
sys.dont_write_bytecode=True
from common import *
from html.parser import HTMLParser
from urllib.parse import unquote
from PIL import Image
import numpy as np
before=read(OUT/'FROZEN_HASHES_BEFORE.json');after=inventory();changed=[k for k,h in before.items() if after.get(k)!=h];added=[k for k in after if k not in before]
dump('FROZEN_HASHES_AFTER.json',after)
initial=read(OUT/'HUMAN_RESPONSE_HASH_BEFORE.json');response_current=ref(RESPONSE) if RESPONSE.is_file() else None;response_ok=(response_current==initial['current_source']) if initial['current_external_source_present'] else not RESPONSE.is_file()
drift={'status':'PASS' if not changed and not added and response_ok else 'FAIL','preexisting_workspace_file_count':len(before),'changed_or_missing_preexisting_workspace_files':changed,'new_files_outside_this_feasibility_directory':added,'PRODUCTION_DRIFT':len(changed),'current_external_response_present_at_start':initial['current_external_source_present'],'current_external_response_present_at_end':RESPONSE.is_file(),'external_response_changed_during_round':not response_ok,'response_byte_verification':'PASS' if initial['current_external_source_present'] and response_ok else 'UNAVAILABLE_MISSING_AT_START; no response creation/write/deletion','prior_response_hold_receipt_byte_preserved':sha(PRIOR/'CURRENT9_HUMAN_RESPONSE_HOLD_VERIFICATION_R1.json')==initial['prior_byte_preservation_receipt']['sha256'],'CURRENT_9_CROSSING_HUMAN_RESPONSE':'HOLD_NOT_CLOSED','production_geometry_normal_weight_rig_joint_material_modifier_writes':0,'formal_APPLY':False,'Stage5_propagation_runs':0,'Full42_runs':0,'Stage6_runs':0,'deformation_qualification_runs':0,'pose_smoke_runs':0,'true_cap_recomputation_runs':0,'Stage6B_runs':0,'production_promotion':False}
dump('PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',drift);assert not changed and not added and response_ok and drift['prior_response_hold_receipt_byte_preserved']
required=[PHASE+'_REPORT.md',PHASE+'_STATUS.json','PALMAR_ROOT_HUMAN_TARGET_LOCK_R1.json','PALMAR_ROOT_DEFECT_CORE_R1.json','PALMAR_ROOT_EXCLUDED_NORMAL_CONTEXT_R1.json','PALMAR_ROOT_SOURCE_ANCESTRY_R1.json','PALMAR_ROOT_DONOR_SOURCE_COMPARISON_R1.json','PALMAR_ROOT_DONOR_TARGET_COORDINATES_R1.json','PALMAR_ROOT_TRANSFER_SCOPE_R1.json','PALMAR_ROOT_TRANSFER_STRUCTURE_AUDIT_R1.json','PALMAR_ROOT_NORMAL_CONTEXT_PROTECTION_AUDIT_R1.json','PALMAR_ROOT_CURRENT9_INDEPENDENCE_R1.json','PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json','review.html','TEMP_PALMAR_ROOT_DONOR_TRANSFER_PROBE_R1.blend']
assert all((OUT/p).is_file() for p in required)
for p in OUT.glob('*.json'):read(p)
class Links(HTMLParser):
 def __init__(self):super().__init__();self.paths=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ['href','src']:self.paths.append(v)
links=Links();links.feed((OUT/'review.html').read_text(encoding='utf-8'));broken=[p for p in links.paths if not (OUT/unquote(p)).is_file()];assert not broken,broken
pngs=list(OUT.rglob('*.png'));sizes={}
for p in pngs:
 with Image.open(p) as im:im.verify()
 with Image.open(p) as im:sizes[p.relative_to(OUT).as_posix()]=list(im.size)
P=read(OUT/'TEMP_PALMAR_ROOT_DONOR_TRANSFER_PROBE_R1.json');scope=read(OUT/'PALMAR_ROOT_TRANSFER_SCOPE_R1.json');core=read(OUT/'PALMAR_ROOT_DEFECT_CORE_R1.json');normal=read(OUT/'PALMAR_ROOT_EXCLUDED_NORMAL_CONTEXT_R1.json');status=read(OUT/(PHASE+'_STATUS.json'));audit=read(OUT/'PALMAR_ROOT_TRANSFER_STRUCTURE_AUDIT_R1.json');protected=read(OUT/'TEMP_PROBE_PAYLOAD_PRESERVATION_R1.json');src=read(OUT/'PALMAR_ROOT_SOURCE_ANCESTRY_R1.json');sections=read(OUT/'PALMAR_ROOT_NATIVE_CROSS_SECTIONS_R1.json');ind=read(OUT/'PALMAR_ROOT_CURRENT9_INDEPENDENCE_R1.json');manifest=read(OUT/'MATCHED_RENDER_MANIFEST_R1.json')
assert audit['status']=='PASS' and audit['NEW_TRUE3D_DEFECT_COUNT']==0 and audit['face_reversal_count']==0
assert protected['all_protected_payloads_exact'] and protected['bone_count']==21
assert set(P['moved_vertex_ids'])==set(range(3348,3364))
assert not set(core['vertex_ids'])&set(normal['vertex_ids']) and not set(core['face_ids'])&set(normal['face_ids'])
assert not set(P['moved_vertex_ids'])&set(normal['vertex_ids'])
assert scope['DEFECT_CORE_COUNT']+scope['ANCESTRY_CLOSURE_COUNT']+scope['TRANSITION_CONTEXT_COUNT']==scope['TOTAL_TRANSFER_PROBE_WRITE_COUNT']==16
assert np.array_equal(np.array(P['world_mm'])[normal['vertex_ids']],np.array(P['baseline_world_mm'])[normal['vertex_ids']])
assert all(len(z)>0 for st in sections['states'].values() for z in st.values())
assert ind['CURRENT9_WRITESET_DIRECT_OVERLAP_COUNT']==ind['CURRENT9_WRITESET_NEIGHBORHOOD_OVERLAP_COUNT']==0
assert status['VERDICT']=='PASS_LOCAL_DONOR_SHAPE_RESTORATION_FEASIBLE' and not status['NEXT_EXECUTED'] and not status['formal_APPLY']
assert len(manifest['records'])==43 and all(r['pose_setters']==0 and not r['qualified_asset_loaded'] for r in manifest['records'])
for view in ['HUMAN_CAMERA','CLOSE','ALTERNATE']:
 for style in ['SOLID','GRAZING','FLAT_SOURCE_NATIVE']:
  rows=[r for r in manifest['records'] if r['view']==view and r['style']==style and r['state'] in ['CURRENT_RAW','TRANSFER_PROBE','OFFICIAL_L1_RSSF_DISPLAY']];assert len(rows)==3
  assert all(r['camera_matrix']==rows[0]['camera_matrix'] and r['orthographic_width_m']==rows[0]['orthographic_width_m'] and r['studio_rotation_z']==rows[0]['studio_rotation_z'] for r in rows)
S=read(SOURCE/'RAW_SOURCE_GEOMETRY.json')['stages'];assert S['OFFICIAL_L1']['canonical_world_m']==S['STAGE2_L1']['canonical_world_m'] and S['OFFICIAL_L1']['faces']==S['STAGE2_L1']['faces']
for s in S.values():assert sha(ROOT/s['input']['path'])==s['input']['sha256']
don=np.array(S['OFFICIAL_L1']['canonical_world_m']);rest=np.array(S['STAGE4A_R2']['canonical_world_m']);old=np.array(S['STAGE4C_R2']['canonical_world_m']);J=np.array(read(SOURCE/'HISTORICAL_RSSF_COORDINATE_CORRESPONDENCE.json')['per_vertex_linear_part']);errors=[]
for i in P['moved_vertex_ids']:
 row=src['current_to_donor'][str(i)];q=sum((don[int(k)]*w for k,w in row['L1_parent_weights'].items()),np.zeros(3));target=old[i]+J[i]@(q-rest[i]);errors.append(float(np.linalg.norm(target*1000-np.array(P['world_mm'][i]))))
assert max(errors)<.0002
dump('INDEPENDENT_DELIVERY_VERIFICATION_R1.json',{'status':'PASS','required_artifacts':required,'broken_review_links':broken,'valid_PNG_count':len(pngs),'image_dimensions':sizes,'diagnostic_static_render_count':43,'all_triple_comparison_cameras_scale_lighting_equal':True,'probe_position_formula_independently_recomputed':True,'max_saved_target_roundtrip_error_mm':max(errors),'source_Stage2_L1_exact_equivalence':True,'all_source_blend_hashes_verified':True,'normal_positions_locked_and_disjoint_membership':True,'core_plus_closure_plus_transition_equals_write_count':True,'actual_native_three_sections_populated':True,'protected_native_payload_reopen_PASS':True,'true3D_exact_structure_PASS':True,'current9_direct_and_neighborhood_overlap_zero':True,'frozen_file_count':len(before),'PRODUCTION_DRIFT':0,'Full42_runs':0,'Stage6_runs':0,'Human_acceptance_pending':True,'NEXT_not_executed':True})
dump('OUTPUT_ARTIFACT_HASH_MANIFEST_R1.json',{'files':{p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='OUTPUT_ARTIFACT_HASH_MANIFEST_R1.json'}})
print('PASS:',len(before),'pre-existing workspace files unchanged;',len(pngs),'PNGs;',len(manifest['records']),'static renders; target recompute max error',max(errors),'mm; no promotion',flush=True)
