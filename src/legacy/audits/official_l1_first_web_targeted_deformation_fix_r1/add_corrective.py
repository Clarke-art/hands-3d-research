import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import numpy as np,shutil
shutil.copy2(CANDIDATE,OUT/'RIGHT_HAND_FIRST_WEB_WEIGHT_ITERATION_2_DESIGN_ONLY.blend')
ob,rig=open_file(CANDIDATE);native=product_payload(ob,rig)
assert ob.data.shape_keys is None
V0,F=evaluate(ob,ob.matrix_world);V0=np.array([list(v) for v in V0])
adj=[set() for _ in V0]
for e in ob.data.edges:
    a,b=e.vertices;adj[a].add(b);adj[b].add(a)
allowed=set(read(OUT/'WEIGHT_ITERATION_2.json')['allowed_vertex_ids'])
center=np.array([1.438,.022,.435]);radii=np.array([.019,.022,.017])
dist=np.sqrt((((V0-center)/radii)**2).sum(1))
region=[i for i in allowed if dist[i]<1]
fade={i:1-smoothstep(.25,1,dist[i]) for i in region}
c=next(c for c in CASES if c['case_id']=='CMC_OPP_30');pose(rig,c)
P=np.array([list(v) for v in evaluate(ob,ob.matrix_world)[0]])
target=P.copy()
# A bounded pose-space rounding brush softens only the residual web-lip crease.
for sweep in range(5):
    tmp=target.copy()
    for i in region:
        ns=sorted(adj[i]);a=1/np.maximum(np.linalg.norm(P[ns]-P[i],axis=1),.001);a/=a.sum()
        offset=(a@target[ns]-target[i])*.38*fade[i]
        tmp[i]+=offset
    target=tmp
delta=target-P
size=np.linalg.norm(delta,axis=1);delta*=np.minimum(1,.0016/np.maximum(size,1e-12))[:,None]
skin={pb.name:<REDACTED_EMAIL>@pb.bone.matrix_local.inverted()@rig.matrix_world.inverted() for pb in rig.pose.bones}
local_delta={}
for i in region:
    blend=np.zeros((3,3))
    for g in ob.data.vertices[i].groups:
        name=ob.vertex_groups[g.group].name
        blend+=g.weight*np.array([list(row) for row in skin[name].to_3x3()])
    worlddelta=np.linalg.solve(blend,delta[i])
    local_delta[i]=ob.matrix_world.inverted().to_3x3()@Vector(worlddelta)
reset_pose(rig);bpy.context.view_layer.update()
basis=ob.shape_key_add(name='Basis',from_mix=False)
key=ob.shape_key_add(name='FIRST_WEB_OPPOSITION_CREASE_R1',from_mix=False)
changed=[]
for i,d in local_delta.items():
    if d.length>1e-9:key.data[i].co=basis.data[i].co+d;changed.append(i)
key.value=0;key.slider_min=0;key.slider_max=1
driver=key.driver_add('value').driver;driver.type='SCRIPTED'
for name,bone in [('opp','THUMB_CMC_R'),('mcp','THUMB_MCP_R')]:
    v=driver.variables.new();v.name=name;v.type='TRANSFORMS'
    t=v.targets[0];t.id=rig;t.bone_target=bone;t.transform_type='ROT_X';t.transform_space='LOCAL_SPACE';t.rotation_mode='XYZ'
driver.expression='max(min(1,max(0,(-opp-0.37)/0.06)),min(1,max(0,(-opp-0.15)/0.15))*min(1,max(0,(-mcp-0.175)/0.175)))'
bpy.context.view_layer.update()
assert key.value==0 and product_payload(ob,rig)==native
assert [list(p.co) for p in basis.data]==native['positions_local_m']
values={}
renderer=Renderer(cameras(),'corrective_1');renderer.sc.display.shading.shadow_intensity=0
for c in CASES:
    pose(rig,c);values[c['case_id']]=float(key.value)
    VP,FP=evaluate(ob,ob.matrix_world)
    renderer.draw('AFTER_CORRECTIVE_1',c['case_id'],VP,FP,['PALMAR_FULL','THENAR_CLOSE'])
renderer.dispose();reset_pose(rig);bpy.context.view_layer.update();assert key.value==0
assert values['INDEX_MCP_45']==values['FULL_OPP_L1']==values['ZERO']==0
bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE),compress=False)
dump('CORRECTIVE_KEY_R1.json',{'key_name':key.name,'corrective_key_count':1,'changed_vertex_ids':changed,'changed_vertex_count':len(changed),'region_center_world_m':center,'region_radii_m':radii,'subset_of_weight_region':True,'max_posed_brush_delta_mm':float(np.max(np.linalg.norm(delta,axis=1))*1000),'driver_expression':driver.expression,'driver_variables':{'opp':'THUMB_CMC_R bone-local Euler X from existing opposition quaternion','mcp':'THUMB_MCP_R bone-local X flexion'},'case_values':values,'basis_vertex_writes':0,'zero_key_value':float(key.value),'candidate':ref(CANDIDATE),'note':'One high-opposition crease key. INDEX fold was resolved by weights, so no index key/driver was added. No controller bones or solver.'})
print('CORRECTIVE_READY',len(changed),values,flush=True)
