from performance_core import *
from PIL import Image,ImageDraw,ImageFont
import subprocess,time
OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1'
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',23);bold=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',28)
sourcevideo=OLD/'product_midi_dual_hand_with_audio.mp4';C=read(P/'KEY_CONTACT_R1.json')['summary']
def encoder(path,size):return subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size',size,'-framerate','60','-i','-','-i',str(sourcevideo),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','copy','-t','3.4','-movflags','+faststart',str(path)],stdin=subprocess.PIPE)
def active(s,t):return ' + '.join(KEYS[n['key_index']]['note_name']+f" / finger {n['finger']}" for n in TL['notes'] if n['hand']==s and n['note_on']<=t<n['note_off']) or 'prepare / release'
def completed_frame(folder,j):
 deadline=time.monotonic()+120
 while True:
  try:
   im=Image.open(folder/'_frames'/f'{j:04}.png').convert('RGB');im.load();return im
  except (FileNotFoundError,OSError):
   if time.monotonic()>deadline:raise RuntimeError(f'Render frame {j} did not complete within120sec')
   time.sleep(.25)
main=P/'product_midi_dual_hand_motion_refined.mp4';compare=P/'product_motion_before_after.mp4'
enc=encoder(main,'1600x900');comp=encoder(compare,'1440x1160')
for j in range(204):
 new=completed_frame(P,j);old=completed_frame(OLD,j)
 im=new.copy();d=ImageDraw.Draw(im);d.rectangle((0,0,1600,92),fill='#14202b');d.text((24,8),'MUSETTE / BWV Anh.126 / MEASURES 1-2',font=bold,fill='white');d.text((24,49),'DESIGN ONLY / MOTION REFINEMENT / HUMAN REVIEW PENDING',font=font,fill='#ffd299');d.text((1320,18),f'{j/60:.3f} / 3.400s',font=font,fill='white')
 d.rectangle((0,830,1600,900),fill='#14202b');d.text((24,848),'LEFT  '+active('L',j/60),font=bold,fill='white');d.text((865,848),'RIGHT  '+active('R',j/60),font=bold,fill='white');enc.stdin.write(im.tobytes())
 if j==69:im.save(P/'review_poster.jpg',quality=94)
 sheet=Image.new('RGB',(1440,1160),'#14202b');dd=ImageDraw.Draw(sheet)
 for row,frame,label in [(0,old,'BEFORE / held R 48/240, L 12/240'),(1,new,f"REFINED / held R {C['R']['held_contact_pass']}/240, L {C['L']['held_contact_pass']}/240")]:
  y=row*580;dd.text((24,y+7),label,font=bold,fill='white');dd.text((1220,y+7),f'{j/60:.3f}s',font=font,fill='#ffd299');sheet.paste(frame.crop((280,280,1160,610)).resize((1440,540),Image.Resampling.LANCZOS),(0,y+40))
 comp.stdin.write(sheet.tobytes())
for p in [enc,comp]:p.stdin.close();assert p.wait()==0
# One mandatory evidence plate with identical screen crop and scale, not selected best frames.
evidence=Image.new('RGB',(1600,1080),'#14202b');d=ImageDraw.Draw(evidence);d.text((20,9),'LEFT IDLE INDEX / MIDDLE / RING — SAME CAMERA / SAME SCALE',font=bold,fill='white')
for col,t in enumerate([.85,1.15,1.85,2.50]):
 j=round(t*60);x=col*400;d.text((x+16,53),f'{t:.2f}s  /  {active("L",t)}',font=font,fill='#ffd299')
 for row,folder,label in [(0,OLD,'BEFORE'),(1,P,'REFINED')]:
  y=92+row*490;im=Image.open(folder/'_frames'/f'{j:04}.png').convert('RGB').crop((300,280,605,620)).resize((390,435),Image.Resampling.LANCZOS);evidence.paste(im,(x+5,y+35));d.text((x+15,y+3),label,font=bold,fill='white')
evidence.save(P/'EVIDENCE_LEFT_IDLE_FINGERS_R1.png')
def adts(path):return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c:a','copy','-f','adts','-'])
originalaudio=adts(sourcevideo);results=[]
for video in [main,compare]:
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]));v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio');assert int(v['nb_read_frames'])==204;assert abs(float(probe['format']['duration'])-3.4)<.01;assert adts(video)==originalaudio
 results.append({'file':video.name,'duration_sec':3.4,'frames':204,'fps':60,'audio_AAC_payload_byte_identical_to_previous':True,'audio_sha256':hashlib.sha256(originalaudio).hexdigest(),'audio_start_time':a['start_time'],'probe':probe})
dump('VIDEO_VERIFICATION_R1.json',{'status':'PASS_MEDIA_STRUCTURE_AND_AUDIO_IDENTITY','videos':results,'source_audio_video_sha256':sha(sourcevideo),'WAV_byte_identical':sha(P/'piano_performance.wav')==sha(OLD/'piano_performance.wav'),'key_angle_array_exact':bool(np.array_equal(np.load(P/'procedural_motion.npz')['key_angles'],np.load(OLD/'procedural_motion.npz')['key_angles']))})
# Compact internal QA: every frame, cropped to the hands, four sheets.
qa=P/'_qa';qa.mkdir(exist_ok=True)
for part in range(4):
 sheet=Image.new('RGB',(1800,1800),'#14202b');d=ImageDraw.Draw(sheet)
 for k in range(51):
  j=part*51+k;x=(k%6)*300;y=(k//6)*200;im=Image.open(P/'_frames'/f'{j:04}.png').crop((280,280,1160,610)).resize((296,111));sheet.paste(im,(x,y+40));d.text((x+5,y+5),f'{j/60:.3f}s',font=font,fill='white')
 sheet.save(qa/f'full_motion_{part+1}.jpg',quality=94)
print('Both complete videos, matched evidence and AAC identity verified',flush=True)
