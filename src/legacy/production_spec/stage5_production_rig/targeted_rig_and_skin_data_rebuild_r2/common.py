import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R1_DIR = ROOT / 'production_spec/stage5_production_rig/targeted_rig_and_skin_data_rebuild_after_approval_r1'
RECON = ROOT / 'audits/skin_static_gate_semantics_and_scope_reconciliation_r1'
AUTH_DIR = ROOT / 'audits/cap_skin_driver_and_weight_authority_reconciliation_r1'
R1 = R1_DIR / 'RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R1.blend'
CANDIDATE = OUT / 'RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R2.blend'
RESPONSE = Path(r'<USER_HOME>\Downloads\SKIN_STATIC_GATE_AND_SCOPE_AMENDMENT_HUMAN_REVIEW_R1_RESPONSE_2026-10-03T14-57-26.511Z.json')
EXPECTED_R1 = '290d2734f80edb25872962bf378dbc4c122d6fafe3fd118b22a6e550ddfcb84a'
EXPECTED_PROPOSAL = 'b023f12f40f4eb0bbf32ba4944a6d43fe1503c7b8a3051326e983e05727f7e02'
PHASE = 'TARGETED_RIG_AND_SKIN_DATA_REBUILD_R2'

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def dump(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()

def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()).hexdigest()

def inventory():
    result = {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents}
    result[str(RESPONSE)] = sha(RESPONSE)
    return result

def metric(a, b):
    delta = {g: abs(a.get(g, 0) - b.get(g, 0)) for g in sorted(set(a) | set(b))}
    return {'L_inf': max(delta.values(), default=0), 'L1': sum(delta.values()), 'per_group': delta}
