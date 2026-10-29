import dynamic_session as w
from dynamic_session import *
# Read-only audits. No animation repair, new candidate, or keyframe edits.
base=np.load(OUT/'BASELINE_CONTEXT_ACTUAL.npz');times=base['times'];pairrows=[]
bp=[selfpairs(V) for V in base['R']]
for number in [1,2]:
 data=np.load(OUT/f'CANDIDATE_{number}_ACTUAL.npz');rows=[]
 for t,V,oldpairs in zip(times,data['V'],bp):
  pairs=selfpairs(V)
  rows.append(dict(time=float(t),self_count=len(pairs),new_pairs_count=len(pairs-oldpairs),removed_pairs_count=len(oldpairs-pairs),new_pair_examples=sorted(pairs-oldpairs)[:8]))
 pairrows.append(dict(candidate=number,new_pair_samples=sum(r['new_pairs_count']>0 for r in rows),new_pair_peak=max(r['new_pairs_count'] for r in rows),rows=rows))
save('ABSOLUTE_AND_NEW_SELF_PAIR_AUDIT.json',dict(rows=pairrows,note='Canonical actual triangle-ID set differences, supersedes validation summary new_self_samples which only measured net count increases. Absolute self counts agree.'))
w.reset();oldaction=w.rig.animation_data.action
oldvalues={(f.data_path,f.array_index):[f.evaluate(1+60*t) for t in [2.45,2.6,2.92,3.35,3.55,4.,4.08,4.2]] for f in s.curves(oldaction)}
oldpayload={(f.data_path,f.array_index):[dict(co=list(k.co),interpolation=k.interpolation,left=list(k.handle_left),right=list(k.handle_right),lt=k.handle_left_type,rt=k.handle_right_type) for k in f.keyframe_points if k.co.x<=1+60*2.92] for f in s.curves(oldaction)}
earlytimes=np.load(safe(R2/'CANDIDATE_2_DENSE.npz'))['times'];earlytimes=[float(t) for t in earlytimes if 2.45-1e-10<=t<=2.92+1e-10]
original=[]
for t in earlytimes:c.settime(w.sc,t);original.append(s.coords_tri(w.mesh)[0])
outside=[]
for number in [1,2]:
 w.reset(OUT/f'CANDIDATE_{number}_NOT_APPROVED.blend');diffs=[];changed_early_payload=[]
 for f in s.curves(w.rig.animation_data.action):
  k=(f.data_path,f.array_index);values=[f.evaluate(1+60*t) for t in [2.45,2.6,2.92,3.35,3.55,4.,4.08,4.2]]
  errors=np.array(values)-oldvalues[k]
  if abs(errors).max()>0:diffs.append(dict(path=k[0],index=k[1],errors=errors))
  payload=[dict(co=list(k.co),interpolation=k.interpolation,left=list(k.handle_left),right=list(k.handle_right),lt=k.handle_left_type,rt=k.handle_right_type) for k in f.keyframe_points if k.co.x<=1+60*2.92]
  if payload!=oldpayload[k]:changed_early_payload.append(k)
 deltas=[]
 for t,V0 in zip(earlytimes,original):
  c.settime(w.sc,t);V=s.coords_tri(w.mesh)[0];deltas.append(float(np.linalg.norm(V-V0,axis=1).max()*1000))
 outside.append(dict(candidate=number,query_times=[2.45,2.6,2.92,3.35,3.55,4.,4.08,4.2],curve_errors=diffs,earlier_keyframe_payload_changed=changed_early_payload,earlier_keyframe_payload_exactly_equal=not changed_early_payload,same_process_fresh_R2_target_samples=len(deltas),same_process_fresh_R2_target_max_skin_delta_mm=max(deltas),strict_earlier_geometry_identical=max(deltas)==0.,historical_dense_arrays_not_identical_warning='Initial validation compared to historical live R2 arrays. This audit compares fresh reopened R2 and candidates in the SAME Blender build/process, retaining any nonzero numerical delta as a strict-equality failure.'))
save('EXTERIOR_AND_EARLIER_R2_STRICT_AUDIT.json',dict(rows=outside,no_candidate_edits=True,failed_candidates_not_repaired_after_two_attempts=True))
protection('FINAL_AUDIT_INPUT_RECEIPT.json')
print('READONLY_FINAL_AUDITS_COMPLETE',json.dumps([dict(candidate=r['candidate'],new_pair_samples=r['new_pair_samples'],new_pair_peak=r['new_pair_peak']) for r in pairrows]),flush=True)
