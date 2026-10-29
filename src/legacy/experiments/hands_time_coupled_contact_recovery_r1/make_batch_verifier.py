import ast,json
from pathlib import Path
O=Path(__file__).resolve().parent;src=(O.parent/'hands_contact_constrained_trajectory_planning_r1/verify_local_path.py').read_text();tree=ast.parse(src);body=[]
for n in tree.body:
 body.append(n)
 if isinstance(n,ast.FunctionDef) and n.name=='measure':break
extra='''
args=sys.argv[sys.argv.index('--')+1:]
requests=json.loads(Path(args[0]).read_text())
output=Path(args[1]);rows=[]
for r in requests:
 row=measure(r);row['scope']='TIME_COUPLED_LOCAL_DIAGNOSTIC';rows.append(row)
 output.write_text(json.dumps(rows,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item()))
 print('ACTUAL_LOCAL',r['id'],r['display_time'],row['all_gates'],row['target_max_depth_mm'],row['non_target_or_wrong_region_max_mm'],flush=True)
'''
(O/'batch_verify.py').write_text(ast.unparse(ast.Module(body=body,type_ignores=[]))+extra,encoding='utf-8')
