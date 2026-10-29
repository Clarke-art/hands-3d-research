"""Independent saved-artifact verification using exact rational arithmetic; no Blender mutations."""
from fractions import Fraction
from common import *

status = read(OUT / (PHASE + '_STATUS.json'))
r1 = read(R1_DIR / 'CANDIDATE_CLEAN_REOPEN_PAYLOAD_R1.json')
r2 = read(OUT / 'R2_CANDIDATE_CLEAN_REOPEN_PAYLOAD.json')
donor = read(R1_DIR / 'LIVE_SOURCE_DATA_R1.json')['R1B']['weights']
scope = read(OUT / 'AUTHORIZED_WEIGHT_WRITE_SET_R2.json')
proposal = read(RECON / 'SKIN_WRITE_SCOPE_AMENDMENT_R2_PROPOSAL.json')
approval = read(RESPONSE)
assert approval['proposal_sha256'] == sha(RECON / 'SKIN_WRITE_SCOPE_AMENDMENT_R2_PROPOSAL.json') == EXPECTED_PROPOSAL
assert approval['candidate_R1_sha256'] == sha(R1) == EXPECTED_R1
assert all(approval[f'Q{i}'] == 'YES' for i in range(1, 6)) and approval['all_accepted'] is True
assert approval['authorized_next_phase'] == PHASE and approval['automatic_apply'] is False
assert all(approval[k] is False for k in ['deformation_approved', 'Stage6_approved', 'production_promotion_approved'])
write = set(scope['approved_write_universe_317'])
original, additional, cleanup = set(proposal['existing_244_write_ids']), set(proposal['continuity_reconstruction_vertex_ids']), set(proposal['zero_cleanup_only_vertex_ids'])
assert len(write) == 317 and write == original | additional | cleanup
assert not original & additional and not original & cleanup and not additional & cleanup
assert (len(original), len(additional), len(cleanup)) == (244, 18, 55)
W, B = r2['weights'], r1['weights']
assert all(W[i] == B[i] for i in range(3416) if i not in write)
assert sum(a != b for a, b in zip(W, B)) == status['actual_changed_count'] == 207
rows = {row['vertex_id']: row for row in proposal['per_vertex']}
for i in cleanup:
    allowed = set(rows[i]['allowed_groups'])
    retained = {g: value for g, value in B[i].items() if g in allowed}
    assert set(W[i]) == set(retained)
    assert all(W[i].get(g, 0) == 0 for g in B[i] if g not in allowed)
    # Float32 error bounded by one rounding ulp relative to the normalized real component.
    for group, value in retained.items():
        expected = Fraction(value) / sum(Fraction(v) for v in retained.values())
        assert abs(Fraction(W[i][group]) - expected) <= abs(expected) * Fraction(1, 1 << 23)
for i, vector in enumerate(W):
    assert all(value >= 0 for value in vector.values()) and len(vector) <= 4
    assert abs(sum(Fraction(value) for value in vector.values()) - 1) <= Fraction(1, 100000)
audit = read(OUT / 'R2_CONTINUITY_STATIC_AUDIT.json')
checked = {r['edge_id'] for r in audit['all_checked_edges']}
old_checked = {r['edge_id'] for r in read(R1_DIR / 'SKIN_CONTINUITY_STATIC_CHECK_R1.json')['all_checked_edges']}
assert len(checked) == 2127 and old_checked <= checked
assert all(eid in checked for eid, (i, j) in enumerate(r2['mesh']['edges']) if i in write or j in write)
bad = []
for eid in sorted(checked):
    i, j = r2['mesh']['edges'][eid]
    differences = [abs(Fraction(W[i].get(g, 0)) - Fraction(W[j].get(g, 0))) for g in set(W[i]) | set(W[j])]
    inf, l1 = max(differences, default=Fraction(0)), sum(differences)
    if inf > Fraction(1, 2) or l1 > 1:
        bad.append(eid)
        assert i not in write and j not in write and W[i] == B[i] == donor[i] and W[j] == B[j] == donor[j]
assert bad == status['inherited_qualification_debt_ids'] and len(bad) == 16
assert 1234 not in bad and 5879 not in bad and 1130 in bad
assert r2['mesh'] == r1['mesh'] and r2['rig'] == r1['rig']
assert digest(W) == read(OUT / 'DETERMINISTIC_REPEAT_BASELINE.json')['vector_hash'] == status['R2_weight_vector_hash']
assert sha(CANDIDATE) == status['R2_candidate_hash'] == read(OUT / 'R2_SAVE_REOPEN_VERIFICATION.json')['candidate_sha256']
assert status['save_reopen'] == 'PASS' and status['serialization_drift'] == 0
assert status['verdict'] == 'PASS_READY_FOR_TARGETED_DEFORMATION' and status['deformation_runs'] == status['Stage6_runs'] == 0
protected = read(OUT / 'FROZEN_HASHES_BEFORE.json')
assert inventory() == protected
required = ['TARGETED_RIG_AND_SKIN_DATA_REBUILD_R2_REPORT.md', 'TARGETED_RIG_AND_SKIN_DATA_REBUILD_R2_STATUS.json',
            'AUTHORIZED_WEIGHT_WRITE_SET_R2.json', 'R2_WEIGHT_EVALUATION_CENSUS.json', 'R2_SCOPE_COMPLIANCE_AUDIT.json',
            'R2_ZERO_CLEANUP_RESULT.json', 'R2_CONTINUITY_STATIC_AUDIT.json', 'R2_STATIC_BLOCKER_CLASSIFICATION.json',
            'R2_VS_R1_WEIGHT_DELTA_CENSUS.json', 'R2_VS_R1B_DONOR_COMPARISON.json', 'R2_SKIN_MATH_INTEGRITY_AUDIT.json',
            'R2_FIRST_WEB_AUDIT.json', 'R2_CAP37_AUDIT.json', 'R2_OLD_CAP9_AUDIT.json', 'R2_EDGE5879_STATIC_AUDIT.json',
            'R2_RIG_GEOMETRY_NO_DRIFT_AUDIT.json', 'R2_SAVE_REOPEN_VERIFICATION.json', CANDIDATE.name]
assert all((OUT / filename).is_file() for filename in required)
manifest = read(OUT / 'OUTPUT_EVIDENCE_HASH_MANIFEST_R2.json')
assert digest(manifest['files']) == manifest['canonical_files_hash']
assert all(sha(OUT / filename) == expected for filename, expected in manifest['files'].items())
result = {'status': 'PASS', 'independent_exact_rational_edges_checked': 2127, 'remaining_absolute_exceedances': 16,
          'all_remaining_exceedances_exact_copy_donor_debt': True, 'new_or_worsened_absolute_defects': 0,
          '317_scope_partition_and_3099_outside_exact': True, '55_proportional_zero_cleanup_verified': True,
          'all3416_normalization_exact_rational_check': True, 'historical_files_exact_before_after': True,
          'required_artifacts_present': True, 'output_manifest_verified': True, 'save_reopen_verified': True,
          'candidate_sha256': sha(CANDIDATE), 'weight_vector_sha256': digest(W), 'deformation_runs': 0, 'Stage6_runs': 0}
dump('R2_INDEPENDENT_FINAL_VERIFICATION.json', result)
print(json.dumps(result, indent=2))
