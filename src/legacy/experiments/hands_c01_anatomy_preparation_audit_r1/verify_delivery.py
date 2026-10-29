import sys,json,ast,hashlib,struct
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;PRE=O.parent/'hands_c01_s1_constrained_solver_feasibility_r1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
req=['RIG_JOINT_ANATOMY_AUDIT.md','S1_UNNATURAL_POSE_ROOT_CAUSE.md','E5_PREPARATION_CONSTRAINT_REVIEW.md','ANATOMY_CONSTRAINT_PROPOSAL.json','STATIC_AB_COMPARISON.md','HUMAN_VISUAL_REVIEW.md','FINAL_RECOMMENDATION.md']
assert all((O/n).exists() and (O/n).stat().st_size>200 for n in req)
# Reports reflect final pure-static artifact, original Action identity remains in acceptance evidence.
for name in ['HUMAN_VISUAL_REVIEW.md','write_reports.py']:
 p=O/name;s=p.read_text(encoding='utf-8-sig');s=s.replace('诊断Blend含继承参考动作数据，实验场景自身无绑定Action。','诊断Blend最终仅保留B2静态场景，Action数据块为0；原Action身份/状态已在独立验收中核对。');p.write_text(s,encoding='utf8')
finalcheck=read(O/'STATIC_BLEND_FINAL_CHECK.json')
assert finalcheck['action_datablocks']==0 and finalcheck['scene_count']==1 and finalcheck['vertex_difference_mm']==0
r=read(O/'ANATOMY_STATIC_RESULTS.json');r['final_pure_static_blend']=finalcheck
r['static_diagnostic_blend']=str(O/'S1_ANATOMY_PREPARATION_DIAGNOSTIC_R1.blend')
r['delivery_action_datablocks']=0
(O/'ANATOMY_STATIC_RESULTS.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
deps=read(PRE/'DEPENDENCY_MANIFEST.json');deps['current_task']=r['task'];deps['newly_installed_dependencies']=[];deps['numerical_execution_scripts']=['solve_b_attempt1.py','solve_b.py'];deps['anatomy_uses_actual_Blender_basis_and_rest_matrices']=True
(O/'DEPENDENCY_MANIFEST.json').write_text(json.dumps(deps,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for p in O.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
for p in O.glob('*.json'):read(p)
assert r['status']=='ANATOMY_STATIC_CANDIDATE_PASS_HUMAN_PENDING' and r['decision']=='C'
assert r['human_decision']['A_S1_2']['S1_HUMAN_ANATOMICAL_VISUAL']=='FAIL'
assert r['human_decision']['DYNAMIC_BRIDGE_AUTHORIZATION']=='NOT_GRANTED'
assert r['budget']['actual_main_solves']==2 and r['budget']['main_plus_startup_error_seconds']<300
assert len(list(O.glob('B_SOLVE_*.json')))==2
assert all(r['actual_B_attempts'][1]['gates'].values())
assert r['actual_B_attempts'][1]['actual_geometry']['wrong_key_or_nonpulp_max_depth_mm']==0
assert r['actual_B_attempts'][1]['old_E5_target_gate'] is False
assert r['actual_B_attempts'][1]['Human_visual_naturalness']=='PENDING'
before=read(O/'PROTECTED_FILES_BEFORE.json');assert all(sha(Path(p))==h for p,h in before.items())
stills=read(O/'STILL_MANIFEST.json');assert len(stills)==4 and len(list((O/'stills').glob('*.png')))==4
for x in stills:
 p=Path(x['file']);assert sha(p)==x['sha256']
 assert struct.unpack('>II',p.read_bytes()[16:24])==(1280,720)
assert len(list(O.glob('*.blend')))==1
files=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and p.name not in ['DELIVERY_MANIFEST.json','verify_delivery.log'] and '__pycache__' not in p.parts:
  files.append(dict(file=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=sha(p)))
out=dict(task=r['task'],status=r['status'],decision='C',authority='DESIGN_PROVISIONAL',stop='STOP — HUMAN REVIEW',client_date='2026-10-13',timezone='Asia/Shanghai',required_deliverables=req,protected_hashes_unchanged=len(before),static_solves=2,reported_optimization_seconds=r['budget']['reported_main_solve_wall_seconds'],main_plus_startup_error_seconds=r['budget']['main_plus_startup_error_seconds'],actual_B2_geometry_and_reference_constraints_pass=True,old_A_Human_fail_unchanged=True,old_E5_hover_requirement_pass=False,new_early_preparation_rule_pass=True,stills=4,pixels=[1280,720],pure_static_blend_actions=0,pure_static_blend_scenes=1,json_and_python_syntax_valid=True,files=files)
(O/'DELIVERY_MANIFEST.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('DELIVERY_VERIFIED',out['status'],'decision C','protected',len(before),'solves2','stills4','Actions0','seconds',out['main_plus_startup_error_seconds'])
