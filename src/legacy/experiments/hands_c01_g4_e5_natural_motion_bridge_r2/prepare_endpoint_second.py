import json
from pathlib import Path
O=Path(__file__).resolve().parent;p=O/'solve_endpoint.py';s=p.read_text(encoding='utf-8-sig')
s=s.replace("seed[:6]=0;seed[6:]=Q1.ravel();lam=1.","seed[:6]=np.array(json.loads((O/'PREFLIGHT_AND_ENDPOINT_DIAGNOSIS.json').read_text())['old_S2']['state'])[:6];seed[6:]=Q1.ravel();seed[14:17]=ACTIVE_FLEX;lam=1.")
s=s.replace("seed=startstate.copy();lam=0.","ACTIVE_FLEX=np.array(next(d for d in json.loads((O/'PREFLIGHT_AND_ENDPOINT_DIAGNOSIS.json').read_text())['old_S2']['actual_anatomy']['digits'] if d['digit']=='MIDDLE')['controls_recovered_deg'][:3])\nassert np.all(ACTIVE_FLEX<=[32,32,20]) and np.all(ACTIVE_FLEX>=0)\nseed=startstate.copy();lam=0.")
s=s.replace(" return st\nx0=np.r_[seed[:6],seed[6:10],lam];"," if ai==2:st[14:17]=(1-x[11])*st[14:17]+x[11]*ACTIVE_FLEX\n return st\nif ai==2:low=np.r_[low,0.];high=np.r_[high,1.]\nx0=np.r_[seed[:6],seed[6:10],lam];\nif ai==2:x0=np.r_[x0,1.]\n")
s=s.replace("1.]\nx0=np", "1.]\nx0=np")
# x0 clipping is on its own following generated blank line/line text.
s=s.replace("1]\ndef obj", "1]\nif ai==2:scale=np.r_[scale,1.]\ndef obj")
s=s.replace("natural_family='conservative approved R1/R2 coupled whole long finger reference; not a general active piano prior',","natural_family='approved spread + provisional old-S2 coordinated active flexion' if ai==2 else 'conservative approved R1/R2 coupled whole long finger reference; not a general active piano prior',active_flex_alpha=float(chosen[11]) if ai==2 else 0.,active_flex_anchor=ACTIVE_FLEX.tolist(),active_flex_reference_Human='NOT_SEPARATELY_REVIEWED; prior audit found hinge-only flexion, old S2 spread rejected',")
p.write_text(s,encoding='utf8')
policy=O/'POLICY_LOCK.json';r=json.loads(policy.read_text(encoding='utf-8-sig'))
plan=dict(first_failure='S1 passive-only family lacks independent striking middle flexion; actual contact failed and non-target depth failed',second_attempt=dict(passive_other_fingers='approved R1/R2 shared lambda',middle_spread='same approved R1/R2 -6.73..-7.20deg range',middle_flex='one alpha [0,1] blending approved passive flex with existing audited S2 hinge-only flex [18.988115,14.196144,7.282417]',original_authorized_middle_domain_deg=[[0,0,0,-25],[32,32,20,25]],no_new_lateral_or_axial_control=True,no_existing_geometry_gate_relaxed=True,source='Previous ACTUAL_RIG_ANATOMY S2 record, hashed/read-only',confidence='Provisional task-specific active pattern; no clinical comfortable-ROM or Human endpoint approval claim'),maximum_new_static_solves=2,third_attempt_forbidden=True)
r['endpoint_phase_family_adaptation']=plan
policy.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(O/'ENDPOINT_SECOND_ATTEMPT_PLAN.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('ACTIVE_PHASE_PATTERN_LOCKED')
