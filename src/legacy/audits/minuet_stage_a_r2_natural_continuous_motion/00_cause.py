from stage_common import *
import itertools
tl=read(R1/'PERFORMANCE_TIMELINE.json');A=np.load(R1/'motion.npz');plan=read(R1/'TARGET_KEY_AND_ROOT_PLAN.json');diag=read(R1/'ENGINEERING_DIAGNOSTICS.json')
dt=np.diff(A['times']);vel=np.diff(np.degrees(A['R_q']),axis=0)/dt[:,None,None]
idx=np.unravel_index(np.argmax(abs(vel)),vel.shape);i,j,d=idx;t=float(A['times'][i+1])
events=tl['notes'];near=[n for n in events if n['note_on']-.12<=t<=n['note_off']+.15]
root=np.array(plan['transitions'][-1]['from_delta']);last=plan['transitions'][-1]
hold=next(n for n in events if n['note_id']=='R13')
data=dict(old_motion_sha256=sha(R1/'motion.npz'),old_plan_sha256=sha(R1/'TARGET_KEY_AND_ROOT_PLAN.json'),
    peak_joint_speed=dict(time_before=float(A['times'][i]),time_after=t,digit=c.DIGITS[j],joint_component=d,
        speed_deg_sec=float(vel[idx]),q_before_deg=np.degrees(A['R_q'][i,j]),q_after_deg=np.degrees(A['R_q'][i+1,j]),
        nearby_events=near),last_root_transition=last,G5_original_event=hold,
    confirmed_early_root_duration_sec=hold['note_off']-last['start'],
    early_shift_fraction_of_G5_duration=(hold['note_off']-last['start'])/(hold['note_off']-hold['note_on']),
    repeated_key_limits=diag['repeated_key_retrigger_limitations'])
# Frozen FK only: coarse lateral envelope, no pose/action/animation generation.
R=o.root('R')[1];ranges=[];bounds=read(R1/'GENERATION_POLICY.json')['joint_bounds_deg']
for finger in [0,4]:
    B=np.radians(bounds['THUMB' if finger==0 else 'LONG']);points=[]
    for q in itertools.product(*[np.linspace(B[0,k],B[1,k],5) for k in range(4)]):
        points.append(c.fk('R',c.DIGITS[finger],np.array(q))[0]@R.T)
    points=np.array(points);ranges.append(dict(finger=finger+1,x_min_m=float(points[:,0].min()),x_max_m=float(points[:,0].max())))
data['coarse_static_lateral_envelopes']=ranges
data['coarse_possible_thumb_little_span_mm']=(ranges[1]['x_max_m']-ranges[0]['x_min_m'])*1000
data['actual_octave_key_center_span_mm']=(c.KEYS[79-21]['key_center'][0]-c.KEYS[67-21]['key_center'][0])*1000
dump('R1_CAUSE_EVIDENCE.json',data)
protected=read(R1/'PROTECTED_INPUTS_BEFORE.json');protected={p:sha(p) for p in protected if Path(p).is_file()}
for f in R1.rglob('*'):
    if f.is_file():protected[str(f)]=sha(f)
dump('PROTECTED_INPUTS_BEFORE.json',protected)
dump('HUMAN_AUTHORITY_BIND.json',dict(client_date='2026-10-10',primary_visible_defect='UNNATURAL_MOTION_TRANSITIONS',
    source='Direct Human R2 request',R1_Human_feedback=['stiff finger handoffs','palm/finger decoupling','abrupt register movement'],
    frozen_assets_unchanged_required=True,ONE_NEW_DYNAMIC_CANDIDATE_ONLY=True,
    Musette_Human_acceptance_carried_forward=True))
print('CAUSE_SAVED',t,c.DIGITS[j],float(vel[idx]),data['coarse_possible_thumb_little_span_mm'],flush=True)
