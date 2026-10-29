import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from bootstrap import *
import bpy,math,types,itertools
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
import model as n,blender_helpers as h
functions_from(ROOT/'audits/hands_recomposition_saved_result_verification_r2/source_actual.py',['curves','actions_digest'],globals())
functions_from(ROOT/'experiments/hands_role_aware_collision_avoidance_r1/baseline_blender.py',['degrees'],globals())
I=read(O/'INPUT_BINDINGS.json');man=I['scene'];motion,_=archive(O/'MOTION_CANDIDATE.npz')
assert (O/'NUMERICAL_LEDGER.json').exists(),'TARGET_COMPARISON_ONLY_AFTER_COMPLETE_CANDIDATE'
times=motion['times']
h.RIG={'R':read(OLD/'RIG_CANONICAL_PROBE_R1.json')['R']};h.MARKERS={'R':n.MARK};h.DIGITS=n.DIGITS;h.SETUPS={('R',d):h.digit_setup('R',d) for d in n.DIGITS};c=h

def coords_tri(ob):
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    try:
        me.calc_loop_triangles();V=np.array([list(<REDACTED_EMAIL>) for v in me.vertices]);F=[list(p.vertices) for p in me.polygons];T=np.array([list(t.vertices) for t in me.loop_triangles],dtype=np.int32)
        return V,F,T
    finally:ev.to_mesh_clear()
def tree(V,F):return BVHTree.FromPolygons([Vector(v) for v in V],F,epsilon=0)
def key_angles():
    a=np.zeros(88)
    for ki,name in man['key_pivots'].items():a[int(ki)]=bpy.data.objects[name].rotation_euler.x
    return a
def roles_owned(t):
    owned={}
    for e in I['right_events']:
        if e['note_on']<=t<e['note_off']+.04:owned.setdefault(e['key_index'],set()).add(n.DIGITS[e['finger']-1])
    return owned
def measure(V,F,t,angles):
    owned=roles_owned(t);trs={d:tree(V,n.ROIS[d]['faces']) for d in n.DIGITS};full=tree(V,F)
    pairs={d+'_'+e:len(trs[d].overlap(trs[e])) for d,e in itertools.combinations(n.DIGITS,2)}
    selfpairs=[(a,b) for a,b in full.overlap(full) if a<b and set(F[a]).isdisjoint(F[b])]
    contacts=[]
    for e in I['right_events']:
        if e['note_on']<=t<e['note_off']:
            j=e['finger']-1;_,miss,gap,_=n.surface_metrics(V[n.PADIDS[j]][None],n.KEYS[e['key_index']],angles[e['key_index']])
            contacts.append(dict(event=e['note_id'],finger=j+1,time=float(t),horizontal_mm=float(miss[0]*1000),gap_mm=float(gap[0]*1000),pass_=bool(miss[0]*1000<=.03 and abs(gap[0]*1000)<=3),skin_vertex=n.PADIDS[j]))
    peak=0.;hits=[];activepeak=0.;keyBHV=0;parity=0.
    for ki,g,pl,ob,kv0 in components:
        key=n.KEYS[ki];pv=np.array(key['press_pivot']);R=h.axisrot(angles[ki],key['press_axis']);local=(V-pv)@R+pv;gv=np.array(g['vertices'])
        actual=np.array([list(<REDACTED_EMAIL>) for v in ob.data.vertices]);expected=(gv-pv)@R.T+pv
        parity=max(parity,float(abs(actual-expected).max()*1000))
        if np.any(local.max(0)<gv.min(0)) or np.any(local.min(0)>gv.max(0)):continue
        depth=np.maximum(0,-np.max(local@pl[:,:3].T-pl[:,3],axis=1))*1000
        kt=tree(actual,[list(p.vertices) for p in ob.data.polygons]);overlap=full.overlap(kt);keyBHV+=len(overlap)
        for region,ids in regions.items():
            if region in owned.get(ki,set()):continue
            mx=float(depth[ids].max()) if len(ids) else 0.;peak=max(peak,mx)
            if region in owned.values():pass
            if region in n.DIGITS and any(e['finger']==n.DIGITS.index(region)+1 and e['note_on']<=t<e['note_off'] for e in I['right_events']):activepeak=max(activepeak,mx)
            if mx>.5:
                vid=int(ids[depth[ids].argmax()]);hits.append(dict(region=region,key=key['note_name'],component=g['name'],vertex=vid,depth_mm=mx,world_m=V[vid],skin_key_BVH_pairs=len(overlap)))
    assert parity<.001
    return dict(time=float(t),contacts=contacts,finger_pairs=pairs,full_nonincident_self_pairs=len(selfpairs),non_target_vertex_peak_mm=peak,active_non_target_vertex_peak_mm=activepeak,
        key_surface_BVH_pairs=keyBHV,vertex_intrusion_witnesses=hits,key_geometry_parity_mm=parity,product_geometry_pass=peak<=.5 and not any(pairs.values()) and not selfpairs)

bpy.ops.wm.open_mainfile(filepath=str(valid_path(man['path'])),load_ui=False,use_scripts=False);assert not bpy.data.libraries
sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
rig=bpy.data.objects[man['mapping']['R']['rig']];mesh=bpy.data.objects[man['mapping']['R']['mesh']];rt=bpy.data.objects[man['mapping']['R']['root']]
native_before=h.digest(h.native(mesh,rig));action_before=actions_digest();assert native_before==I['native_sha256']
union=set(v for d in n.ROIS.values() for v in d['vertices']);regions={d:np.array(n.ROIS[d]['vertices']) for d in n.DIGITS};regions['PALM_SHARED_WEB']=np.array([v for v in range(len(n.W)) if v not in union])
weight=np.column_stack([n.W[:,[i for i,name in enumerate(n.M['bones']) if name.startswith(d+'_')]].sum(1) for d in n.DIGITS]);regions['CROSS_DIGIT_MIXED']=np.flatnonzero((weight>.05).sum(1)>=2)
components=[]
for key,g,pl in n.COMPONENTS:
    ob=next(o for o in sc.objects if o.type=='MESH' and o.get('FROZEN_KEY_INDEX')==key['key_index'] and g['name'] in o.name)
    components.append((key['key_index'],g,pl,ob,np.array([list(v.co) for v in ob.data.vertices])))
BV=[];BT=[];BQ=[];BW=[];KA=[];base_rows=[]
# Original target trace is now post-generation comparison only.
for ix,t in enumerate(times):
    h.settime(sc,float(t));V,F,T=coords_tri(mesh);a=key_angles();BV.append(V);BT.append(T);BQ.append([degrees(d) for d in n.DIGITS]);BW.append(np.array(rig.matrix_world));KA.append(a)
    base_rows.append(measure(V,F,float(t),a))
    if ix%60==0:print('POST_GENERATION_BASELINE',ix,len(times),flush=True)
atomic_record('TARGET_C1_POSTHOC_REFERENCE.npz',dict(times=times,q_deg=BQ,rig_world=BW,actual_vertices=BV,key_angles=KA,triangles=BT),dict(record_type='POST_GENERATION_REFERENCE_NOT_INPUT',candidate_sha256=sha(O/'MOTION_CANDIDATE.npz')))
original_action=rig.animation_data.action;original_slot=rig.animation_data.action_slot;root_action=rt.animation_data.action;root_slot=rt.animation_data.action_slot
original_basis={b.name:b.matrix_basis.copy() for b in rig.pose.bones};original_modes={b.name:b.rotation_mode for b in rig.pose.bones}
rig.animation_data.action=None;rt.animation_data.action=None
VV=[];TT=[];rows=[];paritymax=0.;KA_error=0.
try:
    for ix,t in enumerate(times):
        h.settime(sc,float(t));q=motion['q_deg'][ix];world=motion['rig_world'][ix];rt.matrix_world=Matrix(world.tolist())@Matrix(I['full_root_rig_relation']).inverted()
        basis=n.basis(q)[0]
        for digit in n.DIGITS:
            for name in n.NAMES[n.DIGITS.index(digit)]:
                b=rig.pose.bones[name];b.rotation_mode='QUATERNION';b.rotation_quaternion=Matrix(basis[n.BN[name]].tolist()).to_quaternion()
        bpy.context.view_layer.update();V,F,T=coords_tri(mesh);a=key_angles();err=float(np.linalg.norm(V-n.native(q,world)[0],axis=1).max()*1000);paritymax=max(paritymax,err)
        if err>=.01:
            atomic_record('FRAME_RECONSTRUCTION_FAILURE.npz',dict(time=[t],q=q,world=world,actual_vertices=V),dict(error_mm=err));raise RuntimeError('REAL_CANDIDATE_NATIVE_RECONSTRUCTION_FAIL')
        KA_error=max(KA_error,float(abs(a-motion['key_angles'][ix]).max()))
        VV.append(V);TT.append(T);row=measure(V,F,float(t),a);row['native_skin_error_mm']=err;rows.append(row)
        if ix%60==0:print('REAL_DYNAMIC_CANDIDATE',ix,len(times),'depth',row['non_target_vertex_peak_mm'],'pairs',sum(row['finger_pairs'].values()),flush=True)
    atomic_record('CANDIDATE_ACTUAL_SKIN.npz',dict(times=times,vertices=VV,triangles=TT,key_angles=KA,q_deg=motion['q_deg'],rig_world=motion['rig_world']),dict(record_type='ACTUAL_BLENDER_ONE_DYNAMIC_CANDIDATE',no_original_scene_saved=True))
finally:
    rig.animation_data.action=original_action;rig.animation_data.action_slot=original_slot;rt.animation_data.action=root_action;rt.animation_data.action_slot=root_slot
    for b in rig.pose.bones:b.rotation_mode=original_modes[b.name];b.matrix_basis=original_basis[b.name]
    bpy.context.view_layer.update()
assert h.digest(h.native(mesh,rig))==native_before and actions_digest()==action_before and sha(man['path'])==man['sha256']
atomic_json('DYNAMIC_BLENDER_GEOMETRY.json',dict(rows=rows,baseline_rows=base_rows,actual_sample_count=len(rows),all_five_digits_and_shared_skin=True,key_components=139,
    native_reconstruction_pass=True,native_skin_error_max_mm=paritymax,planned_key_angle_error_max_rad=KA_error,native_unchanged=True,key_and_original_actions_unchanged=True,
    actual_mesh_regions={k:len(v) for k,v in regions.items()},sampling='240Hz actual Blender plus exact phases and Hermite supports; finite samples, not continuous collision certificate'))
contacts=[x for row in rows for x in row['contacts']];numeric=read(O/'NUMERIC_CANDIDATE_GATE.json')
contactpass=all(x['pass_'] for x in contacts);geompass=all(row['product_geometry_pass'] for row in rows)
atomic_json('BLENDER_CANDIDATE_GATE.json',dict(pass_=contactpass and geompass and numeric['pass_'],contact_pass=contactpass,product_geometry_pass=geompass,
    contact_failure_count=sum(not x['pass_'] for x in contacts),contact_horizontal_max_mm=max(x['horizontal_mm'] for x in contacts),contact_gap_abs_max_mm=max(abs(x['gap_mm']) for x in contacts),
    non_target_vertex_peak_mm=max(row['non_target_vertex_peak_mm'] for row in rows),finger_pair_peak=max(sum(row['finger_pairs'].values()) for row in rows),
    numeric_preflight_pass=numeric['pass_'],no_video_authorized=not(contactpass and geompass and numeric['pass_']),original_native_sha256=native_before,original_actions_sha256=action_before))
protect();print('BLENDER_CANDIDATE_GATE',contactpass,geompass,numeric['pass_'],flush=True)
