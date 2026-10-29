from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
R1=ROOT/'audits/minuet_target_key_hand_position_planning_r1'
OLD=ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1'
sys.path.insert(0,str(OLD/'_deps'))
sys.path.insert(0,str(ROOT/'audits/piano_hand_static_to_dynamic_transition_r1'))
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
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False,default=lambda x:x.tolist() if hasattr(x,'tolist') else x),encoding='utf8')
