import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
from mathutils.bvhtree import BVHTree

def check_protected(ob,rig,native,shape,allow_mesh=False,allow_weights=False,helper=False):
    p=m.product_payload(ob,rig)
    for k in native:
        if k=='modifiers' or (allow_mesh and k in ['positions_local_m','faces','UV','weights']) or (allow_weights and k in ['weights','groups']):continue
        if k=='rest' and helper:
            for n in native[k]:assert p[k][n]==native[k][n],n
        else:assert p[k]==native[k],k
    if not allow_mesh:assert core.shape_payload(ob)==shape
    assert digest(action_payload(bpy.data.actions[ACTION]))==read(ROOT/'audits/pianovam_first_web_joint_contribution_isolation_r1/MACHINE_CHECK_R1.json')['actions_before'][ACTION]

def route_a():
    ob,rig=fresh();native=m.product_payload(ob,rig);shape=core.shape_payload(ob);oldme=ob.data
    n0=len(oldme.vertices);P=np.array([list(v.co) for v in oldme.vertices]);W=weights(ob);ids=set(PATCH_IDS)
    faces=[list(f.vertices) for f in oldme.polygons];selected=[i for i,f in enumerate(faces) if all(v in ids for v in f)]
    # Refine the compact bridge grid, redistribute only interior grid nodes tangentially,
    # then project them back to the original surface. No hand-wide remesh.
    tri=[(f[0],f[j],f[j+1]) for f in faces for j in range(1,len(f)-1)]
    tree=BVHTree.FromPolygons([Vector(v) for v in P],tri,all_triangles=True)
    adjacency=[[] for _ in P]
    for e in oldme.edges:
        a,b=e.vertices;adjacency[a].append(b);adjacency[b].append(a)
    mask=support(ob);moved=[];Pnew=P.copy()
    for i in PATCH_IDS:
        if not all(j in ids for j in adjacency[i]) or mask[i]<.08:continue
        delta=(P[adjacency[i]].mean(0)-P[i])*.35
        if np.linalg.norm(delta)>.0006:delta*=.0006/np.linalg.norm(delta)
        nearest,normal,face,dist=tree.find_nearest(Vector(P[i]+delta))
        if nearest is not None and (nearest-Vector(P[i])).length>1e-9:
            Pnew[i]=list(nearest);moved.append(i)
    stencils=[[(i,1.)] for i in range(n0)];verts=Pnew.tolist();mid={};centers={}
    for i in selected:
        f=faces[i]
        for a,b in zip(f,f[1:]+f[:1]):
            e=tuple(sorted((a,b)))
            if e not in mid:
                mid[e]=len(verts);verts.append(((Pnew[a]+Pnew[b])*.5).tolist());stencils.append([(a,.5),(b,.5)])
        centers[i]=len(verts)
        pt=np.mean(Pnew[f],axis=0);near=tree.find_nearest(Vector(pt))[0]
        verts.append(list(near) if near is not None else pt.tolist());stencils.append([(a,.25) for a in f])
    newfaces=[];UVrows=[];mats=[]
    uv_layers=list(oldme.uv_layers)
    for i,f in enumerate(faces):
        uv=[[[*layer.data[k].uv] for k in oldme.polygons[i].loop_indices] for layer in uv_layers]
        if i in centers:
            c=centers[i]
            for j,a in enumerate(f):
                b=f[(j+1)%4];prev=f[(j-1)%4]
                newfaces.append([a,mid[tuple(sorted((a,b)))],c,mid[tuple(sorted((prev,a)))]])
                UVrows.append([[row[j],((np.array(row[j])+row[(j+1)%4])*.5).tolist(),np.mean(row,axis=0).tolist(),((np.array(row[j])+row[(j-1)%4])*.5).tolist()] for row in uv]);mats.append(oldme.polygons[i].material_index)
        else:
            ff=[];u=[[] for _ in uv_layers]
            for j,a in enumerate(f):
                b=f[(j+1)%len(f)];ff.append(a)
                for k,row in enumerate(uv):u[k].append(row[j])
                e=tuple(sorted((a,b)))
                if e in mid:
                    ff.append(mid[e])
                    for k,row in enumerate(uv):u[k].append(((np.array(row[j])+row[(j+1)%len(f)])*.5).tolist())
            newfaces.append(ff);UVrows.append(u);mats.append(oldme.polygons[i].material_index)
    me=bpy.data.meshes.new('DESIGN_ONLY_LOCAL_FIRST_WEB_RETOPO');me.from_pydata(verts,[],newfaces);me.update()
    for mat in oldme.materials:me.materials.append(mat)
    for i,p in enumerate(me.polygons):p.material_index=mats[i];p.use_smooth=oldme.polygons[0].use_smooth
    for k,layer in enumerate(uv_layers):
        newuv=me.uv_layers.new(name=layer.name)
        for i,p in enumerate(me.polygons):
            for li,uv in zip(p.loop_indices,UVrows[i][k]):newuv.data[li].uv=uv
    ob.data=me
    for name in native['groups']:ob.vertex_groups.new(name=name)
    # Retain the approved relative corrective field; interpolate it for newly added nodes.
    for key in shape['keys']:
        kb=ob.shape_key_add(name=key['name'],from_mix=False)
        D=np.array(key['coords'])-P
        for i,s in enumerate(stencils):kb.data[i].co=Vector(verts[i])+Vector(sum((D[j]*w for j,w in s),np.zeros(3)))
        for p in ['interpolation','slider_min','slider_max','vertex_group','mute']:setattr(kb,p,key[p])
    for key in shape['keys']:me.shape_keys.key_blocks[key['name']].relative_key=me.shape_keys.key_blocks[key['relative_key']]
    for fc in oldme.shape_keys.animation_data.drivers:
        nc=me.shape_keys.driver_add(fc.data_path);nc.driver.type=fc.driver.type;nc.driver.expression=fc.driver.expression
        for v in fc.driver.variables:
            nv=nc.driver.variables.new();nv.name=v.name;nv.type=v.type
            for t,nt in zip(v.targets,nv.targets):
                for prop in ['id','bone_target','transform_type','transform_space','rotation_mode','data_path']:setattr(nt,prop,getattr(t,prop))
    for i,s in enumerate(stencils):
        row=sum((W[j]*w for j,w in s),np.zeros(W.shape[1]))
        for k,w in enumerate(row):
            if w>0:ob.vertex_groups[k].add([i],float(w),'REPLACE')
    neutral(rig);check_protected(ob,rig,native,shape,allow_mesh=True)
    assert core.shape_payload(ob)['drivers']==shape['drivers']
    delta=np.linalg.norm(coords(ob)[:n0]-np.array([list(ob.matrix_world@Vector(v)) for v in P]),axis=1)*1000
    path=OUT/'ROUTE_A_LOCAL_RETOPOLOGY_POC_R1.blend';save(ob,path)
    dump('ROUTE_A_BUILD_R1.json',{'method':'One compact 120-quad patch grid refinement + one bounded tangential rest-node redistribution projected to original surface. Existing corrective displacement field retained/interpolated, driver copied exactly. Existing weights interpolated once; no fitting or brush passes.','patch_original_ids':PATCH_IDS,'refined_quad_count':len(selected),'old_vertex_count':n0,'new_vertex_count':len(verts),'added_vertex_count':len(verts)-n0,'relocated_old_vertex_ids':moved,'old_vertex_zero_max_mm':float(delta.max()),'new_vertex_source_stencils':stencils[n0:],'approved_corrective_transfer':'Old per-node relative deltas retained; new nodes interpolate only that same delta field. No new corrective or edited driver expression.','UV_transfer':'Bilinear original loop UVs; one boundary transition ring may use n-gons','existing_21_rest_bones_preserved':True,'action_original_payload_preserved':True,'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'formal_rebuild':False})

def helper_matrix(rig,rest):
    # Blend skin transforms about one bridge anchor, not raw differently rolled local joint axes.
    T=[rig.pose.bones[n]<REDACTED_EMAIL>[n].matrix_local.inverted() for n in ['INDEX_MCP_R','THUMB_CMC_R']]
    q=T[0].to_quaternion().slerp(T[1].to_quaternion(),.5)
    h=rest.translation;target=(T[0]@h+T[1]@h)*.5
    H=q.to_matrix().to_4x4()@rest;H.translation=target
    parent=rig.pose.bones['WRIST_R'].matrix;parentrest=rig.data.bones['WRIST_R'].matrix_local
    return rest.inverted()@<REDACTED_EMAIL>()@H

def route_b():
    ob,rig=fresh();native=m.product_payload(ob,rig);shape=core.shape_payload(ob);W=weights(ob);mask=support(ob)
    bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
    b=rig.data.edit_bones.new('INTERNAL_FIRST_WEB_BRIDGE_R1');b.head=rig.matrix_world.inverted()@Vector((1.443,.022,.45));b.tail=b.head+Vector((0,0,.012));b.parent=rig.data.edit_bones['WRIST_R'];b.use_deform=True
    bpy.ops.object.mode_set(mode='OBJECT');bpy.context.view_layer.update()
    helper=rig.pose.bones['INTERNAL_FIRST_WEB_BRIDGE_R1'];helper.rotation_mode='QUATERNION';rest=helper.bone.matrix_local.copy()
    # Derived animation is isolated in a helper-only NLA action; the authorized Action stays untouched.
    derived=bpy.data.actions.new('DESIGN_ONLY_FIRST_WEB_HELPER_DERIVED_R1');samples=[]
    for i in range(421):
        motion(rig,1+i//2,(i%2)/2);Q=helper_matrix(rig,rest);loc,rot,scale=Q.decompose();samples.append((1+i/2,loc.copy(),rot.copy()))
    rig.animation_data.action=derived
    for f,loc,rot in samples:
        helper.location=loc;helper.rotation_quaternion=rot
        helper.keyframe_insert('location',frame=f,group=helper.name);helper.keyframe_insert('rotation_quaternion',frame=f,group=helper.name)
    rig.animation_data.action=None
    tr=rig.animation_data.nla_tracks.new();tr.name='DESIGN_ONLY_INTERNAL_HELPER';strip=tr.strips.new('DERIVED_FROM_EXISTING_JOINTS',1,derived);strip.blend_type='REPLACE';strip.extrapolation='NOTHING';strip.influence=1
    g=ob.vertex_groups.new(name=helper.name);changed=[]
    for i in PATCH_IDS:
        f=.45*float(mask[i])
        if f<1e-6:continue
        for k,w in enumerate(W[i]):
            if w>0:ob.vertex_groups[k].add([i],float(w*(1-f)),'REPLACE')
        g.add([i],f,'REPLACE');changed.append(i)
    neutral(rig);check_protected(ob,rig,native,shape,allow_weights=True,helper=True)
    originalzero=np.array(read(OUT/'TOPOLOGY_INPUT_R1.json')['ZERO_world']);error=float(np.linalg.norm(coords(ob)-originalzero,axis=1).max()*1000)
    assert error<.001
    path=OUT/'ROUTE_B_HELPER_BONE_POC_R1.blend';save(ob,path)
    dump('ROUTE_B_BUILD_R1.json',{'helper_bone_count':1,'helper_name':helper.name,'method':'One internal bridge bone: translation = mean transformed rest anchor under INDEX_MCP / THUMB_CMC skin transforms; rotation = quaternion slerp(0.5) of those two skin transforms. Converted through unchanged wrist parent into helper local pose.','helper_weight_max':float(.45*mask.max()),'changed_local_weight_ids':changed,'outside_local_weights_unchanged':True,'existing_21_bone_names_rest_motion_unchanged':True,'derived_motion_storage':'421 helper-only pose samples in separate NLA Action; original axis-corrected Action remains assigned for original joints. A simple runtime matrix blend can replace this POC bake.','no_external_mocap_channel':True,'ZERO_max_error_mm':error,'new_correctives':0,'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'formal_rebuild':False})

def route_c():
    ob,rig=fresh();native=m.product_payload(ob,rig);shape=core.shape_payload(ob);mask=support(ob)
    lat=bpy.data.lattices.new('DESIGN_ONLY_FIRST_WEB_LATTICE_R1');lat.points_u=lat.points_v=lat.points_w=3
    lat.interpolation_type_u=lat.interpolation_type_v=lat.interpolation_type_w='KEY_BSPLINE'
    cage=bpy.data.objects.new('INTERNAL_FIRST_WEB_CAGE_R1',lat);bpy.context.scene.collection.objects.link(cage)
    cage.location=(1.443,.022,.45);cage.scale=(.050,.054,.074)
    world=cage.matrix_world.copy();bpy.context.view_layer.update();world=cage.matrix_world.copy()
    cage.parent=rig;cage.parent_type='BONE';cage.parent_bone='WRIST_R';cage.matrix_world=world
    group=ob.vertex_groups.new(name='INTERNAL_FIRST_WEB_CAGE_MASK_R1')
    for i in PATCH_IDS:
        if mask[i]>0:group.add([i],float(mask[i]),'REPLACE')
    mod=ob.modifiers.new('DESIGN_ONLY_LOCAL_POST_SKIN_LATTICE_R1','LATTICE');mod.object=cage;mod.vertex_group=group.name;mod.strength=1
    # One deterministic 2 mm outward volume-support field, derived from relative thumb/index skin rotation.
    # It is not a per-frame sculpt or corrective key library.
    restpoints=[p.co_deform.copy() for p in lat.points]
    for i,p in enumerate(lat.points):
        x,y,z=restpoints[i];w=math.exp(-((x/.55)**2+(z/.55)**2))
        fc=p.driver_add('co_deform',1);d=fc.driver;d.type='SCRIPTED'
        for n,bone in [('i','INDEX_MCP_R'),('t','THUMB_CMC_R')]:
            for j in range(4):
                v=d.variables.new();v.name=n+str(j);v.type='SINGLE_PROP';v.targets[0].id=rig;v.targets[0].data_path=f'pose.bones["{bone}"].rotation_quaternion[{j}]'
        dot='(i0*t0+i1*t1+i2*t2+i3*t3)'
        d.expression=f'{y:.12g}-{.002/.054*w:.12g}*min(1,sqrt(max(0,1-({dot})**2))/.35)'
    cage.hide_render=True;cage.display_type='WIRE'
    neutral(rig)
    for k in ['positions_local_m','faces','UV','rest','mesh_world','rig_world']:assert m.product_payload(ob,rig)[k]==native[k],k
    assert [[g for g in row if g[0]<len(native['groups'])] for row in m.product_payload(ob,rig)['weights']]==native['weights']
    assert core.shape_payload(ob)==shape
    error=float(np.linalg.norm(coords(ob)-np.array(read(OUT/'TOPOLOGY_INPUT_R1.json')['ZERO_world']),axis=1).max()*1000)
    assert error<.001
    path=OUT/'ROUTE_C_LOCAL_CAGE_POC_R1.blend';save(ob,path)
    dump('ROUTE_C_BUILD_R1.json',{'method':'LATTICE','choice_reason':'Small 3×3×3 volume cage, deterministic control-point drivers, no target binding, no simulation; simpler than Mesh/Surface Deform for this bounded volume-support screen.','stack':'Existing shape keys -> original LBS Armature -> one local Lattice modifier','control_points':27,'maximum_control_displacement_m':.002,'driver':'Outward smooth B-spline volume-support field; activation derives from quaternion difference of existing index MCP and thumb CMC local rotations. Raw differing local frames are a POC limitation; no fitted severity gates.','control_point_pose_dependencies':['INDEX_MCP_R','THUMB_CMC_R'],'local_mask_ids':[i for i in PATCH_IDS if mask[i]>0],'original_weights_unchanged':True,'approved_corrective_unchanged':True,'new_shape_keys':0,'ZERO_max_error_mm':error,'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'formal_rebuild':False})

route=sys.argv[sys.argv.index('--route')+1]
{'A':route_a,'B':route_b,'C':route_c}[route]()
inputs();print('BOUNDED_POC_BUILT',route,flush=True)
