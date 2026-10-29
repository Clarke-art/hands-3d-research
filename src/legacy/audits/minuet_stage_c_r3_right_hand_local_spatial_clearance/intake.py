from pathlib import Path
import json,hashlib,subprocess
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
C2=ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement'
C1=ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
files=set()
for folder in [C1,C2,ROOT/'audits/minuet_stage_a_r2_natural_continuous_motion',ROOT/'audits/minuet_stage_b_r3_budget_policy_candidate_recovery_r1']:
    files.update(f for f in folder.rglob('*') if f.is_file() and '__pycache__' not in f.parts and not f.name.startswith('review_server'))
for folder in [ROOT/'production_spec/right_hand_product_baseline_r2',ROOT/'production_spec/left_hand_product_baseline_r1',ROOT.parent/'piano/release/grand-piano-v1.1-rc-candidate']:
    files.update(f for f in folder.rglob('*') if f.is_file())
(P/'PROTECTED_INPUTS_BEFORE.json').write_text(json.dumps({str(f):sha(f) for f in sorted(files)},indent=2),encoding='utf8')
for view in ['teaching','overhead','side_oblique']:
    folder=P/'video_observation'/view;folder.mkdir(parents=True,exist_ok=True)
    subprocess.run(['D:/ffmpeg/bin/ffmpeg.exe','-v','error','-i',str(C2/f'normal_speed_{view}.mp4'),'-vf','fps=5','-start_number','0',str(folder/'%03d.png')],check=True)
    frames=sorted(folder.glob('*.png'))
    for page in range(2):
        sheet=Image.new('RGB',(1600,1200),'#eeeade');d=ImageDraw.Draw(sheet)
        for j,f in enumerate(frames[page*15:page*15+15]):
            im=Image.open(f).convert('RGB');im=im.crop((610,95,1090,445)).resize((320,215))
            x=j%5*320;y=j//5*400;sheet.paste(im,(x,y+28));d.text((x+5,y+5),f'R2 {view} video={(page*15+j)*.2:.2f}s',fill='black')
            full=Image.open(f).convert('RGB').resize((320,150));sheet.paste(full,(x,y+245))
        sheet.save(P/f'full_sequence_{view}_{page}.jpg',quality=94)
print('INTAKE_DONE',len(files))
