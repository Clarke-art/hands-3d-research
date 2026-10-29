from io_core import *
import numpy as np
M=read(MODEL/'SOURCE_MODEL_MANIFEST.json')
D=archive(MODEL/'SOURCE_MODEL.npz')
SH=archive(MODEL/'SHAPE_DELTA.npz')['delta']
CAN=read(OLD/'RIG_CANONICAL_PROBE_R1.json')['R']['bones']
MARK=read(OLD/'FINGERTIP_CONTACT_MARKERS_R1.json')['markers']['R']
KEYS=read(OLD/'KEYBOARD_88_KEY_TABLE_R1.json')['keys']
BN={n:i for i,n in enumerate(M['bones'])};REST=D['rest_matrices'].astype(float)
REL=np.array([np.linalg.inv(REST[p])@r if p>=0 else r for p,r in zip(D['parents'],REST)])
W=D['weights'];W=W/np.maximum(W.sum(1,keepdims=True),1e-12)
H=np.c_[D['rest_vertices'],np.ones(len(W))]@D['mesh_to_rig'].T
LOCAL=np.einsum('bij,vj->bvi',np.linalg.inv(REST),H)*W.T[:,:,None]
SHH=np.c_[SH,np.zeros(len(W))]@D['mesh_to_rig'].T
SHLOCAL=np.einsum('bij,vj->bvi',np.linalg.inv(REST),SHH)*W.T[:,:,None]
DIGITS=['THUMB','INDEX','MIDDLE','RING','LITTLE'];AXES=[];NAMES=[];SPREAD=[]
for digit in DIGITS:
    names=[f'{digit}_{j}_R' for j in (['CMC','MCP','IP'] if digit=='THUMB' else ['MCP','PIP','DIP'])]
    rests=[np.array(CAN[n]['matrix']) for n in names];axes=[]
    for mat in rests:
        a=np.cross(mat[:3,1],[0,0,-1]);a/=np.linalg.norm(a);axes.append(mat[:3,:3].T@a)
    AXES.append(axes);NAMES.append(names);SPREAD.append(rests[0][:3,:3]<REDACTED_EMAIL>([0,0,1]))
extract(PREV/'evaluate.py',['rot','forward','skin','surface_metrics'],globals())
extract(MODEL/'whole_phrase_model.py',['component_planes'],globals())
ROIS=read(ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1/DIGIT_SKIN_ROI.json')
COMPONENTS=[(k,g,component_planes(g)) for k in KEYS for g in k['geometry']]
PADIDS=[r['mesh_vertex'] for r in MARK]
# Only frozen FK/LBS helpers are extracted; no historical optimizer body executes.
extract(R2/'model.py',['basis','native','point_on_key','inset'],globals())
I=read(R2/'INPUT_BINDINGS.json')
EVENTS=I['right_events']
START,END=I['source_window_sec']
assert np.allclose([START,END],[1.2414275,2.134284],rtol=0,atol=1e-12)
START,END=1.2414275,2.134284
QBOUNDS=np.asarray(read(SRC/'POLICY.json')['joint_bounds_deg'])

