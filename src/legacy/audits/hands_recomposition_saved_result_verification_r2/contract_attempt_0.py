"""Deterministic saved-state adapter. No solver and no animation generation."""
from support import *
import numpy as np
sys.path.insert(0,str(OLD/'_deps')) # configure existing Hands dependencies BEFORE mido
SRC=ROOT/'experiments/hands_role_aware_motion_recomposition_r1'
SAMPLES=ROOT/'experiments/hands_reusable_motion_representation_feasibility_r1/SOURCE_AUDIT_SAMPLES.npz'
TIMES=np.array([1.7,2.0,2.0625])

def safe_path(raw):
    p=Path(raw)
    if not p.is_absolute() or not p.is_relative_to(ROOT):raise ValueError('PATH_OUTSIDE_HANDS')
    if any(x.is_symlink() or x.is_junction() for x in [p,*p.parents] if x.is_relative_to(ROOT)):
        raise ValueError('LINK_OR_JUNCTION_REJECTED')
    p=p.resolve()
    if not p.is_relative_to(ROOT):raise ValueError('RESOLVED_PATH_OUTSIDE_HANDS')
    if not p.is_file():raise ValueError('INPUT_FILE_MISSING: '+str(p))
    return p

def fields(value,required,label):
    if not isinstance(value,dict):raise ValueError('OBJECT_REQUIRED: '+label)
    missing=set(required)-set(value)
    if missing:raise ValueError('MISSING_FIELDS '+label+': '+str(sorted(missing)))

def binding(value):
    fields(value,['scene','native_sha256','source','right_events','all_events'], 'bindings')
    for k,typ in [('scene',dict),('native_sha256',str),('source',list),('right_events',list),('all_events',list)]:
        if not isinstance(value[k],typ):raise ValueError('BINDING_TYPE '+k)
    if not value['source'] or len(value['native_sha256'])!=64:raise ValueError('BINDING_IDENTITY_FORMAT')
    m=value['scene'] # repaired source_scene -> scene, original JSON remains immutable
    fields(m,['path','sha256','scene','mapping','fps','key_pivots','actions','lead_sec'],'scene')
    for k,typ in [('path',str),('sha256',str),('scene',str),('mapping',dict),('fps',int),('key_pivots',dict),('actions',dict),('lead_sec',(int,float))]:
        if not isinstance(m[k],typ):raise ValueError('SCENE_TYPE '+k)
    for side in ['R','L']:
        fields(m['mapping'][side],['rig','mesh','root'],'mapping.'+side)
        if any(not isinstance(m['mapping'][side][k],str) or not m['mapping'][side][k] for k in ['rig','mesh','root']):raise ValueError('MAPPING_TYPE')
    for k,n in m['key_pivots'].items():
        if not k.isdigit() or not 0<=int(k)<88 or not isinstance(n,str):raise ValueError('KEY_PIVOT_TYPE')
    for a in m['actions'].values():
        fields(a,['action','object','slot'],'action')
        if any(not isinstance(a[k],str) for k in ['action','object','slot']):raise ValueError('ACTION_TYPE')
    if m['fps']!=60 or m['lead_sec']!=.35:raise ValueError('SOURCE_CLOCK_MISMATCH')
    safe_path(m['path'])
    e=value['source'][-1]
    fields(e,['finger','key_index','midi_note','note_name','note_id','note_on','note_off'],'active event')
    for n in value['all_events']+value['right_events']+value['source']:
        fields(n,['finger','key_index','midi_note','note_name','note_id','note_on','note_off','hand','channel','on_tick','off_tick','velocity'],'event')
        for k in ['finger','key_index','midi_note','channel','on_tick','off_tick','velocity']:
            if not isinstance(n[k],int):raise ValueError('EVENT_INTEGER_TYPE '+k)
        for k in ['note_name','note_id','hand']:
            if not isinstance(n[k],str):raise ValueError('EVENT_STRING_TYPE '+k)
        if not all(isinstance(n[k],(int,float)) and math_isfinite(n[k]) for k in ['note_on','note_off']):raise ValueError('EVENT_TIME_TYPE')
    if (e['finger'],e['key_index'],e['midi_note'],e['note_name'],e['note_id'])!=(5,53,74,'D5','R05'):
        raise ValueError('SOURCE_EVENT_IDENTITY_MISMATCH')
    if not all(e['note_on']<=t<e['note_off'] for t in TIMES):raise ValueError('WITNESS_NOT_ACTIVE')
    return m

def math_isfinite(x):return bool(np.isfinite(x))

def archive(p):
    safe_path(p)
    with np.load(p,allow_pickle=False) as z:
        a={k:z[k].copy() for k in z.files if k!='metadata_utf8'}
        for k,v in a.items():
            if v.dtype.kind not in 'biuf' or not np.isfinite(v).all():raise ValueError('INVALID_ARRAY '+k)
        meta=json.loads(z['metadata_utf8'].tobytes().decode('utf8')) if 'metadata_utf8' in z else {}
    return a,meta

def result(a,meta,t):
    sizes={'x':(6,),'x0':(6,),'grad':(6,),'active_mask':(6,),'q':(5,4),'world':(4,4),'key_angles':(88,)}
    fields(a,[*sizes,'fun'],'saved result')
    for k,shape in sizes.items():
        if a[k].shape!=shape or not np.isfinite(a[k]).all():raise ValueError('BAD_ARRAY '+k)
    if a['fun'].ndim!=1 or not len(a['fun']) or not np.isfinite(a['fun']).all():raise ValueError('BAD_RESIDUAL_ARRAY')
    if meta.get('time')!=t or meta.get('record_type')!='SOURCE_LOCAL_OPTIMIZER_RESULT_NOT_ANIMATION' or meta.get('other_digits_and_root_frozen') is not True:
        raise ValueError('RESULT_METADATA_IDENTITY_MISMATCH')
    if not np.array_equal(a['x'][:4],a['q'][4]):raise ValueError('SAVED_LITTLE_PARAMETERS_MISMATCH')

def load_inputs():
    I=read(SRC/'INPUT_BINDINGS.json');P=read(SRC/'POLICY.json');man=binding(I)
    if (P['contact_horizontal_mm'],P['contact_vertical_abs_mm'],P['wrong_key_depth_mm'],P['nonregression_mm'])!=(.03,3.,.5,.02):raise ValueError('GATE_CHANGED')
    S,sm=archive(SRC/'SOURCE_LOCAL_STATES.npz')
    if not np.array_equal(S['times'],TIMES):raise ValueError('SAVED_TIMES_MISMATCH')
    A,am=archive(SAMPLES);results=[]
    for ix,t in enumerate(TIMES):
        a,meta=archive(SRC/('SOURCE_LOCAL_RESULT_'+str(ix)+'.npz'));result(a,meta,float(t))
        si=int(np.argmin(abs(A['times']-t)))
        if abs(A['times'][si]-t)>1e-10:raise ValueError('SOURCE_SAMPLE_TIME_MISMATCH')
        for k in ['q','world','key_angles']:
            if not np.array_equal(a[k],S[k][ix]):raise ValueError('AGGREGATE_RESULT_MISMATCH '+k)
        if not np.array_equal(a['q'][:4],A['qdeg'][si,:4]) or not np.array_equal(a['world'],A['rig_world'][si]) or not np.array_equal(a['key_angles'],A['key_angles'][si]):
            raise ValueError('FROZEN_OTHER_DIGIT_ROOT_KEY_MISMATCH')
        if not np.array_equal(S['source_vertices'][ix],A['vertices'][si]):raise ValueError('BASELINE_VERTICES_MISMATCH')
        lo,hi=np.array(P['joint_bounds_deg'][4])
        if not np.all((a['q'][4]>=lo)&(a['q'][4]<=hi)):raise ValueError('OUTSIDE_ORIGINAL_JOINT_DOMAIN')
        results.append((a,meta,si))
    if am.get('source_sha256')!=man['sha256']:raise ValueError('SOURCE_SAMPLE_SCENE_IDENTITY_MISMATCH')
    return I,P,man,S,A,results

def selftest():
    import mido
    I,P,man,S,A,results=load_inputs()
    # Imports only the previous fixed FK/LBS and corrective functions; no optimizer.
    import model as numeric
    M=numeric.M;D=numeric.D
    if len(M['bones'])!=21 or D['weights'].shape!=(3300,21) or D['rest_vertices'].shape!=(3300,3) or D['rest_matrices'].shape!=(21,4,4) or D['parents'].shape!=(21,):raise ValueError('FROZEN_MODEL_SHAPES')
    if S['q'].shape!=(3,5,4) or S['world'].shape!=(3,4,4) or S['key_angles'].shape!=(3,88) or S['source_vertices'].shape!=(3,3300,3):raise ValueError('AGGREGATE_SHAPES')
    canonical=read(OLD/'RIG_CANONICAL_PROBE_R1.json')['R']['bones']
    for i,n in enumerate(M['bones']):
        if n not in canonical or not np.allclose(D['rest_matrices'][i],canonical[n]['matrix'],atol=1e-7,rtol=0):raise ValueError('BONE_IDENTITY '+n)
        if D['parents'][i]>=i or D['parents'][i]<-1:raise ValueError('PARENT_IDENTITY')
    if numeric.PADIDS[4]!=1747:raise ValueError('SKIN_PAD_IDENTITY')
    old=read(SRC/'PROTECTED_BEFORE.json')
    critical=[SRC/n for n in ['INPUT_BINDINGS.json','POLICY.json','source_actual.py','model.py','support.py','persistence.py','SOURCE_LOCAL_STATES.npz','SOURCE_LOCAL_NUMERIC_SUMMARY.json','RESULT_READBACK_CHECK.json']]+[SRC/('SOURCE_LOCAL_RESULT_'+str(i)+'.npz') for i in range(3)]
    critical += [Path(man['path']),SAMPLES,ROOT/'AGENTS.md',OLD/'RIG_CANONICAL_PROBE_R1.json',OLD/'FINGERTIP_CONTACT_MARKERS_R1.json',OLD/'KEYBOARD_88_KEY_TABLE_R1.json',OLD/'performance_core.py',MODEL/'SOURCE_MODEL_MANIFEST.json',MODEL/'SOURCE_MODEL.npz',MODEL/'SHAPE_DELTA.npz',MODEL/'whole_phrase_model.py',PREV/'evaluate.py',ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1/DIGIT_SKIN_ROI.json',ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1/blender_preflight.py',C1/'SCENE_MANIFEST.json',C1/'PERFORMANCE_TIMELINE.json',ROOT/'audits/minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid']
    before={str(safe_path(p)):sha(p) for p in critical}
    for p,h in before.items():
        if p in old and old[p]!=h:raise ValueError('HISTORICAL_INPUT_HASH_MISMATCH '+p)
    if before[man['path']]!=man['sha256']:raise ValueError('C1_SHA_MISMATCH')
    if read(C1/'SCENE_MANIFEST.json')!=man:raise ValueError('SCENE_MANIFEST_MISMATCH')
    events=read(C1/'PERFORMANCE_TIMELINE.json')['notes']
    if events!=I['all_events'] or sorted([n for n in events if n['hand']=='R'],key=lambda n:n['note_on'])!=I['right_events']:raise ValueError('EVENT_IDENTITY_MISMATCH')
    mid=mido.MidiFile(str(critical[-1]));tick=0;sec=0.;tempo=500000;active={};music=[]
    for msg in mido.merge_tracks(mid.tracks):
        sec+=mido.tick2second(msg.time,mid.ticks_per_beat,tempo);tick+=msg.time
        if msg.type=='set_tempo':tempo=msg.tempo
        if msg.type=='note_on' and msg.velocity>0:active[msg.channel,msg.note]=dict(channel=msg.channel,midi_note=msg.note,on_tick=tick,on_sec=sec,velocity=msg.velocity)
        elif msg.type=='note_off' or (msg.type=='note_on' and msg.velocity==0):
            n=active.pop((msg.channel,msg.note));n.update(off_tick=tick,off_sec=sec);music.append(n)
    for n in events:
        hit=[m for m in music if all(m[k]==n[k] for k in ['channel','midi_note','on_tick','off_tick','velocity'])]
        if len(hit)!=1 or max(abs(hit[0]['on_sec']+.35-n['note_on']),abs(hit[0]['off_sec']+.35-n['note_off']))>1e-10:raise ValueError('MIDI_CLOCK_MISMATCH')
    expected=[];baseline_errors=[]
    for a,meta,si in results:
        V=numeric.native(a['q'],a['world'])[0];base=numeric.native(A['qdeg'][si],a['world'])[0]
        err=float(np.linalg.norm(base-A['vertices'][si],axis=1).max()*1000)
        if err>=.01:raise ValueError('BASELINE_FIXED_FK_LBS_PARITY')
        expected.append(V);baseline_errors.append(err)
    negative=[]
    bad=dict(I);bad.pop('scene')
    mutations=[('missing_scene',lambda:binding(bad)),('outside_path',lambda:safe_path(ROOT.parent/'unauthorized.blend')),('relative_path',lambda:safe_path(Path('invalid.blend')))]
    a,meta,_=results[0];wrong=dict(a);wrong['q']=np.zeros((4,4));nan=dict(a);nan['x']=np.full(6,np.nan)
    mutations += [('bad_shape',lambda:result(wrong,meta,1.7)),('nonfinite',lambda:result(nan,meta,1.7))]
    for name,fn in mutations:
        try:fn()
        except (ValueError,KeyError):negative.append(name)
        else:raise ValueError('NEGATIVE_TEST_ACCEPTED '+name)
    # Snapshot existing diagnostic helper functions without executing old modules.
    selections=[(ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1/blender_preflight.py',['digest','native','settime','coords']),(MODEL/'whole_phrase_model.py',['component_planes']),(OLD/'performance_core.py',['axisrot','digit_setup','joint_mats'])]
    text='import bpy,numpy as np,math,json,hashlib\nfrom mathutils import Matrix,Vector\n'
    for path,names in selections:
        tree=ast.parse(path.read_text(encoding='utf-8-sig'))
        nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
        if len(nodes)!=len(names):raise ValueError('HELPER_FUNCTION_MISSING')
        text+='\n'+ '\n\n'.join(ast.unparse(n) for n in nodes)+'\n'
    (O/'blender_helpers.py').write_text(text,encoding='utf8')
    np.savez_compressed(O/'EXPECTED_RECONSTRUCTION.npz',times=TIMES,vertices=np.array(expected))
    dump('INPUT_SHA_BEFORE.json',before)
    dump('INPUT_CONTRACT_GATE.json',dict(pass_=True,field_mapping={'source_scene':'scene'},times=TIMES,negative_tests_rejected=negative,baseline_fixed_FK_LBS_errors_mm=baseline_errors,critical_files=len(before),midi_events_verified=len(events),original_npz_modified=False,optimizer_calls=0,bone_names=M['bones'],skin_pad_vertex=1747,blender_launches=0,dependencies={'numpy':np.__version__,'mido_file':mido.__file__},existing_deps=str(OLD/'_deps')))
    print('INPUT_CONTRACT PASS',baseline_errors,flush=True)

if __name__=='__main__':
    try:selftest()
    except BaseException:
        import traceback
        dump('INPUT_CONTRACT_GATE.json',dict(pass_=False,error=traceback.format_exc(),blender_launches=0))
        raise
