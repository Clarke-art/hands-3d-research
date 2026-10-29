import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy
from mathutils import Vector
P=read(OUT/'TEMP_PALMAR_ROOT_DONOR_TRANSFER_PROBE_R1.json');assert not P['scope_blocker'],'normal-context-required-closure-overlap blocks probe'
src=ROOT/'production_spec/stage5_production_rig/geometry_propagation_after_donor_transfer_r1/payload.py'
reuse(src,['plain','props','rna','object_payload','rig_payload','material_payload','snapshot'],globals())
bpy.ops.wm.open_mainfile(filepath=str(R2),load_ui=False,use_scripts=False);before=snapshot();ob=bpy.data.objects[before['object_name']];inv=ob.matrix_world.inverted();original=before['coordinates_world_m'];ids=set(P['moved_vertex_ids'])
assert original==[[x/1000 for x in p] for p in P['baseline_world_mm']] or max((Vector(a)-Vector([x/1000 for x in b])).length for a,b in zip(original,P['baseline_world_mm']))<1e-12
for i in ids:ob.data.vertices[i].co=inv@(Vector(P['world_mm'][i])/1000)
ob.data.update();scene=bpy.context.scene;scene['DESIGN_ONLY']=True;scene['NOT_PRODUCTION']=True;scene['NOT_APPROVED']=True;scene['PALMAR_FEASIBILITY_SOURCE']=PHASE
path=OUT/'TEMP_PALMAR_ROOT_DONOR_TRANSFER_PROBE_R1.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(path),copy=True,compress=False)
bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);after=snapshot();changed=[k for k in before['protected'] if before['protected'][k]!=after['protected'][k]]
assert not changed,changed
assert all(original[i]==after['coordinates_world_m'][i] for i in range(len(original)) if i not in ids)
assert all(original[i]==after['coordinates_world_m'][i] for i in P['normal_position_locked_vertex_ids'])
P['world_mm']=[[x*1000 for x in p] for p in after['coordinates_world_m']];P['saved_float32_roundtrip']=True;P['probe_blend']=ref(path);dump('TEMP_PALMAR_ROOT_DONOR_TRANSFER_PROBE_R1.json',P)
dump('TEMP_PROBE_PAYLOAD_PRESERVATION_R1.json',{'status':'PASS','all_protected_payloads_exact':True,'protected_fields':list(before['protected']),'outside_write_set_positions_exact':True,'excluded_normal_positions_exact':True,'topology_counts':after['protected']['mesh']['counts'],'smooth_sharp_custom_normal_state_exact':True,'UV_materials_weights_rigs_groups_exact':True,'source':ref(R2),'temporary_probe':ref(path),'production_save_calls':0,'temporary_probe_save_calls':1,'temporary_geometry_vertex_writes':len(ids),'pose_setters':0,'deformation_evaluations':0,'bone_count':len(next(iter(after['protected']['rigs'].values()))['bones'])})
print('Temporary design-only probe clean-reopen protected payload PASS;',len(ids),'position writes; production save0',flush=True)
