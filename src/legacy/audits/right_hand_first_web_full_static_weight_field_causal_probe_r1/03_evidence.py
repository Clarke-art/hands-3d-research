"""Only the three requested evidence plates; native matched images stay available."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parent
def font(size,bold=False):return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if bold else 'segoeui.ttf'),size)
BG='#111b25';FG='#e6edf5';MUTED='#9eafbf';OLD='#a7b8c9';NEW='#52d6a8'
views=['FIRST_WEB_OBLIQUE','PALMAR_THENAR_CLOSE'];labels=['BASELINE','FULL_VECTOR_PROBE']
def panel(cv,box,f,view,label):
    x,y,w,h=box;d=ImageDraw.Draw(cv)
    d.text((x+12,y+9),f'F{f}  {label}',font=font(22,True),fill=FG)
    d.text((x+12,y+38),view,font=font(18),fill=MUTED)
    im=Image.open(OUT/'renders'/f'{label}__F{f:03}__{view}.png').convert('RGB');im.thumbnail((w,h-72))
    cv.paste(im,(x+(w-im.width)//2,y+68))
cv=Image.new('RGB',(1920,1960),BG);d=ImageDraw.Draw(cv)
d.text((20,15),'F130 PEAK | FULL STATIC WEIGHT FIELD | DESIGN_ONLY',font=font(30,True),fill=FG)
d.text((20,61),'Same camera / frame / Action / light / shading. Baseline LEFT, unique candidate RIGHT.',font=font(24),fill=MUTED)
for r,v in enumerate(views):
    for c,l in enumerate(labels):panel(cv,(c*960,110+r*925,960,925),130,v,l)
cv.save(OUT/'EVIDENCE_F130_FULL_WEIGHT_FIELD_PROBE.png')
cv=Image.new('RGB',(2048,3250),BG);d=ImageDraw.Draw(cv)
d.text((20,14),'SIX FIXED FRAMES | baseline LEFT / candidate RIGHT within each view',font=font(30,True),fill=FG)
d.text((20,59),'F110/F176 = smooth controls. F127/F130/F160/F205 = folded. No visual PASS from machine numbers.',font=font(23),fill=MUTED)
for r,f in enumerate([110,127,130,160,176,205]):
    for c,(v,l) in enumerate([(v,l) for v in views for l in labels]):panel(cv,(c*512,110+r*520,512,520),f,v,l)
cv.save(OUT/'EVIDENCE_SIX_FRAMES_FULL_WEIGHT_FIELD_PROBE.png')
G=json.loads((OUT/'FULL_VECTOR_GRADIENT_R1.json').read_text());D=json.loads((OUT/'FULL_VECTOR_FIELD_DEFINITION_R1.json').read_text())
cv=Image.new('RGB',(1800,1190),BG);d=ImageDraw.Draw(cv)
d.text((32,20),'FULL VECTOR FIELD | PRE-RENDER MANIPULATION EVIDENCE',font=font(33,True),fill=FG)
d.text((32,76),'8 active bones | 164 free vertices | 70 exact boundary pins | 1 deterministic harmonic solution',font=font(25),fill=MUTED)
for row,(key,title) in enumerate([('ROI_overall','ROI overall: 431 original edges'),('human_visible_high_strain_band','Human-visible high-strain band: 8 inherited F130 edges')]):
    v=G[key];y=145+row*215;d.text((32,y),title,font=font(27,True),fill=FG)
    d.text((1100,y),f"Mean reduction {v['mean_reduction_percent']:.2f}%",font=font(27,True),fill=NEW)
    scale=800/.14
    for j,(k,color) in enumerate([('before',OLD),('after',NEW)]):
        yy=y+48+j*51;d.text((32,yy),k.upper(),font=font(22),fill=color)
        d.rectangle((160,yy+2,160+v[k]['mean']*scale,yy+28),fill=color)
        d.text((1000,yy),f"mean {v[k]['mean']:.6f}    max {v[k]['max']:.6f} /mm",font=font(24),fill=color)
y=585
d.text((32,y),'PER-BONE mean gradient (weight component / mm)',font=font(27,True),fill=FG)
d.text((565,y+45),'ROI before -> after',font=font(23),fill=MUTED)
d.text((1060,y+45),'Band before -> after',font=font(23),fill=MUTED)
for r,(n,v) in enumerate(G['per_active_bone'].items()):
    yy=y+88+r*43;d.text((32,yy),n,font=font(23),fill=FG)
    for x,k in [(565,'ROI'),(1060,'high_strain_band')]:
        s=v[k];d.text((x,yy),f"{s['before']['mean']:.6f} -> {s['after']['mean']:.6f}",font=font(23),fill=FG)
    d.text((1510,yy),f"{v['changed_free_vertices']}/164 changed",font=font(21),fill=NEW)
energy=G['weighted_Dirichlet_energy_before_after'];reduction=(1-energy[1]/energy[0])*100
d.text((32,1070),f'Positive graph Laplacian energy reduction: {reduction:.2f}%. No support pruning / thresholding.',font=font(25),fill=MUTED)
d.text((32,1115),'Secondary evidence only. Surface quality in matched ordinary views decides the causal result.',font=font(25),fill=MUTED)
cv.save(OUT/'EVIDENCE_FULL_VECTOR_GRADIENT_R1.png')
print('THREE_REQUESTED_EVIDENCE_PLATES_READY')
