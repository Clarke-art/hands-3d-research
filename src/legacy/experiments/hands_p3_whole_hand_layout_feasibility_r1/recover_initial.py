"""Re-export the SAME predeclared initial seed; never rerun optimization.

The optimizer terminal state was lost in a post-solve NameError. This script
cannot recover that state and makes no claim about it.
"""
from support import *
sys.path.insert(0,str(OLD/'_deps'));sys.path.insert(0,str(A2))
import coordinated_motion as cm
import numpy as np
P=read(O/'POLICY.json');assert sha(O/'POLICY.json')==read(O/'POLICY_LOCK.json')['policy_sha256']
dump('EXPORT_FAILURE_RECEIPT.json',dict(error='NameError: surface_metrics in post-solve reporting',solver_invoked_once=True,terminal_state_saved=False,terminal_state_recoverable=False,optimizer_restarts=0,solver_result_status='UNKNOWN_LOST_BEFORE_EXPORT',seed_is_original_unchanged_seed_not_a_solution=True,source_script_sha256=sha(O/'solve.py')))
# Identical deterministic initialization prefix only. Excludes least_squares.
code=(O/'solve.py').read_text(encoding='utf8')
original_dump=dump
def dump(n,x):original_dump('INITIALIZATION_'+n,x)
namespace=globals()
exec(compile(code[code.index("I=read(O/"):code.index('r0=residual')],str(O/'solve.py')+':same_initialization_only','exec'),namespace)
dump=original_dump
functions_from(PREV/'evaluate.py',['surface_metrics'],namespace)
root,q,xy=unpack(x0);pads=evaluate(root,q,padids)
rows=[]
for k,t in enumerate(times):
 contacts=[]
 for j,i,l,w in tasks[k]:
  s,h,g,near=surface_metrics(pads[k,j][None],co.keys[events[i]['midi_note']],angles[k,events[i]['key_index']])
  contacts.append(dict(finger=j+1,event=events[i]['note_id'],lift_mm=l*1000,weight=w,horizontal_mm=float(h[0]*1000),gap_mm=float(g[0]*1000),active_or_release=l==0 and w>=4,contact_pass=bool(h[0]*1000<=.03 and abs(g[0]*1000)<=3)))
 rows.append(dict(label=P['phase_labels'][k],time=t,contacts=contacts,root_xyz_mm=(BASE+root[:3]/1000)*1000,root_rotation_deg=root[3:6],q_deg=q[k],min_joint_bound_margin_deg=float(np.minimum(q[k]-cm.B[:,0],cm.B[:,1]-q[k]).min())))
np.savez_compressed(O/'INITIAL_SEED_LAYOUTS.npz',times=times,states=np.c_[np.tile(root,(K,1)),q.reshape(K,20)],contact_xy=xy,world=world(root),qsource=qsource,source_roots=source_roots,key_angles=angles,predicted_pads=pads)
dump('INITIAL_SEED_DIAGNOSTICS.json',dict(status='INITIALIZATION_ONLY_NOT_SOLVED',rows=rows,root_xyz_mm=(BASE+root[:3]/1000)*1000,root_extra_rotation_deg=root[3:6],no_extra_initialization=True,not_optimizer_terminal_state=True))
protect();print('SAME_INITIAL_SEED_EXPORTED; NO_OPTIMIZER_CALL')
for r in rows:print(r['label'],[(c['event'],round(c['horizontal_mm'],3),round(c['gap_mm'],3)) for c in r['contacts'] if c['active_or_release']])
