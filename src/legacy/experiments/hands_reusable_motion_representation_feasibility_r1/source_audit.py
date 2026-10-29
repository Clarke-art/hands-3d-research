"""Read-only temporal source qualification. This is NOT a dynamic candidate.
No extraction, retarget, IK, new Action, saved Blend, or rendering.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from support import *
from persistence import atomic_record,atomic_json
import bpy,numpy as np,math
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(OLD));import performance_core as c
P=read(O/'POLICY.json');I=read(O/'INPUT_BINDINGS.json');man=I['source_scene']
assert sha(O/'POLICY.json')==read(O/'POLICY_LOCK.json')['policy_sha256']
helpers=ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1'
functions_from(helpers/'blender_preflight.py',['digest','native','settime','coords'],globals())
functions_from(ROOT/'experiments/hands_role_aware_collision_avoidance_r1/baseline_blender.py',['degrees'],globals())
functions_from(MODEL/'whole_phrase_model.py',['component_planes'],globals())
rois=read(helpers/'DIGIT_SKIN_ROI.json')
digit_union=set(v for roi in rois.values() for v in roi['vertices'])
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False);assert not bpy.data.libraries
sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
rig=bpy.data.objects[man['mapping']['R']['rig']];mesh=bpy.data.objects[man['mapping']['R']['mesh']]
native_before=digest(native(mesh,rig));assert native_before==I['native_sha256']
groups={k['key_index']:[o for o in sc.objects if o.type=='MESH' and o.get('FROZEN_KEY_INDEX')==k['key_index']] for k in c.KEYS}
components=[];key_geometry_error=0
settime(sc,0.)
for key in c.KEYS:
 assert len(groups[key['key_index']])==len(key['geometry'])
 for g in key['geometry']:
  ob=next(o for o in groups[key['key_index']] if g['name'] in o.name)
  actual=np.array([list(<REDACTED_EMAIL>) for v in ob.data.vertices]);expected=np.array(g['vertices'])
  key_geometry_error=max(key_geometry_error,float(np.max(abs(actual-expected)))*1000)
  components.append((key,g,ob,component_planes(g)))
assert key_geometry_error<.001
def angles():
 ka=np.zeros(88)
 for ki,name in man['key_pivots'].items():ka[int(ki)]=bpy.data.objects[name].rotation_euler.x
 return ka
def roles(t):
 result=[]
 for j,d in enumerate(c.DIGITS):
  ns=[n for n in I['right_events'] if n['finger']==j+1];active=[n for n in ns if n['note_on']<=t<n['note_off']];release=[n for n in ns if n['note_off']<=t<n['note_off']+.04];future=[n for n in ns if t<n['note_on']<=t+.18]
  n=active[-1] if active else release[-1] if release else future[0] if future else None
  role='ACTIVE' if active else 'RELEASING' if release else 'PREPARING' if future else 'IDLE'
  result.append(dict(finger=j+1,digit=d,role=role,event=n['note_id'] if n else None))
 return result
rows=[];VALL=[];Q=[];RW=[];KA=[];contact_records=[];finger_witnesses=[];key_witnesses=[];moving_error=0.
for ix,t0 in enumerate(P['source_audit_times']):
 t=float(t0);settime(sc,t);V,F=coords(mesh);ka=angles();role=roles(t)
 trees={d:BVHTree.FromPolygons([Vector(v) for v in V],rois[d]['faces'],epsilon=0) for d in c.DIGITS}
 pairs={};examples=[]
 for j,d in enumerate(c.DIGITS):
  for e in c.DIGITS[j+1:]:
   overlap=trees[d].overlap(trees[e]);pairs[d+'_'+e]=len(overlap)
   if overlap:
    examples.append(dict(pair=d+'_'+e,count=len(overlap),face_examples=[[rois[d]['faces'][a],rois[e]['faces'][b]] for a,b in overlap[:2]]))
 active=[n for n in I['right_events'] if n['note_on']<=t<n['note_off']];contacts=[]
 for n in active:
  key=c.KEYS[n['key_index']];pv=np.array(key['press_pivot']);pt=V[c.MARKERS['R'][n['finger']-1]['mesh_vertex']];local=c.axisrot(-ka[n['key_index']],key['press_axis'])@(pt-pv)+pv
  s=min(key['key_top_playable_surface'],key=lambda s:np.linalg.norm(local[:2]-np.clip(local[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']])))
  miss=float(np.linalg.norm(local[:2]-np.clip(local[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']]))*1000);gap=float((local[2]-s['z'])*1000)
  r=dict(time=t,event=n['note_id'],finger=n['finger'],note=n['note_name'],horizontal_mm=miss,gap_mm=gap,pass_=miss<=.03 and abs(gap)<=3);contacts.append(r);contact_records.append(r)
 # Previous pressed key ownership lasts only the existing 40ms follow window.
 owned=active+[n for n in I['right_events'] if n['note_off']<=t<n['note_off']+.04]
 hits=[]
 for key,g,ob,planes in components:
  pv=np.array(key['press_pivot']);R=c.axisrot(ka[key['key_index']],key['press_axis']);local=(V-pv)@R+pv;kv=np.array(g['vertices'])
  if np.any(local.max(0)<kv.min(0)) or np.any(local.min(0)>kv.max(0)):continue
  actual=np.array([list(<REDACTED_EMAIL>) for v in ob.data.vertices]);expected=(kv-pv)@R.T+pv
  moving_error=max(moving_error,float(abs(actual-expected).max())*1000)
  depth=-np.max(local@planes[:,:3].T-planes[:,3],axis=1)*1000
  owner={c.DIGITS[n['finger']-1] for n in owned if n['midi_note']==key['midi_note']}
  keytree=BVHTree.FromPolygons([Vector(v) for v in actual],[list(p.vertices) for p in ob.data.polygons],epsilon=0)
  for d in c.DIGITS:
   if d in owner:continue
   ids=np.array(rois[d]['vertices']);positive=ids[depth[ids]>.5];overlap=trees[d].overlap(keytree)
   if len(positive):
    vid=int(positive[np.argmax(depth[positive])]);hits.append(dict(digit=d,key=key['note_name'],key_midi=key['midi_note'],color=key['color'],component=g['name'],vertex=vid,depth_mm=float(depth[vid]),world_m=V[vid].tolist(),skin_key_triangle_pairs=len(overlap),non_owned=True))
  palm=[int(v) for v in np.flatnonzero(depth>.5) if int(v) not in digit_union]
  if palm:
   vid=max(palm,key=lambda v:depth[v]);hits.append(dict(digit='PALM_OR_SHARED_WEB',key=key['note_name'],key_midi=key['midi_note'],color=key['color'],component=g['name'],vertex=vid,depth_mm=float(depth[vid]),world_m=V[vid].tolist(),non_owned=True))
 core=P['source_core_sec'][0]<=t<P['source_core_sec'][1]
 rows.append(dict(time=t,core=core,roles=role,contacts=contacts,finger_skin_pairs=pairs,non_owned_key_hits=hits))
 if core and examples:finger_witnesses.append(dict(time=t,roles=role,examples=examples))
 if core and hits:key_witnesses.append(dict(time=t,roles=role,hits=hits))
 VALL.append(V);Q.append([degrees(d) for d in c.DIGITS]);RW.append(np.array(rig.matrix_world));KA.append(ka)
 if ix%60==0:print('SOURCE_QUALIFICATION',ix,len(P['source_audit_times']),flush=True)
assert digest(native(mesh,rig))==native_before and sha(man['path'])==man['sha256']
core_rows=[r for r in rows if r['core']];source_contacts=[r for r in contact_records if r['event'] in P['source_event_ids']]
contactpass=all(r['pass_'] for r in source_contacts);skinpass=not finger_witnesses;keypass=not key_witnesses
passed=contactpass and skinpass and keypass
summary=[]
for n in I['source']:
 a=[r for r in source_contacts if r['event']==n['note_id']];summary.append(dict(event=n['note_id'],note=n['note_name'],finger=n['finger'],samples=len(a),contact_failures=sum(not r['pass_'] for r in a),horizontal_max_mm=max(r['horizontal_mm'] for r in a),gap_min_mm=min(r['gap_mm'] for r in a),gap_max_mm=max(r['gap_mm'] for r in a)))
atomic_record('SOURCE_AUDIT_SAMPLES.npz',dict(times=P['source_audit_times'],vertices=VALL,qdeg=Q,rig_world=RW,key_angles=KA),dict(record_type='READ_ONLY_SOURCE_QUALIFICATION_SAMPLES_NOT_A_PRIMITIVE',source_sha256=man['sha256'],no_source_save=True))
atomic_json('SOURCE_GEOMETRY_AUDIT.json',dict(rows=rows,source_contacts=summary,core_samples=len(core_rows),total_samples=len(rows),finger_witnesses=finger_witnesses,key_witnesses=key_witnesses,all_ten_digit_pairs_checked=True,real_skin_evaluated=True,real_key_mesh_BVH_checked=True,registered_key_rest_geometry_parity_mm=key_geometry_error,moving_key_geometry_parity_mm=moving_error,native_unchanged=True,source_scene_sha_unchanged=True,scope='Five strong-weight digit skin ROIs plus full hand vertex/key body depth; shared palm/web finger intersection completeness unknown; finite 240Hz not continuous proof'))
atomic_json('SOURCE_QUALIFICATION_GATE.json',dict(SOURCE_QUALIFICATION_GATE='PASS' if passed else 'FAIL',source_contact_pass=contactpass,source_finger_skin_safe=skinpass,source_non_owned_key_safe=keypass,contacts=summary,core_skin_collision_samples=len(finger_witnesses),core_key_intrusion_samples=len(key_witnesses),first_core_skin_collision=finger_witnesses[0]['time'] if finger_witnesses else None,last_core_skin_collision=finger_witnesses[-1]['time'] if finger_witnesses else None,max_core_skin_pairs=max(sum(r['finger_skin_pairs'].values()) for r in core_rows),source_is_approved_clean_primitive=passed,stop_before_extraction=not passed,source_substitution_allowed=False,target_retarget_started=False,local_IK_calls=0,dynamic_candidates=0,interpretation='Donor qualification only; source failure is not a general refutation of motion reuse.'))
protect();print('SOURCE_QUALIFICATION_GATE', 'PASS' if passed else 'FAIL',summary,'skin samples',len(finger_witnesses),'key samples',len(key_witnesses),flush=True)
