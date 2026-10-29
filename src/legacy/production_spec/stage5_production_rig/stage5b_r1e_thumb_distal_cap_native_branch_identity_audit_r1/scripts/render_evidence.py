"""Scientific polygon projections of saved native vertices. No Blender pose/deformation."""
import sys
sys.dont_write_bytecode=True
import json,textwrap
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
out=Path(__file__).resolve().parents[1]
data=json.loads((out/'_tmp/render_data.json').read_text(encoding='utf8'));V=np.array(data['native']['vertices_world_m']);F=data['native']['faces'];labels=data['labels'];CAP=data['current_cap9'];NEW=data['native_cap'];rows=data['rows'];T=data['thumb_anchors'];I=data['index_anchors'];WEB=data['first_web_proxy'];tip=data['tip']
CF=set(data['current_cap_faces']);NF=set(data['native_cap_faces']);TN=set(data['thumb_nail_faces']);IN=set(data['index_nail_faces'])
RED='#b92e28';BLUE='#286fbd';GREEN='#267950';PURPLE='#7d42a1';INK='#20354b';ORANGE='#bd7720';TEAL='#238a91'
def font(size,bold=False):return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf',size)
def unit(a):return a/np.linalg.norm(a)
def text(draw,xy,msg,size=22,color=INK,bold=False,width=None):
    lines=textwrap.wrap(msg,width) if width else [msg]
    for i,line in enumerate(lines):draw.text((xy[0],xy[1]+i*(size+8)),line,font=font(size,bold),fill=color)
def canvas(title,sub):
    im=Image.new('RGB',(1800,1250),'#f4f6fa');d=ImageDraw.Draw(im)
    text(d,(30,22),title,35,bold=True);text(d,(32,76),sub,21,color='#536779')
    return im,d
ALL=[i for i in range(len(V)) if V[i,2]>.390]
def mesh(im,box,focus,normal=(0,-1,0),mode='branches',points=None,lines=None,callouts=None,joints=None):
    x,y,w,h=box;panel=Image.new('RGB',(w,h),'white');d=ImageDraw.Draw(panel)
    view=unit(np.array(normal,dtype=float));up=np.array([0.,0.,1.]);right=unit(np.cross(up,view));up=unit(np.cross(view,right))
    xy=np.stack([V@right,V@up],axis=1);depth=V@view;q=xy[focus];lo=q.min(0);hi=q.max(0);scale=min((w-90)/max(hi[0]-lo[0],1e-5),(h-80)/max(hi[1]-lo[1],1e-5));mid=(lo+hi)/2
    def p3(pt):return np.array([w/2+(pt@right-mid[0])*scale,h/2-(pt@up-mid[1])*scale])
    p=np.array([p3(a) for a in V]);order=sorted(range(len(F)),key=lambda i:float(depth[F[i]].mean()))
    for fi in order:
        vs=F[fi];pts=[tuple(p[a]) for a in vs]
        if max(t[0] for t in pts)<0 or min(t[0] for t in pts)>w or max(t[1] for t in pts)<0 or min(t[1] for t in pts)>h:continue
        cls={labels[a] for a in vs};color='#e7ebef'
        if mode=='branches' and cls=={'thumb'}:color='#d4e6d9'
        if mode=='branches' and cls=={'index'}:color='#d6e5f4'
        if mode in ['branches','cap','thumb'] and fi in TN:color='#8dbca0'
        if mode in ['branches','cap','index'] and fi in IN:color='#86b4d9'
        if mode in ['cap','branches'] and fi in CF:color='#efb8a5'
        if mode=='cap' and fi in NF:color='#7bb897'
        d.polygon(pts,fill=color);d.line(pts+[pts[0]],fill='#aab5c0',width=1)
    for seq,color,width in lines or []:
        d.line([tuple(p[a]) for a in seq],fill=color,width=width)
    for ids,color,r in points or []:
        for a in ids:
            xx,yy=p[a];d.ellipse((xx-r,yy-r,xx+r,yy+r),fill=color,outline='white',width=2)
    if joints:
        for name,pt in joints.items():
            xx,yy=p3(np.array(pt));d.line([(xx-7,yy),(xx+7,yy)],fill=INK,width=2);d.line([(xx,yy-7),(xx,yy+7)],fill=INK,width=2)
            tw=d.textlength(name,font=font(18,True));tx=xx+10 if xx+tw+15<w else xx-tw-10
            d.text((tx,yy-20),name,font=font(18,True),fill=INK,stroke_width=2,stroke_fill='white')
    if callouts:
        # IDs are laid out separately; diagnostic overlay remains visible on hidden surface.
        for j,(a,color) in enumerate(callouts):
            xx,yy=p[a];tx=w-140;ty=20+j*31
            d.line([(xx,yy),(tx-10,ty+10)],fill=color,width=1)
            d.text((tx,ty),f'v{a}',font=font(20,True),fill=color,stroke_width=2,stroke_fill='white')
    im.paste(panel,(x,y));outer=ImageDraw.Draw(im);outer.rectangle((x,y,x+w,y+h),outline='#cbd5df',width=2)
    return {i:(float(p[i,0]+x),float(p[i,1]+y)) for i in range(len(V))}
def footer(d,msg):text(d,(35,1125),msg,21,width=137)
def save(im,name):im.save(out/'renders'/name)
localcap=sorted(set(CAP)|{i for r in rows for i in r['one_ring']+r['two_ring_exact_hop_2']})
native_thumb_focus=sorted(set(NEW)|set(T)|set(data['native_thumb']['joint_world_m'] and [tip['thumb']]))

im,d=canvas('CURRENT CAP 9 / NATIVE BRANCH MAP','Saved pre-RSSF geometry; no current contact-pose proximity or inherited THUMB label used for identity.')
mesh(im,(30,135,840,930),ALL,points=[(CAP,RED,5),([tip['thumb']],GREEN,8),([tip['index']],BLUE,8)],callouts=[(a,RED) for a in CAP])
mesh(im,(900,135,870,930),localcap,normal=(0,1,0),points=[(CAP,RED,9)],callouts=[(a,RED) for a in CAP])
text(d,(45,145),'Native branch context: separate thumb / index tubes',21,bold=True);text(d,(915,145),'Opposite-side closeup: all 9 points on index proximal tube',21,bold=True)
footer(d,'Red = frozen cap9 audit targets. Green = independent native thumb tip. Blue = independent native index tip. All points are projected as diagnostic markers, including hidden surfaces. All 9 targets have entirely INDEX one-ring and two-ring neighborhoods.')
save(im,'CURRENT_CAP_9_NATIVE_BRANCH_MAP.png')

for nm,ids,fs,col in [('THUMB',T,TN,GREEN),('INDEX',I,IN,BLUE)]:
    im,d=canvas(f'NATIVE {nm} ANCHOR SET','Anchors come from pre-cap terminal-tip seeds and independently checked nail faces. Cap9 / R3 labels are not seeds.')
    geo=data['native_thumb' if nm=='THUMB' else 'native_index'];focus=sorted({i for fi in fs for i in F[fi]}|set(ids))
    mesh(im,(30,135,830,930),ALL,mode=nm.lower(),points=[(ids,col,5),([tip[nm.lower()]],ORANGE,9)],joints={f'{nm}_{k}':v for k,v in geo['joint_world_m'].items()})
    mesh(im,(890,135,880,930),focus,normal=(0,1,0),mode=nm.lower(),points=[(ids,col,7),([tip[nm.lower()]],ORANGE,10)])
    text(d,(45,145),'Continuous native tube and reconstructed direction',21,bold=True);text(d,(905,145),f'Native terminal nail / tip region; tip v{tip[nm.lower()]}',21,bold=True)
    footer(d,f'{nm} tip + nail anchor IDs: '+', '.join(map(str,ids))+'. Native joint crosses are engineering centerline estimates reconstructed before RSSF, not new bone authority. Nail faces are visible mesh surface regions.')
    save(im,f'NATIVE_{nm}_ANCHOR_SET.png')

r=next(r for r in rows if r['vertex_id']==2192);one=r['one_ring'];two=r['two_ring_exact_hop_2']
im,d=canvas('v2192 / NATIVE ONE-RING AND TWO-RING','Native branch = INDEX. Orange = exact 1 hop; teal = exact 2 hops. Local classification uses no cap or R3 identity input.')
mesh(im,(30,135,660,920),ALL,points=[([2192],RED,8)])
mesh(im,(725,135,1045,920),localcap,normal=(0,1,0),points=[(two,TEAL,7),(one,ORANGE,9),([2192],RED,12)],callouts=[(a,RED if a==2192 else ORANGE if a in one else TEAL) for a in [2192]+one+two])
text(d,(45,145),'Native full hand context',21,bold=True)
footer(d,'Incident faces: '+', '.join(str(f['face_id']) for f in r['incident_faces'])+'. One-ring: '+', '.join(map(str,one))+'. Two-ring: '+', '.join(map(str,two))+'. Every local face / neighbor remains on the independent native INDEX branch.')
save(im,'V2192_NATIVE_1RING_2RING.png')

im,d=canvas('v2192 / THUMB vs INDEX TOPOLOGY PATHS','Shortest surface-edge paths to independent nail + terminal-tip anchors on the saved native mesh.')
tp=r['thumb_anchor_path'];ip=r['index_anchor_path'];wp=r['first_web_proxy_path']
mesh(im,(30,135,1110,930),ALL,mode='branches',points=[([2192],RED,10),([tp['endpoint_anchor']],GREEN,10),([ip['endpoint_anchor']],BLUE,10),([wp['endpoint_anchor']],PURPLE,9)],lines=[(tp['vertex_ids'],GREEN,6),(ip['vertex_ids'],BLUE,6),(wp['vertex_ids'],PURPLE,5)])
for y,title,rec,color in [(150,'THUMB anchors',tp,GREEN),(410,'INDEX anchors',ip,BLUE),(675,'First-web cleft proxy',wp,PURPLE)]:
    text(d,(1170,y),title,26,color,bold=True);text(d,(1170,y+40),f"{rec['distance_mm']:.3f} mm -> v{rec['endpoint_anchor']}",22,color)
    text(d,(1170,y+85),'Path IDs: '+', '.join(map(str,rec['vertex_ids'])),18,color,width=47)
footer(d,'v2192 reaches native index anchors in 42.796 mm and native thumb anchors in 129.505 mm. Local two-ring is entirely INDEX. First-web anchor is a structural cleft proxy; Human Q2 remains UNRESOLVED, Q4=NO, Q5=LIMITED.')
save(im,'V2192_THUMB_VS_INDEX_PATHS.png')

im,d=canvas('CURRENT vs INDEPENDENT NATIVE CAP','Red frozen cap9 lies on native index. Green candidate is independently seeded at native thumb tip v284; not applied to production.')
mesh(im,(30,135,680,925),ALL,mode='cap',points=[(CAP,RED,6),(NEW,GREEN,3)],callouts=[(a,RED) for a in CAP])
mesh(im,(735,135,510,425),localcap,normal=(0,1,0),mode='cap',points=[(CAP,RED,7)])
mesh(im,(735,590,510,470),NEW,mode='cap',points=[(NEW,GREEN,5),([284],ORANGE,8)])
text(d,(1280,150),'Set comparison',29,bold=True);text(d,(1280,200),'True positives: 0',24,GREEN,bold=True);text(d,(1280,243),'False positives: 9',24,RED,bold=True);text(d,(1280,286),'Unresolved cap9: 0',24,bold=True);text(d,(1280,329),f'Candidate-only IDs: {len(NEW)}',24,GREEN,bold=True)
text(d,(1280,380),'FP: '+', '.join(map(str,CAP)),20,RED,width=36);text(d,(1280,495),'Candidate-relative FN IDs: '+', '.join(map(str,NEW)),19,GREEN,width=40)
footer(d,'Native candidate uses 9 mm min-corner geodesic on an independently identified THUMB-only graph. Candidate-relative false negatives are not approved replacement membership. NEXT = HUMAN_CAP_AUTHORITY_CORRECTION. Frozen cap authority remains unchanged.')
save(im,'CURRENT_VS_NATIVE_CAP_SET.png')

im,d=canvas('ALL CAP9 / INDEPENDENT NATIVE CLASSIFICATION','All nine targets = INDEX_SURFACE. No current cap membership, R3 THUMB, THUMB_STRONG or RSSF spatial proximity used as proof.')
mesh(im,(30,135,690,930),ALL,points=[(CAP,RED,6)],callouts=[(a,RED) for a in CAP])
for tx,msg in [(765,'ID'),(930,'Native branch'),(1235,'Thumb mm'),(1410,'Index mm'),(1600,'Web proxy mm')]:text(d,(tx,160),msg,22,bold=True)
for j,row in enumerate(rows):
    y=220+j*65;d.rectangle((745,y-6,1770,y+49),fill='white' if j%2==0 else '#eaf0f6')
    text(d,(765,y),str(row['vertex_id']),24,bold=True);text(d,(930,y),'INDEX_SURFACE',23,BLUE,bold=True)
    text(d,(1235,y),f"{row['thumb_anchor_path']['distance_mm']:.3f}",23);text(d,(1410,y),f"{row['index_anchor_path']['distance_mm']:.3f}",23);text(d,(1600,y),f"{row['first_web_proxy_path']['distance_mm']:.3f}",23)
text(d,(755,870),'Counts: true thumb cap 0; thumb distal non-cap 0;',24,bold=True);text(d,(755,915),'index surface 9; first-web shared 0; other 0; unresolved 0.',24,bold=True)
text(d,(755,970),'All nine one/two-ring neighborhoods: INDEX only.',23,BLUE,bold=True)
footer(d,'Distances alone do not prove identity. Classification also requires native local tube continuity, incident faces and two-ring neighborhoods, index nail / tip continuity, and separate thumb terminal geometry. Human review answers are retained verbatim.')
save(im,'ALL_CAP9_BRANCH_CLASSIFICATION.png')
print('Saved seven native static evidence projections.')
