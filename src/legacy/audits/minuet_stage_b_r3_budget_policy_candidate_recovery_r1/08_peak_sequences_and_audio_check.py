from stage_common import *
from PIL import Image,ImageDraw,ImageFont
import subprocess
ff='D:/ffmpeg/bin/ffmpeg.exe';font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',15);proof={}
for view in ['teaching','overhead','side_oblique']:
    sheet=Image.new('RGB',(1920,840),'#eeeadf');d=ImageDraw.Draw(sheet)
    for block,indices in enumerate([range(104,110),range(245,251)]):
        for row,base in enumerate([R2,P]):
            folder=base/'_frames'/('OVERHEAD_FULL_HAND' if base==R2 and view=='overhead' else view.upper())
            for col,i in enumerate(indices):
                x=col*320;y=block*420+row*210;sheet.paste(Image.open(folder/f'{i:04d}.png').convert('RGB').resize((320,180)),(x,y+30));d.text((x+3,y+3),f'{"R2" if row==0 else "RECOVERED"} {i/60:.4f}s',font=font,fill='#264b36')
    sheet.save(P/f'peak_sequence_{view}.jpg',quality=96)
    hashes=[]
    for base in [R2,P]:
        hashes.append(subprocess.check_output([ff,'-v','error','-i',str(base/f'normal_speed_{view}.mp4'),'-vn','-f','md5','-'],text=True).strip())
    assert hashes[0]==hashes[1]
    proof[view]=dict(decoded_audio_md5_R2=hashes[0],decoded_audio_md5_recovered=hashes[1],identical=True)
dump('AUDIO_CONTENT_IDENTITY.json',dict(views=proof,source_wav_bitwise_identical=sha(R2/'piano_performance.wav')==sha(P/'piano_performance.wav'),original_music_duration_sec=5.142852,NEW_SOLVER_CALLS=0))
print('THREE_VIEW_DECODED_AUDIO_IDENTICAL_AND_PEAK_FRAME_PAIRS_READY',flush=True)
