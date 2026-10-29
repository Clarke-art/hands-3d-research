import bpy
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *
sys.path.append(str(R1_DIR))
from blender_extract import mesh_payload, rig_payload, weights

record = read(OUT / 'R2_CANDIDATE_SAVE_RECORD.json')
assert sha(CANDIDATE) == record['candidate_sha256']
bpy.ops.wm.open_mainfile(filepath=str(CANDIDATE), load_ui=False, use_scripts=False)
ob = bpy.data.objects['Hand  - Realistic']
rig = bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
post = {'candidate_path': str(CANDIDATE.relative_to(ROOT)), 'candidate_sha256': sha(CANDIDATE),
        'mesh': mesh_payload(ob), 'rig': rig_payload(rig), 'weights': weights(ob),
        'group_order': [g.name for g in ob.vertex_groups]}
pre = read(OUT / 'R2_CANDIDATE_PRE_SAVE_PAYLOAD.json')
checks = {key: post[key] == pre[key] for key in ['mesh', 'rig', 'weights', 'group_order']}
assert all(checks.values()), ('FAIL_CLOSED clean-reopen drift', checks)
assert sha(CANDIDATE) == record['candidate_sha256'] and sha(R1) == EXPECTED_R1
dump('R2_CANDIDATE_CLEAN_REOPEN_PAYLOAD.json', post)
dump('R2_SAVE_REOPEN_VERIFICATION.json', {'status': 'PASS', 'method': 'Independent factory-startup Blender clean reload with autoexec disabled; no save or pose evaluation',
                                      'candidate_path': str(CANDIDATE.relative_to(ROOT)), 'candidate_sha256': sha(CANDIDATE),
                                      'checks': checks, 'all_3416_vectors_exactly_preserved': True,
                                      'vector_hash': digest(post['weights']), 'serialization_drift': 0,
                                      'mesh_transforms_topology_UV_material_binding_exact': checks['mesh'],
                                      'all_21_bones_hierarchy_corrected_slots_exact': checks['rig'],
                                      'deformation_runs': 0, 'Stage6_runs': 0, 'R1_blend_writes': 0, 'R2_blend_writes': 0})
print('R2 clean reopen PASS: all3416 vectors / geometry / 21bones exact', flush=True)
