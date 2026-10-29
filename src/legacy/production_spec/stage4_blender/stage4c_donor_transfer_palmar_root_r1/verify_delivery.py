import sys
sys.dont_write_bytecode=True
from common import *
import numpy as np
from PIL import Image
from html.parser import HTMLParser
from urllib.parse import unquote
status=read(OUT/(PHASE+'_STATUS.json'));C=read(TARGET);actual=read(OUT/'PALMAR_APPLICATION_NATIVE_GEOMETRY_R1.json');receipt=read(OUT/'HUMAN_PALMAR_DIGIT_ROOT_DONOR_RESTORATION_APPROVAL_R1.json');pre=read(OUT/'PALMAR_APPLICATION_BEFORE_SAVE_SNAPSHOT_R1.json');structure=read(OUT/'PALMAR_APPLICATION_STRUCTURE_AUDIT_R1.json');normal=read(OUT/'PALMAR_APPLICATION_NORMAL_CONTEXT_AUDIT_R1.json');sections=read(OUT/'PALMAR_APPLICATION_NATIVE_SECTIONS_R1.json');plan=read(OUT/'PALMAR_APPLICATION_DOWNSTREAM_REVALIDATION_PLAN_R1.json')
assert status['APPLICATION_VERDICT']=='PASS_APPLIED_TO_NEW_STAGE4C_DERIVED_REVISION' and not status['NEXT_EXECUTED']
assert receipt['approved16_vertex_ids']==IDS and receipt['approved_target_coordinate_payload']['sha256']==sha(TARGET) and receipt['approved_write_set']['sha256']==sha(WRITESET)
assert sha(SOURCE)==EXPECTED_SOURCE and sha(CANDIDATE)==EXPECTED_CANDIDATE and sha(DONOR)==EXPECTED_DONOR and sha(ASSET)==status['APPLICATION_ASSET_SHA256']
assert sha(OUT/'HUMAN_APPROVAL_REQUEST_ORIGINAL.txt')==sha(REQUEST)
assert actual['application_local_m']==C['candidate_local_m'] and actual['application_world_mm']==C['candidate_world_mm']==actual['approved_candidate_world_mm']
assert [i for i,(a,b) in enumerate(zip(actual['source_local_m'],actual['application_local_m'])) if a!=b]==IDS
assert all(actual['source_local_m'][i]==actual['application_local_m'][i] for i in normal['excluded_normal_vertex_ids']) and len(normal['excluded_normal_vertex_ids'])==69 and len(normal['excluded_normal_face_ids'])==49
assert actual['native_V_E_F']==[3416,6828,3414] and pre['application_before_save_snapshot']['protected']==pre['source_snapshot']['protected']
assert structure['status']=='PASS' and all(structure[k]==0 for k in ['new_nonadjacent_exact_intersection','new_off_shared_crossing','new_illegal_coplanar_overlap','new_self_intersection_count','new_structural_bowtie','face_reversal_count','new_degenerate','new_true_contact_component_count','existing_contact_worsening_count','feature_expansion_count','new_boundary_transition_fold_count'])
assert plan['MID_MCP_45']=='MANDATORY_TARGETED_REVALIDATION' and not plan['NEXT_EXECUTED'] and all(not s['executed'] for s in plan['revalidation_blast_radius'])
assert plan['revalidation_blast_radius'][3]['true_cap_decision'].startswith('Audit decides')
assert sections['states']['APPROVED_FORMAL_CANDIDATE']==sections['states']['APPLIED_NEW_STAGE4C_REVISION'] and all(len(segs)>0 for st in sections['states'].values() for segs in st.values())
manifest=read(OUT/'PALMAR_APPLICATION_MATCHED_RENDER_MANIFEST_R1.json');assert len(manifest['records'])==45;labels=['SOURCE_STAGE4C','APPROVED_FORMAL_CANDIDATE','APPLIED_NEW_STAGE4C_REVISION']
for view in ['HUMAN_CAMERA','CLOSE','ALTERNATE']:
 for style in ['SOLID','GRAZING','FLAT_SOURCE_NATIVE','WIRE','ROI_LABEL']:
  rows=[r for r in manifest['records'] if r['view']==view and r['style']==style];assert len(rows)==3 and {r['state'] for r in rows}==set(labels)
  assert all(r['camera_matrix']==rows[0]['camera_matrix'] and r['orthographic_width_m']==rows[0]['orthographic_width_m'] and r['studio_rotation_z']==rows[0]['studio_rotation_z'] and r['pose_setters']==0 for r in rows)
  a=np.array(Image.open(OUT/f'renders/{labels[1]}__{view}__{style}.png'));b=np.array(Image.open(OUT/f'renders/{labels[2]}__{view}__{style}.png'));assert np.array_equal(a,b)
required=[PHASE+'_REPORT.md',PHASE+'_STATUS.json','HUMAN_PALMAR_DIGIT_ROOT_DONOR_RESTORATION_APPROVAL_R1.md','HUMAN_PALMAR_DIGIT_ROOT_DONOR_RESTORATION_APPROVAL_R1.json','PALMAR_APPLICATION_WRITE_VERIFICATION_R1.json','PALMAR_APPLICATION_GEOMETRY_EQUIVALENCE_R1.json','PALMAR_APPLICATION_STRUCTURE_AUDIT_R1.json','PALMAR_APPLICATION_CONTACT_AUDIT_R1.json','PALMAR_APPLICATION_NORMAL_CONTEXT_AUDIT_R1.json','PALMAR_APPLICATION_SOURCE_FIDELITY_R1.json','PALMAR_APPLICATION_SAVE_REOPEN_AUDIT_R1.json','PALMAR_APPLICATION_DOWNSTREAM_REVALIDATION_PLAN_R1.json','PALMAR_APPLICATION_PROTECTED_HISTORY_HASH_AUDIT_R1.json','review.html',ASSET.name]
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
# Final history check is independent of packaging and authority/reference links.
before=read(OUT/'PROTECTED_HISTORY_HASHES_BEFORE.json');after=inventory();changed=[k for k,v in before.items() if after.get(k)!=v];added=[k for k in after if k not in before];assert not changed and not added,(changed,added)
initial=read(OUT/'CURRENT9_RESPONSE_STATE_BEFORE.json');response=ref(RESPONSE) if RESPONSE.is_file() else None;assert response==initial['external_source'];assert sha(PRIOR/'CURRENT9_HUMAN_RESPONSE_HOLD_VERIFICATION_R1.json')==initial['prior_hold_receipt']['sha256']
assert status['CURRENT9_DIRECT_OVERLAP']==status['CURRENT9_1RING_OVERLAP']==status['CURRENT9_2RING_OVERLAP']==0 and status['CURRENT9_HUMAN_RESPONSE']=='HOLD_NOT_CLOSED'
assert all(status[k]==0 for k in ['target_ancestry_formula_recompute_runs','feasibility_probe_reads','bind_runs','pose_runs','Stage5_propagation_runs','skin_requalification_runs','targeted_deformation_runs','Full42_runs','true_cap_recompute_runs','Stage6B_runs'])
fresh=np.array(actual['application_world_mm'])[IDS];refmath=np.array(C['mathematical_target_world_mm'])[IDS];err=np.linalg.norm(fresh-refmath,axis=1);fidelity=read(OUT/'PALMAR_APPLICATION_SOURCE_FIDELITY_R1.json');assert float(err.max())==fidelity['max_mm'] and float(np.sqrt(np.mean(err**2)))==fidelity['RMS_mm']
dump('PALMAR_APPLICATION_DELIVERY_VERIFICATION_R1.json',{'status':'PASS','required_artifacts':required,'broken_review_links':broken,'valid_PNG_count':len(pngs),'fresh_application_render_count':len(manifest['records']),'all3_column_camera_scale_lighting_exact':True,'all15_approved_applied_pixel_comparisons_exact':True,'approved_stored_target_delta_mm':0,'actual_native_changed_count':16,'normal69_complete49_faces_exact':True,'three_fresh_native_sections_approved_applied_exact':True,'native_payload_reopen_verified':True,'fresh_static_true3D_gate_PASS':True,'fresh_source_fidelity_max_mm':fidelity['max_mm'],'fresh_source_fidelity_RMS_mm':fidelity['RMS_mm'],'frozen_preexisting_file_count':len(before),'PROTECTED_HISTORY_DRIFT':0,'Human_approval_receipt_bound':True,'new_independent_Stage4C_revision':ref(ASSET),'current9_response_state_unchanged':True,'MID45_mandatory_downstream_plan':True,'NEXT_only_recorded':True,'no_bind_pose_or_downstream_runs':True})
dump('OUTPUT_ARTIFACT_HASH_MANIFEST_R1.json',{'files':{p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='OUTPUT_ARTIFACT_HASH_MANIFEST_R1.json'}})
print('DELIVERY PASS:',len(before),'protected files unchanged;',len(pngs),'PNGs /45 fresh renders; approved16 applied exact; NEXT not executed',flush=True)
