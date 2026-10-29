import bpy,sys,importlib.util
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P));from stage_common import *
from left_chord_motion import *
from mathutils import Matrix,Vector
spec=importlib.util.spec_from_file_location('identity',ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
sm=read(o.STATIC/'STATIC_SCENE_MANIFEST_R2.json');source=o.STATIC/'STATIC_POSTURE_REFINED_CANDIDATE_R2.blend';assert sha(source)==sm['candidate_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
info=sm['mapping']['L1'];src=bpy.data.scenes[info['scene']];bpy.context.window.scene=src
for ob in src.objects:ob['LEFT_PREFLIGHT_COPY_TOKEN']=ob.name
bpy.ops.scene.new(type='FULL_COPY');sc=bpy.context.scene
copied={ob['LEFT_PREFLIGHT_COPY_TOKEN']:ob for ob in sc.objects if 'LEFT_PREFLIGHT_COPY_TOKEN' in ob}
for ob in list(src.objects)+list(sc.objects):
    if 'LEFT_PREFLIGHT_COPY_TOKEN' in ob:del ob['LEFT_PREFLIGHT_COPY_TOKEN']
sc.name='STATIC_PREFLIGHT_ONLY_NO_ACTION_NO_SAVED_CANDIDATE'
rig=copied[info['rig']];rt=copied[info['root']];mesh=copied[info['mesh']];base=rt.matrix_world.copy()
rig.animation_data_clear();rt.animation_data_clear();rt.rotation_mode='QUATERNION'
tl=read(P/'PERFORMANCE_TIMELINE.json');co=EventCoordinator(tl['notes'],read(P/'GENERATION_POLICY.json'));pivots={}
for n in tl['notes']:
    k=c.KEYS[n['key_index']];pv=bpy.data.objects.new('STATIC_PREFLIGHT_KEY_'+str(n['midi_note']),None);sc.collection.objects.link(pv);pv.location=k['press_pivot']
    for ob in [v for v in sc.objects if v.type=='MESH' and v.get('FROZEN_KEY_INDEX')==k['key_index']]:
        world=ob.matrix_world.copy();ob.parent=pv;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=Matrix.Translation(-Vector(k['press_pivot']))@world
    pivots[n['key_index']]=pv
center=float(np.mean([c.KEYS[n['key_index']]['key_center'][0] for n in tl['notes']]))
cameras={}
for view,eye,target in [('TEACHING',(center,-.60,.62),(center,-.04,.015)),('SIDE_OBLIQUE',(center+.07,-.60,.27),(center,-.025,.004))]:
    data=bpy.data.cameras.new('STATIC_LEFT_PREFLIGHT_'+view);data.type='ORTHO';data.ortho_scale=.56;data.clip_start=.001;data.clip_end=10
    ob=bpy.data.objects.new(data.name,data);sc.collection.objects.link(ob);ob.location=eye;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();cameras[view]=ob
sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
results=[];fkerr=0
for row in read(P/'STATIC_FEASIBILITY.json')['static_tests']:
    state=np.array(row['state']);q=np.radians(state[6:].reshape(5,4));extra=extra_rotation(state[3:6]);wrist=Vector(BASE)
    rt.matrix_world=Matrix.Translation(wrist+Vector(state[:3]/1000))@Matrix(extra.tolist()).to_4x4()@Matrix.Translation(-wrist)@base
    for j,d in enumerate(c.DIGITS):
        for name,rot in zip(c.SETUPS['L',d][0],c.joint_mats('L',d,q[j])):
            b=rig.pose.bones[name];b.rotation_mode='QUATERNION';b.rotation_quaternion=Matrix(rot).to_quaternion()
    angles=co.key_angles(row['time'])
    for ki,pv in pivots.items():pv.rotation_euler.x=float(angles[ki])
    bpy.context.view_layer.update();V,_=h.coords(mesh)
    pp=np.array([list(<REDACTED_EMAIL>[r['distal_frame']].matrix@Vector(r['local_pad_point'])) for r in c.MARKERS['L']])
    expected,_=fk_batch(state);fkerr=max(fkerr,float(np.max(np.linalg.norm(pp-expected[0],axis=1))*1000))
    measures=[]
    for n in tl['notes']:
        j=n['finger']-1;sp=V[c.MARKERS['L'][j]['mesh_vertex']]
        measures.append(dict(note=n['note_name'],finger=n['finger'],bone_pad=o.measure(pp[j],n['midi_note'],angles[n['key_index']]),skin_pad=o.measure(sp,n['midi_note'],angles[n['key_index']])))
    results.append(dict(test=row['test'],time=row['time'],measures=measures))
    if row['test']=='all_three_fully_down':
        for view,ob in cameras.items():
            sc.camera=ob;sc.render.filepath=str(P/f'preflight_static_down_{view.lower()}.png');bpy.ops.render.render(write_still=True)
assert fkerr<.03,('LEFT_FK_ADAPTATION_MISMATCH',fkerr)
dump('ACTUAL_LEFT_STATIC_READBACK.json',dict(tests=results,actual_left_pad_vs_FK_max_mm=fkerr,
    left_vertex_count=len(V),bone_count=len(rig.data.bones),original_source_sha256=sha(source),
    actions_created=0,candidate_blend_saved=False,new_dynamic_candidates=0,
    images_are_static_feasibility_checks_only=True,no_hand_asset_saved_or_modified=True))
print('LEFT_ACTUAL_STATIC_PARITY',fkerr,[(r['test'],[(v['note'],v['skin_pad']['gap_mm'],v['skin_pad']['horizontal_mm']) for v in r['measures']]) for r in results],flush=True)
