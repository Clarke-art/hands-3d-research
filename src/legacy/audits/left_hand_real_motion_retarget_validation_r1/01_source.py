from pathlib import Path
import json,hashlib,csv,numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[1];SRC=ROOT/'references/piano_motion/pianovam_sample_r1';REC='2024-03-04_03-46-36'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
expected={f'production_spec/{folder}/{name}.blend':s for folder,name,s in [('left_hand_product_baseline_r1','LEFT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1','54307bb199a75a5e684c29d346de9ca6bf2f8e7696911d9d69c57559516ad1a7'),('right_hand_product_baseline_r2','RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R2','c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0'),('right_hand_product_baseline_r1','RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1','4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2')]}
assert all(sha(ROOT/p)==s for p,s in expected.items())
for folder in [SRC,ROOT/'audits/pianovam_retarget_local_axis_mapping_correction_r1',ROOT/'audits/left_hand_canonical_mirror_baseline_r1',ROOT/'audits/left_hand_product_baseline_r1_promotion_r1']:
 for f in folder.rglob('*'):
  if f.is_file():expected[f.relative_to(ROOT).as_posix()]=sha(f)
for f in ROOT.glob('production_spec/*HAND_PRODUCT_BASELINE.json'):expected[f.relative_to(ROOT).as_posix()]=sha(f)
dump('PROTECTED_INPUTS_BEFORE_R1.json',expected)
source=SRC/f'Handskeleton/{REC}.json';data=json.loads(source.read_text());frames=list(range(690,1111));points=np.array([data[str(i)]['Right'] for i in frames],dtype=float)
assert points.shape==(421,21,3) and np.isfinite(points).all()
notes=list(csv.DictReader((SRC/f'Fingering/{REC}.tsv').open(),delimiter='\t'));left=[r for r in notes if r['hand']=='L' and 11.5<=float(r['onset'])<18.5]
np.savez_compressed(P/'physical_left_source_window.npz',native_points=points,source_frames=frames)
dump('LEFT_SOURCE_QUALIFICATION_R1.json',{'LEFT_REAL_MOTION_SOURCE':'VERIFIED','recording':REC,'dataset_version':'PianoVAM v1.2','license':'CC BY-NC-SA 4.0','USAGE_SCOPE':'INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY','source_path':source.relative_to(ROOT).as_posix(),'source_sha256':sha(source),'hand_side':'PHYSICAL_LEFT','original_JSON_field':'Right','label_rule':'This fixed recording has reversed JSON hand labels. Existing video overlays and present inspection of frame780 identify JSON Right on performer physical left. Original data unchanged.','handedness_evidence':'audits/pianovam_single_sample_right_hand_retarget_r1/overlay780.png','source_frame_range':[690,1110],'source_fps':60,'time_range_seconds':[11.5,18.5],'duration_seconds':7,'observations_including_endpoint':421,'landmark_count':21,'missing_observations':0,'finite':True,'same_recording_and_timeline_as_right':True,'MIDI_context':{'present':True,'used_to_generate_motion':False},'fingering_context':{'present':True,'authority':'AUTOMATIC_PREDICTIONS_NOT_MANUAL_GT','left_note_onsets_in_window':len(left),'fingers':sorted(set(r['finger'] for r in left)),'used_to_generate_motion':False},'coordinate_convention':{'x':'image right','y':'image down; multiply1080/1920 for width-normalized aspect','z':'wrist-relative estimated depth, smaller nearer camera; not calibrated metric 3D','camera_handedness':'right-handed x-right/y-down/z-forward','source_motion_limits':'Video-estimated 2.5D landmarks; validation of retarget semantics, not measured anatomical joint angles or metric fingertip contact.'},'motion_mirrored_from_right':False,'sample_or_time_window_changed':False})
print('PHYSICAL_LEFT_SOURCE_VERIFIED',points.shape,'missing=0')
