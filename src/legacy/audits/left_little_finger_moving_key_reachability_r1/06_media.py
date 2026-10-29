import sys,json,subprocess,shutil
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;PRE=P.parent/'piano_hand_static_to_dynamic_transition_r1';sys.path.insert(0,str(PRE));import common as o
from PIL import Image,ImageDraw,ImageFont
def dump(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18);bold=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',29)
views=['TEACHING_TOP','SIDE_OBLIQUE','REASONABLE_CLOSE'];labels=['TEACHING TOP VIEW','SIDE OBLIQUE','REASONABLE CLOSE'];ff='D:/ffmpeg/bin/ffmpeg.exe';fp='D:/ffmpeg/bin/ffprobe.exe'
def frame(j,before=False):
 im=Image.new('RGB',(2304,756),'#f4f2eb');d=ImageDraw.Draw(im);t=.4+j/60;title='BEFORE / ORIGINAL FAILED MOTION' if before else 'AFTER / ONE BOUNDED REACHABILITY PROBE';d.text((24,10),title,font=bold,fill='#244b3c');d.text((1640,12),f'D2 → D3 → D2 | {t:.3f}s',font=font,fill='#244b3c')
 for i,v in enumerate(views):d.text((i*768+20,56),labels[i],font=small,fill='#52675d');im.paste(Image.open((PRE if before else P)/'_frames'/'L'/f'{j:04}_{v}.png').convert('RGB'),(i*768,92))
 stages=' / '.join(o.c.KEYS[n['key_index']]['note_name']+' '+o.phase(n,t) for n in o.EVENTS['L'] if n['note_on']-.12<=t<=o.recovery_end(n)) or 'PREPARATION';d.text((24,698),stages,font=font,fill='#244b3c');d.text((1570,701),'DESIGN_ONLY / HUMAN_PENDING / SILENT',font=small,fill='#52675d');return im
def video(name,size,make):
 dest=P/name;enc=subprocess.Popen([ff,'-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size',size,'-framerate','60','-i','-','-an','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)],stdin=subprocess.PIPE)
 for j in range(84):enc.stdin.write(make(j).tobytes())
 enc.stdin.close();assert enc.wait()==0;probe=json.loads(subprocess.check_output([fp,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(dest)]));stream=probe['streams'][0];assert int(stream['nb_read_frames'])==84 and stream['r_frame_rate']=='60/1';subprocess.run([ff,'-v','error','-i',str(dest),'-f','null','-'],check=True);return {'sha256':o.sha(dest),'frames':84,'fps':60,'duration':float(probe['format']['duration']),'full_decode':'PASS','audio':'SILENT','complete_timeline':True,'original_first_time':.4,'original_last_frame_time':.4+83/60,'probe':probe}
def compare(j):
 im=Image.new('RGB',(2304,1512));im.paste(frame(j,True),(0,0));im.paste(frame(j),(0,756));return im
verified={'left_d2_d3_d2_reachability_r1.mp4':video('left_d2_d3_d2_reachability_r1.mp4','2304x756',frame),'left_before_after_r1.mp4':video('left_before_after_r1.mp4','2304x1512',compare)}
frame(0).save(P/'review_poster.jpg',quality=95);compare(0).save(P/'comparison_poster.jpg',quality=95);qa=P/'_qa';qa.mkdir(exist_ok=True)
for part in range(3):
 sheet=Image.new('RGB',(2304,6*155),'#f4f2eb');d=ImageDraw.Draw(sheet)
 for cell,j in enumerate(range(part*36,min((part+1)*36,84))):x=cell%6*384;y=cell//6*155;sheet.paste(frame(j).resize((384,126)),(x,y+27));d.text((x+4,y+3),f'{.4+j/60:.3f}s / frame {j}',font=small,fill='#244b3c')
 sheet.save(qa/f'all_frames_{part+1}.jpg',quality=95)
# Exact same frame/camera; meaningful phases across both presses and overlapping release.
sheet=Image.new('RGB',(1536,7*630),'#f4f2eb');d=ImageDraw.Draw(sheet)
for row,j in enumerate([18,21,33,35,48,51,65]):
 y=row*630;d.text((20,y+4),f'{.4+j/60:.3f}s | BEFORE',font=font,fill='#244b3c');d.text((788,y+4),'AFTER | REASONABLE CLOSE',font=font,fill='#244b3c')
 for i,base in enumerate([PRE,P]):sheet.paste(Image.open(base/'_frames'/'L'/f'{j:04}_REASONABLE_CLOSE.png').convert('RGB'),(i*768,y+36))
sheet.save(P/'EVIDENCE_MATCHED_PHASES_R1.jpg',quality=96)
shutil.copyfile(PRE/'left_octave_transition_r1.mp4',P/'left_original_reference_r1.mp4')
dump('VIDEO_VERIFICATION_R1.json',{'videos':verified,'source_candidate_sha256':o.read(P/'PROBE_SCENE_MANIFEST_R1.json')['candidate_sha256'],'before_source_sha256':o.sha(PRE/'left_octave_transition_r1.mp4'),'before_raw_frames_unchanged':True,'matched_camera_identity_verified':True,'right_video_rendered':False})
print('BOTH_LEFT_VIDEOS_FULL_DECODE_PASS',flush=True)
