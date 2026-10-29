from sculpt_common import *
dm=types.ModuleType('frozen_depth_math');dp=ROOT/'audits/hands_saved_pose_geometry_closure_r1/depth_math.py';exec(compile(safe(dp).read_text(encoding='utf8'),str(dp),'exec'),dm.__dict__)
def tree(v,t):return BVHTree.FromPolygons([Vector(x) for x in v],t,all_triangles=True,epsilon=0)
extract(ROOT/'experiments/hands_blender_artist_pose_repair_poc_r1/artist_tools.py',{'segment_distance','edges'},globals())
def exact_clearance(v,t,kv,kt):
 st=tree(v,t);bt=tree(kv,kt)
 if st.overlap(bt):return 0.
 ds=[bt.find_nearest(Vector(p))[3] for p in v[np.unique(t)]]+[st.find_nearest(Vector(p))[3] for p in kv]
 # Both endpoint/face and all edge/edge cases; no vertex-only shortcut.
 ed=edges(v,t);ke=edges(kv,kt);best=min(ds)
 for a in range(0,len(ed),800):best=min(best,segment_distance(ed[a:a+800],ke))
 return best*1000
def components(sc):
 out=[]
 for key in KEYS:
  for geom in key['geometry']:
   ob=next(o for o in sc.objects if o.type=='MESH' and o.get('FROZEN_KEY_INDEX')==key['key_index'] and geom['name'] in o.name)
   v,t,_=coords(ob);planes,_=dm.planes_from_mesh(v,t);out.append((key,geom,ob.name,v,t,planes))
 return out
def collisions(v,t):
 tr=tree(v,t);return {(int(i),int(j)) for i,j in tr.overlap(tr) if i<j and not set(t[i])&set(t[j])}
def keyrows(v,t,comps,exact_keys=set()):
 tris=v[t];lo=tris.min(1);hi=tris.max(1);vl=lo.min(0);vh=hi.max(0);skin=tree(v,t);out=[]
 for key,g,name,kv,kt,pl in comps:
  kl=kv.min(0);kh=kv.max(0)
  if np.any(vh+.02<kl) or np.any(vl-.02>kh):continue
  mask=np.all(hi>=kl,axis=1)&np.all(lo<=kh,axis=1);indices=np.flatnonzero(mask)
  pairs=skin.overlap(tree(kv,kt));ids=np.unique(t[indices]);peak=0.;witness=None
  if len(ids):peak=float(np.maximum(0,np.min(pl[:,3]-v[ids]@pl[:,:3].T,axis=1)).max()*1000)
  for j in indices:
   # Primal/dual triangle-solid bound includes interior intersections missed by vertices.
   rr=dm.max_triangle_depth(tris[j],pl)
   if rr['upper_mm']>peak:peak=rr['upper_mm'];witness={'triangle_index':int(j),**rr}
  row={'key':key['note_name'],'key_index':key['key_index'],'component':name,'depth_mm':peak,'bvh_pairs':len(pairs),'depth_certificate':witness}
  if key['note_name'] in exact_keys:row['exact_clearance_mm']=0. if peak>1e-6 or pairs else exact_clearance(v,t,kv,kt)
  out.append(row)
 return out
def contact(v,key,side,finger):
 i=c.MARKERS[side][finger-1]['mesh_vertex'];point=v[i];name=MAN['key_pivots'].get(str(key['key_index']));angle=bpy.data.objects[name].rotation_euler.x if name else 0.
 pivot=np.array(key['press_pivot']);p=(point-pivot)@c.axisrot(angle,key['press_axis'])+pivot
 surfaces=key['key_top_playable_surface'];s=min(surfaces,key=lambda s:np.linalg.norm(p[:2]-np.clip(p[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']])))
 miss=float(np.linalg.norm(p[:2]-np.clip(p[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']])))*1000;gap=float(p[2]-s['z'])*1000;inside=bool(s['xmin']<=p[0]<=s['xmax'] and s['ymin']<=p[1]<=s['ymax'])
 return {'vertex':i,'skin_world':point,'horizontal_mm':miss,'gap_mm':gap,'inside':inside,'pass_prior_static_strict':inside and miss<=.03 and abs(gap)<=3,'formal_vertical_3mm':abs(gap)<=3,'formal_horizontal_2mm':miss<=2}
def active_contacts(v,l,t):
 return [dict(note_id=n['note_id'],hand=n['hand'],finger=n['finger'],key=n['note_name'],contact=contact(v if n['hand']=='R' else l,KEYS[n['key_index']],n['hand'],n['finger'])) for n in NOTES if n['note_on']<=t<n['note_off']]
def deform_metrics(v,base,allowed,t,base_t):
 face_ids=np.flatnonzero(np.any(np.isin(F,allowed),axis=1));before=base[F[face_ids]];after=v[F[face_ids]]
 def area(p):return (np.linalg.norm(np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]),axis=1)+np.linalg.norm(np.cross(p[:,2]-p[:,0],p[:,3]-p[:,0]),axis=1))/2
 ratio=area(after)/area(before)
 edges0=np.linalg.norm(base[E[:,0]]-base[E[:,1]],axis=1);edges1=np.linalg.norm(v[E[:,0]]-v[E[:,1]],axis=1);ei=np.any(np.isin(E,allowed),axis=1);er=edges1[ei]/edges0[ei]
 bn=np.cross(before[:,1]-before[:,0],before[:,2]-before[:,0]);an=np.cross(after[:,1]-after[:,0],after[:,2]-after[:,0]);flip=np.sum(an*bn,axis=1)<=0
 # Local ray from moved skin point into original opposite surface: thickness proxy, no anatomy threshold.
 bv=tree(base,base_t);cv=tree(v,t);n0=normals(base);n1=normals(v);th=[]
 for i in allowed:
  row={'vertex':int(i)}
  for tag,pts,ns,tr in [('before',base,n0,bv),('after',v,n1,cv)]:
   hit=tr.ray_cast(Vector(pts[i]-ns[i]*.00008),Vector(-ns[i]),.07)
   row[tag+'_normal_ray_thickness_mm']=(hit[3]+.00008)*1000 if hit[0] is not None else None
  th.append(row)
 return {'affected_native_faces':face_ids,'face_area_ratio_min_max':[float(ratio.min()),float(ratio.max())],'edge_length_ratio_min_max':[float(er.min()),float(er.max())],'flipped_face_ids':face_ids[flip],'thickness_proxy':th,'thickness_proxy_limitation':'First inward normal ray exit; not anatomical tissue thickness or a volume certificate.'}
