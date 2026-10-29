"""Coarse overview strip of the close view, used only to locate which frames deserve
full-resolution reading. It is a viewing aid, not a defect detector: no threshold,
no score, no millisecond claim.
"""
import sys
from PIL import Image, ImageDraw
from pathlib import Path

OUT = Path(__file__).resolve().parent
VIEW = sys.argv[1] if len(sys.argv) > 1 else 'REASONABLE_CLOSE_VIEW'
PER = 42
COLS, ROWS = 6, 7
TW, TH = 260, 244

for k in range(5):
    start = k * PER + 1
    cv = Image.new('RGB', (COLS * TW, ROWS * TH), (21, 28, 35))
    d = ImageDraw.Draw(cv)
    for j in range(PER):
        f = start + j
        if f > 210:
            break
        x = (j % COLS) * TW
        y = (j // COLS) * TH
        im = Image.open(OUT / 'product_views' / f'BASELINE_FROZEN__F{f:03}__{VIEW}.png').convert('RGB')
        im.thumbnail((TW, TH - 18))
        cv.paste(im, (x, y + 18))
        d.text((x + 4, y + 3), f'F{f:03} t={11.5 + (f - 1) / 30:.2f}s', fill='white')
    cv.save(OUT / f'OVERVIEW_{VIEW}_P{k + 1}.png')
    print('OVERVIEW', VIEW, k + 1, flush=True)
print('OVERVIEW_READY')