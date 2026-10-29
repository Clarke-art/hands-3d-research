from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
OLD=P.parent/'piano_hand_static_to_dynamic_transition_r1'
LAST=P.parent/'left_octave_root_finger_coordinated_clearance_r1'
sys.path.insert(0,str(OLD));import common as o
import numpy as np
c=o.c

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False,default=lambda v:v.tolist() if hasattr(v,'tolist') else v),encoding='utf8')
TL=read(P/'PERFORMANCE_TIMELINE.json') if (P/'PERFORMANCE_TIMELINE.json').exists() else c.TL
EVENTS={s:[n for n in TL['notes'] if n['hand']==s] for s in ['L','R']}
START=.4;END=3.1;FPS=60

def recovery(n):
 later=[x['note_on']-.12 for x in EVENTS[n['hand']] if x['finger']==n['finger'] and x['note_on']>n['note_on']]
 return min([n['note_off']+.22]+later)
def left(t):
 # Reuse all 29 fitted parameters, unchanged. Only schedule the complete MIDI events.
 ctrl={k:np.array(v) for k,v in read(OLD/'CONTACT_AWARE_MOTION_PLAN_R1.json')['controls_radians'].items()}
 x=np.array(read(LAST/'ROOT_FINGER_COORDINATION_R1.json')['x'])
 ctrl['L1']+=np.radians(x[4:8]);ctrl['L2']+=np.radians(x[8:12])
 q=o.qanchor('L1').copy();q[4]=o.qanchor('L2')[4];ka=c.angles_at(t)
 for n in EVENTS['L']:
  j=n['finger']-1;pose='L1' if j==4 else 'L2';prep='L2' if j==4 else 'L1';a=o.qanchor(pose)[j];b=o.qanchor(prep)[j];on,off=n['note_on'],n['note_off'];end=recovery(n);p=c.keypress(n,t)
  if on-.12<=t<=end:
   if t<on:v=b+(a-b)*c.smooth((t-on+.12)/.12)
   elif t<off+.07:v=o.bernstein(a,ctrl[pose],p)
   else:v=a+(b-a)*c.smooth((t-off-.07)/(end-off-.07))
   q[j]=v
 p=ka[17]/c.KEYS[17]['press_angle_rad'];p3=ka[29]/c.KEYS[29]['press_angle_rad'];b=(1-p3)*x[12:16]+p3*x[16:20]
 q[0]+=p*b*(o.qanchor('L1')[0]-q[0]);q[1:4,:3]+=np.radians(x[20:29].reshape(3,3))*p
 return q,ka,x[:3]*p/1000,x[3]*p

def right(t,coeff):
 q=o.qanchor('R1').copy()
 for n in EVENTS['R']:
  j=n['finger']-1;on,off=n['note_on'],n['note_off'];end=recovery(n);a,down=coeff[j];b=o.qanchor('R1')[j]
  if on-.12<=t<=end:
   if t<on:v=b+(a-b)*c.smooth((t-on+.12)/.12)
   elif t<off+.07:
    ctrl=np.array([a+(down-a)/3,a+2*(down-a)/3,down]);v=o.bernstein(a,ctrl,c.keypress(n,t))
   else:v=a+(b-a)*c.smooth((t-off-.07)/(end-off-.07))
   q[j]=v
 return q
