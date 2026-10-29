from pathlib import Path
import json
O=Path(__file__).resolve().parent;p=O/'solve_b.py';s=p.read_text(encoding='utf-8-sig')
old="""if ai==2:
 assert json.loads((O/'B_ACTUAL_1.json').read_text())['status']!='REFERENCE_STATIC_GATES_PASS'
 seed[6:]=Q0.ravel();seed[:2]=0.;seed[3:6]=0.;v=skin(seed);seed[0]=(c.KEYS[46]['key_center'][0]-v[int(RAW['pad_indices'][0])][0])*1000"""
new="""if ai==2:
 previous=json.loads((O/'B_SOLVE_1.json').read_text());seed=np.array(previous['state'])
 assert json.loads((O/'B_ACTUAL_1.json').read_text())['actual_geometry']['wrong_key_or_nonpulp_max_depth_mm']>0
# This signed LP keeps outside configurations informative instead of a depth-zero plateau.
source=(O/'geometry_detector.py').read_text(encoding='utf-8-sig')
node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='triangle_inside_depth')
signed_source=ast.get_source_segment(source,node).replace('def triangle_inside_depth','def signed_triangle_depth').replace('&(x[:,2]>=-1e-8)','').replace('max(float(best[2])*1000,0.)','float(best[2])*1000')
exec(compile(signed_source,'signed_depth_extension','exec'))
"""
assert old in s;s=s.replace(old,new)
s=s.replace("seed[6:10],0.]","seed[6:10],previous['lambda_reference'] if ai==2 else 0.]")
s=s.replace("candidates=np.flatnonzero(np.all(th>=lo-1e-8,1)&np.all(tl<=hi+1e-8,1))","margin=.001 if ai==2 and note!=67 else 1e-8\n  candidates=np.flatnonzero(np.all(th>=lo-margin,1)&np.all(tl<=hi+margin,1))")
s=s.replace("np.min(sig,axis=1)<=1e-8","np.min(sig,axis=1)<=margin")
s=s.replace("peak=max([triangle_inside_depth(TV[ti],fullplanes[pi])[0] for ti in candidates]+[0.])\n  depths.append(.20-peak)","if ai==2 and note!=67:\n   peak=max([signed_triangle_depth(TV[ti],fullplanes[pi])[0] for ti in candidates]+[-1.])\n   depths.append(-.05-peak)\n  else:\n   peak=max([triangle_inside_depth(TV[ti],fullplanes[pi])[0] for ti in candidates]+[0.])\n   depths.append(.20-peak)")
s=s.replace("not_acceptance=True)","non_target_clearance_strategy='signed triangle LP <= -0.05mm' if ai==2 else 'original stricter-than-gate depth <=0.20mm',not_acceptance=True)")
p.write_text(s,encoding='utf8')
pp=O/'ANATOMY_CONSTRAINT_PROPOSAL.json';pr=json.loads(pp.read_text(encoding='utf-8-sig'))
pr['experiment']['B2_reason']='B1 meets 0.25mm gate but contains ~0.20mm A4/B4 intrusion; final controlled solve strengthens non-target clearance without relaxing anatomy or musical timing.'
pr['experiment']['B2_seed']='Actual B1 final complete controls, fixed original A root Z'
pr['experiment']['B2_non_target_constraint']='Signed original triangle-interior LP extended to negative outside depth <= -0.05mm; same original geometry acceptance, report zero intrusion separately.'
pr['experiment']['B2_constraint_confidence']='Geometric engineering clearance margin; no claim of a physiological angle threshold.'
pp.write_text(json.dumps(pr,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('FINAL_SECOND_SOLVE_LOCKED')
