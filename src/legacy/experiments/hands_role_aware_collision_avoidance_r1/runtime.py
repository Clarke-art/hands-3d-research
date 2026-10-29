"""Read-only historical adapters; every experiment write stays beside this file."""
import sys, os, json, hashlib, time, importlib.util
from pathlib import Path
sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
OLD = ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1'
C1 = ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance'
A2 = ROOT/'audits/minuet_stage_a_r2_natural_continuous_motion'
R6 = ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning'
SOURCE = C1/'STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_DESIGN_ONLY.blend'
MIDI = ROOT/'audits/minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid'

def guard(event, args):
    if event not in ('open', 'os.listdir', 'os.scandir', 'os.mkdir', 'os.remove', 'os.rename'): return
    paths = [args[0]] + ([args[1]] if event == 'os.rename' else [])
    for p in paths:
        if not isinstance(p, (str, bytes, os.PathLike)): continue
        normalized = str(Path(os.fsdecode(p)).resolve()).replace('\\','/').lower()
        if '/3d interactive components/piano' in normalized:
            raise PermissionError('Independent piano path is forbidden: '+normalized)
        write = event in ('os.mkdir','os.remove','os.rename')
        if event == 'open':
            mode, flags = args[1:3]
            write = (isinstance(mode,str) and any(x in mode for x in 'wax+')) or (isinstance(flags,int) and bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC)))
        if write and not normalized.startswith(str(OUT).replace('\\','/').lower()+'/'):
            raise PermissionError('Write outside experiment denied: '+normalized)
sys.addaudithook(guard)
sys.path.insert(0,str(OLD/'_deps')) if 'bpy' not in sys.modules else None
sys.path.insert(0,str(OLD))
import numpy as np
import performance_core as c  # reads only the registered Hands table/rig/markers

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()
def save(n,v):
    (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf8')
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module

MAN=read(C1/'SCENE_MANIFEST.json')
assert sha(SOURCE)==MAN['sha256']=='d8e0f5a85e71323739bfcd4de485ff7a2b4096f8e59bbd4c578ee9d76d3e51a7'
TL=read(C1/'PERFORMANCE_TIMELINE.json')
NOTES=TL['notes']
POL=read(A2/'GENERATION_POLICY.json')

def historical_coordinator():
    load('common',ROOT/'audits/piano_hand_static_to_dynamic_transition_r1/common.py')
    load('stage_common',A2/'stage_common.py')
    module=load('reference_event_coordinator',A2/'coordinated_motion.py')
    return module, module.EventCoordinator([n for n in NOTES if n['hand']=='R'],POL)

def historical_skin():
    # Load only the existing FK/LBS evaluator, never the R6 solver or runner.
    load('common',R6/'common.py')
    return load('reference_frozen_skin',R6/'whole_phrase_model.py')

def referenced_files():
    paths=[ROOT/'AGENTS.md',SOURCE,MIDI,C1/'PERFORMANCE_TIMELINE.json',C1/'SCENE_MANIFEST.json',
           C1/'piano_performance.wav',A2/'coordinated_motion.py',A2/'02_generate.py',A2/'stage_common.py',
           A2/'GENERATION_POLICY.json',OLD/'performance_core.py',OLD/'KEYBOARD_88_KEY_TABLE_R1.json',
           OLD/'RIG_CANONICAL_PROBE_R1.json',OLD/'FINGERTIP_CONTACT_MARKERS_R1.json',
           R6/'common.py',R6/'whole_phrase_model.py',R6/'SOURCE_MODEL.npz',R6/'SOURCE_MODEL_MANIFEST.json',
           R6/'SHAPE_DELTA.npz',ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement/source_numeric.npz',
           ROOT/'audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/LOCAL_SKIN_ROI.json',
           ROOT/'audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/LATE_HANDOFF_240HZ.json',
           ROOT/'audits/piano_hand_static_to_dynamic_transition_r1/common.py',
           ROOT/'audits/piano_hand_static_posture_clearance_refinement_r2/SOLVED_STATIC_POSES_R2.json',
           ROOT/'audits/piano_hand_static_posture_clearance_refinement_r2/STATIC_REFINEMENT_POLICY_R2.json',
           OLD/'PERFORMANCE_TIMELINE_R1.json']
    paths += list((ROOT/'audits/piano_hands_product_route_reassessment_r1').glob('*.md'))
    return paths

def protect_before():
    assert not (OUT/'PROTECTED_BEFORE.json').exists()
    save('PROTECTED_BEFORE.json',{str(p):sha(p) for p in referenced_files()})
def protect_after():
    before=read(OUT/'PROTECTED_BEFORE.json')
    diff=[p for p,h in before.items() if not Path(p).is_file() or sha(p)!=h]
    save('PROTECTION_CHECK.json',dict(files=len(before),changed_or_missing=diff,pass_=not diff,
        scope='Referenced key files only; no full-directory audit, no historical concurrent FAIL rewriting'))
    assert not diff
