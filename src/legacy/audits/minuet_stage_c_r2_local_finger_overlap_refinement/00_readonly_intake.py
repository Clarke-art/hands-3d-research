from local_common import *
import subprocess
from PIL import Image,ImageDraw,ImageFont
assert not DEST.exists()
man=read(C1/'SCENE_MANIFEST.json');assert sha(man['path'])==man['sha256']=='d8e0f5a85e71323739bfcd4de485ff7a2b4096f8e59bbd4c578ee9d76d3e51a7'
for folder in [A,B]:
    m=read(folder/'SCENE_MANIFEST.json');assert sha(m['path'])==m['sha256']
history=read(C1/'PROTECTED_INPUTS_BEFORE.json');files={Path(p) for p in history if Path(p).is_file()}
for folder in [C1,A,B]:files.update(p for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.name.startswith('review_server_'))
snapshot={str(p):sha(p) for p in sorted(files)}
dump('PROTECTED_INPUTS_BEFORE.json',snapshot)
dump('HUMAN_AUTHORITY_RECEIPT.json',dict(authority='Explicit MINUET_STAGE_C_R2_LOCAL_FINGER_OVERLAP_REFINEMENT user request,2026-10-10',R1_review='REOPENED_FOR_LOCAL_VISIBLE_DEFECT',R1_overall_original_speed_motion='Human accepted as overall baseline, local defect not accepted',source_candidate_sha256=man['sha256'],allowed_scope='One finite local refinement only, no frozen changes',arrow_screenshot_received=False))
ff='D:/ffmpeg/bin/ffmpeg.exe'
for view in ['OVERHEAD','TEACHING','SIDE_OBLIQUE']:
    folder=P/'diagnostic_frames'/view;folder.mkdir(parents=True,exist_ok=True)
    subprocess.run([ff,'-y','-v','error','-i',str(C1/f'normal_speed_{view.lower()}.mp4'),'-vf',"select='between(n,36,90)'",'-fps_mode','passthrough','-start_number','36',str(folder/'%04d.png')],check=True)
    sheet=Image.new('RGB',(1600,1200),'#eeeade');draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
    for i,f in enumerate([36,42,48,54,60,63,66,69,72,78,84,90]):
        img=Image.open(folder/f'{f:04d}.png').convert('RGB');img=img.crop((550,70,1050,490)).resize((400,340));x=i%4*400;y=i//4*400
        sheet.paste(img,(x,y+40));draw.text((x+4,y+4),f'frame{f+1} video{f/60:.3f}s / music{f/60-.35:.3f}s',font=font,fill='#173d32')
    sheet.save(P/f'diagnostic_right_{view.lower()}.jpg',quality=95)
print('READONLY_INTAKE_PASS',len(snapshot),'protected files',flush=True)
