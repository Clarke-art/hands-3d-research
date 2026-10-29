"""Independent rational-bound and artifact-integrity checks. No Blender import or mutations."""
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PREV = ROOT / 'production_spec/stage5_production_rig/targeted_rig_and_skin_data_rebuild_after_approval_r1'
AUTH = ROOT / 'audits/cap_skin_driver_and_weight_authority_reconciliation_r1'
load = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
candidate = load(PREV / 'CANDIDATE_CLEAN_REOPEN_PAYLOAD_R1.json')
donor = load(PREV / 'LIVE_SOURCE_DATA_R1.json')['R1B']
scope = load(PREV / 'AUTHORIZED_WEIGHT_WRITE_SET_R1.json')
contract = load(AUTH / 'SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json')
web_contract = load(AUTH / 'FIRST_WEB_SKIN_WEIGHT_WRAPPER_R2.json')
labels = {int(k): v for k, v in load(ROOT / 'audits/human_r3_fresh_result_authority_freeze_r1/FRESH_R3_OWNERSHIP_AUTHORITY_R1.json')['membership']['vertex_labels'].items()}
W, D = candidate['weights'], donor['weights']
original_write = set(scope['REBUILD_REQUIRED'])
web = set(web_contract['membership']['vertex_ids'])
classification = load(OUT / 'STATIC_BLOCKER_CLASSIFICATION_R1.json')
zero = load(OUT / 'FORBIDDEN_WEIGHT_ZERO_SEMANTICS_AUDIT_R1.json')
proposal = load(OUT / 'SKIN_WRITE_SCOPE_AMENDMENT_R2_PROPOSAL.json')
status = load(OUT / 'SKIN_STATIC_GATE_SEMANTICS_AND_SCOPE_RECONCILIATION_R1_STATUS.json')
by_edge = {r['edge_id']: r for r in classification['edges']}
assert len(by_edge) == 64
assert Counter(r['primary_classification'] for r in by_edge.values()) == Counter(classification['primary_counts_mutually_exclusive'])
assert Counter(r['temporal_classification'] for r in by_edge.values()) == Counter(classification['temporal_counts_independent'])

def exact_metrics(a, b):
    ds = [abs(Fraction(a.get(g, 0)) - Fraction(b.get(g, 0))) for g in set(a) | set(b)]
    return max(ds, default=Fraction(0)), sum(ds)

new_count = worsened_count = 0
for eid, r in by_edge.items():
    i, j = candidate['mesh']['edges'][eid]
    assert [i, j] == r['vertex_ids']
    before = exact_metrics(D[i], D[j])
    after = exact_metrics(W[i], W[j])
    assert all(abs(float(value) - r['donor_metrics'][key]) < 1e-12 for key, value in zip(['L_inf', 'L1'], before))
    assert all(abs(float(value) - r['candidate_metrics'][key]) < 1e-12 for key, value in zip(['L_inf', 'L1'], after))
    assert after[0] > Fraction(1, 2) or after[1] > 1
    if r['primary_classification'] == 'PREEXISTING_COPY_ONLY':
        assert i not in original_write and j not in original_write and W[i] == D[i] and W[j] == D[j]
    if before[0] <= Fraction(1, 2) and before[1] <= 1:
        new_count += 1
    elif any(x - y > Fraction(contract['normalization']['absolute_tolerance']) for x, y in zip(after, before)):
        worsened_count += 1
assert (new_count, worsened_count) == (37, 3)

necessary = set()
certified_edges = set()
for r in proposal['per_vertex']:
    v = r['vertex_id']
    assert v not in original_write and W[v] == D[v]
    if r['operation'] == 'EXACT_FORBIDDEN_ENTRY_REMOVAL_AND_NORMALIZATION_ONLY':
        assert any(value > 0 and g not in r['allowed_groups'] for g, value in W[v].items())
    else:
        for witness in r['minimality_witnesses']:
            eid, u = witness['edge_id'], witness['write_vertex']
            assert u in original_write and witness['immutable_vertex'] == v
            assert set(candidate['mesh']['edges'][eid]) == {u, v}
            a = set(web_contract['allowed_deform_groups'] if u in web else contract['ownership_guard']['allowed_by_side'][labels[u]])
            assert a == set(witness['write_allowed_groups'])
            f = sum(Fraction(value) for g, value in W[v].items() if g not in a)
            retained = sum(Fraction(value) for g, value in W[v].items() if g in a)
            inf = max((Fraction(value) for g, value in W[v].items() if g not in a), default=Fraction(0))
            l1 = f + max(Fraction(0), 1 - Fraction(contract['normalization']['absolute_tolerance']) - retained)
            assert inf > Fraction(1, 2) or l1 > 1
            assert abs(float(l1) - witness['minimum_L1_conservative']) < 1e-12
            certified_edges.add(eid)
    necessary.add(v)
assert necessary == set(proposal['new_vertex_ids']) and len(necessary) == 73
assert len(certified_edges) == 32
assert len(zero['per_vertex']) == 55
assert all(r['candidate_value'] == r['historical_donor_value'] > 0 for r in zero['per_group_entry'])
assert status['proposal_sha256'] == sha(OUT / 'SKIN_WRITE_SCOPE_AMENDMENT_R2_PROPOSAL.json')
assert sha(ROOT / candidate['candidate_path']) == status['candidate_blend_sha256_before'] == status['candidate_blend_sha256_after']
inputs = load(OUT / 'READ_ONLY_INPUT_AND_OUTPUT_VERIFICATION_R1.json')['consumed_inputs']
assert all(sha(ROOT / path) == digest for path, digest in inputs.items())
manifest = load(OUT / 'OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json')
assert all(sha(OUT / filename) == digest for filename, digest in manifest['files'].items())
print(json.dumps({'independent_verification': 'PASS', 'rational_metric_edge_count': 64,
                  'rational_scope_conflict_edges': len(certified_edges), 'compulsory_additional_vertex_count': 73,
                  'residue_vertex_count': 55, 'introduced': new_count, 'worsened': worsened_count,
                  'all_source_and_output_hashes_match': True, 'candidate_hash_unchanged': True,
                  'blend_writes': 0, 'weights_written': 0, 'deformation_runs': 0, 'Stage6_runs': 0}, indent=2))
