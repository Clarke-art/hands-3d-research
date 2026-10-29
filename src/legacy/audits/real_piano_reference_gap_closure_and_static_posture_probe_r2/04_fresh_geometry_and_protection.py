import sys,json,hashlib,ast,importlib.util
sys.dont_write_bytecode=True
from pathlib import Path
import bpy,numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[1];OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1';R1=P.parent/'piano_hand_posture_reference_and_static_feasibility_r1'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
before=read(R1/'PROTECTED_INPUTS_BEFORE_R1.json')
for p in R1.rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts:before[str(p.resolve())]=sha(p)
drift=[p for p,v in before.items() if not Path(p).is_file() or sha(Path(p))!=v]
assert not drift,drift
dump('PROTECTED_INPUTS_BEFORE_R2.json',before)
R=read(OLD/'RIG_CANONICAL_PROBE_R1.json');markers=read(OLD/'FINGERTIP_CONTACT_MARKERS_R1.json')['markers']
sp=importlib.util.spec_from_file_location('identity',ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h)
tree=ast.parse((P.parent/'piano_keyboard_spatial_anchor_and_contact_validation_r1/04_hands.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='intrinsic'],type_ignores=[]),'intrinsic','exec'))
out={}
for s,c in R.items():
 source=ROOT/c['baseline'];assert sha(source)==c['baseline_sha256']
 bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);rig=bpy.data.objects[c['rig']];ob=bpy.data.objects[c['mesh']];h.neutral(rig);rig.animation_data_clear()
 V,_=h.coords(ob);C=np.array(c['native_to_canonical']);actual=V@C[:3,:3].T+C[:3,3];delta=float(np.max(np.linalg.norm(actual-np.array(c['rest_verts']),axis=1))*1000)
 identity=hashlib.sha256(json.dumps(intrinsic(ob,rig),sort_keys=True,separators=(',',':')).encode()).hexdigest()
 pads=[]
 for row in markers[s]:
  bone=rig.pose.bones[row['distal_frame']];point=<REDACTED_EMAIL>@__import__('mathutils').Vector(row['local_pad_point']);v=C@np.r_[point,1];pads.append(v[:3])
 pads=np.array(pads)
 out[s]={'path':str(source),'baseline_sha256':sha(source),'fresh_vertex_count':len(V),'fresh_bone_count':len(rig.data.bones),'canonical_mesh_max_delta_mm':delta,'intrinsic_identity_matches':identity==c['static_identity'],'fresh_rest_pad_xyz_mm':(pads*1000).tolist(),'rest_thumb_little_space_distance_mm':float(np.linalg.norm(pads[0]-pads[4])*1000),'rest_thumb_little_x_projection_mm':float(abs(pads[0,0]-pads[4,0])*1000),'saved_any_blend':False}
 assert delta<.001 and identity==c['static_identity']
dump('FORMAL_ASSET_READBACK_R2.json',out)
keys=read(OLD/'KEYBOARD_88_KEY_TABLE_R1.json')['keys'];assert len(keys)==88 and [k['midi_note'] for k in keys]==list(range(21,109))
authority=read(OLD/'KEYBOARD_AUTHORITY_R1.json')
assert sha(Path(authority['source_manifest']))==authority['KEYBOARD_SOURCE_SHA256']
assert sha(Path(authority['runtime']))==authority['runtime_sha256']
ks={m:keys[m-21] for m in [38,50,74,76,78,79,81]}
keyboard={str(m):{'note':k['note_name'],'center_x_mm':k['key_center'][0]*1000,'playable_surfaces_mm':[{a:v*1000 for a,v in r.items()} for r in k['key_top_playable_surface']]} for m,k in ks.items()}
poses={n:{'task':task,'execution':'NOT_RUN','ACTIVE_FINGER_CONTACT':'NOT_RUN','IDLE_FINGER_POSTURE':'NOT_RUN','PALM_CLEARANCE':'NOT_RUN','WRIST_CLEARANCE':'NOT_RUN','NEIGHBOR_KEY_INTERFERENCE':'NOT_RUN','JOINT_POSTURE':'NOT_RUN','naturalness':'NOT_RUN'} for n,task in [('L1','L5 D2 contact; L1 D3 preparation; middle three relaxed'),('L2','L1 D3 contact; L5 D2 preparation; middle three relaxed'),('R1','D5/E5/F#5/G5/A5 preparation; no mandatory simultaneous contact'),('R2','R3 F#5 contact; other digits prepared/relaxed; shared palm')]}
dump('HAND_KEYBOARD_STATIC_FEASIBILITY_R2.json',{'phase':P.name.upper(),'status':'REFERENCE_EVIDENCE_INSUFFICIENT','units':'project equivalent-scale mm; not manufacturer-calibrated','fresh_formal_readback':out,'keyboard_authority':authority,'key_table_sha256':sha(OLD/'KEYBOARD_88_KEY_TABLE_R1.json'),'keyboard':keyboard,'geometry':{'left_octave_centers_mm':(ks[50]['key_center'][0]-ks[38]['key_center'][0])*1000,'left_front_inner_edges_point_minimum_mm':(ks[50]['key_top_playable_surface'][0]['xmin']-ks[38]['key_top_playable_surface'][0]['xmax'])*1000,'right_D5_A5_centers_mm':(ks[81]['key_center'][0]-ks[74]['key_center'][0])*1000,'Fsharp5_height_above_white_mm':(ks[78]['key_top_playable_surface'][0]['z']-ks[74]['key_top_playable_surface'][0]['z'])*1000,'Fsharp5_front_offset_from_white_mm':(ks[78]['key_top_playable_surface'][0]['ymin']-ks[74]['key_top_playable_surface'][0]['ymin'])*1000},'tolerances':{'vertical_mm':3,'horizontal_mm':2,'actual_playable_region_required':True,'unchanged':True},'poses':poses,'candidate_count':0,'static_probe':'NOT_RUN','gate':{'left_octave_reference':'PARTIAL_STATIC','right_black_key_visual_reference':'UNVERIFIED','video_timestamps_observed':[],'reason':'No actually viewable black-key five-finger demonstration in the bounded source check. Not a demand for exact performer, exact repertoire, exact 3D angles, or proven dynamic transitions.'},'classifications':{'REFERENCE_EVIDENCE_LIMIT':'BLOCKING','GEOMETRY_LIMIT':'NOT_ESTABLISHED','POSTURE_CONSTRAINT_LIMIT':'NOT_TESTED','IK_SOLVER_FAILURE':'NOT_RUN'},'L1_L2_root_delta_mm':None,'R1_R2_root_delta_mm':None,'natural_common_palm_feasibility':'UNKNOWN','maximum_natural_hand_span':'UNKNOWN','formal_mesh_or_rig_change_required_evidence':False,'dynamic_transition_proven':False})
print(json.dumps({'protected_count':len(before),'readback':{s:{k:v for k,v in o.items() if k in ['fresh_vertex_count','fresh_bone_count','canonical_mesh_max_delta_mm','intrinsic_identity_matches','rest_thumb_little_space_distance_mm']} for s,o in out.items()}},indent=2))
