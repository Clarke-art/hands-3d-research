from pathlib import Path
from PIL import Image, ImageDraw
OUT=Path(__file__).resolve().parent
conditions=['BASELINE','INDEX_ABD_OFF','INDEX_FLEX_OFF','THUMB_CMC_SWING_OFF','THUMB_MCP_FLEX_OFF']
views=['PALMAR_THENAR_CLOSE','FIRST_WEB_OBLIQUE']
for f in [130,76,205,31,61]:
    canvas=Image.new('RGB',(1700,672),(24,30,37))
    d=ImageDraw.Draw(canvas)
    for y,view in enumerate(views):
        for x,condition in enumerate(conditions):
            p=OUT/'renders'/f'{condition}__F{f:03}__{view}.png'
            im=Image.open(p).convert('RGB');im.thumbnail((340,312))
            canvas.paste(im,(x*340,y*336+24))
            d.text((x*340+5,y*336+5),f'F{f} {condition}',fill='white')
    canvas.save(OUT/f'INSPECTION_F{f:03}.png')
