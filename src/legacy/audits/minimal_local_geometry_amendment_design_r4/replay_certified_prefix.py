import sys
sys.dont_write_bytecode=True
from nonlinear_solve import *
def run():
 live=read(OUT/'R4_LIVE_NONLINEAR_TRACE.json');target=np.array(live['world_mm']);v=V.copy();certificates=[];features=[]
 for record in live['iterations']:
  i=record['iteration'];loss,g,_=objective4(v);d=-(Wc@g);peak=np.linalg.norm(d,axis=1).max()
  if peak>.08:d*=.08/peak
  d,reid=project_constraints(v,d,.08);end=v.copy();end[IDS]+=record['accepted_step_fraction']*d;reg,_,_=registry(end,IDS);comparison=compare(base_components,reg);assert comparison['PASS'];ok,cert=certify(v,end,base_components,reg);assert ok,cert
  dump(f'accepted_steps/step_{i:03}.json',{'before_world_mm_on_support':v[IDS].tolist(),'after_world_mm_on_support':end[IDS].tolist(),'support_ids':IDS,'before_full_coordinate_sha256':digest(v.tolist()),'after_full_coordinate_sha256':digest(end.tolist()),'outside_support_unchanged':True,'reconstructed_from_deterministic_solver_and_recorded_accepted_fraction':True});cert.update({'before_full_coordinate_sha256':digest(v.tolist()),'after_full_coordinate_sha256':digest(end.tolist()),'coordinate_evidence':f'accepted_steps/step_{i:03}.json'});certificates.append({'iteration':i,**cert});features.append({'iteration':i,**reid});v=end;print('PREFIX REPLAY CERTIFIED',i,flush=True)
 error=float(np.max(abs(v-target)));assert error<1e-12,error
 dump('R4_PREFIX_RECONSTRUCTION_VERIFICATION.json',{'maximum_reconstructed_coordinate_error_mm':error,'full_coordinate_sha256_matches_saved_endpoint':digest(v.tolist())==digest(target.tolist()),'reconstructed_prefix_steps':len(certificates),'each_step_continuous_recertification':True});dump('R4_CONTINUOUS_COLLISION_CERTIFICATE.json',{'accepted_step_certificates':certificates,'every_accepted_step_certified':True,'accepted_step_count':len(certificates),'endpoint_only_used_for_safety':False,'full_baseline_to_diagnostic_endpoint_path_certified':True});dump('R4_FEATURE_REIDENTIFICATION_AUDIT.json',{'iterations':features,'feature_reidentification_each_iteration':True,'pair_wide_shared_gap_mm':0,'new_anatomy_clearance_mm':0});print('PREFIX VERIFIED maxerr',error,flush=True)
if __name__=='__main__':run()
