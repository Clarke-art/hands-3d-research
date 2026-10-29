"""Frozen geometric FK/LBS only: no target C1 joint trajectory is read."""
from support import *
sys.path.insert(0,str(OLD/'_deps'))
import numpy as np
M=read(MODEL/'SOURCE_MODEL_MANIFEST.json')
with np.load(MODEL/'SOURCE_MODEL.npz',allow_pickle=False) as archive:
 D={k:archive[k] for k in ['rest_vertices','rest_matrices','parents','weights','mesh_to_rig']}
SH=np.load(MODEL/'SHAPE_DELTA.npz',allow_pickle=False)['delta']
CAN=read(OLD/'RIG_CANONICAL_PROBE_R1.json')['R']['bones'];MARK=read(OLD/'FINGERTIP_CONTACT_MARKERS_R1.json')['markers']['R'];KEYS=read(OLD/'KEYBOARD_88_KEY_TABLE_R1.json')['keys']
BN={n:i for i,n in enumerate(M['bones'])};REST=D['rest_matrices'].astype(float)
REL=np.array([np.linalg.inv(REST[p])@r if p>=0 else r for p,r in zip(D['parents'],REST)])
W=D['weights'];W=W/np.maximum(W.sum(1,keepdims=True),1e-12)
H=np.c_[D['rest_vertices'],np.ones(len(W))]@D['mesh_to_rig'].T;LOCAL=np.einsum('bij,vj->bvi',np.linalg.inv(REST),H)*W.T[:,:,None]
SHH=np.c_[SH,np.zeros(len(W))]@D['mesh_to_rig'].T;SHLOCAL=np.einsum('bij,vj->bvi',np.linalg.inv(REST),SHH)*W.T[:,:,None]
DIGITS=['THUMB','INDEX','MIDDLE','RING','LITTLE'];AXES=[];NAMES=[];SPREAD=[]
for digit in DIGITS:
 names=[f'{digit}_{j}_R' for j in (['CMC','MCP','IP'] if digit=='THUMB' else ['MCP','PIP','DIP'])];rests=[np.array(CAN[n]['matrix']) for n in names];axes=[]
 for mat in rests:
  a=np.cross(mat[:3,1],[0,0,-1]);a/=np.linalg.norm(a);axes.append(mat[:3,:3].T@a)
 AXES.append(axes);NAMES.append(names);SPREAD.append(rests[0][:3,:3]<REDACTED_EMAIL>([0,0,1]))
functions_from(PREV/'evaluate.py',['rot','forward','skin','surface_metrics'],globals())
functions_from(MODEL/'whole_phrase_model.py',['component_planes'],globals())
ROIS=read(ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1/DIGIT_SKIN_ROI.json')
COMPONENTS=[(k,g,component_planes(g)) for k in KEYS for g in k['geometry']]
PADIDS=[r['mesh_vertex'] for r in MARK]
def basis(q):
 q=np.atleast_3d(q) if np.asarray(q).ndim==2 else np.asarray(q)
 if q.shape==(5,4,1):q=q[:,:,0][None]
 out=np.tile(np.eye(3),(len(q),len(REST),1,1))
 for j in range(5):
  for k,name in enumerate(NAMES[j]):
   out[:,BN[name]]=rot(np.radians(q[:,j,k]),AXES[j][k])
   if k==0:out[:,BN[name]]=rot(np.radians(q[:,j,3]),SPREAD[j])@out[:,BN[name]]
 return out
def native(q,world,ids=None):
 q=np.asarray(q);q=q[None] if q.ndim==2 else q;world=np.asarray(world);world=world[None] if world.ndim==2 else world
 return skin(basis(q),np.broadcast_to(world,(len(q),4,4)),np.arange(len(W)) if ids is None else ids)[0]
def point_on_key(key,xy_mm,angle,lift=0):
 surf=key['key_top_playable_surface'][0];pv=np.array(key['press_pivot']);p=np.r_[np.asarray(xy_mm)/1000,surf['z']+.0005]
 p=rot(angle,key['press_axis'])@(p-pv)+pv;p[2]+=lift;return p
def inset(key):
 s=key['key_top_playable_surface'][0];pad=np.array([.002,.002] if key['color']=='BLACK' else [.003,.007])
 return (np.array([s['xmin'],s['ymin']])+pad)*1000,(np.array([s['xmax'],s['ymax']])-pad)*1000
def depths(points,angles,own_key=None):
 out=[];witness=[]
 for key,g,pl in COMPONENTS:
  if own_key is not None and key['key_index']==own_key:continue
  pv=np.array(key['press_pivot']);local=(points-pv)@rot(angles[key['key_index']],key['press_axis'])+pv;kv=np.array(g['vertices'])
  # Fixed residual length; no data-dependent broad-phase changes.
  d=-np.max(local@pl[:,:3].T-pl[:,3],axis=1)*1000
  out.append(d);witness.append((key,g))
 return np.array(out),witness
def local_fit_inputs(q,world,angles,event,preferred_xy,policy):
 j=event['finger']-1;key=KEYS[event['key_index']];loxy,hixy=inset(key);low=np.r_[policy['joint_bounds_deg'][j][0],loxy];high=np.r_[policy['joint_bounds_deg'][j][1],hixy]
 ids=np.flatnonzero(W[:,[i for i,n in enumerate(M['bones']) if n.startswith(DIGITS[j]+'_')]].sum(1)>.05)
 qref=q[j].copy();seed=np.clip(np.r_[qref,preferred_xy],low+1e-7,high-1e-7)
 def residual(x):
  changed=q.copy();changed[j]=x[:4];V=native(changed,world)[0];target=point_on_key(key,x[4:],angles[key['key_index']])
  pad=(V[PADIDS[j]]-target)*1000*6.
  ds,_=depths(V[ids],angles,key['key_index'])
  # Existing simple convex body depth + native skin, one fixed local policy.
  # 0.5mm nominal outside margin; accepted intrusion gate remains <=0.5mm.
  clear=np.maximum(ds+.5,0).ravel()*2.
  return np.r_[pad,clear,(x[:4]-qref)*.055,(x[4:]-preferred_xy)*.12]
 return seed,low,high,residual,ids
