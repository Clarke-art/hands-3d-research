import sys,json
from pathlib import Path
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parent
mode=sys.argv[1]
folder='final_renders' if '--final' in sys.argv else 'renders'
def sheet(name,rows,w=600):
    out=Image.new('RGB',(w*max(map(len,rows)),(round(w*1100/1200)+36)*len(rows)),'#15191e');d=ImageDraw.Draw(out)
    for y,row in enumerate(rows):
        for x,(a,c,v) in enumerate(row):
            im=Image.open(OUT/folder/f'{a}__{c}__{v}.png').convert('RGB');im.thumbnail((w,round(w*1100/1200)))
            yy=y*(round(w*1100/1200)+36);out.paste(im,(x*w,yy+36));d.text((x*w+12,yy+10),a+' / '+c+' / '+v,fill='white')
    out.save(OUT/(name+'.png'))
if mode=='static':
    vv=['PALMAR_FULL','DORSAL_FULL','RADIAL_SIDE','ULNAR_SIDE','THUMB_WEB_OBLIQUE','THENAR_CLOSE']
    for name,views in [('STATIC_FULL_SHEET',vv[:3]),('STATIC_THENAR_SHEET',vv[3:])]:
        sheet(name,[[(a,c,v) for a,c in [('OFFICIAL_L1','REST'),('REBASED','ZERO')]] for v in views],600)
else:
    cases=json.loads((OUT/'REPRESENTATIVE_MOTION_EVIDENCE_R1.json').read_text())['cases']
    for group,names in [('FOUR_FINGER', ['INDEX_MCP_45','MIDDLE_MCP_45','RING_MCP_45','LITTLE_MCP_45']),('THUMB_FLEX',['THUMB_MCP_45','THUMB_IP_45']),('OPPOSITION',['CMC_OPP_30','FULL_OPP_L1','FULL_OPP_L2','FULL_OPP_L3'])]:
        for n in names:
            row=next(c for c in cases if c['case_id']==n)
            vv=row['views']
            sheet(n+'_SHEET',[[('REBASED',n,v) for v in vv[:2]],[('REBASED',n,v) for v in vv[2:]]],600)
