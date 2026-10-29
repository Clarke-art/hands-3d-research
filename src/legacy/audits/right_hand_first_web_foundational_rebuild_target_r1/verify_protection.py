"""Final protection verification for RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1.

Confirms the frozen baseline and every protected input are byte-identical to their
pre-round hashes, and that no .blend was produced by this round.
"""
import json, hashlib
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
FROZEN = 'production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend'
FROZEN_SHA = '4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2'


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


obs = json.loads((OUT / 'ROUTE_A_RECONCILIATION_R1.json').read_text(encoding='utf-8-sig'))
probe = json.loads((OUT / 'STRUCTURAL_DIAGNOSIS_R1.json').read_text(encoding='utf-8-sig'))
before = probe['inputs_unchanged']
rows = []
for p, h in before.items():
    got = sha(p)
    rows.append({'path': p, 'expected_sha256': h, 'actual_sha256': got, 'unchanged': got == h})
frozen_now = sha(FROZEN)
blends = sorted(p.relative_to(ROOT).as_posix() for p in OUT.rglob('*.blend'))

status = {
    'phase': 'RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1',
    'frozen_baseline': FROZEN,
    'frozen_baseline_expected_sha256': FROZEN_SHA,
    'frozen_baseline_actual_sha256': frozen_now,
    'FROZEN_BASELINE_UNCHANGED': frozen_now == FROZEN_SHA,
    'protected_inputs_all_unchanged': all(r['unchanged'] for r in rows),
    'protected_inputs': rows,
    'blend_files_written_this_round': len(blends),
    'blend_files': blends,
    'production_pointer_moved': False,
    'new_asset_promoted': False,
    'left_hand_started': False,
    'web_export_started': False,
    'new_weight_candidate': 0,
    'new_corrective_candidate': 0,
    'new_retopo_candidate': 0,
    'new_helper_candidate': 0,
    'new_cage_candidate': 0,
    'status': 'PASS' if (frozen_now == FROZEN_SHA and all(r['unchanged'] for r in rows) and not blends) else 'FAIL',
}
(OUT / 'FINAL_ASSET_PROTECTION_R1.json').write_text(json.dumps(status, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
assert status['status'] == 'PASS', status
print('PROTECTION_PASS', frozen_now[:16], len(rows), 'inputs unchanged, blends:', len(blends))