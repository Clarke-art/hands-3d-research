"""Build contact sheets only (run under Blender's bundled Python, which has PIL).

Sheets exist so a Human can read continuous motion instead of a single still.
No detection heuristic, no severity census, no millisecond locator.
"""
from PIL import Image, ImageDraw
from pathlib import Path

OUT = Path(__file__).resolve().parent
VIEWS = ['DEFAULT_TEACHING_VIEW', 'NORMAL_ORBIT_VIEW', 'REASONABLE_CLOSE_VIEW']

for v in VIEWS:
    for s in range(7):
        cv = Image.new('RGB', (1800, 1520), (21, 28, 35))
        d = ImageDraw.Draw(cv)
        for j in range(30):
            f = s * 30 + j + 1
            if f > 210:
                break
            x = (j % 6) * 300
            y = (j // 6) * 152
            im = Image.open(OUT / 'product_views' / f'BASELINE_FROZEN__F{f:03}__{v}.png').convert('RGB')
            im.thumbnail((300, 128))
            cv.paste(im, (x, y + 20))
            d.text((x + 4, y + 2), f'F{f:03} t={11.5 + (f - 1) / 30:.2f}s', fill='white')
        cv.save(OUT / f'SHEET_{v}_Q{s + 1}.png')
        print('SHEET', v, s + 1, flush=True)
print('SHEETS_READY')