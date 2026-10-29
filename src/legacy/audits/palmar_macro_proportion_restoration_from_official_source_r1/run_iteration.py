import sys
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import *
import numpy as np

args = sys.argv[sys.argv.index('--') + 1:]
iteration = args[0]
strength = float(args[1])
assert sha(CURRENT) == EXPECTED
raw = read(LINEAGE / 'RAW_SOURCE_GEOMETRY.json')['stages']
source_path = ROOT / raw['OFFICIAL_L1']['input']['path']
assert sha(source_path) == raw['OFFICIAL_L1']['input']['sha256']
# Verify actual Official evaluated L1, never substitute an engineered display mesh.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=str(source_path), load_ui=False, use_scripts=False)
so = bpy.data.objects['Hand  - Realistic']
assert next(m for m in so.modifiers if m.type == 'MULTIRES').levels == 1
eo = so.evaluated_get(bpy.context.evaluated_depsgraph_get()); em = eo.to_mesh()
assert [list(v.co) for v in em.vertices] == raw['OFFICIAL_L1']['local_m']
assert [list(p.vertices) for p in em.polygons] == raw['OFFICIAL_L1']['faces']
S = np.array([list(so.matrix_world @ (Matrix.Diagonal((1.,-1.,-1.)) @ v.co)) for v in em.vertices])
SF = [tuple(p.vertices) for p in em.polygons]; eo.to_mesh_clear()
ob, rig = open_asset(CURRENT); before = snapshot()
VV, F = evaluate(ob, ob.matrix_world); V = np.array(VV)
E = [list(e.vertices) for e in ob.data.edges]
adj = [set() for _ in V]
for a,b in E: adj[a].add(b); adj[b].add(a)
D = Vector((.631289124,.775318801,-.0188387)).normalized(); Z = Vector((0,0,1)); X=D.cross(Z).normalized(); P=-D
W = rig.matrix_world @ rig.data.bones['WRIST_R'].head_local
axes = np.array([list(X),list(P),list(Z)])
C=(V-np.array(W))@axes.T*MM
regions=read(ROOT/'production_spec/stage5_production_rig/stage5b_r1b/_tmp/R1B_REGIONS.json')['regions']
ancestry=read(LINEAGE/'HISTORICAL_OPERATION_RAM_REPLAY.json')['final_ancestry']
lookup={tuple(v):i for i,v in enumerate(raw['STAGE4A_R2_BASE']['local_m'])}
known={i:lookup[tuple(v)] for i,v in enumerate(raw['STAGE4A_R2']['local_m']) if tuple(v) in lookup}
ids=np.array(sorted(known)); SD=np.array([sum(S[int(k)]*float(w) for k,w in ancestry[known[i]].items()) for i in ids])
index={int(i):j for j,i in enumerate(ids)}
def fit(a,b):
    ac=a.mean(0);bc=b.mean(0);u,s,vt=np.linalg.svd((a-ac).T@(b-bc));r=u@vt
    if np.linalg.det(r)<0: u[:,-1]*=-1;r=u@vt
    return r,bc-ac@r
def cent(vs):
    vs=[i for i in vs if i in known]
    return SD[[index[i] for i in vs]].mean(0),V[vs].mean(0),vs
landmarks=[]
wrist=[int(i) for i in ids if -6<C[i,2]<12]
landmarks.append(('WRIST_PALM_BASE',*cent(wrist)))
for name in ['INDEX_MCP_R','MIDDLE_MCP_R','RING_MCP_R','LITTLE_MCP_R']:
    head=np.array(<REDACTED_EMAIL>[name].head_local)
    near=ids[np.argsort(np.linalg.norm(V[ids]-head,axis=1))[:18]].tolist()
    landmarks.append((name,*cent(near)))
central=[int(i) for i in ids if -26<C[i,0]<-4 and 35<C[i,2]<80]
landmarks.append(('CENTRAL_METACARPAL',*cent(central)))
r,t=fit(np.array([a[1] for a in landmarks]),np.array([a[2] for a in landmarks]))
source=S@r+t; donor=SD@r+t
# A separate rigid thumb-shaft fit removes the neutral/RSSF thumb swing from
# thumb shape samples. No thumb-shaft positions are written to the candidate.
shaft=[i for i in regions['THUMB_PROXIMAL'] if i in known and 82<C[i,2]<103]
tr,tt=fit(donor[[index[i] for i in shaft]],V[shaft])
thumb_donor=donor@tr+tt
thumbset=set(regions['THUMB_FIRST_METACARPAL'])|set(regions['THUMB_PROXIMAL'])|set(regions['THUMB_DISTAL'])
sample_ids=[int(i) for i in ids if 5<C[i,2]<108]
samples=[];values=[]
for i in sample_ids:
    j=index[i]; x,p,z=C[i]
    pose_alpha=(smoothstep(20,55,x)*smoothstep(25,80,z)) if i in thumbset else 0.
    if iteration=='05':
        pose_alpha=smoothstep(18,47,x)*smoothstep(28,84,z)
    point=donor[j]*(1-pose_alpha)+thumb_donor[j]*pose_alpha
    delta=(point-V[i])@axes.T
    # Longitudinal RSSF structure retained. Contour and palmar fullness are
    # source-derived signed fields rather than current-surface smoothing.
    if iteration in ('02','03'):
        radial=1. if x>=0 else -1.
        delta[0]=radial*max(0.,radial*delta[0])
        delta[1]=max(0.,delta[1])
    samples.append(C[i]); values.append([delta[0],delta[1],delta[2] if iteration=='05' else 0.])
samples=np.array(samples);values=np.array(values)
d54=set(read(ROOT/'production_spec/stage4_blender/stage4c_donor_transfer_r1/APPLICATION_WRITE_VERIFICATION_R1.json')['actual_changed_vertex_ids'])
p16=set(read(ROOT/'audits/palmar_digit_root_local_donor_shape_restoration_design_r1/PALMAR_ROOT_FORMAL_WRITE_SET_R1.json')['vertex_ids'])
distlock=np.full(len(V),100.)
distlock[list(d54)]=0
front=set(d54)
for n in range(1,5):
    front={j for i in front for j in adj[i] if distlock[j]>n};distlock[list(front)]=n
target=V.copy(); rows=[]
for i,(x,p,z) in enumerate(C):
    # Entire palm, radial edge, thenar, root and lower web, with wrist and
    # four-finger skirts. Thumb shaft and unrelated finger bodies stay exact.
    if i in d54 or z<=5 or z>=108: continue
    if iteration=='01' and i in set(regions['THUMB_DISTAL'])|set(regions['THUMB_PROXIMAL']): continue
    proximal=smoothstep(5,27,z)
    distal=1-smoothstep(86,108,z)
    dorsal=smoothstep(-31,-8,p)
    lock=smoothstep(0,4,distlock[i])
    weight=proximal*distal*dorsal*lock
    if weight<1e-6:continue
    diff=samples-C[i];dist2=(diff[:,0]**2+diff[:,1]**2+diff[:,2]**2)
    kernel=5. if iteration=='05' else (7. if int(iteration)>=4 else 12.)
    infl=np.exp(-dist2/(2*kernel**2)); field=infl@values/infl.sum()
    if iteration=='03':
        # Upper thenar donor fullness is estimated from its palmar envelope,
        # without cancelling it against the dorsal side of the same ring.
        pos=values[:,1]>0.001
        if (infl[pos].sum()>1e-9):
            envelope=float(infl[pos]@values[pos,1]/infl[pos].sum())
            macro=smoothstep(0,18,x)*(1-smoothstep(48,66,x))*smoothstep(22,42,z)*(1-smoothstep(78,101,z))
            field[1]=field[1]*(1-macro)+envelope*macro
        field[0]*=1-smoothstep(30,55,x)
    target[i]+=field@axes*weight*strength
    rows.append({'vertex_id':i,'regional_weight':weight,'donor_contour_delta_mm':(field*MM).tolist()})
inv=ob.matrix_world.inverted()
for row in rows:
    i=row['vertex_id'];ob.data.vertices[i].co=inv@Vector(target[i])
ob.data.update();bpy.context.view_layer.update();after=snapshot()
if protected_static(before['protected'])!=protected_static(after['protected']):
    def diffs(a,b,path=''):
        if type(a)!=type(b):return [path]
        if isinstance(a,dict):return sum((diffs(a[k],b[k],path+'/'+str(k)) for k in a),[])
        if isinstance(a,list):return sum((diffs(x,y,path+'/'+str(i)) for i,(x,y) in enumerate(zip(a,b))),[]) if len(a)==len(b) else [path+'/length']
        return [] if a==b else [path]
    dd=diffs(protected_static(before['protected']),protected_static(after['protected']));print('PROTECTED_DIFF',len(dd),dd[:20],flush=True)
    dump('PROTECTION_DIAGNOSTIC.json',{'differing_fields':dd})
    raise AssertionError('protected payload')
AV,AF=evaluate(ob,ob.matrix_world);assert AF==F
changed=[i for i,(a,b) in enumerate(zip(before['coordinates_local_m'],after['coordinates_local_m'])) if a!=b]
assert not set(changed)&d54
safety,_=safety_check(AV,F,E);assert safety['automatic_status']=='PASS'
old=read(ROOT/'audits/palmar_thenar_source_shape_restoration_r1/ITERATION_03_GEOMETRY.json')
cameras=old['cameras']
# Frame is frozen across all iterations and all three assets.
dump('REGISTRATION_AND_SOURCE_REFERENCE_R1.json',{'source':ref(source_path),'current':ref(CURRENT),
     'official_evaluated_L1_verified':True,'source_rigid_rotation_row':r.tolist(),'source_rigid_translation_m':t.tolist(),
     'source_scale':1.,'palm_landmarks':[{'name':n,'ids':vs,'source_center_m':a.tolist(),'current_center_m':b.tolist(),'residual_mm':float(np.linalg.norm(a@r+t-b)*MM)} for n,a,b,vs in landmarks],
     'thumb_pose_fit_rotation_row':tr.tolist(),'thumb_pose_fit_translation_m':tt.tolist(),'thumb_pose_fit_ids':shaft,
     'source_display':'Native Official L1 with palm rigid registration only; thumb pose difference remains visible in reference A',
     'pose_separation':'Palm rigid landmarks + independent rigid thumb shaft fit for thumb field samples; current longitudinal coordinates and entire thumb shaft retained',
     'engineered_RSSF_donor_not_used':True,'generated_vertices':'interpolation of surrounding ancestry-derived macro displacement field; no fabricated source vertex correspondence'})
dump(f'ITERATION_{iteration}_GEOMETRY.json',{'iteration':iteration,'strength':strength,'vertex_ids':changed,'vertex_count':len(changed),
     'initial_local_m':before['coordinates_local_m'],'candidate_local_m':after['coordinates_local_m'],
     'current_world_m':[list(v) for v in VV],'candidate_world_m':[list(v) for v in AV],
     'donor_visual_world_m':source.tolist(),'donor_faces':[list(f) for f in SF],'faces':[list(f) for f in F],'edges':E,
     'cameras':cameras,'protected_dorsal54':sorted(d54),'palmar16_visual_sentinel':sorted(p16),'rows':rows,
     'protected_payload_equal':True,'machine_static':safety,'source':ref(source_path),'current':ref(CURRENT),
     'method':'Full palm source macro contour/fullness field; 12mm smooth donor field interpolation; broad wrist/MCP/dorsal skirts; no current surface smoothing'})
renderer=Renderer(cameras,f'iteration_{iteration}_renders')
views=['HUMAN_PALMAR','FULL_PALM','THENAR_CLOSE','FIRST_WEB_CLOSE','SIDE_VOLUME','SILHOUETTE']
renderer.draw('OFFICIAL_L1','NEUTRAL',[Vector(v) for v in source],SF,views)
renderer.draw('CURRENT','ZERO',VV,F,views)
renderer.draw('CANDIDATE','ZERO',AV,F,views)
dump(f'ITERATION_{iteration}_RENDER_MANIFEST.json',{'renders':renderer.records,'candidate_saves':0,'dynamic_cases_executed':0})
print('STATIC_ITERATION_READY',iteration,len(changed),flush=True)
