import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from blender_common import *
assert not DEST.exists()
B=read(P/'SOURCE_BINDINGS.json');tl=read(P/'PERFORMANCE_TIMELINE.json')
out={};neutral={};static={};allactions={}
for side,bind in B.items():
    man=bind['manifest'];folder=SOURCES[side];lead=bind['lead_sec'];assert sha(man['path'])==man['sha256']
    bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False)
    sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
    rt,rig,mesh=[bpy.data.objects[man['mapping'][k]] for k in ['root','rig','mesh']]
    assert rt.parent is None,('UNRESOLVED_ROOT_PARENT',side)
    assert rig.parent==rt and mesh.parent==rig
    assert next(m for m in mesh.modifiers if m.type=='ARMATURE').object==rig
    assert sc.render.fps==60 and sc.render.fps_base==1
    actions={}
    for label,ob in [('root',rt),('rig',rig)]+[(k,bpy.data.objects[n]) for k,n in man['key_pivots'].items()]:
        ad=ob.animation_data
        assert ad and ad.action and len(ad.nla_tracks)==0 and len(ad.drivers)==0
        assert all(len(f.modifiers)==0 for f in curves(ad.action))
        payload=action_payload(ad.action);fs=[k.co.x for f in curves(ad.action) for k in f.keyframe_points]
        actions[label]=dict(object=ob.name,action=ad.action.name,slot=ad.action_slot.identifier,payload_sha256=digest(payload),frame_range=[min(fs),max(fs)],fcurves=len(curves(ad.action)),keyframes=len(fs))
        allactions[side+'_'+label]=payload
    settime(sc,0);keyobs=keys(sc);kg={};nw={}
    for k in c.KEYS:
        ki=k['key_index'];obs=keyobs[ki];assert len(obs)==len(k['geometry'])
        kg[str(ki)]=[digest(geometry(ob)) for ob in obs]
        nw[str(ki)]=[np.array([list(<REDACTED_EMAIL>) for v in ob.data.vertices]) for ob in obs]
        # Match frozen Grand table by local geometry rather than renamed object.
        unused=list(k['geometry'])
        for ob in obs:
            actual=np.array([list(<REDACTED_EMAIL>) for v in ob.data.vertices])
            target=next(g for g in unused if len(g['vertices'])==len(actual) and np.max(np.linalg.norm(actual-np.array(g['vertices']),axis=1))<.00003)
            unused.remove(target)
    neutral[side]=nw
    structure=hand_structure(mesh,rig)
    # Capture actual motion, not planner output; include every approved sample,
    # every shared video frame, fractional event boundaries and phase probes.
    A=np.load(folder/'motion.npz');music_times=np.unique(np.round(np.r_[A['times']-lead,np.arange(357)/60-LEAD,*[[n['source_on_sec']-.12,n['source_on_sec'],n['source_on_sec']+.035,(n['source_on_sec']+n['source_off_sec'])/2,n['source_off_sec'],n['source_off_sec']+.07] for n in tl['notes'] if n['hand']==side]],9))
    arrays={k:[] for k in ['root','rig_world','joint_basis','joint_quat','verts','pads','skin_pads','key_angles']}
    for z,tm in enumerate(music_times):
        v=pose(sc,man['mapping'],side,float(tm+lead))
        for k in v:arrays[k].append(v[k])
        aa=np.zeros(88)
        for ki,name in man['key_pivots'].items():aa[int(ki)]=bpy.data.objects[name].rotation_euler.x
        arrays['key_angles'].append(aa)
        if z%200==0:print('READONLY_SOURCE_SAMPLE',side,z,len(music_times),flush=True)
    # Real sample times/curves agree with the saved approved numeric data.
    fkmax=0.;anglemax=0.
    for i in np.linspace(0,len(A['times'])-1,31,dtype=int):
        v=pose(sc,man['mapping'],side,float(A['times'][i]))
        for j,d in enumerate(c.DIGITS):
            for name,mat in zip(c.SETUPS[side,d][0],c.joint_mats(side,d,A[side+'_q'][i,j])):
                anglemax=max(anglemax,float(np.max(abs(np.array(rig.pose.bones[name].matrix_basis.to_3x3())-mat))))
        wrist=np.array(read(ROOT/'audits/piano_hand_static_posture_clearance_refinement_r2/SOLVED_STATIC_POSES_R2.json')['poses'][side+'1']['root_xyz_m'])
        anchor=read(ROOT/'audits/piano_hand_static_posture_clearance_refinement_r2/SOLVED_STATIC_POSES_R2.json')['poses'][side+'1']
        R=np.array(anchor['root_rotation_matrix']);canonical=np.array([c.fk(side,d,A[side+'_q'][i,j])[0] for j,d in enumerate(c.DIGITS)])@R.T+wrist
        expected=(canonical-wrist)@A[side+'_extra_rotation'][i].T+wrist+A[side+'_delta'][i]
        fkmax=max(fkmax,float(np.max(np.linalg.norm(v['pads']-expected,axis=1))*1000))
        assert max(abs(bpy.data.objects[name].rotation_euler.x-A['key_angles'][i,int(ki)]) for ki,name in man['key_pivots'].items())<1e-5
    assert anglemax<1e-5 and fkmax<.03
    np.savez_compressed(P/(side+'_approved_reference.npz'),music_times=music_times,**arrays)
    out[side]=dict(actions=actions,root_parent=None,rig_parent=rt.name,mesh_parent=rig.name,structure_sha256=structure,keyboard_geometry_sha256=kg,sample_count=len(music_times),action_lead_verified_sec=lead,joint_matrix_numeric_parity_max=anglemax,pad_FK_numeric_parity_max_mm=fkmax,render_engine=sc.render.engine,scene_objects=len(sc.objects),driver_targets=[h.driver(f) for f in mesh.data.shape_keys.animation_data.drivers],root_frame1=[list(v) for v in rt.matrix_world])
    sm=read(ROOT/'audits/piano_hand_static_posture_clearance_refinement_r2/STATIC_SCENE_MANIFEST_R2.json')
    st={}
    for label,info in sm['mapping'].items():
        bpy.context.window.scene=bpy.data.scenes[info['scene']];bpy.context.view_layer.update()
        st[label]=digest(h.core(bpy.data.objects[info['mesh']],bpy.data.objects[info['rig']]))
    assert st==man['static_four_core_sha256']
    static[side]=st
assert out['R']['keyboard_geometry_sha256']==out['L']['keyboard_geometry_sha256']
worlderr=max(float(np.max(np.linalg.norm(a-b,axis=1))*1000) for ki in neutral['R'] for a,b in zip(neutral['R'][ki],neutral['L'][ki]))
assert worlderr<.03
dump('APPROVED_ACTION_PAYLOADS.json',allactions)
dump('READONLY_PREFLIGHT.json',dict(pass_=True,hands=out,keyboard_rest_world_max_mm=worlderr,static_four_pose_sha256=static,coordinate_transform='IDENTITY; no hand placement change',key_ownership_conflict=False,shared_midi_count=23,NEW_MOTION_SOLVER_CALLS=0,candidates_saved=0))
print('PREGENERATION_READONLY_PASS',worlderr,flush=True)
