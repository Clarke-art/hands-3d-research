from roi_localization_tools import *
init()
RECEIPT=read(OUT/'ROI_READONLY_BLENDER_RECEIPT.json')
assert RECEIPT['max_snapshot_error_m']==0 and RECEIPT['face_indices_exact'] and RECEIPT['seconds']==2.6
P,D,ID=raster(V,row('OVERHEAD'))
PC,DC,IC=raster(CAND,row('OVERHEAD','CURRENT_BEST'))
PS,DS,IS=raster(V,row('AUX_INDEX_SIDE'))

def fit(view,ident,box,ox,oy,scale):
    ref=Image.open(OUT/('hands_original_red_arrows_overhead.png' if view=='OVERHEAD' else 'hands_original_red_arrows_side.png')).convert('RGB')
    src=Image.open(row(view,ident)['path']).convert('RGB')
    bx,by,ex,ey=box;target=np.asarray(ref.crop(box).resize(((ex-bx)//2,(ey-by)//2))).astype(float)
    red=(target[:,:,0]>170)&(target[:,:,1]<110)&(target[:,:,2]<110)
    # Compare the original raster, excluding Human's red annotations.
    def score(x,y,s):
        out=src.transform(ref.size,Image.Transform.AFFINE,(1/s,0,-x/s,0,1/s,-y/s),Image.Resampling.BILINEAR)
        a=np.asarray(out.crop(box).resize(((ex-bx)//2,(ey-by)//2))).astype(float)
        return float(np.mean((a[~red]-target[~red])**2))
    best=(score(ox,oy,scale),ox,oy,scale)
    for step in [1.,.25]:
        old=best
        for dx in [-step,0,step]:
            for dy in [-step,0,step]:
                for ds in [-.001*step,0,.001*step]:
                    x,y,s=old[1]+dx,old[2]+dy,old[3]+ds
                    v=score(x,y,s)
                    if v<best[0]:best=(v,x,y,s)
    mse,x,y,s=best
    return {'source_image':row(view,ident)['path'],'reference':str(OUT/('hands_original_red_arrows_overhead.png' if view=='OVERHEAD' else 'hands_original_red_arrows_side.png')),'source_native_resolution':[1280,720],'screenshot_xy_equals_native_xy_times_scale_plus_offset':{'scale':s,'offset':[x,y]},'fit_patch_screenshot_xyxy':box,'rgb_rmse_excluding_red':mse**.5,'registration_uncertainty_screenshot_px':2,'arrow_tip_interpretation_uncertainty_screenshot_px':5}

# Known compositor crops and scales, refined against actual non-red pixels.
so=1447/1980*2
REG={
 'B':fit('OVERHEAD','ORIGINAL',(130,390,320,640),80-610*so,99-80*so,so),
 'A':fit('OVERHEAD','CURRENT_BEST',(1110,240,1250,490),80+1320*1447/1980-610*so,99-80*so,so),
 'S':fit('AUX_INDEX_SIDE','ORIGINAL',(350,190,530,350),0,82,1607/2880*.75)}
TIPS={'A':[1162,338],'B':[205,503],'S':[489,252]}
for k,r in REG.items():
    tr=r['screenshot_xy_equals_native_xy_times_scale_plus_offset'];r['tip_screenshot_xy']=TIPS[k];r['tip_native_xy']=((np.array(TIPS[k])-tr['offset'])/tr['scale']).tolist()

def face_neighbours():
    ef={}
    for i,f in enumerate(F):
        for e in zip(f,np.roll(f,-1)):ef.setdefault(tuple(sorted(map(int,e))),[]).append(i)
    nei={i:set() for i in range(len(F))}
    for fs in ef.values():
        for f in fs:nei[f].update(set(fs)-{f})
    return nei
NEI=face_neighbours()
def connected(fs,seed):
    fs=set(map(int,fs));out={seed};todo=[seed]
    while todo:
        i=todo.pop()
        for j in NEI[i]&fs-out:out.add(j);todo.append(j)
    return sorted(out)
def visible_faces(ids):return set(map(int,np.unique(ids)))-{-1}
VIS={'A':visible_faces(IC),'B':visible_faces(ID),'S':visible_faces(IS)}
CORE={}
# A: only the actual visible thumb-facing silhouette strip, not the dorsal arch.
touch=[]
for y in range(232,253):
    xs=np.flatnonzero(IC[y,680:714]>=0)+680
    if len(xs):touch.extend(IC[y,xs[0]:xs[0]+7].tolist())
CORE['A']=connected(set(touch)-{-1},int(IC[244,692]))
# B: first-web lower connector around the original arrow head.
# S: kept independent at the side-view arrow head.
for k,ids,pixelradius in [('B',ID,(7,8)),('S',IS,(20,18))]:
    tx,ty=REG[k]['tip_native_xy'];rx,ry=pixelradius
    yy,xx=np.mgrid[0:720,0:1280];mask=((xx-tx)/rx)**2+((yy-ty)/ry)**2<=1
    fs=set(map(int,np.unique(ids[mask])))-{-1};seed=int(ids[round(ty),round(tx)])
    CORE[k]=connected(fs,seed)
TRANS={k:sorted(set().union(*(NEI[f] for f in fs))&VIS[k]-set(fs)) for k,fs in CORE.items()}

def coords(ids):
    m=np.array(META['mesh_world']);local=(np.c_[V,np.ones(len(V))]@np.linalg.inv(m).T)[:,:3]
    return {str(i):{'basis_mesh_local_m':RV[i].tolist(),'evaluated_mesh_local_m':local[i].tolist(),'evaluated_world_m':V[i].tolist()} for i in ids}
def details(k):
    core=CORE[k];trans=TRANS[k];cv=sorted(set(map(int,F[core].flat)));tv=sorted(set(map(int,F[trans].flat))-set(cv))
    outer=boundary(core+trans);fixed=sorted(set(v for e in outer for v in e))
    # Outer support ring remains fixed; even proposed core vertices are a maximum set, not mandatory edits.
    movable=sorted((set(cv)|set(tv))-set(fixed))
    local_faces=sorted(set().union(*(NEI[f] for f in core+trans))-set(core)-set(trans))
    allv=sorted(set(cv)|set(tv)|set(map(int,F[local_faces].flat)))
    return {'human_confirmed':False,'interpretation_status':'PROPOSED_PENDING_HUMAN','core_face_ids':core,'transition_face_ids':trans,'core_vertex_ids':cv,'transition_only_vertex_ids':tv,'fixed_outer_boundary_vertex_ids':fixed,'maximum_proposed_movable_vertex_ids':movable,'fixed_neighbour_face_ids':local_faces,'core_boundary_edges':boundary(core),'outer_fixed_boundary_edges':outer,'face_vertices':{str(i):F[i].tolist() for i in core+trans+local_faces},'vertex_coordinates':coords(allv),'hidden_surfaces_automatically_included':False}
R={k:details(k) for k in CORE}
cb=V[F[CORE['B']]].mean(axis=1);cs=V[F[CORE['S']]].mean(axis=1)
distance=float(np.linalg.norm(cb[:,None,:]-cs[None,:,:],axis=-1).min()*1000)
print('registration',REG)
print('ROIS', {k:{'core':CORE[k],'transition':TRANS[k],'core_vertices':R[k]['core_vertex_ids'],'movable':R[k]['maximum_proposed_movable_vertex_ids']} for k in CORE})
print('B/S shared core faces',sorted(set(CORE['B'])&set(CORE['S'])),'minimum centroid distance mm',distance)

COL={'A':(0,195,238),'B':(255,151,31),'S':(214,94,255)}
def overlay(view,crop,size):
    r=row(view);pix,dep,ids=(P,D,ID) if view=='OVERHEAD' else (PS,DS,IS)
    img=Image.open(r['path']).convert('RGB');arr=np.asarray(img).copy()
    # Pixel-level depth test from the actual native topology: no X-ray painted faces.
    for k in CORE:
        for fs,alpha in [(TRANS[k],.25),(CORE[k],.67)]:
            mask=np.isin(ids,fs);arr[mask]=(arr[mask]*(1-alpha)+np.array(COL[k])*alpha).astype(np.uint8)
    im=Image.fromarray(arr);dr=ImageDraw.Draw(im)
    def line_visible(a,b,color,width):
        pa,pb=pix[a],pix[b];za,zb=project(V[[a,b]],r)[1];N=max(2,int(np.linalg.norm(pa-pb)*2));prev=None
        for t in np.linspace(0,1,N):
            pt=pa*(1-t)+pb*t;ix,iy=np.floor(pt).astype(int);zz=za*(1-t)+zb*t
            ok=0<=ix<1280 and 0<=iy<720 and zz>=dep[iy,ix]-.00065
            if ok and prev is not None:dr.line([prev,tuple(pt)],fill=color,width=width)
            prev=tuple(pt) if ok else None
    selected=set().union(*(set(CORE[k]+TRANS[k]) for k in CORE))
    for fi in selected:
        for a,b in zip(F[fi],np.roll(F[fi],-1)):line_visible(a,b,'#293948',1)
    for k in CORE:
        for a,b in boundary(CORE[k]):line_visible(a,b,COL[k],3)
        for a,b in boundary(CORE[k]+TRANS[k]):line_visible(a,b,'#eef3f5',2)
    im=im.crop(crop).resize(size,Image.Resampling.LANCZOS)
    # Crisp annotations projected from the actual bones, never used as skin selection.
    dd=ImageDraw.Draw(im)
    def local(xy):return ((xy[0]-crop[0])*size[0]/(crop[2]-crop[0]),(xy[1]-crop[1])*size[1]/(crop[3]-crop[1]))
    if view=='OVERHEAD':
        joints=np.array([META['joints']['INDEX_MCP_R']['head_world'],META['joints']['INDEX_PIP_R']['head_world']])
        jp,_=project(joints,r);a,b=map(local,jp)
        for t in np.arange(0,1,.09):
            aa=tuple(np.array(a)*(1-t)+np.array(b)*t);tt=min(1,t+.045);bb=tuple(np.array(a)*(1-tt)+np.array(b)*tt);dd.line([aa,bb],fill='#ffe27c',width=2)
        for pt,lab in [(a,'MCP'),(b,'PIP')]:
            x,y=pt;dd.ellipse((x-6,y-6,x+6,y+6),fill='#ffe27c',outline='#34312b',width=1);dd.text((x+10,y-13),lab,font=font(23),fill='#ffe27c',stroke_width=1,stroke_fill='#34312b')
    for k,anchor in ([('A',385),('B',1251),('S',1246)] if view=='OVERHEAD' else [('S',1246)]):
        xy=local(pix[F[anchor]].mean(axis=0));x,y=xy
        if 0<x<size[0] and 0<y<size[1]:dd.text((x+12,y-32),k,font=font(27),fill='white',stroke_width=2,stroke_fill='#17202c')
    return im

def make_figure():
    canvas=Image.new('RGB',(2400,1710),'#111b29')
    text(canvas,(30,15),'HANDS | 原 C1 2.600000 秒 · ROI 面片提案',36)
    text(canvas,(30,65),'ROI_PROPOSED — STOP — HUMAN REVIEW    |    仅定位证据；Human 尚未确认；模型资产修改 = 0',24,'#ffd68e')
    text(canvas,(28,115),'Human 原始红箭头 · 俯视',25)
    # Preserve original arrow pixels; these are crops of delivered attachments.
    ref=Image.open(OUT/'hands_original_red_arrows_overhead.png')
    canvas.paste(ref.crop((1030,215,1270,610)).resize((480,790)),(25,155))
    text(canvas,(30,955),'右栏候选上的 A / B 箭头原样保留',20)
    text(canvas,(525,115),'真实原 C1 · 同一拓扑映射到俯视',25)
    canvas.paste(overlay('OVERHEAD',(660,180,748,398),(600,790)),(525,155))
    text(canvas,(540,960),'A：食指近节靠拇指侧；B：第一指蹼下部连接',20)
    text(canvas,(1160,115),'Human 原始红箭头 · 原 C1 侧视',25)
    side=Image.open(OUT/'hands_original_red_arrows_side.png')
    canvas.paste(side.crop((300,165,535,355)).resize((500,405)),(1160,155))
    text(canvas,(1700,115),'真实原 C1 · 侧视定位（S 保持独立）',25)
    canvas.paste(overlay('AUX_INDEX_SIDE',(970,245,1280,520),(665,590)),(1700,155))
    text(canvas,(1160,595),'同一网格在两个视角中交叉核对',25)
    text(canvas,(1160,638),'S 核心与 B 核心无共面；暂不合并。',23,'#ddb2ff')
    text(canvas,(1160,678),'部分区域在另一视角中被皮肤遮挡，',22)
    text(canvas,(1160,710),'已做深度测试；不显示遮挡面颜色。',22)
    canvas.paste(ref.crop((80,430,300,650)).resize((230,230)),(1160,755))
    text(canvas,(1410,765),'原 C1 的 B 箭头（原样局部）',23)
    text(canvas,(1410,805),'俯视左为拇指，紧邻其右为食指。',22)
    text(canvas,(1410,844),'黄虚线 = 实际 MCP—PIP 骨轴投影；',22)
    text(canvas,(1410,883),'骨轴为皮下参考，皮肤颜色只标可见面。',22)
    text(canvas,(1410,928),'A 位于近节侧缘，未纳入 PIP 关节区域。',22)
    y=1025
    for k,label in [('A','食指近节 · 靠虎口的外轮廓'),('B','第一指蹼下部 · 掌部连接'),('S','侧视指根 · 独立待确认')]:
        c=COL[k];dr=ImageDraw.Draw(canvas);dr.rectangle((30,y+3,57,y+30),fill=c)
        text(canvas,(72,y),f'{k}  {label}',25)
        text(canvas,(620,y),f'核心面 {len(CORE[k])} / 过渡面 {len(TRANS[k])}',24)
        text(canvas,(1160,y),'核心面 ID：'+', '.join(map(str,CORE[k])),22)
        y+=65
    text(canvas,(30,1245),'边界图例：深色填充 + 彩色实线 = 核心疑似面；浅色填充 = 一圈过渡面；白线 = 固定外边界。',25)
    text(canvas,(30,1290),'白线外皮肤保持原状；外围固定顶点不移动。颜色只是叠加到实际面片，没有重绘皮肤或生成修复形状。',23)
    text(canvas,(30,1350),'请确认：A 是否覆盖额外弯折？B 是否覆盖缺少饱满度？S 是否应单独保留或由 Human 指定关联？',27,'#ffd68e')
    text(canvas,(30,1404),'最小不确定性：箭头尖附近约 ±5 屏幕像素；A 来自候选姿态并按同顶点 ID 映射回原 C1。',23)
    text(canvas,(30,1445),'A 的核心仅取箭头附近的可见轮廓窄带；未把整根食指、正常虎口凹面或隐藏背面自动纳入。',23)
    text(canvas,(30,1504),'面 ID / 顶点 ID 均从 0 开始；完整面顶点序列、边界和局部坐标见 CONFIRMED_ROI_PROPOSAL.json。',23)
    text(canvas,(30,1545),'文件名含 CONFIRMED 仅为请求指定名称；human_confirmed=false。所有顶点移动量尚未定义。',23)
    text(canvas,(30,1610),'只读核验：Blender 第157帧，60fps，t=(frame−1)/fps；3300顶点 / 3298面；快照逐顶点误差 = 0。',23,'#b9ccd9')
    text(canvas,(30,1650),'本轮不修改 Basis、权重、corrective、Pose Bone、Action；不运行候选、A/B修补或多姿态回归。',22,'#b9ccd9')
    path=OUT/'HUMAN_ROI_CONFIRMATION.png';assert not path.exists();canvas.save(path)

if __name__=='__main__':
    make_figure()
    write('CONFIRMED_ROI_PROPOSAL.json',{'task':'HANDS_LOCAL_SKIN_ASSET_REPAIR_POC_R1','status':'ROI_PROPOSED — STOP — HUMAN REVIEW','human_confirmed':False,'filename_does_not_imply_approval':True,'editing_performed':False,'candidate_generated':False,'source_mesh':RECEIPT,'indexing':'zero based native vertex and polygon IDs','coordinate_units':'meters','registration':REG,'regions':R,'side_vs_B':{'same_3d_patch_confirmed':False,'disposition':'KEEP_SEPARATE_PENDING_HUMAN','shared_core_face_ids':sorted(set(CORE['B'])&set(CORE['S'])),'minimum_core_face_centroid_distance_mm':distance,'distance_is_not_surface_geodesic':True},'A_transfer':'Arrow appears only on CURRENT_BEST; select narrow visible contour there and map identical native polygon IDs to original C1, not screen coordinates.','authority':'Proposal only. No edits until explicit Human confirmation of A, B and any required side region.','uncertainty':'Arrow heads indicate locations, not edit extents. One visible edge-adjacent transition ring is a proposal. No hidden surface automatically included.','original_references':[{'path':str(OUT/n),'sha256':sha(OUT/n)} for n in ['hands_original_red_arrows_overhead.png','hands_original_red_arrows_side.png']]})
