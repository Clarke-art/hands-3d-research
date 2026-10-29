from runtime import *
import mido
mf=mido.MidiFile(str(MIDI));tempo=500000;ticks=0;seconds=0;events=[];tempos=[]
limit=max(n['off_tick'] for n in NOTES)
for msg in mido.merge_tracks(mf.tracks):
    ticks+=msg.time;seconds+=mido.tick2second(msg.time,mf.ticks_per_beat,tempo)
    if ticks>limit:break
    if msg.type=='set_tempo':tempo=msg.tempo;tempos.append(dict(tick=ticks,tempo=tempo))
    if msg.type in ['note_on','note_off']:
        kind='ON' if msg.type=='note_on' and msg.velocity>0 else 'OFF'
        events.append(dict(kind=kind,channel=msg.channel,midi=msg.note,tick=ticks,seconds=seconds))
rows=[]
for n in NOTES:
    values=[]
    for kind,field in [('ON','on'),('OFF','off')]:
        matches=[e for e in events if e['kind']==kind and e['channel']==n['channel'] and e['midi']==n['midi_note'] and e['tick']==n[field+'_tick']]
        assert len(matches)==1,(n['note_id'],kind,matches)
        e=matches[0];err=e['seconds']-n['source_'+field+'_sec'];assert abs(err)<1e-10
        values.append(dict(kind=kind,source_seconds=e['seconds'],presentation_seconds=e['seconds']+.35,error_seconds=err))
    rows.append(dict(event=n['note_id'],values=values))
save('MIDI_TIME_VERIFICATION.json',dict(pass_=True,ppq=mf.ticks_per_beat,tempos=tempos,rows=rows,note_count=len(rows),
    exact_event_seconds_from_merged_midi=True,source_sha256=sha(MIDI)))
actual=read(OUT/'STATIC_ACTUAL_VALIDATION.json');pre=read(OUT/'STATIC_PREFLIGHT_VERIFIED_RESULT.json')
a=dict(np.load(OUT/'STATIC_PREFLIGHT_VERIFIED.npz'))
rate=np.abs(np.diff(a['qdeg'][:,[2,3]],axis=0))/np.diff(a['times'])[:,None,None]
policy=read(OUT/'PLANNER_POLICY_COORDINATE_VERIFIED.json')
released=next(r for row in policy['targets'] for r in row if r['role']=='RELEASING')
budget=dict(limit_seconds=300,valid_preflight_core_seconds=pre['numerical_seconds'],
    invalid_coordinate_batch_core_seconds=read(OUT/'STATIC_PREFLIGHT_RESULT.json')['numerical_seconds'],
    core_total_seconds=pre['numerical_seconds']+read(OUT/'STATIC_PREFLIGHT_RESULT.json')['numerical_seconds'],
    conservative_full_compute_charge_seconds=100,
    charge_scope='Includes input/adapter failures, initialization, one invalid development batch, one valid static batch, Blender baseline/anchor/replay commands, and closing checks; excludes human source reading/report writing. Core timings exact, process overhead charged conservatively, no animation solve/render.')
save('COMPUTE_BUDGET.json',budget)
save('CAUSE_AND_COVERAGE.json',dict(static_rows=[dict(t=r['t'],source_pairs=r['source_middle_ring']['triangle_pairs'],
    new_pairs=r['new_middle_ring']['triangle_pairs'],contacts=r['contacts'],regression_count=len(r['key_regressions']),
    max_regression_mm=max([x['increase_mm'] for x in r['key_regressions']]+[0])) for r in actual['rows']],
    required_direct_connection_average_rate_max_deg_sec=float(rate.max()),
    rate_scope='Necessary mean angular rate IF these failed static endpoints were connected; no trajectory or measured animation velocity.',
    release_portal_at_off_lift_mm=(released['target_world_m'][2]-released['source_world_m'][2])*1000,
    release_target_issue='Full clearance portal assigned at RELEASING entry without a continuous ramp; OFF still requires old-contact left limit. This is an implementation/design defect, not proof of insufficient human time or fixed-root impossibility.',
    capsules='Single full-segment radius around 10-12mm is conservative: two anchors have capsule overlap but actual distal BVH has no intersection. Capsule failure alone is not actual skin failure.',
    candidate_count=0,continuous_motion_check='NOT_RUN_PREGENERATION_FAILURE',
    inherited_B01_B03='Not repaired; original evidence remains',
    naturalness='NO_DYNAMIC_CANDIDATE_HUMAN_NOT_ASSESSED'))
protect_after()
outputs=[p for p in OUT.iterdir() if p.is_file() and p.name!='OUTPUT_MANIFEST.json']
save('OUTPUT_MANIFEST.json',dict(files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in outputs],
    candidate_count=0,blend_count=len(list(OUT.glob('*.blend'))),video_count=len(list(OUT.glob('*.mp4'))),
    all_outputs_inside_experiment=True,stop='STOP — HUMAN REVIEW'))
print('CLOSED',budget['core_total_seconds'],'core sec; 100 sec conservative charge; source protection pass',flush=True)
