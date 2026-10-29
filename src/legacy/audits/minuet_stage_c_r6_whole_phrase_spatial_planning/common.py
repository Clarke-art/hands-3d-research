"""R6 isolated experiment. Historical assets are read-only."""
from pathlib import Path
import sys, json, hashlib
sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
ROOT = P.parents[1]
C1 = ROOT / 'audits/minuet_stage_c_r1_dual_hand_synchronized_performance'
R5 = ROOT / 'audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation'
OLD = ROOT / 'audits/midi_driven_dual_hand_piano_performance_poc_r1'
sys.path.insert(0, str(OLD / '_deps')) if 'bpy' not in sys.modules else None
import numpy as np
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()
def dump(n, v):
    (P/n).write_text(json.dumps(v, ensure_ascii=False, indent=2, allow_nan=False,
        default=lambda x: x.tolist() if hasattr(x,'tolist') else x.item()), encoding='utf8')
TL = read(C1/'PERFORMANCE_TIMELINE.json')
SOURCE_HASH = 'd8e0f5a85e71323739bfcd4de485ff7a2b4096f8e59bbd4c578ee9d76d3e51a7'

