from stage_common import *
from target_key_planner import TargetKeyPlanner
A=np.load(P/'motion.npz');E=np.load(P/'evaluated.npz');tl=read(P/'PERFORMANCE_TIMELINE.json')
T=E['times'];notes=tl['notes'];rows=[]
for n in notes:
    j=n['finger']-1;indices=np.flatnonzero((T>=n['note_on']-1e-9)&(T<n['note_off']-1e-9))
    rr=[o.measure(E['R_pads'][i,j],n['midi_note'],E['key_angles'][i,n['key_index']]) for i in indices]
    sr=[o.measure(E['R_skin_pads'][i,j],n['midi_note'],E['key_angles'][i,n['key_index']]) for i in indices]
    samples=[]
    for t in [n['note_on'],n['note_on']+.035,(n['note_on']+n['note_off'])/2,n['note_off']-1/120]:
        i=int(np.argmin(abs(T-t)));samples.append(dict(time=float(T[i]),
            fixed=o.measure(E['R_pads'][i,j],n['midi_note'],E['key_angles'][i,n['key_index']]),
            skin=o.measure(E['R_skin_pads'][i,j],n['midi_note'],E['key_angles'][i,n['key_index']])))
    rows.append(dict(note_id=n['note_id'],note=n['note_name'],midi=n['midi_note'],finger=n['finger'],
        fixed_gap_min_mm=min(r['gap_mm'] for r in rr),fixed_gap_max_mm=max(r['gap_mm'] for r in rr),
        horizontal_max_mm=max(r['horizontal_mm'] for r in rr),
        skin_gap_min_mm=min(r['gap_mm'] for r in sr),skin_gap_max_mm=max(r['gap_mm'] for r in sr),
        contact_failure_fraction=sum(not r['pass'] for r in rr)/len(rr),samples=samples))
dt=np.diff(T);rv=np.diff(A['R_delta'],axis=0)/dt[:,None]
jv=np.diff(np.degrees(A['R_q']),axis=0)/dt[:,None,None]
limits=np.array([o.SP['joint_increment_bounds_deg']['THUMB' if j==0 else 'LONG'] for j in range(5)])
# Finite engineering screen: fixed skin contact vertex plus three nearby pad points
# per digit and 12 palm representatives. No iterative forensic or parameter repair.
model=o.models('R');indices=[]
for j in range(5):
    idx=c.MARKERS['R'][j]['mesh_vertex'];near=np.argsort(np.linalg.norm(model['V']-model['V'][idx],axis=1))
    indices.extend([int(near[z]) for z in [0,6,12,18]])
palm=np.flatnonzero(model['V'][:,1]<.10);indices.extend(palm[np.linspace(0,len(palm)-1,12).astype(int)].tolist())
indices=sorted(set(indices));collision=[]
for n in notes:
    for t in [n['note_on']+.035,n['note_off']-1/120]:
        i=int(np.argmin(abs(T-t)));V=E['R_verts'][i,indices];worst=0;key=None
        for k in c.KEYS:
            if abs(k['key_center'][0]-float(np.mean(V[:,0])))>.20:continue
            vv=o.keytransform(k['midi_note'],V,E['key_angles'][i,k['key_index']],True)
            for g in k['geometry']:
                lo=np.array(g['vertices']).min(0);hi=np.array(g['vertices']).max(0)
                inside=np.all((vv>lo)&(vv<hi),axis=1)
                if np.any(inside):
                    depth=float(np.max(np.min(np.minimum(vv[inside]-lo,hi-vv[inside]),axis=1))*1000)
                    if depth>worst:worst=depth;key=k['midi_note']
        collision.append(dict(note_id=n['note_id'],time=float(T[i]),max_sampled_key_penetration_mm=worst,key_midi=key))
repeated=[]
for a,b in zip(notes,notes[1:]):
    if a['midi_note']==b['midi_note'] and abs(a['note_off']-b['note_on'])<1e-8:
        idx=np.flatnonzero((T>=a['note_off']-1e-9)&(T<=b['note_on']+.04))
        repeated.append(dict(previous=a['note_id'],next=b['note_id'],note=b['note_name'],
            key_pressure_min_after_retrigger=float(np.min(E['key_angles'][idx,b['key_index']])/c.KEYS[b['key_index']]['press_angle_rad']),
            issue='Inherited max-of-release/attack key envelope does not rebound between abutting repeated notes; audio does retrigger. Preserved and explicitly FAIL, no timing rewrite.'))
dump('ENGINEERING_DIAGNOSTICS.json',dict(notes=rows,
    bounded_relative_joint_domain=True,joint_bound_excess_deg=float(max(np.max(limits[:,0]-np.degrees(A['R_q'])),np.max(np.degrees(A['R_q'])-limits[:,1]),0)),
    root_max_speed_mm_sec=float(np.max(np.linalg.norm(rv,axis=1))*1000),
    root_max_sample_step_mm=float(np.max(np.linalg.norm(np.diff(A['R_delta'],axis=0),axis=1))*1000),
    joint_max_speed_deg_sec=float(np.max(abs(jv))),joint_max_sample_step_deg=float(np.max(abs(np.diff(np.degrees(A['R_q']),axis=0)))),
    finite_collision_probe_count=len(indices),collision=collision,
    contact_failed_notes=[r['note_id'] for r in rows if r['horizontal_max_mm']>2 or max(abs(r['fixed_gap_min_mm']),abs(r['fixed_gap_max_mm']))>3],
    repeated_key_retrigger_limitations=repeated,all_notes_preserved=True,
    status='FAIL_BLOCKED_BY_VISIBLE_CONTACT_AND_RETRIGGER_LIMITS',
    scope='Limited readback diagnostics, not exhaustive collision/physiology certification.'))
print('CONTACT',[(r['note'],r['finger'],round(r['fixed_gap_max_mm'],1),round(r['horizontal_max_mm'],1)) for r in rows])
print('REPEAT_LIMITS',len(repeated),'ROOT_SPEED',np.max(np.linalg.norm(rv,axis=1))*1000,'JOINT_SPEED',np.max(abs(jv)))
