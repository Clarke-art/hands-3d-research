import bpy
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *
sys.path.append(str(R1_DIR))
from blender_extract import mesh_payload, rig_payload, weights

assert not CANDIDATE.exists(), 'FAIL_CLOSED never overwrite an R2 candidate'
assert sha(R1) == EXPECTED_R1 and sha(RECON / 'SKIN_WRITE_SCOPE_AMENDMENT_R2_PROPOSAL.json') == EXPECTED_PROPOSAL
approval = read(OUT / 'HUMAN_AMENDMENT_AND_INPUT_VERIFICATION_R2.json')
assert sha(RESPONSE) == approval['approval_sha256']
payload = read(OUT / 'CANDIDATE_WEIGHT_PAYLOAD_R2.json')
assert digest(payload['weights']) == payload['vector_hash']
source = read(R1_DIR / 'CANDIDATE_CLEAN_REOPEN_PAYLOAD_R1.json')
scope = read(OUT / 'AUTHORIZED_WEIGHT_WRITE_SET_R2.json')
write_ids = scope['approved_write_universe_317']
assert set(write_ids) == set(payload['authorized_write_ids']) and len(write_ids) == 317
bpy.ops.wm.open_mainfile(filepath=str(R1), load_ui=False, use_scripts=False)
ob = bpy.data.objects['Hand  - Realistic']
rig = bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
assert mesh_payload(ob) == source['mesh'] and rig_payload(rig) == source['rig']
assert weights(ob) == source['weights']
assert [g.name for g in ob.vertex_groups] == source['group_order']
VG = {g.name: g for g in ob.vertex_groups}
# Only approved317 IDs are passed to any vertex-group mutation. Outside IDs are never written.
for group in ob.vertex_groups:
    group.remove(write_ids)
for i in write_ids:
    for group, value in payload['weights'][i].items():
        assert group in VG and value > 0
        VG[group].add([i], value, 'REPLACE')
actual = weights(ob)
assert actual == payload['weights'], 'FAIL_CLOSED Blender float32 pre-save drift'
assert mesh_payload(ob) == source['mesh'] and rig_payload(rig) == source['rig']
pre = {'candidate_path': str(CANDIDATE.relative_to(ROOT)), 'source_R1_sha256': EXPECTED_R1,
       'mesh': mesh_payload(ob), 'rig': rig_payload(rig), 'weights': actual,
       'group_order': [g.name for g in ob.vertex_groups], 'vector_hash': digest(actual),
       'procedural_vertex_group_write_ids': write_ids, 'outside_write_calls': 0,
       'pose_evaluations': 0, 'deformation_runs': 0, 'Stage6_runs': 0}
dump('R2_CANDIDATE_PRE_SAVE_PAYLOAD.json', pre)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE), copy=True, compress=False)
assert sha(R1) == EXPECTED_R1
dump('R2_CANDIDATE_SAVE_RECORD.json', {'status': 'SAVED_PENDING_CLEAN_REOPEN', 'candidate_path': str(CANDIDATE.relative_to(ROOT)),
                                     'candidate_sha256': sha(CANDIDATE), 'bytes': CANDIDATE.stat().st_size,
                                     'R2_blend_writes': 1, 'historical_blend_writes': 0, 'outside317_write_calls': 0,
                                     'deformation_runs': 0, 'Stage6_runs': 0})
print('Independent R2 candidate saved SHA256', sha(CANDIDATE), flush=True)
