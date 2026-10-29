import sys,os,json,ast,time
from pathlib import Path
sys.dont_write_bytecode=True
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
O=Path(__file__).resolve().parent;ROOT=O.parent/'hands';sys.path.insert(0,str(ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1/_deps'));sys.path.insert(0,str(ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1'))
import numpy as np
from scipy.spatial.transform import Rotation
import performance_core as c
RAW=np.load(O/'SKIN_MODEL.npz');META=json.loads((O/'SKIN_MODEL_META.json').read_text());REST=RAW['rest_matrices'];INV=np.linalg.inv(REST);REL=np.array([np.linalg.inv(REST[p])@r if p>=0 else r for p,r in zip(RAW['parents'],REST)])
W=RAW['weights'];W=W/np.maximum(W.sum(1,keepdims=True),1e-12);BN={n:i for i,n in enumerate(META['names'])}
H=np.c_[RAW['rest_vertices'],np.ones(len(W))]@RAW['mesh_to_rig'].T;LOCAL=np.einsum('bij,vj->bvi',INV,H)*W.T[:,:,None];SH=np.c_[RAW['shape_delta'],np.zeros(len(W))]@RAW['mesh_to_rig'].T;SHLOCAL=np.einsum('bij,vj->bvi',INV,SH)*W.T[:,:,None]
D={k:RAW[k] for k in ['rest_matrices','parents']};D.update(times=np.array([0.]),rig_world=RAW['base_rig_world'][None],key_angles=np.zeros((1,88)),quat=np.tile([1.,0,0,0],(1,len(REST),1)))
tree=ast.parse((ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning/whole_phrase_model.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if (isinstance(n,ast.FunctionDef) and n.name in ['rot','interp','component_planes']) or isinstance(n,ast.ClassDef) and n.name=='Skin'],type_ignores=[]),'existing_frozen_skin_model','exec'))
S=Skin([0]);BASE=np.array(META['root_base_xyz_m'])
def rr(deg):
 a=np.radians(deg);return c.axisrot(a[2],[0,0,1])@c.axisrot(a[1],[0,1,0])@c.axisrot(a[0],[1,0,0])
def skin(state):
 V=S(np.array(state[6:]).reshape(1,5,4))[0];return (V-BASE)@rr(state[3:6]).T+BASE+np.array(state[:3])/1000
