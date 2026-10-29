"""Correct bound bookkeeping and attach whole-context details; no new search."""
import sys,json,time,hashlib,itertools
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;ROOT=O.parents[1]
sys.path.insert(0,str(ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1/_deps'))
import numpy as np
START=time.perf_counter()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
protection=read(O/'SOURCE_SHA_CHECK.json');before=protection['before']
extra=[ROOT/'AGENTS.md',ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance/APPROVED_MOTION_PARITY.json',
 ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance/FROZEN_ASSET_PROTECTION.json',
 ROOT/'audits/piano_hands_product_route_reassessment_r1/TECHNICAL_ROUTE_COMPARISON.md']
for p in extra:before[str(p)]=sha(p)
ref=dict(np.load(ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance/R_approved_reference.npz'))
D=dict(np.load(ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning/SOURCE_MODEL.npz'))
M=read(ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning/SOURCE_MODEL_MANIFEST.json')
keys=read(ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1/KEYBOARD_88_KEY_TABLE_R1.json')['keys']
mark=read(ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1/FINGERTIP_CONTACT_MARKERS_R1.json')['markers']['R']
shape=np.load(ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning/SHAPE_DELTA.npz')['delta']
weight=D['weights']/np.maximum(D['weights'].sum(1,keepdims=True),1e-12)
restpoints=np.c_[D['rest_vertices'],np.ones(len(weight))]@D['mesh_to_rig'].T
shapepoints=np.c_[shape,np.zeros(len(weight))]@D['mesh_to_rig'].T
BN={n:i for i,n in enumerate(M['bones'])};rests=D['rest_matrices'].astype(float)
rel=np.array([np.linalg.inv(rests[p])@r if p>=0 else r for p,r in zip(D['parents'],rests)])
ev=read(O/'EVENT_VERIFICATION.json');notes=sorted([n for n in ev['notes'] if n['hand']=='R'],key=lambda n:n['on_tick']);by={n['note_id']:n for n in notes}
times=ref['music_times']+ev['presentation_shift_sec'];digits=['THUMB','INDEX','MIDDLE','RING','LITTLE']
def poses(ix):
 out=[]
 for b,p in enumerate(D['parents']):
  mat=rel[b]@ref['joint_basis'][ix,b]
  if p>=0:mat=out[p]@mat
  out.append(mat)
 return np.array(out)
def rx(a):
 return np.array([[1,0,0],[0,np.cos(a),-np.sin(a)],[0,np.sin(a),np.cos(a)]])
geo=read(O/'STATIC_RIG_PROBES.json');comparison=read(O/'CANDIDATE_COMPARISON.json')
# Preserve the actual initial machine output; correcting the formula to the
# prelocked uniform-tolerance bound does not change samples, candidates or rank.
for name in ['STATIC_RIG_PROBES','CANDIDATE_COMPARISON']:
 if not (O/(name+'_PRE_BOUND_CORRECTION.json')).exists():
  (O/(name+'_PRE_BOUND_CORRECTION.json')).write_bytes((O/(name+'.json')).read_bytes())
for g in geo['rows']:
 ix=int(np.argmin(abs(times-g['requested_time_sec'])));ps=poses(ix);world=ref['rig_world'][ix]
 j=g['finger']-1;d=digits[j];names=[f'{d}_{k}_R' for k in (['CMC','MCP','IP'] if j==0 else ['MCP','PIP','DIP'])]
 center=(world@np.r_[ps[BN[names[0]],:3,3],1])[:3];key=keys[by[g['event']]['key_index']]
 angle=ref['key_angles'][ix,key['key_index']];pv=np.array(key['press_pivot']);p=rx(-angle)@(center-pv)+pv
 distance=min(np.linalg.norm(p-np.r_[np.clip(p[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']]),s['z']]) for s in key['key_top_playable_surface'])
 radius=g['fixed_root_virtual_marker_radius_mm']/1000
 g['necessary_virtual_marker_extra_root_mm']=max(0,float(distance-radius-.003001))*1000
 g['virtual_marker_surface_center_distance_mm']=float(distance*1000)
 g['virtual_marker_center_world_m']=center
 g['bound_scope']='Rigid virtual marker, fixed C1 orientation and all upstream state; uniform3.001mm conservative tolerance. Skin blend reach and root rotation require separate reasoning.'
 # A separate conservative bound applies to the ACTUAL weighted skin vertex.
 # Each influenced point is within its bone-chain length + local offset from
 # the fixed MCP. Triangle inequality then bounds the weighted mixture; all
 # thumb corrective coefficients lie within [0,1], so include their full norm.
 vertex=mark[j]['mesh_vertex'];center_native=ps[BN[names[0]],:3,3];skin_radius=0.
 for bone,bname in enumerate(M['bones']):
  w=weight[vertex,bone]
  if w<=0:continue
  local=np.linalg.inv(rests[bone])@restpoints[vertex]
  shlocal=np.linalg.inv(rests[bone])@shapepoints[vertex]
  if bname.startswith(d+'_'):
   length=0.;ancestor=bone
   while ancestor!=BN[names[0]]:
    length+=np.linalg.norm(rel[ancestor,:3,3]);ancestor=int(D['parents'][ancestor]);assert ancestor>=0
   reach=length+np.linalg.norm(local[:3])
  else:
   reach=np.linalg.norm((ps[bone]@local)[:3]-center_native)
  skin_radius+=w*(reach+np.linalg.norm(shlocal[:3]))
 skin_radius*=np.linalg.svd(world[:3,:3],compute_uv=False).max()
 # Float rest matrices can differ infinitesimally from rigid rotations.
 skin_radius+=.00001
 g['actual_skin_marker_conservative_radius_mm']=float(skin_radius*1000)
 g['necessary_actual_skin_marker_center_change_mm']=max(0,float(distance-skin_radius-.003001))*1000
 g['actual_skin_bound_scope']='Frozen weighted marker vertex with full corrective displacement allowance and0.01mm rest roundoff allowance; fixed upstream C1 state. Rotation/translation coordination not tested.'
for s in comparison['summaries']:
 selected=[g for g in geo['rows'] if g['finger']==s['fingers'][next(i for i,n in enumerate(notes) if n['note_id']==g['event'])]]
 s['changed_static_probe_rows']=[g for g in selected if g['event'] in s['changed_event_ids']]
 s['max_necessary_virtual_marker_extra_root_mm']=max(g['necessary_virtual_marker_extra_root_mm'] for g in selected)
 s['max_necessary_actual_skin_marker_center_change_mm']=max(g['necessary_actual_skin_marker_center_change_mm'] for g in selected)
 s['movement_time_for_B02_fingers']=[r for r in s['samefinger_reuse'] if r['ids'][-1] in ['R10','R11','R12']]
 s['kinematic_finger_order_at_B02']=[]
 for a,b in zip(notes,notes[1:]):
  if b['note_id'] not in ['R09','R10','R11','R12','R13','R14']:continue
  ix=int(np.argmin(abs(times-b['note_on'])));ps=poses(ix);world=ref['rig_world'][ix]
  i,j=s['fingers'][notes.index(a)]-1,s['fingers'][notes.index(b)]-1
  def center(j):
   d=digits[j];name=f'{d}_{"CMC" if j==0 else "MCP"}_R'
   return (world@np.r_[ps[BN[name],:3,3],1])[:3]
  mcp_gap=(center(j)-center(i))[0]*1000
  target_gap=(keys[b['key_index']]['key_center'][0]-keys[a['key_index']]['key_center'][0])*1000
  s['kinematic_finger_order_at_B02'].append(dict(ids=[a['note_id'],b['note_id']],fingers=[i+1,j+1],
   frozen_mcp_lateral_gap_mm=float(mcp_gap),target_key_lateral_gap_mm=float(target_gap),
   opposing_order=bool(mcp_gap*target_gap<0),meaning='Necessary endpoint layout/reconfiguration risk; sequential contacts allow reposition, not a collision proof'))
dump('STATIC_RIG_PROBES.json',geo);dump('CANDIDATE_COMPARISON.json',comparison)
past=read(O/'CORRECTION_LOG.json') if (O/'CORRECTION_LOG.json').exists() else None
elapsed=time.perf_counter()-START
dump('CORRECTION_LOG.json',dict(reason='Uniform3mm Euclidean reach tolerance was prelocked; initial implementation used vertical-only tolerance. Corrected to conservative3.001mm allowance; additionally derived actual weighted-skin marker reach bound without sampling or optimization.',
 only_bound_bookkeeping_changed=True,new_candidates=0,new_searches=0,new_static_sample_searches=0,initial_outputs_retained=True,
 corrected_maxima=[dict(id=s['id'],mm=s['max_necessary_virtual_marker_extra_root_mm'],actual_skin_mm=s['max_necessary_actual_skin_marker_center_change_mm']) for s in comparison['summaries']],
 seconds=elapsed,cumulative_details_seconds=elapsed+(past.get('cumulative_details_seconds',past['seconds']) if past else 0)))
dump('HISTORICAL_PROTECTION_NOTE.json',dict(C1_historical_protection=read(extra[2]),
 concurrent_FAIL='Retained as documented in prior route reassessment; not superseded by current narrow SHA checks',
 all_old_manifest_paths_are_text_only=True,no_full_directory_audit=True))
after={p:sha(p) for p in before};mismatches=[p for p in before if before[p]!=after[p]]
protection.update(before=before,after=after,mismatches=mismatches,unchanged=not mismatches)
dump('SOURCE_SHA_CHECK.json',protection);assert not mismatches
print(json.dumps(dict(maxima=[(s['id'],s['max_necessary_virtual_marker_extra_root_mm']) for s in comparison['summaries']],
 orders=[dict(id=s['id'],rows=s['kinematic_finger_order_at_B02']) for s in comparison['summaries']],hash_count=len(before)),ensure_ascii=False))
