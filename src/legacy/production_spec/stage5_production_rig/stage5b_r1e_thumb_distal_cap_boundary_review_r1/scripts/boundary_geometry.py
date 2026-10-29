"""Read-only native geometry quantities and deterministic topological predicates."""
import sys
sys.dont_write_bytecode=True
import collections, heapq, json, math
from pathlib import Path
import numpy as np
OUT=Path(__file__).resolve().parents[1]; ROOT=OUT.parents[2]
SRC=OUT.parent/'stage5b_r1e_human_cap_authority_correction_r1'
AUD=OUT.parent/'stage5b_r1e_thumb_distal_cap_native_branch_identity_audit_r1'
def load(p): return json.loads(p.read_text(encoding='utf8'))
D=load(AUD/'_tmp/render_data.json'); C=load(SRC/'NATIVE_THUMB_CAP_CANDIDATE_R1.json')
V=np.array(D['native']['vertices_world_m'])*1000; F=D['native']['faces']; ED=D['native']['edges']; N=len(V)
CV=set(C['vertex_ids']); CF=set(C['face_ids']); DOMAIN=set(C['graph_vertex_ids'])
NF=set(D['thumb_nail_faces']); NV={v for fi in NF for v in F[fi]}; SEED=284
IP=np.array(D['native_thumb']['joint_world_m']['IP'])*1000; TIP=V[SEED]
def unit(a): return a/max(np.linalg.norm(a),1e-15)
AXIS=unit(TIP-IP); DORSAL=unit(np.array([0.,-1.,0.])-AXIS*np.dot([0.,-1.,0.],AXIS)); SIDE=unit(np.cross(AXIS,DORSAL))
AXIAL=(V-IP)@AXIS; TIPAX=float(AXIAL[SEED]); DEPTH=TIPAX-AXIAL
TRANS=V-IP-AXIAL[:,None]*AXIS; RADIUS=np.linalg.norm(TRANS,axis=1)
ANGLE=(np.degrees(np.arctan2(TRANS@SIDE,TRANS@DORSAL))+360)%360
ADJ=[[] for _ in V]; VF=[[] for _ in V]; EF=collections.defaultdict(list)
FN=np.zeros((len(F),3)); AREA=np.zeros(len(F)); CENT=np.zeros((len(F),3)); VN=np.zeros_like(V)
for a,b in ED:
    w=float(np.linalg.norm(V[a]-V[b])); ADJ[a].append((b,w)); ADJ[b].append((a,w))
for fi,vs in enumerate(F):
    points=V[vs]; av=np.zeros(3)
    for i in range(1,len(vs)-1):
        cr=np.cross(points[i]-points[0],points[i+1]-points[0]); av+=cr/2; AREA[fi]+=np.linalg.norm(cr)/2
    FN[fi]=unit(av); CENT[fi]=points.mean(0)
    for v in vs: VF[v].append(fi); VN[v]+=av
    for a,b in zip(vs,vs[1:]+vs[:1]): EF[tuple(sorted((a,b)))].append(fi)
VN=np.array([unit(n) for n in VN]); NORMAL_AX=VN@AXIS
G=np.full(N,np.inf); G[SEED]=0; PRED={}; q=[(0.,SEED)]
while q:
    cost,a=heapq.heappop(q)
    if cost>G[a]: continue
    for b,w in ADJ[a]:
        if b in DOMAIN and cost+w<G[b]: G[b]=cost+w; PRED[b]=a; heapq.heappush(q,(G[b],b))
CORE=set(v for v in DOMAIN if G[v]<=9); EXP=CV-CORE
TF={fi for fi,vs in enumerate(F) if set(vs)<=DOMAIN}; FDEPTH=TIPAX-(CENT-IP)@AXIS
DUAL=collections.defaultdict(set)
for e,fs in EF.items():
    for a in fs:
        for b in fs:
            if a!=b: DUAL[a].add(b)
def components(faces):
    unseen=set(faces); out=[]
    while unseen:
        todo=[min(unseen)]; unseen.remove(todo[0]); comp=[]
        while todo:
            a=todo.pop(); comp.append(a)
            for b in DUAL[a]&unseen: unseen.remove(b); todo.append(b)
        out.append(sorted(comp))
    return sorted(out,key=lambda x:(-len(x),x))
def patch(fs):
    fs=set(fs); verts={v for fi in fs for v in F[fi]}; se=collections.defaultdict(list)
    for fi in fs:
        vs=F[fi]
        for a,b in zip(vs,vs[1:]+vs[:1]): se[tuple(sorted((a,b)))].append(fi)
    edges=sorted(e for e,x in se.items() if len(x)==1); ba=collections.defaultdict(list)
    for a,b in edges: ba[a].append(b); ba[b].append(a)
    unused=set(edges); loops=[]; paths=[]
    while unused:
        a,b=min(unused); seq=[a,b]; unused.remove((a,b))
        while seq[-1]!=seq[0]:
            opts=[v for v in ba[seq[-1]] if tuple(sorted((v,seq[-1]))) in unused]
            if not opts: break
            nxt=min(opts); unused.remove(tuple(sorted((seq[-1],nxt)))); seq.append(nxt)
        (loops if seq[0]==seq[-1] else paths).append(seq)
    comps=components(fs); nonman=[e for e,x in se.items() if len(x)>2]; degbad=[v for v,x in ba.items() if len(x)!=2]
    euler=len(verts)-len(se)+len(fs)
    # Vertex links must be one path (boundary) or one cycle (interior).
    linkbad=[]
    for v in verts:
        links=collections.defaultdict(set)
        for fi in fs&set(VF[v]):
            vs=F[fi]; j=vs.index(v); a=vs[j-1]; b=vs[(j+1)%len(vs)]; links[a].add(b); links[b].add(a)
        if not links: continue
        seen=set(); todo=[min(links)]
        while todo:
            a=todo.pop()
            if a in seen: continue
            seen.add(a); todo.extend(links[a]-seen)
        ends=sum(len(x)==1 for x in links.values())
        valid=len(seen)==len(links) and max(map(len,links.values()))<=2 and ends in [0,2]
        if not valid: linkbad.append(v)
    disk=bool(fs) and len(comps)==1 and len(loops)==1 and not paths and not nonman and not degbad and not linkbad and euler==1
    bv=sorted(ba); maxgap=None; sectors=[]
    if bv:
        ang=sorted(ANGLE[bv]); gaps=np.diff(ang+[ang[0]+360]); maxgap=float(max(gaps))
        sectors=sorted({min(11,int(ANGLE[v]/30)) for v in bv})
    windings=[float(sum((ANGLE[s[1:]]-ANGLE[s[:-1]]+180)%360-180)/360) for s in loops]
    return {'faces':sorted(fs),'vertices':sorted(verts),'boundary_edges':[list(e) for e in edges],
        'boundary_vertices':bv,'boundary_loops':loops,'open_boundary_paths':paths,'connected_components':comps,
        'boundary_angular_winding_numbers':windings,
        'component_count':len(comps),'closed_loop_count':len(loops),'boundary_degrees_not_two':degbad,
        'nonmanifold_edges':[list(e) for e in nonman],'nonmanifold_vertex_links':linkbad,'euler_characteristic':euler,
        'single_disk':disk,'max_angular_gap_deg':maxgap,'occupied_30deg_sectors':sectors,
        'surface_area_mm2':float(sum(AREA[list(fs)])) if fs else 0,
        'boundary_perimeter_mm':float(sum(np.linalg.norm(V[a]-V[b]) for a,b in edges))}
def seed_component(fs):
    comps=components(fs); seeds=set(VF[SEED])
    return set(next((comp for comp in comps if seeds&set(comp)),[]))
def ring(v):
    one={b for b,w in ADJ[v]}; two={b for a in one for b,w in ADJ[a]}-one-{v}
    return sorted(one), sorted(two)
CURV={}
for v in sorted(DOMAIN):
    one,two=ring(v); peers=[a for a in one+two if a in DOMAIN]; neighbors=[a for a in one if a in DOMAIN]
    angles=[math.acos(float(np.clip(VN[v]@VN[a],-1,1))) for a in neighbors]
    rates=[angle/np.linalg.norm(V[a]-V[v]) for a,angle in zip(neighbors,angles)]
    tangent1=unit(np.cross(VN[v],AXIS))
    if np.linalg.norm(tangent1)<.1: tangent1=unit(np.cross(VN[v],DORSAL))
    tangent2=unit(np.cross(VN[v],tangent1)); rel=V[peers]-V[v]
    x=rel@tangent1; y=rel@tangent2; z=rel@VN[v]
    M=np.stack([.5*x*x,x*y,.5*y*y,x,y,np.ones(len(x))],axis=1)
    fit=np.linalg.lstsq(M,z,rcond=None); pars=fit[0]; eig=np.linalg.eigvalsh([[pars[0],pars[1]],[pars[1],pars[2]]])
    CURV[v]={'normal_variation_rad_per_mm':float(np.median(rates)) if rates else None,
        'one_ring_normal_angle_median_deg':float(np.degrees(np.median(angles))) if angles else None,
        'quadratic_fit_principal_curvatures_per_mm':eig.tolist(),
        'quadratic_fit_rms_mm':float(np.sqrt(np.mean((M@pars-z)**2))), 'quadratic_fit_rank':int(fit[2]),
        'quadratic_fit_sample_count':len(peers),
        'proxy_only':True,'sign_convention':'Quadratic surface height along saved area-weighted native normal; convex exterior may yield negative curvature'}
LOCAL=sorted(v for v in DOMAIN if -1<=DEPTH[v]<=25)
MESHRES=float(np.median([w for a in LOCAL for b,w in ADJ[a] if b in DOMAIN]))
def smooth_profile(bandwidth):
    centers=np.arange(1.,23.01,.5); result=[]
    for s in centers:
        weights=np.exp(-.5*((DEPTH[LOCAL]-s)/bandwidth)**2)
        q=float(np.sum(weights*NORMAL_AX[LOCAL])/weights.sum())
        rad=float(np.sum(weights*RADIUS[LOCAL])/weights.sum())
        curve=float(np.sum(weights*np.array([CURV[v]['normal_variation_rad_per_mm'] for v in LOCAL]))/weights.sum())
        result.append({'depth_from_tip_mm':float(s),'tip_facing_normal_component':q,'radius_mm':rad,'normal_variation_rad_per_mm':curve})
    return result
if __name__=='__main__':
    B={fi for fi in TF if max(G[F[fi]])<=9}
    print('native thumb',len(DOMAIN),'faces',len(TF),'edge median mm',MESHRES,'axis length',TIPAX)
    for k,s in [('A',CF),('B',B)]:
        p=patch(s); print(k,{key:p[key] for key in ['single_disk','component_count','closed_loop_count','euler_characteristic']},len(p['vertices']),len(s),'core covered',len(set(p['vertices'])&CORE))
    print('profiles',json.dumps(smooth_profile(MESHRES*.7)[::4]))
    for v in sorted(EXP):
        print(v,'g',round(G[v],3),'depth',round(DEPTH[v],3),'radius',round(RADIUS[v],3),'normalaxis',round(NORMAL_AX[v],3),'k',round(CURV[v]['normal_variation_rad_per_mm'],4),'nail',v in NV)
