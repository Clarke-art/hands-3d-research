import sys,json,ast,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
required=['S1_SOLVER_ROOT_CAUSE.md','CONSTRAINED_SOLVER_DESIGN.md','EXISTING_SOLVER_COMPARISON.md','S1_CONSTRAINED_RESULTS.json','HUMAN_VISUAL_REVIEW.md','FINAL_RECOMMENDATION.md']
def load(name):return json.loads((O/name).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert all((O/name).exists() and (O/name).stat().st_size>100 for name in required)
for p in O.glob('*.json'):json.loads(p.read_text(encoding='utf-8-sig'))
for p in O.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
r=load('S1_CONSTRAINED_RESULTS.json');assert r['status']=='CONSTRAINED_S1_PASS' and r['technical_decision']=='A' and r['authority']=='DESIGN_PROVISIONAL'
assert len(r['attempts'])==2 and r['budget']['actual_new_solve_wall_seconds']<=600
assert all(r['attempts'][1]['independent_blender']['gates'].values())
assert r['attempts'][1]['solve']['convergence']['success']
assert r['attempts'][1]['supplement']['complete_pulp_to_playable_top_euclidean_distance']['distance_mm']==0
assert r['attempts'][0]['independent_blender']['gates']['actual_surface_contact'] is False
assert r['previous_results_readonly'][1]['independent_blender']['gates']['actual_surface_contact'] is False
assert len(list((O/'stills').glob('*.png')))==4
assert len(list(O.glob('*.blend')))==1
before=load('PROTECTED_FILES_BEFORE.json')
assert all(sha(Path(p))==h for p,h in before.items())
# Correct a supplement field label: it records state, while a true delta is separately computed.
s=load('INDEPENDENT_DISTANCE_AND_PARITY.json')
for item,attempt in zip(s['attempts'],r['attempts']):
 item['state_change_from_previous_repair']=[b-a for a,b in zip(attempt['solve']['initial_state'],attempt['solve']['state'])]
r['budget']['numerical_restarts']=r['budget'].pop('retry_count',r['budget'].get('numerical_restarts',0))
r['verification_startup_retry']=dict(count=1,reason='Blender Python ABI differs from external SciPy ABI; removed optional proxy import, measured parity outside Blender',no_new_solve=True,log='verify_1_startup_error.log')
for i,item in enumerate(s['attempts']):r['attempts'][i]['supplement']=item
(O/'INDEPENDENT_DISTANCE_AND_PARITY.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf8')
(O/'S1_CONSTRAINED_RESULTS.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
manifest=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and p.name not in ['DELIVERY_MANIFEST.json','delivery_verify.log'] and '__pycache__' not in p.parts:
  manifest.append(dict(file=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=sha(p)))
out=dict(task=r['task'],status=r['status'],authority='DESIGN_PROVISIONAL',decision='A',stop=r['stop'],required_deliverables=required,protected_unchanged_count=len(before),main_solve_count=2,wall_seconds=r['budget']['actual_new_solve_wall_seconds'],stills=4,resolution=[1280,720],diagnostic_blends=1,json_and_python_syntax_valid=True,files=manifest)
(O/'DELIVERY_MANIFEST.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('DELIVERY_VERIFIED',out['status'],'A',len(before),'hashes unchanged',out['wall_seconds'],'seconds',len(manifest),'files')

