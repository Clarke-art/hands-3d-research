from guarded_node import *
from corridor_planner import CTX,keyangles,I,contact_transport
from kinematic_derivative_api import motion_derivatives
MD=motion_derivatives(F)
def tangents(X,T):
 v=[]
 for i in range(len(T)):
  if i==0:v.append(0*X[0])
  elif i==len(T)-1:v.append((X[i]-X[i-1])/(T[i]-T[i-1]))
  else:v.append((X[i+1]-X[i-1])/(T[i+1]-T[i-1]))
 return v
def hermite(z0,z1,v0,v1,dt,u):
 z=(2*u**3-3*u**2+1)*z0+(u**3-2*u**2+u)*dt*v0+(-2*u**3+3*u**2)*z1+(u**3-u**2)*dt*v1
 zd=(6*u**2-6*u)/dt*z0+(3*u**2-4*u+1)*v0+(-6*u**2+6*u)/dt*z1+(3*u**2-2*u)*v1
 zdd=(12*u-6)/dt**2*z0+(6*u-4)/dt*v0+(-12*u+6)/dt**2*z1+(6*u-2)/dt*v1
 return z,zd,zdd
def numeric_curve(Z,T,t):
 vv=tangents([np.array(z) for z in Z],T);i=min(max(int(np.searchsorted(T,t,side='right')-1),0),len(T)-2);u=(t-T[i])/(T[i+1]-T[i]);return hermite(np.array(Z[i]),np.array(Z[i+1]),vv[i],vv[i+1],T[i+1]-T[i],u)
class CorridorNode(GuardedNode):
 def __init__(self,z,cts,aa,t,plan):
  self.plan=plan;self.physical_time=t;self.extra_signature=None;self.corridor_switches=0
  super().__init__(z,cts,aa,t,(LOW,HIGH))
 def region_constraints(self,z):
  V=skin(state(z));p=self.plan;t=self.physical_time;event=CTX['time_span']['junction'];end=CTX['time_span']['first_full_press'];rows=[];sig=[]
  def separation(finger,key,axes,margin):
   loc=keylocal(V,key,self.angles[key['key_index']]);tri=loc[TR[np.flatnonzero(LABEL==finger-1)]];lo=tri.min(1);hi=tri.max(1);s=key['key_top_playable_surface'][0]
   allaxes=np.c_[s['xmin']-hi[:,0],lo[:,0]-s['xmax'],s['ymin']-hi[:,1],lo[:,1]-s['ymax'],lo[:,2]-s['z']]
   values=allaxes[:,axes];seps=values.max(1)*1000;win=int(np.argmin(seps));sig.append((finger,win,int(values[win].argmax())));return float(seps[win]-margin*1000)
  obstacle=c.KEYS[p['obstacle']['key_index']];ready=p['reference_time_allocation']['ready'];finger=p['target_contact']['finger']
  if t<event:
   # Whole-triangle clearance union. Descent exit differs by the boundary strategy.
   axes=[0,1,2,3,4] if t<=ready else ([0,1,2,4] if p['mode'].startswith('FRONT') else [0,1,3,4])
   rows.append(separation(finger,obstacle,axes,p['obstacle']['margin_m']))
  if t>=event:
   k=c.KEYS[p['target_contact']['midi']-21];pad=keylocal(np.array([V[int(RAW['pad_indices'][finger-1])]]),k,self.angles[k['key_index']])[0];s=p['target_subset']
   rows.extend([(pad[0]-s['xmin'])*1000,(s['xmax']-pad[0])*1000,(pad[1]-s['ymin'])*1000,(s['ymax']-pad[1])*1000]);sig.append(('target_subset',))
  if abs(t-end)<1e-9:
   # Recovering held key must be clear by the first full new-key press.
   oldkey=c.KEYS[p['held_contact']['midi']-21];rows.append(separation(p['held_contact']['finger'],oldkey,[2,4],p['release_escape']['margin_m']))
  return rows,tuple(sig)
 def value(self,z):
  b=super().value(z);nc=len(self.contacts);kept=[b[:nc]]
  # A selected clipped witness is already inside the patch by construction.
  # Drop its four tautological XY margins to avoid differentiating arbitrary min-witness tie choices.
  for ci in range(nc):kept.append(b[nc+10*ci+4:nc+10*ci+10])
  kept.append(b[nc+10*nc:]);extra,sig=self.region_constraints(z)
  if self.extra_signature is not None and sig!=self.extra_signature:self.corridor_switches+=1
  self.extra_signature=sig;self.last_signature=tuple(self.last_signature)+(sig,)
  return np.r_[*kept,extra]
class BridgeProblem:
 def __init__(self,plan,initial):
  self.plan=plan;self.T=np.array(plan['time_grid']);self.X=ca.MX.sym('corridor_controls',12*len(self.T));zs=[self.X[12*i:12*(i+1)] for i in range(len(self.T))];vs=tangents(zs,self.T);numvs=tangents([np.array(z) for z in initial],self.T);self.nodes=[];self.cbs=[];self.rows=[];g=[];low=[];high=[];self.samples=[];event=CTX['time_span']['junction'];vl=ca.DM(CTX['motion_bounds']['latent_velocity'])
  def add(v,lo,hi,name):
   v=ca.vec(v);n=v.numel();self.rows.append(dict(name=name,start=len(low),count=n));g.append(v);low.extend(np.broadcast_to(lo,(n,)));high.extend(np.broadcast_to(hi,(n,)))
  for i in range(len(self.T)-1):
   dt=self.T[i+1]-self.T[i]
   for u in [0.,.25,.5,.75,1.]:
    z,zd,zdd=hermite(zs[i],zs[i+1],vs[i],vs[i+1],dt,u);v,a,qr=MD(z,zd,zdd);add(ca.sumsqr(v/500),0,1,'wrist_velocity_'+str(i)+'_'+str(u));add(zd/vl,-1,1,'latent_velocity_'+str(i)+'_'+str(u));add(qr/240,-1,1,'mapped_joint_velocity_'+str(i)+'_'+str(u));add(z,LOW,HIGH,'authorized_domain_'+str(i)+'_'+str(u))
   for u in [0.,.5]:
    t=float(self.T[i]+u*dt);z,zd,zdd=hermite(zs[i],zs[i+1],vs[i],vs[i+1],dt,u);z0=numeric_curve(initial,self.T,t)[0];cts=plan['held_contact'] if t<event-1e-10 else plan['target_contact'];cts=[cts]
    if abs(t-event)<1e-10:cts=[plan['held_contact'],plan['target_contact']]
    node=CorridorNode(z0,cts,keyangles(t),t,plan);cb=NodeCallback('r2_'+plan['candidate_id']+'_'+str(len(self.nodes)),node,z0);self.nodes.append(node);self.cbs.append(cb);gg=cb(z);nc=len(cts);add(gg[:nc],-.0005,.0005,'contact_at_'+format(t,'.12f'));add(gg[nc:],0,np.inf,'geometry_and_corridor_at_'+format(t,'.12f'));self.samples.append(dict(time=t,contacts=cts))
  t=float(self.T[-1]);cts=[plan['target_contact']];node=CorridorNode(initial[-1],cts,keyangles(t),t,plan);cb=NodeCallback('r2_'+plan['candidate_id']+'_end',node,initial[-1]);self.nodes.append(node);self.cbs.append(cb);gg=cb(zs[-1]);add(gg[:1],-.0005,.0005,'contact_at_scope_end');add(gg[1:],0,np.inf,'geometry_and_corridor_at_scope_end');self.samples.append(dict(time=t,contacts=cts))
  self.G=ca.vertcat(*g);self.lo=np.array(low);self.hi=np.array(high);self.x0=np.array(initial).ravel();self.lbx=np.tile(LOW.astype(float),len(self.T));self.ubx=np.tile(HIGH.astype(float),len(self.T));self.lbx[:12]=self.x0[:12];self.ubx[:12]=self.x0[:12]
  scale=ca.DM(np.r_[[30,20,10],[8,8,12],[15]*4,1,1]);self.f=sum(.00001*ca.sumsqr((zs[i]-ca.DM(initial[i]))/scale) for i in range(len(zs)));self.gfun=ca.Function('r2_values_'+plan['candidate_id'],[self.X],[self.G]);self.jfun=ca.Function('r2_sparse_'+plan['candidate_id'],[self.X],[ca.jacobian(self.G,self.X)])
 def violation(self,x):
  g=np.array(self.gfun(x)).ravel();v=np.maximum(np.maximum(self.lo-g,g-self.hi),0);return float(v.max()),[dict(**r,violation=float(v[r['start']:r['start']+r['count']].max())) for r in self.rows]
