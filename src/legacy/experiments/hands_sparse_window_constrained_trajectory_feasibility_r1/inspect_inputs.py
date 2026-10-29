from native_model import *
import scipy,mido
from scipy.interpolate import BSpline,PchipInterpolator
from scipy.optimize import minimize,NonlinearConstraint
for relative in ['AGENTS.md','audits/hands_continuous_motion_technical_route_decision_r1/FINAL_TECHNICAL_ROUTE_DECISION.md']:
    readtext=valid_path(ROOT/relative).read_text(encoding='utf-8-sig')
rows={}
for p in [SRC/'SOURCE_FEATURES.npz',ROOT/'audits/minuet_stage_a_r2_natural_continuous_motion/motion.npz',ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance/R_approved_reference.npz']:
    a=archive(p);rows[str(p)]={k:dict(shape=v.shape,min=float(v.min()),max=float(v.max())) for k,v in a.items()}
    print(p.name,rows[str(p)],flush=True)
assert sha(valid_path(I['scene']['path']))==I['scene']['sha256']
mid=mido.MidiFile(str(valid_path(ROOT/'audits/minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid')))
tick=0;sec=0.;tempo=500000;active={};events=[]
for msg in mido.merge_tracks(mid.tracks):
    sec+=mido.tick2second(msg.time,mid.ticks_per_beat,tempo);tick+=msg.time
    if msg.type=='set_tempo':tempo=msg.tempo
    if msg.type=='note_on' and msg.velocity>0: active[(msg.channel,msg.note)]=(tick,sec,msg.velocity)
    elif msg.type=='note_off' or (msg.type=='note_on' and msg.velocity==0):
        on=active.pop((msg.channel,msg.note));events.append((msg.channel,msg.note,on[0],tick,on[1],sec,on[2]))
for e in I['all_events']:
    matched=[r for r in events if r[:4]==(e['channel'],e['midi_note'],e['on_tick'],e['off_tick'])]
    assert len(matched)==1 and abs(matched[0][4]-e['source_on_sec'])<1e-9 and abs(matched[0][5]-e['source_off_sec'])<1e-9
    assert abs(e['note_on']-e['source_on_sec']-.35)<1e-9
stages=[e[p]+d for e in EVENTS for p in ['note_on','note_off'] for d in [-.18,-.075,0,.0175,.035,.04,.07]]
times=np.unique(np.r_[START,END,np.arange(np.ceil(START*240),np.floor(END*240)+1)/240,[t for t in stages if START<=t<=END]])
atomic_record('BASELINE_REQUEST.npz',dict(times=times))
try:
    atomic_record('SAVE_SELFTEST.npz',dict(x=np.arange(6.).reshape(2,3)),dict(kind='SELFTEST_ONLY'))
    raise RuntimeError('EXPECTED_EXCEPTION_SAVE_TEST')
except RuntimeError as ex:
    atomic_record('EXCEPTION_SELFTEST.npz',dict(last_finite=np.zeros(60)),dict(error=str(ex),candidate=False))
atomic_json('INPUT_CONTRACT.json',dict(pass_=True,scipy=scipy.__version__,numpy=np.__version__,midi_events_verified=23,window=[START,END],sample_count=len(times),native_vertices=len(W),rig_bones=len(M['bones']),input_arrays=rows,formal_optimization_calls=0))
protect('PROTECTION_INPUT_CONTRACT.json')

