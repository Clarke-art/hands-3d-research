from pathlib import Path
import json,subprocess
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20);bold=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',24)
def frame(view,j):return Image.open(P/'_render_frames'/view/f'{j:04}.png').convert('RGB')
def encoder(name,w,h):return subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{w}x{h}','-framerate','30','-i','-','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(P/name)],stdin=subprocess.PIPE)
def header(im,j,title):
 d=ImageDraw.Draw(im);d.text((18,8),f'{title} | source {11.5+j/30:.3f}s | {j/30:.3f} / 7.000s',font=bold,fill='#f1f5f8');d.text((18,42),'MODEL A: XYZ + smooth YAW | predicted fingering only | NOT CONTACT VALIDATED',font=font,fill='#ffcc92');d.text((18,im.height-30),'PianoVAM / CC BY-NC-SA 4.0 / INTERNAL NONCOMMERCIAL VALIDATION ONLY',font=font,fill='#bed0dc');return d
jobs=[('product_7s_low_dof_root_pose.mp4',1200,1460),('product_7s_low_dof_contact_close.mp4',1200,780),('product_7s_fixed_vs_low_dof_matched.mp4',2400,780)]
enc=[encoder(*x) for x in jobs]
for j in range(210):
 overview=Image.new('RGB',(1200,1460),'#14212d');d=header(overview,j,'PLAYER + TEACHING VIEWS');overview.paste(frame('PLAYER_A',j),(0,90));overview.paste(frame('TEACHING_A',j),(0,760));d.text((18,85),'PIANO_PLAYER_VIEW / complete88 keys',font=font,fill='#ffffff');d.text((18,748),'TEACHING_TOP_OBLIQUE',font=font,fill='#ffffff')
 close=Image.new('RGB',(1200,780),'#14212d');header(close,j,'CONTACT_CLOSE');close.paste(frame('CONTACT_A',j),(0,80))
 matched=Image.new('RGB',(2400,780),'#14212d');d=header(matched,j,'FIXED REFERENCE vs MODEL A');matched.paste(frame('TEACHING_FIXED_REFERENCE',j),(0,80));matched.paste(frame('TEACHING_A',j),(1200,80));d.text((18,88),'PREVIOUS FIXED ORIENTATION / REJECTED',font=bold,fill='#ffcc92');d.text((1218,88),'MODEL A / SAME CAMERA, KEY MOTION, SOURCE TIME',font=bold,fill='#ffcc92')
 for e,im in zip(enc,[overview,close,matched]):e.stdin.write(im.tobytes())
 if j==130:matched.resize((1600,520)).save(P/'review_poster.jpg',quality=95)
for e in enc:e.stdin.close();assert e.wait()==0
probes={}
for name,w,h in jobs:
 p=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(P/name)]));v=p['streams'][0];assert len(p['streams'])==1 and v['nb_read_frames']=='210' and v['r_frame_rate']=='30/1' and float(p['format']['duration'])==7;probes[name]=p
(P/'VIDEO_VERIFICATION_R1.json').write_text(json.dumps({'status':'PASS','frames_each':210,'fps':30,'duration_each_sec':7,'audio_streams':0,'probes':probes,'matched':'actual old evaluation cache reused; same saved cameras, keyboard and time, no old-model resolve'},indent=2),encoding='utf-8')
# Internal QA sheets, not repeated hero-image deliverables. Every output frame covered.
qa=P/'_qa';qa.mkdir(exist_ok=True)
for sec in range(7):
 sheet=Image.new('RGB',(1800,1100),'#14212d');d=ImageDraw.Draw(sheet)
 for q in range(30):
  j=sec*30+q;col=q%6;row=q//6;sheet.paste(frame('TEACHING_A',j).resize((300,165)),(col*300,row*220+30));d.text((col*300+5,row*220+4),f'{11.5+j/30:.3f}s / F{j+1}',font=font,fill='#ffffff')
 sheet.save(qa/f'all_frames_second_{sec+1}.jpg',quality=94)
sheet=Image.new('RGB',(1800,7*355),'#14212d');d=ImageDraw.Draw(sheet)
for sec in range(7):
 j=sec*30+15
 for col,view in enumerate(['TEACHING_FIXED_REFERENCE','TEACHING_A','CONTACT_A']):sheet.paste(frame(view,j).resize((600,330)),(col*600,sec*355+25))
 d.text((10,sec*355),f'{11.5+j/30:.2f}s | FIXED                        MODEL A                                    CONTACT A',font=font,fill='#ffffff')
sheet.save(qa/'matched_time_strip.jpg',quality=95)
print('THREE_FULL_7S_VIDEOS_VERIFIED')
