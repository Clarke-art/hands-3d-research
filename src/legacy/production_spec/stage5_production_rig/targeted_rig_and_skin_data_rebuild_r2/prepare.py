from common import *

assert not CANDIDATE.exists(), 'FAIL_CLOSED: existing R2 may not be overwritten'
assert not (OUT / 'FROZEN_HASHES_BEFORE.json').exists(), 'Existing protection snapshot may not be replaced'
approval = read(RESPONSE)
expected = {'review_id': 'SKIN_STATIC_GATE_AND_SCOPE_AMENDMENT_HUMAN_REVIEW_R1',
            'phase': 'HUMAN_SKIN_STATIC_GATE_AND_SCOPE_AMENDMENT_APPROVAL',
            'proposal_sha256': EXPECTED_PROPOSAL, 'candidate_R1_sha256': EXPECTED_R1,
            **{f'Q{i}': 'YES' for i in range(1, 6)}, 'all_questions_answered': True, 'all_accepted': True,
            'response_kind': 'HUMAN_STATIC_GATE_SCOPE_AMENDMENT_RESPONSE', 'authorized_next_phase': PHASE,
            'automatic_apply': False, 'deformation_approved': False, 'Stage6_approved': False,
            'production_promotion_approved': False}
for key, value in expected.items():
    assert type(approval.get(key)) is type(value) and approval[key] == value, ('FAIL_CLOSED approval mismatch', key)
proposal_path = RECON / 'SKIN_WRITE_SCOPE_AMENDMENT_R2_PROPOSAL.json'
assert sha(proposal_path) == EXPECTED_PROPOSAL
assert sha(R1) == EXPECTED_R1
proposal = read(proposal_path)
old = read(R1_DIR / 'AUTHORIZED_WEIGHT_WRITE_SET_R1.json')
original = set(old['REBUILD_REQUIRED'])
continuity = set(proposal['continuity_reconstruction_vertex_ids'])
cleanup = set(proposal['zero_cleanup_only_vertex_ids'])
additional = set(proposal['new_vertex_ids'])
assert original == set(proposal['existing_244_write_ids']) and len(original) == 244
assert len(continuity) == 18 and len(cleanup) == 55 and len(additional) == 73
assert not continuity & cleanup and continuity | cleanup == additional
assert not original & additional and len(original | additional) == proposal['proposed_total_write_count'] == 317
assert set(r['vertex_id'] for r in proposal['per_vertex']) == additional
for row in proposal['per_vertex']:
    expected_operation = 'EXACT_FORBIDDEN_ENTRY_REMOVAL_AND_NORMALIZATION_ONLY' if row['vertex_id'] in cleanup else 'LOCAL_CONTINUOUS_RECONSTRUCTION_WITH_APPROVED_SUPPORT'
    assert row['operation'] == expected_operation
bundle = read(AUTH_DIR / 'SKIN_AUTHORITY_PROPOSAL_BUNDLE_R1.json')
previous_approval = read(R1_DIR / 'HUMAN_APPROVAL_RESPONSE_SOURCE_COPY.json')
assert digest(bundle) == previous_approval['proposal_bundle_hash']
for filename, expected_hash in bundle['proposal_files'].items():
    assert sha(AUTH_DIR / filename) == expected_hash, filename
r3_path = ROOT / 'audits/human_r3_fresh_result_authority_freeze_r1/FRESH_R3_OWNERSHIP_AUTHORITY_R1.json'
assert digest(read(r3_path)) == bundle['R3_authority_hash']
data = read(R1_DIR / 'LIVE_SOURCE_DATA_R1.json')
corrected_path = ROOT / data['CORRECTED']['source_path']
assert sha(corrected_path) == bundle['corrected_rig_sha256'] == data['CORRECTED']['source_sha256']
prior_payload = read(R1_DIR / 'CANDIDATE_CLEAN_REOPEN_PAYLOAD_R1.json')
assert prior_payload['candidate_sha256'] == EXPECTED_R1
prior_manifest = read(R1_DIR / 'OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json')
for filename, value in prior_manifest['files'].items():
    assert sha(R1_DIR / filename) == value, filename
dump('FROZEN_HASHES_BEFORE.json', inventory())
(OUT / 'HUMAN_AMENDMENT_APPROVAL_SOURCE_COPY.json').write_bytes(RESPONSE.read_bytes())
dump('HUMAN_AMENDMENT_AND_INPUT_VERIFICATION_R2.json', {
    'status': 'PASS', 'Human_approval_verified': True, 'approval_source': str(RESPONSE),
    'approval_sha256': sha(RESPONSE), 'expected_fields': expected, 'Human_notes': approval['notes'],
    'proposal_sha256': EXPECTED_PROPOSAL, 'R1_candidate_sha256': EXPECTED_R1,
    'original_authority_bundle_hash': digest(bundle), 'authority_component_hashes': bundle['proposal_files'],
    'R3_authority_hash': bundle['R3_authority_hash'], 'corrected_rig_sha256': sha(corrected_path),
    'candidate_base': 'R1 candidate geometry/rig/binding/material/UV/weights; no R1B regeneration',
    'deformation_approved': False, 'Stage6_approved': False, 'production_promotion_approved': False})
dump('AUTHORIZED_WEIGHT_WRITE_SET_R2.json', {
    'phase': PHASE, 'approval_sha256': sha(RESPONSE), 'proposal_sha256': EXPECTED_PROPOSAL,
    'original_244': sorted(original), 'additional_continuity_18': sorted(continuity),
    'cleanup_only_55': sorted(cleanup), 'additional_73': sorted(additional),
    'approved_write_universe_317': sorted(original | additional), 'outside_write_ids': sorted(set(range(3416)) - original - additional),
    'counts': {'original': 244, 'continuity': 18, 'cleanup_only': 55, 'additional': 73, 'total': 317},
    'partitions_disjoint': True, 'arbitrary_scope_extension_allowed': False,
    'cleanup55_free_optimizer_permission': False, 'per_additional_vertex_authority': proposal['per_vertex']})
print('Human approval / hashes PASS; exact write partitions 244 + 18 + 55 = 317')
