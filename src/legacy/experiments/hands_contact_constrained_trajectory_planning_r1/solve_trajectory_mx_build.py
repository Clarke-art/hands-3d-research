import sys,json,time,math,os
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));from symbolic_skin import *
B=json.loads((O/'TRAJECTORY_BENCHMARK_INPUT.json').read_text());I=json.loads((O/'EXPERIMENT_INPUT.json').read_text());chart=json.loads((O/'ACTIVE_GEOMETRY_CHART.json').read_text());data=np.load(O/'COLLOCATION_KEY_STATES.npz');assert json.loads((O/'SYMBOLIC_MODEL_VALIDATION.json').read_text())['verified'];assert json.loads((O/'INPUT_SCENE_VERIFICATION.json').read_text())['native_identity']
z0=np.array(B['Start']['local']['latent']);f=ca.Function.load(str(O/'FROZEN_SKIN_SYMBOLIC.casadi'));_,R=symbolic_model();start,end=B['EventTime']['local'];J=I['junction_time'];dur=[J-start,end-J];V0=skin(state(z0));selfrows=[]
for row in chart['self_chart']:
 margin=(V0[TR[row['a']]]@row['axis']).min()-(V0[TR[row['b']]]@row['axis']).max()
 if margin<.0035:selfrows.append(row)
# Two quintic Bernstein elements; coefficients of both phases are jointly optimized.
C=[ca.MX.sym('C'+str(i),12,6) for i in range(2)];X=ca.vertcat(*[ca.vec(x) for x in C]);gs=[];lbs=[];ubs=[];names=[]
def add(g,lo,hi,name):
 g=ca.vec(g);n=int(g.numel());gs.append(g);lbs.extend(np.broadcast_to(lo,(n,)).tolist());ubs.extend(np.broadcast_to(hi,(n,)).tolist());names.append(dict(name=name,start=len(lbs)-n,count=n))
def curve(cc,s,h,order=0):
 deg=5;fac=1
 for k in range(order):cc=cc[:,1:]-cc[:,:-1];fac*=deg/h;deg-=1
 return fac*sum([math.comb(deg,k)*s**k*(1-s)**(deg-k)*cc[:,k] for k in range(deg+1)],ca.MX.zeros(12,1))
add(C[0][:,0]-z0,0,0,'initial_position')
for order in range(3):add((curve(C[0],1,dur[0],order)-curve(C[1],0,dur[1],order))*(.01**order),0,0,'phase_C'+str(order))
vl=np.r_[[500]*3,[120]*3,[240]*4,5,8];al=np.r_[[50000]*3,[12000]*3,[24000]*4,500,800];objective=0
for i,cc in enumerate(C):
 h=dur[i];dc=5*(cc[:,1:]-cc[:,:-1])/h;ac=4*(dc[:,1:]-dc[:,:-1])/h;jc=3*(ac[:,1:]-ac[:,:-1])/h
 add(dc/ca.repmat(ca.DM(vl),1,5),-1,1,'coefficient_velocity_'+str(i));add(ac/ca.repmat(ca.DM(al),1,4),-1,1,'coefficient_acceleration_'+str(i));objective+=ca.sumsqr(dc/ca.repmat(ca.DM(vl),1,5))+.01*ca.sumsqr(ac/ca.repmat(ca.DM(al),1,4))+.001*ca.sumsqr(jc/ca.repmat(ca.DM(al*100),1,3))
# Wrist derivatives and actual mapped engineering joint rate from symbolic FK.
zz=ca.MX.sym('zz',12);zd=ca.MX.sym('zd',12);za=ca.MX.sym('za',12);vv,ww,ss=f(zz);wv=ca.jtimes(ww,zz,zd)*1000;wa=ca.jtimes(wv,zz,zd)+ca.jtimes(wv,zd,za);sv=ca.jtimes(ss[6:],zz,zd);kin=ca.Function('kin',[zz,zd,za],[wv,wa,sv])
for it,t in enumerate(data['times']):
 ph=0 if t<J-1e-9 else 1;s=(t-(start if ph==0 else J))/dur[ph];z=curve(C[ph],s,dur[ph]);vel=curve(C[ph],s,dur[ph],1);acc=curve(C[ph],s,dur[ph],2);V,wr,st=f(z);wv,wa,sv=kin(z,vel,acc);add(ca.sumsqr(wv/500),0,1,'wrist_speed_'+str(it));add(ca.sumsqr(wa/50000),0,1,'wrist_acc_'+str(it));add(sv/240,-1,1,'mapped_joint_rate_'+str(it));angles=data['angles'][it];cts=I['contacts'] if abs(t-J)<1e-9 else [I['contacts'][0 if t<J else 1]]
 def keycoords(points,midi):
  k=c.KEYS[midi-21];pv=ca.DM(k['press_pivot']);n=points.size2();return ca.DM(c.axisrot(-angles[midi-21],[1,0,0]))@(points-ca.repmat(pv,1,n))+ca.repmat(pv,1,n)
 for ct in cts:
  k=c.KEYS[ct['midi']-21];surf=k['key_top_playable_surface'][0];pt=keycoords(V[:,ct['vertices']]@ca.DM(ct['barycentric']),ct['midi']);pad=keycoords(V[:,int(RAW['pad_indices'][ct['finger']-1])],ct['midi']);add((pt[2]-surf['z'])*1000+.005,-.0005,.0005,'material_contact_'+str(it));
  for p,margin,label in [(pt,.001,'witness'),(pad,.01,'pad')]:
   add(ca.vertcat((p[0]-surf['xmin'])*1000,(surf['xmax']-p[0])*1000,(p[1]-surf['ymin'])*1000,(surf['ymax']-p[1])*1000),margin,np.inf,label+'_region_'+str(it))
  add((pad[2]-surf['z'])*1000,-3,3,'pad_height_'+str(it))
 for n,row in enumerate(chart['key_chart']):
  T=keycoords(V[:,row['vertices']],row['midi']);slack=(row['offset_key_local']-ca.DM(row['normal_key_local']).T@T)*1000;add(slack,-np.inf,.20,'key_certificate_'+str(it)+'_'+str(n))
 for n,row in enumerate(selfrows):
  a=ca.DM(row['axis']);A=a.T@V[:,TR[row['a']].tolist()];BB=a.T@V[:,TR[row['b']].tolist()];sep=ca.mmin(A)-ca.mmax(BB);add(sep*1000,.02,np.inf,'self_chart_'+str(it)+'_'+str(n))
objective+=.001*ca.sumsqr(X-ca.repmat(ca.DM(z0),12,1));G=ca.vertcat(*gs);gfun=ca.Function('constraints',[X],[G]);lbx=np.tile(LOW,12);ubx=np.tile(HIGH,12);x0=np.tile(z0,12)
meta=dict(method='CasADi3.7.2/IPOPT joint-time two quintic Bernstein elements, direct path collocation',variables=int(X.numel()),constraints=int(G.numel()),degrees=5,phases=2,collocation_times=data['times'].tolist(),joint_time_continuity='C2 analytic polynomial constraints',key_certificate_count=len(chart['key_chart']),self_certificate_count=len(selfrows),contact_tolerance_mm=.0005,internal_depth_limit_mm=.20,velocity_limits=vl.tolist(),acceleration_limits=al.tolist(),initialization='constant common static boundary, never old failed path',start_fixed=True,end_pose_free_required_contact=True,max_wall_seconds=240,names=names)
(O/'NLP_DESIGN.json').write_text(json.dumps(meta,indent=2));print('NLP',meta['variables'],meta['constraints'],'self',len(selfrows),flush=True)
tick=time.perf_counter();solver=ca.nlpsol('contact_trajectory','ipopt',dict(x=X,f=objective,g=G),dict(print_time=True,ipopt=dict(max_iter=150,max_wall_time=235.,tol=1e-6,constr_viol_tol=1e-6,acceptable_iter=0,hessian_approximation='limited-memory',print_level=5,linear_solver='mumps')));construction=time.perf_counter()-tick;beg=time.perf_counter();sol=solver(x0=x0,lbx=lbx,ubx=ubx,lbg=lbs,ubg=ubs);elapsed=time.perf_counter()-beg;stats=solver.stats();xx=np.array(sol['x']).ravel();gg=np.array(gfun(xx)).ravel();violation=float(np.maximum(np.array(lbs)-gg,np.maximum(gg-np.array(ubs),0)).max());out=dict(metadata=meta,stats=stats,solver_construction_seconds=construction,solver_wall_seconds=elapsed,numerical_wall_seconds=construction+elapsed+chart['setup_numerical_seconds'],constraint_violation_scaled=violation,coefficients=[xx[i*72:(i+1)*72].reshape(6,12).T.tolist() for i in range(2)],source_start=start,junction=J,end=end,authority='DESIGN_PROVISIONAL',actual_geometry='NOT_YET_VALIDATED');(O/'CASADI_LOCAL_SOLVE.json').write_text(json.dumps(out,indent=2,default=lambda o:o.tolist() if hasattr(o,'tolist') else str(o)));print('SOLVE_END',elapsed,stats['return_status'],violation,flush=True)
