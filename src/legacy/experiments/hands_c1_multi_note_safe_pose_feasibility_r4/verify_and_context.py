import session as w
from session import *
selected={tag:f'{tag}_ROUND_{2 if tag=="R08" else 1}_NOT_APPROVED_POSE.json' for tag,t in targets}
reopened=[]
for tag,filename in selected.items():
 snap=read(OUT/filename)
 sc,rig,mesh,left,lrig=s.open_scene(STARTCOPY);g.init()
 # Update session's references, including the helpers' degree reader.
 w.sc,w.rig,w.mesh,w.left,w.lrig=sc,rig,mesh,left,lrig
 c.settime(sc,snap['time'])
 L0=s.coords_tri(left)[0]
 for name,p in snap['pose'].items():
  b=rig.pose.bones[name];b.location=p['location'];b.rotation_mode=p['rotation_mode'];b.rotation_quaternion=p['quaternion'];b.scale=p['scale']
 bpy.context.view_layer.update()
 row,V,L,cross=w.measure(tag,snap['time'])
 assert row['mesh_digest']==snap['validation']['mesh_digest']
 assert row['machine_pass']
 # Enumerate all finger/key intersections, including idle digits on active key.
 target_intersections=[]
 for co in g.comps:
  if co[0]['note_name']!=row['key']:continue
  kv,P=g.actual(co);pairs=g.tree(V,g.ALLT).overlap(g.tree(kv,co[4]))
  for a,b in pairs:target_intersections.append(dict(triangle=a,skin_digit=tri_label(g.ALLT[a]),key_triangle=b))
 active_digit=DIGITS[row['finger']-1]
 assert all(p['skin_digit']==active_digit for p in target_intersections),'IDLE_DIGIT_TARGET_CONTACT'
 neutral=s.key_local(V,KEYS[row['event']['key_index']])
 distal=[i for i in ROI[active_digit]['vertices'] if max([(mesh.vertex_groups[a.group].name,a.weight) for a in mesh.data.vertices[int(i)].groups],key=lambda x:x[1])[0]==f'{active_digit}_{"IP" if active_digit=="THUMB" else "DIP"}_R']
 patch=neutral[distal]
 add=dict(snapshot=filename,mesh_digest_reproduced=True,validation=row,target_intersections=target_intersections,active_distal_neutral_bounds=dict(min=patch.min(0),max=patch.max(0)),left_reopen_delta_mm=float(np.linalg.norm(L-L0,axis=1).max()*1000),no_idle_digit_target_intersections=True)
 reopened.append(add)
save('REOPENED_STATIC_VALIDATION.json',dict(rows=reopened,all_four_pass=True,source_blend_only_plus_static_snapshots=True,animation_actions_retained=True))
# Reuse R3 evaluated boundary evidence instead of a new dense survey.
r3=ROOT/'experiments/hands_c1_phrase_level_geometry_closure_r3'
survey=read(r3/'BOUNDARY_AND_FINGER_SURVEY.json')['rows']
dense=read(r3/'DENSE_HANDOFF_BOUNDARY_CHECK.json')['extension_rows']
boundary=[]
for t in [2.921426,3.349997,3.5642825,3.708333333333333,3.778568]:
 rows=[r for r in survey if r['version']=='R2' and abs(r['time']-t)<1e-8]
 rows+= [r for r in dense if abs(r['time']-t)<=1/960+1e-9]
 boundary.append(dict(requested_time=t,source='R3 read-only evaluated evidence',rows=rows))
sc,rig,mesh,left,lrig=s.open_scene(STARTCOPY);g.init()
w.sc,w.rig,w.mesh,w.left,w.lrig=sc,rig,mesh,left,lrig
r12=next(n for n in NOTES if n['note_id']=='R12')
fresh=[]
for tag,t in [('R2_SAFE_START',2.92),('R11_END_BEFORE',r12['note_on']-1/960),('R12_ON',r12['note_on']),('R12_AFTER',r12['note_on']+1/960),('R12_HOLD',(r12['note_on']+r12['note_off'])/2)]:
 c.settime(sc,t);row,V,L,cross=w.measure(tag,t);fresh.append(row)
save('BOUNDARY_R12_READONLY.json',dict(reused_boundaries=boundary,fresh_original_R2_rows=fresh,R12=r12,no_boundary_or_R12_edits=True,no_safe_closure_claim=True))
snaprows=[read(OUT/f)['validation'] for f in selected.values()]
chain=[fresh[0]]+snaprows+[next(r for r in fresh if r['tag']=='R12_ON')]
diffs=[]
for a,b in zip(chain,chain[1:]):
 dt=b['time']-a['time'];A=np.array(a['wrist']);B=np.array(b['wrist']);qdiff=np.array(b['q'])-np.array(a['q'])
 ang=math.degrees(math.acos(float(np.clip((np.trace(A[:3,:3].T@B[:3,:3])-1)/2,-1,1))))
 diffs.append(dict(from_tag=a['tag'],to_tag=b['tag'],dt_seconds=dt,wrist_delta_mm=(B[:3,3]-A[:3,3])*1000,wrist_distance_mm=float(np.linalg.norm(B[:3,3]-A[:3,3])*1000),wrist_orientation_difference_deg=ang,q_delta_deg=qdiff,average_wrist_distance_over_time_mm_s=float(np.linalg.norm(B[:3,3]-A[:3,3])*1000/dt),max_abs_joint_difference_deg=float(abs(qdiff).max()),max_joint_difference_over_time_deg_s=float(abs(qdiff).max()/dt),endpoint_difference_only=True,not_velocity_or_path_validation=True))
save('POSE_COMPATIBILITY_METRICS.json',dict(selected=selected,pairs=diffs,events=[n for n in NOTES if n['note_id'] in ['R07','R08','R09','R10','R11','R12']],no_interpolation=True,no_keyframes=True))
protection('RUNTIME_READ_INPUT_RECEIPT.json')
print('R4_REOPEN_CONTEXT_COMPLETE',json.dumps([dict(tag=r['validation']['tag'],idle_clear=r['no_idle_digit_target_intersections'],target_pairs=len(r['target_intersections'])) for r in reopened]),flush=True)
