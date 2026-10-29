from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import numpy as np,subprocess,json
P=Path(__file__).resolve().parent;ROOT=P.parents[1];pts=np.load(P/'physical_left_source_window.npz')['native_points']
xy=pts[:,:,:2]*np.array([960,540]);lo=np.floor(xy.min((0,1))-35).astype(int);hi=np.ceil(xy.max((0,1))+35).astype(int);box=(max(0,int(lo[0])),max(0,int(lo[1])),min(960,int(hi[0])),min(540,int(hi[1])))
video=ROOT/'references/piano_motion/pianovam_sample_r1/Video/2024-03-04_03-46-36.mp4'
decoder=subprocess.Popen(['ffmpeg','-v','error','-ss','11.5','-i',str(video),'-t','7','-vf','fps=30,scale=960:540','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
encoder=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','1800x744','-framerate','30','-i','-','-an','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(P/'product_7s_left_matched_reference.mp4')],stdin=subprocess.PIPE)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20);bold=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',23)
edges=[(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(0,9),(9,10),(10,11),(11,12),(0,13),(13,14),(14,15),(15,16),(0,17),(17,18),(18,19),(19,20)]
for j in range(210):
 buf=decoder.stdout.read(960*540*3);assert len(buf)==960*540*3
 src=Image.frombytes('RGB',(960,540),buf);draw=ImageDraw.Draw(src)
 for a,b in edges:draw.line([tuple(xy[j*2,a]),tuple(xy[j*2,b])],fill='#27ffc7',width=2)
 for x,y in xy[j*2]:draw.ellipse((x-2,y-2,x+2,y+2),fill='#27ffc7')
 tile=ImageOps.pad(src.crop(box),(600,660),color='#101b27')
 im=Image.new('RGB',(1800,744),'#101b27');d=ImageDraw.Draw(im);d.text((16,8),f'PHYSICAL LEFT | matched source t={11.5+j/30:.3f}s | CC BY-NC-SA 4.0 | INTERNAL ONLY',font=bold,fill='#e4edf5')
 for col,label in enumerate(['SOURCE VIDEO + ACTUAL LEFT LANDMARKS','DEFAULT_TEACHING_VIEW','REASONABLE_CLOSE_VIEW']):d.text((col*600+14,47),label,font=font,fill='#b7d7df')
 im.paste(tile,(0,84))
 for col,view in [(1,'DEFAULT_TEACHING_VIEW'),(2,'REASONABLE_CLOSE_VIEW')]:im.paste(Image.open(P/'_render_frames'/view/f'{j:04}.png').convert('RGB'),(col*600,84))
 encoder.stdin.write(im.tobytes())
 if j==150:im.save(P/'MATCHED_SOURCE_CHECK.png')
encoder.stdin.close();assert encoder.wait()==0;decoder.stdout.close();assert decoder.wait()==0
# A single bounded interval after visible change between late overview frames.
sheet=Image.new('RGB',(1800,2*714),'#101b27');d=ImageDraw.Draw(sheet)
for k,j in enumerate([150,153,156,159,162,165]):
 x=(k%3)*600;y=(k//3)*714;d.text((x+12,y+10),f'INDEX/TIP CHECK t={11.5+j/30:.3f}s',font=bold,fill='#e4edf5');sheet.paste(Image.open(P/'_render_frames'/'DEFAULT_TEACHING_VIEW'/f'{j:04}.png'),(x,y+54))
sheet.save(P/'PROBLEM_ZONE.png')
(P/'MATCHED_REFERENCE_METADATA_R1.json').write_text(json.dumps({'source_recording':'2024-03-04_03-46-36','time_range':[11.5,18.5],'physical_left_field':'Right','overlay':'Original actual LEFT x/y, no reflection on source video','fixed_source_crop_960x540':box,'frames':210,'duration':7,'PURPOSE':'Reference-only correspondence; no piano/contact integration','bounded_review_interval':[16.5,17.0],'reason':'Visible index extension/flexion difference in LATE sheet; no machine ranking'},indent=2),encoding='utf-8')
print('MATCHED_REFERENCE_COMPLETE')
