import json,ast,sys,math
from pathlib import Path
import numpy as np
from itertools import combinations
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parent;META=json.loads((O/'SKIN_MODEL_META.json').read_text());D=np.load(O/'SKIN_MODEL.npz');KEYS=META['key_table'];TR=D['triangles'];LABEL=np.array(META['triangle_labels']);DIGITS=['THUMB','INDEX','MIDDLE','RING','LITTLE'];POL=json.loads((O/'POLICY_LOCK.json').read_text())
file=O.parent/'hands/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/whole_phrase_model.py';tree=ast.parse(file.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['rot','component_planes']],type_ignores=[]),'reused_geometry','exec'))
PL={(k['key_index'],j):component_planes(g) for k in KEYS for j,g in enumerate(k['geometry'])}
def keylocal(V,k,angle):return (V-np.array(k['press_pivot']))@rot(angle,k['press_axis'])+np.array(k['press_pivot'])
def keyworld(V,k,angle):return (V-np.array(k['press_pivot']))@rot(angle,k['press_axis']).T+np.array(k['press_pivot'])
def area(poly):
 if len(poly)<3:return 0.
 p=np.array(poly);return abs(float(np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))))/2*1e6

def clip(poly,axis,value,sign):
 result=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=sign*(a[axis]-value);db=sign*(b[axis]-value)
  if da<=1e-12:result.append(a)
  if (da<0 and db>0) or (da>0 and db<0):result.append(a+(b-a)*da/(da-db))
 return result

def triangle_inside_depth(T,planes):
    # Exact max signed-inside depth on a triangle, a 3-variable linear program.
    # Enumerate its polytope vertices; no optimizer or hand geometry modification.
    N=planes[:,:3];d=planes[:,3];dirs=np.column_stack([T[1]-T[0],T[2]-T[0]])
    A=np.c_[N@dirs,np.ones(len(N))];rhs=d-N@T[0]
    A=np.vstack([A,[-1,0,0],[0,-1,0],[1,1,0]]);rhs=np.r_[rhs,0.,0.,1.]
    comb=np.array(list(combinations(range(len(A)),3)));mat=A[comb];det=np.linalg.det(mat);comb=comb[abs(det)>1e-13]
    if not len(comb):return 0.,None
    x=np.linalg.solve(A[comb],rhs[comb][...,None])[...,0];valid=np.all(x@A.T<=rhs+1e-8,axis=1)&(x[:,2]>=-1e-8)
    if not valid.any():return 0.,None
    x=x[valid];best=x[np.argmax(x[:,2])];return max(float(best[2])*1000,0.),T[0]+dirs@best[:2]

def contact_metric(V,k,angle,finger):
 p=keylocal(V,k,angle);ids=np.array(META['pad_patches'][finger-1]);sur=k['key_top_playable_surface'];patchids=set(ids.tolist());tris=[i for i in np.flatnonzero(LABEL==finger-1) if all(int(v) in patchids for v in TR[i])]
 gaps=[];valid=[];cross=[];bandarea=0.;facegaps=[];crosspositions=[]
 for surf in sur:
  ok=(p[ids,0]>=surf['xmin'])&(p[ids,0]<=surf['xmax'])&(p[ids,1]>=surf['ymin'])&(p[ids,1]<=surf['ymax'])
  for v in ids[ok]:gaps.append(float((p[v,2]-surf['z'])*1000));valid.append(int(v))
  for ti in tris:
   poly=[a.copy() for a in p[TR[ti]]]
   for axis,lim,sgn in [(0,surf['xmin'],-1),(0,surf['xmax'],1),(1,surf['ymin'],-1),(1,surf['ymax'],1)]:
    poly=clip(poly,axis,lim,sgn) if poly else []
   if not poly:continue
   zs=[a[2]-surf['z'] for a in poly];facegaps.extend(z*1000 for z in zs)
   if min(zs)<=1e-7 and max(zs)>=-1e-7:
    cross.append(int(ti))
    for aa,bb in zip(poly,poly[1:]+poly[:1]):
     da=aa[2]-surf['z'];db=bb[2]-surf['z']
     if da*db<=0 and abs(da-db)>1e-15:crosspositions.append(aa+(bb-aa)*da/(da-db))
   near=clip(poly,2,surf['z']-.00005,-1);near=clip(near,2,surf['z']+.00005,1) if near else [];bandarea+=area(near)
 pad=p[int(D['pad_indices'][finger-1])];dist=[np.linalg.norm(pad[:2]-np.clip(pad[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']])) for s in sur];si=int(np.argmin(dist));minindex=valid[int(np.argmin(gaps))] if gaps else None
 return dict(pad_gap_mm=float((pad[2]-sur[si]['z'])*1000),pad_horizontal_outside_mm=float(dist[si]*1000),true_pulp_min_signed_gap_mm=min(facegaps+gaps) if facegaps or gaps else None,pulp_min_vertex_gap_mm=min(gaps) if gaps else None,pulp_closest_vertex=minindex,pulp_contact_position_world_m=keyworld(np.array(crosspositions[:1]),k,angle)[0].tolist() if crosspositions else V[minindex].tolist() if minindex is not None else None,true_pulp_surface_contact_distance_mm=0. if cross else min([abs(v) for v in facegaps+gaps]) if facegaps or gaps else None,near_contact_projected_area_mm2=bandarea,near_contact_area_band_mm=.05,top_surface_crossing_triangles=len(set(cross)),top_surface_crossing_triangle_ids=sorted(set(cross)),inside_playable_patch_vertices=len(gaps),hover_only=not bool(cross))

def self_metric(V):
 trees={};ids={};vertices={};pairs=[]
 for j,d in enumerate(DIGITS):
  ids[d]=np.flatnonzero(LABEL==j);faces=TR[ids[d]].tolist();vertices[d]=np.unique(TR[ids[d]]).tolist();trees[d]=BVHTree.FromPolygons([Vector(v) for v in V],faces,all_triangles=True,epsilon=0)
 for ai,a in enumerate(DIGITS):
  for b in DIGITS[ai+1:]:
   raw=trees[a].overlap(trees[b]);kept=[];excluded=0
   for ia,ib in raw:
    ta=int(ids[a][ia]);tb=int(ids[b][ib])
    if tb in META['topological_vertex_neighbors'][ta] or set(TR[ta])&set(TR[tb]):excluded+=1
    else:kept.append([ta,tb])
   gap=0. if kept else min([trees[b].find_nearest(Vector(V[v]))[3] for v in vertices[a][::3]]+[trees[a].find_nearest(Vector(V[v]))[3] for v in vertices[b][::3]])*1000
   pairs.append(dict(digits=[a,b],raw_triangle_pair_count=len(raw),excluded_topology_neighbor_pairs=excluded,true_nonadjacent_triangle_pair_count=len(kept),triangle_pair_ids=kept,minimum_gap_sampled_mm=gap,minimum_gap_method='Vertex-to-opposing-triangle BVH samples; zero for surface intersections, not exhaustive edge-edge gap',self_penetration_depth_mm=None,depth_note='Surface intersection pairs do not define a unique intrusion depth; no conversion of counts into millimetres'))
 return pairs

def detect(V,angles,target=None,with_self=True,with_triangle=True):
 hits=[];near=[];worst=0.;own=0.;full=BVHTree.FromPolygons([Vector(v) for v in V],TR.tolist(),all_triangles=True,epsilon=0) if with_triangle else None
 for k in KEYS:
  local=keylocal(V,k,angles[k['key_index']])
  for j,g in enumerate(k['geometry']):
   gv=np.array(g['vertices']);lo=gv.min(0);hi=gv.max(0)
   if np.any(local.max(0)<lo-.001) or np.any(local.min(0)>hi+.001):continue
   planes=PL[k['key_index'],j];dep=-np.max(local@planes[:,:3].T-planes[:,3],axis=1)*1000;inside=np.flatnonzero(dep>1e-4);peak=max(float(dep.max()),0.);triangles=[]
   if with_triangle:
    W=keyworld(gv,k,angles[k['key_index']]);kt=BVHTree.FromPolygons([Vector(v) for v in W],np.asarray(g['triangles']).reshape(-1,3).tolist(),all_triangles=True,epsilon=0);triangles=full.overlap(kt)
   if not len(inside) and not triangles:continue
   counts={d:int(np.sum(META['source_shape_names'] is None)) for d in []};labels={d:[int(v) for v in inside if D['group_weights'][v,di]>.55] for di,d in enumerate(DIGITS)}
   attr={d:dict(vertices=vs,max_depth_mm=float(dep[vs].max()) if vs else 0.) for d,vs in labels.items() if vs}
   istarget=bool(target and k['midi_note']==target['midi']);allowed=set(META['pad_patches'][target['finger']-1]) if istarget else set();wrong=[int(v) for v in inside if int(v) not in allowed]
   wp=max([float(dep[v]) for v in wrong]+[0.]);surface_peak=peak;surface_rows=[]
   for ti in sorted({int(a) for a,b in triangles}):
    depth,point=triangle_inside_depth(local[TR[ti]],planes)
    surface_peak=max(surface_peak,depth)
    if depth>1e-4:
     legal=istarget and all(int(v) in allowed for v in TR[ti])
     if not legal:wp=max(wp,depth)
     surface_rows.append(dict(hand_triangle_id=ti,inside_depth_mm=depth,world_point_m=keyworld(np.array([point]),k,angles[k['key_index']])[0].tolist(),legal_target_pulp=legal))
   worst=max(worst,wp)
   if istarget:own=max(own,surface_peak)
   hits.append(dict(key=k['note_name'],midi=k['midi_note'],piece=j,color=k['color'],role='TARGET_KEY' if istarget else 'NON_TARGET_KEY',maximum_vertex_inside_depth_mm=peak,maximum_triangle_surface_inside_depth_mm=surface_peak,triangle_interior_witnesses=surface_rows,wrong_region_depth_mm=wp,vertex_ids=inside.tolist(),digit_attribution=attr,shared_palm_or_ambiguous_vertices=[int(v) for v in inside if np.max(D['group_weights'][v])<=.55],triangle_surface_intersection_pairs=len(triangles),hand_triangle_ids=sorted({int(a) for a,b in triangles}),depth_meaning='Minimum distance to supporting planes for vertices inside each convex key piece; not vertical-only depth or triangle-pair count'))
 pairs=self_metric(V) if with_self else []
 result=dict(key_hits=hits,wrong_key_or_nonpulp_max_depth_mm=worst,target_key_max_depth_mm=own,self_skin=pairs,nonadjacent_self_triangle_pairs=sum(p['true_nonadjacent_triangle_pair_count'] for p in pairs),full_88_keys_checked=True,world_space=True)
 if target:result['contact']=contact_metric(V,KEYS[target['midi']-21],angles[target['midi']-21],target['finger'])
 return result

