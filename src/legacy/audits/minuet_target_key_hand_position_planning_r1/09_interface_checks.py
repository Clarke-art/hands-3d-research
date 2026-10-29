from stage_common import *
from target_key_planner import TargetKeyPlanner
tl=read(P/'PERFORMANCE_TIMELINE.json');planner=TargetKeyPlanner(c.KEYS,o.ANCHORS,'R')
plan=read(P/'TARGET_KEY_AND_ROOT_PLAN.json');checks=[]
for n in tl['notes']:
    target=plan['key_targets'][n['note_id']];k=c.KEYS[n['key_index']]
    s=k['key_top_playable_surface'][target['surface_index']];point=target['unpressed_pad_xyz']
    assert target['midi_note']==n['midi_note'] and target['key_index']==n['key_index']
    assert s['xmin']<=point[0]<=s['xmax'] and s['ymin']<=point[1]<=s['ymax']
    assert abs(point[2]-s['z']-.0005)<1e-12
    assert target['color']==k['color']
    checks.append(n['note_id'])
rejects={}
for label,events in [('chord',[dict(tl['notes'][0]),dict(tl['notes'][1],note_on=tl['notes'][0]['note_on'])]),
    ('outside_keyboard',[dict(tl['notes'][0],midi_note=109)]),
    ('invalid_finger',[dict(tl['notes'][0],finger=0)]),
    ('wrong_hand',[dict(tl['notes'][0],hand='L')])]:
    try:planner.plan(events)
    except ValueError as e:rejects[label]=str(e)
    else:raise AssertionError(label)
dump('PLANNING_INTERFACE_VERIFICATION.json',dict(mode='READ_ONLY_NO_NEW_TRAJECTORY',
    all_16_key_targets_inside_real_inset_surface=True,verified_notes=checks,
    invalid_requests_rejected=rejects,module_sha256=sha(P/'target_key_planner.py'),
    new_motion_candidates=0,scope='Interface and geometry checks only; not dynamic qualification.'))
print('INTERFACE_GEOMETRY_CHECKED',len(checks),rejects)
