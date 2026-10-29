from pathlib import Path
O=Path(__file__).resolve().parent;p=O/'geometry_detector.py';s=p.read_text(encoding='utf-8-sig')
s=s.replace('import numpy as np','import numpy as np\nfrom itertools import combinations')
idx=s.index('def contact_metric')
helper='''def triangle_inside_depth(T,planes):
    # Exact max signed-inside depth on a triangle, a 3-variable linear program.
    # Enumerate its polytope vertices; no optimizer or hand geometry modification.
    N=planes[:,:3];d=planes[:,3];dirs=np.column_stack([T[1]-T[0],T[2]-T[0]])
    A=np.c_[N@dirs,np.ones(len(N))];rhs=d-N@T[0]
    A=np.vstack([A,[-1,0,0],[0,-1,0],[1,1,0]]);rhs=np.r_[rhs,0.,0.,1.]
    comb=np.array(list(combinations(range(len(A)),3)));mat=A[comb];det=np.linalg.det(mat);comb=comb[abs(det)>1e-13]
    if not len(comb):return 0.,None
    x=np.linalg.solve(A[comb],rhs[comb]);valid=np.all(x@A.T<=rhs+1e-8,axis=1)&(x[:,2]>=-1e-8)
    if not valid.any():return 0.,None
    x=x[valid];best=x[np.argmax(x[:,2])];return max(float(best[2])*1000,0.),T[0]+dirs@best[:2]

'''
s=s[:idx]+helper+s[idx:]
s=s.replace('gaps=[];valid=[];cross=[];bandarea=0.','gaps=[];valid=[];cross=[];bandarea=0.;facegaps=[];crosspositions=[]')
s=s.replace("zs=[a[2]-surf['z'] for a in poly]","zs=[a[2]-surf['z'] for a in poly];facegaps.extend(z*1000 for z in zs)")
s=s.replace("if min(zs)<=1e-7 and max(zs)>=-1e-7:cross.append(int(ti))","""if min(zs)<=1e-7 and max(zs)>=-1e-7:
    cross.append(int(ti))
    for aa,bb in zip(poly,poly[1:]+poly[:1]):
     da=aa[2]-surf['z'];db=bb[2]-surf['z']
     if da*db<=0 and abs(da-db)>1e-15:crosspositions.append(aa+(bb-aa)*da/(da-db))""")
s=s.replace("true_pulp_min_signed_gap_mm=min(gaps) if gaps else None","true_pulp_min_signed_gap_mm=min(facegaps+gaps) if facegaps or gaps else None,pulp_min_vertex_gap_mm=min(gaps) if gaps else None")
s=s.replace("pulp_contact_position_world_m=V[minindex].tolist() if minindex is not None else None","pulp_contact_position_world_m=keyworld(np.array(crosspositions[:1]),k,angle)[0].tolist() if crosspositions else V[minindex].tolist() if minindex is not None else None")
s=s.replace("wp=max([float(dep[v]) for v in wrong]+[0.]);worst=max(worst,wp)","""wp=max([float(dep[v]) for v in wrong]+[0.]);surface_peak=peak;surface_rows=[]
   for ti in sorted({int(a) for a,b in triangles}):
    depth,point=triangle_inside_depth(local[TR[ti]],planes)
    surface_peak=max(surface_peak,depth)
    if depth>1e-4:
     legal=istarget and all(int(v) in allowed for v in TR[ti])
     if not legal:wp=max(wp,depth)
     surface_rows.append(dict(hand_triangle_id=ti,inside_depth_mm=depth,world_point_m=keyworld(np.array([point]),k,angles[k['key_index']])[0].tolist(),legal_target_pulp=legal))
   worst=max(worst,wp)""")
s=s.replace('if istarget:own=max(own,peak)','if istarget:own=max(own,surface_peak)')
s=s.replace('maximum_vertex_inside_depth_mm=peak,wrong_region_depth_mm=wp','maximum_vertex_inside_depth_mm=peak,maximum_triangle_surface_inside_depth_mm=surface_peak,triangle_interior_witnesses=surface_rows,wrong_region_depth_mm=wp')
p.write_text(s,encoding='utf8')
