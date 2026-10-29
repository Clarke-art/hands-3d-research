"""Generic time-coupled frozen-rig recovery. Inputs contain all musical identities."""
import sys,json,time,hashlib
from pathlib import Path
sys.dont_write_bytecode=True;O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));sys.path.insert(0,str(O.parent/'hands_contact_constrained_trajectory_planning_r1/deps'))
import casadi as ca
from rig_model import *
from contact_solver import ContactProblem
from kinematic_derivative_api import wrist_state_function
F=ca.Function.load(str(O.parent/'hands_contact_constrained_trajectory_planning_r1/FROZEN_SKIN_SYMBOLIC.casadi'));KIN=wrist_state_function(F)
def save(name,value): (O/name).write_text(json.dumps(value,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else str(x)))
class DynamicNode(ContactProblem):
 def __init__(self,rig_state,contact_set,moving_keys,event_time,joint_domain):
  contact_set=[ct for ct in contact_set if ct.get("required_contact",True)]
  super().__init__(rig_state,contact_set,moving_keys);self.time=event_time;self.domain=joint_domain;self.stats=dict(evaluations=0,jacobians=0,eval_seconds=0.,jac_seconds=0.,face_switches=0,collision_switches=0,self_feature_switches=0);self.signature=None;self.switch_log=[];self.localcache={};self.deadline=float('inf');self.last_signature=None
  self.patchfaces={ct['finger']:[int(i) for i in np.flatnonzero(LABEL==ct['finger']-1) if all(int(v) in set(META['pad_patches'][ct['finger']-1]) for v in TR[i])] for ct in contact_set}
 def value(self,z):
  if time.monotonic()>self.deadline:raise TimeoutError('numerical stage deadline')
  z=np.asarray(z).ravel();key=z.tobytes()
  if key in self.localcache:
   self.last_signature=self.localcache[key][1];return self.localcache[key][0]
  tick=time.perf_counter();st=state(z);V=skin(st);eq=[];gg=[];face_sig=[];key_sig=[]
  for ct in self.contacts:
   k=c.KEYS[ct['midi']-21];loc=keylocal(V,k,self.angles[ct['midi']-21]);candidates=[]
   for surfidx,s in enumerate(k['key_top_playable_surface']):
    for ti in self.patchfaces[ct['finger']]:
     poly=[a.copy() for a in loc[TR[ti]]]
     for ax,lim,sgn in [(0,s['xmin'],-1),(0,s['xmax'],1),(1,s['ymin'],-1),(1,s['ymax'],1)]:poly=clip(poly,ax,lim,sgn) if poly else []
     for vi,point in enumerate(poly):candidates.append((float(point[2]-s['z']),ti,surfidx,vi,point,max(a[2]-s['z'] for a in poly)))
   if not candidates:raise ValueError('NO_PROJECTED_PULP_FACE: reject trial, no vertex substitute')
   row=min(candidates,key=lambda r:r[0]);gap,ti,si,vi,pt,maxgap=row;s=k['key_top_playable_surface'][si];pad=loc[int(RAW['pad_indices'][ct['finger']-1])];eq.append(gap*1000+.005);face_sig.append((ti,si,vi));gg.extend([(pt[0]-s['xmin'])*1000-.001,(s['xmax']-pt[0])*1000-.001,(pt[1]-s['ymin'])*1000-.001,(s['ymax']-pt[1])*1000-.001,(pad[0]-s['xmin'])*1000-.01,(s['xmax']-pad[0])*1000-.01,(pad[1]-s['ymin'])*1000-.01,(s['ymax']-pad[1])*1000-.01,3-abs(pad[2]-s['z'])*1000,maxgap*1000-.001])
  TV=V[TR];tl=TV.min(1);th=TV.max(1)
  for pi,(note,N,dd,lo,hi) in enumerate(self.pieces):
   ids=np.flatnonzero(np.all(th>=lo-1e-8,1)&np.all(tl<=hi+1e-8,1))
   if len(ids):
    sig=np.einsum('tvi,ni->tvn',TV[ids],N)-dd;ids=ids[np.all(np.min(sig,axis=1)<=1e-8,axis=1)]
   peak=0.;winner=-1
   for ti in ids:
    depth,_=triangle_inside_depth(TV[ti],self.planes[pi])
    if depth>peak:peak=depth;winner=int(ti)
   gg.append(.20-peak);key_sig.append((int(note),pi,winner))
  self_sig=[]
  if len(self.pairs):
   U=unroot(V,st);A=np.einsum('pvi,pi->pv',U[TR[self.pairs[:,0]]],self.axes);B=np.einsum('pvi,pi->pv',U[TR[self.pairs[:,1]]],self.axes);gg.extend((A.min(1)-B.max(1))*1000-.02);self_sig=list(zip(A.argmin(1).tolist(),B.argmax(1).tolist()))
  signature=(tuple(face_sig),tuple(key_sig),tuple(self_sig));v=np.r_[eq,gg];self.stats['evaluations']+=1;self.stats['eval_seconds']+=time.perf_counter()-tick
  if self.signature is not None:
   changes=[signature[i]!=self.signature[i] for i in range(3)]
   for k,b in zip(['face_switches','collision_switches','self_feature_switches'],changes):self.stats[k]+=int(b)
   if any(changes) and len(self.switch_log)<100:self.switch_log.append(dict(evaluation=self.stats['evaluations'],face=changes[0],collision=changes[1],self_feature=changes[2],scope='Includes FD perturbations and line search; not accepted-state count'))
  self.signature=signature;self.last_signature=signature
  if len(self.localcache)>100:self.localcache.clear()
  self.localcache[key]=(v,signature);return v
 def jac(self,z,h=1e-4):
  t=time.perf_counter();z=np.asarray(z).ravel();cols=[]
  for i in range(12):
   step=h*(.1 if i>=10 else 1);dd=np.eye(12)[i]*step;cols.append((self.value(z+dd)-self.value(z-dd))/(2*step))
  self.stats['jacobians']+=1;self.stats['jac_seconds']+=time.perf_counter()-t;return np.array(cols).T
 def checked_jac(self,z):
  history=[];previous=self.jac(z,1e-4)
  for h in [1e-5,1e-6]:
   current=self.jac(z,h);error=float(np.max(abs(current-previous)));history.append(dict(h=h,max_abs_difference=error))
   if error<1e-3:
    self.last_derivative_guard=dict(status='LOCAL_DIFFERENCE_CONSISTENT',steps=history,universal_smoothness=False);return current
   previous=current
  self.last_derivative_guard=dict(status='NON_SMOOTH_OR_UNVERIFIED',steps=history)
  raise ValueError('NON_SMOOTH_OR_UNVERIFIED: reject derivative rather than silently freeze a branch')
class NodeJac(ca.Callback):
 def __init__(self,name,node,m):self.node=node;self.m=m;ca.Callback.__init__(self);self.construct(name,{})
 def get_n_in(self):return 2
 def get_n_out(self):return 1
 def get_sparsity_in(self,i):return ca.Sparsity.dense(12 if i==0 else self.m,1)
 def get_sparsity_out(self,i):return ca.Sparsity.dense(self.m,12)
 def eval(self,arg):return [ca.DM(self.node.checked_jac(np.array(arg[0]).ravel()))]
class NodeCallback(ca.Callback):
 def __init__(self,name,node,z):self.node=node;self.m=len(node.value(z));self.refs=[];ca.Callback.__init__(self);self.construct(name,{})
 def get_n_in(self):return 1
 def get_n_out(self):return 1
 def get_sparsity_in(self,i):return ca.Sparsity.dense(12,1)
 def get_sparsity_out(self,i):return ca.Sparsity.dense(self.m,1)
 def eval(self,arg):return [ca.DM(self.node.value(np.array(arg[0]).ravel()))]
 def has_jacobian(self):return True
 def get_jacobian(self,name,inames,onames,opts):
  cb=NodeJac(name,self.node,self.m);self.refs.append(cb);return cb
class CoupledProblem:
 def __init__(self,contact_sets,rig_states,moving_keys,time_grid,joint_domain,motion_bounds):
  contact_sets=[[ct for ct in contacts if ct.get("required_contact",True)] for contacts in contact_sets]
  self.times=np.array(time_grid);assert np.all(np.diff(self.times)>0);self.initial=np.asarray(rig_states);self.domain=joint_domain;self.bounds=motion_bounds;self.nodes=[DynamicNode(z,ct,aa,t,joint_domain) for z,ct,aa,t in zip(rig_states,contact_sets,moving_keys,time_grid)];self.cbs=[NodeCallback('node_'+str(i),p,z) for i,(p,z) in enumerate(zip(self.nodes,rig_states))];self.X=ca.MX.sym('all_states',12*len(time_grid));gs=[];lo=[];hi=[];self.rows=[];w=[];states=[]
  def add(g,l,h,label):
   g=ca.vec(g);gs.append(g);n=g.numel();self.rows.append(dict(name=label,start=len(lo),count=n));lo.extend(np.broadcast_to(l,(n,)));hi.extend(np.broadcast_to(h,(n,)))
  for i,cb in enumerate(self.cbs):
   z=self.X[i*12:(i+1)*12];g=cb(z);nc=len(contact_sets[i]);add(g[:nc],-.0005,.0005,'contact_'+str(i));add(g[nc:],0,np.inf,'geometry_'+str(i));wi,st=KIN(z);w.append(wi);states.append(st)
  self.objective=0;vl=ca.DM(motion_bounds['latent_velocity']);scale=ca.DM(np.r_[[30,20,10],[8,8,12],[15]*4,1,1])
  for i in range(len(time_grid)):
   z=self.X[i*12:(i+1)*12];self.objective+=.0001*ca.sumsqr((z-ca.DM(rig_states[i]))/scale)
   if i:
    dt=time_grid[i]-time_grid[i-1];dz=z-self.X[(i-1)*12:i*12];add(ca.sumsqr((w[i]-w[i-1])*1000/(motion_bounds['wrist_speed_mm_s']*dt)),0,1,'wrist_secant_'+str(i));add(dz/(vl*dt),-1,1,'latent_rate_'+str(i));add((states[i][6:]-states[i-1][6:])/(motion_bounds['mapped_joint_rate_deg_s']*dt),-1,1,'mapped_joint_rate_'+str(i));self.objective+=.00001*ca.sumsqr(dz/(vl*dt))
  self.G=ca.vertcat(*gs);self.lo=np.array(lo);self.hi=np.array(hi);self.gfun=ca.Function('coupled_constraints',[self.X],[self.G]);self.jfun=ca.Function('coupled_jacobian',[self.X],[ca.jacobian(self.G,self.X)]);self.x0=self.initial.ravel();self.lbx=np.tile(joint_domain[0],len(time_grid));self.ubx=np.tile(joint_domain[1],len(time_grid))
 def violation(self,x):
  g=np.array(self.gfun(x)).ravel();vv=np.maximum(np.maximum(self.lo-g,g-self.hi),0);return float(vv.max()),[dict(**r,max_violation=float(vv[r['start']:r['start']+r['count']].max())) for r in self.rows]
 def interface(self):return dict(variables=self.X.numel(),constraints=self.G.numel(),jacobian_shape=[self.G.numel(),self.X.numel()],structural_nonzeros=self.jfun.sparsity_out(0).nnz(),rows=self.rows,times=self.times,initial_states=self.initial,lower=self.lo,upper=self.hi,variable_lower=self.lbx,variable_upper=self.ubx,anchors=[],anchor_policy='All core nodes adjustable. External prior valid state held out, not constrained; no approach or exit compatibility claim',jacobian='Node-local adaptive-geometry central differences; sparse off-node zero blocks from true dependency. Adjacent wrist/joint blocks use validated pruned CasADi AD.',collision_threshold_mm=.20,actual_acceptance_mm=.25,self_pair_counts=[len(p.pairs) for p in self.nodes],all_key_piece_counts=[len(p.pieces) for p in self.nodes],contact_mode_mapping=[p.contacts for p in self.nodes])
def load_problem():
 data=json.loads((O/'RECOVERY_TIMELINE_INPUT.json').read_text());n=data['nodes'];p=CoupledProblem([r['contacts'] for r in n],[r['initial_latent'] for r in n],[r['key_angles'] for r in n],[r['time'] for r in n],(data['joint_domain']['lower'],data['joint_domain']['upper']),data['motion_bounds']);return p,data
