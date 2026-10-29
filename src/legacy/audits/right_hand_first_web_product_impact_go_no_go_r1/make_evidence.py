"""Small, purposeful evidence set: problem visible / peak / recovery, plus a
three-view strip at the peak. Deliberately few images, no repeated bulk screenshots.
"""
from PIL import Image, ImageDraw
from pathlib import Path

OUT = Path(__file__).resolve().parent
VIEWS = ['DEFAULT_TEACHING_VIEW', 'NORMAL_ORBIT_VIEW', 'REASONABLE_CLOSE_VIEW']

# Frames chosen by direct Human reading of the 7-second continuous close view,
# not by any automated severity score.
EVIDENCE = [
    ('PROBLEM_VISIBLE_F115', 115, '问题已出现，first-web 折口开始形成'),
    ('PROBLEM_PEAK_F130', 130, '本段最明显：拇指-食指间深折 + 上方尖角'),
    ('PROBLEM_PEAK_ALT_F160', 160, '不同姿态下再次出现深折，证明非单一姿态偶发'),
    ('PROBLEM_RECOVERY_F176', 176, '离开该姿态后折口基本消失，表面恢复平滑'),
    ('PROBLEM_RETURN_F205', 205, '回到张开姿态，折口再次出现（反复性证据）'),
]
for name, f, note in EVIDENCE:
    im = Image.open(OUT / 'product_views' / f'BASELINE_FROZEN__F{f:03}__REASONABLE_CLOSE_VIEW.png').convert('RGB')
    im.save(OUT / f'EVIDENCE_{name}.png')

# Peak frame across all three product views, side by side.
cv = Image.new('RGB', (3 * 640, 640), (21, 28, 35))
d = ImageDraw.Draw(cv)
for i, v in enumerate(VIEWS):
    im = Image.open(OUT / 'product_views' / f'BASELINE_FROZEN__F130__{v}.png').convert('RGB')
    im.thumbnail((640, 600))
    cv.paste(im, (i * 640, 34))
    d.text((i * 640 + 6, 10), v, fill='white')
cv.save(OUT / 'EVIDENCE_PEAK_F130_THREE_VIEWS.png')

# Peak vs recovery vs return, close view only.
cv = Image.new('RGB', (3 * 560, 580), (21, 28, 35))
d = ImageDraw.Draw(cv)
for i, (lbl, f) in enumerate([('F130 PEAK', 130), ('F176 RECOVERY', 176), ('F205 RETURN', 205)]):
    im = Image.open(OUT / 'product_views' / f'BASELINE_FROZEN__F{f:03}__REASONABLE_CLOSE_VIEW.png').convert('RGB')
    im.thumbnail((560, 540))
    cv.paste(im, (i * 560, 34))
    d.text((i * 560 + 6, 10), lbl, fill='white')
cv.save(OUT / 'EVIDENCE_CONTINUOUS_BEHAVIOUR.png')
print('EVIDENCE_READY')