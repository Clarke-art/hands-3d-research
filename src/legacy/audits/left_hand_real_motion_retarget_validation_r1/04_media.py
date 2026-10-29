from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import subprocess,json
P=Path(__file__).resolve().parent
views=['DEFAULT_TEACHING_VIEW','NORMAL_ORBIT_VIEW','REASONABLE_CLOSE_VIEW']
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20);bold=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',23)
W,H=1800,744
proc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate','30','-i','-','-an','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(P/'product_7s_left_three_views.mp4')],stdin=subprocess.PIPE)
def composite(j):
 im=Image.new('RGB',(W,H),'#111c28');d=ImageDraw.Draw(im)
 d.text((16,8),f'PHYSICAL LEFT | source Right | t={11.5+j/30:.3f}s | DESIGN ONLY',font=bold,fill='#e5edf6')
 d.text((1150,12),'PianoVAM | CC BY-NC-SA 4.0 | INTERNAL ONLY',font=font,fill='#a9c0d1')
 for col,view in enumerate(views):
  d.text((col*600+16,47),view,font=font,fill='#b7d7df');im.paste(Image.open(P/'_render_frames'/view/f'{j:04}.png').convert('RGB'),(col*600,84))
 return im
for j in range(210):proc.stdin.write(composite(j).tobytes())
proc.stdin.close();assert proc.wait()==0
# Three small time-ordered contact sheets, not ranked blocker frames.
for name,indices in [('EARLY',[0,15,30,45]),('MID',[75,90,105,120]),('LATE',[150,165,180,209])]:
 sheet=Image.new('RGB',(1800,H*4),'#111c28')
 for row,j in enumerate(indices):sheet.paste(composite(j),(0,row*H))
 sheet.save(P/f'{name}.png')
composite(0).save(P/'review_poster.png')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(P/'product_7s_left_three_views.mp4')]))
assert probe['streams'][0]['nb_frames']=='210' and abs(float(probe['format']['duration'])-7)<.001
(P/'VIDEO_VERIFICATION_R1.json').write_text(json.dumps({'status':'PASS','frames':210,'duration_seconds':7,'views':views,'probe':probe},indent=2),encoding='utf-8')
print('7_SECONDS_210_FRAMES_THREE_VIEWS_COMPLETE')
