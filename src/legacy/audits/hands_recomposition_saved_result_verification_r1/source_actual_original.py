import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from support import *
import bpy,numpy as np,math
from persistence import atomic_record,atomic_json,load_record
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(OLD));import performance_core as c
I=read(O/'INPUT_BINDINGS.json');man=I['source_scene'];P=read(O/'POLICY.json')
helpers=ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1'
functions_from(helpers/'blender_preflight.py',['digest','native','settime','coords'],globals())
functions_from(MODEL/'whole_phrase_model.py',['component_planes'],globals())
rois=read(helpers/'DIGIT_SKIN_ROI.json')
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False);assert not bpy.data.libraries
sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
rig=bpy.data.objects[man['mapping']['R']['rig']];mesh=bpy.data.objects[man['mapping']['R']['mesh']]
identity=digest(native(mesh,rig));assert identity==I['native_sha256']
S,_=load_record('SOURCE_LOCAL_STATES.npz');rows=[];vs=[];F=None
group={g.index:g.name for g in mesh.vertex_groups}
ids=np.array([v.index for v in mesh.data.vertices if sum(g.weight for g in v.groups if group[g.group].startswith('LITTLE_'))>.05])
for ix,t in enumerate(S['times']):
 settime(sc,float(t));original=[b.matrix_basis.copy() for b in rig.pose.bones];action=rig.animation_data.action
 baseV,F=coords(mesh);rig.animation_data.action=None
 for n,r in zip(c.SETUPS['R','LITTLE'][0],c.joint_mats('R','LITTLE',np.radians(S['q'][ix,4]))):
  rig.pose.bones[n].rotation_mode='QUATERNION';rig.pose.bones[n].rotation_quaternion=Matrix(r.tolist()).to_quaternion()
 bpy.context.view_layer.update();V,F=coords(mesh);ka=S['key_angles'][ix];key=c.KEYS[I['source'][-1]['key_index']];pv=np.array(key['press_pivot'])
 local=c.axisrot(-ka[key['key_index']],key['press_axis'])@(V[1747]-pv)+pv
 surf=min(key['key_top_playable_surface'],key=lambda s:np.linalg.norm(local[:2]-np.clip(local[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']])))
 h=float(np.linalg.norm(local[:2]-np.clip(local[:2],[surf['xmin'],surf['ymin']],[surf['xmax'],surf['ymax']]))*1000);gap=float((local[2]-surf['z'])*1000)
 tree=BVHTree.FromPolygons([Vector(v) for v in V],rois['LITTLE']['faces'],epsilon=0);baseTree=BVHTree.FromPolygons([Vector(v) for v in baseV],rois['LITTLE']['faces'],epsilon=0)
 peak=0.;witness=None;parity=0.
 for k in c.KEYS:
  if k['key_index']==key['key_index']:continue
  for g in k['geometry']:
   pl=component_planes(g);pivot=np.array(k['press_pivot']);R=c.axisrot(ka[k['key_index']],k['press_axis']);vlocal=(V[ids]-pivot)@R+pivot
   depth=-np.max(vlocal@pl[:,:3].T-pl[:,3],axis=1)*1000;mx=float(depth.max())
   if mx>peak:
    peak=mx;vid=int(ids[depth.argmax()]);witness=dict(key=k['note_name'],vertex=vid,depth_mm=mx)
   if mx>-.2:
    ob=next(o for o in sc.objects if o.type=='MESH' and o.get('FROZEN_KEY_INDEX')==k['key_index'] and g['name'] in o.name)
    actual=np.array([list(<REDACTED_EMAIL>) for v in ob.data.vertices]);expected=(np.array(g['vertices'])-pivot)@R.T+pivot;parity=max(parity,float(abs(actual-expected).max()*1000))
    kt=BVHTree.FromPolygons([Vector(v) for v in actual],[list(p.vertices) for p in ob.data.polygons],epsilon=0)
    if witness and witness['key']==k['note_name']:witness['skin_key_face_pairs']=len(tree.overlap(kt))
 pairs={};basepairs={}
 for d in c.DIGITS[:-1]:
  pairs[d]=len(tree.overlap(BVHTree.FromPolygons([Vector(v) for v in V],rois[d]['faces'],epsilon=0)))
  basepairs[d]=len(baseTree.overlap(BVHTree.FromPolygons([Vector(v) for v in baseV],rois[d]['faces'],epsilon=0)))
 rows.append(dict(time=float(t),contact_h_mm=h,contact_gap_mm=gap,contact_pass=h<=.03 and abs(gap)<=3,active_skin_wrong_key_depth_mm=peak,witness=witness,little_other_pairs=pairs,baseline_little_other_pairs=basepairs,local_geometry_pass=peak<=.5 and all(pairs[d]<=basepairs[d] for d in pairs),world_matrix_error_mm=float(abs(np.array(rig.matrix_world)-S['world'][ix]).max()*1000),real_key_parity_mm=parity))
 vs.append(V);print('REAL_SOURCE_LOCAL',rows[-1],flush=True)
 for b,m in zip(rig.pose.bones,original):b.matrix_basis=m
 rig.animation_data.action=action
assert digest(native(mesh,rig))==identity and sha(man['path'])==man['sha256']
atomic_record('SOURCE_LOCAL_REAL_SKIN.npz',dict(times=S['times'],vertices=vs),dict(record_type='ACTUAL_BLENDER_STATIC_CAPABILITY_ONLY',no_action_or_blend_saved=True))
passed=all(r['contact_pass'] and r['local_geometry_pass'] for r in rows)
atomic_json('SOURCE_LOCAL_ACTUAL_GATE.json',dict(pass_=passed,rows=rows,source_complete_repair=False,stage2_authorized_by_local_evidence=passed,native_unchanged=True,scope='Three active little finger states; other source defects remain; not a continuous safe source'))
protect()
