import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import numpy as np
from mathutils.bvhtree import BVHTree

assert sha(SOURCE)==SOURCE_SHA and sha(CURRENT)==EXPECTED and sha(RIG_SOURCE)==RIG_SHA
assert not CANDIDATE.exists(),'Never overwrite a review candidate'
ob,oldrig=open_asset(CURRENT)
V,F=evaluate(ob,ob.matrix_world);V=np.array(V)
groups=[g.name for g in ob.vertex_groups]
assert len(groups)==16
WD=np.zeros((len(V),len(groups)))
payload=[]
for v in ob.data.vertices:
    for g in v.groups:WD[v.index,g.group]=g.weight
    payload.append({groups[g.group]:float(g.weight) for g in v.groups if g.weight>0})
assert digest(payload)==WEIGHT_SHA
oldbones={b.name:{'head':list(<REDACTED_EMAIL>_local),'tail':list(<REDACTED_EMAIL>_local),
    'x':list(oldrig.matrix_world.to_3x3()@b.matrix_local.to_3x3().col[0]),
    'z':list(oldrig.matrix_world.to_3x3()@b.matrix_local.to_3x3().col[2]),
    'parent':b.parent.name if b.parent else None,'connected':b.use_connect,'deform':b.use_deform} for b in oldrig.data.bones}
raw=read(LINEAGE/'RAW_SOURCE_GEOMETRY.json')['stages']
ancestor=read(LINEAGE/'HISTORICAL_OPERATION_RAM_REPLAY.json')['final_ancestry']
lookup={tuple(v):i for i,v in enumerate(raw['STAGE4A_R2_BASE']['local_m'])}
known={i:lookup[tuple(v)] for i,v in enumerate(raw['STAGE4A_R2']['local_m']) if tuple(v) in lookup}
reg=read(LINEAGE/'DONOR_TO_CURRENT_TOPOLOGY_CORRESPONDENCE_R1.json')['rigid_display_registration']
R=np.array(reg['rotation_row']);T=np.array(reg['translation_mm'])/MM
source_world=np.array(raw['OFFICIAL_L1']['canonical_world_m'])@R+T
ids=np.array(sorted(known));mapped=np.array([sum(source_world[int(k)]*float(w) for k,w in ancestor[known[i]].items()) for i in ids])
engineering=V[ids]

def fit_point(point,bone=None,k=48):
    """Local affine spatial fit; source points remain untouched."""
    point=np.array(point);distance=np.linalg.norm(engineering-point,axis=1)
    pool=np.arange(len(ids))
    if bone and bone!='WRIST_R':
        digit=bone.split('_')[0]
        cols=[j for j,n in enumerate(groups) if n.startswith(digit+'_')]
        # MCP root also samples palm for continuity; other joints use the digit.
        threshold=.12 if '_MCP_' in bone or '_CMC_' in bone else .45
        semantic=np.sum(WD[ids][:,cols],axis=1)>threshold
        if semantic.sum()>=k:pool=pool[semantic]
    near=pool[np.argsort(distance[pool])[:k]]
    rel=engineering[near]-point
    h=max(float(np.median(distance[near])),.004)
    w=np.exp(-distance[near]**2/(2*h*h))
    design=np.column_stack((np.ones(len(near)),rel/h))
    # Modest linear regularization stabilizes fits around surface cylinders.
    lhs=design.T@(w[:,None]*design)+np.diag([1e-12,.002,.002,.002])
    beta=np.linalg.solve(lhs,design.T@(w[:,None]*mapped[near]))
    return beta[0],beta[1:].T/h,near

proxy=np.zeros_like(V)
proxy[ids]=mapped
unknown=sorted(set(range(len(V)))-set(ids))
for i in unknown:proxy[i]=fit_point(V[i],k=32)[0]
# Weight donor is only an unsaved registration proxy. No engineering faces
# or positions are placed in the product mesh.
triangles=[]
for f in F:
    for j in range(1,len(f)-1):
        tri=(f[0],f[j],f[j+1]);a,b,c=proxy[list(tri)]
        if np.linalg.norm(np.cross(b-a,c-a))>.00000000001:triangles.append(tri)
bvh=BVHTree.FromPolygons([Vector(v) for v in proxy],triangles,all_triangles=True)
new_weights=[];transfer=[]
for i,v in enumerate(source_world):
    hit,normal,face,distance=bvh.find_nearest(Vector(v));assert face is not None
    tri=triangles[face];a,b,c=proxy[list(tri)];e=b-a;f=c-a;d=np.array(hit)-a
    ee=e@e;ef=e@f;ff=f@f;den=ee*ff-ef*ef
    bb=(ff*(d@e)-ef*(d@f))/den;cc=(ee*(d@f)-ef*(d@e))/den
    bary=np.maximum([1-bb-cc,bb,cc],0);bary/=bary.sum()
    weights=bary@WD[list(tri)];weights[weights<1e-8]=0;weights/=weights.sum()
    new_weights.append(weights.tolist());transfer.append({'source_vertex_id':i,'donor_proxy_triangle':list(tri),'barycentric':bary.tolist(),'distance_mm':float(distance*MM)})

# Append only the approved corrected 21-bone armature, then fit its positions.
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(RIG_SOURCE),link=False) as (src,dst):
    dst.objects=['RIGHT_HAND_PRODUCTION_RIG']
rig=dst.objects[0];assert rig and rig.type=='ARMATURE'
bpy.context.scene.collection.objects.link(rig)
assert len(rig.data.bones)==21
for b in rig.data.bones:
    assert b.name in oldbones and (b.parent.name if b.parent else None)==oldbones[b.name]['parent']
    assert b.use_deform==oldbones[b.name]['deform']
rig.matrix_world=Matrix.Identity(4)
fitted={}
for name,b in oldbones.items():
    head,J,near=fit_point(b['head'],name)
    tail,_,_=fit_point(b['tail'],name)
    mapped_z=<REDACTED_EMAIL>(b['z'])
    fitted[name]={'head':head.tolist(),'tail':tail.tolist(),'z':mapped_z.tolist(),'neighbors':ids[near].tolist()}
for name,b in oldbones.items():
    if b['connected'] and b['parent']:fitted[name]['head']=fitted[b['parent']]['tail']
rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
for b in rig.data.edit_bones:
    fit=fitted[b.name];b.head=fit['head'];b.tail=fit['tail']
    assert (b.tail-b.head).length>.001
    b.align_roll(Vector(fit['z']))
    b.use_deform=oldbones[b.name]['deform']
bpy.ops.object.mode_set(mode='OBJECT');reset_pose(rig)

# Actual Official L1 mesh and evaluated UV/material data, without engineering
# retopology, old patches, or any source vertex setter.
with bpy.data.libraries.load(str(SOURCE),link=False) as (src,dst):dst.objects=['Hand  - Realistic']
so=dst.objects[0];bpy.context.scene.collection.objects.link(so)
assert next(m for m in so.modifiers if m.type=='MULTIRES').levels==1
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
me=bpy.data.meshes.new_from_object(so.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
assert [list(v.co) for v in me.vertices]==raw['OFFICIAL_L1']['local_m']
assert [list(f.vertices) for f in me.polygons]==raw['OFFICIAL_L1']['faces']
source_local=[list(v.co) for v in me.vertices]
world=Matrix(R).transposed().to_4x4();world.translation=Vector(T)
world=<REDACTED_EMAIL><REDACTED_EMAIL>((1.,-1.,-1.,1.))
product=bpy.data.objects.new(MESH_NAME,me);bpy.context.scene.collection.objects.link(product);product.matrix_world=world
bpy.data.objects.remove(so,do_unlink=True)
for j,name in enumerate(groups):product.vertex_groups.new(name=name)
for i,weights in enumerate(new_weights):
    for j,w in enumerate(weights):
        if w>0:product.vertex_groups[j].add([i],float(w),'REPLACE')
arm=product.modifiers.new('OFFICIAL_L1_TRANSFERRED_SKIN','ARMATURE');arm.object=rig
arm.use_vertex_groups=True;arm.use_bone_envelopes=False;arm.use_deform_preserve_volume=False
product.parent=rig;product.matrix_parent_inverse=rig.matrix_world.inverted();product.matrix_world=world
bpy.context.view_layer.update();ZV,ZF=evaluate(product,product.matrix_world)
SV=[world@Vector(v) for v in source_local];SF=[tuple(f) for f in raw['OFFICIAL_L1']['faces']]
assert ZF==SF and len(SV)==3300 and len(SF)==3298
zero_error=max((a-b).length*MM for a,b in zip(ZV,SV));print('BIND_ZERO_CHECK',zero_error,state_zero(rig),flush=True)
assert zero_error<=.0005 and state_zero(rig)
assert [list(v.co) for v in me.vertices]==source_local
E=[list(e.vertices) for e in me.edges]
safety,_=safety_check(ZV,ZF,E);assert safety['automatic_status']=='PASS'
assert [b.name for b in rig.data.bones if b.use_deform]==[n for n,b in oldbones.items() if b['deform']]
assert all(not b.use_deform for b in rig.data.bones if '_TIP_' in b.name)
# Cameras are source-derived once and frozen for static and motion comparison.
D=Vector((.631289124,.775318801,-.0188387)).normalized();P=-D;Z=Vector((0,0,1));X=D.cross(Z).normalized()
allpoints=SV
upper=[v for v in SV if v.z>min(p.z for p in SV)+.065]
thumb=Vector(fitted['THUMB_CMC_R']['head']);mcp=Vector(fitted['THUMB_MCP_R']['head'])
thenar=[v for v in SV if (v-(thumb+mcp)/2).length<.052]
cameras={
 'PALMAR_FULL':frame(allpoints,P,[1200,1100],padding=1.12),
 'DORSAL_FULL':frame(allpoints,D,[1200,1100],padding=1.12),
 'RADIAL_SIDE':frame(allpoints,X,[1200,1100],padding=1.12),
 'ULNAR_SIDE':frame(allpoints,-X,[1200,1100],padding=1.12),
 'THUMB_WEB_OBLIQUE':frame(upper,(P+X*.42+Z*.14).normalized(),[1200,1100],padding=1.13),
 'THENAR_CLOSE':frame(thenar,(P+X*.30).normalized(),[1200,1100],scale=.135),
 'FINGER_ROOTS_CLOSE':frame(upper,(P+Z*.24).normalized(),[1200,1100],scale=.19),
}
original=product_payload(product,rig)
for k,v in {'DESIGN_ONLY':True,'NOT_PRODUCTION':True,'HUMAN_APPROVAL':'PENDING','DO_NOT_PROMOTE':True,
 'PRODUCT_ROUTE':'OFFICIAL_L1_PLUS_EXISTING_21_BONE_RIG_PLUS_TRANSFERRED_SKIN','SOURCE_MESH_SHA256':SOURCE_SHA,
 'RIG_SOURCE_SHA256':RIG_SHA,'WEIGHT_DONOR_SHA256':WEIGHT_SHA,'PRODUCTION_PROMOTION':'NO'}.items():bpy.context.scene[k]=v
bpy.context.view_layer.objects.active=product
rig.select_set(False);product.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE),copy=True,compress=False)
product,rig=open_candidate();assert product_payload(product,rig)==original
dump('STATIC_BIND_AND_REBASE_R1.json',{'source':ref(SOURCE),'rig_source':ref(RIG_SOURCE),'weight_donor':ref(CURRENT),
 'candidate':ref(CANDIDATE),'source_counts':[3300,len(E),3298], 'bone_count':21,'group_names':groups,
 'source_native_local_positions_exact':True,'source_evaluated_faces_exact':True,'source_UV_materials_from_official_evaluated_L1':True,
 'zero_evaluated_source_error_mm':zero_error,'SOURCE_SHAPE_PRESERVED':'YES_EXACT_NATIVE_LOCAL_GEOMETRY',
 'armature_fit':'Local affine spatial correspondence fit for head/tail and mapped local roll; connected joints share endpoints; hierarchy/names/deform semantics retained',
 'bone_fit':fitted,'old_bone_structure':oldbones,'fitted_rest':original['rest'],
 'weight_transfer_method':'Nearest surface + barycentric interpolation on an unsaved pose-registered R2 donor proxy; normalize 16 deform influences; no TIP weights',
 'weight_donor_positive_payload_hash':digest(payload),'transferred_weight_payload_hash':digest(original['weights']),
 'transfer_rows':transfer,'proxy_missing_ancestry_vertex_count':len(unknown),'proxy_missing_vertex_method':'local affine interpolation from surrounding known surface correspondences',
 'proxy_geometry_not_part_of_candidate':True,'engineering_shape_or_faces_copied_to_product':False,
 'local_weight_tuning_vertex_count':0,'candidate_save_calls':1,'candidate_clean_reopen':'PASS','production_save_calls':0,
 'source_shape_vertex_setters':0,'static_machine':safety,'cameras':cameras,
 'source_world_m':[list(v) for v in SV],'rebased_zero_world_m':[list(v) for v in ZV],'faces':[list(f) for f in SF],
 'candidate_native_payload_hash':digest(original),'formal_pose_definitions':cases()})
renderer=Renderer(cameras)
views=['PALMAR_FULL','DORSAL_FULL','RADIAL_SIDE','ULNAR_SIDE','THUMB_WEB_OBLIQUE','THENAR_CLOSE']
renderer.draw('OFFICIAL_L1','REST',SV,SF,views)
renderer.draw('REBASED','ZERO',ZV,ZF,views)
renderer.dispose()
dump('STATIC_MATCHED_RENDER_MANIFEST_R1.json',{'renders':renderer.records,'cameras':cameras,'same_camera_scale_light_material':True,
 'source_shape_exact_preservation':True,'static_gate':'PENDING_ORDINARY_VISIBLE_SCREEN','dynamic_cases_executed':0})
print('STATIC_BIND_READY',zero_error,sha(CANDIDATE),flush=True)
