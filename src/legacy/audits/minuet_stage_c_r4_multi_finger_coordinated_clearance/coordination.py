"""Finite local joint-increment coordination over frozen FK and actual LBS skin.

No root unknowns, no new music planner, no per-pitch pose templates.
"""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
OLD=ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1'
sys.path.insert(0,str(OLD/'_deps'));sys.path.insert(0,str(OLD))
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
import performance_core as c
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item(),allow_nan=False),encoding='utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
TL=read(ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance/PERFORMANCE_TIMELINE.json')
M=read(P/'LOCAL_MODEL_MANIFEST.json');D=dict(np.load(P/'LOCAL_MODEL.npz'))
BN={n:i for i,n in enumerate(M['bone_names'])};IDS={v:i for i,v in enumerate(M['ids'])};DIGITS=['INDEX','MIDDLE','RING']
def rot(a,axis):
    axis=np.asarray(axis);axis=axis/np.linalg.norm(axis);x,y,z=axis;K=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
    return np.eye(3)+np.sin(a)[...,None,None]*K+(1-np.cos(a))[...,None,None]*(K@K)
REST=D['rest_matrices'];INV=np.linalg.inv(REST)
REL=np.array([np.linalg.inv(REST[p])@r if p>=0 else r for p,r in zip(D['parents'],REST)])
W=D['weights'];W=W/np.maximum(W.sum(1,keepdims=True),1e-12)
H=np.c_[D['rest_vertices'],np.ones(len(W))]@D['mesh_to_rig'].T
LOCAL=np.einsum('bij,vj->bvi',INV,H)*W.T[:,:,None]
ROI={d:np.array([IDS[v] for v in M['rois'][d]['vertices']]) for d in M['rois']}
TRIS={d:np.array([[IDS[f[0]],IDS[f[i]],IDS[f[i+1]]] for f in M['rois'][d]['faces'] for i in range(1,len(f)-1)]) for d in ROI}
PADS=np.array([IDS[m['mesh_vertex']] for m in M['markers']])
def interpolate(arr,t):
    shape=arr.shape[1:];flat=arr.reshape(len(D['times']),-1)
    return np.column_stack([np.interp(t,D['times'],flat[:,j]) for j in range(flat.shape[1])]).reshape((len(t),)+shape)
class Context:
    def __init__(self,times):
        self.t=np.atleast_1d(times);self.K=len(self.t)
        q=interpolate(D['quat'],self.t);q/=np.linalg.norm(q,axis=-1,keepdims=True)
        self.base=Rotation.from_quat(q[:,:,[1,2,3,0]].reshape(-1,4)).as_matrix().reshape(self.K,-1,3,3)
        self.world=interpolate(D['rig_world'],self.t);self.angles=interpolate(D['key_angles'],self.t)
        self.original=self.skin(np.zeros((self.K,3,4)))
        self.active=[]
        for t in self.t:
            self.active.append({n['finger']-1:n for n in TL['notes'] if n['hand']=='R' and n['note_on']<=t<n['note_off']})
        self.keys=[k for k in c.KEYS if k['color']=='BLACK' and 66<=k['midi_note']<=80]
        self.key_lo=np.array([np.array(k['geometry'][0]['vertices']).min(0) for k in self.keys]);self.key_hi=np.array([np.array(k['geometry'][0]['vertices']).max(0) for k in self.keys]);self.key_pv=np.array([k['press_pivot'] for k in self.keys]);self.key_inv=rot(-self.angles[:,[k['key_index'] for k in self.keys]],[1,0,0])
    def skin(self,delta,return_pose=False):
        basis=self.base.copy();delta=np.radians(np.asarray(delta).reshape(self.K,3,4))
        for j,d in enumerate(DIGITS):
            names,rels,axes,spread,pad=c.SETUPS['R',d]
            for k,name in enumerate(names):
                b=BN[name];basis[:,b]=basis[:,b]@rot(delta[:,j,k],axes[k])
                if k==0:basis[:,b]=rot(delta[:,j,3],spread)@basis[:,b]
        poses=[]
        for b,p in enumerate(D['parents']):
            mat=np.broadcast_to(REL[b],(self.K,4,4)).copy();J=np.broadcast_to(np.eye(4),(self.K,4,4)).copy();J[:,:3,:3]=basis[:,b];mat=mat@J
            if p>=0:mat=poses[p]@mat
            poses.append(mat)
        poses=np.stack(poses,axis=1);v=np.einsum('kbij,bvj->kvi',poses,LOCAL)
        V=np.einsum('kij,kvj->kvi',self.world,v)[:,:,:3]
        return (V,poses,basis) if return_pose else V
    def normals(self,V,d):
        tri=TRIS[d];normal=np.cross(V[:,tri[:,1]]-V[:,tri[:,0]],V[:,tri[:,2]]-V[:,tri[:,0]])
        out=np.zeros_like(V)
        for k in range(self.K):
            for j in range(3):np.add.at(out[k],tri[:,j],normal[k])
        out/=np.maximum(np.linalg.norm(out,axis=-1,keepdims=True),1e-12)
        return out[:,ROI[d]]
    def pair_clearance(self,V):
        out=[]
        for a,b in [('INDEX','MIDDLE'),('MIDDLE','RING'),('RING','LITTLE')]:
            pa=V[:,ROI[a]];pb=V[:,ROI[b]];na=self.normals(V,a);nb=self.normals(V,b)
            dist=np.sum((pa[:,:,None]-pb[:,None])**2,axis=-1)
            for aa,bb,nn,ds in [(pa,pb,nb,dist),(pb,pa,na,dist.transpose(0,2,1))]:
                ix=np.argmin(ds,axis=-1);near=bb[np.arange(self.K)[:,None],ix];normal=nn[np.arange(self.K)[:,None],ix]
                signed=np.sum((aa-near)*normal,axis=-1)*1000;distance=np.sqrt(ds.min(axis=-1))*1000
                # Finite open distal patches: only local nearest-surface constraints,
                # remote points cannot be classified as inside from normals alone.
                out.append(np.where(distance<8,np.maximum(.7-signed,0),0))
        return np.concatenate(out,axis=1)
    def black_clearance(self,V):
        vv=np.einsum('kbij,kvbj->kvbi',self.key_inv,V[:,:,None]-self.key_pv[None,None])+self.key_pv[None,None]
        dd=np.abs(vv-(self.key_lo+self.key_hi)/2)-(self.key_hi-self.key_lo)/2
        sdf=np.linalg.norm(np.maximum(dd,0),axis=-1)+np.minimum(dd.max(axis=-1),0)
        margin=np.full_like(sdf,.0005)
        for k,active in enumerate(self.active):
            for j,n in active.items():
                if n['key_color']=='BLACK':
                    bi=next(i for i,key in enumerate(self.keys) if key['midi_note']==n['midi_note'])
                    d=c.DIGITS[j]
                    if d in ROI:margin[k,ROI[d],bi]=-.00065
        return np.maximum(margin-sdf,0)*1000,sdf*1000
    def contacts(self,V):
        values=np.zeros((self.K,3,6));details=[]
        for k,active in enumerate(self.active):
            for j,n in active.items():
                if j not in [1,2,3]:continue
                pt=V[k,PADS[j]];old=self.original[k,PADS[j]];key=c.KEYS[n['key_index']];pv=np.array(key['press_pivot']);R=c.axisrot(-self.angles[k,n['key_index']],[1,0,0]);p=R@(pt-pv)+pv;po=R@(old-pv)+pv
                s=min(key['key_top_playable_surface'],key=lambda s:np.linalg.norm(po[:2]-np.clip(po[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']])))
                gap=(p[2]-s['z'])*1000;miss=np.maximum([s['xmin']+.002-p[0],p[0]-s['xmax']+.002,s['ymin']+.001-p[1],p[1]-s['ymax']+.001],0)*1000
                values[k,j-1]=[(gap-.5)*12,miss.max()*15,(p[0]-po[0])*1000*.4,(p[1]-po[1])*1000*.2,max(0,abs(p[0]-po[0])*1000-5)*8,max(0,abs(p[1]-po[1])*1000-12)*8]
                details.append(dict(t=float(self.t[k]),note=n['note_id'],gap_mm=float(gap),horizontal_margin_violation_mm=float(miss.max()),pad_movement_mm=float(np.linalg.norm(pt-old)*1000)))
        return values,details
    def residual(self,delta):
        delta=np.asarray(delta).reshape(self.K,3,4);V=self.skin(delta);black,_=self.black_clearance(V);pairs=self.pair_clearance(V);contact,_=self.contacts(V)
        # Source curve fidelity, moderate multi-joint change, no imposed V/claw pose.
        prior=delta*np.array([.035,.045,.060,.085]);floor=np.maximum(-.001-V[:,:,2],0)*1000
        # Active/releasing skin follows the real moving target key, not the
        # stationary white-key plane. The floor is a safeguard, not a contact goal.
        for k,t in enumerate(self.t):
            owned={n['finger']-1:n for n in TL['notes'] if n['hand']=='R' and n['note_on']<=t<n['note_off']+.07}
            for j,n in owned.items():
                d=c.DIGITS[j]
                if d not in ROI:continue
                ids=ROI[d];key=c.KEYS[n['key_index']];pv=np.array(key['press_pivot']);R=c.axisrot(-self.angles[k,n['key_index']],[1,0,0]);pts=(V[k,ids]-pv)@R.T+pv
                floor[k,ids]=np.maximum(key['key_top_playable_surface'][0]['z']-.001-pts[:,2],0)*1000
        return np.c_[contact.reshape(self.K,-1),black.reshape(self.K,-1)*7,pairs*5,prior.reshape(self.K,-1),floor*5]
DELTA_LIMIT=np.array([18,25,22,14.])
def original_degrees(times):
    a=np.load(ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement/source_numeric.npz')
    return np.array([np.column_stack([np.interp(times,a['times'],a['qdeg'][:,j,k]) for k in range(4)]) for j in [1,2,3]]).transpose(1,0,2)
def bounds(times):
    q=original_degrees(times);lo=np.maximum(-DELTA_LIMIT,np.array([0,0,0,-28])-q);hi=np.minimum(DELTA_LIMIT,np.array([75,95,65,28])-q)
    return lo,hi
