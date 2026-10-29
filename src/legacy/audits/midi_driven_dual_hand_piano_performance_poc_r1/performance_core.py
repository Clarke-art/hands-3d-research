from pathlib import Path
import sys,json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[1];PRE=P.parent/'piano_keyboard_spatial_anchor_and_contact_validation_r1';PIANO=ROOT.parent/'piano/release/grand-piano-v1.1-rc-candidate'
if 'bpy' not in sys.modules:sys.path.insert(0,str(P/'_deps'))
import numpy as np
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False,default=lambda v:v.tolist() if hasattr(v,'tolist') else v),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def smooth(u):u=np.clip(u,0,1);return u*u*u*(10+u*(-15+6*u))
TL=read(P/'PERFORMANCE_TIMELINE_R1.json');KEYS=read(P/'KEYBOARD_88_KEY_TABLE_R1.json')['keys'];RIG=read(P/'RIG_CANONICAL_PROBE_R1.json');MARKERS=read(P/'FINGERTIP_CONTACT_MARKERS_R1.json')['markers']
DIGITS=['THUMB','INDEX','MIDDLE','RING','LITTLE'];FPS=60;HZ=120;DURATION=TL['presentation_duration_sec']
def axisrot(a,v):
 v=np.array(v);v=v/np.linalg.norm(v);x,y,z=v;K=np.array([[0,-z,y],[z,0,-x],[-y,x,0]]);return np.eye(3)+np.sin(a)*K+(1-np.cos(a))*(K@K)
def rz(a):return axisrot(a,[0,0,1])
def keypress(n,t):
 if t<n['note_on'] or t>=n['note_off']+.07:return 0.
 if t<n['note_off']:return float(smooth((t-n['note_on'])/.035))
 return float(1-smooth((t-n['note_off'])/.07))
def angles_at(t):
 a=np.zeros(88)
 for n in TL['notes']:a[n['key_index']]=max(a[n['key_index']],keypress(n,t)*KEYS[n['key_index']]['press_angle_rad'])
 return a
def keypoint(midi,y,angle=0):
 k=KEYS[midi-21];z=k['key_top_playable_surface'][0]['z'];p=np.array([k['key_center'][0],y,z]);pv=np.array(k['press_pivot']);return axisrot(angle,[1,0,0])@(p-pv)+pv
def digit_setup(s,d):
 names=[f'{d}_{j}_{s}' for j in (['CMC','MCP','IP'] if d=='THUMB' else ['MCP','PIP','DIP'])];b=RIG[s]['bones'];rests=[np.array(b[n]['matrix']) for n in names];rels=[rests[0]]+[np.linalg.inv(rests[j-1])@rests[j] for j in [1,2]];axes=[]
 for M in rests:
  y=M[:3,1];a=np.cross(y,[0,0,-1]);a/=np.linalg.norm(a);axes.append(M[:3,:3].T@a)
 spread=rests[0][:3,:3]<REDACTED_EMAIL>([0,0,1]);pad=np.r_[MARKERS[s][DIGITS.index(d)]['local_pad_point'],1]
 return names,rels,axes,spread,pad
SETUPS={(s,d):digit_setup(s,d) for s in ['R','L'] for d in DIGITS}
def joint_mats(s,d,q):
 names,rels,axes,spread,pad=SETUPS[s,d];out=[]
 for j in range(3):
  r=axisrot(q[j],axes[j]);r=(axisrot(q[3],spread)@r) if j==0 else r;out.append(r)
 return out
def fk(s,d,q):
 names,rels,axes,spread,pad=SETUPS[s,d];M=np.eye(4)
 for rel,r in zip(rels,joint_mats(s,d,q)):
  J=np.eye(4);J[:3,:3]=r;M=M@rel@J
 return (M@pad)[:3],M[:3,:3]
def bounds(d):return (np.radians([0,0,0,-35 if d=='THUMB' else -28]),np.radians([40,55,55,35] if d=='THUMB' else [75,95,65,28]))
def prior(d):return np.radians([10,15,10,0] if d=='THUMB' else [28,30,18,0])
