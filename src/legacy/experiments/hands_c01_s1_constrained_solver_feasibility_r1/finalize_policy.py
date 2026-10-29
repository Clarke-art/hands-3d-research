import json
from pathlib import Path
O=Path(__file__).resolve().parent;p=O/'POLICY_LOCK.json';r=json.loads(p.read_text(encoding='utf-8-sig'))
r['previous_policy_readonly_reference']=str(O.parent/'hands_c01_g4_e5_skin_safe_bridge_r1/POLICY_LOCK.json')
r.update(max_new_bridge_trajectories=0,total_new_numerical_budget_seconds=600,max_new_static_solves=2,static_attempt_wall_limit_seconds=240,root_z_ablation=dict(executed=False,allowed_in_this_experiment=False,reason='Both main solves fix their respective previous final seed Z'),max_main_iterations=60,static_only=True,stop='STOP — HUMAN REVIEW')
for k in ['max_new_static_nfev','max_nfev_per_initialization','max_test_seconds','validation_hz','risk_adaptive_sampling']:r.pop(k,None)
r['solver']['root_z']='Fixed at each previous REPAIR_ATTEMPT final candidate value; no Z optimization in this task'
r['representation_change_attempt2']='Replace conservative fixed key supporting-plane inequalities with the original triangle-interior LP inequalities; no extra solve'
r['proxy_equivalence_limits']=['fixed self-nearface pool not proven globally exhaustive over allowed move domain','E5 per-axis 2mm expansion is not Euclidean-corner equivalent','negative/positive clipped patch extrema do not prove same-face crossing']
r['full_actual_acceptance_required']=True
p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
