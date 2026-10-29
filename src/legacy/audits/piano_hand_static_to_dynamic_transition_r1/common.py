from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
STATIC=P.parent/'piano_hand_static_posture_clearance_refinement_r2'
FORMAL=P.parent/'piano_hand_four_pose_static_feasibility_r1'
OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1'
if 'bpy' not in sys.modules: sys.path.insert(0,str(OLD/'_deps'))
sys.path.insert(0,str(OLD))
import performance_core as c
import numpy as np
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(n,x): (P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False,default=lambda x:x.tolist() if hasattr(x,'tolist') else x),encoding='utf-8')
ANCHORS=read(STATIC/'SOLVED_STATIC_POSES_R2.json')['poses']
SP=read(STATIC/'STATIC_REFINEMENT_POLICY_R2.json')
EVENTS={'L':[n for n in c.TL['notes'] if n['note_id'] in ['n01','n02','n04']], 'R':[n for n in c.TL['notes'] if n['note_id']=='n05']}
WINDOWS={'L':[.4,1.8],'R':[1.025,1.8]}
def qanchor(p): return np.radians(ANCHORS[p]['joint_increments_deg'])
def root(s): return np.array(ANCHORS['L1' if s=='L' else 'R1']['root_xyz_m']),np.array(ANCHORS['L1' if s=='L' else 'R1']['root_rotation_matrix'])
def recovery_end(n):
 later=[x['note_on']-.12 for x in EVENTS[n['hand']] if x['finger']==n['finger'] and x['note_on']>n['note_on']]
 return min([n['note_off']+.22]+later)
def phase(n,t):
 on,off=n['note_on'],n['note_off']
 if t<on-.12:return 'PREPARATION'
 if t<on:return 'APPROACH'
 if abs(t-on)<1e-8:return 'CONTACT'
 if t<on+.035:return 'KEY_PRESS'
 if t<off:return 'HOLD'
 if t<off+.07:return 'RELEASE'
 if t<recovery_end(n):return 'RECOVERY'
 return 'PREPARATION'
def bernstein(q0,ctrl,p): return (1-p)**3*q0+3*(1-p)**2*p*ctrl[0]+3*(1-p)*p*p*ctrl[1]+p**3*ctrl[2]
def sample(s,t,controls):
 q=qanchor('L1' if s=='L' else 'R1').copy()
 if s=='L':q[4]=qanchor('L2')[4]
 angles=np.zeros(88)
 for n in EVENTS[s]:
  j=n['finger']-1;pose='L1' if s=='L' and j==4 else 'L2' if s=='L' else 'R2';prepare='L2' if pose=='L1' else 'L1' if pose=='L2' else 'R1'
  a=qanchor(pose)[j];b=qanchor(prepare)[j];on,off=n['note_on'],n['note_off'];p=c.keypress(n,t)
  end=recovery_end(n)
  if on-.12<=t<=end:
   if t<on:v=b+(a-b)*c.smooth((t-(on-.12))/.12)
   elif t<off+.07:v=bernstein(a,controls[pose],p)
   else:v=a+(b-a)*c.smooth((t-(off+.07))/(end-(off+.07)))
   q[j]=v
  angles[n['key_index']]=max(angles[n['key_index']],p*c.KEYS[n['key_index']]['press_angle_rad'])
 return q,angles
def worldpads(s,q):
 r,R=root(s);return np.array([c.fk(s,d,q[j])[0] for j,d in enumerate(c.DIGITS)])@R.T+r
def keytransform(midi,points,angle,inverse=False):
 pv=np.array(c.KEYS[midi-21]['press_pivot']);R=c.axisrot(angle,[1,0,0]);return (np.array(points)-pv)@(R if inverse else R.T)+pv
def measure(pt,midi,angle):
 pt0=keytransform(midi,pt,angle,True);sur=c.KEYS[midi-21]['key_top_playable_surface'];ds=[np.linalg.norm(pt0[:2]-np.clip(pt0[:2],[x['xmin'],x['ymin']],[x['xmax'],x['ymax']])) for x in sur];i=int(np.argmin(ds));gap=float(pt0[2]-sur[i]['z'])*1000;h=float(ds[i])*1000
 return {'gap_mm':gap,'horizontal_mm':h,'inside':h<1e-5,'pass':bool(h<1e-5 and abs(gap)<=3),'key_local_xyz_mm':pt0*1000}
def models(s):
 d=read(FORMAL/'FORMAL_INPUT_EXTRACTION_R1.json')[s];V=np.array(d['rest_vertices_canonical']);W=np.array(d['weights']);names=d['bone_names'];bones=c.RIG[s]['bones'];rest={n:np.array(bones[n]['matrix']) for n in names};inv={n:np.linalg.inv(rest[n]) for n in names}
 return dict(V=V,W=W,names=names,bones=bones,rest=rest,inv=inv,weighted=np.c_[V,np.ones(len(V))][:,None,:]*W[:,:,None])
def skin(s,q,m):
 basis={}
 for j,d in enumerate(c.DIGITS):
  for n,r in zip(c.SETUPS[s,d][0],c.joint_mats(s,d,q[j])):B=np.eye(4);B[:3,:3]=r;basis[n]=B
 pose={}
 def get(n):
  if n not in pose:
   p=m['bones'][n]['parent'];pose[n]=(get(p)@m['inv'][p]@m['rest'][n] if p else m['rest'][n])@basis.get(n,np.eye(4))
  return pose[n]
 M=np.array([get(n)@m['inv'][n] for n in m['names']]);V=np.einsum('bij,nbj->nbi',M,m['weighted']).sum(1)[:,:3];r,R=root(s);return V@R.T+r
