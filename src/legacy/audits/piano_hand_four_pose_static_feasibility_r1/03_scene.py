import sys,json,hashlib,ast,importlib.util
sys.dont_write_bytecode=True
from pathlib import Path
import bpy,numpy as np
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parent;ROOT=P.parents[1];OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1'
sys.path.insert(0,str(OLD));import performance_core as c
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
sp=importlib.util.spec_from_file_location('identity',ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h)
tree=ast.parse((P.parent/'piano_keyboard_spatial_anchor_and_contact_validation_r1/04_hands.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='intrinsic'],type_ignores=[]),'intrinsic','exec'))
policy=read(P/'STATIC_POSTURE_POLICY_R1.json');sol=read(P/'SOLVED_STATIC_POSES_R1.json');assert sha(P/'STATIC_POSTURE_POLICY_R1.json')==sol['policy_sha256']
bpy.ops.wm.read_factory_settings(use_empty=True);first=bpy.context.scene;mapping={};snapshots={}
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def camera(sc,name,eye,target,scale):
 d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=scale;d.clip_start=.001;d.clip_end=10;ob=bpy.data.objects.new(name,d);sc.collection.objects.link(ob);ob.location=eye;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();return ob
for pose,row in sol['poses'].items():
 s=row['hand'];cfg=c.RIG[s];sc=first if pose=='L1' else bpy.data.scenes.new('STATIC_'+pose);sc.name='STATIC_'+pose;bpy.context.window.scene=sc;sc['DESIGN_ONLY']=True;sc['PHASE']='PIANO_HAND_FOUR_POSE_STATIC_FEASIBILITY_R1';sc['POSE']=pose;sc['POLICY_SHA256']=sol['policy_sha256'];sc['NO_DYNAMIC_TRANSITION_CLAIM']=True;sc.frame_start=sc.frame_end=1;sc.unit_settings.system='METRIC'
 source=ROOT/cfg['baseline'];assert sha(source)==cfg['baseline_sha256']
 with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.objects=[cfg['mesh'],cfg['rig']]
 for obj in dst.objects:
  if obj and not obj.users_collection:sc.collection.objects.link(obj)
 rig=next(o for o in dst.objects if o.type=='ARMATURE');ob=next(o for o in dst.objects if o.type=='MESH')
 if rig.animation_data:rig.animation_data.action=None
 h.neutral(rig);bpy.context.view_layer.update();snapshots[pose]=digest(intrinsic(ob,rig));originalcolor=list(ob.color)
 if pose in ['L1','R1']:assert snapshots[pose]==cfg['static_identity'],('FIRST_IMPORT_IDENTITY',pose)
 root=bpy.data.objects.new('STATIC_ROOT_'+pose,None);sc.collection.objects.link(root);rig.parent=root;rig.matrix_parent_inverse=Matrix.Identity(4);rig.matrix_basis=Matrix.Identity(4);root.matrix_world=Matrix.Translation(Vector(row['root_xyz_m']))@Matrix(row['root_rotation_matrix']).to_4x4()@Matrix(cfg['native_to_canonical'])
 q=np.radians(row['joint_increments_deg'])
 for j,digit in enumerate(c.DIGITS):
  for name,r in zip(c.SETUPS[s,digit][0],c.joint_mats(s,digit,q[j])):
   bone=rig.pose.bones[name];bone.rotation_mode='QUATERNION';bone.rotation_quaternion=Matrix(r).to_quaternion()
 ob.color=(.73,.49,.34,1);ob['STATIC_POSE']=pose
 for key in c.KEYS:
  for geom in key['geometry']:
   me=bpy.data.meshes.new(pose+'_'+geom['name']);inds=geom['triangles'];me.from_pydata(geom['vertices'],[],[inds[i:i+3] for i in range(0,len(inds),3)]);ko=bpy.data.objects.new(pose+'_'+geom['name'],me);sc.collection.objects.link(ko);ko.color=(.86,.85,.80,1) if key['color']=='WHITE' else (.025,.028,.031,1)
   ko['FROZEN_KEY_INDEX']=key['key_index'];ko['MIDI_NOTE']=key['midi_note'];ko['DISPLAY_TINT_ONLY']=True
   if key['midi_note']==row['task'].get('active_midi'):ko.color=(.38,.62,.64,1) if key['color']=='WHITE' else (.025,.10,.12,1)
 for midi in ([38,50] if s=='L' else [74,76,78,79,81]):
  key=c.KEYS[midi-21];d=bpy.data.curves.new(pose+'_label_'+key['note_name'],'FONT');d.body=key['note_name'];d.size=.008;d.align_x='CENTER';d.extrude=0;lab=bpy.data.objects.new(d.name,d);sc.collection.objects.link(lab);lab.location=(key['key_center'][0],-.012,.001);lab.color=(.1,.16,.17,1)
 # Display-only case below, never alters the frozen key meshes.
 xs=[v[0] for k in c.KEYS for g in k['geometry'] for v in g['vertices']];width=max(xs)-min(xs);cx=(max(xs)+min(xs))/2
 bpy.ops.mesh.primitive_cube_add(size=1,location=(cx,.055,-.049));bed=bpy.context.object;bed.name='DISPLAY_ONLY_KEYBED_'+pose;bed.scale=(width+.01,.15,.025);bed.color=(.20,.18,.16,1)
 center=(-.2274 if s=='L' else .2394)
 cams={'TEACHING_TOP':camera(sc,pose+'_TEACHING_TOP',(center,.013,.75),(center,.013,.012),.31),'SIDE_OBLIQUE':camera(sc,pose+'_SIDE_OBLIQUE',(center+.28,-.34,.14),(center,.015,.025),.35),'REASONABLE_CLOSE':camera(sc,pose+'_REASONABLE_CLOSE',(center-.10,-.20,.32),(center,.020,.028),.245)}
 sc.camera=cams['TEACHING_TOP'];sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1100;sc.render.resolution_y=850;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
 sc.display.shading.light='STUDIO';sc.display.shading.studio_light='paint.sl';sc.display.shading.color_type='OBJECT';sc.display.shading.show_shadows=True;sc.display.shading.show_cavity=True;sc.display.shading.cavity_type='BOTH';sc.display.shading.curvature_ridge_factor=1.2;sc.display.shading.curvature_valley_factor=.7;sc.display.shading.show_specular_highlight=True;sc.display.shading.show_object_outline=False;sc.display.shading.background_type='WORLD';sc.world=bpy.data.worlds.new('AUDIT_STUDIO_'+pose);sc.world.color=(.16,.17,.19);sc.view_settings.view_transform='Standard';sc.render.fps=1
 mapping[pose]={'scene':sc.name,'hand':s,'mesh':ob.name,'rig':rig.name,'root':root.name,'original_color':originalcolor,'source_intrinsic_at_import':snapshots[pose],'cameras':{k:v.name for k,v in cams.items()},'active_key_display_tint':row['task'].get('active_midi')}
 bpy.context.view_layer.update()
# Only unbound imported source Actions, if present, are removed from the audit file.
assert not any(o.animation_data and o.animation_data.action for o in bpy.data.objects)
for action in list(bpy.data.actions):
 if action.users==0:bpy.data.actions.remove(action)
bpy.context.window.scene=bpy.data.scenes['STATIC_L1'];dest=P/'STATIC_POSTURE_CANDIDATE_R1.blend';assert not dest.exists(),'Do not overwrite another candidate.'
bpy.ops.wm.save_as_mainfile(filepath=str(dest));bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False)
out={};arrays={};identities={}
for pose,info in mapping.items():
 sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[info['rig']];ob=bpy.data.objects[info['mesh']];root=bpy.data.objects[info['root']];s=info['hand'];cfg=c.RIG[s];bpy.context.view_layer.update()
 V,F=h.coords(ob);pads=np.array([list(<REDACTED_EMAIL>[r['distal_frame']].matrix@Vector(r['local_pad_point'])) for r in c.MARKERS[s]]);skin=np.array([V[r['mesh_vertex']] for r in c.MARKERS[s]]);pred=np.array(sol['poses'][pose]['pad_prediction_xyz_m'])
 out[pose]={'pad_xyz_m':pads.tolist(),'skin_pad_xyz_m':skin.tolist(),'FK_saved_reopened_max_error_mm':float(np.max(np.linalg.norm(pads-pred,axis=1))*1000),'skin_rigid_pad_drift_mm':(np.linalg.norm(skin-pads,axis=1)*1000).tolist(),'evaluated_vertices':len(V),'bone_count':len(rig.data.bones),'shape_key_values':h.values(ob),'root_scale_singular_values':np.linalg.svd(np.array(root.matrix_world)[:3,:3],compute_uv=False).tolist()}
 arrays[pose+'_verts']=V;arrays[pose+'_pads']=pads;arrays[pose+'_skin_pads']=skin
 assert out[pose]['FK_saved_reopened_max_error_mm']<.03
 # Neutralize only in memory for immutable intrinsic comparison; never save the reset.
 ob.color=info['original_color'];del ob['STATIC_POSE'];rig.parent=None;rig.matrix_world=Matrix.Identity(4);h.neutral(rig)
 actual=digest(intrinsic(ob,rig));identities[pose]={'before':info['source_intrinsic_at_import'],'after_reset_not_saved':actual,'matches':actual==info['source_intrinsic_at_import']};assert identities[pose]['matches'],('INTRINSIC_CHANGED',pose)
np.savez_compressed(P/'evaluated_static_candidate.npz',**arrays)
dump('STATIC_SCENE_MANIFEST_R1.json',{'candidate_path':str(dest),'candidate_sha256':sha(dest),'policy_sha256':sol['policy_sha256'],'mapping':mapping,'readback':out,'intrinsic_after_pose_save_reopen_reset_checks':identities,'candidate_count':1,'static_scene_count':4,'new_action_count':0,'save_reopen_verified':True,'verification_reset_not_saved':True,'display':'Workbench object color and active-key tint only; no material/mesh/topology/weight/rest/driver changes.'})
print('STATIC_CANDIDATE_SAVED_REOPENED',json.dumps({p:{k:v for k,v in o.items() if k not in ['pad_xyz_m','skin_pad_xyz_m','shape_key_values']} for p,o in out.items()}),flush=True)
