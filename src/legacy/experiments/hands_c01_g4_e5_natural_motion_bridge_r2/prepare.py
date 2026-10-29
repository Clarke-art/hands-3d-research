import sys,json,hashlib,shutil
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;PRE=O.parent/'hands_c01_anatomy_preparation_audit_r1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((PRE/'DELIVERY_MANIFEST.json').read_text(encoding='utf-8-sig'))
for f in manifest['files']:assert sha(PRE/f['file'])==f['sha256'],f['file']
protected=json.loads((PRE/'PROTECTED_FILES_BEFORE.json').read_text(encoding='utf-8-sig'))
for p in PRE.rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts:protected[str(p)]=sha(p)
assert all(sha(Path(p))==h for p,h in protected.items())
for n in ['skin_proxy.py','geometry_detector.py','triangle_distance.py','SKIN_MODEL.npz','SKIN_MODEL_META.json','extract_anatomy.py']:shutil.copyfile(PRE/n,O/n)
p=json.loads((PRE/'POLICY_LOCK.json').read_text(encoding='utf-8-sig'))
p.update(task='PIANO_C01_G4_E5_NATURAL_MOTION_BRIDGE_R2',max_main_solves=2,max_endpoint_solves=2,endpoint_per_solve_wall_seconds=140,max_new_bridge_trajectories=1,new_solve_wall_budget_seconds=600,total_new_numerical_budget_seconds=600,main_trajectory_wall_seconds=280,static_only=False,authority='DESIGN_PROVISIONAL',source_B2=str(PRE),sample_Hz=120,source_lead_seconds=.35,interval=dict(start=2.527855,exchange=2.921426,E5_full_press=2.956426,E5_off=3.349997),stop='STOP — HUMAN REVIEW')
p['human_decision']=dict(B2_middle_visual_preliminary='ACCEPTED_FOR_ISOLATED_RESEARCH',formal_teaching='NOT_APPROVED',dynamic_bridge='AUTHORIZED_THIS_SINGLE_R07_TO_R08_EXPERIMENT',previous_A_visual='FAIL_UNCHANGED',expand_B02_23_notes='NOT_AUTHORIZED')
p['root_domains']=dict(X_mm=[-150,60],Y_mm=[-30,35],Z_mm=[-12.217247311392744,12],rotation_deg=[[-8,-8,-12],[8,8,12]],meaning='Existing authorized control domain; relative to approved rest root Z42.217247mm, wrist Z30..54.217247mm; not clinical ROM. Start B2 fixed; only endpoint and trajectory may use existing root Z.')
p['natural_family']=dict(source='Previous approved R1/R2 reference and explicit local proposal',conservative_test='All long fingers share lambda [0,1] between approved R1/R2; thumb retains authorized 4 axes. No independent PIP/DIP lateral rotation.',not_general_active_piano_prior=True,no_new_abnormal_joint_range=True)
for n,x in [('POLICY_LOCK.json',p),('PROTECTED_FILES_BEFORE.json',protected)]: (O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('INPUTS_PROTECTED',len(protected),'B2 manifest validated')
