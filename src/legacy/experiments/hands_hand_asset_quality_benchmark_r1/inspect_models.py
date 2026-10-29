import bpy,sys,os,json,hashlib
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
os.environ.update(TEMP=str(OUT),TMP=str(OUT))
def save(n,x):
 if (OUT/n).exists():return
 with (OUT/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2,ensure_ascii=False)
def vec(v):return list(v)
def inspect():
 data=[]
 for ob in bpy.context.scene.objects:
  row=dict(name=ob.name,type=ob.type,matrix_world=[list(r) for r in ob.matrix_world],dimensions=list(ob.dimensions),parent=ob.parent.name if ob.parent else None)
  if ob.type=='MESH':
   me=ob.data;me.calc_loop_triangles()
   row.update(vertices=len(me.vertices),faces=len(me.polygons),triangles=len(me.loop_triangles),face_sizes={str(n):sum(len(f.vertices)==n for f in me.polygons) for n in sorted(set(len(f.vertices) for f in me.polygons))},vertex_groups=[g.name for g in ob.vertex_groups],modifiers=[dict(name=m.name,type=m.type,object=m.object.name if m.type=='ARMATURE' and m.object else None) for m in ob.modifiers],shape_keys=[k.name for k in me.shape_keys.key_blocks] if me.shape_keys else [],smooth_count=sum(f.use_smooth for f in me.polygons),uv_layers=len(me.uv_layers),custom_normals=me.has_custom_normals)
  if ob.type=='ARMATURE':
   row['bones']=[dict(name=b.name,parent=b.parent.name if b.parent else None,head=list(b.head_local),tail=list(b.tail_local),matrix=[list(r) for r in b.matrix_local],deform=b.use_deform,rotation_mode=ob.pose.bones[b.name].rotation_mode,rotation_euler=list(ob.pose.bones[b.name].rotation_euler),constraints=[dict(type=c.type,name=c.name) for c in ob.pose.bones[b.name].constraints]) for b in ob.data.bones]
  data.append(row)
 return data
def export(ob,name):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles()
 np.savez(OUT/(name+'.npz'),V=np.array([list(<REDACTED_EMAIL>) for v in me.vertices]),T=np.array([list(t.vertices) for t in me.loop_triangles]),F=np.array([list(f.vertices) for f in me.polygons],dtype=object))
 ev.to_mesh_clear()
source=ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance/STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_DESIGN_ONLY.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
assert not bpy.data.libraries
for seq in [bpy.data.images,bpy.data.sounds,bpy.data.fonts]:
 for b in seq:
  if getattr(b,'filepath','') and not getattr(b,'packed_file',None) and b.filepath not in ['<builtin>','Bfont']:
   p=Path(bpy.path.abspath(b.filepath)).resolve();assert p.is_relative_to(ROOT),str(p)
sc=bpy.data.scenes['STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_DESIGN_ONLY'];bpy.context.window.scene=sc;sc.frame_set(157)
mesh=bpy.data.objects['RIGHT_HAND_OFFICIAL_L1_PRODUCT_MESH.002'];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG.002']
export(mesh,'baseline_C1_2p6')
save('BASELINE_INVENTORY.json',[x for x in inspect() if x['name'] in [mesh.name,rig.name]])
save('BASELINE_JOINTS_C1.json',{b.name:dict(head=list(<REDACTED_EMAIL>),tail=list(<REDACTED_EMAIL>)) for b in rig.pose.bones})
rig.data.pose_position='REST';bpy.context.view_layer.update();export(mesh,'baseline_REST')
save('BASELINE_JOINTS_REST.json',{b.name:dict(head=list(<REDACTED_EMAIL>_local),tail=list(<REDACTED_EMAIL>_local)) for b in rig.data.bones})
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(OUT/'sources/hand-posable.glb'),import_pack_images=True)
assert not bpy.data.libraries
save('CANDIDATE_INVENTORY.json',inspect())
for ob in bpy.context.scene.objects:
 if ob.type=='MESH' and ob.name=='Avery | anatomical body':export(ob,'candidate_REST')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'CANDIDATE_IMPORTED_UNALTERED.blend'),check_existing=False)
print('INSPECTION_FINISHED',flush=True)
