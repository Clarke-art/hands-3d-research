import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from support import *
import support as s
rn=[n for n in NOTES if n['hand']=='R' and n['finger']==2]
ends=[0.,.18,1.35,2.1,2.28,3.35]+[x for n in rn for x in [n['note_on']-.18-.04,n['note_on']-.18,n['note_on'],n['note_off'],n['note_off']+.04]]
ts=np.unique([max(0.,t+e) for t in ends for e in [-.002,-.001,-.0001,0,.0001,.001,.002]])
base={};rows=[]
for identity,path in [('base',SOURCE),('candidate',OUT/'IDLE_INDEX_CLEARANCE_B_NOT_APPROVED.blend')]:
 sc,rig,mesh,left,lrig=s.open_scene(path)
 for t in ts:
  c.settime(sc,float(t));V,T,F=s.coords_tri(mesh);r=dict(time=t,q=s.degrees('INDEX'),pad=V[1750],allV=V)
  if identity=='base':base[t]=r
  else:rows.append(dict(time=t,deltaq_deg=r['q']-base[t]['q'],pad_shift_mm=float(np.linalg.norm(r['pad']-base[t]['pad'])*1000),max_skin_shift_mm=float(np.max(np.linalg.norm(V-base[t]['allV'],axis=1))*1000)))
summary=[]
for t in ends:
 rr=[r for r in rows if abs(r['time']-t)<.00201];r0=min(rr,key=lambda r:abs(r['time']-t));before=min(rr,key=lambda r:abs(r['time']-(t-.0001)));after=min(rr,key=lambda r:abs(r['time']-(t+.0001)))
 summary.append(dict(boundary=t,at_boundary=r0,deltaq_change_across_0_2ms_deg=float(np.max(abs(np.array(after['deltaq_deg'])-before['deltaq_deg']))),skin_shift_change_across_0_2ms_mm=abs(after['max_skin_shift_mm']-before['max_skin_shift_mm'])))
save('TRANSITION_SUBFRAME_CHECK.json',dict(sampling_offsets_sec=[-.002,-.001,-.0001,0,.0001,.001,.002],rows=rows,boundaries=summary,warning='Finite samples do not prove continuous-time or acceleration safety; max()/domain clipping may introduce derivative kinks. Original piecewise-linear quaternion interpolation retained.'))
protection('TRANSITION_INPUT_RECEIPT.json');print('TRANSITIONS_DONE',flush=True)
