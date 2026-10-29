import sys,os,json,time
from pathlib import Path
sys.dont_write_bytecode=True
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
O=Path(__file__).resolve().parent;ROOT=O.parent/'hands';sys.path.insert(0,str(ROOT/'audits/minuet_stage_a_r2_natural_continuous_motion'))
from coordinated_motion import *
I=json.loads((O/'INPUT_BINDINGS.json').read_text());KA=np.load(O/'KEY_ACTION_SAMPLES.npz');EVENTS=I['notes'];P=O
pol=DEFAULT_POLICY.copy();pol.update(max_trajectory_nfev=40,prepare_sec=.22,contact_weight=8.,clearance_weight=3.,candidate_limit=1,no_fixed_root=True,key_actions_preserved=True,sample_step=.09,root_z_abs_max_mm=65.,root_z_abs_min_mm=30.)
class PreservedKeyCoordinator(EventCoordinator):
 def key_angles(self,t):return np.array([np.interp(t,KA['times'],KA['key_angles'][:,j]) for j in range(88)])
 def tasks(self,t):
  out=super().tasks(t)
  # Same-finger repeated note preparation follows the unchanged key's reset window.
  for index,(j,i,l,w) in enumerate(out):
   n=self.events[i]
   if n['note_id'] in self.repeats and n['note_off']-.045<=t<n['note_off']:
    u=(t-(n['note_off']-.045))/.045;out[index]=(j,i,.002*float(np.sin(np.pi*u)**2),w)
  return out
co=PreservedKeyCoordinator(EVENTS,pol)
co.state_low[2]=max(co.state_low[2],30.-BASE[2]*1000);co.state_high[2]=min(co.state_high[2],65.-BASE[2]*1000)
# Use actual keyboard geometry and canonical FK, never PianoPlayer's estimated shift.
START=I['clip_start_sec'];END=I['clip_end_sec'];events=co.events

def dump(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf8')
