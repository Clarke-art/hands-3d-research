from pathlib import Path
from PIL import Image,ImageDraw
import json,numpy as np
OUT=Path(__file__).resolve().parent
for label in ['A','B','C']:
    for f in [130,76,205,61]:
        cv=Image.new('RGB',(1280,1220),(21,28,35));d=ImageDraw.Draw(cv)
        for y,v in enumerate(['PALMAR_THENAR_CLOSE','FIRST_WEB_OBLIQUE']):
            for x,l in enumerate(['BASELINE',label]):
                im=Image.open(OUT/(l.lower()+'_selected')/f'{l}__F{f:03}__{v}.png').convert('RGB');im.thumbnail((640,586));cv.paste(im,(x*640,y*610+24));d.text((x*640+6,y*610+5),f'{l} F{f} {v}',fill='white')
        cv.save(OUT/f'{label}_F{f:03}_COMPARISON.png')
    for v in ['PALMAR_FULL','THENAR_CLOSE','DORSAL_FULL','FIRST_WEB_CLOSE']:
        cv=Image.new('RGB',(1280,700),(21,28,35));d=ImageDraw.Draw(cv)
        for x,l in enumerate(['BASELINE',label]):
            im=Image.open(OUT/(l.lower()+'_selected')/f'{l}__ZERO__{v}.png').convert('RGB');im.thumbnail((640,670));cv.paste(im,(x*640,24));d.text((x*640+6,5),f'{l} ZERO {v}',fill='white')
        cv.save(OUT/f'{label}_ZERO_{v}_COMPARISON.png')
j=json.loads((OUT/'TOPOLOGY_INPUT_R1.json').read_text());cam=json.loads((OUT/'SCREEN_MATCHED_CAMERAS_R1.json').read_text())['motion']['130']['FIRST_WEB_OBLIQUE']
V=np.array(j['F130_world']);d=np.array(cam['direction']);d/=np.linalg.norm(d);right=np.cross([0,0,1],d);right/=np.linalg.norm(right);up=np.cross(d,right);up/=np.linalg.norm(up);center=np.array(cam['center']);w,h=cam['resolution'];scale=cam['ortho_scale_m']
xy=np.stack(((V-center)@right,(V-center)@up),axis=1);xy[:,0]=w/2+xy[:,0]*w/scale;xy[:,1]=h/2-xy[:,1]*w/scale
im=Image.open(OUT/'baseline_selected/BASELINE__F130__FIRST_WEB_OBLIQUE.png').convert('RGB');draw=ImageDraw.Draw(im)
for edge in j['local_edges']:
    a,b=edge['vertices'];draw.line([tuple(xy[a]),tuple(xy[b])],fill='#30d2a2',width=1)
# Number only nodes near the screen-visible notch, for direct identification, not a severity census.
annotated=[]
for i in j['patch_ids']:
    x,y=xy[i]
    if 215<x<470 and 285<y<550:
        draw.ellipse((x-2,y-2,x+2,y+2),fill='#ffbd76');draw.text((x+3,y),str(i),fill='#ffffff');annotated.append(i)
im.save(OUT/'CURRENT_F130_LOCAL_WIREFLOW.png')
(OUT/'WIRE_OVERLAY_VERTEX_LABELS_R1.json').write_text(json.dumps({'camera':cam,'labelled_vertex_ids':annotated,'note':'Local quad edges projected onto the existing F130 ordinary solid view. No normal-dot/strain metric or intersections.'},indent=2))
print('KEY_SCREEN_COMPARISONS_READY')
