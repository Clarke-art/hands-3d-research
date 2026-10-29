from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
C1=ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance'
A=ROOT/'audits/minuet_stage_a_r2_natural_continuous_motion'
B=ROOT/'audits/minuet_stage_b_r3_budget_policy_candidate_recovery_r1'
OLD=ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1'
MIDI=ROOT/'audits/minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid'
DEST=P/'STAGE_C_R2_LOCAL_FINGER_OVERLAP_DESIGN_ONLY.blend'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf8')
def doc(n,v):(P/n).write_text(v,encoding='utf8')
