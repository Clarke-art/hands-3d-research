import sys,json,hashlib,ast,struct,platform
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((O/'PROTECTED_FILES_BEFORE.json').read_text(encoding='utf-8-sig'));after={p:sha(Path(p)) for p in old};changed=[p for p,h in old.items() if after[p]!=h];assert not changed,changed
(O/'PROTECTED_FILES_AFTER.json').write_text(json.dumps(dict(protected_count=len(old),all_unchanged=not changed,changed=changed,sha256=after),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
required=['ENDPOINT_ANATOMY_AND_GEOMETRY.md','STAGED_MOTION_PLAN.md','BRIDGE_MOTION_METRICS.json','HUMAN_VISUAL_REVIEW.md','PRODUCT_ROUTE_CHECK.md','FINAL_RECOMMENDATION.md'];assert all((O/n).is_file() for n in required)
for f in O.glob('*.json'):json.loads(f.read_text(encoding='utf-8-sig'))
for f in O.glob('*.py'):ast.parse(f.read_text(encoding='utf-8-sig'))
frames=list((O/'stills').glob('*.png'));assert len(frames)==6
for f in frames:assert struct.unpack('>II',f.read_bytes()[16:24])==(1280,720)
assert not any(O.glob('*.mp4'))
m=json.loads((O/'BRIDGE_MOTION_METRICS.json').read_text(encoding='utf-8-sig'));assert m['numerical_budget']['total_seconds']<=600 and m['candidate_count']==1 and m['status']=='BRIDGE_MOTION_PARTIAL';assert m['root_domain_failed_samples']==0
b=json.loads((O/'ACTION_BINDINGS.json').read_text(encoding='utf-8-sig'));assert len(b['new_actions'])==2
sys.path.insert(0,str(O.parent/'hands/audits/midi_driven_dual_hand_piano_performance_poc_r1/_deps'))
import scipy,numpy
refs=[O.parent/'hands_c01_whole_hand_motion_feasibility_r1/blender_utils.py',O.parent/'hands/audits/midi_driven_dual_hand_piano_performance_poc_r1/performance_core.py',O.parent/'hands/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/whole_phrase_model.py']
deps=dict(python=platform.python_version(),scipy=scipy.__version__,numpy=numpy.__version__,blender='5.1.2',blender_executable=r'D:\blender\blender.exe',read_only_existing_dependency_directory=str(O.parent/'hands/audits/midi_driven_dual_hand_piano_performance_poc_r1/_deps'),no_packages_installed=True,source_modules=[dict(path=str(f),sha256=sha(f)) for f in refs],copied_geometry_modules=[dict(file=n,sha256=sha(O/n)) for n in ['skin_proxy.py','geometry_detector.py','triangle_distance.py','extract_anatomy.py']])
(O/'DEPENDENCY_MANIFEST.json').write_text(json.dumps(deps,indent=2)+'\n')
notes='\n序列化精度说明：理论Hermite曲线按C1构造，实际float32 FCurve手柄计算出的对象根平移斜率跳差最大约1.789122mm/s，四元数分量约0.000815512/s。因此不宣称实际Action严格数学C1；腕部速度/加速度来自实际120Hz差分，不能据此认证舒适度。\n'
f=O/'STAGED_MOTION_PLAN.md'
if '序列化精度说明' not in f.read_text(encoding='utf-8-sig'):f.write_text(f.read_text(encoding='utf-8-sig')+notes,encoding='utf8')
check=dict(status='DELIVERY_CHECK_PASS',protected_files=len(old),all_protected_hashes_unchanged=True,required_deliverables=required,stills=len(frames),stills_resolution=[1280,720],videos=0,numerical_seconds=m['numerical_budget']['total_seconds'],endpoint_solves=2,bridge_candidates=1,new_hand_actions=2,python_syntax_and_json_parse_pass=True,actual_action_status=m['status'],root_control_domain_failures=0)
(O/'DELIVERY_CHECK.json').write_text(json.dumps(check,indent=2)+'\n')
files=[dict(file=str(f.relative_to(O)),size=f.stat().st_size,sha256=sha(f)) for f in sorted(O.rglob('*')) if f.is_file() and f.name not in ['DELIVERY_MANIFEST.json','delivery_verify.log'] and '__pycache__' not in f.parts]
(O/'DELIVERY_MANIFEST.json').write_text(json.dumps(dict(task=m['task'],status=m['status'],authority='DESIGN_PROVISIONAL',files=files),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(check,ensure_ascii=False))
