import sys, os, json, hashlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
PREV=ROOT/'experiments/hands_index_root_webspace_anatomy_repair_r1'
MATCH=ROOT/'experiments/hands_anatomical_whole_hand_pose_repair_r1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(name,obj):
    with (OUT/name).open('x',encoding='utf8') as f:json.dump(obj,f,ensure_ascii=False,indent=2)
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
F=np.array(read(PREV/'NATIVE_TOPOLOGY.json')['faces'],int)
E=np.array(read(PREV/'NATIVE_TOPOLOGY.json')['edges'],int)
Z=np.load(PREV/'ORIGINAL_SNAPSHOT.npz')
V=Z['V']; RV=Z['RV']
CAND=np.load(PREV/'REJECTED_GEOMETRY_PASS_SNAPSHOT.npz')['V']
META=read(PREV/'ORIGINAL_SNAPSHOT.json')
ROWS=read(MATCH/'MATCHED_CAMERA_RENDER_MANIFEST.json')
def row(view,ident='ORIGINAL'):return next(r for r in ROWS if r['view']==view and r['identity']==ident)
def project(v,r):
    m=np.array(r['camera_matrix']); q=(v-m[:3,3])@np.linalg.inv(m[:3,:3]).T
    scale=r.get('scale',r.get('ortho_scale'))
    return np.c_[640+q[:,0]*1280/scale,360-q[:,1]*1280/scale],q[:,2]
def raster(v,r):
    p,z=project(v,r); idmap=np.full((720,1280),-1,int);dep=np.full((720,1280),-np.inf)
    for fi,face in enumerate(F):
        for loc in [(0,1,2),(0,2,3)]:
            ids=face[list(loc)];a,b,c=p[ids];zz=z[ids]
            lo=np.maximum(np.floor(np.minimum(np.minimum(a,b),c)).astype(int),[0,0]);hi=np.minimum(np.ceil(np.maximum(np.maximum(a,b),c)).astype(int),[1279,719])
            if np.any(hi<lo):continue
            x,y=np.meshgrid(np.arange(lo[0],hi[0]+1)+.5,np.arange(lo[1],hi[1]+1)+.5)
            den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(den)<1e-10:continue
            u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den
            w=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den
            t=1-u-w;d=u*zz[0]+w*zz[1]+t*zz[2]
            sl=np.s_[lo[1]:hi[1]+1,lo[0]:hi[0]+1];valid=(u>=0)&(w>=0)&(t>=0)&(d>dep[sl]);dep[sl][valid]=d[valid];idmap[sl][valid]=fi
    return p,dep,idmap
def boundary(faces):
    counts={}
    for fi in faces:
        face=F[fi]
        for a,b in zip(face,np.roll(face,-1)):
            edge=tuple(sorted([int(a),int(b)]));counts[edge]=counts.get(edge,0)+1
    return [list(e) for e,n in counts.items() if n==1]
def font(n):return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
def text(im,xy,s,n=22,c='#edf2f8'):
    ImageDraw.Draw(im).text(xy,s,font=font(n),fill=c)
def init():
    refs=[('<USER_HOME>/AppData/Local/Temp/codex-clipboard-744336b8-2bf5-4b8d-b9d9-0f76359a67e5.png','hands_original_red_arrows_overhead.png'),('<USER_HOME>/AppData/Local/Temp/codex-clipboard-8d6065e4-0fd1-4a10-af61-db34b9ed8cd2.png','hands_original_red_arrows_side.png')]
    for src,dest in refs:
        target=OUT/dest
        if not target.exists():
            with target.open('xb') as f:f.write(Path(src).read_bytes())
        assert sha(src)==sha(target)
    paths=[Path(x['path']) for x in read(OUT/'PROTECTED_BEFORE.json')['files']]
    paths += [PREV/n for n in ['NATIVE_TOPOLOGY.json','ORIGINAL_SNAPSHOT.npz','ORIGINAL_SNAPSHOT.json','REJECTED_GEOMETRY_PASS_SNAPSHOT.npz','DIAGNOSTIC_RENDER_MANIFEST.json']]
    paths += [OUT/n for n in ['HUMAN_ROI_LOCALIZATION_REQUIRED.png','LOCALIZATION_MAP.json']]
    paths += [MATCH/'MATCHED_CAMERA_RENDER_MANIFEST.json',MATCH/'make_review_images.py']
    paths += [Path(row(view,ident)['path']) for view in ['OVERHEAD','AUX_INDEX_SIDE'] for ident in ['ORIGINAL','CURRENT_BEST']]
    paths += [OUT/d for _,d in refs]
    if not (OUT/'ROI_INPUT_SHA256_BEFORE.json').exists():write('ROI_INPUT_SHA256_BEFORE.json',[{'path':str(p),'sha256':sha(p)} for p in dict.fromkeys(paths)])
def inspect():
    init(); print('native bounds',V.min(0),V.max(0))
    for view,ident,v in [('OVERHEAD','ORIGINAL',V),('OVERHEAD','CURRENT_BEST',CAND),('AUX_INDEX_SIDE','ORIGINAL',V)]:
        r=row(view,ident);p,d,ids=raster(v,r)
        target={'OVERHEAD':([695.6,356.6] if ident=='ORIGINAL' else [690.8,243.5]),'AUX_INDEX_SIDE':[1172,407.5]}[view]
        dist=np.linalg.norm(p-np.array(target),axis=1);nearest=np.argsort(dist)[:12]
        print(view,ident,'target',target,'nearest',[(int(i),p[i].round(1).tolist(),round(float(dist[i]),2)) for i in nearest])
        x,y=np.rint(target).astype(int);print('face at tip',ids[y,x])
        im=Image.open(r['path']).convert('RGB');dr=ImageDraw.Draw(im)
        for i in nearest[:8]:
            x,y=p[i];dr.ellipse((x-2,y-2,x+2,y+2),fill='red');dr.text((x+2,y),str(i),font=font(10),fill='red')
        if view=='OVERHEAD':box=(650,165,755,405)
        else:box=(1020,270,1280,520)
        im=im.crop(box).resize((int((box[2]-box[0])*3),int((box[3]-box[1])*3)))
        dest=OUT/f'ROI_ALIGNMENT_CHECK_{view}_{ident}.png'
        if not dest.exists():im.save(dest)
if __name__=='__main__':inspect()
