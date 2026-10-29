import sys, json, copy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *

# READ-ONLY probe: no blend is written. Determine product-level framing from the
# frozen baseline evaluated across the same 7-second PianoVAM sample.
probe = {'status': 'READ_ONLY_PROBE', 'blend_written': False, 'frames': []}
before = protected_inputs()
verify_inputs(before)
ob, rig = open_frozen()
neutral(rig)
V0 = coords(ob)
probe['zero_bbox'] = {'min': V0.min(0).tolist(), 'max': V0.max(0).tolist()}
web = np.array([list(ob.matrix_world @ ob.data.vertices[i].co) for i in PATCH_IDS])
probe['patch_ids_count'] = len(PATCH_IDS)
probe['zero_patch_bbox'] = {'min': web.min(0).tolist(), 'max': web.max(0).tolist()}

for f in range(1, 211):
    motion(rig, f)
    V = coords(ob)
    w = V[PATCH_IDS]
    probe['frames'].append({
        'frame': f,
        'source_frame': 690 + 2 * (f - 1),
        'time_seconds': 11.5 + (f - 1) / 30.0,
        'hand_bbox_min': V.min(0).tolist(),
        'hand_bbox_max': V.max(0).tolist(),
        'hand_center': ((V.min(0) + V.max(0)) / 2).tolist(),
        'hand_extent': (V.max(0) - V.min(0)).tolist(),
        'web_center': ((w.min(0) + w.max(0)) / 2).tolist(),
        'web_extent': (w.max(0) - w.min(0)).tolist(),
    })
    if f % 30 == 0:
        print('PROBE_PROGRESS', f, '/210', flush=True)
neutral(rig)
restore = float(np.linalg.norm(coords(ob) - V0, axis=1).max() * 1000)
probe['ZERO_restore_max_mm'] = restore
probe['ZERO_restore'] = 'PASS' if restore < 0.001 else 'FAIL'
assert restore < 0.001
probe['action_payload_sha256'] = digest(action_payload(bpy.data.actions[ACTION]))
assert probe['action_payload_sha256'] == APPROVED_ACTION_SHA
probe['inputs_unchanged'] = before
verify_inputs(before)
probe['frozen_baseline_sha256'] = sha(BASE)
assert probe['frozen_baseline_sha256'] == FROZEN_SHA
probe['blend_written'] = False
dump('FRAMING_PROBE_R1.json', probe)
print('FRAMING_PROBE_READY')