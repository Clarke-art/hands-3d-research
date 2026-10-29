import sys,os,json,time,hashlib,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
R1=ROOT/'experiments/hands_role_aware_collision_avoidance_r1'
C1=ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance'
A2=ROOT/'audits/minuet_stage_a_r2_natural_continuous_motion'
OLD=ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1'
R6=ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning'
SOURCE=C1/'STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_DESIGN_ONLY.blend'
MIDI=ROOT/'audits/minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid'
def guard(event,args):
    if event not in ['open','os.listdir','os.scandir','os.mkdir','os.remove','os.rename']:return
    for p in [args[0]]+([args[1]] if event=='os.rename' else []):
        if not isinstance(p,(str,bytes,os.PathLike)):continue
        path=str(Path(os.fsdecode(p)).resolve()).replace('\\','/').lower()
        if '/3d interactive components/piano' in path:raise PermissionError('Independent piano excluded')
        write=event in ['os.mkdir','os.remove','os.rename']
        if event=='open':
            mode,flags=args[1:3]
            write=(isinstance(mode,str) and any(x in mode for x in 'wax+')) or (isinstance(flags,int) and bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC)))
        if write and not path.startswith(str(OUT).replace('\\','/').lower()+'/'):raise PermissionError('Write outside R2')
sys.addaudithook(guard)
if 'bpy' not in sys.modules:sys.path.insert(0,str(OLD/'_deps'))
sys.path.insert(0,str(OLD))
import numpy as np
import performance_core as c
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(name,data):(OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf8')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def skin_module():
    load('common',R6/'common.py');return load('frozen_skin_r2_readonly',R6/'whole_phrase_model.py')
MAN=read(C1/'SCENE_MANIFEST.json');TL=read(C1/'PERFORMANCE_TIMELINE.json');NOTES=TL['notes'];POL=read(A2/'GENERATION_POLICY.json')
assert sha(SOURCE)==MAN['sha256']=='d8e0f5a85e71323739bfcd4de485ff7a2b4096f8e59bbd4c578ee9d76d3e51a7'
SCOPE=read(R1/'EVENT_SCOPE.json');START=SCOPE['start'];END=SCOPE['end'];CHANGED=[SCOPE['new']['finger']-1,SCOPE['old']['finger']-1]
BASE=dict(np.load(R1/'BASELINE_ACTUAL.npz'))
ROIS=read(ROOT/'audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/LOCAL_SKIN_ROI.json')
def interp(arr,t):
    flat=arr.reshape(len(BASE['times']),-1)
    return np.column_stack([np.interp(t,BASE['times'],flat[:,j]) for j in range(flat.shape[1])]).reshape((len(t),)+arr.shape[1:])
def smooth(u):u=np.clip(u,0,1);return u**3*(10+u*(-15+6*u))
def smooth_derivative(u):return np.where((u>0)&(u<1),30*u*u*(u-1)**2,0.)
def release_gate(t,off,follow,next_prepare_end):
    # Zero value AND derivative at OFF; two quintic pieces meet at the A2
    # release endpoint. An overlapping PREPARING label does not cause a reset.
    t=np.asarray(t);up=smooth((t-off)/follow);down=1-smooth((t-off-follow)/(next_prepare_end-off-follow))
    return up*down
def role(t,j):
    ns=sorted([n for n in NOTES if n['hand']=='R' and n['finger']==j+1],key=lambda n:n['note_on'])
    active=next((n for n in ns if n['note_on']<=t<n['note_off']),None)
    releasing=next((n for n in reversed(ns) if n['note_off']<=t<n['note_off']+POL['finger_release_follow_sec']),None)
    prepare=next((n for n in ns if n['note_on']-POL['prepare_sec']<=t<n['note_on']),None)
    state,n=('ACTIVE_HOLD',active) if active else ('RELEASING',releasing) if releasing else ('PREPARING',prepare) if prepare else ('IDLE',None)
    return state,n
def refs():
    paths=[ROOT/'AGENTS.md',SOURCE,MIDI,C1/'SCENE_MANIFEST.json',C1/'PERFORMANCE_TIMELINE.json',A2/'coordinated_motion.py',A2/'02_generate.py',A2/'GENERATION_POLICY.json',
      OLD/'performance_core.py',OLD/'PERFORMANCE_TIMELINE_R1.json',OLD/'KEYBOARD_88_KEY_TABLE_R1.json',OLD/'RIG_CANONICAL_PROBE_R1.json',OLD/'FINGERTIP_CONTACT_MARKERS_R1.json',
      R6/'common.py',R6/'whole_phrase_model.py',R6/'SOURCE_MODEL.npz',R6/'SOURCE_MODEL_MANIFEST.json',R6/'SHAPE_DELTA.npz',
      ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement/source_numeric.npz',ROOT/'audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/LOCAL_SKIN_ROI.json',
      R1/'BASELINE_ACTUAL.npz',R1/'BASELINE_GEOMETRY.json',R1/'STATIC_ACTUAL_SKIN.npz',R1/'STATIC_ACTUAL_VALIDATION.json',R1/'PLANNER_POLICY_COORDINATE_VERIFIED.json',R1/'role_planner.py',R1/'runtime.py',R1/'EVENT_SCOPE.json']
    return paths+list(R1.glob('*.md'))
def protect_after():
    before=read(OUT/'PROTECTED_BEFORE.json');changed=[p for p,h in before.items() if not Path(p).is_file() or sha(p)!=h]
    save('PROTECTION_CHECK.json',dict(files=len(before),changed_or_missing=changed,pass_=not changed,no_global_audit=True,historical_concurrent_fail_untouched=True));assert not changed
