import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
assert read(OUT/'ITERATION_2_VISUAL_SCREEN_R1.json')['corrective_gate_satisfied']
assert not CANDIDATE.exists(), 'Only one new corrective candidate permitted'
inputs=check_inputs()
WEIGHT2=OUT/'RIGHT_HAND_REAL_MOTION_WEIGHT_ITERATION_2_DESIGN_ONLY.blend'
ob,rig=load(WEIGHT2)
native=m.product_payload(ob,rig);oldshape=core.shape_payload(ob);saved_actions=actions()
solver=core.Solver(ob,rig,2)
V0=Varray(ob);W=weights(ob);groups=[g.name for g in ob.vertex_groups]
allowed=read(OUT/'WEIGHT_ITERATION_2_R1.json')['region_vertex_ids']
adj=[set() for _ in V0]
for e in ob.data.edges:
    a,b=e.vertices;adj[a].add(b);adj[b].add(a)
# A compact rounding brush at the upper web bridge. Far thenar and thumb outline are excluded.
center=np.array([1.443,.022,.450]);radii=np.array([.019,.019,.023])
dist=np.sqrt((((V0-center)/radii)**2).sum(1))
region=[i for i in allowed if dist[i]<1]
fade={i:1-m.smoothstep(.40,1,dist[i]) for i in region}
targets=[]
for f in [130,76,205,31]:
    motion(rig,f);P=Varray(ob);target=P.copy()
    # Bounded pose-space surface rounding only; does not alter mesh Basis or topology.
    for sweep in range(10):
        temp=target.copy()
        for i in region:
            ns=sorted(adj[i]);a=1/np.maximum(np.linalg.norm(P[ns]-P[i],axis=1),.0008);a/=a.sum()
            temp[i]+=(a@target[ns]-target[i])*.48*fade[i]
        target=temp
    delta=target-P
    size=np.linalg.norm(delta,axis=1);delta*=np.minimum(1,.0028/np.maximum(size,1e-12))[:,None]
    transforms=skin(rig);local={}
    for i in region:
        B=sum(float(W[i,j])*np.array([list(r) for r in transforms[g].to_3x3()]) for j,g in enumerate(groups) if W[i,j]>0)
        local[i]=ob.matrix_world.inverted().to_3x3()@Vector(np.linalg.solve(B,delta[i]))
    targets.append(local)
neutral(rig)
key=ob.shape_key_add(name='FIRST_WEB_REAL_MOTION_CORRECTIVE_R1',from_mix=False)
basis=ob.data.shape_keys.key_blocks['Basis']
changed=[]
for i in region:
    # One shared delta fitted to four real-motion poses, not a per-frame shape library.
    d=sum((t[i] for t in targets),Vector())/len(targets)
    if d.length>1e-9:
        key.data[i].co=basis.data[i].co+d;changed.append(i)
key.value=0;key.slider_min=0;key.slider_max=1

# Exact inverse of existing solver calibration, using only existing animated local quaternions.
# Two derived scalar properties on the mesh object, no controls/bones/new animation keys.
Cal=solver.calibration['INDEX_MCP_R']
rot=Cal
def term(coeff,vars):
    parts=[f'({float(a):.7g}*{v})' for a,v in zip(coeff,vars) if abs(float(a))>1e-7]
    return '('+'+'.join(parts)+')' if parts else '0'
ix=term(rot[0],['x','y','z']);iy=term(rot[1],['x','y','z']);iz=term(rot[2],['x','y','z'])
idx_expr=f'atan2(2*({ix}*{iy}-w*{iz}),1-2*({ix}**2+{iz}**2))'
# Thumb calibrated swing elevation is reconstructed from the same independent thumb base frame.
R=solver.rest['THUMB_CMC_R'];A=solver.thumb_anatom
l=R.transposed()@<REDACTED_EMAIL>_src_rest.transposed()@Vector((0,0,1))
v=solver.thumb_roll_offset.transposed()@Vector((0,1,0))
lv=float(l.dot(v));cross=v.cross(l)
dot_expr=f'({lv:.7g}*(w*w-x*x-y*y-z*z)+2*{term(l,["x","y","z"])}*{term(v,["x","y","z"])}+2*w*{term(cross,["x","y","z"])})'
neutral_elevation=math.asin(solver.thumb_neutral.z)
thumb_expr=f'asin(min(1,max(-1,{dot_expr})))-({neutral_elevation:.7g})'
derived=[('_FW_INDEX_ABDUCTION_R1','INDEX_MCP_R',idx_expr),('_FW_THUMB_SWING_ELEVATION_R1','THUMB_CMC_R',thumb_expr)]
for prop,bone,expression in derived:
    ob[prop]=0.0
    driver=ob.driver_add(f'["{prop}"]').driver;driver.type='SCRIPTED'
    for k,name in enumerate(['w','x','y','z']):
        var=driver.variables.new();var.name=name;var.type='SINGLE_PROP'
        t=var.targets[0];t.id=rig;t.data_path=f'pose.bones["{bone}"].rotation_quaternion[{k}]'
    driver.expression=expression
    assert driver.expression==expression, ('Driver expression truncated',len(expression))
driver=key.driver_add('value').driver;driver.type='SCRIPTED'
for name,prop in [('a',derived[0][0]),('s',derived[1][0])]:
    var=driver.variables.new();var.name=name;var.type='SINGLE_PROP'
    t=var.targets[0];t.id=ob;t.data_path=f'["{prop}"]'
expression='min(1,max(0,(abs(a)-.002)/.006))*max(min(1,max(0,(abs(a)-.06)/.06))*min(1,max(0,(.30-abs(a))/.06)),min(1,max(0,(s-.015)/.035))*min(1,max(0,(.15-s)/.04)))'
driver.expression=expression
assert driver.expression==expression
def expected_components():
    q=rig.pose.bones['INDEX_MCP_R'].rotation_quaternion
    S=<REDACTED_EMAIL>_matrix()@Cal.transposed();d=S@Vector((0,1,0))
    abd=math.atan2(d.x,d.y)
    q=rig.pose.bones['THUMB_CMC_R'].rotation_quaternion
    T=<REDACTED_EMAIL>()@<REDACTED_EMAIL>_matrix()@solver.thumb_roll_offset.transposed()
    td=T@Vector((0,1,0));s=math.asin(max(-1,min(1,td.z)))-neutral_elevation
    return abd,s
def inspect_case(label):
    bpy.context.view_layer.update()
    a,s=expected_components()
    actual_a,actual_s=float(ob[derived[0][0]]),float(ob[derived[1][0]])
    assert abs(a-actual_a)<2e-6 and abs(s-actual_s)<2e-6, (label,a,s,actual_a,actual_s)
    expected=eval(expression,{'__builtins__':{},'min':min,'max':max,'abs':abs},{'a':a,'s':s})
    assert abs(float(key.value)-expected)<8e-5,(label,key.value,expected)
    return {'case':label,'INDEX_MCP_abduction_rad':a,'THUMB_CMC_swing_elevation_relative_neutral_rad':s,'new_corrective_value':float(key.value)}
values=[]
for f in FRAMES+[181]:
    motion(rig,f);values.append(inspect_case(f'F{f}'))
reg_values=[]
for c in m.CASE_IDS:
    regression(rig,c);r=inspect_case(c);reg_values.append(r)
    assert float(key.value)==0, ('Approved pose must not activate new corrective',r)
neutral(rig)
assert key.value==0
assert m.product_payload(ob,rig)==native
shape=core.shape_payload(ob)
assert shape['keys'][:-1]==oldshape['keys'] and shape['drivers'][:-1]==oldshape['drivers']
assert [list(v.co) for v in basis.data]==native['positions_local_m']
assert actions()==saved_actions
design(ob);motion(rig,1)
bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE),compress=False)
dump('REAL_MOTION_CORRECTIVE_R1.json',{'key_name':key.name,'new_corrective_count':1,'basis_vertex_position_writes':0,
    'region_vertex_ids':region,'changed_vertex_ids':changed,'changed_vertex_count':len(changed),'region_center_world_m':center,'region_radii_m':radii,
    'method':'Single bounded shared pose-space surface-rounding delta fitted to F130/F76/F205/F31, inverted through unchanged LBS skin matrices; only new key coordinates written.',
    'max_posed_target_delta_mm':2.8,'ZERO_value':0,'existing_corrective_and_driver_unchanged':True,
    'driver_components':['INDEX_MCP anatomical abduction','THUMB_CMC swing elevation relative to previous calibrated-neutral'],
    'derived_scalar_driver_definitions':[{'property':p,'bone':b,'expression':e,'quaternion_variables':4} for p,b,e in derived],
    'corrective_driver_expression':expression,'corrective_driver_variable_count':2,'unique_joint_quaternion_inputs':8,
    'new_control_bones':0,'new_Action_channels':0,'no_Euler_channel_proxy':True,
    'defect_and_low_defect_actual_values':values,'approved_pose_values':reg_values,
    'selection_basis':'F61 low-defect remains inactive; four selected defects activate through differing index-abduction/thumb-swing patterns. F181 existing low-defect reference is auxiliary and may overlap. Correlation controls compensation, not a primary-cause claim.',
    'candidate_path':CANDIDATE.relative_to(ROOT).as_posix(),'candidate_sha256':sha(CANDIDATE),'further_corrective_iterations_allowed':False})
assert check_inputs()==inputs
print('ONE_REAL_MOTION_CORRECTIVE_READY',len(changed),values,reg_values,flush=True)
