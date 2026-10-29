from pathlib import Path
import json,subprocess,io
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
C1=ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance';C2=ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement'
ff='D:/ffmpeg/bin/ffmpeg.exe';font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
def frame(folder,view,idx):
    data=subprocess.check_output([ff,'-v','error','-i',str(folder/f'normal_speed_{view}.mp4'),'-vf',fr'select=eq(n\,{idx})','-frames:v','1','-f','image2pipe','-vcodec','png','-'])
    return Image.open(io.BytesIO(data)).convert('RGB')
# Exact source frame indices, avoiding fps-filter sampling offsets.
for view in ['teaching','overhead','side_oblique']:
    folder=P/'video_observation'/view
    subprocess.run([ff,'-y','-v','error','-i',str(C2/f'normal_speed_{view}.mp4'),'-vf',r'select=not(mod(n\,12))','-fps_mode','passthrough','-start_number','0',str(folder/'%03d.png')],check=True)
    for page in range(2):
        sheet=Image.new('RGB',(1600,1200),'#eeeade');d=ImageDraw.Draw(sheet)
        for j in range(15):
            idx=page*15+j;im=Image.open(folder/f'{idx:03d}.png').convert('RGB');x=j%5*320;y=j//5*400
            sheet.paste(im.crop((610,95,1090,445)).resize((320,215)),(x,y+28));sheet.paste(im.resize((320,150)),(x,y+245))
            d.text((x+5,y+5),f'R2 {view} video={idx*.2:.2f}s',fill='black')
        sheet.save(P/f'full_sequence_{view}_{page}.jpg',quality=94)
coords=json.loads((P/'WITNESS_SCREEN_COORDINATES.json').read_text())
samples=[(26,'INDEX','G#4'),(108,'RING','C#5'),(156,'INDEX','A#4'),(204,'MIDDLE','C#5'),(233,'MIDDLE','D#5'),(295,'RING','C#5')]
(P/'evidence_frames').mkdir(exist_ok=True)
for idx,digit,note in samples:
    t=idx/60;sheet=Image.new('RGB',(1440,750),'#eeeade');draw=ImageDraw.Draw(sheet)
    for col,view in enumerate(['teaching','overhead','side_oblique']):
        for row,(label,folder) in enumerate([('R1',C1),('R2',C2)]):
            im=frame(folder,view,idx);im.save(P/'evidence_frames'/f'{label}_{view}_{idx:03d}.png')
            im=im.crop((610,95,1090,445));ds=ImageDraw.Draw(im)
            cs=[c for c in coords if c['stage']==label and c['view']==view.upper() and abs(c['video_sec']-t)<1e-6 and c['digit']==digit and c['note']==note]
            if cs:
                x,y=cs[0]['pixel'];x-=610;y-=95;ds.ellipse((x-13,y-13,x+13,y+13),outline='#ed5555',width=2)
            x=col*480;y=row*375;sheet.paste(im,(x,y+25));draw.text((x+4,y+3),f'{label} {view} {digit}/{note} t={t:.3f}s',font=font,fill='black')
    sheet.save(P/f'witness_{idx:03d}.jpg',quality=97)
for view in ['teaching','overhead','side_oblique']:
    sheet=Image.new('RGB',(1440,750),'#eeeade');draw=ImageDraw.Draw(sheet)
    for col,idx in enumerate([65,68,72]):
        for row,(label,folder) in enumerate([('R1',C1),('R2',C2)]):
            im=frame(folder,view,idx);x=col*480;y=row*375;sheet.paste(im.crop((610,95,1090,445)),(x,y+25));draw.text((x+4,y+3),f'{label} {view} t={idx/60:.3f}s',font=font,fill='black')
    sheet.save(P/f'residual_{view}.jpg',quality=97)
print('EXACT_FRAME_VISUAL_EVIDENCE_DONE')
