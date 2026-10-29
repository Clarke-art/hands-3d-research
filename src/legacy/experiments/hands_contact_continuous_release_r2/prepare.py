from runtime import *
import mido
assert not (OUT/'PROTECTED_BEFORE.json').exists()
save('PROTECTED_BEFORE.json',{str(p):sha(p) for p in refs()})
mf=mido.MidiFile(str(MIDI));tick=0;seconds=0;tempo=500000;events=[]
for msg in mido.merge_tracks(mf.tracks):
    tick+=msg.time;seconds+=mido.tick2second(msg.time,mf.ticks_per_beat,tempo)
    if tick>max(n['off_tick'] for n in NOTES):break
    if msg.type=='set_tempo':tempo=msg.tempo
    if msg.type in ['note_on','note_off']:events.append((msg.channel,msg.note,tick,'ON' if msg.type=='note_on' and msg.velocity>0 else 'OFF',seconds))
errors=[]
for n in NOTES:
    for kind,field in [('ON','on'),('OFF','off')]:
        e=next(e for e in events if e[:4]==(n['channel'],n['midi_note'],n[field+'_tick'],kind));errors.append(e[4]-n['source_'+field+'_sec'])
assert max(abs(x) for x in errors)<1e-10
old,new,nxt=[SCOPE[k] for k in ['old','new','next_for_releasing']]
assert START==old['note_on']-POL['prepare_sec'] and END==new['note_off']+POL['prepare_sec']
save('INPUT_CHECK.json',dict(pass_=True,source_sha256=sha(SOURCE),midi_sha256=sha(MIDI),max_event_time_error_seconds=max(abs(x) for x in errors),note_count=len(NOTES),scope=SCOPE,
    independent_piano_access='EXCLUDED_PYTHON_AUDIT_GUARD',source_reference_samples=len(BASE['times'])))
# Verify release blend itself before constructing any geometric or IK target.
off=old['note_off'];follow=POL['finger_release_follow_sec'];exit=nxt['note_on']-.075
boundary=[off,off+follow,exit];rows=[]
for t in boundary:
    eps=1e-7;v=[float(release_gate(t+d,off,follow,exit)) for d in [-eps,0,eps]]
    rows.append(dict(time=t,value=v[1],value_left=v[0],value_right=v[2],left_secant=(v[1]-v[0])/eps,right_secant=(v[2]-v[1])/eps))
assert release_gate(off,off,follow,exit)==0
assert all(abs(r['value_right']-r['value_left'])<1e-8 and abs(r['left_secant']-r['right_secant'])<1e-3 for r in rows)
save('PHASE_FUNCTION_GATE.json',dict(pass_=True,one_mechanism='quintic add-on to original A2 release-follow target; no reset at role PREPARING label',
    boundaries=rows,off_extra_offset=0.,off_extra_velocity=0.,old_follow_seconds=follow,next_exit=exit,
    off_source='Exact original contact left limit; release remains NOTE_OFF not continued MIDI hold',
    formula='P_source(t) + smooth((t-OFF)/follow)*(1-smooth((t-OFF-follow)/(prepare_exit-OFF-follow)))*witness_displacement'))
print('MIDI_AND_C1_PHASE_GATE_PASS',START,END,flush=True)
