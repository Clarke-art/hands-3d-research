"""Actual evaluated-skin boundary constraints, Blender runtime, no optimizer.

Only closed convex key bodies get inside tests. Open finger patches get actual
surface intersection queries, never a global inside/outside normal test.
This is a diagnostic gate, not yet a differentiable trajectory constraint model.
"""
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def convex_key_penetration(vertices,faces,skin,ids):
 center=vertices.mean(0);planes=[]
 for f in faces:
  p=vertices[f];n=np.cross(p[1]-p[0],p[2]-p[0]);length=np.linalg.norm(n)
  if length<1e-12:continue
  n/=length
  if np.dot(n,center-p[0])>0:n=-n
  planes.append(np.r_[n,np.dot(n,p[0])])
 planes=np.array(planes)
 # Restrict this fast inside test to verified convex bodies. Nonconvex white
 # keys need a separate closed-surface query and are NOT certified here.
 if np.max(vertices@planes[:,:3].T-planes[:,3])>1e-6:raise ValueError('Convex key query cannot certify this key geometry')
 pts=skin[np.array(ids)];depth=-np.max(pts@planes[:,:3].T-planes[:,3],axis=1)*1000
 j=int(np.argmax(depth));tree=BVHTree.FromPolygons([Vector(v) for v in vertices],faces,epsilon=0);near=tree.find_nearest(Vector(pts[j]))
 return dict(inside_vertices=int(np.sum(depth>.02)),max_internal_depth_mm=max(0,float(depth[j])),witness_vertex=int(ids[j]),witness_world_m=pts[j].tolist(),nearest_key_surface_world_m=list(near[0]),distance_to_actual_key_surface_mm=float(near[3]*1000),convex_verified=True)

def boundary_key_constraint(skin,roi,key_vertices,key_faces,limit_mm=.5):
 result=convex_key_penetration(key_vertices,key_faces,skin,roi['vertices'])
 hand=BVHTree.FromPolygons([Vector(v) for v in skin],roi['faces'],epsilon=0);key=BVHTree.FromPolygons([Vector(v) for v in key_vertices],key_faces,epsilon=0)
 result['intersecting_face_pairs']=len(hand.overlap(key));result['slack_mm']=limit_mm-result['max_internal_depth_mm'];result['hard_violation']=result['slack_mm']<0
 return result
