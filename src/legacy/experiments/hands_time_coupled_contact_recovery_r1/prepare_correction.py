from coupled_model import *
p,data=load_problem();primary=json.loads((O/'TIME_COUPLED_SOLVE_RESULTS.json').read_text());assert not primary['numeric_gate'];assert primary['solver_stats']['return_status']=='Maximum_WallTime_Exceeded';save('MAIN_SOLVE_RESULTS.json',primary)
# One existing common pose, analytically translated to each actual moving surface.
# No per-node optimization, no random seed and no interpolation of separate solutions.
seed=np.array(data['nodes'][0]['initial_latent']);zs=[];traces=[]
for node,source in zip(p.nodes,data['nodes']):
 z=seed.copy();trace=[]
 for iteration in range(2):
  g=node.value(z);eq=g[0];ct=source['contacts'][0];k=c.KEYS[ct['midi']-21];normal_z=c.axisrot(-source['key_angles'][ct['midi']-21],k['press_axis'])[2,2];trace.append(dict(gap_residual_mm=float(eq),root_z=float(z[2]),face=node.last_signature[0]));z[2]-=eq/normal_z
 zs.append(z);traces.append(trace)
x=np.array(zs).ravel();v,rows=p.violation(x);domain=bool(np.all(x>=p.lbx)&np.all(x<=p.ubx));segments=[]
for i in range(1,len(zs)):
 dt=p.times[i]-p.times[i-1];wa=KIN(zs[i-1])[0];wb=KIN(zs[i])[0];segments.append(dict(wrist_speed_mm_s=float(np.linalg.norm(np.array(wb-wa))*1000/dt),latent_rates=((zs[i]-zs[i-1])/dt).tolist()))
out=dict(method='Shared existing earliest recovered posture; analytic root-Z transport against original moving-key normal at each time; every node checked in the joint hard-constraint function',reason='Primary disconnected initialization starts with large motion infeasibility; no change to hard constraints, original objective or keys',initial_states=zs,max_violation=v,row_violations=rows,domain_pass=domain,segments=segments,traces=traces,per_node_optimization_count=0,scope='Coupled initialization only, not yet accepted geometry')
save('TARGETED_CORRECTION_INITIALIZATION.json',out);print('CORRECTION_INITIAL',v,domain,segments,flush=True)
assert domain and v<primary['violation'],'No targeted improvement; no second solve'
# Generate the sole correction driver with the same graph/objective and original node certificates.
s=(O/'solve_joint.py').read_text();s=s.replace("assert not (O/'TIME_COUPLED_SOLVE_RESULTS.json').exists(),'Do not repeat main solve'","assert not (O/'CORRECTION_SOLVE_RESULTS.json').exists(),'Do not repeat correction'")
s=s.replace('p,data=load_problem();deadline=beg+200',"p,data=load_problem();p.x0=np.array(json.loads((O/'TARGETED_CORRECTION_INITIALIZATION.json').read_text())['initial_states']).ravel();deadline=beg+110")
s=s.replace('max_iter=60,max_wall_time=170.','max_iter=25,max_wall_time=90.')
s=s.replace("'JOINT_PROGRESS.json'","'CORRECTION_PROGRESS.json'").replace("'TIME_COUPLED_SOLVE_RESULTS.json'","'CORRECTION_SOLVE_RESULTS.json'")
s=s.replace("id='coupled_'+str(i)","id='corrected_'+str(i)").replace('candidate_count=1','candidate_count=2')
# Feasibility-first: an actually feasible iterate satisfies the requested primary goal.
s=s.replace("return [int(time.monotonic()>deadline)]","return [int(time.monotonic()>deadline or (v<1e-6 and len(self.history)>1))]")
(O/'solve_correction.py').write_text(s,encoding='utf-8')
