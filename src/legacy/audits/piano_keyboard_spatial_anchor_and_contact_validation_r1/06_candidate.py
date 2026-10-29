import bpy,sys,json,hashlib,ast,importlib.util
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def read(n):return json.loads((P/n).read_text(encoding='utf-8-sig'))
def dump(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
sp=importlib.util.spec_from_file_location('identity',ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h)
for file,fn in [(ROOT/'audits/pianovam_first_web_corrective_ab_isolation_r1/isolate.py','action_payload'),(P/'04_hands.py','intrinsic')]:
 tree=ast.parse(file.read_text(encoding='utf-8-sig'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==fn],type_ignores=[]),fn,'exec'))
ex=read('HAND_EXTRACTION_R1.json');keys=read('KEYBOARD_88_KEY_TABLE_R1.json')['keys'];A=np.load(P/'spatial_evaluations.npz');marker=read('FINGERTIP_CONTACT_MARKERS_R1.json')['markers'];bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
sc.render.fps=30;sc.frame_start=1;sc.frame_end=210;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
sc['PHASE']='PIANO_KEYBOARD_SPATIAL_ANCHOR_AND_CONTACT_VALIDATION_R1';sc['USAGE_SCOPE']='INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY';sc['LICENSE']='CC BY-NC-SA 4.0';sc['NOT_PRODUCTION']=True;sc['STATUS']='FAILED_CONTACT_FIT_CANDIDATE_FOR_HUMAN_REVIEW';sc['PERFORMANCE_TIMELINE']='PERFORMANCE_TIMELINE_R1.json'
def linear(obj):
 for l in obj.animation_data.action.layers:
  for s in l.strips:
   for b in s.channelbags:
    for f in b.fcurves:
     for k in f.keyframe_points:k.interpolation='LINEAR'
for side,c in ex['cfg'].items():
 with bpy.data.libraries.load(str(ROOT/c['baseline']),link=False) as (a,b):b.objects=[c['mesh'],c['rig']]
 for ob in b.objects:
  if ob and not ob.users_collection:sc.collection.objects.link(ob)
 rig=bpy.data.objects[c['rig']];h.neutral(rig)
 with bpy.data.libraries.load(str(ROOT/c['source']),link=False) as (a,b):b.actions=[c['action']]
 act=bpy.data.actions[c['action']];assert digest(action_payload(act))==ex['action_hashes'][side]
 rig.animation_data_create();rig.animation_data.action=act;rig.animation_data.action_slot=act.slots[0]
 root=bpy.data.objects.new('AUDIT_ONLY_KEYBOARD_ROOT_'+side,None);sc.collection.objects.link(root);Q=Matrix(ex['frames'][side]['rotation']);w=Vector(ex['frames'][side]['native_wrist']);root.rotation_mode='QUATERNION';root.rotation_quaternion=Q.to_quaternion();root['translation_only_dynamic']=True
 rig.parent=root;rig.matrix_parent_inverse=Matrix.Identity(4)
 for i,t in enumerate(A[side+'_roots']):root.location=Vector(t)-Q@w;root.keyframe_insert(data_path='location',frame=1+i*.5)
 linear(root)
 for row in marker[side]:
  o=bpy.data.objects.new('VIRTUAL_PAD_'+side+'_'+row['digit'],None);sc.collection.objects.link(o);o.empty_display_type='SPHERE';o.empty_display_size=.002;o.parent=rig;o.parent_type='BONE';o.parent_bone=row['distal_frame'];o.matrix_parent_inverse=Matrix.Identity(4);o.location=Vector(row['local_pad_point'])-Vector((0,rig.data.bones[row['distal_frame']].length,0));o['AUDIT_ONLY']=True;o['canonical_mesh_vertex']=row['mesh_vertex']
for k in keys:
 pv=np.array(k['press_pivot']);pivot=bpy.data.objects.new(k['semantic_identity'],None);sc.collection.objects.link(pivot);pivot.location=pv;pivot['midi_note']=k['midi_note'];pivot['key_index']=k['key_index'];pivot['source_object']=k['source_object'];pivot['KEY_MOTION_SOURCE']='MIDI_EVENT_TIMELINE'
 for g in k['geometry']:
  me=bpy.data.meshes.new(g['name']);ind=g['triangles'];me.from_pydata((np.array(g['vertices'])-pv).tolist(),[],[ind[j:j+3] for j in range(0,len(ind),3)]);ob=bpy.data.objects.new(g['name'],me);sc.collection.objects.link(ob);ob.parent=pivot;ob.color=(.82,.80,.75,1) if k['color']=='WHITE' else (.035,.045,.055,1)
 for i,a in enumerate(A['angles'][:,k['key_index']]):pivot.rotation_euler.x=float(a);pivot.keyframe_insert(data_path='rotation_euler',index=0,frame=1+i*.5)
 linear(pivot)
def camera(name,eye,target,scale):
 d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=scale;d.clip_start=.001;d.clip_end=10;o=bpy.data.objects.new(name,d);sc.collection.objects.link(o);o.location=eye;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
fullx=[v[0] for k in keys for g in k['geometry'] for v in g['vertices']];cx=(max(fullx)+min(fullx))/2
camera('PIANO_PLAYER_VIEW',(cx,-.85,.66),(cx,-.025,0),1.40)
allv=np.concatenate([A[s+'_verts'].reshape(-1,3) for s in ['L','R']]);mid=(allv.min(0)+allv.max(0))/2
camera('TEACHING_TOP_OBLIQUE',(float(mid[0]),-.42,.85),(float(mid[0]),-.025,0),.88)
camera('CONTACT_CLOSE',(float(mid[0]),-.38,.18),(float(mid[0]),.035,0),.62)
sc.camera=bpy.data.objects['PIANO_PLAYER_VIEW'];sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1400;sc.render.resolution_y=780;sc.render.resolution_percentage=100;sc.display.shading.color_type='OBJECT';sc.display.shading.light='STUDIO';sc.display.shading.studio_light='paint.sl';sc.display.shading.show_shadows=True;sc.display.shading.show_cavity=False;sc.world=bpy.data.worlds.new('Audit World');sc.world.color=(.065,.085,.115);sc.display.shading.background_type='WORLD';sc.view_settings.view_transform='Standard';sc.frame_set(1)
dest=P/'PIANO_KEYBOARD_SPATIAL_ANCHOR_VALIDATION_CANDIDATE_R1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest));bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False)
identity=read('ACTION_IDENTITY_R1.json');errs={s:[] for s in ['R','L']};paderrs={s:[] for s in ['R','L']}
for i in range(421):
 bpy.context.scene.frame_set(1+i//2,subframe=(i%2)*.5)
 for s,c in ex['cfg'].items():
  ob=bpy.data.objects[c['mesh']];v,_=h.coords(ob);errs[s].append(float(np.max(np.abs(v-A[s+'_verts'][i]))*1000))
  for row in marker[s]:paderrs[s].append(float((bpy.data.objects['VIRTUAL_PAD_'+s+'_'+row['digit']].matrix_world.translation-Vector(A[s+'_pads'][i,row['finger']-1])).length*1000))
for s,c in ex['cfg'].items():
 ob=bpy.data.objects[c['mesh']];rig=bpy.data.objects[c['rig']];a=rig.animation_data.action;actual=digest(action_payload(a));assert actual==ex['action_hashes'][s];assert max(errs[s])<.005;assert max(paderrs[s])<.005
 rig.parent=None;rig.animation_data.action=None;h.neutral(rig);d=digest(intrinsic(ob,rig));assert d==read('STATIC_COMPONENT_DIGESTS_R1.json')[s],('STATIC_DRIFT',s)
 identity['hands'][s].update(saved_reopened_action_sha256=actual,static_components='MATCH',evaluated_421_max_error_mm=max(errs[s]),marker_binding_max_error_mm=max(paderrs[s]))
identity['phase']='SAVED_AND_REOPENED_VERIFIED';identity['candidate_sha256']=hashlib.sha256(dest.read_bytes()).hexdigest();dump('ACTION_IDENTITY_R1.json',identity)
dump('CANDIDATE_VERIFICATION_R1.json',{'status':'PASS','source_mesh_rig_weights_corrective_rest_unchanged':True,'action_identity':'MATCH_BOTH','internal_deformation_matches_isolated_421':True,'key_count':88,'virtual_markers':10,'camera_count':3,'file':dest.name,'note':'Verification detached parents in memory only; verification state was never saved.'})
print('CANDIDATE_SAVE_REOPEN_PASS',errs['R'] and max(errs['R']),max(errs['L']),flush=True)
