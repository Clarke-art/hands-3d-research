"""Presentation-only contact sheets; originals remain the render evidence."""
import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
M = json.loads((OUT / 'MATCHED_RENDER_MANIFEST_R1.json').read_text(encoding='utf-8'))
lookup = {(r['asset'], r['pose'], r['view']): r['path'] for r in M['renders']}
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 15)
(OUT / 'inspection_sheets').mkdir(exist_ok=True)
def sheet(name, rows, width):
    cells = []
    for row in rows:
        rr = []
        for key in row:
            im = Image.open(OUT / lookup[key]).convert('RGB')
            im = im.resize((width, round(im.height * width / im.width)), Image.Resampling.LANCZOS)
            cell = Image.new('RGB', (width, im.height + 44), '#15191e')
            ImageDraw.Draw(cell).text((7, 5), key[0] + ' / ' + key[1] + '\n' + key[2], font=font, fill='#eaf0f7')
            cell.paste(im, (0, 44)); rr.append(cell)
        cells.append(rr)
    canvas = Image.new('RGB', (width * max(map(len, cells)), sum(max(c.height for c in row) for row in cells)), '#15191e')
    y = 0
    for row in cells:
        for x, im in enumerate(row): canvas.paste(im, (x * width, y))
        y += max(c.height for c in row)
    canvas.save(OUT / 'inspection_sheets' / (name + '.png'))

assets = [('OFFICIAL_L1', 'NEUTRAL'), ('CURRENT', 'ZERO'), ('CANDIDATE', 'ZERO')]
for name, views in [('STATIC_MAIN', ['HUMAN_PALMAR', 'FULL_PALM', 'THENAR_CLOSE']),
                    ('STATIC_WEB_SIDE', ['SIDE_VOLUME', 'SILHOUETTE', 'FIRST_WEB_CLOSE'])]:
    sheet(name, [[(a, p, v) for a, p in assets] for v in views], 420)
for pose in ['FULL_OPP_L1', 'FULL_OPP_L2', 'FULL_OPP_L3']:
    sheet(pose, [[(a, pose, v) for a in ['CURRENT', 'CANDIDATE']]
                 for v in ['HUMAN_PALMAR', 'THENAR_CLOSE', 'SIDE_VOLUME', 'FULL_PALM']], 520)
sheet('REGRESSION_SENTINELS', [[(a, 'ZERO', v) for a in ['CURRENT', 'CANDIDATE']]
      for v in ['DORSAL54_SENTINEL', 'PALMAR16_SENTINEL']], 520)
print('Six ordinary-render inspection sheets cover all 46 final images')
