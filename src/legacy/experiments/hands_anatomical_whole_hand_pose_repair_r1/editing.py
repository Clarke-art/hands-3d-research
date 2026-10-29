import session as w
from geometry import *
import geometry as g
def commit_digit(d,q):
 for name,M in zip(c.SETUPS['R',d][0],c.joint_mats('R',d,np.radians(q))):
  b=w.rig.pose.bones[name];b.rotation_quaternion=Matrix(M.tolist()).to_quaternion();b.keyframe_insert('rotation_quaternion',frame=157,group='ANATOMICAL_STATIC_'+d)
 bpy.context.view_layer.update()
def rotate_whole_hand_about_thumb(x_deg,y_deg,z_deg=0.,translation=(0.,0.,0.)):
 # Direct animator pivot operation, not an IK/contact solver. Angles selected
 # only by the operator after viewing models; no pose/parameter search.
 P=Vector(w.THUMB_PAD);R=Matrix.Rotation(math.radians(z_deg),4,'Z')@Matrix.Rotation(math.radians(y_deg),4,'Y')@Matrix.Rotation(math.radians(x_deg),4,'X')
 D=Matrix.Translation(Vector(translation))@Matrix.Translation(P)@<REDACTED_EMAIL>(-P)
 b=w.rig.pose.bones['WRIST_R'];b.matrix=w.rig.matrix_world.inverted()@<REDACTED_EMAIL><REDACTED_EMAIL>_WRIST
 b.keyframe_insert('location',frame=157,group='ANATOMICAL_STATIC_WRIST');b.keyframe_insert('rotation_quaternion',frame=157,group='ANATOMICAL_STATIC_WRIST');bpy.context.view_layer.update()
def record(number,rationale,bones):
 assert 1<=number<=4
 V,T,F=s.coords_tri(w.mesh);L,LT,LF=s.coords_tri(w.left);rows=g.keycheck(V,all_hand=True)
 for row in rows:
  comps=[co for co in g.comps if co[0]['key_index']==row['key_index']]
  row['exact_clearance_mm']=0. if row['depth_mm']>1e-6 else min(w.exact_clearance(V,g.ALLT,g.actual(co)[0],co[4]) for co in comps)
 current_self=w.self_full(V);q=np.array([s.degrees(d) for d in DIGITS]);bd=w.BOUNDS
 WB=<REDACTED_EMAIL>['WRIST_R'].matrix;oldWB=<REDACTED_EMAIL>_WRIST
 rot=WB.to_quaternion().rotation_difference(oldWB.to_quaternion()).angle
 active=w.active_contacts(V,L);oldkeys={k['key']:k for k in w.baseline_keys};newkeys=[dict(key=r['key'],depth_mm=r['depth_mm']) for r in rows if r['depth_mm']>1e-6 and oldkeys.get(r['key'],{}).get('depth_mm',0)<=1e-6]
 changed=np.flatnonzero(np.linalg.norm(V-w.B,axis=1)>1e-10);CT=g.ALLT[np.any(np.isin(g.ALLT,changed),axis=1)]
 cp=set(g.tree(V,CT).overlap(g.tree(L,LT))) if len(CT) else set();bp=set(g.tree(w.B,CT).overlap(g.tree(w.BL,LT))) if len(CT) else set()
 assert w.NATIVE=={side:c.digest(c.native(ob,rg)) for side,ob,rg in [('R',w.mesh,w.rig),('L',w.left,w.lrig)]}
 assert w.ACTIONS=={**s.protected_state(),w.rig.name:w.ACTIONS[w.rig.name]}
 sc=w.sc;sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']];path=OUT/f'ROUND_{number}_STATIC_NOT_APPROVED.blend';assert not path.exists();bpy.ops.wm.save_as_mainfile(filepath=str(path),check_existing=True)
 views=w.render_views(f'ROUND_{number}')
 keydict={r['key']:r for r in rows};baselineG4=max(r['depth_mm'] for r in w.baseline_keys if r['key']=='G4');candidateG4=max(r['depth_mm'] for r in rows if r['key']=='G4')
 result=dict(round=number,rationale=rationale,edited_bones=bones,qdeg={d:q[i] for i,d in enumerate(DIGITS)},strict_in_joint_domain=bool(np.all(q>=bd[:,0]) and np.all(q<=bd[:,1])),raw_domain_violation_deg=float(max(0,np.max(bd[:,0]-q),np.max(q-bd[:,1]))),keys=rows,illegal_intersections=[r for r in rows if r['key']!='G4' and (r['depth_mm']>1e-6 or r['bvh_pairs']>0)],G4_legal_contact=dict(baseline_depth_mm=baselineG4,candidate_depth_mm=candidateG4,increase_mm=candidateG4-baselineG4),new_collision_key_identities=newkeys,new_self_pairs=sorted(current_self-w.BASE_SELF),self_pair_count=len(current_self),new_cross_hand_pairs=sorted(cp-bp),active_contacts=active,thumb_pad_shift_mm=float(np.linalg.norm(V[2963]-w.B[2963])*1000),wrist_position_world=list(WB.translation),wrist_delta_world_mm=(np.array(WB.translation)-np.array(oldWB.translation))*1000,wrist_rotation_delta_deg=math.degrees(rot),wrist_pose_matrix=np.array(w.rig.pose.bones['WRIST_R'].matrix),root_object_unchanged=np.array_equal(np.array(w.rig.matrix_world),w.RIG_M),mcp_displacement_mm={d:(np.array(<REDACTED_EMAIL>[c.SETUPS['R',d][0][0]].head)-np.array(w.rig.matrix_world@Vector(w.BASE_BONES[c.SETUPS['R',d][0][0]]['matrix'][:3,3])))*1000 for d in DIGITS},candidate=str(path),candidate_sha256=sha(path),views=views,reference_naturality='PENDING_OPERATOR_VIEW_AND_HUMAN',native_unchanged=True)
 save(f'ROUND_{number}_DATA.json',result);np.savez_compressed(OUT/f'ROUND_{number}_STATIC.npz',V=V,L=L,q=q)
 print('ROUND_RESULT',json.dumps(dict(round=number,keys=[(r['key'],round(r['depth_mm'],6),r['bvh_pairs']) for r in rows if r['depth_mm']>1e-6],new_self=len(result['new_self_pairs']),thumb_shift=result['thumb_pad_shift_mm'],wrist_delta=result['wrist_delta_world_mm'].tolist(),wrist_rotation=result['wrist_rotation_delta_deg'],domain=result['raw_domain_violation_deg'],active=active),ensure_ascii=False),flush=True)
 return result
