from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
R2=ROOT/'audits/minuet_stage_b_r2_left_hand_continuous_accompaniment'
R3=ROOT/'audits/minuet_stage_b_r3_left_hand_global_contact_placement'
ISO=ROOT/'audits/minuet_stage_b_r3_dynamic_failure_isolation_r1'
OLD=ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1'
if 'bpy' not in sys.modules:sys.path.insert(0,str(OLD/'_deps'))
sys.path.insert(0,str(ROOT/'audits/piano_hand_static_to_dynamic_transition_r1'))
sys.path.insert(1,str(R2))
import common as o
import numpy as np
c=o.c
SOURCE=ROOT/'audits/minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def dump(name,v):
    (P/name).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False,default=lambda x:x.tolist() if hasattr(x,'tolist') else x),encoding='utf8')
