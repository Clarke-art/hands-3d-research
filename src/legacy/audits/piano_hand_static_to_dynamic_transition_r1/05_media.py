from common import *
from PIL import Image,ImageDraw,ImageFont
import subprocess
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19);bold=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',30)
views=['TEACHING_TOP','SIDE_OBLIQUE','REASONABLE_CLOSE'];titles=['TEACHING TOP VIEW','SIDE OBLIQUE','REASONABLE CLOSE'];names={'L':'left_octave_transition_r1.mp4','R':'right_fsharp_transition_r1.mp4'}
def compose(s,j):
 out=Image.new('RGB',(2304,756),'#f4f2eb');d=ImageDraw.Draw(out);t=WINDOWS[s][0]+j/60
 title='LEFT / D2 → D3 → D2' if s=='L' else 'RIGHT / F#5 CONTACT & RELEASE'
 d.text((24,10),title,font=bold,fill='#20392f');d.text((1600,14),f'MIDI clock {t:.3f}s  |  60fps',font=font,fill='#20392f')
 for i,(v,label) in enumerate(zip(views,titles)):
  d.text((i*768+20,55),label,font=small,fill='#4c6159');im=Image.open(P/'_frames'/s/f'{j:04}_{v}.png').convert('RGB');out.paste(im,(i*768,92))
 d.text((24,695),' / '.join(c.KEYS[n['key_index']]['note_name']+' '+phase(n,t) for n in EVENTS[s] if n['note_on']-.12<=t<=recovery_end(n)) or 'PREPARATION',font=font,fill='#20392f');d.text((1410,699),'DESIGN_ONLY / HUMAN REVIEW PENDING / SILENT',font=small,fill='#6a6557');return out
manifest=read(P/'RENDER_MANIFEST_R1.json');verification={};qa=P/'_qa';qa.mkdir(exist_ok=True)
for s in ['L','R']:
 N=manifest[s]['frames'];path=P/names[s];enc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','2304x756','-framerate','60','-i','-','-an','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',str(path)],stdin=subprocess.PIPE)
 for j in range(N):enc.stdin.write(compose(s,j).tobytes())
 enc.stdin.close();assert enc.wait()==0
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(path)]));v=next(x for x in probe['streams'] if x['codec_type']=='video');assert int(v['nb_read_frames'])==N and v['r_frame_rate']=='60/1';subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','null','-'],check=True)
 verification[s]={'file':path.name,'sha256':sha(path),'full_decode':'PASS','frames':N,'fps':60,'duration_sec':float(probe['format']['duration']),'complete_three_views':True,'audio':'SILENT_BY_SCOPE; inherited audio engine/interface/files protected unchanged','original_time_window':WINDOWS[s],'last_render_original_time':WINDOWS[s][0]+(N-1)/60,'probe':probe}
 compose(s,0).save(P/(s+'_review_poster.jpg'),quality=95)
 # Small audit-only all-frame strips: no extra deliverable screenshot flood.
 for part in range((N+35)//36):
  ids=range(part*36,min((part+1)*36,N));sheet=Image.new('RGB',(2304,6*155),'#f4f2eb');d=ImageDraw.Draw(sheet)
  for k,j in enumerate(ids):im=compose(s,j).resize((384,126));x=k%6*384;y=k//6*155;sheet.paste(im,(x,y+27));d.text((x+4,y+3),f'{WINDOWS[s][0]+j/60:.3f}s / frame {j}',font=small,fill='#20392f')
  sheet.save(qa/f'{s}_all_frames_{part+1}.jpg',quality=95)
 print('VIDEO_FULLY_DECODED',s,N,flush=True)
dump('VIDEO_VERIFICATION_R1.json',verification)
sm=read(STATIC/'STATIC_SCENE_MANIFEST_R2.json');plan=read(P/'CONTACT_AWARE_MOTION_PLAN_R1.json');ctrl={p:np.array(v) for p,v in plan['controls_radians'].items()};contact=read(P/'DYNAMIC_CONTACT_R1.json')
anchor_sheet=Image.new('RGB',(2200,4*450+90),'#f4f2eb');d=ImageDraw.Draw(anchor_sheet);d.text((24,20),'HUMAN APPROVED STATIC → DYNAMIC KEY-DOWN / MATCHED SIDE VIEW',font=bold,fill='#20392f');provenance=[]
for row,pose in enumerate(['L1','L2','R1','R2']):
 s=ANCHORS[pose]['hand'];n=EVENTS[s][1] if pose=='L2' else EVENTS[s][0];t=n['note_on']+.06 if pose!='R1' else n['note_on']-.15;j=round((t-WINDOWS[s][0])*60);left=STATIC/'renders'/f'{pose}__SIDE_OBLIQUE.png';right=P/'_frames'/s/f'{j:04}_SIDE_OBLIQUE.png';a=Image.open(left).convert('RGB').resize((550,425));b=Image.open(right).convert('RGB').resize((550,425));y=90+row*450;anchor_sheet.paste(a,(0,y));anchor_sheet.paste(b,(550,y));d.text((1140,y+30),pose+' / original clock '+f'{WINDOWS[s][0]+j/60:.3f}s',font=bold,fill='#20392f');d.text((1140,y+95),'Left: approved static unpressed reference',font=font,fill='#20392f');d.text((1140,y+140),'Right: current moving-key geometry',font=font,fill='#20392f');d.text((1140,y+205),'Static anchors retained; dynamic contact has bounded motion.',font=small,fill='#6a6557');provenance.append({'pose':pose,'static_file':str(left),'static_sha256':sha(left),'dynamic_file':str(right),'dynamic_sha256':sha(right),'dynamic_t':WINDOWS[s][0]+j/60})
anchor_sheet.save(P/'EVIDENCE_STATIC_ANCHOR_VS_DYNAMIC_R1.png')
sheet=Image.new('RGB',(2304,4*650+90),'#f4f2eb');d=ImageDraw.Draw(sheet);d.text((24,20),'DYNAMIC CONTACT / KEY PRESS, HOLD, RETURN / ACTUAL ROTATED SURFACE',font=bold,fill='#20392f')
for row,(s,idx) in enumerate([('L',0),('L',1),('L',2),('R',0)]):
 n=EVENTS[s][idx];y=90+row*650
 for col,t in enumerate([n['note_on']+.05,(n['note_on']+.035+n['note_off'])/2,n['note_off']+.035]):
  j=round((t-WINDOWS[s][0])*60);f=P/'_frames'/s/f'{j:04}_SIDE_OBLIQUE.png';im=Image.open(f).convert('RGB');sheet.paste(im,(col*768,y+32));d.text((col*768+16,y),c.KEYS[n['key_index']]['note_name']+f' / {WINDOWS[s][0]+j/60:.3f}s / '+['DOWN','HOLD','RETURN'][col],font=font,fill='#20392f')
sheet.save(P/'EVIDENCE_DYNAMIC_CONTACT_R1.png');dump('EVIDENCE_PROVENANCE_R1.json',{'source_candidate_sha256':read(P/'DYNAMIC_SCENE_MANIFEST_R1.json')['candidate_sha256'],'anchor_comparison_panels':provenance,'static_renders_reused':True,'whole_frame_resize_and_labels_only':True,'no_external_or_generated_images':True})
