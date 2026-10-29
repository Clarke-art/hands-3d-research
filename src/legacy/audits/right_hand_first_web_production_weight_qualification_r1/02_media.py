"""Three product videos, four temporal scan sheets, two required pose plates."""
from pathlib import Path
import json,subprocess,hashlib
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
PRODUCT=ROOT/'audits/right_hand_first_web_product_impact_go_no_go_r1'
VIEWS=['DEFAULT_TEACHING_VIEW','NORMAL_ORBIT_VIEW','REASONABLE_CLOSE_VIEW']
FF='D:/ffmpeg/bin/ffmpeg.exe';FP='D:/ffmpeg/bin/ffprobe.exe'
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def font(n,bold=False):return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if bold else 'segoeui.ttf'),n)
BG='#101c28';FG='#e3edf5';MUTED='#aabed0'
assert (OUT/'APPROVED_POSE_REGRESSION_R1.json').exists(),'Wait for actual read-only qualification render completion'
def frame(v,f):return OUT/'_tmp/motion_frames'/f'CANDIDATE__F{f:03}__{v}.png'
assert all(frame(v,f).exists() for v in VIEWS for f in range(1,211))
def textfilter(text,x):
    return "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='"+text+f"':x={x}:y=12:fontcolor=white:fontsize=22:box=1:boxcolor=black@0.6"
def encode(args,path):
    subprocess.run([FF,'-y','-loglevel','error',*args,'-frames:v','210','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(path)],check=True)
    meta=json.loads(subprocess.check_output([FP,'-v','error','-show_entries','stream=width,height,nb_frames,r_frame_rate:format=duration','-of','json',str(path)]))
    assert abs(float(meta['format']['duration'])-7)<.001 and meta['streams'][0]['nb_frames']=='210'
    return {'path':path.name,'metadata':meta,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
args=[]
for v in VIEWS:args+=['-framerate','30','-start_number','1','-i',str(OUT/'_tmp/motion_frames'/f'CANDIDATE__F%03d__{v}.png')]
filt='[0:v][1:v][2:v]hstack=inputs=3,'+','.join(textfilter(v.replace('_',' '),i*960+12) for i,v in enumerate(VIEWS))+'[out]'
videos=[encode(args+['-filter_complex',filt,'-map','[out]'],OUT/'product_7s_candidate_three_views.mp4')]
for v,offset in [('NORMAL_ORBIT_VIEW',960),('REASONABLE_CLOSE_VIEW',1920)]:
    baseline=PRODUCT/f'product_7s_{v.lower()}.mp4'
    filt=f'[1:v]crop=960:900:{offset}:0[c];[0:v][c]hstack=inputs=2,'+textfilter('BASELINE - FROZEN',12)+','+textfilter('CANDIDATE - SAME APPROVED FIELD',972)+'[out]'
    videos.append(encode(['-i',str(baseline),'-i',str(OUT/'product_7s_candidate_three_views.mp4'),'-filter_complex',filt,'-map','[out]'],OUT/f'product_7s_matched_{v.lower()}.mp4'))
dump('VIDEO_VERIFICATION_R1.json',{'status':'PASS','duration_seconds':7,'fps':30,'frames':210,'views':VIEWS,'videos':videos,'matched_baseline':'Reused byte-protected existing product video; no baseline motion rerender','all_integer_camera_definitions_identical':True})
(OUT/'contact_sheets').mkdir(exist_ok=True)
segments={'EARLY':[1,7,13,19,25,31,37,43,49,55,61,67],'MID':[73,78,83,88,93,98,103,108,110,112,114,116],'PROBLEM_ZONE':[119,124,127,130,136,142,148,154,160,164,168,172],'LATE':[176,179,182,185,188,191,194,197,200,203,205,210]}
contact_records=[]
for segment,frames in segments.items():
    cv=Image.new('RGB',(1920,2650),BG);d=ImageDraw.Draw(cv)
    d.text((20,18),'FULL 7s MOTION | '+segment+' | REASONABLE_CLOSE_VIEW',font=font(31,True),fill=FG)
    d.text((20,63),'Same candidate / mature product camera / no repair. Timeline scan; full playback provided separately.',font=font(24),fill=MUTED)
    for index,f in enumerate(frames):
        x=(index%3)*640;y=110+(index//3)*635
        d.text((x+10,y+5),f'F{f:03} | {11.5+(f-1)/30:.3f}s source | {(f-1)/30:.3f}s clip',font=font(23),fill=FG)
        im=Image.open(frame('REASONABLE_CLOSE_VIEW',f)).convert('RGB');im.thumbnail((640,600));cv.paste(im,(x,y+36))
    dst=OUT/'contact_sheets'/f'{segment}_R1.png';cv.save(dst)
    contact_records.append({'segment':segment,'view':'REASONABLE_CLOSE_VIEW','frames':frames,'path':dst.relative_to(OUT).as_posix()})
def pose_plate(poses,views,width,title,name):
    cell=width//(len(views)*2);rh=int(cell*900/960)+58
    cv=Image.new('RGB',(width,110+rh*len(poses)),BG);d=ImageDraw.Draw(cv)
    d.text((20,18),title,font=font(30,True),fill=FG)
    d.text((20,60),'Mature product directions / normal scales. Baseline LEFT, candidate RIGHT within each view.',font=font(23),fill=MUTED)
    for row,pose in enumerate(poses):
        for col,(view,label) in enumerate([(v,l) for v in views for l in ['BASELINE','CANDIDATE']]):
            x=col*cell;y=110+row*rh
            d.text((x+8,y+3),pose+' | '+label,font=font(19,True),fill=FG);d.text((x+8,y+27),view,font=font(15),fill=MUTED)
            im=Image.open(OUT/'pose_renders'/f'{label}__{pose}__{view}.png').convert('RGB');im.thumbnail((cell,rh-56));cv.paste(im,(x,y+54))
    cv.save(OUT/name)
pose_plate(['ZERO','INDEX_MCP_45','CMC_OPP_30','FULL_OPP_L1','FULL_OPP_L2','FULL_OPP_L3'],['DEFAULT_TEACHING_VIEW','REASONABLE_CLOSE_VIEW'],1920,'APPROVED POSE REGRESSION | EXISTING CANDIDATE','EVIDENCE_APPROVED_POSE_REGRESSION_R1.png')
pose_plate(['ZERO'],VIEWS,2880,'ZERO / RSSF | BASIS AND REST UNCHANGED','EVIDENCE_ZERO_R1.png')
dump('CONTACT_SHEET_DEFINITION_R1.json',{'purpose':'Few temporal scan sheets across entire 7 seconds, not 421 individual reports','sheets':contact_records,'followup_policy':'Only expand adjacent frames if suspicious visible interval is found; no repair allowed','candidate_motion_frame_intermediates':'_tmp/motion_frames/; only video source frames, no individual per-frame diagnosis reports'})
print('QUALIFICATION_MEDIA_COMPLETE_3_VIDEOS_4_CONTACT_SHEETS_2_POSE_PLATES',flush=True)
