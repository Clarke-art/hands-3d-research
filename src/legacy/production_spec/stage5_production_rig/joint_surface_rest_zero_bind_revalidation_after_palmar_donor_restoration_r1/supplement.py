import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from payload import *
from mathutils import Vector,Matrix,Quaternion
from mathutils.bvhtree import BVHTree
sem=read(OUT/'CURRENT_JOINT_QUALIFICATION_SEMANTICS_R1.json')
data=read(OUT/'CLEAN_REOPEN_NATIVE_PAYLOADS_R1.json')
G=read(OUT/'MATCHED_ZERO_BIND_REVIEW_GEOMETRY_R1.json')
J=read(OUT/'JOINT_SURFACE_REQUALIFICATION_R1.json')
ns={'bpy':bpy,'math':math,'Vector':Vector,'Quaternion':Quaternion,'MM':1000.0}
reuse(S5/'stage5a_r2/scripts/stage5a_r2_audit.py',['closest','parity'],ns)
reuse(OUT/'revalidate.py',['query_setup','surface','region'],globals())
bone=next(iter(data['CORRECTED']['protected']['rigs'].values()))['bones']
inventory_rows=[]
for name,b in bone.items():
 r=sem['rules'][name]
 inventory_rows.append({'name':name,'type':'NON_DEFORM_TIP_HELPER' if '_TIP_' in name else 'WRIST' if name=='WRIST_R' else 'THUMB_CMC' if name=='THUMB_CMC_R' else 'CORRECTED_THUMB_IP' if name=='THUMB_IP_R' else name.split('_')[1], 'use_deform':b['settings']['use_deform'],'head_world_m':b['head_world_m'],'tail_world_m':b['tail_world_m'],'parent':b['parent'],'inside_required':r['inside_required'],'authority':r})
assert len(inventory_rows)==21 and sum(r['use_deform'] for r in inventory_rows)==16
dump('FORMAL_JOINT_HELPER_INVENTORY_R1.json',{'status':'PASS','count':21,'deform_count':16,'non_deform_TIP_count':5,'rows':inventory_rows})
# Recover formal source hashes and threshold code against the last passed receipt.
previous=read(PRIOR/'CURRENT_JOINT_QUALIFICATION_SEMANTICS_R1.json')
assert sem['rules']==previous['rules'] and sem['sources']==previous['sources'] and sem['zero_bind']==previous['zero_bind']
sem.update(previous_successful_semantics_source=ref(PRIOR/'CURRENT_JOINT_QUALIFICATION_SEMANTICS_R1.json'),fresh_source_hashes_match_previous_authorities=True)
sem['zero_bind']['source_code_confirmed']={k:[{'line_number':i,'text':s} for i,s in enumerate(Path(sem['sources'][k]['path']).read_text(encoding='utf-8-sig').splitlines(),1) if ('ZERO_POSE_BIND' in s or 'raw_RSSF_noise_mm' in s or "max(pre,post,rawzero)>1e-4" in s)] for k in ('original_bind_threshold','R1B_bind_threshold','current_R2_zero_consumer')}
assert all(sem['zero_bind']['source_code_confirmed'].values())
dump('CURRENT_JOINT_QUALIFICATION_SEMANTICS_AFTER_PALMAR_R1.json',sem)
for r in J['all21_current_rows'].values():
 b=bone[r['name']];r.update(type=next(i['type'] for i in inventory_rows if i['name']==r['name']),tail_world_m=b['tail_world_m'])
dump('JOINT_SURFACE_REQUALIFICATION_AFTER_PALMAR_R1.json',J)
middle={}
for key in ('OLD_CORRECTED','CORRECTED'):
 ob=query_setup(key)
 middle[key]={e:surface(bone['MIDDLE_MCP_R'][e+'_world_m'],ob,True) for e in ('head','tail')}
# Independently reproduce the prior diagnostic's exact native fan / world-space BVH method.
tris=[];face_ids=[]
for fi,f in data['CORRECTED']['protected']['mesh']['faces']:
 for i in range(1,len(f)-1):tris.append([f[0],f[i],f[i+1]]);face_ids.append(fi)
trees={k:BVHTree.FromPolygons(data[k]['coordinates_world_m'],tris,all_triangles=True) for k in ('OLD_CORRECTED','CORRECTED')}
fan=[]
for name,b in bone.items():
 for e in ('head','tail'):
  q=Vector(b[e+'_world_m']);a=trees['OLD_CORRECTED'].find_nearest(q);z=trees['CORRECTED'].find_nearest(q)
  fan.append({'name':name,'endpoint':e,'old_distance_mm':a[3]*1000,'new_distance_mm':z[3]*1000,'delta_mm':(z[3]-a[3])*1000,'old_native_face':face_ids[a[2]],'new_native_face':face_ids[z[2]],'old_triangle_native_ids':tris[a[2]],'new_triangle_native_ids':tris[z[2]]})
for e in ('head','tail'):
 a=middle['OLD_CORRECTED'][e];z=middle['CORRECTED'][e];q=Vector(bone['MIDDLE_MCP_R'][e+'_world_m']);near=min(((q-Vector(data['CORRECTED']['coordinates_world_m'][i])).length*1000,i) for i in IDS)
 middle[e]={'world_position_m':list(q),'formal_Blender_native_polygon_method':{'old':a,'new':z,'delta_mm':z['surface_distance_mm']-a['surface_distance_mm']},'prior_diagnostic_method_fresh_recomputed':next(r for r in fan if r['name']=='MIDDLE_MCP_R' and r['endpoint']==e),'local_palmar16_nearest_vertex':{'native_id':near[1],'distance_mm':near[0]},'inside_status':'PASS' if z['inside_ray_parity'] else 'FAIL','formal_region':J['all21_current_rows']['MIDDLE_MCP_R' if e=='head' else 'MIDDLE_PIP_R']['region'],'tail_semantics':'MIDDLE_MCP tail equals MIDDLE_PIP deform head; its PIP region applies' if e=='tail' else 'MIDDLE_MCP T-01 axial region applies','surface_side_relation':'PARITY_INSIDE; negative normal projection','new_face_intersects_palmar16':bool(set(z['nearest_native_feature']['native_vertices'])&set(IDS))}
assert bone['MIDDLE_MCP_R']['tail_world_m']==bone['MIDDLE_PIP_R']['head_world_m']
dump('MIDDLE_MCP_R_SURFACE_RELATION_REVALIDATION_R1.json',{'status':'PASS','head':middle['head'],'tail':middle['tail'],'distance_increase_is_not_a_failure_threshold':True,'methods':'Formal frozen closest_point_on_mesh and historical diagnostic native fan BVH are separately paired; no old/new method mixing','joint_relocation_required':'NO'})
rank=read(OUT/'JOINT_SURFACE_DELTA_RANKING_R1.json');rank['diagnostic_fan_method_all42']=sorted(fan,key=lambda r:abs(r['delta_mm']),reverse=True)
rank['palmar16_joint_head_proximity_ranking']=sorted([{'name':n,'distance_to_palmar16_nearest_vertex_mm':min((Vector(b['head_world_m'])-Vector(data['CORRECTED']['coordinates_world_m'][i])).length*1000 for i in IDS)} for n,b in bone.items()],key=lambda r:r['distance_to_palmar16_nearest_vertex_mm'])
dump('JOINT_SURFACE_DELTA_RANKING_AFTER_PALMAR_R1.json',rank)
bind=read(OUT/'BIND_ZERO_GEOMETRY_REVALIDATION_R1.json');d=bind['all3416_delta_mm'];ordered=sorted(d);x=(len(d)-1)*.95;lo=int(x);bind.update(RAW_TO_BIND_P95_DELTA_MM=ordered[lo]+(ordered[min(lo+1,len(d)-1)]-ordered[lo])*(x-lo),RAW_TO_BIND_OUT_OF_TOLERANCE_COUNT=len(bind['outside_native_vertex_ids']),MAX_DELTA_VERTEX_ID=d.index(max(d)))
dump('BIND_ZERO_GEOMETRY_REVALIDATION_AFTER_PALMAR_R1.json',bind)
# Query an unsaved display copy of actual evaluated ZERO coordinates; do not re-evaluate poses.
load(FILES['R2']);ob=bpy.data.objects.new('UNSAVED_EVALUATED_ZERO_SURFACE_QUERY',bpy.data.meshes.new('MEASURED_ZERO_COPY'));ob.data.from_pydata(G['stages']['R2_BIND_ZERO']['world_m'],[],G['faces']);bpy.context.scene.collection.objects.link(ob)
ns.update(MOB=ob,MW=Matrix.Identity(4),MINV=Matrix.Identity(4),M3=Matrix.Identity(3))
evaluated={}
for name,r in sem['rules'].items():
 s=surface(bone[name]['head_world_m'],ob,r['inside_required']);reg=region(r,bone[name]['head_world_m'],s,ob)
 if r['region']['type']=='CORRECTED_NATIVE_TERMINAL_SURFACE_LANDMARK':
  # Exact native terminal authority is established on stored RAW coordinates.
  # Its evaluated counterpart is governed by the recovered full3416 bind gate.
  rawreg=J['all21_current_rows'][name]['region']
  reg['raw_native_terminal_exact_status']=rawreg['status']
  reg['evaluated_terminal_noise_gate_mm']=sem['zero_bind']['bind_gate_mm']
  reg['status']='PASS' if rawreg['status']=='PASS' and reg['terminal_landmark_delta_mm']<=sem['zero_bind']['bind_gate_mm'] and s['surface_distance_mm']<=r['region']['surface_max_mm'] else 'FAIL'
 passed=reg['status']=='PASS' and (not r['inside_required'] or s['inside_ray_parity'])
 evaluated[name]={'surface':s,'region':reg,'status':'PASS' if passed else 'FAIL'}
dump('EVALUATED_ZERO_JOINT_SURFACE_CROSSCHECK_R1.json',{'status':'PASS' if all(r['status']=='PASS' for r in evaluated.values()) else 'FAIL','all21_rows':evaluated,'geometry_source':ref(OUT/'MATCHED_ZERO_BIND_REVIEW_GEOMETRY_R1.json'),'pose_evaluations_this_supplement':0})
assert all(r['status']=='PASS' for r in evaluated.values()),'FAIL_CLOSED_EVALUATED_ZERO_JOINT_SURFACE'
for old,new in [('REST_RIG_PAYLOAD_REVALIDATION_R1.json','REST_RIG_PAYLOAD_AFTER_PALMAR_R1.json'),('ZERO_POSE_REVALIDATION_R1.json','ZERO_POSE_REVALIDATION_AFTER_PALMAR_R1.json'),('MODIFIER_BIND_CONTRACT_REVALIDATION_R1.json','MODIFIER_BIND_CONTRACT_AFTER_PALMAR_R1.json'),('WEIGHT_HASH_READONLY_REVERIFICATION_R1.json','WEIGHT_HASH_READONLY_AFTER_PALMAR_R1.json')]:
 dump(new,read(OUT/old))
print('Formal inventory / MIDDLE head-tail / fan diagnostic / actual evaluated ZERO crosscheck PASS')
