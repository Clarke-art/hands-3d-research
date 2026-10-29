from common import *
import subprocess,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
begin=time.perf_counter();FF='D:/ffmpeg/bin/ffmpeg.exe';FP='D:/ffmpeg/bin/ffprobe.exe'
FONT='C:/Windows/Fonts/msyh.ttc'
font=lambda size:ImageFont.truetype(FONT,size)
GREEN='#35e38a';CYAN='#00e5ff';GOLD='#ffda57';RED='#ff485d';PINK='#ff73e7';WHITE='#eeeeee'
rows=read(OUT/'STILL_PROJECTIONS.json');deep=read(OUT/'INDEX_BLACK_KEY_REAL_GEOMETRY.json');geo=read(OUT/'ANATOMICAL_SAMPLES_AND_METHOD.json');keys=read(OLD/'KEYBOARD_88_KEY_TABLE_R1.json')['keys']
M=np.array(geo['camera_matrix']);W=geo['orthographic_scale'];H=W*720/1280
def px(x,y):return ((x-M[0,3])/W*1280+640,360-(y-M[1,3])/H*720)
def hull(points):
    a=sorted(set(map(tuple,points)))
    def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    low=[];up=[]
    for p in a:
        while len(low)>=2 and cross(low[-2],low[-1],p)<=0:low.pop()
        low.append(p)
    for p in reversed(a):
        while len(up)>=2 and cross(up[-2],up[-1],p)<=0:up.pop()
        up.append(p)
    return low[:-1]+up[:-1]
def cross(d,p,color,r=5,width=2):
    x,y=p;d.line((x-r,y,x+r,y),fill=color,width=width);d.line((x,y-r,x,y+r),fill=color,width=width)
def dash(d,a,b,color,width=2):
    a=np.array(a);b=np.array(b);length=np.linalg.norm(b-a)
    for t in np.arange(0,length,8):
        x=a+(b-a)*t/length;y=a+(b-a)*min(t+4,length)/length;d.line([tuple(x),tuple(y)],fill=color,width=width)
def seam(d,r):
    f=r['finger'];k=next(a for a in keys if a['note_name']==f['key']);a=k['key_top_playable_surface'][0]
    if k['color']!='WHITE':return
    whites=[b for b in keys if b['color']=='WHITE'];i=whites.index(k);left=f['pad_x_fraction']<.5
    n=whites[i-1 if left else i+1]['key_top_playable_surface'][0]
    x=(a['xmin']+n['xmax'])/2 if left else (a['xmax']+n['xmin'])/2
    dash(d,px(x,.004),px(x,.047),PINK)
def annotate(im,r):
    im=im.convert('RGB');d=ImageDraw.Draw(im);f=r['finger'];idle=r['state']['role']=='IDLE';color=RED if idle else GREEN
    for a in f['target_surfaces']:d.line([tuple(p) for p in a['pixels']]+[tuple(a['pixels'][0])],fill=color,width=2)
    hp=hull(f['cap_pixels'])
    if hp:d.line(hp+[hp[0]],fill=WHITE,width=2)
    seam(d,r);cross(d,f['pad_pixel'],CYAN,r=5);x,y=f['terminal_pixel'];d.ellipse((x-3,y-3,x+3,y+3),outline=GOLD,width=2)
    risk=next((x for x in deep if abs(x['time']-r['time'])<1e-7 and x['vertex_peak_mm']>0),None)
    if risk:
        for p in risk['penetration_pixels']:cross(d,p,RED,2,1)
        cross(d,risk['witness_pixel'],RED,7,2)
    d.text((f['pad_pixel'][0]-48,f['pad_pixel'][1]+12),f"R{f['finger']} {f['key']}",font=font(15),fill=CYAN,stroke_width=2,stroke_fill='#222222')
    return im
captions={
'01_INDEX_ACTIVE_A4':['食指正在按A4：pad在左侧约13%键宽处。','原接触PASS；末端皮肤投影有部分超出目标键面。','该时刻未检出食指黑键内部顶点；不等于整段无碰撞。'],
'02_MIDDLE_ACTIVE_B4':['中指正在按B4：pad偏右；末端与无名指在俯视下挤近。','轮廓包络由实际末端皮肤投影生成，不是接触斑。','当前食指已结束A4释放，属于IDLE。'],
'03_MIDDLE_ACTIVE_C5':['中指正在按C5：pad靠右，末端皮肤更接近C#5。','相邻HOLD采样检出C#5皮肤顶点侵入，详见机器JSON。','有实际三维依据，不能仅用“俯视错觉”解释。'],
'04_INDEX_IDLE_GSHARP':['食指此时IDLE；碰撞对象G#4不是其触键目标。','红色为真实内部皮肤顶点：最大深度4.328mm。','终端皮肤区域侵入，非仅二维轮廓重叠。'],
'05_INDEX_IDLE_ASHARP':['食指此时IDLE；当前活动音为拇指G4。','A#4：内部顶点5.604mm，三角面深度5.637mm。','红色标记来自真实三维皮肤与实际键体。'],
'06_C1_B01_HANDOFF':['原C1：B4持键末段，C5即将起音。','中指与无名指粘连保留，不能用候选替代基线。','食指IDLE；不承担B4或C5的活动触键。'],
'07_B01_CANDIDATE_B4':['B01失败候选：中指pad向B4内部移动约0.938mm。','本时刻侧边余量由3.665增至4.544mm。','两指分离改善；不代表已获准使用。'],
'08_B01_CANDIDATE_PRE_C5':['B01失败候选：无名指PREPARE，尚未到C5起音。','pad已低于C5键面约0.532mm；历史深查0.647mm。','活动接触PASS不检查此提前入键时刻。']}
outputs=[]
for r in rows:
    im=annotate(Image.open(r['raw_path']),r);canvas=Image.new('RGB',(1920,1080),'#141b24');canvas.paste(im,(0,64));zoom=im.crop((610,80,910,400)).resize((600,640),Image.Resampling.LANCZOS);canvas.paste(zoom,(1300,80));d=ImageDraw.Draw(canvas)
    title=f"DIAGNOSTIC_ONLY | {r['identity']} | t={r['time']:.6f}s | R{r['finger']['finger']} {r['state']['role']}"
    d.text((22,16),title,font=font(25),fill=WHITE)
    d.text((1310,736),'同一正俯视画面局部放大 2×',font=font(22),fill=WHITE)
    f=r['finger'];txt=captions[r['name']]
    for i,t in enumerate(txt):d.text((26,810+i*38),t,font=font(24),fill=WHITE)
    d.text((1110,810),'青十字：真实skin pad',font=font(22),fill=CYAN);d.text((1110,848),'黄圈：固定末端皮肤顶点',font=font(22),fill=GOLD)
    d.text((1110,886),'白线：末端皮肤投影包络',font=font(22),fill=WHITE);d.text((1110,924),'绿框：合法键面；粉虚线：键缝',font=font(22),fill=GREEN)
    d.text((26,957),f"pad XYZ (mm): {', '.join(f'{v*1000:.3f}' for v in f['pad_world_m'])}   |   terminal vertex {f['terminal_vertex']}",font=font(21),fill='#bec8d7')
    d.text((26,997),'标注为三维几何经原STAGE_C_OVERHEAD投影；未修改动作；包络不代表物理接触面积。',font=font(22),fill='#bec8d7')
    path=OUT/(r['name']+'_DIAGNOSTIC_ONLY.png');assert not path.exists();canvas.save(path);outputs.append(str(path))

video=safe(C1/'normal_speed_overhead.mp4');READS[str(video)]=sha(video);assert sha(video)=='08a5ccc7cf679722f6a5fdde4c1c77de41b6ac1ce2d19c71bc0df8354ceb6da4'
frames=read(OUT/'FULL_VIDEO_357_FRAME_PROJECTIONS.json')['frames'];silent=OUT/'ANNOTATED_SILENT.mp4'
dec=subprocess.Popen([FF,'-v','error','-i',str(video),'-map','0:v:0','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
enc=subprocess.Popen([FF,'-v','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','60','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(silent)],stdin=subprocess.PIPE)
check=[]
for r in frames:
    raw=dec.stdout.read(1280*720*3);assert len(raw)==1280*720*3
    im=Image.frombytes('RGB',(1280,720),raw);d=ImageDraw.Draw(im)
    d.rectangle((0,0,1280,30),fill='#111923');d.text((12,3),f"DIAGNOSTIC_ONLY | ORIGINAL C1 | t={r['time']:.3f}s | 1x",font=font(18),fill=WHITE)
    active=r['active']
    for a in active:
        for surf in a['surfaces']:d.line([tuple(p) for p in surf['pixels']]+[tuple(surf['pixels'][0])],fill=GREEN,width=2)
        cross(d,a['pad'],CYAN);x,y=a['terminal'];d.ellipse((x-3,y-3,x+3,y+3),outline=GOLD,width=2)
        d.text((a['pad'][0]-30,a['pad'][1]+13),f"R{a['finger']} {a['key']}",font=font(14),fill=CYAN,stroke_width=1,stroke_fill='black')
    d.rectangle((0,666,1280,720),fill='#111923');label=' / '.join(f"{a['event']} {a['key']} R{a['finger']} ACTIVE" for a in active) or '无右手活动音（准备/释放/尾段仍保留）'
    d.text((12,670),label+'   | 青：skin pad   黄：末端皮肤点   绿：合法键面',font=font(18),fill=WHITE)
    risk=r['risk']
    if risk:
        for p in risk['pixels']:cross(d,p,RED,2,1)
        d.text((12,694),f"食指 {risk['index_role']} / {risk['key']} 真皮肤顶点侵入 {risk['vertex_depth_mm']:.3f}mm；红色为内部点",font=font(17),fill=RED)
    else:d.text((12,694),'完整23音原C1；点接触PASS不等于整指/邻键几何PASS；动作与音轨原样保留。',font=font(17),fill='#bbc8d8')
    enc.stdin.write(im.tobytes())
    if r['frame'] in [27,67,79,157,208]:
        p=OUT/f"VIDEO_QC_{r['frame']:03d}.png";im.save(p);check.append(str(p))
assert dec.stdout.read(1)==b'';dec.stdout.close();assert dec.wait()==0;enc.stdin.close();assert enc.wait()==0
dest=OUT/'C1_OVERHEAD_ALIGNMENT_DIAGNOSTIC_1X.mp4'
subprocess.run([FF,'-v','error','-n','-i',str(silent),'-i',str(video),'-map','0:v:0','-map','1:a:0','-c','copy','-t','5.95','-movflags','+faststart',str(dest)],check=True)
probe=json.loads(subprocess.check_output([FP,'-v','error','-show_streams','-show_format','-of','json',str(dest)]));v=next(x for x in probe['streams'] if x['codec_type']=='video');assert v['nb_frames']=='357' and v['avg_frame_rate']=='60/1' and abs(float(v['duration'])-5.95)<1e-6
subprocess.run([FF,'-v','error','-i',str(dest),'-f','null','-'],check=True)
def pcm(p):return subprocess.check_output([FF,'-v','error','-i',str(p),'-map','0:a:0','-f','s16le','-acodec','pcm_s16le','pipe:1'])
a=pcm(video);b=pcm(dest);assert a==b
save('MEDIA_QC_AND_SHA.json',dict(seconds=time.perf_counter()-begin,images=outputs,video=str(dest),video_sha256=sha(dest),probe=probe,frames=357,fps=60,duration_sec=5.95,audio_pcm_identical_to_C1=True,audio_pcm_sha256=hashlib.sha256(a).hexdigest(),diagnostic_only=True,original_video_sha256=sha(video),qc_frames=check))
protection('MEDIA_INPUT_SHA_RECEIPT.json');print('MEDIA_COMPLETE',time.perf_counter()-begin,flush=True)
