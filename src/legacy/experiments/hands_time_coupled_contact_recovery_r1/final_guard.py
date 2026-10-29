from coupled_model import *
from triangle_distance import distances
start=time.monotonic();p,data=load_problem();r=json.loads((O/'CORRECTION_SOLVE_RESULTS.json').read_text());x=np.array([n['latent'] for n in r['nodes']]).ravel();rows=[]
for i,n in enumerate(p.nodes):
 z=x[i*12:(i+1)*12];a=n.jac(z,1e-3);b=n.jac(z,1e-4);cc=n.jac(z,1e-5);U=unroot(skin(state(z)),state(z));dd,wa,wb=distances(U[TR[n.pairs[:,0]]],U[TR[n.pairs[:,1]]]);axes=(wa-wb)/np.maximum(dd[:,None],1e-12);axisdelta=np.linalg.norm(axes-n.axes,axis=1);n.value(z)
 rows.append(dict(node=i,max_coarse_fine=float(abs(a-b).max()),max_fine_finer=float(abs(b-cc).max()),relative_frobenius=float(np.linalg.norm(b-cc)/max(np.linalg.norm(cc),1e-12)),verified=bool(abs(b-cc).max()<1e-3),nearest_axis_change_max=float(axisdelta.max()),nearest_axis_changed_pairs=int(np.sum(axisdelta>1e-4)),min_disjoint_feature_distance_mm=float(dd.min()*1000),certificate_axes_fixed=True,axis_policy='A changed nearest feature does not alter fixed valid separating certificate; finite differences redetect min/max features. Full BVH is mandatory at accepted nodes/samples.',active_face_signature=n.last_signature[0],stats=n.stats))
for n in p.nodes:n.localcache.clear()
t=time.perf_counter();J=np.array(p.jfun(x));cold=time.perf_counter()-t;direction=np.cos(np.arange(len(x))+.4);checks=[]
for h in [1e-3,1e-4,1e-5]:
 fd=(np.array(p.gfun(x+h*direction)).ravel()-np.array(p.gfun(x-h*direction)).ravel())/(2*h);checks.append(dict(h=h,max_abs=float(abs(fd-J@direction).max()),relative=float(np.linalg.norm(fd-J@direction)/max(np.linalg.norm(fd),1e-12))))
# Same API with a RELEASE-only set: no required contact rows, all collision rows retained.
release=next(q for q in data['nodes'][0]['modes'] if not q['required_contact']);ct=dict(release);trial=CoupledProblem([[ct]],[x[:12]],[data['nodes'][0]['key_angles']],[p.times[0]],p.domain,p.bounds);release_rows=[r for r in trial.rows if r['name'].startswith('contact')];release_pass=sum(r['count'] for r in release_rows)==0
save('FINAL_DERIVATIVE_GUARD.json',dict(local_checks=rows,cold_full_jacobian_seconds=cold,directional_checks=checks,local_branches_pass=all(r['verified'] for r in rows) and checks[-1]['max_abs']<1e-3,nonsmooth_global_verified=False,release_interface=dict(mode=release,zero_contact_rows=release_pass,geometry_rows=trial.G.numel(),collision_piece_count=len(trial.nodes[0].pieces),no_other_song_solve=True),wall_seconds=time.monotonic()-start))
print('FINAL_GUARD',cold,checks,release_pass,flush=True)
