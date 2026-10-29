"""Deterministic static constrained repair, based on R1 only; no pose/deformation imports."""
from common import *
import collections
import numpy as np

SCOPE = read(OUT / 'AUTHORIZED_WEIGHT_WRITE_SET_R2.json')
BASE = read(R1_DIR / 'CANDIDATE_CLEAN_REOPEN_PAYLOAD_R1.json')
CONT = read(AUTH_DIR / 'SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json')
CAP = read(AUTH_DIR / 'CAP37_SKIN_DRIVER_AUTHORITY_R1.json')
WEB = read(AUTH_DIR / 'FIRST_WEB_SKIN_WEIGHT_WRAPPER_R2.json')
OLD = read(AUTH_DIR / 'OLD_CAP9_SKIN_CORRECTION_AUTHORITY_R1.json')
R3 = read(ROOT / 'audits/human_r3_fresh_result_authority_freeze_r1/FRESH_R3_OWNERSHIP_AUTHORITY_R1.json')
PARAM = read(ROOT / CAP['rule']['parameter_source']['path'])
LABEL = {int(k): v for k, v in R3['membership']['vertex_labels'].items()}
ORIGINAL = set(SCOPE['original_244'])
NEW18 = set(SCOPE['additional_continuity_18'])
CLEAN = set(SCOPE['cleanup_only_55'])
WRITE = set(SCOPE['approved_write_universe_317'])
CAPIDS = {row['vertex_id'] for row in CAP['per_vertex_surface_evidence']}
WEBIDS = set(WEB['membership']['vertex_ids'])
OLDIDS = set(OLD['vertex_ids'])
GROUPS = CONT['deform_bones']
G = {name: i for i, name in enumerate(GROUPS)}
V = np.asarray(BASE['mesh']['positions_world_mm'])
EDGES = BASE['mesh']['edges']
BONES = BASE['rig']['bones']
MED = PARAM['derivation']['med_edge_mm']
TOL = CONT['normalization']['absolute_tolerance']

def allowed(i):
    if i in WEBIDS:
        return set(WEB['allowed_deform_groups'])
    if i in CAPIDS:
        return set(CAP['allowed_cap_deform_groups'])
    if i in OLDIDS:
        return set(OLD['allowed_deform_groups'])
    return set(CONT['ownership_guard']['allowed_by_side'][LABEL[i]])

XBASE = np.zeros((3416, len(GROUPS)))
for i, vec in enumerate(BASE['weights']):
    for group, weight in vec.items():
        XBASE[i, G[group]] = weight
FIXED = XBASE.copy()
cleanup_records = []
proposal_rows = {r['vertex_id']: r for r in SCOPE['per_additional_vertex_authority']}
for i in sorted(CLEAN):
    row = proposal_rows[i]
    assert set(row['allowed_groups']) == allowed(i)
    retained = {g: w for g, w in BASE['weights'][i].items() if g in allowed(i)}
    forbidden = {g: w for g, w in BASE['weights'][i].items() if g not in allowed(i)}
    assert forbidden and sum(retained.values()) > 0
    # The only permitted operation: remove listed foreign entries, proportional normalization.
    target = {g: float(np.float32(w / sum(retained.values()))) for g, w in retained.items()}
    FIXED[i] = 0
    for group, weight in target.items():
        FIXED[i, G[group]] = weight
    cleanup_records.append({'vertex_id': i, 'rule': row['operation'], 'before': BASE['weights'][i],
                            'forbidden_entries_removed': forbidden, 'normalization_denominator': sum(retained.values()),
                            'expected_float32_after': target, 'new_driver_components': [], 'free_optimizer_variable': False})

def segment(p, a, b):
    p, a, b = np.asarray(p), np.asarray(a), np.asarray(b)
    delta = b - a
    mu = max(0., min(1., float(np.dot(p - a, delta) / np.dot(delta, delta))))
    return float(np.linalg.norm(p - a - mu * delta)), mu

def profile(i):
    pts = [BONES[g]['head_world_mm'] for g in ['THUMB_CMC_R', 'THUMB_MCP_R', 'THUMB_IP_R']] + [BONES['THUMB_IP_R']['tail_world_mm']]
    lengths = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    knots = np.r_[0, np.cumsum(lengths)]
    choices = []
    for k in range(3):
        d, mu = segment(V[i], pts[k], pts[k+1])
        choices.append((d, k, float(knots[k] + mu * lengths[k])))
    distance, k, s = min(choices, key=lambda row: (row[0], row[1]))
    t = max(0., min(1., .5 + (s - CAP['rule']['s_IP_mm']) / (2 * CAP['rule']['h_mm'])))
    q = t*t*t*(t*(6*t-15)+10)
    return {'distance_mm': distance, 'nearest_segment': k, 'arc_mm': s, 'quintic_t': t, 'IP_share': q, 'MCP_share': 1-q}

# Preserve the already correct distal field, including cap37 and its compatible adjacent thumb support.
# Proximal CMC/WRIST transition budget can be re-solved; its conditional IP/MCP blend stays quintic.
DISTAL_PINS = {i for i in ORIGINAL if LABEL[i] == 'THUMB' and i not in WEBIDS and set(BASE['weights'][i]) <= {'THUMB_IP_R', 'THUMB_MCP_R'}}
assert CAPIDS <= DISTAL_PINS and len(DISTAL_PINS) == 110
profile_records = {}
for i in sorted(DISTAL_PINS):
    row = profile(i)
    expected = {g: float(np.float32(value)) for g, value in [('THUMB_IP_R', row['IP_share']), ('THUMB_MCP_R', row['MCP_share'])] if value > 0}
    assert expected == BASE['weights'][i], ('FAIL_CLOSED distal authority differs from R1', i)
    profile_records[i] = {'vertex_id': i, 'rule': 'CORRECTED_ARC_QUINTIC_DISTAL_FIXED_AUTHORITY', **row,
                          'float32_vector_exact': expected, 'cap37': i in CAPIDS, 'free_optimizer_variable': False}

FREE = sorted((ORIGINAL | NEW18) - DISTAL_PINS)
FIDX = {i: k for k, i in enumerate(FREE)}
assert len(FREE) == 152 and not CLEAN.intersection(FREE)
N = len(FREE)
# A per-vertex convex basis, at most four real driver influences. No global post-prune.
B = np.zeros((N, 4, len(GROUPS)))
ACTIVE = np.zeros((N, 4), dtype=bool)
for k, i in enumerate(FREE):
    a = allowed(i)
    if i in NEW18:
        assert a == set(proposal_rows[i]['allowed_groups'])
    if LABEL[i] == 'THUMB' and i not in WEBIDS:
        row = profile(i)
        B[k, 0, G['WRIST_R']] = 1
        B[k, 1, G['THUMB_CMC_R']] = 1
        B[k, 2, G['THUMB_IP_R']] = row['IP_share']
        B[k, 2, G['THUMB_MCP_R']] = row['MCP_share']
        ACTIVE[k, :3] = True
        profile_records[i] = {'vertex_id': i, 'rule': 'PROXIMAL_BASE_TRANSITION_STATIC_REPAIR_WITH_QUINTIC_IP_MCP_DRIVER_BLEND',
                              **row, 'base_budget_variables': ['WRIST_R', 'THUMB_CMC_R', 'THUMB_IP_MCP_PROFILE_PAIR'],
                              'authority_context': 'Existing proximal support and approved local transition optimization; no cap/profile pin moved.'}
    else:
        for component, group in enumerate(sorted(a)):
            B[k, component, G[group]] = 1
            ACTIVE[k, component] = True
COEFF = np.einsum('nkg,nkg->nk', B, B)
COEFF[~ACTIVE] = 1

def project_vertex_block(Y, indices=None):
    if indices is None:
        basis, active, coeff = B, ACTIVE, COEFF
    else:
        basis, active, coeff = B[indices], ACTIVE[indices], COEFF[indices]
    z = np.einsum('nkg,ng->nk', basis, Y) / coeff
    scores = np.where(active, z * coeff, -np.inf)
    order = np.argsort(-scores, axis=1, kind='stable')
    sorted_z = np.take_along_axis(np.where(active, z, 0), order, axis=1)
    inv = np.take_along_axis(np.where(active, 1 / coeff, 0), order, axis=1)
    breakpoints = np.take_along_axis(scores, order, axis=1)
    thresholds = (np.cumsum(sorted_z, axis=1) - 1) / np.maximum(np.cumsum(inv, axis=1), 1e-30)
    positive = breakpoints > thresholds
    rho = np.sum(positive, axis=1) - 1
    theta = thresholds[np.arange(len(Y)), rho]
    factors = np.where(active, np.maximum(z - theta[:, None] / coeff, 0), 0)
    return np.einsum('nk,nkg->ng', factors, basis)

ADJ = [[] for _ in FREE]
all_incident = []
for eid, (i, j) in enumerate(EDGES):
    if i in WRITE or j in WRITE:
        all_incident.append(eid)
    c = MED / float(np.linalg.norm(V[i] - V[j]))
    for u, v in [(i, j), (j, i)]:
        if u in FIDX:
            ADJ[FIDX[u]].append((v, c))
PRIOR = np.zeros((N, len(GROUPS)))
for k, i in enumerate(FREE):
    groups = sorted(allowed(i))
    distances = np.array([segment(V[i], BONES[g]['head_world_mm'], BONES[g]['tail_world_mm'])[0] for g in groups])
    weights = 1 / (distances + MED)**2
    weights /= weights.sum()
    for group, weight in zip(groups, weights):
        PRIOR[k, G[group]] = weight
PRIOR = project_vertex_block(PRIOR)
lam = WEB['prior_strength']
diag = np.array([lam + sum(c for j, c in neighbors) for neighbors in ADJ])
X = project_vertex_block(XBASE[FREE])

def harmonic_update(k, X):
    rhs = lam * PRIOR[k].copy()
    for j, coeff in ADJ[k]:
        rhs += coeff * (X[FIDX[j]] if j in FIDX else FIXED[j])
    return project_vertex_block((rhs / diag[k])[None], np.array([k]))[0]

for iteration in range(1, 20001):
    max_change = 0.
    for k in range(N):
        update = harmonic_update(k, X)
        max_change = max(max_change, float(np.max(np.abs(update - X[k]))))
        X[k] = update
    if max_change <= 1e-12:
        break
else:
    raise RuntimeError('FAIL_CLOSED harmonic initialization did not converge')
SEED = X.copy()
print('STATIC harmonic initialization', iteration, 'sweeps; free', N, 'fixed distal', len(DISTAL_PINS), flush=True)

# Independent edges within each color have disjoint variable endpoints. Projections commute.
colors, used = [], collections.defaultdict(set)
for eid, (i, j) in enumerate(EDGES):
    if i not in FIDX and j not in FIDX:
        continue
    forbidden_colors = used[i] | used[j]
    color = next(k for k in range(len(colors) + 1) if k not in forbidden_colors)
    if color == len(colors):
        colors.append([])
    colors[color].append((eid, i, j))
    if i in FIDX:
        used[i].add(color)
    if j in FIDX:
        used[j].add(color)
batches = []
for rows in colors:
    a = np.array([i for eid, i, j in rows])
    b = np.array([j for eid, i, j in rows])
    ia = np.array([FIDX.get(int(i), -1) for i in a])
    ib = np.array([FIDX.get(int(i), -1) for i in b])
    ma, mb = ia >= 0, ib >= 0
    batches.append({'rows': rows, 'a': a, 'b': b, 'ia': ia, 'ib': ib, 'ma': ma, 'mb': mb,
                    'denom': (ma.astype(float) + mb.astype(float))[:, None]})

def l1_project(DIFF, radius):
    absolute = np.abs(DIFF)
    active = absolute.sum(axis=1) > radius
    result = DIFF.copy()
    if np.any(active):
        rows = absolute[active]
        ordered = np.sort(rows, axis=1)[:, ::-1]
        threshold = (np.cumsum(ordered, axis=1) - radius) / np.arange(1, len(GROUPS) + 1)
        rho = np.sum(ordered > threshold, axis=1) - 1
        theta = threshold[np.arange(len(rows)), rho]
        result[active] = np.sign(DIFF[active]) * np.maximum(rows - theta[:, None], 0)
    return result

def edges_max_violation(X, inf_target, l1_target):
    maximum = 0.
    for batch in batches:
        a, b = FIXED[batch['a']].copy(), FIXED[batch['b']].copy()
        a[batch['ma']] = X[batch['ia'][batch['ma']]]
        b[batch['mb']] = X[batch['ib'][batch['mb']]]
        delta = np.abs(a - b)
        maximum = max(maximum, float(np.max(delta) - inf_target), float(np.max(delta.sum(axis=1)) - l1_target))
    return maximum

def constrained_projection(seed, guard):
    X = seed.copy()
    vertex_correction = np.zeros_like(X)
    corrections = [(np.zeros((len(batch['rows']), len(GROUPS))), np.zeros((len(batch['rows']), len(GROUPS)))) for mode in ['L_inf', 'L1'] for batch in batches]
    inf_target, l1_target = .5 - guard, 1 - 2 * guard
    progress = []
    for sweep in range(1, 30001):
        previous = X.copy()
        Y = X + vertex_correction
        projected = project_vertex_block(Y)
        vertex_correction = Y - projected
        X = projected
        offset = 0
        for mode in ['L_inf', 'L1']:
            for batch in batches:
                pa, pb = corrections[offset]
                offset += 1
                ma, mb, ia, ib = batch['ma'], batch['mb'], batch['ia'], batch['ib']
                a, b = FIXED[batch['a']].copy(), FIXED[batch['b']].copy()
                a[ma] = X[ia[ma]] + pa[ma]
                b[mb] = X[ib[mb]] + pb[mb]
                difference = a - b
                p = np.clip(difference, -inf_target, inf_target) if mode == 'L_inf' else l1_project(difference, l1_target)
                correction = (difference - p) / batch['denom']
                aa, bb = a - correction, b + correction
                pa[ma] = a[ma] - aa[ma]
                pb[mb] = b[mb] - bb[mb]
                X[ia[ma]] = aa[ma]
                X[ib[mb]] = bb[mb]
        if sweep % 100 == 0:
            vertex_violation = float(np.max(np.abs(X - project_vertex_block(X))))
            edge_violation = edges_max_violation(X, inf_target, l1_target)
            change = float(np.max(np.abs(X - previous)))
            progress.append({'sweep': sweep, 'vertex_projection_residual': vertex_violation,
                             'edge_gate_residual': edge_violation, 'max_change': change})
            if sweep % 1000 == 0:
                print('STATIC constrained projection', sweep, 'vertex', vertex_violation, 'edge', edge_violation, flush=True)
            if max(vertex_violation, edge_violation, change) <= 1e-10:
                return project_vertex_block(X), {'converged': True, 'sweeps': sweep, 'rounding_guard': guard, 'progress': progress}
    return project_vertex_block(X), {'converged': False, 'sweeps': sweep, 'rounding_guard': guard, 'progress': progress}

# Rounding guard is tighter than the approved gate, never a relaxation of it.
X, solve = constrained_projection(SEED, 2e-6)
if not solve['converged']:
    print('STATIC tighter rounding guard not converged; trying exact unchanged gate', flush=True)
    first_attempt = solve
    X, solve = constrained_projection(SEED, 0)
    solve['stricter_rounding_attempt'] = first_attempt
FINAL = [dict(v) for v in BASE['weights']]
for i in sorted(CLEAN):
    FINAL[i] = next(row['expected_float32_after'] for row in cleanup_records if row['vertex_id'] == i)
for k, i in enumerate(FREE):
    FINAL[i] = {g: float(np.float32(X[k, G[g]])) for g in GROUPS if X[k, G[g]] > 0}
    assert set(FINAL[i]) <= allowed(i) and len(FINAL[i]) <= 4
    assert abs(sum(FINAL[i].values()) - 1) <= TOL and all(v >= 0 for v in FINAL[i].values())
for i in range(3416):
    if i not in WRITE:
        assert FINAL[i] == BASE['weights'][i]
evaluations = []
for i in sorted(WRITE):
    if i in CLEAN:
        detail = next(row for row in cleanup_records if row['vertex_id'] == i)
    elif i in DISTAL_PINS:
        detail = profile_records[i]
    else:
        detail = {'vertex_id': i, 'rule': 'APPROVED_LOCAL_STATIC_CONSTRAINED_RECONSTRUCTION',
                  'allowed_groups': sorted(allowed(i)), 'free_optimizer_variable': True,
                  'profile_constraint': profile_records.get(i),
                  'geometry_prior': {g: float(PRIOR[FIDX[i], G[g]]) for g in GROUPS if PRIOR[FIDX[i], G[g]] > 0},
                  'static_neighbor_ids': [j for j, c in ADJ[FIDX[i]]],
                  'additional_amendment_row': proposal_rows.get(i)}
    evaluations.append({**detail, 'evaluated': True, 'changed_vs_R1': FINAL[i] != BASE['weights'][i],
                        'before_R1': BASE['weights'][i], 'after_float32': FINAL[i]})
assert len(evaluations) == 317
dump('R2_WEIGHT_EVALUATION_CENSUS.json', {'status': 'ALL_317_RULES_EVALUATED', 'total_evaluated': 317,
                                       'rule_counts': dict(collections.Counter(row['rule'] for row in evaluations)),
                                       'cleanup_only_excluded_from_optimizer': True, 'fixed_distal_profile_count': len(DISTAL_PINS),
                                       'free_static_variable_count': N, 'per_vertex': evaluations})
dump('R2_ZERO_CLEANUP_EXPECTED.json', {'count': 55, 'per_vertex': cleanup_records})
dump('DETERMINISTIC_STATIC_SOLVER_R2.json', {'status': 'CONVERGED' if solve['converged'] else 'FAIL_CLOSED_NOT_CONVERGED',
                                          'method': 'Reuse approved sorted cyclic positive-edge harmonic initialization; deterministic Dykstra Euclidean projection onto exact driver/profile simplices and all incident L_inf/L1 gate constraints.',
                                          'objective': 'Minimum Euclidean departure from static harmonic field under approved support and continuity; no pose/deformation loss.',
                                          'harmonic_prior_strength': lam, 'harmonic_sweeps': iteration,
                                          'deterministic_order': 'ascending vertex/edge IDs, stable component sorting, fixed greedy edge colors',
                                          'fixed_initialization': 'R1 vectors then static bone-distance harmonic initialization',
                                          'projection_tolerance': 1e-10, 'projection_max_sweeps': 30000,
                                          'edge_color_count': len(batches), 'constrained_edge_count': sum(len(b['rows']) for b in batches),
                                          'solver': solve, 'cap37_and_compatible_distal_field_fixed_exact': True,
                                          'proximal_rule': 'Continuous base-budget repair with conditional corrected-arc quintic IP/MCP blend; geometry/topology/support only.',
                                          'canonical_gates': {'L_inf': .5, 'L1': 1, 'no_regression_tolerance': TOL},
                                          'threshold_relaxations': [], 'scope_extensions': [], 'deformation_runs': 0, 'Stage6_runs': 0})
dump('CANDIDATE_WEIGHT_PAYLOAD_R2.json', {'phase': PHASE, 'R1_candidate_sha256': EXPECTED_R1, 'proposal_sha256': EXPECTED_PROPOSAL,
                                      'weights': FINAL, 'vector_hash': digest(FINAL), 'authorized_write_ids': sorted(WRITE),
                                      'evaluated_ids': sorted(WRITE), 'outside_write_drift_count': 0,
                                      'solver_converged': solve['converged'], 'intended_changed_count': sum(a != b for a, b in zip(FINAL, BASE['weights']))})
print(json.dumps({'solver_converged': solve['converged'], 'evaluated': 317, 'changed': sum(a != b for a, b in zip(FINAL, BASE['weights'])), 'weight_vector_hash': digest(FINAL)}, indent=2), flush=True)
