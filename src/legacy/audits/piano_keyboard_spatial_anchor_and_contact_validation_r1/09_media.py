from pathlib import Path
import json,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;W=1200;H=780
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20);bold=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',24)
jobs={'PIANO_PLAYER_VIEW':'product_7s_dual_on_88keys.mp4','TEACHING_TOP_OBLIQUE':'product_7s_teaching_keyboard_view.mp4','CONTACT_CLOSE':'product_7s_contact_close.mp4'}
tl=json.loads((P/'PERFORMANCE_TIMELINE_R1.json').read_text());probes={}
if '--close-only' in sys.argv:probes=json.loads((P/'VIDEO_VERIFICATION_R1.json').read_text())['probes']
for view,name in jobs.items():
 if '--close-only' in sys.argv and view!='CONTACT_CLOSE':continue
 enc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate','30','-i','-','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(P/name)],stdin=subprocess.PIPE)
 for j in range(210):
  im=Image.new('RGB',(W,H),'#14212d');im.paste(Image.open(P/'_render_frames'/view/f'{j:04}.png').convert('RGB'),(0,78));d=ImageDraw.Draw(im)
  d.text((18,7),f'{view} | source {11.5+j/30:.3f}s | {j/30:.3f} / 7.000s',fill='#f3f5f7',font=bold)
  d.text((18,40),'CONTACT FIT FAILED / audit candidate | cyan L / copper R / gold unknown',fill='#ffcb8e',font=font)
  d.text((18,749),'PianoVAM / CC BY-NC-SA 4.0 / INTERNAL NONCOMMERCIAL VALIDATION ONLY',fill='#c3d0dc',font=font)
  enc.stdin.write(im.tobytes())
  if view=='TEACHING_TOP_OBLIQUE' and j==75:im.save(P/'review_poster.png')
 enc.stdin.close();assert enc.wait()==0
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(P/name)]));v=probe['streams'][0];assert len(probe['streams'])==1 and v['nb_read_frames']=='210' and v['r_frame_rate']=='30/1' and float(probe['format']['duration'])==7;probes[name]=probe
print('THREE_7S_VIDEOS_ENCODED')
# Exhaustive ordinary-view contact sheets: every rendered frame, no cherry picking.
for sec in range(7):
 sheet=Image.new('RGB',(1800,1100),'#14212d');d=ImageDraw.Draw(sheet)
 for q in range(30):
  j=sec*30+q;col=q%6;row=q//6;im=Image.open(P/'_render_frames/TEACHING_TOP_OBLIQUE'/f'{j:04}.png').convert('RGB');sheet.paste(im.resize((300,165)),(col*300,row*220+30));d.text((col*300+5,row*220+4),f'{11.5+j/30:.3f}s / F{j+1}',fill='#f2f5f7',font=font)
 sheet.save(P/f'FULL_REVIEW_SECOND_{sec+1}.jpg',quality=94)
# Near-view time strip to make hovering and key penetration easy to see at normal scale.
sheet=Image.new('RGB',(1200,7*355),'#14212d');d=ImageDraw.Draw(sheet)
for sec in range(7):
 j=sec*30+15;sheet.paste(Image.open(P/'_render_frames/CONTACT_CLOSE'/f'{j:04}.png').resize((600,330)),(0,sec*355+25));sheet.paste(Image.open(P/'_render_frames/TEACHING_TOP_OBLIQUE'/f'{j:04}.png').resize((600,330)),(600,sec*355+25));d.text((12,sec*355),f'Source {11.5+j/30:.2f}s',font=font,fill='#f2f5f7')
sheet.save(P/'CONTACT_AND_TEACHING_TIME_STRIP.jpg',quality=95)
(P/'VIDEO_VERIFICATION_R1.json').write_text(json.dumps({'status':'PASS','fps':30,'frames_each':210,'duration_each_sec':7,'audio_streams':0,'endpoint':'421 native observations include18.5s; video210 frames spans11.5..18.4667s with duration7s; no duplicated endpoint','probes':probes},indent=2))
