import json,csv,subprocess,struct,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];SRC=ROOT/'references/piano_motion/pianovam_sample_r1';R='2024-03-04_03-46-36'
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
a=json.loads((SRC/f'Handskeleton/{R}.json').read_text());notes=list(csv.DictReader((SRC/f'Fingering/{R}.tsv').open(),delimiter='\t'))
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(SRC/f'Video/{R}.mp4')]))
dump('SOURCE_VIDEO_PROBE_R1.json',probe)
order=['WRIST','THUMB_CMC','THUMB_MCP','THUMB_IP','THUMB_TIP','INDEX_MCP','INDEX_PIP','INDEX_DIP','INDEX_TIP','MIDDLE_MCP','MIDDLE_PIP','MIDDLE_DIP','MIDDLE_TIP','RING_MCP','RING_PIP','RING_DIP','RING_TIP','LITTLE_MCP','LITTLE_PIP','LITTLE_DIP','LITTLE_TIP']
v=np.array([f['Right'] for f in a.values() if f['Right'] is not None]);assert v.shape[1:]==(21,3) and np.isfinite(v).all()
schema={'root_type':'object','frame_representation':'Contiguous decimal string keys 0..1369; values objects with Left and Right','frame_count':len(a),'hand_fields':['Left','Right'],'missing_hand':'JSON null; no per-landmark confidence in this sample','landmark_representation':'Array length 21 of arrays length 3 [x,y,z]','explicit_timestamp':False,'time_sec':'int(frame_key)/60','fps':60,'video_nb_frames':int(probe['streams'][0]['nb_frames']),'landmark_order':dict(enumerate(order)),'LANDMARK_ORDER_VERIFIED':True,'order_authority':['Dataset card: MediaPipe Hands 21 points','MediaPipe standard ordering; thumb0-4,index5-8,middle9-12,ring13-16,little17-20; visually verify overlay on downloaded video'],'coordinate_units':'Normalized image landmarks, not metric world coordinates','x_y':'Actual sample stores native normalized x,y near [0,1], x rightward/y downward; a few y outside 1. Do not apply repository GUI remapping [-1,1].','z':'MediaPipe relative-depth convention: wrist near zero, smaller nearer camera, approximate x normalized scale. Not calibrated metric depth.','aspect_correction':'x unchanged; y multiplied by 1080/1920; z unchanged. All axes then width-normalized.','json_Right_min_xyz':v.min((0,1)).tolist(),'json_Right_max_xyz':v.max((0,1)).tolist(),'json_Right_valid_frames':len(v),'json_Right_tracking_missing_begin_frames':39,'json_Right_tracking_missing_end_frames':185,'sources':['https://huggingface.co/datasets/PianoVAM/PianoVAM_v1','https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/python','https://github.com/yonghyunk1m/PianoVAM-Code']}
assert schema['frame_count']==schema['video_nb_frames'];dump('PIANOVAM_HANDSKELETON_SCHEMA_R1.json',schema)
# Direct MIDI parser: PPQ, variable-length delta, running status, tempo map. No MIDI-generated animation.
data=(SRC/f'MIDI/{R}.mid').read_bytes();header_len=int.from_bytes(data[4:8],'big');fmt,ntracks,ppq=struct.unpack('>HHH',data[8:14]);assert ppq<32768
events=[];offset=8+header_len
def vlq(d,i):
 val=0
 while True:
  b=d[i];i+=1;val=(val<<7)|(b&127)
  if b<128:return val,i
for track in range(ntracks):
 assert data[offset:offset+4]==b'MTrk';length=int.from_bytes(data[offset+4:offset+8],'big');d=data[offset+8:offset+8+length];offset+=8+length;i=0;tick=0;running=None
 while i<len(d):
  delta,i=vlq(d,i);tick+=delta;b=d[i]
  if b>=128:status=b;i+=1
  else:status=running
  assert status is not None
  if status==255:
   typ=d[i];i+=1;sz,i=vlq(d,i);payload=d[i:i+sz];i+=sz
   if typ==81:events.append((tick,'tempo',int.from_bytes(payload,'big')))
  elif status in (240,247):sz,i=vlq(d,i);i+=sz;running=None
  else:
   running=status;count=1 if status&240 in (192,208) else 2;payload=d[i:i+count];i+=count
   if status&240==144 and payload[1]>0:events.append((tick,'note_on',int(payload[0]),int(payload[1])))
tempo=500000;last_tick=0;seconds=0;midi_notes=[]
for event in sorted(events,key=lambda x:(x[0],x[1]!='tempo')):
 tick,typ,*payload=event;seconds+=(tick-last_tick)*tempo/1e6/ppq;last_tick=tick
 if typ=='tempo':tempo=payload[0]
 else:midi_notes.append({'onset':seconds,'note':payload[0],'velocity':payload[1]})
start,end=11.5,18.5;frames=list(range(690,1111));rightnotes=[n for n in notes if start<=float(n['onset'])<end and n['hand']=='R'];allnotes=[n for n in notes if start<=float(n['onset'])<end]
matches=[min(abs(n['onset']-float(t['onset'])) for n in midi_notes if n['note']==int(t['note'])) for t in notes]
schema['physical_right_source_field']='Left';schema['hand_label_semantics']='In this recording, JSON Left overlays physical right hand and JSON Right overlays physical left. Verified at source frames 300,420,600,780 against unmirrored piano video and thumb anatomy. Keep original JSON unchanged.';schema['handedness_overlay_evidence']=['overlay300.png','overlay420.png','overlay600.png','overlay780.png'];schema['physical_right_valid_frames']=sum(f['Left'] is not None for f in a.values());dump('PIANOVAM_HANDSKELETON_SCHEMA_R1.json',schema)
dump('PIANOVAM_SELECTED_WINDOW_R1.json',{'SOURCE_RECORDING_ID':R,'WINDOW_START_SEC':start,'WINDOW_END_SEC':end,'WINDOW_DURATION_SEC':end-start,'source_start_frame':frames[0],'source_end_frame_inclusive':frames[-1],'source_fps':60,'source_frame_count_including_endpoint':len(frames),'physical_right_source_field':'Left','RIGHT_HAND_VALID_FRAME_RATIO':sum(a[str(i)]['Left'] is not None for i in frames)/len(frames),'RIGHT_HAND_NOTE_COUNT':len(rightnotes),'RIGHT_HAND_FINGERS_PRESENT':sorted(set(int(n['finger']) for n in rightnotes)),'all_note_onsets_count':len(allnotes),'right_thumb_note_count':sum(n['finger']=='1' for n in rightnotes),'fingering_authority':'AUTOMATIC_PREDICTIONS_NOT_MANUAL_GT','missing_frames':[],'long_missing_intervals':0,'window_selection':'Complete physical-right tracking after video-verified hand label correction; all five R finger labels and continuous melodic activity. Seven seconds within shortest small solo sample.','midi_sync_check':{'midi_format':fmt,'ppq':ppq,'midi_note_on_count':len(midi_notes),'fingering_rows':len(notes),'max_onset_difference_sec':max(matches),'matching_onsets_within_1ms':all(x<.001 for x in matches)},'right_notes':rightnotes,'MOTION_AUTHORITY':'Handskeleton only; MIDI and Fingering select/synchronize, never generate rotations'})
def palm(p):
 y=p[9]-p[0];y/=np.linalg.norm(y);x=p[5]-p[17];x-=y*np.dot(x,y);x/=np.linalg.norm(x);z=np.cross(x,y);return np.column_stack([x,y,z])
ps=np.array([a[str(i)]['Left'] for i in frames]);ps[:,:,1]*=1080/1920;bs=np.array([palm(p) for p in ps]);local=np.array([(p-p[0])@b for p,b in zip(ps,bs)])
np.savez(OUT/'source_window_hand_local.npz',points=ps,bases=bs,local=local,source_frames=np.array(frames))
# Raw time sequence: overlay native image positions, plus two hand-local orthographic skeleton projections.
tmp=OUT/'raw_source_frames';tmp.mkdir(exist_ok=True);edges=[(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(0,9),(9,10),(10,11),(11,12),(0,13),(13,14),(14,15),(15,16),(0,17),(17,18),(18,19),(19,20),(5,9),(9,13),(13,17)]
for j in range(210):
 p=ps[j*2];l=local[j*2];im=Image.new('RGB',(960,420),(28,34,42));dr=ImageDraw.Draw(im);dr.text((16,12),f'RAW physical-right (JSON Left) | t={start+j/30:.3f}s | no smoothing',(235,235,235))
 for column,coords,title in [(0,(p[:,:2]-p[0,:2])*1800,'Camera XY aspect-corrected'),(1,l[:,:2]*1800,'Palm-local X/Y'),(2,l[:,[1,2]]*1800,'Palm-local Y/Z')]:
  c=coords.copy();c[:,1]*=-1 if column>0 else 1;c+=np.array([column*320+140,250]);dr.text((column*320+16,42),title,(170,195,220))
  for u,w in edges:dr.line([tuple(c[u]),tuple(c[w])],fill=(100,190,220),width=3)
  for k,(x,y) in enumerate(c):dr.ellipse((x-3,y-3,x+3,y+3),fill=(245,180,110));dr.text((x+4,y),str(k),fill=(230,230,230))
 im.save(tmp/f'{j:04}.png')
subprocess.run(['ffmpeg','-y','-v','error','-framerate','30','-i',str(tmp/'%04d.png'),'-frames:v','210','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart',str(OUT/'RAW_SOURCE_LANDMARK_PREVIEW.mp4')],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-ss',str(start),'-i',str(SRC/f'Video/{R}.mp4'),'-t',str(end-start),'-vf','scale=960:540','-c:v','libx264','-crf','22','-c:a','aac','-movflags','+faststart',str(OUT/'source_window.mp4')],check=True)
print('SOURCE_INSPECTION_DONE',len(rightnotes),max(matches))
