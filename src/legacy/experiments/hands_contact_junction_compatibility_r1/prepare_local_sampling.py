import sys,json,ast
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));from rig_model import *
p=json.loads((O/'LOCAL_PATH_PLAN.json').read_text());I=json.loads((O/'EXPERIMENT_INPUT.json').read_text());idx=json.loads((O/'LOCAL_PATH_KNOT_INDEX.json').read_text());assert len(idx)==4 and all(x['all_gates'] for x in idx)
j=json.loads((O/'runs/junction_2.json').read_text());zz=[j['latent'],j['latent']]+[json.loads((O/f'runs/path_{i}.json').read_text())['latent'] for i in range(1,5)];f=PchipInterpolator(p['knots'],zz,axis=0);J=p['junction'];ts=list(np.arange(p['interval'][0],p['interval'][1]+1e-9,1/120))+p['knots']+[J-.0001,J+.0001,J+.001]
# Each interval is high-risk: switching contacts and <=0.05mm key-depth headroom.
for a,b in zip(p['knots'][:-1],p['knots'][1:]):ts+=list(np.linspace(a,b,5))
ts=sorted(set(round(t,12) for t in ts));rows=[]
for n,t in enumerate(ts):
 z=f(t);contacts=I['contacts'] if abs(t-J)<1e-9 else [I['contacts'][0 if t<J else 1]]
 rows.append(dict(id='sample_'+str(n).zfill(3),display_time=t,latent=z.tolist(),state=state(z).tolist(),contacts=contacts,latent_velocity=f(t,1).tolist(),latent_acceleration=f(t,2).tolist()))
out=dict(plan=p,knots=p['knots'],latent_knots=zz,samples=rows,interpolation='scipy PchipInterpolator, exact coefficients below',coefficients=f.c.tolist(),base_sampling_hz=120,adaptive_reason='Every knot interval has small key-clearance headroom and contact switching; quarter-interval subdivision plus event +/-0.1ms and +1ms',candidate_count=1)
(O/'LOCAL_CONTROL_TRAJECTORY.json').write_text(json.dumps(out,indent=2))
# Reuse exactly the independent static verifier calculation in one Blender session.
src=(O/'blender_verify.py').read_text(encoding='utf-8-sig');tree=ast.parse(src);cut=next(i for i,x in enumerate(tree.body) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='args' for t in x.targets));head=ast.unparse(ast.Module(body=tree.body[:cut],type_ignores=[]))
block=tree.body[cut+1].orelse;body=block[2:-2];function=ast.FunctionDef(name='measure',args=ast.arguments(posonlyargs=[],args=[ast.arg(arg='r')],kwonlyargs=[],kw_defaults=[],defaults=[]),body=body+[ast.Return(value=ast.Name(id='out',ctx=ast.Load()))],decorator_list=[]);ast.fix_missing_locations(function)
script=head+'\n'+ast.unparse(function)+'''\ntrajectory=json.loads((O/'LOCAL_CONTROL_TRAJECTORY.json').read_text());out=[]
for r in trajectory['samples']:
 row=measure(r);out.append(row);print('SAMPLE',r['id'],r['display_time'],row['all_gates'],row['gates'],flush=True)
 (O/'LOCAL_PATH_ACTUAL_SAMPLES.json').write_text(json.dumps(out,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item()))
'''
(O/'verify_local_path.py').write_text(script,encoding='utf8');print('samples',len(rows))
