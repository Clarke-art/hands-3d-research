import json,hashlib,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;ROOT=P.parents[1];S=ROOT/'audits/minuet_stage_c_lightweight_animation_poc_r1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.file_digest(open(p,'rb'),'sha256').hexdigest()
old=read(S/'PROTECTED_INPUTS_BEFORE.json');changed=[p for p,h in old.items() if not Path(p).exists() or sha(p)!=h]
assert not changed,changed
files={str(p):sha(p) for p in S.rglob('*') if p.is_file()}
files.update(old)
(P/'PROTECTED_INPUTS_BEFORE.json').write_text(json.dumps(files,indent=2),encoding='utf8')
assert sha(Path(read(S/'SCENE_MANIFEST.json')['path']))==read(S/'SCENE_MANIFEST.json')['sha256']
for name,data in read(S/'VIDEO_VERIFICATION.json').items():
 if name.startswith('normal_speed'):assert sha(S/name)==data['sha256']
rows=read(P/'SKIN_KEY_SAMPLES.json')['rows']
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for start in range(0,23,4):
 subset=rows[start:start+4];im=Image.new('RGB',(1920,len(subset)*400),'#182127');d=ImageDraw.Draw(im)
 for y,r in enumerate(subset):
  n=r['note'];d.text((8,y*400),f"{n['note_id']} {n['hand']} finger {n['finger']} {n['note_name']} | video {n['note_on']:.6f} - {n['note_off']:.6f}",font=font,fill='white')
  for x,phase in enumerate(['on','hold','release']):
   a=next(s for s in r['samples'] if s['phase']==phase);img=Image.open(S/f"_frames/TEACHING/{a['frame']:04d}.png");im.paste(img.resize((640,360)),(x*640,y*400+40));d.text((x*640+4,y*400+22),f"{phase}: frame {a['frame']} / {a['frame']/60:.6f}s",font=font,fill='white')
 im.save(P/f'contact_sheet_{start//4+1}.jpg',quality=93)
for r in rows:
 n=r['note'];print(n['note_id'],n['note_name'],n['finger'],round(n['note_on'],6),round(n['note_off'],6),[(s['phase'],round(s['skin_marker_gap_mm'],2),round(s['skin_marker_horizontal_mm'],2),round(s['nearest_patch_vertex_gap_mm'],2) if s['nearest_patch_vertex_gap_mm'] is not None else None,round(s['key_angle_rad'],4)) for s in r['samples']])
print('PROTECTED',len(files),'HISTORICAL_HASH_MATCH',len(old))
