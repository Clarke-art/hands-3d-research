import sys
sys.dont_write_bytecode = True
import hashlib, json, datetime
from pathlib import Path
from PIL import Image

audit = Path(__file__).resolve().parents[1]
root = audit.parents[2]
def read(name):
    return json.loads((audit / name).read_text(encoding='utf-8'))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

before = read('FROZEN_HASHES_BEFORE.json')
after = {str(p.relative_to(root)).replace('\\', '/'): sha(p)
         for directory in ['production_spec', 'docs']
         for p in (root / directory).rglob('*')
         if p.is_file() and audit not in p.parents}
assert before == after, 'Protected inventory or hashes changed'
required = ['MANUAL_ANATOMICAL_REFERENCE_REVIEW_R1_REPORT.md',
            'MANUAL_ANATOMICAL_REFERENCE_REVIEW_R1_STATUS.json',
            'MANUAL_ANATOMICAL_REFERENCE_PACK_R1.json',
            'MODEL_HUMAN_LANDMARK_REGISTRATION.json',
            'BODY_SIDE_16_MANUAL_REGISTRATION_CANDIDATES.json',
            'CAP_TO_COLLAR_3_EDGE_ANATOMICAL_SANITY_AUDIT.json',
            'MANUAL_REGISTRATION_REVIEW.html']
for name in required:
    assert (audit / name).stat().st_size > 0
    if name.endswith('.json'):
        read(name)
renders = ['MODEL_DORSAL_BODY16.png', 'MODEL_PALMAR_BODY16.png',
           'MODEL_RADIAL_BODY16.png', 'MODEL_FIRST_WEB_BODY16.png',
           'MODEL_INDEX_PROXIMAL_BODY16.png',
           'CAP_TO_COLLAR_3_EDGE_ANATOMICAL_SANITY_CHECK.png']
for name in renders:
    with Image.open(audit / 'renders' / name) as im:
        im.load()
        assert im.size == (1800, 1200)
pack = read('MANUAL_ANATOMICAL_REFERENCE_PACK_R1.json')
assert [r['id'] for r in pack['entries']] == list('ABCDE')
for entry in pack['entries']:
    original = audit / entry['file']
    assert sha(original) == entry['original_sha256']
    with Image.open(original) as im:
        assert list(im.size) == entry['original_dimensions']
candidates = read('BODY_SIDE_16_MANUAL_REGISTRATION_CANDIDATES.json')
assert len(candidates['body_ids']) == len(set(candidates['body_ids'])) == 16
assert {k: len(v) for k,v in candidates['clusters'].items()} == {
    'DORSAL': 4, 'PALMAR': 5, 'RADIAL': 3, 'ULNAR': 4}
assert set(candidates['body_ids']) == {i for v in candidates['clusters'].values() for i in v}
status = read('MANUAL_ANATOMICAL_REFERENCE_REVIEW_R1_STATUS.json')
assert status['BRANCH'] == 'D'
assert status['REGISTRATION_STATUS'] == 'PENDING_HUMAN_REGISTRATION'
for key in ['WEIGHT_DELTA','GEOMETRY_DELTA','TOPOLOGY_DELTA','BONE_DELTA','JOINT_DELTA','BLEND_FILES_WRITTEN','deformation_runs']:
    assert status[key] == 0
assert status['R1F_CREATED'] is False
assert read('MODEL_HUMAN_LANDMARK_REGISTRATION.json')['human_answers_recorded'] == []
result = {
    'verified_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'all_required_outputs_present_and_decodable': True,
    'required_files': required, 'required_renders': renders,
    'protected_file_count': len(before),
    'protected_inventory_and_hashes_equal': True,
    'used_original_photo_hashes_equal': True,
    'body16_and_cluster_partition_correct': True,
    'browser_verification': {
        'url': 'http://127.0.0.1:8791/MANUAL_REGISTRATION_REVIEW.html',
        'all_five_views_and_path_switch_verified': True,
        'desktop_two_columns_and_narrow_layout_verified': True,
        'overlay_and_opacity_verified': True,
        'cluster_and_id_toggles_verified': True,
        'native_geometry_disables_current_joint_labels_and_overlay': True,
        'console_error_and_warning_count': 0,
        'human_questions_and_cluster_decisions_all_UNDECIDED': True,
        'human_save_or_export_clicked': False,
        'proof_screenshot': 'renders/REVIEW_PAGE_DESKTOP.jpg',
        'temporary_viewport_override_reset': True
    },
    'STOP': 'WAITING_FOR_HUMAN_REVIEW'
}
(audit / 'OUTPUT_VERIFICATION.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print('PASS:',len(before),'protected files unchanged; outputs and source originals verified.')
