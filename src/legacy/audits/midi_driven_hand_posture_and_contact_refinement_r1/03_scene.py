import bpy,sys,ast,importlib.util,json,hashlib
from pathlib import Path
import numpy as np
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from performance_core import *
sp=importlib.util.spec_from_file_location('identity',ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h)
tree=ast.parse((PRE/'04_hands.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='intrinsic'],type_ignores=[]),'intrinsic','exec'))
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
A=np.load(P/'procedural_motion.npz');bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.render.fps=FPS;sc.frame_start=1;sc.frame_end=round(DURATION*FPS);sc.unit_settings.system='METRIC'
sc['PHASE']='MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1';sc['SOURCE']='Public-domain Mutopia MIDI; procedural joint actions; no PianoVAM';sc['STATUS']='UNVALIDATED_SINGLE_CANDIDATE';sc['TIMEBASE']='PERFORMANCE_TIMELINE_R1.json seconds; frame1=time0';sc['NOT_PRODUCTION']=True
def mat(name,col,rough):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;return m
skin=mat('POC_ONLY_SEMI_REALISTIC_HUMAN_SKIN',(.52,.31,.22),.49);p=skin.node_tree.nodes.get('Principled BSDF');p.inputs['Subsurface Weight'].default_value=.055;p.inputs['Subsurface Radius'].default_value=(1,.42,.23);p.inputs['Subsurface Scale'].default_value=.008;p.inputs['IOR'].default_value=1.4
noise=skin.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=480;noise.inputs['Detail'].default_value=2
bump=skin.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.1;bump.inputs['Distance'].default_value=.00012;skin.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);skin.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
white=mat('Frozen white key display',(.83,.82,.78),.3);black=mat('Frozen black key display',(.012,.014,.018),.29);case=mat('Audit support dark wood',(.026,.02,.017),.39)
def linear(obj):
 if not obj.animation_data or not obj.animation_data.action:return
 for l in obj.animation_data.action.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for f in bag.fcurves:
     for k in f.keyframe_points:k.interpolation='LINEAR'
added_material_slot={}
for s,c in RIG.items():
 assert sha(ROOT/c['baseline'])==c['baseline_sha256']
 with bpy.data.libraries.load(str(ROOT/c['baseline']),link=False) as (src,dst):dst.objects=[c['mesh'],c['rig']]
 for ob in dst.objects:
  if ob and not ob.users_collection:sc.collection.objects.link(ob)
 rig=bpy.data.objects[c['rig']];ob=bpy.data.objects[c['mesh']];rig.animation_data_clear();h.neutral(rig)
 assert digest(intrinsic(ob,rig))==c['static_identity'],('INITIAL_IDENTITY',s)
 added_material_slot[s]=not bool(ob.material_slots)
 if not ob.material_slots:ob.data.materials.append(skin)
 for slot in ob.material_slots:slot.link='OBJECT';slot.material=skin
 root=bpy.data.objects.new('COORDINATED_PALM_ROOT_'+s,None);sc.collection.objects.link(root);C=Matrix(c['native_to_canonical']);root.rotation_mode='QUATERNION';rig.parent=root;rig.matrix_parent_inverse=Matrix.Identity(4)
 for i,t in enumerate(A['times']):
  frame=1+t*FPS
  last=root.rotation_quaternion.copy();root.matrix_world=Matrix.Translation(Vector(A[s+'_root'][i]))@Matrix(A[s+'_rotation'][i]).to_4x4()@C
  if i and root.rotation_quaternion.dot(last)<0:root.rotation_quaternion.negate()
  root.keyframe_insert(data_path='location',frame=frame);root.keyframe_insert(data_path='rotation_quaternion',frame=frame)
  for j,d in enumerate(DIGITS):
   names=SETUPS[s,d][0]
   for name,m in zip(names,joint_mats(s,d,A[s+'_q'][i,j])):
    bone=rig.pose.bones[name];bone.rotation_mode='QUATERNION';q=Matrix(m).to_quaternion()
    if i and bone.rotation_quaternion.dot(q)<0:q.negate()
    bone.rotation_quaternion=q;bone.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=d)
 rig.animation_data.action.name='NEW_MIDI_PROCEDURAL_REFINED_'+s+'_R1';linear(rig)
 root.animation_data.action.name='NEW_MIDI_PROCEDURAL_PALM_'+s+'_R1';linear(root)
 for row in MARKERS[s]:
  o=bpy.data.objects.new('PAD_'+s+'_'+row['digit'],None);sc.collection.objects.link(o);o.parent=rig;o.parent_type='BONE';o.parent_bone=row['distal_frame'];o.matrix_parent_inverse=Matrix.Identity(4);o.location=Vector(row['local_pad_point'])-Vector((0,rig.data.bones[row['distal_frame']].length,0));o.empty_display_size=.002
for action in list(bpy.data.actions):
 if not action.name.startswith('NEW_MIDI_PROCEDURAL_'):bpy.data.actions.remove(action)
for k in KEYS:
 pv=np.array(k['press_pivot']);pivot=bpy.data.objects.new(k['semantic_identity'],None);sc.collection.objects.link(pivot);pivot.location=pv;pivot['midi_note']=k['midi_note'];pivot['TIMEBASE']='PERFORMANCE_TIMELINE_R1.json'
 for g in k['geometry']:
  me=bpy.data.meshes.new(g['name']);inds=g['triangles'];me.from_pydata((np.array(g['vertices'])-pv).tolist(),[],[inds[j:j+3] for j in range(0,len(inds),3)]);o=bpy.data.objects.new(g['name'],me);sc.collection.objects.link(o);o.parent=pivot;me.materials.append(white if k['color']=='WHITE' else black)
 for i,t in enumerate(A['times']):pivot.rotation_euler.x=float(A['key_angles'][i,k['key_index']]);pivot.keyframe_insert(data_path='rotation_euler',index=0,frame=1+t*FPS)
 linear(pivot)
def cube(name,loc,scale,material):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(material);return o
xs=[v[0] for k in KEYS for g in k['geometry'] for v in g['vertices']];cx=(max(xs)+min(xs))/2;width=max(xs)-min(xs)
cube('DISPLAY_ONLY_BACK_RAIL',(cx,.14,-.016),(width+.025,.045,.045),case);cube('DISPLAY_ONLY_UNDER_KEY_BED',(cx,.06,-.045),(width+.025,.18,.025),case)
def camera(name,eye,target,scale):
 d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=scale;d.clip_start=.001;d.clip_end=10;o=bpy.data.objects.new(name,d);sc.collection.objects.link(o);o.location=eye;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
camera('PRODUCT_DUAL_HAND',(cx,-.62,.69),(cx,-.006,.015),width+.06)
camera('CONTACT_SIDE',(0,-.52,.255),(0,.02,.02),.89)
camera('SKIN_REVIEW',(.015,-.5,.72),(.015,-.012,.028),.88)
def area(name,loc,power,size,col):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=col;o=bpy.data.objects.new(name,d);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
area('Large soft key',(-.35,-.35,.8),55,1,(1,.92,.86));area('Soft fill',(.45,-.05,.65),35,.8,(.85,.91,1));area('Rear rim',(0,.35,.7),38,.7,(1,.96,.9))
sc.world=bpy.data.worlds.new('Neutral studio');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.11,.13,.16,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.35
sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.render.resolution_x=1600;sc.render.resolution_y=900;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.camera=bpy.data.objects['PRODUCT_DUAL_HAND'];sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
sc.frame_set(43);dest=P/'HAND_POSTURE_CONTACT_REFINED_DESIGN_ONLY_R1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest));bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False)
V={s:[] for s in ['R','L']};PAD={s:[] for s in ['R','L']};parity={s:[] for s in ['R','L']};skin_drift={s:[] for s in ['R','L']}
for i,t in enumerate(A['times']):
 f=1+t*FPS;bpy.context.scene.frame_set(int(f),subframe=f-int(f))
 for s,c in RIG.items():
  v,_=h.coords(bpy.data.objects[c['mesh']]);V[s].append(v);pp=np.array([list(bpy.data.objects['PAD_'+s+'_'+d].matrix_world.translation) for d in DIGITS]);PAD[s].append(pp);parity[s].append(float(np.max(np.linalg.norm(pp-A[s+'_pads'][i],axis=1))*1000));skin_drift[s].append(float(max(np.linalg.norm(pp[j]-v[row['mesh_vertex']])*1000 for j,row in enumerate(MARKERS[s]))))
np.savez_compressed(P/'evaluated_candidate.npz',**{s+'_verts':np.array(V[s]) for s in V},**{s+'_pads':np.array(PAD[s]) for s in PAD},times=A['times'],key_angles=A['key_angles'])
identity={}
for s,c in RIG.items():
 rig=bpy.data.objects[c['rig']];ob=bpy.data.objects[c['mesh']];name=rig.animation_data.action.name;rig.animation_data_clear();rig.parent=None;rig.matrix_world=Matrix.Identity(4);h.neutral(rig)
 if added_material_slot[s]:ob.data.materials.clear()
 actual=digest(intrinsic(ob,rig));identity[s]={'new_action':name,'intrinsic_static_identity':'MATCHED' if actual==c['static_identity'] else 'MISMATCH','vertex_count':len(ob.data.vertices),'bone_count':len(rig.data.bones),'pad_FK_saved_reopened_max_error_mm':max(parity[s]),'rigid_marker_vs_skin_vertex_max_mm':max(skin_drift[s]),'NaN_Inf':not bool(np.isfinite(V[s]).all())};assert actual==c['static_identity'],('STATIC_CHANGED',s);assert max(parity[s])<.02
dump('CANDIDATE_IDENTITY_R1.json',{'hands':identity,'candidate_sha256':sha(dest),'PianoVAM_Action_present':False,'static_material_override_only':True,'save_reopen_verified':True,'verification_reset_not_saved':True})
print('CANDIDATE_VERIFIED',json.dumps(identity),flush=True)
