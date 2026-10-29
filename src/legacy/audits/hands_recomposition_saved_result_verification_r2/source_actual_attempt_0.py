"""One read-only static verification batch of the three immutable saved states."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from contract import *
from persistence import atomic_json,atomic_record
import bpy,math,traceback,itertools
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
import blender_helpers as h
import model as numeric

class ReconstructionError(RuntimeError):pass

def curves(action):
    return [f for layer in action.layers for strip in layer.strips for bag in strip.channelbags for f in bag.fcurves]

def actions_digest():
    return h.digest({a.name:[dict(path=f.data_path,index=f.array_index,extrapolation=f.extrapolation,
        points=[dict(co=list(k.co),interpolation=k.interpolation,handle_left=list(k.handle_left),handle_right=list(k.handle_right),handle_left_type=k.handle_left_type,handle_right_type=k.handle_right_type) for k in f.keyframe_points],
        modifiers=[dict(type=m.type) for m in f.modifiers]) for f in curves(a)] for a in bpy.data.actions})

def tree(V,F):return BVHTree.FromPolygons([Vector(v) for v in V],F,epsilon=0)
def overlap(a,b):return set((int(i),int(j)) for i,j in a.overlap(b))
def points_error(a,b):return float(np.linalg.norm(np.asarray(a)-np.asarray(b),axis=-1).max()*1000)

def contact(V,key,angle):
    vertex=numeric.PADIDS[4];p=V[vertex];pivot=np.array(key['press_pivot'])
    local=h.axisrot(-angle,key['press_axis'])@(p-pivot)+pivot
    s=min(key['key_top_playable_surface'],key=lambda s:np.linalg.norm(local[:2]-np.clip(local[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']])))
    miss=float(np.linalg.norm(local[:2]-np.clip(local[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']]))*1000)
    gap=float((local[2]-s['z'])*1000)
    inside=bool(s['xmin']<=local[0]<=s['xmax'] and s['ymin']<=local[1]<=s['ymax'])
    return dict(skin_vertex=vertex,world_m=p.tolist(),key_local_m=local.tolist(),horizontal_mm=miss,gap_mm=gap,inside_original_playable_region=inside,pass_=miss<=.03 and abs(gap)<=3 and inside)

def selfpairs(V,F):
    tr=tree(V,F);members=[set(f) for f in F]
    # Exclude topologically incident faces, including the intentional shared surface seam.
    return {(i,j) for i,j in overlap(tr,tr) if i<j and members[i].isdisjoint(members[j])}

def geometry(V,F,rois,regions,face_regions,components,owned):
    handtree=tree(V,F);digit_trees={d:tree(V,rois[d]['faces']) for d in numeric.DIGITS}
    pairsets={d+'_'+e:overlap(digit_trees[d],digit_trees[e]) for d,e in itertools.combinations(numeric.DIGITS,2)}
    selfset=selfpairs(V,F);keys={};little_peak=0.;little_witness=None;little_pairs=set();depth_witnesses=[]
    for key,g,keyV,keyF,planes in components:
        ki=key['key_index'];label=str(ki)+':'+g['name']
        depth=-np.max(V@planes[:,:3].T-planes[:,3],axis=1)*1000
        pairs=overlap(handtree,tree(keyV,keyF))
        regionrows={}
        for name,ids in regions.items():
            allowed=name in owned.get(ki,set())
            peak=float(max(0,depth[ids].max())) if len(ids) else 0.
            vp=int(ids[depth[ids].argmax()]) if len(ids) else None
            rp={(fi,kf) for fi,kf in pairs if fi in face_regions[name]}
            regionrows[name]=dict(depth_mm=peak,vertex=vp,allowed_own_key=allowed,pairs=rp)
            if peak>.5 and not allowed:
                depth_witnesses.append(dict(region=name,key=key['note_name'],component=g['name'],vertex=vp,depth_mm=peak,world_m=V[vp].tolist(),skin_key_face_pairs=len(rp)))
        active=regionrows['LITTLE_INFLUENCE_GT_005']
        if ki!=53:
            little_pairs.update((label,fi,kf) for fi,kf in active['pairs'])
            if active['depth_mm']>little_peak:
                little_peak=active['depth_mm'];vid=active['vertex']
                little_witness=dict(key=key['note_name'],component=g['name'],vertex=vid,depth_mm=little_peak,world_m=V[vid].tolist(),skin_key_face_pairs=len(active['pairs']))
        keys[label]=dict(key=key['note_name'],component=g['name'],regions=regionrows)
    return dict(digit_pairs=pairsets,self_pairs=selfset,keys=keys,little_depth_mm=little_peak,little_witness=little_witness,little_pairs=little_pairs,nonowned_depth_witnesses=depth_witnesses)

def serial_summary(g):
    return dict(digit_pairs={k:len(v) for k,v in g['digit_pairs'].items()},nonadjacent_full_hand_self_pairs=len(g['self_pairs']),
        active_little_wrong_key_depth_mm=g['little_depth_mm'],active_little_wrong_key_BVH_pairs=len(g['little_pairs']),active_little_witness=g['little_witness'],
        nonowned_depth_witnesses=g['nonowned_depth_witnesses'],keys={k:dict(key=v['key'],component=v['component'],regions={r:dict(depth_mm=s['depth_mm'],vertex=s['vertex'],allowed_own_key=s['allowed_own_key'],BVH_pairs=len(s['pairs'])) for r,s in v['regions'].items()}) for k,v in g['keys'].items()})

def compare(base,new):
    regressions=[]
    for pair,b in base['digit_pairs'].items():
        added=new['digit_pairs'][pair]-b
        if added:regressions.append(dict(kind='DIGIT_SKIN_NEW_FACE_INTERSECTION',region=pair,baseline_count=len(b),corrected_count=len(new['digit_pairs'][pair]),added_count=len(added),examples=sorted(added)[:12]))
    added=new['self_pairs']-base['self_pairs']
    if added:regressions.append(dict(kind='FULL_SKIN_NEW_NONADJACENT_INTERSECTION',added_count=len(added),examples=sorted(added)[:12]))
    for label,bk in base['keys'].items():
        for region,b in bk['regions'].items():
            if region=='LITTLE_INFLUENCE_GT_005':continue # checked independently as the active digit
            n=new['keys'][label]['regions'][region]
            if n['allowed_own_key']:continue
            if n['depth_mm']>.5 and n['depth_mm']>b['depth_mm']+.02:
                regressions.append(dict(kind='NONOWNED_KEY_DEPTH_REGRESSION',region=region,key=bk['key'],component=bk['component'],baseline_mm=b['depth_mm'],corrected_mm=n['depth_mm'],vertex=n['vertex']))
            added=n['pairs']-b['pairs']
            if added:regressions.append(dict(kind='NEW_SKIN_KEY_SURFACE_INTERSECTION',region=region,key=bk['key'],component=bk['component'],baseline_count=len(b['pairs']),corrected_count=len(n['pairs']),added_count=len(added),examples=sorted(added)[:12]))
    return regressions

def run():
    assert read(O/'INPUT_CONTRACT_GATE.json')['pass_']
    I,P,man,S,A,results=load_inputs()
    before=read(O/'INPUT_SHA_BEFORE.json')
    assert all(sha(p)==v for p,v in before.items()),'INPUT_CHANGED_BEFORE_BLENDER'
    atomic_json('BLENDER_BATCH_STARTED.json',dict(poses=TIMES,source_sha256=man['sha256'],optimizer_calls=0,code_sha256=sha(__file__)))
    h.RIG={'R':read(OLD/'RIG_CANONICAL_PROBE_R1.json')['R']};h.MARKERS={'R':numeric.MARK};h.DIGITS=numeric.DIGITS
    h.SETUPS={('R',d):h.digit_setup('R',d) for d in numeric.DIGITS}
    bpy.ops.wm.open_mainfile(filepath=str(safe_path(man['path'])),load_ui=False,use_scripts=False)
    assert not bpy.data.libraries,'EXTERNAL_LIBRARY_FORBIDDEN'
    sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
    assert sc.render.fps==60 and sc.render.fps_base==1.,'SCENE_CLOCK'
    rig=bpy.data.objects[man['mapping']['R']['rig']];mesh=bpy.data.objects[man['mapping']['R']['mesh']]
    left=bpy.data.objects[man['mapping']['L']['mesh']]
    native_before=h.digest(h.native(mesh,rig));assert native_before==I['native_sha256'],'FROZEN_NATIVE_IDENTITY'
    assert [b.name for b in rig.data.bones]==numeric.M['bones'],'BONE_ORDER_IDENTITY'
    assert np.array_equal(np.array([b.matrix_local for b in rig.data.bones]),numeric.D['rest_matrices']),'REST_IDENTITY'
    action_before=actions_digest();action_count=len(bpy.data.actions)
    for r in man['actions'].values():
        ob=bpy.data.objects[r['object']]
        assert ob.animation_data.action.name==r['action'] and ob.animation_data.action_slot.identifier==r['slot'],'SOURCE_ACTION_BINDING'
    rois=read(ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1/DIGIT_SKIN_ROI.json')
    groups={g.index:g.name for g in mesh.vertex_groups}
    weights=np.array([[sum(g.weight for g in v.groups if groups[g.group].startswith(d+'_')) for d in numeric.DIGITS] for v in mesh.data.vertices])
    ids=np.flatnonzero(weights[:,4]>.05);strong_union=set(v for r in rois.values() for v in r['vertices'])
    regions={d:np.array(rois[d]['vertices'],dtype=int) for d in numeric.DIGITS}
    regions['PALM_SHARED_WEB']=np.array([i for i in range(len(weights)) if i not in strong_union],dtype=int)
    regions['CROSS_DIGIT_MIXED_GT_005']=np.flatnonzero((weights>.05).sum(1)>=2)
    regions['LITTLE_INFLUENCE_GT_005']=ids
    saved=[];state_rows=[];key_parity=0.
    with np.load(O/'EXPECTED_RECONSTRUCTION.npz',allow_pickle=False) as ex:expected=ex['vertices'].copy()
    for ix,(a,meta,si) in enumerate(results):
        t=float(TIMES[ix]);h.settime(sc,t)
        basis_before={b.name:b.matrix_basis.copy() for b in rig.pose.bones};modes={b.name:b.rotation_mode for b in rig.pose.bones}
        action=rig.animation_data.action;slot=rig.animation_data.action_slot
        world=np.array(rig.matrix_world);baseV,F=h.coords(mesh);leftV,leftF=h.coords(left)
        ka=np.zeros(88)
        for k,n in man['key_pivots'].items():ka[int(k)]=bpy.data.objects[n].rotation_euler.x
        base_error=points_error(baseV,S['source_vertices'][ix]);world_error=float(abs(world-a['world']).max()*1000)
        if base_error>=.01 or world_error>=.001 or not np.array_equal(ka,a['key_angles']):raise ReconstructionError('ORIGINAL_C1_RECONSTRUCTION_MISMATCH')
        components=[]
        for key in numeric.KEYS:
            obs=[ob for ob in sc.objects if ob.type=='MESH' and ob.get('FROZEN_KEY_INDEX')==key['key_index']]
            assert len(obs)==len(key['geometry']),'88_KEY_COMPONENT_MAPPING'
            for g in key['geometry']:
                ob=next(ob for ob in obs if g['name'] in ob.name);kV,kF=h.coords(ob)
                pivot=np.array(key['press_pivot']);expect=(np.array(g['vertices'])-pivot)@h.axisrot(ka[key['key_index']],key['press_axis']).T+pivot
                key_parity=max(key_parity,float(abs(kV-expect).max()*1000))
                planes=h.component_planes(dict(vertices=kV,triangles=[i for f in kF for j in range(1,len(f)-1) for i in (f[0],f[j],f[j+1])]))
                components.append((key,g,kV,kF,planes))
        if key_parity>=.001:raise ReconstructionError('ACTUAL_88_KEY_GEOMETRY_MISMATCH')
        rig.animation_data.action=None
        try:
            for name,r in zip(h.SETUPS['R','LITTLE'][0],h.joint_mats('R','LITTLE',np.radians(a['q'][4]))):
                b=rig.pose.bones[name];b.rotation_mode='QUATERNION';b.rotation_quaternion=Matrix(r.tolist()).to_quaternion()
            bpy.context.view_layer.update();V,Fnew=h.coords(mesh)
            if Fnew!=F:raise ReconstructionError('SKIN_TOPOLOGY_MISMATCH')
            unchanged_error=max(float(abs(np.array(b.matrix_basis)-np.array(basis_before[b.name])).max()) for b in rig.pose.bones if b.name not in h.SETUPS['R','LITTLE'][0])
            if unchanged_error!=0.:raise ReconstructionError('OTHER_DIGIT_OR_SHARED_WRIST_CHANGED')
            pred_basis=numeric.basis(a['q'])[0]
            basis_error=max(float(abs(np.array(rig.pose.bones[n].matrix_basis)[:3,:3]-pred_basis[i]).max()) for i,n in enumerate(numeric.M['bones']))
            fk_expected=numeric.forward(pred_basis[None])[0]
            fk_actual=np.array([rig.pose.bones[n].matrix for n in numeric.M['bones']])
            fk_translation=points_error(fk_actual[:,:3,3],fk_expected[:,:3,3]);fk_matrix=float(abs(fk_actual-fk_expected).max())
            skin_error=points_error(V,expected[ix]);left_error=points_error(h.coords(left)[0],leftV)
            row=dict(time=t,baseline_skin_error_mm=base_error,corrected_skin_error_mm=skin_error,bone_basis_matrix_error=basis_error,FK_translation_error_mm=fk_translation,FK_matrix_error=fk_matrix,
                world_matrix_error_mm=world_error,other_bone_basis_error=unchanged_error,left_skin_error_mm=left_error,key_angles_exact=True,little_q_deg=a['q'][4],skin_vertex_count=len(V),skin_face_count=len(F))
            state_rows.append(row)
            atomic_json('STATE_RECONSTRUCTION_'+str(ix)+'.json',row)
            if skin_error>=.01 or basis_error>=.000035 or fk_translation>=.01 or fk_matrix>=.000035 or left_error!=0.:raise ReconstructionError('SAVED_STATE_ACTUAL_RIG_PARITY_FAIL')
            saved.append((baseV,V,F,components,ka,leftV,leftF))
            print('STATE_REBUILT',t,skin_error,fk_translation,flush=True)
        finally:
            for b in rig.pose.bones:b.rotation_mode=modes[b.name];b.matrix_basis=basis_before[b.name]
            rig.animation_data.action=action;rig.animation_data.action_slot=slot;bpy.context.view_layer.update()
    # Do not announce any geometry until all three saved states have been reconstructed.
    atomic_json('BLENDER_STATE_RECONSTRUCTION.json',dict(pass_=True,rows=state_rows,blender=bpy.app.version_string,key_geometry_parity_mm=key_parity,native_sha256=native_before))
    flat=[v for f in saved[0][2] for v in f];offsets=np.cumsum([0]+[len(f) for f in saved[0][2]])
    atomic_record('ACTUAL_BLENDER_STATIC_SKIN.npz',dict(times=TIMES,baseline_vertices=np.array([s[0] for s in saved]),corrected_vertices=np.array([s[1] for s in saved]),face_vertices=flat,face_offsets=offsets),dict(record_type='ACTUAL_BLENDER_EVALUATED_SKIN_STATIC_ONLY',source_sha256=man['sha256'],no_action_or_blend_saved=True))
    F=saved[0][2];face_regions={}
    for region,rids in regions.items():
        members=set(rids.tolist());face_regions[region]={i for i,f in enumerate(F) if any(v in members for v in f)}
    atomic_json('GEOMETRY_COVERAGE.json',dict(vertices=len(weights),faces=len(F),regions={r:dict(vertex_count=len(v),face_count=len(face_regions[r]),vertex_ids=v) for r,v in regions.items()},
        full_hand_self_surface_check='All nonincident face pairs; faces sharing a vertex excluded',ten_digit_pairs='Original strong digit weight >0.55 face ROIs',active_little='Vertex digit weight >0.05 plus every face incident to those vertices',
        key_body='All 3300 hand vertices versus all 88 actual evaluated convex key components',shared='Complement of five strong digit vertex ROIs, plus all cross-digit weights >0.05; full surface self/key BVH',
        exclusions=['Topologically incident self-face pairs','Volumetric containment between hand regions without a surface crossing','Force, tissue compression, under-sampled/subvertex pad area and anatomy','Continuous motion and Human naturalness']))
    rows=[]
    for ix,(baseV,V,F,components,ka,leftV,leftF) in enumerate(saved):
        t=float(TIMES[ix]);owned={}
        for n in I['right_events']:
            if n['note_on']<=t<n['note_off']+.04:owned.setdefault(n['key_index'],set()).add(numeric.DIGITS[n['finger']-1])
        owned.setdefault(53,set()).add('LITTLE_INFLUENCE_GT_005')
        bg=geometry(baseV,F,rois,regions,face_regions,components,owned);ng=geometry(V,F,rois,regions,face_regions,components,owned)
        regressions=compare(bg,ng);key=numeric.KEYS[53];ct=contact(V,key,ka[53]);baseline_ct=contact(baseV,key,ka[53])
        bp=overlap(tree(baseV,F),tree(leftV,leftF));npairs=overlap(tree(V,F),tree(leftV,leftF))
        if npairs-bp:regressions.append(dict(kind='NEW_RIGHT_LEFT_SKIN_INTERSECTION',added_count=len(npairs-bp),examples=sorted(npairs-bp)[:12]))
        active_pass=ng['little_depth_mm']<=.5 and not ng['little_pairs']
        row=dict(time=t,contact=ct,baseline_contact=baseline_ct,active_neighbor_pass=active_pass,nonregression_pass=not regressions,regressions=regressions,
            baseline=serial_summary(bg),corrected=serial_summary(ng),left_hand_BVH_pairs=dict(baseline=len(bp),corrected=len(npairs)),
            pass_=ct['pass_'] and active_pass and not regressions)
        rows.append(row);atomic_json('GEOMETRY_POSE_'+str(ix)+'.json',row)
        # Exact witnesses preserve actual skin/key meshes, not a bone marker or proxy.
        added_self=sorted(ng['self_pairs']-bg['self_pairs'])
        e5=[dict(key=k['note_name'],component=g['name'],world_vertices_m=kV,faces=kF) for k,g,kV,kF,pl in components if k['note_name']=='E5']
        atomic_json('GEOMETRY_WITNESS_'+str(ix)+'.json',dict(time=t,active_skin_vertex_ids=ids,baseline_active_wrong_key_face_pairs=sorted(bg['little_pairs']),corrected_active_wrong_key_face_pairs=sorted(ng['little_pairs']),
            E5_actual_geometry=e5,new_self_face_pairs=added_self,new_self_examples=[dict(faces=[F[i],F[j]],baseline_skin_m=[baseV[F[i]],baseV[F[j]]],corrected_skin_m=[V[F[i]],V[F[j]]]) for i,j in added_self[:24]],
            actual_skin_archive='ACTUAL_BLENDER_STATIC_SKIN.npz',regressions=regressions))
        print('GEOMETRY_POSE',t,'contact',ct['pass_'],'neighbor',active_pass,'regressions',len(regressions),'PASS',row['pass_'],flush=True)
        if not row['pass_']:break # real geometric FAIL: preserve witness and stop the batch
    native_after=h.digest(h.native(mesh,rig));after_action=actions_digest()
    assert native_after==native_before and after_action==action_before and len(bpy.data.actions)==action_count,'IN_MEMORY_FROZEN_PROTECTION_FAIL'
    after={p:sha(p) for p in before};assert after==before,'DISK_FROZEN_PROTECTION_FAIL'
    atomic_json('FROZEN_PROTECTION.json',dict(pass_=True,native_before=native_before,native_after=native_after,actions_before=action_before,actions_after=after_action,action_count=action_count,input_sha256_after=after,other_bones_unchanged=True,no_save=True))
    result='STATIC_SOURCE_CORRECTION_VERIFIED' if len(rows)==3 and all(r['pass_'] for r in rows) else 'STATIC_SOURCE_CORRECTION_FAIL'
    atomic_json('BLENDER_VERIFICATION_RESULT.json',dict(RESULT=result,reconstruction_pass=True,geometry_poses_checked=len(rows),requested_poses=3,rows=[dict(time=r['time'],contact=r['contact'],active_neighbor_pass=r['active_neighbor_pass'],nonregression_pass=r['nonregression_pass'],regressions=r['regressions']) for r in rows],frozen_protection_pass=True,optimizer_calls=0,DYNAMIC_RECOMPOSITION='NOT_EXECUTED',HUMAN_NATURALNESS='NOT_TESTED'))
    print('RESULT',result,flush=True)

if __name__=='__main__':
    try:run()
    except BaseException as error:
        atomic_json('BLENDER_FAILURE.json',dict(RESULT='INCONCLUSIVE' if isinstance(error,ReconstructionError) else 'BLOCKED_TOOLCHAIN',error=traceback.format_exc(),optimizer_calls=0))
        raise
