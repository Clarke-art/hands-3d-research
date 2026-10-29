import sys,json,hashlib,math,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;LATEST=P.parent/'left_little_finger_moving_key_reachability_r1';OLD=P.parent/'piano_hand_static_to_dynamic_transition_r1';sys.path.insert(0,str(OLD))
import bpy
from mathutils import Matrix,Vector
import common as o
import numpy as np
c=o.c
def dump(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False,default=lambda v:v.tolist() if hasattr(v,'tolist') else v),encoding='utf8')
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def action(a):
 return {'name':a.name,'curves':[[{'path':f.data_path,'index':f.array_index,'points':[[*k.co,*k.handle_left,*k.handle_right,k.interpolation] for k in f.keyframe_points]} for bag in s.channelbags for f in bag.fcurves] for l in a.layers for s in l.strips]}
assert not (P/'COUNTERFACTUAL_RAW_R1.json').exists(),'One controlled diagnostic evaluation only.'
protected=o.read(LATEST/'PROTECTED_INPUTS_BEFORE_R1.json')
for folder in [LATEST,OLD,o.STATIC]:
 for f in folder.rglob('*'):
  if f.is_file() and '__pycache__' not in f.parts:protected[str(f.resolve())]=o.sha(f)
assert all(Path(p).is_file() and o.sha(p)==s for p,s in protected.items())
dump('PROTECTED_INPUTS_BEFORE_R1.json',protected)
dump('DIAGNOSTIC_POLICY_R1.json',{'new_action_candidates':0,'states':{'A':'Saved current root + saved current finger Action','B':'Same current finger Action, external root temporarily restored to approved common static matrix; never saved'},'target_keys':[40,42],'sampling_hz':240,'timing':'Original 0.4–1.8s plus inherited exact phase boundaries','penetration_definition':'Inside true unchanged rectangular key solid, minimum exit distance >0.00001mm; separately report >3mm below-top legacy screen. Numerical epsilon is not a tolerance relaxation.','contacts':'Original fixed and actual skin pads, strict playable region,3mm vertical,2mm horizontal; actual current key angle','render_times':[.7333333333333333,.75,.7666666666666667],'render_scope':'Three consecutive60fps frames, three mature cameras, A reused unchanged; B rendered in unsaved memory. No full animation.','no_optimization':True,'not_a_candidate':True,'source_sha256':o.sha(LATEST/'LEFT_LITTLE_MOVING_KEY_PROBE_R1.blend')})
source=LATEST/'LEFT_LITTLE_MOVING_KEY_PROBE_R1.blend';man=o.read(LATEST/'PROBE_SCENE_MANIFEST_R1.json');assert o.sha(source)==man['candidate_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
spec=importlib.util.spec_from_file_location('identity',o.ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
sm=o.read(o.STATIC/'STATIC_SCENE_MANIFEST_R2.json');static={}
for label,m in sm['mapping'].items():
 bpy.context.window.scene=bpy.data.scenes[m['scene']];bpy.context.view_layer.update();v=digest(h.core(bpy.data.objects[m['mesh']],bpy.data.objects[m['rig']]))
 expected=o.read(LATEST/'STATIC_ANCHOR_PROTECTION_R1.json')['reopened_static_scene_identity'][label]['expected'];assert v==expected;static[label]={'core_sha256':v,'matches':True}
staticroot=bpy.data.objects[sm['mapping']['L1']['root']].matrix_world.copy();staticroot2=bpy.data.objects[sm['mapping']['L2']['root']].matrix_world.copy();assert np.max(abs(np.array(staticroot)-np.array(staticroot2)))<1e-7
info=man['mapping'];sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[info['rig']];mesh=bpy.data.objects[info['mesh']];rt=bpy.data.objects[info['root']];act=rt.animation_data.action;slot=rt.animation_data.action_slot
actions_before={a.name:digest(action(a)) for a in bpy.data.actions};count_before=len(bpy.data.actions)
extract=o.read(o.FORMAL/'FORMAL_INPUT_EXTRACTION_R1.json')['L'];weights=np.array(extract['weights']);bone_names=extract['bone_names']
pieces={};keygeometry={}
for midi in [40,42]:
 pieces[midi]=[];k=c.KEYS[midi-21]
 for g in k['geometry']:
  ob=next(v for v in sc.objects if v.type=='MESH' and g['name'] in v.name);local=np.array([list(v.co) for v in ob.data.vertices]);uniq=np.unique(local,axis=0);lo=local.min(0);hi=local.max(0)
  assert len(uniq)==8 and np.all(np.isclose(uniq,lo,atol=1e-10)|np.isclose(uniq,hi,atol=1e-10)),'Do not assume irregular piece is a box'
  actual=np.array([list(<REDACTED_EMAIL>) for v in ob.data.vertices]);assert np.max(abs(actual-np.array(g['vertices'])))<1e-7
  pieces[midi].append((ob,lo,hi));keygeometry[g['name']]={'vertices':g['vertices'],'triangles':g['triangles'],'true_rectangular_solid':True,'object':ob.name,'matrix':[list(r) for r in ob.matrix_world]}
def settime(t):
 rt.animation_data.action=act;rt.animation_data.action_slot=slot;f=1+(t-.4)*60;i=math.floor(f+1e-7);sc.frame_set(i,subframe=max(0,f-i));bpy.context.view_layer.update()
def basis():return np.array([np.array(b.matrix_basis) for b in rig.pose.bones])
def geom():
 ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();arr=np.empty(len(me.vertices)*3);me.vertices.foreach_get('co',arr);W=np.array(ev.matrix_world);V=arr.reshape(-1,3)@W[:3,:3].T+W[:3,3];ev.to_mesh_clear();pp=np.array([list(<REDACTED_EMAIL>[r['distal_frame']].matrix@Vector(r['local_pad_point'])) for r in c.MARKERS['L']]);return V,pp
def capture(t):
 V,pp=geom();contact={};angles={k:float(bpy.data.objects[n].rotation_euler.x) for k,n in info['key_pivots'].items()}
 for j,midi in [(4,38),(0,50)]:
  sk=V[c.MARKERS['L'][j]['mesh_vertex']];contact[str(midi)]={'fixed':o.measure(pp[j],midi,angles[str(midi-21)]),'skin':o.measure(sk,midi,angles[str(midi-21)]),'fixed_xyz_mm':pp[j]*1000,'skin_xyz_mm':sk*1000}
 hits={}
 for midi in [40,42]:
  rows=[]
  for ob,lo,hi in pieces[midi]:
   inv=np.array(ob.matrix_world.inverted());local=V@inv[:3,:3].T+inv[:3,3];exitdist=np.minimum(local-lo,hi-local).min(1);ids=np.flatnonzero(exitdist>1e-8)
   for vid in ids:rows.append({'vertex':int(vid),'piece':ob.name,'xyz_mm':V[vid]*1000,'vertical_below_top_mm':float((hi[2]-local[vid,2])*1000),'minimum_exit_distance_mm':float(exitdist[vid]*1000)})
  hits[str(midi)]={'key_name':c.KEYS[midi-21]['note_name'],'midi':midi,'depression_fraction':0,'key_unchanged_unpressed':all(np.max(abs(np.array(ob.matrix_world)-np.array(keygeometry[next(g for g in keygeometry if g in ob.name)]['matrix'])))<1e-7 for ob,_,_ in pieces[midi]),'penetrations':rows}
 active=[{'note_id':n['note_id'],'midi':n['midi_note'],'phase':'NOTE_ON' if abs(t-n['note_on'])<1e-8 else o.phase(n,t)} for n in o.EVENTS['L'] if n['note_on']-1e-8<=t<=n['note_off']+.07+1e-8]
 return {'contact':contact,'keys':hits,'active_contact_tasks':active,'root_matrix':[list(r) for r in rt.matrix_world],'key_angles_rad':angles}
oldmotion=np.load(LATEST/'probe_motion.npz');times=np.unique(np.r_[np.arange(96,433)/240,oldmotion['times']]);rows=[];jointdiff=0;keydiff=0
for i,t in enumerate(times):
 settime(float(t));beforebasis=basis();A=capture(float(t));rt.animation_data.action=None;rt.matrix_world=staticroot;bpy.context.view_layer.update();B=capture(float(t));jointdiff=max(jointdiff,float(np.max(abs(basis()-beforebasis))));keydiff=max(keydiff,max(abs(A['key_angles_rad'][k]-B['key_angles_rad'][k]) for k in A['key_angles_rad']));rows.append({'time':float(t),'A':A,'B':B})
 if i%80==0:print('CONTROLLED_AB_EVALUATION',i,len(times),flush=True)
settime(.4)
assert jointdiff==0 and keydiff==0 and len(bpy.data.actions)==count_before and {a.name:digest(action(a)) for a in bpy.data.actions}==actions_before
ids=sorted(set(p['vertex'] for r in rows for s in ['A','B'] for k in ['40','42'] for p in r[s]['keys'][k]['penetrations']));regions={}
for vid in ids:
 w=weights[vid];groups={d:float(sum(w[j] for j,n in enumerate(bone_names) if n.startswith(d+'_'))) for d in c.DIGITS};groups['PALM']=float(sum(w[j] for j,n in enumerate(bone_names) if not any(n.startswith(d+'_') for d in c.DIGITS)));dominant=int(np.argmax(w));regions[str(vid)]={'dominant_digit':max(groups,key=groups.get),'dominant_bone':bone_names[dominant],'dominant_bone_weight':float(w[dominant]),'digit_weight_sums':groups,'canonical_rest_y_m':extract['rest_vertices_canonical'][vid][1]}
dump('COUNTERFACTUAL_RAW_R1.json',{'source_sha256':man['candidate_sha256'],'mesh_object':mesh.name,'sampling_hz':240,'sample_count':len(times),'rows':rows,'affected_vertex_regions_only':regions,'key_geometry':keygeometry,'static_anchor_identity':static,'all_10_original_markers':c.MARKERS,'markers_sha256':o.sha(o.OLD/'FINGERTIP_CONTACT_MARKERS_R1.json'),'static_root_matrix':[list(r) for r in staticroot],'same_joint_action_max_matrix_difference':jointdiff,'same_key_angle_max_difference_rad':keydiff,'actions_sha256_before':actions_before,'actions_sha256_after':{a.name:digest(action(a)) for a in bpy.data.actions},'action_count_before':count_before,'action_count_after':len(bpy.data.actions),'new_action_candidates':0,'saved_blend':False})
# Nine counterfactual stills only; source A normal frames are reused, not rerendered.
folder=P/'_frames_B';folder.mkdir(exist_ok=True);render=[];sc.render.resolution_x=768;sc.render.resolution_y=594
for frame in [20,21,22]:
 t=.4+frame/60;settime(t);rt.animation_data.action=None;rt.matrix_world=staticroot;bpy.context.view_layer.update()
 for view,name in info['cameras'].items():
  sc.camera=bpy.data.objects[name];file=folder/f'{frame:04}_{view}.png';sc.render.filepath=str(file);bpy.ops.render.render(write_still=True);afile=LATEST/'_frames'/'L'/file.name;assert afile.is_file();render.append({'time':t,'view':view,'A_original_frame':str(afile),'A_sha256':o.sha(afile),'B_diagnostic_frame':str(file),'B_sha256':o.sha(file),'same_camera':name,'B_is_not_candidate':True})
settime(.4);assert {a.name:digest(action(a)) for a in bpy.data.actions}==actions_before and o.sha(source)==man['candidate_sha256'];dump('DIAGNOSTIC_RENDER_MANIFEST_R1.json',{'frames':render,'new_normal_A_renders':0,'new_B_stills':9,'new_action_candidates':0,'source_not_saved':True,'camera_specs_unchanged':True})
print('CONTROLLED_DIAGNOSIS_COMPLETE_NO_BLEND_SAVE',flush=True)
