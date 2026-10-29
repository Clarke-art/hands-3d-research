import dynamic_artist as w
from geometry import *
import geometry as g
def pose(q,angles,translation):
 c.settime(w.sc,2.6)
 for name,M in zip(c.SETUPS['R','INDEX'][0],c.joint_mats('R','INDEX',np.radians(q))):
  w.rig.pose.bones[name].rotation_quaternion=Matrix(M.tolist()).to_quaternion()
 R=Matrix.Rotation(math.radians(angles[2]),4,'Z')@Matrix.Rotation(math.radians(angles[1]),4,'Y')@Matrix.Rotation(math.radians(angles[0]),4,'X')
 D=Matrix.Translation(Vector(translation))@Matrix.Translation(w.P0)@<REDACTED_EMAIL>(-w.P0)
 w.rig.pose.bones['WRIST_R'].matrix=w.rig.matrix_world.inverted()@<REDACTED_EMAIL>_world@w.W0
 bpy.context.view_layer.update()
def record(tag,rationale):
 V,T,F=s.coords_tri(w.mesh);L,LT,LF=s.coords_tri(w.left)
 rows=g.keycheck(V,all_hand=True)
 for r in rows:
  r['exact_clearance_mm']=0. if r['depth_mm']>1e-6 or r['bvh_pairs'] else min(w.exact_clearance(V,T,g.actual(co)[0],co[4]) for co in g.comps if co[0]['key_index']==r['key_index'])
 q={d:s.degrees(d) for d in DIGITS}
 bounds=np.array(read(ROOT/'experiments/hands_role_aware_motion_recomposition_r1/POLICY.json')['joint_bounds_deg'])
 contacts=[dict(event=n['note_id'],key=n['note_name'],contact=s.contact(V if n['hand']=='R' else L,KEYS[n['key_index']],n['hand'],n['finger'])) for n in NOTES if n['note_on']<=2.6<n['note_off']]
 r=dict(tag=tag,rationale=rationale,qdeg=q,keys=rows,illegal=[r for r in rows if r['key']!='G4' and (r['depth_mm']>1e-6 or r['bvh_pairs'])],new_self=sorted(w.fullself(V)-w.SELF0),cross_pairs=len(g.tree(V,T).overlap(g.tree(L,LT))),contacts=contacts,domain=bool(np.all(np.array(list(q.values()))>=bounds[:,0]-1e-5) and np.all(np.array(list(q.values()))<=bounds[:,1]+1e-5)),wrist_matrix=np.array(w.rig.pose.bones['WRIST_R'].matrix),wrist_location=list(w.rig.pose.bones['WRIST_R'].location),wrist_quaternion=list(w.rig.pose.bones['WRIST_R'].rotation_quaternion),left_delta_mm=float(np.max(np.linalg.norm(L-w.L0,axis=1)))*1000)
 assert w.NATIVE=={a:c.digest(c.native(o,rg)) for a,o,rg in [('R',w.mesh,w.rig),('L',w.left,w.lrig)]}
 save(tag+'_STATIC_CHECK.json',r);np.savez_compressed(OUT/(tag+'_STATIC.npz'),V=V,T=T,L=L)
 w.render(tag)
 print(json.dumps(dict(tag=tag,illegal=[(a['key'],a['depth_mm'],a['bvh_pairs']) for a in r['illegal']],clearance=[(a['key'],a['exact_clearance_mm']) for a in rows if a['key'] in ['A#4','A4','C#5']],contacts=contacts,new_self=len(r['new_self']),cross_pairs=r['cross_pairs'],domain=r['domain']),ensure_ascii=False))
 return r
