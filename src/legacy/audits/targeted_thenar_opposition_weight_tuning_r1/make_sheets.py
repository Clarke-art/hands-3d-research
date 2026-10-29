import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
OUT = Path(__file__).resolve().parent
(OUT / 'inspection_sheets').mkdir(exist_ok=True)
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 16)
def sheet(name, pose, views):
    rows = []
    for view in views:
        cells = []
        for asset in ['BASELINE', 'TUNED']:
            im = Image.open(OUT / 'renders' / f'{asset}__{pose}__{view}.png').convert('RGB')
            im = im.resize((520, round(im.height * 520 / im.width)), Image.Resampling.LANCZOS)
            cell = Image.new('RGB', (520, im.height + 44), '#15191e')
            ImageDraw.Draw(cell).text((8, 4), f'{asset} / {pose}\n{view}', font=font, fill='#edf1f5')
            cell.paste(im, (0, 44)); cells.append(cell)
        rows.append(cells)
    canvas = Image.new('RGB', (1040, sum(row[0].height for row in rows)), '#15191e'); y = 0
    for row in rows:
        for j, im in enumerate(row): canvas.paste(im, (j * 520, y))
        y += row[0].height
    canvas.save(OUT / 'inspection_sheets' / f'{name}.png')
for pose in ['ZERO', 'FULL_OPP_L1', 'FULL_OPP_L2', 'FULL_OPP_L3']:
    sheet(pose, pose, ['HUMAN_PALMAR', 'THENAR_CLOSE', 'SIDE_VOLUME', 'FULL_PALM'])
sheet('SENTINELS', 'ZERO', ['DORSAL54_SENTINEL', 'PALMAR16_SENTINEL'])
print('Five sheets cover all 36 final ordinary renders')
