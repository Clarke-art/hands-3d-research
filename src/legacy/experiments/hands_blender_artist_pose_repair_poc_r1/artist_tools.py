import artist_session as a
from geometry import *
import geometry as g
def segment_distance(E,F):
 # Exact segment-segment minimum: endpoint projections plus feasible interior pair.
 A=E[:,None,0];U=E[:,None,1]-A;B=F[None,:,0];W=F[None,:,1]-B;R=A-B
 aa=np.sum(U*U,axis=2);bb=np.sum(U*W,axis=2);cc=np.sum(W*W,axis=2);dd=np.sum(U*R,axis=2);ee=np.sum(W*R,axis=2);den=aa*cc-bb*bb
 ss=np.divide(bb*ee-cc*dd,den,out=np.zeros_like(den),where=abs(den)>1e-20);tt=np.divide(aa*ee-bb*dd,den,out=np.zeros_like(den),where=abs(den)>1e-20)
 valid=(den>1e-20)&(ss>=0)&(ss<=1)&(tt>=0)&(tt<=1)
 best=np.where(valid,np.sum((R+ss[:,:,None]*U-tt[:,:,None]*W)**2,axis=2),np.inf)
 for p in [E[:,None,0],E[:,None,1]]:
  t=np.clip(np.sum((p-B)*W,axis=2)/cc,0,1);best=np.minimum(best,np.sum((p-B-t[:,:,None]*W)**2,axis=2))
 for p in [F[None,:,0],F[None,:,1]]:
  t=np.clip(np.sum((p-A)*U,axis=2)/aa,0,1);best=np.minimum(best,np.sum((p-A-t[:,:,None]*U)**2,axis=2))
 return float(np.sqrt(best.min()))
def edges(V,T):
 ix=np.unique(np.sort(np.r_[T[:,[0,1]],T[:,[1,2]],T[:,[2,0]]],axis=1),axis=0);return V[ix]
def exact_clearance(V,T,kv,kt):
 st=g.tree(V,T);bt=g.tree(kv,kt)
 if st.overlap(bt):return 0.
 ds=[bt.find_nearest(Vector(v))[3] for v in V[np.unique(T)]]+[st.find_nearest(Vector(v))[3] for v in kv]
 return min(min(ds),segment_distance(edges(V,T),edges(kv,kt)))*1000
def selfpairs(V,T):
 ids=np.flatnonzero(np.any(np.isin(g.ALLT,np.unique(T)),axis=1));part=g.ALLT[ids];pairs=g.tree(V,part).overlap(g.tree(V,g.ALLT));out=set()
 for i,j in pairs:
  ix=int(ids[i]);j=int(j)
  if ix==j or np.intersect1d(g.ALLT[ix],g.ALLT[j]).size:continue
  out.add(tuple(sorted((ix,j))))
 return out
def record_round(number,rationale,suffix=''):
 assert number in [1,2,3]
 q=s.degrees('INDEX');V,T,F=s.coords_tri(a.mesh);changed=np.flatnonzero(np.linalg.norm(V-a.V0,axis=1)>1e-10)
 tri=g.ALLT[np.any(np.isin(g.ALLT,np.union1d(g.IDS,changed)),axis=1)]
 oldIT=g.IT;g.IT=tri
 rows=g.keycheck(V);base=g.keycheck(a.V0)
 for row in rows:
  comps=[co for co in g.comps if co[0]['key_index']==row['key_index']]
  row['exact_surface_clearance_mm']=0. if row['depth_mm']>1e-6 else min(exact_clearance(V,tri,*((lambda co:(g.actual(co)[0],co[4]))(co))) for co in comps)
 bp=selfpairs(a.V0,tri);cp=selfpairs(V,tri)
 thumb=s.contact(V,KEYS[46],'R',1)
 assert a.native=={side:c.digest(c.native(ob,rg)) for side,ob,rg in [('R',a.mesh,a.rig),('L',a.left,a.lrig)]}
 assert np.array_equal(np.array(a.rig.matrix_world),a.rootmat)
 for name in c.SETUPS['R','INDEX'][0]:a.rig.pose.bones[name].keyframe_insert('rotation_quaternion',frame=157,group='ARTIST_INDEX_STATIC')
 path=OUT/f'ROUND_{number}{suffix}_STATIC_NOT_APPROVED.blend';assert not path.exists();sc=a.sc;sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']];bpy.ops.wm.save_as_mainfile(filepath=str(path),check_existing=True)
 views=a.render_views(f'ROUND_{number}{suffix}_2_600')
 result=dict(round=number,rationale=rationale,time=2.6,qdeg=q,thumb_contact=thumb,thumb_pad_shift_mm=float(np.linalg.norm(V[2963]-a.V0[2963])*1000),keys=rows,baseline_keys=base,new_self_pairs=sorted(cp-bp),baseline_self_pairs=len(bp),candidate_self_pairs=len(cp),changed_vertex_count=len(changed),new_pose_path=str(path),views=views,native_unchanged=True,palm_unchanged=True,strict_q_in_bounds=bool(np.all(q>=a.bounds[0]) and np.all(q<=a.bounds[1])),source_sha256=sha(SOURCE),candidate_sha256=sha(path))
 save(f'ROUND_{number}{suffix}_STATIC_CHECK.json',result);np.savez_compressed(OUT/f'ROUND_{number}{suffix}_STATIC.npz',V=V,q=q,T=tri)
 g.IT=oldIT
 print(json.dumps(dict(round=number,q=q.tolist(),collisions=[(r['key'],r['depth_mm'],r['bvh_pairs']) for r in rows if r['depth_mm']>1e-6],nearest=[(r['key'],r['exact_surface_clearance_mm']) for r in rows],thumb=thumb,new_self_pairs=len(cp-bp)),ensure_ascii=False),flush=True)
 return result
