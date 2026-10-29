import sys,json,hashlib,importlib.util,math
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
PRE=P.parent/'piano_hand_static_to_dynamic_transition_r1'
sys.path.insert(0,str(PRE))
import bpy
from mathutils import Matrix,Vector
import common as old
import numpy as np
c=old.c
def dump(n,x): (P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False,default=lambda v:v.tolist() if hasattr(v,'tolist') else v),encoding='utf-8')
def sha(p): return old.sha(p)
def digest(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert not (P/'CONTACT_PHASE_MEASUREMENTS_R1.json').exists(),'One read-only diagnosis, no rerun.'
protected=old.read(PRE/'PROTECTED_INPUTS_BEFORE_R1.json')
for d in [PRE,old.STATIC]:
 for f in d.rglob('*'):
  if f.is_file() and '__pycache__' not in f.parts: protected[str(f.resolve())]=sha(f)
assert all(Path(p).is_file() and sha(p)==s for p,s in protected.items())
dump('PROTECTED_INPUTS_BEFORE_R1.json',protected)
manifest=old.read(PRE/'DYNAMIC_SCENE_MANIFEST_R1.json')
source=PRE/'STATIC_TO_DYNAMIC_TRANSITION_CANDIDATE_R1.blend'
assert sha(source)==manifest['candidate_sha256']
spec=importlib.util.spec_from_file_location('identity',old.ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
actions_before=len(bpy.data.actions)
static={}
sm=old.read(old.STATIC/'STATIC_SCENE_MANIFEST_R2.json')
for label,m in sm['mapping'].items():
 bpy.context.window.scene=bpy.data.scenes[m['scene']];bpy.context.view_layer.update()
 got=digest(h.core(bpy.data.objects[m['mesh']],bpy.data.objects[m['rig']]))
 static[label]={'expected':manifest['static_anchor_scene_identity'][label]['saved'],'actual':got,'matches':got==manifest['static_anchor_scene_identity'][label]['saved']}
assert all(v['matches'] for v in static.values())
dump('STATIC_ANCHOR_PROTECTION_R1.json',{'status':'UNCHANGED','human_approval_remains_valid':True,'source_static_blend_sha256':sha(old.STATIC/'STATIC_POSTURE_REFINED_CANDIDATE_R2.blend'),'source_dynamic_blend_sha256':sha(source),'reopened_static_scene_identity':static,'markers_sha256':sha(old.OLD/'FINGERTIP_CONTACT_MARKERS_R1.json'),'keyboard_table_sha256':sha(old.OLD/'KEYBOARD_88_KEY_TABLE_R1.json'),'anchors':{k:old.ANCHORS[k] for k in ['L1','L2']},'official_L_markers':c.MARKERS['L'],'D2_D3_geometry':{str(k):c.KEYS[k-21] for k in [38,50]}})
info=manifest['mapping']['L'];sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc
rig=bpy.data.objects[info['rig']];ob=bpy.data.objects[info['mesh']];rt=bpy.data.objects[info['root']]
def time(t):
 f=1+(t-.4)*60;i=math.floor(f+1e-7);sc.frame_set(i,subframe=max(0.,f-i));bpy.context.view_layer.update()
def signed(R,axis):
 axis=np.array(axis);axis/=np.linalg.norm(axis)
 return np.arctan2(np.dot(axis,[R[2,1]-R[1,2],R[0,2]-R[2,0],R[1,0]-R[0,1]])/2,(np.trace(R)-1)/2)
def qread(d):
 names,rels,axes,spread,pad=c.SETUPS['L',d];Rs=[np.array(rig.pose.bones[n].matrix_basis.to_3x3()) for n in names]
 v=np.array(spread);a=np.array(axes[0]);w=Rs[0].T@v;u=v-a*np.dot(a,v);w=w-a*np.dot(a,w)
 flex=-np.arctan2(np.dot(a,np.cross(u,w)),np.dot(u,w))
 spreadq=signed(Rs[0]@c.axisrot(-flex,axes[0]),spread)
 return np.array([flex,signed(Rs[1],axes[1]),signed(Rs[2],axes[2]),spreadq])
def geom():
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();V=np.array([list(<REDACTED_EMAIL>) for v in me.vertices]);ev.to_mesh_clear()
 pads=np.array([list(<REDACTED_EMAIL>[r['distal_frame']].matrix@Vector(r['local_pad_point'])) for r in c.MARKERS['L']])
 return V,pads,V[[r['mesh_vertex'] for r in c.MARKERS['L']]]
def actual_contact(pt,midi):
 k=c.KEYS[midi-21];parts=[]
 for child in sc.objects:
  if child.type!='MESH' or child.get('FROZEN_KEY_INDEX')!=midi-21:continue
  local=np.array([list(v.co) for v in child.data.vertices]);lo=local.min(0);hi=local.max(0);localpt=np.array(child.matrix_world.inverted()@Vector(pt));z=hi[2]
  hdist=float(np.linalg.norm(localpt[:2]-np.clip(localpt[:2],lo[:2],hi[:2])))*1000
  surf=child.matrix_world@Vector((float(localpt[0]),float(localpt[1]),float(z)))
  n=child.matrix_world.to_3x3().inverted().transposed()@Vector((0,0,1));n.normalize()
  gap=float((Vector(pt)-surf).dot(n))*1000;vertical=gap/float(n.z)
  parts.append({'piece':child.name,'inside':hdist<1e-5,'horizontal_mm':hdist,'normal_gap_mm':gap,'world_vertical_gap_mm':vertical,'plane_point_at_local_xy_mm':np.array(surf)*1000,'world_vertical_surface_below_point_mm':[float(pt[0]*1000),float(pt[1]*1000),float(pt[2]*1000-vertical)],'plane_normal':list(n),'local_pad_xyz_mm':localpt*1000,'pass':bool(hdist<1e-5 and abs(gap)<=3)})
 return min(parts,key=lambda x:x['horizontal_mm'])
M=np.load(PRE/'temporal_motion.npz');samples=[];maximum_key_error=0;max_gap_disagreement=0;max_q_error=0
critical={}
for n in old.EVENTS['L']:
 if n['finger']!=5:continue
 on,off=n['note_on'],n['note_off']
 critical[n['note_id']]=[(on-.12,'PREPARATION'),(on,'NOTE_ON'),(on+1/120,'DESCENT_BEGIN'),(on+.035,'FULL_DOWN'),((on+.035+off)/2,'HOLD'),(off,'NOTE_OFF'),(off+.035,'REBOUND_MID'),(off+.07,'REBOUND_END'),((off+.07+old.recovery_end(n))/2,'RECOVERY')]
times=sorted(set(list(M['L_times'])+[t for v in critical.values() for t,_ in v]))
for t in times:
 time(float(t));V,pp,sp=geom();q=np.array([qread(d) for d in c.DIGITS]);ka={k:float(bpy.data.objects[v].rotation_euler.x) for k,v in info['key_pivots'].items()}
 for ki,pname in info['key_pivots'].items():
  key=c.KEYS[int(ki)];pivot=bpy.data.objects[pname]
  for g in key['geometry']:
   child=next(o for o in pivot.children if g['name'] in o.name);actual=np.array([list(<REDACTED_EMAIL>) for v in child.data.vertices]);expected=old.keytransform(key['midi_note'],g['vertices'],ka[ki]);maximum_key_error=max(maximum_key_error,float(np.max(np.linalg.norm(actual-expected,axis=1))*1000))
 idx=np.flatnonzero(np.abs(M['L_times']-t)<1e-8)
 if len(idx):max_q_error=max(max_q_error,float(np.max(np.abs(np.degrees(q-M['L_q'][idx[0]])))))
 contacts={}
 for j,midi in [(4,38),(0,50)]:
  fixed=actual_contact(pp[j],midi);skin=actual_contact(sp[j],midi)
  max_gap_disagreement=max(max_gap_disagreement,abs(fixed['normal_gap_mm']-old.measure(pp[j],midi,ka[str(midi-21)])['gap_mm']))
  contacts[str(midi)]={'fixed_pad_xyz_mm':pp[j]*1000,'skin_pad_xyz_mm':sp[j]*1000,'fixed':fixed,'skin':skin}
 b=np.array(old.SP['joint_increment_bounds_deg']['LONG']);degrees=np.degrees(q[4]);active=[{'note_id':n['note_id'],'midi':n['midi_note'],'finger':n['finger'],'phase':old.phase(n,t)} for n in old.EVENTS['L'] if n['note_on']-1e-8<=t<=n['note_off']+.07+1e-8]
 samples.append({'time':float(t),'key_angles_rad':ka,'contact':contacts,'little_joint_increments_deg':degrees,'little_margins_to_lower_deg':degrees-b[0],'little_margins_to_upper_deg':b[1]-degrees,'little_local_quaternions':{n:list(rig.pose.bones[n].rotation_quaternion) for n in c.SETUPS['L','LITTLE'][0]},'root_world_matrix':[list(r) for r in rt.matrix_world],'root_xyz_mm':np.array(rt.matrix_world.translation)*1000,'root_orientation_quaternion':list(rt.matrix_world.to_quaternion()),'other_contact_tasks':[a for a in active if a['finger']!=5]})
phase_rows={n:[{'stage':label,**min(samples,key=lambda x:abs(x['time']-t))} for t,label in vv] for n,vv in critical.items()}
dump('CONTACT_PHASE_MEASUREMENTS_R1.json',{'source_sha256':sha(source),'method':'Saved/reopened Blender evaluated mesh and actual child mesh top planes; no rebuilt skinning. Quaternion joint decomposition from saved pose matrices.','samples_hz':120,'critical_phases':phase_rows,'all_samples':samples,'actual_key_world_vertex_max_error_mm':maximum_key_error,'independent_actual_plane_vs_old_gap_max_error_mm':max_gap_disagreement,'saved_joint_decomposition_vs_original_q_max_error_deg':max_q_error,'release_overlap':{'D2_release_D3_contact':[.95,1.02],'D3_release_D2_contact':[1.2,1.27]},'no_new_action':True})
# Infinitesimal one-sided sensitivity measurements in memory, restored without saving.
# These are local derivatives at the existing poses, not reachable-pose searches or candidates.
sens=[]
for t in [.7,.735,.95,1.235]:
 time(t);q=qread('LITTLE');V,pp,sp=geom();names=c.SETUPS['L','LITTLE'][0];saved={n:rig.pose.bones[n].matrix_basis.copy() for n in names};action=rig.animation_data.action;slot=rig.animation_data.action_slot;rig.animation_data.action=None
 J=[];S=[];delta=.05;b=np.array(old.SP['joint_increment_bounds_deg']['LONG'])
 for j in range(4):
  step=delta if np.degrees(q[j])+delta<=b[1,j]+1e-7 else -delta;v=q.copy();v[j]+=np.radians(step)
  for n,R in zip(names,c.joint_mats('L','LITTLE',v)):rig.pose.bones[n].matrix_basis=Matrix(R).to_4x4()
  bpy.context.view_layer.update();_,p2,s2=geom();J.append((p2[4]-pp[4])*1000/step);S.append((s2[4]-sp[4])*1000/step)
  for n,B in saved.items():rig.pose.bones[n].matrix_basis=B
  bpy.context.view_layer.update()
 rig.animation_data.action=action;rig.animation_data.action_slot=slot;bpy.context.view_layer.update()
 sens.append({'time':t,'q_deg':np.degrees(q),'fixed_xyz_mm':pp[4]*1000,'skin_xyz_mm':sp[4]*1000,'fixed_J_xyz_mm_per_deg':np.array(J).T,'skin_J_xyz_mm_per_deg':np.array(S).T,'finite_difference_step_deg':delta,'local_only':True})
dump('JOINT_REACHABILITY_R1.json',{'engineering_bounds_deg':old.SP['joint_increment_bounds_deg']['LONG'],'not_physiological_bounds':True,'no_global_unreachability_claim':True,'local_derivative_measurements':sens,'method':'Blender evaluated one-sided 0.05 degree local differential at saved pose; source action temporarily detached in memory and restored, no file save, no Action creation, no search or solver.','old_control_bounds':{'lower_deg':np.maximum([0,0,0,-25],np.degrees(old.qanchor('L1')[4])-12),'upper_deg':np.minimum([31.5,32,20,24.5],np.degrees(old.qanchor('L1')[4])+12)},'original_near_bound_dwell_sec':.2916666666666667,'new_candidate_executed':False})
assert len(bpy.data.actions)==actions_before and sha(source)==manifest['candidate_sha256']
print(json.dumps({'samples':len(samples),'key_error_mm':maximum_key_error,'gap_disagreement_mm':max_gap_disagreement,'q_error_deg':max_q_error,'sensitivity':sens},default=lambda x:x.tolist() if hasattr(x,'tolist') else x),flush=True)
