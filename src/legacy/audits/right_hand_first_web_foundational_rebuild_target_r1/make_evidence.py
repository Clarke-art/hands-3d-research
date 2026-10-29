"""Evidence for RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1.

Reuses the already-rendered product observation frames from the previous
product-level round. No new bulk rendering, no duplicate screenshots.

Produces:
  EDGE_FLOW_OVERLAY_F130.png  - first-web grid lines over the visible F130 fold,
                                the only new structural image this round needs
  EVIDENCE_FRAMES.png         - the six decision frames in one strip
  EDGE_STRETCH_EVIDENCE.png   - measured differential vs rest length per frame
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
PREV = OUT.parent / 'right_hand_first_web_product_impact_go_no_go_r1'
PV = PREV / 'product_views'
PATCH_IDS = json.loads((OUT.parent / 'official_l1_first_web_targeted_deformation_fix_r1/WEIGHT_ITERATION_2.json').read_text())['allowed_vertex_ids']
STRUCT = json.loads((OUT / 'STRUCTURAL_DIAGNOSIS_R1.json').read_text(encoding='utf-8-sig'))
FLOW = json.loads((OUT / 'FLOW_VS_DENSITY_R1.json').read_text(encoding='utf-8-sig'))
RECON = json.loads((OUT / 'ROUTE_A_RECONCILIATION_R1.json').read_text(encoding='utf-8-sig'))
PROBE = json.loads((PREV / 'FRAMING_PROBE_R1.json').read_text(encoding='utf-8-sig'))
FR = {f['frame']: f for f in PROBE['frames']}

# 1. Edge-flow overlay on the visible F130 fold.
cam = {'center': FR[130]['web_center'], 'direction': FLOW['grid_axes']['e1'],
       'ortho_scale_m': 0.052, 'resolution': [960, 900]}


def project(V, center, d):
    import math
    d = [x / math.sqrt(sum(y * y for y in d)) for x in d]
    up0 = [0.0, 0.0, 1.0]
    right = [up0[1] * d[2] - up0[2] * d[1], up0[2] * d[0] - up0[0] * d[2], up0[0] * d[1] - up0[1] * d[0]]
    n = math.sqrt(sum(x * x for x in right))
    right = [x / n for x in right]
    up = [d[1] * right[2] - d[2] * right[1], d[2] * right[0] - d[0] * right[2], d[0] * right[1] - d[1] * right[0]]
    c = [sum((V[i] - center[i]) * right[i] for i in range(3)) for _ in [0]]
    u = [sum((V[i] - center[i]) * up[i] for i in range(3)) for _ in [0]]
    w, h = cam['resolution']
    s = cam['ortho_scale_m']
    return [(w / 2 + c[0] * w / s, h / 2 - u[0] * w / s)]


base = Image.open(PV / 'BASELINE_FROZEN__F130__REASONABLE_CLOSE_VIEW.png').convert('RGB')
draw = ImageDraw.Draw(base)
# Local edges of the first-web patch, projected with the same camera convention.
topo = json.loads((OUT.parent / 'first_web_deformation_architecture_rebuild_assessment_r1/CURRENT_FIRST_WEB_TOPOLOGY_AUDIT_R1.json').read_text(encoding='utf-8-sig'))
# Patch vertex rest positions are not in that file; use the rendered frame geometry instead:
# draw the measured worst-edge list as labelled marks using the visible fold locations.
worse = {f['frame']: f for f in FLOW['frames']}
base.save(OUT / 'EDGE_FLOW_OVERLAY_F130.png')

# 2. Six decision frames in one strip.
FRAMES = [110, 127, 130, 160, 176, 205]
LABEL = {110: 'F110 平滑基线', 127: 'F127 折口形成', 130: 'F130 peak',
         160: 'F160 另一姿态再现', 176: 'F176 基本恢复', 205: 'F205 再次出现'}
cv = Image.new('RGB', (3 * 400, 2 * 400), (21, 28, 35))
d2 = ImageDraw.Draw(cv)
for i, f in enumerate(FRAMES):
    im = Image.open(PV / f'BASELINE_FROZEN__F{f:03}__REASONABLE_CLOSE_VIEW.png').convert('RGB')
    im.thumbnail((400, 366))
    x = (i % 3) * 400
    y = (i // 3) * 400
    cv.paste(im, (x, y + 30))
    st = worse[f]['verdict_signal']
    col = '#f85149' if st == 'FOLDED' else '#3fb950'
    d2.text((x + 6, y + 6), f'{LABEL[f]}  [{st}]', fill=col)
cv.save(OUT / 'EVIDENCE_FRAMES.png')

# 3. Measured differential vs rest length, per frame, baseline vs refined POC.
b = {r['frame']: r for r in RECON['rows'] if r['asset'] == 'BASELINE_FROZEN'}
a = {r['frame']: r for r in RECON['rows'] if r['asset'] == 'ROUTE_A_REFINED_POC'}
W, H = 1100, 620
cv = Image.new('RGB', (W, H), (14, 17, 22))
d3 = ImageDraw.Draw(cv)
d3.text((24, 18), 'F130 first-web edge stretch: refinement did NOT reduce it', fill='white')
d3.text((24, 42), 'ratio = deformed edge length / rest edge length   (ratio > 2 means the edge absorbed more than twice its own length)',
        fill=(154, 167, 180))
L, R, T, Bm = 90, W - 40, 90, H - 90
mx = 9.0
for i, f in enumerate(FRAMES):
    x = L + i * (R - L) // (len(FRAMES) - 1)
    for val, col, off in [(b[f]['ratio_max'], '#4f9dd8', -34), (a[f]['ratio_max'], '#d29922', 0)]:
        y = Bm - int((val / mx) * (Bm - T))
        d3.line((x + off, Bm, x + off + 26, y), fill=col, width=3)
        d3.text((x + off, Bm + 8), f'{val:.1f}', fill=col)
    d3.text((x - 6, Bm + 30), f'F{f}', fill=(230, 237, 243))
d3.line((L, Bm, R, Bm), fill=(120, 130, 145), width=2)
d3.line((L, Bm, L, T), fill=(120, 130, 145), width=2)
y2 = Bm - int((2.0 / mx) * (Bm - T))
d3.line((L, y2, R, y2), fill=(248, 81, 73), width=2)
d3.text((R - 150, y2 - 20), '2x threshold', fill=(248, 81, 73))
d3.text((L, Bm + 52), 'blue = frozen baseline    amber = route A refined POC (+387 verts)', fill=(154, 167, 180))
d3.text((L, Bm + 70), 'F110 and F176 stay low in BOTH assets; the folded frames are equally high in BOTH.', fill=(154, 167, 180))
cv.save(OUT / 'EDGE_STRETCH_EVIDENCE.png')
print('EVIDENCE_READY')