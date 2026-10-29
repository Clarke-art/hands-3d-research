import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import numpy as np
iteration=2 if '--iteration2' in sys.argv else 1
if iteration==2:
    import shutil
    shutil.copy2(CANDIDATE,OUT/'RIGHT_HAND_FIRST_WEB_WEIGHT_ITERATION_1_DESIGN_ONLY.blend')
ob,rig=open_file(INPUT); original=product_payload(ob,rig)
V0,F=evaluate(ob,ob.matrix_world);V=np.array([list(v) for v in V0]);n=len(V)
groups=[g.name for g in ob.vertex_groups];active=[groups.index(g) for g in ['WRIST_R','THUMB_CMC_R','THUMB_MCP_R','INDEX_MCP_R']]
W=np.zeros((n,len(groups)))
for v in ob.data.vertices:
    for g in v.groups:W[v.index,g.group]=g.weight
adj=[set() for _ in range(n)]
for e in ob.data.edges:
    a,b=e.vertices;adj[a].add(b);adj[b].add(a)
# Compact support around the visible web lip, including its surface thickness.
center=np.array([1.443,.022,.445]);radii=np.array([.024,.024,.027])
dist=np.sqrt((((V-center)/radii)**2).sum(1))
region=np.where((dist<1)&(W[:,active].sum(1)>.01))[0].tolist()
support=sorted(set(region)|{j for i in region for j in adj[i]})
fade=np.array([1-smoothstep(.55,1,dist[i]) for i in region]);N=len(region)
print('BOUNDED_REGION',N,'MODIFIERS',original['modifiers'],flush=True)
L=np.zeros((len(support),n))
for k,i in enumerate(support):
    ns=sorted(adj[i]);a=1/np.maximum(np.linalg.norm(V[ns]-V[i],axis=1),.001)
    a/=a.sum();L[k,i]=1;L[k,ns]=-a
# The objective is curvature of the actual displacement across four failed poses.
# No iterative neighbour weight averaging; solve one constrained pose-space fit.
rows=[];targets=[]
for c in CASES:
    if c['case_id'] in ['ZERO','FULL_OPP_L1']:continue
    pose(rig,c);P=np.array([list(v) for v in evaluate(ob,ob.matrix_world)[0]])
    transforms={}
    for gi in active:
        pb=rig.pose.bones[groups[gi]]
        T=<REDACTED_EMAIL>@pb.bone.matrix_local.inverted()@rig.matrix_world.inverted()
        transforms[gi]=np.array([list(T@Vector(v)) for v in V[region]])
    A=np.zeros((len(support),3,N,3))
    for k,gi in enumerate(active[1:]):
        dv=(transforms[gi]-transforms[active[0]])*fade[:,None]
        A[:,:,:,k]=L[:,region][:,None,:]*dv.T[None,:,:]
    rows.append(A.reshape(-1,N*3)*1000)
    targets.append((-L@(P-V)).reshape(-1)*1000)
A=np.concatenate(rows);b=np.concatenate(targets)
# Original weights are a soft tether, while the compact brush boundary stays fixed.
reg=.12 if iteration==2 else .8
H=A.T@A+reg*np.eye(N*3);rhs=A.T@b
x=np.linalg.solve(H,rhs).reshape(N,3)
base=W[region][:,active[1:]];total=W[region][:,active].sum(1)
def project(x):
    y=np.maximum(base+x,0)
    for k in range(N):
        if y[k].sum()>total[k]:
            z=np.sort(y[k])[::-1];css=np.cumsum(z)-total[k]
            rho=np.where(z-css/np.arange(1,4)>0)[0][-1]
            y[k]=np.maximum(y[k]-css[rho]/(rho+1),0)
    return y-base
x=project(x);rate=1/np.linalg.eigvalsh(H)[-1]
for step in range(160):x=project(x-rate*(<REDACTED_EMAIL>()-rhs).reshape(N,3))
result=W.copy()
result[np.ix_(region,active[1:])]=base+x*fade[:,None]
result[region,active[0]]=total-result[np.ix_(region,active[1:])].sum(1)
changed=[]
for i in region:
    if np.max(np.abs(result[i]-W[i]))<1e-7:continue
    for gi in active:
        if result[i,gi]>0:ob.vertex_groups[gi].add([i],float(result[i,gi]),'REPLACE')
        else:ob.vertex_groups[gi].remove([i])
    changed.append(i)
reset_pose(rig);bpy.context.view_layer.update();after=product_payload(ob,rig)
for k in original:
    if k!='weights':assert original[k]==after[k],k
ob['DESIGN_ONLY']=True;ob['PRODUCTION_PROMOTION']='NO'
bpy.context.scene['PHASE']='OFFICIAL_L1_FIRST_WEB_TARGETED_DEFORMATION_FIX_R1'
bpy.context.scene['HUMAN_APPROVAL_PENDING']=True
bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE),compress=False)
dump(f'WEIGHT_ITERATION_{iteration}.json',{'input':ref(INPUT),'candidate':ref(CANDIDATE),'method':'Constrained multi-pose displacement-curvature least squares with original-weight tether and compact elliptical support; not generic weight smoothing','region_center_world_m':center,'region_radii_m':radii,'allowed_vertex_ids':region,'changed_vertex_ids':changed,'changed_vertex_count':len(changed),'active_groups':[groups[j] for j in active],'basis_vertex_writes':0,'iterations':iteration,'regularization':reg,'objective_cases':['INDEX_MCP_45','CMC_OPP_30','FULL_OPP_L2','FULL_OPP_L3'],'objective_initial':float(b@b),'objective_final':float(np.linalg.norm(<REDACTED_EMAIL>()-b)**2)})
renderer=Renderer(cameras(),f'weight_iteration_{iteration}');renderer.sc.display.shading.shadow_intensity=0
for c in CASES:
    pose(rig,c);VP,FP=evaluate(ob,ob.matrix_world)
    renderer.draw(f'AFTER_WEIGHT_{iteration}',c['case_id'],VP,FP,['PALMAR_FULL','THENAR_CLOSE'])
renderer.dispose();print('WEIGHT_ITERATION_READY',iteration,len(changed),flush=True)
