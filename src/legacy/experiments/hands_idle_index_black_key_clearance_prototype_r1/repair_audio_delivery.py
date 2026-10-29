from common import *
import subprocess
FF='D:/ffmpeg/bin/ffmpeg.exe';FP='D:/ffmpeg/bin/ffprobe.exe'
def run(args):
 r=subprocess.run(args,cwd=OUT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf8',errors='replace');assert r.returncode==0,r.stderr[-2000:];return r.stdout
rows=[];names=[]
for speed,tag,count in [(1,'1X',173),(.5,'0_5X',346)]:
 old=OUT/f'FINAL_C1_VS_IDLE_INDEX_B_OVERHEAD_{tag}.mp4';new=OUT/f'VERIFIED_C1_VS_IDLE_INDEX_B_OVERHEAD_{tag}.mp4';duration=count/60
 cmd=[FF,'-v','error','-i',str(old),'-i',str(OUT/'final_comparison_audio.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k']
 if speed==.5:cmd+=['-af','atempo=0.5,apad']
 cmd+=['-t',str(duration),'-movflags','+faststart',str(new)];run(cmd)
 meta=json.loads(run([FP,'-v','error','-show_streams','-show_format','-of','json',str(new)]))
 vi=next(s for s in meta['streams'] if s['codec_type']=='video');au=next(s for s in meta['streams'] if s['codec_type']=='audio');assert int(vi['nb_frames'])==count;assert abs(float(au['duration'])-duration)<.025
 def video_hash(p):return run([FF,'-v','error','-i',str(p),'-map','0:v:0','-c:v','copy','-f','hash','-hash','sha256','-']).strip()
 assert video_hash(old)==video_hash(new)
 rows.append(dict(path=str(new),sha256=sha(new),metadata=meta,visual_elementary_stream_unchanged=True,complete_audio=True));names.append((old.name,new.name))
save('VERIFIED_MEDIA_AUDIO_AND_VIDEO_RECEIPT.json',dict(rows=rows,reason='Initial -frames:v encoding truncated buffered AAC audio. Remux identical verified video elementary streams with complete original trimmed WAV; atempo 0.5 from full WAV for slow version. No motion change.'))
for name in ['TECHNICAL_REPORT.md','HUMAN_REVIEW.md']:
 p=OUT/name;before=p.read_text(encoding='utf8')
 backup=OUT/(p.stem+'_PRE_AUDIO_VERIFICATION.md')
 with backup.open('x',encoding='utf8') as f:f.write(before)
 after=before
 for old,new in names:after=after.replace(old,new)
 after=after.replace('以 FINAL 版本为准','以 VERIFIED 版本为准').replace('以下 FINAL 媒体','以下 VERIFIED 媒体')
 after=after.replace('早期无 FINAL 前缀媒体为保留过程证据','早期非 VERIFIED 媒体为保留过程证据')
 if name=='TECHNICAL_REPORT.md':after+='\n最终音轨补充复核：初次带 FINAL 前缀的视频受编码器提前结束影响，1×音轨被截短；现用完整原 C1 裁切 WAV 重新封装，VERIFIED 两版保留完全相同 H.264 视频流，分别 173/346 帧，音轨覆盖全部约 2.883/5.767s。以 VERIFIED 版本为交付依据。详见 VERIFIED_MEDIA_AUDIO_AND_VIDEO_RECEIPT.json。\n'
 p.write_text(after,encoding='utf8')
files=['TECHNICAL_REPORT.md','HUMAN_REVIEW.md','RESULT.json','QUANTITATIVE_TABLE.csv','VERIFIED_C1_VS_IDLE_INDEX_B_OVERHEAD_1X.mp4','VERIFIED_C1_VS_IDLE_INDEX_B_OVERHEAD_0_5X.mp4','A_BEFORE_AFTER_GEOMETRY.png','B_BEFORE_AFTER_GEOMETRY.png','IDLE_INDEX_CLEARANCE_B_NOT_APPROVED.blend','PROTECTED_AFTER_AND_SHA256_RECEIPT.json','VERIFIED_MEDIA_AUDIO_AND_VIDEO_RECEIPT.json']
save('VERIFIED_FINAL_DELIVERY_MANIFEST.json',dict(result='PARTIAL',supersedes='FINAL_DELIVERY_MANIFEST.json',files=[dict(path=str(OUT/n),sha256=sha(OUT/n)) for n in files],stop='HUMAN REVIEW'))
protected=read(OUT/'PROTECTED_AFTER_AND_SHA256_RECEIPT.json');assert all(sha(r['path'])==r['before'] for r in protected['files'])
save('VERIFIED_FINAL_POST_REPORT_CHECK.json',dict(result='PARTIAL',delivery_hashes_pass=True,protected_inputs_still_unchanged=True,protected_input_count=len(protected['files']),audio_complete=True,motion_candidate_unchanged=sha(OUT/'IDLE_INDEX_CLEARANCE_B_NOT_APPROVED.blend')==read(OUT/'CANDIDATE_RECEIPT.json')['sha256'],stop='HUMAN REVIEW'))
print('VERIFIED_DELIVERY_COMPLETE',[(r['metadata']['format']['filename'],[(s['codec_type'],s.get('duration'),s.get('nb_frames')) for s in r['metadata']['streams']]) for r in rows],flush=True)
