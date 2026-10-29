"""Original A2 sparse event/PCHIP formulation with native frozen skin pads.

All interior support states participate in ONE time-coupled solve. No independent
static solves, new bone freedom, obstacle engine, or saved animation.
"""
from support import *
sys.path.insert(0,str(OLD/'_deps'));sys.path.insert(0,str(A2))
import coordinated_motion as cm
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.sparse import lil_matrix
from persistence import load_record
# Exactly the historical frozen model/FK/LBS definitions, not historical search.
code=(PREV/'evaluate.py').read_text(encoding='utf-8-sig')
exec(compile(code[code.index('M=read(MODEL/'):code.index('ref_t=REF')],str(PREV/'evaluate.py')+':native_model_only','exec'))
functions_from(PREV/'evaluate.py',['surface_metrics'],globals())
def worlds(states,I):
 base=np.array(I['base_xyz_m']);const=np.array(I['static_root_base_matrix'])@np.array(I['full_root_rig_relation'])
 RR=cm.extra_rotation(states[:,3:6]);out=np.tile(np.eye(4),(len(states),1,1))
 out[:,:3,:3]=RR@const[:3,:3]
 out[:,:3,3]=base+states[:,:3]/1000+np.einsum('kij,j->ki',RR,const[:3,3]-base)
 return out
def native_skin(states,I,ids):
 q=states[:,6:].reshape(-1,5,4);basis=np.tile(np.eye(3),(len(states),len(REST),1,1))
 for j,d in enumerate(DIGITS):
  for k,name in enumerate(NAMES[j]):
   basis[:,BN[name]]=rot(np.radians(q[:,j,k]),AXES[j][k])
   if k==0:basis[:,BN[name]]=rot(np.radians(q[:,j,3]),SPREAD[j])@basis[:,BN[name]]
 return skin(basis,worlds(states,I),ids)[0]
class Problem:
 def __init__(self):
  self.P=read(O/'POLICY.json');self.I=read(O/'INPUT_BINDINGS.json');self.source,self.source_meta=load_record('SOURCE_PROBE.npz')
  self.events=self.I['p3_events'];self.co=cm.EventCoordinator(self.events,cm.DEFAULT_POLICY)
  self.T=np.array(self.P['control_times_sec']);self.E=np.array(self.P['evaluation_times_sec']);self.C=np.array(self.P['blender_check_times_sec']);self.K=len(self.T);self.N=len(self.E)
  def select(ts):
   ix=np.array([np.argmin(abs(self.source['times']-t)) for t in ts]);assert np.max(abs(self.source['times'][ix]-ts))<1e-10
   return ix
  self.ixE=select(self.E);self.ixT=select(self.T);self.ixC=select(self.C)
  self.sourceT=self.source['states'][self.ixT];self.sourceE=self.source['states'][self.ixE];self.angles=self.source['key_angles'][self.ixE]
  self.boundary=self.sourceT[[0,-1]].copy()
  self.padids=[m['mesh_vertex'] for m in MARK];self.xy0=self.co.xy_seed.copy()
  for i in range(7,15):
   t=self.events[i]['note_on']+.035;ix=select([t])[0] if self.T[0]<=t<=self.T[-1] else self.ixT[0]
   finger=self.I['original_events'][i]['finger']-1;p=self.source['vertices'][ix,self.padids[finger]]
   key=self.co.keys[self.events[i]['midi_note']];pv=np.array(key['press_pivot']);ang=self.source['key_angles'][ix,self.events[i]['key_index']]
   local=rot(-ang,key['press_axis'])@(p-pv)+pv
   self.xy0[i]=np.clip(local[:2]*1000,self.co.xy_low[i],self.co.xy_high[i])
  lo=np.r_[self.P['root_low'],cm.B[:,0].ravel()];hi=np.r_[self.P['root_high'],cm.B[:,1].ravel()]
  self.state_lo=lo;self.state_hi=hi
  self.low=np.r_[np.tile(lo,self.K-2),self.co.xy_low[8:14].ravel()];self.high=np.r_[np.tile(hi,self.K-2),self.co.xy_high[8:14].ravel()]
  self.x0=np.clip(np.r_[self.sourceT[1:-1].ravel(),self.xy0[8:14].ravel()],self.low+1e-7,self.high-1e-7)
  self.taskrows=[self.co.tasks(float(t)) for t in self.E]
  self.idx=np.zeros((self.N,5),int);self.weight=np.zeros((self.N,5));self.lift=np.zeros((self.N,5));self.assigned=np.zeros((self.N,5),bool)
  self.boxkeys=np.array(self.co.boxkeys);self.boxp=np.array([self.co.keys[m]['press_pivot'] for m in self.boxkeys]);self.boxlo=self.co.boxlo;self.boxhi=self.co.boxhi
  self.boxrot=cm.rotations(-self.angles[:,self.boxkeys-21],[1,0,0]);self.margin=np.full((self.N,5,len(self.boxkeys)),.003)
  for k,tasks in enumerate(self.taskrows):
   for j,i,l,w in tasks:
    self.idx[k,j]=i;self.weight[k,j]=w;self.lift[k,j]=l;self.assigned[k,j]=True
    if w>1:self.margin[k,j,self.boxkeys==self.events[i]['midi_note']]=-.004
  self.tops=np.array([s['z']+.0005 for s in self.co.surfaces]);self.pivots=np.array([self.co.keys[n['midi_note']]['press_pivot'] for n in self.events]);self.keyindex=np.array([n['key_index'] for n in self.events])
  self.targetrot=cm.rotations(self.angles[np.arange(self.N)[:,None],self.keyindex[self.idx]],[1,0,0])
  self.weights=self.P['weights'];self.dt=np.diff(self.T);self.calls=0
 def unpack(self,x):
  states=np.empty((self.K,26));states[[0,-1]]=self.boundary;states[1:-1]=x[:(self.K-2)*26].reshape(-1,26)
  xy=self.xy0.copy();xy[8:14]=x[(self.K-2)*26:].reshape(6,2)
  return states,xy
 def sample(self,x,times):
  states,xy=self.unpack(x);curve=PchipInterpolator(self.T,states,axis=0)
  return curve(np.asarray(times)),xy,curve
 def residual(self,x):
  self.calls+=1;controls,xy=self.unpack(x);st=PchipInterpolator(self.T,controls,axis=0)(self.E)
  pads=native_skin(st,self.I,self.padids);_,jp=cm.fk_batch(st)
  target0=np.concatenate([xy[self.idx]/1000,self.tops[self.idx][...,None]],axis=-1);pv=self.pivots[self.idx]
  target=np.einsum('kdij,kdj->kdi',self.targetrot,target0-pv)+pv;target[:,:,2]+=self.lift
  contact=((pads-target)*1000*self.weight[:,:,None]).reshape(self.N,-1)
  pp=np.einsum('kbij,kdbj->kdbi',self.boxrot,pads[:,:,None,:]-self.boxp[None,None,:,:])+self.boxp[None,None,:,:]
  dd=np.abs(pp-(self.boxlo+self.boxhi)/2)-(self.boxhi-self.boxlo)/2
  sdf=np.linalg.norm(np.maximum(dd,0),axis=-1)+np.minimum(np.max(dd,axis=-1),0)
  keyclear=(np.maximum(self.margin-sdf,0)*1000*self.weights['clearance']).reshape(self.N,-1)
  pts=jp[:,:,1:,:]
  covers=(pts[:,:,:,None,0]>self.boxlo[None,None,None,:,0])&(pts[:,:,:,None,0]<self.boxhi[None,None,None,:,0])&(pts[:,:,:,None,1]>self.boxlo[None,None,None,:,1])&(pts[:,:,:,None,1]<self.boxhi[None,None,None,:,1])
  top=np.max(np.where(covers,self.boxhi[None,None,None,:,2],-.010),axis=-1)
  jointclear=(np.maximum(top+.005-pts[:,:,:,2],0)*1000*.5).reshape(self.N,-1)
  neutral=(st[:,6:]-cm.NEUTRAL.ravel())*.055;prior=(st[:,6:]-self.sourceE[:,6:])*.055
  rotation=st[:,3:6]*.20;rootprior=(st[:,:3]-self.sourceE[:,:3])*np.array([.015,.035,.06])
  passive=np.maximum(.005-pads[:,:,2],0)*(~self.assigned)*1000*2
  pose=np.c_[contact,keyclear,jointclear,neutral,prior,rotation,rootprior,passive];self.pernode=pose.shape[1]
  velocity=np.diff(controls,axis=0)/self.dt[:,None];acceleration=np.diff(velocity,axis=0)/((self.dt[:-1]+self.dt[1:])/2)[:,None]
  added=(np.diff(controls[:,6:]-self.sourceT[:,6:],axis=0)/self.dt[:,None]);guard=np.maximum(abs(added)-180,0)*self.weights['added_velocity_excess']
  return np.r_[pose.ravel(),(velocity*np.array(self.weights['velocity'])).ravel(),(acceleration*np.array(self.weights['acceleration'])).ravel(),guard.ravel(),((xy[8:14]-self.xy0[8:14])*.12).ravel()]
 def sparsity(self):
  sample=self.residual(self.x0);J=lil_matrix((len(sample),len(self.x0)),dtype=np.int8);row=0
  def columns(nodes):
   return [c for n in nodes if 0<n<self.K-1 for c in range((n-1)*26,n*26)]
  for k,t in enumerate(self.E):
   hit=np.flatnonzero(abs(self.T-t)<1e-10)
   if len(hit):nodes=[int(hit[0])]
   else:
    a=int(np.searchsorted(self.T,t)-1);nodes=range(max(0,a-1),min(self.K,a+3))
   cols=columns(nodes)
   for j,i,l,w in self.taskrows[k]:
    if 8<=i<14:cols.extend([(self.K-2)*26+2*(i-8),(self.K-2)*26+2*(i-8)+1])
   J[row:row+self.pernode,cols]=1;row+=self.pernode
  for k in range(self.K-1):J[row:row+26,columns([k,k+1])]=1;row+=26
  for k in range(self.K-2):J[row:row+26,columns([k,k+1,k+2])]=1;row+=26
  for k in range(self.K-1):J[row:row+20,columns([k,k+1])]=1;row+=20
  J[row:row+12,(self.K-2)*26:]=1;row+=12
  assert row==len(sample)
  return J.tocsr()
