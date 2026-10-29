import sys,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
import bpy,numpy as np
P=Path(__file__).resolve().parent;OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1';sys.path.insert(0,str(OLD));import performance_core as c
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
man=read(P/'STATIC_SCENE_MANIFEST_R1.json');sol=read(P/'SOLVED_STATIC_POSES_R1.json');policy=read(P/'STATIC_POSTURE_POLICY_R1.json');lock=read(P/'PRE_SOLVE_LOCK_R1.json');results=read(P/'STATIC_POSTURE_RESULTS_R1.json');ui=read(P/'REVIEW_UI_VALIDATION_R1.json')
assert sha(P/'STATIC_POSTURE_POLICY_R1.json')==lock['policy_sha256']==sol['policy_sha256']==results['policy_sha256']
assert sha(P/'02_solve.py')==lock['solver_script_sha256']==sol['script_sha256']
assert sha(P/'STATIC_POSTURE_CANDIDATE_R1.blend')==man['candidate_sha256']==results['candidate_sha256']
assert len(list(P.glob('*.blend')))==1 and not list(P.glob('*.mp4')) and not list(P.glob('*.wav'))
required=['PIANO_HAND_FOUR_POSE_STATIC_FEASIBILITY_R1_REPORT.md','review.html','STATIC_POSTURE_POLICY_R1.json','STATIC_POSTURE_CANDIDATE_R1.blend','STATIC_POSTURE_RESULTS_R1.json','HAND_KEYBOARD_CLEARANCE_R1.json','LEFT_OCTAVE_POSE_COMPARISON_R1.json','RIGHT_FSHARP_POSTURE_R1.json','FINAL_ASSET_PROTECTION_R1.json','EVIDENCE_LEFT_L1_L2_R1.png','EVIDENCE_RIGHT_R1_R2_R1.png','EVIDENCE_SIDE_CLEARANCE_R1.png']
assert all((P/n).is_file() and (P/n).stat().st_size>0 for n in required)
assert ui['status']=='PASS_DELIVERY_UI_NOT_HUMAN_APPROVAL' and len(ui['states'])==12 and ui['question_rows']==13
assert all(d['success'] and d['one_initialization'] and d['restart_count']==0 for d in sol['solver_diagnostics'].values())
before=read(P/'PROTECTED_INPUTS_BEFORE_R1.json');changed=[p for p,v in before.items() if not Path(p).is_file() or sha(Path(p))!=v];assert not changed
renders=read(P/'RENDER_MANIFEST_R1.json');assert len(renders['renders'])==12 and all(sha(Path(row['file']))==row['sha256'] for row in renders['renders'])
bpy.ops.wm.open_mainfile(filepath=str(P/'STATIC_POSTURE_CANDIDATE_R1.blend'),load_ui=False,use_scripts=False)
assert len(bpy.data.scenes)==4 and len(bpy.data.actions)==0
geometry={};rigchecks={}
for pose,info in man['mapping'].items():
 sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc;assert sc.frame_start==sc.frame_end==1
 keyobs=[o for o in sc.objects if 'FROZEN_KEY_INDEX' in o];assert len({o['FROZEN_KEY_INDEX'] for o in keyobs})==88
 assert len(keyobs)==sum(len(k['geometry']) for k in c.KEYS)
 deltas=[]
 for k in c.KEYS:
  for g in k['geometry']:
   o=bpy.data.objects[pose+'_'+g['name']];v=np.array([list(<REDACTED_EMAIL>) for x in o.data.vertices]);assert len(v)==len(g['vertices']);deltas.append(float(np.max(np.linalg.norm(v-np.array(g['vertices']),axis=1))*1000))
   faces=[list(p.vertices) for p in o.data.polygons];inds=g['triangles'];assert faces==[inds[i:i+3] for i in range(0,len(inds),3)]
 assert max(deltas)<.001;geometry[pose]={'keys':88,'pieces':len(keyobs),'max_original_vertex_delta_mm':max(deltas),'triangle_order_unchanged':True,'key_transform_static':True}
 rig=bpy.data.objects[info['rig']];assert len(rig.data.bones)==21 and not (rig.animation_data and rig.animation_data.action)
 q=np.radians(sol['poses'][pose]['joint_increments_deg']);maxerr=0
 for j,d in enumerate(c.DIGITS):
  for name,r in zip(c.SETUPS[info['hand'],d][0],c.joint_mats(info['hand'],d,q[j])):maxerr=max(maxerr,float(np.max(np.abs(np.array(rig.pose.bones[name].matrix_basis)[:3,:3]-r))))
 assert maxerr<1e-5;rigchecks[pose]={'bones':21,'joint_basis_max_difference':maxerr,'no_bound_action':True,'intrinsic_matches':man['intrinsic_after_pose_save_reopen_reset_checks'][pose]['matches']};assert rigchecks[pose]['intrinsic_matches']
assert sha(P/'STATIC_POSTURE_CANDIDATE_R1.blend')==man['candidate_sha256']
out={'status':'PASS_DELIVERY_PROTECTION_AND_DECLARED_RESULTS_NOT_HUMAN_APPROVAL','required_outputs':{n:sha(P/n) for n in required},'protected_files_checked':len(before),'changed_files':changed,'one_candidate_verified':True,'four_static_scenes_verified':True,'continuous_action_count':0,'key_geometry':geometry,'rig_pose_roundtrip':rigchecks,'policy_and_script_prelock_matched':True,'one_initialization_no_restart_no_sweep':True,'tolerances_mm':{'vertical':3,'horizontal':2,'strict_actual_region':True},'pose_classes':{p:r['classification'] for p,r in results['poses'].items()},'render_count':12,'ui':{'states':12,'question_rows':13,'desktop':ui['desktop'],'mobile':ui['mobile'],'status':ui['status']},'FINAL_STATUS':results['FINAL_STATUS'],'dynamic_transition_proven':False,'human_approval':False}
(P/'DELIVERY_VERIFICATION_R1.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(out['status'],len(before),'UNCHANGED','keys',[g['max_original_vertex_delta_mm'] for g in geometry.values()])
