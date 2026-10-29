from support import *
import support as s
dm=types.ModuleType('depth_math')
pp=ROOT/'audits/hands_saved_pose_geometry_closure_r1/depth_math.py'
exec(compile(safe(pp).read_text(encoding='utf8'),str(pp),'exec'),dm.__dict__)
def init():
 global comps,IT,IF,IDS,ALLT
 comps=[]
 for key,g,pl in s.registered_components():
  ob=next(o for o in s.sc.objects if o.type=='MESH' and o.get('FROZEN_KEY_INDEX')==key['key_index'] and g['name'] in o.name)
  me=ob.data;me.calc_loop_triangles();v=np.array([list(a.co) for a in me.vertices]);tr=np.array([list(a.vertices) for a in me.loop_triangles],int);p,_=dm.planes_from_mesh(v,tr)
  comps.append((key,g,ob.name,v,tr,p))
 V,ALLT,F=s.coords_tri(s.mesh);IDS=np.array(ROI['INDEX']['vertices'],int);IF=ROI['INDEX']['faces'];IT=ALLT[np.any(np.isin(ALLT,IDS),axis=1)]
def actual(comp):
 key,g,name,v,tr,p=comp;M=np.array(bpy.data.objects[name].matrix_world);kv=(np.c_[v,np.ones(len(v))]@M.T)[:,:3]
 pp=np.c_[p[:,:3],-p[:,3]]@np.linalg.inv(M);norm=np.linalg.norm(pp[:,:3],axis=1);P=np.c_[pp[:,:3]/norm[:,None],-pp[:,3]/norm]
 pv=np.array(key['press_pivot']);registered=(np.array(g['vertices'])-pv)@c.axisrot(s.keyangle(key),key['press_axis']).T+pv
 assert np.max(abs(kv-registered))<1e-6
 return kv,P
def tree(V,T):return BVHTree.FromPolygons([Vector(v) for v in V],T,all_triangles=True,epsilon=0)
def keycheck(V,black_only=False,deep=True,margin=.02,all_hand=False):
 T=ALLT if all_hand else IT;tris=V[T];lo=tris.min(1);hi=tris.max(1);vmin=lo.min(0);vmax=hi.max(0);out=[]
 for comp in comps:
  key=comp[0]
  if black_only and key['color']!='BLACK':continue
  kv,P=actual(comp);kl=kv.min(0);kh=kv.max(0)
  if np.any(vmax+margin<kl) or np.any(vmin-margin>kh):continue
  mask=np.all(hi>=kl,axis=1)&np.all(lo<=kh,axis=1);peak=0.;cert=None
  ids=np.unique(T[mask])
  if len(ids):
   dep=np.maximum(0,np.min(P[:,3]-V[ids]@P[:,:3].T,axis=1))*1000;peak=float(dep.max())
  if deep:
   for j in np.flatnonzero(mask):
    rr=dm.max_triangle_depth(tris[j],P)
    if rr['upper_mm']>peak:peak=rr['upper_mm'];cert=dict(triangle=T[j],**rr)
  kt=tree(kv,comp[4]);skin=tree(V,T);pairs=skin.overlap(kt)
  # True triangle surface distance in both vertex directions; separated edge-edge
  # distance is additionally bounded by a separating AABB when disjoint.
  near=[]
  for v in V[np.unique(T)]:
   rr=kt.find_nearest(Vector(v))
   if rr[0] is not None:near.append(rr[3])
  for v in kv:
   rr=skin.find_nearest(Vector(v))
   if rr[0] is not None:near.append(rr[3])
  clearance=0 if pairs or peak>1e-6 else min(near)*1000
  # AABB separation is a conservative lower bound for positive mesh clearance.
  lower=float(np.linalg.norm(np.maximum(0,np.maximum(kl-vmax,vmin-kh)))*1000)
  out.append(dict(key=key['note_name'],key_index=key['key_index'],color=key['color'],depth_mm=peak,bvh_pairs=len(pairs),clearance_vertex_surface_mm=clearance,clearance_aabb_lower_mm=lower,certificate=cert))
 return out
def joint_set(q):
 for name,M in zip(c.SETUPS['R','INDEX'][0],c.joint_mats('R','INDEX',np.radians(q))):
  s.rig.pose.bones[name].rotation_quaternion=Matrix(M.tolist()).to_quaternion()
 bpy.context.view_layer.update()
