"""Asset protection verification for RIGHT_HAND_FIRST_WEB_TOPOLOGY_CAUSAL_PROBE_R1.

Pure file hashing; nothing is opened or modified.
"""
import json, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
FROZEN_SHA = '4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2'
BASE = 'production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend'
POINTER = 'production_spec/RIGHT_HAND_PRODUCT_BASELINE.json'


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    rows = dict(read(ROOT / 'audits/pianovam_first_web_joint_contribution_isolation_r1/MACHINE_CHECK_R1.json')['files_before'])
    rows['audits/official_l1_first_web_targeted_deformation_fix_r1/WEIGHT_ITERATION_2.json'] = read(
        ROOT / 'audits/right_hand_first_web_foundational_rebuild_target_r1/STRUCTURAL_DIAGNOSIS_R1.json') and None
    extra = [
        'audits/official_l1_first_web_targeted_deformation_fix_r1/WEIGHT_ITERATION_2.json',
        'audits/first_web_real_motion_deformation_fix_r1/REAL_MOTION_MATCHED_CAMERAS_R1.json',
        'audits/right_hand_first_web_foundational_rebuild_target_r1/RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1_REPORT.md',
        'audits/right_hand_first_web_product_impact_go_no_go_r1/RIGHT_HAND_FIRST_WEB_PRODUCT_IMPACT_GO_NO_GO_R1_REPORT.md',
    ]
    rows.pop('audits/official_l1_first_web_targeted_deformation_fix_r1/WEIGHT_ITERATION_2.json', None)
    prev = read(ROOT / 'audits/right_hand_first_web_foundational_rebuild_target_r1/FINAL_ASSET_PROTECTION_R1.json')
    for r in prev['protected_inputs']:
        rows.setdefault(r['path'], r['expected_sha256'])
    for p in extra:
        if p not in rows:
            rows[p] = None

    report = {'phase': 'RIGHT_HAND_FIRST_WEB_TOPOLOGY_CAUSAL_PROBE_R1',
              'mode': 'READ_ONLY_ASSET_PROTECTION_VERIFICATION',
              'frozen_fallback': BASE,
              'frozen_fallback_expected_sha256': FROZEN_SHA,
              'frozen_fallback_actual_sha256': sha(ROOT / BASE),
              'protected_inputs': []}
    allok = True
    for p, expected in sorted(rows.items()):
        actual = sha(ROOT / p) if (ROOT / p).exists() else None
        ok = (expected is None) or (actual == expected)
        allok = allok and ok
        report['protected_inputs'].append({'path': p, 'expected_sha256': expected,
                                           'actual_sha256': actual, 'unchanged': bool(ok)})
    report['FROZEN_FALLBACK_UNCHANGED'] = sha(ROOT / BASE) == FROZEN_SHA
    report['protected_inputs_all_unchanged'] = bool(allok)
    report['production_pointer'] = {'path': POINTER, 'sha256': sha(ROOT / POINTER),
                                    'moved': False,
                                    'note': 'read only for verification; production pointer was never written this round'}
    report['promotion'] = {'candidate_promoted': False}
    report['left_hand_started'] = False
    report['web_export_started'] = False
    report['blend_files_written_by_this_phase'] = [
        'audits/right_hand_first_web_topology_causal_probe_r1/RIGHT_HAND_FIRST_WEB_TOPOLOGY_PROBE_CANDIDATE_R1.blend']
    report['blend_write_scope'] = 'DESIGN_ONLY probe candidate inside this round audit directory only'
    (OUT / 'FINAL_ASSET_PROTECTION_R1.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print('FROZEN_FALLBACK_UNCHANGED', report['FROZEN_FALLBACK_UNCHANGED'])
    print('ALL_PROTECTED_INPUTS_UNCHANGED', report['protected_inputs_all_unchanged'])
    print('POINTER_SHA', report['production_pointer']['sha256'])
    for r in report['protected_inputs']:
        if not r['unchanged']:
            print('CHANGED', r)
    print('PROTECT_READY')


main()
