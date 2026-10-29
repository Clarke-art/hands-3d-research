"""Read-only static evidence reconciliation. Writes reports only, never a blend/vector payload."""
import collections
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PREV = ROOT / 'production_spec/stage5_production_rig/targeted_rig_and_skin_data_rebuild_after_approval_r1'
AUTH_DIR = ROOT / 'audits/cap_skin_driver_and_weight_authority_reconciliation_r1'
PHASE = 'SKIN_STATIC_GATE_SEMANTICS_AND_SCOPE_RECONCILIATION_R1'
EXPECTED = '290d2734f80edb25872962bf378dbc4c122d6fafe3fd118b22a6e550ddfcb84a'
CANDIDATE = PREV / 'RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R1.blend'
CONSUMED = {}

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()

def rel(path):
    return path.relative_to(ROOT).as_posix()

def read(path):
    CONSUMED[rel(path)] = sha(path)
    return json.loads(path.read_text(encoding='utf-8-sig'))

def canonical_hash(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()).hexdigest()

def dump(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')

def source(relative, needle, meaning, authority_role):
    path = ROOT / relative
    CONSUMED[rel(path)] = sha(path)
    lines = path.read_text(encoding='utf-8-sig').splitlines()
    matches = [i + 1 for i, line in enumerate(lines) if needle in line]
    assert matches, (relative, needle)
    return {'path': rel(path), 'sha256': sha(path), 'line_numbers': matches,
            'excerpts': [lines[i - 1].strip() for i in matches],
            'meaning': meaning, 'authority_role': authority_role}

assert sha(CANDIDATE) == EXPECTED
CONSUMED[rel(CANDIDATE)] = EXPECTED
bundle = read(AUTH_DIR / 'SKIN_AUTHORITY_PROPOSAL_BUNDLE_R1.json')
approval = read(PREV / 'HUMAN_APPROVAL_RESPONSE_SOURCE_COPY.json')
assert canonical_hash(bundle) == approval['proposal_bundle_hash']
for filename, digest in bundle['proposal_files'].items():
    assert sha(AUTH_DIR / filename) == digest, filename
    CONSUMED[rel(AUTH_DIR / filename)] = digest
previous_manifest = read(PREV / 'OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json')
assert canonical_hash(previous_manifest['files']) == previous_manifest['canonical_files_hash']
for filename, digest in previous_manifest['files'].items():
    assert sha(PREV / filename) == digest, filename
    CONSUMED[rel(PREV / filename)] = digest

candidate = read(PREV / 'CANDIDATE_CLEAN_REOPEN_PAYLOAD_R1.json')
sources = read(PREV / 'LIVE_SOURCE_DATA_R1.json')
assert candidate['candidate_sha256'] == EXPECTED
donor_path = ROOT / sources['R1B']['source_path']
assert sha(donor_path) == sources['R1B']['source_sha256']
CONSUMED[rel(donor_path)] = sha(donor_path)
partition = read(PREV / 'AUTHORIZED_WEIGHT_WRITE_SET_R1.json')
prior_static = read(PREV / 'SKIN_CONTINUITY_STATIC_CHECK_R1.json')
contract = read(AUTH_DIR / 'SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json')
web_contract = read(AUTH_DIR / 'FIRST_WEB_SKIN_WEIGHT_WRAPPER_R2.json')
reuse_contract = read(AUTH_DIR / 'R1B_SAFE_WEIGHT_REUSE_SET_R1.json')
cap_contract = read(AUTH_DIR / 'CAP37_SKIN_DRIVER_AUTHORITY_R1.json')
old_contract = read(AUTH_DIR / 'OLD_CAP9_SKIN_CORRECTION_AUTHORITY_R1.json')
r3 = read(ROOT / 'audits/human_r3_fresh_result_authority_freeze_r1/FRESH_R3_OWNERSHIP_AUTHORITY_R1.json')
assert canonical_hash(r3) == approval['R3_authority_hash']
W, D, EDGES = candidate['weights'], sources['R1B']['weights'], candidate['mesh']['edges']
SETS = {k: set(partition[k]) for k in ('SAFE_REUSE', 'TARGETED_REVALIDATION', 'REBUILD_REQUIRED')}
WRITE = SETS['REBUILD_REQUIRED']
LABEL = {int(k): v for k, v in r3['membership']['vertex_labels'].items()}
WEB = set(web_contract['membership']['vertex_ids'])
CAP = {r['vertex_id'] for r in cap_contract['per_vertex_surface_evidence']}
OLD = set(old_contract['vertex_ids'])
TOL = contract['normalization']['absolute_tolerance']
INF_GATE = contract['static_edge_gates']['max_single_group_jump_proposal']
L1_GATE = contract['static_edge_gates']['max_L1_jump_proposal']
assert (INF_GATE, L1_GATE, TOL, contract['ownership_guard']['forbidden_weight']) == (.5, 1, 1e-5, 0)
CL = {i: name for name, ids in SETS.items() for i in ids}
INCIDENT = collections.defaultdict(list)
for eid, (i, j) in enumerate(EDGES):
    INCIDENT[i].append(eid)
    INCIDENT[j].append(eid)

def allowed(i):
    if i in WEB:
        return set(web_contract['allowed_deform_groups'])
    if i in CAP:
        return set(cap_contract['allowed_cap_deform_groups'])
    if i in OLD:
        return set(old_contract['allowed_deform_groups'])
    if i in LABEL:
        return set(contract['ownership_guard']['allowed_by_side'][LABEL[i]])
    return set(contract['deform_bones'])

def metric(a, b):
    delta = {g: abs(a.get(g, 0) - b.get(g, 0)) for g in sorted(set(a) | set(b))}
    return {'L_inf': max(delta.values(), default=0), 'L1': sum(delta.values()), 'per_group': delta}

def fails(m):
    return m['L_inf'] > INF_GATE or m['L1'] > L1_GATE

def endpoint(i):
    return {'vertex_id': i, 'classification': CL[i], 'authorized_write': i in WRITE,
            'frozen_R3_side': LABEL.get(i, 'OUTSIDE_BOUNDED_R3'), 'FIRST_WEB21': i in WEB,
            'allowed_groups': sorted(allowed(i)), 'forbidden_groups': sorted(set(contract['deform_bones']) - allowed(i)),
            'donor_vector': D[i], 'candidate_vector': W[i], 'exact_donor_copy': D[i] == W[i]}

def support_witness(write_vertex, immutable_vertex, edge_id):
    a = allowed(write_vertex)
    fixed = W[immutable_vertex]
    foreign = {g: value for g, value in fixed.items() if g not in a}
    f = sum(foreign.values())
    retained_mass = sum(value for g, value in fixed.items() if g in a)
    # Even permitting every allowed group and ignoring max-4 restrictions cannot beat this lower bound.
    lower_inf = max(foreign.values(), default=0)
    lower_l1 = f + max(0, 1 - TOL - retained_mass)
    if lower_inf <= INF_GATE and lower_l1 <= L1_GATE:
        return None
    return {'edge_id': edge_id, 'write_vertex': write_vertex, 'immutable_vertex': immutable_vertex,
            'write_allowed_groups': sorted(a), 'fixed_forbidden_components': foreign,
            'fixed_forbidden_mass': f, 'fixed_allowed_mass': retained_mass,
            'minimum_L_inf': lower_inf, 'minimum_L1_conservative': lower_l1,
            'normalization_tolerance_accounted_for': TOL,
            'formula': 'min L_inf >= max fixed forbidden component; min L1 >= F + max(0, 1 - normalization_tolerance - A)',
            'proof': 'All foreign components are exact zero at the writable endpoint. Fixed endpoint cannot change under R1. Sum of allowed components at the writable endpoint must be >=1-tolerance. A lower bound already exceeds the unchanged gate; changing only existing authorized vertices cannot solve this edge.'}

provenance_sources = [
    source('production_spec/stage5_production_rig/stage5b_r1a/scripts/s5b_r1a_audit.py', 'if w <= 1e-6:',
           'R1A cross-digit reporting significance cutoff, with documented donor carry-over; not a universal mathematical-zero definition.', 'HISTORICAL_VALIDATOR'),
    source('production_spec/stage5_production_rig/stage5b_r1a/scripts/s5b_r1a_audit.py', 'NORM_ERR < 1e-6',
           'Historical R1A normalization criterion; later R1B and current approved contract use 1e-5.', 'HISTORICAL_VALIDATOR'),
    source('production_spec/stage5_production_rig/stage5b_r1a/scripts/s5b_r1a_build.py', 'if v > EPS or g in frozen',
           'EPS=1e-8 prunes free groups only. Frozen groups are explicitly retained even below EPS.', 'HISTORICAL_GENERATOR'),
    source('production_spec/stage5_production_rig/stage5b_r1b/scripts/r1b_common.py', 'EPS = 1e-8',
           'R1B free-weight construction epsilon; not a runtime influence cutoff.', 'HISTORICAL_GENERATOR'),
    source('production_spec/stage5_production_rig/stage5b_r1b/scripts/r1b_common.py', 'if v > EPS or g in frozen',
           'R1B preserves frozen positive weights below its free-weight prune threshold.', 'HISTORICAL_GENERATOR'),
    source('production_spec/stage5_production_rig/stage5b_r1b/scripts/s5b_r1b_verify.py', 'if w > 0.0',
           'Positive saved influences count even below 1e-8/1e-6.', 'HISTORICAL_VALIDATOR'),
    source('production_spec/stage5_production_rig/stage5b_r1b/scripts/s5b_r1b_verify.py', '> 1e-5',
           'R1B serialized normalization tolerance, not zero-weight epsilon.', 'HISTORICAL_VALIDATOR'),
    source('production_spec/stage5_production_rig/stage5b_r1c/scripts/s5b_r1c_build.py', 'if v > 1e-6',
           'R1C generated free vectors prune at 1e-6 before normalization/serialization.', 'HISTORICAL_GENERATOR'),
    source('production_spec/stage5_production_rig/stage5b_r1c/scripts/s5b_r1c_build.py', 'foreign group survived',
           'R1C rejects any surviving foreign group on corrected vertices; generation prune is not permission to retain it.', 'HISTORICAL_VALIDATOR'),
    source('production_spec/stage5_production_rig/stage5b_r1d/scripts/s5b_r1d_build.py', 'if v > 1e-6',
           'R1D construction/relaxation prune threshold applies only inside its own authorized region.', 'HISTORICAL_GENERATOR'),
    source('production_spec/stage5_production_rig/stage5b_r1d/scripts/s5b_r1d_build.py', 'len(FLIP_AFTER_W) <= len(FLIP_BEFORE)',
           'R1D combines a local distal hard-flip zero target with global count no-regression; its 0.95/0.05 hard-flip predicate is not the later 0.5/1.0 metric gate.', 'HISTORICAL_VALIDATOR'),
    source('production_spec/stage5_production_rig/stage5b_r1e/scripts/s5b_r1e_build.py', 'only NEW hard steps are touched',
           'R1E boundary relaxation targets new hard flips, within approved region only.', 'HISTORICAL_GENERATOR'),
    source('production_spec/stage5_production_rig/stage5b_r1e/scripts/s5b_r1e_build.py', 'unchanged_pre_existing_hard_flip_edges',
           'R1E explicitly distinguishes inherited hard flips.', 'HISTORICAL_VALIDATOR'),
    source('production_spec/stage5_production_rig/stage5b_r1e/scripts/s5b_r1e_build.py', 'len(NEW_FLIPS) == 0',
           'R1E applies new-flip no-regression plus local correction-domain/distal/collar checks, not a global erasure of historical debt.', 'HISTORICAL_VALIDATOR'),
    source('production_spec/stage5_production_rig/stage5b_r1e/scripts/s5b_r1e_build.py', 'if v > 1e-6',
           'R1E candidate construction prunes generated vectors; no global semantic-zero waiver.', 'HISTORICAL_GENERATOR'),
    source('audits/cap_skin_driver_and_weight_authority_reconciliation_r1/SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json', 'New conservative screening gates',
           '0.5/1.0 are new Human-review gates. They were not R1A/R1B global physical laws.', 'HASH_BOUND_CURRENT_AUTHORITY'),
    source('audits/cap_skin_driver_and_weight_authority_reconciliation_r1/SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json', 'existing bad baseline does not waive',
           'Current contract retains absolute screening on envelope/internal/crossing edges plus no worsening by >1e-5 unless recorded and qualified.', 'HASH_BOUND_CURRENT_AUTHORITY'),
    source('audits/cap_skin_driver_and_weight_authority_reconciliation_r1/SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json', 'every exceeding edge requires',
           'Absolute exceedance requires local smoothing or targeted deformation justification. This audit performs neither and grants no acceptance waiver.', 'HASH_BOUND_CURRENT_AUTHORITY'),
    source('audits/cap_skin_driver_and_weight_authority_reconciliation_r1/SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json', '"forbidden_weight": 0',
           'Current ownership guard uses exact mathematical zero for forbidden groups.', 'HASH_BOUND_CURRENT_AUTHORITY'),
    source('audits/cap_skin_driver_and_weight_authority_reconciliation_r1/R1B_SAFE_WEIGHT_REUSE_SET_R1.json', 'exact forbidden-group removal if retained',
           'The current reuse plan explicitly calls for removal of numerical remnants; significance bands are not semantic-zero authority.', 'HASH_BOUND_CURRENT_AUTHORITY'),
    source('audits/cap_skin_driver_and_weight_authority_reconciliation_r1/FIRST_WEB_SKIN_WEIGHT_WRAPPER_R2.json', 'All three interfaces contribute',
           'FIRST_WEB permits shared groups but requires all three interfaces to contribute continuity; side labels cannot waive an interface jump.', 'HASH_BOUND_CURRENT_AUTHORITY'),
    source('production_spec/stage5_production_rig/targeted_rig_and_skin_data_rebuild_after_approval_r1/AUTHORIZED_WEIGHT_WRITE_SET_R1.json', '244 set controls write permission',
           'Executed R1 scope makes the 771/2401 partitions copy-only. Future cleanup needs explicit amendment, not silent reinterpretation.', 'EXECUTED_SCOPE_CONTRACT'),
    source('production_spec/stage5_production_rig/targeted_rig_and_skin_data_rebuild_after_approval_r1/HUMAN_APPROVAL_RESPONSE_SOURCE_COPY.json', 'authority_scope',
           'Human approved deterministic rebuild plan only, not new candidate static/deformation acceptance.', 'HUMAN_APPROVAL'),
]

provenance = {
    'authority_id': 'CONTINUITY_GATE_PROVENANCE_R1', 'status': 'RESOLVED_MIXED_SCOPED_SCREEN_AND_NO_REGRESSION',
    'authority_precedence': ['Human hash-bound current proposal + Human notes', 'current exact-copy/write partition', 'historical validators as provenance, not overrides'],
    'proposal_bundle_hash': canonical_hash(bundle), 'Human_notes_preserved': approval['notes'],
    'sources': provenance_sources,
    'canonical_semantics': {
        'name': 'SCOPED_ABSOLUTE_SCREEN_PLUS_NO_REGRESSION_WITH_EXPLICIT_QUALIFICATION',
        'absolute_gates': {'L_inf': INF_GATE, 'L1': L1_GATE, 'scope': 'all approved envelope internal and crossing edges'},
        'regression_tolerance': TOL,
        'old_validators': 'Region-specific hard-flip removal plus no-new/no-worse checks; no provenance for global eradication of all donor discontinuity.',
        'current_gates': 'Retain 0.5/1.0 screening, record and qualify every affected exceedance; no increase in a preexisting seam >1e-5 unless explicitly recorded and qualified.',
        'copy_only_defects': 'INHERITED_BASELINE_DEFECT. Never candidate-introduced. Within an affected interface they still need recorded qualification before candidate acceptance; exact copy alone is not a PASS.',
        'semantic_boundaries': 'FIRST_WEB/R3/driver-family boundary is context, not an automatic continuity exemption.',
        'global_old_defect_clearance_contract_found': False,
        'no_new_no_worse_only_reinterpretation_authorized': False,
        'threshold_changes': [], 'acceptance_waivers_applied': [],
        'unresolved_provenance_conflicts': [],
    },
    'edge1130_verdict': 'Inherited exact-copy FIRST_WEB transition debt; unchanged, no candidate regression. It cannot justify a candidate-introduced rejection or a mandatory global cleanup. Its scoped absolute screen still exceeds gate and needs later explicit qualification. No static PASS is granted here.',
    'zero_semantics': {'canonical_forbidden_weight_epsilon': 0, 'normalization_tolerance': TOL,
                       'free_weight_prune_eps_R1A_R1B': 1e-8, 'generated_field_prune_R1C_R1D_R1E': 1e-6,
                       'runtime_cutoff': 'No project-authoritative runtime zero cutoff found in reviewed source chain; positive saved influences are retained/read/countable.',
                       'serialization': 'Saved float32 positive value is not exact zero. Float equality/normalization tolerances do not authorize foreign influence.'},
}
dump('CONTINUITY_GATE_PROVENANCE_R1.json', provenance)

CATEGORIES = ['PREEXISTING_COPY_ONLY', 'REBUILD_INTRODUCED', 'REBUILD_WORSENED',
              'REBUILD_IMPROVED_BUT_STILL_ABSOLUTE_FAIL', 'SEMANTIC_TRANSITION_EDGE', 'TRUE_SCOPE_CONFLICT']
records, mandatory = [], collections.defaultdict(list)
for prior in prior_static['blockers']:
    eid = prior['edge_id']
    i, j = EDGES[eid]
    before, after = metric(D[i], D[j]), metric(W[i], W[j])
    assert before == prior['before'] and after == prior['after'] and fails(after)
    copy_only = i not in WRITE and j not in WRITE
    assert not copy_only or (W[i] == D[i] and W[j] == D[j])
    delta_inf, delta_l1 = after['L_inf'] - before['L_inf'], after['L1'] - before['L1']
    if copy_only:
        temporal = 'PREEXISTING_COPY_ONLY'
    elif not fails(before):
        temporal = 'REBUILD_INTRODUCED'
    elif delta_inf > TOL or delta_l1 > TOL:
        temporal = 'REBUILD_WORSENED'
    elif delta_inf < 0 or delta_l1 < 0:
        temporal = 'REBUILD_IMPROVED_BUT_STILL_ABSOLUTE_FAIL'
    else:
        temporal = 'BASELINE_ABSOLUTE_FAIL_WITH_REBUILT_ENDPOINT_NO_MATERIAL_REGRESSION'
    boundaries = []
    if i in WEB or j in WEB:
        boundaries.append('FIRST_WEB_INTERFACE' if (i in WEB) != (j in WEB) else 'FIRST_WEB_INTERNAL')
    if i in LABEL and j in LABEL and LABEL[i] != LABEL[j]:
        boundaries.append('FRESH_R3_OWNERSHIP_BOUNDARY')
    if allowed(i) != allowed(j):
        boundaries.append('APPROVED_DRIVER_SUPPORT_BOUNDARY')
    witnesses = []
    for u, v in ((i, j), (j, i)):
        if u in WRITE and v not in WRITE:
            witness = support_witness(u, v, eid)
            if witness:
                witnesses.append(witness)
                mandatory[v].append(witness)
    if copy_only:
        primary, reason = 'PREEXISTING_COPY_ONLY', 'Both immutable endpoint vectors are exact R1B copies.'
    elif witnesses:
        primary, reason = 'TRUE_SCOPE_CONFLICT', 'Fixed-neighbor/forbidden-support lower bound exceeds approved absolute screening gate.'
    elif boundaries:
        primary, reason = 'SEMANTIC_TRANSITION_EDGE', 'Boundary requires its approved transition semantics; temporal defect classification remains explicit and no gate exemption is granted.'
    else:
        primary, reason = temporal, 'Ordinary same-support edge classified by donor/candidate comparison.'
    assert primary in CATEGORIES
    records.append({'edge_id': eid, 'vertex_ids': [i, j], 'primary_classification': primary,
                    'primary_reason': reason, 'temporal_classification': temporal,
                    'endpoints': [endpoint(i), endpoint(j)], 'donor_metrics': before, 'candidate_metrics': after,
                    'L_inf_delta': delta_inf, 'L1_delta': delta_l1,
                    'donor_absolute_fail': fails(before), 'candidate_absolute_fail': True,
                    'regression_over_existing_tolerance': delta_inf > TOL or delta_l1 > TOL,
                    'candidate_introduced_or_worsened': temporal in ('REBUILD_INTRODUCED', 'REBUILD_WORSENED'),
                    'semantic_boundary_tags': boundaries, 'boundary_exemption_granted': False,
                    'true_scope_conflict_witnesses': witnesses,
                    'baseline_attribution': 'INHERITED_BASELINE_DEFECT' if fails(before) else 'NO_DONOR_ABSOLUTE_DEFECT',
                    'candidate_acceptance': 'NOT_QUALIFIED_STATIC_EXCEEDANCE_RECORDED',
                    'absolute_limits': {'L_inf': INF_GATE, 'L1': L1_GATE}})

assert len(records) == 64 and len({r['edge_id'] for r in records}) == 64
counts = {name: sum(r['primary_classification'] == name for r in records) for name in CATEGORIES}
temporal_counts = dict(collections.Counter(r['temporal_classification'] for r in records))
classification = {'authority_id': 'STATIC_BLOCKER_CLASSIFICATION_R1', 'edge_count': 64,
                  'primary_counts_mutually_exclusive': counts,
                  'primary_precedence': ['PREEXISTING_COPY_ONLY', 'TRUE_SCOPE_CONFLICT', 'SEMANTIC_TRANSITION_EDGE', 'temporal classification'],
                  'precedence_reason': 'Copy-only attribution is decisive; mathematical scope impossibility then takes priority over descriptive boundary and causal tags. Preserve independent temporal tags so worsening/improvement are never hidden by category precedence.',
                  'temporal_counts_independent': temporal_counts, 'edges': records,
                  'thresholds_changed': False, 'weights_generated': 0, 'weights_written': 0}
dump('STATIC_BLOCKER_CLASSIFICATION_R1.json', classification)

residue_rows, residue_entries = [], []
for prior in prior_static['ownership_guard']['per_vertex']:
    i = prior['vertex_id']
    foreign = {g: v for g, v in W[i].items() if g not in allowed(i) and v > 0}
    assert foreign == prior['forbidden_groups'] and W[i] == D[i] and i not in WRITE
    entries = []
    for group, weight in sorted(foreign.items()):
        entry = {'vertex_id': i, 'group': group, 'weight': weight, 'classification': CL[i],
                 'historical_donor_value': D[i].get(group, 0), 'candidate_value': weight,
                 'exact_donor_copy': True, 'new_residue': False,
                 'existing_prune_zero_contract': {'current_forbidden_weight': 0, 'source': rel(AUTH_DIR / 'SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json'),
                                                'reuse_rule': reuse_contract['threshold_policy'],
                                                'historical_free_prune_1e_8_applies_to_this_retained_group': False,
                                                'historical_generated_field_prune_1e_6_is_zero_waiver': False},
                 'semantic_zero_verdict': 'TRUE_FORBIDDEN_RESIDUE_REQUIRING_WRITE',
                 'reason': 'Strict hash-bound side guard requires exact zero; current plan explicitly requires numerical remnant removal. Retained positive float is not made zero by a free-prune or reporting cutoff.'}
        entries.append(entry)
        residue_entries.append(entry)
    residue_rows.append({'vertex_id': i, 'classification': CL[i], 'frozen_R3_side': LABEL[i],
                         'semantic_zero_verdict': 'TRUE_FORBIDDEN_RESIDUE_REQUIRING_WRITE',
                         'historical_donor_vector': D[i], 'candidate_vector': W[i],
                         'forbidden_entries': entries, 'new_residue_count': 0,
                         'maximum_forbidden_weight': max(foreign.values()),
                         'total_forbidden_weight': sum(foreign.values()),
                         'allowed_groups': sorted(allowed(i)),
                         'incident_edge_ids': INCIDENT[i],
                         'cleanup_only_conservative_vertex_L1_change_bound': 2 * sum(foreign.values()) + abs(sum(W[i].values()) - 1)})
assert len(residue_rows) == 55
residue_ids = {r['vertex_id'] for r in residue_rows}
zero_audit = {'authority_id': 'FORBIDDEN_WEIGHT_ZERO_SEMANTICS_AUDIT_R1', 'status': 'RESOLVED_EXACT_ZERO_WRITE_PERMISSION_REQUIRED',
              'canonical_forbidden_weight_zero_epsilon': 0,
              'semantic_zero_counts_vertices': {'NUMERICAL_ZERO_BY_EXISTING_AUTHORITY': 0, 'TRUE_FORBIDDEN_RESIDUE_REQUIRING_WRITE': 55, 'UNRESOLVED': 0},
              'vertex_count': 55, 'group_entry_count': len(residue_entries),
              'classification_counts': dict(collections.Counter(r['classification'] for r in residue_rows)),
              'above_1e_8_vertex_count': sum(r['maximum_forbidden_weight'] > 1e-8 for r in residue_rows),
              'above_1e_6_vertex_count': sum(r['maximum_forbidden_weight'] > 1e-6 for r in residue_rows),
              'new_residue_count': 0, 'historical_residues_are_candidate_introduced': False,
              'authority_sources': [s for s in provenance_sources if any(word in s['meaning'].lower() for word in ('prun', 'zero', 'positive', 'remnant', 'foreign', 'normalization'))],
              'float32_serialization_is_not_a_zero_contract': True,
              'precedence_explanation': 'Historical reporting epsilons differ by region and version. Latest hash-bound guard and remnant-removal requirement explicitly demand exact zero. This is a resolvable scope conflict, not unresolved provenance.',
              'per_vertex': residue_rows, 'per_group_entry': residue_entries,
              'weights_written': 0, 'epsilon_changes': []}
dump('FORBIDDEN_WEIGHT_ZERO_SEMANTICS_AUDIT_R1.json', zero_audit)

by_edge = {r['edge_id']: r for r in records}
edge1234 = {'authority_id': 'EDGE1234_SCOPE_CONFLICT_R1', 'verdict': 'TRUE_SKIN_TRANSITION_DEFECT_AND_TRUE_SCOPE_CONFLICT',
            'edge': by_edge[1234],
            'legal_driver_family_boundary': True, 'boundary_legality_waives_discontinuity': False,
            'decision': 'Driver support changes here legally, but FIRST_WEB three-way continuity is mandatory. The new 1.0 THUMB_MCP jump is not a legally exempt boundary.',
            'proof': 'v338 outside FIRST_WEB is frozen R3 INDEX: THUMB_MCP_R=0. Copy-only FIRST_WEB v1448 has THUMB_MCP_R=1 exactly. Every legal 244-only solution has jump 1 >0.5, independent of solver or pose.',
            'minimum_additional_vertices_for_edge1234_alone': [1448],
            'minimum_additional_vertices_for_all_v338_incident_conflicts': [1447, 1448, 1550],
            'edge1234_target': {'v1448_THUMB_MCP_max': .5, 'joint_shared_support': ['WRIST_R', 'INDEX_MCP_R'],
                                'L_inf_max': INF_GATE, 'L1_max': L1_GATE,
                                'no_THUMB_groups_allowed_at_v338': True},
            'v338_one_ring': [ {'edge_id': e, 'vertex_ids': EDGES[e], 'endpoints': [endpoint(v) for v in EDGES[e]],
                                 'donor_metrics': metric(D[EDGES[e][0]], D[EDGES[e][1]]),
                                 'candidate_metrics': metric(W[EDGES[e][0]], W[EDGES[e][1]])} for e in INCIDENT[338]],
            'v1448_one_ring': [ {'edge_id': e, 'vertex_ids': EDGES[e], 'endpoints': [endpoint(v) for v in EDGES[e]],
                                 'donor_metrics': metric(D[EDGES[e][0]], D[EDGES[e][1]]),
                                 'candidate_metrics': metric(W[EDGES[e][0]], W[EDGES[e][1]])} for e in INCIDENT[1448]],
            'v1550_required_by_independent_edge1438_same_fixed_one_hot_conflict': True,
            'v296_role': 'Additional global amendment witness edge1440 requires v296; it is not added merely for being a neighbor of v1448.',
            'v3162_role': 'Retained pin. Its inherited edge6028 is debt; no evidence here requires its write permission.',
            'FIRST_WEB21_automatic_rebuild': False, 'poses_used_for_decision': 0, 'applied': False}
dump('EDGE1234_SCOPE_CONFLICT_R1.json', edge1234)

additional = sorted(residue_ids | set(mandatory))
assert len(mandatory) == 18 and len(additional) == 73 and not residue_ids.intersection(mandatory)
proposal_rows = []
for i in additional:
    cleanup_only = i in residue_ids
    witnesses = mandatory.get(i, [])
    forbidden = sorted(set(contract['deform_bones']) - allowed(i)) + contract['helpers']['names']
    proposal_rows.append({'vertex_id': i, 'original_classification': CL[i], 'frozen_R3_side': LABEL[i], 'FIRST_WEB21': i in WEB,
                          'operation': 'EXACT_FORBIDDEN_ENTRY_REMOVAL_AND_NORMALIZATION_ONLY' if cleanup_only else 'LOCAL_CONTINUOUS_RECONSTRUCTION_WITH_APPROVED_SUPPORT',
                          'why_must_change': 'Positive forbidden donor residue must become exact zero; no other vertex edit can remove this entry.' if cleanup_only else 'Neighbor support lower bound makes an incident absolute gate impossible while this vertex remains an exact copy.',
                          'related_blocker_edges': sorted({x['edge_id'] for x in witnesses}),
                          'all_incident_edges_for_static_revalidation': INCIDENT[i],
                          'allowed_groups': sorted(allowed(i)), 'forbidden_groups': forbidden,
                          'existing_candidate_vector': W[i], 'historical_donor_vector': D[i],
                          'continuity_target': {'L_inf_max': INF_GATE, 'L1_max': L1_GATE,
                                                'preexisting_seam_no_regression_tolerance': TOL,
                                                'existing_qualification_path': 'Any surviving inherited scoped exceedance needs an explicit record/qualification; not an automatic pass.',
                                                'new_defects': 'No new unqualified crossing jump or hard driver swap.'},
                          'additional_restrictions': 'Preserve relative ratios among retained allowed components; normalization only, no smoothing or new driver components.' if cleanup_only else 'Use already approved side/wrapper support; no new anatomy/ownership/driver-family permission.',
                          'minimality_witnesses': witnesses if witnesses else [ {'vertex_id': i, 'forbidden_entries': {g: value for g, value in W[i].items() if g not in allowed(i)}, 'required_value': 0} ]})

proposal = {'authority_id': 'SKIN_WRITE_SCOPE_AMENDMENT_R2_PROPOSAL', 'status': 'PENDING_HUMAN_APPROVAL_NOT_APPLIED',
            'proposal_type': 'MINIMAL_MANDATORY_ADDITIONAL_WRITE_PERMISSIONS', 'new_vertex_count': len(additional), 'new_vertex_ids': additional,
            'continuity_reconstruction_vertex_count': len(mandatory), 'continuity_reconstruction_vertex_ids': sorted(mandatory),
            'zero_cleanup_only_vertex_count': len(residue_ids), 'zero_cleanup_only_vertex_ids': sorted(residue_ids),
            'original_classification_counts': dict(collections.Counter(CL[i] for i in additional)),
            'FIRST_WEB_additional_count': len(WEB.intersection(additional)), 'FIRST_WEB_additional_ids': sorted(WEB.intersection(additional)),
            'FIRST_WEB_kept_copy_only_ids': sorted(WEB - WRITE - set(additional)),
            'existing_244_write_ids': sorted(WRITE), 'proposed_total_write_count': len(WRITE) + len(additional),
            'minimality': {'method': 'Independent compulsory-vertex witnesses, not neighborhood smoothing.',
                           'lower_bound': len(additional),
                           'proof': 'Every one of the 55 residue vertices must itself change to achieve exact zero. Each of the 18 disjoint continuity vertices is the immutable endpoint of a support-incompatibility witness whose lower bound already exceeds 0.5/1.0 even if all existing244 are free. Omitting any listed point preserves its witness. No unproved closure vertices are added.',
                           'minimality_scope': 'Necessary additional permissions for strict zero and the unqualified absolute support conflicts among the specified64 blockers; not proof of a unique future weight field.',
                           'neighborhood_closure_vertices_without_witness': [],
                           'sufficiency_claim': 'No claim that a future generated R2 automatically passes. Existing244 must also repair their introduced defects; all incident/outer seams, max4, normalization, geometry and targeted validation still apply. Any later proven new conflict needs another explicit approval, never automatic expansion.',
                           'solver_runs': 0, 'hypothetical_weight_vectors_generated': 0},
            'per_vertex': proposal_rows, 'canonical_zero_epsilon': 0, 'gate_changes': [],
            'candidate_R1_remains_immutable': {'path': rel(CANDIDATE), 'sha256': EXPECTED},
            'authority_changes': 'Only listed additional write permissions. Existing approved groups/ownership/membership and thresholds unchanged. Cleanup55 is restricted to exact removal plus normalization.',
            'R2_generation_authorized_now': False, 'Human_approval_required_before_apply': True,
            'target_after_approval': 'TARGETED_RIG_AND_SKIN_DATA_REBUILD_R2',
            'deformation_or_Stage6_permission_requested': False, 'applied': False}
dump('SKIN_WRITE_SCOPE_AMENDMENT_R2_PROPOSAL.json', proposal)
proposal_hash = sha(OUT / 'SKIN_WRITE_SCOPE_AMENDMENT_R2_PROPOSAL.json')

baseline_debt = [r for r in records if r['donor_absolute_fail']]
introduced = [r for r in records if r['candidate_introduced_or_worsened']]
all_baseline_failures = [r for r in prior_static['all_checked_edges'] if fails(r['before'])]
resolved_baseline = [r['edge_id'] for r in all_baseline_failures if not fails(r['after'])]
diagnostic_increases = [r for r in prior_static['regression_increase_edges'] if r['edge_id'] not in by_edge]
dump('INHERITED_DONOR_STATIC_DEBT_R1.json', {
    'authority_id': 'INHERITED_DONOR_STATIC_DEBT_R1', 'attribution': 'DONOR_BASELINE_ONLY_NOT_R1_INTRODUCTION',
    'count_unit': 'debt records: edge baseline manifestations + forbidden-residue vertices',
    'remaining_debt_record_count': len(baseline_debt) + len(residue_rows), 'continuity_edge_count': len(baseline_debt),
    'exact_copy_only_continuity_count': counts['PREEXISTING_COPY_ONLY'], 'forbidden_residue_vertex_count': 55,
    'baseline_absolute_failure_count_all_2089_checked_edges': len(all_baseline_failures),
    'baseline_edges_resolved_by_candidate_count': len(resolved_baseline), 'baseline_edges_resolved_by_candidate_ids': resolved_baseline,
    'edge_records': [ {'record_id': f"DONOR_EDGE_{r['edge_id']}", 'edge_id': r['edge_id'], 'vertex_ids': r['vertex_ids'],
                      'donor_metrics': r['donor_metrics'], 'candidate_metrics': r['candidate_metrics'],
                      'exact_copy_only': r['primary_classification'] == 'PREEXISTING_COPY_ONLY',
                      'candidate_delta_also_has_separate_defect_record': r['candidate_introduced_or_worsened'],
                      'temporal_classification': r['temporal_classification']} for r in baseline_debt ],
    'residue_records': [ {'record_id': f"DONOR_RESIDUE_VERTEX_{r['vertex_id']}", **r} for r in residue_rows ],
    'candidate_delta_overlap_edge_ids': [r['edge_id'] for r in baseline_debt if r['candidate_introduced_or_worsened']],
    'overlap_explanation': 'A historical defect and an additional worsening at the same edge are distinct causal records, not double-attribution of an unchanged defect.',
    'debt_is_waived': False, 'deformation_qualification': 'Future targeted harness must report baseline and R2 delta separately.'})
dump('CANDIDATE_INTRODUCED_STATIC_DEFECT_R1.json', {
    'authority_id': 'CANDIDATE_INTRODUCED_STATIC_DEFECT_R1', 'count_scope': 'absolute blockers among the requested64 edges',
    'candidate_introduced_or_worsened_blocker_count': len(introduced),
    'new_absolute_blocker_count': temporal_counts['REBUILD_INTRODUCED'], 'worsened_baseline_blocker_count': temporal_counts['REBUILD_WORSENED'],
    'records': [ {'record_id': f"CANDIDATE_DELTA_EDGE_{r['edge_id']}", **r} for r in introduced ],
    'new_forbidden_residue_count': 0,
    'all_checked_edges_increase_over_1e_5_count': len(prior_static['regression_increase_edges']),
    'subthreshold_increase_diagnostic_count': len(diagnostic_increases),
    'subthreshold_increase_diagnostics': diagnostic_increases,
    'diagnostic_policy': 'Do not hide the234 subthreshold increases. An increase is not automatically a new absolute blocker. Preexisting seam increases require the current contract recorded/qualified treatment; R2 must compare these records. No qualification granted here.',
    'candidate_R1_static_pass': False, 'scope_expansion_alone_proves_future_pass': False})

status = {'phase': PHASE, 'verdict': 'STATIC_CONTRACT_RECONCILED_SCOPE_AMENDMENT_REQUIRED',
          'blocker_primary_counts': counts, 'blocker_temporal_counts': temporal_counts,
          'edge1130_verdict': 'INHERITED_BASELINE_DEFECT_EXACT_COPY_NOT_CANDIDATE_INTRODUCED_STILL_REQUIRES_SCOPED_QUALIFICATION',
          'edge1234_verdict': edge1234['verdict'],
          'residue_counts': zero_audit['semantic_zero_counts_vertices'], 'canonical_zero_epsilon': 0,
          'continuity_gate_canonical_semantics': provenance['canonical_semantics']['name'],
          'candidate_introduced_blocker_count': len(introduced), 'inherited_donor_debt_count': len(baseline_debt) + 55,
          'inherited_donor_debt_count_units': {'remaining_continuity_edges': len(baseline_debt), 'residue_vertices': 55},
          'baseline_candidate_worsening_overlap_edge_ids': [r['edge_id'] for r in baseline_debt if r['candidate_introduced_or_worsened']],
          'scope_expansion_required': True, 'additional_write_vertex_count': len(additional), 'additional_write_ids': additional,
          'additional_write_breakdown': {'continuity': 18, 'residue_cleanup_only': 55},
          'candidate_blend_sha256_before': EXPECTED, 'candidate_blend_sha256_after': sha(CANDIDATE),
          'candidate_blend_hash_unchanged': sha(CANDIDATE) == EXPECTED,
          'weights_generated': 0, 'weights_written': 0, 'candidate_blend_writes': 0, 'R2_candidate_created': False,
          'deformation_runs': 0, 'pose_evaluations': 0, 'Stage6_runs': 0, 'anatomy_research_runs': 0, 'R3_reruns': 0,
          'gate_threshold_changes': 0, 'authority_waivers': 0, 'prior_successes_reopened': False,
          'NEXT': 'HUMAN_SKIN_STATIC_GATE_AND_SCOPE_AMENDMENT_APPROVAL', 'STOP': True,
          'after_Human_approval_only': 'TARGETED_RIG_AND_SKIN_DATA_REBUILD_R2',
          'proposal_sha256': proposal_hash, 'review_id': 'SKIN_STATIC_GATE_AND_SCOPE_AMENDMENT_HUMAN_REVIEW_R1',
          'Human_approval_received': False}
assert status['candidate_blend_hash_unchanged']

questions = [
    ('Q1', '是否接受区分 inherited donor debt 与 candidate-introduced defect？', '保留27条仍存在的 baseline edge debt（其中20条copy-only）、55点历史residue；37条新增和3条恶化作为独立candidate delta。3条edge同时有历史缺陷与本轮恶化，各自原因分开记录。'),
    ('Q2', '是否接受 continuity gate 按恢复出的正式语义执行？', '保留 affected envelope 的L∞≤0.5、L1≤1筛查及preexisting seam不恶化>1e-5的规则。跨FIRST_WEB/R3不自动豁免；历史受影响exceedance需明确记录和后续qualification，本轮不判PASS。'),
    ('Q3', '是否接受正式 zero 定义？', '当前hash-bound forbidden-weight epsilon=0（exact zero）。历史1e-8 free-prune、1e-6生成/prune和reporting cutoff不等于零权重豁免。55点只获精确清除forbidden项和归一化权限。'),
    ('Q4', '是否接受 minimal additional write set？', '精确73个新增顶点：18点连续性修复、55点仅清除残留；下表逐点给出必要性。FIRST_WEB仅增加13点，剩余7个copy-only点保留；不自动扩大邻域。'),
    ('Q5', '是否批准生成 TARGETED_SKIN_REBUILD_R2 candidate？', '仅在明确审批后，由原244点加本提案73点生成单独R2 candidate；不覆盖R1。R2仍需完整静态验证。此审批不包含deformation、Stage6、anatomy或production promotion。'),
]
html_rows = ''.join(f'<tr><td>v{x["vertex_id"]}</td><td>{x["original_classification"]}</td><td>{"残留清除与归一化" if x["vertex_id"] in residue_ids else "连续性修复"}</td><td>{", ".join(map(str,x["related_blocker_edges"])) or "精确非零 forbidden 项"}</td><td>{html.escape(", ".join(x["allowed_groups"]))}</td></tr>' for x in proposal_rows)
edge_rows = ''.join(f'<tr><td>{x["edge_id"]}</td><td>{" / ".join(map(str,x["vertex_ids"]))}</td><td>{x["primary_classification"]}</td><td>{x["temporal_classification"]}</td><td>{x["donor_metrics"]["L_inf"]:.9g} / {x["donor_metrics"]["L1"]:.9g}</td><td>{x["candidate_metrics"]["L_inf"]:.9g} / {x["candidate_metrics"]["L1"]:.9g}</td></tr>' for x in records)
qhtml = ''.join(f'<fieldset><legend>{key} · {html.escape(title)}</legend><p>{html.escape(description)}</p><label><input type="radio" name="{key}" value="YES" required> 接受</label><label><input type="radio" name="{key}" value="NO" required> 不接受</label></fieldset>' for key, title, description in questions)
review = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Skin static gate & scope amendment · R1</title>
<style>body{margin:0;background:#f3f5f7;color:#162331;font:15px/1.7 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1150px;margin:auto;padding:34px 24px 70px}h1{font-size:28px;line-height:1.35}h2{font-size:20px;margin-top:32px}.card,fieldset{background:white;border:1px solid #d3dce4;border-radius:10px;padding:18px 22px;margin:16px 0}legend{font-weight:650;padding:0 7px}.state{color:#915811;font-weight:650}.metrics{display:flex;gap:12px;flex-wrap:wrap}.metric{background:#e8eff4;padding:12px 20px;border-radius:8px}.metric b{font-size:25px;display:block}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:12px;background:white}th,td{padding:9px;border:1px solid #dce2e8;text-align:left;vertical-align:top}th{background:#e9eff4}code{overflow-wrap:anywhere}label{margin-right:24px}button{border:0;border-radius:7px;background:#17465d;color:white;padding:13px 22px;font-size:15px;cursor:pointer}button:disabled{background:#84949e;cursor:not-allowed}textarea{width:100%;min-height:85px;box-sizing:border-box}a{color:#146089}details{margin:20px 0}summary{cursor:pointer;font-weight:650}.small{font-size:13px;color:#475765}</style>
<main><p class="state">PENDING HUMAN APPROVAL · 提案未应用</p><h1>Skin 静态 gate 语义与最小写权限修订</h1><p>本次完成只读静态审计。R1 candidate 保持不可变；需要Human明确审批后才能生成单独的R2。</p>
<div class="metrics"><div class="metric"><b>64</b>逐条分类 edges</div><div class="metric"><b>40</b>新增37 / 恶化3</div><div class="metric"><b>73</b>新增写权限：18 + 55</div><div class="metric"><b>0</b>权重写入 / deformation / Stage6</div></div>
<section class="card"><h2>恢复出的 authority</h2><p>Continuity 是局部绝对筛查与不恶化规则并用。没有全局清零旧 donor 缺陷的contract；也没有将新0.5/1.0筛查改为纯no-regression的权限。FIRST_WEB三方连续性仍是要求，合法driver boundary不自动豁免。</p><p>edge1130两端exact-copy，是inherited donor debt。它的绝对screen仍fail，必须记录并在后续资格验证中明确裁决；本轮不授予PASS。edge1234为新skin-transition defect：v338禁止THUMB_MCP，v1448却固定为1，因此244-only数学上无法修复。</p><p>Canonical forbidden weight zero = <b>0，exact mathematical zero</b>。55点均为历史值、新增residue=0，但最新authority要求清除；构建prune阈值不能替代此定义。</p><p>73点是每点有必要性证明的最小新增权限集合，不承诺未来R2权重自动通过。R2还必须修复原244内缺陷、复核所有新外边界和234条低于绝对gate但增加的诊断边；任何额外冲突都需新审批。</p></section>
<section class="card"><p>Candidate SHA256：<code>__CANDIDATE_HASH__</code></p><p>Proposal SHA256：<code>__PROPOSAL_HASH__</code></p><p><a href="SKIN_STATIC_GATE_SEMANTICS_AND_SCOPE_RECONCILIATION_R1_REPORT.md">完整报告</a> · <a href="SKIN_WRITE_SCOPE_AMENDMENT_R2_PROPOSAL.json">精确提案JSON</a> · <a href="STATIC_BLOCKER_CLASSIFICATION_R1.json">64条详细edge证据</a> · <a href="FORBIDDEN_WEIGHT_ZERO_SEMANTICS_AUDIT_R1.json">55点逐项zero审计</a> · <a href="CONTINUITY_GATE_PROVENANCE_R1.json">provenance与行号</a></p></section>
<h2>Human 只审批以下5项</h2><form id="approval">__QUESTIONS__<label>审批备注<textarea id="notes"></textarea></label><p><button id="download" disabled>下载审批响应 JSON</button></p><p class="small">所有项无默认答案。下载只保存Human响应，不执行solver或写入任何blend；响应仍需交回项目并验证精确proposal hash。</p><p id="result" role="status"></p></form>
<details><summary>73个新增顶点 · 权限与必要性</summary><div class="scroll"><table><thead><tr><th>Vertex</th><th>原分类</th><th>允许操作</th><th>冲突edges / 必要性</th><th>已批准groups</th></tr></thead><tbody>__VERTICES__</tbody></table></div></details>
<details><summary>64条blocker · 主分类与独立因果分类</summary><p>主分类按copy-only→数学scope conflict→semantic transition→时间因果优先。独立时间因果统计：37 introduced、3 worsened、2 improved、2 rebuilt但无实质恶化、20 copy-only。</p><div class="scroll"><table><thead><tr><th>Edge</th><th>Endpoints</th><th>主分类</th><th>时间因果</th><th>Donor L∞ / L1</th><th>Candidate L∞ / L1</th></tr></thead><tbody>__EDGES__</tbody></table></div></details>
<p class="state">NEXT = HUMAN_SKIN_STATIC_GATE_AND_SCOPE_AMENDMENT_APPROVAL · STOP</p></main>
<script>const form=document.getElementById('approval');const keys=['Q1','Q2','Q3','Q4','Q5'];const btn=document.getElementById('download');form.addEventListener('change',()=>{btn.disabled=!keys.every(k=>form.querySelector('input[name="'+k+'"]:checked'))});form.addEventListener('submit',e=>{e.preventDefault();if(!form.reportValidity())return;const answers=Object.fromEntries(keys.map(k=>[k,form.querySelector('input[name="'+k+'"]:checked').value]));const accepted=keys.every(k=>answers[k]==='YES');const response={review_id:'SKIN_STATIC_GATE_AND_SCOPE_AMENDMENT_HUMAN_REVIEW_R1',phase:'HUMAN_SKIN_STATIC_GATE_AND_SCOPE_AMENDMENT_APPROVAL',proposal_sha256:'__PROPOSAL_HASH__',candidate_R1_sha256:'__CANDIDATE_HASH__',...answers,notes:document.getElementById('notes').value,timestamp:new Date().toISOString(),all_questions_answered:true,all_accepted:accepted,automatic_apply:false,Stage6_approved:false,deformation_approved:false,production_promotion_approved:false,response_kind:'HUMAN_STATIC_GATE_SCOPE_AMENDMENT_RESPONSE',authorized_next_phase:accepted?'TARGETED_RIG_AND_SKIN_DATA_REBUILD_R2':null};const blob=new Blob([JSON.stringify(response,null,2)+String.fromCharCode(10)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='SKIN_STATIC_GATE_AND_SCOPE_AMENDMENT_HUMAN_REVIEW_R1_RESPONSE_'+response.timestamp.replaceAll(':','-')+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);document.getElementById('result').textContent='审批响应已下载。未自动应用任何更改。'});</script></html>'''
review = review.replace('__QUESTIONS__', qhtml).replace('__VERTICES__', html_rows).replace('__EDGES__', edge_rows).replace('__CANDIDATE_HASH__', EXPECTED).replace('__PROPOSAL_HASH__', proposal_hash)
(OUT / 'SKIN_STATIC_GATE_AND_SCOPE_AMENDMENT_HUMAN_REVIEW.html').write_text(review, encoding='utf-8')

table = '\n'.join(f'| {name} | {counts[name]} |' for name in CATEGORIES)
report = f'''# {PHASE}

Verdict: **{status['verdict']}**. NEXT: **{status['NEXT']}**. STOP.

本轮仅读取既有hash绑定证据并生成审计报告和Human Review。candidate没有修改；没有权重生成、权重写入、pose、deformation、R3重算或Stage6。上一轮已确认成功的244评估/238变化、2401/771 exact-copy、cap37/oldcap9/FIRST_WEB/edge5879和save/reopen结果保持，不重新裁决。

## 64条blocker分类

主分类互斥，按copy-only→可证明scope conflict→semantic boundary→普通同域时间因果优先。

| 分类 | 数量 |
| --- | ---: |
{table}

独立时间因果标签保留真实变化：**37 introduced，3 worsened，2 improved-but-fail，2 rebuilt endpoint但无实质恶化，20 exact copy-only**。主分类中worsened/improved为0是优先级归入scope conflict，不表示不存在恶化或改善。64条edge ID、两端原分类/side/支持、donor/candidate完整向量与逐group L∞/L1均在`STATIC_BLOCKER_CLASSIFICATION_R1.json`。

## Gate provenance与恢复后的语义

当前proposal bundle canonical hash `{canonical_hash(bundle)}` 与Human响应匹配，所有组件hash及上一轮38个证据文件manifest匹配；不是把旧生产validator的阈值移植成新authority。

R1A/R1B：归一化容差由R1A的1e-6演进到R1B/当前1e-5；free-prune EPS=1e-8，冻结foreign组甚至低于EPS也保持原值。R1A跨digit审计报告忽略≤1e-6，但同时对有意义的历史残留独立记录。R1C：仅授权修复区生成向量prune>1e-6，修复点foreign group存活即失败。R1D：distal域hard-flip必须清零，global hard-flip count不得增加。R1E：NEW hard-flip不增加，局部distal/collar/correction-domain有额外要求，明确记录unchanged preexisting hard-flips。其hard-flip谓词为双向≥0.95/≤0.05，不能当成后来L∞0.5/L1 1的同一个gate。

最新hash绑定`SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json`明确称0.5/1.0为**new conservative screening gates**，覆盖envelope内部与crossing edges；同时要求preexisting seam不恶化超过R1B+1e-5（除非明确记录并qualified），并明确“existing bad baseline does not waive new absolute gates”。每个受影响exceedance需要local smoothing或targeted deformation justification。故canonical语义是 **SCOPED_ABSOLUTE_SCREEN_PLUS_NO_REGRESSION_WITH_EXPLICIT_QUALIFICATION**，既不是全局physical absolute law，也不是纯no-regression。

没有任何恢复出的正式contract要求全局清零所有donor旧defect。copy-only edge必须记为inherited baseline defect，不能归因于本轮制造；若在受影响interface中仍超过screen，其后续qualification义务仍存在。此审计没有waive gate、没有判candidate PASS、没有批准deformation。所有来源的文件hash、准确行号和原文摘录在`CONTINUITY_GATE_PROVENANCE_R1.json`。

## edge1130

v303/v1396均TARGETED_REVALIDATION且exact donor copy。Donor=candidate：L∞=0.655587911605835、L1=1.31117582321167。结论为 **INHERITED_BASELINE_DEFECT**，新增/恶化为0；244-only当然无法改变它。它不是candidate-introduced blocker，也不构成强制全局旧defect清零权限。其FIRST_WEB受影响interface的绝对screen仍fail，后续必须明确记录并qualify，不因exact-copy自动PASS。

## edge1234

合法driver-family边界，**同时存在真实skin-transition defect与scope conflict**；合法边界不豁免FIRST_WEB三方连续性。v338是非web INDEX支持，THUMB_MCP必须精确0；v1448是copy-only web，THUMB_MCP=1。每个合法244-only解都有jump=1。Donor L∞={by_edge[1234]['donor_metrics']['L_inf']}、L1={by_edge[1234]['donor_metrics']['L1']}，candidate为1 / {by_edge[1234]['candidate_metrics']['L1']}。

单独edge1234最小必须开放v1448；v338还有edge1438(v1550固定THUMB_MCP=1)和edge1233(v1447不兼容THUMB总量0.8405)，联合one-ring冲突最低需要 **[1447,1448,1550]**。v1525已经属于244 write set。v296通过独立edge1440证明必须开放，不是因为邻接就加入；v3162保持copy-only inherited debt pin。逐条one-ring证据保留在`EDGE1234_SCOPE_CONFLICT_R1.json`。没有依据pose或anatomy作出决定。

## 55点semantic-zero

分类：numerical-zero=0，true forbidden=55，unresolved=0。34 TARGETED_REVALIDATION / 21 SAFE_REUSE；23点>1e-8，0点>1e-6，全部exact donor copy、新增residue=0。

**Canonical forbidden zero epsilon=0（exact mathematical zero）**；1e-5只适用于归一化与明确的比较容差，1e-8/1e-6分别是版本/区域限定的构建prune与reporting意义阈值。特别是当前hash-bound reuse plan明写“numerical remnants require targeted revalidation and exact forbidden-group removal if retained”；这直接排除将55点历史微量当成合法零的解释。没有项目authority允许用runtime cutoff或float32 serialization把正值视为0。历史检查不同不构成无法解决的provenance冲突，最新具体guard优先。

每点group/正值、原分类、donor/candidate数值、正式规则和verdict均记录在`FORBIDDEN_WEIGHT_ZERO_SEMANTICS_AUDIT_R1.json`。它们是历史债务，同时因严格新guard与本次copy-only权限冲突而需要显式清除权限。

## 最小新增write权限

**73点**：18点continuity修复 + 55点仅exact forbidden entry removal/normalization，两个子集不重叠。

18 continuity IDs：`{sorted(mandatory)}`。

55 cleanup-only IDs：`{sorted(residue_ids)}`。

每个18点都拥有独立lower-bound证书：固定邻点中不被write端允许的group，不能通过修改现有244消除。令F=固定端forbidden总量，A=其allowed总量，则 min L∞≥最大forbidden component；min L1≥F+max(0,1−1e-5−A)。这里已考虑正常容差，忽略max4等附加约束只会给solver更多自由，仍无法通过。32条edge具此证据。每个55点有独立非零entry，必须该点本身改变才能达exact0。故任何更小集合都会漏掉至少一个compulsory witness；没有加入无证据的smoothing-neighborhood点。

该**最小必要权限集合**不是R2权重充分性/唯一解证明。原244仍需修复自己的新增缺陷；R2生成后必须检查所有 incident/crossing seams、支持与归一化。若后续静态构建暴露新的必需权限，须单独提交证据和审批，不得自动扩圈。

FIRST_WEB仅新增{len(WEB.intersection(additional))}点，保留copy-only `{sorted(WEB-WRITE-set(additional))}`（另外v3125已经获原write权限）。总潜在write权限317；55点并不获自由smoothing权限。原分类21 SAFE_REUSE +52 TARGETED_REVALIDATION。逐点operation、允许/禁止groups、必要性、关联edge与continuity target在`SKIN_WRITE_SCOPE_AMENDMENT_R2_PROPOSAL.json`，sha256 `{proposal_hash}`。

## Donor debt与candidate defect

在2089条既有checked edges中，R1B原有100条绝对fail；candidate已使73条通过，仍存在27条baseline edge manifestation，其中20条copy-only。剩余donor debt为**82记录=27 edge baseline+55 residue vertices**。3条baseline edge还被candidate恶化：[2206,4773,5797]；同edge上的历史缺陷与新增恶化使用不同record ID分开归因。

candidate introduced/worsened绝对blocker为**40=37新增+3恶化**，不包含55点copied residue。274条edge超过1e-5的增加完整保存；其中234条未超过absolute gate，作为preexisting-seam记录/qualification与R2比较诊断，不能隐藏，也不能不加区分地等同于新增absolute blocker。本轮没有qualification waiver。

## Human审批与停止

`SKIN_STATIC_GATE_AND_SCOPE_AMENDMENT_HUMAN_REVIEW.html`仅包含Q1 donor/candidate区分、Q2正式continuity语义、Q3正式zero定义、Q4精确新增73点权限、Q5生成独立R2。所有问题无默认答案，响应绑定精确proposal/R1 hash；HTML仅下载响应，不自动执行任何变更。没有anatomy审批。

Candidate SHA256 before/after：`{EXPECTED}`，unchanged=YES。weights written=0，deformation runs=0，Stage6 runs=0。

NEXT = **HUMAN_SKIN_STATIC_GATE_AND_SCOPE_AMENDMENT_APPROVAL**。只有Human批准后才允许 **TARGETED_RIG_AND_SKIN_DATA_REBUILD_R2**。STOP。
'''
(OUT / (PHASE + '_REPORT.md')).write_text(report, encoding='utf-8')

# Consumed files, including candidate, donor, approval and all prior round evidence are immutable.
drifts = [path for path, digest in CONSUMED.items() if sha(ROOT / path) != digest]
assert not drifts, drifts
status['consumed_source_drift_count'] = len(drifts)
dump(PHASE + '_STATUS.json', status)
dump('READ_ONLY_INPUT_AND_OUTPUT_VERIFICATION_R1.json', {
    'status': 'PASS', 'candidate_hash_unchanged': sha(CANDIDATE) == EXPECTED,
    'prior_round_evidence_manifest_file_count': len(previous_manifest['files']),
    'Human_proposal_components_verified': len(bundle['proposal_files']),
    'consumed_inputs': CONSUMED, 'input_drift_count': 0,
    '64_edge_metrics_match_saved_prior_evidence': True, 'all55_residue_values_match_exact_donor': True,
    '73_additional_vertices_have_independent_compulsory_witnesses': True,
    'weights_written': 0, 'blend_writes': 0, 'deformation_runs': 0, 'Stage6_runs': 0,
    'STOP': True})
outputs = {p.name: sha(p) for p in OUT.iterdir() if p.is_file() and p.name != 'OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json'}
dump('OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json', {'files': outputs, 'canonical_files_hash': canonical_hash(outputs), 'excludes_self': True})
print(json.dumps(status, ensure_ascii=False, indent=2))
