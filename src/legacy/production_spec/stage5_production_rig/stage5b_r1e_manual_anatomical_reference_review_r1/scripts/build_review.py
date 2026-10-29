"""Immutable static geometry + unmodified photographic references, with SVG annotation layers.
No Blender writes, weight logic, deformation or automatic anatomical approval.
"""
import sys
sys.dont_write_bytecode=True
import json, math, hashlib, html, base64, heapq, datetime, textwrap
from pathlib import Path
from collections import deque
import numpy as np
from PIL import Image, ImageDraw, ImageFont

AUD=Path(__file__).resolve().parents[1];ROOT=AUD.parents[2];S5=AUD.parent
R=json.loads((S5/'stage5b_r1e_endpoint_authority_review/_tmp/review_raw.json').read_text(encoding='utf-8'))
STATIC=json.loads((S5/'stage5b_r1e_narrow_anatomical_review/_tmp/anatomy_static_extract.json').read_text(encoding='utf-8'))
PREAUD=json.loads((S5/'stage5b_r1e_narrow_anatomical_review/BODY_SIDE_COLLAR_ANATOMICAL_CLUSTER_AUDIT.json').read_text(encoding='utf-8'))
V=np.array(R['R1B']['v']);VP=np.array(STATIC['historical']['STAGE4A_R2_PRE_RSSF']['vertices_world_m']);F=R['R1B']['faces'];E=R['R1B']['edges'];N=len(V)
BODY=PREAUD['body_vertex_ids'];INDEX=PREAUD['index_side_vertex_ids'];GROUPS={c['cluster']:c['vertex_ids'] for c in PREAUD['clusters']}
CL={i:n for n,ids in GROUPS.items() for i in ids};CAP=R['R3']['CAP'];WEB=R['R3']['WEB'];BOUND=R['R3']['boundary_edges_R3'];PATH=[2192,703,2169,704]
J={k:np.array(v) for k,v in R['R2A_joints'].items()};JN=['INDEX_MCP_R','INDEX_PIP_R','THUMB_CMC_R','THUMB_MCP_R']
COL={'DORSAL':'#2d69bb','PALMAR':'#b54884','RADIAL':'#ad7318','ULNAR':'#6a8328'}
GEN=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,o):(AUD/n).write_text(json.dumps({'review':'MANUAL_ANATOMICAL_REFERENCE_REVIEW_R1','generated_at':GEN,'read_only_production':True,**o},indent=2,ensure_ascii=False),encoding='utf-8')
BEFORE=json.loads((AUD/'FROZEN_HASHES_BEFORE.json').read_text(encoding='utf-8'))
assert all(sha(ROOT/k)==h for k,h in BEFORE.items())
assert sha(S5/'stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend')==STATIC['historical']['STAGE5B_R1B']['sha256']
def unit(v):return v/max(float(np.linalg.norm(v)),1e-20)
def normals(v):
    out=np.zeros_like(v)
    for f in F:np.add.at(out,f,np.cross(v[f],np.roll(v[f],-1,axis=0)).sum(axis=0))
    return out/np.maximum(np.linalg.norm(out,axis=1)[:,None],1e-20)
NV=normals(V);NP=normals(VP)
ADJ=[set() for _ in V];INC=[[] for _ in V]
EDGE_LOOK={tuple(sorted(e)):i for i,e in enumerate(E)}
for a,b in E:ADJ[a].add(b);ADJ[b].add(a)
for fi,f in enumerate(F):
    for a in f:INC[a].append(fi)
def shortest(seeds,target):
    q=[(0.,v) for v in seeds];heapq.heapify(q);dist={v:0. for v in seeds};par={}
    while q:
        cost,a=heapq.heappop(q)
        if cost!=dist[a]:continue
        if a in target:
            path=[a]
            while path[-1] in par:path.append(par[path[-1]])
            return cost,path[::-1]
        for b in sorted(ADJ[a]):
            c=cost+float(np.linalg.norm(V[a]-V[b])*1000)
            if c<dist.get(b,float('inf')):dist[b]=c;par[b]=a;heapq.heappush(q,(c,b))
cost,path=shortest(CAP,set(INDEX));assert path==PATH
lengths=np.linalg.norm(np.diff(V[PATH],axis=0),axis=1)*1000
prelengths=np.linalg.norm(np.diff(VP[PATH],axis=0),axis=1)*1000
L=unit(J['INDEX_PIP_R']-J['INDEX_MCP_R']);seglen=float(np.linalg.norm(J['INDEX_PIP_R']-J['INDEX_MCP_R'])*1000)
pathrows=[]
for a in PATH:
    pathrows.append({'vertex_id':a,'world_mm_R1B':(V[a]*1000).tolist(),'world_mm_pre_RSSF':(VP[a]*1000).tolist(),'R3_display_only':R['R3']['R3'][a],'in_approved_cap':a in CAP,'in_body_collar':a in BODY,'in_index_collar':a in INDEX,'in_approved_first_web':a in WEB,'current_index_axial_fraction':float((V[a]-J['INDEX_MCP_R'])@L*1000/seglen),'incident_face_ids':INC[a],'one_ring':sorted(ADJ[a]),'candidate_visual_region':'Index proximal tube surface in pre-RSSF geometry; current contact pose needs Human confirmation'})
AUDIT={'path_vertex_ids':PATH,'edge_ids':[EDGE_LOOK[tuple(sorted((a,b)))] for a,b in zip(PATH,PATH[1:])],'edge_lengths_R1B_mm':lengths.tolist(),'total_R1B_mm':float(lengths.sum()),'matches_previous_13_1646_mm':abs(cost-13.1646)<.0001,'independently_recomputed_global_shortest':True,'pre_RSSF_edge_lengths_mm':prelengths.tolist(),'pre_RSSF_total_mm':float(prelengths.sum()),'vertices':pathrows,'first_web_intersection':sorted(set(PATH)&set(WEB)),'all_edges_have_two_incident_mesh_faces':all(sum(a in f and b in f for f in F)==2 for a,b in zip(PATH,PATH[1:])),'path_topological_continuity':'PASS: ordinary existing mesh edges; no new bridging edge, gap or nonmanifold seam is demonstrated','anatomical_sanity_option':'C','option_C_scope':'Visible region/semantic correspondence conflict; not a proven broken mesh topology','visual_observation':'In pre-RSSF geometry, the path runs longitudinally along the index proximal tube. v2192 is not visually at the separate native thumb terminal branch. Current v2192 is close to the engineered thumb-tip endpoint in the contact pose; proximity alone cannot settle its native surface origin.','v2169_candidate':'Dorsoradial index proximal surface, inherited DORSAL sector. A true shared thumb/index interface has not been registered.','v2192_anatomical_correspondence':'NOT_VISUALLY_CONFIRMED_AS_NATIVE_THUMB_DISTAL_CAP; visible pre-RSSF conflict requires Human Review','v2192_distance_to_current_engineered_thumb_endpoint_mm':float(np.linalg.norm(V[2192]-np.array(R['R2A_chains']['THUMB'])[-1])*1000),'no_first_web_shortcut_established':True,'no_topology_edit_authorized':True,'approved_distal_cap_authority':'FROZEN, UNCHANGED — observation does not revoke project authority','human_decision':'PENDING_HUMAN_REGISTRATION'}
dump('CAP_TO_COLLAR_3_EDGE_ANATOMICAL_SANITY_AUDIT.json',AUDIT)

# Pixel landmarks are manual visible surface observations, with internal joint centres explicitly excluded.
# Coordinates refer to unmodified originals. SVG supplies separate overlays and viewBox crops.
def lm(n,x,y,kind='VISIBLE_SURFACE_CUE',lim='Manual approximate surface observation, not an internal bone centre'):
    return dict(id=n,source_pixel=[x,y],type=kind,limitation=lim,status='CANDIDATE_PENDING_HUMAN_REVIEW')
A_LM=[lm('INDEX_MCP',1450,1655,'APPROXIMATE_DORSAL_KNUCKLE_SURFACE'),lm('INDEX_PIP',1465,865,'VISIBLE_DORSAL_PIP_WRINKLES'),lm('INDEX_PROXIMAL_PHALANX',1455,1250),lm('FIRST_WEB_COMMISSURE_MARGIN',1770,1910),lm('THUMB_MCP',2050,1980,'APPROXIMATE_THUMB_KNUCKLE_CONTOUR'),lm('THUMB_CMC_REGION',1720,2500,'APPROXIMATE_SURFACE_REGION','Broad thumb-base area only; CMC joint itself is not visible'),lm('DORSAL_FIRST_WEB',1850,1960)]
B_LM=[lm('INDEX_MCP',1310,2080,'VISIBLE_PROXIMAL_DIGITAL_CREASE','MCP skin crease is not identical to the internal joint centre'),lm('INDEX_PIP',1250,1435,'VISIBLE_PIP_FLEXION_CREASE'),lm('INDEX_PROXIMAL_PHALANX',1280,1755),lm('FIRST_WEB_COMMISSURE_MARGIN',1060,2370),lm('THUMB_MCP',1010,2780,'APPROXIMATE_THUMB_MCP_SURFACE'),lm('THUMB_CMC_REGION',1390,3550,'APPROXIMATE_SURFACE_REGION','CMC is internal; only a broad thumb-base surface region is annotated'),lm('THENAR_EMINENCE',1210,3090),lm('PALMAR_FIRST_WEB',1075,2470)]
C_LM=[lm('INDEX_MCP',1070,925,'APPROXIMATE_SURFACE_CONTOUR','Scar and perspective limit precision'),lm('INDEX_PIP',1360,730,'APPROXIMATE_VISIBLE_CREASE','Near frame edge; not a complete index view'),lm('INDEX_PROXIMAL_PHALANX',1220,815),lm('FIRST_WEB_COMMISSURE_MARGIN',855,980,'VISIBLE_RECONSTRUCTED_MARGIN','Reconstructed tissue, not a normal native boundary'),lm('PALMAR_FIRST_WEB',920,1030,'RECONSTRUCTED_WEB_SURFACE')]
def ref(id,view,file,crop,landmarks,source,author,license,limitations,orientation):
    with Image.open(AUD/'references'/file) as im:wh=list(im.size)
    return dict(id=id,view=view,file='references/'+file,original_dimensions=wh,viewport_crop_pixels=crop,landmarks=landmarks,source_url=source,author=author,license=license,limitations=limitations,orientation=orientation,original_sha256=sha(AUD/'references'/file),pixel_editing='NONE; original preserved. Separate SVG landmarks and viewBox viewport only.',medical_normality='Appearance reference only; no clinical screening data',registration_status='PENDING_HUMAN_REGISTRATION')
REFS=[
ref('A','RIGHT_HAND_DORSAL','male_both_sides.jpg',[0,0,2505,3296],A_LM,'https://commons.wikimedia.org/wiki/File:Hand_male_both_sides.jpg','Sciencia58','CC BY-SA 4.0','Only the left/dorsal panel is used. The other palmar panel has different chirality. Joint centres require palpation; photo supplies surface cues.','Fingers up; dorsal nails visible; thumb at image right; right-hand dorsal appearance'),
ref('B','RIGHT_HAND_PALMAR','Hand female 5.jpg',[0,0,3472,4424],B_LM,'https://commons.wikimedia.org/wiki/File:Hand_female_5.jpg','Sciencia58','CC BY-SA 4.0','Adult-appearing right palm; history unverified. Thumb is not at maximal abduction; crease/joint offset and perspective prevent exact registration.','Fingers up; palm/creases visible; thumb at image left; right-hand palmar appearance'),
ref('C','RIGHT_HAND_RADIAL_OBLIQUE','clinical_web_oblique.jpg',[0,300,1536,1400],C_LM,'https://congenitalhand.wustl.edu/2020/08/tight-first-webspace/','Charles A. Goldfarb, MD / Washington University in St. Louis','Copyright / no redistribution license established; local research reference','Postoperative reconstructed first web with scars and clinician occlusion. Right-hand appearance; source does not explicitly state laterality. It is supplementary oblique context, not a normal boundary standard.','Index points toward upper right; palm/radial web visible; perspective oblique; laterality candidate'),
ref('D','FIRST_WEB_OPEN','male_both_sides.jpg',[1450,1180,1050,1500],A_LM,'https://commons.wikimedia.org/wiki/File:Hand_male_both_sides.jpg','Sciencia58','CC BY-SA 4.0','Viewport of an actually open dorsal web; not a new capture, not calibrated maximal radial/palmar abduction. No claim of seeing deep structures.','Right dorsal thumb/index web; crop of A'),
ref('E','INDEX_PROXIMAL_PHALANX_CLOSEUP','Hand female 5.jpg',[950,1100,850,1600],B_LM,'https://commons.wikimedia.org/wiki/File:Hand_female_5.jpg','Sciencia58','CC BY-SA 4.0','Viewport from B, not another subject/capture. Shows PIP and proximal digital/MCP surface crease; bones remain internal.','Right index palmar proximal segment; crop of B')]
dump('MANUAL_ANATOMICAL_REFERENCE_PACK_R1.json',{'pack_id':'MANUAL_ANATOMICAL_REFERENCE_PACK_R1','entries':REFS,'distinct_used_original_photos':3,'required_views_present':['A','B','C','D','E'],'radial_reference_limitation':'C is a surgical oblique supplement, not normal unscarred anatomy or a proven calibrated right radial view. This remains a Human review limitation.','required_visible_landmark_coverage':sorted({l['id'] for r in REFS for l in r['landmarks']}),'excluded_references':[{'file':'references/human_right_front_back.jpg','reason':'Source calls this right hand but visible chirality conflicts; not used or mirrored to force a match.'},{'file':'references/right_hand_palm.png','reason':'Title calls this right palm, but thumb-at-right palmar appearance conflicts with unmirrored right hand; excluded.'},{'file':'references/Hand male 2.jpg','reason':'Palmar chirality is opposite to the selected right dorsal view; excluded.'}],'source_asset_use':'Real photographs only; no generated anatomy reference, commercial illustration or ordinary 3D model used as human authority. Annotation layers are review hypotheses.'})

def esc(s):return html.escape(str(s),quote=True)
def photo_svg(r):
    x,y,w,h=r['viewport_crop_pixels'];iw,ih=r['original_dimensions'];font=max(w/42,23)
    s=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" aria-label="{r["view"]}"><image href="{r["file"]}" width="{iw}" height="{ih}"/>'
    for i,p in enumerate(r['landmarks']):
        px,py=p['source_pixel']
        if not(x<=px<=x+w and y<=py<=y+h):continue
        label=p['id'];tx=max(x+12,min(px+font*.7,x+w-font*len(label)*.52));ty=py-font*.8
        color='#7b4305' if p['type'].startswith('APPROXIMATE') else '#064d75'
        s+=f'<g class="ref-landmark"><circle cx="{px}" cy="{py}" r="{font*.26}" fill="white" stroke="{color}" stroke-width="{font*.09}"/><text x="{tx}" y="{ty}" fill="{color}" font-size="{font}" font-family="Arial" paint-order="stroke" stroke="white" stroke-width="{font*.09}">{label}</text></g>'
    pip=next((p['source_pixel'] for p in r['landmarks'] if p['id']=='INDEX_PIP'),None);mcp=next((p['source_pixel'] for p in r['landmarks'] if p['id']=='INDEX_MCP'),None)
    if pip and mcp:s+=f'<path d="M{mcp[0]} {mcp[1]} L{pip[0]} {pip[1]}" fill="none" stroke="#175a8c" stroke-width="{font*.08}" stroke-dasharray="{font*.25} {font*.18}"/>'
    return s+'</svg>'

# Orthographic geometry projections. Camera basis is right-handed: horizontal = up cross viewer.
# All points are static native data; reference photographs are not resculpted to match.
VIEWS=[('DORSAL',np.array([0.,1.,0.]),'MODEL_DORSAL_BODY16.png','A'),('PALMAR',np.array([0.,-1.,0.]),'MODEL_PALMAR_BODY16.png','B'),('RADIAL',np.array([1.,0.,0.]),'MODEL_RADIAL_BODY16.png','C'),('FIRST_WEB',unit(np.array([1.,.75,.2])),'MODEL_FIRST_WEB_BODY16.png','D'),('INDEX_PROXIMAL',np.array([0.,-1.,0.]),'MODEL_INDEX_PROXIMAL_BODY16.png','E')]
FONT='C:/Windows/Fonts/arial.ttf';BOLD='C:/Windows/Fonts/arialbd.ttf'
def ft(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
def basis(view):
    up=np.array([0.,0.,1.]);right=unit(np.cross(view,up));up=unit(np.cross(right,view));return np.array([right,up,view])
ALL=np.where(VP[:,2]>.393)[0].tolist()
LOCAL=sorted(set(PREAUD['C0'])|set(PREAUD['C1'])|set(PREAUD['C2'])|set(CAP))
def project(v,view,focus,box,joints=False):
    x,y,w,h=box;A=basis(view);q=v@A.T*1000;bounds=q[focus,:2]
    if joints:bounds=np.vstack([bounds,*[(J[k]@A.T*1000)[:2][None,:] for k in ['INDEX_MCP_R','INDEX_PIP_R']]])
    lo=bounds.min(axis=0);hi=bounds.max(axis=0);pad=np.maximum((hi-lo)*.15,4);lo-=pad;hi+=pad
    scale=min((w-70)/(hi[0]-lo[0]),(h-70)/(hi[1]-lo[1]));c=(hi+lo)/2
    p=np.column_stack([x+w/2+(q[:,0]-c[0])*scale,y+h/2-(q[:,1]-c[1])*scale])
    def position(world):
        a=world@A.T*1000;return [float(x+w/2+(a[0]-c[0])*scale),float(y+h/2-(a[1]-c[1])*scale)]
    return p,q,A,position
def mesh_layer(v,view,focus,box,joints=False,ids=False,path=False):
    p,q,A,pos=project(v,view,focus,box,joints);x,y,w,h=box;n=NV if v is V else NP
    # Return both SVG and PNG drawing commands so UI toggles never erase underlying geometry.
    s='';cmd=[];depth=np.array([q[f,2].mean() for f in F])
    for fi in np.argsort(depth):
        face=F[int(fi)];pts=p[face]
        if not all(x+2<=a<=x+w-2 and y+2<=b<=y+h-2 for a,b in pts):continue
        shade=.35+.65*abs(float(unit(n[face].sum(axis=0))@A[2]));g=int(170+65*shade);color=f'#{g:02x}{g:02x}{min(255,g+4):02x}'
        if len(set(face)&set(WEB))>=2:color='#c5afd9'
        if len(set(face)&set(CAP))>=2:color='#e5cb8c'
        coords=' '.join(f'{a:.2f},{b:.2f}' for a,b in pts)
        s+=f'<polygon points="{coords}" fill="{color}" stroke="#b5bec9" stroke-width="0.45"/>';cmd.append(('polygon',pts.tolist(),color))
    for ei in BOUND:
        pts=p[E[ei]].tolist()
        if all(x<=a<=x+w and y<=b<=y+h for a,b in pts):s+=f'<path d="M{pts[0][0]:.2f} {pts[0][1]:.2f} L{pts[1][0]:.2f} {pts[1][1]:.2f}" stroke="#242c38" stroke-width="3.5"/>';cmd.append(('line',pts,'#242c38',4))
    for group,color,rad in [(WEB,'#874aaa',3),(CAP,'#a97a0d',4),(INDEX,'#2086b4',4),(BODY,None,6)]:
        for a in group:
            px,py=p[a]
            if not(x+8<=px<=x+w-8 and y+8<=py<=y+h-8):continue
            c=COL[CL[a]] if a in BODY else color;front=float(n[a]@A[2])>=0;fill=c if front else 'white';cls='cluster-'+CL[a] if a in BODY else 'fixed-region'
            s+=f'<g class="{cls}"><circle cx="{px:.2f}" cy="{py:.2f}" r="{rad}" fill="{fill}" stroke="{c}" stroke-width="2"/></g>';cmd.append(('dot',[px,py],fill,c,rad))
    if joints:
        for k in JN:
            px,py=pos(J[k])
            if x+12<=px<=x+w-12 and y+12<=py<=y+h-12:
                label=k.replace('_R','');s+=f'<g class="model-landmark"><path d="M{px-7} {py}h14 M{px} {py-7}v14" stroke="#162a42" stroke-width="2"/><text x="{px+10}" y="{py-10}" font-size="17" font-family="Arial" fill="#142840" paint-order="stroke" stroke="white" stroke-width="3">{label}</text></g>';cmd.append(('text',[px+10,py-20],label,'#142840',17))
    if path:
        for a,b in zip(PATH,PATH[1:]):
            pts=p[[a,b]].tolist();s+=f'<path d="M{pts[0][0]} {pts[0][1]} L{pts[1][0]} {pts[1][1]}" stroke="#e23c20" stroke-width="6" fill="none"/>';cmd.append(('line',pts,'#e23c20',6))
        for a in PATH:
            px,py=p[a];s+=f'<circle cx="{px}" cy="{py}" r="8" fill="#ffe243" stroke="#aa2417" stroke-width="2"/>';cmd.append(('dot',[px,py],'#ffe243','#aa2417',8))
            tx=px+15;ty=py-20;s+=f'<text x="{tx}" y="{ty}" font-size="22" fill="#af2419" font-family="Arial" paint-order="stroke" stroke="white" stroke-width="4">v{a}</text>';cmd.append(('text',[tx,ty],f'v{a}','#af2419',22))
    elif 2169 in focus:
        px,py=p[2169];s+=f'<circle cx="{px}" cy="{py}" r="12" fill="none" stroke="#dc3422" stroke-width="3"/>';cmd.append(('outline',[px,py],'#dc3422',12))
    if ids:
        # Fixed separated callout rows; every ID is visible even when its point lies behind the mesh.
        for side,verts in [(0,BODY[:8]),(1,BODY[8:])]:
            for i,a in enumerate(verts):
                px,py=p[a];tx=x+5 if side==0 else x+w-75;ty=y+55+i*30
                c=COL[CL[a]];s+=f'<g class="cluster-{CL[a]}"><path d="M{px} {py} L{tx+30} {ty+5}" stroke="{c}" stroke-width="0.9" opacity=".55"/><text x="{tx}" y="{ty}" font-family="Arial" font-size="17" fill="{c}" paint-order="stroke" stroke="white" stroke-width="2">{a}</text></g>';cmd.append(('line',[(px,py),(tx+30,ty+5)],c,1));cmd.append(('text',[tx,ty-13],str(a),c,17))
    return s,cmd,pos,p
def paint(d,cmd):
    for row in cmd:
        k=row[0]
        if k=='polygon':d.polygon(row[1],fill=row[2]);d.line(row[1]+[row[1][0]],fill='#b5bec9',width=1)
        elif k=='line':d.line(row[1],fill=row[2],width=row[3])
        elif k=='dot':
            x,y=row[1];r=row[4];d.ellipse((x-r,y-r,x+r,y+r),fill=row[2],outline=row[3],width=2)
        elif k=='outline':
            x,y=row[1];r=row[3];d.ellipse((x-r,y-r,x+r,y+r),outline=row[2],width=3)
        elif k=='text':d.text(row[1],row[2],font=ft(row[4],True),fill=row[3],stroke_width=1,stroke_fill='white')
def write_lines(d,xy,text,width=120,size=22):
    x,y=xy
    for l in textwrap.wrap(text,width):d.text((x,y),l,font=ft(size),fill='#33485c');y+=size+7
    return y
MODELS={};positions={}
for name,view,file,refid in VIEWS:
    MODELS[name]={}
    for asset,v in [('R1B',V),('PRE_RSSF',VP)]:
        focus=LOCAL if name=='INDEX_PROXIMAL' else ALL
        # Local SVG is square for consistent overlay coordinates.
        svg,cmd,pos,p=mesh_layer(v,view,focus,(0,0,1000,1000),joints=asset=='R1B',ids=True)
        MODELS[name][asset]=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">{svg}</svg>'
        if asset=='R1B':positions[name]={k:pos(J[k]) for k in JN}
    im=Image.new('RGB',(1800,1200),'#f6f7fa');d=ImageDraw.Draw(im)
    d.text((30,22),name.replace('_',' ')+' / frozen R1B static geometry',font=ft(34,True),fill='#172b43')
    d.text((30,70),'No pose evaluation. Solid/hollow = front/back normal. Red circle = v2169. Joint crosses = engineered skeleton, not skin creases.',font=ft(20),fill='#495d70')
    d.rectangle((25,125,590,1040),fill='white',outline='#d1d9e2');d.rectangle((620,125,1775,1040),fill='white',outline='#d1d9e2')
    _,c,_,_=mesh_layer(V,view,ALL,(30,135,550,875),joints=True);paint(d,c)
    _,c,_,_=mesh_layer(V,view,LOCAL,(635,135,1125,875),joints=True,ids=True);paint(d,c)
    write_lines(d,(35,1060),'Left: full context includes approved WEB (purple), CAP (ochre), live CMC/MCP/PIP, body/index endpoints and all 16 cut edges. Right: local circumferential collar with all body IDs. Human crease/margin assignment remains pending.',width=145,size=21)
    im.save(AUD/'renders'/file)

im=Image.new('RGB',(1800,1200),'#f6f7fa');d=ImageDraw.Draw(im)
d.text((30,22),'CAP -> COLLAR: anatomical sanity check',font=ft(36,True),fill='#172b43')
d.text((30,76),'v2192 -> v703 -> v2169 -> v704 | three real mesh edges | R1B 13.1646179 mm',font=ft(25),fill='#923322')
for box,v,title in [((30,150,845,795),VP,'Pre-RSSF native geometry: path on index tube'),((925,150,845,795),V,'Frozen R1B contact pose: same IDs and topology')]:
    x,y,w,h=box;d.rectangle((x,y,x+w,y+h),fill='white',outline='#d1d9e2');d.text((x+10,y+10),title,font=ft(22,True),fill='#27394b')
    _,c,_,_=mesh_layer(v,np.array([0.,1.,0.]),LOCAL,(x+5,y+55,w-10,h-65),path=True);paint(d,c)
    # Preserve native branch context while keeping all four path IDs legible.
    ix,iy,iw,ih=x+12,y+h-345,240,330
    d.rectangle((ix,iy,ix+iw,iy+ih),fill='white',outline='#a5b2c3',width=2)
    _,c,_,_=mesh_layer(v,np.array([0.,1.,0.]),ALL,(ix+5,iy+30,iw-10,ih-35));paint(d,c)
    d.text((ix+8,iy+7),'Whole hand context',font=ft(16,True),fill='#27394b')
write_lines(d,(35,978),'Path continuity is topologically ordinary. It does not pass through approved first web. v2192 is an approved cap ID, yet in native pre-RSSF geometry it is on the index branch rather than the separate thumb tip. This is a visible REGION CORRESPONDENCE conflict; it does not revoke frozen cap authority or prove a broken topology.',width=135,size=24)
im.save(AUD/'renders/CAP_TO_COLLAR_3_EDGE_ANATOMICAL_SANITY_CHECK.png')
# A separate tightly cropped path view makes all four points inspectable without replacing whole-hand context.
psvg,cmd,_,_=mesh_layer(V,np.array([0.,1.,0.]),LOCAL,(0,0,1000,1000),joints=True,path=True)
MODELS['PATH']={'R1B':f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">{psvg}</svg>'}
psvg,_,_,_=mesh_layer(VP,np.array([0.,1.,0.]),LOCAL,(0,0,1000,1000),path=True)
MODELS['PATH']['PRE_RSSF']=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">{psvg}</svg>'

CAND=[]
for row in PREAUD['vertices']:
    CAND.append({'vertex_id':row['vertex_id'],'cluster':row['cluster'],'model_index_axial_fraction':row['MCP_to_PIP_axial_fraction'],'candidate_human_region':{'DORSAL':'Index proximal dorsal integument between candidate MCP knuckle surface and PIP wrinkles','PALMAR':'Index volar proximal skin between proximal digital and PIP flexion creases','RADIAL':'Index radial lateral proximal skin; commissure extension not established','ULNAR':'Index ulnar lateral proximal skin'}[row['cluster']],'MCP_crease_side_candidate':'DISTAL (subject to photo crease/joint offset)','PIP_crease_side_candidate':'PROXIMAL (subject to photo crease/joint offset)','first_web_margin_side_candidate':'UNREGISTERED — do not assign from radial direction alone','photo_reference_ids':{'DORSAL':['A','D'],'PALMAR':['B','E'],'RADIAL':['A','C','D'],'ULNAR':['A','B']}[row['cluster']],'confidence':'Model coordinate HIGH; human surface assignment CANDIDATE only','registration_status':'PENDING_HUMAN_REGISTRATION','human_registered_vertex':False,'R3_display_only':'THUMB unchanged'})
dump('BODY_SIDE_16_MANUAL_REGISTRATION_CANDIDATES.json',{'body_ids':BODY,'clusters':GROUPS,'vertices':CAND,'v2169':'Dorsoradial index tube candidate; shared interface unresolved','no_true_shared_web_patch_registered':True,'no_AI_final_registration':True})
dump('MODEL_HUMAN_LANDMARK_REGISTRATION.json',{'status':'PENDING_HUMAN_REGISTRATION','model_source':'Frozen R1B static world coordinates; source file SHA-256 verified against immutable extraction','model_joint_world_mm':{k:(J[k]*1000).tolist() for k in JN},'model_2D_joint_positions':positions,'reference_entries':REFS,'registration_type':'Human-auditable visible surface landmark pairs; provisional 2D INDEX MCP/PIP axis alignment only','internal_structure_policy':'Photo MCP/PIP labels refer to visible creases/contours; CMC marked as broad approximate surface region. No hidden bone/ligament is claimed directly visible.','overlay_available_for':['DORSAL/A','PALMAR/B','INDEX_PROXIMAL/E'],'overlay_disabled_for':['RADIAL/C — surgical perspective and occlusion','FIRST_WEB/D — cropped opening lacks complete paired PIP context','PATH — topological sanity evidence, not a registration view','all PRE_RSSF — current live joint coordinates cannot be reused in the native pre-RSSF frame'],'overlay_model_fit_error':'Not a 3D or nonrigid fit; MCP/PIP pair is matched by construction and does not validate other landmarks. No false registration error is reported.','THUMB_CMC_MCP_and_commissure_validation':'Separate visible reference cues retained; no whole-hand alignment asserted','reference_original_pixels_changed':False,'AI_registered_vertices':[],'human_answers_recorded':[]})

photos={r['id']:photo_svg(r) for r in REFS}
DATA={'models':MODELS,'refs':REFS,'photos':photos,'modelLandmarks':positions,'body':BODY,'groups':GROUPS,'candidates':CAND}
payload=json.dumps(DATA,ensure_ascii=False).replace('</','<\\/')
template=(AUD/'scripts/review_template.html').read_text(encoding='utf-8')
(AUD/'MANUAL_REGISTRATION_REVIEW.html').write_text(template.replace('__REVIEW_DATA__',payload),encoding='utf-8')

STATUS={'BRANCH':'D','FINAL_BRANCH_NAME':'MANUAL_REGISTRATION_REQUIRED','REGISTRATION_STATUS':'PENDING_HUMAN_REGISTRATION','BODY_SIDE_16_REGISTERED_AS_INDEX_PROXIMAL_SURFACE':False,'BODY_SIDE_16_CANDIDATE':'Circumferential index proximal surface between MCP and PIP; 0.628–0.730 current engineered axis','RADIAL_WEB_EXTENSION':'UNRESOLVED','TRUE_SHARED_WEB_PATCH_REGISTERED':False,'CAP_TO_COLLAR_SANITY_OPTION':'C — region correspondence conflict; not a proven topology break','v2169':'Dorsoradial index proximal surface candidate; shared interface pending Human','v2192':'Native thumb distal cap correspondence not visually confirmed; pre-RSSF index-branch conflict visible','DIGIT_OWNERSHIP_AUTHORITY_R3':'HUMAN_APPROVED unchanged','R3_EXACT_COLLAR':'PASS inherited unchanged','APPROVED_DISTAL_CAP':'FROZEN unchanged','FIRST_WEB_AUTHORITY':'FROZEN unchanged','CMC_CAGE':'FROZEN unchanged','Stage5B_R1B':'FROZEN PRODUCTION MASTER','Stage5B_R1E':'FAIL-CLOSED CANDIDATE','R1F_CREATED':False,'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,'BLEND_FILES_WRITTEN':0,'deformation_runs':0,'weight_authority_proposals':0,'retopo':False,'human_review_page':'MANUAL_REGISTRATION_REVIEW.html','human_questions':['Q1 Body 16 visually index proximal-phalanx surface?','Q2 Radial cluster extends into true commissure?','Q3 Palmar cluster index volar or palm/web transition?','Q4 v2169 a reasonable true index/thumb shared interface?','Q5 Three-edge path visually consistent with native continuous hand surface?'],'STOP':'WAITING_FOR_HUMAN_REVIEW'}
dump('MANUAL_ANATOMICAL_REFERENCE_REVIEW_R1_STATUS.json',STATUS)
AFTER={k:sha(ROOT/k) for k in BEFORE};assert AFTER==BEFORE
blends_before={k:h for k,h in BEFORE.items() if k.endswith('.blend')};blends_after={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in ROOT.rglob('*.blend') if AUD not in p.parents}
# All workspace blends were included in the preceding snapshot except source/reference folders.
new_production_blends=[k for k in blends_after if k.startswith('production_spec/') and k not in blends_before];assert not new_production_blends
dump('FROZEN_HASH_VERIFICATION.json',{'before':BEFORE,'after':AFTER,'protected_file_count':len(BEFORE),'all_before_equals_after':True,'changed_files':[],'new_production_blends':[],'BLEND_FILES_WRITTEN':0,'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,'verification_scope':'Every pre-existing production_spec file and every docs file, including all previous evidence/audits; writes confined to this new review directory.'})
REPORT=f'''# MANUAL_ANATOMICAL_REFERENCE_REVIEW_R1

本轮仅 anatomical registration。**最终 Branch D：MANUAL_REGISTRATION_REQUIRED**，状态 **PENDING_HUMAN_REGISTRATION**。已制作本地双栏/SVG 标注审阅页、A–E 真实参考图包、五个冻结 R1B 视图及 3-edge path 检查图。没有替 Human 注册点或推导 weight authority。

## 优先发现

Body 16 模型表面仍是食指近节管周向环的强候选，沿当前 engineered INDEX MCP→PIP 投影 0.628–0.730。其候选位置在 MCP 表面/皮纹远侧、PIP 皮纹近侧；照片 skin crease 不与骨关节中心完全重合，故此为候选关系。4 簇保持背侧4、掌侧5、桡侧3、尺侧4。桡侧不能仅凭朝向虎口被注册为 first web。逐点候选、照片可见表面线索及限制记录在 JSON。

**v2192 的解剖对应存在可见冲突。** 在 pre-RSSF native geometry，它与 v703、v2169、v704 连续沿食指管表面排列；不像独立拇指分支的末端。当前 contact pose 中它距 engineered thumb-tip endpoint {AUDIT['v2192_distance_to_current_engineered_thumb_endpoint_mm']:.3f} mm；这个接近不能反证 native surface identity。v2169 在原始表面是背桡侧食指近节候选，并非已证明 shared interface。所有 cap authority 保持冻结，不由本次观察撤销。

## 3-edge path：视觉与拓扑分开

重算全 CAP→INDEX collar 的 edge-length shortest path：**v2192→v703→v2169→v704**。三个现有边长为 {', '.join(f'{v:.6f}' for v in lengths)} mm，总长 **{float(lengths.sum()):.7f} mm**；对应 pre-RSSF 总长 {float(prelengths.sum()):.7f} mm。每边均有两个 incident faces，没有新桥接边/裂缝/非流形证据；路径与 approved WEB 无交集。

sanity 检查选 **C：region/semantic correspondence anomaly**，限定为“冻结 cap 的工程名字与 native 模型位置不一致的可见冲突”，不是宣称模型有破损拓扑。它看起来是沿同一食指管的普通连续路径，不能称为已证明的 thumb distal cap→first-web 合理解剖捷径。总体人体对应仍待 Human，因此全局最终分支保持 D，未强行使用 A/B 或注册为真实 shared patch。

## 真实照片与手性筛选

A 采用 Sciencia58 原始双图中的右手背侧部分；B 采用同作者另一张右手掌侧。D 为 A 的开放虎口 viewport，E 为 B 的 index proximal closeup viewport；只是展示窗口，未改原像素。C 为 Charles A. Goldfarb / Washington University 的术后虎口斜视实拍，用作补充；其瘢痕、遮挡、laterality 未在来源明说和非正常 native margin 的限制均显示。没有把它当正常虎口边界标准。

参考来源：[Sciencia58 背侧双图](https://commons.wikimedia.org/wiki/File:Hand_male_both_sides.jpg)、[Sciencia58 掌侧照片](https://commons.wikimedia.org/wiki/File:Hand_female_5.jpg)、[Washington University 斜视实拍](https://congenitalhand.wustl.edu/2020/08/tight-first-webspace/)。A/B 原图许可证 CC BY-SA 4.0，页面保留署名/来源/许可证。C 仅为本地研究参考，未建立再分发许可。

另有两张标题声称 right hand 的图与可见手性冲突，已明确排除，未镜像造出右手。主参考是外观正常的成人照片，没有临床健康筛查数据，也不是该模型的原始扫描对象。

## 可见 landmarks

在原图独立 SVG 层标出 INDEX MCP 的表面 knuckle/皮纹候选、PIP 可见皮纹、近节表面、commissure margin、thumb MCP 表面轮廓、CMC broad approximate region、thenar eminence、dorsal/palmar first web。没有把隐藏骨中心、韧带或肌肉插入点标成照片直接可见结构。C 的被遮挡 landmarks 未补画成确定位置。

模型显示 body16、INDEX16、exact16 edges、live INDEX MCP/PIP、thumb CMC/MCP、approved WEB/CAP。5 个 PNG 均有全局上下文和局部近景；v2169 在背、掌、桡和斜视有红圈。pre-RSSF 切换保留同 ID 原生形状，不错误复用 current engineered joint frame。

## Review 页

打开 `MANUAL_REGISTRATION_REVIEW.html`。默认双栏真实参考↔模型，支持切换5视图及路径、R1B/pre-RSSF、landmarks、ID、4簇显示。背侧/掌侧/掌侧近景可启用 INDEX MCP/PIP 两点轴对齐的 opacity overlay；它只是一项可人工修正的二维 similarity hypothesis。匹配两点不意味着其它 landmarks 正确，也不是非刚性配准。斜视/虎口/路径以及 pre-RSSF 自动关闭 overlay，避免错误外观。

Human 的五个问题已经放在页尾，逐簇也可记录候选/未决。答复可导出 JSON，仅本地保存，不改生产文件，不自动修改 authority。默认答复均“未判断”，本轮 Human answers=0。

## 冻结与停止

{len(BEFORE)} 个既有 production_spec/docs 文件 SHA-256 before=after；包含 R2A/R1B/R1E、R3 evidence、feasibility、endpoint authority 和 narrow anatomy 各轮输出。WEIGHT/GEOMETRY/TOPOLOGY/BONE/JOINT DELTA=0；BLEND_FILES_WRITTEN=0；R1F_CREATED=false。未跑 deformation、Stage6 或 retopo，未提出生产权重数值。

**STOP — WAITING FOR HUMAN REVIEW**。
'''
(AUD/'MANUAL_ANATOMICAL_REFERENCE_REVIEW_R1_REPORT.md').write_text(REPORT,encoding='utf-8')
print('Generated review pack, five model views, path check and pending review page. Frozen hashes equal:',len(BEFORE))
print('Path:',path,'length',cost,'sanity option C; overall branch D')
