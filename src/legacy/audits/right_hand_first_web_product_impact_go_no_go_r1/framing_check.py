"""Framing check: 3 product views on 3 sample frames only. Read-only, no blend written."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *
import importlib.util
spec = importlib.util.spec_from_file_location('obs', OUT / 'observe_and_render.py')

VIEWS = ['DEFAULT_TEACHING_VIEW', 'NORMAL_ORBIT_VIEW', 'REASONABLE_CLOSE_VIEW']
DIR_TEACHING = [-0.38183954, -0.92405248, 0.0180442]
DIR_ORBIT = [0.19980031, -0.93906146, 0.27972043]
PROBE = read(OUT / 'FRAMING_PROBE_R1.json')
FR = {f['frame']: f for f in PROBE['frames']}


def product_cameras(frame):
    f = FR[frame]
    hand = f['hand_center']
    web = f['web_center']
    mid = [(hand[i] * 0.35 + web[i] * 0.65) for i in range(3)]
    return {
        'DEFAULT_TEACHING_VIEW': {'center': hand, 'direction': DIR_TEACHING,
                                  'ortho_scale_m': 0.42, 'resolution': [960, 900]},
        'NORMAL_ORBIT_VIEW': {'center': mid, 'direction': DIR_ORBIT,
                              'ortho_scale_m': 0.22, 'resolution': [960, 900]},
        'REASONABLE_CLOSE_VIEW': {'center': mid, 'direction': DIR_ORBIT,
                                  'ortho_scale_m': 0.115, 'resolution': [960, 900]},
    }


ob, rig = open_frozen()
neutral(rig)
rr = m.Renderer(product_cameras(1), 'framing_check')
rr.sc.display.shading.shadow_intensity = 0
for f in [30, 130, 200]:
    motion(rig, f)
    V, F = m.evaluate(ob, ob.matrix_world)
    rr.cameras = product_cameras(f)
    rr.draw('CHECK', f'F{f:03}', V, F, VIEWS)
rr.dispose()
neutral(rig)
print('FRAMING_CHECK_READY')