import sys,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
import bpy,numpy as np
P=Path(__file__).resolve().parent;R1=P.parent/'piano_hand_four_pose_static_feasibility_r1';OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1';sys.path.insert(0,str(OLD));import performance_core as c
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
man=read(P/'STATIC_SCENE_MANIFEST_R2.json');sol=read(P/'SOLVED_STATIC_POSES_R2.json');lock=read(P/'PRE_SOLVE_LOCK_R2.json');results=read(P/'STATIC_POSTURE_RESULTS_R2.json');ui=read(P/'REVIEW_UI_VALIDATION_R2.json');clear=read(P/'HAND_KEYBOARD_CLEARANCE_R2.json')
assert sha(P/'STATIC_REFINEMENT_POLICY_R2.json')==lock['policy_sha256']==sol['policy_sha256']==results['policy_sha256'];assert sha(P/'01_solve.py')==lock['solver_script_sha256']==sol['script_sha256'];assert sha(P/'STATIC_POSTURE_REFINED_CANDIDATE_R2.blend')==man['candidate_sha256']==results['candidate_sha256']
assert len(list(P.glob('*.blend')))==1 and not list(P.glob('*.mp4')) and not list(P.glob('*.wav'));assert all(d['success'] and d['one_initialization'] and d['restart_count']==0 for d in sol['solver_diagnostics'].values())
required=['PIANO_HAND_STATIC_POSTURE_CLEARANCE_REFINEMENT_R2_REPORT.md','review.html','STATIC_REFINEMENT_POLICY_R2.json','STATIC_POSTURE_REFINED_CANDIDATE_R2.blend','STATIC_POSTURE_RESULTS_R2.json','LEFT_OCTAVE_REFINEMENT_R2.json','RIGHT_NEIGHBOR_KEY_CLEARANCE_R2.json','HAND_KEYBOARD_CLEARANCE_R2.json','FINAL_ASSET_PROTECTION_R2.json','EVIDENCE_LEFT_BEFORE_AFTER_R2.png','EVIDENCE_RIGHT_BEFORE_AFTER_R2.png','EVIDENCE_SIDE_CLEARANCE_R2.png'];assert all((P/n).is_file() and (P/n).stat().st_size>0 for n in required)
before=read(P/'PROTECTED_INPUTS_BEFORE_R2.json');changed=[p for p,v in before.items() if not Path(p).is_file() or sha(Path(p))!=v];assert not changed;assert ui['status']=='PASS_MATCHED_REVIEW_UI_NOT_HUMAN_APPROVAL' and len(ui['states'])==12 and ui['question_rows']==13
renders=read(P/'RENDER_MANIFEST_R2.json');assert len(renders['renders'])==12 and all(sha(Path(r['file']))==r['sha256'] for r in renders['renders'])
assert all(p['mesh_deep_key_vertices']==0 and p['palm_deep_key_vertices']==0 and p['wrist_deep_key_vertices']==0 and not p['unexpected_fixed_pad_contacts'] for p in clear['poses'].values())
assert all(p['all_required_fixed_pad_contacts_pass'] and p['all_required_skin_pad_contacts_pass'] and p['all_prepared_regions_and_gaps_pass'] for p in results['poses'].values())
def camera_signature(sc,info):
 return {'cameras':{v:{'matrix_world':[list(r) for r in bpy.data.objects[n].matrix_world],'type':bpy.data.objects[n].data.type,'ortho_scale':bpy.data.objects[n].data.ortho_scale,'clip_start':bpy.data.objects[n].data.clip_start,'clip_end':bpy.data.objects[n].data.clip_end} for v,n in info['cameras'].items()},'render':[sc.render.engine,sc.render.resolution_x,sc.render.resolution_y,sc.render.resolution_percentage,sc.view_settings.view_transform],'display':[sc.display.shading.light,sc.display.shading.studio_light,sc.display.shading.color_type,sc.display.shading.show_shadows,sc.display.shading.show_cavity,sc.display.shading.cavity_type,sc.display.shading.curvature_ridge_factor,sc.display.shading.curvature_valley_factor,sc.display.shading.show_specular_highlight,sc.display.shading.show_object_outline]}
def key_signature(sc):
 out={}
 for o in sc.objects:
  if 'FROZEN_KEY_INDEX' in o:
   out[o.name]={'index':o['FROZEN_KEY_INDEX'],'midi':o['MIDI_NOTE'],'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'world':[list(r) for r in o.matrix_world],'color':list(o.color),'materials':[m.name if m else None for m in o.data.materials]}
 return out
baseline={};bpy.ops.wm.open_mainfile(filepath=str(R1/'STATIC_POSTURE_CANDIDATE_R1.blend'),load_ui=False,use_scripts=False)
for pose,info in man['mapping'].items():
 sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc;bpy.context.view_layer.update();baseline[pose]={'keys':key_signature(sc),'presentation':camera_signature(sc,info)}
bpy.ops.wm.open_mainfile(filepath=str(P/'STATIC_POSTURE_REFINED_CANDIDATE_R2.blend'),load_ui=False,use_scripts=False);assert len(bpy.data.scenes)==4 and len(bpy.data.actions)==0;verified={}
for pose,info in man['mapping'].items():
 sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc;bpy.context.view_layer.update();assert sc.frame_start==sc.frame_end==1;keys=key_signature(sc);assert keys==baseline[pose]['keys'];assert camera_signature(sc,info)==baseline[pose]['presentation'],('PRESENTATION_DIFF',pose,camera_signature(sc,info),baseline[pose]['presentation']);assert len({x['index'] for x in keys.values()})==88
 rig=bpy.data.objects[info['rig']];assert len(rig.data.bones)==21 and not (rig.animation_data and rig.animation_data.action);assert man['intrinsic_identity'][pose]['matches'];q=np.radians(sol['poses'][pose]['joint_increments_deg']);maxerr=0
 for j,d in enumerate(c.DIGITS):
  for name,r in zip(c.SETUPS[info['hand'],d][0],c.joint_mats(info['hand'],d,q[j])):maxerr=max(maxerr,float(np.max(abs(np.array(rig.pose.bones[name].matrix_basis)[:3,:3]-r))))
 assert maxerr<1e-5;verified[pose]={'keys':88,'keyboard_vertices_faces_transforms_colors_materials_exactly_match_R1':True,'cameras_framing_render_display_exactly_match_R1':True,'bones':21,'joint_basis_max_error':maxerr,'intrinsic_identity_matches':True,'no_continuous_action':True}
for a,b in [('L1','L2'),('R1','R2')]:assert np.array_equal(np.array(bpy.data.objects[man['mapping'][a]['root']].matrix_world),np.array(bpy.data.objects[man['mapping'][b]['root']].matrix_world))
assert sha(P/'STATIC_POSTURE_REFINED_CANDIDATE_R2.blend')==man['candidate_sha256']
out={'status':'PASS_DELIVERY_AND_PROTECTION_CANDIDATE_NOT_HUMAN_APPROVAL','required_outputs':{n:sha(P/n) for n in required},'protected_files_checked':len(before),'changed_files':changed,'one_candidate':True,'static_scenes':4,'policy_script_prelock_verified':True,'one_initialization_per_pair_no_sweep':True,'source_R1_not_rerun':True,'scene_verification':verified,'root_pairs_exactly_shared':True,'all_contact_and_preparation_screens_pass':True,'all88_key_depth_screens_zero':True,'human_visible_precheck_not_human_approval':True,'new_unique_renders':12,'matched_ui_states':12,'desktop':ui['desktop'],'mobile':ui['mobile'],'FINAL_STATUS':results['FINAL_STATUS'],'Human_approval':False,'dynamic_transition_proven':False}
(P/'DELIVERY_VERIFICATION_R2.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(out['status'],len(before),'UNCHANGED','MATCHED_CAMERAS_MATERIAL_KEYS','ZERO_ACTION')
