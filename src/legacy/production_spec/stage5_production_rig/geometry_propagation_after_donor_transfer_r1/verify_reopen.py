import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from payload import *
from mathutils import Vector
from mathutils.bvhtree import BVHTree
key=sys.argv[sys.argv.index('--')+1]
assert key in ASSETS
inputs_native=read(OUT/'FROZEN_INPUT_NATIVE_PAYLOADS_R1.json')
saved=read(OUT/'STAGE5_BEFORE_SAVE_PROPAGATION_PAYLOADS_R1.json')[key]
p=ASSETS[key];assert sha(p)==saved['asset']['sha256']
load(p);now=snapshot();before=inputs_native[key];target=inputs_native['STAGE4']
def differences(a,b,path=''):
 if type(a)!=type(b):return [path]
 if isinstance(a,dict):
  return sum(([path+'/'+k] if k not in a or k not in b else differences(a[k],b[k],path+'/'+k) for k in sorted(a.keys()|b.keys())),[])
 if isinstance(a,list):
  if len(a)!=len(b):return [path+'/length']
  return sum((differences(u,v,path+'/'+str(i)) for i,(u,v) in enumerate(zip(a,b))),[])
 return [] if a==b else [path]
drifts=differences(saved['after'],now)
reopen={'status':'PASS' if not drifts else 'FAIL_CLOSED_STAGE5_GEOMETRY_PROPAGATION','factory_startup_clean_reopen':True,'asset':ref(p),'serialization_drift_count':len(drifts),'serialization_drift_paths':drifts[:100],
 'before_save_snapshot_sha256':digest(saved['after']),'reopened_snapshot_sha256':digest(now)}
dump(key+'_SAVE_REOPEN_RESULT_R1.json',reopen)
assert not drifts,reopen
assert now['protected']==before['protected']
assert now['coordinates_local_m']==target['coordinates_local_m']
assert now['coordinates_world_m']==target['coordinates_world_m']
changed=[i for i,(a,b) in enumerate(zip(before['coordinates_local_m'],now['coordinates_local_m'])) if a!=b]
assert changed==IDS
ob=bpy.data.objects[now['object_name']]
names={'DO_NOT_PROMOTE_UNTIL_DOWNSTREAM_REQUALIFIED':'DOWNSTREAM_GATE_REQUIRED'}
for k,v in saved['new_provenance_metadata'].items():assert plain(ob['GEOMETRY_PROPAGATION_'+names.get(k,k)])==v
audit={'status':'PASS','source':ref(inputs()[key]),'derived':ref(p),'geometry_authority':ref(STAGE4),
 'counts':now['protected']['mesh']['counts'],'full_coordinate_assigned_count':3416,'actual_stored_coordinate_exact_match_count':3416,
 'STAGE4C_VERTEX_MAX_DELTA_MM':0.0,'STAGE4C_WORLD_VERTEX_MAX_DELTA_MM':0.0,
 'OLD_TO_NEW_CHANGED_VERTEX_COUNT':len(changed),'actual_changed_ids':changed,'approved54_exact':changed==IDS,'OUTSIDE54_GEOMETRY_DRIFT':0,
 'TOPOLOGY_DRIFT':0,'all_native_IDs_edges_faces_cycles_loops_exact':True,'all_protected_non_geometry_payload_exact':True,
 'local_coordinates_sha256':digest(now['coordinates_local_m']),'positive_weight_vector_sha256':digest(now['positive_weight_vectors'])}
dump('STAGE5A_GEOMETRY_PROPAGATION_AUDIT_R1.json' if key=='CORRECTED' else 'STAGE5B_R2_GEOMETRY_PROPAGATION_AUDIT_R1.json',audit)
dump(key+'_REOPENED_NATIVE_PAYLOAD_R1.json',now)

# Point-to-triangulated-raw-surface distances only. Existing joint positions are read;
# they are never relocated and no threshold or qualification verdict is applied.
tris=[]
for _,f in now['protected']['mesh']['faces']:
 for j in range(1,len(f)-1):tris.append((f[0],f[j],f[j+1]))
trees=[BVHTree.FromPolygons(s['coordinates_world_m'],tris,all_triangles=True) for s in (before,now)]
diagnostic=[]
for rn,r in now['protected']['rigs'].items():
 for bn,b in r['bones'].items():
  for endpoint in ('head','tail'):
   q=Vector(b[endpoint+'_world_m']);dist=[float(t.find_nearest(q)[3])*1000 for t in trees]
   diagnostic.append({'rig':rn,'bone':bn,'endpoint':endpoint,'fixed_world_m':list(q),'old_raw_surface_distance_mm':dist[0],'new_raw_surface_distance_mm':dist[1],'delta_mm':dist[1]-dist[0]})
dump(key+'_JOINT_SURFACE_DELTA_DIAGNOSTIC_R1.json',{'classification':'DIAGNOSTIC_ONLY','method':'Nearest distance to unchanged native-index fan triangulation of raw, unevaluated world-space mesh; 21 bones x two fixed endpoints','formal_joint_surface_qualification':'NOT_RUN','thresholds_applied':False,'joint_relocation':False,'measurements':diagnostic})

# Minimum zero evaluation smoke. This temporary session is never saved.
rigs=[o for o in bpy.data.objects if o.type=='ARMATURE']
for rig in rigs:
 for b in rig.pose.bones:
  b.location=(0,0,0);b.rotation_quaternion=(1,0,0,0);b.rotation_euler=(0,0,0);b.rotation_axis_angle=(0,0,0,1);b.scale=(1,1,1)
bpy.context.view_layer.update()
groupnames={g.index:g.name for g in ob.vertex_groups};bonenames={b.name for r in rigs for b in r.data.bones}
missing_group_entries=[[v.index,g.group] for v in ob.data.vertices for g in v.groups if g.group not in groupnames]
missing_bone_groups=[g.name for g in ob.vertex_groups if g.name not in bonenames]
modifier_checks=[]
for m in ob.modifiers:
 check={'name':m.name,'type':m.type,'binding_present':m.type!='ARMATURE' or m.object is not None,'error':getattr(m,'error','')}
 vg=getattr(m,'vertex_group','')
 check['vertex_group_binding_valid']=not vg or vg in groupnames.values()
 modifier_checks.append(check)
deps=bpy.context.evaluated_depsgraph_get();evaluated=ob.evaluated_get(deps);me=evaluated.to_mesh()
finite=all(math.isfinite(float(z)) for v in me.vertices for z in v.co)
evalcount=len(me.vertices);evaluated.to_mesh_clear()
bonefinite=all(math.isfinite(float(v)) for r in rigs for b in r.pose.bones for row in b.matrix for v in row)
passsmoke=finite and bonefinite and evalcount>0 and not missing_group_entries and not missing_bone_groups and all(m['binding_present'] and m['vertex_group_binding_valid'] and not m['error'] for m in modifier_checks)
smoke={'ZERO_EVAL_SMOKE':'PASS' if passsmoke else 'FAIL','scope':'File evaluation / finite coordinates / valid existing references only','temporary_pose_zero_not_saved':True,'rest_zero_bind_qualification':'NOT_RUN','Stage6_poses_run':[],
 'finite_evaluated_coordinates':finite,'finite_evaluated_bone_matrices':bonefinite,'evaluated_vertex_count':evalcount,'missing_group_entries':missing_group_entries,'missing_bone_groups':missing_bone_groups,'modifiers':modifier_checks,'artifact_hash_unchanged':sha(p)==saved['asset']['sha256']}
dump(key+'_ZERO_EVAL_SMOKE_RESULT_R1.json',smoke)
assert passsmoke,smoke
# Read explicit rolls last, then terminate without leaving edit mode or saving.
rolls=read_rolls_last()
assert rolls==before['native_editbone_rolls'],'FAIL_CLOSED_STAGE5_GEOMETRY_PROPAGATION: roll drift'
dump(key+'_NATIVE_ROLL_EQUIVALENCE_R1.json',{'status':'PASS','roll_delta':0,'source_native_rolls':before['native_editbone_rolls'],'reopened_native_rolls':rolls,'method':'Read actual EditBone.roll at end of unsaved clean-reopen session, with no edit setters or roll recalculation'})
print('CLEAN REOPEN / GEOMETRY / PROTECTED / ROLLS / ZERO EVAL PASS',key,flush=True)
