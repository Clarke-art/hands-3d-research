"""Read already captured 1.7s Blender meshes; no Blender run or pose evaluation."""
from support import *
import numpy as np
W=read(O/'GEOMETRY_WITNESS_0.json');G=read(O/'GEOMETRY_POSE_0.json')
with np.load(O/'ACTUAL_BLENDER_STATIC_SKIN.npz',allow_pickle=False) as data:
    B=data['baseline_vertices'][0];V=data['corrected_vertices'][0]
    flat=data['face_vertices'];offsets=data['face_offsets'];F=[flat[offsets[i]:offsets[i+1]].tolist() for i in range(len(offsets)-1)]
functions_from(O/'blender_helpers.py',['component_planes'],globals())
key=W['E5_actual_geometry'][0];KV=np.array(key['world_vertices_m']);KF=key['faces']
planes=component_planes(dict(vertices=KV,triangles=[v for f in KF for j in range(1,len(f)-1) for v in (f[0],f[j],f[j+1])]))

def clip(poly,plane):
    out=[]
    for i,p in enumerate(poly):
        q=poly[(i+1)%len(poly)];dp=float(p@plane[:3]-plane[3]);dq=float(q@plane[:3]-plane[3])
        if dp<=0:out.append(p)
        if (dp<0<dq) or (dq<0<dp):out.append(p+(q-p)*dp/(dp-dq))
    return out

def witness(triangle):
    poly=list(triangle)
    for pl in planes:
        if not poly:break
        poly=clip(poly,pl)
    if len(poly)<3:return dict(inside_depth_lower_bound_mm=0.)
    p=np.mean(poly,axis=0);depth=float(-np.max(p@planes[:,:3].T-planes[:,3])*1000)
    return dict(inside_depth_lower_bound_mm=max(0.,depth),point_world_m=p.tolist(),clipped_patch_world_m=np.array(poly).tolist())

faces=sorted({p[1] for p in W['corrected_active_wrong_key_face_pairs']})
patches=[]
for fi in faces:
    ids=F[fi];assert len(ids)==4
    alternatives=[[(0,1,2),(0,2,3)],[(0,1,3),(1,2,3)]]
    choices=[]
    for triangles in alternatives:
        rows=[dict(skin_triangle_vertices=[ids[j] for j in tri],**witness(V[[ids[j] for j in tri]])) for tri in triangles]
        choices.append(rows)
    lower=min(max(r['inside_depth_lower_bound_mm'] for r in rows) for rows in choices)
    patches.append(dict(skin_face_index=fi,skin_face_vertices=ids,triangulation_independent_depth_lower_bound_mm=lower,triangle_witnesses_by_quad_diagonal=choices))
dump('E5_SURFACE_INTERIOR_WITNESS.json',dict(time=1.7,source='Only already evaluated Blender meshes in ACTUAL_BLENDER_STATIC_SKIN.npz and GEOMETRY_WITNESS_0.json',
    method='Clip each intersecting skin face triangle against original real convex key planes; centroid of clipped patch is a point on that triangle inside the key. Check both possible quad diagonals; report smaller lower bound. No optimizer, pose changes or new samples.',
    existing_depth_gate_mm=.5,vertex_only_corrected_depth_mm=G['corrected']['active_little_wrong_key_depth_mm'],patches=patches,
    proof_exceeds_existing_half_mm_gate=any(p['triangulation_independent_depth_lower_bound_mm']>.5 for p in patches)))
print('E5_SURFACE_DEPTH_LOWER_BOUNDS',[(p['skin_face_index'],p['triangulation_independent_depth_lower_bound_mm']) for p in patches],flush=True)

os.environ['MPLCONFIGDIR']=str(O/'mpl_config')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
fig=plt.figure(figsize=(12,5),layout='constrained')
for ix,(skin,pairs,label) in enumerate([(B,W['baseline_active_wrong_key_face_pairs'],'Original C1'),(V,W['corrected_active_wrong_key_face_pairs'],'Saved correction')]):
    ax=fig.add_subplot(1,2,ix+1,projection='3d')
    ax.add_collection3d(Poly3DCollection([KV[f]*1000 for f in KF],facecolor='#bbbbbb',edgecolor='#666666',alpha=.17,linewidth=.5))
    selected=sorted({p[1] for p in pairs})
    ax.add_collection3d(Poly3DCollection([skin[F[i]]*1000 for i in selected],facecolor='#e25141',edgecolor='#9a2020',alpha=.65,linewidth=.7))
    ax.set_title(label+' | E5 BVH face pairs: '+str(len(pairs)),fontsize=12)
    extent=np.concatenate([KV,skin[[v for i in selected for v in F[i]]]])*1000
    center=extent.mean(0);span=np.maximum(extent.max(0)-extent.min(0),[10,10,10]);span=np.array([max(span[0],25),35,22])
    ax.set_xlim(center[0]-span[0]/2,center[0]+span[0]/2);ax.set_ylim(0,35);ax.set_zlim(-15,7)
    ax.set_xlabel('world X (mm)');ax.set_ylabel('world Y (mm)');ax.set_zlabel('world Z (mm)')
    ax.view_init(elev=22,azim=-65);ax.set_box_aspect((span[0],35,22))
fig.suptitle('1.7000 s | Actual Blender skin / E5 surface witness\nRed: intersecting little-finger faces. Gray: unchanged real E5 key.',fontsize=13)
fig.savefig(O/'E5_REAL_SKIN_WITNESS.png',dpi=160)
plt.close(fig)
