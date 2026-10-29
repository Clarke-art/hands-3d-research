from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent; ROOT=P.parents[1]; OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1'; REF=P.parent/'midi_driven_hand_posture_and_contact_refinement_r1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
before=read(REF/'PROTECTED_INPUTS_BEFORE_R1.json')
for p in REF.rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts:before[str(p.resolve())]=sha(p)
assert all(Path(p).exists() and sha(Path(p))==v for p,v in before.items())
dump('PROTECTED_INPUTS_BEFORE_R1.json',before)
sys.path.insert(0,str(OLD));import performance_core as c
import numpy as np
A=np.load(REF/'procedural_motion.npz');E=np.load(REF/'evaluated_candidate.npz');out={}
for s in ['L','R']:
 b=c.RIG[s]['bones'];pad=np.array([c.fk(s,d,np.zeros(4))[0] for d in c.DIGITS]);span=np.linalg.norm(E[s+'_pads'][:,0]-E[s+'_pads'][:,4],axis=1)*1000
 lengths={}
 for j,d in enumerate(c.DIGITS):
  names=c.SETUPS[s,d][0];heads=[np.array(b[n]['head']) for n in names]
  seg=[np.linalg.norm(heads[1]-heads[0]),np.linalg.norm(heads[2]-heads[1]),np.linalg.norm(pad[j]-heads[2])]
  lengths[d]={'proximal_to_pad_polyline_mm':float(sum(seg)*1000),'segments_to_pad_mm':(np.array(seg)*1000).tolist(),'bone_lengths_mm':[b[n]['length']*1000 for n in names]}
 v=np.array(c.RIG[s]['rest_verts']);mask=(v[:,1]>=.045)&(v[:,1]<.105);wrist=v[:,1]<.045
 basegap=np.linalg.norm(np.array(b['THUMB_CMC_'+s]['head'])-np.array(b['LITTLE_MCP_'+s]['head']))*1000
 upper=basegap+lengths['THUMB']['proximal_to_pad_polyline_mm']+lengths['LITTLE']['proximal_to_pad_polyline_mm']
 out[s]={'baseline':c.RIG[s]['baseline'],'baseline_sha256':sha(ROOT/c.RIG[s]['baseline']),'bone_count':c.RIG[s]['bone_count'],'mesh_vertices':len(v),'rest_pad_xyz_mm':(pad*1000).tolist(),'rest_thumb_little_euclidean_mm':float(np.linalg.norm(pad[0]-pad[4])*1000),'rest_thumb_little_x_span_mm':float(abs(pad[0,0]-pad[4,0])*1000),'palm_width_index_little_MCP_euclidean_mm':float(np.linalg.norm(np.array(b['INDEX_MCP_'+s]['head'])-np.array(b['LITTLE_MCP_'+s]['head']))*1000),'coarse_palm_band_x_width_mm':float(np.ptp(v[mask,0])*1000),'palm_band_definition':'canonical rest y in [45,105) mm; includes proximal thumb, not an anatomical segmentation','fingers':lengths,'unrestricted_triangle_inequality_span_upper_bound_mm':float(upper),'upper_bound_warning':'Loose kinematic necessary bound. No joint-limit, common-palm, collision or naturalness guarantee. NOT maximum natural span.','existing_refined_pose_observed_span_mm':[float(span.min()),float(span.max())],'existing_observed_span_warning':'Read-only failed prior candidate; sampled evidence only, not a search or a naturalness witness.','prior_wrist_root_z_range_mm':(np.array([A[s+'_root'][:,2].min(),A[s+'_root'][:,2].max()])*1000).tolist(),'prior_coarse_wrist_mesh_min_z_mm':float(E[s+'_verts'][:,wrist,2].min()*1000),'prior_coarse_palm_mesh_min_z_mm':float(E[s+'_verts'][:,mask,2].min()*1000),'natural_wrist_height_interval':None,'wrist_interval_reason':'No body/forearm model or side-view calibrated performance reference; previous root constraints were numerical policy, not an anatomical range.'}
ks={m:c.KEYS[m-21] for m in [38,50,74,76,78,79,81]}
front=lambda m:ks[m]['key_top_playable_surface'][0]
minimum=(front(50)['xmin']-front(38)['xmax'])*1000
keydata={str(m):{'note':k['note_name'],'center_x_mm':k['key_center'][0]*1000,'playable_surfaces_mm':[{a:v*1000 for a,v in r.items()} for r in k['key_top_playable_surface']],'press_angle_rad':k['press_angle_rad']} for m,k in ks.items()}
contacts=read(REF/'KEY_CONTACT_R1.json')
report={'PHASE':'PIANO_HAND_POSTURE_REFERENCE_AND_STATIC_FEASIBILITY_R1','units':'mm derived from frozen equivalent-scale metres; no physical keyboard calibration claim','keyboard_metres_per_native_unit':read(OLD/'KEYBOARD_COORDINATE_FRAME_R1.json')['metres_per_native_unit'],'formal_hands':out,'keyboard':keydata,'left_octave':{'center_to_center_x_mm':(ks[50]['key_center'][0]-ks[38]['key_center'][0])*1000,'minimum_front_region_point_to_point_distance_mm':minimum,'minimum_warning':'Pads treated as points at inner edges; realistic pad area and edge safety require more. Not a target prescription.','natural_common_palm_feasibility':'UNPROVEN','hard_geometric_impossibility_proven':False,'reason':'Rest shape and loose upper bound bracket the task; old poses touch separately but collide. No collision-free, natural common-palm witness.'},'right_five_finger':{'D5_A5_center_x_span_mm':(ks[81]['key_center'][0]-ks[74]['key_center'][0])*1000,'Fsharp5_black_top_height_mm':front(78)['z']*1000,'Fsharp5_black_front_y_mm':front(78)['ymin']*1000,'natural_common_palm_feasibility':'UNPROVEN','reason':'Different digit lengths and raised/rearward F# surface require coordinated common-palm setup; per-note reach is not simultaneous five-finger proof.'},'existing_refined_contact_summary':contacts['summary'],'measurement_limits':['No optimizer, parameter sweep, new pose candidate or Action generated.','No natural joint ranges inferred from photographs.','Prior contact is marker-based; prior collision is vertex-volume screen, not exhaustive triangle collision.','Reachable-set upper bound does not establish attainability.','Rest pad positions derive from unchanged distal markers and formal rest bone frames; mesh parity independently verified.'],'formal_asset_change_required':'NOT_ESTABLISHED','static_probe_gate':'REFERENCE_EVIDENCE_INSUFFICIENT'}
dump('HAND_KEYBOARD_SPAN_FEASIBILITY_R1.json',report)
print(json.dumps({'hands':{s:{k:v for k,v in out[s].items() if k in ['rest_thumb_little_euclidean_mm','rest_thumb_little_x_span_mm','palm_width_index_little_MCP_euclidean_mm','unrestricted_triangle_inequality_span_upper_bound_mm','existing_refined_pose_observed_span_mm','prior_wrist_root_z_range_mm']} for s in out},'left':report['left_octave'],'right':report['right_five_finger'],'protected':len(before)},indent=2))
