from bootstrap import *
import model as n,mido
from scipy.optimize import least_squares
from scipy.interpolate import PchipInterpolator
from depth_math import selftest
import traceback
I=read(SRC/'INPUT_BINDINGS.json');P=read(SRC/'POLICY.json');man=I['scene'];valid_path(man['path'])
assert [e['note_id'] for e in I['source']]==['R04','R05'] and [e['note_id'] for e in I['target']]==['R12','R13']
assert [e['finger'] for e in I['source']]==[4,5] and [e['finger'] for e in I['target']]==[4,5]
assert read(CLOSE/'FINAL_GEOMETRY_RESULT.json')['RESULT']=='STATIC_GEOMETRY_CLOSED'
assert sha(man['path'])==man['sha256']
midi=ROOT/'audits/minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid';valid_path(midi)
mid=mido.MidiFile(str(midi));tick=0;sec=0.;tempo=500000;active={};music=[]
for m in mido.merge_tracks(mid.tracks):
    sec+=mido.tick2second(m.time,mid.ticks_per_beat,tempo);tick+=m.time
    if m.type=='set_tempo':tempo=m.tempo
    if m.type=='note_on' and m.velocity>0:active[m.channel,m.note]=dict(channel=m.channel,midi_note=m.note,on_tick=tick,on_sec=sec,velocity=m.velocity)
    elif m.type=='note_off' or (m.type=='note_on' and m.velocity==0):
        e=active.pop((m.channel,m.note));e.update(off_tick=tick,off_sec=sec);music.append(e)
for e in I['source_context']+I['target_context']:
    hit=[m for m in music if all(m[k]==e[k] for k in ['channel','midi_note','on_tick','off_tick','velocity'])];assert len(hit)==1
    assert max(abs(hit[0]['on_sec']+.35-e['note_on']),abs(hit[0]['off_sec']+.35-e['note_off']))<1e-10
F,fm=archive(SRC/'SOURCE_FEATURES.npz');assert F['q_prior'].shape==(239,5,4)
C,cm=archive(ROOT/'audits/hands_recomposition_saved_result_verification_r2/ACTUAL_BLENDER_STATIC_SKIN.npz');S,sm=archive(SRC/'SOURCE_LOCAL_STATES.npz')
ix=np.argmin(abs(F['times']-1.7));assert abs(F['times'][ix]-1.7)<1e-10
fkerr=float(np.linalg.norm(n.native(F['q_prior'][ix],F['wrist_relative_world'][ix])[0]-C['baseline_vertices'][0],axis=1).max()*1000);assert fkerr<.01
# No optimizer invocation: test interfaces and persistence of a normal/exception result.
atomic_record('PERSISTENCE_NORMAL_SELFTEST.npz',dict(x=np.arange(6.),fun=np.arange(3.)),dict(record_type='NO_SOLVE_SELFTEST'))
try:raise RuntimeError('DETERMINISTIC_EXCEPTION_PERSISTENCE_TEST')
except RuntimeError:atomic_record('PERSISTENCE_EXCEPTION_SELFTEST.npz',dict(x=np.arange(6.),fun=np.arange(3.)),dict(error=traceback.format_exc(),record_type='NO_SOLVE_SELFTEST'))
assert np.array_equal(archive(O/'PERSISTENCE_NORMAL_SELFTEST.npz')[0]['x'],np.arange(6.))
tests=selftest()
atomic_json('INPUT_BINDINGS.json',I)
start,end=I['target_window_sec'];events=I['target_context']
times=unique_times([start,end,*np.arange(start,end+1e-6,1/240),*[e[p]+d for e in events for p in ['note_on','note_off'] for d in [-.18,-.075,-.04,0,.0175,.035,.04,.07]]]);times=times[(times>=start)&(times<=end)]
atomic_record('TARGET_CLOCK_REQUEST.npz',dict(times=times),dict(record_type='KEY_ACTION_CLOCK_ONLY'))
atomic_json('STAGE0_PYTHON_GATE.json',dict(pass_=True,numpy=np.__version__,dependencies=[mido.__file__,least_squares.__module__,PchipInterpolator.__module__],FK_skin_error_mm=fkerr,geometry_tests=tests,
    MIDI_events_verified=8,persistence_normal_and_exception_pass=True,solver_calls=0,target_joint_trace_read=False,units='q degrees; vertices/world meters; contact mm; event seconds'))
protect();print('STAGE0_PYTHON_PASS',fkerr,flush=True)
