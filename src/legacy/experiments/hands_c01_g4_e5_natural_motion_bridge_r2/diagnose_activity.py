import sys,json,ast
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
p=O/'FIXED_ENDPOINT_RELEASE_PROXY_DIAGNOSIS.json';r=json.loads(p.read_text());r['cause']='Hypothesis not confirmed at fixed endpoint: global release inequality is positive here. Infinite-plane representation can be over-conservative outside the footprint but does not explain this endpoint.';r['hypothesis_supported']=False;p.write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
src=(O/'solve_motion.py').read_text(encoding='utf-8-sig');nodes=[]
for n in ast.parse(src).body:
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='initial' for t in n.targets):break
 if isinstance(n,ast.Assert) and 'MOTION_CANDIDATE' in ast.get_source_segment(src,n):continue
 nodes.append(n)
env=dict(__file__=str(O/'solve_motion.py'));exec(compile(ast.Module(body=nodes,type_ignores=[]),'diagnostic_existing_activity_pool','exec'),env)
np=env['np'];Y=np.load(O/'MOTION_CANDIDATE.npz')['latent_knots'];z=env['curve'](Y)(env['TC']);reports=[]
for ci,(t,v) in enumerate(zip(env['TC'],z)):
 arr=env['cell'](ci,v);m=env['models'][ci];j=int(np.argmin(arr));contacts=1 if abs(t-env['EXCHANGE'])>1e-10 else 2;nn=7*contacts;pointn=len(m['vertices']);selfn=len(m['pairs'])
 if j<nn:kind='contact_or_pad';detail=dict(contact_ordinal=j//7,component=j%7)
 elif j<nn+pointn:
  ii=j-nn;kind='fixed_material_key_plane';point=np.einsum('i,ij->j',m['bary'][ii],env['skin'](env['state'](v))[m['vertices'][ii]]);detail=dict(vertices=m['vertices'][ii].tolist(),barycentric=m['bary'][ii].tolist(),world_point_m=point.tolist(),fixed_normal=m['normal'][ii].tolist(),fixed_offset=float(m['offset'][ii]))
 elif j<nn+pointn+selfn:kind='fixed_triangle_separation_axis';detail=dict(triangles=m['pairs'][j-nn-pointn].tolist())
 else:kind='global_release_plane';detail={}
 st=env['state'](v);V=env['skin'](st)
 detail['G4_clipped_pulp']=env['contact_metric'](V,env['c'].KEYS[46],m['angles'][46],1)
 detail['E5_clipped_pulp']=env['contact_metric'](V,env['c'].KEYS[55],m['angles'][55],3)
 reports.append(dict(time=float(t),minimum_constraint_mm=float(arr[j]),kind=kind,detail=detail))
out=dict(not_new_optimization=True,trajectory_unchanged=True,overall_worst=min(reports,key=lambda x:x['minimum_constraint_mm']),collocation_rows=reports,scope='re-evaluation of the same initial fixed activity pool on retained candidate; not independent Blender acceptance')
(O/'ACTIVITY_PROXY_FAILURE_DIAGNOSIS.json').write_text(json.dumps(out,indent=2,default=lambda x:x.item() if hasattr(x,'item') else x.tolist())+'\n',encoding='utf8')
print('WORST_PROXY',out['overall_worst']['time'],out['overall_worst']['minimum_constraint_mm'],out['overall_worst']['kind'])
