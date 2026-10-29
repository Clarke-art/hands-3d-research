"""Finite static native-Blender diagnosis, original C1 versus SAME initial seed.
No terminal solver state exists; no saved Blend/Action or trajectory is made.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from support import *
import bpy,numpy as np,math
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(OLD))
import performance_core as c
I=read(O/'INPUT_BINDINGS.json');P=read(O/'POLICY.json');man=I['source_scene']
helpers=ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1'
functions_from(helpers/'blender_preflight.py',['digest','native','settime','coords'],globals())
functions_from(MODEL/'whole_phrase_model.py',['component_planes'],globals())
rois=read(helpers/'DIGIT_SKIN_ROI.json')
PLANES={(k['key_index'],j):component_planes(g) for k in c.KEYS for j,g in enumerate(k['geometry'])}
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False)
sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
assert not bpy.data.libraries,'EXTERNAL_LINKED_LIBRARY_FORBIDDEN'
for image in bpy.data.images:
 assert '/3d interactive components/piano' not in image.filepath.replace('\\','/').lower(),'EXCLUDED_EXTERNAL_IMAGE_REFERENCE'
rig=bpy.data.objects[man['mapping']['R']['rig']];mesh=bpy.data.objects[man['mapping']['R']['mesh']];rt=bpy.data.objects[man['mapping']['R']['root']]
left=bpy.data.objects[man['mapping']['L']['rig']]
native_before=digest(native(mesh,rig));assert native_before==I['native_sha256']
def payload(a):
 return [(f.data_path,f.array_index,[(list(k.co),k.interpolation,list(k.handle_left),list(k.handle_right)) for k in f.keyframe_points]) for layer in a.layers for strip in layer.strips for bag in strip.channelbags for f in bag.fcurves]
key_before={ki:digest(payload(bpy.data.objects[name].animation_data.action)) for ki,name in man['key_pivots'].items()}
A=dict(np.load(O/'INITIAL_SEED_LAYOUTS.npz'));rows=[];source=[];roots=[];allpairs=[];timedata=[]
def angles():
 ans=np.zeros(88)
 for ki,name in man['key_pivots'].items():ans[int(ki)]=bpy.data.objects[name].rotation_euler.x
 return ans
def measure(V,t,events):
 ang=angles();trees={d:BVHTree.FromPolygons([Vector(v) for v in V],rois[d]['faces'],epsilon=0) for d in c.DIGITS}
 pairs={a+'_'+b:len(trees[a].overlap(trees[b])) for j,a in enumerate(c.DIGITS) for b in c.DIGITS[j+1:]}
 owned=[n for n in events if n['note_on']-1e-9<=t<n['note_off']+.04-1e-9]
 contact=[];footprints=[]
 for n in owned:
  j=n['finger']-1;key=c.KEYS[n['key_index']];pv=np.array(key['press_pivot']);R=c.axisrot(ang[n['key_index']],key['press_axis'])
  local=(V-pv)@R+pv;p=local[c.MARKERS['R'][j]['mesh_vertex']]
  ss=key['key_top_playable_surface'];s=min(ss,key=lambda s:np.linalg.norm(p[:2]-np.clip(p[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']])))
  miss=float(np.linalg.norm(p[:2]-np.clip(p[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']]))*1000);gap=float((p[2]-s['z'])*1000)
  contact.append(dict(event=n['note_id'],finger=n['finger'],phase='HOLD_OR_PRESS' if t<n['note_off'] else 'RELEASE_FOLLOW',horizontal_mm=miss,gap_mm=gap,pass_=miss<=.03 and abs(gap)<=3))
  ids=np.array(rois[c.DIGITS[j]]['vertices']);near=ids[(np.linalg.norm(V[ids]-V[c.MARKERS['R'][j]['mesh_vertex']],axis=1)<=.012)&(abs(local[ids,2]-s['z'])<=.003)]
  footprints.append(dict(event=n['note_id'],finite_near_pad_vertex_count=len(near),near_pad_xyz_key_local_mm=(local[near]*1000).tolist(),definition='Strong digit skin vertices <=12mm from pad and <=3mm from current surface; diagnostic only, not new acceptance gate'))
 depths=[];surface=[];wrongmax=0.;all_depth=np.full((88,len(V)),-1e6)
 for key in c.KEYS:
  pv=np.array(key['press_pivot']);R=c.axisrot(ang[key['key_index']],key['press_axis']);local=(V-pv)@R+pv
  for j,g in enumerate(key['geometry']):
   kv=np.array(g['vertices']);lo=kv.min(0);hi=kv.max(0)
   if np.any(local.max(0)<lo) or np.any(local.min(0)>hi):continue
   pl=PLANES[key['key_index'],j];depth=-np.max(local@pl[:,:3].T-pl[:,3],axis=1)*1000
   all_depth[key['key_index']]=np.maximum(all_depth[key['key_index']],depth)
   owners={c.DIGITS[n['finger']-1] for n in owned if n['midi_note']==key['midi_note']}
   allowed=set(v for d in owners for v in rois[d]['vertices']);bad=[int(v) for v in np.flatnonzero(depth>.5) if int(v) not in allowed]
   if bad:
    vid=max(bad,key=lambda v:depth[v]);wrongmax=max(wrongmax,float(depth[vid]));depths.append(dict(key=key['note_name'],key_index=key['key_index'],color=key['color'],piece=g['name'],vertex=vid,depth_mm=float(depth[vid]),world_m=V[vid].tolist()))
   world=(kv-pv)@R.T+pv;tris=np.asarray(g['triangles']).reshape(-1,3).tolist();kt=BVHTree.FromPolygons([Vector(v) for v in world],tris,all_triangles=True,epsilon=0)
   for d in c.DIGITS:
    if d in owners:continue
    overlap=trees[d].overlap(kt)
    if overlap:surface.append(dict(key=key['note_name'],piece=g['name'],digit=d,triangle_pairs=len(overlap)))
 return dict(contacts=contact,finite_pad_regions=footprints,finger_intersection_pairs=pairs,wrong_or_inactive_key_depth_witnesses=depths,max_wrong_or_inactive_depth_mm=wrongmax,inactive_surface_intersections=surface),all_depth
for k,t in enumerate(A['times']):
 settime(sc,float(t));V0,F=coords(mesh);d0,dep0=measure(V0,float(t),I['original_events']);source.append(dict(label=P['phase_labels'][k],time=float(t),**d0))
 old_rt=rt.matrix_world.copy();old_basis={b.name:b.matrix_basis.copy() for b in rig.pose.bones};left_before=np.array([np.array(b.matrix_basis) for b in left.pose.bones]);ang0=angles()
 root0=np.array(rig.matrix_world);delta_world=A['world']@np.linalg.inv(root0)
 if not rig.animation_data:raise RuntimeError('MISSING_C1_RIG_ACTION')
 rigaction=rig.animation_data.action;rigslot=rig.animation_data.action_slot;rtaction=rt.animation_data.action;rtslot=rt.animation_data.action_slot
 rig.animation_data.action=None;rt.animation_data.action=None
 rt.matrix_world=Matrix(delta_world.tolist())@old_rt
 q=A['states'][k,6:].reshape(5,4)
 for j,d in enumerate(c.DIGITS):
  for name,R in zip(c.SETUPS['R',d][0],c.joint_mats('R',d,np.radians(q[j]))):rig.pose.bones[name].rotation_mode='QUATERNION';rig.pose.bones[name].rotation_quaternion=Matrix(R.tolist()).to_quaternion()
 bpy.context.view_layer.update();V1,_=coords(mesh);d1,dep1=measure(V1,float(t),I['p3_events'])
 regression=np.argwhere((dep1>.5)&(dep1-np.maximum(.5,dep0)>.02));witness=[]
 for keyid,vid in regression[:12]:witness.append(dict(key_index=int(keyid),vertex=int(vid),new_depth_mm=float(dep1[keyid,vid]),source_depth_mm=float(dep0[keyid,vid])))
 parity=float(np.max(np.linalg.norm(V1[[r['mesh_vertex'] for r in c.MARKERS['R']]]-A['predicted_pads'][k],axis=1))*1000)
 actual_world_error=float(np.max(abs(np.array(rig.matrix_world)-A['world'])))
 left_error=float(abs(np.array([np.array(b.matrix_basis) for b in left.pose.bones])-left_before).max());assert left_error<1e-7
 assert np.max(abs(angles()-ang0))<1e-9
 rows.append(dict(label=P['phase_labels'][k],time=float(t),**d1,new_vertex_depth_regression_count=len(regression),depth_regression_witnesses=witness,native_LBS_pad_parity_mm=parity,shared_rig_world_error=actual_world_error,left_basis_error=left_error,joint_min_bound_margin_deg=float(np.minimum(q-np.array(P['joint_bounds_deg'])[:,0],np.array(P['joint_bounds_deg'])[:,1]-q).min())))
 rig.animation_data.action=rigaction;rig.animation_data.action_slot=rigslot;rt.animation_data.action=rtaction;rt.animation_data.action_slot=rtslot
 rt.matrix_world=old_rt
 for b in rig.pose.bones:b.matrix_basis=old_basis[b.name]
 settime(sc,float(t))
 print('ACTUAL_INITIAL_ONLY',P['phase_labels'][k],'contactfail',sum(not r['pass_'] for r in d1['contacts']),'pairs',sum(d1['finger_intersection_pairs'].values()),'wrongdepth',round(d1['max_wrong_or_inactive_depth_mm'],3),flush=True)
assert digest(native(mesh,rig))==native_before
assert key_before=={ki:digest(payload(bpy.data.objects[name].animation_data.action)) for ki,name in man['key_pivots'].items()}
# Context boundary reference poses only; no new layout for R07 or R14.
context=[]
for noteid in ['R07','R14']:
 n=next(n for n in I['original_events'] if n['note_id']==noteid);t=n['note_on']+.035;settime(sc,t);V,_=coords(mesh);d,_=measure(V,t,I['original_events']);context.append(dict(event=noteid,time=t,rig_world=np.array(rig.matrix_world),**d))
dump('BLENDER_STATIC_DIAGNOSTICS.json',dict(status='INITIALIZATION_ONLY_OPTIMIZER_TERMINAL_STATE_LOST',version=bpy.app.version_string,source=source,initial_seed=rows,boundary_context=context,native_unchanged=True,key_actions_unchanged=True,external_libraries=0,new_actions=0,new_blends=0,new_videos=0,continuous_success=False,scope='10 same-seed static phases; all ten strong-digit skin BVH pairs, all 88 key pieces, entire 3300-vertex depth check; shared palm/web pair collision completeness remains unknown'))
protect();print('NATIVE_STATIC_DIAGNOSIS_COMPLETE; NOT A SOLUTION; NOT A TRAJECTORY')
