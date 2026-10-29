from coupled_model import *
start=time.monotonic();p,data=load_problem();r=json.loads((O/'CORRECTION_SOLVE_RESULTS.json').read_text());z=np.array(r['nodes'][0]['latent']);n=p.nodes[0];mats={};traces=[]
for h in [1e-3,1e-4,1e-5,1e-6]:mats[h]=n.jac(z,h)
difference=abs(mats[1e-4]-mats[1e-5]);rr,cc=np.where(difference>1e-3)
for row,col in zip(rr,cc):
 typ='face_contact' if row==0 else 'pad_or_witness' if row<11 else 'key_triangle_depth' if row<11+len(n.pieces) else 'self_minmax_certificate'
 one=[]
 for h in [1e-4,1e-5,1e-6]:
  step=h*(.1 if col>=10 else 1);delta=np.eye(12)[col]*step;base=n.value(z)[row];ap=n.value(z+delta)[row];sigp=n.last_signature;am=n.value(z-delta)[row];sigm=n.last_signature;one.append(dict(h=h,forward=float((ap-base)/step),backward=float((base-am)/step),central=float((ap-am)/(2*step)),contact_signature_changed=sigp[0]!=sigm[0],key_witness_changed=sigp[1]!=sigm[1],self_feature_changed=sigp[2]!=sigm[2]))
 traces.append(dict(row=int(row),variable=int(col),type=typ,steps=one))
result=dict(node=0,coarse_to_fine_max=float(difference.max()),fine_to_finer_max=float(abs(mats[1e-5]-mats[1e-6]).max()),sensitive_rows=traces,classification='NON_SMOOTH_OR_UNVERIFIED',geometry_acceptance_independent=True,corrective_solves_remaining=0,no_new_solve=True,wall_seconds=time.monotonic()-start)
save('NONSMOOTH_BRANCH_DIAGNOSIS.json',result);print(result['fine_to_finer_max'],[(r['row'],r['variable'],r['type']) for r in traces],flush=True)
