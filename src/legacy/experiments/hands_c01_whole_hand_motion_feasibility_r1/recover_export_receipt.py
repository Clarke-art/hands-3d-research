import sys,json,hashlib,numpy as np
from pathlib import Path
O=Path(__file__).resolve().parent;A=np.load(O/'motion.npz')
assert all(np.isfinite(A[k]).all() for k in A.files)
meta=dict(candidate_count=1,restarts=0,planned_max_nfev=40,actual_nfev=None,solver_success=None,solver_message='Metadata serialization failed after sole solved trajectory had already been saved; convergence flag not retained, no rerun',observed_residual_call_lower_bound=3504,observed_last_weighted_contact_rms=.546,source_notes=9,samples=len(A['times']),motion_sha256=hashlib.sha256((O/'motion.npz').read_bytes()).hexdigest(),executed_script_sha256=hashlib.sha256((O/'solve_continuous_executed.py').read_bytes()).hexdigest(),arrays_finite=True,root_and_all_fingers_joint_unknowns=True,temporal_velocity_acceleration_constraints=True,post_export_error='Migrated metadata hash attempted to read coordinated_motion.py from new directory instead of source module',trajectory_recomputed=False)
(O/'MOTION_GENERATION.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf8')
print('SAVED_TRAJECTORY_FINITE',len(A['times']),A['times'][0],A['times'][-1],meta['motion_sha256'])
