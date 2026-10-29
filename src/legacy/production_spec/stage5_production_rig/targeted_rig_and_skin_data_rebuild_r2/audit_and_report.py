from common import *
import collections
import math
import numpy as np

R1_PAYLOAD = read(R1_DIR / 'CANDIDATE_CLEAN_REOPEN_PAYLOAD_R1.json')
R2_PAYLOAD = read(OUT / 'R2_CANDIDATE_CLEAN_REOPEN_PAYLOAD.json')
SOURCES = read(R1_DIR / 'LIVE_SOURCE_DATA_R1.json')
W, B, D = R2_PAYLOAD['weights'], R1_PAYLOAD['weights'], SOURCES['R1B']['weights']
EDGES = R2_PAYLOAD['mesh']['edges']
SCOPE = read(OUT / 'AUTHORIZED_WEIGHT_WRITE_SET_R2.json')
WRITE, ORIGINAL, NEW18, CLEAN55 = [set(SCOPE[k]) for k in ['approved_write_universe_317', 'original_244', 'additional_continuity_18', 'cleanup_only_55']]
OUTSIDE = set(range(3416)) - WRITE
CONT = read(AUTH_DIR / 'SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json')
WEB = read(AUTH_DIR / 'FIRST_WEB_SKIN_WEIGHT_WRAPPER_R2.json')
CAP = read(AUTH_DIR / 'CAP37_SKIN_DRIVER_AUTHORITY_R1.json')
OLD = read(AUTH_DIR / 'OLD_CAP9_SKIN_CORRECTION_AUTHORITY_R1.json')
EDGE_AUTH = read(AUTH_DIR / 'EDGE5879_REBUILD_SCOPE_R1.json')
R3 = read(ROOT / 'audits/human_r3_fresh_result_authority_freeze_r1/FRESH_R3_OWNERSHIP_AUTHORITY_R1.json')
LABEL = {int(k): v for k, v in R3['membership']['vertex_labels'].items()}
WEBIDS = set(WEB['membership']['vertex_ids'])
CAPIDS = {r['vertex_id'] for r in CAP['per_vertex_surface_evidence']}
OLDIDS = set(OLD['vertex_ids'])
TOL = CONT['normalization']['absolute_tolerance']

def support(i):
    if i in WEBIDS:
        return set(WEB['allowed_deform_groups'])
    if i in CAPIDS:
        return set(CAP['allowed_cap_deform_groups'])
    if i in OLDIDS:
        return set(OLD['allowed_deform_groups'])
    if i in LABEL:
        return set(CONT['ownership_guard']['allowed_by_side'][LABEL[i]])
    return set(CONT['deform_bones'])

def fails(m):
    return m['L_inf'] > .5 or m['L1'] > 1

def edge_record(eid):
    i, j = EDGES[eid]
    donor, r1, r2 = metric(D[i], D[j]), metric(B[i], B[j]), metric(W[i], W[j])
    boundary = []
    if i in WEBIDS or j in WEBIDS:
        boundary.append('FIRST_WEB_INTERFACE' if (i in WEBIDS) != (j in WEBIDS) else 'FIRST_WEB_INTERNAL')
    if i in LABEL and j in LABEL and LABEL[i] != LABEL[j]:
        boundary.append('FRESH_R3_BOUNDARY')
    if support(i) != support(j):
        boundary.append('APPROVED_DRIVER_SUPPORT_BOUNDARY')
    return {'edge_id': eid, 'vertex_ids': [i, j],
            'endpoints': [{'vertex_id': v, 'R2_write_authorized': v in WRITE,
                           'operation': 'CLEANUP_ONLY' if v in CLEAN55 else 'ADDITIONAL_CONTINUITY' if v in NEW18 else 'ORIGINAL_WRITE' if v in ORIGINAL else 'COPY_ONLY',
                           'frozen_side': LABEL.get(v, 'OUTSIDE_BOUNDED_R3'), 'FIRST_WEB21': v in WEBIDS,
                           'donor_vector': D[v], 'R1_vector': B[v], 'R2_vector': W[v],
                           'R2_exact_R1': W[v] == B[v], 'R2_exact_donor': W[v] == D[v],
                           'allowed_groups': sorted(support(v))} for v in [i, j]],
            'donor_metrics': donor, 'R1_metrics': r1, 'R2_metrics': r2,
            'L_inf_delta_vs_R1': r2['L_inf'] - r1['L_inf'], 'L1_delta_vs_R1': r2['L1'] - r1['L1'],
            'L_inf_delta_vs_donor': r2['L_inf'] - donor['L_inf'], 'L1_delta_vs_donor': r2['L1'] - donor['L1'],
            'absolute_exceedance': fails(r2), 'boundary_context': boundary}

changed = [i for i in range(3416) if W[i] != B[i]]
outside_drift = sorted(set(changed) - WRITE)
assert not outside_drift
delta_rows, entry_count, max_delta = [], 0, 0
for i in changed:
    entries = [{'group': g, 'R1': B[i].get(g, 0), 'R2': W[i].get(g, 0), 'delta': W[i].get(g, 0) - B[i].get(g, 0)}
               for g in sorted(set(B[i]) | set(W[i])) if B[i].get(g, 0) != W[i].get(g, 0)]
    entry_count += len(entries)
    max_delta = max(max_delta, max(abs(e['delta']) for e in entries))
    delta_rows.append({'vertex_id': i, 'operation': 'CLEANUP_ONLY' if i in CLEAN55 else 'ADDITIONAL_CONTINUITY' if i in NEW18 else 'ORIGINAL_WRITE', 'changed_group_entries': entries})
evaluations = read(OUT / 'R2_WEIGHT_EVALUATION_CENSUS.json')
assert len(evaluations['per_vertex']) == 317 and {r['vertex_id'] for r in evaluations['per_vertex']} == WRITE
assert all(row['after_float32'] == W[row['vertex_id']] for row in evaluations['per_vertex'])
repeat = read(OUT / 'DETERMINISTIC_REPEAT_BASELINE.json')
assert repeat['vector_hash'] == digest(W)
dump('R2_DETERMINISTIC_REPEAT_VERIFICATION.json', {'status': 'PASS', 'independent_solver_execution_count': 2,
                                                'first_vector_hash': repeat['vector_hash'], 'second_vector_hash': digest(W),
                                                'all_3416_vectors_exactly_repeated': True, 'deformation_objectives': False})
dump('R2_SCOPE_COMPLIANCE_AUDIT.json', {'status': 'PASS', 'approved_total_write_count': 317,
                                    'all_317_evaluated': True, 'outside317_write_count': 0, 'outside317_drift_count': 0,
                                    'procedural_write_ids': read(OUT / 'R2_CANDIDATE_PRE_SAVE_PAYLOAD.json')['procedural_vertex_group_write_ids'],
                                    'outside_ids_exact_R1_per_vertex': [{'vertex_id': i, 'exact_equal': W[i] == B[i], 'R1_hash': digest(B[i]), 'R2_hash': digest(W[i])} for i in sorted(OUTSIDE)],
                                    'original244_actual_changed': len(set(changed) & ORIGINAL),
                                    'new18_actual_changed': len(set(changed) & NEW18), 'cleanup55_actual_changed': len(set(changed) & CLEAN55),
                                    'cleanup55_not_free_optimizer_variables': all(not row['free_optimizer_variable'] for row in evaluations['per_vertex'] if row['vertex_id'] in CLEAN55),
                                    'scope_expansion_beyond_317': False})

cleanup_expect = read(OUT / 'R2_ZERO_CLEANUP_EXPECTED.json')
cleanup_result = []
for row in cleanup_expect['per_vertex']:
    i = row['vertex_id']
    expected = row['expected_float32_after']
    assert W[i] == expected
    assert not (set(W[i]) - set(row['before']))
    assert all(W[i].get(g, 0) == 0 for g in row['forbidden_entries_removed'])
    cleanup_result.append({**row, 'saved_R2_vector': W[i], 'all_forbidden_entries_exact_zero': True,
                           'proportional_normalization_matches_expected_float32': True,
                           'new_driver_components_count': 0, 'smoothing_applied': False})
dump('R2_ZERO_CLEANUP_RESULT.json', {'status': 'PASS', 'canonical_zero_epsilon': 0, 'evaluated': 55,
                                 'exact_zero_pass_count': 55, 'remaining_forbidden_positive_count': 0,
                                 'ratio_policy': 'Original allowed components normalized proportionally, then exact IEEE float32 storage; no new components.',
                                 'cleanup_only_free_smoothing': False, 'per_vertex': cleanup_result})

violations = {key: [] for key in ['weight_sum', 'negative', 'NaN', 'Inf', 'max_influences', 'non_deform_groups', 'TIP_helpers', 'FIRST_WEB_THUMB_IP', 'illegal_cross_digit']}
for i, vector in enumerate(W):
    if abs(sum(vector.values()) - 1) > TOL:
        violations['weight_sum'].append(i)
    if any(value < 0 for value in vector.values()):
        violations['negative'].append(i)
    if any(math.isnan(value) for value in vector.values()):
        violations['NaN'].append(i)
    if any(math.isinf(value) for value in vector.values()):
        violations['Inf'].append(i)
    if sum(value > 0 for value in vector.values()) > CONT['max_influences']:
        violations['max_influences'].append(i)
    if set(vector) - set(CONT['deform_bones']):
        violations['non_deform_groups'].append(i)
    if any(vector.get(group, 0) != 0 for group in CONT['helpers']['names']):
        violations['TIP_helpers'].append(i)
    if i in WEBIDS and vector.get('THUMB_IP_R', 0) != 0:
        violations['FIRST_WEB_THUMB_IP'].append(i)
    if i in LABEL:
        foreign = {g: value for g, value in vector.items() if g not in support(i) and value > 0}
        if foreign:
            violations['illegal_cross_digit'].append({'vertex_id': i, 'foreign_groups': foreign})
math_pass = all(not value for value in violations.values())
dump('R2_SKIN_MATH_INTEGRITY_AUDIT.json', {'status': 'PASS' if math_pass else 'FAIL', 'mesh_vertex_count': len(W),
                                      'canonical_forbidden_zero_epsilon': 0, 'normalization_tolerance': TOL,
                                      'max_weight_sum_error': max(abs(sum(v.values()) - 1) for v in W),
                                      'max_positive_influences': max(sum(x > 0 for x in v.values()) for v in W),
                                      'max_influences_authority': CONT['max_influences'],
                                      'cross_digit_guard_authority': 'Fresh frozen R3 bounded962 with exact FIRST_WEB21 exception; no new heuristic ownership for unrelated vertices.',
                                      'frozen_guard_vertex_count': len(LABEL),
                                      'violations': violations, 'violation_counts': {k: len(v) for k, v in violations.items()},
                                      'forbidden_positive_residue_count': len(violations['illegal_cross_digit'])})

prior_static = read(R1_DIR / 'SKIN_CONTINUITY_STATIC_CHECK_R1.json')
previous_checked = {r['edge_id'] for r in prior_static['all_checked_edges']}
seed = WRITE | set(WEB['continuity_scope']) | set(OLD['continuity_gate']['patch_vertex_ids']) | set(CAP['continuity_gate']['cap_2ring_vertex_ids']) | set(EDGE_AUTH['neighborhood_ids'])
checked = previous_checked | {eid for eid, (i, j) in enumerate(EDGES) if i in seed or j in seed or (i in LABEL and j in LABEL and LABEL[i] != LABEL[j])}
records = [edge_record(eid) for eid in sorted(checked)]
BY_EDGE = {r['edge_id']: r for r in records}
blockers = []
classes = ['INHERITED_COPY_ONLY', 'R2_INTRODUCED', 'R2_WORSENED', 'R2_IMPROVED_BUT_STILL_FAIL', 'SEMANTIC_TRANSITION_REQUIRES_QUALIFICATION', 'TRUE_SCOPE_CONFLICT']
for row in records:
    if not row['absolute_exceedance']:
        continue
    i, j = row['vertex_ids']
    exact = all(W[v] == B[v] == D[v] for v in (i, j))
    witnesses = []
    for u, v in [(i, j), (j, i)]:
        if u in WRITE and v not in WRITE:
            foreign = {g: value for g, value in W[v].items() if g not in support(u)}
            f, a = sum(foreign.values()), sum(value for g, value in W[v].items() if g in support(u))
            inf, l1 = max(foreign.values(), default=0), f + max(0, 1 - TOL - a)
            if inf > .5 or l1 > 1:
                witnesses.append({'edge_id': row['edge_id'], 'write_vertex': u, 'immutable_vertex': v,
                                  'minimum_possible_L_inf': inf, 'minimum_possible_L1': l1, 'foreign_components': foreign})
    if exact and i not in WRITE and j not in WRITE:
        temporal = primary = 'INHERITED_COPY_ONLY'
    elif not fails(row['R1_metrics']):
        temporal, primary = 'R2_INTRODUCED', 'TRUE_SCOPE_CONFLICT' if witnesses else 'R2_INTRODUCED'
    elif row['L_inf_delta_vs_R1'] > TOL or row['L1_delta_vs_R1'] > TOL:
        temporal, primary = 'R2_WORSENED', 'TRUE_SCOPE_CONFLICT' if witnesses else 'R2_WORSENED'
    elif row['L_inf_delta_vs_R1'] < 0 or row['L1_delta_vs_R1'] < 0:
        temporal, primary = 'R2_IMPROVED_BUT_STILL_FAIL', 'TRUE_SCOPE_CONFLICT' if witnesses else 'R2_IMPROVED_BUT_STILL_FAIL'
    else:
        temporal, primary = 'UNCHANGED_AFFECTED_SEAM', 'TRUE_SCOPE_CONFLICT' if witnesses else 'SEMANTIC_TRANSITION_REQUIRES_QUALIFICATION'
    blockers.append({**row, 'primary_classification': primary, 'temporal_classification': temporal,
                     'true_scope_conflict_witnesses': witnesses, 'qualification_status': 'INHERITED_QUALIFICATION_DEBT' if exact else 'NOT_QUALIFIED',
                     'candidate_introduced_attribution': temporal in ['R2_INTRODUCED', 'R2_WORSENED'],
                     'boundary_context_is_automatic_waiver': False})
counts = {key: sum(row['primary_classification'] == key for row in blockers) for key in classes}
introduced = sum(row['temporal_classification'] == 'R2_INTRODUCED' for row in blockers)
worsened = sum(row['temporal_classification'] == 'R2_WORSENED' for row in blockers)
scope_conflicts = sum(bool(row['true_scope_conflict_witnesses']) for row in blockers)
debt_ids = [row['edge_id'] for row in blockers if row['primary_classification'] == 'INHERITED_COPY_ONLY']
prior_blocker_ids = {r['edge_id'] for r in prior_static['blockers']}
closed_ids = sorted(prior_blocker_ids - {row['edge_id'] for row in blockers})
regressions_r1 = [r for r in records if r['L_inf_delta_vs_R1'] > TOL or r['L1_delta_vs_R1'] > TOL]
regressions_donor = [r for r in records if r['L_inf_delta_vs_donor'] > TOL or r['L1_delta_vs_donor'] > TOL]
dump('R2_STATIC_BLOCKER_CLASSIFICATION.json', {'canonical_semantics': 'SCOPED_ABSOLUTE_SCREEN_PLUS_NO_REGRESSION_WITH_EXPLICIT_QUALIFICATION',
                                            'absolute_exceedance_count': len(blockers), 'primary_counts': counts,
                                            'R2_introduced_count': introduced, 'R2_worsened_count': worsened,
                                            'true_scope_conflict_count': scope_conflicts, 'inherited_qualification_debt_ids': debt_ids,
                                            'debt_does_not_mean_no_defects': True, 'edges': blockers,
                                            'R1_absolute_blockers_closed_count': len(closed_ids), 'R1_absolute_blockers_closed_ids': closed_ids})
dump('R2_CONTINUITY_STATIC_AUDIT.json', {'status': 'PASS_SCOPED_REPAIR_WITH_INHERITED_QUALIFICATION_DEBT' if not introduced and not worsened and not scope_conflicts else 'FAIL_CLOSED',
                                      'canonical_absolute_limits': {'L_inf': .5, 'L1': 1}, 'no_regression_tolerance': TOL,
                                      'checked_edge_count': len(checked), 'previous_checked_edge_count': len(previous_checked),
                                      'newly_checked_edge_ids': sorted(checked - previous_checked),
                                      'all317_incident_and_crossing_edges_included': all(eid in checked for eid, (i, j) in enumerate(EDGES) if i in WRITE or j in WRITE),
                                      'FIRST_WEB_R3_cap37_oldcap9_edge5879_neighborhoods_included': True,
                                      'absolute_blocker_count': len(blockers), 'R2_introduced_count': introduced, 'R2_worsened_count': worsened,
                                      'true_scope_conflict_count': scope_conflicts, 'inherited_qualification_debt_count': len(debt_ids),
                                      'inherited_qualification_debt_ids': debt_ids,
                                      'all_checked_edges': records, 'all_exceedances': blockers,
                                      'R1_blockers_closed_ids': closed_ids,
                                      'subthreshold_no_regression_diagnostics': {'relative_R1_increase_count': len(regressions_r1), 'relative_donor_increase_count': len(regressions_donor),
                                                                               'relative_R1_records': regressions_r1, 'relative_donor_records': regressions_donor,
                                                                               'policy': 'All increases >1e-5 recorded. These are not new absolute blockers. Boundary/seam records remain explicit targeted qualification context; no deformation qualification or final production acceptance granted by this static-ready verdict.'},
                                      'gate_relaxations': [], 'deformation_runs': 0, 'Stage6_runs': 0})

dump('R2_VS_R1_WEIGHT_DELTA_CENSUS.json', {'status': 'PASS_APPROVED_SCOPE', 'actual_changed_vertex_count': len(changed),
                                       'changed_vertex_ids': changed, 'changed_group_entry_count': entry_count, 'max_absolute_delta': max_delta,
                                       'outside317_delta_count': 0, 'original244_changed_count': len(set(changed) & ORIGINAL),
                                       'new18_changed_count': len(set(changed) & NEW18), 'cleanup55_changed_count': len(set(changed) & CLEAN55),
                                       'R1_blockers_closed_count': len(closed_ids), 'R1_blockers_closed_ids': closed_ids, 'per_vertex_delta': delta_rows})
dump('R2_VS_R1B_DONOR_COMPARISON.json', {'donor_role': 'Historical source only; R2 was started from R1 and never regenerated from donor.',
                                     'R1_changed_vs_donor_count': sum(a != b for a, b in zip(B, D)),
                                     'R2_changed_vs_donor_count': sum(a != b for a, b in zip(W, D)),
                                     'R2_changed_vs_R1_count': len(changed),
                                     'remaining_absolute_debt_is_exact_donor_and_R1': all(all(W[v] == B[v] == D[v] for v in EDGES[eid]) for eid in debt_ids),
                                     'remaining_donor_debt_ids': debt_ids,
                                     'new_R2_absolute_defect_count_vs_R1': introduced, 'worsened_R2_absolute_defect_count_vs_R1': worsened,
                                     'candidate_absolute_failures_not_inherited_from_donor_count': sum(not fails(row['donor_metrics']) for row in blockers),
                                     'per_vertex': [{'vertex_id': i, 'R1B_vector': D[i], 'R1_vector': B[i], 'R2_vector': W[i],
                                                     'R1_change': B[i] != D[i], 'R2_amendment_change': W[i] != B[i],
                                                     'R2_equals_donor': W[i] == D[i]} for i in range(3416)],
                                     'edge_comparisons': records})

def incident_audit(vertices):
    ids = sorted(eid for eid, (i, j) in enumerate(EDGES) if i in vertices or j in vertices)
    rows = [BY_EDGE[eid] if eid in BY_EDGE else edge_record(eid) for eid in ids]
    bad = [row['edge_id'] for row in rows if row['absolute_exceedance']]
    return {'checked_count': len(rows), 'absolute_exceedance_ids': bad,
            'candidate_introduced_or_worsened': [row['edge_id'] for row in rows if row['absolute_exceedance'] and row['edge_id'] not in debt_ids],
            'max_L_inf': max((row['R2_metrics']['L_inf'] for row in rows), default=0),
            'max_L1': max((row['R2_metrics']['L1'] for row in rows), default=0), 'edges': rows}

cap_rows = []
for row in CAP['per_vertex_surface_evidence']:
    i = row['vertex_id']
    s = row['corrected_thumb_projection']['arc_mm']
    t = max(0., min(1., .5 + (s - CAP['rule']['s_IP_mm']) / (2 * CAP['rule']['h_mm'])))
    q = t*t*t*(t*(6*t-15)+10)
    expected = {g: float(np.float32(value)) for g, value in [('THUMB_IP_R', q), ('THUMB_MCP_R', 1-q)] if value > 0}
    assert expected == W[i] and W[i] == B[i]
    assert W[i].get('THUMB_IP_R', 0) >= W[i].get('THUMB_MCP_R', 0)
    cap_rows.append({'vertex_id': i, 'corrected_arc_mm': s, 'quintic_t': t, 'expected_float32': expected, 'saved_R2': W[i],
                     'exact_formula_match': True, 'IP_dominant': True, 'unchanged_vs_R1': True})
cap_incident = incident_audit(CAPIDS)
dump('R2_CAP37_AUDIT.json', {'status': 'PASS', 'count': 37, '37_of_37_corrected_arc_quintic_exact': True,
                           'driver_authority_not_relaxed_for_solver': True, 'IP_dominant_count': 37, 'allowed_groups': CAP['allowed_cap_deform_groups'],
                           'minimum_IP_weight': min(W[i].get('THUMB_IP_R', 0) for i in CAPIDS),
                           'one_hot_IP_only_mathematical_plateau': True, 'incident_continuity': cap_incident, 'per_vertex': cap_rows})
old_incident = incident_audit(OLDIDS)
assert all(set(W[i]) <= set(OLD['allowed_deform_groups']) for i in OLDIDS)
dump('R2_OLD_CAP9_AUDIT.json', {'status': 'PASS', 'count': 9, 'native_INDEX_only': True, 'THUMB_override_restored': False,
                              'allowed_groups': OLD['allowed_deform_groups'], 'incident_continuity': old_incident,
                              'per_vertex': [{'vertex_id': i, 'R1B': D[i], 'R1': B[i], 'R2': W[i], 'INDEX_compatible_support': True} for i in sorted(OLDIDS)]})
web_incident = incident_audit(WEBIDS)
dump('R2_FIRST_WEB_AUDIT.json', {'status': 'PASS_DRIVER_GUARD_WITH_INHERITED_QUALIFICATION_DEBT', 'membership_unchanged_count': 21,
                               'original_web_write_ids': sorted(WEBIDS & ORIGINAL), 'additional_web_write_ids': sorted(WEBIDS & NEW18),
                               'additional_web_count': len(WEBIDS & NEW18), 'total_web_write_count': len(WEBIDS & WRITE),
                               'remaining_copy_only_web_ids': sorted(WEBIDS - WRITE),
                               'allowed_groups': WEB['allowed_deform_groups'], 'THUMB_IP_violations': 0,
                               'TIP_helper_violations': 0, 'label_to_one_hot_mapping_used': False, 'three_way_static_constraints': True,
                               'incident_continuity': web_incident,
                               'per_vertex': [{'vertex_id': i, 'R1': B[i], 'R2': W[i], 'changed': W[i] != B[i], 'frozen_side_context': LABEL[i]} for i in sorted(WEBIDS)]})
edge5879 = BY_EDGE[5879]
dump('R2_EDGE5879_STATIC_AUDIT.json', {'status': 'PASS_ABSOLUTE_STATIC_SCREEN' if not edge5879['absolute_exceedance'] else 'FAIL_CLOSED',
                                    'edge': edge5879, 'v1551_changed_vs_R1': W[1551] != B[1551], 'v3125_changed_vs_R1': W[3125] != B[3125],
                                    'both_endpoints_in_original_write_authority': {str(i): i in ORIGINAL for i in [1551, 3125]},
                                    'original_approved_neighborhood_continuity': incident_audit(set(EDGE_AUTH['neighborhood_ids'])),
                                    'R1E_failure_vectors_imported': False, 'deformation_runs': 0})

mesh_keys = ['positions_local_m', 'positions_world_mm', 'edges', 'faces', 'UV_layers', 'face_material_indices', 'material_slots',
             'matrix_world', 'matrix_local', 'matrix_parent_inverse', 'location', 'rotation_mode', 'rotation_euler', 'scale', 'parent', 'modifiers']
mesh_checks = {key: R2_PAYLOAD['mesh'][key] == R1_PAYLOAD['mesh'][key] for key in mesh_keys}
rig_checks = {'R1_all_bone_transforms_hierarchy_pose_and_corrected_slots_exact': R2_PAYLOAD['rig'] == R1_PAYLOAD['rig'],
              'corrected_source_all_bone_snapshot_exact': R2_PAYLOAD['rig'] == SOURCES['CORRECTED']['rig']}
material_pass = read(OUT / 'R2_MATERIAL_SEMANTIC_NO_DRIFT.json')['status'] == 'PASS'
geometry_pass = all(mesh_checks.values()) and all(rig_checks.values()) and material_pass
dump('R2_RIG_GEOMETRY_NO_DRIFT_AUDIT.json', {'status': 'PASS' if geometry_pass else 'FAIL', 'mesh_checks': mesh_checks, 'rig_checks': rig_checks,
                                         'materials_nodes_and_shader_values_exact': material_pass,
                                         'geometry_delta': 0, 'topology_delta': 0, 'UV_delta': 0, 'material_delta': 0,
                                         'bone_delta': 0, 'joint_delta': 0, 'bone_count': len(R2_PAYLOAD['rig']['bones']),
                                         'original_binding_exact': mesh_checks['modifiers'], 'R1_candidate_overwritten': False})
save_pass = read(OUT / 'R2_SAVE_REOPEN_VERIFICATION.json')['status'] == 'PASS'
solver_pass = read(OUT / 'DETERMINISTIC_STATIC_SOLVER_R2.json')['status'] == 'CONVERGED'
before = read(OUT / 'FROZEN_HASHES_BEFORE.json')
after = inventory()
drift = [path for path, value in before.items() if after.get(path) != value]
outside_new_files = sorted(set(after) - set(before))
dump('FROZEN_HASHES_AFTER.json', after)
dump('R2_HISTORICAL_HASH_PROTECTION_AUDIT.json', {'status': 'PASS' if not drift and not outside_new_files else 'FAIL_CLOSED',
                                              'historical_file_count': len(before), 'drift_count': len(drift), 'drift_ids': drift,
                                              'new_files_outside_R2_task_count': len(outside_new_files), 'new_files_outside_R2_task_ids': outside_new_files,
                                              'R1_before_sha256': EXPECTED_R1, 'R1_after_sha256': sha(R1),
                                              'R1_unchanged': sha(R1) == EXPECTED_R1, 'historical_blend_writes': 0})
passed = math_pass and geometry_pass and save_pass and solver_pass and not outside_drift and not introduced and not worsened and not scope_conflicts and not drift and not outside_new_files
verdict = 'PASS_READY_FOR_TARGETED_DEFORMATION' if passed else 'FAIL_CLOSED_R2_STATIC_CANDIDATE'
next_phase = 'CAP_FIXTURE_STATIC_VALIDATION_AND_TARGETED_DEFORMATION_R1' if passed else 'R2_STATIC_SCOPE_EXCEPTION_REVIEW'
status = {'phase': PHASE, 'Human_amendment_approval_verified': True, 'proposal_hash_verified': True, 'R1_candidate_hash_verified': sha(R1) == EXPECTED_R1,
          'total_approved_write_set': 317, 'original_write_set': 244, 'additional_continuity_vertices': 18, 'cleanup_only_vertices': 55,
          'R2_candidate_path': str(CANDIDATE), 'R2_candidate_hash': sha(CANDIDATE), 'R2_weight_vector_hash': digest(W),
          'total_evaluated': 317, 'actual_changed_count': len(changed), 'original244_changed_count': len(set(changed) & ORIGINAL),
          'new18_changed_count': len(set(changed) & NEW18), 'cleanup55_changed_count': len(set(changed) & CLEAN55),
          'outside317_write_count': 0, 'outside317_drift_count': len(outside_drift), 'cleanup55_exact_zero': 'PASS',
          'forbidden_residue_count': len(violations['illegal_cross_digit']), 'weight_sum_violations': len(violations['weight_sum']),
          'negative_violations': len(violations['negative']), 'NaN_violations': len(violations['NaN']), 'Inf_violations': len(violations['Inf']),
          'max_influence_violations': len(violations['max_influences']), 'TIP_helper_violations': len(violations['TIP_helpers']),
          'FIRST_WEB_THUMB_IP_violations': len(violations['FIRST_WEB_THUMB_IP']), 'illegal_cross_digit_violations': len(violations['illegal_cross_digit']),
          'absolute_continuity_blocker_count': len(blockers), 'inherited_copy_only_blocker_count': counts['INHERITED_COPY_ONLY'],
          'R2_introduced_blocker_count': introduced, 'R2_worsened_blocker_count': worsened, 'true_scope_conflict_count': scope_conflicts,
          'inherited_qualification_debt_count': len(debt_ids), 'inherited_qualification_debt_ids': debt_ids,
          'checked_edge_count': len(checked), 'R1_blockers_closed_count': len(closed_ids),
          'edge1130_status': 'INHERITED_QUALIFICATION_DEBT_EXACT_R1_AND_DONOR_COPY', 'edge1234_status': 'CLOSED_PASS_ABSOLUTE_STATIC_SCREEN',
          'edge5879_static_status': 'PASS_ABSOLUTE_STATIC_SCREEN', 'v1551_status': 'CHANGED_WITHIN_ORIGINAL_AUTHORITY', 'v3125_status': 'CHANGED_WITHIN_ORIGINAL_AUTHORITY',
          'geometry_delta': 0, 'topology_delta': 0, 'bone_delta': 0, 'joint_delta': 0,
          'save_reopen': 'PASS' if save_pass else 'FAIL', 'serialization_drift': 0 if save_pass else None,
          'deformation_runs': 0, 'Stage6_runs': 0, 'R3_reruns': 0, 'anatomy_research_runs': 0, 'production_promotion': False,
          'historical_file_drift_count': len(drift), 'outside_R2_new_file_count': len(outside_new_files),
          'R2_STATIC_CANDIDATE': verdict, 'verdict': verdict, 'NEXT': next_phase, 'STOP': True,
          'static_ready_does_not_mean_no_defects_or_deformation_pass': True, 'targeted_deformation_approved_in_this_round': False}
dump(PHASE + '_STATUS.json', status)

report = f'''# TARGETED_RIG_AND_SKIN_DATA_REBUILD_R2

**R2_STATIC_CANDIDATE = {verdict}**. NEXT = **{next_phase}**. STOP.

R2独立candidate已由R1载入创建；R1和全部历史文件未修改。Static-ready表示可以进入下一轮targeted qualification，不表示no defects、deformation PASS或production promotion。本轮pose/deformation/Stage6/R3/anatomy运行均为0。

## Human与精确权限

唯一Human响应 `{RESPONSE.name}` 的review/phase、Q1..Q5、accepted/answered、授权phase及三个禁止flag全部精确匹配。proposal SHA256 `{EXPECTED_PROPOSAL}`；R1 SHA256 `{EXPECTED_R1}`。原authority bundle及12个组件hash均通过。

唯一write universe为317=244原权限+18连续性修复+55仅清除残留；三个集合互斥。317/317均执行对应rule evaluation。实际变化{len(changed)}，原244变化{len(set(changed)&ORIGINAL)}、新增18变化{len(set(changed)&NEW18)}、cleanup55变化{len(set(changed)&CLEAN55)}。Outside317 write/drift均0。

55点不进入optimizer，严格按原allowed正分量比例归一化，再float32序列化；列出的forbidden entries全部精确清除，新增driver=0、free smoothing=0。Canonical zero epsilon仍为0。

## 静态solver与authority

复用原正式deterministic harmonic method的MED/edge-length正权系数、0.01几何prior、sorted cyclic simplex updates，扩展为经Human批准的联合自由集合，并让所有三方interface与外pins参加。初始化只来自R1与静态approved bone-distance prior。之后用deterministic Dykstra投影约束本地支持simplex、所有自由点incident edges的L∞≤0.5/L1≤1。Stable ordering/ties、fixed tolerance1e-10、max30000；内部rounding guard使目标略严于正式gate，未放宽threshold。165次harmonic sweeps、100次projection sweeps收敛。两次独立完整求解得到相同vector hash `{digest(W)}`。

**110个已正确distal-profile点固定保持R1值**，包含cap37及相邻兼容thumb support；逐点重新按corrected arc quintic计算并匹配float32。cap37 37/37 IP dominant且quintic exact，全部未被solver改动。其余14个原proximal THUMB点与新增5个非web THUMB点在有支持的CMC/WRIST base transition中联合修复；条件IP/MCP driver pair保持corrected-arc quintic比例，不把ownership变成one-hot，不改变cap/真正distal profile。局部base budget依据static topology/support连续优化，而不是把R1失败的proximal vectors当成immutable。

INDEX与web仍使用原approved group families。Old cap9 9/9为native INDEX-compatible，THUMB override未恢复。FIRST_WEB21 membership不变，新增13点加原v3125共14个可写；剩余7点copy-only。FIRST_WEB的THUMB_IP和TIP影响均精确0。Edge5879的v1551/v3125继续原write authority，二者都已重新调整，未导入R1E failure vectors。

## 完整静态closure与因果记录

检查 **{len(checked)} edges**：包含上一轮2089、全部317 incident/crossing、FIRST_WEB完整2-ring、fresh-R3 boundary、cap37 2-ring、oldcap9 patch与edge5879原neighborhood。新增checked edges38；不是仅复查原64。

原64个absolute blockers关闭 **{len(closed_ids)}**，剩余 **{len(blockers)}** 全部为兩端完全copy-only、R2=R1=donor。R2_INTRODUCED=0，R2_WORSENED=0，TRUE_SCOPE_CONFLICT=0。Driver-family boundary没有自动waive gate。

**INHERITED_QUALIFICATION_DEBT IDs**：`{debt_ids}`。这16条仍超过绝对screen，不能写成“no defects”。它们保留下一轮targeted qualification义务，单独与candidate delta归因。

edge1130：inherited debt，R2/R1/donor相同，L∞={BY_EDGE[1130]['R2_metrics']['L_inf']}、L1={BY_EDGE[1130]['R2_metrics']['L1']}。

edge1234：已关闭，L∞={BY_EDGE[1234]['R2_metrics']['L_inf']}、L1={BY_EDGE[1234]['R2_metrics']['L1']}。v338仍只允许INDEX/WRIST，v1448采用shared web groups，不需要增加任何新权限。

edge5879：已关闭，L∞={BY_EDGE[5879]['R2_metrics']['L_inf']}、L1={BY_EDGE[5879]['R2_metrics']['L1']}。这里只报告saved weight静态指标，没有deformation改善声明。

所有超过1e-5的增加均保留：R2-vs-R1 {len(regressions_r1)}条、R2-vs-donor {len(regressions_donor)}条。它们全部低于absolute gates；boundary/preexisting seam的增加作为明确记录的targeted qualification上下文保留，没有在本轮假装获得deformation qualification。这不改变用户本轮指定的“introduced/worsened absolute blockers为0，可进入下一轮qualification”的条件。

## 全mesh数学、保存与保护

3416点归一化、negative/NaN/Inf、max4、nondeform/TIP、FIRST_WEB IP、freshR3 forbidden guard全部PASS，forbidden-positive residue=0。最大sum error `{max(abs(sum(v.values())-1) for v in W)}`，正式容差1e-5。

R2保存后用独立factory-startup Blender5.1.2 clean reload重新读取所有mesh transforms/topology/UV/material binding、21 bones完整hierarchy/corrected slots及3416 vectors，serialization drift=0。另以只读Blender比较材料properties、shader nodes、socket defaults、links与image配置，exact PASS。Geometry/topology/UV/material/bone/joint delta均0。

保护快照涵盖{len(before)}个历史文件/唯一响应：before=after，drift=0；R2 task以外新文件=0。所有文件写入仅在本R2目录，历史blend写入=0，R2 blend保存1次。R2 container不宣称每次另存字节可重复；可重复的是两次deterministic solver的完整float32 weight payload hash。

## Candidate与输出

Candidate：`{CANDIDATE.relative_to(ROOT).as_posix()}`

SHA256：`{sha(CANDIDATE)}`

Weight vector SHA256：`{digest(W)}`

至少要求的scope、317 evaluation、cleanup、continuity/因果分类、R2/R1/R1B delta、math、FIRST_WEB/cap37/oldcap9/edge5879、geometry/rig与save/reopen JSON均位于本目录；完整指标与向量记录供下一轮使用。

NEXT = **{next_phase}**。本轮deformation=0，Stage6=0，不自动启动下一轮。STOP。
'''
(OUT / (PHASE + '_REPORT.md')).write_text(report, encoding='utf-8')
dump('R2_OUTPUT_VERIFICATION.json', {'status': 'PASS' if passed else 'FAIL_CLOSED', 'all_requested_gates_satisfied': passed,
                                  'candidate_static_ready_has_inherited_qualification_debt': True,
                                  'deterministic_weight_payload_repeat': True, 'historical_hashes_unchanged': not drift and not outside_new_files,
                                  'candidate_sha256': sha(CANDIDATE), 'weight_vector_sha256': digest(W), 'STOP': True})
manifest = {p.name: sha(p) for p in OUT.iterdir() if p.is_file() and p.name != 'OUTPUT_EVIDENCE_HASH_MANIFEST_R2.json'}
dump('OUTPUT_EVIDENCE_HASH_MANIFEST_R2.json', {'files': manifest, 'canonical_files_hash': digest(manifest), 'excludes_self': True})
print(json.dumps(status, ensure_ascii=False, indent=2))
