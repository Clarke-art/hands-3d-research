from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[1];OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1';PRE=P.parent/'piano_keyboard_spatial_anchor_and_contact_validation_r1'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=read(P/'PROTECTED_INPUTS_BEFORE_R1.json');changed=[p for p,v in before.items() if not Path(p).is_file() or sha(Path(p))!=v];assert not changed,changed
required=['PIANO_HAND_POSTURE_REFERENCE_AND_STATIC_FEASIBILITY_R1_REPORT.md','review.html','REAL_PIANO_REFERENCE_MANIFEST_R1.md','HAND_KEYBOARD_SPAN_FEASIBILITY_R1.json','NATURAL_PIANO_HAND_POSTURE_CONTRACT_R1.md','EVIDENCE_LEFT_OCTAVE_POSTURE_R1.png','EVIDENCE_RIGHT_FIVE_FINGER_POSTURE_R1.png','NEXT_MOTION_ENGINE_REQUIREMENTS_R1.md','FINAL_ASSET_PROTECTION_R1.json']
assert all((P/n).stat().st_size>0 for n in required)
assert not list(P.glob('*.blend*')) and not list(P.glob('*.npz'))
assert read(P/'REVIEW_UI_VALIDATION_R1.json')['status']=='PASS'
authority=read(OLD/'KEYBOARD_AUTHORITY_R1.json')
assert sha(Path(authority['source_manifest']))==authority['KEYBOARD_SOURCE_SHA256']
assert sha(Path(authority['runtime']))==authority['runtime_sha256']
assert read(OLD/'KEYBOARD_88_KEY_TABLE_R1.json')==read(PRE/'KEYBOARD_88_KEY_TABLE_R1.json')
keys=read(OLD/'KEYBOARD_88_KEY_TABLE_R1.json')['keys'];assert len(keys)==88 and [k['midi_note'] for k in keys]==list(range(21,109))
report={'status':'PASS_DELIVERY_AND_PROTECTION_NOT_POSTURE_PASS','protected_files_checked':len(before),'changed_files':changed,'new_static_candidate_count':0,'reason_no_blend':'Reference-evidence gate did not pass; user made static probe conditional.','keyboard_source_manifest_current_sha256':sha(Path(authority['source_manifest'])),'keyboard_runtime_current_sha256':sha(Path(authority['runtime'])),'key_table_matches_spatial_audit':True,'key_count':88,'readback':read(P/'FORMAL_ASSET_READBACK_R1.json'),'ui':read(P/'REVIEW_UI_VALIDATION_R1.json'),'required_outputs':{n:sha(P/n) for n in required},'final_status':read(P/'FINAL_STATUS_R1.json')['FINAL_STATUS']}
(P/'DELIVERY_VERIFICATION_R1.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8');print(report['status'],len(before),'UNCHANGED')
