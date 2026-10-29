import sys
sys.dont_write_bytecode=True
from geometry import *
import re
from collections import Counter

REQUIRED=['MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R4_REPORT.md','MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R4_STATUS.json','R4_NONLINEAR_SOLVER_AUDIT.json','R4_FEATURE_REIDENTIFICATION_AUDIT.json','R4_CONTINUOUS_COLLISION_CERTIFICATE.json','R4_BASELINE_CONTACT_COMPONENT_AUDIT.json','R4_GEOMETRY_CANDIDATES.json','R4_CANDIDATE_WRITE_SET.json','R4_BOUNDARY_CONTINUITY_AUDIT.json','R4_TRUE3D_STRUCTURE_AUDIT.json','R4_NEGATIVE_CONTROL_REGRESSION.json','R4_BIND_POSE_SMOKE_PREVIEW.json','PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json','review.html']

def verify():
 old=read(OUT/'HISTORICAL_HASHES_BEFORE.json');now=inventory();changed=[p for p in old if p in now and now[p]!=old[p]];missing=sorted(set(old)-set(now));extra=sorted(set(now)-set(old))
 assert not changed and not missing and not extra;assert sha(CAND)==EXPECTED_CAND
 dump('PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',{'status':'PASS','protected_preexisting_file_count':len(old),'verified_preexisting_file_count':len(now),'changed_files':changed,'missing_files':missing,'unexpected_files_outside_R4':extra,'PRODUCTION_DRIFT':0,'HISTORICAL_ARTIFACT_DRIFT':0,'production_input':ref(CAND),'production_expected_sha256':EXPECTED_CAND,'production_blend_save_count':0,'production_coordinate_write_count':0,'only_new_R4_directory_written':True,'prior_R1_R2_R3_reconciled_phase_and_temporary_assets_immutable':True,'topology_UV_material_normalflags_customnormals_weights_bones_joints_RSSF_drift':0,'Full42_Stage6B_ownershipR3_skin_rebuild_promotion_started':False})
 cert=read(OUT/'R4_CONTINUOUS_COLLISION_CERTIFICATE.json');previous=V.copy();checks=[];IDS=read(OUT/'R4_NONLINEAR_SOLVER_AUDIT.json')['support_ids']
 for c in cert['accepted_step_certificates']:
  z=read(OUT/c['coordinate_evidence']);before=V.copy();before[IDS]=np.array(z['before_world_mm_on_support']);after=V.copy();after[IDS]=np.array(z['after_world_mm_on_support'])
  assert np.array_equal(before,previous);assert digest(before.tolist())==z['before_full_coordinate_sha256']==c['before_full_coordinate_sha256'];assert digest(after.tolist())==z['after_full_coordinate_sha256']==c['after_full_coordinate_sha256'];assert c['status']=='CERTIFIED_CONTINUOUS_SAFE'
  from fractions import Fraction
  delta=after-before
  assert all(Fraction.from_float(float(before[i,k]))+Fraction.from_float(float(delta[i,k]))==Fraction.from_float(float(after[i,k])) for i in IDS for k in range(3))
  previous=after;checks.append({'iteration':c['iteration'],'before_after_coordinates_and_SHA_match':True,'outside_S4_fixed':True,'rational_affine_endpoint_equals_stored_endpoint_exactly':True})
 assert np.array_equal(previous,np.array(read(OUT/'R4_NONLINEAR_SOLVER_AUDIT.json')['world_mm']))
 dump('R4_COORDINATE_CHAIN_VERIFICATION.json',{'status':'PASS','step_count':len(checks),'steps':checks,'source_coordinate_sha256':digest(V.tolist()),'final_coordinate_sha256':digest(previous.tolist())})
 frozen=read(OUT/'R4_FROZEN_REFERENCE_RENDER_MANIFEST.json');copied=[]
 for row in frozen['renders']:
  p=ROOT/row['path'];src=ROOT/row['frozen_render_source'];assert sha(p)==sha(src);copied.append({'render':row['path'],'source':row['frozen_render_source'],'byte_identical':True})
 dump('R4_MATCHED_RENDER_SOURCE_VERIFICATION.json',{'status':'PASS','copied_render_count':len(copied),'renders':copied})
 s=read(OUT/'MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R4_STATUS.json');s['PRODUCTION_DRIFT']=0;s['PRODUCTION_READONLY_VERIFICATION']='PASS';s['HISTORICAL_FILE_COUNT_VERIFIED']=len(old);s['COORDINATE_CHAIN_VERIFIED']=True;s['VISUAL_REVIEW_OBSERVATION']='Final ordinary close view retains a sharp/deep central contour notch; native sections show only limited improvement. No qualified Human candidate.'
 s['failure_secondary']=[x.replace('C_BASELINE_CONTACT_COMPONENT_CONFLICT_LOCAL_TRIAL_ONLY','C_BASELINE_CONTACT_COMPONENT_CONFLICT') for x in s['failure_secondary']];s['conflict_scope']='Rejected local trial directions only; no global infeasibility or topology necessity proof.';dump('MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R4_STATUS.json',s)
 required_missing=[x for x in REQUIRED if not (OUT/x).is_file()];assert not required_missing
 text=(OUT/'review.html').read_text(encoding='utf-8');links=re.findall(r'(?:src|href)="([^"]+)"',text);broken=[x for x in links if not (OUT/x).is_file()];assert not broken
 from urllib.request import urlopen
 from urllib.parse import quote
 http=[]
 for path in ['review.html']+sorted(set(links)):
  with urlopen('http://127.0.0.1:8955/'+quote(path),timeout=5) as response:
   data=response.read();assert response.status==200;assert hashlib.sha256(data).hexdigest()==sha(OUT/path)
   http.append({'path':path,'HTTP_status':200,'served_bytes_match_local_file':True})
 dump('R4_PREVIEW_HTTP_VERIFICATION.json',{'status':'PASS','url':'http://127.0.0.1:8955/review.html','resources':http})
 # All emitted JSON must parse and have no non-finite numbers.
 def reject_constant(c):raise ValueError('Non-finite JSON value: '+c)
 for p in OUT.rglob('*.json'):json.loads(p.read_text(encoding='utf-8-sig'),parse_constant=reject_constant)
 neg=read(OUT/'R4_NEGATIVE_CONTROL_REGRESSION.json');assert neg['NEGATIVE_CONTROLS_PASS']==16 and neg['NEGATIVE_CONTROL_TOTAL']==16
 dump('R4_DELIVERY_VERIFICATION.json',{'status':'PASS','required_files':REQUIRED,'required_missing':required_missing,'html_local_link_count':len(links),'broken_local_links':broken,'all_JSON_parse_finite':True,'candidate_count':0,'production_drift':0,'coordinate_chain_count':len(checks),'negative_controls_pass':16,'first_view':'Ordinary original Human camera CURRENT / R1-C failed / R2-S5 failed / R4-A unavailable; no colored forensic first.'})
 manifest={p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and not p.name.endswith('_LOG.txt') and p.name!='R4_OUTPUT_MANIFEST.json'}
 dump('R4_OUTPUT_MANIFEST.json',{'files':manifest,'scope':'New R4 output only; mutable run logs omitted.','source_inventory_verification':'PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json'})
 print('DELIVERY_PASS',len(old),'protected files,',len(checks),'continuous steps,',len(manifest),'output files',flush=True)

if __name__=='__main__':verify()
