import sys
from pathlib import Path
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parent
tag=sys.argv[1] if len(sys.argv)>1 else 'WEIGHT_1'
prefix=tag.lower()
views=['PALMAR_THENAR_CLOSE','FIRST_WEB_OBLIQUE']
for f in [130,76,205,31,61]:
    canvas=Image.new('RGB',(1280,1220),(21,28,35));d=ImageDraw.Draw(canvas)
    for y,v in enumerate(views):
        for x,(label,folder) in enumerate([('BEFORE','before_selected'),(tag,prefix+'_selected')]):
            im=Image.open(OUT/folder/f'{label}__F{f:03}__{v}.png').convert('RGB');im.thumbnail((640,586))
            canvas.paste(im,(x*640,y*610+24));d.text((x*640+6,y*610+5),f'{label} F{f} {v}',fill='white')
    canvas.save(OUT/f'{tag}_F{f:03}_PREVIEW.png')
for v in ['PALMAR_FULL','DORSAL_FULL','THENAR_CLOSE']:
    cases=['ZERO','INDEX_MCP_45','CMC_OPP_30','FULL_OPP_L1','FULL_OPP_L2','FULL_OPP_L3']
    canvas=Image.new('RGB',(1440,1500),(21,28,35));d=ImageDraw.Draw(canvas)
    for j,c in enumerate(cases):
        for k,(label,folder) in enumerate([('BEFORE','before_regression'),(tag,prefix+'_regression')]):
            im=Image.open(OUT/folder/f'{label}__{c}__{v}.png').convert('RGB');im.thumbnail((360,476))
            x=(j%2)*720+k*360;y=(j//2)*500
            canvas.paste(im,(x,y+24));d.text((x+4,y+5),f'{label} {c}',fill='white')
    canvas.save(OUT/f'{tag}_REGRESSION_{v}_PREVIEW.png')
for s in range(7):
    canvas=Image.new('RGB',(1800,1520),(21,28,35));d=ImageDraw.Draw(canvas)
    for j,f in enumerate(range(s*30+1,s*30+31)):
        x=(j%3)*600;y=(j//3)*152
        for k,v in enumerate(['PALMAR_MOTION','OBLIQUE_MOTION']):
            im=Image.open(OUT/(prefix+'_motion')/f'{tag}__F{f:03}__{v}.png').convert('RGB');im.thumbnail((150,128))
            canvas.paste(im,(x+k*150,y+20))
        # BEFORE beside AFTER in each frame cell provides complete segment QC without severity ranking.
        for k,v in enumerate(['PALMAR_MOTION','OBLIQUE_MOTION']):
            im=Image.open(OUT/'before_motion'/f'BEFORE__F{f:03}__{v}.png').convert('RGB');im.thumbnail((150,128))
            canvas.paste(im,(x+300+k*150,y+20))
        d.text((x+4,y+2),f'F{f:03} AFTER P/O | BEFORE P/O',fill='white')
    canvas.save(OUT/f'{tag}_FULL_MOTION_QC_{s+1}.png')
print('PREVIEWS_READY',tag)
