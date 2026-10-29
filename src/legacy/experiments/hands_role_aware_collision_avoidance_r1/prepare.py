from runtime import *
if not (OUT/'PROTECTED_BEFORE.json').exists(): protect_before()
else:
    assert all(sha(p)==h for p,h in read(OUT/'PROTECTED_BEFORE.json').items())
sys.path.insert(0,str(OLD/'_deps'))
import mido
mf=mido.MidiFile(str(MIDI));matched=[]
for track_id,track in enumerate(mf.tracks):
    ticks=0;on={}
    for msg in track:
        ticks+=msg.time
        if msg.type=='note_on' and msg.velocity>0: on[msg.channel,msg.note]=(ticks,msg.velocity)
        elif msg.type=='note_off' or msg.type=='note_on' and msg.velocity==0:
            start,vel=on.pop((msg.channel,msg.note))
            matched.append((track_id,msg.channel,msg.note,start,ticks,vel))
matched=[r for r in matched if r[3]<max(n['off_tick'] for n in NOTES)]
assert len(matched)==23
assert sorted(matched)==sorted((n['track'],n['channel'],n['midi_note'],n['on_tick'],n['off_tick'],n['velocity']) for n in NOTES)
# The task selects this event pair; generation itself is independent of IDs/pitches.
right=sorted([n for n in NOTES if n['hand']=='R'],key=lambda n:n['note_on'])
old=next(n for n in right if n['note_id']=='R10');new=next(n for n in right if n['note_id']=='R11')
nxt=next(n for n in right if n['finger']==old['finger'] and n['note_on']>old['note_off'])
start=old['note_on']-POL['prepare_sec'];end=new['note_off']+POL['prepare_sec']
assert old['finger']==4 and new['finger']==3 and old['note_off']==new['note_on']
co_module,co=historical_coordinator()
times=sorted(set([start,old['note_on'],new['note_on']-POL['prepare_sec'],old['note_off'],
    old['note_off']+POL['finger_release_follow_sec'],nxt['note_on']-POL['prepare_sec'],
    new['note_off'],nxt['note_off'],end]))
save('EVENT_SCOPE.json',dict(old=old,new=new,next_for_releasing=nxt,start=start,end=end,duration=end-start,
    lead_sec=.35,source_ticks_verified=True,ppq=mf.ticks_per_beat,reference_tasks=[dict(t=t,tasks=co.tasks(t)) for t in times],
    outside_inherited_defects='B01/B03 not repaired; local existing key conflicts must be recorded and cannot be worsened'))
save('ACCESS_AND_SOURCE_POLICY.json',dict(independent_piano_access='FORBIDDEN_AUDIT_HOOK_INSTALLED',
    historical_scripts_executed=['performance_core definitions','A2 coordinator definitions'],
    historical_solvers_called=0,source_sha256=sha(SOURCE),key_table_source=str(OLD/'KEYBOARD_88_KEY_TABLE_R1.json'),
    output_root=str(OUT),candidate_limit=1,numerical_budget_seconds=300))
print('SOURCE_AND_EVENTS_VERIFIED',start,end,end-start,flush=True)
