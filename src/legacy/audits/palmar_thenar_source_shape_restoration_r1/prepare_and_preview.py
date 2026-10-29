"""Source profile restoration to a continuous local patch, without a blend save."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *
import numpy as np

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
strength = float(args[0]) if args else .42
iteration = args[1] if len(args) > 1 else '01'
assert sha(CURRENT) == EXPECTED
source_path = ROOT / 'references/licenses/blender_human_base_meshes/extracted/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend'
raw = read(LINEAGE / 'RAW_SOURCE_GEOMETRY.json')['stages']['OFFICIAL_L1']
assert sha(source_path) == raw['input']['sha256']
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=str(source_path), load_ui=False, use_scripts=False)
so = bpy.data.objects['Hand  - Realistic']; assert next(m for m in so.modifiers if m.type == 'MULTIRES').levels == 1
eo = so.evaluated_get(bpy.context.evaluated_depsgraph_get()); em = eo.to_mesh()
assert [list(v.co) for v in em.vertices] == raw['local_m'] and [list(p.vertices) for p in em.polygons] == raw['faces']
reg = read(LINEAGE / 'DONOR_TO_CURRENT_TOPOLOGY_CORRESPONDENCE_R1.json')['rigid_display_registration']
rot = Matrix(reg['rotation_row']).transposed(); translation = Vector(reg['translation_mm']) / MM
sourceV = [rot @ (so.matrix_world @ (Matrix.Diagonal((1., -1., -1.)) @ v.co)) + translation for v in em.vertices]
sourceF = [tuple(p.vertices) for p in em.polygons]; eo.to_mesh_clear()
ob, rig = open_asset(CURRENT); initial = snapshot(); V, F = evaluate(ob, ob.matrix_world)
E = [list(e.vertices) for e in ob.data.edges]; N = [ob.matrix_world.to_3x3() @ v.normal for v in ob.data.vertices]
regions_path = ROOT / 'production_spec/stage5_production_rig/stage5b_r1b/_tmp/R1B_REGIONS.json'
regions = read(regions_path)['regions']
d54_path = ROOT / 'production_spec/stage4_blender/stage4c_donor_transfer_r1/APPLICATION_WRITE_VERIFICATION_R1.json'
p16_path = ROOT / 'audits/palmar_digit_root_local_donor_shape_restoration_design_r1/PALMAR_ROOT_FORMAL_WRITE_SET_R1.json'
d54 = set(read(d54_path)['actual_changed_vertex_ids']); p16 = set(read(p16_path)['vertex_ids'])
normal69 = set(read(p16_path)['normal_locked_vertex_ids'])
protected = d54 | p16 | normal69
adj = [set() for _ in V]
for a, b in E: adj[a].add(b); adj[b].add(a)
# Protect the prior approved patch boundaries as well as their exact positions.
locked = protected | {j for i in protected for j in adj[i]}
D = Vector((.631289124, .775318801, -.0188387)).normalized(); Z = Vector((0, 0, 1))
X = D.cross(Z).normalized(); P = -D
W = rig.matrix_world @ rig.data.bones['WRIST_R'].head_local
coords = np.array([[(v - W).dot(a) * MM for a in (X, P, Z)] for v in V])

# Donor's lower thenar is placed at the current preserved lower thenar. Only
# a translation is added to the previous rigid registration; no donor shape edit.
anchors = [i for i in regions['THENAR_BASE'] if coords[i, 1] > 0 and 15 < coords[i, 2] < 35]
assert len(anchors) >= 5
anchor_shift = Vector(np.median(np.array([list(V[i] - sourceV[i]) for i in anchors]), axis=0))
placed_source = [v + anchor_shift for v in sourceV]

ancestry = read(LINEAGE / 'HISTORICAL_OPERATION_RAM_REPLAY.json')['final_ancestry']
base = read(LINEAGE / 'RAW_SOURCE_GEOMETRY.json')['stages']['STAGE4A_R2_BASE']
rest = read(LINEAGE / 'RAW_SOURCE_GEOMETRY.json')['stages']['STAGE4A_R2']
lookup = {tuple(p): i for i, p in enumerate(base['local_m'])}
# Existing, identity-verified native coordinates carry exact historical parentage.
known = {i: lookup[tuple(p)] for i, p in enumerate(rest['local_m']) if tuple(p) in lookup}
semantic = set(regions['THENAR_BASE']) | set(regions['THUMB_FIRST_METACARPAL']) | set(regions['FIRST_WEB'])
eligible = semantic.copy()
for _ in range(2): eligible |= {j for i in eligible for j in adj[i]}
profile_samples = []
profile_values = []
for i in sorted(eligible):
    if i not in known or not (25 < coords[i, 2] < 92): continue
    a = ancestry[known[i]]
    donor_point = sum((placed_source[int(k)] * float(w) for k, w in a.items()), Vector())
    delta = donor_point - V[i]
    profile_samples.append(list(V[i]))
    profile_values.append([max(0., delta.dot(X)), max(0., delta.dot(P))])
profile_samples = np.array(profile_samples)
profile_values = np.array(profile_values)
target = [v.copy() for v in V]; rows = []; core = []; transition = []; unknown_locked = []
for i in sorted(eligible - locked):
    x, palmar, z = coords[i]
    # Complete thenar/upper-root patch with a compact skirt, below four MCPs.
    radius = math.sqrt(((x - 31.) / 29.) ** 2 + ((z - 65.) / 34.) ** 2)
    spatial = 1. - smoothstep(.56, 1., radius)
    # Coordinate-depth skirt varies smoothly across existing creases. Do not
    # multiply by sharp per-vertex normal changes on the first-web floor.
    facing = smoothstep(-28., -6., palmar)
    proximal = smoothstep(30., 42., z)
    # Preserve the web opening and the thumb shaft above its floor.
    distal = 1. - smoothstep(60., 82., z)
    weight = strength * spatial * facing * proximal * distal
    if weight <= 1e-6: continue
    # Interpolate the donor-derived contour field, never the current mesh.
    # This also extends the same field across generated CMC transition vertices
    # without inventing an exact donor-ID correspondence there.
    distances2 = np.sum((profile_samples - np.array(V[i])) ** 2, axis=1)
    influence = np.exp(-distances2 / (2 * .009 ** 2))
    transverse, fullness = (influence @ profile_values) / influence.sum()
    contour_delta = X * transverse + P * fullness
    if contour_delta.length < 1e-8: continue
    target[i] = V[i] + contour_delta * weight
    a = ancestry[known[i]] if i in known else None
    rows.append({'vertex_id': i, 'historical_base_vertex_id': known.get(i), 'L1_parent_weights': a,
                 'blend_weight': weight, 'region_coords_mm': list(coords[i]),
                 'source_profile_field_extension': i not in known,
                 'transferred_profile_delta_m': list(contour_delta),
                 'candidate_world_m': list(target[i])})
    (core if spatial >= .65 and facing >= .65 else transition).append(i)
ids = [r['vertex_id'] for r in rows]
assert len(ids) >= 60 and not set(ids) & protected
inv = ob.matrix_world.inverted()
for i in ids: ob.data.vertices[i].co = inv @ target[i]
ob.data.update(); bpy.context.view_layer.update(); after = snapshot()
assert after['protected'] == initial['protected']
actual, actualF = evaluate(ob, ob.matrix_world)
changed = [i for i, (a, b) in enumerate(zip(initial['coordinates_local_m'], after['coordinates_local_m'])) if a != b]
assert changed == ids and actualF == F
automatic, _ = safety_check(actual, F, E)
assert automatic['automatic_status'] == 'PASS'
camera_old = read(OLD / 'RENDER_MANIFEST_R1.json')['cameras']
main = camera_old['HUMAN_MATCHED_PALMAR_OBLIQUE']
close_ids = [i for i in eligible if 32 < coords[i, 2] < 90 and i < 3300]
web_ids = [i for i in range(len(V)) if 12 < coords[i, 0] < 48 and -30 < coords[i, 1] < 10 and 65 < coords[i, 2] < 109]
cameras = {'HUMAN_PALMAR': main, 'FULL_PALM': camera_old['FULL_PALM'],
           'THENAR_CLOSE': frame([V[i] for i in close_ids] + [actual[i] for i in close_ids], main['direction'], [1200, 1000], scale=.115),
           'FIRST_WEB_CLOSE': frame([V[i] for i in web_ids], main['direction'], [1200, 1000], scale=.085),
           'SIDE_VOLUME': camera_old['VOLUME_SIDE_OBLIQUE'], 'SILHOUETTE': main}
dorsal = read(ROOT / 'production_spec/stage4_blender/stage4c_donor_transfer_r1/APPLICATION_MATCHED_REVIEW_GEOMETRY_R1.json')
cameras['DORSAL54_SENTINEL'] = {'center': [x / MM for x in dorsal['frame']['origin_world_mm']], 'direction': list(D), 'ortho_scale_m': .05, 'resolution': [1100, 1100]}
palcore = read(ROOT / 'audits/palmar_digit_root_local_donor_shape_restoration_design_r1/PALMAR_ROOT_DEFECT_CORE_R1.json')
palids = sorted(set(palcore['visible_upper_box_hit_vertex_ids']) | p16)
cameras['PALMAR16_SENTINEL'] = frame([V[i] for i in palids], -D, [1100, 1100], scale=.07)
dump(f'ITERATION_{iteration}_GEOMETRY.json', {'source': ref(CURRENT), 'donor': ref(source_path),
     'initial_local_m': initial['coordinates_local_m'], 'candidate_local_m': after['coordinates_local_m'],
     'current_world_m': [list(v) for v in V], 'candidate_world_m': [list(v) for v in actual],
     'donor_visual_world_m': [list(v) for v in sourceV], 'donor_faces': [list(f) for f in sourceF],
     'faces': [list(f) for f in F], 'edges': E, 'vertex_ids': ids, 'core_ids': core, 'transition_ids': transition,
     'protected_dorsal54': sorted(d54), 'protected_palmar16': sorted(p16), 'protected_normal69': sorted(normal69),
     'generated_CMC_field_extension_ids': [r['vertex_id'] for r in rows if r['source_profile_field_extension']], 'outside_write_set_position_drift': 0,
     'blend_strength': strength, 'lower_thenar_alignment_anchor_ids': anchors,
     'lower_thenar_source_placement_translation_m': list(anchor_shift),
     'method': 'Existing rigid source registration + preserved lower-thenar translation anchor; ancestry-derived donor transverse contour/palmar fullness field interpolated at 9mm support, then compact smooth regional blending; current RSSF axial arrangement and upper thumb shaft retained; no current-mesh smoothing',
     'per_vertex': rows, 'machine_static': automatic, 'cameras': cameras,
     'protected_payload_equal': True, 'protected_payload_hash': digest(initial['protected']),
     'helper_reuse': HELPERS, 'candidate_blend_saves': 0, 'production_saves': 0})
renderer = Renderer(cameras, f'iteration_{iteration}_renders')
views = ['HUMAN_PALMAR', 'THENAR_CLOSE', 'FIRST_WEB_CLOSE', 'SIDE_VOLUME', 'SILHOUETTE']
renderer.draw('CURRENT', 'ZERO', V, F, views)
renderer.draw('CANDIDATE', 'ZERO', actual, F, views)
dump(f'ITERATION_{iteration}_RENDER_MANIFEST.json', {'renders': renderer.records, 'candidate_blend_saved': False})
print('PREVIEW_READY', iteration, 'writes', len(ids), 'core', len(core), 'transition', len(transition), 'strength', strength, 'source_anchor_shift_mm', list(anchor_shift * MM), flush=True)
