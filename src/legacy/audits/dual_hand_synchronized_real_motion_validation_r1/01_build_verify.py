"""Append approved Actions unchanged; compare isolated and dual evaluation. Audit only."""
import bpy,sys,json,hashlib,importlib.util,ast,re
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent; ROOT=P.parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def dump(n,x): (P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
spec=importlib.util.spec_from_file_location('identity',ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
tree=ast.parse((ROOT/'audits/pianovam_first_web_corrective_ab_isolation_r1/isolate.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='action_payload'],type_ignores=[]),'approved_identity','exec'))
cfg={
 'R':dict(baseline='production_spec/right_hand_product_baseline_r2/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R2.blend',sha='c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0',mesh='RIGHT_HAND_OFFICIAL_L1_PRODUCT_MESH',rig='RIGHT_HAND_PRODUCTION_RIG',source='audits/pianovam_retarget_local_axis_mapping_correction_r1/RIGHT_HAND_PIANO_AXIS_CORRECTED_TEST_R1.blend',source_sha='a5190adc13d39318096490f8fd2c9956d0daff457d25753fa3c216eee2027bbd',action='PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1',field='Left'),
 'L':dict(baseline='production_spec/left_hand_product_baseline_r1/LEFT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend',sha='54307bb199a75a5e684c29d346de9ca6bf2f8e7696911d9d69c57559516ad1a7',mesh='LEFT_HAND_OFFICIAL_L1_MIRROR_PRODUCT_MESH',rig='LEFT_HAND_PRODUCTION_RIG',source='audits/left_hand_real_motion_retarget_validation_r1/LEFT_HAND_REAL_MOTION_VALIDATION_CANDIDATE_R1.blend',source_sha='c356c3d223f9f0853b3451d93a2cdc4a0212805b72a7aea3bc829d084f41665d',action='PIANOVAM_PHYSICAL_LEFT_MIRRORED_MAPPING_R1',field='Right')}
protected={}
for folder in ['production_spec/right_hand_product_baseline_r1','production_spec/right_hand_product_baseline_r2','production_spec/left_hand_product_baseline_r1','audits/left_hand_real_motion_retarget_validation_r1','audits/pianovam_retarget_local_axis_mapping_correction_r1','references/piano_motion/pianovam_sample_r1']:
 for f in (ROOT/folder).rglob('*'):
  if f.is_file():protected[f.relative_to(ROOT).as_posix()]=sha(f)
for name in ['RIGHT_HAND_PRODUCT_BASELINE.json','LEFT_HAND_PRODUCT_BASELINE.json']:
 f=ROOT/'production_spec'/name;protected[f.relative_to(ROOT).as_posix()]=sha(f)
dump('PROTECTED_INPUTS_BEFORE_R1.json',protected)
for c in cfg.values():
 assert sha(ROOT/c['baseline'])==c['sha'];assert sha(ROOT/c['source'])==c['source_sha']
def curves(a):return [f for l in a.layers for s in l.strips for b in s.channelbags for f in b.fcurves]
def extra(a):return {'settings':h.scalars(a,('use_fake_user','users','is_updated','is_updated_data','is_runtime_data','is_evaluated','tag','session_uid','is_editable')),'props':h.props(a),'curves':[{'settings':h.scalars(f,('is_valid',)),'modifiers':[h.scalars(m) for m in f.modifiers],'key_settings':[h.scalars(k) for k in f.keyframe_points]} for f in curves(a)]}
def append_action(c):
 with bpy.data.libraries.load(str(ROOT/c['source']),link=False) as (a,b):b.actions=[c['action']]
 return bpy.data.actions[c['action']]
def bind(r,a):
 r.animation_data_create();r.animation_data.action=a;r.animation_data.action_slot=a.slots[0]
def frame(i):bpy.context.scene.frame_set(1+i//2,subframe=(i%2)*.5)
def objects(c):return bpy.data.objects[c['mesh']],bpy.data.objects[c['rig']]
def static(ob,rig):
 x=h.core(ob,rig)
 # Only container memberships and intentional runtime Action attachment are excluded.
 for k in ['mesh_object','armature_object']:x[k].pop('collections')
 x['armature_object'].pop('animation')
 # Blender append changes this read-only library bookkeeping flag; not deformation.
 for mod in x['modifiers']:mod['settings'].pop('is_override_data',None)
 return x
def sample(ob):return h.coords(ob)[0]
payloads={};extras={};identity={};bases={};isolated={};zero={};faces={};smooth={};corrective={}
for side,c in cfg.items():
 # Read exact approved source before append, without writing or evaluating retarget code.
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/c['source']),load_ui=False,use_scripts=False)
 a=bpy.data.actions[c['action']];payloads[side]=action_payload(a);extras[side]=extra(a)
 if side=='R':assert digest(payloads[side])=='b03d02e4f9f4f624c6c3faf1c1c1d53d717eac4770a216d3b1f54af89672cdb0','RIGHT_ACTION_IDENTITY_MISMATCH'
 assert len(curves(a))==64
 expected=[1+i*.5 for i in range(421)]
 assert all([float(k.co.x) for k in f.keyframe_points]==expected for f in curves(a))
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/c['baseline']),load_ui=False,use_scripts=False)
 ob,rig=objects(c);h.neutral(rig);bases[side]=static(ob,rig);zero[side]=sample(ob);faces[side]=[list(f.vertices) for f in ob.data.polygons];smooth[side]=[f.use_smooth for f in ob.data.polygons]
 a=append_action(c);assert action_payload(a)==payloads[side]
 if extra(a)!=extras[side]:
  dump('EXTRA_SOURCE_DEBUG.json',extras[side]);dump('EXTRA_APPEND_DEBUG.json',extra(a));raise AssertionError('EXTRA_SETTINGS_DIFFERENCE')
 bind(rig,a);v=[];vals=[]
 for i in range(421):frame(i);v.append(sample(ob));vals.append(h.values(ob))
 isolated[side]=np.array(v);corrective[side]=vals
 rig.animation_data.action=None;h.neutral(rig)
 assert np.array_equal(sample(ob),zero[side]);assert static(ob,rig)==bases[side],('ISOLATED_STATIC_MISMATCH',side)
 identity[side]={'action':c['action'],'source':c['source'],'source_file_sha256':c['source_sha'],'approved_payload_sha256':digest(payloads[side]),'curves':64,'keys_per_curve':421,'source_vs_appended_payload':'EXACT','supplementary_settings_keys_modifiers':'EXACT','prior_payload_digest_available':side=='R','left_source_binding':'Human-approved saved Action, exact source file SHA and full payload read before append' if side=='L' else None}
 print('ISOLATED_VERIFIED',side,flush=True)
# Create independent scene from the two formal object sets; preserve data names and parenting.
bpy.ops.wm.read_factory_settings(use_empty=True)
for side,c in cfg.items():
 with bpy.data.libraries.load(str(ROOT/c['baseline']),link=False) as (a,b):b.objects=[c['mesh'],c['rig']]
 for ob in b.objects:
  if ob and not ob.users_collection:bpy.context.scene.collection.objects.link(ob)
 ob,rig=objects(c);h.neutral(rig)
 if static(ob,rig)!=bases[side]:
  dump('STATIC_SOURCE_DEBUG.json',bases[side]);dump('STATIC_APPEND_DEBUG.json',static(ob,rig));raise AssertionError(('APPEND_STATIC_MISMATCH',side))
 bind(rig,append_action(c))
sc=bpy.context.scene;sc.render.fps=30;sc.render.fps_base=1;sc.frame_start=1;sc.frame_end=210
binding={};dual={s:[] for s in cfg};leaks=[]
for side,c in cfg.items():
 ob,rig=objects(c);a=rig.animation_data.action
 channels=[]
 for f in curves(a):
  m=re.fullmatch(r'pose.bones\["([^\"]+)"\].rotation_quaternion',f.data_path)
  assert m and m[1].endswith('_'+side) and m[1] in rig.pose.bones
  channels.append(m[1])
 assert all(m.object==rig for m in ob.modifiers if m.type=='ARMATURE')
 assert ob.parent==rig and not ob.constraints and not rig.constraints and all(not b.constraints for b in rig.pose.bones)
 drivers=[]
 for f in ob.data.shape_keys.animation_data.drivers:
  for var in f.driver.variables:
   for t in var.targets:
    assert t.id==rig and t.bone_target.endswith('_'+side)
    drivers.append({'variable':var.name,'target':t.id.name,'bone':t.bone_target})
 assert len(rig.animation_data.nla_tracks)==0 and len(rig.animation_data.drivers)==0
 binding[side]={'mesh':ob.name,'armature':rig.name,'action':a.name,'slot':rig.animation_data.action_slot.identifier,'slot_handle':rig.animation_data.action_slot.handle,'bag_slot_handles':[b.slot_handle for l in a.layers for s in l.strips for b in s.channelbags],'animated_bones':sorted(set(channels)),'corrective_targets':drivers,'constraints':0,'NLA_tracks':0,'mesh_armature_target':'SAME_SIDE_ONLY'}
 assert binding[side]['bag_slot_handles']==[rig.animation_data.action_slot.handle]
for i in range(421):
 frame(i)
 for side,c in cfg.items():dual[side].append(sample(objects(c)[0]))
for side in cfg:
 dual[side]=np.array(dual[side]);assert np.array_equal(dual[side],isolated[side]),('COMBINED_EVALUATION_REGRESSION',side,float(np.max(np.abs(dual[side]-isolated[side]))))
dump('CROSS_HAND_BINDING_R1.json',{'status':'PASS','CROSS_HAND_CHANNEL_LEAKAGE':0,'hands':binding,'isolated_vs_combined_all_421':'NUMERICALLY_EXACT','first_web_driver_crosswire':False})
# Static review translations are external empty parents, not edits to product transforms.
d=Vector((-.38,-.924,.018)).normalized();r=Vector((0,0,1)).cross(d).normalized();offsets={}
for side,c in cfg.items():
 ob,rig=objects(c);center=(isolated[side].reshape(-1,3).min(0)+isolated[side].reshape(-1,3).max(0))/2
 off=np.array(r)*(.145 if side=='R' else -.145)-center
 root=bpy.data.objects.new('DISPLAY_ONLY_REVIEW_OFFSET_'+side,None);sc.collection.objects.link(root);root.location=off;root['DUAL_HAND_REVIEW_OFFSETS']='DISPLAY_ONLY';root['NOT_PIANO_SPATIALIZED']=True;root['NOT_PRODUCT_ROOT_TRANSFORM']=True
 rig.parent=root;rig.matrix_parent_inverse=Matrix.Identity(4);offsets[side]=list(root.location)
for k in list(sc.keys()):del sc[k]
sc['PHASE']='DUAL_HAND_SYNCHRONIZED_REAL_MOTION_VALIDATION_R1';sc['DESIGN_ONLY']=True;sc['NOT_PRODUCTION']=True;sc['HUMAN_APPROVAL_PENDING']=True;sc['USAGE_SCOPE']='INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY';sc['LICENSE']='CC BY-NC-SA 4.0';sc['DUAL_HAND_REVIEW_OFFSETS']='DISPLAY_ONLY';sc['NOT_PIANO_SPATIALIZED']=True
frame(0);dest=P/'DUAL_HAND_REAL_MOTION_VALIDATION_CANDIDATE_R1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest))
bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False)
display={s:[] for s in cfg};safety={};staticchecks={}
for side,c in cfg.items():
 ob,rig=objects(c);a=rig.animation_data.action
 assert action_payload(a)==payloads[side] and extra(a)==extras[side],('REOPEN_ACTION_IDENTITY',side)
 identity[side]['saved_reopened_payload_sha256']=digest(action_payload(a));identity[side]['identity']='MATCHED'
for i in range(421):
 frame(i)
 for side,c in cfg.items():display[side].append(sample(objects(c)[0]))
for side,c in cfg.items():
 display[side]=np.array(display[side]);err=float(np.max(np.abs(display[side]-np.array(offsets[side])-isolated[side])))
 assert err<1e-6,('DISPLAY_OFFSET_PARITY',side,err)
 ob,rig=objects(c);rig.parent=None;rig.animation_data.action=None;h.neutral(rig)
 zeroerr=float(np.max(np.abs(sample(ob)-zero[side])));assert zeroerr==0
 current=static(ob,rig);staticchecks[side]={k:current[k]==v for k,v in bases[side].items()};assert all(staticchecks[side].values()),('REOPEN_STATIC',side,staticchecks[side])
 V=isolated[side];edges=np.array([list(e.vertices) for e in ob.data.edges]);length=np.linalg.norm(V[:,edges[:,0]]-V[:,edges[:,1]],axis=2);base=np.linalg.norm(zero[side][edges[:,0]]-zero[side][edges[:,1]],axis=1)
 triangles=np.array([[f[0],f[j],f[j+1]] for f in faces[side] for j in range(1,len(f)-1)]);areas=np.linalg.norm(np.cross(V[:,triangles[:,1]]-V[:,triangles[:,0]],V[:,triangles[:,2]]-V[:,triangles[:,0]]),axis=2)*.5
 extent=np.linalg.norm(np.ptp(V,axis=1),axis=1);extent0=float(np.linalg.norm(np.ptp(zero[side],axis=0)))
 safety[side]={'observations':421,'NaN_Inf':int(np.count_nonzero(~np.isfinite(V))),'degenerate_edges_under_1e-8m':int((length<1e-8).sum()),'degenerate_triangles_under_1e-14m2':int((areas<1e-14).sum()),'gross_collapse_extent_under_20pct_ZERO':int((extent<extent0*.2).sum()),'gross_tearing_edges_over_10x_ZERO':int((length/base>10).sum()),'min_triangle_area_m2':float(areas.min()),'max_edge_stretch_ratio':float((length/base).max()),'ZERO_restore_mm':zeroerr*1000,'isolated_vs_combined_max_mm':0.0,'display_offset_removed_max_mm':err*1000,'corrective_range':[min(list(x.values())[0] for x in corrective[side]),max(list(x.values())[0] for x in corrective[side])]}
 assert all(safety[side][k]==0 for k in ['NaN_Inf','degenerate_edges_under_1e-8m','degenerate_triangles_under_1e-14m2','gross_collapse_extent_under_20pct_ZERO','gross_tearing_edges_over_10x_ZERO'])
dump('DUAL_ACTION_IDENTITY_R1.json',{'status':'PASS','hands':identity,'retarget_smooth_axis_limit_rebuild_resample_operations':0,'candidate_sha256':sha(dest)})
dump('MINIMUM_SAFETY_R1.json',{'status':'PASS','hands':safety,'static_component_identity_after_save_reopen':staticchecks,'machine_checks_do_not_constitute_Human_approval':True})
rows=[{'observation_index':i,'source_frame':690+i,'source_timestamp_seconds':11.5+i/60,'right_blender_frame':1+i*.5,'left_blender_frame':1+i*.5,'output_frame_0based':i//2 if i%2==0 and i<420 else None} for i in range(421)]
dump('DUAL_SOURCE_TIMELINE_PARITY_R1.json',{'SOURCE_TIMELINE_PARITY':'EXACT','EXACT_SYNC':True,'recording':'2024-03-04_03-46-36','window_seconds':[11.5,18.5],'observations_per_hand':421,'source_Hz':60,'physical_right_field':'Left','physical_left_field':'Right','physical_mapping':'INHERITED_APPROVED_MAPPING','scene_fps':30,'output_frames':210,'endpoint_blender_frame':211,'last_rendered_source_time':11.5+209/30,'endpoint_note':'18.5s is retained at Action key211; 210 output frames sample11.5..18.4666667s, with duration7s ending18.5s. No duplicate endpoint frame.','manual_shifts':0,'mapping':rows})
np.savez_compressed(P/'evaluated_dual_motion.npz',R=display['R'],L=display['L'],R_isolated=isolated['R'],L_isolated=isolated['L'])
dump('RENDER_INPUT_R1.json',{'faces':faces,'smooth':smooth,'offsets':offsets,'DUAL_HAND_REVIEW_OFFSETS':'DISPLAY_ONLY','NOT_PIANO_SPATIALIZED':True})
unchanged={p:sha(ROOT/p)==v for p,v in protected.items()};assert all(unchanged.values())
dump('FINAL_ASSET_PROTECTION_R1.json',{'status':'PASS','protected_files':len(protected),'all_unchanged':True,'baselines':{s:{'path':c['baseline'],'sha256':sha(ROOT/c['baseline']),'unchanged':True} for s,c in cfg.items()},'RIGHT_R1_UNCHANGED':sha(ROOT/'production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend')=='4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2','production_pointer_updates':0})
print('DUAL_BUILD_AND_421_OBSERVATION_VERIFICATION_PASS',json.dumps(safety),flush=True)
