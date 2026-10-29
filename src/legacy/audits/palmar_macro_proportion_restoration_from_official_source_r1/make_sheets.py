from PIL import Image, ImageDraw
from pathlib import Path
import sys
p=Path(__file__).resolve().parent
iteration=sys.argv[1]
folder=p/('renders' if iteration=='final' else f'iteration_{iteration}_renders')
views=['HUMAN_PALMAR','THENAR_CLOSE','FIRST_WEB_CLOSE','FULL_PALM','SIDE_VOLUME','SILHOUETTE']
for sheet,vv in [('main',views[:3]),('other',views[3:])]:
    out=Image.new('RGB',(1800,1560),'#16191e');d=ImageDraw.Draw(out)
    for y,v in enumerate(vv):
        for x,(a,pose) in enumerate([('OFFICIAL_L1','NEUTRAL'),('CURRENT','ZERO'),('CANDIDATE','ZERO')]):
            im=Image.open(folder/f'{a}__{pose}__{v}.png').convert('RGB');im.thumbnail((600,490))
            out.paste(im,(x*600,y*520+30));d.text((x*600+12,y*520+8),a+' / '+v,fill='white')
    out.save(p/f'ITERATION_{iteration}_{sheet}_sheet.png')
if iteration=='final':
    out=Image.new('RGB',(1600,1660),'#16191e');d=ImageDraw.Draw(out)
    for y,v in enumerate(['DORSAL54_SENTINEL','PALMAR16_SENTINEL']):
        for x,a in enumerate(['CURRENT','CANDIDATE']):
            im=Image.open(folder/f'{a}__ZERO__{v}.png').convert('RGB');im.thumbnail((800,800));out.paste(im,(x*800,y*830+30));d.text((x*800+12,y*830+8),a+' / '+v,fill='white')
    out.save(p/'FINAL_SENTINELS_sheet.png')
