"""A bounded local weight-paint smooth pass; native geometry is locked."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import *
import numpy as np

bind_human_receipt()
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
iteration = args[0] if args else '01'
strength = float(args[1]) if len(args) > 1 else .90
sweeps = int(args[2]) if len(args) > 2 else 12
G = read(PRIOR / 'ITERATION_03_GEOMETRY.json')
ob, rig = open_asset(CURRENT); original = snapshot()
V, F = evaluate(ob, ob.matrix_world); E = [list(e.vertices) for e in ob.data.edges]
N = len(V); adj = [set() for _ in V]
for a, b in E: adj[a].add(b); adj[b].add(a)
protected = set(G['protected_dorsal54']) | set(G['protected_palmar16']) | set(G['protected_normal69'])
locked = protected | {j for i in protected for j in adj[i]}
regions = read(ROOT / 'production_spec/stage5_production_rig/stage5b_r1b/_tmp/R1B_REGIONS.json')['regions']
eligible = set(regions['THENAR_BASE']) | set(regions['THUMB_FIRST_METACARPAL']) | set(regions['FIRST_WEB']) | set(G['vertex_ids'])
for _ in range(2): eligible |= {j for i in eligible for j in adj[i]}
D = Vector((.631289124, .775318801, -.0188387)).normalized(); Z = Vector((0, 0, 1)); X = D.cross(Z).normalized(); P = -D
W = rig.matrix_world @ rig.data.bones['WRIST_R'].head_local
local = np.array([[(v - W).dot(a) * MM for a in (X, P, Z)] for v in V])
names = ['WRIST_R', 'THUMB_CMC_R', 'THUMB_MCP_R', 'THUMB_IP_R']
weights = original['positive_weight_vectors']
matrix = np.array([[w.get(n, 0.) for n in names] for w in weights])
active_total = matrix.sum(axis=1)
brush = {}
for i in sorted(eligible - locked):
    x, depth, z = local[i]
    radius = math.sqrt(((x - 32.) / 31.) ** 2 + ((z - 68.) / 35.) ** 2)
    b = strength * (1 - smoothstep(.40, 1., radius)) * smoothstep(-30., -8., depth)
    b *= smoothstep(36., 46., z) * (1 - smoothstep(87., 103., z))
    if b > 1e-4 and active_total[i] > .75: brush[i] = b
ids = sorted(brush)
field = matrix.copy()
# Standard local smoothing of existing influences over the native one-ring.
# Four-finger and other influence columns retain their exact original values.
for _ in range(sweeps):
    previous = field.copy()
    for i in ids:
        neighbors = sorted(adj[i])
        distances = np.array([(V[i] - V[j]).length for j in neighbors])
        factors = np.exp(-distances ** 2 / (2 * .009 ** 2))
        avg = factors @ previous[neighbors] / factors.sum()
        value = .5 * previous[i] + .5 * avg
        if value.sum() > 0: field[i] = value / value.sum() * active_total[i]
new = matrix.copy()
for i in ids: new[i] = matrix[i] * (1 - brush[i]) + field[i] * brush[i]
apply_weights(ob, ids, names, new[ids])
after = snapshot()
assert after['coordinates_local_m'] == original['coordinates_local_m']
assert protected_without_weights(after) == protected_without_weights(original)
changed = [i for i, (a, b) in enumerate(zip(original['protected']['weights_exact_including_zero'], after['protected']['weights_exact_including_zero'])) if a != b]
assert set(changed) <= set(ids) and not set(changed) & protected
for i in changed:
    assert all(weights[i].get(n) == after['positive_weight_vectors'][i].get(n) for n in weights[i] if n not in names)
assert len(changed) > 0
dump(f'ITERATION_{iteration}_WEIGHTS.json', {
    'source': ref(CURRENT), 'vertex_ids': changed, 'group_names': names,
    'candidate_group_weights': [[after['positive_weight_vectors'][i].get(n, 0.) for n in names] for i in changed],
    'brush_strength': strength, 'local_smooth_sweeps': sweeps,
    'brush_falloff': {str(i): brush[i] for i in changed},
    'geometry_local_m': original['coordinates_local_m'], 'geometry_unchanged': True,
    'protected_payload_without_weights_hash': digest(protected_without_weights(original)),
    'outside_scope_weights_exact': True, 'non_thumb_wrist_columns_exact': True,
    'dorsal54_palmar16_normal69_and_boundary_unchanged': True,
    'scope': 'PALMAR_THENAR_OPPOSITION_REGION plus compact one-region transition',
    'method': 'Local one-ring weight smooth + compact regional blend; only WRIST / THUMB CMC / MCP / IP existing groups',
    'candidate_blend_saved': False,
})
# Fresh baseline and tuned evaluation, sharing the exact previous review cameras.
cameras = G['cameras']; views = ['HUMAN_PALMAR', 'THENAR_CLOSE', 'SIDE_VOLUME']
records = []; safety = []; resets = []; coordinates = {}
for label in ['BASELINE', 'TUNED']:
    ob, rig = open_asset(CURRENT)
    if label == 'TUNED': apply_weights(ob, changed, names, [[after['positive_weight_vectors'][i].get(n, 0.) for n in names] for i in changed])
    renderer = Renderer(cameras, f'iteration_{iteration}_renders')
    rows, coords, rr = sample(ob, rig, label, renderer, views)
    renderer.dispose(); records.extend(renderer.records); safety.extend(rows); resets.extend(rr); coordinates[label] = coords
dump(f'ITERATION_{iteration}_PREVIEW.json', {'renders': records, 'machine_rows': safety, 'resets': resets,
     'coordinates': coordinates, 'ZERO_native_geometry_exact': True, 'production_saves': 0, 'candidate_saves': 0})
print('WEIGHT_PREVIEW_READY', iteration, 'changed vertices', len(changed), 'geometry writes 0; ZERO restored', flush=True)
