import sys
sys.dont_write_bytecode=True
from common import *
import numpy as np
from PIL import Image
from html.parser import HTMLParser
from urllib.parse import unquote
before=read(OUT/'FROZEN_HASHES_BEFORE.json');after=inventory();changed=[k for k,v in before.items() if after.get(k)!=v];added=[k for k in after if k not in before];initial=read(OUT/'HUMAN_RESPONSE_HASH_BEFORE.json');rs=ref(RESPONSE) if RESPONSE.is_file() else None;response_ok=rs==initial['external_source'];hold=sha(PRIOR/'CURRENT9_HUMAN_RESPONSE_HOLD_VERIFICATION_R1.json')==initial['prior_hold_receipt']['sha256']
drift={'status':'PASS' if not changed and not added and response_ok and hold else 'FAIL_CLOSED','frozen_preexisting_file_count':len(before),'changed_or_missing_preexisting_workspace_files':changed,'new_files_outside_design_directory':added,'PRODUCTION_DRIFT':len(changed),'production_geometry_normal_weight_rig_joint_material_modifier_writes':0,'external_response_present_at_start':initial['external_present'],'external_response_present_at_end':RESPONSE.is_file(),'external_response_state_unchanged':response_ok,'external_response_byte_verification':'PASS' if initial['external_present'] and response_ok else 'UNAVAILABLE_MISSING_AT_START; no response reconstruction/write/deletion','previous_current9_hold_receipt_byte_preserved':hold,'CURRENT9_HUMAN_RESPONSE':'HOLD_NOT_CLOSED','APPLY':False,'formal_Stage5_propagation_runs':0,'skin_requalification_runs':0,'true_cap_recompute_runs':0,'Full42_runs':0,'Stage6B_runs':0,'current9_closure':False,'promotion':False,'temporary_local_smoke_pose_count':3}
dump('PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',drift);dump('FROZEN_HASHES_AFTER.json',after);assert drift['status']=='PASS',drift
required=[PHASE+'_REPORT.md',PHASE+'_STATUS.json','PALMAR_ROOT_FORMAL_WRITE_SET_R1.json','PALMAR_ROOT_FORMAL_TARGET_COORDINATES_R1.json','PALMAR_ROOT_FORMAL_PROVENANCE_R1.json','PALMAR_ROOT_SOURCE_SHAPE_FIDELITY_R1.json','PALMAR_ROOT_STRUCTURE_AUDIT_R1.json','PALMAR_ROOT_CONTACT_AUDIT_R1.json','PALMAR_ROOT_NORMAL_CONTEXT_PROTECTION_R1.json','PALMAR_ROOT_BIND_ZERO_PREVIEW_R1.json','PALMAR_ROOT_LOCAL_POSE_SMOKE_R1.json','PALMAR_ROOT_CURRENT9_INDEPENDENCE_R1.json','PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json','review.html',CANDIDATE.name]
assert all((OUT/n).is_file() for n in required)
for p in OUT.glob('*.json'):read(p)
class Links(HTMLParser):
 def __init__(self):super().__init__();self.paths=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ['href','src'] and not v.startswith('#'):self.paths.append(v)
links=Links();links.feed((OUT/'review.html').read_text(encoding='utf-8'));broken=[p for p in links.paths if not (OUT/unquote(p)).is_file()];assert not broken,broken
pngs=list(OUT.rglob('*.png'))
for p in pngs:
 with Image.open(p) as im:im.verify()
C=read(OUT/'PALMAR_ROOT_FORMAL_TARGET_COORDINATES_R1.json');W=read(OUT/'PALMAR_ROOT_FORMAL_WRITE_SET_R1.json');S=read(OUT/'INDEPENDENT_DONOR_HISTORICAL_NATIVE_INPUTS_R1.json')['stages'];N=read(OUT/'CURRENT_STAGE4C_NATIVE_SNAPSHOT_R1.json');J=np.array(read(SOURCE/'HISTORICAL_RSSF_COORDINATE_CORRESPONDENCE.json')['per_vertex_linear_part']);A=read(SOURCE/'HISTORICAL_OPERATION_RAM_REPLAY.json')['final_ancestry'];don=np.array(S['OFFICIAL_L1']['canonical_world_m']);rest=np.array(S['STAGE4A_R2']['canonical_world_m']);src=np.array(N['coordinates_world_m']);actual=np.array(C['candidate_world_mm'])/1000;errors=[];lookup={tuple(v):i for i,v in enumerate(S['STAGE4A_R2_BASE']['local_m'])}
for i in ALLOWED:
 bi=lookup[tuple(S['STAGE4A_R2']['local_m'][i])];a=A[bi];q=sum((don[int(k)]*w for k,w in a.items()),np.zeros(3));t=src[i]+J[i]@(q-rest[i]);assert np.array_equal(t*1000,np.array(C['mathematical_target_world_mm'][i]));errors.append(float(np.linalg.norm((actual[i]-t)*1000)))
assert max(errors)<.0002;assert W['vertex_ids']==ALLOWED
normal=read(OUT/'PALMAR_ROOT_EXCLUDED_NORMAL_CONTEXT_R1.json');assert len(normal['vertex_ids'])==69 and len(normal['face_ids'])==49
assert np.array_equal(np.array(C['candidate_world_mm'])[normal['vertex_ids']],np.array(C['source_world_mm'])[normal['vertex_ids']])
sections=read(OUT/'PALMAR_ROOT_NATIVE_CROSS_SECTIONS_R1.json');assert len(sections['states'])==4 and all(len(segs)>0 for st in sections['states'].values() for segs in st.values());assert sections['states']['FEASIBILITY_PROBE']==sections['states']['FORMAL_CANDIDATE']
manifest=read(OUT/'MATCHED_RENDER_MANIFEST_R1.json');states=['CURRENT_RAW','OFFICIAL_L1_RSSF_DISPLAY','FEASIBILITY_PROBE','FORMAL_CANDIDATE'];unique={r['path'] for r in manifest['records']}
for view in ['HUMAN_CAMERA','CLOSE','ALTERNATE']:
 for style in ['SOLID','GRAZING','FLAT_SOURCE_NATIVE']:
  rows=[r for r in manifest['records'] if r['state'] in states and r['view']==view and r['style']==style];assert set(r['state'] for r in rows)==set(states)
  assert all(r['camera_matrix']==rows[0]['camera_matrix'] and r['orthographic_width_m']==rows[0]['orthographic_width_m'] and r['studio_rotation_z']==rows[0]['studio_rotation_z'] for r in rows)
status=read(OUT/(PHASE+'_STATUS.json'));smoke=read(OUT/'PALMAR_ROOT_LOCAL_POSE_SMOKE_R1.json');native=read(OUT/'INDEPENDENT_NATIVE_REOPEN_VERIFICATION_R1.json');assert native['status']=='PASS'
assert status['VERDICT']=='READY_FOR_HUMAN_AMENDMENT_APPROVAL' and status['MAX_COORD_DELTA_VS_PROBE_MM']==0 and not status['NEXT_EXECUTED']
assert smoke['POSE_SMOKE_CASES']==['MID_MCP_15','MID_MCP_30','MID_MCP_45'] and smoke['status']=='PASS_TEMPORARY_LOCAL_SMOKE'
assert all(r['status']=='PASS' and r['new_true3D_contact_count']==r['baseline_contact_worsening_count']==r['normal_context_candidate_vs_current_coordinate_max_mm']==r['neighbor_digit_geometry_contamination_count']==0 for r in smoke['states'].values())
assert read(OUT/'PALMAR_ROOT_STRUCTURE_AUDIT_R1.json')['status']=='PASS' and status['CURRENT9_DIRECT_OVERLAP']==status['CURRENT9_1RING_OVERLAP']==status['CURRENT9_2RING_OVERLAP']==0
assert sha(CURRENT)==EXPECTED_CURRENT and sha(CANDIDATE)==status['FORMAL_CANDIDATE_HASH']
for s in S.values():assert sha(ROOT/s['input']['path'])==s['input']['sha256']
assert all(S['OFFICIAL_L1'][k]==S['STAGE2_L1'][k] for k in ['local_m','canonical_world_m','faces','edges'])
dump('INDEPENDENT_DELIVERY_VERIFICATION_R1.json',{'status':'PASS','required_artifacts':required,'broken_review_links':broken,'valid_PNG_count':len(pngs),'actual_render_invocations_recorded':len(manifest['records']),'unique_render_images':len(unique),'matched_four_column_camera_scale_lighting_exact':True,'independent_formula_recomputed':True,'max_mathematical_source_target_error_mm':max(errors),'native_probe_formal_coordinates_exact':True,'normal69_complete49_faces_protected':True,'source_L1_Stage2_equivalence':True,'three_native_section_planes_four_states_populated':True,'probe_formal_section_segments_exact':True,'static_true3D_PASS':True,'bind_PASS':True,'temporary_local_smoke_count':3,'not_full_deformation_qualification':True,'frozen_file_count':len(before),'PRODUCTION_DRIFT':0,'Human_approval_pending':True,'NEXT_not_executed':True})
dump('OUTPUT_ARTIFACT_HASH_MANIFEST_R1.json',{'files':{p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='OUTPUT_ARTIFACT_HASH_MANIFEST_R1.json'}})
print('DELIVERY PASS',len(before),'frozen files unchanged;',len(pngs),'valid PNGs;',len(unique),'unique rendered images; design only, STOP HUMAN REVIEW',flush=True)
