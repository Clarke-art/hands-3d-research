from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=read(P/'PROTECTED_INPUTS_BEFORE_R2.json');changed=[p for p,v in before.items() if not Path(p).is_file() or sha(Path(p))!=v];assert not changed
required=['REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT.md','review.html','REAL_PIANO_REFERENCE_MANIFEST_R2.md','NATURAL_PIANO_HAND_POSTURE_CONTRACT_R2.md','HAND_KEYBOARD_STATIC_FEASIBILITY_R2.json','NEXT_MOTION_PLANNER_REQUIREMENTS_R2.md','FINAL_ASSET_PROTECTION_R2.json']
assert all((P/n).is_file() and (P/n).stat().st_size>0 for n in required)
assert not list(P.glob('*.blend*')) and not list(P.glob('*.npz')) and not list(P.glob('*.mp4'))
assert not (P/'STATIC_POSTURE_RESULTS_R2.json').exists()
f=read(P/'HAND_KEYBOARD_STATIC_FEASIBILITY_R2.json');assert f['candidate_count']==0 and f['static_probe']=='NOT_RUN'
checks=['ACTIVE_FINGER_CONTACT','IDLE_FINGER_POSTURE','PALM_CLEARANCE','WRIST_CLEARANCE','NEIGHBOR_KEY_INTERFERENCE','JOINT_POSTURE']
assert set(f['poses'])=={'L1','L2','R1','R2'} and all(all(row[k]=='NOT_RUN' for k in checks) for row in f['poses'].values())
ui=read(P/'REVIEW_UI_VALIDATION_R2.json');assert ui['status']=='PASS_DELIVERY_UI_NOT_POSTURE_PASS' and not ui['external_images_embedded']
play=read(P/'EMBEDDED_PLAYBACK_R2.json');assert len(play)==3 and all('聊天机器人' in row['text'] and all(v['ready']==0 and v['time']==0 for v in row['videos']) for row in play)
protection=read(P/'FINAL_ASSET_PROTECTION_R2.json');assert protection['HAND_BASELINES_UNCHANGED'] and protection['PIANO_BASELINE_UNCHANGED']
out={'status':'PASS_DELIVERY_AND_PROTECTION_NOT_POSTURE_PASS','protected_files_checked':len(before),'changed_files':changed,'required_outputs':{n:sha(P/n) for n in required},'fresh_formal_readback':read(P/'FORMAL_ASSET_READBACK_R2.json'),'four_pose_check_fields':'ALL_NOT_RUN','new_static_candidates':0,'new_actions':0,'external_video_observed_timestamps':[],'official_playback_attempts_confirmed_blocked':3,'conditional_outputs_not_generated_reason':'Reference evidence gate not met; no probe executed. Do not create fake blend/result/evidence PNG.','review_ui':ui,'FINAL_STATUS':read(P/'FINAL_STATUS_R2.json')['FINAL_STATUS']}
(P/'DELIVERY_VERIFICATION_R2.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(out['status'],len(before),'UNCHANGED')
