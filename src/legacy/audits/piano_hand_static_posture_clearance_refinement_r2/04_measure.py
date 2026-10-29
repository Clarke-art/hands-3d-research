import sys,json,hashlib,math
sys.dont_write_bytecode=True
from pathlib import Path
P=Path(__file__).resolve().parent;R1=P.parent/'piano_hand_four_pose_static_feasibility_r1';OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1';sys.path.insert(0,str(OLD/'_deps'))
import numpy as np
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
keys=read(OLD/'KEYBOARD_88_KEY_TABLE_R1.json')['keys'];sol=read(P/'SOLVED_STATIC_POSES_R2.json');policy=read(P/'STATIC_REFINEMENT_POLICY_R2.json');man=read(P/'STATIC_SCENE_MANIFEST_R2.json');data=read(R1/'FORMAL_INPUT_EXTRACTION_R1.json');A=np.load(P/'evaluated_static_candidate.npz');assert sha(P/'STATIC_POSTURE_REFINED_CANDIDATE_R2.blend')==man['candidate_sha256']
def measurement(pt,key):
 surfaces=key['key_top_playable_surface'];ds=[math.hypot(max(s['xmin']-pt[0],0,pt[0]-s['xmax']),max(s['ymin']-pt[1],0,pt[1]-s['ymax'])) for s in surfaces];j=int(np.argmin(ds));s=surfaces[j];inside=ds[j]<1e-8;gap=float(pt[2]-s['z'])*1000;h=ds[j]*1000
 return {'xyz_mm':(np.array(pt)*1000).tolist(),'midi':key['midi_note'],'note':key['note_name'],'vertical_gap_mm':gap,'horizontal_error_mm':h,'inside_actual_playable_region':inside,'contact_pass':bool(inside and abs(gap)<=3 and h<=2)}
surfrows=np.array([[s[n] for n in ['xmin','xmax','ymin','ymax','z']] for k in keys for s in k['key_top_playable_surface']])
def heights(V):
 mask=(V[:,None,0]>=surfrows[:,0])&(V[:,None,0]<=surfrows[:,1])&(V[:,None,1]>=surfrows[:,2])&(V[:,None,1]<=surfrows[:,3]);z=np.max(np.where(mask,surfrows[:,4],-1e6),axis=1);return z
def min_over(V,ids):
 zz=heights(V[ids]);valid=zz>-1e5
 return {'vertices_over_actual_key_surface':int(valid.sum()),'min_vertical_surface_gap_mm':float(np.min((V[ids,2]-zz)[valid])*1000) if valid.any() else None,'no_projected_overlap_with_key_top':not bool(valid.any())}
measure={};clearances={}
for pose,row in sol['poses'].items():
 s=row['hand'];task=row['task'];V=A[pose+'_verts'];pads=A[pose+'_pads'];skin=A[pose+'_skin_pads'];rest=np.array(data[s]['rest_vertices_canonical']);W=np.array(data[s]['weights']);names=data[s]['bone_names'];palm=np.flatnonzero((rest[:,1]>=.045)&(rest[:,1]<.105));wrist=np.flatnonzero(rest[:,1]<.045)
 fingers=[np.flatnonzero(W[:,[i for i,n in enumerate(names) if n.startswith(d+'_')]].sum(1)>.65) for d in ['THUMB','INDEX','MIDDLE','RING','LITTLE']]
 hit=np.zeros(len(V),bool);hitrows=[]
 for key in keys:
  mask=np.zeros(len(V),bool);maxdepth=0
  for g in key['geometry']:
   pts=np.array(g['vertices']);lo=pts.min(0);hi=pts.max(0);inside=np.all(V>=lo-1e-8,axis=1)&np.all(V<=hi+1e-8,axis=1);deep=inside&(V[:,2]<hi[2]-.003);mask|=deep
   if deep.any():maxdepth=max(maxdepth,float(np.max(hi[2]-V[deep,2])*1000))
  if mask.any():hitrows.append({'midi':key['midi_note'],'note':key['note_name'],'vertices':int(mask.sum()),'max_depth_mm':maxdepth,'palm_vertices':int(mask[palm].sum()),'wrist_vertices':int(mask[wrist].sum()),'digit_vertex_counts':[int(mask[ids].sum()) for ids in fingers],'vertex_indices':np.flatnonzero(mask).tolist()})
  hit|=mask
 active=task['active_finger'];active_m=None
 if active is not None:
  key=keys[task['active_midi']-21];active_m={'finger':active,'fixed_pad':measurement(pads[active-1],key),'skin_pad':measurement(skin[active-1],key)}
 prep=[]
 for finger,midi in task['prepared'].items():
  j=int(finger)-1;m=measurement(pads[j],keys[midi-21]);m['finger']=j+1;m['prepared_gap_in_policy_interval']=bool(m['inside_actual_playable_region'] and 4<=m['vertical_gap_mm']<=18);m['skin_pad']=measurement(skin[j],keys[midi-21]);prep.append(m)
 wrong=[]
 for j in range(5):
  expected=task.get('active_midi') if active==j+1 else task['prepared'].get(str(j+1))
  for key in keys:
   if key['midi_note']==expected:continue
   m=measurement(pads[j],key)
   if m['contact_pass']:wrong.append({'finger':j+1,'unexpected_key':key['note_name'],'midi':key['midi_note'],'gap_mm':m['vertical_gap_mm']})
 idle=[j for j in range(5) if active!=j+1];boundsok=row['bounded'];skincontactok=active_m is None or active_m['skin_pad']['contact_pass'];fixedcontactok=active_m is None or active_m['fixed_pad']['contact_pass'];prepareok=all(x['prepared_gap_in_policy_interval'] for x in prep)
 clearances[pose]={'screen_type':'Evaluated full 3300-vertex inclusion in every frozen rectangular key piece at >3mm depth, plus surface-projection distances; not exhaustive triangle collision. Normal side visual review required.','palm_region':'canonical rest y [45,105)mm; engineering band, not anatomical segmentation','wrist_region':'canonical rest y <45mm','palm':min_over(V,palm),'wrist':min_over(V,wrist),'mesh_deep_key_vertices':int(hit.sum()),'palm_deep_key_vertices':int(hit[palm].sum()),'wrist_deep_key_vertices':int(hit[wrist].sum()),'per_digit_deep_key_vertices':[int(hit[ids].sum()) for ids in fingers],'idle_digit_deep_key_vertices':sum(int(hit[fingers[j]].sum()) for j in idle),'key_intersections':hitrows,'unexpected_fixed_pad_contacts':wrong,'idle_digit_surface_gaps':[{'finger':j+1,**min_over(V,fingers[j])} for j in idle],'machine_clearance_screen_pass':not bool(hit.any()) and not wrong}
 measure[pose]={'execution':'GENERATED_SAVED_REOPENED','STATIC_GEOMETRIC_FEASIBILITY':'PASS_SCREEN' if fixedcontactok and skincontactok and prepareok and not hit.any() and not wrong else 'FAIL_SCREEN','active_contact':active_m,'prepared_fingers':prep,'all_required_fixed_pad_contacts_pass':fixedcontactok,'all_required_skin_pad_contacts_pass':skincontactok,'all_prepared_regions_and_gaps_pass':prepareok,'joint_policy_bounds_pass':boundsok,'joint_increments_deg':row['joint_increments_deg'],'root_xyz_mm':(np.array(row['root_xyz_m'])*1000).tolist(),'root_yaw_pitch_roll_deg':row['root_yaw_pitch_roll_deg'],'actual_pad_span_thumb_little_mm':float(np.linalg.norm(pads[0]-pads[4])*1000),'pad_skin_drift_mm':man['readback'][pose]['skin_rigid_pad_drift_mm'],'HUMAN_VISIBLE_NATURALNESS':'PENDING_AGENT_VIEW_REVIEW','classification':'PENDING_VISUAL_REVIEW','continuous_transition_proven':False}
dump('STATIC_GEOMETRIC_MEASUREMENTS_R2.json',measure);dump('HAND_KEYBOARD_CLEARANCE_R2.json',{'poses':clearances,'key_table_sha256':sha(OLD/'KEYBOARD_88_KEY_TABLE_R1.json'),'tolerances_unchanged':{'vertical_mm':3,'horizontal_mm':2,'strict_inside':True},'screen_is_not_human_approval':True})
left1=sol['poses']['L1'];left2=sol['poses']['L2'];R1=np.array(left1['root_rotation_matrix']);R2=np.array(left2['root_rotation_matrix']);deltaR=float(np.degrees(np.arccos(np.clip((np.trace(R1.T@R2)-1)/2,-1,1))))
dump('LEFT_OCTAVE_REFINEMENT_R2.json',{'poses':['L1','L2'],'shared_root_enforced_before_solve':True,'root_position_delta_mm':float(np.linalg.norm(np.array(left1['root_xyz_m'])-left2['root_xyz_m'])*1000),'root_orientation_delta_deg':deltaR,'actual_pad_span_mm':{p:measure[p]['actual_pad_span_thumb_little_mm'] for p in ['L1','L2']},'thumb_little_contact_and_prepared':{p:{'active':measure[p]['active_contact'],'prepared':measure[p]['prepared_fingers']} for p in ['L1','L2']},'idle_index_middle_ring_joint_delta_deg':(np.array(left2['joint_increments_deg'])[1:4]-np.array(left1['joint_increments_deg'])[1:4]).tolist(),'per_digit_max_joint_delta_deg':np.max(np.abs(np.array(left2['joint_increments_deg'])-np.array(left1['joint_increments_deg'])),axis=1).tolist(),'same_reasonable_octave_configuration':'PENDING_VISUAL_REVIEW','sequence_feasibility':'UNPROVEN','no_large_root_transport_used':True,'solver_bound_saturation':['L shared root z at70mm and roll at-6deg','L1 little MCP increment at32deg','L2 thumb MCP/IP increments at25/18deg'],'bound_saturation_meaning':'Engineering-policy conflict indicator, not physiological maximum span or impossible hand geometry.'})
dump('RIGHT_NEIGHBOR_KEY_CLEARANCE_R2.json',{'finger_mapping_design_provisional':{'1':'D5','2':'E5','3':'F#5','4':'G5','5':'A5'},'black_height_above_white_mm':15.44418011715685,'black_front_offset_mm':49.42137705420048,'frozen_geometry_source':str(OLD/'KEYBOARD_88_KEY_TABLE_R1.json'),'root_position_delta_mm':float(np.linalg.norm(np.array(sol['poses']['R1']['root_xyz_m'])-sol['poses']['R2']['root_xyz_m'])*1000),'root_orientation_same':bool(np.array_equal(sol['poses']['R1']['root_rotation_matrix'],sol['poses']['R2']['root_rotation_matrix'])),'middle_joint_increments_deg':{p:sol['poses'][p]['joint_increments_deg'][2] for p in ['R1','R2']},'R1_middle_prepare':next(x for x in measure['R1']['prepared_fingers'] if x['finger']==3),'R2_middle_contact':measure['R2']['active_contact'],'other_four_digit_joint_delta_deg':(np.array(sol['poses']['R2']['joint_increments_deg'])[[0,1,3,4]]-np.array(sol['poses']['R1']['joint_increments_deg'])[[0,1,3,4]]).tolist(),'geometry_contact_pass':measure['R2']['all_required_fixed_pad_contacts_pass'] and measure['R2']['all_required_skin_pad_contacts_pass'],'naturalness':'PENDING_VISUAL_REVIEW','transition_proven':False})
print(json.dumps({p:{'geometry':o['STATIC_GEOMETRIC_FEASIBILITY'],'active':o['active_contact'],'prepared_pass':o['all_prepared_regions_and_gaps_pass'],'clearance':{k:clearances[p][k] for k in ['mesh_deep_key_vertices','palm_deep_key_vertices','wrist_deep_key_vertices','per_digit_deep_key_vertices']}} for p,o in measure.items()},indent=2))

