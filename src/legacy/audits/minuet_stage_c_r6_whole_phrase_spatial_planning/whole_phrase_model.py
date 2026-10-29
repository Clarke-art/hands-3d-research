"""Five-digit absolute engineering coordinates and frozen, weighted skin.

No event-specific pose constants. Root and key matrices are sampled from C1.
"""
from common import *
sys.path.insert(0,str(OLD))
import performance_core as c
from scipy.spatial.transform import Rotation
M=read(P/'SOURCE_MODEL_MANIFEST.json')
D=dict(np.load(P/'SOURCE_MODEL.npz'))
S=dict(np.load(ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement/source_numeric.npz'))
BN={n:i for i,n in enumerate(M['bones'])}
REST=D['rest_matrices'];INV=np.linalg.inv(REST)
REL=np.array([np.linalg.inv(REST[p])@r if p>=0 else r for p,r in zip(D['parents'],REST)])
W=D['weights'];W=W/np.maximum(W.sum(1,keepdims=True),1e-12)
H=np.c_[D['rest_vertices'],np.ones(len(W))]@D['mesh_to_rig'].T
LOCAL=np.einsum('bij,vj->bvi',INV,H)*W.T[:,:,None]
SHAPE=np.load(P/'SHAPE_DELTA.npz')['delta']
SH=np.c_[SHAPE,np.zeros(len(W))]@D['mesh_to_rig'].T
SHLOCAL=np.einsum('bij,vj->bvi',INV,SH)*W.T[:,:,None]
def rot(a,axis):
    v=np.asarray(axis)/np.linalg.norm(axis);x,y,z=v
    K=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
    return np.eye(3)+np.sin(a)[...,None,None]*K+(1-np.cos(a))[...,None,None]*(K@K)
def interp(a,t):
    flat=a.reshape(len(D['times']),-1)
    return np.column_stack([np.interp(t,D['times'],flat[:,j]) for j in range(flat.shape[1])]).reshape((len(t),)+a.shape[1:])
def source_angles(t):
    return np.column_stack([np.interp(t,S['times'],S['qdeg'].reshape(-1,20)[:,j]) for j in range(20)]).reshape(-1,5,4)
class Skin:
    def __init__(self,t,ids=None):
        self.t=np.atleast_1d(t);self.K=len(self.t)
        self.ids=np.arange(len(W)) if ids is None else np.array(ids)
        self.world=interp(D['rig_world'],self.t);self.angles=interp(D['key_angles'],self.t)
        quat=interp(D['quat'],self.t);quat/=np.linalg.norm(quat,axis=-1,keepdims=True)
        self.base=Rotation.from_quat(quat[:,:,[1,2,3,0]].reshape(-1,4)).as_matrix().reshape(self.K,-1,3,3)
        self.local=LOCAL[:,self.ids]
        self.shlocal=SHLOCAL[:,self.ids]
        self.bone_ids=[np.flatnonzero(W[self.ids,b]>0) for b in range(len(REST))]
    def __call__(self,q=None,original=False):
        basis=self.base.copy()
        if not original:
            q=np.radians(np.asarray(q).reshape(self.K,5,4))
            for j,d in enumerate(c.DIGITS):
                names,_,axes,spread,_=c.SETUPS['R',d]
                for k,name in enumerate(names):
                    basis[:,BN[name]]=rot(q[:,j,k],axes[k])
                    if k==0:basis[:,BN[name]]=rot(q[:,j,3],spread)@basis[:,BN[name]]
        opp=np.arctan2(basis[:,BN['THUMB_CMC_R'],2,1],basis[:,BN['THUMB_CMC_R'],2,2])
        mcp=np.arctan2(basis[:,BN['THUMB_MCP_R'],2,1],basis[:,BN['THUMB_MCP_R'],2,2])
        shape=np.maximum(np.clip((-opp-.37)/.06,0,1),np.clip((-opp-.15)/.15,0,1)*np.clip((-mcp-.175)/.175,0,1))
        poses=[];V=np.zeros((self.K,len(self.ids),4))
        for b,p in enumerate(D['parents']):
            J=np.broadcast_to(np.eye(4),(self.K,4,4)).copy();J[:,:3,:3]=basis[:,b]
            mat=REL[b]@J
            if p>=0:mat=poses[p]@mat
            poses.append(mat)
            ids=self.bone_ids[b]
            if len(ids):
                V[:,ids]+=np.einsum('kij,vj->kvi',mat,self.local[b,ids])
                V[:,ids]+=np.einsum('kij,vj->kvi',mat,self.shlocal[b,ids])*shape[:,None,None]
        return np.einsum('kij,kvj->kvi',self.world,V)[:,:,:3]

def key_components():
    notes=[n['midi_note'] for n in TL['notes'] if n['hand']=='R']
    # One whole-phrase neighborhood, including original known F#4/G#5 edges.
    return [(k,g) for k in c.KEYS if min(notes)-3<=k['midi_note']<=max(notes)+3 for g in k['geometry']]
def component_planes(g):
    v=np.array(g['vertices']);center=v.mean(0);planes=[]
    for tri in np.asarray(g['triangles']).reshape(-1,3):
        a,b,c0=v[tri];n=np.cross(b-a,c0-a);l=np.linalg.norm(n)
        if l<1e-12:continue
        n/=l
        if np.dot(n,center-a)>0:n=-n
        planes.append(np.r_[n,np.dot(n,a)])
    planes=np.unique(np.round(planes,10),axis=0)
    assert np.max(v@planes[:,:3].T-planes[:,3])<1e-7
    return planes
def body_depth(points,key,g,angles):
    pv=np.array(key['press_pivot']);R=rot(-angles[:,key['key_index']],[1,0,0])
    local=np.einsum('kij,kvj->kvi',R,points-pv)+pv
    pl=component_planes(g)
    return -np.max(local@pl[:,:3].T-pl[:,3],axis=-1)*1000

