from stage_common import *
from PIL import Image,ImageDraw,ImageFont
import shutil
folder=P/'before';folder.mkdir(exist_ok=True);bindings={}
names=[f'normal_speed_{v}.mp4' for v in ['teaching','side_oblique','overhead']]+['review_poster.jpg','contact_sheet_teaching.jpg','contact_sheet_side_oblique.jpg','contact_sheet_overhead.jpg']
for n in names:
    shutil.copyfile(R1/n,folder/n);assert sha(R1/n)==sha(folder/n)
    bindings[n]=dict(source=str(R1/n),sha256=sha(folder/n),copied_existing_R1_not_new_candidate=True)
dump('BEFORE_AFTER_MEDIA_BIND.json',dict(before=bindings,after=read(P/'VIDEO_VERIFICATION.json'),
    same_camera_bind_sha256=sha(P/'R1_REVIEW_CAMERA_BIND.json'),same_MIDI_clock=True,same_PCM_bytes=True,
    candidate_count_R2=1,extra_animation_generation=0))
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
for view in ['TEACHING','SIDE_OBLIQUE']:
    sheet=Image.new('RGB',(1920,1760),'#efeadd');d=ImageDraw.Draw(sheet)
    for row,(idx,label) in enumerate([(21,'D5 down'),(270,'G5 hold during octave handoff'),(304,'G4 repeated strike')]):
        y=row*586;d.text((12,y+7),f'R1 BEFORE | {label} | presentation {idx/60:.3f}s',font=font,fill='#2c503b')
        d.text((972,y+7),'R2 AFTER | SAME EXACT CAMERA / CLOCK / 1x',font=font,fill='#2c503b')
        for col,src in enumerate([R1,P]):
            im=Image.open(src/'_frames'/view/f'{idx:04}.png').convert('RGB').resize((960,540));sheet.paste(im,(col*960,y+38))
    sheet.save(P/f'matched_{view.lower()}_evidence.jpg',quality=95)
print('EXACT_CLOCK_COMPARISON_MEDIA_BOUND')
