import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
iteration=int(sys.argv[sys.argv.index('--iteration')+1]) if '--iteration' in sys.argv else 1
assert iteration in [1,2]
outblend=OUT/f'RIGHT_HAND_REAL_MOTION_WEIGHT_ITERATION_{iteration}_DESIGN_ONLY.blend'
assert not outblend.exists(), 'Do not create additional iterations under the same label'
if iteration==2:assert (OUT/'ITERATION_1_VISUAL_SCREEN_R1.json').exists(), 'Inspect iteration 1 full motion and regressions first'
inputs=check_inputs()
ob,rig=load(SOURCE)
native=m.product_payload(ob,rig);shape=core.shape_payload(ob);original_actions=actions()
V=Varray(ob);n=len(V);W=weights(ob)
groups=[g.name for g in ob.vertex_groups]
names=['WRIST_R','THUMB_CMC_R','THUMB_MCP_R','INDEX_MCP_R'];active=[groups.index(g) for g in names]
# Reuse precisely the previously approved first-web support. No whole-palm brush.
region=read(FIX/'WEIGHT_ITERATION_2.json')['allowed_vertex_ids'];N=len(region)
adj=[set() for _ in V]
for e in ob.data.edges:
    a,b=e.vertices;adj[a].add(b);adj[b].add(a)
support=sorted(set(region)|{j for i in region for j in adj[i]})
center=np.array([1.443,.022,.445]);radii=np.array([.024,.024,.027])
dist=np.sqrt((((V-center)/radii)**2).sum(1))
fade=np.array([1-m.smoothstep(.55,1,dist[i]) for i in region])
L=np.zeros((len(support),n))
for k,i in enumerate(support):
    ns=sorted(adj[i]);a=1/np.maximum(np.linalg.norm(V[ns]-V[i],axis=1),.001);a/=a.sum()
    L[k,i]=1;L[k,ns]=-a
def columns():
    T=skin(rig)
    B=np.stack([transform(T[g],V[region])-transform(T['WRIST_R'],V[region]) for g in names[1:]],axis=-1)
    return B*fade[:,None,None]
rows=[];targets=[]
fit_frames=sorted(set(FRAMES+[1,16,46,91,106,121,151,166,181,196,210]))
for f in fit_frames:
    motion(rig,f);P=Varray(ob)
    B=columns()
    # Smooth the *deformation displacement*, relative to unchanged wrist rigid motion.
    # Rest curvature is retained; this is a constrained multi-pose skin fit, not averaging weights.
    rigid=transform(skin(rig)['WRIST_R'],V)
    A=L[:,region,None,None]*B[None,:,:,:]
    A=A.transpose(0,2,1,3).reshape(-1,N*3)
    importance=2.0 if f in [130,76,205,31] else 1.0
    rows.append(A*1000*importance)
    targets.append((-L@(P-rigid)).reshape(-1)*1000*importance)
regression_strength=.16 if iteration==1 else 3.0
for c in m.CASE_IDS[1:]:
    regression(rig,c);B=columns()
    # Preserve actual approved deformed vertices as a soft pose-space constraint.
    A=np.zeros((N,3,N,3))
    for j in range(N):A[j,:,j,:]=B[j]
    rows.append(A.reshape(-1,N*3)*1000*regression_strength)
    targets.append(np.zeros(N*3))
A=np.concatenate(rows);b=np.concatenate(targets)
reg=.35 if iteration==1 else .025
H=A.T@A+reg*np.eye(N*3);rhs=A.T@b
base=W[np.ix_(region,active[1:])];total=W[region][:,active].sum(1)
def project(x):
    y=np.maximum(base+x,0)
    for k in range(N):
        if y[k].sum()>total[k]:
            z=np.sort(y[k])[::-1];css=np.cumsum(z)-total[k]
            rho=np.where(z-css/np.arange(1,4)>0)[0][-1]
            y[k]=np.maximum(y[k]-css[rho]/(rho+1),0)
    return y-base
x=project(np.linalg.solve(H,rhs).reshape(N,3));rate=1/np.linalg.eigvalsh(H)[-1]
for step in range(220):x=project(x-rate*(<REDACTED_EMAIL>()-rhs).reshape(N,3))
result=W.copy()
result[np.ix_(region,active[1:])]=base+x*fade[:,None]
result[region,active[0]]=total-result[np.ix_(region,active[1:])].sum(1)
changed=[];changes=[]
for i in region:
    if np.max(np.abs(result[i]-W[i]))<1e-7:continue
    for gi in active:
        if result[i,gi]>0:ob.vertex_groups[gi].add([i],float(result[i,gi]),'REPLACE')
        else:ob.vertex_groups[gi].remove([i])
    changed.append(i)
    changes.append({'vertex_id':i,'before':{groups[g]:float(W[i,g]) for g in active},'after':{groups[g]:float(result[i,g]) for g in active}})
neutral(rig);after=m.product_payload(ob,rig)
for k in native:
    if k!='weights':assert native[k]==after[k],k
assert core.shape_payload(ob)==shape and actions()==original_actions
for i,(a,b) in enumerate(zip(native['weights'],after['weights'])):
    if a!=b:
        assert i in region
        assert {g:w for g,w in a if g not in active}=={g:w for g,w in b if g not in active}
        assert abs(sum(w for g,w in a)-sum(w for g,w in b))<2e-7
design(ob)
motion(rig,1)
bpy.context.scene.render.fps=30;bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=210
bpy.ops.wm.save_as_mainfile(filepath=str(outblend),compress=False)
dump(f'WEIGHT_ITERATION_{iteration}_R1.json',{'iteration':iteration,'candidate_path':outblend.relative_to(ROOT).as_posix(),'candidate_sha256':sha(outblend),
    'method':'Constrained multi-pose deformation-displacement curvature fit relative to source wrist rigid transform, with exact approved-pose vertex preservation soft constraints; not generic weight smoothing.',
    'region_vertex_ids':region,'region_vertex_count':N,'changed_vertex_ids':changed,'changed_vertex_count':len(changed),'changes':changes,
    'active_influences':names,'other_existing_influences_unchanged':True,'all_outside_weights_exact':True,
    'region_center_world_m':center,'region_radii_m':radii,'fit_motion_frames':fit_frames,'approved_pose_soft_constraints':m.CASE_IDS[1:],
    'weight_tether':reg,'regression_strength':regression_strength,'basis_vertex_position_writes':0,
    'same_action_hashes':original_actions,'protected_input_hashes':inputs,
    'objective_note':'Optimization residual is engineering fit data only; Human-visible rendering decides acceptance.'})
assert check_inputs()==inputs
print('WEIGHT_ITERATION_READY',iteration,'REGION',N,'CHANGED',len(changed),flush=True)
