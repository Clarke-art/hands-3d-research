import json
from pathlib import Path
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parent
S=json.loads((OUT/'SENSITIVITY_RESPONSE_R1.json').read_text())
rep=sorted(x['vertex'] for x in S['frames'][0]['per_vertex'])
cv=Image.new('RGB',(1920,1590),(18,27,35));d=ImageDraw.Draw(cv)
for y,v in enumerate(['FIRST_WEB_OBLIQUE','PALMAR_THENAR_CLOSE']):
    for x,l in enumerate(['BASELINE','WRIST_TO_THUMB','THUMB_TO_WRIST']):
        im=Image.open(OUT/'renders'/f'{l}__F130__{v}.png').convert('RGB');im.thumbnail((640,580));cv.paste(im,(x*640,y*610+26));d.text((x*640+7,y*610+7),f'F130 {l} delta=0.02 | {v}',fill='white')
d.text((12,1234),'MEASURED CLOSING PROJECTION (mm): + WRIST->THUMB / - THUMB->WRIST; direction proxy, not a target surface',fill='white')
for x,i in enumerate(rep):d.text((105+x*126,1270),str(i),fill='white')
for y,row in enumerate(S['frames']):
    yy=1295+y*45;d.text((10,yy+8),'F'+str(row['frame']),fill='white')
    for x,i in enumerate(rep):
        value=next(r for r in row['per_vertex'] if r['vertex']==i)['plus_transfer_closing_projection_mm'];color='#194d39' if value>.01 else '#5a3137' if value<-.01 else '#303d48'
        xx=94+x*126;d.rectangle((xx,yy,xx+118,yy+38),fill=color);d.text((xx+8,yy+10),f'{value:+.4f}',fill='white')
cv.save(OUT/'EVIDENCE_WEIGHT_SENSITIVITY_R1.png')
if (OUT/'WEIGHT_FIELD_PROBE_VERIFICATION_R1.json').exists():
    cv=Image.new('RGB',(1280,1220),(18,27,35));d=ImageDraw.Draw(cv)
    for y,v in enumerate(['FIRST_WEB_OBLIQUE','PALMAR_THENAR_CLOSE']):
        for x,l in enumerate(['BASELINE','WEIGHT_FIELD_PROBE']):
            im=Image.open(OUT/'renders'/f'{l}__F130__{v}.png').convert('RGB');im.thumbnail((640,580));cv.paste(im,(x*640,y*610+26));d.text((x*640+7,y*610+7),f'F130 {l} | {v}',fill='white')
    cv.save(OUT/'EVIDENCE_F130_WEIGHT_FIELD_PROBE.png')
    cv=Image.new('RGB',(1600,1850),(18,27,35));d=ImageDraw.Draw(cv)
    for y,f in enumerate([110,127,130,160,176,205]):
        for x,(v,l) in enumerate([(v,l) for v in ['FIRST_WEB_OBLIQUE','PALMAR_THENAR_CLOSE'] for l in ['BASELINE','WEIGHT_FIELD_PROBE']]):
            im=Image.open(OUT/'renders'/f'{l}__F{f:03}__{v}.png').convert('RGB');im.thumbnail((400,278));cv.paste(im,(x*400,y*306+22));d.text((x*400+5,y*306+4),f'F{f} {l} {v}',fill='white')
    cv.save(OUT/'EVIDENCE_SIX_FRAMES_WEIGHT_FIELD_PROBE.png')
print('FEW_CAUSAL_EVIDENCE_PANELS_READY')
