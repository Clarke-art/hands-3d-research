from articulation_common import *
EVENTS=[n for n in TL['notes'] if n['hand']=='R']
PREP=o.qanchor('R1');B=np.array([np.radians(o.SP['joint_increment_bounds_deg']['THUMB' if j==0 else 'LONG']) for j in range(5)])
APPROACH=.06;LIFT=.02;RECOVERY=.05

def phases(t):
 # Event-only phases. No pitch-specific timing or amplitude branch.
 activation=np.zeros(5);contactweight=np.zeros(5);pressureweight=np.zeros(5);liftweight=np.zeros(5)
 for n in EVENTS:
  j=n['finger']-1;on=n['note_on'];off=n['note_off'];end=off+.07+RECOVERY
  if on-APPROACH<=t<=end:
   if t<on-APPROACH+LIFT:
    liftweight[j]=c.smooth((t-on+APPROACH)/LIFT)
   elif t<on:
    a=c.smooth((t-(on-APPROACH+LIFT))/(APPROACH-LIFT));contactweight[j]=a;liftweight[j]=1-a
   elif t<=off+.07:contactweight[j]=1;pressureweight[j]=c.keypress(n,t)
   else:contactweight[j]=1-c.smooth((t-off-.07)/RECOVERY)
   activation[j]=max(liftweight[j],contactweight[j])
 # Common-root stance: smooth60ms preparation, stays engaged through adjacent notes;
 # no repeated palm pumping to exaggerate articulation.
 stance=0.
 for n in EVENTS:
  on=n['note_on'];off=n['note_off'];end=off+.07+RECOVERY
  if on-APPROACH<=t<on:w=c.smooth((t-on+APPROACH)/APPROACH)
  elif on<=t<=off+.07:w=1.
  elif off+.07<t<=end:w=1-c.smooth((t-off-.07)/RECOVERY)
  else:w=0.
  stance=max(stance,w)
 return stance,contactweight,pressureweight,liftweight

def sample_right(t,x):
 coef=np.radians(x[:40].reshape(5,2,4));root=x[40:44];idle=np.radians(x[44:59].reshape(5,3))
 stance,a,p,lift=phases(t);rest=PREP.copy();rest[:,:3]+=idle*stance
 raised=rest.copy();raised[:,0]=np.maximum(B[:,0,0],raised[:,0]-np.radians(3))
 # The same Bernstein endpoint interpolation as before, with explicit event phases.
 # 20ms lift,40ms descent;35ms key following;NOTE_OFF70ms return+50ms recovery.
 q=rest.copy()
 for j in range(5):
  on,down=coef[j];ctrl=np.array([on+(down-on)/3,on+2*(down-on)/3,down]);press=o.bernstein(on,ctrl,float(p[j]))
  q[j]=rest[j]+a[j]*(press-rest[j])+lift[j]*(raised[j]-rest[j])
 return q,root[:3]*stance/1000,root[3]*stance

def transform_right(V,delta,pitch):
 wrist=np.array(o.ANCHORS['R1']['root_xyz_m']);R=c.axisrot(np.radians(pitch),[1,0,0]);return (V-wrist)@R.T+wrist+delta
