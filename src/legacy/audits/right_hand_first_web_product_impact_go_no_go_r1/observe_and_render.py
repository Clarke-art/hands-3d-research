"""Product-level observation render: 210 frames x 3 product views, frozen baseline, read-only.

No .blend is written. Mesh / topology / weights / bones / rest pose / corrective /
driver / Action / retarget mapping are all untouched. Only the already-approved
Action is appended as a library datablock for playback.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *

VIEWS = ['DEFAULT_TEACHING_VIEW', 'NORMAL_ORBIT_VIEW', 'REASONABLE_CLOSE_VIEW']
# Camera directions are reused verbatim from already-approved mature project cameras.
# No new extreme or forensic angle is invented.
DIR_TEACHING = [-0.38183954, -0.92405248, 0.0180442]        # approved PALMAR_THENAR_CLOSE / PALMAR_FULL axis
DIR_ORBIT = [0.19980031, -0.93906146, 0.27972043]          # approved FIRST_WEB_OBLIQUE axis
PROBE = read(OUT / 'FRAMING_PROBE_R1.json')
FR = {f['frame']: f for f in PROBE['frames']}


def product_cameras(frame):
    f = FR[frame]
    hand = f['hand_center']
    web = f['web_center']
    mid = [(hand[i] * 0.45 + web[i] * 0.55) for i in range(3)]
    return {
        'DEFAULT_TEACHING_VIEW': {
            'center': hand, 'direction': DIR_TEACHING,
            'ortho_scale_m': 0.42, 'resolution': [960, 900]},
        'NORMAL_ORBIT_VIEW': {
            'center': mid, 'direction': DIR_ORBIT,
            'ortho_scale_m': 0.22, 'resolution': [960, 900]},
        'REASONABLE_CLOSE_VIEW': {
            'center': mid, 'direction': DIR_ORBIT,
            'ortho_scale_m': 0.115, 'resolution': [960, 900]},
    }


def main():
    before = protected_inputs()
    verify_inputs(before)
    ob, rig = open_frozen()
    neutral(rig)
    V0 = coords(ob)
    initial_shape = shape_state(ob)
    faces = [tuple(p.vertices) for p in ob.data.polygons]
    edges = np.array([list(e.vertices) for e in ob.data.edges])
    tris = np.array([[f[0], f[j], f[j + 1]] for f in faces for j in range(1, len(f) - 1)])
    owners = np.array([i for i, f in enumerate(faces) for j in range(1, len(f) - 1)])

    def areas(v):
        a = np.linalg.norm(np.cross(v[tris[:, 1]] - v[tris[:, 0]], v[tris[:, 2]] - v[tris[:, 0]]), axis=1) * .5
        return np.bincount(owners, weights=a, minlength=len(faces))

    A0 = areas(V0)

    def safety(v):
        a = areas(v)
        length = np.linalg.norm(v[edges[:, 0]] - v[edges[:, 1]], axis=1)
        return {'NaN_Inf': int((~np.isfinite(v)).sum()),
                'collapsed_faces': int(((a <= 1e-12) | (a / A0 <= 1e-6)).sum()),
                'degenerate_edges': int((length <= 1e-12).sum())}

    rr = m.Renderer(product_cameras(1), 'product_views')
    rr.sc.display.shading.shadow_intensity = 0
    rows = []
    records = []
    for f in range(1, 211):
        cams = product_cameras(f)
        motion(rig, f)
        V, F = m.evaluate(ob, ob.matrix_world)
        VA = np.array([list(v) for v in V])
        ch = safety(VA)
        rr.cameras = cams
        rr.draw('BASELINE_FROZEN', f'F{f:03}', V, F, VIEWS)
        rows.append({'frame': f, 'source_frame': 690 + 2 * (f - 1),
                     'time_seconds': 11.5 + (f - 1) / 30.0,
                     'minimum_machine_safety': ch,
                     'approved_corrective_natural_values': values(ob),
                     'cameras': cams})
        if f % 15 == 0:
            print('PRODUCT_RENDER_PROGRESS', f, '/210', flush=True)
    rr.dispose()

    # second half-frame samples: safety only, no extra renders
    for i in range(421):
        if i % 2 == 0:
            continue
        f = 1 + i // 2
        motion(rig, f, (i % 2) / 2)
        rows.append({'frame': f, 'subframe': (i % 2) / 2, 'observation': i,
                     'source_frame': 690 + i, 'time_seconds': 11.5 + i / 60.0,
                     'minimum_machine_safety': safety(coords(ob)),
                     'approved_corrective_natural_values': values(ob),
                     'renders': []})
        if i % 60 == 1:
            print('SUBFRAME_SAFETY_PROGRESS', i, '/421', flush=True)

    neutral(rig)
    restore = float(np.linalg.norm(coords(ob) - V0, axis=1).max() * 1000)
    assert restore < 0.001
    assert shape_state(ob) == initial_shape
    assert digest(action_payload(bpy.data.actions[ACTION])) == APPROVED_ACTION_SHA
    verify_inputs(before)
    assert sha(BASE) == FROZEN_SHA

    full = [r for r in rows if 'observation' not in r]
    obs_all = [r for r in rows if r.get('observation') is not None or 'observation' not in r]
    maximum = {k: max(r['minimum_machine_safety'][k] for r in obs_all) for k in ['NaN_Inf', 'collapsed_faces', 'degenerate_edges']}
    assert all(v == 0 for v in maximum.values()), maximum

    dump('PRODUCT_VIEW_OBSERVATION_R1.json', {
        'status': 'PASS',
        'phase': PHASE,
        'mode': 'OBSERVATION_ONLY_NO_ASSET_MODIFICATION',
        'frozen_baseline': BASE.relative_to(ROOT).as_posix(),
        'frozen_baseline_sha256': sha(BASE),
        'action': ACTION,
        'action_payload_sha256': digest(action_payload(bpy.data.actions[ACTION])),
        'sample': 'PIANOVAM v1.2 INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY CC BY-NC-SA 4.0',
        'window_seconds': [11.5, 18.5],
        'duration_seconds': 7,
        'observations_safety_sampled': 421,
        'rendered_frames_per_view': TOTAL_FRAMES,
        'views': VIEWS,
        'camera_authority': 'Directions reused verbatim from approved mature project cameras (PALMAR_THENAR_CLOSE axis, FIRST_WEB_OBLIQUE axis). Only product-level framing distance/center differs. No new forensic angle.',
        'minimum_machine_safety_maximum': maximum,
        'ZERO_restore': 'PASS',
        'ZERO_restore_max_mm': restore,
        'blend_files_written': 0,
        'new_weight_candidate': 0, 'new_corrective_candidate': 0, 'new_retopo_candidate': 0,
        'new_helper_candidate': 0, 'new_cage_candidate': 0,
        'forbidden_forensics_run': False,
        'inputs_unchanged': before,
        'frames': rows,
    })
    print('PRODUCT_VIEW_OBSERVATION_READY', maximum, flush=True)


main()