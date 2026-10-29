import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy
from mathutils import Vector
P=read(OUT/'TEMP_DONOR_TRANSFER_DESIGN_ONLY.json');S=read(OUT/'RAW_SOURCE_GEOMETRY.json')['stages']['R2_PRODUCTION'];path=ROOT/S['input']['path']
def protected(ob):
 me=ob.data
 return {'counts':[len(me.vertices),len(me.edges),len(me.polygons)],'faces':[list(f.vertices) for f in me.polygons],'edges':[list(e.vertices) for e in me.edges],'UV':{u.name:[list(z.uv) for z in u.data] for u in me.uv_layers},'material_assignments':[f.material_index for f in me.polygons],'materials':[m.name if m else None for m in me.materials],'weights':[[[g.group,float(g.weight)] for g in v.groups] for v in me.vertices],'vertex_group_names':[g.name for g in ob.vertex_groups],'smooth':[f.use_smooth for f in me.polygons],'object_world':[list(r) for r in ob.matrix_world],'armatures':{o.name:{'world':[list(r) for r in o.matrix_world],'bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local),'matrix':[list(r) for r in b.matrix_local],'parent':b.parent.name if b.parent else None,'deform':b.use_deform} for b in o.data.bones},'pose':{b.name:{'matrix_basis':[list(r) for r in b.matrix_basis],'location':list(b.location),'scale':list(b.scale),'quaternion':list(b.rotation_quaternion)} for b in o.pose.bones}} for o in bpy.data.objects if o.type=='ARMATURE'}}
bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);ob=bpy.data.objects['Hand  - Realistic'];before=protected(ob);original=[list(<REDACTED_EMAIL>) for v in ob.data.vertices]
inv=ob.matrix_world.inverted()
for i in P['moved_vertex_ids']:ob.data.vertices[i].co=inv@(Vector(P['world_mm'][i])/1000)
ob.data.update();ob['NOT_PRODUCTION']=True;ob['NOT_APPROVED']=True;ob['DESIGN_ONLY_SOURCE']=PHASE
outpath=OUT/'TEMP_DONOR_TRANSFER_DESIGN_ONLY.blend';bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(outpath),copy=True,compress=False)
bpy.ops.wm.open_mainfile(filepath=str(outpath),load_ui=False,use_scripts=False);ob=bpy.data.objects['Hand  - Realistic'];after=protected(ob);assert before==after
saved=[list(<REDACTED_EMAIL>) for v in ob.data.vertices];moved=set(P['moved_vertex_ids'])
assert all(original[i]==saved[i] for i in range(len(saved)) if i not in moved)
P['world_mm']=[[z*1000 for z in p] for p in saved];P['saved_float32_roundtrip_verified']=True;P['blend_sha256']=sha(outpath);dump('TEMP_DONOR_TRANSFER_DESIGN_ONLY.json',P)
dump('PROBE_PROTECTED_PAYLOAD_VERIFICATION.json',{'all_protected_payloads_identical':True,'fields':list(before),'outside_write_set_exactly_unchanged':True,'source_path':str(path.relative_to(ROOT)),'temporary_probe_path':str(outpath.relative_to(ROOT)),'NOT_PRODUCTION':True,'NOT_APPROVED':True,'source_blend_save_count':0,'temporary_probe_blend_save_count':1})
print('PROBE saved and independently reopened; protected payload exact',flush=True)
