from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import numpy as np,subprocess,json
P=Path(__file__).resolve().parent;ROOT=P.parents[1];H=764
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20);bold=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',23)
def title(im,j,label):
 d=ImageDraw.Draw(im);d.text((16,8),f'{label} | source t={11.5+j/30:.3f}s | frame {j+1}/210',font=bold,fill='#edf4fc');d.text((16,42),'DISPLAY_ONLY REVIEW OFFSETS | NOT PIANO-SPATIALIZED',font=font,fill='#ffd296');d.text((16,H-29),'PianoVAM | CC BY-NC-SA 4.0 | INTERNAL NONCOMMERCIAL VALIDATION ONLY',font=font,fill='#b8cadb');return d
def teaching(j):
 im=Image.new('RGB',(1200,H),'#111c28');d=title(im,j,'DUAL TEACHING VIEW');im.paste(Image.open(P/'_render_frames/DUAL_TEACHING_VIEW'/f'{j:04}.png').convert('RGB'),(0,76));d.text((22,85),'PHYSICAL LEFT / source Right',font=font,fill='#71e6c5');d.text((660,85),'PHYSICAL RIGHT / source Left',font=font,fill='#ffb097');return im
def detail(j):
 im=Image.new('RGB',(1200,H),'#111c28');d=title(im,j,'LEFT + RIGHT DETAIL VIEWS')
 for col,s in enumerate(['L','R']):im.paste(Image.open(P/f'_render_frames/{s}_DETAIL_VIEW'/f'{j:04}.png').convert('RGB'),(col*600,76))
 d.text((18,85),'PHYSICAL LEFT | fixed close orientation',font=font,fill='#71e6c5');d.text((618,85),'PHYSICAL RIGHT | fixed close orientation',font=font,fill='#ffb097');return im
def encode(name,w):return subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{w}x{H}','-framerate','30','-i','-','-an','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(P/name)],stdin=subprocess.PIPE)
srcdir=ROOT/'references/piano_motion/pianovam_sample_r1';rec='2024-03-04_03-46-36';data=json.loads((srcdir/f'Handskeleton/{rec}.json').read_text());points={s:np.array([data[str(i)][field] for i in range(690,1111)])[:,:,:2]*[960,540] for s,field in [('L','Right'),('R','Left')]}
xy=np.concatenate(list(points.values()),axis=1);lo=np.floor(xy.min((0,1))-35).astype(int);hi=np.ceil(xy.max((0,1))+35).astype(int);box=(max(0,int(lo[0])),max(0,int(lo[1])),min(960,int(hi[0])),min(540,int(hi[1])))
decoder=subprocess.Popen(['ffmpeg','-v','error','-ss','11.5','-i',str(srcdir/f'Video/{rec}.mp4'),'-t','7','-vf','fps=30,scale=960:540','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
encoders=[encode('product_7s_dual_teaching_view.mp4',1200),encode('product_7s_dual_detail_views.mp4',1200),encode('product_7s_dual_with_source_reference.mp4',1800)]
edges=[(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(0,9),(9,10),(10,11),(11,12),(0,13),(13,14),(14,15),(15,16),(0,17),(17,18),(18,19),(19,20)]
for j in range(210):
 teach=teaching(j);det=detail(j);buf=decoder.stdout.read(960*540*3);assert len(buf)==960*540*3;src=Image.frombytes('RGB',(960,540),buf);d=ImageDraw.Draw(src)
 for s,color in [('L','#27ffc7'),('R','#ff8976')]:
  pts=points[s][j*2]
  for a,b in edges:d.line([tuple(pts[a]),tuple(pts[b])],fill=color,width=2)
  for x,y in pts:d.ellipse((x-2,y-2,x+2,y+2),fill=color)
 ref=Image.new('RGB',(1800,H),'#111c28');ref.paste(teach,(0,0));ref.paste(ImageOps.pad(src.crop(box),(600,580),color='#111c28'),(1200,130));d=ImageDraw.Draw(ref);d.text((1210,12),'SAME RECORDING / SAME SOURCE TIME',font=font,fill='#e8eff8');d.text((1210,47),'GREEN = PHYSICAL LEFT (JSON Right)',font=font,fill='#71e6c5');d.text((1210,78),'CORAL = PHYSICAL RIGHT (JSON Left)',font=font,fill='#ffb097');d.text((1210,110),'Unmirrored video + actual landmarks',font=font,fill='#b8cadb');d.text((1210,H-29),'REFERENCE ONLY / contact unvalidated',font=font,fill='#ffd296')
 for enc,im in zip(encoders,[teach,det,ref]):enc.stdin.write(im.tobytes())
 if j==0:ref.save(P/'review_poster.png')
for enc in encoders:enc.stdin.close();assert enc.wait()==0
decoder.stdout.close();assert decoder.wait()==0
for name,indices in [('EARLY',[0,30,60]),('MID',[75,105,135]),('LATE',[150,180,209])]:
 sheet=Image.new('RGB',(1600,3*510),'#111c28')
 for row,j in enumerate(indices):
  pair=Image.new('RGB',(2400,H));pair.paste(teaching(j),(0,0));pair.paste(detail(j),(1200,0));sheet.paste(pair.resize((1600,510)),(0,row*510))
 sheet.save(P/f'{name}.png')
probes={}
for f in P.glob('product_7s_*.mp4'):
 p=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(f)]));s=p['streams'][0];assert s['nb_read_frames']=='210' and s['r_frame_rate']=='30/1' and float(p['format']['duration'])==7
 probes[f.name]=p
(P/'VIDEO_VERIFICATION_R1.json').write_text(json.dumps({'status':'PASS','frames_per_video':210,'fps':30,'duration':7,'source_crop_960x540':box,'source_video_is_unmirrored':True,'probes':probes},indent=2),encoding='utf-8')
print('THREE_FULL_7_SECOND_VIDEOS_VERIFIED')
