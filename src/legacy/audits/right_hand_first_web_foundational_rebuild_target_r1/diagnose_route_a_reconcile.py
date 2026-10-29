"""Read-only probe 6: reconcile this round's density diagnosis with route A's failure.

This round measured that at F130 a 3.5 mm edge absorbs ~25 mm of differential
(7.16x). Route A refined the same 120-quad layout into ~507 quads and the visible
notch remained. Those two facts cannot both be explained by "the grid is too
coarse", so one of the two readings must be wrong.

This probe measures route A's actual edge stretch at the same frames, on the
existing DESIGN_ONLY POC file, without modifying it. It answers one question only:
did refinement actually reduce the differential, or did the added resolution fail
to help because the deformation field itself is not grid-limited?

Read-only. The POC file is opened, never saved.
"""
import sys, json, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *

FRAMES = [110, 127, 130, 160, 176, 205]
POC = ROOT / 'audits/first_web_deformation_architecture_rebuild_assessment_r1/ROUTE_A_LOCAL_RETOPOLOGY_POC_R1.blend'
POC_SHA = read(ROOT / 'audits/first_web_deformation_architecture_rebuild_assessment_r1/ROUTE_A_BUILD_R1.json')['sha256']


def stretch_of(ob, rig, frame):
    m.reset_pose(rig)
    rig.animation_data.action = bpy.data.actions[ACTION]
    for t in rig.animation_data.nla_tracks:
        t.mute = False
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()
    rest = None
    neutral(rig)
    rest = coords(ob)
    motion(rig, frame)
    P = coords(ob)
    edges = np.array([list(e.vertices) for e in ob.data.edges])
    d = (P[edges[:, 0]] - P[edges[:, 1]])
    r = (rest[edges[:, 0]] - rest[edges[:, 1]])
    dl = np.linalg.norm(d, axis=1)
    rl = np.linalg.norm(r, axis=1)
    ratio = dl / np.maximum(rl, 1e-12)
    return rest, P, edges, ratio, rl


def run():
    before = protected_inputs()
    verify_inputs(before)
    assert sha(POC) == POC_SHA, 'ROUTE A POC HASH CHANGED'
    original_sha = sha(BASE)

    rows = []
    for label, path in [('BASELINE_FROZEN', BASE), ('ROUTE_A_REFINED_POC', POC)]:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False, use_scripts=False)
        ob = bpy.data.objects[m.MESH_NAME]
        rig = bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
        with bpy.data.libraries.load(str(SOURCE), link=False) as (s, d):
            d.actions = [ACTION]
        rig.animation_data_create()
        rig.animation_data.action = bpy.data.actions[ACTION]
        bpy.data.actions[ACTION].use_fake_user = True
        assert digest(action_payload(bpy.data.actions[ACTION])) == APPROVED_ACTION_SHA

        for f in FRAMES:
            neutral(rig)
            rest = coords(ob)
            motion(rig, f)
            P = coords(ob)
            edges = np.array([list(e.vertices) for e in ob.data.edges])
            d = P[edges[:, 0]] - P[edges[:, 1]]
            r = rest[edges[:, 0]] - rest[edges[:, 1]]
            dl = np.linalg.norm(d, axis=1)
            rl = np.linalg.norm(r, axis=1)
            ratio = dl / np.maximum(rl, 1e-12)
            rows.append({'asset': label, 'frame': f, 'vertices': len(ob.data.vertices),
                         'edges': len(edges),
                         'edge_rest_median_mm': round(float(np.median(rl)) * 1000, 4),
                         'ratio_median': round(float(np.median(ratio)), 3),
                         'ratio_p99': round(float(np.percentile(ratio, 99)), 3),
                         'ratio_max': round(float(ratio.max()), 3),
                         'edges_above_2x': int((ratio > 2).sum()),
                         'edges_above_4x': int((ratio > 4).sum()),
                         'corrective': values(ob)})
            print('RECON', label, f, 'v', len(ob.data.vertices), 'edgeMed', rows[-1]['edge_rest_median_mm'],
                  'max', rows[-1]['ratio_max'], '>2x', rows[-1]['edges_above_2x'], flush=True)
        neutral(rig)

    assert sha(BASE) == original_sha
    verify_inputs(before)
    out = {'phase': PHASE, 'mode': 'READ_ONLY_ROUTE_A_RECONCILIATION', 'blend_written': False,
           'route_a_poc_sha256': POC_SHA,
           'frozen_baseline_sha256': sha(BASE),
           'rows': rows,
           'reading': 'Compare per-asset ratio_p99 and ratio_max at the same frame. If refinement cut the stretch as a density story predicts, route A should have improved these numbers even though the visible notch persisted.'}
    dump('ROUTE_A_RECONCILIATION_R1.json', out)
    print('RECON_READY')


run()