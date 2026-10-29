import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O))
from motion_model import *
from scipy.spatial.transform import Rotation
A=np.load(O/'MOTION_CANDIDATE.npz');f=curve(A['latent_knots']);times=A['times'];pf=json.loads((O.parent/'hands_c01_whole_hand_motion_feasibility_r1/RIG_PREFLIGHT.json').read_text());RM=np.array(pf['static_root_base_matrix'])[:3,:3];names=[n for d in c.DIGITS for n in c.SETUPS['R',d][0]]
def channels(t):
 st=state(f(t));rootq=Rotation.from_matrix(rr(st[3:6])@RM).as_quat()[[3,0,1,2]]
 bq=[]
 for j,d in enumerate(c.DIGITS):
  for R in c.joint_mats('R',d,np.radians(st[6+4*j:10+4*j])):bq.append(Rotation.from_matrix(R).as_quat()[[3,0,1,2]])
 return BASE+st[:3]/1000,rootq,np.array(bq)
values=[];der=[];h=.00005
for t in times:
 loc,q,b=channels(float(t));lp,qp,bp=channels(float(t+h));lm,qm,bm=channels(float(t-h))
 if qp@q<0:qp=-qp
 if qm@q<0:qm=-qm
 for j in range(len(b)):
  if bp[j]@b[j]<0:bp[j]=-bp[j]
  if bm[j]@b[j]<0:bm[j]=-bm[j]
 values.append((loc,q,b));der.append(((lp-lm)/(2*h),(qp-qm)/(2*h),(bp-bm)/(2*h)))
np.savez_compressed(O/'ACTION_TRACKS.npz',times=times,root_location=np.array([v[0] for v in values]),root_quat=np.array([v[1] for v in values]),bone_quat=np.array([v[2] for v in values]),root_location_derivative=np.array([v[0] for v in der]),root_quat_derivative=np.array([v[1] for v in der]),bone_quat_derivative=np.array([v[2] for v in der]),bone_names=names)
print('C1_ACTION_TRACKS',len(times),'no optimization')
